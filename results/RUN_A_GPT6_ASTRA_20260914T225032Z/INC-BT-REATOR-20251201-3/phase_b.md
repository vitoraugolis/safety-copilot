# Escalate immediately to Operations and apply standing abnormal/emergency procedures for rising pressure outside the validated barrier envelope.

## Fact

This trigger adds a **new pressure HI alarm**, not a barrier demand, to the existing feed-flow alarms and protection backlog. The crossing is supported by `identidade.gatilho[0]` and `a2_estado_atual.alarmes_ativos[2]`; its onset, duration and current state are recorded there. B1 has not been demanded (`a2_estado_atual.demandas.B1`).

This assessment is frozen at `identidade.ts`, over `identidade.janela_de` onward. The recorded operating condition is in `a2_estado_atual.regime.mudanca`; pressure units, current value and measured rate are respectively `a2_estado_atual.margem.PIT-7001.{unidade,valor,taxa_por_min}`, with the regression window in `a2_estado_atual.taxas.PIT-7001.entradas`.

The crossing is sufficiently supported for conservative action: the agreeing channels identify B as divergent, and its low variability supports freezing rather than drift (`a2_estado_atual.grupo_votado`). Independent pressure accuracy remains unverified because common error in the agreeing pair is unresolved (`a3_cruzamentos[4].lacunas`).

Phase A is accepted as closed, with decision-bearing gaps retained: independent pressure verification; actual response windows; conflicting maintenance clocks and barrier mappings; threat classification; instrument range, quality flags and clock synchronisation; bypass/test/isolation status; approved bowtie revision, consequence analysis and tolerability criteria. These are not demonstrated by the supplied context; closure of Phase A does not resolve them (`fase`; `a2_estado_atual.contradicoes`; `a3_cruzamentos`; SKILL.md, Phase B prerequisites).

## Scenario and mechanism

**Loss of stream feed → B1 automatic prevention → B2 backup after command–position discrepancy → loss of reactor control → consequence/receptor not specified.** The SIS is a separately declared downstream automated layer, not evidence of B1 success; no mitigating-barrier performance or consequence model is supplied (`diagrams/BT-REATOR.txt`; design basis §§3–5).

The near-zero feed reading and persistent low alarms support the T1 scenario, but do not establish its root cause (`a2_estado_atual.margem.FIT-1001`; `a2_estado_atual.alarmes_ativos[0:2]`).

Two erosion mechanisms coexist:

- Recorded channel failure and overdue competence renewal feed the calculated barrier PFDs (`a2_estado_atual.canais`; `a2_estado_atual.ordens_servico`; `a1_base_de_projeto.barreiras[*].pfd_atual`).
- Faster pressure escalation and an unrevalidated operating change invalidate the effectiveness windows independently of equipment availability (`envelope.gatilhos_de_invalidacao`; `envelope.invalidada`).

The engines propagate these model PFDs to top-event frequency, but the shared actuation dependency prevents treating their multiplication as demonstrated independent protection credit (`motores`; `a1_base_de_projeto.declarado.independencia`). This analysis was opened by an alarm criterion; a frequency-threshold breach is not established (`identidade.gatilho`).

## Analysis

### 1. Bowtie

**B1 — `degraded`.** Detection redundancy is reduced, the repair remains outstanding, and the operating envelope is invalidated; failure on demand is not demonstrated (`a3_cruzamentos[3]`; `envelope.invalidada`; `a2_estado_atual.demandas.B1`). Its automatic response is intrinsically faster than human intervention, but successful arrest under current conditions remains unverified (design basis §§4–5; `a3_cruzamentos[2]`).

For B1, read design → current PFD at `a1_base_de_projeto.barreiras[0].{pfd_projeto,pfd_atual}`. Both the **whole-barrier multiplier** and **worst-component multiplier** are in `.c2.{multiplicador_barreira,componente_pior.multiplicador}`; the final-element contribution still dominates (`.c2.elemento_dominante`).

The voted group is **known degraded**, not hidden degraded. B is frozen near the former reference regime; the exposure clock is the unresolved repair backlog, with no repair deadline recorded—not an assumed future proof-test horizon (`a2_estado_atual.grupo_votado.congelamento`; `a3_cruzamentos[3].relogio`; `a2_estado_atual.ordens_servico[3]`).

