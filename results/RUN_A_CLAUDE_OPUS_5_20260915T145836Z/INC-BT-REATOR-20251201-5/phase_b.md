# Escalate now under the standing emergency procedure: PIT-7001 has reached the SIS trip at 2900 kPa with B1 failed on demand, no bowtie barrier left on pathway T1, and no declared protection layer between the SIS and the 3000 kPa physical limit.

## Fact

- Trigger of this analysis: `identidade.gatilho` — `record:process_event:trip_sis` at `2025-12-01T02:25:25` (`eventos_operacionais`, detail `{"limiar_kPa": 2900.0, "valor_kPa": 2900.1, "barreira": "SIS"}`). This is the third episode event in the stream, after the operating-condition change of 2025-11-28 and the interlock failure at 02:07:22.
- **What this trigger changed.** Until the trip, B1's demand (anchor `demandas.B1.instantes.ancora` = 02:07:22) was an open demand with no actuation signature. It is now settled: `demandas.B1.desfecho.criterio_atendido = false`, `minutos_da_demanda_ao_trip = 18.1`. The last declared automated layer has acted, and the next named target is the physical limit (`margem.PIT-7001.alvos_declarados`).
- PIT-7001 `margem.PIT-7001.valor` kPa; HI crossed by +150.1 and HIHI by +100.1 (`limiares_ja_cruzados`); SIS trip already crossed (distance −0.1); model physical limit 3000 kPa at +99.9 kPa, `tempo_min = 20.1` (computed from the current rate, design basis §3 for the limit).
- Rate `a2_estado_atual.taxas.PIT-7001` = 4.969 kPa/min (linear regression, 61 samples, 300 s window). Rate ladder `envelope.degraus`: 2.05 → 5.52 kPa/min across five declared windows, decision window HIHI→SIS at 5.52 (5.0× design).
- Alarms active: PIT-7001 HI for 28.2 min, HIHI for 17.9 min (`alarmes_ativos`, HIHI `e_demanda = 1`); FIT-1001 LO and LOLO for 145.3 min at −0.0016 kscmh, essentially flat (`margem.FIT-1001`).
- Data quality: voted group PT-007 running 2oo2, channel B frozen at 2708.4 kPa since ≈2025-08-29 (`grupo_votado.congelamento`), spread 192.01 kPa against a 17.5 kPa limit (`discrepancia_canais`). A and C agree within 5.79 kPa; B is the divergent channel by majority (`grupo_votado.concordancia_no_ultimo_instante`). The voted reading used for the trip is therefore supported by the two agreeing channels.
- The crossing is reproducible from the series, the alarm record and the process event. No `inconsistent trigger`.

## Scenario and mechanism

Qualitative chain: **threat T1** — loss of stream 1 feed (FIT-1001 at LOLO since 00:00:05) → **preventive barrier B1** (high-pressure interlock) demanded at HIHI and failed → **B2** (manual operator action) whose demand cannot be observed → **top event** loss of reactor control → the SIS trip at 2900 kPa is the layer beyond the bowtie's preventive barriers (`demandas.SIS.nota`), not a barrier of T1 → consequence and receptor: **not declared in any supplied input**.

Quantitative chain, link by link:

| Link | Value / field | Source strength |
|---|---|---|
| FIT-1001 at LOLO, flat | `margem.FIT-1001`, `a2_estado_atual.taxas.FIT-1001` | demonstrated (series + alarm record) |
| Pressure escalation 2.05–5.52 kPa/min vs 1.1 design | `envelope.degraus`, `envelope.referencia_de_projeto` | demonstrated |
| B1 detection worked | `demandas.B1.detectar.voto_2oo3_satisfeito = true`; event field `deteccao_ok = true` | demonstrated |
| B1 logic did not command outputs | `eventos_operacionais` falha_intertravamento, `saidas_comandadas = false`; WO-RUN_A-UZ007 | demonstrated |
| No actuation signature on any final element | `demandas.B1.agir.algum_como_esperado = false` (six tags, 5 min before/after the anchor, 5.0 pp deadband) | demonstrated |
| B1 PFD 2.053e-02 → 1.000 | `a1_base_de_projeto.barreiras[B1].pfd_atual`, C2 barrier multiplier 48.71× | demonstrated (open corrective WO on a 1oo1 item; PFD = 1 is a declared model assumption, `premissas_do_modelo.single_channel_item_with_known_failure`) |
| Top event frequency 1.754e-03 → 1.366e-01 /yr | `motores.conventional` | computed by the engine |

