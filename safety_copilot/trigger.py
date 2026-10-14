"""
Pacote de disparo — o que a ponte BowTie envia ao Safety Copilot.

Decisão de formato: **JSON é a fonte da verdade**; markdown é uma *view*
gerada a partir dele. Motivo: o pacote precisa ser versionável, difável entre
varreduras e validável por schema, e o LLM precisa de prosa densa. Manter as
duas como formatos independentes duplicaria a verdade — aqui o `.md` é
derivado, nunca editado à mão.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class BarrierState:
    """Uma barreira cuja PFD foi reavaliada a partir de dado de processo."""
    node: str
    tag: str = ""
    tag_value: float | None = None
    pfd_design: float = 0.0
    pfd_current: float = 0.0

    @property
    def degradation(self) -> float:
        """Quantas vezes a PFD atual é pior que a de projeto."""
        return self.pfd_current / self.pfd_design if self.pfd_design > 0 else float("inf")


@dataclass
class ConsequenceState:
    name: str
    freq_design: float
    freq_current: float


@dataclass
class TriggerPacket:
    bowtie_id: str
    bowtie_name: str
    top_event: str
    timestamp: str
    engine: str                      # "fuzzy" | "conventional"
    reason: str                      # qual limiar disparou; "" quando nenhum
    status: str                      # nominal | atencao | critico
    erosion: float                   # 0 = base de projeto, 1 = gatilho atingido
    freq_design: float               # top event com as frequências de projeto
    freq_current: float              # top event com os dados de processo atuais
    attention_frequency: float
    barriers: list[BarrierState] = field(default_factory=list)
    consequences: list[ConsequenceState] = field(default_factory=list)
    pathways: list[dict] = field(default_factory=list)   # {nodes, frequency, contribution_pct}
    linguistic: str | None = None    # categoria fuzzy do top event

    @property
    def ratio(self) -> float:
        return self.freq_current / self.freq_design if self.freq_design > 0 else float("inf")

    # ------------------------------------------------------------- render

    def to_dict(self) -> dict:
        d = asdict(self)
        d["ratio"] = self.ratio
        for b, src in zip(d["barriers"], self.barriers):
            b["degradation"] = src.degradation
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def to_markdown(self) -> str:
        L = [
            f"# Disparo de atenção — {self.bowtie_name}",
            "",
            f"- **BowTie:** `{self.bowtie_id}`",
            f"- **Top Event:** {self.top_event}",
            f"- **Detectado em:** {self.timestamp}",
            f"- **Engine:** {self.engine}"
            + (f" (categoria: **{self.linguistic}**)" if self.linguistic else ""),
            f"- **Estado:** {self.status.upper()}",
            f"- **Motivo do disparo:** {self.reason or '—'}",
            "",
            "## Frequência do Top Event",
            "",
            "| | Projeto | Atual | Razão |",
            "|---|---|---|---|",
            f"| 1/ano | {self.freq_design:.3e} | {self.freq_current:.3e} | "
            f"**{self.ratio:.2f}×** |",
            "",
            f"Limiar de atenção configurado: {self.attention_frequency:.3e} 1/ano.",
            "",
        ]

        degraded = [b for b in self.barriers if b.degradation > 1.0]
        if degraded:
            L += [
                "## Barreiras degradadas",
                "",
                "| Barreira | Tag | Leitura | PFD projeto | PFD atual | Degradação |",
                "|---|---|---|---|---|---|",
            ]
            for b in sorted(degraded, key=lambda x: -x.degradation):
                v = "—" if b.tag_value is None else f"{b.tag_value:g}"
                L.append(
                    f"| {b.node} | `{b.tag or '—'}` | {v} | {b.pfd_design:.3e} | "
                    f"{b.pfd_current:.3e} | {b.degradation:.2f}× |"
                )
            L.append("")

        if self.pathways:
            L += [
                "## Caminhos preventivos dominantes",
                "",
                "| Caminho | Frequência (1/ano) | Contribuição |",
                "|---|---|---|",
            ]
            for p in sorted(self.pathways, key=lambda x: -x["contribution_pct"])[:10]:
                L.append(
                    f"| {' → '.join(p['nodes'])} | {p['frequency']:.3e} | "
                    f"{p['contribution_pct']:.1f}% |"
                )
            L.append("")

        if self.consequences:
            L += [
                "## Consequências",
                "",
                "| Consequência | Projeto (1/ano) | Atual (1/ano) | Razão |",
                "|---|---|---|---|",
            ]
            for c in self.consequences:
                r = c.freq_current / c.freq_design if c.freq_design > 0 else float("inf")
                L.append(
                    f"| {c.name} | {c.freq_design:.3e} | {c.freq_current:.3e} | {r:.2f}× |"
                )
            L.append("")

        return "\n".join(L)

    def write(self, directory: str | Path) -> Path:
        """Grava `<id>_<timestamp>.json` e o `.md` derivado. Retorna o .json."""
        d = Path(directory)
        d.mkdir(parents=True, exist_ok=True)
        stem = f"{self.bowtie_id}_{self.timestamp.replace(':', '').replace('-', '')}"
        js = d / f"{stem}.json"
        js.write_text(self.to_json(), encoding="utf-8")
        (d / f"{stem}.md").write_text(self.to_markdown(), encoding="utf-8")
        return js
