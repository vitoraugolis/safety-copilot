#!/usr/bin/env python3
"""Incident reporting — two views over one frozen context.

    report.html   the decision. Concise: what to do, which barriers moved, the
                  charts, the envelope verdict. What an operations reader needs.
    log.html      the audit chain. Identity and provenance, recovery rules,
                  every rate window, all eight crossings, gaps, contradictions
                  and model assumptions. What a reviewer needs to check the
                  report line by line.

Both read the same `contexto.json`; neither originates a number.

Original note kept for provenance:
Relatorio de ocorrencia — Fase A auditavel + Fase B do agente.

Forma: o molde `saida_RUN_A.html`. A folha de estilo vive em `relatorio_css.py`,
extraida do molde byte a byte.

Cadeia de informacao. Cada valor exibido carrega tres coisas: o valor, de onde
veio e como foi obtido. A convencao do molde:

    sem marca                          leitura direta do banco
    <span class="badge calc">          valor derivado de formula declarada
    <span class="badge warn">premissa  valor assumido pelo modelo, nao lido
    <span class="badge bad">ausente    campo que nao existe na fonte

Fonte da verdade dos numeros: `contexto.json` (Fase A). Do julgamento: o
markdown do agente (Fase B). O HTML compoe os dois e nao origina nenhum numero.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

from . import blind_feed as bf
from .relatorio_css import CSS


def _n(x, casas: int = 2) -> str:
    """Number in English notation, without invented precision.

    The skill forbids precision beyond the input data: 2923.1756 kPa on a
    pressure instrument is manufactured precision. Two decimals for process
    quantities; scientific notation stays as is, because PFD reads in decades.
    No thousands separator, so figures match the context fields verbatim.
    """
    if x is None:
        return "—"
    if isinstance(x, str):
        return x
    return f"{x:.{casas}f}"


def _e(x) -> str:
    return html.escape(str(x))


def _inl(s: str) -> str:
    s = _e(s)
    s = re.sub(r"`([^`]+)`", r"<code class='mono'>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    return s


def _md(t: str) -> str:
    """Markdown minimo -> HTML, nas classes do molde."""
    out, i, lines = [], 0, t.splitlines()
    while i < len(lines):
        l = lines[i]
        if re.match(r"^\|.*\|\s*$", l) and i + 1 < len(lines) \
                and re.match(r"^\|[\s:|-]+\|\s*$", lines[i + 1]):
            hdr = [c.strip() for c in l.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and re.match(r"^\|.*\|\s*$", lines[i]):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            out.append("<table><tr>" + "".join(f"<th>{_inl(c)}</th>" for c in hdr) + "</tr>"
                       + "".join("<tr>" + "".join(f"<td>{_inl(c)}</td>" for c in r) + "</tr>"
                                 for r in rows) + "</table>")
            continue
        m = re.match(r"^(#{2,4})\s+(.*)$", l)
        if m:
            out.append(f"<h3 class='s'>{_inl(m.group(2))}</h3>")
            i += 1
            continue
        if re.match(r"^#\s+", l):
            out.append(f"<h2 style='font-size:15px;margin:0 0 10px'>{_inl(l[2:])}</h2>")
            i += 1
            continue
        if re.match(r"^\s*[-*]\s+", l):
            # Um item de lista pode ocupar varias linhas no fonte. Sem absorver
            # a continuacao, um **negrito** que atravessa a quebra sai com os
            # asteriscos literais.
            itens = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                buf = [re.sub(r"^\s*[-*]\s+", "", lines[i])]
                i += 1
                while (i < len(lines) and lines[i].strip()
                       and not re.match(r"^(\s*[-*]\s|#{1,4}\s|\|)", lines[i])):
                    buf.append(lines[i].strip())
                    i += 1
                itens.append(f"<li>{_inl(' '.join(buf))}</li>")
            out.append("<ul class='tight'>" + "".join(itens) + "</ul>")
            continue
        if l.strip():
            buf = []
            while i < len(lines) and lines[i].strip() \
                    and not re.match(r"^(#{1,4}\s|\s*[-*]\s|\|)", lines[i]):
                buf.append(lines[i].strip())
                i += 1
            out.append(f"<p style='font-size:12.5px;line-height:1.6'>{_inl(' '.join(buf))}</p>")
            continue
        i += 1
    return "\n".join(out)


# ─────────────────────────────────────────────────────────────────── grafico

def _serie(run: str, tag: str, t0: str, t1: str, n: int = 700) -> list[float]:
    con = bf.connect()
    rows = con.execute(
        """SELECT valor FROM series WHERE run_id=? AND tag=?
             AND COALESCE(canal,'voted')='voted' AND ts BETWEEN ? AND ? ORDER BY ts""",
        (run, bf.REVERSE.get(tag, tag), t0, t1)).fetchall()
    step = max(1, len(rows) // n)
    return [r["valor"] for r in rows[::step]]


def _chart(v: list[float], lim: dict, marcos: list[dict] | None = None,
           W: int = 1000, H: int = 180) -> str:
    if not v:
        return "<p class='sub'>no sample in the window</p>"
    cand = [x for x in (lim.get("lolo"), lim.get("hihi"), lim.get("trip_sis"), min(v), max(v))
            if x is not None]
    lo, hi = min(cand), max(cand)
    folga = (hi - lo) * 0.08 or 1.0
    lo, hi = lo - folga, hi + folga
    pad = 6
    X = lambda i: pad + (i / max(1, len(v) - 1)) * (W - 2 * pad)
    Y = lambda y: H - pad - ((y - lo) / (hi - lo)) * (H - 2 * pad)

    p = []
    for a, b, cor in (("hi", "hihi", "#fbeaea"), ("hihi", None, "#f6d3d1"),
                      ("lo", "lolo", "#fbeaea"), ("lolo", None, "#f6d3d1")):
        va = lim.get(a)
        vb = lim.get(b) if b else (hi if a == "hihi" else lo)
        if va is None or vb is None:
            continue
        y0, y1 = sorted((Y(va), Y(vb)))
        p.append(f'<rect x="{pad}" width="{W-2*pad}" y="{y0:.1f}" '
                 f'height="{max(1,y1-y0):.1f}" fill="{cor}"/>')
    for k, cor in (("hi", "#b4790c"), ("hihi", "#b3261e"),
                   ("lo", "#b4790c"), ("lolo", "#b3261e")):
        if lim.get(k) is None:
            continue
        y = Y(lim[k])
        p.append(f'<line x1="{pad}" x2="{W-pad}" y1="{y:.1f}" y2="{y:.1f}" stroke="{cor}" '
                 f'stroke-width="1" stroke-dasharray="4 3" opacity=".75"/>'
                 f'<text x="{W-pad-4}" y="{y-3:.1f}" text-anchor="end" font-size="9" '
                 f'fill="{cor}">{k.upper()} {lim[k]:g}</text>')
    if lim.get("trip_sis") is not None:
        y = Y(lim["trip_sis"])
        p.append(f'<line x1="{pad}" x2="{W-pad}" y1="{y:.1f}" y2="{y:.1f}" stroke="#6d1414" '
                 f'stroke-width="1.4" opacity=".9"/>'
                 f'<text x="{W-pad-4}" y="{y-3:.1f}" text-anchor="end" font-size="9" '
                 f'fill="#6d1414">SIS TRIP {lim["trip_sis"]:g}</text>')
    for m in (marcos or []):
        x = X(int(m["frac"] * (len(v) - 1)))
        p.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{pad}" y2="{H-pad}" '
                 f'stroke="#5c5c5c" stroke-width="1" stroke-dasharray="2 3" opacity=".6"/>'
                 f'<text x="{x+3:.1f}" y="{pad+10}" font-size="9" fill="#5c5c5c">'
                 f'{_e(m["rotulo"])}</text>')
    d = " ".join(("M" if i == 0 else "L") + f"{X(i):.1f} {Y(x):.1f}"
                 for i, x in enumerate(v))
    return (f'<svg class="chart" viewBox="0 0 {W} {H}" preserveAspectRatio="none">'
            + "".join(p)
            + f'<path d="{d}" fill="none" stroke="#b3261e" stroke-width="2" '
              f'vector-effect="non-scaling-stroke"/>'
            + f'<circle cx="{X(len(v)-1):.1f}" cy="{Y(v[-1]):.1f}" r="3.5" fill="#b3261e"/>'
            + "</svg>")


# ──────────────────────────────────────────────────────────── shared chrome
def _head(title: str) -> str:
    return (f"<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            f"<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
            f"<title>{_e(title)}</title><style>{CSS}</style></head><body>")


def _banner(c: dict) -> str:
    """Safety limit first. It outranks any analytical conclusion."""
    a2 = c["a2_estado_atual"]
    dem = a2.get("demandas") or {}
    pit = a2["margem"].get("PIT-7001", {})
    limite = next((a for a in pit.get("alvos_declarados", [])
                   if a["nome"].startswith("model")), None)
    b1 = dem.get("B1") or {}
    sis = dem.get("SIS")
    if sis:
        txt = (f"<b>B1 was demanded at {_e(b1['instantes']['ancora'][11:])} and did not arrest "
               f"the excursion; the SIS tripped at {_e(sis['atuou_em'][11:])} and pressure kept "
               f"rising.</b> Last record {_n(pit.get('valor'))} kPa at "
               f"{_n(pit.get('taxa_por_min'))} kPa/min"
               + (f", {_n(limite['distancia'])} kPa below the declared physical limit of "
                  f"{limite['valor']:.0f} kPa — about <b>{limite['tempo_min']:.0f} min</b> at this "
                  "rate" if limite and limite.get("tempo_min") else "")
               + ". Apply the standing emergency procedures without waiting for this report.")
    elif b1.get("demandada"):
        txt = (f"<b>Active demand on B1 since {_e(b1['instantes']['ancora'][11:])}</b>; "
               "success criterion: " + ("not yet determined" if b1['desfecho']['criterio_atendido'] is None
                                        else f"met: {_e(b1['desfecho']['criterio_atendido'])}") + ".")
    else:
        ativos = [f"{a['tag']} {a['tipo']}" for a in a2["alarmes_ativos"]]
        txt = ("<b>No demand on a barrier</b> at the instant assessed"
               + (f"; active alarms: {_e(', '.join(ativos))}" if ativos else "") + ".")
    return f"<div class='banner'><span class='dot'></span><div>{txt}</div></div>"


def _hdr(c: dict, kind: str, sibling: str) -> str:
    i = c["identidade"]
    gat = ", ".join(g.get("chave", "") for g in i.get("gatilho") or []) or "—"
    return (f"<header><div><h1>{'Incident report' if kind == 'report' else 'Analysis log'}"
            f" · episode <code>{_e(i['run'])}</code></h1>"
            f"<p><code>{_e(i['incident_id'])}</code> · bowtie <code>{_e(i['bowtie_id'])}</code>"
            f" (pathway {_e(i['pathway_avaliada'])}) · <code>t_now {_e(i['ts'])}</code> · "
            f"trigger <code>{_e(gat)}</code> · "
            f"<a href='{sibling}' style='color:#fff'>{'audit log' if kind == 'report' else 'report'}</a>"
            f"</p></div>{_banner(c)}</header><main>")


def _marcos(c: dict, t0: str, ts: str) -> list[dict]:
    from datetime import datetime
    d = lambda t: datetime.fromisoformat(t)
    span = max(1.0, (d(ts) - d(t0)).total_seconds())
    dem = c["a2_estado_atual"].get("demandas") or {}
    out = []
    b1 = dem.get("B1") or {}
    if b1.get("demandada") and b1["instantes"]["ancora"] >= t0:
        out.append({"frac": (d(b1["instantes"]["ancora"]) - d(t0)).total_seconds() / span,
                    "rotulo": f"B1 demand {b1['instantes']['ancora'][11:16]}"})
    if dem.get("SIS") and dem["SIS"]["atuou_em"] >= t0:
        out.append({"frac": (d(dem["SIS"]["atuou_em"]) - d(t0)).total_seconds() / span,
                    "rotulo": f"SIS trip {dem['SIS']['atuou_em'][11:16]}"})
    return out


def _estado_barreira(b: dict, dem: dict) -> tuple[str, str]:
    """Colour class and label for the macro bowtie. A demanded barrier whose
    success criterion was not met is shown by its outcome, not by its PFD."""
    d = dem.get(b["id"]) or {}
    if d.get("demandada") and (d.get("desfecho") or {}).get("criterio_atendido") is False:
        return "bad", "demanded · criterion not met"
    m = b["c2"]["multiplicador_barreira"]
    return ("bad" if m >= 2.0 else "warn" if m > 1.05 else ""), f"{m}× design"


# ──────────────────────────────────────────────────────────────────── report

def _frontmatter(txt: str) -> tuple[str, str]:
    """Split the skill's YAML header off phase B: a compact line plus the body."""
    if not txt.startswith("---\n") or "\n---" not in txt[4:]:
        return "", txt
    cab, corpo = txt[4:].split("\n---", 1)
    campos = [l.split(":", 1) for l in cab.splitlines() if ":" in l]
    linha = " · ".join(f"<b>{_e(k.strip())}</b> {_e(v.strip())}" for k, v in campos)
    return f"<p class='sub'>{linha}</p>", corpo.lstrip("-\n")