Escalation factors, each sourced: voted group degraded to 2oo2 since 2025-08-29 with repair backlog 94 d (`a3_cruzamentos[C4].relogio`); functional test of the interlock overdue 184 d (WO-RUN_A-TEST); operator competence overdue 124 d (WO-RUN_A-TRAIN); operating condition changed 2025-11-28 with `regime.revalidacao_registrada = false`.

The temporal ordering (condition change → three LO episodes → fast escalation → failed demand → trip) is a sequence, not a demonstration of root cause. The mechanism of the UZ-007 failure is not in the data.

## Analysis

### 1. Bowtie

**B1 — high-pressure interlock: `critical`, failed on demand.** The demand is settled, not probabilistic: the declared trigger fired (`demandas.B1.gatilho_declarado`), the 2oo3 vote was satisfied, no output was commanded, no final element moved, and the success criterion "pressure reverts without reaching the SIS trip" (design basis §5) was not met. The record implicates the **logic element UZ-007**: detection is exonerated by the vote and by `deteccao_ok = true`. What the data **cannot** separate is the state of the final elements XV-1001 and VLV-006 — they were never commanded, so they remain untested by this demand, and their design PFD contributions (1.1e-02 and 8.8e-03, `detalhe_componentes`) carry no observational support either way. C2: barrier multiplier 48.71×, worst component UZ-007 at 1515.15×, dominant element UZ-007 at 100 % of the current total.

**B2 — manual operator action: `critical`, and its demand is not observable.** Three independent reasons, none of which is "the operator failed":

- C3: the design tolerable delay of 67 min is 3.7× the entire measured HIHI→SIS window of 18.1 min (`a3_cruzamentos[C3]`). The barrier has no time to act in the current dynamics — the function cannot be met, whatever the PFD says. The design PFD's number survives and its meaning does not; adjusting it requires an approved method, which does not exist here. This is recorded as a gap, not as an adjusted figure.
- Competence renewal expired 124 d (WO-RUN_A-TRAIN, open). The current PFD `barreiras[B2].pfd_atual` (2.27× design, C2) is dominated by OP-B2 at 91.8 %, and that 0.25 is a **model assumption**, not asset data (`premissas_do_modelo.human_barrier_pfd_with_overdue_competence`).
- C5 gap: B2's declared trigger is a command-versus-position discrepancy on ZT-1001, and ZT-1001 exists in neither `ativos` nor `series`. Whether B2 was ever demanded cannot be answered from the dataset (`demandas.B2`). Since `saidas_comandadas = false`, no command was issued, so the discrepancy that constitutes B2's demand may never have been generatable at all.

**Independence and credit.** C6: detection independent (PT-007 vs ZT-1001), actuation **shared** (XV-1001, VLV-006). The PFDs of B1 and B2 must not be multiplied for joint credit (design basis §4). Beyond that, PT-007 is listed as a component of both barriers in `a3_cruzamentos[C6].comparado.shared_items` — the design basis says B2 detects on ZT-1001, and that contradiction between the asset composition and the design basis is itself a finding for the IPL review. No IPL/SIL credit is granted here: no approved analysis authorising credit was supplied.

**Pathway.** Conventional engine: pathway T1 now carries 99.6 % of the top event frequency against 70.1 % in design (`motores.conventional`). The fuzzy engine gives the same shift (98.8 %). The SIS trip is not a T1 barrier and receives no barrier credit in this report.

**C4 observability.** The group state is *known degraded* (record and reading agree: B failed-detected-unrepaired and B frozen). The clock that applies is the repair backlog, 94 d and running. Note the structural consequence: with B frozen at the old regime value, a HIHI vote required **both** A and C; a single further failure in A or C would have removed detection entirely.

### 2. Process

Trajectory, not last value. PIT-7001 rose from a valley of 2543 kPa at 00:44:25 through HI (01:57:10) and HIHI (02:07:30) to the trip at 02:25:25. The rate ladder is monotonically steepening toward the decision window: 3.62 (valley→trip), 4.58 (HI→HIHI), **5.52 (HIHI→trip)**, 5.23 (last 10 min). The episode-wide figure of 2.05 kPa/min is the only window below the 2.2 kPa/min invalidation limit, and it is the one that describes the decision worst.

