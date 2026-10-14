---
incident_id: INC-BT-REATOR-20251129-1
bowtie_id: BT-REATOR
opened_at: 2025-11-29T04:00:00
engine: conventional
status: action_required
urgency: immediate
confidence: medium
---

# The LO alarm needs no process action, but pathway T1 is running outside its validated envelope with a known-degraded voted group — repair `PT-007.B`, execute the overdue interlock test and the OP-B2 competence renewal, and revalidate the design basis windows for the condition established on 2025-11-28, before any escalation demand can arise.

## Fact

- Trigger: `identidade.gatilho[0]` — `alarme:PIT-7001:LO`, voted PIT-7001 below the LO threshold at `t_now`, active `a2_estado_atual.alarmes_ativos[0].ativo_ha_min` = 0.0 min, `e_demanda` = 0. It is **not** a demand on B1, whose declared trigger is voted PIT-7001 ≥ HIHI (`a1.declarado.barreiras.B1.gatilho`).
- The crossing is reproducible: a previous LO episode is recorded 2025-11-28T00:00→08:00 (`a2.alarmes_normalizados[0]`), and the two channels that agree at `t_now` (A, C — `a2.grupo_votado.concordancia_no_ultimo_instante`) both carry it.
- Operating mode: changed at 2025-11-28T00:00:00 (`a2.eventos_operacionais[0]`, `carga_pct` 15, `escala_setpoints_alimentacao` 1.15). Pressure regime shifted by `a2.regime.deslocamento_kpa` = −122.18 kPa; `a2.regime.revalidacao_registrada` = false.
- Data quality limitation, decisive for this report: **no rate is available**. `envelope.degraus` is empty with `lacuna` "serie insuficiente na janela", and every `taxa_por_min` in `a2.margem` is null. Distances exist; time-to-target does not. No conclusion on trajectory is issued here (SKILL.md, "Do not conclude from an instantaneous value").
- No demand on B1 up to `t_now` (`a2.demandas.B1.demandada` = false); C3 therefore does not apply (`a3[C3].nao_se_aplica`).
- Channel divergence: spread `a2.discrepancia_canais[0].spread` = 172.61 kPa against limit 17.5 kPa; divergent channel by majority = B.

**What this trigger changed.** This is the first analysis in this stream. The frozen state of `PT-007.B` has been recorded since 2025-08-29 (`WO-RUN_A-CH-B`), but while the plant sat in the old regime the frozen value was indistinguishable from the process: `a2.grupo_votado.congelamento.diferenca_para_o_regime` = 0.04 kPa. The 2025-11-28 condition change moved the process down and left the frozen channel behind; this LO alarm is the instant at which that latent degradation became visible in the readings as a 172.61 kPa spread.

## Scenario and mechanism

Qualitative chain (pathway T1, `diagrams/BT-REATOR.txt`):
`loss of stream 1 feed → B1 high-pressure interlock → B2 manual operator action → loss of reactor control (top event) → [consequence and receptor not declared in the supplied basis]`.

Quantitative chain, link by link:

1. `PT-007.B` failed detected, unrepaired for 92 d (`a3[C4].relogio`); group running 2oo2 without reconfiguration (`premissas_do_modelo.voted_group_without_reconfiguration`, an assumption, not a record) → item PFD 34.17× design (`a1.barreiras[B1].c2.componente_pior`). **Source: reliability record + model assumption. Strength: demonstrated for the failure, inferred for the 2oo2 arithmetic.**
2. The failure mode the data supports is a **frozen channel**, not drift: B's sd 0.2 kPa over 181 samples against A 29.52 and C 29.46 (`a2.grupo_votado.estatistica_por_canal`), stuck within ±1.5 kPa of the pre-change regime. **Demonstrated.**
3. Barrier effect: B1 `pfd_projeto` 2.053e-02 → `pfd_atual` 2.285e-02, barrier multiplier 1.11× — the sensor degradation is absorbed because the dominant element is XV-1001 at 48 % of the total (`a1.barreiras[B1].c2`). The same component moves B2 by 2.27× only because OP-B2 (competence overdue) dominates at 92 % (`a1.barreiras[B2].c2`). **Demonstrated (C2 reports both multipliers).**
4. Envelope: the condition change without revalidation is an explicit invalidation trigger (`a1.declarado.invalidacao.gatilhos[1]`; design basis §7). The windows of §5 (HIHI→SIS, B2 tolerable delay) therefore **do not describe the current condition** and are not cited here as valid.
5. Top event frequency: `motores.conventional.projeto.evento_topo_por_ano` → `motores.conventional.atual.evento_topo_por_ano`, ratio `motores.conventional.razao`; pathway T1's share rises from 70.1 % to `motores.conventional.atual.pathways[0].contribuicao_pct`. **Computed by phase A.**