**B2 — `degraded`; current effectiveness not demonstrated.** Overdue competence renewal supports reduced assurance, not a finding that an operator failed. Neither a demand nor inability to complete the task is demonstrated; the actual response window is unavailable (`a2_estado_atual.ordens_servico[2]`; `a3_cruzamentos[2]`; design basis §4).

For B2, design → current PFD and both multipliers are at `a1_base_de_projeto.barreiras[1].{pfd_projeto,pfd_atual,c2}`. The dominant human contribution uses an explicit model assumption, not measured current competence (`premissas_do_modelo.human_barrier_pfd_with_overdue_competence`). The design human delay cannot be credited after envelope invalidation, and no replacement PFD is justified (design basis §§5,7; SKILL.md B3).

B2 detects **ZT-1001 command–position discrepancy**, not pressure HI. Its calculated component list instead includes PT-007: this unresolved mapping conflicts with the declared independent detection. Both barriers nevertheless share final elements, so joint IPL/SIL credit is not demonstrated (`a1_base_de_projeto.barreiras[1].componentes`; `a1_base_de_projeto.declarado.barreiras.B2`; `.independencia`).

### 2. Process

The episode-wide average masks the faster recent rise: compare `envelope.degraus[0]` with `[1]` and `[2]`. Together with the operating change, this invalidates the design windows. The plateau has **not yet been assessed**, because its band has not been reached; its absence later cannot be inferred (`envelope.gatilhos_de_invalidacao`).

Read dynamic margins together:

| Target | Distance | Rate and computed time |
|---|---|---|
| HI, already crossed | `a2_estado_atual.margem.PIT-7001.limiares_ja_cruzados` | `.taxa_por_min` |
| HIHI / B1 demand | `.distancia` | `.taxa_por_min`; `.tempo_ate_limiar_min` |
| SIS trip | `.alvos_declarados[0].distancia` | `.taxa_por_min`; `.alvos_declarados[0].tempo_min` |
| Model physical limit | `.alvos_declarados[1].distancia` | `.taxa_por_min`; `.alvos_declarados[1].tempo_min` |

Here, dotted paths continue `a2_estado_atual.margem.PIT-7001`. These times are **computed constant-rate projections**, not observed response windows or guaranteed available time (`.nota`; `a2_estado_atual.taxas.PIT-7001`).

No B1 actuation should be inferred from valve trends before its declared demand. Feed remains suppressed, but persistent-versus-removable threat classification requires the missing removal test (`a2_estado_atual.demandas.B1`; `a3_cruzamentos[7]`).

### 3. Context

The prior channel repair, outstanding channel failure, overdue functional test and overdue training indicate multiple assurance weaknesses warranting organisational review, without assigning operator blame (`a2_estado_atual.ordens_servico`; risk-analysis reference §§4–5).

Reconcile before granting quantitative credit:

- The proof-test clock conflict and its already-computed sensitivity (`a2_estado_atual.contradicoes[0]`).
- The training age in `a1_base_de_projeto.barreiras[1].motivos[1]` versus `a2_estado_atual.ordens_servico[2].vencida_ha_dias`.
- Asset-summed PFDs, `.pfd_documento`, the supplied diagram and design-basis declarations; their agreement is not established (`a1_base_de_projeto.barreiras`; design basis §4).
- Threshold/voting/test-interval configuration history: the declared invalidation criteria are not all explicitly resolved by the supplied checks (`a1_base_de_projeto.declarado.invalidacao`; `envelope.gatilhos_de_invalidacao`).

Review the recorded operating change through applicable MOC requirements; missing revalidation is evidence of an assurance gap, not proof of regulatory non-compliance (`a2_estado_atual.regime`; risk-analysis reference §4).

## Risk judgement

**Barrier erosion demonstrated; risk tolerability not determined.**

The conventional design/current frequency pair is `motores.conventional.{projeto,atual}.evento_topo_por_ano`, with ratio `motores.conventional.razao`. The fuzzy pair and ratio are `motores.fuzzy.{projeto,atual}.evento_topo_por_ano` and `.razao`; its unchanged labels do not negate erosion. Exposure is declared in `motores.janela_de_exposicao_anos`; T1 dominates the calculated current contribution (`motores.conventional.atual.pathways[0]`).

