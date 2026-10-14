"""
Verificação mínima do Safety Copilot (RUN_A) — `python3 -m pytest test_safety_copilot.py`.

Cobre a lógica que quebra em silêncio: mascaramento, corte temporal, detector,
fase A fechada, PFD só com falha conhecida e disparos do stream.
"""

import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def test_mascaramento_barra_por_prefixo():
    """O padrão proibido tem de barrar a FAMÍLIA do prefixo, não uma forma.

    Regressão de um vazamento real: a regra era `\bXMV[_ ]?\d+\b` — exigia
    dígitos — e deixou passar `XMV-FEED`, identificador de equipamento vindo da
    tabela de ativos. Saiu num relatório antes de ser notado. Qualquer forma
    nova do prefixo precisa falhar alto; passar silencioso invalida o teste
    cego e o faz parecer válido, que é o pior dos dois estados.
    """
    from safety_copilot.blind_feed import scrub

    assert scrub("Ativo XMV-FEED isolado") == "Ativo XV-1001 isolado"
    assert scrub("Abertura de XMV_10") == "Abertura de FCV-1002"
    # tags que o banco corrigido trouxe: traduzidas, nao barradas
    assert scrub("Valvula XMV_4 em 70%") == "Valvula XV-1001D em 70%"
    assert scrub("Vazao XMEAS_4") == "Vazao FIT-1004"

    # o que nao tem alias tem de falhar alto, qualquer que seja a forma
    # o evento de MOC sai com nome de planta e sem a marca de simulacao
    assert scrub('mudanca_caso_base {"modo": "x", "carga_pct": 15, "aplicado_na_simulacao": true}') \
        == 'operating_condition_change {"modo": "x", "carga_pct": 15}'

    for termo in ("XMV_9", "XMV", "XMV-BLEED", "XMEAS_33", "XMEAS", "IDV_6",
                  "caso_base", "simulacao"):
        try:
            scrub(f"registro citando {termo} solto")
        except ValueError:
            continue
        raise AssertionError(f"termo de procedência passou sem barreira: {termo}")


# ─────────────────────────────────────── streaming, Fase A e teste cego (v2)

def test_invariante_temporal():
    """Nenhum campo publicado carrega timestamp maior que t_now.

    Em LOTE isso nunca foi exercitado: o unico instante consultado era o fim do
    horizonte, onde nao existe futuro. Em STREAMING cada ponto tem futuro, e
    tres consultas vazavam — `sensor_channels` sem filtro de ts nenhum,
    `alarm_events.ts_fim` e `work_orders.data_fechamento`. O ultimo entregava a
    ablacao inteira: nos runs de controle se via, desde janeiro, que todo teste
    do ano seria fechado no prazo.
    """
    import re
    from safety_copilot.blind_feed import connect, context
    con = connect()
    for ts in ("2025-01-15T00:00:00", "2025-04-01T12:00:00", "2025-09-01T00:00:00",
               "2025-12-01T01:00:00", "2025-12-01T02:07:30"):
        for run in ("RUN_A", "RUN_B"):
            s = json.dumps(context(con, run, ts), ensure_ascii=False)
            fut = sorted({t for t in re.findall(r"20\d\d-\d\d-\d\dT\d\d:\d\d:\d\d", s)
                          if t > ts})
            assert not fut, f"look-ahead em {run} @ {ts}: {fut}"


def test_detector_reproduz_alarm_events():
    """O detector de streaming tem de reproduzir `alarm_events` exatamente.

    Sem histerese, o cruzamento de limiar derivado de `alarm_config` cai no
    mesmo instante que o banco registrou — e isso faz do banco o autoteste do
    detector. Se divergir, ou o limiar mudou ou o detector ganhou logica que o
    banco nao tem.
    """
    from safety_copilot.blind_feed import connect, limiares, stream_pontos, ALIAS
    from safety_copilot.stream import Estado
    con = connect()
    esperado = {(ALIAS.get(r["tag"], r["tag"]), r["tipo"]): r["ts_inicio"]
                for r in con.execute(
                    """SELECT tag, tipo, ts_inicio FROM alarm_events
                       WHERE run_id='RUN_A' AND ts_inicio>='2025-12-01T00:00:00'""")}
    est = Estado(limiares(con))
    visto: dict[tuple, str] = {}
    for p in stream_pontos(con, "RUN_A", "2025-11-30T23:59:59"):
        for m in est.passo(p)["motivos"]:
            if m["chave"].startswith("alarme:"):
                visto.setdefault((m["tag"], m["tipo"]), m and p["ts"])
    for chave, ts in esperado.items():
        assert chave in visto, f"detector nao viu {chave}"
        assert visto[chave] == ts, f"{chave}: detector {visto[chave]} != banco {ts}"


