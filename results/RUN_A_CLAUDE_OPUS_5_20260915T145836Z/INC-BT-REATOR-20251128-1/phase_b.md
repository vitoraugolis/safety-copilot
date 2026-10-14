---
incident_id: INC-BT-REATOR-20251128-1
bowtie_id: BT-REATOR
opened_at: 2025-11-28T00:00:00
engine: conventional
status: action_required
urgency: planned
confidence: medium
---

# Treat the T1 design basis as unverified from this instant and restore the three overdue maintenance items on PT-007 / OP-B2 before sustained operation at the new load, because the operating condition changed with no revalidation while the pressure voted group runs 2oo2 with a frozen channel.

## Fact

Three triggers fired at the same instant, `identidade.gatilho`:

1. `record:process_event:operating_condition_change` at 2025-11-28T00:00:00 — mode "campanha padrao", `carga_pct` 15, `escala_setpoints_alimentacao` 1.15, affecting FIT-1001 and PIT-7001 (`a2_estado_atual.eventos_operacionais[0]`). `a2_estado_atual.regime.revalidacao_registrada` = false.
2. `alarme:PIT-7001:LO` — LO (2550 kPa) crossed downward, value at `a2_estado_atual.alarmes_ativos[0].valor_pico`, exceedance in `a2_estado_atual.margem.PIT-7001.limiares_ja_cruzados`, `e_demanda` = 0, active 0.0 min.
3. `discrepancia:PIT-7001` — spread against limit in `a2_estado_atual.discrepancia_canais[0]` (190.5 kPa against 17.5 kPa), divergent channel B by majority.

Operating mode: standard campaign, load changed at `t_now`. No demand on any barrier is recorded (`a2_estado_atual.demandas.B1.demandada` = false).

**Data quality.** The rate ladder is empty: `a2_estado_atual.escada_de_taxas.lacuna` = "serie insuficiente na janela", so no rate is available for any tag and every `tempo_ate_limiar_min` is null. Per the honesty rule "do not conclude from an instantaneous value", every margin statement below is a distance without a rate, and no time-to-target exists at `t_now`. The post-change regime is not yet established (`a2_estado_atual.regime.regime_depois` = null, `deslocamento_kpa` = null): the change and the reading are simultaneous, so the magnitude of the regime shift is not demonstrated. One channel of the voted group is frozen (`a2_estado_atual.grupo_votado.congelamento`). The crossing itself is reproducible from the voted series and the alarm record, so the B1 gate is passed; the inference below is bounded by the missing rate, not by the crossing.

**What this trigger establishes.** This analysis opens the stream for BT-REATOR; there is no earlier analysis to compare against. What the trigger changed in the plant's knowledge is observability: channel B has been flat at 2708.42 kPa since about 2025-08-29 (`a2_estado_atual.grupo_votado.congelamento.parado_desde_aprox`), 0.05 kPa from the pre-change regime median (`.diferenca_para_o_regime`). While the plant sat at that regime the freeze was invisible in the spread; the load change moved A and C and exposed it. The freeze did not cause the pressure change — it was masked by the old regime and is unmasked by the new one.

## Scenario and mechanism

Qualitative chain, pathway T1 (`diagrams/BT-REATOR.txt`):

`T1 loss of stream 1 feed → B1 automatic high-pressure interlock → B2 manual operator action → top event "loss of reactor control" → (mitigation not in scope of phase A) → consequence not declared`

The threat is not manifest at `t_now`: FIT-1001 reads above the design base-case feed of 0.252 kscmh (`a2_estado_atual.margem.FIT-1001.valor`; design basis §2), and the pressure excursion is downward, away from the T1 escalation direction. What this analysis addresses is the erosion of the two T1 barriers, not an active demand.

Quantitative chain, link by link:

