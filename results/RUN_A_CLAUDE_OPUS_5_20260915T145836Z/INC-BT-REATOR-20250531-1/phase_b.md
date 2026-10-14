---
incident_id: INC-BT-REATOR-20250531-1
bowtie_id: BT-REATOR
opened_at: 2025-05-31T00:00:00
engine: conventional
status: monitoring
urgency: planned
confidence: medium
---

# Execute the overdue functional test WO-RUN_A-TEST on PT-007 (barrier reator.T1.B1) and settle which test clock governs the PFD; no process condition at `t_now` requires operational intervention.

**Safety limit check.** None of the escalation conditions of SKILL.md ("Safety limits") is present at `t_now`: no active alarm (`a2_estado_atual.alarmes_ativos` empty), no demand on any barrier (`a2_estado_atual.demandas.B1.demandada = false`), no threshold crossed on any flagged tag (`a2_estado_atual.margem.*.limiares_ja_cruzados` empty), no barrier unavailable (`a1_base_de_projeto.barreiras[*].c2.multiplicador_barreira = 1.0`). No emergency escalation is indicated by this analysis.

## Fact

**What this trigger is.** Two records, both dated at `t_now = 2025-05-31T00:00:00`: `record:wo_opened:WO-RUN_A-TEST` and `record:wo_overdue:WO-RUN_A-TEST` (`identidade.gatilho`). The work order is a `teste_funcional` on PT-007, barrier `reator.T1.B1`, class `overdue_not_executed`, `vencida_ha_dias = 0`, no closure date (`a2_estado_atual.ordens_servico[1]`). The trigger is a maintenance-calendar record, not a process signal — the erosion mechanism the stream exists to catch, which the process series cannot show (SKILL.md, "Analyses over time").

**What this trigger changed.** This is the first analysis in the stream for BT-REATOR. It changes the barrier's *verification* status, not its measured performance: at `t_now` the periodic demonstration of B1's detection function falls due and is not executed. No PFD, no channel state and no process value moved with it.

**Plant state at `t_now`.** PIT-7001 2708.2431 kPa, TIT-9001 120.3864 °C, LIT-8001 74.4803 %, TIT-2101 94.5399 °C, FIT-1001 0.238 kscmh (`a2_estado_atual.margem`). Nothing crossed; nearest threshold ahead on the pressure tag is HI 2750 at a distance of 41.76 kPa, with SIS trip at +191.76 kPa and the model physical limit at +291.76 kPa (`a3_cruzamentos[C7].comparado.PIT-7001`).

**Data quality — decisive limitation.** `taxa_por_min` is null for every tag and the rate ladder is empty with the declared gap `serie insuficiente na janela` (`envelope.lacuna`). No time-to-target can be computed, and under the honesty rule "do not conclude from an instantaneous value" the point values above do not on their own establish that the plant is steady. The substitute evidence is the 30-day per-channel statistics on the pressure tag — n = 181 per channel, means 2708.37–2708.40, sd 1.95–1.97, full range 2702.85–2714.01 (`a2_estado_atual.grupo_votado.estatistica_por_canal`) — which is consistent with a stationary regime at the declared base-case pressure of 2708 kPa (design basis §2) and with the declared noise of 1.93 kPa (`declarado.escada_protecao.ruido_kpa`). That statistic covers PIT-7001 only; for the other four tags no rate and no dispersion statistic is carried, and their stability is **not demonstrated** in this context.

The crossing that opened the analysis is a record, reproducible by inspection of `work_orders`. The B1 gate of B1 is passed.

## Scenario and mechanism

**Qualitative chain (pathway T1).** Loss of stream 1 feed (`diagrams/BT-REATOR.txt`, f = 0.5/yr) → pressure escalation on PIT-7001 → **B1** automatic high-pressure interlock at voted HIHI 2800 kPa → **B2** manual operator action, demanded only by command-versus-position discrepancy on ZT-1001, i.e. only after B1 has tried and failed (design basis §4) → top event "Perda de controle do reator". The SIS trip at 2900 kPa is the last automated layer beyond the pathway, not a barrier of it (design basis §3).

**Quantitative chain, and where it stops.** The trigger touches one link only:

`WO-RUN_A-TEST overdue → PT-007 proof-test interval not demonstrated → hidden-failure clock on the voted group → PT-007 item PFD → B1 PFD → pathway T1 frequency → top event frequency`

The chain is measurable up to the top event and breaks there: phase A carries no consequence, no receptor and no tolerability criterion, so the last link (`consequence frequency and severity`) cannot be walked.

