---
incident_id: INC-BT-REATOR-20251201-6
bowtie_id: BT-REATOR
opened_at: 2025-12-01T02:30:20
engine: conventional
status: action_required
urgency: emergency
confidence: high
---

# Escalate to operations now under the standing emergency procedure: reactor pressure is above the SIS trip and still rising with no declared layer before the physical limit, B1 failed on demand, and no preventive barrier on pathway T1 is available.

## Fact

- Parameter: PIT-7001 (reaction vessel pressure), voted series. Value at `t_now` 2923.1756 kPa (`a2_estado_atual.margem.PIT-7001.valor`), rising at 4.5366 kPa/min over a 300 s window, 61 samples (`a2_estado_atual.taxas.PIT-7001`).
- Criteria crossed: HI 2750 (exceedance +173.18) and HIHI 2800 (+123.18) — `margem.PIT-7001.limiares_ja_cruzados`; SIS trip 2900 kPa crossed, distance −23.18 kPa (`margem.PIT-7001.alvos_declarados[0]`, source `alarm_config.trip_sis`). Remaining declared target: model physical limit 3000 kPa, distance +76.82 kPa, 16.9 min at the measured rate (`alvos_declarados[1]`, `computed`, design basis §3).
- Instants and durations: HI active since 2025-12-01T01:57:10 (33.2 min), HIHI since 02:07:30 (22.8 min, `e_demanda=1`) — `a2_estado_atual.alarmes_ativos`. Interlock failure event 02:07:22, SIS trip 02:25:25 — `a2_estado_atual.eventos_operacionais`.
- Concurrent: FIT-1001 below LO and LOLO since 00:00:05 (150.2 min) at 0.0017 kscmh, rate ≈ 0 (`alarmes_ativos`, `margem.FIT-1001`). TIT-9001, LIT-8001 and TIT-2101 are inside band with small rates (`a3_cruzamentos[C7]`).
- Operating mode: standard campaign at load 15 %, feed setpoints scaled 1.15, changed 2025-11-28T00:00:00 (`a2_estado_atual.regime.mudanca`). This is **not** the design base case of design basis §2.
- Current state: excursion active and unarrested; rate after the SIS acted 4.54 kPa/min (`envelope.degraus[after the SIS acted]`).
- Data quality — the crossing is reproducible. Channels A and C agree within 5.79 kPa (3× design noise) and both were above HIHI at the demand; B is the majority-identified divergent channel, flat at 2708.4 kPa (sd 0.2, band ±1.5) since about 2025-08-29 against a pre-change regime of 2708.37 kPa — a frozen-at-regime failure mode, not a drift (`a2_estado_atual.grupo_votado`). Group spread 214.59 kPa against a limit of 17.5 (`discrepancia_canais`). The voted reading is therefore sound; the group is running 2oo2.
- This trigger (`end_of_record`, 02:30:20) settles what earlier points in the stream could not: B1's demand outcome is now closed as **not met** (`demandas.B1.desfecho.criterio_atendido = false`), and the escalation has continued for 4.9 min *past* the last automated layer.

## Scenario and mechanism

