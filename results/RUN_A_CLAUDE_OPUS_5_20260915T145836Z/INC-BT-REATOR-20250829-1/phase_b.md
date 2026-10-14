---
incident_id: INC-BT-REATOR-20250829-1
bowtie_id: BT-REATOR
opened_at: 2025-08-29T00:30:00
engine: conventional
status: action_required
urgency: planned
confidence: medium
---

# Repair PT-007 channel B and execute the 90-day-overdue interlock functional test as priority maintenance: pathway T1 barriers have eroded to twice the design top-event frequency with the process still at its design base case and no demand yet made.

## Fact

Record-side trigger only, no process deviation. Two records at `t_now` opened this analysis: `identidade.gatilho[0]` (`wo_opened:WO-RUN_A-CH-B`) and `identidade.gatilho[1]` (`channel_failure_detected:PT-007.B`). Channel B of the voted group PT-007 failed at 2025-08-29T00:00:00, was detected at 00:30:00 and is unrepaired (`a2_estado_atual.canais[1]`); the corrective order is open with 0 d elapsed since detection (`a3_cruzamentos[C4].relogio`).

Process condition at `t_now` sits on the design base case: PIT-7001 2708.1107 kPa against a declared steady value of 2708 kPa, LIT-8001 74.7278 %, TIT-9001 120.4156 °C, FIT-1001 0.253 kscmh (`a2_estado_atual.margem`, design basis §2 via `a1_base_de_projeto.declarado.condicao_de_projeto`). No active alarms (`a2_estado_atual.alarmes_ativos`), no threshold crossed, no demand on B1 up to `t_now` (`a2_estado_atual.demandas.B1`), no operating-condition change (`a2_estado_atual.regime`).

Data quality: the three PT-007 channels agree within 0.54 kPa against a 17.5 kPa limit, with no channel outside the 5.79 kPa majority tolerance and no divergent channel by majority (`a2_estado_atual.discrepancia_canais[0]`, `a2_estado_atual.grupo_votado.concordancia_no_ultimo_instante`); per-channel standard deviations 1.96/1.97/1.98 kPa are consistent with the declared design noise of 1.93 kPa and no channel is frozen (`a2_estado_atual.grupo_votado`). **Limit on the fact:** the rate ladder is empty with the declared gap `serie insuficiente na janela` (`envelope.lacuna`), so every PIT-7001 statement here is a distance, not a trend; `taxa_por_min` and `tempo_ate_limiar_min` are null for all five tags and no time-to-target is asserted.

**What this trigger changed** — first analysis in this stream. The change is that the PT-007 voted group moved from redundant to **known degraded**, running 2oo2 without reconfiguration (`a3_cruzamentos[C4].resultado`, `premissas_do_modelo.voted_group_without_reconfiguration`), which is what lifts the PT-007 item multiplier to 24.69× and, combined with the already-overdue OP-B2 competence, doubles the top-event frequency.

## Scenario and mechanism

Qualitative chain: **T1 — loss of stream 1 feed** → **B1 high-pressure interlock** (voted PT-007 ≥ HIHI closes feeds, opens purge) → **B2 manual operator action** (demanded only on ZT-1001 command-versus-position discrepancy, i.e. after B1 has tried and failed) → **top event: loss of reactor control** → mitigation and consequence/receptor **not declared in the supplied basis**.

Quantitative chain, with the source of each link:

| Link | Evidence | Strength |
|---|---|---|
| PT-007.B failed, detected, unrepaired → group runs 2oo2 without reconfiguration | `a2_estado_atual.canais[1]`; `premissas_do_modelo.voted_group_without_reconfiguration` (the fall to 2oo2 is an assumption declared in the model, not an asset record) | inferred |
| 2oo2 + 240 d since last test → PT-007 item PFD 24.69× design | `a1_base_de_projeto.barreiras[0].detalhe_componentes[PT-007]`, `.motivos` | demonstrated (from the declared model) |
| PT-007 24.69× → B1 barrier only 1.08×, because XV-1001 holds 49.6 % of B1's PFD | `a1_base_de_projeto.barreiras[0].c2` (C2: both multipliers) | demonstrated |
| OP-B2 competence overdue → PFD 0.25 → B2 barrier 2.27× | `a1_base_de_projeto.barreiras[1].c2`; `premissas_do_modelo.human_barrier_pfd_with_overdue_competence` — an assumed value, **not** asset data | inferred |
| Barrier PFDs → top event 2.02× design | `motores.conventional.razao`, `motores.pfd_atual` | demonstrated (engine output) |
| Top event → consequence and receptor | not present in the supplied basis | undetermined |

