# Escalate immediately to operations and apply standing emergency procedures: B1’s logic is unavailable while pressure rises toward the SIS trip (`a2_estado_atual.demandas.B1`; SKILL.md, Safety limits).

## Fact

This trigger adds a recorded UZ-007 failure with no outputs commanded, its corrective work order, and a reproducible HIHI crossing—not merely further probabilistic degradation (`identidade.gatilho`; `a2_estado_atual.demandas.B1.decidir`).

The assessment is frozen at `identidade.ts`, over the window beginning `identidade.janela_de`. Pressure value, units, crossed thresholds and recent rate are in `a2_estado_atual.margem["PIT-7001"]`; alarm onset, duration and rate-calculation window are in `a2_estado_atual.alarmes_ativos`. The recorded operating condition is `a2_estado_atual.regime.mudanca`, not demonstrated equivalent to the validated base case.

The agreeing channels reproduce the demand vote, but the logic-event timestamp precedes the first sampled crossing; exact synchronisation remains unverified. No populated post-demand actuation signature is available, and the process success criterion remains unresolved (`a2_estado_atual.demandas.B1.{instantes,detectar,agir,desfecho}`).

## Scenario and mechanism

**Loss of stream 1 feed → B1 automatic interlock / B2 manual backup → loss of reactor control → downstream SIS layer → consequences and receptors not specified.** The SIS is a separate downstream layer, not evidence of B1 action; no SIS demand or outcome is established at this instant (`diagrams/BT-REATOR.txt`; design basis §§3–5; `a2_estado_atual.demandas.B1.desfecho`).

Low feed flow and its rate support the initiating-threat interpretation; UZ-007’s recorded failure removes automatic command execution. Reliability assumptions translate that condition into the current B1 PFD, which propagates through the supplied engines. This supports barrier erosion, not a demonstrated root cause of the excursion or a quantified consequence frequency (`a2_estado_atual.margem["FIT-1001"]`; `a2_estado_atual.demandas.B1.decidir`; `premissas_do_modelo.single_channel_item_with_known_failure`; `motores`).

## Analysis

### 1. Bowtie

- **B1 — `critical` on availability evidence:** the record identifies unavailable logic and absent commands. This classification does **not** settle the still-open pressure-reversal outcome or demonstrate failed valves. Detection is supported by the sampled vote; final-element response remains unverified (`a2_estado_atual.demandas.B1`; SKILL.md, B3).
- **B2 — `degraded`:** competence renewal is overdue and current-condition effectiveness is unverified. Its demand and outcome are undetermined: HIHI is not its trigger, ZT-1001 is absent, and B1 issued no command. Do not assume automatic escalation to this backup or classify an operator failure (`a2_estado_atual.ordens_servico[2]`; `a2_estado_atual.demandas.B2`; design basis §4).

PFD design → current pairs are `a1_base_de_projeto.barreiras[0].{pfd_projeto,pfd_atual}` and `[1].{pfd_projeto,pfd_atual}`. Both whole-barrier and worst-component multipliers, with dominant-element shares, are in each entry’s `c2`: UZ-007 dominates B1; OP-B2 dominates B2 despite PT-007 having its largest component multiplier. These are model calculations, including an assumed human PFD—not demonstrated current performance (`premissas_do_modelo`; `a1_base_de_projeto.barreiras`).

PT-007 is **known degraded**, not hidden degraded. Channel B’s own variability supports freezing near the former regime, rather than drift; agreement identifies B as the outlier but cannot exclude common error in A/C. Exposure follows the repair backlog, with no repair deadline supplied (`a2_estado_atual.grupo_votado`; `a3_cruzamentos[3].relogio`; `a2_estado_atual.ordens_servico[3]`).

Automatic response time does not compensate for unavailable logic. The actual demand-to-SIS window and compression remain unmeasured; B2’s base-case delay allowance cannot be credited under the invalidated envelope (`a3_cruzamentos[2]`; `envelope.invalidada`; design basis §§5–7).

B1/B2 share final elements, defeating independent joint credit. Their declared independent detection also conflicts with the asset decomposition assigning PT-007 to B2; reconcile this before IPL/SIL assessment. B3/B4 values in the engine do not demonstrate their availability or protection against T1 (`a3_cruzamentos[5].comparado`; `a1_base_de_projeto.barreiras[1].componentes`; `motores.pfd_atual`; risk-analysis reference §2).

### 2. Process

The episode-wide average masks faster escalation after the valley and through the alarm interval. Both the rate criterion and the recorded operating-condition change invalidate base-case windows; the plateau has not yet been traversed, so its disappearance is not established (`envelope.degraus`; `envelope.gatilhos_de_invalidacao`).

Read pressure exceedances alongside `a2_estado_atual.margem["PIT-7001"].taxa_por_min`; for **each** downstream target, read `.alvos_declarados[].distancia` together with `.tempo_min`. Those times are computed trend projections, not measured response windows or guaranteed time remaining (`a2_estado_atual.margem["PIT-7001"].nota`; cross-checks C3/C7).

Feed remains low without demonstrated recovery; formal persistent/removable classification is still unavailable. Neither stable operation nor recovery after a barrier action can be inferred (`a3_cruzamentos[7]`; design basis §6).

### 3. Context

