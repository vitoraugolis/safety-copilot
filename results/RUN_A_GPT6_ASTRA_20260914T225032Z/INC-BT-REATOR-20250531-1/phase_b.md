# Escalate the overdue B1 functional test for immediate review, reconcile the conflicting test clocks, and obtain an authorised restoration plan.

## Fact

This trigger introduces a **maintenance-assurance lapse, not a demonstrated process excursion**: the functional-test order opened and became overdue at `identidade.ts`, under the inclusive due-date rule. Its elapsed overdue duration is recorded in `a2_estado_atual.ordens_servico[1].vencida_ha_dias`; no test finding or completion is recorded. The trigger is reproducible from `identidade.gatilho` and `a2_estado_atual.ordens_servico[1]`.

There are no active alarms or recorded B1 demands (`a2_estado_atual.alarmes_ativos`, `a2_estado_atual.demandas.B1`). Pressure-channel agreement and channel variation support the reported intact voted group, without evidence of freezing; they do not demonstrate the complete interlock function (`a2_estado_atual.grupo_votado`; design basis §4).

The assessment is frozen at `identidade.ts`, over `identidade.janela_de` onward. Units are supplied in `a1_base_de_projeto.limiares`; actual operating mode, clock synchronisation, signal-quality flags, bypass/test/isolation status, approved acceptance criteria and bowtie revision are **not demonstrated** by the supplied context. Process inference is additionally limited by `a2_estado_atual.escada_de_taxas.lacuna`; this does not invalidate the calendar trigger.

## Scenario and mechanism

**Loss of stream 1 feed → B1 automatic interlock → B2 backup manual action → loss of reactor control → downstream protection and consequences.** The diagram defines the preventive pathway and top event; the design basis identifies the SIS as a downstream automated layer, not evidence that B1 acted. Consequence severity, receptors and subsequent mitigation are not supplied (`diagrams/BT-REATOR.txt`; design basis §§3–5).

The supported quantitative chain is:

- Unexecuted functional test → uncertainty in latent-failure exposure and test-age PFD, **not an observed equipment failure** (`a2_estado_atual.ordens_servico[1]`; `premissas_do_modelo.mean_channel_pfd_between_tests`).
- Conflicting test clocks → alternative component and barrier PFDs (`a2_estado_atual.contradicoes[0].sensibilidade`).
- Model PFD inputs → computed top-event frequencies (`motores.pfd_atual`, `motores.conventional`, `motores.fuzzy`).

No frequency-criterion breach is established: this analysis was opened by maintenance records, and no numerical acceptance criterion is supplied (`identidade.gatilho`; risk-analysis reference §3).

## Analysis

### 1. Bowtie

- **B1 — degraded assurance, not demonstrated failure on demand.** The required test is overdue, but the context establishes neither functional removal nor a hard service-life expiry that would justify `critical`. The voted group remains intact by available evidence. Current calculated PFD is not proof of functional availability (`a2_estado_atual.ordens_servico[1]`, `a2_estado_atual.demandas.B1`, `a3_cruzamentos[3]`; SKILL.md B3).
- **B2 — degraded assurance/credit, not demonstrated physical failure.** Its model includes PT-007, while the declared detector is ZT-1001; the context supplies no B2 demand assessment or current human-response window. Full performance therefore cannot be demonstrated from its PFD alone (`a1_base_de_projeto.barreiras[1].componentes`, `a1_base_de_projeto.declarado.barreiras.B2`, `a3_cruzamentos[2]`; risk-analysis reference §§2, 5).

For both barriers, design/current PFDs, whole-barrier multipliers, worst-component multipliers and dominant-element shares are respectively in `a1_base_de_projeto.barreiras[0].{pfd_projeto,pfd_atual,c2}` and `a1_base_de_projeto.barreiras[1].{pfd_projeto,pfd_atual,c2}`. XV-1001 dominates B1; OP-B2 dominates B2. The disputed sensor-clock multiplier and corresponding **whole-barrier** sensitivities must be read together in `a2_estado_atual.contradicoes[0].sensibilidade`; component sensitivity is not equivalent to barrier deterioration.

B1 and B2 have independently declared detection but shared final elements. Their PFD product cannot receive independent-layer credit; the component mapping additionally contradicts the detection declaration (`a3_cruzamentos[5].comparado`; design basis §4).

### 2. Process

Pressure distances to the alert, SIS and physical boundary are recorded alongside **unavailable rates and projection times** in `a2_estado_atual.margem.PIT-7001`. These distances do not establish available response time. The same limitation applies to the other tags in `a2_estado_atual.margem`; instantaneous readings cannot establish a safe trajectory (cross-checks reference C7).

No operating-condition change is recorded, but the rate ladder and invalidation checks are incomplete. Accordingly, neither envelope invalidation nor current dynamic validity is demonstrated; the design response windows must not be presented as measured current margins (`a2_estado_atual.regime`, `a3_cruzamentos[0].comparado`, `envelope`; design basis §7).

### 3. Context

