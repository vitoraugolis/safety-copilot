"""
Ponte BowTie v3 → Safety Copilot.

Reavalia continuamente, em backend, o conjunto de BowTies monitorados usando
dados de processo em tempo real. Quando um deles entra em ponto de atenção,
emite um `TriggerPacket` (JSON + markdown) em `triggers/`, que é o gatilho da
análise multiagente.

Importa `bowtie_v3` como biblioteca (mesmas engines Convencional e Fuzzy do
app Streamlit) em vez de falar HTTP com o `server.py` — um processo a menos
para manter de pé.

Uso:
    python -m safety_copilot.bridge --once      # uma varredura (para cron)
    python -m safety_copilot.bridge --watch     # laço contínuo
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import tomllib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from .trigger import BarrierState, ConsequenceState, TriggerPacket

ROOT = Path(__file__).resolve().parent.parent


# ------------------------------------------------------------------- config

@dataclass
class Config:
    raw: dict
    root: Path

    @classmethod
    def load(cls, path: str | Path) -> "Config":
        p = Path(path).resolve()
        return cls(raw=tomllib.loads(p.read_text(encoding="utf-8")), root=p.parent)

    def path(self, value: str) -> Path:
        v = Path(value)
        return v if v.is_absolute() else (self.root / v)


def monitored(cfg: Config) -> list[dict]:
    """BowTies vigiados = os declarados em `config.toml` + os enviados pela
    interface (`state/bowties.json`). Separados porque `tomllib` só lê: gravar
    TOML de volta exigiria um escritor, e o registro em JSON resolve sem isso."""
    out = list(cfg.raw.get("monitored", []))
    p = cfg.path(cfg.raw.get("output", {}).get("bowties", "state/bowties.json"))
    if p.exists():
        try:
            out += json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass                       # registro corrompido não derruba a ponte
    return out


def _import_bowtie(bowtie_path: Path):
    """Coloca o pacote bowtie_v3 no sys.path e devolve as engines."""
    if not (bowtie_path / "bowtie_v3").is_dir():
        raise SystemExit(
            f"bowtie_v3 não encontrado em {bowtie_path}.\n"
            "Ajuste [bowtie].path no config.toml para a raiz do BowTie v3."
        )
    if str(bowtie_path) not in sys.path:
        sys.path.insert(0, str(bowtie_path))
    from bowtie_v3.core.model import BowTieDiagram  # noqa: PLC0415
    from bowtie_v3.engines.conventional import ConventionalEngine  # noqa: PLC0415
    from bowtie_v3.engines.fuzzy import FuzzyEngine  # noqa: PLC0415

    return BowTieDiagram, {"conventional": ConventionalEngine, "fuzzy": FuzzyEngine}


# ------------------------------------------------------- dado de processo → PFD

def pfd_from_tag(value: float, points: list[list[float]]) -> float:
    """Interpola a PFD da barreira a partir da leitura do processo.

    `points` são pares (leitura, PFD) crescentes em leitura; fora da faixa a
    função satura no extremo. Curva declarada, não inferida: quem calibra é o
    time de segurança de processos, com base em taxa de falha do equipamento.

    ponytail: interpolação linear por partes. É o modelo mais simples que
    honra "degradação é contínua, não binária" — trocar por Weibull/Markov se
    a validação com dados de campo mostrar que a linear erra a curvatura.
    """
    pts = sorted(points, key=lambda p: p[0])
    xs = np.array([p[0] for p in pts], dtype=float)
    ys = np.array([p[1] for p in pts], dtype=float)
    return float(np.interp(value, xs, ys))


def read_tags(path: Path) -> dict[str, float]:
    """Leituras atuais do processo: {tag: valor}.

    ponytail: arquivo JSON reescrito pelo historiador/OPC-UA. Trocar por
    cliente OPC-UA ou PI Web API aqui dentro, sem tocar no resto da ponte.
    """
    if not path.exists():
        return {}
    return {k: float(v) for k, v in json.loads(path.read_text(encoding="utf-8")).items()}


# ----------------------------------------------------------------- avaliação

# Cálculo do estado de PROJETO. É invariante — mesmo arquivo, mesmo motor,
# mesmo tempo — e reparsear o diagrama a cada avaliação custava metade do tempo
# de `evaluate`. Só o lado de projeto entra aqui: o diagrama "atual" tem os nós
# sobrescritos pelas leituras e precisa nascer limpo em toda chamada. A chave
# inclui o mtime para que editar o diagrama invalide o cache sem reinício.
_BASE: dict[tuple, object] = {}


def _base_calculada(diagram_path: Path, engine_name: str, t: float,
                    BowTieDiagram, engine):
    chave = (str(diagram_path), diagram_path.stat().st_mtime_ns, engine_name, t)
    if chave not in _BASE:
        _BASE.clear()                       # só o diagrama vigente interessa
        _BASE[chave] = engine.calculate(
            BowTieDiagram.from_v1_txt(str(diagram_path)), time=t)
    return _BASE[chave]


def evaluate(cfg: Config, mon: dict, tags: dict[str, float], BowTieDiagram, engines) -> TriggerPacket:
    """Roda o BowTie duas vezes — projeto e atual — e devolve sempre o quadro
    completo. `packet.reason` vazio significa que nenhum limiar disparou; é o
    que `scan()` usa para decidir emitir, e o que o painel usa para mostrar
    estado contínuo em vez de só alarme."""
    engine_name = mon.get("engine", cfg.raw["bowtie"].get("engine", "conventional"))
    engine = engines[engine_name]()
    t = float(cfg.raw["bowtie"].get("time", 1.0))
    diagram_path = cfg.path(mon["diagram"])

    base = _base_calculada(diagram_path, engine_name, t, BowTieDiagram, engine)

    live_diagram = BowTieDiagram.from_v1_txt(str(diagram_path))
    barriers: list[BarrierState] = []
    for ov in mon.get("overrides", []):
        node = live_diagram.nodes.get(ov["node"])
        if node is None:
            raise SystemExit(
                f"[{mon['id']}] nó '{ov['node']}' não existe em {diagram_path.name}"
            )
        pfd_design = node.effective_frequency(t)

        if "pfd" in ov:                      # override fixo (ex.: barreira em MOC)
            pfd_current, value = float(ov["pfd"]), None
        elif ov["tag"] in tags:
            value = tags[ov["tag"]]
            pfd_current = pfd_from_tag(value, ov["points"])
        else:                                 # tag sem leitura: mantém projeto
            pfd_current, value = pfd_design, None

        node.frequency, node.mttf = pfd_current, 0.0
        barriers.append(BarrierState(
            node=ov["node"], tag=ov.get("tag", ""), tag_value=value,
            pfd_design=pfd_design, pfd_current=pfd_current,
        ))

    cur = engine.calculate(live_diagram, time=t)

    limit = float(mon["attention_frequency"])
    ratio_limit = float(mon.get("attention_ratio", 0)) or None
    ratio = cur.top_event_frequency / base.top_event_frequency if base.top_event_frequency else float("inf")

    reasons = []
    if cur.top_event_frequency >= limit:
        reasons.append(
            f"frequência do top event {cur.top_event_frequency:.3e} ≥ limiar {limit:.3e} 1/ano"
        )
    if ratio_limit and ratio >= ratio_limit:
        reasons.append(f"erosão de {ratio:.2f}× sobre a base de projeto (limite {ratio_limit:.2f}×)")

    # Erosão = quanto do caminho entre a base de projeto e o gatilho já foi
    # percorrido. 0 no projeto, 1 no disparo — normalizado assim para os dois
    # critérios, para o painel poder mostrar a degradação *antes* do alarme.
    def _progress(atual: float, base_: float, gatilho: float) -> float:
        span = gatilho - base_
        return (atual - base_) / span if span > 0 else (1.0 if atual >= gatilho else 0.0)

    erosion = _progress(cur.top_event_frequency, base.top_event_frequency, limit)
    if ratio_limit:
        erosion = max(erosion, _progress(ratio, 1.0, ratio_limit))
    erosion = max(0.0, erosion)

    status = "critico" if reasons else ("atencao" if erosion >= 0.5 else "nominal")

    base_conseq = {c.name: c.frequency for c in base.consequences}
    return TriggerPacket(
        bowtie_id=mon["id"],
        bowtie_name=mon.get("name", mon["id"]),
        top_event=live_diagram.top_event.name,
        timestamp=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        engine=engine_name,
        reason="; ".join(reasons),
        status=status,
        erosion=erosion,
        freq_design=base.top_event_frequency,
        freq_current=cur.top_event_frequency,
        attention_frequency=limit,
        barriers=barriers,
        consequences=[
            ConsequenceState(c.name, base_conseq.get(c.name, 0.0), c.frequency)
            for c in cur.consequences
        ],
        pathways=[
            {"nodes": p.nodes, "frequency": p.frequency,
             "contribution_pct": p.contribution_pct}
            for p in cur.preventive_pathways
        ],
        linguistic=cur.linguistic,
    )


def scan(cfg: Config) -> list[Path]:
    """Uma varredura completa dos BowTies monitorados. Retorna os .json emitidos."""
    BowTieDiagram, engines = _import_bowtie(cfg.path(cfg.raw["bowtie"]["path"]))
    tags = read_tags(cfg.path(cfg.raw["tags"]["source"]))
    triggers_dir = cfg.path(cfg.raw.get("output", {}).get("triggers", "triggers"))
    state_path = cfg.path(cfg.raw.get("output", {}).get("state", "state/bridge_state.json"))
    state = json.loads(state_path.read_text()) if state_path.exists() else {}

    emitted: list[Path] = []
    for mon in monitored(cfg):
        packet = evaluate(cfg, mon, tags, BowTieDiagram, engines)
        freq = packet.freq_current
        prev = state.get(mon["id"])

        if not packet.reason:
            state.pop(mon["id"], None)          # normalizou: rearma o disparo
            print(f"[{packet.status}] {mon['id']}: {freq:.3e} 1/ano")
            continue

        # Debounce: só reemite se é novo ou se piorou >20% desde o último aviso.
        if prev and freq < prev["freq"] * 1.2:
            print(f"[warn] {mon['id']}: {freq:.3e} 1/ano (já notificado)")
            continue

        path = packet.write(triggers_dir)
        state[mon["id"]] = {"freq": freq, "ts": packet.timestamp}
        emitted.append(path)
        print(f"[DISPARO] {mon['id']}: {freq:.3e} 1/ano → {path.name}")

    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return emitted


def main() -> None:
    ap = argparse.ArgumentParser(description="Ponte BowTie v3 → Safety Copilot")
    ap.add_argument("--config", default=str(ROOT / "config.toml"))
    ap.add_argument("--once", action="store_true", help="uma varredura (padrão)")
    ap.add_argument("--watch", action="store_true", help="laço contínuo")
    args = ap.parse_args()

    cfg = Config.load(args.config)
    interval = float(cfg.raw.get("bowtie", {}).get("interval_s", 300))

    while True:
        scan(cfg)
        if not args.watch:
            return
        time.sleep(interval)


if __name__ == "__main__":
    main()