def test_pico_de_alarme_nao_revela_futuro():
    """Changing future observations must not change an earlier context."""
    import sqlite3
    from safety_copilot.blind_feed import connect, alarmes_visiveis
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    source = connect()
    source.backup(con)
    source.close()
    ts = "2025-12-01T02:07:30"
    before = alarmes_visiveis(con, "RUN_A", ts)
    con.execute("UPDATE alarm_events SET valor_pico=999999 WHERE run_id='RUN_A' AND (ts_fim IS NULL OR ts_fim>?)", (ts,))
    con.execute("UPDATE series SET valor=999999 WHERE run_id='RUN_A' AND ts>?", (ts,))
    assert alarmes_visiveis(con, "RUN_A", ts) == before
    pressure = next(a for a in before if a["tag"] == "PIT-7001" and a["tipo"] == "HIHI")
    assert pressure["valor_pico"] < 2900
    con.close()


def test_referencias_astra_nao_carregam_resultados_do_episodio():
    from safety_copilot.astra import approved_material
    reference = approved_material()["references/cross-checks.md"]
    assert "On the reference reactor episode" not in reference
    assert "**Worked case.**" not in reference
    # nenhum instante nem rotulo de run do episodio no material aprovado
    import re
    todo = "".join(approved_material().values())
    assert not re.search(r"20\d\d-\d\d-\d\dT\d\d:\d\d|RUN_[A-Z]\b", todo)
    assert "## C8" in reference


def test_narrativa_futura_nao_muda_contexto_anterior():
    import sqlite3
    from safety_copilot import blind_feed as bf
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    source = bf.connect()
    source.backup(con)
    source.close()
    ts = "2025-04-01T00:30:00"
    before = bf.context(con, "RUN_A", ts)
    events = bf.eventos_de_registro(con, "RUN_A", ts)
    con.execute("UPDATE work_orders SET descricao='FUTURE_REPAIR_SECRET', falha_encontrada=0 WHERE run_id='RUN_A' AND data_fechamento>?", (ts,))
    assert bf.context(con, "RUN_A", ts) == before
    assert bf.eventos_de_registro(con, "RUN_A", ts) == events
    assert before["ordens_servico"][0]["falha_encontrada"] is None
    assert "reteste" not in before["ordens_servico"][0]["descricao"].lower()
    con.close()


def test_fase_a_fechada():
    """A Fase A tem de sair completa e auditavel, sem julgamento."""
    from safety_copilot import contexto as ctx
    from safety_copilot.blind_feed import scrub
    c = ctx.montar("RUN_A", "2025-12-01T02:07:30")

    # os oito cruzamentos, cada um com resultado OU nao_se_aplica preenchido
    ids = [x["id"] for x in c["a3_cruzamentos"]]
    assert ids == [f"C{n}" for n in range(1, 9)], ids
    for x in c["a3_cruzamentos"]:
        assert x["resultado"] or x["nao_se_aplica"], x["id"]

    # C2 devolve os DOIS multiplicadores; nunca so um
    for b in c["a1_base_de_projeto"]["barreiras"]:
        assert b["c2"]["multiplicador_barreira"] is not None
        assert b["c2"]["componente_pior"]["multiplicador"] is not None
        assert b["c2"]["elemento_dominante"]["item"]

    # C7: nenhuma tag apresenta distancia sem taxa
    for tag, m in c["a2_estado_atual"]["margem"].items():
        assert "taxa_por_min" in m, tag

    # a escada de taxas mede a mesma grandeza em varias janelas, cada uma
    # declarada — e o que sustenta C1 sem base de projeto
    esc = c["envelope"]
    assert len(esc["degraus"]) >= 4
    for d in esc["degraus"]:
        assert d["de"] < d["ate"] and d["amostras"] >= 3 and d["span_min"] > 0
    # a base de projeto agora e declarada, entao a escada compara contra ela e
    # avalia os gatilhos da secao 7 um a um
    assert esc["referencia_de_projeto"]["taxa_kpa_min"] > 0
    assert esc["limite_de_invalidacao"]["taxa_kpa_min"] > 0
    assert len(esc["gatilhos_de_invalidacao"]) == 3
    for g in esc["gatilhos_de_invalidacao"]:
        assert isinstance(g["observado"], bool) and g["evidencia"]
    assert esc["invalidada"] is any(g["observado"] for g in esc["gatilhos_de_invalidacao"])

    # os numeros do extrato batem com o documento da base de projeto
    doc = (Path(".agents/skills/analise-seguranca/references")
           / "design-basis-barriers.md").read_text()
    db = ctx.DESIGN_BASIS
    for n in (db["condicao_de_projeto"]["taxa_escalada_kpa_min"],
              db["invalidacao"]["taxa_limite_kpa_min"],
              db["desempenho"]["janela_hihi_sis_min"],
              db["desempenho"]["atraso_tolerav_b2_min"],
              db["escada_protecao"]["trip_sis"]):
        assert f"{n:g}" in doc, f"{n} nao consta do documento da base de projeto"

    # a fronteira do teste cego: nem o contexto, nem o markdown, nem o HTML
    # renderizado podem vazar procedencia
    import re
    from safety_copilot import relatorio as rel
    scrub(ctx.render_md(c))
    assert "falho_oculto" not in json.dumps(c, ensure_ascii=False)
    # Check the original bytes, not scrub's returned (translated) copy.
    from safety_copilot.blind_feed import _FORBIDDEN_RE
    assert not _FORBIDDEN_RE.search(json.dumps(c, ensure_ascii=False))
    assert not _FORBIDDEN_RE.search(ctx.render_md(c))
    # as DUAS visoes passam pela fronteira do cego: o relatorio e o log
    dir_ = Path("state/analises/_teste")
    rel.render(c, "# test\n\nBody.\n", dir_)
    for nome in ("report.html", "log.html"):
        assert (dir_ / nome).exists(), nome
        scrub(re.sub(r"<[^>]+>", " ", (dir_ / nome).read_text()))
        assert not _FORBIDDEN_RE.search((dir_ / nome).read_text())