def render_report(c: dict, phase_b: str | None, destino: Path,
                  timeline: list[dict] | None = None, meta: dict | None = None) -> Path:
    """The decision. Barrier impacts and charts; the audit apparatus is in the log."""
    i, a1, a2 = c["identidade"], c["a1_base_de_projeto"], c["a2_estado_atual"]
    env, mot = c.get("envelope") or {}, c.get("motores") or {}
    dem = a2.get("demandas") or {}
    gv = a2.get("grupo_votado") or {}
    lims = {l["tag"]: l for l in a1["limiares"]}
    ts, run, t0 = i["ts"], i["run"], i["janela_de"]
    P = [_head(f"Incident report · {i['incident_id']}"), _hdr(c, "report", "log.html")]
    add = P.append

    # Provenance comes from meta.json, never from a default: a phase B written
    # outside the sandbox must not be presented as the blind agent's.
    blind = bool((meta or {}).get("blind"))
    if phase_b and blind:
        add("<section class='card'><h2>Required decision "
            "<span class='badge n'>agent judgement · blind</span></h2>"
            "<p class='sub'>Single agent governed by <code>SKILL.md</code>, run blind in a "
            "sandbox. Figures are cited from the context fields, not retyped. The full chain "
            "is in the <a href='log.html'>audit log</a>.</p>"
            f"{''.join(_frontmatter(phase_b)[0:1])}{_md(_frontmatter(phase_b)[1])}</section>")
    elif phase_b:
        add("<section class='card'><h2>Required decision "
            "<span class='badge warn'>judgement · not blind</span></h2>"
            f"<p class='sub'>Written by {_e((meta or {}).get('phase_b_by') or 'an unrecorded author')}. "
            "It follows <code>SKILL.md</code> and cites the phase A fields, but its author had "
            "access to the project, so it is not evidence of blind performance. Phase A, in the "
            "<a href='log.html'>audit log</a>, is unaffected.</p>"
            f"{''.join(_frontmatter(phase_b)[0:1])}{_md(_frontmatter(phase_b)[1])}</section>")
    else:
        add("<section class='card'><h2>Required decision "
            "<span class='badge warn'>phase B pending</span></h2>"
            "<p class='sub'>Phase A is closed and shown below. The blind agent that writes "
            "phase B has not produced a text for this analysis.</p></section>")

    add("<div class='grid'><div>")

    # process variables
    add("<section class='card'><h2>Process variables</h2>"
        f"<p class='sub'>Window {_e(t0)} → {_e(ts)}. Shaded bands and dashed lines are the "
        "<code>alarm_config</code> thresholds; the solid line is the SIS trip "
        "(<code>alarm_config.trip_sis</code>). Every chart carries value and rate.</p>")
    marcos = _marcos(c, t0, ts)
    for tag in ("PIT-7001", "FIT-1001"):
        if tag not in lims:
            continue
        m = a2["margem"].get(tag, {})
        cruz = m.get("limiares_ja_cruzados") or []
        casas = 4 if tag == "FIT-1001" else 2
        add(f"<div class='chart-head'><span class='nm'>{_e(tag)} — {_e(lims[tag]['descricao'])} "
            f"<span class='badge {'bad' if cruz else 'ok'}'>{'anomaly' if cruz else 'normal'}</span>"
            f"</span><span class='vl'>{_n(m.get('valor'), casas)} {_e(lims[tag]['unidade'])}</span></div>"
            + _chart(_serie(run, tag, t0, ts), lims[tag], marcos if tag == "PIT-7001" else None)
            + "<div class='lg'><span><i style='background:#fbeaea'></i>alarm band</span>"
              f"<span>rate <b>{_n(m.get('taxa_por_min'), casas)}</b> {_e(lims[tag]['unidade'])}/min "
              "<span class='badge calc'>computed</span></span>"
            + ("<span>already crossed <b>" + ", ".join(x["nome"].upper() for x in cruz) + "</b></span>"
               if cruz else "") + "</div>")
        for alvo in m.get("alvos_declarados", []):
            marca = ("<span class='badge bad'>crossed</span>" if alvo["ja_cruzado"]
                     else f"<span class='badge warn'>≈ {alvo['tempo_min']:.0f} min</span>"
                     if alvo.get("tempo_min") else "")
            add(f"<p class='sub' style='margin:3px 0'>→ {_e(alvo['nome'])} ({alvo['valor']:.0f} kPa): "
                f"{_n(alvo['distancia'])} kPa {marca} <span class='mono'>{_e(alvo['fonte'])}</span></p>")
    add("</section>")

    # barrier impact
    b1, b2 = a1["barreiras"][0], a1["barreiras"][1]
    c1, l1 = _estado_barreira(b1, dem)
    c2_, l2 = _estado_barreira(b2, dem)
    add("<section class='card'><h2>Barrier impact</h2>"
        "<p class='sub'>Barriers of the pathway combine by <b>AND</b>. PFD as design → current, "
        "with both C2 multipliers. A demanded barrier is shown by its outcome.</p>"
        "<div class='bt'><div class='flow'>"
        "<div class='node threat'><div class='n1'>T1 — loss of stream 1 feed</div>"
        f"<div class='n2'>FIT-1001 at {_n(a2['margem'].get('FIT-1001', {}).get('valor'), 4)} kscmh</div></div>"
        "<span class='op'>AND</span>"
        f"<div class='node b {c1}'><div class='n1'>B1 — interlock</div><div class='n2'>{_e(l1)}</div></div>"
        "<span class='op'>AND</span>"
        f"<div class='node b {c2_}'><div class='n1'>B2 — operator</div><div class='n2'>{_e(l2)}</div></div>"
        "<span class='op'>→</span>"
        "<div class='node top'><div class='n1'>Loss of reactor<br>control</div></div></div>"
        + ("<div class='rule' style='margin-top:8px'>Beyond the pathway: <b>SIS trip</b> "
           f"({_n(dem['SIS']['limiar'], 0)} kPa, <code>alarm_config.trip_sis</code>) acted at "
           f"{_e(dem['SIS']['atuou_em'][11:])}. It is not a barrier of T1 and its action is not "
           "B1's.</div>" if dem.get("SIS") else "")
        + "</div>")
    for b in a1["barreiras"]:
        c2 = b["c2"]
        pior, dom = c2["componente_pior"], c2["elemento_dominante"]
        sev = "bad" if c2["multiplicador_barreira"] >= 2.0 else "warn"
        det = {x["item"]: x for x in b["detalhe_componentes"]}[pior["item"]]
        add(f"<div class='bcard'><div class='bhead'><div><div class='bname'>{_e(b['nome'])}</div>"
            f"<div class='bnode'>{_e(' · '.join(b['componentes']))}</div></div>"
            f"<span class='badge {sev}'>{c2['multiplicador_barreira']}× design</span></div>"
            "<div class='pfd2'>"
            f"<div class='pcol'><div class='t'>Most degraded component — {_e(pior['item'])}</div>"
            f"<div class='pair'><span class='from'>{det['pfd_projeto']:.2e}<em>design</em></span>"
            f"<span class='to bad'>{det['pfd']:.2e}<em>current</em></span></div>"
            f"<div class='dl bad'>{pior['multiplicador']}× design</div></div>"
            f"<div class='pcol'><div class='t'>Barrier {_e(b['id'])} complete</div>"
            f"<div class='pair'><span class='from'>{b['pfd_projeto']['valor']:.2e}<em>design</em></span>"
            f"<span class='to {sev}'>{b['pfd_atual']['valor']:.2e}<em>current</em></span></div>"
            f"<div class='dl {sev}'>{c2['multiplicador_barreira']}× — {_e(dom['item'])} carries "
            f"{dom['fracao_do_total']:.0%}</div></div></div>")
        if b["id"] == "B1" and gv.get("estatistica_por_canal"):
            parados = set(gv.get("canais_parados") or [])
            outlier = (gv.get("concordancia_no_ultimo_instante") or {}).get("divergente_pela_maioria")
            rec = {x["channel_id"][-1]: x for x in a2["canais"]}
            add("<div class='chn'>")
            for k, st in gv["estatistica_por_canal"].items():
                ruim = k in parados or k == outlier
                add(f"<div class='ch {'bad' if ruim else 'ok'}'>Channel {k}"
                    f"<small>{_n(st['ultimo'])} kPa · sd {_n(st['desvio'])}</small>"
                    f"<small>record: {_e(rec.get(k, {}).get('estado', '—'))}</small></div>")
            add("</div>")
            if gv.get("congelamento"):
                g = gv["congelamento"]
                add(f"<div class='gap'>Channel <b>{_e(g['canal'])}</b> is flat at "
                    f"{_n(g['valor_medio'])} kPa since about {_e(g['parado_desde_aprox'][:10])}; the "
                    f"pressure regime before the operating-condition change was {_n(g['regime_de_referencia'])} kPa. "
                    "<span class='badge calc'>computed</span></div>")
        add("</div>")
    add("</section></div><div>")

    # demand outcome
    add("<section class='card'><h2>Demand outcome</h2>"
        "<p class='sub'>Each barrier on the detect–decide–act model, at its own demand, against "
        "the design basis success criterion.</p>")
    d1 = dem.get("B1") or {}
    if d1.get("demandada"):
        det, dec, act, out = d1["detectar"], d1["decidir"], d1["agir"], d1["desfecho"]
        add(f"<div class='kv'><b>B1 demand</b><span class='mono'>{_e(d1['instantes']['ancora'])}</span>"
            f"<b>detect</b><span>2oo3 vote satisfied: <b>{_e(det['voto_2oo3_satisfeito'])}</b> "
            f"(channels above HIHI: {_e(', '.join(det['canais_acima']) or 'none')})</span>"
            f"<b>decide</b><span>" + ("; ".join(f"{_e(e['tipo'])} at {_e(e['ts'][11:])}: "
                                               + _e(json.dumps(e['detalhe']))
                                               for e in dec["eventos_registrados"]) or "no record")
            + "</span>"
            f"<b>act</b><span>" + (("no actuation signature" if not act["algum_como_esperado"]
                                    else "actuation signature present")
                                   if act["sinais"] else "window too short") + "</span>"
            "<b>outcome</b><span>criterion met: <b>"
            + ("not yet determined" if out['criterio_atendido'] is None else _e(out['criterio_atendido']))
            + "</b> — "
            f"{_e(out['nota'])}</span></div>")
    else:
        add(f"<p class='sub'>B1: {_e(d1.get('nota', 'not demanded'))}</p>")
    d2 = dem.get("B2")
    if d2:
        add(f"<div class='rule' style='margin-top:8px'><b>B2</b> trigger: {_e(d2['gatilho_declarado'])}. "
            f"ZT-1001 in the data: {_e(d2['sinal_de_posicao_ZT-1001']['presente'])}; outputs "
            f"commanded at B1's demand: {_e(d2['comando_registrado_na_demanda_de_B1'])}.</div>")
    add("</section>")

    # top event frequency
    if mot:
        add("<section class='card'><h2>Top event frequency <span class='badge calc'>computed</span></h2>"
            "<p class='sub'>Design diagram against current barrier PFDs. Conventional for "
            "magnitude; fuzzy for the propagation of linguistic uncertainty.</p><table>"
            "<tr><th>Engine</th><th>Design /yr</th><th>Current /yr</th><th>×</th><th>Label</th></tr>")
        for eng in ("conventional", "fuzzy"):
            e = mot[eng]
            lab = (f"{e['projeto']['rotulo']} → {e['atual']['rotulo']}" if e["projeto"]["rotulo"] else "—")
            add(f"<tr><td>{eng}</td><td class='num'>{e['projeto']['evento_topo_por_ano']:.2e}</td>"
                f"<td class='num'><b>{e['atual']['evento_topo_por_ano']:.2e}</b></td>"
                f"<td class='num'>{e['razao']}</td><td>{_e(lab)}</td></tr>")
        add("</table></section>")

    # envelope
    add("<section class='card'><h2>Validity envelope "
        f"<span class='badge {'bad' if env.get('invalidada') else 'ok'}'>"
        f"{'invalidated' if env.get('invalidada') else 'holds'}</span></h2>")
    ref, disp = env.get("referencia_de_projeto"), env.get("dispersao") or {}
    if ref and disp:
        add("<div class='env'>"
            f"<div class='envbox ref'><div class='t'>Design rate</div><div class='big'>"
            f"{_n(ref['taxa_kpa_min'], 1)}</div><div class='u'>kPa/min · {_e(ref['fonte'])}</div></div>"
            f"<div class='envbox now'><div class='t'>Highest rate in the ladder</div><div class='big'>"
            f"{_n(disp['maxima'])}</div><div class='u'>kPa/min · "
            f"{_n(disp['maxima'] / ref['taxa_kpa_min'], 1)}× design</div></div></div>")
    for g in env.get("gatilhos_de_invalidacao", []):
        if g["observado"]:
            add(f"<div class='contra'><b>OBSERVED</b> — {_e(g['gatilho'])}<br>"
                f"<span class='sub'>{_e(g['evidencia'])}</span></div>")
    reg = a2.get("regime") or {}
    if reg.get("mudanca") and not env.get("degraus"):
        add(f"<div class='contra'><b>Base-case change</b> at {_e(reg['mudanca']['ts'])}, regime shift "
            f"{_n(reg.get('deslocamento_kpa'))} kPa, no revalidation recorded.</div>")
    add("</section>")

    # gaps
    add("<section class='card'><h2>Gaps that bear on the decision <span class='badge warn'>C5</span></h2>")
    n = 0
    for x in c["a3_cruzamentos"]:
        for l in x.get("lacunas", []) or []:
            n += 1
            add(f"<div class='gap'><b>{n}. {_e(l['pergunta'])}</b><br>"
                f"<b>External check:</b> {_e(l['verificacao_externa'])}</div>")
    if not n:
        add("<p class='sub'>None at this instant.</p>")
    add("</section></div></div>")

    if timeline:
        add("<section class='card'><h2>Analyses over time</h2>"
            "<p class='sub'>Each trigger in the stream opened its own dated analysis, and each "
            "decision uses only the context frozen at its <code>t_now</code>.</p><table><tr><th>#</th><th>t_now</th><th>Trigger(s)</th>"
            "<th>Decision</th></tr>")
        # Only analyses up to this one: a report dated at t_now showed the
        # titles of every later decision.
        for a in (x for x in timeline if x["ts"] <= ts):
            titulo = a.get("titulo") or ("phase B pending" if not a.get("phase_b") else "—")
            atual = " style='background:#eef6f6'" if a["incident_id"] == i["incident_id"] else ""
            add(f"<tr{atual}><td>{a['n']}</td><td class='mono'>"
                f"<a href='../{_e(a['incident_id'])}/report.html'>{_e(a['ts'])}</a></td>"
                f"<td class='mono'>{_e(', '.join(a['triggers']))}</td><td>{_e(titulo)}</td></tr>")
        add("</table></section>")

    add("<div class='foot'>Figures come from <code>context.json</code> (phase A, deterministic, from "
        "the database). The decision text is phase B, governed by <code>SKILL.md</code>; "
        + ("written by the blind single agent. " if blind else "not blind (see its note above). ")
        + "Every recovery rule, cross-check and assumption behind these "
        "numbers is in the <a href='log.html'>audit log</a>.</div></main></body></html>")
    destino.write_text("\n".join(P))
    return destino


