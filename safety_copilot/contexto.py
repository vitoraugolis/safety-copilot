#!/usr/bin/env python3
"""Fase A da skill `analise-seguranca` — montagem de contexto, deterministica.

A skill argumenta sobre si mesma que o bloco de contexto "pode ser auditado por
inspecao: ou o valor bate com o banco, ou nao bate. Nao ha raciocinio a
questionar". Se um LLM monta esse bloco, a segunda frase e falsa e a
justificativa inteira cai. Entao a Fase A e codigo: o portao A->B vira fronteira
de processo, nao instrucao no prompt.

Regra dura do modulo: aqui nao se reimplementa nenhuma formula. Todo numero e
lido de `blind_feed` / `bridge` / `trajetoria`, e o campo `fonte` diz de onde
veio. Numero novo e composicao de numeros lidos, nunca conta nova.

    python3 -m safety_copilot.contexto --run RUN_A               # markdown
    python3 -m safety_copilot.contexto --run RUN_A --json        # o bloco cru
"""

from __future__ import annotations

import argparse
import json
import statistics
from datetime import datetime, timedelta
from pathlib import Path

from . import blind_feed as bf

ROOT = Path(__file__).resolve().parent.parent

# Janela de calculo da taxa de variacao. A skill exige a taxa e exige declarar a
# janela ("longa o bastante para nao capturar ruido e curta o bastante para
# refletir a tendencia atual"). 300 s cobre 60 amostras no episodio a 5 s.
JANELA_TAXA_S = 300
SPAN_MIN_TAXA_S = 60

# Discrepancia entre canais de um grupo votado que conta como achado, em fracao
# da faixa lolo..hihi da tag. 5% de 350 kPa = 17,5 kPa.
#
# ponytail: fracao unica para toda tag votada. Vira coluna em `ativos` quando o
# time de seguranca quiser diferenciar por instrumento.
FRAC_DISCREPANCIA = 0.05

BARREIRAS_PATHWAY = {"T1": ["B1", "B2"], "T2": ["B3", "B4"]}


def _dt(ts: str) -> datetime:
    return datetime.fromisoformat(ts)


def _leitura(valor, fonte: str) -> dict:
    return {"valor": valor, "tipo": "leitura", "fonte": fonte}


def _calculo(valor, formula: str, entradas: str) -> dict:
    return {"valor": valor, "tipo": "calculo", "formula": formula, "entradas": entradas}


# ─────────────────────────────────────────────────────────────── A2: estado

def taxas(con, run: str, ts: str) -> dict:
    """Taxa de variacao por tag na janela recente, por regressao linear.

    Obrigatoria pela skill (C7): valor instantaneo nao distingue um alarme ativo
    ha 4 h com a variavel estavel de um ativo ha 20 min subindo rapido.
    """
    t1 = _dt(ts)
    out: dict[str, dict] = {}
    for tag, alias in bf.ALIAS.items():
        rows = con.execute(
            """SELECT ts, valor FROM series
               WHERE run_id=? AND tag=? AND COALESCE(canal,'voted')='voted'
                 AND ts<=? ORDER BY ts DESC LIMIT 400""", (run, tag, ts)).fetchall()
        pts = [(_dt(r["ts"]), r["valor"]) for r in rows
               if (t1 - _dt(r["ts"])).total_seconds() <= JANELA_TAXA_S]
        if len(pts) < 3:
            continue
        span = (pts[0][0] - pts[-1][0]).total_seconds()
        if span < SPAN_MIN_TAXA_S:
            out[alias] = {"valor": None, "tipo": "lacuna",
                          "motivo": f"janela cobre {span:.0f} s; minimo {SPAN_MIN_TAXA_S} s"}
            continue
        x = [(p[0] - pts[-1][0]).total_seconds() for p in reversed(pts)]
        y = [p[1] for p in reversed(pts)]
        incl = statistics.linear_regression(x, y).slope
        out[alias] = _calculo(round(incl * 60.0, 4),
                              "regressao linear sobre a janela, em unidade/min",
                              f"{len(pts)} amostras, span {span:.0f} s, janela {JANELA_TAXA_S} s")
    return out


def discrepancia_canais(con, run: str, ts: str, lims: list[dict]) -> list[dict]:
    """Spread entre canais A/B/C de cada grupo votado, contra a faixa de alarme.

    E o observavel que revela transmissor degradado sem depender do registro de
    manutencao — a operacao ve os tres canais, mesmo sem saber que um falhou.
    """
    faixa = {l["tag"]: (l["hihi"] - l["lolo"]) for l in lims
             if l["hihi"] is not None and l["lolo"] is not None}
    out = []
    for tag, alias in bf.ALIAS.items():
        rows = con.execute(
            """SELECT canal, valor FROM series
               WHERE run_id=? AND tag=? AND canal IN ('A','B','C')
                 AND ts=(SELECT MAX(ts) FROM series
                         WHERE run_id=? AND tag=? AND canal IN ('A','B','C') AND ts<=?)""",
            (run, tag, run, tag, ts)).fetchall()
        if len(rows) < 2:
            continue
        v = {r["canal"]: round(r["valor"], 2) for r in rows}
        spread = round(max(v.values()) - min(v.values()), 2)
        f = faixa.get(alias)
        mediana = statistics.median(v.values())
        out.append({
            "tag": alias, "canais": v,
            "spread": _calculo(spread, "max(canais) - min(canais)", "leitura por canal"),
            "desvio_contra_mediana": {k: round(x - mediana, 2) for k, x in v.items()},
            "limite": _leitura(round(FRAC_DISCREPANCIA * f, 2) if f else None,
                               f"{FRAC_DISCREPANCIA:.0%} da faixa lolo..hihi de alarm_config"),
            "acima_do_limite": bool(f and spread >= FRAC_DISCREPANCIA * f),
        })
    return out


def contradicoes(con, run: str, ts: str, wos: list[dict]) -> list[dict]:
    """Sources that disagree. The skill says record both, never choose.

    The case in this dataset: the PFD creep clock resets on the last CLOSED
    test/calibration/training work order. PT-007's only closed order is
    corrective, which does not count, so the clock falls back to the start of
    the horizon and reports the item within its interval — while the functional
    test of the SAME item is overdue.

    Choosing is the team's call. What phase A can do without choosing is compute
    the PFD under both readings: the calendar implies a last test one interval
    before the due date.
    """
    out = []
    comp = bf.componentes(con)
    vencidas = [w for w in wos
                if not w["data_fechamento"] and w["vencimento"] and w["vencimento"] <= ts
                and w["tipo"] in ("teste_funcional", "calibracao")]
    for w in vencidas:
        eq = w["equipamento_id"]
        pfd = bf.pfd_confiabilidade(con, run, ts, eq)
        dentro = [m for m in pfd.get("motivos", []) if "since the last test" in m]
        if not dentro:
            continue
        a = con.execute("SELECT intervalo_teste_h FROM ativos WHERE equipamento_id=?",
                        (eq,)).fetchone()
        T = float(a["intervalo_teste_h"] or 8760.0)
        implicito = (_dt(w["vencimento"]) - timedelta(hours=T)).isoformat()
        alt = bf.pfd_confiabilidade(con, run, ts, eq, implicito)
        barreiras_do_item = [b for b, itens in comp.items() if eq in itens and b in ("B1", "B2")]
        sens = {}
        for b in barreiras_do_item:
            mod = bf.pfd_barreira(con, run, ts, b)["pfd"]
            cal = bf.pfd_barreira(con, run, ts, b, {eq: implicito})["pfd"]
            sens[b] = {"pfd_relogio_do_modelo": round(mod, 6),
                       "pfd_relogio_do_calendario": round(cal, 6),
                       "razao": round(cal / mod, 2) if mod else None}
        out.append({
            "item": eq,
            "fonte_a": {"o_que": "PFD creep clock", "diz": dentro[0],
                        "regra": "resets on the last CLOSED test/calibration/training "
                                 "work order; a corrective order does not reset it"},
            "fonte_b": {"o_que": f"maintenance calendar ({w['wo_id']})",
                        "diz": f"{w['tipo']} overdue by "
                               f"{(_dt(ts) - _dt(w['vencimento'])).days} d",
                        "regra": "work_orders.vencimento <= t_now with no data_fechamento"},
            "sensibilidade": {
                "ultimo_teste_implicito": implicito,
                "premissa": "due date minus the declared test interval "
                            f"({T/24:.0f} d); an assumption, not a record",
                "pfd_item_relogio_do_modelo": pfd["pfd"],
                "pfd_item_relogio_do_calendario": alt["pfd"],
                "razao_item": round(alt["pfd"] / pfd["pfd"], 2) if pfd["pfd"] else None,
                "por_barreira": sens,
            },
            "nao_resolvida": "Both readings come from the same database and disagree. "
                             "Phase A reports the PFD under each; which clock governs "
                             "is a decision for the team.",
        })
    return out


