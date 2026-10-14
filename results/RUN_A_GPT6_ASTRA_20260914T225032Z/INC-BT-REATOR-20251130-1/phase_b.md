# Escalate immediately to Operations to assess the recurring low-pressure alarm and protection outside its validated operating basis (`identidade.gatilho`; `envelope.invalidada`).

## Fact

This trigger adds a **new active LO alarm**, not a high-pressure demand or demonstrated frequency-criterion breach. Its measured value, crossed limit and first instant are `identidade.gatilho[0].{valor,limite,ts}`; duration and current state are `a2_estado_atual.alarmes_ativos[0].{ativo_ha_min,estado}`. Earlier LO episodes had cleared (`a2_estado_atual.alarmes_normalizados`).

The analysis is frozen at `identidade.ts`, over `identidade.janela_de` onward. Pressure units are `a2_estado_atual.margem.PIT-7001.unidade`; the recorded operating mode and changed settings are in `a2_estado_atual.regime.mudanca.detalhe`. Pair the pressure reading with the **computed falling trend**, its window and sample count in `envelope.degraus[0]`; the alarm-local rate is absent.

The crossing is supported by the agreeing channels, despite the known divergent channel (`a2_estado_atual.grupo_votado.concordancia_no_ultimo_instante`). Phase A is accepted as closed, with decision-bearing limitations: independent pressure verification, short-window dynamics, current response windows, configuration/clock reconciliation, document approval/version, bypass/test/isolation status, and consequence/tolerability evidence remain unverified. Instrument quality flags, saturation, overrides and clock synchronisation are not supplied; agreement alone does not settle these gaps (C5; `references/risk-analysis-reference.md`, §§2–3).

## Scenario and mechanism

**Declared scenario:** loss of stream feed → B1 automatic interlock and B2 backup manual action → loss of reactor control → mitigation and receptor-specific consequences **not demonstrated**. The SIS is a separately declared downstream automated layer, not evidence that either upstream barrier acted (`motores.diagrama`; design basis §§3–5).

**Supported erosion chain:** unrepaired pressure-channel failure and overdue maintenance/competence renewal → reduced detection redundancy and assumed human-performance deterioration → increased model PFDs → increased computed top-event frequency (`a2_estado_atual.canais`; `a2_estado_atual.ordens_servico`; `a1_base_de_projeto.barreiras`; `motores`).

Separately, the recorded operating-condition change without revalidation invalidates the applicability of the design response windows; its quantitative effect is not established by those PFD calculations (`envelope.gatilhos_de_invalidacao`; design basis §7).

The present LO alarm does **not** establish feed-loss initiation, impending high-pressure escalation or root cause. The changed regime and recurring alarms are temporally associated; B1 has no recorded demand (`a2_estado_atual.regime`; `a2_estado_atual.demandas.B1`).

## Analysis

### 1. Bowtie

For the references below, **B1** means `a1_base_de_projeto.barreiras[0]` and **B2** means `a1_base_de_projeto.barreiras[1]`.

| Barrier | State and interpretation | Quantitative evidence |
|---|---|---|
| B1 | **degraded**: detection redundancy is reduced, testing is overdue and effectiveness outside the validated condition is unverified. No failed demand is demonstrated. | Design → current: `B1.pfd_projeto` → `B1.pfd_atual`; whole-barrier multiplier: `B1.c2.multiplicador_barreira`; component multiplier: `B1.c2.componente_pior.multiplicador`; dominant final element and share: `B1.c2.elemento_dominante`. |
| B2 | **degraded**: competence renewal is overdue and the available human-response window is unknown. This does not demonstrate loss of all operator capability or failure on demand. Its numerical credit is provisional. | Design → current: `B2.pfd_projeto` → `B2.pfd_atual`; whole-barrier multiplier: `B2.c2.multiplicador_barreira`; component multiplier: `B2.c2.componente_pior.multiplicador`; dominant human element and share: `B2.c2.elemento_dominante`. |

