---
incident_id: INC-BT-REATOR-20251201-1
bowtie_id: BT-REATOR
opened_at: 2025-12-01T00:00:05
engine: conventional
status: action_required
urgency: immediate
confidence: medium
---

# Escalate now: the T1 initiating event (total loss of stream 1 feed) has just occurred while both preventive barriers of that pathway are degraded and the design basis that would give the available response window is invalidated — treat the HI→SIS windows as unknown and restore feed or prove the escalation rate before it matters.

## Fact

- Trigger: `identidade.gatilho` — `alarme:FIT-1001:LO` and `alarme:FIT-1001:LOLO`, both at `2025-12-01T00:00:05`, value `a2_estado_atual.margem.FIT-1001.valor` kscmh against design feed `a1_base_de_projeto.declarado.condicao_de_projeto.vazao_alimentacao_kscmh`. Both thresholds crossed simultaneously (`margem.FIT-1001.limiares_ja_cruzados`), duration `a2_estado_atual.alarmes_ativos[].ativo_ha_min` = 0.0 min.
- These alarms are **not** a demand on any barrier (`alarmes_ativos[].e_demanda = 0`); B1's declared trigger is voted PIT-7001 ≥ HIHI (`a1_base_de_projeto.declarado.barreiras.B1.gatilho`) and no demand on B1 is recorded (`a2_estado_atual.demandas.B1.demandada = false`). This is the initiating event of pathway T1, not a barrier failure.
- Pressure at t_now: `margem.PIT-7001.valor` kPa, no threshold crossed, distance to HI `margem.PIT-7001.distancia`, to SIS trip and physical limit per `margem.PIT-7001.alvos_declarados`.
- **Data quality limit:** the rate ladder is empty — `envelope.lacuna` = "serie insuficiente na janela"; every `taxa_por_min` and `tempo_ate_limiar_min` in `a2_estado_atual.margem` is null. No rate exists at t_now, so no distance in this report may be read as time available (SKILL.md, "Do not conclude from an instantaneous value").
- Voted group PIT-7001 reads A/B/C per `a2_estado_atual.discrepancia_canais[0].canais`, spread 63.21 kPa against limit 17.5 (`.spread`, `.limite`) — above limit. Channel B is the majority outlier (`grupo_votado.concordancia_no_ultimo_instante.divergente_pela_maioria`).
- Operating mode: "campanha padrao" with `carga_pct 15` and `escala_setpoints_alimentacao 1.15`, recorded `2025-11-28T00:00:00` (`a2_estado_atual.eventos_operacionais[0]`), `regime.revalidacao_registrada = false`.

The crossing is reproducible from the voted series and the alarm record; the trigger is not inconsistent. What is insufficient is the *dynamic* context, and that is carried forward as a gap, not as an inference.

**What this trigger changed.** This is the first analysis in the stream. It changes the status of the T1 threat from a diagram frequency (0.5/yr, `diagrams/BT-REATOR.txt`) to an observed event. Everything else in the block — the degraded voted group, the two overdue work orders, the 2025-11-28 regime shift — was already true before t_now and is now loaded onto an active pathway.

## Scenario and mechanism

Qualitative chain: **T1 loss of stream 1 feed** → **B1 automatic high-pressure interlock** (AND) → **B2 manual operator action** (AND) → **top event: loss of reactor control** → (mitigation not in scope of the T1 pathway as declared) → consequence/receptor **not declared in any supplied source**.

Quantitative chain, link by link:

| Link | Value | Source | Strength |
|---|---|---|---|
| FIT-1001 → 0 kscmh = threat T1 realised | `margem.FIT-1001.valor`; threat node "Perda de alimentacao da corrente 1" | trigger + diagram | demonstrated |
| T1 → pressure escalation | design basis §2/§5 measured escalation 1.1 kPa/min in the **base case only** | `declarado.condicao_de_projeto.taxa_escalada_kpa_min` | inferred — the base case no longer describes the plant (see C1 below) |
| PT-007.B failed unrepaired → B1 detection degraded | `a2_estado_atual.canais[PT-007.B].estado`, WO-RUN_A-CH-B open since 2025-08-29T00:30, `a3_cruzamentos[C4].relogio` = 93 d backlog | maintenance + reliability records | demonstrated |
| Frozen channel B → vote effectively 2oo2 on A and C | `grupo_votado.congelamento` (B flat at 2708.41, band ±1.5, sd 0.21 vs 43.08/43.01 for A/C in `grupo_votado.estatistica_por_canal`); model assumption `voted_group_without_reconfiguration` | computed from series + model assumption | corroborated |
| Overdue functional test + degraded group → PT-007 PFD ×34.35 | `a1_base_de_projeto.barreiras[B1].c2.componente_pior` | reliability model | demonstrated (under the model clock; see contradiction) |
| Overdue competence → OP-B2 PFD 0.25 | `premissas_do_modelo.human_barrier_pfd_with_overdue_competence` | **model assumption, not asset data** | inferred |
| Barrier PFDs → top event frequency ×2.07 | `motores.conventional.razao` | engine | demonstrated (conditional on the assumptions above) |
| Top event → consequence severity/receptor | — | absent from all supplied sources | undetermined |