Temporal note: nothing in the process series participates in this chain. The erosion is entirely in the reliability and maintenance layers, which is precisely the mechanism a process-value detector cannot see (SKILL.md, *Analyses over time*).

## Analysis

### 1. Bowtie

**B1 — high-pressure interlock: `degraded`.** Not `critical`: there is no bypass, no isolation, and no demand up to `t_now` (`a2_estado_atual.demandas.B1`), so no observation outranks the PFD. Not `healthy`: the detection element is running with one failed channel and its functional test `WO-RUN_A-TEST` is 90 d overdue and not executed (`a2_estado_atual.ordens_servico[1]`), so the *detect–decide–act* chain has no current proof of function. C2 must be read in both directions: the component multiplier is 24.69× (PT-007) while the barrier multiplier is 1.08× (`a1_base_de_projeto.barreiras[0].c2`) — reporting only the first would produce over-reaction, only the second would hide that the group lost its arbiter. The dominant element is **XV-1001 at 49.6 % of B1's PFD**, and it is unchanged at its design value (`detalhe_componentes[XV-1001].fator` = 1.0); B1's floor is therefore set by a final element whose condition is asserted by absence of record, not by test (`premissas_do_modelo.items_without_test_records`).

**B2 — manual operator action: `degraded`.** Barrier multiplier 2.27×, dominated by OP-B2 at 92.1 % of the total (`a1_base_de_projeto.barreiras[1].c2`). The 0.25 PFD is a model assumption applied because `WO-RUN_A-TRAIN` is overdue and open; it is not an asset figure and must not be presented as measured. The design basis states that **all of B2's margin is perception and decision, none is execution** (§5), so a competence lapse attacks exactly the part of B2 that carries the margin. C3 is `não se aplica` here — no demand occurred, so no real window is measurable (`a3_cruzamentos[C3]`) and the 67 min tolerable delay stays a design-case figure, untested in the current condition.

**Independence — the decisive finding.** The design basis §4 declares detection independent (PT-007 versus ZT-1001) and the final element shared (XV-1001, VLV-006), with the explicit consequence that *joint credit must not multiply the two PFDs* (`a3_cruzamentos[C6].comparado.declared_independence`). Two consequences follow:

- The conventional engine folds pathway T1 as a product of B1 and B2 PFDs (`motores.conventional`), i.e. on an independence the design basis denies. The current 3.536e-3/yr is therefore **not conservative** with respect to common-cause failure of XV-1001/VLV-006; the ratio 2.02× is the more robust number, since the same optimism sits on both sides of it.
- The asset composition in phase A lists **PT-007 inside B2's components** (`a1_base_de_projeto.barreiras[1].componentes`, and `a3_cruzamentos[C6].comparado.shared_items.PT-007 = [B1, B2]`), which contradicts the design basis's claim of independent detection. Recorded, not resolved: if the asset list is right, one degraded transmitter group erodes both barriers of the pathway simultaneously and B2 cannot be credited as compensation for B1 at all. This is a data-versus-document contradiction that has to be settled by the team, not by this report.

**C6 side effect.** B1's action closes the A+C feed valve, which is the actuator of the LIC-8001 level cascade: inventory control is lost, level goes to about −2.5 % and a low-level trip follows roughly 1 h later (`a3_cruzamentos[C6].resultado`). This is a declared secondary consequence, not a failure of B1 against the T1 top event (design basis §5), but it forbids any "prove it works" demand forced on line.

**C8.** T1's persistent-versus-removable classification is not available: the removal test was not executed (`a3_cruzamentos[C8].lacuna`, design basis §6). With the plant at base case and no excursion, no behavioural evidence is available either. The success criterion to apply to B1/B2 in a real event therefore remains undetermined.

No IPL/SIL credit is asserted here: neither an approved LOPA decision nor a tolerability criterion is present in the supplied inputs.

