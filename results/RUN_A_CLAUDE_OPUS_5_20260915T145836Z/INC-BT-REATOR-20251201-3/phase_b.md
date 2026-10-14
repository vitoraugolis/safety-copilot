---
incident_id: INC-BT-REATOR-20251201-3
bowtie_id: BT-REATOR
opened_at: 2025-12-01T01:57:10
engine: conventional
status: action_required
urgency: immediate
confidence: medium
---

# Escalate now to operations: PIT-7001 has crossed HI and is climbing at a rate that invalidates the barrier design basis, with B1's demand threshold ~10 min ahead and the SIS trip ~31 min ahead, while the pressure voting group runs 2oo2 and both B1's functional test and B2's competence renewal are overdue.

> **Safety limit (SKILL.md, "Safety limits").** This is an approach to a trip with a degraded detection group and an invalidated validity envelope. Recommend immediate escalation to operations and application of the standing emergency procedures, without waiting for further certainty. This report does not authorise any manoeuvre.

## Fact

- Trigger: `identidade.gatilho[0]` — `alarme:PIT-7001:HI`, threshold 2750.0 kPa, value 2751.015 kPa at `identidade.ts` = 2025-12-01T01:57:10. Alarm active for `a2_estado_atual.alarmes_ativos[2].ativo_ha_min` (first instant of the crossing).
- Rate at the trigger: `a2_estado_atual.margem.PIT-7001.taxa_por_min` (linear regression, 61 samples, 300 s window). Rate ladder: `envelope.degraus` — 1.13 kPa/min over the day, 2.88 from the 00:44:25 valley, 4.9 over the last 10 min; dispersion 4.34× (`envelope.dispersao`).
- Margins (`a2_estado_atual.margem.PIT-7001`): HI already crossed (+1.02); next threshold HIHI 2800 at `tempo_ate_limiar_min`; declared targets SIS trip 2900 and physical limit 3000 with `alvos_declarados[*].tempo_min`. All times are computed from the measured rate, not read.
- Also active, unchanged in kind: FIT-1001 LO and LOLO since 2025-12-01T00:00:05, feed at `a2_estado_atual.margem.FIT-1001.valor` with rate `...taxa_por_min` — no recovery.
- Operating mode: standard campaign at 15 % load with feed setpoints scaled 1.15, changed 2025-11-28T00:00:00 (`a2_estado_atual.regime.mudanca`), i.e. **not** the design base case of design basis §2.
- Data quality: the voted value is carried by channels A and C, which agree within `a2_estado_atual.grupo_votado.concordancia_no_ultimo_instante.tolerancia_kpa`; channel B is flat and divergent (`...congelamento`). The crossing is reproducible on two independent channels; the trigger is not an artefact of the failed channel. No freezing, saturation or manual override is recorded on A or C (σ 62.03 kPa over the month, `grupo_votado.estatistica_por_canal`).
- **What this trigger changed.** Earlier today pressure was below LO (last LO normalised 01:07:00, `a2_estado_atual.alarmes_normalizados[3]`). This trigger is the first crossing of HI in this episode — the formal start of the response window (design basis §3) — and it arrives with the approach-window rates already above the invalidation threshold (`envelope.gatilhos_de_invalidacao[0]`). No demand on B1 is recorded up to `t_now` (`a2_estado_atual.demandas.B1`).

**Gate:** crossing reproducible, data quality sufficient to infer.

## Scenario and mechanism

Qualitative chain (pathway T1, `diagrams/BT-REATOR.txt`):

`T1 loss of stream 1 feed → B1 automatic high-pressure interlock → B2 manual operator action → top event "loss of reactor control" → (mitigation not in scope of this pathway) → consequence not declared in the inputs`

Quantitative chain, link by link:

| Link | Evidence | Strength |
|---|---|---|
| FIT-1001 at LOLO since 00:00:05, rate ≈ 0 — the threat is present and not clearing | `a2_estado_atual.margem.FIT-1001`, `a3_cruzamentos[C8].comparado` | demonstrated |
| Pressure escalation follows, 2.88–4.9 kPa/min against a design rate of 1.1 | `envelope.degraus`, `envelope.referencia_de_projeto` | demonstrated |
| Envelope invalidated: rate trigger and MOC-without-revalidation trigger both observed | `envelope.gatilhos_de_invalidacao[0..1]`, `regime.revalidacao_registrada` | demonstrated |
| PT-007 2oo3 running 2oo2, channel B failed-detected-unrepaired for 94 d; item PFD ×34.36 | `a3_cruzamentos[C4]`, `a1_base_de_projeto.barreiras[0].detalhe_componentes[0]` | demonstrated |
| B1 barrier PFD ×1.11 only, because XV-1001 dominates (48 %) | `a1_base_de_projeto.barreiras[0].c2` | demonstrated |
| B2 PFD ×2.27, dominated by OP-B2 (92 %), whose 0.25 is a **model assumption** | `a1_base_de_projeto.barreiras[1].c2`, `premissas_do_modelo.human_barrier_pfd_with_overdue_competence` | inferred |
| Top event frequency ×2.07, pathway T1 share 70.1 → 85.6 % | `motores.conventional` | demonstrated |
| Consequence and tolerability | not present in any input | undetermined |

