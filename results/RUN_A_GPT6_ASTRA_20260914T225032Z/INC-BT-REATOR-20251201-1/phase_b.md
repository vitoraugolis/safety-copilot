# Escalate the new feed-loss indication immediately to operations; do not rely on unvalidated barrier windows to justify continued operation.

## Fact

This trigger adds active low-flow indications to an already degraded protection context; it does **not** establish a pressure excursion or barrier failure on demand. The recorded crossings are reproducible against `identidade.gatilho[*].limite` and `a2_estado_atual.margem.FIT-1001`; their onset, duration and active state are in `a2_estado_atual.alarmes_ativos[*]`. B1 has not been demanded (`a2_estado_atual.demandas.B1`).

The assessment is frozen at `identidade.ts`, over the window beginning `identidade.janela_de`. Units are supplied in `a2_estado_atual.margem`; the recorded operating condition is in `a2_estado_atual.regime.mudanca`. Rates are unavailable, so persistence, escalation and time available cannot yet be established (`a2_estado_atual.taxas`, `envelope.lacuna`).

Instrument quality flags, clock synchronisation, saturation, manual overrides, current bypass/test/isolation status and an approved bowtie revision are not supplied. The alarm crossing is supported; physical feed loss remains subject to field verification rather than being inferred conclusively from one reading (SKILL.md, B1).

## Scenario and mechanism

**Indicated loss of stream 1 feed → B1 automatic interlock → B2 backup manual action → loss of reactor control → downstream mitigation and receptor consequences not demonstrated.** The pathway comes from `motores.diagrama`; the SIS is a downstream protection layer, not evidence that B1 acted (`a1_base_de_projeto.declarado.escada_protecao`, `.barreiras`).

Two distinct chains must remain separate:

- The new flow indication is consistent with threat T1, but neither its physical cause nor a resulting pressure escalation is established (`identidade.gatilho`, `envelope.lacuna`).
- Known sensor degradation, maintenance backlog and overdue competence renewal feed the modelled barrier PFDs and increased top-event frequency. This erosion predates the alarm; the trigger does not demonstrate a new PFD change (`a1_base_de_projeto.barreiras[*].motivos`, `a2_estado_atual.ordens_servico`, `motores`).

Consequence frequency and severity cannot be completed from the supplied material; temporal association with the operating-condition change is not root cause (references/risk-analysis-reference.md, §§1, 3, 7).

## Analysis

### 1. Bowtie

- **B1 — `degraded`.** Detection redundancy is reduced and functional testing is overdue; complete loss of function or failure on demand is not demonstrated. Read the design/current PFD pair at `a1_base_de_projeto.barreiras[0].pfd_projeto` and `.pfd_atual`; compare **both** `.c2.componente_pior.multiplicador` and `.c2.multiplicador_barreira`. XV-1001 still dominates, as recorded in `.c2.elemento_dominante`. Effectiveness under the changed operating condition remains unverified.
- **B2 — `degraded`; credit unverified.** Competence renewal is overdue, but operator failure on demand is not observed. Its PFD pair and both component/barrier multipliers are at `a1_base_de_projeto.barreiras[1].pfd_projeto`, `.pfd_atual` and `.c2`; OP-B2 dominates. Its current human contribution is a **model assumption**, not measured competence (`premissas_do_modelo.human_barrier_pfd_with_overdue_competence`). Available human response time is unknown, not demonstrated adequate (`a3_cruzamentos[2]`).

PT-007 is **known degraded**, not hidden degraded. Channel B’s own low variability supports freezing near the former regime, rather than drift; A and C identify B as the divergent channel. Their possible common error remains unresolved (`a2_estado_atual.grupo_votado`, `a3_cruzamentos[4].lacunas`). Exposure follows the repair backlog clock in `a3_cruzamentos[3].relogio`; a repair deadline is absent from the associated work order.

The declared B2 detector is ZT-1001, but its model component list includes PT-007 instead. This unresolved mapping discrepancy limits interpretation of B2’s sensor multiplier (`a1_base_de_projeto.barreiras[1].componentes` versus `.declarado.barreiras.B2`). No B2 demand outcome or command-position evidence is supplied.

B1 and B2 share final elements despite independent declared detection. Their PFD product is therefore **not demonstrated joint protection credit**; neither IPL nor SIL credit follows from the diagram (`a3_cruzamentos[5]`; references/risk-analysis-reference.md, §2).

### 2. Process

The recorded operating-condition change without revalidation invalidates reliance on the base-case response windows independently of whether an excessive escalation rate is observed. Compression itself cannot yet be measured (`a2_estado_atual.regime.revalidacao_registrada`, `a3_cruzamentos[2]`; design basis, §7).

Pressure distance to HI and the downstream targets must be read alongside the **null** rate and time fields in `a2_estado_atual.margem.PIT-7001`. These distances do not demonstrate comfortable response time. The same limitation applies to the other monitored variables; the C7 summary does not overcome the missing rate ladder (`a2_estado_atual.escada_de_taxas`). The declared HIHI target also lacks a corresponding dynamic-margin calculation (`a1_base_de_projeto.limiares[0].hihi`).

