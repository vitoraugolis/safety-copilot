---
incident_id: INC-BT-REATOR-20251130-1
bowtie_id: BT-REATOR
opened_at: 2025-11-30T08:00:00
engine: conventional
status: action_required
urgency: immediate
confidence: medium
---

# Escalate to operations: the pathway T1 barriers must be treated as operating outside a validated envelope — the 2025-11-28 load change was never revalidated (`a3_cruzamentos[C1].comparado.invalidation_triggers[1]`) and the LO crossing has now exposed PT-007 channel B frozen at the *pre-change* regime, leaving the voted group with no arbiter; no manoeuvre is recommended, but repair, test and revalidation decisions cannot wait for the next campaign.

## Fact

- Trigger: `identidade.gatilho[0]` — `alarme:PIT-7001:LO`, voted PIT-7001 at `a2_estado_atual.alarmes_ativos[0].valor_pico` against the LO threshold `a1_base_de_projeto.limiares[PIT-7001].lo`; active for `a2_estado_atual.alarmes_ativos[0].ativo_ha_min` at `t_now`. Not a demand (`e_demanda = 0`); B1's declared demand trigger is the opposite direction, voted PIT-7001 ≥ HIHI (`a1_base_de_projeto.declarado.barreiras.B1.gatilho`).
- This is the third LO episode since the operating-condition change: `a2_estado_atual.regime.alarmes_entre_a_mudanca_e_o_episodio` (2025-11-28 and 2025-11-29, both normalised) plus the present one.
- Operating mode: `campanha padrao`, load 15 %, feed setpoint scale 1.15 (`a2_estado_atual.eventos_operacionais[0].detalhe`), effective since 2025-11-28T00:00:00.
- Data quality: rate ladder has one window and three samples (`a2_estado_atual.escada_de_taxas.degraus[0].amostras`); `a2_estado_atual.taxas` is empty, so **no rate exists for TIT-9001, LIT-8001, FIT-1001 or TIT-2101** — their values in `a2_estado_atual.margem` are instantaneous only and are not, on their own, a basis for conclusion (SKILL.md, honesty rules). Post-change regime statistics rest on n = 12 (`a2_estado_atual.regime.regime_depois.n`).
- Crossing is reproducible against `alarm_config`; the B1 gate is not triggered here. No demand on any pathway-T1 barrier up to `t_now` (`a2_estado_atual.demandas.B1.demandada = false`).

**What this trigger changed.** It is the first analysis in this stream. Its substantive addition is not the pressure value: it is that the regime shift makes a long-recorded channel failure *observable*. PT-007.B has been `failed_detected_unrepaired` since 2025-08-29 (`a2_estado_atual.canais[1]`), frozen at 2708.41 kPa, which differs from the pre-change reference regime by 0.04 kPa (`a2_estado_atual.grupo_votado.congelamento.diferenca_para_o_regime`). While the plant ran at the old regime the frozen channel was indistinguishable from a healthy one; at the new regime the spread is 160.78 kPa against a limit of 17.5 kPa (`a2_estado_atual.discrepancia_canais[0]`).

## Scenario and mechanism

Qualitative chain (pathway T1, `diagrams/BT-REATOR.txt`):

`loss of stream 1 feed → B1 high-pressure interlock (AND) B2 manual operator action → loss of reactor control (top event) → mitigation and consequence: not declared in phase A`

Quantitative chain, link by link:

| Link | Evidence | Strength |
|---|---|---|
| Threat T1 not currently manifest: FIT-1001 at `a2_estado_atual.margem.FIT-1001.valor` against LO 0.15 / LOLO 0.05 (`a1_base_de_projeto.limiares`), no threshold crossed | phase A reading; no rate available | inferred (no rate) |
| PT-007.B failed and unrepaired 93 d (`a3_cruzamentos[C4].relogio`), group running 2oo2 without reconfiguration (`premissas_do_modelo.voted_group_without_reconfiguration`) | `a2_estado_atual.canais[1]`, WO-RUN_A-CH-B | demonstrated |
| PT-007 item PFD ×34.29 (`a1_base_de_projeto.barreiras[B1].c2.componente_pior`) | reliability layer | demonstrated |
| B1 barrier PFD ×1.11, B2 ×2.27 (`a1_base_de_projeto.barreiras[*].c2.multiplicador_barreira`) | computed from component PFDs | demonstrated |
| Top event frequency ×2.07 conventional (`motores.conventional.razao`), T1 share 70.1 % → 85.6 % (`motores.conventional.*.pathways[0].contribuicao_pct`) | engine on the declared diagram | demonstrated |
| Design windows no longer describe the plant: envelope invalidated (`envelope.invalidada = true`) | design basis §7, trigger 2 | demonstrated |
| The engine product B1×B2 assumes independence that C6 refutes in the actuation arm | `a3_cruzamentos[C6].comparado.declared_independence` | inferred |