Temporal correlation between the 2025-11-28 condition change and today's episode is recorded, not demonstrated as cause: the regime shift (`regime.deslocamento_kpa`) and three subsequent LO alarms are consistent with an unrevalidated operating point, but no causal link to the feed loss is in the data.

## Analysis

### 1. Bowtie

**B1 — automatic high-pressure interlock: `degraded`.** Not demanded up to `t_now` (`a2_estado_atual.demandas.B1`), so no observation settles its state; the judgement rests on PFD and on the maintenance record. Barrier multiplier `a1_base_de_projeto.barreiras[0].c2.multiplicador_barreira` — modest, because the dominant element XV-1001 (48 % of the total) is unchanged at design PFD. The component multiplier is `...c2.componente_pior.multiplicador` on PT-007, two orders of magnitude of headroom below the dominant element, which is why a 34× component degradation moves the barrier by 1.11× (C2, both multipliers reported). Degradation is nonetheless real and cumulative: the functional test of the interlock is overdue by 184 d (`WO-RUN_A-TEST`), so the declared PFD is not test-demonstrated — the number survives, its verification does not. Detection remains functional for a *high* trip: A and C agree and both sit above the voted value, so a 2-out-of-3 vote at HIHI is still achievable with B stuck low (`grupo_votado`); this is the reason B1 is `degraded` and not `critical`.

**Voted group PT-007 (C4): known degraded, not hidden.** Failure detected 2025-08-29T00:30:00 with `WO-RUN_A-CH-B` open; the applicable clock is repair backlog, 94 d since detection (`a3_cruzamentos[C4].relogio`). Failure mode supported by the data: **frozen channel**, not drift — B's standard deviation is 0.2 kPa against 62.03 on A and C, and it is stuck at 2708.4 kPa, within 0.03 kPa of the pre-change regime median (`grupo_votado.congelamento`). The measured spread 43.18 kPa against a 17.5 kPa limit (`a2_estado_atual.discrepancia_canais[0]`) exceeds the limit and agrees with the maintenance record — reading and record do not contradict each other here. There is no arbiter left: a second channel failure removes the vote entirely.

**B2 — manual operator action: `degraded`, with its effectiveness not demonstrable in the current condition.** PFD `a1_base_de_projeto.barreiras[1].pfd_atual` against design `...pfd_projeto` (×2.27), dominated by OP-B2 at 92 % with competence renewal overdue 124 d (`WO-RUN_A-TRAIN`). Two qualifications outrank that number:

- **C3, window compression.** Phase A declares the real window not measurable at `t_now` because B1 has not been demanded (`a3_cruzamentos[C3].nao_se_aplica`), so no compression factor is established. What the C7 projections do show is that the interval between the HIHI demand and the SIS trip, at the current rate, is the difference between `margem.PIT-7001.alvos_declarados[0].tempo_min` and `margem.PIT-7001.tempo_ate_limiar_min` — roughly 21 min (inferred from phase A projections, not measured), against a design HIHI→SIS window of 162 min and a maximum tolerable delay for B2 of 67 min (`envelope.janelas_de_projeto`). If the current rate holds, B2's tolerable delay exceeds the whole available window. Per C3 this is a **gap**, not an adjusted PFD: no approved method exists to re-derive a human PFD under a compressed window, and B2's entire margin is declared to be perception and decision, not execution (design basis §5).
- **C6, independence.** B1 and B2 have independent detection (PT-007 vs ZT-1001) but a shared final element (XV-1001, VLV-006) — `a3_cruzamentos[C6].comparado.declared_independence`. Joint credit must not be taken as the product of the two PFDs; a failure of XV-1001, the element that dominates B1's PFD, removes both barriers at once. B2 is a backup whose demand trigger is the command-versus-position discrepancy on ZT-1001 — i.e. it exists only after B1 has tried and failed (design basis §4).

