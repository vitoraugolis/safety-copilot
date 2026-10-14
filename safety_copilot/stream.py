#!/usr/bin/env python3
"""Streaming ponto a ponto de uma RUN, com deteccao de anomalia.

Substitui o processamento em lote: percorre a serie na ordem temporal como se
fosse aquisicao ao vivo, mantem estado incremental (valor, taxa por tag, alarmes
abertos, discrepancia entre canais) e, ao detectar anomalia, congela o contexto
da Fase A e chama o agente unico.

Processo unico e sincrono. O relogio virtual PAUSA durante a analise: a fonte e
uma tabela, nao um sensor, entao pausar nao perde amostra nenhuma e o agente
analisa um instante coerente em vez de um alvo em movimento.

    python3 -m safety_copilot.stream --run RUN_A                  # so o detector
    python3 -m safety_copilot.stream --run RUN_A --analisar       # com o agente
    python3 -m safety_copilot.stream --run RUN_A --speed 0        # sem dormir
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from datetime import datetime
from pathlib import Path

from . import blind_feed as bf
from . import contexto as ctx

ROOT = Path(__file__).resolve().parent.parent
SAIDA = ROOT / "state" / "stream"

# dt acima disto e lacuna: o motor adianta sem dormir E zera a janela da taxa.
# O horizonte longo e amostrado a 4 h e o episodio a 5 s; taxa calculada
# atravessando a juncao seria lixo numerico, e a taxa e obrigatoria por C7.
LACUNA_S = 60
TETO_SLEEP_S = 2.0


def _dt(ts: str) -> datetime:
    return datetime.fromisoformat(ts)


class Estado:
    """Estado incremental do motor. Memoria; o checkpoint e o proprio ts."""

    def __init__(self, lims: list[dict]):
        self.lim = {l["tag"]: l for l in lims}
        self.faixa = {l["tag"]: (l["hihi"] - l["lolo"])
                      for l in lims if l["hihi"] is not None and l["lolo"] is not None}
        self.janela: dict[str, list[tuple[float, float]]] = {}
        self.abertos: set[tuple[str, str]] = set()
        self.ts: str | None = None

    # ---------------------------------------------------------------- taxa
    def _taxa(self, tag: str, epoch: float, v: float, lacuna: bool) -> float | None:
        j = self.janela.setdefault(tag, [])
        if lacuna:
            j.clear()
        j.append((epoch, v))
        corte = epoch - ctx.JANELA_TAXA_S
        while len(j) > 2 and j[0][0] < corte:
            j.pop(0)
        span = j[-1][0] - j[0][0]
        if len(j) < 3 or span < ctx.SPAN_MIN_TAXA_S:
            return None
        return statistics.linear_regression([p[0] for p in j], [p[1] for p in j]).slope * 60.0

    # -------------------------------------------------------------- alarmes
    def _alarmes(self, tags: dict[str, float]) -> list[dict]:
        """Maquina de estado por (tag, tipo), sem histerese.

        Sem histerese reproduz `alarm_events` exatamente, o que faz do banco o
        autoteste do detector. `e_demanda` NAO e rederivado: o banco e
        inconsistente nele, e inventar a regra colocaria julgamento no motor —
        a skill pede que o agente decida se o alarme constitui demanda.
        """
        novos = []
        for tag, v in tags.items():
            l = self.lim.get(tag)
            if not l:
                continue
            for tipo, limite, acima in (("HIHI", l["hihi"], True), ("HI", l["hi"], True),
                                        ("LO", l["lo"], False), ("LOLO", l["lolo"], False)):
                if limite is None:
                    continue
                dentro = (v >= limite) if acima else (v <= limite)
                chave = (tag, tipo)
                if dentro and chave not in self.abertos:
                    self.abertos.add(chave)
                    novos.append({"tag": tag, "tipo": tipo, "limite": limite, "valor": round(v, 3)})
                elif not dentro and chave in self.abertos:
                    self.abertos.discard(chave)
        return novos

    # --------------------------------------------------------- discrepancia
    def _discrepancia(self, canais: dict[str, dict]) -> list[dict]:
        out = []
        for tag, v in canais.items():
            if len(v) < 2:
                continue
            spread = max(v.values()) - min(v.values())
            f = self.faixa.get(tag)
            if f and spread >= ctx.FRAC_DISCREPANCIA * f:
                med = statistics.median(v.values())
                fora = max(v, key=lambda k: abs(v[k] - med))
                out.append({"tag": tag, "spread": round(spread, 2),
                            "limite": round(ctx.FRAC_DISCREPANCIA * f, 2),
                            "canal_divergente": fora,
                            "desvio": round(v[fora] - med, 2)})
        return out

    # ---------------------------------------------------------------- passo
    def passo(self, p: dict) -> dict:
        epoch = _dt(p["ts"]).timestamp()
        lacuna = bool(self.ts and (epoch - _dt(self.ts).timestamp()) > LACUNA_S)
        taxas = {t: self._taxa(t, epoch, v, lacuna) for t, v in p["tags"].items()}
        motivos = []
        for a in self._alarmes(p["tags"]):
            motivos.append({"chave": f"alarme:{a['tag']}:{a['tipo']}", **a})
        for d in self._discrepancia(p["canais"]):
            motivos.append({"chave": f"discrepancia:{d['tag']}", **d})
        self.ts = p["ts"]
        return {"ts": p["ts"], "taxas": taxas, "motivos": motivos,
                "alarmes_abertos": sorted(f"{t}:{k}" for t, k in self.abertos)}


# Merging of triggers into one analysis. Anything closer than GRUPO_S belongs to
# the same moment (the interlock event at 02:07:22 and the HIHI alarm at
# 02:07:30 are one demand). Record-only groups merge over an hour: a work order
# opened at 00:00 and the channel failure it records, detected at 00:30, are one
# fact, not two.
GRUPO_S = 120
GRUPO_REGISTRO_S = 3600


def _eh_registro(m: dict) -> bool:
    return m["chave"].startswith("record:")


def renderizar(analises: list[dict]) -> None:
    """Re-render every analysis with the complete timeline.

    Each report links the whole dated sequence, and the decision titles come
    from the phase B texts as written. Also callable after phase B is added.
    """
    from . import relatorio
    for a_ in analises:
        pb = Path(a_["dir"]) / "phase_b.md"
        if pb.exists():
            a_["titulo"] = next((l.lstrip("# ").strip() for l in pb.read_text().splitlines()
                                 if l.startswith("# ")), None)
    for a_ in analises:
        d = Path(a_["dir"])
        cj = d / "context.json"
        if not cj.exists():
            continue
        pb = d / "phase_b.md"
        relatorio.render(json.loads(cj.read_text()), pb.read_text() if pb.exists() else None,
                         d, timeline=analises)


def rodar(run: str, speed: float = 0.0, modo: str = "detector",
          desde: str | None = None, ate: str | None = None,
          max_analises: int | None = None, modelo: str | None = None) -> Path:
    """Replay a RUN point by point; open an analysis on qualifying triggers.

    modo = "detector" → triggers only; "fase_a" → also freeze phase A per
    analysis; "completa" → also run phase B (the sandboxed agent).
    """
    from . import agente, relatorio
    con = bf.connect()
    est = Estado(bf.limiares(con))
    sess = SAIDA / run
    sess.mkdir(parents=True, exist_ok=True)
    inc_log = (sess / "triggers.jsonl").open("w")

    registros = bf.eventos_de_registro(con, run, ate)
    if desde:
        registros = [e for e in registros if e["ts"] > desde]
        for r in con.execute(
            """SELECT tag, tipo FROM alarm_events WHERE run_id=? AND ts_inicio<=?
                 AND (ts_fim IS NULL OR ts_fim>?)""", (run, desde, desde)):
            est.abertos.add((bf.ALIAS.get(r["tag"], r["tag"]), r["tipo"]))

    grupo: list[dict] = []
    analises: list[dict] = []
    por_dia: dict[str, int] = {}
    vistos_alarme_dia: set[tuple] = set()
    vistos_disc: set[str] = set()
    n = 0
    t_parede = time.time()

    def analisar_grupo(g: list[dict]) -> None:
        if modo == "detector" or (max_analises and len(analises) >= max_analises):
            return
        ts = g[-1]["ts"]
        dia = ts[:10].replace("-", "")
        por_dia[dia] = por_dia.get(dia, 0) + 1
        inc = f"INC-BT-REATOR-{dia}-{por_dia[dia]}"
        destino = agente.SAIDA / inc
        chaves = [m["chave"] for m in g]
        print(f"  -> analysis {len(analises)+1} at {ts} ({inc}): {', '.join(chaves)}", flush=True)
        if modo == "completa":
            res = agente.analisar(run, ts, motivos=g, incident_id=inc, modelo=modelo,
                                  destino=destino)
            ok, fase_b = res["ok"], res["phase_b"]
        else:
            res = agente.preparar(run, ts, motivos=g, incident_id=inc, destino=destino)
            ok, fase_b = False, ""
        relatorio.render(res["contexto"], fase_b or None, destino)
        analises.append({"n": len(analises) + 1, "ts": ts, "incident_id": inc,
                         "triggers": chaves, "phase_b": ok, "dir": str(destino)})

    def emitir(m: dict, pede: bool) -> None:
        nonlocal grupo
        inc_log.write(json.dumps({**m, "requests_analysis": pede}, ensure_ascii=False) + "\n")
        if not pede:
            return
        print(f"[{m['ts']}] trigger: {m['chave']}", flush=True)
        if grupo:
            janela = (GRUPO_REGISTRO_S if all(map(_eh_registro, grupo + [m])) else GRUPO_S)
            if (_dt(m["ts"]) - _dt(grupo[0]["ts"])).total_seconds() > janela:
                analisar_grupo(grupo)
                grupo = []
        grupo.append(m)

    ultimo_ts = None
    anterior_epoch = None
    for p in bf.stream_pontos(con, run, desde):
        if ate and p["ts"] > ate:
            break
        while registros and registros[0]["ts"] <= p["ts"]:
            e = registros.pop(0)
            emitir({"chave": f"record:{e['tipo']}:{e['ref']}", **e}, True)
        epoch = _dt(p["ts"]).timestamp()
        if speed > 0 and anterior_epoch is not None:
            dt = epoch - anterior_epoch
            if dt <= LACUNA_S:
                time.sleep(min(dt / speed, TETO_SLEEP_S))
        anterior_epoch = epoch
        r = est.passo(p)
        n += 1
        ultimo_ts = p["ts"]
        for m in r["motivos"]:
            m = {**m, "ts": p["ts"]}
            if m["chave"].startswith("alarme:"):
                k = (m["tag"], m["tipo"], p["ts"][:10])
                pede = k not in vistos_alarme_dia
                vistos_alarme_dia.add(k)
            else:
                pede = m["chave"] not in vistos_disc
                vistos_disc.add(m["chave"])
            emitir(m, pede)

    if ultimo_ts:
        emitir({"chave": "end_of_record", "ts": ultimo_ts}, True)
    if grupo:
        analisar_grupo(grupo)
    inc_log.close()

    renderizar(analises)

    meta = {"run": run, "points": n, "wall_seconds": round(time.time() - t_parede, 2),
            "mode": modo, "database": bf.DB.name, "analyses": analises}
    (sess / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    (sess / "analyses.json").write_text(json.dumps(analises, ensure_ascii=False, indent=2))
    print(f"\n{n} points in {meta['wall_seconds']}s · {len(analises)} analysis(es) · {sess}")
    return sess


def main() -> None:
    ap = argparse.ArgumentParser(prog="python3 -m safety_copilot.stream")
    ap.add_argument("--run", default="RUN_A")
    ap.add_argument("--speed", type=float, default=0.0, help="acceleration; 0 = no sleep")
    ap.add_argument("--modo", choices=["detector", "fase_a", "completa", "render"],
                    default="detector", help="render = re-render an existing session only")
    ap.add_argument("--desde", default=None)
    ap.add_argument("--ate", default=None)
    ap.add_argument("--max-analises", type=int, default=None)
    ap.add_argument("--modelo", default=None)
    a = ap.parse_args()
    if a.modo == "render":
        idx = SAIDA / a.run / "analyses.json"
        analises = json.loads(idx.read_text())
        renderizar(analises)
        idx.write_text(json.dumps(analises, ensure_ascii=False, indent=2))
        print(f"re-rendered {len(analises)} analysis(es)")
        return
    rodar(a.run, a.speed, a.modo, a.desde, a.ate, a.max_analises, a.modelo)


if __name__ == "__main__":
    main()