The closed Phase A gaps carry forward: pressure common cause, B2 demand observability and threat classification. Additional verification is needed for clock synchronisation, instrument quality/range/override status, current bypass/test/isolation status, bowtie revision, approved acceptance criteria and SIS availability; these are not established by the supplied fields (`a3_cruzamentos[4].lacunas`; `a3_cruzamentos[7].lacuna`; `identidade`; SKILL.md, B1/B3).

Preserve the conflicting PT-007 maintenance clocks and supplied sensitivity. Training overdue duration also differs between the work order and model explanation; PFD document fields differ from the supplied diagram/design basis. None should be silently reconciled (`a2_estado_atual.contradicoes[0]`; `a2_estado_atual.ordens_servico[2]`; `a1_base_de_projeto.barreiras[1].motivos`; `a1_base_de_projeto.barreiras[].pfd_documento`; design basis §4).

Backlog, overdue assurance activities and an operating change without recorded revalidation justify integrity/MOC triage and investigation of organisational controls—not operator blame or an unsupported compliance finding. The overdue sensor test predates the recorded channel-B failure, so its timely execution cannot be claimed to have detected that later failure (`a2_estado_atual.ordens_servico`; `a2_estado_atual.canais[1]`; `a2_estado_atual.regime`; risk-analysis reference §§4–5).

## Risk judgement

**Barrier erosion demonstrated; risk tolerability not determined.** Consequence severity, receptors, conditional consequence probabilities and approved tolerability criteria are absent; the supplied triggers also provide no numerical frequency acceptance threshold (SKILL.md, B4; `identidade.gatilho`; `motores`).

- **Conventional magnitude:** cite `motores.conventional.projeto.evento_topo_por_ano` → `motores.conventional.atual.evento_topo_por_ano`, with `motores.conventional.razao`.
- **Fuzzy uncertainty propagation:** cite `motores.fuzzy.projeto` → `motores.fuzzy.atual`, with `motores.fuzzy.razao`; labels qualify frequency, not risk.
- **Exposure and dominant pathway:** `motores.janela_de_exposicao_anos` and `motores.conventional.atual.pathways`.

These are computed diagram outputs, not validated residual-risk estimates: shared actuation, inconsistent B2 detection mapping and invalidated human-performance windows undermine quantitative credit. The supplied diagram uses direct node values rather than MTTF-derived values; current barrier inputs are `motores.pfd_atual` (`diagrams/BT-REATOR.txt`; `motores.nota`; risk-analysis reference §§2–3).

**Urgency: emergency; status: action_required.** Rising pressure, projected approach to the last declared automated layer and unavailable primary logic justify immediate escalation despite uncertain consequences. Confidence is limited for quantitative risk, but the recorded functional loss supports conservative action (`a2_estado_atual.margem["PIT-7001"]`; `a2_estado_atual.demandas.B1.decidir`; SKILL.md, Safety limits).

## Recommendation

**Immediate containment:** Operations should apply standing emergency procedures now, verify remaining protection and obtain independent pressure confirmation without delaying response. Do not improvise valve manoeuvres, setpoints or bypasses; feed closure has a declared inventory-control/low-level shutdown consequence (`a3_cruzamentos[4–5]`; SKILL.md, Safety limits).

**Restoration:** Instrumentation and maintenance should resolve UZ-007 and channel B, reconcile assurance clocks, and test detection–logic–final-element function under authorised safe conditions. Resolve B2 demand visibility and competence assurance before claiming credit (`a2_estado_atual.ordens_servico`; risk-analysis reference §§2, 8).

**Definitive solution:** Process safety and engineering should prioritise threat reduction, observable backup demand, dependency review and window revalidation; separately investigate backlog, assurance and change-control weaknesses. Evaluate intervention transients and shared-actuator side effects through the applicable change process (`a3_cruzamentos[5,7]`; risk-analysis reference §§4–6).

**Suggested owner / deadline:** Shift manager immediately; maintenance, engineering and process safety before return-to-service approval. **Expected return / leading indicators:** controlled pressure trajectory, verified command/position response, restored channel agreement and traceable assurance completion (SKILL.md, B5; risk-analysis reference §8).

**Closure criteria:** Controlled condition, restored and tested functions, managed temporary changes, revalidated operating windows, reassessed residual risk and traceable open items—not merely pressure returning to band (SKILL.md, Closure gate).

**Residual risk / accepting authority:** Undetermined; acceptance belongs to the facility’s designated competent authority, whose identity is absent. **Human decision: pending** (SKILL.md, B5).

## Evidence and assumptions

- **[demonstrated]** New logic non-execution and sampled demand: `identidade.gatilho`; `a2_estado_atual.demandas.B1`.
- **[corroborated]** Recorded channel-B degradation and frozen signal behaviour: `a2_estado_atual.canais`; `a2_estado_atual.grupo_votado`.
- **[inferred]** Feed-loss scenario mechanism, not root cause: `a2_estado_atual.margem["FIT-1001"]`; design basis §§4–6.
- **[undetermined]** B1 process outcome, B2 demand, consequence risk and quantitative credit: `a2_estado_atual.demandas`; `a3_cruzamentos[4–5]`; `premissas_do_modelo`.
- **Scope:** Only supplied material through `identidade.ts`; recovery uses `a2_estado_atual.regra_de_recuperacao`. No later outcome or external verification is assumed.