Temporal note: the regime shift (`a2_estado_atual.regime.deslocamento_kpa`) and the channel-B freeze are not causally linked — the freeze predates the change by three months (`a2_estado_atual.grupo_votado.congelamento.parado_desde_aprox`). The change made it visible; it did not cause it.

## Analysis

### 1. Bowtie

**B1 — high-pressure interlock: `degraded`.** Function not removed and never demanded (`a2_estado_atual.demandas.B1`), so it is not `critical`. Degradation is demonstrated on the detection arm: 2oo3 declared, one channel failed-detected-unrepaired, group state *known degraded* (`a3_cruzamentos[C4].resultado`) with a repair clock of 93 d — a backlog clock, not a test-interval clock, so exposure is bounded by repair scheduling, not by the next proof test. C2 must be read in both columns: the component moved ×34.29 but the barrier only ×1.11, because the dominant element is XV-1001 at 48 % of the total (`a1_base_de_projeto.barreiras[B1].c2`). Over-reacting to 34× would be wrong; so would reporting 1.11× alone, because the detection degradation is what removes the arbiter.

A consequence the PFD does not carry: channel B is frozen at 2708.41 kPa, below HIHI 2800. B1's demand requires the *vote* to reach HIHI. A channel that cannot rise cannot contribute a vote, so the demand now effectively rests on A and C together — one further failure in the agreeing pair leaves B1 undemandable, and that state would be hidden until the overdue functional test runs. Marked **inferred** (it follows from `a2_estado_atual.grupo_votado.congelamento` plus the declared trigger, not from a recorded test).

**B2 — manual operator action: `degraded`.** PFD ×2.27, dominated by OP-B2 at 92 % of the total (`a1_base_de_projeto.barreiras[B2].c2.elemento_dominante`), with competence renewal overdue 123 d (WO-RUN_A-TRAIN). The 0.25 value is a **model assumption**, not asset data (`premissas_do_modelo.human_barrier_pfd_with_overdue_competence`); the direction of the finding is sound, the magnitude is not measured.

C3 cannot be executed: no demand, so no measured window (`a3_cruzamentos[C3].resultado`). This matters more than "not applicable" suggests. The design basis states that B2's entire margin is perception and decision, not execution (design-basis §5), and C1 has declared the envelope invalid — so the 162 min HIHI→SIS window and the 67 min tolerable delay are **design figures that no longer describe this condition** and must not be cited as current margin (`envelope.janelas_de_projeto` read against `envelope.invalidada`). B2's real window at 15 % load is **not demonstrated**. Under SKILL.md B3, this is a gap, not an adjusted PFD.

**Independence and credit.** C6 is explicit: detection independent (PT-007 vs ZT-1001), **final element shared** (XV-1001, VLV-006). Joint credit must not be taken as the product of the two PFDs. The engines nonetheless fold the pathway as an AND chain, so `motores.conventional.atual.evento_topo_por_ano` is best read as a **lower bound** for pathway T1. No IPL/SIL credit is claimed here; none is documented in phase A.

**Declared side effect (C6).** B1's action closes the A+C feed valve that actuates the level cascade LIC-8001; inventory control is lost and a low-level trip follows about 1 h later (`a3_cruzamentos[C6].comparado.declared_side_effect`). Any recommendation that would make B1 more likely to act must be weighed against this route.

**B3/B4 (temperature pathway).** PFDs at design values (`motores.pfd_atual`); their share falls from 29.9 % to 14.4 % only because T1 grew, not because they improved. Not otherwise analysed in this run (`identidade.pathway_avaliada = T1`).

### 2. Process