These states follow the partial-performance evidence, not the fuzzy label; neither barrier can be called `healthy` within an invalidated envelope (SKILL.md, B3; C1–C4). Compression itself is **not measured**, and automatic speed alone does not prove effectiveness (`a3_cruzamentos[id=C3]`).

The voted group is **known degraded**. Channel B’s own low variability supports freezing near the former operating regime, rather than drift; the agreement of A and C identifies B as divergent. A shared error in A/C remains open (`a2_estado_atual.grupo_votado.{estatistica_por_canal,congelamento}`; C5). Exposure follows the repair backlog clock in `a3_cruzamentos[id=C4].relogio`; a committed repair deadline is absent.

B2 is demanded by valve command-versus-position discrepancy, **not this pressure alarm**. No B2 demand/response record or discrepancy signal is supplied. B1’s lack of demand settles neither B2 availability nor a hypothetical response (`a1_base_de_projeto.declarado.barreiras.B2`; `a2_estado_atual.demandas`).

Independent detection does not establish independent barriers: B1/B2 share final elements. Do not grant multiplied IPL/SIL credit. The model also assigns PT-007 to B2, contradicting the declared ZT-1001 detector; that mapping requires reconciliation (C6; `B2.componentes`; design basis §4).

### 2. Process

The lower post-change pressure regime and recurring LO alarms are supported by `a2_estado_atual.regime`. The pressure margin fields in `a2_estado_atual.margem.PIT-7001` must be read alongside `envelope.degraus[0]`: the available average is falling, not a demonstrated approach to the high-pressure trip. Larger distance from that trip does not establish safe operation.

C7 is incomplete despite its summary: rate/time fields are null, and the margin output omits some declared targets, notably the lower pressure target relevant to a falling trajectory. Only one rate window is supplied. Therefore current time-to-target and short-term acceleration are **not demonstrated**, and no projection is made (`a2_estado_atual.margem`; `a1_base_de_projeto.limiares`; `envelope.degraus`).

Envelope invalidation comes from the **unrevalidated operating change**, not excessive measured escalation. Failure to enter the plateau band proves neither its presence nor its disappearance. Threshold-change and voting/test-interval-change checks are not explicitly resolved in the supplied results (`envelope.gatilhos_de_invalidacao`; design basis §7).

### 3. Context

Maintenance evidence was selected by the opening-time cutoff in `a2_estado_atual.regra_de_recuperacao["work orders"]`; visible events use its `events` rule. The backlog and overdue activities justify integrity and organisational review, not operator blame or an unsupported non-compliance finding (`a2_estado_atual.ordens_servico`; risk-analysis reference §§4–5).

Resolve these contradictions before relying on quantitative credit:

- Test-clock versus calendar PFDs: retain both alternatives and their computed sensitivities in `a2_estado_atual.contradicoes[0].sensibilidade`.
- Training overdue duration: `B2.motivos` disagrees with `a2_estado_atual.ordens_servico[wo_id=WO-RUN_A-TRAIN].vencida_ha_dias`.
- Baseline PFD provenance: `B1.pfd_documento` and `B2.pfd_documento` disagree with their component-based baselines and the supplied diagram; the prose design basis also differs.

The overdue functional-test due date precedes the recorded B-channel failure; it cannot be claimed that execution on that date would have detected that later failure (`a2_estado_atual.ordens_servico`; `a2_estado_atual.canais`).

PHA, approved credit/acceptance criteria, MOC disposition and contemporaneous document revisions are absent. The supplied basis is usable as the declared reference, but its historical approval at `identidade.ts` is not demonstrated.

## Risk judgement

**Barrier erosion demonstrated; risk tolerability not determined.**

- **Conventional magnitude, computed:** `motores.conventional.projeto.evento_topo_por_ano` → `motores.conventional.atual.evento_topo_por_ano`; ratio `motores.conventional.razao`.
- **Fuzzy uncertainty propagation, computed:** `motores.fuzzy.projeto.evento_topo_por_ano` → `motores.fuzzy.atual.evento_topo_por_ano`; ratio `motores.fuzzy.razao`. Its label remains unchanged (`motores.fuzzy.{projeto,atual}.rotulo`), which does not negate erosion.
- T1 dominates current modeled contribution (`motores.conventional.atual.pathways`). Exposure is `motores.janela_de_exposicao_anos`. These are supplied direct-frequency/PFD calculations, not an MTTF-derived interpretation of the zero-MTTF diagram nodes (`motores`; `diagrams/BT-REATOR.txt`).