**Strength of the link at `t_now`: weak, and measurably so.** The item-level effect of the clock dispute is 2.53× (`a2_estado_atual.contradicoes[0].sensibilidade.razao_item`), but the barrier-level effect is 1.0× on both B1 and B2 (`...sensibilidade.por_barreira`). This is C2 operating as intended: PT-007 contributes 2.78e-05 against a B1 total of 2.05e-02, more than two orders below the dominant element XV-1001 (`a1_base_de_projeto.barreiras[0].detalhe_componentes`). The overdue test is therefore a **verification** finding, not, at `t_now`, a performance finding. Reporting only the item multiplier would produce over-reaction; reporting only the barrier multiplier would hide the lapsed verification (cross-checks, C2).

## Analysis

### 1. Bowtie

**B1 — high-pressure interlock: `healthy`, with its verification validity expiring at this instant.**
Current PFD equals design to the reported precision, barrier multiplier 1.0×, worst component UZ-007 at 1.0×, dominant element XV-1001 at 53.7 % of the total (`a3_cruzamentos[C2].comparado.B1`). The 2oo3 group PT-007 is **intact by record and by reading** (`a3_cruzamentos[C4].resultado`): spread 0.62 kPa against a declared limit of 17.5 kPa, all three pairs agreeing inside the 5.79 kPa tolerance, no divergent channel by majority, no frozen channel (`a2_estado_atual.grupo_votado`). The April channel-A discrepancy is closed — failed 2025-04-01, repaired 2025-04-02, WO-RUN_A-CH-A `closed_with_finding` (`a2_estado_atual.canais[0]`). No demand on B1 is recorded up to `t_now`, so no observation outranks the PFD here.

The state is `healthy` on every criterion phase A can measure, and it sits on the boundary of the SKILL.md definition ("requirement demonstrated and within validity") for one reason: the periodic demonstration is due now and unexecuted. This is the verification element of barrier performance (risk-analysis-reference §2), and it is the only element of B1 not currently satisfied. Each day the test stays unexecuted moves the barrier further from "within validity"; that judgement belongs to the next analysis in the stream, not this one.

**Recorded contradiction, unresolved and carried forward.** Two readings of the same database disagree on the proof-test clock: the creep clock says 150 d elapsed against a 365 d interval, the maintenance calendar says overdue by 0 d (`a2_estado_atual.contradicoes[0]`). The calendar reading rests on an implied last test at 2024-05-31, which phase A marks explicitly as "an assumption, not a record". So there is **no record of a closed prior functional test on PT-007** in this context; the model assumption `items_without_test_records` keeps such items at design PFD (`premissas_do_modelo`). Both clocks are reported, neither is adopted here — which clock governs is a decision for the team, not for this analysis.

**B2 — manual operator action: `healthy` on PFD, with its effectiveness envelope unverified.**
Current PFD equals design, multiplier 1.0×, dominant element OP-B2 at 83.5 % of the total (`a3_cruzamentos[C2].comparado.B2`); the overdue-competence assumption of 0.25 is not invoked, since no training work order is open. C3 cannot be evaluated: no demand occurred, so no real HIHI→SIS window is measurable and the compression factor is null (`a3_cruzamentos[C3]`). The design basis records the design window as 162 min and B2's maximum tolerable delay as ≈ 67 min, and states that essentially all of that margin is human perception and decision rather than execution, and that the window is a parameter of the operating condition, not a constant (design basis §5). B2's PFD of 0.1198 therefore describes a barrier whose validity depends on a window that has not been measured under the current condition. That is a gap, not a reason to adjust the number — adjusting requires an approved method (cross-checks, C3).

**Independence — do not multiply.** Detection is independent (PT-007 for B1, ZT-1001 for B2); the final elements XV-1001 and VLV-006 are **shared** (`a3_cruzamentos[C6]`, design basis §4). Joint credit for B1 and B2 must not be taken as the product of the two PFDs. A sensor failure fells one barrier; a failure of XV-1001 or VLV-006 fells both — and XV-1001 is already the dominant element of B1 (53.7 %) and a component of B2. No IPL or SIL credit is claimed or endorsed here; none is documented in the phase A block.

**Declared side effect of B1's action, for the record.** B1 closes the A+C feed valve XV-1001D, which is the actuator of the level cascade LIC-8001; inventory control is lost, level goes to about −2.5 % and a low-level trip follows roughly 1 h later (`a3_cruzamentos[C6].comparado.declared_side_effect`). This coupling is not mapped in the bowtie. No barrier action is recommended in this analysis, so the coupling is not triggered by anything proposed here, but it must be weighed by whoever recommends a B1 action later.

