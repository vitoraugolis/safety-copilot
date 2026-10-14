# Escalate the newly recorded pressure-channel failure for immediate operational review and restoration; continued-operation risk acceptance is not demonstrated.

## Fact

This trigger adds a detected, unrepaired PT-007.B failure and its corrective work order to the existing test and training backlog; it is a **record-triggered deterioration**, not a demonstrated process excursion or frequency-criterion crossing (`identidade.gatilho`, `a2_estado_atual.canais`, `a2_estado_atual.ordens_servico`).

The assessment is frozen at `identidade.ts`, over `identidade.janela_de` onward, using `identidade.banco`. Failure onset, detection and unresolved repair status are recorded in `a2_estado_atual.canais[channel_id=PT-007.B]`; the exposure clock is `a3_cruzamentos[id=C4].relogio`. No active alarm or B1 demand is recorded (`a2_estado_atual.alarmes_ativos`, `a2_estado_atual.demandas.B1`).

**Pre-inference limitations:** units are supplied in `a2_estado_atual.margem`; actual operating mode, clock synchronisation, signal-quality flags, instrument ranges, overrides, bypass/test/isolation status, graph revision and approved acceptance criteria are not supplied. The absence of a recorded operating-condition change does not confirm the design operating mode (`a2_estado_atual.regime`; design basis §2; SKILL.md, Phase B).

The failure record is reproducible, but the analogue readings do not corroborate its stated discrepancy: all channel pairs agree, no majority outlier is identified, and the channel statistics do not demonstrate freezing. The failure mechanism remains undetermined; agreement does not establish functional availability (`a2_estado_atual.grupo_votado`, `a2_estado_atual.discrepancia_canais`, `a2_estado_atual.canais`).

## Scenario and mechanism

**Declared scenario:** loss of stream 1 feed → B1 automatic intervention, followed by B2 on command–position discrepancy → loss of reactor control → downstream protection → consequence/receptor **not demonstrated**. The SIS is the last declared automated layer, not evidence that B1 succeeded; no consequence model or mitigating performance beyond it is supplied (`diagrams/BT-REATOR.txt`; design basis §§3–5).

**Supported quantitative chain:** recorded channel failure → modelled degraded voting and sensor PFD → calculated B1 PFD; overdue competence renewal → assumed human-component PFD → calculated B2 PFD → engine-reported top-event frequency. Sources are `a2_estado_atual.canais`, `premissas_do_modelo`, `a1_base_de_projeto.barreiras` and `motores`. These support barrier erosion, not root cause or consequence frequency.

For compact citations below, **B1/B2** denote the corresponding entries in `a1_base_de_projeto.barreiras[id=…]`.

## Analysis

### 1. Bowtie

- **B1 — `degraded`.** Recorded detection redundancy is reduced and proof testing is overdue, but complete function loss or failure on demand is not demonstrated. Compare `B1.pfd_projeto` → `B1.pfd_atual`, alongside both `B1.c2.componente_pior.multiplicador` and `B1.c2.multiplicador_barreira`. XV-1001 remains dominant (`B1.c2.elemento_dominante`). The automatic response class does not prove current effectiveness without a validated window (`a3_cruzamentos[id=C3]`; SKILL.md B3).
- **B2 — `degraded`.** Competence renewal is overdue; the supplied record does not establish complete loss or formal expiry of the operator function. Compare `B2.pfd_projeto` → `B2.pfd_atual`, both C2 multipliers, and the human-component factor in `B2.detalhe_componentes[item=OP-B2].fator`. OP-B2 dominates the calculated total, but its current PFD is an assumption, not measured competence (`B2.c2`, `premissas_do_modelo.human_barrier_pfd_with_overdue_competence`). No B2-specific demand assessment is supplied; neither success nor failure on demand can be assigned.
- **Dependency/model conflict:** the basis gives B2 independent ZT-1001 detection, whereas `B2.componentes` includes PT-007 and C6 lists it as shared. Therefore the calculated transfer of PT-007 degradation into B2 is not established by the declared architecture. Shared XV-1001/VLV-006 actuation independently prevents treating B1 and B2 as independent IPLs (design basis §4; `a3_cruzamentos[id=C6]`).
- **Exposure:** the group is known degraded, governed by repair backlog rather than an unidentified hidden-failure interval. No repair deadline is supplied. The effective voting arrangement is described in the work order but remains a model assumption requiring field verification (`a3_cruzamentos[id=C4]`, `a2_estado_atual.ordens_servico[wo_id=WO-RUN_A-CH-B]`, `premissas_do_modelo.voted_group_without_reconfiguration`).

### 2. Process

Current readings and distances must be read together with their unavailable rates: `a2_estado_atual.margem.PIT-7001.{valor,distancia,taxa_por_min,tempo_ate_limiar_min,alvos_declarados}`, and the corresponding fields for the other tags. These do **not** demonstrate a stable trajectory or usable response time (`references/cross-checks.md`, C7).

The empty rate ladder explicitly reports insufficient series. Consequently, the C1/C7 summary statements do not establish envelope validity or complete dynamic margins; pressure HIHI and lower targets also lack the full distance/rate treatment in `margem` despite appearing in `a1_base_de_projeto.limiares` (`a2_estado_atual.escada_de_taxas`, `a3_cruzamentos[id=C1]`, `a3_cruzamentos[id=C7]`).

Compression is unmeasurable, not demonstrated absent. Neither the design response windows nor the human delay allowance can be adopted as the current available time; configuration-change invalidation checks remain incomplete (`a3_cruzamentos[id=C3]`; design basis §§5,7).

### 3. Context

The selected work orders follow `a2_estado_atual.regra_de_recuperacao["work orders"]`; channel and event evidence is restricted by the corresponding visibility rules. The prior channel repair and current channel failure justify examining recurring integrity problems, but do not prove common cause or organisational failure (`a2_estado_atual.ordens_servico`).

