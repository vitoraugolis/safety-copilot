# Escalate immediately to operations under standing emergency procedures: B1 failed on demand, and the newly recorded SIS trip has not yet demonstrated pressure arrest.

## Fact

This trigger records the excursion reaching the SIS, settling B1’s unsuccessful pressure-reversal outcome and establishing the observed demand-to-SIS window. It does **not** demonstrate successful SIS containment; post-trip response is unavailable at this analysis instant. Sources: `identidade.gatilho`, `a2_estado_atual.demandas.B1.desfecho`, `a2_estado_atual.demandas.SIS`.

The reactor, analysis instant, observation window and database are identified in `identidade`; the recorded operating mode and changed feed settings are in `a2_estado_atual.regime.mudanca`. Pressure value, units, crossed thresholds and computed rate are paired in `a2_estado_atual.margem.PIT-7001`; alarm onset, duration and active state are in `a2_estado_atual.alarmes_ativos`.

The trip crossing is reproducible from the pressure margin and visible event. However, B1’s logic timestamp precedes the first sampled HIHI crossing; exact clock alignment remains unverified. Channel B is frozen near the earlier regime, while A and C agree; this supports the observed excursion but does not exclude common error in the agreeing pair. Sources: `a2_estado_atual.demandas.B1.instantes`, `a2_estado_atual.grupo_votado`, `a3_cruzamentos[4].lacunas`.

## Scenario and mechanism

**Loss of stream 1 feed → B1 automatic interlock / B2 conditional manual backup → loss of reactor control → downstream SIS and unverified further protection → consequences and receptors not established.** The graph supplies the threat and top event; the basis distinguishes B2’s demand from the pressure alarm and places the SIS beyond the preventive barriers. Sources: `motores.diagrama`; design basis §§3–4; `a3_cruzamentos[4].lacunas`.

The supported quantitative chain is:

- Low feed indication with little recovery supports the initiating-threat interpretation, but does not establish its cause or permanent persistence: `a2_estado_atual.margem.FIT-1001`, `a3_cruzamentos[7]`.
- A satisfied pressure vote followed by no commanded outputs implicates UZ-007; absent actuation signatures and the failed success criterion establish B1 failure: `a2_estado_atual.demandas.B1`.
- Known channel degradation and overdue competence enter the supplied PFD model; faster dynamics separately invalidate design response-window credit: `a1_base_de_projeto.barreiras[].motivos`, `premissas_do_modelo`, `envelope`.
- These model inputs produce the increased top-event frequency in `motores`; consequence frequency and severity remain **not demonstrated** because consequence and receptor data are absent.

## Analysis

### 1. Bowtie

**B1 — `critical`, failed on demand.** Detection satisfied the declared vote; the logic record identifies no output commands, and the final-element signatures did not match the required action. The SIS crossing fails the declared success criterion. This observation outranks prospective PFD. It implicates the logic/output function, but does not prove the uncommanded valves themselves failed. Sources: `a2_estado_atual.demandas.B1`; SKILL.md B3.

B1’s design → current PFD is carried by `a1_base_de_projeto.barreiras[0].pfd_projeto` and `.pfd_atual`; both degradation multipliers and the dominant UZ-007 contribution are in `.c2`. Automatic response speed does not compensate for unavailable logic. Source: `a3_cruzamentos[2].comparado.B1`.

**B2 — `degraded`; demand and outcome undetermined.** Its detector is the declared command-versus-position discrepancy, not HIHI. The position signal is absent and B1 issued no command, exposing a backup-coverage question for logic failure rather than demonstrating operator failure. Sources: `a2_estado_atual.demandas.B2`; design basis §4.

B2’s design → current PFD is in `a1_base_de_projeto.barreiras[1].pfd_projeto` and `.pfd_atual`; `.c2` distinguishes the worst component multiplier from whole-barrier degradation and identifies OP-B2 as dominant. The human contribution is an assumption, and compressed response time invalidates design-window performance credit. The design tolerable delay is not an observed operator response time; no adjusted PFD is justified. Sources: `premissas_do_modelo.human_barrier_pfd_with_overdue_competence`, `a3_cruzamentos[2]`.