### 2. Process

No alarm is active and no threshold is crossed on any flagged tag. Against the declared targets of PIT-7001: 41.76 kPa to HI, 191.76 kPa to the SIS trip, 291.76 kPa to the model physical limit (`a3_cruzamentos[C7].comparado.PIT-7001`). **Time to each of these is not computable** — the measured rate is null and phase A suppresses the projection rather than inventing one. Under C7, distance without rate is not a margin statement; what can be said is that the distances are large and that the pressure channels show no trend departure over the 30-day window, not that the approach rate is known.

C1 returns "no escalation window at `t_now`" (`a3_cruzamentos[C1].resultado`): there is no excursion against which to test the design escalation rate of 1.1 kPa/min or the invalidation threshold of 2.2 kPa/min (design basis §2, §7). The envelope is therefore **neither confirmed nor invalidated** by this analysis. Phase A records no operating-condition change up to `t_now` (`a2_estado_atual.regime`), and PIT-7001, LIT-8001 and TIT-9001 all sit on their declared base-case values (design basis §2).

**One observation not carried as a phase A finding.** FIT-1001 reads 0.238 kscmh against a declared base-case stream 1 feed flow of 0.252 kscmh (`declarado.condicao_de_projeto.vazao_alimentacao_kscmh`) — about 5.6 % low, though far above LO 0.15. FIT-1001 is the tag of threat T1 itself. Phase A carries no rate, no dispersion statistic and no noise band for this tag, so I cannot tell normal variation from a drift, and phase A's regime check found no declared change. I record it as an open question, not a finding, and it is the reason the confidence of this report is medium rather than high.

### 3. Context

**Design basis.** `references/design-basis-barriers.md` is declared and loaded in full (`a1_base_de_projeto.base_de_projeto_declarada = true`). It states explicitly that it describes only the base case and that its Section 5 performance does not apply outside the Section 2 condition. Nothing in this context demonstrates a departure from that condition; nothing demonstrates adherence under dynamics either, because no excursion occurred.

**Mechanical integrity and testing.** One closed corrective order with a finding on PT-007 channel A (WO-RUN_A-CH-A), one overdue preventive functional test on the same item (WO-RUN_A-TEST). A corrective order does not reset the proof-test clock (`a2_estado_atual.contradicoes[0].fonte_a.regra`), so the April repair, although it retested the channel, does not substitute for the due functional test of the interlock. No repeated-failure pattern is visible: one channel event in the horizon from 2025-01-01, repaired inside 24 h.

**Management of change.** No operating-condition change, no threshold change, no voting-arrangement or test-interval change is recorded up to `t_now`; none of the four invalidation triggers of design basis §7 is observed. Absence of a record is a gap, not proof of compliance (SKILL.md, honesty rules).

**Human and organisational factors.** OP-B2 carries 83.5 % of B2's PFD and its training interval is 4380 h (design basis §4); no training work order appears in this context, so competence currency is neither confirmed nor refuted here. Nothing in this analysis assigns fault to an operator; the finding is a planning one — a scheduled test reached its due date unexecuted.

**Gaps bearing on the decision.** C5 names zero gaps (`a3_cruzamentos[C5]`). Reading the context against the three recurring gap sources of the cross-checks reference, I add two, both marked as my inference rather than as phase A output:

1. **Uninstrumented or unobserved demand trigger for B2.** B2's declared demand is a command-versus-position discrepancy on ZT-1001 (`declarado.barreiras.B2.gatilho`). No ZT-1001 series appears in `a2_estado_atual.margem`, and `a2_estado_atual.demandas` carries an entry for B1 only. In this context B2 cannot be shown to have been demanded, to have responded, or to have failed. External check that would settle it: confirm ZT-1001 is historised and that a B2 demand record exists in the database schema.
2. **Threat T1 unclassified.** The persistent-versus-removable classification requires a threat-removal campaign that was not executed for this bowtie (`a3_cruzamentos[C8].lacuna`, design basis §6). Without it, the success criterion for B1 and B2 under a real T1 is not settled: "pressure reverts without reaching the SIS trip" (design basis §5) is the criterion used in the measurements, but if T1 is persistent the honest criterion is "we reached the upstream repair alive" (cross-checks, C8). External check: the removal test at varied injection instants, with and without barrier action.

## Risk judgement

**Top event frequency, both engines** (`motores`, exposure window 1.0 yr):