# ─────────────────────────────────────────────── declared design basis
#
# Machine-readable extract of
# `.agents/skills/analise-seguranca/references/design-basis-barriers.md`.
# The document is the source of truth for a human reader; this dict is what the
# crossings compare against, and every entry names the section it came from.
#
# ponytail: a dict, not a parser. The document changes on the order of months;
# a markdown parser would be more code than the six numbers are worth. If the
# two ever disagree, the test below fails.

# Masked name of the MOC record (blind_feed.TEXT_SUBS).
MOC = "operating_condition_change"

DESIGN_BASIS = {
    "documento": "references/design-basis-barriers.md",
    "condicao_de_projeto": {
        "secao": "2",
        "pressao_regime_kpa": 2708.0,
        "nivel_regime_pct": 74.4,
        "temperatura_regime_c": 120.4,
        "vazao_alimentacao_kscmh": 0.252,
        "taxa_escalada_kpa_min": 1.1,
        "plato": {"de_kpa": 2850.0, "ate_kpa": 2870.0, "duracao_h": 1.7,
                  "taxa_local_kpa_min": 0.27},
    },
    "escada_protecao": {"secao": "3", "hi": 2750.0, "hihi": 2800.0,
                        "trip_sis": 2900.0, "limite_fisico": 3000.0,
                        "ruido_kpa": 1.93},
    "desempenho": {
        "secao": "5",
        "janela_hi_sis_min": 202.0,
        "janela_hihi_sis_min": 162.0,
        "atraso_tolerav_b2_min": 67.0,
        "criterio_sucesso": "pressure reverts without reaching the SIS trip",
    },
    "barreiras": {
        "B1": {"classe": "automatic", "tempo_atuacao": "seconds",
               "gatilho": "voted PIT-7001 >= HIHI",
               "efeito_colateral": "closes the A+C feed valve, which is the actuator "
                                   "of the level cascade LIC-8001; inventory control is "
                                   "lost, level goes to about -2.5 % and a low-level "
                                   "trip follows roughly 1 h later"},
        "B2": {"classe": "human", "tempo_atuacao": "minutes",
               "gatilho": "command-versus-position discrepancy on ZT-1001",
               "nota": "not triggered by the pressure alarm; demand exists only after "
                       "B1 has tried and failed. Detection is independent of B1 "
                       "(ZT-1001 versus PT-007); the final element is shared."},
    },
    "independencia": {
        "secao": "4",
        "deteccao": "independent (PT-007 versus ZT-1001)",
        "atuacao": "shared (XV-1001 and VLV-006)",
        "consequencia": "joint credit must not multiply the two PFDs",
    },
    "invalidacao": {
        "secao": "7",
        "taxa_limite_kpa_min": 2.2,
        "gatilhos": ["measured escalation rate above 2.2 kPa/min",
                     "operating-condition change without subsequent revalidation",
                     "alarm_config thresholds changed without recomputing windows",
                     "voting arrangement or test interval changed in ativos"],
    },
    "ameaca": {"secao": "6", "T1": "not classified; requires threat-removal test"},
}


def _plato_medido(rows: list[tuple[str, float]], de: float, ate: float) -> dict | None:
    """How long the pressure actually spent inside the design plateau band."""
    seg = [(t, v) for t, v in rows if de <= v <= ate]
    if len(seg) < 3:
        return None
    dur_min = (_dt(seg[-1][0]) - _dt(seg[0][0])).total_seconds() / 60.0
    d = _taxa_janela(rows, seg[0][0], seg[-1][0])
    return {"de": seg[0][0], "ate": seg[-1][0], "duracao_min": round(dur_min, 1),
            "taxa_local": d["taxa"] if d else None}


# ─────────────────────────────────────────────── C1: escada de taxas
#
# Um valor unico de taxa conta a historia errada em duas direcoes opostas: a
# media do episodio dilui a escalada com a queda inicial, e o valor instantaneo
# nao mostra que a escalada e sustentada. A escada mede a MESMA grandeza em
# varias janelas e declara a janela em cada linha — e o que permite dizer "a
# taxa global esta em X e a taxa na janela em que a decisao e tomada esta em Y".

def _taxa_janela(rows: list[tuple[str, float]], t0: str, t1: str) -> dict | None:
    seg = [(_dt(t), v) for t, v in rows if t0 <= t <= t1]
    if len(seg) < 3:
        return None
    x = [(p[0] - seg[0][0]).total_seconds() for p in seg]
    y = [p[1] for p in seg]
    return {"taxa": round(statistics.linear_regression(x, y).slope * 60.0, 2),
            "amostras": len(seg), "span_min": round(x[-1] / 60.0, 1),
            "de": t0, "ate": t1}


def escada_de_taxas(con, run: str, ts: str, a2_eventos: list[dict] | None = None,
                    tag: str = "PIT-7001") -> dict:
    """Taxa da mesma tag em varias janelas, cada uma declarada.

    Todos os marcos vem de fonte que a operacao conhece em `ts`: alarm_events
    com ts_inicio <= ts, process_events com visivel_copiloto=1 e ts <= ts, e a
    propria serie. Nenhum marco vem do gabarito.
    """
    a2_eventos = a2_eventos or []
    interno = bf.REVERSE.get(tag, tag)
    t0_ep = ts[:10] + "T00:00:00"
    rows = [(r["ts"], r["valor"]) for r in con.execute(
        """SELECT ts, valor FROM series WHERE run_id=? AND tag=?
             AND COALESCE(canal,'voted')='voted' AND ts BETWEEN ? AND ? ORDER BY ts""",
        (run, interno, t0_ep, ts))]
    if len(rows) < 3:
        return {"tag": tag, "degraus": [], "lacuna": "serie insuficiente na janela"}

    marcos: dict[str, str] = {}
    for r in con.execute(
        """SELECT tipo, ts_inicio FROM alarm_events WHERE run_id=? AND tag=?
             AND ts_inicio<=? AND ts_inicio>=? ORDER BY ts_inicio""",
        (run, interno, ts, t0_ep)):
        marcos.setdefault(r["tipo"], r["ts_inicio"])
    trip = con.execute(
        """SELECT ts, detalhe FROM process_events WHERE run_id=? AND visivel_copiloto=1
             AND tipo='trip_sis' AND ts<=? ORDER BY ts LIMIT 1""", (run, ts)).fetchone()
    vale = min(rows, key=lambda r: r[1])

    degraus = []
    def _add(nome, t0, t1, nota=""):
        if not (t0 and t1) or t0 >= t1:
            return
        d = _taxa_janela(rows, t0, t1)
        if d:
            degraus.append({"janela": nome, "nota": nota, **d})

    fim_ref = trip["ts"] if trip else ts
    fim_nome = "the SIS trip" if trip else "t_now"
    _add("since 00:00 of the day", t0_ep, ts, "includes any initial fall")
    _add(f"valley ({vale[1]:.0f} kPa) to {fim_nome}", vale[0], fim_ref)
    if marcos.get("HI") and marcos.get("HIHI"):
        _add("HI to HIHI", marcos["HI"], marcos["HIHI"])
    if marcos.get("HIHI"):
        _add(f"HIHI to {fim_nome}", marcos["HIHI"], fim_ref,
             "the window in which the decision is taken")
    if trip:
        _add("after the SIS acted", trip["ts"], ts,
             "escalation continues after the last automated layer")
    _add("last 10 min before t_now",
         max(t0_ep, (_dt(ts) - timedelta(minutes=10)).isoformat()), ts)

    cb = DESIGN_BASIS["condicao_de_projeto"]
    inv = DESIGN_BASIS["invalidacao"]
    ref, limite = cb["taxa_escalada_kpa_min"], inv["taxa_limite_kpa_min"]
    for d in degraus:
        d["razao_vs_projeto"] = round(d["taxa"] / ref, 1) if ref else None
        # Escalation is a rise. A falling pressure at -2.76 kPa/min once counted
        # as "escalation above 2.2" because of an abs() here.
        d["excede_limite"] = d["taxa"] > limite

    # gatilhos da secao 7, avaliados um a um
    moc = [e for e in a2_eventos if e["tipo"] == MOC]
    plato = _plato_medido(rows, cb["plato"]["de_kpa"], cb["plato"]["ate_kpa"])
    gatilhos = [
        {"gatilho": inv["gatilhos"][0],
         "observado": any(d["excede_limite"] for d in degraus),
         "evidencia": f"{sum(d['excede_limite'] for d in degraus)} of "
                      f"{len(degraus)} windows above {limite} kPa/min"},
        {"gatilho": inv["gatilhos"][1],
         "observado": bool(moc),
         "evidencia": (f"operating-condition change at {moc[0]['ts']}; no work order and no window "
                       "revalidation event after that date" if moc
                       else "no operating-condition change event in the window")},
        {"gatilho": "design plateau not observed",
         "observado": bool(plato and plato["duracao_min"] <
                           cb["plato"]["duracao_h"] * 60 * 0.5),
         "evidencia": (f"the {cb['plato']['de_kpa']:.0f}-{cb['plato']['ate_kpa']:.0f} kPa band "
                       f"lasted {plato['duracao_min']} min at {plato['taxa_local']} kPa/min, "
                       f"against {cb['plato']['duracao_h']} h at "
                       f"{cb['plato']['taxa_local_kpa_min']} kPa/min in the design case"
                       if plato else "plateau band not crossed in the window")},
    ]

    tx = [d["taxa"] for d in degraus]
    return {
        "tag": tag,
        "degraus": degraus,
        "dispersao": {"minima": min(tx), "maxima": max(tx),
                      "razao": round(max(tx) / min(tx), 2) if min(tx) else None} if tx else None,
        "trip_sis": (dict(trip) if trip else None),
        "referencia_de_projeto": {"taxa_kpa_min": ref, "fonte": "design basis, section "
                                  + cb["secao"]},
        "limite_de_invalidacao": {"taxa_kpa_min": limite, "fonte": "design basis, section "
                                  + inv["secao"]},
        "gatilhos_de_invalidacao": gatilhos,
        "plato_medido": plato,
        "invalidada": any(g["observado"] for g in gatilhos),
        "janelas_de_projeto": DESIGN_BASIS["desempenho"],
    }