| Link | Source | Strength |
|---|---|---|
| PT-007.B failed detected, unrepaired since 2025-08-29T00:30:00, WO-RUN_A-CH-B open | `a2_estado_atual.canais`, `ordens_servico` | demonstrated |
| Failure mode is a frozen channel, not drift: B sd 0.2 against A 14.22 and C 14.16 over the 30-day window, B flat inside a ±1.5 kPa band at the old regime value | `a2_estado_atual.grupo_votado.estatistica_por_canal`, `.congelamento` | demonstrated |
| Group therefore runs 2oo2 without reconfiguration → channel PFD grows linearly from detection | `premissas_do_modelo.voted_group_without_reconfiguration` (model assumption, not asset data) | inferred |
| PT-007 item multiplier 34.05× against design | `a1_base_de_projeto.barreiras[*].c2.componente_pior` | demonstrated (under the model clock; see contradiction) |
| B1 PFD design → current, ×1.11; B2 ×2.27 | `a1_base_de_projeto.barreiras[*].pfd_projeto`, `.pfd_atual`, `.c2.multiplicador_barreira` | demonstrated |
| OP-B2 at 0.25 drives 92 % of B2's PFD | `a1_base_de_projeto.barreiras[1].c2.elemento_dominante`; value is `premissas_do_modelo.human_barrier_pfd_with_overdue_competence` | inferred (assumed PFD, not read from the asset) |
| Top event frequency design → current, ×2.07 conventional | `motores.conventional.projeto/atual/razao` | demonstrated (given the PFD inputs above) |
| Consequence / receptor / tolerability | not present in any phase A field | undetermined |

Temporal coincidence between the condition change and the LO alarm is recorded; with no post-change regime and no rate, it is not established as causal.

## Analysis

### 1. Bowtie

**B1 — high-pressure interlock: `degraded`.** Not demanded up to `t_now` (`a2_estado_atual.demandas.B1`), so no observation settles the state and the PFD governs. The barrier multiplier is small (`c2.multiplicador_barreira` 1.11×) precisely because the dominant element is XV-1001 at 48 % of the total (`c2.elemento_dominante`), not the sensor — C2's two multipliers disagree by a factor of ~31, and reporting only the component's 34.05× would over-state, reporting only the barrier's 1.11× would hide the loss of redundancy. What makes it `degraded` rather than `healthy` is not the multiplier: it is that the requirement is no longer demonstrated. The functional test of the interlock is 181 d overdue and not executed (WO-RUN_A-TEST), so nothing currently verifies the detect–decide–act path; and the voted group is known degraded (C4) with a 90-day repair backlog (`a3_cruzamentos[C4].relogio`). The frozen channel has a directional consequence for the demand trigger: B's reading is stuck at 2708.42 kPa, below HIHI (2800, `a1_base_de_projeto.limiares`), so on a genuine T1 escalation B cannot contribute to the vote and satisfaction of "voted PIT-7001 ≥ HIHI" rests on A and C together. Not `critical`: the function is not removed, isolated or bypassed, and the majority pair is live.

**B2 — manual operator action: `degraded`.** PFD ×2.27, dominated by OP-B2 at 92 %, with the competence renewal 121 d overdue and open (WO-RUN_A-TRAIN). The 0.25 figure is a model assumption, not an asset value — the erosion of B2 is demonstrated by the overdue training record; its magnitude is assumed. C3 cannot be evaluated (`a3_cruzamentos[C3].nao_se_aplica` — no demand, real window not measurable), and because C1 has fired, the 67-min tolerable delay and the 162-min HIHI→SIS window of design basis §5 must not be cited as current. The design basis states that all of B2's margin is perception and decision, none execution; that margin is a property of the operating condition, and the operating condition just changed without revalidation. So B2 carries two independent degradations — an assumed-higher human PFD, and an unknown window — and the second is a gap, not a number to adjust (C3 rule; risk-analysis-reference §5).

**Dependencies (C6).** Detection independent (PT-007 versus ZT-1001), actuation shared (XV-1001 and VLV-006): `a3_cruzamentos[C6].declared_independence`. Joint credit must not multiply the two PFDs, and no IPL/SIL credit is claimed here — none is documented in any phase A field. Note a divergence between sources: the asset composition of B2 lists PT-007 among its components (`a1_base_de_projeto.barreiras[1].componentes`, and `a3_cruzamentos[C6].shared_items.PT-007` = [B1, B2]), while the design basis §4 declares B2's detection to be ZT-1001 and its trigger to be a command-versus-position discrepancy. Both readings come from the supplied material and disagree; the practical effect is that the current PFD model already propagates the PT-007 degradation into B2, which is conservative if the design basis is right and correct if the asset table is right. Either way the direction of the finding is unchanged; the record should be reconciled.