The failure mode of channel B is named by its own variance, not by the spread: sd 0.21 kPa over 180 samples against 43.08 and 43.01 for A and C, flat inside a ±1.5 kPa band since ≈2025-08-29 — a **stuck-at-last-value** transmitter, not a drift. Its frozen value (2708.41) sits 0.04 kPa from the pre-change regime median (`congelamento.diferenca_para_o_regime`). The mechanism worth naming: **the freeze was invisible in the data until the process moved.** While the plant ran at its old regime the frozen reading agreed with the live channels; the 2025-11-28 operating-condition change dropped the regime by 148.86 kPa (`regime.deslocamento_kpa`) and the frozen channel stayed put, which is why the spread only now exceeds its limit. The maintenance record found it on 2025-08-29; the process data confirms it on 2025-12-01. Both sources agree, by different routes — corroborated.

## Analysis

### 1. Bowtie

**B1 — high-pressure interlock: `degraded`.** No demand up to t_now (`demandas.B1`), so no observation outranks the PFD. C2 (`barreiras[B1].c2`): barrier multiplier 1.11× — the barrier moves little because the dominant element is XV-1001 at 48 % of the total and unchanged, while the worst component PT-007 moves 34.35×. Both multipliers must be read together: reporting only 34.35× over-reacts, reporting only 1.11× hides that the *detection* arm is what degraded. The state is `degraded`, not `critical` — the function is neither removed nor bypassed — but with two qualifications:

- The vote is running effectively 2oo2 on A and C, because a channel frozen at 2708.41 kPa can never vote above HIHI 2800. A single further channel failure removes B1's detection entirely.
- C4 clock: this is **known degraded** (work order exists), so the exposure horizon is the repair backlog, 93 d and running (`a3_cruzamentos[C4].relogio`) — not a test interval. The functional test WO-RUN_A-TEST is nonetheless overdue by 184 d, which is why no independent proof of the interlock's function exists in this horizon.

**B2 — manual operator action: `degraded`, with its PFD's *meaning* unsupported.** C2 (`barreiras[B2].c2`): barrier multiplier 2.27×, dominant element OP-B2 at 91.8 % of the total. The current figure rests on `premissas_do_modelo.human_barrier_pfd_with_overdue_competence` = 0.25 — a model assumption, not a value read from the asset. Two further findings bear on it and neither may be converted into a number here:

- The design basis states that B2's whole margin is perception and decision, not execution (§5), and that its demand arises only after B1 has tried and failed (§4). Its 67-min tolerable delay is a property of the base-case window.
- C3 could not be evaluated (`a3_cruzamentos[C3].nao_se_aplica` — no demand on B1), so the real window is not measured. Combined with C1 below, B2's declared window is **unknown, not merely compressed**. Per SKILL.md this is recorded as a gap; the PFD is not adjusted.

**Independence (C6).** Detection is independent (PT-007 vs ZT-1001) but the final elements XV-1001 and VLV-006 are shared between B1 and B2 (`a3_cruzamentos[C6].comparado.shared_items`, `declared_independence`). Joint credit must not be taken as the product of the two PFDs. No IPL/SIL credit is claimed here for either barrier; none is documented in the supplied sources.

**Declared side effect of B1 acting (C6).** Closing the A+C feed valve removes the actuator of level cascade LIC-8001; inventory control is lost, level goes to ≈ −2.5 % and a low-level trip follows roughly 1 h later. This is a declared secondary consequence, not a failure of B1 against the T1 top event (design basis §4, §5).

