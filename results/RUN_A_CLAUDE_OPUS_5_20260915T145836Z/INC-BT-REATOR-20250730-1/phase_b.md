---
incident_id: INC-BT-REATOR-20250730-1
bowtie_id: BT-REATOR
opened_at: 2025-07-30T00:00:00
engine: conventional
status: action_required
urgency: planned
confidence: medium
---

# Execute the two overdue safety-critical work orders on pathway T1 — OP-B2 competence renewal (`WO-RUN_A-TRAIN`) and the B1 functional test (`WO-RUN_A-TEST`, 60 d overdue) — because barrier erosion by the maintenance calendar has raised the modelled top event frequency by `motores.conventional.razao` with the plant quiet and no process signal to show it.

## Fact

- **Trigger:** `identidade.gatilho` — `record:wo_opened:WO-RUN_A-TRAIN` and `record:wo_overdue:WO-RUN_A-TRAIN`, both at `t_now = 2025-07-30T00:00:00`, item `OP-B2`, barrier `reator.T1.B2` (periodic competence training, `a2_estado_atual.ordens_servico[WO-RUN_A-TRAIN]`, `status: vencida`, `vencida_ha_dias: 0`).
- **This is the opening analysis of the stream.** What the trigger changed against the design baseline: the human element of B2 moved from its design PFD to the model's overdue-competence value (`premissas_do_modelo.human_barrier_pfd_with_overdue_competence`, marked *model assumption, not asset data*), taking barrier B2 from `a1_base_de_projeto.barreiras[B2].pfd_projeto` to `.pfd_atual` (`a3_cruzamentos[C2].comparado.B2.barrier_multiplier`), and the T1 pathway's share of the top event from `motores.conventional.projeto.pathways[0].contribuicao_pct` to `motores.conventional.atual.pathways[0].contribuicao_pct`.
- **Process state:** no active alarms (`a2_estado_atual.alarmes_ativos` empty); no process events (`eventos_operacionais` empty); no operating-condition change (`a2_estado_atual.regime.mudanca: null`). No demand on B1 up to `t_now` (`a2_estado_atual.demandas.B1.demandada: false`). Values of `PIT-7001`, `TIT-9001`, `LIT-8001`, `FIT-1001` in `a2_estado_atual.margem` sit at or near the declared base case (design basis §2); no threshold crossed.
- **Data quality:** no measurable rate in the window — `a2_estado_atual.escada_de_taxas.lacuna = "serie insuficiente na janela"`, and every `taxa_por_min` in `a2_estado_atual.margem` is null. The crossing that opened this analysis is a **record event**, not a process crossing, and is reproducible by inspection of the work-order table. Voted group `PT-007` reads consistently (`a2_estado_atual.grupo_votado`, spread `a2_estado_atual.discrepancia_canais[0].spread` against limit 17.5 kPa; no divergent channel by majority).

## Scenario and mechanism

Qualitative chain (pathway T1, `diagrams/BT-REATOR.txt`):

`T1 loss of stream 1 feed → B1 automatic high-pressure interlock → B2 manual operator action → top event "loss of reactor control" → (mitigating barriers not modelled in this diagram) → consequence/receptor not declared`

Quantitative chain:

1. **Initiating frequency** — `Perda de alimentacao da corrente 1`, 0.5/yr, read from the diagram (`diagrams/BT-REATOR.txt`). *demonstrated* (diagram reading).
2. **No process link.** `FIT-1001` at `a2_estado_atual.margem.FIT-1001.valor`, no threshold ahead, no rate. Nothing in the process layer contributes to this trigger. *demonstrated*.
3. **Degradation link — maintenance calendar, not process.** `WO-RUN_A-TRAIN` overdue and open on the human element of B2 → OP-B2 PFD raised by the model (`premissas_do_modelo.human_barrier_pfd_with_overdue_competence`), dominating the barrier at `a3_cruzamentos[C2].comparado.B2.dominant_element.fracao_do_total`. *inferred* — the PFD value is an assumption, the overdue state is a record.
4. **Second degradation link.** `WO-RUN_A-TEST` (`teste_funcional`, `PT-007`, barrier `reator.T1.B1`) overdue 60 d and not executed. The barrier multiplier for B1 is `a3_cruzamentos[C2].comparado.B1.barrier_multiplier` — the calendar lapse does **not** move B1's PFD in this model, because `XV-1001` dominates (`a3_cruzamentos[C2].comparado.B1.dominant_element`). What is lost is demonstration, not modelled availability. *demonstrated* (record) + *inferred* (effect).
5. **Top event frequency** — `motores.conventional.projeto.evento_topo_por_ano` → `motores.conventional.atual.evento_topo_por_ano`, ratio `motores.conventional.razao`; fuzzy `motores.fuzzy.projeto.evento_topo_por_ano` → `motores.fuzzy.atual.evento_topo_por_ano`, ratio `motores.fuzzy.razao`, label `Moderate → Moderate` (`motores.fuzzy.atual.rotulo`). Conventional for magnitude, fuzzy for propagation of linguistic uncertainty; neither checks the other (`motores.nota`). *demonstrated* (engine output over declared inputs).
6. **Consequence and receptor** — not declared in any supplied input. The chain stops here.

Temporal correlation is not root cause: the trigger is a calendar due date, and no process mechanism links it to any measured variable in this window.

## Analysis

### 1. Bowtie

**B1 — high-pressure interlock: `degraded`.**
PFD unmoved (`a1_base_de_projeto.barreiras[B1].pfd_atual` versus `.pfd_projeto`, multiplier `a3_cruzamentos[C2].comparado.B1.barrier_multiplier`), worst component multiplier also 1.0 (`...worst_component`), dominant element `XV-1001` at 53.7 % of the total. The C2 pair is the point: the PT-007 component sits *below* design (`detalhe_componentes[PT-007].fator = 0.56` by the model clock) while the functional test that would demonstrate the loop's function is 60 d overdue and unexecuted. The requirement is therefore not *demonstrated within validity* — that is `degraded`, not `healthy`, and not `critical`: there is no demand record and no failure record to remove the function. C4 supports the reading on the detection arm only: the 2oo3 group is **intact by record and reading** (`a3_cruzamentos[C4].resultado`), channels agree within 3× design noise, no frozen channel (`grupo_votado.canais_parados` empty, `congelamento: null`). The relevant clock for the undetected-failure exposure is the test interval (`a3_cruzamentos[C4].relogio`), and that clock is the one that has been allowed to run past its due date.

**Recorded contradiction, unresolved.** `a2_estado_atual.contradicoes[0]`: the PFD creep clock (210 d since last test, interval 365 d) versus the maintenance calendar (overdue 60 d, implying a 2024-05-31 last test derived from an assumption, not a record). Item PFD differs by `contradicoes[0].sensibilidade.razao_item`; barrier-level effect is 1.0 under both (`...por_barreira`). So the contradiction changes nothing in today's number and everything in what "tested" means for B1 — which clock governs is a team decision, not an analyst's.

**B2 — manual operator action: `degraded`.**
Barrier multiplier `a3_cruzamentos[C2].comparado.B2.barrier_multiplier`, worst component `OP-B2` at `...worst_component.multiplicador`, dominant element `OP-B2` at 92.6 % of the barrier total. Both C2 multipliers reported; reporting only the component's would overstate, only the barrier's would hide the single dominating element. The value 0.25 is a **model assumption**, not an asset figure (`a1_base_de_projeto.barreiras[B2].motivos[0]`; `premissas_do_modelo.human_barrier_pfd_with_overdue_competence`) — the erosion is demonstrated by record, its magnitude is assumed.

*A second clock disagreement, noted not resolved:* the same motive line states the OP-B2 competence "test overdue by 28 d (interval 182 d)" while `ordens_servico[WO-RUN_A-TRAIN].vencida_ha_dias = 0`. Two sources in the same database disagree on when the competence lapsed. This does not change the state (both say overdue) but it does change the exposure already accrued.