- PIT-7001: value `a2_estado_atual.margem.PIT-7001.valor`; LO crossed by −2.01 kPa; next threshold ahead HI at +202.01 kPa; SIS trip at +352.01 kPa; physical limit at +452.01 kPa (`a2_estado_atual.margem.PIT-7001.alvos_declarados`). Rate over the single declared window is −0.08 kPa/min, 0.1× the design escalation rate and far below the 2.2 kPa/min invalidation threshold (`envelope.degraus[0]`). Distance and rate together: the variable is moving **away** from every high-side target, and phase A correctly suppresses time-to-target (`taxa_por_min = null`, note in `a2_estado_atual.margem.PIT-7001.nota`). There is no approach to a trip.
- **Direction gap.** Phase A's margin table enumerates targets on the high side only; LOLO 2450 kPa is declared in `a1_base_de_projeto.limiares` but carries no distance/rate line. The plant is drifting in the low direction and the margin ladder does not cover it. Recorded as a gap, not filled.
- Regime: median voted pressure fell from 2708.37 to 2566.13 kPa, a shift of −142.24 kPa, with `revalidacao_registrada = false` (`a2_estado_atual.regime`). The post-change band (2518.25–2602.79) straddles the LO threshold of 2550, which explains three LO alarms in three days without any equipment fault — an alarm-configuration mismatch to the new regime, not a process excursion.
- Other tags: TIT-9001 at 120.43 °C sits essentially at the design regime of 120.4 °C; LIT-8001 at 70.99 % against a design regime of 74.4 %; TIT-2101 at 94.03 °C, between LO 88 and HI 100; FIT-1001 at 0.371 kscmh against a design value of 0.252 kscmh. **None has a rate in phase A**, so none of these supports a trend statement.
- The design plateau (2850–2870 kPa) was not entered (`envelope.gatilhos_de_invalidacao[2]`), so nothing here tests whether the base case's time distribution still exists at 15 % load.

### 3. Context

- **Management of change.** The 2025-11-28 operating-condition change (load 15 %, feed setpoint scale 1.15) moved the process off the single declared base case (design basis §2) with no revalidation work order and no revalidation event after that date. This is simultaneously an integrity finding and the fired invalidation trigger of design basis §7 (risk-analysis-reference §4). The design basis states plainly that when invalidated, "the real actuation window **is not known**" — that is the condition the plant is in now.
- **Mechanical integrity / testing.** WO-RUN_A-TEST, functional test of the B1 interlock, overdue 183 d and not executed. Its due date (2025-05-31) **precedes** the PT-007.B failure detection (2025-08-29), so on dates the test could not have pre-empted this failure — but it is the check that would now confirm whether the remaining channels and the logic still satisfy the vote. WO-RUN_A-CH-A closed with a finding on channel A in April 2025; WO-RUN_A-CH-B is the second channel discrepancy on the same transmitter within five months. Two channel findings on one voted group inside one test interval is a repeat-failure signal on PT-007, and warrants a common-cause review rather than another channel swap.
- **Human and organisational factors.** OP-B2 competence renewal overdue 123 d with the work order open. The design basis assigns B2's whole margin to perception and decision; combining overdue competence with an unknown window is the exact condition risk-analysis-reference §5 warns against. This is a task/organisation finding (training scheduling and backlog), not operator blame.
- **Recorded contradiction, unresolved.** `a2_estado_atual.contradicoes[0]`: the PFD creep clock reads 333 d since the last test while the maintenance calendar reads the test 183 d overdue. Both come from the same database. Sensitivity is carried: item PFD ratio 1.65×, but only 1.07× on B1 and 1.01× on B2. **The choice of clock does not change any conclusion in this report**; it does change the item-level figure, and which clock governs is a team decision, not mine.
- **Gaps carried from phase A.** C5: whether a common cause affects the agreeing pair A and C cannot be settled with current instrumentation — the majority identifies B as divergent, but with only two channels left there is no arbiter for A and C. External check: an independent field measurement of vessel pressure (`a3_cruzamentos[C5].lacunas[0]`). C8: threat T1 unclassified; the removal test of design basis §6 was never run, so the success criterion that should apply to B1/B2 is undetermined. Consequence, receptors and tolerability are absent from phase A and from the design basis.

## Risk judgement