These outputs are diagram-model indicators, **not validated residual-risk estimates**: shared actuation, B2 mapping, clock discrepancies, assumed human PFD and invalidated windows limit their applicability. Consequence severity, receptors, conditional consequence frequencies and approved tolerability are absent; no frequency-acceptance breach can be asserted (risk-analysis reference §§2–3).

**Urgency: immediate; status: action required.** Current evidence supports prompt operational assessment, not a demonstrated high-pressure emergency. Apply standing emergency procedures immediately if field assessment identifies an unsafe envelope, trip approach or other safety-limit condition. Confidence is moderate in observed erosion and low in residual-risk quantification (SKILL.md, Safety limits; C1, C4, C7).

## Recommendation

**Immediate containment:** Operations should assess the LO alarm under approved procedures, obtain independent vessel-pressure confirmation, verify actual protection/configuration status and establish usable recent trends against all declared targets. Do not improvise valve action or lower alarm settings (C5, C7; design basis §§3–4).

**Restoration:** Instrumentation/Maintenance should prioritise channel repair and relevant end-to-end testing; Operations should restore demonstrated competence readiness. Reconcile test/training clocks, B2 detection mapping and baseline PFD provenance before restoring quantitative credit (C2–C6; risk-analysis reference §8).

**Definitive solution:** Process Engineering and Process Safety should perform MOC triage, revalidate response windows for the actual condition, review dependency-aware credit and assess the shared-actuator inventory-control consequence. Threat persistence remains unclassified; resolve it through the approved threat-removal study, not inference from this alarm (design basis §§4–7).

**Suggested owner / deadline:** Shift Operations—immediate assessment; Maintenance and Process Safety—prioritised restoration plan with explicit deadlines before relying on restored protection. Review repeated channel defects, backlog and unrevalidated change through a separate formal investigation (SKILL.md, B5).

**Action risks:** Feed isolation can defeat level control; testing/repair can temporarily reduce protection. Require authorised procedures, managed temporary changes and explicit monitoring/withdrawal conditions (C6; risk-analysis reference §§2, 6).

**Expected return / leading indicator:** Independently confirmed pressure, responsive and agreeing channels, completed functional tests, demonstrated operator readiness, resolved records and validated response margins—not merely alarm clearance (C4–C7; risk-analysis reference §8).

**Closure criteria:** Controlled condition, restored and tested functions, managed temporary changes, revalidated windows, reassessed residual risk and traceable open actions. None is established by this new alarm record (SKILL.md, B5).

**Residual risk / accepting authority:** Not determined; acceptance belongs to the facility’s designated competent authority, whose identity is absent from the package (risk-analysis reference §3).

**Human decision:** pending.

## Evidence and assumptions

- **[demonstrated]** Current crossing and previous cleared alarms: `identidade.gatilho`; `a2_estado_atual.alarmes_normalizados`.
- **[demonstrated]** Known channel degradation and unrevalidated operating change: `a2_estado_atual.canais`; `a2_estado_atual.regime`.
- **[inferred]** Frozen-channel failure mode: channel variability and old-regime comparison in `a2_estado_atual.grupo_votado`; its approximate onset is computed, not a recorded failure timestamp.
- **[undetermined]** A/C common cause, actual response windows, threat persistence and tolerability: C3, C5, C8; absent consequence/acceptance inputs.
- **[assumption]** Human PFD substitution, degraded voting model and default treatment of missing tests: `premissas_do_modelo`; none establishes field performance.
- **[refuted]** The LO alarm constitutes a B1 demand: `a2_estado_atual.alarmes_ativos[0].e_demanda`; `a2_estado_atual.demandas.B1`.