No IPL/SIL credit is claimed here: none is declared in the inputs, and appearance in the bowtie does not grant it.

**Dominant path.** `motores.conventional.atual.pathways[0].contribuicao_pct` — the T1 pressure pathway now carries the great majority of the top event frequency, against `motores.conventional.projeto.pathways[0].contribuicao_pct` at design. The fuzzy engine reproduces the same split shift (`motores.fuzzy`), with label `Moderate → Moderate`: a label that has not moved is not evidence that nothing has moved, since the conventional magnitude doubled inside the same linguistic term.

**Declared side effect of B1's action (C6).** Actuation closes the A+C feed valve, which is the actuator of the LIC-8001 level cascade; inventory control is lost, level goes to about −2.5 % and a low-level trip follows roughly 1 h later (`a3_cruzamentos[C6].comparado.declared_side_effect`). B1 succeeding against the T1 top event therefore produces a shutdown by an unmapped route. LIT-8001 is currently at `margem.LIT-8001.valor` and rising slowly; this coupling must be anticipated by operations, not discovered.

### 2. Process

The trajectory, not the last value: the day opens below LO, reaches a valley of 2543 kPa at 00:44:25, then climbs monotonically through HI. The rate ladder (`envelope.degraus`) is the finding — 1.13 kPa/min over the whole day would read as "within design", while the decision window reads 2.88 and the last ten minutes 4.9, i.e. 2.6× and 4.5× the design rate of 1.1 (design basis §2). Two of three windows exceed the 2.2 kPa/min invalidation limit of design basis §7. The design plateau between 2850 and 2870 kPa, where most of the barriers' declared margin sits, has not been reached and cannot be assumed: it is a property of the base case, and the plant is not in the base case.

Distance and rate side by side (C7, `a3_cruzamentos[C7].comparado.PIT-7001`): 48.98 kPa to HIHI, 148.98 kPa to the SIS trip, 248.98 kPa to the physical limit, with the corresponding computed times. The margin in kPa looks comfortable; the margin in minutes does not.

Other tags are quiet and coherent with a feed-loss scenario rather than a heat-removal scenario: TIT-9001 stable at 120.43 °C with a slightly negative rate, TIT-2101 at 94.35 °C falling, LIT-8001 rising at 0.0123 %/min (`a2_estado_atual.taxas`). No temperature pathway signal supports the T2 branch. Basic process control is active — FCV-0601 and the XV-1001 valves show non-zero rates in `a2_estado_atual.taxas` — but BPCS action is not a barrier and is not credited here; no barrier actuation event is recorded.

**C8.** The threat classification is a declared gap: the removal test of design basis §6 was never run (`a3_cruzamentos[C8].lacuna`). The observed behaviour — feed at ~0 kscmh with a rate indistinguishable from zero and no recovery over 117 min — is *consistent with* a persistent threat. That is evidence, not a classification. If it is persistent, no barrier produces a stable state: B1 and B2 buy time until the feed is restored, and "the barrier worked" means "we reached the repair alive", not "pressure returned to normal".

### 3. Context

- **Design basis and its validity.** `references/design-basis-barriers.md` declares its scope as the base case only, and declares the invalidation criteria of §7. Two of the three evaluated triggers are observed (`envelope.gatilhos_de_invalidacao`). The consequence is explicit in §7: the real actuation window **is not known** and must be derived from current data. Accordingly, the 202 min / 162 min / 67 min figures of §5 must not be used to argue that there is time.
- **Management of change.** The operating-condition change of 2025-11-28T00:00:00 (load 15 %, feed setpoint scale 1.15) shifted the voted pressure regime by `regime.deslocamento_kpa` and is recorded with `regime.revalidacao_registrada` = false — no work order and no window revalidation event after that date. Three LO alarms followed in the three days between the change and this episode (`regime.alarmes_entre_a_mudanca_e_o_episodio`). This belongs to MOC triage and to C1 simultaneously (risk-analysis reference §4). Absence of a revalidation record is a gap; it is not by itself proof of a procedural non-conformance.
- **Mechanical integrity / backlog.** Three open items on this pathway: `WO-RUN_A-CH-B` (channel repair, open 94 d), `WO-RUN_A-TEST` (interlock functional test, 184 d overdue), `WO-RUN_A-TRAIN` (OP-B2 competence, 124 d overdue). One closed with a finding, `WO-RUN_A-CH-A` (April, channel A relay replaced, retest OK) — a second channel failure on the same transmitter within the same year is a repeat-defect signal on PT-007.
- **Human factors.** Do not read OP-B2's contribution as operator blame. The organisational facts are an overdue competence renewal left open for 124 d and a design in which the operator's whole margin is perception and decision (design basis §5), under a window that the current dynamics compress. Task, information and time — not the individual — are the degraded terms.
- **Recorded contradiction, not resolved.** PT-007's creep clock (334 d since last test) disagrees with the maintenance calendar (test overdue by 184 d), `a2_estado_atual.contradicoes[0]`. The sensitivity is immaterial at barrier level (`...sensibilidade.por_barreira`, 1.07× on B1 and 1.01× on B2) and does not change this decision; which clock governs is a decision for the team.
- **Model assumptions carried into the numbers** (`premissas_do_modelo`): OP-B2 at 0.25 is assumed, not an asset datum; the fall of the voted group to 2oo2 without reconfiguration is assumed; items without test records are held at design PFD.