Hypothesis, marked as such: the LO excursions are a consequence of the 2025-11-28 load/setpoint change rather than of a T1 feed loss — `FIT-1001` reads 0.4964 kscmh, above, not below, the design base value of 0.252 kscmh (`a1.declarado.condicao_de_projeto.vazao_alimentacao_kscmh`). Temporal correlation with the change record is not causation; see the unresolved inconsistency in §3 below.

## Analysis

### 1. Bowtie

**B1 — `degraded`.** Requirement is not demonstrated: the functional test `WO-RUN_A-TEST` is 182 d overdue and not executed, so the interlock's ability to act has not been proven since before the last two channel events. Detection is in the C4 state **known degraded** (`a3[C4].resultado`) — the clock that applies is the repair backlog, 92 d, not the test interval. The function is not removed and there is no failed demand, so the state is `degraded`, not `critical`. Dominant element remains XV-1001 (48 %), unchanged and untested.

**B2 — `degraded`.** PFD 2.27× design, 92 % of it carried by OP-B2 at 0.25 — and that 0.25 is `premissas_do_modelo.human_barrier_pfd_with_overdue_competence`, a **model assumption, not asset data**. The underlying fact is the record: `WO-RUN_A-TRAIN` overdue 122 d and open. Per the design basis §5, the whole of B2's margin is perception and decision, not execution; with the envelope invalidated (C1) the available window for that perception is **not known**, so B2's design PFD cannot be read as describing the current condition. That is a gap, not an adjusted number (C3 doctrine; risk-analysis reference §5).

**Independence / credit.** C6 is explicit: detection independent (PT-007 vs ZT-1001), **actuation shared** (XV-1001, VLV-006) — joint credit must not multiply the two PFDs. The conventional engine folds a pathway as one AND per barrier (SKILL.md, "A pathway folds as the diagram reads"), i.e. as a product; with a shared final element that product is optimistic. The current figure should be read as a **lower bound** on pathway T1. *Inferred.*

**Recorded contradiction, unresolved:** phase A lists PT-007 among B2's components (`a1.barreiras[B2].componentes`, `detalhe_componentes`) while the declared basis states B2 detects via ZT-1001 (`a1.declarado.independencia`). Both come from the supplied material and disagree; the reliability model may be attributing B1's detector to B2. This does not change the direction of the conclusion (OP-B2 dominates B2 either way) but it does affect any future independence claim.

**Second recorded contradiction (phase A, `a2.contradicoes[0]`):** model clock vs maintenance calendar for PT-007. The sensitivity is decisive only in that it is small — B1 1.07×, B2 1.01×. Which clock governs is a team decision; the judgement in this report holds under either.

**No demand, no settled state by observation.** No barrier on T1 was demanded up to `t_now`, so every state above rests on PFD and record, not on outcome.

### 2. Process

Direction matters: the excursion is **low** pressure, away from the T1 top-event direction. Against every declared target (`a3[C7]`): LO already crossed by −14.36 kPa; HI ahead at 214.36 kPa; SIS trip at 364.36 kPa (`alarm_config.trip_sis`); model physical limit at 464.36 kPa (design basis §3). **All time-to-target fields are null because no rate could be computed** — distance alone does not establish margin, and this report does not convert it into one.

