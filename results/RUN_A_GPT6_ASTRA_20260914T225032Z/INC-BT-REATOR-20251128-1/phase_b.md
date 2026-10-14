# Escalate immediately to Operations for a safe-operating decision: the changed operating condition has no revalidated barrier windows, while existing barrier degradation remains unresolved.

## Fact

This analysis is frozen at `identidade.ts`, for the reactor and pathway identified in `identidade`. **This trigger adds an operating-condition change and a low-pressure alarm; the detected channel failure already existed.** The recorded mode and change are in `a2_estado_atual.regime.mudanca.detalhe`; no subsequent revalidation is recorded in `a2_estado_atual.regime.revalidacao_registrada`.

The alarm crossing is reproducible from `identidade.gatilho[1].valor` against `.limite`; its first instant, duration and active state are in `a2_estado_atual.alarmes_ativos[0]`. The channel-discrepancy crossing is supported by `a2_estado_atual.discrepancia_canais[0]`. Neither establishes a high-pressure demand: `a2_estado_atual.demandas.B1.demandada` is false.

**Decision-limiting gaps:** current-window rates are absent (`a2_estado_atual.taxas`, `envelope.lacuna`); independent pressure confirmation remains outstanding (`a3_cruzamentos[4].lacunas`). Clock synchronisation, signal-quality flags, instrument range/saturation, overrides, bypass/test/isolation status, approved bowtie revision and risk criteria are not supplied. Thus the recorded crossings support analysis, but trajectory, absolute measurement accuracy and operating safety are not demonstrated. [SKILL.md, B1]

## Scenario and mechanism

**Declared scenario:** loss of stream feed → B1 automatic interlock → B2 backup manual action → loss of reactor control. The SIS is a separately declared downstream automated layer, not evidence that either upstream barrier succeeded. Consequence severity, receptors and credited mitigation beyond this ladder are absent. [`motores.diagrama`; `a1_base_de_projeto.declarado.escada_protecao`; design basis §§3–5]

**Supported erosion chain:** unrepaired pressure-channel failure and overdue assurance activities → reduced detection redundancy and uncertain human-response performance → calculated barrier PFD increases → increased diagram-model top-event frequency. Sources are `a2_estado_atual.canais`, `.ordens_servico`, `a1_base_de_projeto.barreiras[*].detalhe_componentes`, `premissas_do_modelo` and `motores`.

Separately, the recorded operating-condition change without revalidation invalidates reliance on the declared response windows. It does **not** establish window compression, a feed-loss threat, or the cause of the pressure alarm. [`a2_estado_atual.regime`; design basis §7; `envelope.lacuna`]

## Analysis

### 1. Bowtie

- **B1 — `degraded`.** Detection redundancy is reduced; failure of the complete function is not demonstrated, and no demand is recorded. Compare `a1_base_de_projeto.barreiras[0].pfd_projeto.valor` → `.pfd_atual.valor`, with both `.c2.componente_pior.multiplicador` and `.c2.multiplicador_barreira`. The dominant contribution remains XV-1001, including its share at `.c2.elemento_dominante.fracao_do_total`. Current-condition effectiveness is unverified, irrespective of automatic actuation speed. [`a2_estado_atual.demandas.B1`; design basis §7]
- **B2 — `degraded`.** Overdue competence renewal reduces assurance; neither failed-on-demand performance nor complete functional unavailability is demonstrated. Compare `a1_base_de_projeto.barreiras[1].pfd_projeto.valor` → `.pfd_atual.valor`, and both `.c2.componente_pior.multiplicador` and `.c2.multiplicador_barreira`. OP-B2 dominates at `.c2.elemento_dominante`; its own multiplier is `.detalhe_componentes[3].fator`. The human PFD adjustment is an **assumption**, not measured performance (`premissas_do_modelo.human_barrier_pfd_with_overdue_competence`). The actual response window and B2 demand outcome are not supplied; the pressure alarm is not B2’s trigger. [Design basis §§4–5]

PT-007 is **known degraded**, not hidden degraded. Channel B’s low variation and computed flat interval support freezing near the preceding regime, rather than drift; A and C identify B as the outlier, but cannot exclude their own common-cause error. The applicable exposure clock is the repair backlog, with no repair deadline supplied—not a presumed short repair horizon. [`a2_estado_atual.grupo_votado`; `a3_cruzamentos[3].relogio`; `a3_cruzamentos[4].lacunas`; `a2_estado_atual.ordens_servico[3]`]

**Joint IPL/SIL credit is not demonstrated.** The declared detection paths are independent, but final elements are shared. Moreover, the calculated B2 component list contains PT-007 rather than the declared ZT-1001 detection path. This mapping contradiction must be resolved; it must not be interpreted as proof of shared detection. [`a1_base_de_projeto.barreiras[1].componentes`; `.declarado.independencia`; design basis §4]

### 2. Process

Pressure value, units and distances must be read together with the **missing rate and time-to-target** in `a2_estado_atual.margem["PIT-7001"]`. Static distance from upper targets establishes neither recovery nor adequate response time. The low-pressure excursion also requires attention; the supplied margin block does not quantify every configured target, including the lower pressure limit. [`a1_base_de_projeto.limiares[0]`; `references/cross-checks.md`, C7]

The rate ladder is empty and the post-change regime is null. Therefore, no escalation rate, settled regime shift, compression factor or physical-balance explanation is supported. C1’s wording about a shift by “None” is not a measured shift. Nevertheless, the **recorded-change invalidation criterion already applies**; the other invalidation criteria cannot be verified from the supplied configuration history. [`a2_estado_atual.escada_de_taxas`; `.regime`; `a3_cruzamentos[0]`; design basis §7]