# ─────────────────────────────────────────────── demand outcome per barrier
#
# The previous version anchored B1's actuation check on the SIS trip, and the
# report then read the trip as B1's actuation. They are different layers: B1 is
# demanded at HIHI (2800 kPa) and succeeds only if pressure reverts before the
# SIS trip (2900 kPa). The SIS acting is evidence that B1 did NOT arrest the
# excursion — never evidence that B1 acted.
#
# Each barrier is walked on the detect-decide-act model at its OWN demand
# instant, and the outcome is compared with the design basis success criterion.
# Phase A compares; it does not classify.

# Design basis, section 4: B1 closes the feeds and opens the purge; closing the
# A+C feed destroys inventory control, so level falls.
ATUACAO_ESPERADA_B1 = (("XV-1001A", "close"), ("XV-1001B", "close"),
                       ("XV-1001C", "close"), ("XV-1001D", "close"),
                       ("FCV-0601", "open"), ("LIT-8001", "fall"))
# ponytail: one deadband for every signal, in percentage points. Per-tag when a
# valve's normal control travel is shown to exceed it.
BANDA_MORTA_PP = 5.0


def _media(con, run: str, tag: str, a: str, b: str) -> float | None:
    interno = bf.REVERSE.get(tag, tag)
    xs = [r[0] for r in con.execute(
        """SELECT valor FROM series WHERE run_id=? AND tag=?
             AND COALESCE(canal,'voted')='voted' AND ts>=? AND ts<? ORDER BY ts""",
        (run, interno, a, b))]
    return sum(xs) / len(xs) if xs else None


def desfecho_das_demandas(con, run: str, ts: str, lims: list[dict], a2: dict) -> dict:
    pit = next((l for l in lims if l["tag"] == "PIT-7001"), None)
    if not pit:
        return {}
    interno = bf.REVERSE["PIT-7001"]
    hihi, trip_v = pit["hihi"], pit.get("trip_sis")
    comp = bf.componentes(con)
    out: dict = {}

    alarme = con.execute(
        """SELECT ts_inicio FROM alarm_events WHERE run_id=? AND tag=? AND tipo='HIHI'
             AND e_demanda=1 AND ts_inicio<=? ORDER BY ts_inicio DESC LIMIT 1""",
        (run, interno, ts)).fetchone()
    if not alarme:
        out["B1"] = {"barreira": "B1", "demandada": False,
                     "gatilho_declarado": DESIGN_BASIS["barreiras"]["B1"]["gatilho"],
                     "nota": "no demand on B1 recorded up to t_now"}
        return out
    t_alarme = alarme["ts_inicio"]
    amostra = con.execute(
        """SELECT ts FROM series WHERE run_id=? AND tag=? AND canal='voted'
             AND valor>=? AND ts<=? AND ts>=? ORDER BY ts LIMIT 1""",
        (run, interno, hihi, t_alarme,
         (_dt(t_alarme) - timedelta(minutes=5)).isoformat())).fetchone()
    t_amostra = amostra["ts"] if amostra else t_alarme

    eventos_b1 = []
    for e in a2["eventos_operacionais"]:
        try:
            det = json.loads(e["detalhe"]) if isinstance(e["detalhe"], str) else (e["detalhe"] or {})
        except json.JSONDecodeError:
            det = {}
        if (det.get("barreira", "").endswith(".B1") or det.get("ativo") in comp.get("B1", [])) \
                and (_dt(t_alarme) - timedelta(minutes=2)).isoformat() <= e["ts"] <= ts:
            eventos_b1.append({"ts": e["ts"], "tipo": e["tipo"], "detalhe": det})
    ancora = min([t_amostra] + [e["ts"] for e in eventos_b1])

    canais = {r["canal"]: round(r["valor"], 2) for r in con.execute(
        """SELECT canal, valor FROM series WHERE run_id=? AND tag=? AND canal IN ('A','B','C')
             AND ts=?""", (run, interno, t_amostra))}
    acima = sorted(k for k, v in canais.items() if v >= hihi)

    ordens = [w for w in a2["ordens_servico"]
              if w["equipamento_id"] in comp.get("B1", []) and w["falha_encontrada"]
              and w["data_abertura"] >= (_dt(ancora) - timedelta(minutes=2)).isoformat()]

    fim = min(ts, (_dt(ancora) + timedelta(minutes=5)).isoformat())
    sinais = []
    if (_dt(fim) - _dt(ancora)).total_seconds() >= 60:
        a0 = (_dt(ancora) - timedelta(minutes=5)).isoformat()
        for tag, esperado in ATUACAO_ESPERADA_B1:
            ma, md = _media(con, run, tag, a0, ancora), _media(con, run, tag, ancora, fim)
            if ma is None or md is None:
                continue
            d = md - ma
            ok = (d <= -BANDA_MORTA_PP if esperado in ("close", "fall")
                  else d >= BANDA_MORTA_PP)
            sinais.append({"tag": tag, "descricao": (bf.DESCRICAO.get(tag) or ("",))[0],
                           "esperado": esperado, "media_antes": round(ma, 2),
                           "media_depois": round(md, 2), "delta": round(d, 2),
                           "como_esperado": ok})

    trip = con.execute(
        """SELECT ts, detalhe FROM process_events WHERE run_id=? AND visivel_copiloto=1
             AND tipo='trip_sis' AND ts>=? AND ts<=? ORDER BY ts LIMIT 1""",
        (run, ancora, ts)).fetchone()
    reverteu = con.execute(
        """SELECT ts FROM series WHERE run_id=? AND tag=? AND canal='voted'
             AND valor<? AND ts>? AND ts<=? ORDER BY ts LIMIT 1""",
        (run, interno, hihi, t_amostra, trip["ts"] if trip else ts)).fetchone()
    if trip:
        atendido, nota = False, ("the next layer (SIS trip) was reached after the demand: "
                                 "pressure did not revert before it")
    elif reverteu:
        atendido, nota = True, f"pressure fell back below HIHI at {reverteu['ts']}"
    else:
        atendido, nota = None, "still escalating at t_now; outcome not yet determined"

    out["B1"] = {
        "barreira": "B1", "demandada": True,
        "gatilho_declarado": DESIGN_BASIS["barreiras"]["B1"]["gatilho"],
        "fonte_gatilho": "design basis, section 4",
        "instantes": {"primeira_amostra_acima_hihi": t_amostra, "alarme_hihi": t_alarme,
                      "evento_de_logica": eventos_b1[0]["ts"] if eventos_b1 else None,
                      "ancora": ancora},
        "detectar": {"canais_na_demanda": canais, "limiar_hihi": hihi,
                     "canais_acima": acima, "voto_2oo3_satisfeito": len(acima) >= 2,
                     "fonte": f"series per channel at {t_amostra}"},
        "decidir": {"eventos_registrados": eventos_b1,
                    "ordens_abertas_na_demanda": [{"wo_id": w["wo_id"], "item": w["equipamento_id"],
                                                   "descricao": w["descricao"]} for w in ordens]},
        "agir": {"janela": f"5 min before vs after {ancora}", "banda_morta_pp": BANDA_MORTA_PP,
                 "sinais": sinais,
                 "algum_como_esperado": any(s_["como_esperado"] for s_ in sinais) if sinais else None},
        "desfecho": {"criterio": DESIGN_BASIS["desempenho"]["criterio_sucesso"],
                     "fonte_criterio": "design basis, section 5",
                     "proxima_camada": {"nome": "SIS trip", "valor": trip_v,
                                        "fonte": "alarm_config.trip_sis"},
                     "proxima_camada_atingida_em": trip["ts"] if trip else None,
                     "minutos_da_demanda_ao_trip": (round((_dt(trip["ts"]) - _dt(ancora))
                                                          .total_seconds() / 60, 1) if trip else None),
                     "criterio_atendido": atendido, "nota": nota},
    }

    comando = next((e["detalhe"].get("saidas_comandadas") for e in eventos_b1
                    if "saidas_comandadas" in e["detalhe"]), None)
    out["B2"] = {
        "barreira": "B2",
        "gatilho_declarado": DESIGN_BASIS["barreiras"]["B2"]["gatilho"],
        "fonte_gatilho": "design basis, section 4",
        "sinal_de_posicao_ZT-1001": {"presente": "ZT-1001" in bf.REVERSE,
                                     "nota": "not in ativos nor in series"},
        "comando_registrado_na_demanda_de_B1": comando,
        "fonte_comando": ("process_events " + eventos_b1[0]["tipo"] + " at "
                          + eventos_b1[0]["ts"]) if eventos_b1 else None,
    }

    if trip:
        pos = next((d for d in (a2.get("escada_de_taxas") or {}).get("degraus", [])
                    if d["janela"].startswith("after the SIS")), None)
        out["SIS"] = {"camada": "SIS trip", "limiar": trip_v, "fonte_limiar": "alarm_config.trip_sis",
                      "atuou_em": trip["ts"], "detalhe": trip["detalhe"],
                      "taxa_depois_kpa_min": pos["taxa"] if pos else None,
                      "nota": "a layer beyond the bowtie's preventive barriers; it is not B1"}
    return out