**C3 cannot be applied today.** `a3_cruzamentos[C3].resultado` = "real window not measurable at t_now", `nao_se_aplica` = "no demand on B1 up to t_now". The design windows (HIHI→SIS `a1_base_de_projeto.declarado.desempenho.janela_hihi_sis_min`; B2 tolerable delay `...atraso_tolerav_b2_min`) are base-case properties (design basis §5) and cannot be cited as the current window. The design basis is explicit that B2's whole margin is perception and decision, none of it execution (§5), and that B2's real window is HIHI→SIS *minus* B1's attempt and the discrepancy-detection latency (§4). A degraded human element on that arm is therefore degradation of exactly the quantity the window compresses first — an exposure that will only become measurable when a demand occurs.

**Independence — C6.** Detection independent (`PT-007` versus `ZT-1001`), **final element shared** (`XV-1001`, `VLV-006`) — `a3_cruzamentos[C6].comparado.declared_independence`, and the design basis is explicit that joint credit must not multiply the two PFDs (§4). The engines fold the pathway as AND nodes over B1 then B2 (`motores.pfd_atual`), i.e. as if independent; to the extent the shared actuation arm is real, the reported top event frequency is **optimistic**. No IPL/SIL credit is granted here for either barrier: none is documented in the supplied inputs, and appearance in the bowtie does not confer it (SKILL.md, B3).

**Declared side effect — C6.** B1's action closes the A+C feed valve, which actuates the LIC-8001 level cascade; inventory control is lost, level goes to about −2.5 % and a low-level trip follows roughly 1 h later (`a3_cruzamentos[C6].comparado.declared_side_effect`). This is a declared secondary consequence, not a failure of B1 against the T1 top event (design basis §5) — but it is a second shutdown route that any B1 demand carries with it.

**C8.** Threat T1 is **not classified**; the removal test was not executed (`a3_cruzamentos[C8].lacuna`, design basis §6). With no demand and no escalation in this window there is no observed behaviour to offer as evidence either way. The success criterion that would apply to a B2 demand is therefore itself undetermined.

**Dominant path.** T1 (feed loss → B1 → B2) at `motores.conventional.atual.pathways[0].contribuicao_pct` of the current top event frequency, up from `...projeto.pathways[0].contribuicao_pct`. The fuzzy engine reproduces the shift in the split (`motores.fuzzy.atual.pathways`), as expected — the split survives quantisation, the magnitude does not.

### 2. Process

No trajectory to analyse. Every flagged tag is within band with no threshold crossed (`a2_estado_atual.margem`), and **no rate is available in any window** (`a2_estado_atual.escada_de_taxas.lacuna`). C7 is therefore reported as distance without rate for `PIT-7001`: 45.00 kPa below HI, `a2_estado_atual.margem.PIT-7001.alvos_declarados` = 195 kPa below the SIS trip (`alarm_config.trip_sis`) and 295 kPa below the model physical limit (design basis §3), with `tempo_ate_limiar_min: null` in each case. **No time-to-target can be stated**, and a distance without a rate does not support a conclusion of comfort (SKILL.md, honesty rules).

C1 returns "no escalation window at t_now" (`a3_cruzamentos[C1].resultado`) with an empty rate ladder. Consequently: the envelope is **neither confirmed nor invalidated**. None of the four invalidation triggers of design basis §7 is observed (`a2_estado_atual.regime.mudanca: null`; thresholds and voting arrangement unchanged in the supplied inputs), and the steady values match §2 closely — but a measured escalation rate is the quantity §7 tests against, and there is none. The design windows must not be quoted as current windows on the strength of a quiet steady state.

Precursor signals: none. The 30-day channel statistics (`a2_estado_atual.grupo_votado.estatistica_por_canal`) show all three channels at the same mean with standard deviations at design noise (1.86/1.90/1.92 against `ruido_de_projeto_kpa` 1.93) — consistent with three live, unfrozen channels.

### 3. Context