**Declared side effect of B1's action (C6).** Actuation closes the A+C feed valve, which is the actuator of the LIC-8001 level cascade; inventory control is lost, level goes to about −2.5 % and a low-level trip follows roughly 1 h later. This is a declared secondary consequence, not a failure of B1 against the T1 top event (design basis §4, §5). It constrains how the overdue functional test may be executed on line.

**Pathway 2 (temperature, B3/B4)** was not assessed in phase A; the engines were fed `motores.pfd_atual.B3` and `.B4` at their diagram values, i.e. design. The shift of pathway share from 70.1 % to 85.6 % (`motores.conventional.*.pathways`) therefore reflects T1 erosion against an unexamined pathway 2, and does not demonstrate that pathway 2 is intact.

### 2. Process

Trajectory cannot be analysed: the rate ladder is empty (`envelope.lacuna`), so C7 delivers distance without rate for every tag and every `tempo_ate_limiar_min` is null. Against the declared upward targets, PIT-7001 sits 231.75 kPa below HI, 381.75 below the SIS trip (`alarm_config.trip_sis`) and 481.75 below the model physical limit (design basis §3) — all uncrossed (`a3_cruzamentos[C7].comparado.PIT-7001`). TIT-9001, LIT-8001 and TIT-2101 are below their HI thresholds with no target crossed.

Two qualifications matter more than those distances:

- **The excursion is downward and the margin ladder looks upward.** LO is crossed; LOLO is declared at 2450 kPa (`a1_base_de_projeto.limiares`), and phase A carries no distance or time to it, because `limiar_a_frente` is computed toward HI. With no rate, neither distance nor time to LOLO can be stated here without fabricating a figure. This is a gap in the decision-relevant direction.
- **No rate means no persistence judgement.** The alarm has been active 0.0 min. An alarm one sample old with an unknown rate is not evidence of a stable condition; it is an absence of evidence either way.

Precursor coherence: A and C agree within 5.79 kPa (3× the design noise of 1.93 kPa, design basis §3) and both fell; B did not move. Coherence between the pressure fall and the recorded feed setpoint scaling of 1.15 at the same instant is plausible but is not demonstrated by any field — `regime_depois` is null.

### 3. Context

**Design basis and envelope (C1).** `a3_cruzamentos[C1].resultado` records an operating-condition change with no revalidation. That is explicitly an invalidation trigger of design basis §7 ("a recorded change of the operating condition of Section 2 … without subsequent revalidation of the windows"). Consequence: from this instant the windows of §5 — 202 min HI→SIS, 162 min HIHI→SIS, 67 min tolerable delay for B2 — are unverified and must not be quoted as the plant's current actuation windows. §7 states that when invalidated, the real window "is not known and must be derived from current data". No escalation window exists at `t_now` from which to derive it, and the design rate of 1.1 kPa/min has nothing to be compared against (`a3_cruzamentos[C1].comparado.rate_ladder` empty). This is the single most consequential finding of the trigger, and it is independent of every PFD in the report.

**Mechanical integrity and testing.** Three items are open against the T1 barriers, all traceable in the calendar: WO-RUN_A-TEST (interlock functional test, 181 d overdue, never executed), WO-RUN_A-TRAIN (OP-B2 competence, 121 d overdue), WO-RUN_A-CH-B (channel B corrective, open, detection 2025-08-29T00:30:00). WO-RUN_A-CH-A closed with a finding on channel A on 2025-04-02 — a second discrepancy on the same transmitter group within the horizon. Two channel discrepancies in eight months on one voted group, plus an unexecuted functional test on the same asset, is a pattern worth a separate integrity review of PT-007; with n = 2 it is a signal, not a demonstrated systemic failure.