**Envelope invalidated (C1), on three independent triggers** (`envelope.gatilhos_de_invalidacao`, design basis §7): rate above 2.2 kPa/min in 4 of 5 windows; operating-condition change without revalidation; and the design plateau absent — the 2850–2870 kPa band lasted 3.6 min at 5.31 kPa/min against 1.7 h at 0.27 kPa/min in the base case (`envelope.plato_medido`). The plateau is where the design basis says most of the barriers' margin sits (design basis §2). It did not exist in this episode. Consequently the 162 min HIHI→SIS window and the 67 min tolerable delay may not be cited as valid windows for this condition; they are cited above only as the design reference against which the compression is measured.

**C7 margins.** PIT-7001 has no alarm threshold ahead; the only declared targets left are the SIS trip (crossed) and the 3000 kPa physical limit at 99.9 kPa, 20.1 min at the current rate (computed, not read). That projection assumes the current rate persists; `demandas.SIS.taxa_depois_kpa_min` is null — the effect of the trip on the rate is not measurable at `t_now`, and this is the single most important unknown in the report.

Other tags are away from their thresholds and moving slowly or favourably: TIT-9001 120.43 °C falling 0.0036 °C/min; TIT-2101 93.48 °C falling; LIT-8001 71.56 % rising 0.0928 %/min, 144.8 min to HI. Note that the level is *rising*: this is coherent with B1 **not** having closed the feeds, and is the inverse of the declared B1 side effect (C6, level to ≈ −2.5 %). Coherence between tags supports the conclusion that no interlock action occurred.

**Precursors.** Since the operating-condition change of 2025-11-28 (load 15 %, feed setpoint scale 1.15) the voted PIT-7001 median moved from 2708.37 to 2559.51 kPa, a shift of −148.86 kPa, with three LO alarm episodes between the change and this episode (`regime`). The process was running in a displaced regime for three days, with alarms, before the excursion.

### 3. Context

- **Design basis validity.** `references/design-basis-barriers.md` declares performance only for the base case of §2. The plant is not in it (regime shift, `regime.deslocamento_kpa`), and `regime.revalidacao_registrada = false`. Per §7 the basis must be treated as **unverified**: the real actuation window is not known and must be derived from current data.
- **Management of change.** The condition change of 2025-11-28 has no subsequent revalidation work order or event. This is both an integrity finding and a C1 invalidation trigger (risk-analysis reference §4). Whether formal MOC was required is not determinable from the supplied inputs — the applicable rule was not provided; the absence of a record is a gap, not proof of non-compliance.
- **Mechanical integrity.** Interlock functional test overdue 184 d (WO-RUN_A-TEST, due 2025-05-31). The due date precedes the UZ-007 failure evidenced at 02:07:22 by 184 d, so the overdue test **did** fall due before the failure became manifest; whether it would have exposed this specific failure mode is not demonstrated — no test coverage statement was supplied. Channel B corrective open 94 d (WO-RUN_A-CH-B). Channel A had a comparable discrepancy in April, closed with a finding (WO-RUN_A-CH-A): two of three channels of the same transmitter group have now produced discrepancy findings within eight months. That pattern, plus an overdue test, an overdue training and an unrepaired channel coexisting on one safety function, is evidence of a **systemic backlog issue**, not of a single component fault.
- **Human factors.** The operator's task is judged here as task design, not performance: the barrier's demand signal is uninstrumented, the available window is 3.7× shorter than the declared tolerable delay, and competence renewal is 124 d overdue. The design basis states that all of B2's margin is perception and decision, none execution (§5) — exactly the margin a compressed window removes (risk-analysis reference §5). No operator action is implicated by any record in phase A.
- **Recorded contradiction, unresolved.** PT-007 PFD clock: 334 d since last test by the model clock versus 184 d overdue by the maintenance calendar (`a2_estado_atual.contradicoes`). Effect on the decision is negligible — B1 is 1.0 under both clocks, B2 ratio 1.01 — but the governing clock is a team decision, not an analyst's.

## Risk judgement