- **Top event frequency.** Conventional engine: `motores.conventional.projeto.evento_topo_por_ano` → `motores.conventional.atual.evento_topo_por_ano`, ratio `motores.conventional.razao` (2.07×). Fuzzy engine: `motores.fuzzy.projeto.evento_topo_por_ano` → `motores.fuzzy.atual.evento_topo_por_ano`, ratio 1.98×, label `Moderate → Moderate`. The conventional figure is cited for magnitude, the fuzzy for the propagation of linguistic uncertainty; neither checks the other (SKILL.md). The unchanged fuzzy label is **not** reassurance — with ~one-decade quantisation a doubling need not move a term, and the label qualifies a frequency, not a barrier state and not risk.
- Pathway T1 now carries 85.6 % of the top event frequency against 70.1 % on design (`motores.conventional.*.pathways[0]`). The erosion is concentrated in the pathway this trigger concerns.
- Because C6 refutes independence in the actuation arm, the current figure should be read as a **lower bound**, not a best estimate.
- **Consequence and tolerability.** Not declared anywhere in phase A or the design basis. Therefore the correct conclusion is: **barrier erosion demonstrated (×2.07 on the top event frequency, T1 share 70.1 % → 85.6 %); risk tolerability not determined.** That is a result, not a failure of the analysis.
- **Uncertainty.** Three decisive weaknesses: OP-B2 PFD = 0.25 is a model assumption; the 2oo2 fall-back is an assumption, not a recorded reconfiguration; the post-change regime rests on n = 12 and the rate on 3 samples. Overall confidence is capped by the weakest decisive link: **medium**.
- **Urgency: immediate, not emergency.** No active loss of containment, no approach to a trip, no barrier bypassed or isolated, and the variable is moving away from every high-side target at −0.08 kPa/min. What is urgent is not the current process state but the exposure: a voted group with no arbiter for 93 d, an interlock functional test 183 d overdue, human competence 123 d overdue, and — decisively — an operating condition in which the actuation window for the T1 pathway is **not known**. Time available cannot be taken from C7 (no rate toward a high-side target) nor from the design windows (invalidated). Absence of a demand to date is not evidence of capability.

## Recommendation

**Immediate containment:** escalate this analysis to the shift supervisor and the process safety authority for a decision on continued operation at 15 % load without revalidated barrier windows. I recommend no manoeuvre, no setpoint, logic, alarm or bypass change. Obtain an independent field measurement of vessel pressure (C5 external check) to test for common cause in the agreeing pair A/C; until that is in hand, treat voted PIT-7001 as a two-channel reading with no arbiter and require an independent confirmation before acting on any single pressure indication. Do not re-rank the LO alarms as nuisance before the field check.

**Restoration, in this order:**
1. WO-RUN_A-CH-B — repair/replace PT-007 channel B (93 d in backlog) and verify the restored channel tracks the *current* regime, not the 2708 kPa value it is frozen at.
2. WO-RUN_A-TEST — execute the overdue functional test of the B1 interlock (183 d), covering the vote resolution and the final elements XV-1001/VLV-006, with the frozen-channel failure mode explicitly in scope.
3. WO-RUN_A-TRAIN — execute OP-B2 competence renewal (123 d), with the scenario briefed at the current operating condition.

**Definitive solution:**
- Raise management of change retroactively for the 2025-11-28 operating-condition change and revalidate the barrier windows at 15 % load following `references/producing-a-design-basis.md` steps 2–6 (threshold crossing times, escalation rate, windows, B2 maximum tolerable delay, and whether the plateau still exists). Until this is done, design basis §5 does not apply.
- Run the threat-removal test of design basis §6 to close the C8 classification, so B1/B2 have a defensible success criterion.
- Review the alarm configuration against the new regime — the LO threshold of 2550 kPa sits inside the post-change operating band and is generating repeat alarms. Note that changing `alarm_config` is itself an invalidation trigger (design basis §7): any threshold change must recompute the windows in the same change package, not after it.
- Review the joint credit taken for B1 and B2 in the bowtie given the shared final element (C6); the current diagram folds them as independent.
- Two channel findings on PT-007 within one test interval (WO-RUN_A-CH-A, WO-RUN_A-CH-B) plus two overdue preventive orders on the same barrier pathway are consistent with a systemic maintenance-backlog issue rather than two coincidences. Recommend a **separate formal investigation** of the preventive backlog on safety-instrumented assets; this analysis does not perform root cause.

**Suggested owner / deadline:** field pressure check and escalation — shift supervisor, this shift. WO-RUN_A-CH-B — maintenance planning, 7 days. WO-RUN_A-TEST and WO-RUN_A-TRAIN — maintenance planning / operations training, 14 days. MOC and window revalidation — process safety, 30 days. Threat-removal test and bowtie credit review — process safety, next review cycle. Priority: high on the first three; deadlines are proposals for the accountable function, not authorisations.

**Expected return / leading indicator:** PT-007 channel spread back within the 17.5 kPa limit (`a2_estado_atual.discrepancia_canais[0].limite`) and all three channels tracking the current regime; B1 barrier multiplier back to 1.00× and B2 to its design PFD with the assumption removed rather than re-assumed; count of PIT-7001 LO alarms per day trending to zero after the alarm review; a revalidated HIHI→SIS window and B2 tolerable delay recorded for 15 % load.