**B3/B4 (temperature pathway).** Entered the engines at their design PFDs (`motores.pfd_atual`). No evidence was assembled for them in this run; their state is **not assessed**, not "healthy".

### 2. Process

Trajectory, not last value — but the trajectory is exactly what is missing. `envelope.lacuna` declares the series insufficient in the window, so every rate is null and C7 (`a3_cruzamentos[C7]`) reduces to distance without time. Distances stand at `margem.PIT-7001` (104.43 kPa to HI; 254.43 to SIS trip, source `alarm_config.trip_sis`; 354.43 to the physical limit, source design basis §3). **Time to any of those targets is not determined.**

I will not convert distance into time using the design basis rate of 1.1 kPa/min, because C1 has declared the envelope unverified — the operating-condition change of 2025-11-28 shifted the pressure regime by −148.86 kPa with no revalidation recorded (`a3_cruzamentos[C1].resultado`), which is explicitly an invalidation trigger of the basis (§7, "operating-condition change without subsequent revalidation"). Under an invalidated basis the windows of §5 (202 min HI→SIS, 162 min HIHI→SIS, 67 min B2 tolerable delay) do not describe the current condition and must not be cited as available time. The plateau at 2850–2870 kPa, where most of the barriers' margin sits in the base case (§2), is likewise a property of the base case and cannot be assumed present.

Precursors since the change: three PIT-7001 LO alarms between 2025-11-28 and t_now (`regime.alarmes_entre_a_mudanca_e_o_episodio`), peaks 2518.25 / 2535.64 / 2545.81, all normalised. The plant has been running below its validated pressure regime for three days.

Other tags at t_now, all instantaneous and all without rate: TIT-9001 120.34 °C against design steady 120.4 °C — unremarkable; TIT-2101 94.94 °C, 5.06 below HI; LIT-8001 80.91 %, 4.09 below HI 85 and **6.5 points above the design steady level of 74.4 %** (`declarado.condicao_de_projeto.nivel_regime_pct`). That last one deserves attention but does not support a conclusion without a rate, and it interacts with the C6 side effect: B1 acting from an elevated level drives the level cascade in the opposite direction.

### 3. Context

- **Design basis** (`references/design-basis-barriers.md`, converted 2026-09-11): declared and loaded, but its own §7 invalidation criteria are met. Its performance section is unusable in the current condition. This is a document that correctly declares its own limits; the gap is the missing revalidation, not the document.
- **Management of change:** an operating-condition change was recorded on 2025-11-28 with `revalidacao_registrada = false`. Per the risk-analysis reference §4, a load/setpoint change without revalidation of the barrier windows is both an integrity finding and an envelope invalidation trigger. Whether a formal MOC was required is not determined from the supplied records — the absence of a record is a gap, not proof of non-compliance.
- **Mechanical integrity:** WO-RUN_A-TEST (functional test of the B1 interlock) overdue 184 d and not executed; WO-RUN_A-CH-B (channel B corrective) open 93 d. Repeat pattern on the same asset: WO-RUN_A-CH-A was a channel discrepancy on PT-007 closed with a finding on 2025-04-02. Two channel failures in one voted group within five months, with the functional test overdue across both, is a pattern worth a separate look — I flag it as a candidate for systemic review, not as a demonstrated systemic failure.
- **Human and organisational factors:** WO-RUN_A-TRAIN overdue 124 d against a declared 182-d interval. Credit for B2 requires indication, time, competence, access and means (risk-analysis reference §5); competence renewal is overdue and the available time is undetermined. No blame attaches to the operator: the task, the window and the training calendar are the findings.
- **Recorded contradiction, unresolved:** the PT-007 creep clock says 334 d since the last test (interval 365 d); the maintenance calendar says the test is overdue by 184 d (`a2_estado_atual.contradicoes[0]`). The sensitivity is small at barrier level — B1 1.07×, B2 1.01× — so it does not change this decision, but which clock governs is a decision for the team, not for this report.

## Risk judgement

Top event frequency, both engines, design → current (`motores`):

- **Conventional (magnitude):** `motores.conventional.projeto.evento_topo_por_ano` → `motores.conventional.atual.evento_topo_por_ano`, ratio `motores.conventional.razao` = 2.07×. Pathway T1 share rises from 70.1 % to 85.6 % of the total.
- **Fuzzy (linguistic uncertainty):** `motores.fuzzy.projeto.evento_topo_por_ano` → `motores.fuzzy.atual.evento_topo_por_ano`, ratio 1.98×, label **Moderate → Moderate**.