# ───────────────────────────────────────────── voted group characterisation
#
# The last report called channel B "divergent" and stopped. The series showed
# more: B sat inside a 1.4 kPa band from late August while A and C moved across
# 10 kPa, and the value it sat at is the pre-change regime. A divergence and a
# freeze are different failure modes, and only the second is told apart by the
# channel's own variance.

def _std(xs: list[float]) -> float:
    return statistics.pstdev(xs) if len(xs) > 1 else 0.0


def caracterizar_grupo_votado(con, run: str, ts: str, desde: str, regime: dict) -> dict:
    tag = "PIT-7001"
    interno = bf.REVERSE[tag]
    ruido = DESIGN_BASIS["escada_protecao"]["ruido_kpa"]
    serie = {k: [(r["ts"], r["valor"]) for r in con.execute(
        """SELECT ts, valor FROM series WHERE run_id=? AND tag=? AND canal=?
             AND ts BETWEEN ? AND ? ORDER BY ts""", (run, interno, k, desde, ts))]
        for k in "ABC"}
    if not all(serie.values()):
        return {"tag": tag, "lacuna": "no per-channel series in the window"}
    est = {k: {"n": len(v), "media": round(statistics.mean(x for _, x in v), 2),
               "desvio": round(_std([x for _, x in v]), 2),
               "min": round(min(x for _, x in v), 2), "max": round(max(x for _, x in v), 2),
               "ultimo": round(v[-1][1], 2)} for k, v in serie.items()}

    parados = []
    for k in "ABC":
        outros = [est[o]["desvio"] for o in "ABC" if o != k]
        ref = statistics.median(outros)
        if ref > ruido and est[k]["desvio"] < 0.25 * ref:
            parados.append(k)

    ultimos = {k: est[k]["ultimo"] for k in "ABC"}
    tol = round(3 * ruido, 2)
    concordam = [(a, b) for a, b in (("A", "B"), ("A", "C"), ("B", "C"))
                 if abs(ultimos[a] - ultimos[b]) <= tol]
    outlier = None
    if len(concordam) == 1:
        par = set(concordam[0])
        outlier = next(k for k in "ABC" if k not in par)

    congelado = None
    if len(parados) == 1:
        k = parados[0]
        completo = [(r["ts"], r["valor"]) for r in con.execute(
            """SELECT ts, valor FROM series WHERE run_id=? AND tag=? AND canal=?
                 AND ts<=? ORDER BY ts""", (run, interno, k, ts))]
        m = est[k]["media"]
        banda = max(3 * est[k]["desvio"], 1.5)
        inicio = completo[-1][0]
        for t_, v in reversed(completo):
            if abs(v - m) > banda:
                break
            inicio = t_
        antes = (regime or {}).get("regime_antes") or {}
        congelado = {
            "canal": k, "valor_medio": m, "banda_kpa": round(banda, 2),
            "parado_desde_aprox": inicio,
            "regime_de_referencia": antes.get("mediana"),
            "fonte_regime": (f"median voted {tag} {antes.get('de')} → {antes.get('ate')}"
                             if antes else None),
            "diferenca_para_o_regime": (round(m - antes["mediana"], 2)
                                        if antes.get("mediana") else None),
            "nota": "computed from the series; the start is the first sample of the "
                    "final stretch inside the band, not a recorded failure time",
        }

    return {
        "tag": tag, "janela": {"de": desde, "ate": ts},
        "estatistica_por_canal": est, "ruido_de_projeto_kpa": ruido,
        "canais_parados": parados,
        "concordancia_no_ultimo_instante": {"tolerancia_kpa": tol, "pares": concordam,
                                            "divergente_pela_maioria": outlier},
        "congelamento": congelado,
    }


# ──────────────────────────────────────────── regime and precursor alarms
#
# The pressure regime fell by about 150 kPa after the 28 Nov operating-condition change,
# with LO alarms on three days. Those alarms were in the database and never
# reached the last analysis. The change is also what made the frozen channel
# visible: sitting at the old regime value, it is indistinguishable from A and C
# until the regime moves away from it.

def regime_e_precursores(con, run: str, ts: str, eventos: list[dict]) -> dict:
    tag = "PIT-7001"
    interno = bf.REVERSE[tag]
    moc = [e for e in eventos if e["tipo"] == MOC and e["ts"] <= ts]
    if not moc:
        return {"mudanca": None, "nota": "no operating-condition change up to t_now"}
    t_moc = moc[-1]["ts"]
    origem = bf.origem_do_horizonte(con, run)
    fim_depois = ts[:10] + "T00:00:00" if ts[:10] > t_moc[:10] else ts

    def _reg(a, b):
        xs = [r[0] for r in con.execute(
            """SELECT valor FROM series WHERE run_id=? AND tag=? AND canal='voted'
                 AND ts>=? AND ts<? ORDER BY ts""", (run, interno, a, b))]
        if not xs:
            return None
        return {"de": a, "ate": b, "n": len(xs), "mediana": round(statistics.median(xs), 2),
                "min": round(min(xs), 2), "max": round(max(xs), 2)}

    antes, depois = _reg(origem, t_moc), _reg(t_moc, fim_depois)
    alarmes = [{"tipo": r["tipo"], "ts_inicio": r["ts_inicio"],
                "ts_fim": (r["ts_fim"] if r["ts_fim"] and r["ts_fim"] <= ts else None),
                "valor_pico": r["valor_pico"]}
               for r in bf.alarmes_visiveis(con, run, ts)
               if r["tag"] == tag and t_moc <= r["ts_inicio"] < fim_depois]
    return {
        "mudanca": moc[-1], "regime_antes": antes, "regime_depois": depois,
        "deslocamento_kpa": (round(depois["mediana"] - antes["mediana"], 2)
                             if antes and depois else None),
        "alarmes_entre_a_mudanca_e_o_episodio": alarmes,
        "revalidacao_registrada": False,
        "nota": "regime medians are computed from the voted series; alarms are read "
                "from alarm_events between the change and the start of the current day",
    }


# ─────────────────────────────────────────────────── top event, both engines
#
# The last run wrote the engines' output into meta.json from the DESIGN diagram
# and the analysis then declared the top event frequency "not computed". Both
# errors had the same root: nobody fed the current PFDs to the engines. Phase A
# now evaluates design and current, with both engines, and hands the pair over.

DIAGRAMA = ROOT / "diagrams" / "BT-REATOR.txt"