**Named gap (C5).** "Is there a common cause affecting channels A and C?" — the majority already identifies B as the divergent channel, so *which channel is correct* is not the open question; what cannot be ruled out is a shared error in the agreeing pair, and with B failed there is no arbiter. External check: an independent field measurement of vessel pressure (`a3_cruzamentos[C5].lacunas[0].verificacao_externa`). This is the single check that most changes the reading of the present episode.

## Risk judgement

- **Top event frequency.** Conventional engine: `motores.conventional.projeto.evento_topo_por_ano` → `motores.conventional.atual.evento_topo_por_ano`, ratio `motores.conventional.razao`. Fuzzy engine: `motores.fuzzy.projeto.evento_topo_por_ano` → `motores.fuzzy.atual.evento_topo_por_ano`, ratio `motores.fuzzy.razao`, label `Moderate → Moderate`. Cite the conventional engine for magnitude and the fuzzy engine only for the propagation of linguistic uncertainty; neither checks the other.
- **Consequence, receptors, tolerability.** Not declared in any supplied input. Therefore the correct conclusion is: **barrier erosion demonstrated; risk tolerability not determined.** That is a result, not a failure of the analysis. Do not convert the `Moderate` label into an acceptance statement.
- **Uncertainty.** Medium confidence overall, limited by the weakest decisive links: OP-B2's PFD is a model assumption; B2's available window is a projection from the current rate, not a measurement; the C5 common-cause gap on the A/C pair is open; the threat classification is unrun. The rate itself is well supported (three windows, 1407/874/121 samples).
- **Urgency: immediate.** Not from the frequency figure but from C7 and C4: time to the B1 demand threshold and to the SIS trip is measured in tens of minutes at the current rate (`margem.PIT-7001`), the last automated layer is the SIS trip with nothing declared between it and the physical limit, the detection group has no arbiter, and the envelope that would have justified "there is time" is invalidated. High-consequence/low-frequency is not discounted by the absence of a declared consequence.

## Recommendation

**Immediate containment:** escalate to the shift supervisor and operations now, under the standing procedures for approach to a trip, and treat the design basis windows as unverified (design basis §7). Brief the operating crew, before HIHI is reached, that if B1 acts it will close the A+C feed valve and destroy LIC-8001 level control, with a low-level trip expected roughly 1 h later (C6) — the response to the secondary event should be prepared in advance, not improvised. Obtain an independent field measurement of vessel pressure to close the C5 gap on the A/C pair. No bypass, no threshold change, no barrier disablement: authorised persons decide and execute.

**Restoration:** execute `WO-RUN_A-CH-B` (restore PT-007 to 2oo3 and re-establish an arbiter); execute `WO-RUN_A-TEST` (interlock functional test, 184 d overdue) with post-test evidence covering the relevant failure mode; execute `WO-RUN_A-TRAIN` (OP-B2 competence, 124 d overdue). Repairs on the voted group must be scheduled with their effect on B1's availability explicit, not silently.

**Definitive solution:** per the response hierarchy, act on the threat before adding administrative layers — establish why stream 1 feed is lost and whether it is removable, and run the threat-removal campaign that would close the C8 classification. Revalidate the design basis windows (HI→SIS, HIHI→SIS, B2 tolerable delay) under the current operating condition of 15 % load / 1.15 feed-setpoint scale, and put the 2025-11-28 change through MOC triage including revalidation of alarm thresholds against the new regime (three LO alarms in three days suggests the thresholds no longer fit the operating point). Address the shared final element XV-1001/VLV-006 in the bowtie so that joint credit for B1 and B2 reflects the declared dependency. An administrative control does not compensate for the compressed human window.

**Suggested owner / deadline:** operations shift supervisor (immediate containment, now); maintenance/I&C planning (restoration work orders, priority against backlog); process safety with the plant's technical authority (revalidation, MOC triage and threat-removal test, planned).

