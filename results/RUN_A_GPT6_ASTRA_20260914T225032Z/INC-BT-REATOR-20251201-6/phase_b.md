# Escalate immediately to Operations and apply standing emergency procedures: pressure continues rising after the SIS trip, with no demonstrated downstream arresting layer.

## Fact

This analysis is frozen at `identidade.ts`, over `identidade.janela_de → identidade.ts`, for the reactor pathway identified in `identidade`. The `end_of_record` trigger establishes the endpoint of available observation—not recovery or a new equipment failure; escalation remains present after the recorded SIS action (`identidade.gatilho`, `a2_estado_atual.demandas.SIS`).

Pressure value, units, crossed alarms, SIS exceedance and current rate are recorded together in `a2_estado_atual.margem.PIT-7001`; the rate calculation and sampling window are in `a2_estado_atual.taxas.PIT-7001`. Alarm onset, duration and active status are in `a2_estado_atual.alarmes_ativos`. The latest recorded operating condition is `a2_estado_atual.regime.mudanca`, not demonstrated equivalent to the validated base case.

Pressure crossing is supported by the agreeing channels and recorded demand, but measurement assurance is incomplete: B is frozen; common error in A/C remains unresolved; and the logic-event timestamp precedes the first sampled crossing (`a2_estado_atual.grupo_votado`, `a2_estado_atual.demandas.B1.instantes`). Clock synchronisation, instrument range/quality flags, overrides, bypass/test/isolation status, bowtie revision/hash and approved frequency/tolerability criteria are **not demonstrated** in the supplied package. These gaps qualify interpretation but do not negate the recorded excursion or justify delaying escalation (SKILL.md, “Safety limits”).

## Scenario and mechanism

**Loss of stream 1 feed → B1 automatic interlock / B2 manual backup → loss of reactor control → downstream SIS and unverified further protection → possible pressure-related containment failure.** The threat and top event come from `diagrams/BT-REATOR.txt`; continuing feed deprivation is supported by `a2_estado_atual.margem.FIT-1001`. Containment failure is a plausible scenario, not an observed consequence; hazardous inventory, severity and exposed receptors are absent (`a3_cruzamentos[id=C5].lacunas`; risk-analysis-reference §1).

The supported quantitative chain is:

- Recorded UZ-007 non-command on demand → B1 function unavailable → current B1 PFD and dominant contribution (`a2_estado_atual.demandas.B1.decidir`; `a1_base_de_projeto.barreiras[0].pfd_atual`, `.c2`).
- Unrepaired sensor degradation and overdue competence renewal → modelled barrier erosion, with human performance additionally outside its validated window (`a1_base_de_projeto.barreiras[1].motivos`; `premissas_do_modelo`; `a3_cruzamentos[id=C3]`).
- Current PFD inputs → increased modelled top-event frequency and dominant T1 contribution (`motores.pfd_atual`, `motores.conventional.atual.pathways`).

The operating-condition change and compressed trajectory support envelope invalidation, not a proven root cause of the excursion or logic failure (`envelope.gatilhos_de_invalidacao`; risk-analysis-reference §7).

## Analysis

### 1. Bowtie

| Barrier | State and interpretation |
|---|---|
| **B1** | **critical — failed on demand.** Detection vote was satisfied; UZ-007 recorded no commanded outputs; the expected feed/purge signature was absent in B1’s own demand window; the success criterion was not met. The record implicates the logic/output-command function, not demonstrated mechanical failure of the valves. No command means their ability to respond remains untested by this episode (`a2_estado_atual.demandas.B1.{detectar,decidir,agir,desfecho}`). |
| **B2** | **degraded; demand and outcome undetermined.** Competence renewal is overdue and the validated human-response margin does not apply. HIHI is not its trigger: ZT-1001 discrepancy indication is absent, and B1 recorded no command. Do not label B2 failed on demand or credit it as available protection (`a2_estado_atual.demandas.B2`; `a3_cruzamentos[id=C3]`; design basis §§4–5). |