- **Design basis:** declared and loaded (`a1_base_de_projeto.base_de_projeto_declarada: true`, `references/design-basis-barriers.md`, rev. 2026-09-11 as supplied). It declares base case (§2), ladder (§3), elements and PFD split (§4), measured windows (§5), the unrun threat-removal test (§6) and invalidation criteria (§7).
- **Mechanical integrity / testing:** two overdue safety-critical work orders on the same pathway, neither executed — `WO-RUN_A-TEST` (B1 functional test, 60 d) and `WO-RUN_A-TRAIN` (B2 competence, opened at due date). One closed corrective with a finding on the same detection group: `WO-RUN_A-CH-A` — channel A discrepancy, relay/channel replaced, retest OK, closed 2025-04-02 (`a2_estado_atual.ordens_servico`). A single closed corrective four months ago is not a pattern; two concurrent overdue preventives on one pathway is a backlog finding. Note the rule declared in `a2_estado_atual.contradicoes[0].fonte_a.regra`: a corrective order does **not** reset the proof-test clock, so April's repair does not stand in for the May test.
- **Management of change:** no operating-condition change up to `t_now` (`a2_estado_atual.regime`). No MOC record is present in the supplied inputs; absence of a record is a gap, not proof of compliance.
- **Human and organisational factors:** the finding is on a human barrier whose declared training interval is six-monthly (design basis §4) and whose entire margin is perception and decision (§5). Assess this as a scheduling/organisational finding — the competence WO was raised automatically at its due date (`ordens_servico[WO-RUN_A-TRAIN].origem: agenda_automatica`) and is already unexecuted. No operator action is in question: there has been no demand.
- **Gaps carried into judgement** (phase A named none formally — `a3_cruzamentos[C5].resultado` = 0 gaps — these are phase B's):
  1. **Consequence and tolerability not declared** anywhere in the supplied inputs. External check: the approved PHA/LOPA record for this top event.
  2. **B2's demand trigger observability.** The declared trigger is command-versus-position discrepancy on `ZT-1001` (`a1_base_de_projeto.declarado.barreiras.B2.gatilho`), and `ZT-1001` appears in no threshold, margin or demand record in phase A; `a2_estado_atual.demandas` carries B1 only. Whether the dataset instruments this trigger is **undetermined**. External check: confirm `ZT-1001` command/position acquisition and the discrepancy logic against the historian tag list.
  3. **Which clock governs PT-007** (`a2_estado_atual.contradicoes[0]`) and, by the same pattern, OP-B2. External check: retrieve the last closed proof-test and last closed training certificates and reconcile against the CMMS calendar.
  4. **T1 classification** (persistent versus removable) — external check: the removal-test campaign of design basis §6.
  5. **Magnitude of the B2 erosion** rests on a model assumption, not an asset figure. External check: an approved human-reliability basis for competence lapse, or execution of the training, which removes the question.

## Risk judgement

**Frequency.** Top event, conventional engine: `motores.conventional.projeto.evento_topo_por_ano` (design) → `motores.conventional.atual.evento_topo_por_ano` (current), ratio `motores.conventional.razao`. Fuzzy engine: `motores.fuzzy.projeto.evento_topo_por_ano` → `motores.fuzzy.atual.evento_topo_por_ano`, ratio `motores.fuzzy.razao`, label `Moderate → Moderate`. The label did not move; the frequency did — a label is not an acceptance criterion, and its stability is not evidence of stability. The T1 pathway now carries `motores.conventional.atual.pathways[0].contribuicao_pct` of the total. Both figures are conditional on the independence assumption the engines make and C6 contradicts (shared `XV-1001`/`VLV-006`); the true current figure is plausibly higher.

**Consequence and receptors.** Not declared in any supplied input. **Tolerability criterion.** Not declared.

**Conclusion, per SKILL.md B4:** *barrier erosion demonstrated; risk tolerability not determined.* Erosion is demonstrated at the record level (two overdue safety-critical WOs on one pathway) and quantified at the model level (barrier and top-event ratios above); whether the resulting frequency is acceptable cannot be stated without the approved criterion and a consequence with a receptor.

**Uncertainty.** Medium confidence overall — bounded by the weakest decisive link, which is the assumed 0.25 for OP-B2. Sensitivity: were OP-B2 held at its design PFD, B2's barrier multiplier and the top-event ratio would both fall towards 1; were the actuation-arm dependency modelled, they would rise. Both directions are open and neither is quantified here.

**Urgency: planned.** Plausible consequence unquantified, but: no demand on any T1 barrier (`a2_estado_atual.demandas.B1.demandada: false`), no active alarm, no crossed threshold, `PIT-7001` 195 kPa from the SIS trip and 295 kPa from the physical limit. Time available cannot be computed from C7 — there is no rate — so the case for urgency rests on proximity of demand, and nothing in this window indicates one. The exposure horizon is the C4 clock: the test interval, already 60 d past due and running. Low frequency with an undeclared consequence is not grounds for discarding the finding — it is grounds for scheduling it, not for emergency action.

**No safety limit is triggered.** No loss of containment, no approach to a trip, no condition outside the safe envelope, no barrier in bypass or isolation.

## Recommendation

**Immediate containment:** none in the process. Do not change setpoints, alarms, logic or bypasses. Recommend that operations be informed that pathway T1 currently rests on a human barrier whose competence renewal is overdue and open, and that both T1 barriers share their final elements (`XV-1001`, `VLV-006`) — so the two are not independent layers for the purposes of any operating decision taken before the WOs are closed.

**Restoration:** execute and close `WO-RUN_A-TRAIN` (OP-B2 competence, `reator.T1.B2`) and `WO-RUN_A-TEST` (functional test of the B1 interlock on `PT-007`, 60 d overdue, `reator.T1.B1`). Record the as-found result of the functional test explicitly — an as-found failure would change B1's state from `degraded` to `critical` retrospectively and must not be lost in a "retest OK" closure note. Re-run both engines after closure and confirm the top-event ratio returns toward 1.

**Definitive solution:** three items, in descending robustness.
1. *Reduce the reliance identified by C2:* `OP-B2` carries 92.6 % of B2's PFD and B2's entire margin is perception and decision (design basis §5). An engineering route that reduces T1's dependence on a human barrier outranks any improvement in training frequency — administrative control does not permanently compensate for engineering without a demonstration of adequacy (SKILL.md, B5). Scope as an engineering evaluation, not a decided change.
2. *Instrument and verify B2's demand trigger* (`ZT-1001` command-versus-position discrepancy). A barrier whose demand cannot be observed cannot be credited or audited whatever its PFD (risk-analysis reference §6). Confirm first whether it is instrumented (gap 2 above).
3. *Resolve the clock rule* that produced `a2_estado_atual.contradicoes[0]` so that one governing date exists per safety-critical item, and close the same question for OP-B2.

Also recommend, as analysis rather than action: run the threat-removal test of design basis §6 to close the C8 classification, and record the approved consequence and tolerability for this top event so a future analysis can complete the risk statement instead of stopping at erosion.

**Checked before recommending (C6):** none of the above actuates a barrier or touches `XV-1001`/`VLV-006`, so the declared level-cascade side effect is not invoked. Executing the B1 functional test may itself place the interlock in a test condition — require that the test procedure declare the compensatory measure for that period; that is a real transient introduced by the recommendation.

**Suggested owner / deadline:** maintenance planning (WO execution) with operations supervision for the competence renewal; process safety engineering for items 1–3. Deadline to be set by the facility's authority; both WOs are already past due.

**Expected return / leading indicator:** on closure of both WOs, B2's barrier multiplier returns toward 1.0 and the conventional top-event ratio toward 1.0. Leading indicators: count and age of overdue safety-critical work orders on BT-REATOR barriers (currently 2, oldest 60 d); days since last *closed* proof test on `PT-007`; days since last closed competence record for `OP-B2`.

**Closure criteria:** both WOs closed with as-found results recorded; B1 interlock function tested and demonstrated (test outcome, not process variables in band); OP-B2 competence recorded and the model PFD returned to a declared value; the PT-007 clock contradiction resolved by the team with the governing rule written down; both engines re-run on the restored PFDs; design basis §5 windows revalidated if the operating condition has changed by then (it has not up to `t_now`). The absence of alarms does **not** close this occurrence — there were none when it opened.

**Residual risk / accepting authority:** not determined here; tolerability criterion absent from the supplied inputs. Acceptance rests with the facility's designated authority.

**Human decision:** pending

## Evidence and assumptions

- [demonstrated] `a2_estado_atual.ordens_servico[WO-RUN_A-TRAIN]`, 2025-07-30 — competence training for `OP-B2` (barrier `reator.T1.B2`) overdue and open; this is the trigger for this analysis.
- [demonstrated] `a2_estado_atual.ordens_servico[WO-RUN_A-TEST]`, due 2025-05-31 — functional test of the B1 interlock on `PT-007` overdue 60 d, not executed.
- [demonstrated] `a2_estado_atual.ordens_servico[WO-RUN_A-CH-A]`, closed 2025-04-02 — channel A discrepancy, closed with a finding; by the declared rule it does not reset the proof-test clock.
- [demonstrated] `a3_cruzamentos[C2]` — both multipliers per barrier; B1 dominated by `XV-1001` (53.7 %), B2 by `OP-B2` (92.6 %).
- [demonstrated] `motores.conventional` / `motores.fuzzy`, design versus current with ratios and pathway splits; conventional cited for magnitude, fuzzy for linguistic uncertainty only.
- [demonstrated] `a3_cruzamentos[C4]` + `a2_estado_atual.grupo_votado` — 2oo3 `PT-007` intact by record and by reading; spread far below limit, no frozen channel, no majority outlier.
- [demonstrated] `a3_cruzamentos[C6]` and design basis §4 — detection independent, final element shared; joint credit must not multiply the two PFDs.
- [demonstrated] `a3_cruzamentos[C1]`, `a2_estado_atual.escada_de_taxas.lacuna` — no measurable escalation rate in the window; envelope neither confirmed nor invalidated.
- [demonstrated] `a3_cruzamentos[C3]` — real window not measurable; design windows of §5 not applicable as current windows.
- [demonstrated] `a2_estado_atual.demandas.B1` — no demand on B1 up to `t_now`; no barrier state is settled by observation in this analysis.
- [inferred] B1 state `degraded` — depends on reading "requirement demonstrated and within validity" as requiring the overdue functional test; PFD itself is unmoved (`C2.comparado.B1.barrier_multiplier`).
- [inferred] Magnitude of B2's erosion — rests on `premissas_do_modelo.human_barrier_pfd_with_overdue_competence` (0.25), a model assumption, not asset data. The overdue state is a record; the number is not.
- [inferred] The reported top-event frequency is optimistic with respect to the shared actuation arm, since the engines fold B1 and B2 as independent AND nodes (`motores.pfd_atual`) against design basis §4.
- [undetermined] `a2_estado_atual.contradicoes[0]` — model clock (210 d, interval 365 d) versus calendar (60 d overdue, last test implied by assumption); item PFD differs 2.11×, barrier effect 1.0× under both. Unresolved by design.
- [undetermined] Second clock disagreement on `OP-B2` — `a1_base_de_projeto.barreiras[B2].motivos[0]` says overdue by 28 d (interval 182 d); `ordens_servico[WO-RUN_A-TRAIN].vencida_ha_dias` says 0. Both say overdue; the accrued exposure differs.
- [undetermined] Whether B2's declared demand trigger (`ZT-1001` command-versus-position discrepancy, design basis §4) is instrumented in this dataset — it appears in no phase A threshold, margin or demand field.
- [undetermined] Threat T1 persistent versus removable — `a3_cruzamentos[C8]`, removal test not executed (design basis §6).
- [undetermined] Consequence, receptor and tolerability criterion — absent from all supplied inputs; the risk statement stops at demonstrated erosion.
- [assumption, phase A] Recovery rules as declared in `a2_estado_atual.regra_de_recuperacao` — failures not detected by `t_now` are masked and do not enter the PFD; this analysis knows nothing after `t_now`.