**Expected return / leading indicator:** PIT-7001 rate ladder back below 2.2 kPa/min across all declared windows; PIT-7001 below HI; PT-007 spread below the 17.5 kPa limit with three channels live; zero overdue preventive work orders on `reator.T1.B1`/`B2`.

**Closure criteria:** condition controlled; PT-007 restored to 2oo3 and functionally tested; interlock functional test executed with result recorded; OP-B2 competence renewed; the 2025-11-28 change formally revalidated with new declared windows and invalidation criteria; residual risk reassessed and accepted; all open items traceable. Pressure returning to band does **not** close this occurrence.

**Residual risk / accepting authority:** not determined here — no tolerability criterion or consequence definition exists in the supplied basis; acceptance belongs to the facility's competent authority.

**Further analysis:** the pattern — a repeat channel failure on the same transmitter within one year, three preventive/corrective items overdue between 94 and 184 d on a single protective pathway, and an operating-condition change without revalidation — is evidence of systemic maintenance and MOC weakness rather than an isolated defect. Recommend a separate formal investigation of that pattern, independent of this occurrence.

**Human decision:** pending

## Evidence and assumptions

- [demonstrated] `identidade.gatilho[0]`, 2025-12-01T01:57:10 — PIT-7001 crossed HI 2750 kPa; crossing carried by two agreeing channels.
- [demonstrated] `envelope.degraus` / `envelope.gatilhos_de_invalidacao` — measured rate 2.6× and 4.5× design in the decision windows; envelope invalidated on two of three triggers (design basis §7).
- [demonstrated] `a2_estado_atual.margem.PIT-7001` — distance and computed time to HIHI, SIS trip and physical limit at the current rate (C7).
- [demonstrated] `a3_cruzamentos[C4]` + `a2_estado_atual.grupo_votado.congelamento` — PT-007 known degraded, running 2oo2; channel B frozen at 2708.4 kPa (σ 0.2 vs 62.03) since ≈2025-08-29; repair clock 94 d.
- [demonstrated] `a1_base_de_projeto.barreiras[*].c2` — B1 barrier ×1.11 with component ×34.36 (dominant XV-1001, 48 %); B2 barrier ×2.27 with dominant OP-B2 (92 %).
- [demonstrated] `a3_cruzamentos[C6]` + design basis §4 — detection independent, final element shared; declared side effect of B1's action on the LIC-8001 level cascade.
- [demonstrated] `a2_estado_atual.ordens_servico` — `WO-RUN_A-TEST` overdue 184 d, `WO-RUN_A-TRAIN` overdue 124 d, `WO-RUN_A-CH-B` open, `WO-RUN_A-CH-A` closed with a finding.
- [demonstrated] `a2_estado_atual.regime` — condition change 2025-11-28 with regime shift −148.86 kPa and no revalidation recorded.
- [demonstrated] `motores.conventional` / `motores.fuzzy` — top event frequency design vs current, both engines, with ratios and pathway split.
- [demonstrated] `a2_estado_atual.demandas.B1` — no demand on B1 up to `t_now`; nothing in this episode may be read as B1 having acted.
- [corroborated] `a3_cruzamentos[C4].reading_spread` vs `a2_estado_atual.canais` — process reading and maintenance record agree that channel B is the failed one.
- [inferred] B2's available window under the current rate — derived from the C7 projections (`margem.PIT-7001`), not measured; C3 declares the real window not measurable at `t_now` because B1 has not been demanded. Assumption: the current rate persists through HIHI.
- [inferred] OP-B2 PFD 0.25 — `premissas_do_modelo.human_barrier_pfd_with_overdue_competence`; a model assumption, not asset data. B2's ×2.27 depends on it.
- [inferred] 2oo3 → 2oo2 without reconfiguration — `premissas_do_modelo.voted_group_without_reconfiguration`.
- [undetermined] Common cause on the agreeing pair A/C — `a3_cruzamentos[C5].lacunas[0]`; resolvable only by an independent field pressure measurement.
- [undetermined] T1 persistent vs removable — `a3_cruzamentos[C8]`; removal test never executed (design basis §6). Observed behaviour is consistent with persistence.
- [undetermined] PT-007 test clock: model clock vs maintenance calendar — `a2_estado_atual.contradicoes[0]`; both readings presented, immaterial at barrier level (1.07× / 1.01×), not resolved.
- [undetermined] Consequence, receptors and tolerability criterion — absent from all supplied inputs; risk tolerability not determined.