Material inconsistencies remain despite C5 reporting no named gaps:

- **Test clock:** retain both model/calendar readings and their calculated sensitivity; obtain executed test records and the approved schedule to resolve them (`a2_estado_atual.contradicoes[0]`). The overdue test predates the recorded B failure, so claiming it would have exposed that later failure is unsupported.
- **Training clock:** `B2.motivos` disagrees with `a2_estado_atual.ordens_servico[wo_id=WO-RUN_A-TRAIN].vencida_ha_dias`; reconcile competence records before assigning quantitative human credit.
- **Design provenance:** barrier `pfd_documento` fields do not match the supplied diagram, and component-sum design PFDs differ from the narrative basis. Obtain the controlled graph, asset mapping and approved credit basis (`B1/B2.pfd_documento`, `B1/B2.pfd_projeto`; diagram; design basis §4).
- **Field verification:** inspect channel diagnostics, failure evidence, voting logic and independent pressure indication; obtain time-aligned trends and operating/configuration records to settle functional state, mode and dynamics (`references/cross-checks.md`, C1, C4–C5).
- **Missing assurance:** approved PHA/LOPA, tolerability, consequence/receptor data and current temporary-change records are absent. Threat persistence also remains unclassified pending the declared removal test (design basis §6; `references/risk-analysis-reference.md`, §§1–4).

## Risk judgement

**Barrier erosion demonstrated; risk tolerability not determined.**

The computed conventional design/current pair is `motores.conventional.projeto.evento_topo_por_ano` versus `motores.conventional.atual.evento_topo_por_ano`, with ratio `motores.conventional.razao`, over `motores.janela_de_exposicao_anos`. T1 dominates the current modelled contribution (`motores.conventional.atual.pathways[0].contribuicao_pct`).

The corresponding fuzzy pair and ratio are `motores.fuzzy.{projeto,atual}.evento_topo_por_ano` and `motores.fuzzy.razao`; its unchanged labels qualify frequency only. Conventional results provide model magnitude; fuzzy results express linguistic propagation, not independent validation (`motores.nota`).

These are **diagram-model outputs, not validated residual-risk estimates**: shared actuation, B2 detector mapping, assumed human PFD and unresolved clocks limit their credit. Current barrier values enter through `motores.pfd_atual`, not the MTTF transformation; the supplied diagram carries zero node MTTFs (SKILL.md, “Reading the engine’s numbers”).

**Urgency: immediate review; status: action required.** No emergency excursion is demonstrated, but restoration cannot be deferred on static margins or an unspecified repair horizon. Confidence in quantitative residual risk is low because consequence severity, receptors, acceptance criteria and decisive dependencies remain unresolved (`a2_estado_atual.margem`; C4; `references/risk-analysis-reference.md`, §§3,7).

## Recommendation

**Immediate containment:** Operations should immediately verify field condition, remaining protection and temporary configurations, and obtain an authorised continued-operation decision under standing procedures. If approach to trip, unsafe-envelope operation or multiple critical barriers is identified, escalate under emergency procedures without awaiting certainty. Do not improvise manoeuvres or change voting, thresholds or bypasses (SKILL.md, Safety limits).

**Restoration:** Instrumentation/maintenance should establish a repair deadline, diagnose and repair PT-007.B, and perform approved channel, voting and end-to-end functional tests. Training ownership should verify and renew B2 competence; reliability/process safety should reconcile both clocks and the detector mapping before restoring quantitative credit (`a2_estado_atual.ordens_servico`; `references/risk-analysis-reference.md`, §§2,4,8).

**Definitive solution:** Review recurrent channel defects and backlog controls; prioritise observable B2 demand and robust reduction of shared-actuator dependence over permanent administrative compensation. Assess changes through the applicable hazard/MOC process. Any intervention involving shared feed valves must address loss of level control and the declared secondary shutdown route (`a3_cruzamentos[id=C6]`; design basis §4; risk-analysis reference §§4–6).

**Suggested owner / deadline:** Operations superintendent for the immediate decision; maintenance, instrumentation, training and process-safety leads for time-bound restoration. The authorised team must set the repair horizon and any temporary measure’s expiry and withdrawal conditions; no safe numerical deadline is demonstrated (C4; risk-analysis reference §6).

**Expected return / leading indicator:** Verified functional redundancy, completed proof testing and competence renewal, resolved overdue items, and measured process trends sufficient to assess all declared targets—not merely agreeing channel readings (C4–C7; risk-analysis reference §8).

**Closure criteria:** Controlled condition; repaired and tested functions; reconciled configuration and clocks; managed temporary changes; current-condition window validation; reassessed residual risk and traceable open actions. No closure is supported at this snapshot (SKILL.md B5).

**Residual risk / accepting authority:** Not determined; acceptance belongs to the facility’s designated authority, whose identity is absent—not to this report (SKILL.md B4–B5).

**Human decision:** pending.

## Evidence and assumptions

- **[demonstrated]** `identidade.gatilho` and `a2_estado_atual.canais`: newly recorded unrepaired failure at the frozen analysis instant.
- **[demonstrated]** `a2_estado_atual.grupo_votado`: analogue agreement does not reproduce the recorded discrepancy; freezing is not demonstrated.
- **[inferred]** `B1/B2.pfd_atual`, `motores`: calculated erosion depends on declared model assumptions and unresolved architecture.
- **[undetermined]** `a2_estado_atual.contradicoes`, `envelope.lacuna`, design basis §§4–7: governing clock, current effectiveness window, validated joint credit and threat persistence.
- **[undetermined]** No supplied consequence/acceptance basis: residual-risk tolerability and authorisation to operate.