**Top event frequency** (cite the pair, do not average): conventional `motores.conventional.projeto` 1.754e-03 /yr → `motores.conventional.atual` 1.366e-01 /yr, ratio **77.89×** — the magnitude figure. Fuzzy `motores.fuzzy`: label **Moderate → High**, ratio 15.17× — the propagation of linguistic uncertainty, not a check on the conventional value. The label qualifies a frequency; it is neither a barrier state nor an acceptance criterion.

**Consequence and tolerability.** No consequence severity, receptor, or tolerability criterion is declared in any supplied input, and no vessel design pressure or downstream relief is confirmed (C5 gap 2). The correct conclusion is therefore: **barrier erosion demonstrated; risk tolerability not determined.** That is a result, not a failure of the analysis. Do not read the 1.366e-01 /yr as an accepted or rejected figure.

**Urgency: emergency.** It follows from proximity and time available, not from frequency:

- Both preventive barriers of pathway T1 are unavailable — one demonstrated failed on demand, one unable to meet its function in the measured window.
- The last declared automated layer has already acted (`demandas.SIS.atuou_em`).
- The only target ahead is the 3000 kPa physical limit, computed 20.1 min away at the current rate, and the design basis declares **no layer between the SIS and that limit** (C5 gap 2).
- The threat is not recovering: FIT-1001 flat at LOLO, and threat classification is a gap (C8) — the removal test was never run. Observed behaviour is consistent with a persistent threat, which is evidence, not a classification. Under a persistent threat no barrier produces a stable state; recovery requires removing the threat upstream.

**Uncertainty that bears on the decision:** the post-trip rate is not measurable at `t_now`, so the 20.1 min projection may be conservative or optimistic; OP-B2's PFD of 0.25 is a model assumption; PFD = 1 for UZ-007 is a model convention over an open WO; C5 gap 1 (a common-cause error shared by A and C cannot be excluded) means the trip value itself rests on two channels with no arbiter left. **Confidence: high** on the decisive link — B1 failed on demand is supported by the logic event, the absence of any actuation signature and the outcome against the declared criterion, three independent records. Confidence in the frequency magnitude is lower, and in tolerability nil.

## Recommendation

**Immediate containment.** Escalate to the shift supervisor and operations now and apply the standing emergency procedure for high reactor pressure with the interlock unavailable. Treat the SIS trip as having occurred with no credited preventive barrier behind it. Independently verify vessel pressure in the field (C5 gap 1) — the voted reading rests on two channels with no arbiter. Confirm in the field whether a relief device exists downstream of the SIS and what the vessel design pressure is (C5 gap 2); this is the question that decides how much time exists. Report authorises nothing: authorised people decide and execute; this analysis performs no manoeuvre and changes no setpoint, logic, bypass or work order.

**Before any manual feed closure via the B2 route**, note C6: XV-1001D is the actuator of the LIC-8001 level cascade; closing the feeds destroys inventory control, level goes to ≈ −2.5 % and a low-level trip follows roughly 1 h later (design basis §4). That is a declared secondary consequence to be anticipated, not a reason to withhold the action — the decision belongs to operations.

**Restoration**, in the hierarchy of the response (SKILL.md B5):

1. Repair UZ-007 under WO-RUN_A-UZ007 and prove the safety function end-to-end, including output commanding — the element the record implicates and the one the failed demand leaves untested downstream of it.
2. Repair PT-007 channel B (WO-RUN_A-CH-B, 94 d in backlog) and restore 2oo3.
3. Execute the overdue interlock functional test (WO-RUN_A-TEST, 184 d) and the overdue competence renewal (WO-RUN_A-TRAIN, 124 d).
4. **Instrument ZT-1001 or an equivalent command-versus-position signal.** A barrier whose demand cannot be observed cannot be credited or audited whatever its PFD (risk-analysis reference §6); this belongs at the top of the hierarchy, not the bottom.

**Definitive solution.** Revalidate the design basis windows under the current operating condition, per §7 — the 202/162/67 min figures do not describe this plant today, and no analysis on this pathway should cite them until they are re-measured. Reconcile the 2025-11-28 condition change through the facility's change-management route, with barrier-window revalidation as an explicit deliverable. Run the threat-removal test to close the C8 classification. Do not compensate the loss of an automatic barrier with an operator action under a window compressed 9.0× — an administrative control does not permanently replace engineering without a demonstration of adequacy, and C3 shows the demonstration would fail.