The previous channel repair and successful retest are recorded, but a corrective order does not reset the model’s functional-test clock. The newly overdue test cannot be portrayed as a missed opportunity to detect the earlier channel failure: its due date follows that failure and repair (`a2_estado_atual.ordens_servico`; `a2_estado_atual.contradicoes[0].fonte_a.regra`).

Further unresolved issues remain despite the empty C5 list:

- **Governing test clock:** verify the last qualifying test certificate and approved schedule; the calendar-implied date is an assumption (`a2_estado_atual.contradicoes[0]`).
- **Barrier configuration and PFD basis:** reconcile component-derived PFDs, `pfd_documento`, diagram values and design-basis declarations against approved configuration records (`a1_base_de_projeto.barreiras`; design basis §4; diagram).
- **Operational readiness:** verify mode, bypasses, temporary changes and complete functional-test coverage with operations and maintenance records (SKILL.md B3; risk-analysis reference §§2, 4).
- **Threat persistence:** remains unclassified pending the declared removal test (`a3_cruzamentos[7]`).

The supplied design reference is identifiable, but its approval and applicability at `identidade.ts`, and the diagram’s revision, are not established. No additional operational history or approved PHA/LOPA is supplied (design-basis provenance; risk-analysis reference §§3–4).

## Risk judgement

The computed design/current annual top-event frequencies and ratios are:

- **Conventional magnitude:** `motores.conventional.projeto.evento_topo_por_ano`, `motores.conventional.atual.evento_topo_por_ano`, `motores.conventional.razao`.
- **Fuzzy uncertainty propagation:** corresponding fields under `motores.fuzzy`, with labels in its `projeto.rotulo` and `atual.rotulo`.

These pairs do not demonstrate numerical escalation. T1 dominates the model contribution split (`motores.conventional.atual.pathways`), but shared actuation and unresolved configuration prevent treating the model output as validated independent-barrier risk credit. The exposure window is `motores.janela_de_exposicao_anos`; the diagram uses supplied frequencies/PFDs rather than an active MTTF conversion (`diagrams/BT-REATOR.txt`; `motores.pfd_atual`).

**Barrier erosion demonstrated at the assurance level; risk tolerability not determined.** Consequence frequencies, severities, receptors and approved tolerability criteria are absent. Confidence is high in the maintenance trigger, but low in a quantitative residual-risk conclusion (risk-analysis reference §§3, 7).

**Immediate review is warranted; an emergency condition is not demonstrated.** Missing dynamic margins prevent a justified operating grace period. If an excursion, approach to trip or critical protection loss is identified, escalate immediately under standing emergency procedures (`a2_estado_atual.margem`; SKILL.md Safety limits).

## Recommendation

**Immediate containment:** Operations and the safety-function owner should review the overdue test and actual protection status now, and make a documented interim operating decision; this report does not authorise continued operation (SKILL.md B5).

**Restoration:** Reconcile the test clock and arrange the authorised functional test covering detection, logic and final elements; retain traceable findings and post-repair test evidence where needed (risk-analysis reference §§2, 8).

**Definitive solution:** Resolve detector/PFD mapping discrepancies and review dependency-aware credit through the applicable configuration/MOC process. Prioritise observing B2’s actual demand signal rather than substituting pressure-alarm evidence (design basis §4; risk-analysis reference §§2, 4, 6).

**Suggested owner / deadline:** Operations and instrument-maintenance leads, supported by process safety; immediate review, with the test deadline set by the competent authority rather than an invented grace period (SKILL.md B5).

**Action risks:** Functional testing may temporarily impair protection or actuate shared valves. The approved test plan must address the declared loss of level control and downstream shutdown consequence (`a3_cruzamentos[5]`; risk-analysis reference §6).

**Expected return / leading indicator:** A verified functional-test record, reconciled clock and configuration, and tracked overdue-test exposure—not merely an unchanged model PFD (risk-analysis reference §8).

**Closure criteria:** Keep the occurrence open until function is verified by testing, temporary configurations are restored or managed, current envelope applicability is established, residual risk is reassessed and outstanding actions are traceable (SKILL.md Closure gate).

**Residual risk / accepting authority:** Undetermined; acceptance belongs to the facility’s designated competent authority, whose identity is absent from the supplied material (SKILL.md B5).

**Human decision:** pending.

## Evidence and assumptions

- **[demonstrated]** Newly overdue, unexecuted test: `identidade.gatilho`; `a2_estado_atual.ordens_servico[1]`.
- **[demonstrated]** Channel agreement without recorded B1 demand: `a2_estado_atual.grupo_votado`; `a2_estado_atual.demandas.B1`.
- **[undetermined]** Governing test age: conflicting database interpretations in `a2_estado_atual.contradicoes[0]`; calendar-implied last test is explicitly an assumption.
- **[inferred]** Maintenance-assurance erosion, not observed hardware failure: overdue test interpreted under SKILL.md B3 and risk-analysis reference §2.
- **[undetermined]** Actual dynamic margin, independent-layer credit and tolerability: `envelope.lacuna`, `a3_cruzamentos[5]`, and absent approved consequence/acceptance basis.
- **[assumption]** Calculated PFDs inherit `premissas_do_modelo`, including design-PFD retention where test records are absent; these are not proof of completed maintenance.