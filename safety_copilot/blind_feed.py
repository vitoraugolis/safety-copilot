"""
Driver de dados do teste cego — planta química anônima.

Único caminho autorizado entre o banco do experimento e a mesa multiagente.
Faz duas coisas que nenhuma outra parte do sistema faz:

  1. MASCARA a procedência. O banco usa a nomenclatura de um benchmark público
     de engenharia química, que qualquer LLM reconhece de imediato — receber
     `XMEAS_7` é receber a resposta. Este módulo traduz para TAGs de instrumento
     no padrão ISA-5.1, plausíveis para qualquer planta.
  2. FILTRA o gabarito. `process_events.visivel_copiloto = 0` é ground truth do
     experimento. Nada com essa marca sai daqui, em nenhuma consulta.

O mascaramento é declarado em ALIAS/DESCRICAO abaixo, não escondido em regex:
quem audita o experimento precisa ver exatamente o que foi substituído.

    python3 -m safety_copilot.blind_feed --run RUN_A --list
    python3 -m safety_copilot.blind_feed --run RUN_A --at 2025-12-01T02:00:00
    python3 -m safety_copilot.blind_feed --run RUN_A --replay --speed 120
    python3 -m safety_copilot.blind_feed --run RUN_A --audit
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
from datetime import datetime
from itertools import groupby
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = Path(os.environ.get("SC_DB") or ROOT / "data" / "blind" / "safety_copilot_v2.db")
TAGS = ROOT / "data" / "live_tags.json"
PREFIX = "PLANT_"

# ─────────────────────────────────────────────────────────── mascaramento

# Tag do banco → TAG de instrumento ISA-5.1 da "planta anônima".
# A função física é preservada (pressão continua pressão); só a procedência
# some. Sem isto, o nome da variável entrega o benchmark de origem.
ALIAS = {
    "XMEAS_7":  "PIT-7001",   # pressão do vaso de reação
    "XMEAS_9":  "TIT-9001",   # temperatura do vaso de reação
    "XMEAS_8":  "LIT-8001",   # nível do vaso de reação
    "XMEAS_1":  "FIT-1001",   # vazão de alimentação da corrente 1
    "XMEAS_21": "TIT-2101",   # temperatura de saída da água de resfriamento
    "XMV_10":   "FCV-1002",   # abertura da válvula de água de resfriamento
    "XMV_6":    "FCV-0601",   # abertura da válvula de alívio/purga
    # Banco corrigido (2026-09-11): vazões e válvulas de alimentação passam a
    # ter série. Sem alias elas eram descartadas em silêncio pelo feed, e a
    # assinatura de atuação de B1 (fechar alimentações) ficava invisível.
    "XMEAS_2":  "FIT-1002",   # vazão de alimentação da corrente 2
    "XMEAS_3":  "FIT-1003",   # vazão de alimentação da corrente 3
    "XMEAS_4":  "FIT-1004",   # vazão de alimentação da corrente 4 (A+C)
    "XMV_1":    "XV-1001A",   # válvula de alimentação da corrente 2
    "XMV_2":    "XV-1001B",   # válvula de alimentação da corrente 3
    "XMV_3":    "XV-1001C",   # válvula de alimentação da corrente 1
    "XMV_4":    "XV-1001D",   # válvula de alimentação da corrente 4 (A+C)
    # Identificador de EQUIPAMENTO, não de tag de processo — vinha da tabela de
    # ativos e escapava porque o padrão proibido exigia dígitos depois do
    # prefixo. `XV` é a nomenclatura ISA-5.1 para válvula de bloqueio on-off,
    # que é a função declarada deste item.
    "XMV-FEED": "XV-1001",    # bloqueio da alimentação (conjunto de válvulas)
}
REVERSE = {v: k for k, v in ALIAS.items()}

# Descrições de engenharia neutras. As do banco citam "alimentação A", que
# junto com o resto do vocabulário aponta para o benchmark.
DESCRICAO = {
    "PIT-7001": ("Reaction vessel pressure", "kPa"),
    "TIT-9001": ("Reaction vessel temperature", "C"),
    "LIT-8001": ("Reaction vessel level", "%"),
    "FIT-1001": ("Stream 1 feed flow", "kscmh"),
    "TIT-2101": ("Cooling water outlet temperature", "C"),
    "FCV-1002": ("Cooling water valve opening", "%"),
    "FCV-0601": ("Purge valve opening", "%"),
    "FIT-1002": ("Stream 2 feed flow", "kscmh"),
    "FIT-1003": ("Stream 3 feed flow", "kscmh"),
    "FIT-1004": ("Stream 4 (A+C) feed flow", "kscmh"),
    "XV-1001A": ("Stream 2 feed valve opening", "%"),
    "XV-1001B": ("Stream 3 feed valve opening", "%"),
    "XV-1001C": ("Stream 1 feed valve opening", "%"),
    "XV-1001D": ("Stream 4 (A+C) feed valve opening", "%"),
}

# Termos que jamais podem alcançar um prompt. Verificados por `scrub()` em
# tudo que sai deste módulo — cinto e suspensório sobre o ALIAS.
FORBIDDEN = [
    # Regra de PREFIXO, não de forma exata. A versão anterior era
    # `\bXMV[_ ]?\d+\b` — exigia dígitos — e deixou passar `XMV-FEED`, um
    # identificador de equipamento que carrega a convenção de nomes do
    # benchmark de origem. O vazamento saiu num relatório antes de ser notado.
    # Barrar o prefixo inteiro faz o caso não previsto falhar alto em vez de
    # passar silencioso, que é a única política defensável aqui.
    r"\bXMEAS[-_ ]?\w*", r"\bXMV[-_ ]?\w*", r"\bIDV[-_ ]?\w*",
    r"\btennessee\b", r"\beastman\b", r"\bTEP\b", r"\bdowns\b", r"\bvogel\b",
    r"G/H\s*\d+-\d+",          # razão mássica G/H: nomenclatura do benchmark
    r"\bG/H\b",
    # O evento de MOC chegava como `mudanca_caso_base`, com a chave
    # `aplicado_na_simulacao`: vocabulário do cenário simulado, não de um
    # registro de planta. A base de projeto ainda citava o nome exato do evento.
    r"caso[_ ]base", r"simula[cç][aã]o",
]
_FORBIDDEN_RE = re.compile("|".join(FORBIDDEN), re.IGNORECASE)

# Substituições textuais para campos livres que sobrevivem ao ALIAS.
TEXT_SUBS = [
    (re.compile(r'"?G/H\s*\d+-\d+"?', re.I), '"campanha padrao"'),
    (re.compile(r"\bG/H\b", re.I), "razao de produto"),
    (re.compile(r"\bmudanca_caso_base\b"), "operating_condition_change"),
    (re.compile(r',\s*"aplicado_na_simulacao"\s*:\s*(?:true|false)'), ""),
    (re.compile(r'"aplicado_na_simulacao"\s*:\s*(?:true|false)\s*,?\s*'), ""),
]


def scrub(text: str) -> str:
    """Aplica ALIAS e substituições textuais. Levanta se algo proibido restar.

    Falhar alto é deliberado: um vazamento silencioso invalida o teste cego
    inteiro, e um teste cego inválido é pior que nenhum teste — porque parece
    válido.
    """
    for src, dst in ALIAS.items():
        text = re.sub(rf"\b{re.escape(src)}\b", dst, text)
    for rx, dst in TEXT_SUBS:
        text = rx.sub(dst, text)
    leak = _FORBIDDEN_RE.search(text)
    if leak:
        raise ValueError(f"vazamento de procedência não mascarado: {leak.group(0)!r}")
    return text


def scrub_obj(obj):
    """scrub() recursivo sobre estrutura JSON."""
    if isinstance(obj, str):
        return scrub(obj)
    if isinstance(obj, dict):
        return {scrub(k) if isinstance(k, str) else k: scrub_obj(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [scrub_obj(v) for v in obj]
    return obj


# ───────────────────────────────────────────────────────────── consultas

def connect() -> sqlite3.Connection:
    if not DB.exists():
        raise SystemExit(f"banco do experimento não encontrado: {DB}")
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)   # somente leitura
    con.row_factory = sqlite3.Row
    return con


# Início do horizonte de cada run. Vale um cache porque a consulta é cara e o
# valor é constante: `ix_series` cobre (run_id, tag, canal) e não `ts`, então
# MIN(ts) varre as ~45 mil linhas do run — 149 ms, contra 0,1 ms de todas as
# outras consultas do caminho quente. Dentro de `pfd_confiabilidade`, chamada
# uma vez por ativo por ponto da trajetória, isso sozinho respondia por 93% do
# tempo da varredura. Memorizar é preferível a criar índice: o banco do
# experimento é aberto somente-leitura e não deve ser alterado pela análise.
_ORIGEM: dict[str, str] = {}


def origem_do_horizonte(con, run: str) -> str:
    if run not in _ORIGEM:
        _ORIGEM[run] = con.execute(
            "SELECT MIN(ts) FROM series WHERE run_id=?", (run,)).fetchone()[0]
    return _ORIGEM[run]


def runs(con) -> list[dict]:
    q = """SELECT run_id, COUNT(*) n, MIN(ts) t0, MAX(ts) t1, COUNT(DISTINCT tag) tags
           FROM series GROUP BY run_id ORDER BY run_id"""
    return [dict(r) for r in con.execute(q)]


def snapshot(con, run: str, ts: str | None = None) -> dict:
    """Leituras vigentes em `ts` (ou a última amostra, se ts=None).

    Devolve o valor votado de cada tag e, quando existirem, os canais A/B/C
    individuais — é a discrepância entre canais que revela um transmissor
    degradado, então ela precisa chegar à mesa.
    """
    ts = ts or con.execute(
        "SELECT MAX(ts) FROM series WHERE run_id=?", (run,)).fetchone()[0]
    # Função de janela em vez de subconsulta correlacionada: a versão correlata
    # reexecutava um MAX(ts) por linha e levava minutos sobre 56 mil amostras.
    q = """SELECT tag, canal, valor FROM (
             SELECT tag, COALESCE(canal,'voted') canal, valor,
                    ROW_NUMBER() OVER (PARTITION BY tag, COALESCE(canal,'voted')
                                       ORDER BY ts DESC) rn
             FROM series WHERE run_id=? AND ts<=?
           ) WHERE rn=1"""
    out: dict[str, float] = {}
    for r in con.execute(q, (run, ts)):
        alias = ALIAS.get(r["tag"])
        if alias is None:
            continue                       # tag desconhecida não é publicada
        suffix = "" if r["canal"] == "voted" else f"_CH{r['canal']}"
        out[f"{PREFIX}{alias.replace('-', '_')}{suffix}"] = round(r["valor"], 4)
    return {"ts": ts, "tags": out}


# ─────────────────────────────────────────────────────── corte temporal
#
# Em LOTE nada disto importava: o unico instante consultado era o fim do
# horizonte, onde nao existe futuro. Em STREAMING cada ponto tem futuro, e tres
# consultas de `context()` publicavam campos que a operacao nao poderia
# conhecer:
#
#   · sensor_channels nao tinha filtro de ts nenhum — em janeiro devolvia a
#     falha de abril, a deteccao 30 min depois e o reparo de 2 de abril;
#   · alarm_events filtrava por ts_inicio mas publicava ts_fim — o agente sabia
#     quando o alarme ia normalizar (20 dos 38 alarmes tinham ts_fim);
#   · work_orders filtrava por data_abertura mas publicava data_fechamento e
#     status finais — nos runs de CONTROLE, isso entrega a ablacao inteira: a
#     partir de janeiro se ve que todo teste e todo treinamento do ano SERAO
#     fechados no prazo.
#
# O corte mora aqui, e nao em quem chama, porque este modulo e a fronteira do
# teste cego. Chamador novo que filtrasse por conta propria reabriria o furo.

def _futuro(valor: str | None, ts: str) -> bool:
    """Um timestamp ISO e futuro em relacao a `ts`? Ordem lexicografica basta."""
    return bool(valor) and valor > ts


def canais_visiveis(con, run: str, ts: str) -> list[dict]:
    """Estado dos canais como a operacao o conhece em `ts`.

    Fonte unica para qualquer consumidor. Canal cuja falha ainda nao foi
    detectada ATE `ts` sai como `sem_discrepancia_reportada` com as datas
    anuladas — falha oculta e, por definicao, o que ninguem sabe. Nenhum campo
    devolvido carrega timestamp maior que `ts`.
    """
    out = []
    for r in con.execute(
        """SELECT channel_id, equipamento_id, estado, ts_falha, ts_deteccao,
                  ts_reparo, wo_id FROM sensor_channels
           WHERE run_id=? ORDER BY channel_id""", (run,)):
        c = dict(r)
        detectado = c["ts_deteccao"] and not _futuro(c["ts_deteccao"], ts)
        reparado = c["ts_reparo"] and not _futuro(c["ts_reparo"], ts)
        if not detectado:
            # Nao detectado ainda: a operacao nao ve falha nenhuma.
            c["estado"] = "no_discrepancy_reported"
            c["ts_falha"] = c["ts_deteccao"] = c["ts_reparo"] = None
            c["wo_id"] = None
        else:
            c["estado"] = "ok" if reparado else "failed_detected_unrepaired"
            if not reparado:
                c["ts_reparo"] = None
        out.append(c)
    return out


def stream_pontos(con, run: str, desde: str | None = None):
    """Cursor ordenado: um dict por instante, com todas as tags daquele ts.

    Existe porque `snapshot()` usa uma funcao de janela sobre `ts<=?` e custa
    ~64 ms por chamada — chamar por ponto torna qualquer replay O(n^2) (medido:
    273 s para os pontos de um episodio, contra 0,115 s por este cursor).

    Publica ja com o ALIAS aplicado; tag desconhecida nao sai.
    """
    q = """SELECT ts, tag, COALESCE(canal,'voted') canal, valor FROM series
           WHERE run_id=? AND (? IS NULL OR ts>?) ORDER BY ts"""
    for ts, grupo in groupby(con.execute(q, (run, desde, desde)),
                             key=lambda r: r["ts"]):
        votado: dict[str, float] = {}
        canais: dict[str, dict[str, float]] = {}
        for r in grupo:
            alias = ALIAS.get(r["tag"])
            if alias is None:
                continue
            if r["canal"] == "voted":
                votado[alias] = r["valor"]
            else:
                canais.setdefault(alias, {})[r["canal"]] = r["valor"]
        yield {"ts": ts, "tags": votado, "canais": canais}


def alarmes_visiveis(con, run: str, ts: str) -> list[dict]:
    """Alarm history as known at ts, including only the peak observed so far."""
    alarms = [dict(r) for r in con.execute(
        """SELECT tag, tipo, ts_inicio, ts_fim, valor_pico, e_demanda
           FROM alarm_events WHERE run_id=? AND ts_inicio<=? ORDER BY ts_inicio""",
        (run, ts))]
    for a in alarms:
        if a["ts_fim"] is None or _futuro(a["ts_fim"], ts):
            # The stored peak covers the COMPLETE alarm, potentially the future.
            aggregate = "MIN" if a["tipo"] in ("LO", "LOLO") else "MAX"
            a["valor_pico"] = con.execute(
                f"""SELECT {aggregate}(valor) FROM series
                    WHERE run_id=? AND tag=? AND COALESCE(canal,'voted')='voted'
                    AND ts>=? AND ts<=?""",
                (run, a["tag"], a["ts_inicio"], ts)).fetchone()[0]
            a["fonte_pico"] = "extreme of voted series from alarm start through t_now"
            a["ts_fim"] = None
        a["tag"] = ALIAS.get(a["tag"], a["tag"])
        a["estado"] = "ativo" if a["ts_fim"] is None else "normalizado"
    return alarms


def context(con, run: str, ts: str) -> dict:
    """Contexto que a operação legitimamente conhece em `ts`.

    Alarmes já ocorridos, ordens de serviço, estado dos canais de sensor e
    APENAS os eventos de processo marcados como visíveis. É o material do
    indutor e do abdutor.
    """
    alarms = alarmes_visiveis(con, run, ts)

    wos = [dict(r) for r in con.execute(
        """SELECT wo_id, origem, tipo, equipamento_id, barreira_id, data_abertura,
                  data_fechamento, vencimento, status, falha_encontrada, descricao
           FROM work_orders WHERE run_id=? AND data_abertura<=? ORDER BY data_abertura""",
        (run, ts))]
    for w in wos:
        if _futuro(w["data_fechamento"], ts):
            w["data_fechamento"] = None
            w["status"] = "vencida" if _futuro(ts, w["vencimento"] or ts) else "aberta"
            # Free text is not versioned: the final narrative can describe a
            # repair/test that has not happened yet. Do not expose it early.
            w["descricao"] = "Narrative unavailable at t_now (no time-versioned source)"
            w["falha_encontrada"] = None

    chans = canais_visiveis(con, run, ts)

    # visivel_copiloto = 0 é gabarito e nunca sai daqui.
    ev = [dict(r) for r in con.execute(
        """SELECT ts, tipo, detalhe, tags_afetadas FROM process_events
           WHERE run_id=? AND visivel_copiloto=1 AND ts<=? ORDER BY ts""", (run, ts))]

    ativos = [dict(r) for r in con.execute(
        """SELECT equipamento_id, nome, classe, arranjo, mttf_ref_h, beta_ref,
                  intervalo_teste_h, pfd_projeto, barreiras FROM ativos""")]

    return scrub_obj({"ts": ts, "alarmes": alarms, "ordens_servico": wos,
                      "canais_sensor": chans, "eventos_operacionais": ev,
                      "ativos": ativos})


def pfd_confiabilidade(con, run: str, ts: str, equipamento: str,
                       origem_teste: str | None = None) -> dict:
    """PFD dinâmica de um ativo, a partir da camada de confiabilidade.

    Usa os parâmetros DECLARADOS no banco (`lambda_du`, `beta_ref`,
    `intervalo_teste_h`), não uma inversão do PFD de projeto. A diferença
    importa: a inversão embutia o intervalo de teste duas vezes e inflava a
    degradação. Verificado — com λ_DU·T/2 a fórmula 2oo3 da especificação
    reproduz o `pfd_projeto` do banco a menos de 2%.

    Três mecanismos, conforme a especificação:

      1. Creep entre testes: PFD₁(t) = λ_DU·t/2, com reset a cada teste
         funcional executado. Teste vencido deixa o creep passar do projeto.
      2. Redundância degradada: qualquer canal falho leva o grupo votado de
         2oo3 (3[(1−β)PFD₁]² + β·PFD₁) para 2oo2 (2·PFD₁), sem reconfiguração.
      3. Competência vencida: barreira humana com treinamento fora do prazo
         degrada para o valor de competência vencida.
    """
    a = con.execute("""SELECT equipamento_id, classe, arranjo, pfd_projeto,
                              intervalo_teste_h, beta_ref, lambda_du FROM ativos
                       WHERE equipamento_id=?""", (equipamento,)).fetchone()
    if a is None or a["pfd_projeto"] is None:
        return {"pfd": None, "motivos": ["asset has no declared design PFD"]}

    base = float(a["pfd_projeto"])
    T = float(a["intervalo_teste_h"] or 8760.0)
    agora = datetime.fromisoformat(ts)
    motivos: list[str] = []

    # 0 · falha conhecida e nao reparada num item de canal unico. A operacao
    # sabe (WO corretiva aberta, com falha encontrada), e um item 1oo1 falho
    # nao cumpre a funcao: PFD = 1 ate a WO fechar. Sem isto uma barreira que
    # acabou de falhar sob demanda continuaria "degradada" pelo relogio de
    # envelhecimento, que so conhece tempo desde o teste.
    arr0 = (a["arranjo"] or "1oo1").lower()
    if arr0 == "1oo1":
        falha = con.execute("""SELECT wo_id, data_abertura FROM work_orders
            WHERE run_id=? AND equipamento_id=? AND tipo='corretiva'
              AND falha_encontrada=1 AND data_abertura<=?
              AND (data_fechamento IS NULL OR data_fechamento>?)
            ORDER BY data_abertura LIMIT 1""", (run, equipamento, ts, ts)).fetchone()
        if falha:
            return {"pfd": 1.0, "pfd_projeto": base,
                    "motivos": [f"known unrepaired failure ({falha['wo_id']}, opened "
                                f"{falha['data_abertura']}): function unavailable, PFD = 1"]}

    # 1 · tempo desde o último teste funcional FECHADO
    ultimo = con.execute("""SELECT MAX(data_fechamento) FROM work_orders
        WHERE run_id=? AND equipamento_id=? AND data_fechamento IS NOT NULL
          AND tipo IN ('teste_funcional','calibracao','treinamento')
          AND data_fechamento<=?""", (run, equipamento, ts)).fetchone()[0]
    # O item tem programa de teste registrado ATE ts, neste run? A versao
    # anterior contava WO de qualquer tipo, de qualquer run e sem corte de
    # tempo: uma WO corretiva aberta em dezembro mudava o modelo do item ja em
    # janeiro. So WO de teste/calibracao/treinamento diz algo sobre o relogio.
    tem_registro = con.execute(
        """SELECT COUNT(*) FROM work_orders WHERE run_id=? AND equipamento_id=?
             AND tipo IN ('teste_funcional','calibracao','treinamento')
             AND data_abertura<=?""", (run, equipamento, ts)).fetchone()[0] > 0

    if not tem_registro:
        # Sem registro de teste o relogio assume o intervalo declarado cumprido
        # (t = T). Mas uma falha de canal CONHECIDA continua valendo: o grupo
        # votado cai a 2oo2 independentemente do calendario de teste. A versao
        # anterior retornava a PFD de projeto aqui e escondia a falha do canal A
        # em abril, porque o PT-007 so ganha WO de teste em 31/05.
        lam0 = a["lambda_du"]
        if lam0 and arr0 == "2oo3":
            conhecidos = con.execute("""SELECT COUNT(*) FROM sensor_channels
                WHERE run_id=? AND equipamento_id=? AND ts_deteccao IS NOT NULL
                  AND ts_deteccao<=? AND (ts_reparo IS NULL OR ts_reparo>?)""",
                (run, equipamento, ts, ts)).fetchone()[0]
            if conhecidos:
                pfd1 = float(lam0) * T / 2.0
                return {"pfd": min(1.0, 2 * pfd1), "pfd_projeto": base,
                        "motivos": ["no test record for this item; declared interval taken "
                                    "as met; voted group running 2oo2 without reconfiguration "
                                    f"— {conhecidos} detected channel failure(s) not repaired"]}
        # Item sem NENHUMA ordem de servico no conjunto de dados. Tratar isso
        # como "nunca testado desde o inicio do horizonte" seria inventar
        # degradacao a partir de dado ausente — o oposto da disciplina que a
        # mesa exige ("ausencia de registro nao e ausencia de evento"). O
        # conjunto simplesmente nao modela a manutencao destes itens, entao a
        # premissa honesta e a do projeto: intervalo declarado sendo cumprido.
        return {"pfd": base, "pfd_projeto": base,
                "motivos": ["no test record for this item; design PFD assumed "
                            "(declared interval taken as met)"]}

    # `origem_teste` existe para a analise de sensibilidade: quando o relogio
    # do modelo e o calendario discordam sobre o ultimo teste, a Fase A calcula
    # a PFD pelas duas leituras em vez de escolher uma.
    origem = origem_teste or ultimo or origem_do_horizonte(con, run)
    horas = max(0.0, (agora - datetime.fromisoformat(origem)).total_seconds() / 3600.0)
    motivos.append(
        (f"test overdue by {(horas-T)/24:.0f} d" if horas > T
         else f"{horas/24:.0f} d since the last test")
        + f" (interval {T/24:.0f} d)")

    lam = a["lambda_du"]
    beta = float(a["beta_ref"] or 0.05)
    arranjo = (a["arranjo"] or "1oo1").lower()

    if lam:                                    # item com taxa de falha declarada
        pfd1 = float(lam) * horas / 2.0        # PFD média de canal desde o teste
        # So falha CONHECIDA em ts. Contar a falha nao detectada punha no PFD
        # — e no texto do motivo — o gabarito do teste cego: a data de uma
        # falha que a operacao, por definicao, nao sabe que existe.
        falhos = con.execute("""SELECT channel_id, ts_deteccao FROM sensor_channels
            WHERE run_id=? AND equipamento_id=? AND ts_falha IS NOT NULL
              AND ts_deteccao IS NOT NULL AND ts_deteccao<=?
              AND (ts_reparo IS NULL OR ts_reparo>?)""",
            (run, equipamento, ts, ts)).fetchall()
        if arranjo == "2oo3" and not falhos:
            pfd = 3 * ((1 - beta) * pfd1) ** 2 + beta * pfd1
        elif arranjo == "2oo3":
            pfd = 2 * pfd1                     # sem reconfiguração: cai a 2oo2
            motivos.append(
                f"voted group running 2oo2 without reconfiguration — "
                f"{len(falhos)} detected channel failure(s) not repaired")
        else:
            pfd = pfd1 * 2.0                   # 1oo1: PFD média = λ·t/2 ·2 = λ·t
    else:
        # Sem taxa declarada (barreira humana): o projeto é o valor de partida.
        pfd = base

    # 3 · competência: treinamento vencido degrada a barreira humana
    if (a["classe"] or "") == "humano":
        venc = con.execute("""SELECT COUNT(*) FROM work_orders
            WHERE run_id=? AND equipamento_id=? AND tipo='treinamento'
              AND data_fechamento IS NULL AND vencimento<=?""",
            (run, equipamento, ts)).fetchone()[0]
        if venc:
            pfd = PFD_COMPETENCIA_VENCIDA
            motivos.append(
                f"competence renewal overdue and open; PFD assumed "
                f"{PFD_COMPETENCIA_VENCIDA} (model assumption, not declared in the asset)")
        else:
            pfd = base

    return {"pfd": min(1.0, pfd), "pfd_projeto": base, "motivos": motivos}


# PFD de projeto de cada barreira, do documento de bowtie de referência. É a
# PFD da malha inteira (detectar-decidir-agir), não a soma dos componentes.
ATIVOS_PFD = ["PT-007", "UZ-007", "OP-B2", "TT-009", "UZ-009", "OP-B4"]

# PFD de uma barreira humana com renovação de competência vencida.
#
# É PREMISSA DO MODELO, não dado do ativo: nenhuma coluna de `ativos` a declara,
# e ela não se deriva de `pfd_projeto`, de `lambda_du` nem do intervalo. Contra
# o projeto de 0,1 das barreiras humanas deste conjunto, corresponde a um degrau
# de +0,15 no dia do vencimento.
#
# Estava embutida como literal no meio do cálculo, e a mesa a encontrou por
# subtração: apontou que 81% da subida de frequência de um dos cenários vinha de
# "uma constante de +0,150000 que nenhum campo do dossiê declara", e mostrou que
# sem ela o horizonte inteiro ficaria dentro de critério. A crítica é
# procedente. O número não muda; o que muda é que ele passa a ser premissa
# VISÍVEL, confrontável pela mesa, em vez de um degrau sem fonte.
#
# ponytail: valor único para toda barreira humana. Vira coluna em `ativos`
# quando o time de segurança quiser diferenciar por função ou por criticidade
# do treinamento vencido.
PFD_COMPETENCIA_VENCIDA = 0.25


def premissas_do_modelo() -> dict:
    """Parâmetros que a camada de confiabilidade assume e o banco não declara.

    Vão no dossiê para que a mesa possa CONFRONTÁ-LOS. Uma curva herda toda
    premissa que entrou nela, e uma premissa invisível produz um número preciso
    cuja fragilidade ninguém consegue avaliar — que é a pior combinação num
    instrumento de decisão.
    """
    return {
        "human_barrier_pfd_with_overdue_competence": {
            "valor": PFD_COMPETENCIA_VENCIDA,
            "origem": "model assumption; not in the asset table",
            "efeito": "replaces the human barrier's design PFD from the training "
                      "due date, while the work order stays open",
        },
        "mean_channel_pfd_between_tests": {
            "formula": "lambda_du * t / 2",
            "origem": "standard hidden-failure model with periodic testing",
            "efeito": "grows from the last closed test; with no test record the "
                      "declared interval is taken as met",
        },
        "voted_group_without_reconfiguration": {
            "formula": "2oo3 = 3[(1-beta)*PFD1]^2 + beta*PFD1; with a detected "
                       "channel failure, 2oo2 = 2*PFD1",
            "origem": "arrangement declared in the asset; the fall to 2oo2 is an assumption",
            "efeito": "from the detected channel failure on, growth is linear in t, "
                      "without the beta factor",
        },
        "single_channel_item_with_known_failure": {
            "valor": 1.0,
            "origem": "model assumption; an open corrective work order with a "
                      "failure found on a 1oo1 item",
            "efeito": "the item is unavailable (PFD = 1) from the work order's "
                      "opening until it closes",
        },
        "items_without_test_records": {
            "origem": "model assumption",
            "efeito": "items with no test, calibration or training record are kept "
                      "at their design PFD; absence of a record is not treated as "
                      "absence of maintenance",
        },
    }


def eventos_de_registro(con, run: str, ate: str | None = None) -> list[dict]:
    """What the plant's records announce, dated when each fact becomes known.

    The streaming detector watches process series; the thesis mechanism —
    barrier erosion by the maintenance calendar — never shows up there. These
    events are the calendar and record side of the stream: a work order opened,
    a scheduled check falling overdue, a work order closed, a channel failure
    detected or repaired, and a visible process event. Each carries the instant
    at which operations would learn it, so no field lies in the future of that
    instant. `visivel_copiloto = 0` never enters.
    """
    ev: list[dict] = []
    for w in con.execute("SELECT * FROM work_orders WHERE run_id=?", (run,)):
        w = dict(w)
        ev.append({"ts": w["data_abertura"], "tipo": "wo_opened", "ref": w["wo_id"],
                   "item": w["equipamento_id"], "barreira": w["barreira_id"],
                   "wo_tipo": w["tipo"], "falha_encontrada":
                   None if _futuro(w["data_fechamento"], w["data_abertura"])
                   else w["falha_encontrada"]})
        if w["vencimento"] and not (w["data_fechamento"]
                                    and w["data_fechamento"] <= w["vencimento"]):
            ev.append({"ts": w["vencimento"], "tipo": "wo_overdue", "ref": w["wo_id"],
                       "item": w["equipamento_id"], "barreira": w["barreira_id"],
                       "wo_tipo": w["tipo"]})
        if w["data_fechamento"]:
            ev.append({"ts": w["data_fechamento"], "tipo": "wo_closed", "ref": w["wo_id"],
                       "item": w["equipamento_id"], "barreira": w["barreira_id"],
                       "wo_tipo": w["tipo"], "falha_encontrada": w["falha_encontrada"]})
    for c in con.execute("SELECT * FROM sensor_channels WHERE run_id=?", (run,)):
        c = dict(c)
        if c["ts_deteccao"]:
            ev.append({"ts": c["ts_deteccao"], "tipo": "channel_failure_detected",
                       "ref": c["channel_id"], "item": c["equipamento_id"]})
        if c["ts_reparo"]:
            ev.append({"ts": c["ts_reparo"], "tipo": "channel_repaired",
                       "ref": c["channel_id"], "item": c["equipamento_id"]})
    for e in con.execute("""SELECT ts, tipo, detalhe FROM process_events
                            WHERE run_id=? AND visivel_copiloto=1""", (run,)):
        ev.append({"ts": e["ts"], "tipo": "process_event", "ref": e["tipo"],
                   "detalhe": e["detalhe"]})
    ev = [e for e in ev if e["ts"] and (ate is None or e["ts"] <= ate)]
    ev.sort(key=lambda e: e["ts"])
    return scrub_obj(ev)


def limiares(con) -> list[dict]:
    """Limiares de alarme configurados, com a tag traduzida.

    Sem isto o agente nao consegue dizer "2906 kPa contra HIHI de 2900" — na
    calibracao o curador teve de inferir os limiares por interpolacao entre o
    instante do alarme e a serie, o que e engenhoso e desnecessario.
    """
    out = []
    for r in con.execute("SELECT * FROM alarm_config"):
        r = dict(r)
        alias = ALIAS.get(r["tag"])
        if alias is None:
            continue
        out.append({"tag": alias, "descricao": DESCRICAO.get(alias, (r["descricao"], ""))[0],
                    "unidade": r["unidade"], "lolo": r["lolo"], "lo": r["lo"],
                    "hi": r["hi"], "hihi": r["hihi"], "trip_sis": r.get("trip_sis")})
    return out


def series_window(con, run: str, t0: str, t1: str, step: int = 1,
                  pontos: int = 16) -> dict:
    """Serie da janela: resumo estatistico + pontos rotulados e decimados.

    Historico desta funcao, porque a licao nao e obvia e custou caro:

      · v1 — array de objetos por amostra. Funcionava, mas consumia 77% do
        prompt inteiro.
      · v2 — eixo de tempo implicito e valores num array puro de floats. 62%
        menor... e o modelo PAROU de terminar: cinco timeouts de 15 min contra
        275 s do formato anterior. Bissecao isolou o array como causa.
      · v3 — esta. O resumo evita recalculo de min/max/desvio, e os pontos
        voltam rotulados mas decimados.

    Em modelo de raciocinio, reduzir tokens nao e gratuito: pode custar a
    terminacao. Otimizacao de prompt se valida por conclusao, nao por bytes.
    """
    out: dict[str, dict] = {}
    for tag, alias in ALIAS.items():
        rows = con.execute(
            """SELECT ts, valor FROM series
               WHERE run_id=? AND tag=? AND COALESCE(canal,'voted')='voted'
                 AND ts BETWEEN ? AND ? ORDER BY ts""", (run, tag, t0, t1)).fetchall()
        rows = rows[::step]
        if not rows:
            continue
        v = [round(r["valor"], 3) for r in rows]
        n = len(v)
        media = sum(v) / n
        desvio = (sum((x - media) ** 2 for x in v) / n) ** 0.5
        imin, imax = v.index(min(v)), v.index(max(v))
        passo = 0
        if n > 1:
            passo = round((datetime.fromisoformat(rows[-1]["ts"]) -
                           datetime.fromisoformat(rows[0]["ts"])).total_seconds() / (n - 1))
        d = max(1, n // max(1, pontos))
        idx = sorted(set(list(range(0, n, d)) + [n - 1]))
        out[alias] = {
            "unidade": DESCRICAO.get(alias, ("", ""))[1],
            "de": rows[0]["ts"], "ate": rows[-1]["ts"],
            "amostras_na_janela": n, "passo_s": passo,
            "resumo": {"inicio": v[0], "fim": v[-1], "min": min(v), "max": max(v),
                       "ts_min": rows[imin]["ts"], "ts_max": rows[imax]["ts"],
                       "media": round(media, 3), "desvio": round(desvio, 4),
                       "delta": round(v[-1] - v[0], 3)},
            "trajetoria": [{"ts": rows[i]["ts"], "v": v[i]} for i in idx],
        }
    return out


# PFD de projeto de cada barreira, do documento de bowtie de referencia.
PFD_PROJETO_BARREIRA = {"B1": 0.01, "B2": 0.10, "B3": 0.01, "B4": 0.10}
NOME_BARREIRA = {
    "B1": "B1 High-pressure interlock",
    "B2": "B2 Manual operator action",
    "B3": "B3 High-temperature interlock",
    "B4": "B4 Manual operator action",
}


def componentes(con) -> dict[str, list[str]]:
    """Composição de cada barreira, LIDA do campo `barreiras` dos ativos.

    Derivada do banco em vez de escrita à mão porque escrevê-la à mão já
    produziu erro: PT-007 serve B1 **e** B2, e TT-009 serve B3 **e** B4 — o
    transmissor é compartilhado entre a barreira principal e a sua retaguarda.
    Tratá-las como independentes subestima o risco, porque uma falha do
    transmissor cega as duas ao mesmo tempo. É a falha de causa comum que o
    próprio documento de bowtie aponta como principal fraqueza de projeto.
    """
    import json as _json
    out: dict[str, list[str]] = {}
    for r in con.execute("SELECT equipamento_id, barreiras FROM ativos"):
        for b in _json.loads(r["barreiras"] or "[]"):
            out.setdefault(b.split(".")[-1], []).append(r["equipamento_id"])
    return out


def pfd_barreira(con, run: str, ts: str, barreira: str,
                 origens: dict[str, str] | None = None) -> dict:
    """PFD dinâmica de uma barreira: SOMA das PFDs dos seus componentes.

    Numa malha em série detectar-decidir-agir, a barreira falha se qualquer elo
    falhar; para PFDs pequenas, a probabilidade da união é a soma.

    Foi a segunda tentativa. A primeira usava o pior componente como
    *multiplicador* da PFD de projeto da barreira, e levava B2 a 1,0 — porque
    um transmissor 34× pior multiplicava uma barreira cujo valor é dominado
    pelo operador, quando o transmissor contribui ~1e-4 dos 0,1 dela. O erro
    era de composição, não de aritmética.

    A PFD de projeto reportada é a soma dos componentes no estado de projeto,
    não o valor do documento de bowtie: são grandezas diferentes, e a
    divergência entre elas é informação — fica em `pfd_documento`.
    """
    comps = componentes(con).get(barreira, [])
    atual = proj = 0.0
    detalhe, motivos = [], []
    for eq in comps:
        r = pfd_confiabilidade(con, run, ts, eq, (origens or {}).get(eq))
        if r["pfd"] is None or not r.get("pfd_projeto"):
            continue
        atual += r["pfd"]
        proj += r["pfd_projeto"]
        fator = r["pfd"] / r["pfd_projeto"]
        detalhe.append({"item": eq, "pfd": r["pfd"], "pfd_projeto": r["pfd_projeto"],
                        "fator": round(fator, 2)})
        if fator > 1.1:
            motivos.append(f"{eq}: {fator:.1f}x - " + "; ".join(r["motivos"]))
    return {"pfd": min(1.0, atual), "pfd_projeto": proj,
            "pfd_documento": PFD_PROJETO_BARREIRA[barreira],
            "degradacao": round(min(1.0, atual) / proj, 2) if proj else 1.0,
            "componentes": detalhe, "motivos": motivos,
            "nome": NOME_BARREIRA[barreira]}


def pfd_tags(con, run: str, ts: str) -> dict[str, float]:
    """PFD dinâmica de cada ativo, publicada como tag.

    Vira tag em vez de virar caso especial na ponte por dois motivos: aparece
    na tela de Aquisição junto com as leituras de processo, e a curva do BowTie
    passa a ser identidade — a evidência de manutenção entra pelo mesmo caminho
    que a variável de processo, sem via privilegiada.
    """
    out = {}
    for eq in ATIVOS_PFD:
        r = pfd_confiabilidade(con, run, ts, eq)
        if r["pfd"] is not None:
            out[f"{PREFIX}PFD_{eq.replace('-', '_')}"] = round(r["pfd"], 8)
    for b in PFD_PROJETO_BARREIRA:
        out[f"{PREFIX}PFD_{b}"] = round(pfd_barreira(con, run, ts, b)["pfd"], 8)
    return out


def publish(snap: dict) -> Path:
    """Grava as leituras mascaradas no contrato de tags que a ponte já lê."""
    tags = {}
    if TAGS.exists():
        try:
            tags = json.loads(TAGS.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            tags = {}
    tags = {k: v for k, v in tags.items() if not k.startswith(PREFIX)}
    tags.update(snap["tags"])
    TAGS.parent.mkdir(parents=True, exist_ok=True)
    TAGS.write_text(json.dumps(tags, indent=2, ensure_ascii=False), encoding="utf-8")
    return TAGS


def audit(con, run: str) -> dict:
    """Prova de que o mascaramento cobre tudo que sai deste módulo."""
    ts = con.execute("SELECT MAX(ts) FROM series WHERE run_id=?", (run,)).fetchone()[0]
    payload = json.dumps({"snapshot": snapshot(con, run, ts),
                          "contexto": context(con, run, ts)}, ensure_ascii=False)
    hits = _FORBIDDEN_RE.findall(payload)
    oculto = con.execute(
        "SELECT COUNT(*) FROM process_events WHERE run_id=? AND visivel_copiloto=0",
        (run,)).fetchone()[0]
    return {"run": run, "bytes_expostos": len(payload),
            "termos_proibidos_encontrados": hits,
            "eventos_ground_truth_retidos": oculto,
            "tags_publicadas": sorted(snapshot(con, run, ts)["tags"])}


# ───────────────────────────────────────────────────────────────── CLI

def main() -> None:
    ap = argparse.ArgumentParser(description="Driver do teste cego (planta anônima)")
    ap.add_argument("--run", default="RUN_A")
    ap.add_argument("--list", action="store_true", help="lista os runs disponíveis")
    ap.add_argument("--at", help="publica as leituras vigentes neste timestamp")
    ap.add_argument("--context", action="store_true", help="imprime o contexto mascarado")
    ap.add_argument("--audit", action="store_true", help="verifica o mascaramento")
    ap.add_argument("--replay", action="store_true", help="reproduz a janela do episódio")
    ap.add_argument("--speed", type=float, default=60.0, help="segundos de processo por segundo real")
    args = ap.parse_args()

    con = connect()
    if args.list:
        for r in runs(con):
            print(f"  {r['run_id']}  {r['n']:>6} amostras  {r['t0']} → {r['t1']}")
        return
    if args.audit:
        print(json.dumps(audit(con, args.run), indent=2, ensure_ascii=False))
        return
    if args.context:
        print(json.dumps(context(con, args.run, args.at or
              con.execute("SELECT MAX(ts) FROM series WHERE run_id=?",
                          (args.run,)).fetchone()[0]), indent=2, ensure_ascii=False))
        return
    if args.replay:
        import time
        stamps = [r[0] for r in con.execute(
            "SELECT DISTINCT ts FROM series WHERE run_id=? ORDER BY ts", (args.run,))]
        stamps = stamps[-4300:]                     # janela do episódio
        print(f"reproduzindo {len(stamps)} amostras de {args.run} a {args.speed}×")
        for i, ts in enumerate(stamps):
            publish(snapshot(con, args.run, ts))
            if i % 60 == 0:
                print(f"  {ts}")
            time.sleep(5.0 / args.speed)
        return

    snap = snapshot(con, args.run, args.at)
    snap["tags"].update(pfd_tags(con, args.run, snap["ts"]))
    p = publish(snap)
    print(f"{args.run} @ {snap['ts']} → {p}")
    for k, v in sorted(snap["tags"].items()):
        print(f"  {k:32} {v}")


if __name__ == "__main__":
    main()