For **each barrier**, design → current PFD is in `a1_base_de_projeto.barreiras[0/1].{pfd_projeto,pfd_atual}`; whole-barrier and worst-component multipliers are separately in `.c2.{multiplicador_barreira,componente_pior.multiplicador}`. UZ-007 dominates B1; OP-B2 dominates B2, with shares recorded in `.c2.elemento_dominante.fracao_do_total`. The human contribution is a model assumption, not measured competence (`premissas_do_modelo.human_barrier_pfd_with_overdue_competence`).

PT-007 is **known degraded**, not hidden degraded. B’s own low variability supports freezing at the previous regime; A/C agreement identifies B as divergent. Exposure follows the unresolved repair backlog, with no scheduled completion demonstrated—not an assumed short repair horizon (`a2_estado_atual.grupo_votado`; `a3_cruzamentos[id=C4].relogio`; WO-RUN_A-CH-B).

B1/B2 have declared independent detection but shared final elements: joint IPL/SIL credit is **not demonstrated**. The computational B2 component list nevertheless includes PT-007 rather than its declared ZT-1001 detection; this mismatch requires reconciliation before quantitative credit (`a1_base_de_projeto.barreiras[1].componentes`; `.declarado.independencia`; design basis §4).

The SIS is downstream of the T1 preventive barriers. Its recorded trip does not establish B1 actuation or successful excursion arrest (`a2_estado_atual.demandas.SIS`).

### 2. Process

The episode-wide average masks faster escalation during the decision window. The threshold-to-threshold and post-SIS rates invalidate reliance on base-case response windows; the design plateau was not reproduced (`envelope.degraus`, `.plato_medido`, `.invalidada`).

Read current pressure and rate alongside **both** crossed-alarm exceedances and target distances in `a2_estado_atual.margem.PIT-7001.{valor,taxa_por_min,limiares_ja_cruzados,alvos_declarados}`. The model-limit projection is the **computed** `.alvos_declarados[1].tempo_min`, using the recent rate window in `a2_estado_atual.taxas.PIT-7001.entradas`; it is not guaranteed remaining response time or a certified vessel limit (design basis §3; cross-checks §C7).

Automatic response speed would not itself exhaust the measured window, but B1 failed to command. B2’s base-case tolerable delay exceeds the measured window; that does not prove every possible manual response impossible, but invalidates its design performance credit. Its actual demand-anchored window is unobservable (`a3_cruzamentos[id=C3]`; `a2_estado_atual.demandas.B2`).

Feed deprivation and continued post-SIS escalation are consistent with an ongoing threat; persistent-versus-removable classification remains unresolved without the declared removal test (`a3_cruzamentos[id=C8]`).

### 3. Context

Open corrective work, overdue testing/training and an operating change without recorded window revalidation justify integrity and management-of-change review—not operator blame or a finding of procedural non-compliance (`a2_estado_atual.ordens_servico`, `.regime`; risk-analysis-reference §§4–5). Work orders were recovered by the frozen opening/closure rules in `a2_estado_atual.regra_de_recuperacao["work orders"]`.

Reconcile these unresolved source issues before restoring credit:

- PT-007 model clock versus maintenance calendar; the supplied sensitivity leaves B1 unavailable under either reading (`a2_estado_atual.contradicoes[0].sensibilidade`).
- Training lateness in B2’s model narrative versus WO-RUN_A-TRAIN (`a1_base_de_projeto.barreiras[1].motivos`; `a2_estado_atual.ordens_servico`).
- Asset-sum PFDs, `.pfd_documento`, supplied diagram values and design-basis declarations (`a1_base_de_projeto.barreiras`; `diagrams/BT-REATOR.txt`; design basis §4).

Threshold-change and configured voting/test-interval histories are not supplied for complete verification of all design-basis §7 invalidation criteria; the already-supported invalidations remain sufficient.

## Risk judgement

**Barrier erosion demonstrated; risk tolerability not determined.**

