---
incident_id: INC-BT-REATOR-20251201-4
bowtie_id: BT-REATOR
opened_at: 2025-12-01T02:07:30
engine: conventional
status: action_required
urgency: emergency
confidence: high
---

# Escalate now to operations: B1 was demanded at HIHI and commanded nothing — the high-pressure interlock is failed on demand with PIT-7001 rising at `a2_estado_atual.margem.PIT-7001.taxa_por_min` and ~`a2_estado_atual.margem.PIT-7001.alvos_declarados[0].tempo_min` to the SIS trip; apply the standing emergency procedure for an uncontrolled pressure excursion with the interlock unavailable.

## Fact

- PIT-7001 crossed HIHI at `identidade.gatilho[2].ts`, value `identidade.gatilho[2].valor` kPa against threshold `identidade.gatilho[2].limite`; HI has been active `a2_estado_atual.alarmes_ativos[2].ativo_ha_min` min. Rate over the last 10 min: `a2_estado_atual.taxas.PIT-7001.valor` kPa/min (computed, linear regression, 61 samples / 300 s).
- Logic event `falha_intertravamento` at `a2_estado_atual.eventos_operacionais[1].ts`: `deteccao_ok = true`, `saidas_comandadas = false`, asset UZ-007, barrier reator.T1.B1. Corrective WO-RUN_A-UZ007 opened at the same instant (`a2_estado_atual.ordens_servico[4]`).
- Demand on B1 is anchored on its own declared trigger (`a2_estado_atual.demandas.B1.instantes.ancora`); the 2oo3 vote was satisfied (`a2_estado_atual.demandas.B1.detectar.voto_2oo3_satisfeito`), channels A and C above HIHI, B at 2708.51.
- Actuation signature in B1's own window: `a2_estado_atual.demandas.B1.agir.sinais` is empty — no final-element movement recorded. Outcome not yet determined (`a2_estado_atual.demandas.B1.desfecho.nota`): the SIS trip at `a2_estado_atual.demandas.B1.desfecho.proxima_camada.valor` kPa has not been reached at t_now.
- FIT-1001 LO and LOLO active for `a2_estado_atual.alarmes_ativos[0].ativo_ha_min` min at essentially zero flow, with no recovery trend (`a3_cruzamentos[7].comparado.rate.valor`).
- Data quality: PIT-7001 channel B is flat at `a2_estado_atual.grupo_votado.congelamento.valor_medio` kPa since ~`...parado_desde_aprox` (sd 0.2 over 30 d against A/C sd 72.91); the majority pair A–C agrees within `a2_estado_atual.grupo_votado.concordancia_no_ultimo_instante.tolerancia_kpa` kPa, so the divergent channel is identified and the voted value is usable. Trigger is reproducible from three independent record types (process event, work order, alarm). No override, saturation or clock anomaly reported.

**What this trigger changed.** The previous condition of this stream was calendar-driven erosion of B1 (channel B unrepaired, functional test overdue). This trigger converts that erosion into an observed failure: B1's PFD moves from `a1_base_de_projeto.barreiras[0].pfd_projeto.valor` to `...pfd_atual.valor`, pathway T1 rises to `motores.conventional.atual.pathways[0].contribuicao_pct` % of the top event frequency, and the pathway's remaining prevention is a single human barrier whose demand trigger is not instrumented.

## Scenario and mechanism

Qualitative: loss of stream 1 feed (T1) → B1 automatic high-pressure interlock → B2 manual operator action → top event "Perda de controle do reator" (`diagrams/BT-REATOR.txt`) → downstream layer SIS trip at 2900 kPa (design basis §3, a layer, not a bowtie barrier).

Quantitative chain:

| Link | Value | Source | Strength |
|---|---|---|---|
| FIT-1001 ≈ 0, LO/LOLO active, no recovery | `a2_estado_atual.margem.FIT-1001` | series/alarm_events | demonstrated |
| Pressure escalation above the validated rate | `envelope.degraus` (1.47→4.58 kPa/min, ratio 3.12) vs design 1.1 | design basis §2 | demonstrated |
| B1 detection functioned, logic did not command | `a2_estado_atual.demandas.B1.detectar` + `...decidir` | process_events, work_orders | demonstrated |
| B1 unavailable, PFD = 1 | `a1_base_de_projeto.barreiras[0].pfd_atual` (model assumption `single_channel_item_with_known_failure`) | reliability model | corroborated by the demand record |
| B2 degraded, dominated by OP-B2 | `a1_base_de_projeto.barreiras[1].c2` | WO-RUN_A-TRAIN + model assumption 0.25 | inferred (PFD value is an assumption, not asset data) |
| Top event frequency ×`motores.conventional.razao` | `motores.conventional` | engines | computed |