**Recorded contradiction, not resolved.** `a2_estado_atual.contradicoes[0]`: the PFD creep clock says 331 d since the last test (interval 365 d), the maintenance calendar says the functional test is 181 d overdue. The sensitivity is carried in the same field: item PFD ratio 1.65×, but barrier ratios 1.07× (B1) and 1.01× (B2). The decision is therefore insensitive to which clock governs — the barrier conclusions above hold under both. Which clock is authoritative remains a team decision and a data-governance defect.

**Management of change.** A load and feed-setpoint change with no revalidation recorded belongs to MOC triage (risk-analysis-reference §4) and is simultaneously the C1 invalidation trigger. Whether an MOC was raised cannot be determined: no MOC record appears in any phase A field. Absence of a record is a gap, not a non-conformance.

**Human and organisational factors.** The overdue competence renewal is a task-and-organisation finding (an automatically opened work order left unexecuted for 121 d), not operator fault. The design basis is explicit that B2's entire margin is perception and decision; competence overdue and window unknown erode the same margin from two directions.

**C5 gap.** The single named gap is whether a common cause affects the agreeing pair A and C. The majority already identifies B as divergent, so "which channel is correct" is not open; what is open is a shared error in A and C. External check: an independent field measurement of vessel pressure.

**C8.** T1 is not classified; the removal test of design basis §6 was not executed. With the threat not manifest at `t_now`, no behavioural evidence is available either. The success criterion to be applied to B1/B2 in a future episode therefore remains undetermined.

## Risk judgement

Top event frequency, both engines, from `motores`:

- conventional: `motores.conventional.projeto.evento_topo_por_ano` → `motores.conventional.atual.evento_topo_por_ano`, ratio `motores.conventional.razao` = 2.07×; pathway T1 share 70.1 % → 85.6 %.
- fuzzy: `motores.fuzzy.projeto/atual`, ratio 1.98×, label `Moderate` → `Moderate`.

The conventional figure carries the magnitude; the fuzzy figure carries the propagation of linguistic uncertainty, and the two are not checks on each other (SKILL.md, "The fuzzy engine"). The unchanged fuzzy label is not a statement that nothing changed: a doubling sits inside one linguistic term. The label qualifies a frequency, not a barrier state and not risk.

**Consequence and tolerability.** No consequence severity, receptor or tolerability criterion exists in any supplied field or in the design basis. Therefore: **barrier erosion demonstrated (T1 barrier PFDs ×1.11 and ×2.27, top event frequency ×2.07, design basis envelope invalidated); risk tolerability not determined.** This is a result, not a failure of the analysis, and it cannot be closed by this report — it requires the facility's approved criteria.

**Uncertainty.** Three items bound confidence: (i) OP-B2's 0.25 is a model assumption, and it drives 92 % of B2's PFD, so B2's current figure and roughly the whole ratio above inherit that assumption; (ii) no rate is available anywhere, so no time-to-target and no trajectory judgement exists; (iii) the actuation window under the new condition is unknown, not merely uncertain. The 2oo2 fall-back is itself an assumption (`premissas_do_modelo.voted_group_without_reconfiguration`). Overall confidence is medium — bounded by the weakest decisive link, the assumed human PFD.

**Urgency: planned.** Plausible consequence is unquantified but the event is not proximate: no demand on any barrier, the threat is not present, the excursion is away from the T1 direction, and all upward targets are uncrossed by wide distances. Both T1 barriers remain functional (`degraded`, not `critical`), so no safety-limit escalation criterion of SKILL.md is met. The exposure horizon is the C4 clock — 90 d of backlog on a detected channel failure, with the functional test 181 d overdue — which is a calendar problem, not a control-room problem. What makes it non-routine is that the plant is now operating outside the validated envelope: if T1 occurs before revalidation, the available time is unknown.

## Recommendation