Earlier low-pressure alarms document the changed regime, not proof of the present threat’s cause. Threat persistence remains unclassified; neither stable recovery nor inevitable continued escalation can be claimed (`a2_estado_atual.regime`, `a3_cruzamentos[7]`).

### 3. Context

Work-order findings are restricted to the frozen recovery rule in `a2_estado_atual.regra_de_recuperacao["work orders"]`. They support restoration and maintenance-governance review, not operator blame (`a2_estado_atual.ordens_servico`; references/risk-analysis-reference.md, §§4–5).

Resolve these discrepancies before accepting quantitative credit:

- Test-clock alternatives and their existing sensitivity results: `a2_estado_atual.contradicoes[0]`.
- Competence-overdue duration: `a1_base_de_projeto.barreiras[1].motivos` versus `a2_estado_atual.ordens_servico[2].vencida_ha_dias`.
- PFD provenance: `.pfd_documento` versus `.pfd_projeto` for both barriers, the supplied diagram and design-basis §4.

The basis is declared, but approval/version evidence, applicable MOC rules and operational authorisation are absent. Absence of these records does not establish non-compliance (references/risk-analysis-reference.md, §4).

## Risk judgement

**Barrier erosion demonstrated; risk tolerability not determined.**

The conventional design/current frequencies and ratio are `motores.conventional.projeto.evento_topo_por_ano`, `.atual.evento_topo_por_ano` and `.razao`; T1 dominates the current split in `.atual.pathways`. These are model outputs, not validated residual-risk estimates, given dependence, mapping and envelope limitations.

The fuzzy counterparts are `motores.fuzzy.projeto`, `.atual` and `.razao`. Their unchanged linguistic label does not negate erosion or establish acceptance. Use conventional results for modelled magnitude and fuzzy results for linguistic propagation—not mutual validation (`motores.nota`).

The diagram uses direct frequency/PFD inputs rather than an MTTF-derived path; exposure is recorded in `motores.janela_de_exposicao_anos` (`diagrams/BT-REATOR.txt`; SKILL.md, “Reading the engine’s numbers”).

No approved frequency acceptance criterion, consequence severity, receptor assessment or consequence-frequency model is supplied. **Urgency: immediate**, because the new threat indication coincides with degraded protection and unknown response time; emergency conditions are not established. Quantitative residual-risk confidence is **low** for the limitations above (SKILL.md, B4).

## Recommendation

**Immediate containment:** Operations should promptly verify feed status, obtain an independent vessel-pressure check and apply standing abnormal-operation procedures. Escalate under standing emergency procedures if the safety-limit conditions arise; do not wait for analytical certainty. Do not improvise valve actions, setpoint changes or bypasses (`identidade.gatilho`; `a3_cruzamentos[4].lacunas`; SKILL.md, “Safety limits”).

**Restoration:** Instrumentation and maintenance should repair and test the failed channel, complete overdue functional testing, reconcile test records and verify actual voting configuration. Operations/training should renew and demonstrate B2 readiness, including its discrepancy indication and realistic response window (`a2_estado_atual.ordens_servico`; references/risk-analysis-reference.md, §§2, 8).

**Definitive solution:** Process safety and engineering should reconcile the B2 mapping and dependent-barrier model, assess the operating change under applicable MOC rules and revalidate response windows. Review recurring channel defects and overdue safety work; investigate formally if systemic failure is confirmed (references/risk-analysis-reference.md, §§4–6; SKILL.md, B5).

**Action risks:** Feed-valve closure can remove inventory control and introduce a low-level shutdown; maintenance can temporarily reduce redundancy. Authorised action planning must address both (`a3_cruzamentos[5]`; references/risk-analysis-reference.md, §2).

**Suggested owner / deadline:** Shift operations—immediate assessment; maintenance, training and process-safety leads—restoration and validation before renewed barrier-credit acceptance (SKILL.md, B5).

**Expected return / leading indicator:** Verified feed condition, usable rate windows, restored channel agreement, successful functional tests, reconciled deadlines and demonstrated operator readiness—not merely alarm clearance (references/risk-analysis-reference.md, §8).

**Closure criteria:** Controlled condition, restored and tested functions, managed temporary changes, revalidated windows, reassessed residual risk and traceable remaining actions. The occurrence remains action-required (SKILL.md, B5).

**Residual risk / accepting authority:** Undetermined; acceptance belongs to the facility’s designated authority, whose identity is not supplied (references/risk-analysis-reference.md, §3).

**Human decision:** pending.

## Evidence and assumptions

- **Demonstrated:** Recorded alarm crossings, unrepaired channel failure, overdue work and missing recorded revalidation (`identidade.gatilho`, `a2_estado_atual`).
- **Inferred:** Physical feed loss and its prospective T1 progression; no current escalation trajectory establishes that progression (`envelope.lacuna`; design basis, §§2, 4).
- **Undetermined:** Common cause in A/C, actual response windows, B2 demand observability, consequence severity and tolerability (`a3_cruzamentos[2]`, `[4]`; missing decision inputs above).
- **Assumptions retained, not endorsed:** Human PFD substitution, degraded-vote model and default treatment of missing test records (`premissas_do_modelo`).