Qualitative chain: loss of stream 1 feed (threat T1) → B1 high-pressure interlock → B2 manual operator action → top event "loss of reactor control" → SIS trip (a layer beyond the bowtie's preventive barriers, `demandas.SIS.nota`) → consequence not declared in the available basis.

Quantitative chain, link by link:

| Link | Evidence | Strength |
|---|---|---|
| FIT-1001 below LOLO for 150.2 min, rate ≈ 0 → feed loss sustained | `alarmes_ativos`, `margem.FIT-1001` | demonstrated |
| Pressure escalation at 2.19–5.52 kPa/min, 2.0–5.0× the design 1.1 kPa/min | `envelope.degraus`, `referencia_de_projeto` | demonstrated |
| Demand on B1 raised at HIHI; detection healthy, 2oo3 vote satisfied by A and C | `demandas.B1.detectar` | demonstrated |
| Logic UZ-007 commanded no outputs (`saidas_comandadas=false`, `deteccao_ok=true`) | `eventos_operacionais` 02:07:22 + `WO-RUN_A-UZ007` | demonstrated |
| Final elements did not move: all four XV-1001 valves opened slightly instead of closing, FCV-0601 closed 2.08 pp instead of opening, level did not fall | `demandas.B1.agir.sinais`, `algum_como_esperado=false` | demonstrated |
| B1 element implicated = logic (decide). Detection is exonerated by the vote record; the final elements were never commanded, so the data **cannot** separate a healthy actuator from a stuck one | `demandas.B1.detectar` vs `.agir` | demonstrated (logic), undetermined (actuator) |
| B2's declared demand is a command-versus-position discrepancy on ZT-1001; no command was issued, and ZT-1001 exists in neither `ativos` nor `series` | `demandas.B2`, C5 gap 3 | inferred — if B1's logic never commands, the discrepancy that constitutes B2's demand cannot arise; this is a structural blind spot, not an operator failure |
| SIS reached 2900.1 kPa at 02:25:25, 18.1 min after B1's demand; pressure kept rising afterwards | `demandas.SIS`, `envelope.degraus` | demonstrated |
| No declared layer between the SIS and 3000 kPa | C5 gap 2, design basis §3 | demonstrated (as a documentary gap) |

The SIS acting is evidence that B1 did **not** arrest the excursion; it is not evidence that B1 acted (SKILL.md, A2). Temporal correlation between the 2025-11-28 condition change and the escalation rate is not established as causal here.

## Analysis

### 1. Bowtie

**B1 — high-pressure interlock: `critical`.** Demanded at 02:07:22 and the success criterion ("pressure reverts without reaching the SIS trip", design basis §5) was not met (`demandas.B1.desfecho`). A demand settles the state, whatever the PFD says. C2: barrier multiplier `a1.barreiras[B1].c2.multiplicador_barreira` = 48.71×, worst component UZ-007 at 1515.15×, dominant element UZ-007 at 100 % of the total — the barrier PFD is at 1.0 because a 1oo1 logic solver with an open corrective order is modelled unavailable (`premissas_do_modelo.single_channel_item_with_known_failure`, an assumption). The observation on demand corroborates the assumption independently.

**B2 — manual operator action: `critical`.** Not on its PFD (2.27× design, `c2.multiplicador_barreira`), but on two independent grounds: (i) C3 — the HIHI→SIS window measured 18.1 min against 162 min in design, a 9.0× compression, and B2's design tolerable delay of 67 min is 3.7× the *whole* measured window; per the C3 rule a barrier whose tolerable delay exceeds the measured window has no time to act. All of B2's margin is perception and decision, none is execution (design basis §5), so compression removes the margin outright. (ii) Its declared demand trigger is uninstrumented (C5 gap 3), so the barrier cannot be shown to have been demanded, to have responded or to have failed — it cannot be credited or audited. The design PFD of 0.272 is **not** adjusted here: adjusting requires an approved method (SKILL.md B3); the compression is recorded as a gap. Competence renewal is overdue by 124 d (`WO-RUN_A-TRAIN`), and the 0.25 PFD applied to OP-B2 is a model assumption, not asset data.

**Dependencies and credit.** C6: detection is independent (PT-007 vs ZT-1001) but the final element is shared (XV-1001 and VLV-006) — joint credit must not multiply the two PFDs (design basis §4). A single valve-arm failure takes both barriers; a sensor failure takes only one. No IPL/SIL credit is granted here beyond what the approved basis declares.

**Escalation factors.** PT-007 group known degraded at 2oo2 since 2025-08-29, repair backlog 94 d (`a3_cruzamentos[C4].relogio`); functional test of the interlock overdue 184 d (`WO-RUN_A-TEST`, due 2025-05-31). The overdue test removed the scheduled opportunity to find a logic failure before a demand; the data does not date the onset of the UZ-007 failure, so it cannot be said that the test *would have* exposed it.

**Declared side effect (C6).** B1's action closes XV-1001D, the actuator of the LIC-8001 level cascade; inventory control is lost, level goes to about −2.5 % and a low-level trip follows roughly 1 h later. Because B2 shares those final elements, a manual closure carries the same secondary consequence. It is a declared secondary consequence, not a failure against the T1 top event (design basis §4–5).

**Pathway T2** (cooling valve jam → B3/B4) contributes 0.4 % of the current top event frequency (`motores.conventional.atual.pathways`); no precursor is visible in TIT-9001 or TIT-2101 (C7).

### 2. Process

The trajectory, not the last value: the rate ladder spans 2.19 to 5.52 kPa/min across six declared windows, a 2.52× dispersion (`envelope.dispersao`). The whole-day figure (2.19, below the 2.2 invalidation threshold) understates the situation; the window in which the decision was taken — HIHI→SIS — is 5.52 kPa/min, 5.0× design. Five of six windows exceed 2.2 kPa/min.

C1 verdict: **envelope invalidated**, all three declared triggers observed (`envelope.gatilhos_de_invalidacao`) — rate above 2.2 kPa/min; operating-condition change of 2025-11-28 with no revalidation recorded; and the design plateau absent (2850–2870 kPa lasted 3.6 min at 5.31 kPa/min, against 1.7 h at 0.27 kPa/min in design). The plateau is where most of the barriers' design margin sat (design basis §2); it did not exist in this episode. Consequently the §5 windows (202 / 162 / 67 min) do not describe this condition and must not be cited as available time.

C7, margin: HI and HIHI already crossed; SIS crossed by 23.18 kPa; the only target ahead is the 3000 kPa model physical limit at 76.82 kPa, 16.9 min at the current rate (`computed`). Level is rising slowly (12.61 % to HI, 597.6 min) and cooling water outlet is 6.55 °C from HI (1007.7 min) — neither is a near-term constraint. Pre-episode precursors: three LO alarms on PIT-7001 between the 2025-11-28 change and the episode, with a regime shift of −148.86 kPa (median 2708.37 → 2559.51, `a2_estado_atual.regime`), i.e. the process had been running well below the validated steady pressure before the excursion.

C8: the threat classification requires a removal test that was not executed for this bowtie (design basis §6). Observed behaviour — feed at 0.0017 kscmh with rate ≈ 0 for 150.2 min and no recovery — is consistent with a persistent threat. That is evidence, not a classification. If it is persistent, no barrier produces a stable state and "the barrier worked" would mean "we reached the upstream repair alive".

### 3. Context

- **Design basis**: `references/design-basis-barriers.md`, declared and loaded (`a1_base_de_projeto.base_de_projeto_declarada`). It describes the base case only and is now invalidated for this condition (C1).
- **Management of change**: the operating-condition change of 2025-11-28 (load 15 %, feed setpoint scale 1.15) has no revalidation of the barrier windows recorded (`regime.revalidacao_registrada = false`). Per the risk analysis reference §4 this is simultaneously an integrity finding and an envelope invalidation trigger, and warrants MOC triage. Whether MOC was formally required is not determined from the available records — absence of a record is a gap, not proof of non-compliance.
- **Mechanical integrity / testing**: `WO-RUN_A-TEST` (interlock functional test) overdue 184 d; `WO-RUN_A-CH-B` (channel B corrective) open 94 d; `WO-RUN_A-TRAIN` (OP-B2 competence) overdue 124 d; `WO-RUN_A-UZ007` opened at the demand with a failure found. One closed order with a finding on the same group (`WO-RUN_A-CH-A`, channel A, 2025-04). Three overdue safety-related orders on one pathway plus an unrepaired redundancy failure is evidence of a systemic backlog, not an isolated defect.
- **Recorded contradiction, unresolved**: the PT-007 PFD creep clock says 334 d since the last test (interval 365 d); the maintenance calendar says the functional test is overdue by 184 d (`a2_estado_atual.contradicoes[0]`). Item PFD differs by 1.64× between the two clocks; the effect at barrier level is negligible (B1 ratio 1.00, B2 ratio 1.01). Which clock governs is a decision for the team, not for this report.
- **Human factors**: do not read this as operator error. B2's demand signal is not instrumented, its competence renewal is overdue, and the available window was compressed 9×. Task, instrumentation and organisation account for the failure of the human layer to be creditable here.

## Risk judgement

- **Top event frequency** (`motores`, exposure window 1.0 yr, current PFDs B1 = 1.0, B2 = 0.272206): conventional design 1.7541e-03 /yr → current 1.3663e-01 /yr, ratio 77.89× (`motores.conventional`). Fuzzy design → current label Moderate → High, ratio 15.17× (`motores.fuzzy`). Cite the conventional engine for magnitude and the fuzzy engine for the propagation of linguistic uncertainty; neither checks the other. The T1 pathway now carries 99.6 % of the current conventional frequency, against 70.1 % in design.
- **Consequence and receptors**: not declared in the available basis. No tolerability criterion, SIL target or risk matrix is present in the inputs.
- **Conclusion on tolerability**: **barrier erosion demonstrated; risk tolerability not determined.** That is a result, not a failure of the analysis. Neither the fuzzy label nor the 77.89× ratio is an acceptance criterion.
- **Uncertainty**: high on consequence (no declared consequence or receptor); high on what lies downstream of the SIS (C5 gap 2); moderate on the state of the final elements, which were never commanded and therefore never tested in this demand; low on the facts of the demand itself, which are corroborated by three independent records (process event, work order, actuation signature).
- **Urgency: emergency.** Not from frequency but from proximity: the last declared automated layer has acted, the excursion continues at 4.54 kPa/min, the only remaining declared target is 76.82 kPa away (16.9 min, `computed`), the design basis declares no layer in between, and both preventive barriers of the pathway are unavailable. The C7 time-to-target, not the distance, is the quantity that governs. High-consequence/low-frequency is not discounted by the absence of history.

## Recommendation

**Immediate containment (do not wait for further analysis):** escalate to the operations shift supervisor now and apply the standing emergency procedure for pressure excursion beyond the SIS trip. Treat B1 as unavailable and do not wait on it. Confirm by field means whether pressure relief exists downstream of the SIS and what the vessel design pressure is (C5 gap 2) — the analysis cannot answer it. Obtain an independent field measurement of vessel pressure to close C5 gap 1 (A and C agree, so the majority already identifies B as divergent; what is open is a common cause in the agreeing pair). Any manual isolation via XV-1001/VLV-006 must be decided and executed by authorised operations staff, with the declared C6 side effect anticipated: loss of the LIC-8001 level cascade, level to about −2.5 % and a low-level trip roughly 1 h later. Under a threat that behaves as persistent, success means reaching the upstream feed repair safely, not the process returning to normal.

**Restoration:** repair UZ-007 and close `WO-RUN_A-UZ007` with a post-repair proof test covering the observed failure mode (demand raised, no outputs commanded); repair PT-007 channel B and close `WO-RUN_A-CH-B`, returning the group to 2oo3; execute the overdue interlock functional test `WO-RUN_A-TEST`; execute the overdue OP-B2 competence renewal `WO-RUN_A-TRAIN`. Verify XV-1001A–D and FCV-0601 stroke independently — this demand did not test them.

**Definitive solution**, in hierarchy order: (1) address the threat itself — restore stream 1 feed and remove the persistent driver, since no barrier on this pathway produces a stable state under it (C8); (2) engineering — instrument the ZT-1001 command-versus-position signal, so B2's demand can be observed at all; per the risk analysis reference §6 this sits at the top of the hierarchy, not the bottom, because a barrier whose demand cannot be observed cannot be credited; (3) close the MOC on the 2025-11-28 operating-condition change with an experimental revalidation of the HI→SIS and HIHI→SIS windows and of B2's tolerable delay under the current load, per `references/producing-a-design-basis.md` steps 2–6; (4) run the threat-removal test to settle the C8 classification; (5) decide and document which PFD clock governs PT-007 (model vs calendar contradiction). Administrative measures — a watch-keeping instruction on PIT-7001 — do not permanently compensate for an unavailable interlock and a non-creditable human layer.

**Separate formal investigation:** recommended. Three overdue safety-related work orders on one pathway, a 94-day unrepaired redundancy failure and an uninstrumented demand trigger together indicate systemic failure, which is outside the scope of this analysis.

**Suggested owner / deadline:** operations shift supervisor — immediate, now. I&C maintenance lead — UZ-007 and PT-007.B before any return to service. Process safety authority — MOC closure and window revalidation before the next campaign at the changed load. Plant manager — commission the formal investigation within the facility's standard period.

**Expected return / leading indicator:** PIT-7001 rate returning below 2.2 kPa/min (design basis §7) and pressure reverting below HIHI; PT-007 group spread back within its 17.5 kPa limit with three live channels; zero overdue safety-critical work orders on `reator.T1`; a proof-test record on UZ-007 showing outputs commanded on a simulated HIHI demand.

**Closure criteria:** not met, and the pressure returning to band will not on its own meet them. Required: condition controlled; B1 function restored **and** proof-tested on the observed failure mode; PT-007 back to 2oo3; the ZT-1001 gap either instrumented or B2's credit formally withdrawn; design basis windows revalidated under the current operating condition; the C5 questions answered by their external checks; residual risk reassessed and accepted; all open items traceable.

**Residual risk / accepting authority:** not determined here — no consequence, receptor or tolerability criterion exists in the supplied basis. Acceptance belongs to the facility's designated risk authority, not to this analysis.

**Human decision:** pending

## Evidence and assumptions

- [demonstrated] `process_events` 2025-12-01T02:07:22, `falha_intertravamento` on UZ-007 (`saidas_comandadas=false`, `deteccao_ok=true`) — B1's logic did not execute the safety function on a valid demand.
- [corroborated] `demandas.B1.agir.sinais` + `WO-RUN_A-UZ007` (opened at the demand, failure found) — no final element moved as expected in B1's own demand window; `algum_como_esperado=false`.
- [demonstrated] `demandas.B1.detectar` — 2oo3 vote satisfied by channels A and C at HIHI; detection is exonerated.
- [demonstrated] `demandas.B1.desfecho` — SIS trip reached 18.1 min after the demand; design basis §5 success criterion not met.
- [demonstrated] `envelope.gatilhos_de_invalidacao` — all three design basis §7 invalidation triggers observed; the §5 windows do not describe this condition.
- [demonstrated] `a3_cruzamentos[C3]` — HIHI→SIS window compressed 9.0×; B2's 67 min tolerable delay is 3.7× the whole measured window.
- [demonstrated] `grupo_votado` — channel B frozen at 2708.4 kPa (sd 0.2) since about 2025-08-29, 0.03 kPa from the pre-change regime median; failure mode is frozen-at-regime, evidenced by its own variance, not by the spread.
- [demonstrated] `a2_estado_atual.ordens_servico` — `WO-RUN_A-TEST` overdue 184 d, `WO-RUN_A-TRAIN` overdue 124 d, `WO-RUN_A-CH-B` open 94 d.
- [demonstrated] `a3_cruzamentos[C6]` / design basis §4 — detection independent, final element shared; PFDs must not be multiplied.
- [inferred] B2's declared demand could not arise, because no command was issued and there was therefore no command-versus-position discrepancy to detect. Depends on the design basis §4 wording of the trigger; ZT-1001 is absent from `ativos` and `series` (C5 gap 3).
- [inferred] Threat T1 behaves as persistent — FIT-1001 at 0.0017 kscmh with rate ≈ 0 for 150.2 min, no recovery. Behaviour only; the classification test was not run (design basis §6).
- [undetermined] Common cause affecting the agreeing pair A/C (C5 gap 1); what lies downstream of the SIS before 3000 kPa (C5 gap 2); the health of XV-1001A–D and FCV-0601, which were never commanded; whether the UZ-007 failure predated the overdue functional test.
- [undetermined] Consequence, receptors and tolerability — not present in the supplied basis; no value fabricated.
- Assumptions carried, not read: `premissas_do_modelo.single_channel_item_with_known_failure` (UZ-007 PFD = 1.0 from work-order opening), `human_barrier_pfd_with_overdue_competence` (OP-B2 = 0.25), `voted_group_without_reconfiguration` (fall to 2oo2), `mean_channel_pfd_between_tests`, `items_without_test_records`. Recorded contradiction on the PT-007 clock (`a2_estado_atual.contradicoes[0]`) left unresolved by design.
- Analytical limits: the bowtie organises, it does not prove causality, independence or compliance; this report is not a PHA/LOPA, not a formal investigation, and not authorisation to operate.