# ─────────────────────────────────────────────────────────────────────── log

def _j(x, limite: int = 900) -> str:
    t = json.dumps(x, ensure_ascii=False, indent=1)
    return t if len(t) <= limite else t[:limite] + " …"


def render_log(c: dict, destino: Path) -> Path:
    """The audit chain. Everything needed to check the report line by line."""
    i, a1, a2 = c["identidade"], c["a1_base_de_projeto"], c["a2_estado_atual"]
    env, mot = c.get("envelope") or {}, c.get("motores") or {}
    dem, gv, reg = a2.get("demandas") or {}, a2.get("grupo_votado") or {}, a2.get("regime") or {}
    P = [_head(f"Analysis log · {i['incident_id']}"), _hdr(c, "log", "report.html")]
    add = P.append

    add("<section class='card'><h2>Identity and provenance</h2><div class='kv'>"
        + "".join(f"<b>{_e(k)}</b><span class='mono'>{_e(v)}</span>" for k, v in (
            ("incident_id", i["incident_id"]), ("bowtie_id", i["bowtie_id"]), ("run_id", i["run"]),
            ("t_now", i["ts"]), ("window from", i["janela_de"]),
            ("horizon from", i["origem_do_horizonte"]), ("database", i["banco"]),
            ("design basis", a1.get("documento") or "—")))
        + "</div><h3 class='s'>Trigger(s)</h3><span class='q'>"
        + _e("\n".join(json.dumps(g, ensure_ascii=False) for g in i.get("gatilho") or []) or "—")
        + "</span><h3 class='s'>Recovery rules applied</h3><span class='q'>"
        + _e("\n".join(f"{k:14} {v}" for k, v in a2["regra_de_recuperacao"].items()))
        + "</span></section>")

    if dem:
        add("<section class='card'><h2>Demand outcome, in full</h2>"
            "<p class='sub'>Anchored on each barrier's own demand. The SIS is a separate layer.</p>"
            f"<span class='q'>{_e(_j(dem, 6000))}</span></section>")

    if gv.get("estatistica_por_canal"):
        add("<section class='card'><h2>Voted group PIT-7001 <span class='badge calc'>computed</span></h2>"
            f"<p class='sub'>Window {_e(gv['janela']['de'])} → {_e(gv['janela']['ate'])}; design noise "
            f"{_e(gv['ruido_de_projeto_kpa'])} kPa (design basis §3).</p><table>"
            "<tr><th>Channel</th><th>n</th><th>Mean</th><th>SD</th><th>Min</th><th>Max</th><th>Last</th></tr>")
        for k, st in gv["estatistica_por_canal"].items():
            add(f"<tr><td>{k}</td><td class='num'>{st['n']}</td><td class='num'>{_n(st['media'])}</td>"
                f"<td class='num'>{_n(st['desvio'])}</td><td class='num'>{_n(st['min'])}</td>"
                f"<td class='num'>{_n(st['max'])}</td><td class='num'>{_n(st['ultimo'])}</td></tr>")
        add(f"</table><span class='q'>{_e(_j({'flat_channels': gv['canais_parados'], 'agreement': gv['concordancia_no_ultimo_instante'], 'freeze': gv['congelamento']}, 3000))}</span></section>")

    if reg.get("mudanca"):
        add("<section class='card'><h2>Regime and precursors since the operating-condition change</h2>"
            f"<span class='q'>{_e(_j(reg, 3000))}</span></section>")

    if env.get("degraus"):
        add("<section class='card'><h2>Rate ladder <span class='badge calc'>computed</span></h2><table>"
            "<tr><th>Window</th><th>From → to</th><th>kPa/min</th><th>vs design</th><th>Samples</th>"
            "<th>&gt; 2.2</th></tr>")
        for d in env["degraus"]:
            add(f"<tr><td>{_e(d['janela'])}</td><td class='mono'>{_e(d['de'][11:16])} → "
                f"{_e(d['ate'][11:16])}</td><td class='num'>{_n(d['taxa'])}</td>"
                f"<td class='num'>{_n(d.get('razao_vs_projeto'), 1)}×</td><td class='num'>{d['amostras']}</td>"
                f"<td>{'yes' if d.get('excede_limite') else 'no'}</td></tr>")
        add("</table>")
        for g in env.get("gatilhos_de_invalidacao", []):
            add(f"<div class='{'contra' if g['observado'] else 'rule'}'><b>"
                f"{'OBSERVED' if g['observado'] else 'not observed'}</b> — {_e(g['gatilho'])}<br>"
                f"<span class='sub'>{_e(g['evidencia'])}</span></div>")
        add("</section>")

    if mot:
        add("<section class='card'><h2>Engines, design versus current <span class='badge calc'>computed</span></h2>"
            f"<p class='sub'>Diagram <code>{_e(mot['diagrama'])}</code>; exposure window "
            f"{_e(mot['janela_de_exposicao_anos'])} yr; current PFDs fed: "
            f"<code>{_e(json.dumps(mot['pfd_atual']))}</code>.</p><table>"
            "<tr><th>Engine</th><th>State</th><th>Top event /yr</th><th>Label</th><th>Pathway %</th></tr>")
        for eng in ("conventional", "fuzzy"):
            for est, lab in (("projeto", "design"), ("atual", "current")):
                e = mot[eng][est]
                add(f"<tr><td>{eng}</td><td>{lab}</td><td class='num'>{e['evento_topo_por_ano']:.3e}</td>"
                    f"<td>{_e(e['rotulo'] or '—')}</td>"
                    f"<td class='num'>{_e([p['contribuicao_pct'] for p in e['pathways']])}</td></tr>")
        add(f"</table><p class='sub'>{_e(mot['nota'])}</p></section>")

    add("<section class='card'><h2>The eight cross-checks <span class='badge n'>none produces judgement</span></h2><table>"
        "<tr><th>#</th><th>Compared</th><th>Result</th></tr>")
    for x in c["a3_cruzamentos"]:
        add(f"<tr><td><b>{_e(x['id'])}</b><br><span class='sub'>{_e(x['titulo'])}</span></td>"
            f"<td><span class='q'>{_e(_j(x['comparado'], 700))}</span></td>"
            f"<td>{_e(x['resultado'])}"
            + (f"<br><span class='sub'>gap: {_e(x['lacuna'])}</span>" if x.get("lacuna") else "")
            + (f"<br><span class='sub'>not applicable: {_e(x['nao_se_aplica'])}</span>" if x.get("nao_se_aplica") else "")
            + "</td></tr>")
    add("</table></section>")

    add("<section class='card'><h2>Named gaps and contradictions</h2>")
    n = 0
    for x in c["a3_cruzamentos"]:
        for l in x.get("lacunas", []) or []:
            n += 1
            add(f"<div class='gap'><b>{n}. {_e(l['pergunta'])}</b><br>{_e(l['por_que_nao_responde'])}.<br>"
                f"<b>External check:</b> {_e(l['verificacao_externa'])}</div>")
    for k in a2["contradicoes"]:
        s_ = k["sensibilidade"]
        add(f"<div class='contra'><b>{_e(k['item'])}</b><br>{_e(k['fonte_a']['o_que'])}: "
            f"“{_e(k['fonte_a']['diz'])}”<br>{_e(k['fonte_b']['o_que'])}: “{_e(k['fonte_b']['diz'])}”<br>"
            f"<span class='sub'>{_e(k['fonte_a']['regra'])}</span><br>Sensitivity "
            "<span class='badge calc'>computed</span>: last test implied by the calendar "
            f"{_e(s_['ultimo_teste_implicito'][:10])} (<span class='badge warn'>assumption</span> "
            f"{_e(s_['premissa'])}); item PFD {s_['pfd_item_relogio_do_modelo']:.2e} → "
            f"{s_['pfd_item_relogio_do_calendario']:.2e} ({s_['razao_item']}×); per barrier "
            f"{_e(json.dumps(s_['por_barreira']))}.<br><b>{_e(k['nao_resolvida'])}</b></div>")
    add("</section>")

    add("<section class='card'><h2>Model assumptions <span class='badge warn'>assumption</span></h2>"
        "<p class='sub'>None of these is in the asset table. They stay visible so they can be "
        "challenged.</p><table><tr><th>Assumption</th><th>Value</th><th>Effect</th></tr>")
    for k, v in c["premissas_do_modelo"].items():
        add(f"<tr><td class='mono'>{_e(k)}</td><td><b>{_e(v.get('valor', v.get('formula', '—')))}</b></td>"
            f"<td>{_e(v['efeito'])}</td></tr>")
    add("</table></section>")

    add(f"<div class='gate'><b>Phase A→B gate.</b> {n} named gap(s), {len(a2['contradicoes'])} "
        f"recorded contradiction(s), validity envelope "
        f"{'invalidated' if env.get('invalidada') else 'not invalidated by the rate ladder'}. "
        "Phase B was written under these declared restrictions; none was filled in by estimate. "
        "<a href='report.html'>Back to the report</a>.</div></main></body></html>")
    destino.write_text("\n".join(P))
    return destino


def render(c: dict, phase_b: str | None, pasta: Path, timeline: list[dict] | None = None) -> Path:
    """Write both views into `pasta`: report.html and log.html."""
    pasta.mkdir(parents=True, exist_ok=True)
    render_log(c, pasta / "log.html")
    mj = pasta / "meta.json"
    meta = json.loads(mj.read_text()) if mj.exists() else None
    return render_report(c, phase_b, pasta / "report.html", timeline, meta)