The link that supports the breach is the logic solver: detection was correct and the outputs were not commanded. The data **cannot** separate logic from final element in the sense of proving XV-1001/VLV-006 would have worked — they were never commanded, so their capability is untested in this demand.

## Analysis

### 1. Bowtie

- **B1 — `critical`.** A demand occurred and the safety function did not execute (`a2_estado_atual.demandas.B1.decidir`). An observation outranks a probability (SKILL.md, B3). C2: barrier multiplier `a3_cruzamentos[1].comparado.B1.barrier_multiplier`, worst component UZ-007 at `...worst_component.multiplicador`, and UZ-007 is now the dominant element at 100 % of the total — the sensor degradation (PT-007, 34.36×) is no longer what governs this barrier.
- **B2 — `degraded`, and its demand status is undetermined.** C2: barrier multiplier `a3_cruzamentos[1].comparado.B2.barrier_multiplier`, dominant element OP-B2 at 91.8 % of the total, driven by the overdue competence WO (`a2_estado_atual.ordens_servico[2]`, 124 d). Two qualifications that the PFD does not carry: (i) B2's declared trigger is a command-versus-position discrepancy on ZT-1001, and no command was issued (`a2_estado_atual.demandas.B2.comando_registrado_na_demanda_de_B1 = false`) — if no command exists there may be no discrepancy to detect, so B2 may not be demanded at all by its declared route (inferred); (ii) C3 reports the real window not measurable at t_now, but the design tolerable delay for B2 is `envelope.janelas_de_projeto.atraso_tolerav_b2_min` min against a projected `a2_estado_atual.margem.PIT-7001.alvos_declarados[0].tempo_min` min to the SIS trip at the current rate. The design PFD's *meaning* does not survive that comparison; this is recorded as a gap, and the PFD is not adjusted (no approved method).
- **Independence / IPL credit.** C6: detection independent (PT-007 vs ZT-1001), actuation shared (XV-1001, VLV-006). Joint credit must not be taken by multiplying the two PFDs. No IPL/SIL credit is claimed here beyond what the approved basis declares.
- **Voted group (C4).** Known degraded, 2oo2 without reconfiguration, repair backlog `a3_cruzamentos[3].relogio` (94 d). The clock is the repair backlog, not the test interval — but the functional test WO-RUN_A-TEST is itself overdue by 184 d, so the group's PFD growth and its verification are both uncovered.
- **Contradiction (recorded, not resolved).** PT-007 model clock vs maintenance calendar: item PFD 1.64× apart, barrier effect `a2_estado_atual.contradicoes[0].sensibilidade.por_barreira` (B1 1.00×, B2 1.01×). Immaterial to this decision; still a data-governance item.
- **Declared side effect (C6), not yet realised.** B1's action closes the A+C feed valve, which actuates the level cascade LIC-8001; inventory control is lost and a low-level trip follows ~1 h later. Because B1 commanded nothing, this has not occurred — LIT-8001 is at `a2_estado_atual.margem.LIT-8001.valor` % with rate 0.0010 %/min. Any manual or restored closure will produce it.

### 2. Process

PIT-7001 fell to a valley at 00:44:25 and has climbed since: `envelope.degraus` gives 1.47 kPa/min over the day, 3.14 from the valley, 4.58 between HI and HIHI and over the last 10 min — a 3.12× spread, so no single number describes this episode. Three of four windows exceed the invalidation limit of 2.2 kPa/min (design basis §7). Distance and rate side by side (C7): HI exceeded by 50.38 kPa, HIHI by 0.38 kPa, SIS trip 99.62 kPa ahead ≈ 19.9 min, physical limit 199.62 kPa ahead ≈ 39.9 min (computed from the measured rate, not read). TIT-9001, LIT-8001 and TIT-2101 are all far from their thresholds with rates at noise level — this is a single-variable pressure excursion. TIT-2101 falling at 0.0192 °C/min with feed lost is consistent with reduced reaction duty, not with a cooling fault.