def motores(con, run: str, ts: str) -> dict:
    import tomllib
    from .bridge import _import_bowtie
    cfg = tomllib.loads((ROOT / "config.toml").read_text())
    Diagram, engines = _import_bowtie(ROOT / cfg["bowtie"]["path"])
    t_exp = float(cfg["bowtie"].get("time", 1.0))
    atual = {b: bf.pfd_barreira(con, run, ts, b)["pfd"] for b in ("B1", "B2", "B3", "B4")}

    def _avaliar(nome_engine: str, pfds: dict | None) -> dict:
        d = Diagram.from_v1_txt(str(DIAGRAMA))
        if pfds:
            for n, node in d.nodes.items():
                bid = n.split()[0]
                if bid in pfds:
                    node.frequency, node.mttf = pfds[bid], 0.0
        r = engines[nome_engine]().calculate(d, t_exp)
        return {"evento_topo_por_ano": float(r.top_event_frequency), "rotulo": r.linguistic,
                "pathways": [{"nos": list(p.nodes), "contribuicao_pct": round(float(p.contribution_pct), 1)}
                             for p in r.preventive_pathways]}

    out = {"diagrama": "diagrams/BT-REATOR.txt", "janela_de_exposicao_anos": t_exp,
           "pfd_atual": {k: round(v, 6) for k, v in atual.items()}}
    for eng in ("conventional", "fuzzy"):
        proj, cur = _avaliar(eng, None), _avaliar(eng, atual)
        out[eng] = {"projeto": proj, "atual": cur,
                    "razao": (round(cur["evento_topo_por_ano"] / proj["evento_topo_por_ano"], 2)
                              if proj["evento_topo_por_ano"] else None)}
    out["nota"] = ("conventional engine for magnitude; fuzzy engine for the propagation of "
                   "linguistic uncertainty (SKILL.md, 'The fuzzy engine'). Never one as a "
                   "check on the other.")
    return out


def estado_atual(con, run: str, ts: str, lims: list[dict]) -> dict:
    """A2 da skill: o que esta em falha, alarmes ativos com taxa, WOs por classe."""
    ctx = bf.context(con, run, ts)
    ativos_alarme = [a for a in ctx["alarmes"] if a["ts_fim"] is None]
    tx = taxas(con, run, ts)
    for a in ativos_alarme:
        a["ativo_ha_min"] = round((_dt(ts) - _dt(a["ts_inicio"])).total_seconds() / 60.0, 1)
        a["taxa"] = tx.get(a["tag"])

    wos = ctx["ordens_servico"]
    def _classe(w):
        if w["data_fechamento"]:
            return "closed_with_finding" if w["falha_encontrada"] else "closed"
        if w["vencimento"] and w["vencimento"] <= ts:
            return "overdue_not_executed"
        return "open"
    for w in wos:
        w["classe"] = _classe(w)
        if w["classe"] == "overdue_not_executed":
            w["vencida_ha_dias"] = (_dt(ts) - _dt(w["vencimento"])).days

    return {
        "contradicoes": contradicoes(con, run, ts, wos),
        "alarmes_ativos": ativos_alarme,
        "alarmes_normalizados": [a for a in ctx["alarmes"] if a["ts_fim"]],
        "taxas": tx,
        "canais": ctx["canais_sensor"],
        "discrepancia_canais": discrepancia_canais(con, run, ts, lims),
        "ordens_servico": wos,
        "eventos_operacionais": ctx["eventos_operacionais"],
        "regra_de_recuperacao": {
            "alarms": "alarm_events with ts_inicio <= t_now; future ts_fim nulled; active peaks from voted series through t_now",
            "work orders": "work_orders with data_abertura <= t_now; future closure, final narrative and findings omitted",
            "channels": "blind_feed.canais_visiveis — a failure undetected by t_now is masked",
            "reliability": "blind_feed.pfd_confiabilidade — only failures known by t_now enter the PFD",
            "events": "process_events with visivel_copiloto=1 and ts <= t_now",
        },
    }


# ─────────────────────────────────────────────────────────── A1: barreiras

def barreiras(con, run: str, ts: str) -> list[dict]:
    """A1 + o par de multiplicadores de C2, por barreira do bowtie."""
    comp = bf.componentes(con)
    out = []
    for bid in ("B1", "B2"):                      # pathway de pressao (RUN_A/B)
        b = bf.pfd_barreira(con, run, ts, bid)
        dominante = max(b["componentes"], key=lambda c: c["pfd"]) if b["componentes"] else None
        pior = max(b["componentes"], key=lambda c: c["fator"]) if b["componentes"] else None
        out.append({
            "id": bid, "nome": b["nome"], "pathway": "T1",
            "componentes": comp.get(bid, []),
            "pfd_projeto": _leitura(b["pfd_projeto"], "sum of the components' pfd_projeto (ativos)"),
            "pfd_atual": _calculo(b["pfd"], "sum of component PFDs",
                                  "blind_feed.pfd_confiabilidade per asset"),
            "pfd_documento": _leitura(b["pfd_documento"], "loop PFD from the bowtie document"),
            "c2": {
                "multiplicador_barreira": b["degradacao"],
                "componente_pior": pior and {"item": pior["item"], "multiplicador": pior["fator"]},
                "elemento_dominante": dominante and {
                    "item": dominante["item"], "pfd": dominante["pfd"],
                    "fracao_do_total": round(dominante["pfd"] / b["pfd"], 3) if b["pfd"] else None},
            },
            "detalhe_componentes": b["componentes"],
            "motivos": b["motivos"],
        })
    return out


# ─────────────────────────────────────────────────── A3: os oito cruzamentos