**PT-007 — known degraded, not hidden degraded.** Channel B’s own variability supports freezing, and its stuck reading matches the former regime. The applicable exposure clock is the repair backlog, with no scheduled repair deadline supplied—not a future test horizon. Sources: `a2_estado_atual.grupo_votado.congelamento`, `a3_cruzamentos[3].relogio`, `a2_estado_atual.ordens_servico[3]`.

**No independent joint IPL/SIL credit is demonstrated.** B1 and B2 have independently declared detection but shared final elements. The model nevertheless assigns PT-007 to B2; reconcile that mapping before accepting quantitative credit. B3/B4 inputs are present, but their current functionality is not demonstrated by this T1 context. Sources: `a3_cruzamentos[5].comparado`, `a1_base_de_projeto.barreiras[1].componentes`, `motores.pfd_atual`; risk-analysis reference §2.

### 2. Process

The episode-wide average masks the faster decision-window rise. The rate ladder and loss of the design plateau support envelope invalidation, reinforced by the operating-condition change without recorded revalidation. Base-case windows cannot describe this episode. Sources: `envelope.degraus`, `envelope.plato_medido`, `envelope.gatilhos_de_invalidacao`; design basis §§2, 7.

Read pressure distance and rate together in `a2_estado_atual.margem.PIT-7001`: alarm exceedances are in `.limiares_ja_cruzados`, SIS status and physical-limit distance in `.alvos_declarados`, and recent rate in `.taxa_por_min`. The physical-limit `.tempo_min` is a **computed pre-trip-trend projection**, not guaranteed time remaining after SIS action. Neither continued escalation nor recovery after the trip is observable yet. Source: `a2_estado_atual.demandas.SIS.taxa_depois_kpa_min`.

The model physical limit is not a verified vessel design pressure. Threat persistence also remains unclassified; ongoing low feed indication alone cannot replace the removal test. Sources: `a3_cruzamentos[4].lacunas[1]`, `a3_cruzamentos[7]`.

### 3. Context

Open corrective work, overdue testing and competence renewal, and absent window revalidation warrant a separate investigation of maintenance prioritisation and change assurance—not operator blame or an automatic non-compliance finding. Sources: `a2_estado_atual.ordens_servico`, `a2_estado_atual.regime.revalidacao_registrada`; risk-analysis reference §§4–5.

Unresolved assurance issues include:

- Conflicting test clocks and their supplied sensitivity: `a2_estado_atual.contradicoes[0]`.
- Competence-overdue chronology differing between `a1_base_de_projeto.barreiras[1].motivos` and `a2_estado_atual.ordens_servico[2]`.
- Differing PFD declarations across `.pfd_documento`, `.pfd_projeto`, the supplied diagram and design basis §4.

Approved bowtie revision, tolerability criterion, bypass/isolation register, instrument quality flags and configuration-change verification are not supplied. Obtain controlled records and timestamp verification; absence does not establish normal configuration. Sources: `identidade`, `a1_base_de_projeto.declarado.invalidacao`; SKILL.md B1/B3.

## Risk judgement

**Barrier erosion demonstrated; risk tolerability not determined.**

For annual magnitude, cite the computed conventional pair `motores.conventional.projeto.evento_topo_por_ano` → `motores.conventional.atual.evento_topo_por_ano`, with `motores.conventional.razao`; exposure is declared in `motores.janela_de_exposicao_anos`. T1 dominates the current model contribution in `motores.conventional.atual.pathways`.

The separate fuzzy pair and ratio are `motores.fuzzy.projeto.evento_topo_por_ano`, `.atual.evento_topo_por_ano` and `.razao`; its `.rotulo` fields describe frequency uncertainty, not risk acceptance or barrier condition. These engines must not validate one another. Source: `motores.nota`.