| Engine | Design /yr | Current /yr | Ratio | Label |
|---|---|---|---|---|
| conventional | `motores.conventional.projeto.evento_topo_por_ano` = 1.754e-03 | `motores.conventional.atual.evento_topo_por_ano` = 1.751e-03 | `motores.conventional.razao` = 1.0 | — |
| fuzzy | `motores.fuzzy.projeto.evento_topo_por_ano` = 2.496e-04 | `motores.fuzzy.atual.evento_topo_por_ano` = 2.490e-04 | `motores.fuzzy.razao` = 1.0 | Moderate → Moderate |

Cite the conventional engine for magnitude and the fuzzy engine for the propagation of linguistic uncertainty; the two differ by roughly sevenfold and neither checks the other (SKILL.md, "The fuzzy engine"). Pathway T1 carries 70.1 % of the current conventional top event frequency and 74.1 % of the fuzzy one (`motores.*.atual.pathways`), so it remains the dominant pathway, as it is in the design diagram.

**Barrier erosion: not demonstrated at `t_now`.** Both barriers are at their design multiplier, the voted group is intact, and the top event frequency ratio is 1.0× on both engines. What is demonstrated is a lapse in **verification**, not in performance.

**Tolerability: not determined.** Phase A carries no consequence, no receptor, no severity and no approved tolerability criterion. Under SKILL.md B4 the correct conclusion is stated as such: *no barrier erosion demonstrated; risk tolerability not determined.* That is a result, not a failure of the analysis. Do not read the fuzzy label "Moderate" as an acceptance statement — it qualifies a frequency, not risk.

**Uncertainty, in order of weight on the decision.** (i) No measured rate on any tag, so no time-to-target and no C1 envelope test — the largest single limitation of this report. (ii) The proof-test clock contradiction, 2.53× at the item and 1.0× at the barrier. (iii) No record of a closed prior proof test on PT-007, so the model's design-PFD default for untested items is carrying the sensor's figure. (iv) B2's window unverified under current conditions and its demand trigger unobserved here. (v) T1 unclassified. (vi) FIT-1001 5.6 % below the declared base-case flow, with no dispersion statistic to judge it.

**Urgency: planned.** Plausible consequence is not quantified; proximity is low — no demand, no alarm, large nominal distances to every declared target; remaining barriers are at design; confidence in the data is medium. Nothing here supports an immediate or emergency classification, and nothing supports treating the overdue test as routine either: it is the periodic demonstration of the detection element of the dominant pathway's automatic barrier.

## Recommendation

**Immediate containment:** none required by process condition. Keep B1 and B2 in service; do not bypass, isolate or defer either while the test is scheduled. No setpoint, logic or bowtie change is proposed by this analysis.

**Restoration:** execute and close WO-RUN_A-TEST — the functional test of interlock `reator.T1.B1` on PT-007 — recording the result per element (detection vote, logic resolution, final-element stroke) and the closure date, so the proof-test clock acquires a record base. *Risk introduced by the action itself:* a functional test of the interlock may require bypass, forcing or a partial stroke of XV-1001/VLV-006, and XV-1001D is the actuator of the level cascade LIC-8001 (C6). Test planning must state the bypass duration, the compensating watch during it, and the reversion check — a bypass is a `critical` barrier state even without a demand (SKILL.md, B3).

**Definitive solution:**
1. Settle which test clock governs the PFD model — the creep clock or the maintenance calendar — and make the rule explicit in the reliability layer, so the same database stops returning two answers (`a2_estado_atual.contradicoes[0]`). The barrier-level impact is 1.0× today; the rule matters because the same defect on a dominant element would not be harmless.
2. Confirm that B2's demand trigger (ZT-1001 command-versus-position discrepancy) is instrumented and historised. A barrier whose demand cannot be observed cannot be credited or audited, whatever its PFD (risk-analysis-reference §6).
3. Run the threat-removal campaign for T1 and close the C8 classification, then restate the success criterion for B1 and B2 accordingly (design basis §6).
4. Restore continuous rate computation for the flagged tags: with the rate ladder empty, C1 and C7 cannot deliver their primary output, and the next analysis in this stream will inherit the same blindness.

**Suggested owner / deadline:** maintenance and instrumentation planning — execute WO-RUN_A-TEST at the earliest scheduled opportunity, with a stated date; process safety / reliability engineering — clock rule and ZT-1001 observability; process safety with the simulation owner — C8 campaign and rate-ladder restoration. Deadlines are for the facility to set; none is declared in the phase A block.