def cruzamentos(ctx_a1: list[dict], a2: dict, ts: str) -> list[dict]:
    """Exactly eight, in order C1..C8. None produces judgement."""
    C = []
    esc = a2.get("escada_de_taxas") or {}
    disp = esc.get("dispersao") or {}
    dem = a2.get("demandas") or {}
    gv = a2.get("grupo_votado") or {}
    reg = a2.get("regime") or {}
    dbb, desemp = DESIGN_BASIS["barreiras"], DESIGN_BASIS["desempenho"]

    # C1 — envelope
    C.append({
        "id": "C1", "titulo": "Envelope: current versus validated dynamics",
        "comparado": {
            "rate_ladder": [{"window": d["janela"], "rate": d["taxa"], "span_min": d["span_min"],
                             "vs_design": d.get("razao_vs_projeto")} for d in esc.get("degraus", [])],
            "design_rate": (esc.get("referencia_de_projeto") or {}).get("taxa_kpa_min"),
            "invalidation_triggers": esc.get("gatilhos_de_invalidacao"),
            "regime_shift_kpa": reg.get("deslocamento_kpa"),
        },
        "resultado": (f"rate ranges {disp.get('minima')} to {disp.get('maxima')} kPa/min across "
                      f"windows ({disp.get('razao')}x); envelope "
                      f"{'invalidated' if esc.get('invalidada') else 'holds'}"
                      if disp else
                      (f"no escalation window at t_now; operating-condition change at "
                       f"{reg['mudanca']['ts']} shifted the pressure regime by "
                       f"{reg.get('deslocamento_kpa')} kPa with no revalidation recorded"
                       if reg.get("mudanca") else "no escalation window at t_now")),
        "lacuna": None, "nao_se_aplica": None,
    })

    # C2 — PFD decomposition
    C.append({
        "id": "C2", "titulo": "PFD decomposition: component versus barrier",
        "comparado": {b["id"]: {"barrier_multiplier": b["c2"]["multiplicador_barreira"],
                                "worst_component": b["c2"]["componente_pior"],
                                "dominant_element": b["c2"]["elemento_dominante"]}
                      for b in ctx_a1},
        "resultado": "both multipliers reported per barrier",
        "lacuna": None, "nao_se_aplica": None,
    })

    # C3 — window compression, measured from B1's OWN demand to the SIS trip
    b1 = dem.get("B1") or {}
    janela_real = (b1.get("desfecho") or {}).get("minutos_da_demanda_ao_trip")
    jp = desemp["janela_hihi_sis_min"]
    comp_ = round(jp / janela_real, 1) if janela_real else None
    C.append({
        "id": "C3", "titulo": "Barrier class under window compression",
        "comparado": {"hihi_to_sis_window": {"design_min": jp, "measured_min": janela_real,
                                             "compression": comp_,
                                             "design_source": "design basis, section 5"},
                      "B1": {"class": dbb["B1"]["classe"], "time": dbb["B1"]["tempo_atuacao"]},
                      "B2": {"class": dbb["B2"]["classe"], "time": dbb["B2"]["tempo_atuacao"],
                             "tolerable_delay_min": desemp["atraso_tolerav_b2_min"]}},
        "resultado": (f"HIHI→SIS window {jp:.0f} min in design, {janela_real} min measured "
                      f"from B1's demand ({comp_}x). B1 is automatic (seconds); B2's design "
                      f"tolerable delay of {desemp['atraso_tolerav_b2_min']:.0f} min is "
                      f"{round(desemp['atraso_tolerav_b2_min']/janela_real,1)}x the whole "
                      "measured window"
                      if janela_real else "real window not measurable at t_now"),
        "lacuna": ("B2's design PFD was calibrated for the design window; under the measured "
                   "window the number survives and its meaning does not" if janela_real else None),
        "nao_se_aplica": None if b1.get("demandada") else "no demand on B1 up to t_now",
    })

    # C4 — voted group: record, reading, failure mode, clock
    canais = a2["canais"]
    falhos = [c for c in canais if c["estado"] == "failed_detected_unrepaired"]
    disc = [d for d in a2["discrepancia_canais"] if d["acima_do_limite"]]
    cong = gv.get("congelamento")
    C.append({
        "id": "C4", "titulo": "State and observability of redundant groups",
        "comparado": {"declared_arrangement": "2oo3 (PT-007)",
                      "record": {c["channel_id"]: c["estado"] for c in canais},
                      "reading_spread": [{"tag": d["tag"], "spread": d["spread"]["valor"],
                                          "limit": d["limite"]["valor"]} for d in disc],
                      "flat_channels": gv.get("canais_parados"),
                      "majority_outlier": (gv.get("concordancia_no_ultimo_instante") or {})
                                          .get("divergente_pela_maioria")},
        "resultado": ("known degraded: "
                      + ", ".join(f"{c['channel_id']} failure detected {c['ts_deteccao']} "
                                  f"({c['wo_id']}, not repaired)" for c in falhos)
                      + (f"; channel {cong['canal']} flat at {cong['valor_medio']} kPa since "
                         f"about {cong['parado_desde_aprox']}" if cong else "")
                      if falhos else
                      ("hidden degraded: reading diverges from a record that reports no "
                       "discrepancy" if disc else "intact by record and reading")),
        "relogio": ("repair backlog: "
                    + ", ".join(f"{(_dt(ts) - _dt(c['ts_deteccao'])).days} d since detection "
                                f"of {c['channel_id']}" for c in falhos)
                    if falhos else "test interval"),
        "lacuna": None, "nao_se_aplica": None,
    })

    # C5 — decidability gaps
    lac = []
    conc = gv.get("concordancia_no_ultimo_instante") or {}
    if disc:
        if conc.get("divergente_pela_maioria"):
            par = next(iter(conc.get("pares") or []), ("?", "?"))
            lac.append({
                "pergunta": f"Is there a common cause affecting channels {par[0]} and {par[1]}?",
                "por_que_nao_responde": (
                    f"{par[0]} and {par[1]} agree within {conc['tolerancia_kpa']} kPa and "
                    f"{conc['divergente_pela_maioria']} diverges, so the majority identifies the "
                    "divergent channel; what the group cannot rule out is a shared error in the "
                    "agreeing pair"),
                "verificacao_externa": "an independent field measurement of vessel pressure",
            })
        else:
            lac.append({
                "pergunta": "Which of the voted channels is correct?",
                "por_que_nao_responde": "no two channels agree within tolerance",
                "verificacao_externa": "an independent field measurement of vessel pressure",
            })
    sis = dem.get("SIS")
    pit = a2["margem"].get("PIT-7001") or {}
    if sis:
        lim = next((a for a in pit.get("alvos_declarados", []) if a["nome"].startswith("model")),
                   None)
        lac.append({
            "pergunta": "Which layer arrests the escalation downstream of the SIS?",
            # At the trip instant itself the rate after is not measurable yet.
            "por_que_nao_responde": (
                f"the SIS acted at {sis['atuou_em']}; "
                + (f"pressure kept rising at {sis['taxa_depois_kpa_min']} kPa/min"
                   if sis.get("taxa_depois_kpa_min") is not None
                   else "the rate after it is not measurable at t_now")
                + (f"; the design basis puts the model physical limit at {lim['valor']:.0f} kPa"
                   if lim else "")
                + " and declares no layer between the SIS and that limit"),
            "verificacao_externa": "confirm whether pressure relief exists downstream of the "
                                   "SIS, and the vessel design pressure",
        })
    b2 = dem.get("B2")
    if b2 and not b2["sinal_de_posicao_ZT-1001"]["presente"]:
        lac.append({
            "pergunta": "Was B2 ever demanded?",
            "por_que_nao_responde": (
                "B2's declared trigger is a command-versus-position discrepancy on ZT-1001, "
                "and ZT-1001 is in neither ativos nor series"
                + (f"; the record at B1's demand says outputs commanded = "
                   f"{b2['comando_registrado_na_demanda_de_B1']}"
                   if b2.get("comando_registrado_na_demanda_de_B1") is not None else "")),
            "verificacao_externa": "instrument feed valve position, or the control room record",
        })
    if b1.get("demandada") and not (b1.get("decidir") or {}).get("eventos_registrados"):
        lac.append({
            "pergunta": "Did B1's logic command its final element?",
            "por_que_nao_responde": "no record of the logic output at the demand",
            "verificacao_externa": "the logic solver's event log",
        })
    C.append({"id": "C5", "titulo": "Decidability gap", "comparado": None,
              "resultado": f"{len(lac)} named gap(s)", "lacunas": lac,
              "lacuna": None, "nao_se_aplica": None})

    # C6 — side effect
    compartilhados: dict = {}
    for b in ctx_a1:
        for item in b["componentes"]:
            compartilhados.setdefault(item, []).append(b["id"])
    ind = DESIGN_BASIS["independencia"]
    C.append({
        "id": "C6", "titulo": "Side effect of the barrier action",
        "comparado": {"shared_items": {k: v for k, v in compartilhados.items() if len(v) > 1},
                      "declared_independence": ind,
                      "declared_side_effect": dbb["B1"]["efeito_colateral"]},
        "resultado": (f"detection {ind['deteccao']}; actuation {ind['atuacao']}. "
                      f"{ind['consequencia']}. Declared side effect of B1's action: "
                      + dbb["B1"]["efeito_colateral"]),
        "lacuna": None, "nao_se_aplica": None,
    })

    # C7 — distance and rate
    C.append({"id": "C7", "titulo": "Static indicator versus dynamic margin",
              "comparado": a2.get("margem", {}),
              "resultado": "distance and rate side by side against every declared target",
              "lacuna": None, "nao_se_aplica": None})

    # C8 — threat
    C.append({"id": "C8", "titulo": "Persistent versus removable threat",
              "comparado": {"feed_flow": a2["margem"].get("FIT-1001"),
                            "rate": a2["taxas"].get("FIT-1001")},
              "resultado": "classification requires the threat-removal test",
              "lacuna": "The removal test (design basis, section 6) was not executed for "
                        "this bowtie.",
              "nao_se_aplica": None})
    return C


def margens(con, run: str, ts: str, lims: list[dict], a2: dict) -> dict:
    """C7: distance AND rate, side by side, against every declared target."""
    snap = bf.snapshot(con, run, ts)["tags"]
    out = {}
    for l in lims:
        key = f"{bf.PREFIX}{l['tag'].replace('-', '_')}"
        v = snap.get(key)
        if v is None:
            continue
        tx = (a2["taxas"].get(l["tag"]) or {}).get("valor")
        cruzados = [(n, l[n], round(v - l[n], 2)) for n in ("hi", "hihi")
                    if l.get(n) is not None and v >= l[n]]
        cruzados += [(n, l[n], round(v - l[n], 2)) for n in ("lo", "lolo")
                     if l.get(n) is not None and v <= l[n]]
        alvo, nome = None, None
        for n in (("hi", "hihi") if (tx or 0) >= 0 else ("lo", "lolo")):
            if l.get(n) is None:
                continue
            if (v < l[n]) if n in ("hi", "hihi") else (v > l[n]):
                alvo, nome = l[n], n
                break
        dist = round(abs(alvo - v), 2) if alvo is not None else None
        t_lim = None
        if dist is not None and tx and (alvo - v) * tx > 0:
            cand = dist / abs(tx)
            t_lim = round(cand, 1) if cand <= 1440 else None

        alvos = []
        if l.get("trip_sis") is not None:
            alvos.append(("SIS trip", l["trip_sis"], "alarm_config.trip_sis"))
        if l["tag"] == "PIT-7001":
            esc_p = DESIGN_BASIS["escada_protecao"]
            alvos.append(("model physical limit", esc_p["limite_fisico"],
                          "design basis, section " + esc_p["secao"]))
        alvos_declarados = []
        for nome_a, alvo_v, fonte in alvos:
            d_ = round(alvo_v - v, 2)
            alvos_declarados.append({
                "nome": nome_a, "valor": alvo_v, "distancia": d_, "ja_cruzado": d_ <= 0,
                "tempo_min": round(d_ / tx, 1) if tx and tx > 0 and d_ > 0 else None,
                "fonte": fonte})
        out[l["tag"]] = {
            "valor": v, "unidade": l["unidade"], "alvos_declarados": alvos_declarados,
            "limiar_a_frente": {"nome": nome, "valor": alvo}, "distancia": dist,
            "limiares_ja_cruzados": [{"nome": n, "valor": val, "excedencia": exc}
                                     for n, val, exc in cruzados],
            "taxa_por_min": tx, "tempo_ate_limiar_min": t_lim,
            "nota": "time to a threshold is computed from the measured rate, not read; "
                    "suppressed beyond 24 h as rate noise",
        }
    return out