These are model outputs, not validated residual-risk estimates: shared actuators, the B2 detector mismatch, human-PFD assumptions and invalidated effectiveness limit their interpretation. The supplied diagram uses direct inputs with zero MTTF; current barrier inputs come from reliability-derived PFDs, not an MTTF conversion (`diagrams/BT-REATOR.txt`; `motores.pfd_atual`; `premissas_do_modelo`).

Consequence frequency, severity, receptors and approved acceptance criteria are absent. The declared inventory-control loss following protective action is a separate secondary consequence, not an observed event here (`a1_base_de_projeto.declarado.barreiras.B1.efeito_colateral`; risk-analysis reference §3).

**Urgency: immediate escalation; action required.** Rising pressure, projected proximity to protection thresholds and invalidated windows justify applying standing abnormal/emergency procedures without waiting for uncertainty resolution. Confidence is moderate in this operational conclusion, but low in quantitative residual risk (`a2_estado_atual.margem.PIT-7001`; `envelope`; SKILL.md, Safety limits).

## Recommendation

**Immediate containment:** Operations should assess and control the excursion under approved procedures now, without waiting for B1 demand or further analysis. Obtain independent pressure confirmation without delaying response; verify protection availability and capture each barrier’s own demand/action evidence. Do not improvise setpoint, bypass or valve changes (SKILL.md, Safety limits; `a3_cruzamentos[4].lacunas`).

**Restoration:** Instrumentation and maintenance should repair and functionally test the failed channel and affected protection chain, resolve proof-test records, and establish an accountable repair deadline. Operations/training should verify current response capability and renew competence evidence (`a2_estado_atual.ordens_servico`; risk-analysis reference §§2,8).

**Definitive solution:** Process safety and engineering should revalidate current-condition windows, correct the B2 detection model, assess dependent protection and threat removal, and review inventory-control consequences before approving changes. Undertake a separate formal investigation of recurring integrity and assurance weaknesses (`envelope`; `a3_cruzamentos[5,7]`; risk-analysis reference §§4–6).

**Suggested owner / deadline:** Shift Operations lead immediately; maintenance, instrumentation and process-safety leads before claiming restored protection. Authorised action planning must address shared-actuator failure, loss of inventory control and testing/maintenance exposure (`a1_base_de_projeto.declarado.independencia`; design basis §4; SKILL.md B5).

**Expected return / leading indicator:** A controlled pressure trajectory with verified dynamic margin, demonstrated channel agreement, successful functional tests and traceable closure of overdue assurance tasks—not merely alarm clearance (`a2_estado_atual.margem`; `a2_estado_atual.ordens_servico`; risk-analysis reference §8).

**Closure criteria:** Keep open until the condition is controlled, protection restored and tested, temporary configurations resolved, windows revalidated, residual risk reassessed and remaining actions assigned (SKILL.md B5, Closure gate).

**Residual risk / accepting authority:** Undetermined; acceptance belongs to the facility’s designated competent authority, whose identity is not supplied (risk-analysis reference §3).

**Human decision:** pending.

## Evidence and assumptions

- **[demonstrated]** New HI crossing and recorded undemanded B1 at `identidade.ts`: `identidade.gatilho`; `a2_estado_atual.demandas.B1`.
- **[corroborated]** Known channel degradation: failure/maintenance records and computed freezing statistics converge (`a2_estado_atual.canais`; `.ordens_servico`; `.grupo_votado`).
- **[demonstrated]** Declared envelope invalidated: `envelope.invalidada`; design basis §7.
- **[inferred]** Feed-loss pressure scenario fits the observations; root cause remains unproven (`a2_estado_atual.margem.FIT-1001`; `envelope`; diagram).
- **[undetermined]** Current human success probability, independent protection credit and tolerability: `premissas_do_modelo`; `a1_base_de_projeto.declarado.independencia`; missing consequence/acceptance basis.
- **[undetermined]** All conclusions use only the frozen recovery scope in `a2_estado_atual.regra_de_recuperacao`; no subsequent event or intervention outcome is assumed.