### 2. Process

All five flagged tags sit inside their bands with the nearest threshold ahead: PIT-7001 41.89 kPa below HI 2750, 191.89 kPa below the SIS trip and 291.89 kPa below the model physical limit; TIT-9001 14.58 °C below HI; LIT-8001 10.27 % below HI; TIT-2101 5.45 °C below HI (`a3_cruzamentos[C7].comparado`). C7 requires distance and rate side by side, and **the rate half is missing**: every `taxa_por_min` is null and the ladder carries the gap `serie insuficiente na janela` (`a2_estado_atual.escada_de_taxas`). The correct reading is therefore "no crossing observed and no trend demonstrated", not "stable". C1 returns `no escalation window at t_now` with no design-rate comparison performed, so the 2.2 kPa/min invalidation trigger (design basis §7) is neither observed nor excluded — the envelope is untested at this instant, and the §5 windows (202 min HI→SIS, 162 min HIHI→SIS, 67 min tolerable B2 delay) remain design-case values only.

Precursor signals present are all in the reliability layer: one prior channel discrepancy on PT-007.A closed with a finding in April 2025 (`a2_estado_atual.ordens_servico[0]`), now a second discrepancy on channel B — two channel failures in the same transmitter group inside five months. That repetition is the leading signal, and it is in the maintenance record, not in the series.

### 3. Context

**Mechanical integrity.** Three maintenance findings bear on the decision: `WO-RUN_A-TEST` (functional test of `reator.T1.B1`) overdue 90 d and not executed; `WO-RUN_A-TRAIN` (OP-B2 competence) overdue 30 d and open; `WO-RUN_A-CH-B` open in repair backlog. Note the sequence: the functional test fell due 2025-05-31 and the channel B failure occurred 2025-08-29 — the test's due date precedes the failure, so the overdue test did not miss this failure (it was caught by discrepancy monitoring); what it does mean is that B1's logic and final-element function are unproven since before the failure.

**Recorded contradiction on the PT-007 clock.** The PFD creep clock says 240 d since the last test against a 365 d interval; the maintenance calendar implies the test was due at 365 d from an assumed last test of 2024-05-31 and is 90 d overdue (`a2_estado_atual.contradicoes[0]`). Phase A quantified the sensitivity rather than resolving it: item PFD 1.9× between the two clocks, but only **1.07× on B1 and 1.01× on B2** (`contradicoes[0].sensibilidade.por_barreira`). The contradiction is real and must be settled by the team for the reliability model to be auditable, but it does not change this report's conclusion under either clock.

**Second, smaller disagreement (this analysis, flagged not resolved):** B2's degradation reason states "test overdue by 58 d (interval 182 d)" for OP-B2 (`a1_base_de_projeto.barreiras[1].motivos[1]`), while `WO-RUN_A-TRAIN` is recorded 30 d overdue (`ordens_servico[2].vencida_ha_dias`). Two fields of the same database disagree on how long the competence has been lapsed. It does not change B2's state — the assumed PFD of 0.25 is applied from the due date regardless — but it should be reconciled.

**Human and organisational.** No operator blame is available or appropriate: the finding is an organisational one — a periodic competence renewal past due with the work order auto-opened and not executed, on a barrier whose entire margin is human perception and decision (design basis §5).

**Management of change.** No operating-condition change up to `t_now` (`a2_estado_atual.regime`); no threshold or voting-arrangement change is recorded. The fall from 2oo3 to 2oo2 is a *de facto* degradation, not a declared MOC, and it should not be formalised into a 1oo1 or a reconfigured vote without one.

**Gaps.** Phase A named zero C5 gaps (`a3_cruzamentos[C5]`). The limits on this conclusion therefore come from the declared `lacunas` elsewhere: the missing rate ladder (C1/C7), the unmeasurable real window (C3), the unexecuted threat-removal test (C8), and the absence of a consequence description, receptor and tolerability criterion in the supplied inputs.

## Risk judgement

Top event frequency, design against current, both engines, from `motores`:

- **conventional** (magnitude): `motores.conventional.projeto.evento_topo_por_ano` → `motores.conventional.atual.evento_topo_por_ano`, ratio `motores.conventional.razao` = 2.02×. Pathway T1's contribution moves from 70.1 % to **85.2 %** of the total (`motores.conventional.*.pathways`) — the eroded pathway now dominates the diagram.
- **fuzzy** (propagation of linguistic uncertainty): `motores.fuzzy.razao` = 1.9×, label **Moderate → Moderate** (`motores.fuzzy.atual.rotulo`), T1 share 89.1 %. The unchanged label is not evidence of an unchanged condition: a fuzzy label qualifies a frequency, is not an acceptance criterion, and quantises to roughly a decade per AND node (SKILL.md, *The fuzzy engine*). The two engines are not cross-checks on each other and their absolute values are not comparable.

Both figures rest on an independence the design basis explicitly denies (C6), so the current frequency is a lower bound with respect to common-cause failure of the shared final element.

**Consequence, receptors and tolerability are not declared in the supplied inputs.** The correct conclusion is therefore: **barrier erosion demonstrated; risk tolerability not determined.** That is a result, not a shortfall of the analysis.

**Uncertainty.** Medium confidence overall, capped by the weakest decisive links: the OP-B2 PFD of 0.25 is a model assumption; the 2oo2 fall is an assumption; the PT-007 clock is contradicted; B2's detection composition contradicts the design basis; and no rate is available to qualify the process side.

**Urgency: planned, not immediate.** No process excursion, no threshold crossed, no active alarm, no demand on B1, and the nearest declared target on PIT-7001 is 41.89 kPa away (`a2_estado_atual.margem.PIT-7001`). The relevant clock is C4's repair backlog, which has just started (0 d), not a process clock — but that clock must not be allowed to run: with the functional test already 90 d overdue, a third channel failure would take the group below vote, and C1/C3 have no measured window to say how much time a real T1 demand would leave.

## Recommendation

**Immediate containment:** no process manoeuvre is indicated and none is recommended — the plant is at its declared base case. Notify operations that PT-007 is running 2oo2 with one detected unrepaired channel and that `reator.T1.B1` has no valid functional-test evidence. Do **not** bypass, isolate or reconfigure the vote to 1oo1, and do not force a demand on B1 to "prove" it: B1's actuation destroys inventory control via the LIC-8001 cascade and brings a low-level trip roughly 1 h later (C6). Treat B2 as **not** a compensating measure for B1 while PT-007 is degraded — shared final element, and the asset list places PT-007 in B2 as well.

**Restoration:** (1) repair PT-007.B under `WO-RUN_A-CH-B` and retest to restore 2oo3; (2) execute `WO-RUN_A-TEST`, the 90-d-overdue functional test of `reator.T1.B1`, covering detect–decide–act end to end including XV-1001 and VLV-006, not the transmitter alone; (3) execute `WO-RUN_A-TRAIN` to restore OP-B2 competence and remove the assumed 0.25 PFD from the model.

**Definitive solution:** address the engineering layer before the administrative one (SKILL.md B5 hierarchy). (a) XV-1001 dominates B1's PFD at 49.6 % and is carried at design value purely because no test record exists — establish proof testing (e.g. partial stroke) so that B1's floor is demonstrated rather than assumed. (b) Resolve the PT-007 clock rule so that model and calendar cannot disagree (`a2_estado_atual.contradicoes[0]`). (c) Reconcile B2's component list with design basis §4: if PT-007 genuinely feeds B2, the pathway has shared detection and the bowtie's joint credit must be revised. (d) Run the threat-removal test for T1 (design basis §6) so C8 has a classification and B1/B2 have a defensible success criterion. (e) Revalidate the §5 windows under the current condition, and instrument/verify that the ZT-1001 discrepancy trigger for B2 is observable in the dataset — a demand that cannot be observed cannot be credited or audited.

**Suggested owner / deadline:** maintenance and reliability for (1)–(3), the corrective repair as priority backlog and the two overdue orders inside the current week; process safety / bowtie owner for (b)–(e); instrumentation engineering for (a). Deadlines are for the facility's authority to set.

**Expected return / leading indicator:** on completion of (1)–(3), B1 and B2 return toward their design multipliers and the conventional ratio toward 1.0× — re-run phase A after each closure and compare against `motores.conventional.razao`. Leading indicators: days of open corrective backlog on PT-007; count of channel discrepancies per rolling 12 months on PT-007 (two since April 2025); percentage of safety-related preventive orders overdue.