The two engines are reported side by side and neither checks the other. The label has not changed; the frequency has roughly doubled. That is the point of reporting both: linguistic quantisation absorbs a factor of two, so "still Moderate" is not evidence of stability. The label qualifies a frequency, not a barrier state and not risk.

**Consequence, receptors and tolerability: not declared in any supplied source.** No consequence severity, no receptor, no approved tolerability criterion, no SIL/IPL allocation appears in the bowtie, the diagram or the design basis. Therefore the correct conclusion is:

> **Barrier erosion demonstrated (2.07× on the conventional engine, concentrated 85.6 % in the active pathway T1); risk tolerability not determined.**

Uncertainty, and what it rests on: OP-B2's 0.25 is a model assumption; the 2oo2 fallback is an assumption; the available time is not determined at all; the threat is unclassified (C8 — the removal test of design basis §6 was never run, so whether barriers can produce a stable state or only buy time until the feed is restored is unknown); and one named decidability gap remains (C5 — a common cause affecting the agreeing pair A and C cannot be excluded without an independent field pressure measurement). Confidence is capped at **medium** by the weakest decisive link: the undetermined window.

**Urgency: immediate** (not emergency). No active loss of containment, no threshold crossed on PIT-7001, and 254 kPa of distance to the SIS trip at t_now. But the initiating event of the pathway has occurred, both preventive barriers on it are degraded, the interlock's detection is one channel from being lost, and the quantity that would justify waiting — time to HI — does not exist. Escalation is warranted now, on the strength of the plausible scenario and the missing data, not after the rate is measured. High consequence with an unquantified frequency is not discarded by the absence of a consequence table.

## Recommendation

**Immediate containment:** escalate to the shift supervisor and process safety now — T1 initiating event confirmed on a pathway whose barriers are degraded and whose response window is not known. Establish continuous manned watch on PIT-7001 with the rate computed over declared windows (the single most valuable missing number). Verify by field indication whether the stream 1 feed loss is a trip, a blockage or an upstream supply loss, and restore feed if it can be done safely: under C8 the recovery route is removal of the threat, and no barrier on this pathway produces a stable state. Confirm, before it is needed, that the operator on shift knows B2's real trigger is the ZT-1001 command-versus-position discrepancy and not the pressure alarm (design basis §4).

**Restoration:** repair PT-007 channel B (WO-RUN_A-CH-B, open 93 d) — highest priority, as it restores the vote from an effective 2oo2 to 2oo3 and removes the single-failure exposure on B1's detection. Execute WO-RUN_A-TEST (overdue 184 d) so the interlock function is proven rather than assumed. Execute WO-RUN_A-TRAIN (overdue 124 d) — noting that this restores competence but does **not** restore B2's window, which is a property of the operating condition.

**Definitive solution:** revalidate the design basis windows under the operating condition introduced on 2025-11-28 (procedure in `references/producing-a-design-basis.md`, steps 2–6) and close the missing MOC revalidation; run the threat-removal test of §6 to close the C8 classification; obtain an independent field measurement of vessel pressure to close the C5 gap on a possible common cause in channels A and C. Prefer, in the response hierarchy, measures that act on the threat (feed supply reliability) over measures that add administrative load to an already-degraded human barrier — an administrative control does not permanently compensate for the engineering gap.

**Risks introduced by the recommended actions:** if B1 acts, the declared C6 side effect follows — loss of inventory control via LIC-8001, level to ≈ −2.5 %, low-level trip about 1 h later. Any manual intervention through XV-1001 or VLV-006 uses the same shared final elements and carries the same coupling. Repair of PT-007.B and execution of the functional test may require a bypass of the interlock: that bypass makes B1 `critical` while it is in force and needs a compensating watch, a declared validity and a withdrawal condition.

**Suggested owner / deadline:** operations shift supervisor (containment, now); maintenance/I&C lead (PT-007.B repair and WO-RUN_A-TEST, target within the current shift-plus-24 h given the 93-d backlog); process safety/technical authority (basis revalidation and MOC closure, before the next campaign at the altered condition); training coordinator (WO-RUN_A-TRAIN).