**Expected return / leading indicator:** after the test closes, PT-007's item PFD returns to a record-based clock and both clock readings converge; B1's barrier multiplier is expected to stay at 1.0× (the sensor is two orders below the dominant element), so the test's value is diagnostic, not numerical. Leading indicators to watch in the next analyses: days overdue on WO-RUN_A-TEST; inter-channel spread on PIT-7001 against the 17.5 kPa limit; per-channel sd against the 1.93 kPa design noise; FIT-1001 against the declared base-case 0.252 kscmh.

**Closure criteria:** WO-RUN_A-TEST executed and closed with the result recorded per element and any finding raised as a corrective order; the proof-test clock recomputed from the recorded test date, with both database readings agreeing; any bypass used during the test documented as restored; B1's PFD and the top event frequency re-evaluated on the post-test basis. The process variables being in band does not close this occurrence (SKILL.md, closure gate).

**Residual risk / accepting authority:** residual risk is not quantifiable from this context — tolerability is not determined. Acceptance belongs to the facility's designated risk authority, which is not named in the phase A block. This analysis does not authorise operation.

**Human decision:** pending

## Evidence and assumptions

- [demonstrated] `identidade.gatilho` + `a2_estado_atual.ordens_servico[1]`, 2025-05-31 — functional test WO-RUN_A-TEST on PT-007 / `reator.T1.B1` opened and overdue at `t_now`, 0 d, not executed. The trigger of this analysis.
- [demonstrated] `a3_cruzamentos[C2]`, `a1_base_de_projeto.barreiras[*]` — B1 and B2 at barrier multiplier 1.0×; dominant elements XV-1001 (53.7 %) and OP-B2 (83.5 %); PT-007 contributes 2.78e-05 to B1's 2.05e-02.
- [corroborated] `a3_cruzamentos[C4]` + `a2_estado_atual.grupo_votado` — 2oo3 group PT-007 intact by record *and* by reading: spread 0.62 kPa vs limit 17.5, all pairs inside 5.79 kPa, no divergent channel, no frozen channel, per-channel sd 1.95–1.97 against design noise 1.93.
- [demonstrated] `motores.conventional` / `motores.fuzzy` — top event frequency design vs current, ratio 1.0× on both engines; fuzzy label Moderate → Moderate; pathway T1 dominant at 70.1 % (conventional) / 74.1 % (fuzzy).
- [demonstrated] `a2_estado_atual.contradicoes[0]` — proof-test clock contradiction, 2.53× at the item, 1.0× at both barriers; the implied last test date 2024-05-31 is marked an assumption, not a record. Unresolved, as recorded.
- [demonstrated] `a3_cruzamentos[C6]` + design basis §4 — detection independent, final elements XV-1001 and VLV-006 shared; joint credit must not multiply the two PFDs; declared side effect of B1's action on the LIC-8001 level cascade.
- [undetermined] `a3_cruzamentos[C1]`, `envelope.lacuna` — no escalation window and no rate ladder at `t_now` (`serie insuficiente na janela`); the validity envelope is neither confirmed nor invalidated, and no time-to-target exists for any declared target.
- [undetermined] `a3_cruzamentos[C3]` — B2's window compression not measurable: no demand on B1 up to `t_now`. Design window 162 min and tolerable delay ≈ 67 min stand as design figures only (design basis §5).
- [undetermined] `a3_cruzamentos[C8].lacuna` + design basis §6 — threat T1 not classified; the removal test was not executed. The applicable success criterion for B1 and B2 is therefore unsettled.
- [inferred] `declarado.barreiras.B2.gatilho` vs `a2_estado_atual.margem` and `a2_estado_atual.demandas` — B2's declared demand trigger (ZT-1001) carries no series and no demand record in this context; B2's demand observability is not demonstrated. My inference from the phase A block, not a phase A finding (C5 named zero gaps).
- [inferred] `a2_estado_atual.margem.FIT-1001` (0.238 kscmh) vs design basis §2 (0.252 kscmh) — stream 1 feed reads ~5.6 % below the declared base case, with no rate and no dispersion statistic available to distinguish variation from drift. Recorded as an open question, not a finding; phase A declares no regime change (`a2_estado_atual.regime`).
- [assumption] `premissas_do_modelo` — model assumptions carried, not asset data: `mean_channel_pfd_between_tests` (λ_du·t/2), `items_without_test_records` (design PFD retained where no test record exists), `voted_group_without_reconfiguration`. The human-barrier override of 0.25 for overdue competence is *not* invoked in this run; OP-B2 stands at its design 0.10.
- [refuted] "barrier erosion at `t_now`" — refuted by the 1.0× multipliers on both barriers and the 1.0× top event ratio on both engines. The finding of this analysis is a lapsed verification, not a degraded barrier.