**Immediate containment (today, no plant action by this analysis):**
- Notify operations and the process safety authority that design basis §7 is triggered: the §5 windows (202 / 162 / 67 min) are unverified from 2025-11-28T00:00:00 and must not be used in shift briefings or emergency response assumptions until revalidated.
- Brief the shift that PT-007 channel B is frozen at 2708.42 kPa and is not a valid indication, that the group is running 2oo2 on A and C, and that B will not contribute to a high-pressure vote.
- Take an independent field measurement of vessel pressure to close the C5 gap (common cause in the agreeing pair A/C). This is the one external check that the current instrumentation cannot substitute.
- Restore process-data capture so a rate can be computed for PIT-7001: at present no time-to-target exists for any declared target, in either direction.

**Restoration (engineering before administrative, per the response hierarchy):**
- Close WO-RUN_A-CH-B: repair or replace PT-007 channel B and retest; restore 2oo3. This removes the dominant driver of the 34.05× item multiplier and restores the arbiter.
- Execute WO-RUN_A-TEST, the B1 interlock functional test, 181 d overdue. **C6 constraint:** a test that actuates the final element closes the A+C feed valve and destroys LIC-8001 inventory control, with a low-level trip about 1 h later; schedule accordingly, or use a test method that exercises detect and logic without full actuation, and record which coverage was achieved.
- Execute WO-RUN_A-TRAIN, OP-B2 competence renewal, 121 d overdue. This is what retires the 0.25 assumption; until it is closed, B2's current PFD is assumed, not measured.
- Re-run the engines after each closure and record the new pair against `motores`.

**Definitive solution:**
- Revalidate the barrier windows under the new operating condition, following `references/producing-a-design-basis.md` steps 2–6, and add the alternative condition to the sensitivity table of the design basis. Without this, C1 has nothing to compare against on the next trigger.
- Run the threat-removal test (design basis §6) to classify T1 under C8 and fix the success criterion that will be applied to B1/B2.
- Raise MOC triage for the load / feed-setpoint change, including the requirement that a base-case change forces window revalidation before it is accepted as the new normal.
- Reconcile the B2 composition record (PT-007 in the asset table versus ZT-1001 in design basis §4) and confirm that the declared demand trigger — command-versus-position discrepancy on ZT-1001 — is instrumented and observable; a barrier whose demand cannot be observed cannot be credited or audited (risk-analysis-reference §6).
- Resolve the PFD-clock rule (model clock versus maintenance calendar) so that the two sources stop disagreeing; the barrier-level sensitivity is 1.07× / 1.01×, so this is a governance fix, not a risk fix.
- Review PT-007 as a repeat offender: two channel discrepancies within the horizon plus an unexecuted functional test on the same asset.

**Suggested owner / deadline:** operations shift lead for the containment items, today; maintenance planning for WO-RUN_A-CH-B and WO-RUN_A-TEST, with a date set by the facility's backlog rule for a degraded voted group; training function for WO-RUN_A-TRAIN; process safety engineering for revalidation, MOC triage and the C8 campaign. Deadlines are to be set by the accountable functions — none is declared in the supplied material.

**Expected return / leading indicator:** PT-007 spread back inside the 17.5 kPa limit with three channels moving together (sd of each channel comparable with A and C, not 0.2); B1 and B2 PFDs recomputed against `pfd_projeto`; the conventional top event frequency returning toward `motores.conventional.projeto.evento_topo_por_ano`. Leading indicators: age of the oldest overdue safety-critical work order on a T1 asset, and days a voted group has run without reconfiguration.

**Closure criteria:** channel B repaired and post-repair tested against the frozen-reading failure mode; B1 functional test executed with its coverage recorded; OP-B2 competence renewed and the 0.25 assumption replaced by asset data; the design basis windows revalidated under the current operating condition and the §7 invalidation cleared; MOC dispositioned; the C5 field check documented; the PFD-clock contradiction resolved. The pressure returning to band does not close this occurrence.

**Residual risk / accepting authority:** not determined — no tolerability criterion or consequence severity exists in the supplied basis. Acceptance belongs to the facility's designated risk authority.

**Human decision:** pending

## Evidence and assumptions