Because C1 declares the envelope invalidated, the design windows (HI→SIS 202 min, HIHI→SIS 162 min) must not be cited as available time. The usable time figure is the C7 projection above.

### 3. Context

- **Management of change.** `operating_condition_change` at 2025-11-28T00:00:00 (load 15 %, feed setpoint scale 1.15) shifted the voted pressure regime by `a2_estado_atual.regime.deslocamento_kpa` kPa, with three subsequent LO alarms and `revalidacao_registrada = false`. That is simultaneously an integrity finding and a declared envelope invalidation trigger (design basis §7; risk-analysis reference §4). The design basis' base case (2708 kPa steady) no longer describes the plant.
- **Mechanical integrity.** Functional test of the interlock overdue 184 d and channel B corrective open 94 d, both on the barrier that has now failed on demand. The overdue test predates the UZ-007 failure record, but phase A carries no failure date for UZ-007 other than the WO opening at the demand, so whether an on-time test would have exposed it is not demonstrable from these records.
- **Human factors.** OP-B2 competence renewal overdue 124 d and open. Per the design basis §5, the whole of B2's margin is perception and decision, not execution; under a compressed window that margin is the first thing lost. No blame attaches to the operator: the task now demands diagnosis of an interlock failure through an uninstrumented signal.
- **Threat classification (C8).** Not classified — the removal test was never executed (design basis §6). Observed behaviour (feed at zero, flat, 127 min) is *consistent with* a persistent threat: barriers buy time to the upstream repair, they do not produce a stable state.
- **Gaps carried from phase A (C5).** (1) Common cause in the agreeing pair A–C cannot be excluded — external check: independent field pressure measurement. (2) Whether B2 was ever demanded cannot be answered — ZT-1001 is in neither `ativos` nor `series`; external check: instrument feed valve position, or the control-room record. Additionally, phase A carries no evidence of the SIS trip's own availability, and the design basis declares no layer between it and the physical limit — status `not demonstrated`.

## Risk judgement

Top event frequency, design → current (`motores`): conventional `motores.conventional.projeto.evento_topo_por_ano` → `motores.conventional.atual.evento_topo_por_ano` /yr, ratio `motores.conventional.razao`; fuzzy `motores.fuzzy.projeto.evento_topo_por_ano` → `motores.fuzzy.atual.evento_topo_por_ano` /yr, label `Moderate → High`, ratio `motores.fuzzy.razao`. The conventional figure is the magnitude; the fuzzy label is the propagation of linguistic uncertainty and is not a check on it, nor an acceptance criterion. Pathway T1 now carries `motores.conventional.atual.pathways[0].contribuicao_pct` % of the total.

Frequency is not risk. Phase A carries no consequence severity, no receptor set and no tolerability criterion for "Perda de controle do reator". The correct conclusion is therefore: **barrier erosion demonstrated and preventive barrier failure on demand observed; risk tolerability not determined.**

Urgency is **emergency**, and it does not depend on tolerability: the pathway's first preventive barrier is failed on demand, the second is degraded with an unobservable demand trigger and a tolerable delay larger than the projected time to the next layer, the threat is not recovering, the validity envelope is invalidated on two independent triggers, and the projected time to the SIS trip is ~19.9 min (computed). Uncertainty raises caution here, it does not reduce it: OP-B2's PFD is a model assumption, the C3 window is not measurable, and the final elements' capability is untested in this demand.

## Recommendation

**Immediate containment:** escalate to the shift supervisor and apply the standing emergency procedure for pressure excursion with the high-pressure interlock unavailable. Consider manual reduction of pressure by the declared route (feed isolation / purge via XV-1001 + VLV-006) **with the C6 side effect planned for**: the same final elements actuate the LIC-8001 level cascade, and closure drives level toward −2.5 % with a low-level trip roughly 1 h later. Confirm the SIS trip at 2900 kPa is in service and not bypassed before relying on it. Verify pressure against an independent field measurement (C5 gap 1) before any decision that depends on the voted value. *Authorised operations personnel decide and execute; this report performs no action.*

**Restoration:** repair UZ-007 under WO-RUN_A-UZ007 and prove the safety function end-to-end, including the final elements that were never commanded; repair PT-007 channel B (WO-RUN_A-CH-B, 94 d in backlog) and restore the 2oo3 arrangement; execute the overdue functional test WO-RUN_A-TEST; execute OP-B2 competence renewal WO-RUN_A-TRAIN. Order by safety function, not by backlog age.