### 3. Context

Maintenance recovery includes orders opened by the frozen instant, with future closures and findings excluded (`a2_estado_atual.regra_de_recuperacao["work orders"]`). It shows prior repair/retest, an unresolved channel repair, overdue functional testing and overdue training—not proof of operator fault. [`a2_estado_atual.ordens_servico`; risk-analysis reference §5]

The supplied records leave material contradictions unresolved:

- Test-clock alternatives and their already-computed sensitivity remain in `a2_estado_atual.contradicoes[0]`; the calendar-implied test date is an assumption.
- Training overdue duration in `a1_base_de_projeto.barreiras[1].motivos[1]` differs from `a2_estado_atual.ordens_servico[2].vencida_ha_dias`.
- `.pfd_documento`, `.pfd_projeto`, the supplied diagram and design-basis declarations do not consistently identify the same design PFDs. [`a1_base_de_projeto.barreiras`; `diagrams/BT-REATOR.txt`; design basis §4]

Approved historical revisions, PHA/LOPA, MOC disposition and operational-readiness records are absent. The supplied design basis is used as instructed, but its approval/applicability at `identidade.ts` is not established. [Design-basis provenance; risk-analysis reference §§2, 4]

## Risk judgement

**Barrier erosion demonstrated; risk tolerability not determined.**

The computed conventional comparison is `motores.conventional.projeto.evento_topo_por_ano` → `.atual.evento_topo_por_ano`, with ratio `motores.conventional.razao`. The fuzzy comparison is the corresponding `motores.fuzzy` pair and `.razao`; its unchanged label does not negate erosion. Use conventional output for diagram-model magnitude and fuzzy output for linguistic uncertainty, over `motores.janela_de_exposicao_anos`. These inputs follow the calculated-PFD/direct-frequency path, not an MTTF conversion. [`motores`; `diagrams/BT-REATOR.txt`; SKILL.md, engine interpretation]

T1 dominates the current model contribution (`motores.conventional.atual.pathways[0].contribuicao_pct`). However, shared actuation, detector mapping, disputed clocks and unvalidated windows prevent treating that magnitude as demonstrated residual-risk credit. No frequency attention threshold, consequence model, receptor specification or approved tolerability criterion is supplied. [Risk-analysis reference §§2–3]

**Urgency: immediate; status: action_required.** The changed condition lacks demonstrated protection windows and the available response time is unknown. An imminent high-pressure event is not established. Confidence in quantitative residual risk is **low**, while the need to resolve the documented degradation is supported. [`a2_estado_atual.regime`; `.margem`; `.ordens_servico`; SKILL.md, B4]

## Recommendation

**Immediate containment:** Operations should assess the alarm and changed operating condition now under standing procedures, obtain the independent pressure check identified in C5, and establish time-resolved trends. If field conditions meet the skill’s emergency triggers, apply standing emergency procedures without waiting for analytical certainty. Do not improvise setpoint, voting, bypass or valve changes. [SKILL.md, Safety limits; `a3_cruzamentos[4].lacunas`]

**Restoration:** Instrumentation/Maintenance should prioritise the channel repair and authorised end-to-end functional testing, reconcile test records and actual voting configuration, and restore competence assurance. Verify B2’s discrepancy indication and demand recording. Testing and shared-valve intervention require control of temporary protection loss and the declared inventory-control side effect. [`a2_estado_atual.ordens_servico`; design basis §4; risk-analysis reference §§2, 6]

**Definitive solution:** Process Safety and Engineering should resolve the detector/PFD mapping, review dependent-barrier credit, and revalidate windows for the changed condition through approved change review. Review the repeated channel findings and overdue assurance backlog for a separate systemic investigation; organisational cause is not yet demonstrated. Threat persistence requires the declared removal test. [`a3_cruzamentos[5]`, `[7]`; risk-analysis reference §§4–6]

**Suggested owner / deadline:** Shift authority immediately for the operating decision; Maintenance, Training and Process Safety for restoration and documented deadlines before renewed reliance on the affected protection. [SKILL.md, B5]

**Expected return / leading indicator:** Independently confirmed pressure, restored channel agreement, passing functional tests, reconciled assurance dates and validated current-condition response windows; none is yet observed. [Risk-analysis reference §8]

**Closure criteria:** Controlled condition, restored and tested functions, managed temporary changes, revalidated windows, reassessed residual risk and traceable remaining actions—not merely alarm clearance. [SKILL.md, Closure gate]

**Residual risk / accepting authority:** Undetermined; acceptance belongs to the facility’s designated competent authority, whose identity is not supplied. **Human decision: pending.** [SKILL.md, B5]

## Evidence and assumptions

- **Demonstrated:** recorded change without revalidation, active alarm and unrepaired channel failure at the frozen instant. [`a2_estado_atual.regime`, `.alarmes_ativos`, `.canais`]
- **Inferred:** frozen-channel failure mode from channel variability and flat-regime evidence; internal physical cause unresolved. [`a2_estado_atual.grupo_votado`]
- **Assumption:** human PFD uplift, degraded voting model and treatment of missing test records. [`premissas_do_modelo`]
- **Undetermined:** current dynamic margin, agreeing-channel common cause, approved joint credit, consequence severity and tolerability. [`envelope`; `a3_cruzamentos[4]`, `[5]`; risk-analysis reference §§2–3]
- **Refuted:** interpreting the pressure alarm as a demonstrated B1 or B2 demand. [`a2_estado_atual.demandas.B1`; `a1_base_de_projeto.declarado.barreiras.B2.gatilho`]