**Risks introduced by the action itself:** repair work on a 2oo2 group can take the vote below quorum — require a documented degraded-operation provision before the intervention; any reconfiguration of the vote requires MOC.

**Further analysis required:** the repetition of PT-007 channel failures within five months, combined with two overdue safety-related preventive orders on the same pathway, is a candidate for systemic failure. Recommend a separate formal review of the safety-critical maintenance backlog; this report does not perform root cause.

**Closure criteria:** PT-007.B repaired and the group retested to 2oo3; `WO-RUN_A-TEST` executed and passed with results recorded; `WO-RUN_A-TRAIN` completed; the PT-007 clock contradiction and the B2 composition contradiction resolved in the source data; design basis windows revalidated under the current condition; top-event frequency recomputed and reviewed. Absence of a process excursion does not close this occurrence.

**Residual risk / accepting authority:** tolerability not determined — no approved criterion is present in the supplied inputs. Residual risk acceptance belongs to the facility's designated authority.

**Human decision:** pending

## Evidence and assumptions

- [demonstrated] `a2_estado_atual.canais[1]` / `identidade.gatilho`, 2025-08-29T00:30:00 — PT-007.B failed, detected, unrepaired; `WO-RUN_A-CH-B` open.
- [demonstrated] `a2_estado_atual.ordens_servico[1]`, due 2025-05-31 — functional test of `reator.T1.B1` 90 d overdue, not executed; due date precedes the channel B failure.
- [demonstrated] `a2_estado_atual.ordens_servico[2]`, due 2025-07-30 — OP-B2 competence renewal 30 d overdue, open.
- [demonstrated] `a1_base_de_projeto.barreiras[*].c2` — C2 both multipliers: B1 1.08× barrier / 24.69× component, dominant XV-1001 49.6 %; B2 2.27× barrier / 24.69× component, dominant OP-B2 92.1 %.
- [demonstrated] `motores.conventional` and `motores.fuzzy` — top event design → current, ratios 2.02× and 1.9×, T1 share 70.1 % → 85.2 % (conventional).
- [corroborated] `a2_estado_atual.discrepancia_canais[0]` + `a2_estado_atual.grupo_votado` — readings agree within 0.54 kPa against a 17.5 kPa limit, sd 1.96–1.98 kPa against design noise 1.93 kPa, no frozen channel, no majority outlier: the record-declared failure of channel B is **not** visible in the process readings at `t_now`.
- [demonstrated] `a3_cruzamentos[C6]` + design basis §4 — detection declared independent, final element shared; joint credit must not multiply the two PFDs.
- [inferred] `a1_base_de_projeto.barreiras[1].componentes` versus design basis §4 — PT-007 appears in B2's asset list, contradicting independent detection. Contradiction recorded, not resolved.
- [inferred] `premissas_do_modelo.human_barrier_pfd_with_overdue_competence` (0.25) and `premissas_do_modelo.voted_group_without_reconfiguration` (2oo2) — both model assumptions, not asset data; B2's state and part of B1's erosion depend on them.
- [undetermined] `a2_estado_atual.contradicoes[0]` — PT-007 test clock: model 240 d versus calendar 90 d overdue; item PFD 1.9× apart, barrier effect 1.07× (B1) / 1.01× (B2).
- [undetermined] `a1_base_de_projeto.barreiras[1].motivos[1]` versus `ordens_servico[2].vencida_ha_dias` — OP-B2 lapse stated as 58 d and as 30 d in the same database.
- [undetermined] `envelope.lacuna` = `serie insuficiente na janela`; `a3_cruzamentos[C1].resultado` = no escalation window — no rate available, so C7's dynamic half and C1's envelope verdict are absent.
- [undetermined] `a3_cruzamentos[C3]` — real window not measurable, no demand on B1 up to `t_now`; the §5 windows and the 67 min B2 tolerable delay remain design-case only.
- [undetermined] `a3_cruzamentos[C8].lacuna` — threat-removal test not executed; T1 persistent-versus-removable unclassified, so the applicable barrier success criterion is not settled.
- [undetermined] supplied inputs — no consequence description, receptor or tolerability criterion; risk tolerability not determined.