Other tags carry no rate either: TIT-9001 14.52 °C below HI, LIT-8001 17.24 % below HI, TIT-2101 4.47 °C below HI. LIT-8001 at 67.76 % sits below the design regime level of 74.4 % (`a1.declarado.condicao_de_projeto.nivel_regime_pct`), consistent with a reduced-load condition. *Inferred.*

New-regime alarm behaviour: the post-change median is 2586.19 kPa (`a2.regime.regime_depois.mediana`) against a LO threshold of 2550 kPa — the plant is now operating ~36 kPa above a deviation alarm, and two LO episodes have already occurred since the change. The alarm configuration was set for a 2708 kPa base (design basis §3) and has not been recomputed. Recurrent LO alarms in this condition are expected and are an alarm-management finding, not evidence of a new process upset.

Precursor structure to watch, stated as a mechanism and not as an observation: with B frozen at 2708.4 kPa and the group at 2oo2, the voted signal that feeds B1's HIHI comparison now depends on A and C alone; a single further channel failure removes the vote. This is exactly the exposure C4 separates from a repaired failure — the clock here is a 92-day repair backlog.

### 3. Context

- **Design basis status: invalidated.** `references/design-basis-barriers.md` §7, trigger "operating-condition change without subsequent revalidation"; `a2.regime.revalidacao_registrada` = false. The escalation rate of 1.1 kPa/min, the 202/162 min windows and the 67 min B2 tolerable delay are all base-case properties (§2, §5) and are **not** available to this analysis as current parameters.
- **Management of change.** A load and feed-setpoint change was executed and recorded; no revalidation of barrier windows, no alarm-threshold recomputation and no design-basis revision accompany it in the supplied records. Per the risk-analysis reference §4, that belongs both to integrity and to envelope invalidation. The absence of a record is a gap, not proof of non-compliance.
- **Mechanical integrity backlog, three items, all traceable in the calendar:** `WO-RUN_A-TEST` (interlock functional test, 182 d overdue), `WO-RUN_A-TRAIN` (OP-B2 competence, 122 d overdue), `WO-RUN_A-CH-B` (channel repair, open 92 d). A prior identical channel event on A (`WO-RUN_A-CH-A`, closed with finding, repaired in 1 d) shows the repair loop functioned in April and has not for B — a possible systemic degradation of the maintenance response, *inferred*, not demonstrated.
- **Human factors.** Competence renewal overdue is an organisational condition, not operator fault. With the actuation window unknown (C1) and the whole B2 margin being perception and decision (§5), crediting the operator action in the current condition is not supportable.
- **Unresolved data inconsistency.** Declared change = load 15 %, feed setpoint ×1.15; observed `FIT-1001` = 0.4964 kscmh against a design-base 0.252 kscmh, with pressure 122 kPa lower. These do not reconcile on the material supplied; unit, scaling and operating mode need confirmation before any quantitative use of the feed tag. **Undetermined.**
- **C5 gap (phase A):** whether a common cause affects A and C cannot be settled internally — the majority identifies B as divergent, but a shared error in the agreeing pair remains open. External check: an independent field measurement of vessel pressure.
- **Analyst-observed gap, marked as inferred:** B2's declared demand trigger, ZT-1001 (command-versus-position discrepancy), does not appear among the tags carried in `a1.limiares` or `a2.margem`. If that signal is not instrumented in the dataset, B2 cannot be shown to have been demanded, to have responded, or to have failed — a barrier whose demand cannot be observed cannot be credited or audited (risk-analysis reference §6; cross-checks C5, "an uninstrumented trigger").
- **C8:** threat classification for T1 not executed (design basis §6); no removal test. Remains a gap.

## Risk judgement