These are diagram-model outputs, not validated residual-risk estimates: shared actuation, B2’s detector mismatch, assumed human PFD and invalid response windows constrain their applicability. Barrier inputs follow the supplied reliability/PFD calculation path, not a demonstrated MTTF-derived frequency path. Sources: `a1_base_de_projeto.barreiras`, `premissas_do_modelo`, `motores.pfd_atual`; SKILL.md “Reading the engine’s numbers.”

**Urgency: emergency; status: action required.** B1 failure, a newly reached final declared automated layer and uncertain downstream protection justify escalation without waiting for outcome certainty. Confidence is strong in B1’s observed failure, but low in quantified residual risk; consequence severity, receptors and approved acceptance criteria remain undetermined. Sources: `a2_estado_atual.demandas`, `a3_cruzamentos[4]`; SKILL.md “Safety limits.”

## Recommendation

**Immediate containment:** Operations should apply standing emergency procedures, verify SIS outputs and pressure response, obtain independent pressure confirmation where safely practicable, and confirm relief provision and vessel design pressure. Do not wait for the projected limit time or improvise setpoint, bypass or valve changes. Sources: `a3_cruzamentos[4].lacunas`; SKILL.md “Safety limits.”

**Restoration:** Repair and functionally test UZ-007 and channel B; verify the complete detection–logic–actuation chain, reconcile test records and restore demonstrated operator readiness. Recover control-room records for B2 demand assessment. Sources: `a2_estado_atual.ordens_servico`, `a2_estado_atual.demandas`; risk-analysis reference §8.

**Definitive solution:** Review hazard reduction, backup coverage for a no-command logic failure, observable valve-position discrepancy, shared actuators and operating-window revalidation through authorised engineering/change review. Investigate accumulated maintenance and revalidation gaps separately. Sources: design basis §§4, 7; risk-analysis reference §§4–6.

**Suggested owner / deadline:** Shift operations lead immediately; instrumentation, maintenance and process-safety engineering before protection credit or return-to-service acceptance. These are proposed responsibilities under SKILL.md B5.

**Action risks:** Feed isolation can remove level-cascade control and introduce low-level shutdown; this is a declared coupling, not an observed consequence here. Review it before authorised intervention. Source: `a3_cruzamentos[5]`.

**Expected return / leading indicator:** Demonstrated pressure arrest over a justified observation window, verified commanded-versus-actual actuation, restored channel agreement and traceable completion of tests and revalidation. Sources: `a2_estado_atual.demandas`, `a3_cruzamentos[4]`; risk-analysis reference §8.

**Closure criteria:** Controlled condition, repaired and tested barriers, managed temporary changes, revalidated current-condition windows, reassessed residual risk and traceable outstanding actions—not merely pressure returning to band. Source: SKILL.md B5.

**Residual risk / accepting authority:** Undetermined; acceptance belongs to the facility’s designated competent authority, not this report. **Human decision: pending.** Source: SKILL.md B5.

## Evidence and assumptions

- **[demonstrated]** Frozen at `identidade.ts`: B1’s failed success criterion and recorded SIS trip—`a2_estado_atual.demandas`.
- **[demonstrated]** Frozen-channel behaviour and known unrepaired state—`a2_estado_atual.grupo_votado`, `.canais`; the computed freezing onset is not a recorded failure timestamp.
- **[inferred]** Feed-loss scenario and changed-condition contribution are consistent with the trajectory; root cause is not established—`a2_estado_atual.margem.FIT-1001`, `.regime`, `envelope`.
- **[undetermined]** SIS effectiveness, B2 demand, common error in A/C and downstream protection—`a3_cruzamentos[4].lacunas`.
- **[assumption]** Human PFD, degraded-vote treatment and default test-history treatment remain model assumptions—`premissas_do_modelo`.
- **[demonstrated]** Evidence selection excludes future closures and non-visible events using `a2_estado_atual.regra_de_recuperacao`; no later outcome is used.