- [demonstrated] `identidade.gatilho` / `a2_estado_atual.eventos_operacionais[0]`, 2025-11-28T00:00:00 — operating-condition change (load 15, feed setpoint scale 1.15) with `regime.revalidacao_registrada` = false; triggers design basis §7 invalidation.
- [demonstrated] `a2_estado_atual.grupo_votado.congelamento` + `.estatistica_por_canal` — channel B flat at 2708.42 kPa (sd 0.2) since ~2025-08-29 against A/C sd ≈ 14.2; failure mode is a frozen reading stuck at the pre-change regime (difference 0.05 kPa), which is why the freeze became visible only when the regime moved.
- [demonstrated] `a2_estado_atual.canais` + `ordens_servico.WO-RUN_A-CH-B` — PT-007.B failed detected, unrepaired; C4 clock = 90 d repair backlog.
- [demonstrated] `ordens_servico.WO-RUN_A-TEST` (181 d overdue) and `.WO-RUN_A-TRAIN` (121 d overdue) — B1 interlock test never executed; OP-B2 competence lapsed.
- [demonstrated] `a1_base_de_projeto.barreiras[*].c2` — B1 barrier ×1.11 with dominant element XV-1001 (48 %); B2 barrier ×2.27 with dominant element OP-B2 (92 %); worst component PT-007 ×34.05 in both.
- [demonstrated] `motores.conventional` and `motores.fuzzy` — top event frequency design → current, ratios 2.07× and 1.98×; fuzzy label `Moderate` → `Moderate`; T1 share 70.1 % → 85.6 % (conventional).
- [demonstrated] `a3_cruzamentos[C6]` / design basis §4 — detection independent, actuation shared (XV-1001, VLV-006); joint credit must not multiply; B1 actuation destroys LIC-8001 inventory control with a low-level trip ≈ 1 h later.
- [corroborated] `a2_estado_atual.grupo_votado.concordancia_no_ultimo_instante` and `a2_estado_atual.discrepancia_canais[0].desvio_contra_mediana` — A and C agree within 5.79 kPa, B divergent by majority; the record (WO-RUN_A-CH-B) and the reading agree on which channel is faulty.
- [inferred] `premissas_do_modelo.human_barrier_pfd_with_overdue_competence` = 0.25 — model assumption, not asset data; drives 92 % of B2's current PFD and hence most of the ratio in the risk judgement.
- [inferred] `premissas_do_modelo.voted_group_without_reconfiguration` — the fall to 2oo2 is an assumption declared by the model, not a recorded reconfiguration.
- [undetermined] `a2_estado_atual.escada_de_taxas.lacuna` / `envelope.lacuna` — "serie insuficiente na janela": no rate for any tag, no time to any target, in either direction; distance and time to LOLO (2450 kPa, `a1_base_de_projeto.limiares`) not carried by phase A.
- [undetermined] `a3_cruzamentos[C3]` — real actuation window not measurable, no demand on B1; window compression for the human barrier cannot be quantified and must not be converted into an adjusted PFD.
- [undetermined] `a3_cruzamentos[C5]` — common cause in the agreeing pair A/C; external check = independent field measurement of vessel pressure.
- [undetermined] `a3_cruzamentos[C8]` / design basis §6 — T1 persistent-versus-removable classification not executed; success criterion for the barriers consequently unfixed.
- [undetermined] `a2_estado_atual.contradicoes[0]` — PFD creep clock (331 d) versus maintenance calendar (181 d overdue); item ratio 1.65×, barrier ratios 1.07× / 1.01×; decision insensitive, governance defect open.
- [undetermined] B2 composition — `a1_base_de_projeto.barreiras[1].componentes` lists PT-007 while design basis §4 declares ZT-1001 as B2's detection; the two supplied sources disagree and the record needs reconciliation.
- [undetermined] consequence, receptor, tolerability criterion, IPL/SIL credit — absent from every supplied field; no value substituted.
- [undetermined] pathway 2 (B3/B4) — not assessed in phase A; engine inputs `motores.pfd_atual.B3/.B4` equal their diagram values, so the pathway-share shift does not demonstrate that pathway 2 is intact.