**Closure criteria:** all four conditions together — (a) PT-007 restored to 2oo3 and **proof-tested**, with the functional test closed with result; (b) OP-B2 competence closed; (c) design basis windows revalidated under the current operating condition and the invalidation trigger cleared; (d) top event frequency recomputed on the restored PFDs and the pathway T1 share reviewed. Any temporary change made in the interim must be managed with a stated reversion condition. **The pressure returning inside the alarm band does not close this occurrence.**

**Residual risk / accepting authority:** not determined — consequence, receptors and a tolerability criterion are absent from every source available here. Residual risk acceptance belongs to the facility's designated authority and cannot be discharged by this report.

**Human decision:** pending

## Evidence and assumptions

- [demonstrated] `a2_estado_atual.canais[1]` + WO-RUN_A-CH-B, 2025-08-29 — PT-007.B failed, detected, unrepaired for 93 d; voted group known degraded, arbiter lost.
- [demonstrated] `a2_estado_atual.grupo_votado.congelamento`, computed from the series — channel B flat at 2708.41 kPa since ≈2025-08-29, 0.04 kPa from the pre-change regime; invisible by spread until the regime moved. Start instant is inferred from the series, not a recorded failure time.
- [demonstrated] `a2_estado_atual.regime`, event 2025-11-28T00:00:00 — regime shift −142.24 kPa, `revalidacao_registrada = false`.
- [demonstrated] `envelope.invalidada = true`, design basis §7 trigger 2 — design windows (162 min, 67 min) do not describe the current condition and are not cited as current margin.
- [demonstrated] `a1_base_de_projeto.barreiras[*].c2` — B1 ×1.11 with XV-1001 dominant (48 %); B2 ×2.27 with OP-B2 dominant (92 %); worst component PT-007 ×34.29 in both.
- [demonstrated] `motores.conventional` / `motores.fuzzy` — top event frequency ×2.07 (conventional, magnitude) and ×1.98 with label `Moderate → Moderate` (fuzzy, linguistic uncertainty); T1 share 70.1 % → 85.6 %.
- [demonstrated] WO-RUN_A-TEST overdue 183 d; WO-RUN_A-TRAIN overdue 123 d; WO-RUN_A-CH-A closed with a finding 2025-04-02.
- [corroborated] `a3_cruzamentos[C6]` + design basis §4 — detection independent, final element shared; joint credit must not be the product of the two PFDs.
- [inferred] Channel B frozen at 2708.41 kPa is below HIHI 2800 and cannot contribute a vote, so B1's demand effectively requires both remaining channels; a further single failure would leave B1 undemandable and hidden until the overdue test. Depends on the declared trigger `voted PIT-7001 ≥ HIHI`; not confirmed by any test record.
- [inferred] `motores.conventional.atual.evento_topo_por_ano` is a lower bound for pathway T1, because the engine folds B1 and B2 as independent while C6 refutes independence in the actuation arm.
- [inferred] Threat T1 is not currently manifest — FIT-1001 above its LO/LOLO thresholds — but `a2_estado_atual.taxas` is empty, so there is no rate to support a trend.
- [undetermined] C5 — common cause affecting the agreeing pair A and C. External check: independent field measurement of vessel pressure.
- [undetermined] C8 — T1 persistent vs removable; removal test (design basis §6) never executed, so the applicable success criterion for B1/B2 is not established.
- [undetermined] C3 — window compression not measurable; no demand on B1 up to `t_now` (`a3_cruzamentos[C3].nao_se_aplica`). B2's real window at 15 % load is **not demonstrated**.
- [undetermined] `a2_estado_atual.contradicoes[0]` — PFD creep clock (333 d) vs maintenance calendar (183 d overdue). Sensitivity carried: item 1.65×, B1 1.07×, B2 1.01×. No conclusion in this report turns on it.
- [assumption] `premissas_do_modelo.human_barrier_pfd_with_overdue_competence` — OP-B2 PFD 0.25, model value, not asset data; it dominates B2's multiplier.
- [assumption] `premissas_do_modelo.voted_group_without_reconfiguration` — the fall to 2oo2 is assumed, not a recorded reconfiguration.
- [absent] Consequence, receptors and tolerability criterion — not present in phase A or the design basis; hence risk tolerability not determined.
- [absent] Low-side margin — LOLO 2450 kPa is declared in `a1_base_de_projeto.limiares` but carries no distance/rate line in `a2_estado_atual.margem`, which is the direction the plant is drifting.