# ─────────────────────────────────────────────────────────────────── montar

def _janela(con, run: str, ts: str, alarmes_ativos: list[dict]) -> str:
    """Start of the window the analysis looks at: the day the current alarm
    episode began, or 30 days back when no alarm is active."""
    if alarmes_ativos:
        return min(a["ts_inicio"] for a in alarmes_ativos)[:10] + "T00:00:00"
    return max(bf.origem_do_horizonte(con, run),
               (_dt(ts) - timedelta(days=30)).isoformat())


def montar(run: str, ts: str | None = None, incident_id: str | None = None,
           gatilho: list | None = None) -> dict:
    """Phase A block, closed. No network, no LLM, no writes."""
    con = bf.connect()
    ts = ts or con.execute("SELECT MAX(ts) FROM series WHERE run_id=?", (run,)).fetchone()[0]
    lims = bf.limiares(con)
    a2 = estado_atual(con, run, ts, lims)
    a2["margem"] = margens(con, run, ts, lims, a2)
    esc = escada_de_taxas(con, run, ts, a2["eventos_operacionais"])
    a2["escada_de_taxas"] = esc
    desde = _janela(con, run, ts, a2["alarmes_ativos"])
    a2["regime"] = regime_e_precursores(con, run, ts, a2["eventos_operacionais"])
    # A caracterizacao do grupo votado olha pelo menos 30 dias: um canal parado
    # so se distingue pela variancia, e um dia de janela nao tem variancia.
    desde_gv = min(desde, max(bf.origem_do_horizonte(con, run),
                              (_dt(ts) - timedelta(days=30)).isoformat()))
    a2["grupo_votado"] = caracterizar_grupo_votado(con, run, ts, desde_gv, a2["regime"])
    a2["demandas"] = desfecho_das_demandas(con, run, ts, lims, a2)
    a1 = barreiras(con, run, ts)
    inc = incident_id or f"INC-BT-REATOR-{ts[:10].replace('-', '')}-1"
    return bf.scrub_obj({
        "identidade": {"incident_id": inc, "run": run, "ts": ts, "janela_de": desde,
                       "bowtie_id": "BT-REATOR", "pathway_avaliada": "T1",
                       "origem_do_horizonte": bf.origem_do_horizonte(con, run),
                       "banco": str(bf.DB.name), "gatilho": gatilho or []},
        "a1_base_de_projeto": {"barreiras": a1, "limiares": lims,
                               "base_de_projeto_declarada": True,
                               "documento": DESIGN_BASIS["documento"],
                               "declarado": DESIGN_BASIS, "lacuna": None},
        "a2_estado_atual": a2,
        "a3_cruzamentos": cruzamentos(a1, a2, ts),
        "envelope": esc,
        "motores": motores(con, run, ts),
        "premissas_do_modelo": bf.premissas_do_modelo(),
        "fase": "A — context assembled; no conclusion issued",
    })


# ──────────────────────────────────────────────────────────────── view md

def _f(x, casas=2):
    return "—" if x is None else (f"{x:.{casas}f}" if isinstance(x, float) else str(x))