**Expected return / leading indicator:** PT-007 spread back within the 17.5 kPa limit with three live channels each showing noise comparable to design (1.93 kPa, §3); B1 PFD returning toward its design value with the barrier multiplier back to ≈1×; PIT-7001 rate measured and compared against the revalidated basis; zero overdue safety-critical work orders on `reator.T1`.

**Closure criteria:** feed restored or the threat otherwise removed and pressure stable within a technically justified window; PT-007.B repaired **and functionally tested** covering the stuck-at failure mode; the B1 interlock functional test executed with its result recorded; any bypass documented as restored; OP-B2 competence renewed; design basis windows revalidated under the current operating condition and the invalidation cleared; C5 and C8 gaps either closed or formally carried as accepted open items. The pressure returning to band does not close this occurrence.

**Residual risk / accepting authority:** not determinable in this report — no tolerability criterion is declared in any supplied source. Acceptance belongs to the facility's designated authority, and must be taken against the *current* frequency (`motores.conventional.atual.evento_topo_por_ano`), not the design figure.

**Human decision:** pending

## Evidence and assumptions

- [demonstrated] Trigger package, `identidade.gatilho`, 2025-12-01T00:00:05 — total loss of stream 1 feed; LO and LOLO crossed simultaneously; this is the T1 initiating event, not a barrier demand (`alarmes_ativos[].e_demanda = 0`).
- [demonstrated] `a2_estado_atual.canais` + WO-RUN_A-CH-B, 2025-08-29 — PT-007 channel B failed, detected, unrepaired; 93 d repair backlog (C4 clock).
- [corroborated] `grupo_votado.congelamento` + `grupo_votado.estatistica_por_canal` — channel B stuck-at-last-value (sd 0.21 vs 43.08/43.01); reading and maintenance record agree on the same failure by independent routes.
- [demonstrated] `a3_cruzamentos[C1]` + design basis §7 — operating-condition change 2025-11-28 shifted the regime −148.86 kPa with `revalidacao_registrada = false`; the §5 windows are unverified and were not used.
- [demonstrated] `a1_base_de_projeto.barreiras[*].c2` — B1 1.11× barrier / 34.35× worst component, dominant XV-1001 (48 %); B2 2.27× barrier / 34.35× worst component, dominant OP-B2 (91.8 %).
- [demonstrated] `a3_cruzamentos[C6]` + design basis §4 — detection independent, final elements XV-1001 and VLV-006 shared; PFDs must not be multiplied; declared side effect on LIC-8001 with low-level trip ≈1 h after B1 acts.
- [demonstrated] `motores` — conventional 2.07×, fuzzy 1.98×, label Moderate → Moderate; T1 share 70.1 % → 85.6 %.
- [inferred] OP-B2 PFD 0.25 — `premissas_do_modelo.human_barrier_pfd_with_overdue_competence`, a model assumption replacing the design value while WO-RUN_A-TRAIN stays open; not read from the asset.
- [inferred] Effective 2oo2 vote on A and C — from `premissas_do_modelo.voted_group_without_reconfiguration` plus the frozen value of B sitting below HIHI; the fall to 2oo2 is declared an assumption in the model.
- [undetermined] Available time to HI, SIS trip and physical limit — `envelope.lacuna` "serie insuficiente na janela"; all rates null. External check: rate of PIT-7001 over declared windows once the series is sufficient.
- [undetermined] Common cause affecting channels A and C — `a3_cruzamentos[C5]`; external check: independent field measurement of vessel pressure.
- [undetermined] T1 persistent vs removable — `a3_cruzamentos[C8]`; the removal test of design basis §6 was never executed.
- [undetermined] Consequence, receptor, tolerability criterion, IPL/SIL credit — absent from bowtie, diagram and design basis; no value fabricated.
- [undetermined] State of B3/B4 and the temperature pathway — entered the engines at design PFD; no evidence assembled in this run.
- [demonstrated, unresolved] PT-007 clock contradiction — `a2_estado_atual.contradicoes[0]`; model clock vs calendar clock, barrier-level sensitivity B1 1.07× / B2 1.01×; does not change this decision, but the governing clock is a team decision.
- Doctrine consulted: CCPS/Energy Institute, *Bow Ties in Risk Management* (CCPS–EI, 2018), on barrier independence and IPL credit — used to withhold credit, not to authorise a conclusion.