- **Top event frequency (cite, not retype):** conventional `motores.conventional.projeto.evento_topo_por_ano` → `motores.conventional.atual.evento_topo_por_ano`, ratio `motores.conventional.razao` (2.07×). Fuzzy `motores.fuzzy.projeto/atual.evento_topo_por_ano`, ratio `motores.fuzzy.razao`, label Moderate → Moderate. The two engines are not checks on each other: conventional for magnitude, fuzzy for propagation of linguistic uncertainty. The fuzzy label staying at Moderate does **not** mean nothing changed — it is a frequency label, not a barrier state and not risk.
- **Pathway share:** T1 rises from 70.1 % to 85.6 % of the current top event frequency (conventional). The erosion is concentrated on the pathway this trigger touches.
- **Consequence and tolerability:** no consequence, receptor or tolerability criterion is declared in the supplied basis. Therefore the correct conclusion is **`barrier erosion demonstrated; risk tolerability not determined`**. That is a result, not a failure of the analysis.
- **Uncertainty.** Three items limit confidence: no rate anywhere in the window; B2's dominant PFD is a model assumption, not a measurement; the shared final element means the engine's pathway figure is a lower bound. The PT-007 clock contradiction is *not* a material source of uncertainty (1.07× / 1.01×).
- **Urgency: immediate, not emergency.** No active loss of containment, no approach to a trip, no failed demand, and the excursion is in the low direction. But the T1 demand path is simultaneously (a) degraded and unobservably so if one more channel fails, (b) untested for 182 d, (c) backed by a human barrier whose window is unknown, and (d) operating outside a validated envelope. If a T1 escalation occurs in this condition, neither the available time nor the barrier performance is known. The actions below should not wait for a scheduled outage.

## Recommendation

**Immediate containment:** escalate to the shift supervisor and the process safety authority that pathway T1 is operating outside its validated envelope (design basis §7) with the PT-007 voted group at 2oo2. Until `PT-007.B` is repaired and the interlock tested, treat B1 as not demonstrated and impose compensatory monitoring of PIT-7001 channel spread against the 17.5 kPa limit. No setpoint, logic, bypass or valve change is recommended or authorised by this report.

**Restoration, in priority order:** (1) close `WO-RUN_A-CH-B` — repair `PT-007.B`, restoring 2oo3 and the arbiter the group currently lacks (C5); (2) execute `WO-RUN_A-TEST`, the 182-d-overdue interlock functional test, with coverage of the final element XV-1001, which dominates B1's PFD at 48 % and is the element no channel repair touches; (3) execute `WO-RUN_A-TRAIN` for OP-B2 and replace the assumed 0.25 with an asset-recorded value.

**Definitive solution:** revalidate the design basis windows under the condition established 2025-11-28 — escalation rate, HI/HIHI→SIS windows and B2 tolerable delay — per `references/producing-a-design-basis.md`, and recompute the alarm thresholds, which were sized for a 2708 kPa base and now sit 36 kPa below the operating median. Route the 2025-11-28 change through management-of-change triage retrospectively. Instrument or confirm instrumentation of ZT-1001 so B2's demand is observable; an uninstrumented demand trigger sits at the top of the response hierarchy, not the bottom. Prefer these engineering and design actions over administrative watchkeeping, which does not permanently compensate (SKILL.md B5).

**Risks introduced by the actions themselves:** any test or repair that can actuate B1 carries the declared C6 side effect — closure of the A+C feed valve destroys inventory control via LIC-8001, level goes to ≈ −2.5 % and a low-level trip follows ≈ 1 h later. Plan the functional test so that this coupling is managed, and do not treat a B1 actuation as a consequence-free event.

**Suggested owner / deadline:** maintenance and instrumentation lead — channel repair and functional test, this week; operations training lead — OP-B2 renewal, this month; process safety authority — envelope revalidation and MOC triage before the next campaign in this condition. Deadlines are proposals for the accepting authority, not commitments.

**Expected return / leading indicator:** PT-007 channel spread back within 17.5 kPa with three live channels; B1 component multiplier for PT-007 back toward 1×; B2 PFD sourced from the asset rather than the assumption; a revalidated rate and window pair for the current condition.

**Closure criteria:** all three work orders closed with results; interlock function tested post-repair covering the relevant failure mode; design basis windows revalidated under the current operating condition and the invalidation trigger cleared; alarm thresholds reviewed against the new regime; the ZT-1001 observability question answered. Pressure returning inside band does **not** close this occurrence.