def render_md(c: dict) -> str:
    i, a1, a2 = c["identidade"], c["a1_base_de_projeto"], c["a2_estado_atual"]
    esc, mot = c.get("envelope") or {}, c.get("motores") or {}
    L = [f"## Phase A context · {i['incident_id']}", "",
         f"`run={i['run']}` · `t_now={i['ts']}` · `window_from={i['janela_de']}` · "
         f"`bowtie={i['bowtie_id']}` · pathway `{i['pathway_avaliada']}` · database `{i['banco']}`",
         f"Horizon from {i['origem_do_horizonte']}. Design basis: `{a1['documento']}`.", ""]
    if i.get("gatilho"):
        L.append("**Trigger(s) that opened this analysis:** "
                 + "; ".join(f"`{g.get('chave', g)}`" for g in i["gatilho"]))
        L.append("")

    L += ["### Active alarms", ""]
    if a2["alarmes_ativos"]:
        L += ["| Tag | Type | Since | Active (min) | Peak | Demand | Rate /min |", "|---|---|---|---|---|---|---|"]
        for a in a2["alarmes_ativos"]:
            L.append(f"| {a['tag']} | {a['tipo']} | {a['ts_inicio']} | {a['ativo_ha_min']} | "
                     f"{a['valor_pico']} | {'yes' if a['e_demanda'] else 'no'} | "
                     f"{_f((a.get('taxa') or {}).get('valor'), 4)} |")
    else:
        L.append("None.")

    L += ["", "### Distance and rate, side by side (C7)", "",
          "| Tag | Value | Crossed | Next threshold | Distance | Rate /min | Declared targets |",
          "|---|---|---|---|---|---|---|"]
    for t, m in a2["margem"].items():
        cruz = ", ".join(f"{x['nome'].upper()} ({x['excedencia']:+g})" for x in m["limiares_ja_cruzados"]) or "—"
        alvos = "; ".join(f"{x['nome']} {x['valor']:g}: {x['distancia']:+g}"
                          + (f" ≈{x['tempo_min']} min" if x.get("tempo_min") else "")
                          + (" (crossed)" if x["ja_cruzado"] else "") + f" [{x['fonte']}]"
                          for x in m.get("alvos_declarados", [])) or "—"
        lf = m["limiar_a_frente"]
        L.append(f"| {t} | {m['valor']} {m['unidade']} | {cruz} | "
                 f"{(lf['nome'] or '—').upper()} {lf['valor'] or ''} | {_f(m['distancia'])} | "
                 f"{_f(m['taxa_por_min'], 4)} | {alvos} |")

    gv = a2.get("grupo_votado") or {}
    L += ["", "### Voted group PIT-7001 (C4)", ""]
    for c_ in a2["canais"]:
        L.append(f"- `{c_['channel_id']}` record: **{c_['estado']}**"
                 + (f", detected {c_['ts_deteccao']}" if c_.get("ts_deteccao") else "")
                 + (f", repaired {c_['ts_reparo']}" if c_.get("ts_reparo") else "")
                 + (f" ({c_['wo_id']})" if c_.get("wo_id") else ""))
    for d in a2["discrepancia_canais"]:
        L.append(f"- reading at t_now: {d['canais']} · spread **{d['spread']['valor']}** kPa "
                 f"against a limit of {d['limite']['valor']} ({d['limite']['fonte']}) · "
                 f"deviation from median {d['desvio_contra_mediana']}")
    if gv.get("estatistica_por_canal"):
        L.append(f"- per-channel statistics over {gv['janela']['de']} → {gv['janela']['ate']} "
                 f"(computed): " + "; ".join(f"{k} mean {v['media']} sd {v['desvio']} "
                                             f"range {v['min']}–{v['max']}"
                                             for k, v in gv["estatistica_por_canal"].items()))
        cc = gv["concordancia_no_ultimo_instante"]
        L.append(f"- agreement at t_now within {cc['tolerancia_kpa']} kPa (3× design noise "
                 f"{gv['ruido_de_projeto_kpa']} kPa, design basis §3): pairs {cc['pares']}; "
                 f"divergent by majority: {cc['divergente_pela_maioria']}")
        if gv.get("congelamento"):
            g = gv["congelamento"]
            L.append(f"- flat channel (computed): **{g['canal']}** at {g['valor_medio']} kPa "
                     f"(band ±{g['banda_kpa']}) since about {g['parado_desde_aprox']}; "
                     f"reference regime {g['regime_de_referencia']} kPa ({g['fonte_regime']}); "
                     f"difference {g['diferenca_para_o_regime']} kPa. {g['nota']}")

    dem = a2.get("demandas") or {}
    if dem:
        L += ["", "### Demand outcome per barrier (anchored on each barrier's own demand)", ""]
        b1 = dem.get("B1") or {}
        if b1.get("demandada"):
            ins, det, dec, act, out = b1["instantes"], b1["detectar"], b1["decidir"], b1["agir"], b1["desfecho"]
            L.append(f"- **B1** declared trigger: {b1['gatilho_declarado']} ({b1['fonte_gatilho']}). "
                     f"First sample ≥ HIHI {ins['primeira_amostra_acima_hihi']}; HIHI alarm "
                     f"{ins['alarme_hihi']}; logic event {ins['evento_de_logica']}; anchor {ins['ancora']}.")
            L.append(f"  - detect: channels at demand {det['canais_na_demanda']}, HIHI {det['limiar_hihi']}, "
                     f"above: {det['canais_acima']} → 2oo3 vote satisfied: **{det['voto_2oo3_satisfeito']}** ({det['fonte']})")
            for e in dec["eventos_registrados"]:
                L.append(f"  - decide: `{e['ts']}` **{e['tipo']}** {json.dumps(e['detalhe'], ensure_ascii=False)}")
            for w in dec["ordens_abertas_na_demanda"]:
                L.append(f"  - decide: work order {w['wo_id']} on {w['item']}: \"{w['descricao']}\"")
            if act["sinais"]:
                L.append(f"  - act ({act['janela']}, deadband {act['banda_morta_pp']} pp): "
                         + "; ".join(f"{s_['tag']} ({s_.get('descricao') or 'no description'}) expected "
                                     f"{s_['esperado']}, Δ {s_['delta']:+g} "
                                     f"({'as expected' if s_['como_esperado'] else 'not as expected'})"
                                     for s_ in act["sinais"]))
            L.append(f"  - outcome: criterion \"{out['criterio']}\" ({out['fonte_criterio']}); next layer "
                     f"{out['proxima_camada']['nome']} {out['proxima_camada']['valor']} "
                     f"[{out['proxima_camada']['fonte']}] "
                     + (f"reached at {out['proxima_camada_atingida_em']} "
                        f"({out['minutos_da_demanda_ao_trip']} min after the anchor)"
                        if out['proxima_camada_atingida_em'] else "not reached by t_now")
                     + " → criterion met: "
                     + (f"**{out['criterio_atendido']}**" if out['criterio_atendido'] is not None
                        else "**not yet determined**") + f". {out['nota']}")
        else:
            L.append(f"- **B1**: {b1.get('nota', 'not demanded')}")
        b2 = dem.get("B2")
        if b2:
            L.append(f"- **B2** declared trigger: {b2['gatilho_declarado']} ({b2['fonte_gatilho']}); "
                     f"ZT-1001 present: {b2['sinal_de_posicao_ZT-1001']['presente']}; "
                     f"outputs commanded at B1's demand: {b2['comando_registrado_na_demanda_de_B1']} "
                     f"({b2['fonte_comando']})")
        if dem.get("SIS"):
            s_ = dem["SIS"]
            L.append(f"- **SIS** (not a bowtie barrier of T1): tripped {s_['atuou_em']} at "
                     f"{s_['limiar']} kPa [{s_['fonte_limiar']}]; rate after: "
                     + (f"{s_['taxa_depois_kpa_min']} kPa/min" if s_['taxa_depois_kpa_min'] is not None
                        else "not measurable at t_now") + f". {s_['nota']}")

    reg = a2.get("regime") or {}
    if reg.get("mudanca"):
        L += ["", "### Regime and precursors since the last operating-condition change", ""]
        L.append(f"- `{reg['mudanca']['ts']}` **{reg['mudanca']['tipo']}** {reg['mudanca']['detalhe']}")
        for k, lab in (("regime_antes", "before"), ("regime_depois", "after")):
            r_ = reg.get(k)
            if r_:
                L.append(f"- voted PIT-7001 {lab}: median {r_['mediana']} kPa, range "
                         f"{r_['min']}–{r_['max']} ({r_['de']} → {r_['ate']}, n={r_['n']}) (computed)")
        L.append(f"- regime shift: {reg.get('deslocamento_kpa')} kPa; revalidation recorded: "
                 f"{reg.get('revalidacao_registrada')}")
        for a in reg.get("alarmes_entre_a_mudanca_e_o_episodio", []):
            L.append(f"- alarm PIT-7001 {a['tipo']} {a['ts_inicio']} → {a['ts_fim']}, peak {a['valor_pico']}")

    L += ["", "### Work orders", "", "| WO | Type | Item | Class | Opened | Due | Overdue (d) | Description |",
          "|---|---|---|---|---|---|---|---|"]
    for w in a2["ordens_servico"]:
        L.append(f"| {w['wo_id']} | {w['tipo']} | {w['equipamento_id']} | {w['classe']} | "
                 f"{w['data_abertura']} | {(w['vencimento'] or '—')} | {w.get('vencida_ha_dias', '—')} | "
                 f"{w['descricao']} |")

    if a2["eventos_operacionais"]:
        L += ["", "### Visible operational events", ""]
        for e in a2["eventos_operacionais"]:
            L.append(f"- `{e['ts']}` **{e['tipo']}** — {e['detalhe']}")

    L += ["", "### Barriers (A1 + C2)", "",
          "| Barrier | Design PFD | Current PFD | Barrier × | Worst component | Dominant element |",
          "|---|---|---|---|---|---|"]
    for b in a1["barreiras"]:
        c2 = b["c2"]; p_, d_ = c2["componente_pior"], c2["elemento_dominante"]
        L.append(f"| {b['nome']} | {b['pfd_projeto']['valor']:.3e} | {b['pfd_atual']['valor']:.3e} | "
                 f"**{c2['multiplicador_barreira']}×** | {p_['item']} {p_['multiplicador']}× | "
                 f"{d_['item']} ({d_['fracao_do_total']:.0%}) |")
    for b in a1["barreiras"]:
        for m in b["motivos"]:
            L.append(f"- {b['id']}: {m}")

    if mot:
        L += ["", "### Top event frequency, design versus current, both engines (computed)", "",
              "| Engine | Design /yr | Current /yr | Ratio | Label design → current | Pathway % current |",
              "|---|---|---|---|---|---|"]
        for eng in ("conventional", "fuzzy"):
            e = mot[eng]
            L.append(f"| {eng} | {e['projeto']['evento_topo_por_ano']:.3e} | "
                     f"{e['atual']['evento_topo_por_ano']:.3e} | {e['razao']}× | "
                     f"{e['projeto']['rotulo'] or '—'} → {e['atual']['rotulo'] or '—'} | "
                     f"{[p['contribuicao_pct'] for p in e['atual']['pathways']]} |")
        L.append(f"- current barrier PFDs fed to the engines: {mot['pfd_atual']}. {mot['nota']}")

    if a2["contradicoes"]:
        L += ["", "### Contradictions between sources (recorded, not resolved)", ""]
        for k in a2["contradicoes"]:
            s_ = k["sensibilidade"]
            L.append(f"- `{k['item']}` — {k['fonte_a']['o_que']}: \"{k['fonte_a']['diz']}\" "
                     f"**versus** {k['fonte_b']['o_que']}: \"{k['fonte_b']['diz']}\". Rule A: "
                     f"{k['fonte_a']['regra']}. Sensitivity (computed): last test implied by the "
                     f"calendar {s_['ultimo_teste_implicito']} ({s_['premissa']}); item PFD "
                     f"{s_['pfd_item_relogio_do_modelo']:.3e} by the model clock versus "
                     f"{s_['pfd_item_relogio_do_calendario']:.3e} by the calendar ({s_['razao_item']}×); "
                     f"per barrier {s_['por_barreira']}. {k['nao_resolvida']}")

    L += ["", "### Cross-checks", "", "| # | Result | Gap / not applicable |", "|---|---|---|"]
    for x in c["a3_cruzamentos"]:
        L.append(f"| {x['id']} {x['titulo']} | {x['resultado']} | "
                 f"{x.get('lacuna') or x.get('nao_se_aplica') or '—'} |")
    L += ["", "### Named gaps (C5)", ""]
    for x in c["a3_cruzamentos"]:
        for l in x.get("lacunas", []) or []:
            L.append(f"- **{l['pergunta']}** {l['por_que_nao_responde']}. External check: "
                     f"{l['verificacao_externa']}")
    if esc.get("degraus"):
        L += ["", "### Rate ladder PIT-7001 (computed)", "", "| Window | From → to | kPa/min | vs design | > 2.2 |",
              "|---|---|---|---|---|"]
        for d in esc["degraus"]:
            L.append(f"| {d['janela']} | {d['de']} → {d['ate']} | {d['taxa']} | {d.get('razao_vs_projeto')}× | "
                     f"{'yes' if d.get('excede_limite') else 'no'} |")
        for g in esc.get("gatilhos_de_invalidacao", []):
            L.append(f"- invalidation trigger (design basis §7) — {g['gatilho']}: "
                     f"{'OBSERVED' if g['observado'] else 'not observed'} ({g['evidencia']})")
    L += ["", "### Recovery rules", ""]
    for k, v in a2["regra_de_recuperacao"].items():
        L.append(f"- `{k}`: {v}")
    L += ["", "### Model assumptions (not asset data)", ""]
    for k, v in c["premissas_do_modelo"].items():
        L.append(f"- `{k}`: {v.get('valor', v.get('formula', ''))} — {v['efeito']}")
    return "\n".join(L) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(prog="python3 -m safety_copilot.contexto")
    ap.add_argument("--run", default="RUN_A")
    ap.add_argument("--at", default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    c = montar(a.run, a.at)
    txt = json.dumps(c, ensure_ascii=False, indent=2) if a.json else render_md(c)
    bf.scrub(txt)                     # falha alto se vazar procedencia
    print(txt)


if __name__ == "__main__":
    main()