def test_pfd_so_conta_falha_conhecida():
    """A falha que a operacao nao detectou nao pode entrar na PFD.

    Contar uma falha oculta punha no numero — e no texto do motivo — a data de
    algo que, por definicao, ninguem sabe que existe: o gabarito do teste cego
    chegava ao agente pela camada de confiabilidade. O banco corrigido nao tem
    falha oculta, entao o teste fabrica uma sobre uma copia.
    """
    import shutil
    import sqlite3
    import tempfile
    from safety_copilot import blind_feed as bf

    TS = "2025-12-01T02:00:00"
    conhecida = bf.pfd_confiabilidade(bf.connect(), "RUN_A", TS, "PT-007")["pfd"]

    with tempfile.TemporaryDirectory() as tmp:
        copia = Path(tmp) / "db.sqlite"
        shutil.copy(bf.DB, copia)
        copia.chmod(0o644)
        w = sqlite3.connect(copia)
        w.execute("""UPDATE sensor_channels SET ts_deteccao=NULL, wo_id=NULL,
                     estado='falho_oculto' WHERE run_id='RUN_A' AND channel_id='PT-007.B'""")
        w.execute("DELETE FROM work_orders WHERE wo_id='WO-RUN_A-CH-B'")
        w.commit()
        w.close()
        antes, bf.DB = bf.DB, copia
        try:
            oculta = bf.pfd_confiabilidade(bf.connect(), "RUN_A", TS, "PT-007")
            visivel = bf.context(bf.connect(), "RUN_A", TS)
        finally:
            bf.DB = antes

    assert oculta["pfd"] < conhecida, "falha oculta nao pode degradar a PFD publicada"
    assert not any("2oo2" in m for m in oculta["motivos"])
    assert "falho_oculto" not in json.dumps(visivel, ensure_ascii=False)


def test_stream_dispara_no_calendario_e_nos_registros():
    """O mecanismo da tese — erosao por calendario — nao aparece na serie.

    Sem assinatura de registro, o detector varria o horizonte inteiro e nao via
    nem o teste funcional vencido em 31/05 nem o treinamento em 30/07.
    """
    from safety_copilot import blind_feed as bf

    con = bf.connect()
    ev = {e["ts"][:10] + ":" + e["tipo"] for e in bf.eventos_de_registro(con, "RUN_A")}
    for esperado in ("2025-04-01:wo_opened", "2025-04-01:channel_failure_detected",
                     "2025-05-31:wo_overdue", "2025-07-30:wo_overdue",
                     "2025-08-29:channel_failure_detected", "2025-11-28:process_event",
                     "2025-12-01:process_event"):
        assert esperado in ev, esperado
    cru = json.dumps(bf.eventos_de_registro(con, "RUN_A"), ensure_ascii=False).lower()
    assert "idv" not in cru, "evento de registro nao pode carregar o gabarito"


if __name__ == "__main__":
    for name, fn in sorted(list(globals().items())):
        if name.startswith("test_"):
            fn()
            print(f"ok  {name}")
    print("\ntudo passou")