**Residual risk / accepting authority:** not determined — no tolerability criterion or consequence declared. Acceptance is for the facility's competent authority.

**Further analysis required:** a formal look at why an identical channel failure was repaired in 1 d in April and has stood 92 d since August, alongside two overdue calendar items — evidence consistent with a systemic maintenance-response failure, which warrants a separate investigation rather than closure inside this occurrence.

**Human decision:** pending

## Evidence and assumptions

- [demonstrated] `a2.alarmes_ativos[0]`, `a2.alarmes_normalizados[0]`, 2025-11-29 — LO crossing on voted PIT-7001, second episode since the condition change; `e_demanda` = 0, not a demand on B1.
- [demonstrated] `a2.eventos_operacionais[0]` + `a2.regime`, 2025-11-28 — operating-condition change, regime shift −122.18 kPa, `revalidacao_registrada` = false → design basis §7 invalidation trigger met; §5 windows not usable as current.
- [demonstrated] `a2.grupo_votado.estatistica_por_canal` / `.congelamento`, window 2025-10-30→2025-11-29 — channel B sd 0.2 kPa vs A/C ≈ 29.5 kPa, flat at 2708.41 kPa within 0.04 kPa of the pre-change regime: failure mode is frozen, not drifting.
- [demonstrated] `a2.discrepancia_canais[0]` — spread 172.61 kPa against a 17.5 kPa limit; majority identifies B as divergent (`a2.grupo_votado.concordancia_no_ultimo_instante`).
- [demonstrated] `a2.ordens_servico` — `WO-RUN_A-CH-B` open 92 d; `WO-RUN_A-TEST` overdue 182 d; `WO-RUN_A-TRAIN` overdue 122 d; `WO-RUN_A-CH-A` closed with finding in 1 d.
- [demonstrated] `a1.barreiras[B1].c2`, `a1.barreiras[B2].c2` — both C2 multipliers per barrier: barrier 1.11× / 2.27×, worst component PT-007 34.17×, dominant elements XV-1001 (48 %) and OP-B2 (92 %).
- [demonstrated] `motores.conventional` and `motores.fuzzy` — design vs current top event frequency, ratios 2.07× and 1.98×, fuzzy label Moderate → Moderate, T1 share 70.1 % → 85.6 %.
- [corroborated] `a3[C6]` + design basis §4 — detection independent, final element shared (XV-1001, VLV-006); declared side effect of B1 actuation on the LIC-8001 level cascade.
- [inferred] Conventional pathway figure is a lower bound, because the engine folds barriers as a product (SKILL.md, fuzzy/engine section) while C6 refutes actuation independence.
- [inferred] ZT-1001, B2's declared demand trigger, is absent from `a1.limiares` and `a2.margem` — B2's demand may not be observable in the dataset (C5, "an uninstrumented trigger").
- [undetermined] `a2.margem.FIT-1001` 0.4964 kscmh vs design base 0.252 kscmh (§2) against a declared 15 % load and ×1.15 feed setpoint — does not reconcile; unit and operating mode need confirmation.
- [undetermined] `a3[C5]` — common cause on the agreeing pair A/C cannot be excluded; external check: independent field measurement of vessel pressure.
- [undetermined] `a3[C8]` + design basis §6 — T1 persistent/removable classification not executed; success criterion under a persistent threat therefore not established.
- [undetermined] `a2.contradicoes[0]` — PT-007 model clock vs maintenance calendar; both from the same database, unresolved; sensitivity B1 1.07×, B2 1.01×, so the conclusion holds either way.
- [assumption] `premissas_do_modelo.human_barrier_pfd_with_overdue_competence` = 0.25, `voted_group_without_reconfiguration` (2oo2 = 2·PFD1), `mean_channel_pfd_between_tests` — model assumptions, not asset data; they carry most of B2's current PFD and the linear growth of PT-007's.
- [absent] Consequence, receptor and tolerability criterion for the top event — not present in the supplied basis; no risk classification issued.
- [not applicable] C3 window compression — no demand on B1 up to `t_now` (`a3[C3].nao_se_aplica`); measured window not obtainable.