**Separate formal investigation recommended.** The coexistence of an overdue functional test, an overdue competence renewal, a 94-day unrepaired safety channel and an unrevalidated condition change on one safety function is evidence of systemic failure and exceeds what this analysis can resolve.

**Suggested owner / deadline.** Immediate containment: shift supervisor, now. UZ-007 repair and proof test, PT-007 channel B: maintenance lead, before any restart of the affected function. Window revalidation and MOC reconciliation: process safety lead. Formal investigation: the facility's authority. Deadlines to be set by those owners — this report does not set them.

**Expected return / leading indicator.** After repair: a passed end-to-end interlock proof test with outputs commanded; PT-007 spread back within the 17.5 kPa limit with three live channels; revalidated HIHI→SIS window measured under the current condition; backlog age of safety-critical work orders as the standing leading indicator.

**Closure criteria.** Pressure controlled and the threat removed or the upstream supply restored; B1 function restored **and tested** against the failure mode observed; B2's demand trigger instrumented; PT-007 at 2oo3; design basis windows revalidated under the current condition; residual risk reassessed with a declared consequence and tolerability. Pressure returning to band does not close this occurrence.

**Residual risk / accepting authority.** Not determined here — no tolerability criterion or consequence basis was supplied. Acceptance belongs to the facility's authorised function.

**Human decision:** pending

## Evidence and assumptions

- [demonstrated] `eventos_operacionais` / `demandas.B1`, 2025-12-01T02:07:22 — B1 demanded, 2oo3 vote satisfied, `saidas_comandadas = false`, no actuation signature on six tags: B1 failed on demand, logic UZ-007 implicated, final elements untested.
- [demonstrated] `demandas.B1.desfecho`, trip at 02:25:25, 18.1 min after the anchor — success criterion not met. The SIS action is a downstream layer, not B1's actuation (`demandas.SIS.nota`).
- [demonstrated] `envelope` / C1 — three invalidation triggers observed; design basis windows unverified for this condition.
- [demonstrated] C3 — HIHI→SIS window 18.1 min measured against 162 min design, 9.0× compression; B2's 67 min tolerable delay exceeds the whole measured window.
- [demonstrated] C4 / `grupo_votado` — PT-007 known degraded, channel B frozen at 2708.4 kPa since ≈2025-08-29, repair backlog 94 d, spread 192.01 vs 17.5 kPa.
- [demonstrated] C6 / design basis §4 — shared final element XV-1001/VLV-006; PFDs of B1 and B2 must not be multiplied.
- [corroborated] `regime` + `alarmes_normalizados` — condition change 2025-11-28, −148.86 kPa regime shift, three LO episodes, no revalidation recorded.
- [corroborated] WO-RUN_A-TEST (184 d), WO-RUN_A-TRAIN (124 d), WO-RUN_A-CH-B (open), WO-RUN_A-CH-A (closed with finding) — systemic maintenance backlog on one safety function.
- [inferred] `margem.PIT-7001` — 20.1 min to the 3000 kPa limit; depends on the current rate persisting after the trip, which `demandas.SIS.taxa_depois_kpa_min` cannot confirm.
- [inferred] C8 — FIT-1001 flat at LOLO for 145.3 min is behaviour consistent with a persistent threat; the classification itself is undetermined.
- [undetermined] C5 gap 1 — common cause shared by channels A and C; external check: independent field pressure measurement.
- [undetermined] C5 gap 2 — the layer downstream of the SIS; external check: confirm relief provision and vessel design pressure.
- [undetermined] C5 gap 3 — whether B2 was ever demanded; ZT-1001 absent from `ativos` and `series`.
- [undetermined] Consequence severity, receptors and tolerability criterion — not present in any supplied input.
- [assumption] `premissas_do_modelo` — OP-B2 PFD 0.25 with overdue competence; UZ-007 PFD 1.0 on an open corrective WO; 2oo3→2oo2 without reconfiguration; mean channel PFD λ·t/2. None is asset data.
- [recorded contradiction, unresolved] `a2_estado_atual.contradicoes` — PT-007 model clock (334 d) vs calendar (184 d overdue); barrier effect B1 1.00×, B2 1.01×.