The computed conventional design/current pair is `motores.conventional.{projeto,atual}.evento_topo_por_ano`, with ratio `motores.conventional.razao`; use it for **modelled magnitude**. The fuzzy pair and ratio are `motores.fuzzy.{projeto,atual}.evento_topo_por_ano` and `.razao`, with linguistic propagation in the corresponding `.rotulo` fields—not a risk category or cross-check on conventional magnitude (`motores.nota`).

Exposure is declared in `motores.janela_de_exposicao_anos`. Barrier inputs follow the current-PFD path, not an MTTF conversion; diagram initiating inputs are direct entries (`motores.pfd_atual`; `diagrams/BT-REATOR.txt`; SKILL.md, “Reading the engine’s numbers”).

These are conditional diagram calculations, **not validated residual-risk estimates**, because dependency, B2 mapping, human-window validity and model assumptions remain unresolved. Consequence frequency/severity, receptor exposure and approved acceptance criteria are absent; no frequency-criterion breach can be established from this endpoint trigger alone (risk-analysis-reference §§2–3).

**Urgency: emergency; status: action required.** B1 failure, continued post-SIS rise and the computed target horizon support escalation despite uncertain downstream protection. Confidence is strong in B1’s observed failure, but low in quantitative residual-risk adequacy (`a2_estado_atual.demandas`; `a3_cruzamentos[id=C5]`; SKILL.md, “Safety limits”).

## Recommendation

**Immediate containment:** Operations should apply standing emergency procedures now, without waiting for model reconciliation. Obtain independent pressure confirmation and verify downstream relief/design pressure without delaying response; review control-room evidence for B2 demand (`a3_cruzamentos[id=C5].lacunas`; SKILL.md, “Safety limits”).

**Restoration:** Instrumentation/maintenance should restore and functionally test UZ-007, the voted group and the complete commanded final-element chain; verify SIS effectiveness and B2 indication/readiness before reinstating credit (`a2_estado_atual.demandas`; risk-analysis-reference §§2, 8).

**Definitive solution:** Process safety and engineering should prioritise hazard/threat reduction, observable backup initiation and demonstrably effective protection under the changed condition; reconcile dependencies and revalidate response windows. Review loss of level control caused by shared feed-valve action before selecting interventions; it is a declared secondary consequence, not observed recovery (`a3_cruzamentos[id=C6]`; design basis §§4–7). Investigate the combined backlog, overdue assurance and unrevalidated change separately as potential systemic failure (risk-analysis-reference §§4–6).

**Suggested owner / deadline:** Shift authority immediately; maintenance, controls and process safety before return-to-service credit. Manage intervention transients, isolation/bypass exposure and inventory-control coupling through authorised procedures (SKILL.md §B5; risk-analysis-reference §§6, 8).

**Expected return / leading indicator:** Demonstrated pressure arrest and stable control over a justified window; successful demand-to-action tests, restored channel agreement and traceable repair/test completion—not merely alarm clearance (risk-analysis-reference §8).

**Closure criteria:** Condition controlled; functions restored **and tested**; temporary changes resolved; current-condition windows revalidated; residual risk reassessed and open actions traceable. None is established by `end_of_record` (SKILL.md, “Closure gate”).

**Residual risk / accepting authority:** Undetermined; acceptance belongs to the facility’s designated authority, whose identity is absent. **Human decision: pending** (SKILL.md §B5).

## Evidence and assumptions

- **[demonstrated]** B1 failed its declared demand success criterion: `a2_estado_atual.demandas.B1`.
- **[demonstrated]** Current dynamics invalidate base-case windows: `envelope`; design basis §§2, 5, 7.
- **[inferred]** Feed-loss mechanism is consistent with the pressure excursion; root cause is not established: `a2_estado_atual.margem.FIT-1001`; `diagrams/BT-REATOR.txt`.
- **[undetermined]** B2 demand, common error in A/C and downstream arresting protection: `a3_cruzamentos[id=C5].lacunas`.
- **[undetermined]** Approved quantitative credit and tolerability: `premissas_do_modelo`, `a2_estado_atual.contradicoes`; risk-analysis-reference §§2–3.