**Definitive solution:** (1) revalidate the design basis windows under the post-2025-11-28 operating condition, or revert the condition — an envelope invalidated on two triggers cannot be closed by a repair; (2) instrument B2's demand trigger (ZT-1001 feed valve position) — a barrier whose demand cannot be observed cannot be credited or audited (risk-analysis reference §6); (3) run the MOC triage that the 2025-11-28 change did not receive; (4) run the C8 threat-removal campaign so the success criterion for this pathway is defined; (5) map the B1→LIC-8001 coupling into the bowtie as a declared secondary consequence; (6) given an overdue test, an unrepaired channel, overdue training and a load change without revalidation all on the same pathway, open a **separate formal investigation** into the maintenance and MOC system — this is evidence of systemic failure, not of a single asset fault.

**Suggested owner / deadline:** immediate containment — shift supervisor / operations manager, now. Restoration — maintenance and instrumentation leads, per the emergency work order. Envelope revalidation, MOC triage and systemic investigation — process safety authority, deadlines set by that authority.

**Expected return / leading indicator:** PIT-7001 rate falling below the design 1.1 kPa/min and reversing before 2900 kPa; FIT-1001 recovering above LO; leading indicators — count of overdue safety-critical WOs on pathway T1 (currently 2 overdue + 2 open), voted-group spread against the 17.5 kPa limit, days since last closed functional test of reator.T1.B1.

**Closure criteria:** pressure back inside band **and** stable over a justified window; B1 function restored and *tested* including final elements; PT-007 back to 2oo3 with the discrepancy cleared; OP-B2 competence current; design basis windows revalidated under the current operating condition; the PT-007 clock contradiction resolved by a decision on which clock governs; C5 gaps either closed or carried as tracked open items. The process variable returning to band does not close this occurrence.

**Residual risk / accepting authority:** not determined here — no tolerability criterion or consequence severity exists in the supplied basis. Acceptance belongs to the facility's designated process safety authority.

**Human decision:** pending

## Evidence and assumptions

- [demonstrated] `process_events` 2025-12-01T02:07:22 `falha_intertravamento` (UZ-007, `saidas_comandadas=false`, `deteccao_ok=true`) — B1 detected and did not command; barrier failed on demand.
- [demonstrated] `work_orders` WO-RUN_A-UZ007, opened 2025-12-01T02:07:22 — corrective, failure found, open at t_now.
- [demonstrated] `a2_estado_atual.demandas.B1.detectar` — 2oo3 vote satisfied by channels A and C; the failure is not in detection.
- [demonstrated] `envelope` / C1 — rate ladder 1.47–4.58 kPa/min, two invalidation triggers observed; design basis §7 windows unverified.
- [demonstrated] `a2_estado_atual.regime` — operating-condition change 2025-11-28, regime shift −148.86 kPa, `revalidacao_registrada=false`.
- [demonstrated] `a2_estado_atual.ordens_servico` — WO-RUN_A-TEST overdue 184 d; WO-RUN_A-TRAIN overdue 124 d; WO-RUN_A-CH-B open 94 d.
- [corroborated] C4 — record (`PT-007.B failed_detected_unrepaired`) and series (channel B flat at 2708.4 kPa, sd 0.2 vs 72.91) agree on the failure mode: frozen channel, not drift.
- [inferred] B2 may not be demanded by its declared route, since no command was issued and the trigger is a command-versus-position discrepancy — depends on the assumption that no command implies no discrepancy signal.
- [inferred] Feed loss behaves as a persistent threat — from observed non-recovery of FIT-1001, not from a classification.
- [undetermined] B1's demand outcome at t_now (`desfecho.criterio_atendido = null`); whether B2 was demanded (C5 gap 2); common cause in the agreeing pair A–C (C5 gap 1); SIS trip availability and any layer below it — `not demonstrated`.
- [assumption] OP-B2 PFD 0.25 (`premissas_do_modelo.human_barrier_pfd_with_overdue_competence`), UZ-007 PFD 1.0 (`...single_channel_item_with_known_failure`), 2oo2 fall without reconfiguration, PT-007 clock rule — model assumptions, not asset data; the PT-007 clock contradiction is recorded and unresolved with barrier effect 1.00×/1.01×.
- [assumption] C3 measured window not determinable at t_now; the 67 min tolerable delay is compared against the C7 projection for meaning only, with no PFD adjustment.