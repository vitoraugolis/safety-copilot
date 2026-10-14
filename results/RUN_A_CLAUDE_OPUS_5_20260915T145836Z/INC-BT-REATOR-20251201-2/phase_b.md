---
incident_id: INC-BT-REATOR-20251201-2
bowtie_id: BT-REATOR
opened_at: 2025-12-01T00:34:25
engine: conventional
status: action_required
urgency: immediate
confidence: medium
---

# Treat the T1 barrier set as operating outside its validated envelope: authorise the field pressure check and the PT-007 / proof-test / competence backlog this shift, and rule on revalidation of the 2025-11-28 condition change before the campaign continues — no process manoeuvre is recommended from this analysis.

## Fact

Trigger `alarme:PIT-7001:LO` (`identidade.gatilho`): voted PIT-7001 crossed the LO threshold downward at `2025-12-01T00:34:25`, active 0.0 min at t_now, exceedance −0.45 kPa (`a2_estado_atual.margem.PIT-7001.limiares_ja_cruzados`). Rate −0.5829 kPa/min over a 300 s window, 61 samples (`a2_estado_atual.taxas.PIT-7001`); next threshold LOLO 2450 at 99.55 kPa distance, 170.8 min at the current rate (computed, `margem.PIT-7001.tempo_ate_limiar_min`). Direction is **away** from the T1 top-event side: SIS trip 2900 is +350.45 kPa away and not approached (`margem.PIT-7001.alvos_declarados`).

Concurrent: FIT-1001 LO and LOLO active since `2025-12-01T00:00:05` (34.3 min) at −0.0012 kscmh with rate −0.0000 kscmh/min (`a2_estado_atual.alarmes_ativos`) — the declared T1 threat signal (loss of stream 1 feed) is present and flat.

Operating mode: "campanha padrao", load 15 %, feed setpoint scale 1.15, declared at `2025-11-28T00:00:00` (`a2_estado_atual.eventos_operacionais`). No demand on B1 up to t_now (`a2_estado_atual.demandas.B1`).

Data quality: the voted group is **known degraded**. Channel spread 159.11 kPa against a 17.5 kPa limit; A and C agree within 5.79 kPa, B is the majority outlier and is flat at 2708.41 kPa (sd 0.2) since about `2025-08-29T00:00:00`, 0.04 kPa from the pre-change regime median (`a2_estado_atual.grupo_votado`). The crossing is reproducible on the two live channels; the trigger is not inconsistent.

**What this trigger changed.** This is the fourth LO excursion since the condition change (three closed episodes in `a2_estado_atual.regime.alarmes_entre_a_mudanca_e_o_episodio`, this one open), and the first to coincide with the T1 threat signal active (FIT-1001 LO/LOLO). It also makes the channel-B freeze unambiguous: B sits at the *old* regime value while the voted regime has moved −148.86 kPa (`a2_estado_atual.regime.deslocamento_kpa`), so the frozen reading now stands out by 159 kPa rather than by noise.

## Scenario and mechanism

Qualitative chain (pathway T1, `diagrams/BT-REATOR.txt`): loss of stream 1 feed → B1 high-pressure interlock (automatic, seconds) → B2 manual operator action (human, minutes) → loss of reactor control → mitigating barriers and consequence/receptor **not declared in the supplied basis**.

Quantitative chain:

| Link | Value | Source | Strength |
|---|---|---|---|
| Operating-condition change without revalidation → barrier validity envelope invalid | trigger OBSERVED; regime shift −148.86 kPa; `revalidacao_registrada: false` | C1 / `envelope.gatilhos_de_invalidacao`, design basis §7 | demonstrated |
| PT-007 channel B failed, detected, unrepaired 94 d → group runs 2oo2 without reconfiguration | `a2_estado_atual.canais`, WO-RUN_A-CH-B, C4 `relogio` | reading + model assumption `voted_group_without_reconfiguration` | corroborated |
| Proof test 184 d overdue → PT-007 item PFD ×34.36 | WO-RUN_A-TEST; `a1_base_de_projeto.barreiras[].detalhe_componentes` | reading + `mean_channel_pfd_between_tests` | demonstrated |
| Competence renewal 124 d overdue → OP-B2 PFD 0.25 (×2.5) | WO-RUN_A-TRAIN; `premissas_do_modelo.human_barrier_pfd_with_overdue_competence` | **assumption**, not asset data | inferred |
| Barrier PFDs → top event frequency ×2.07 (conventional) | `motores.conventional.razao` | computed | demonstrated |

The mechanism is calendar-driven barrier erosion plus an unrevalidated condition change, not a process excursion toward the top event. No causal link is claimed between the LO alarm and the barrier degradations: they are concurrent, and temporal correlation is not root cause.

## Analysis

### 1. Bowtie

**B1 — high-pressure interlock: `degraded`.** Not demanded up to t_now, so the state is set by performance, not by an outcome (`a2_estado_atual.demandas.B1`). C2 gives both multipliers: barrier ×1.11, worst component PT-007 ×34.36, dominant element XV-1001 at 48 % of the total (`a3_cruzamentos[C2]`). Reporting only the component multiplier would over-react; only the barrier multiplier would hide a sensor subsystem thirty-four times worse than design. C4 places the group in **known degraded** with a 94 d repair backlog — a clock in days, not the test-interval clock — but the proof test is itself 184 d overdue, so the arbiter that would bound the remaining channels does not exist. The frozen channel B sits at 2708.41 kPa, below HI 2750; it can therefore never contribute a high vote, which is what "2oo2 without reconfiguration" means in practice: a genuine HIHI demand now requires **both** surviving channels. Function is not removed and no bypass is recorded — this is not `critical`.

**B2 — manual operator action: `degraded`.** Barrier ×2.27, dominant element OP-B2 at 92 % of the total, PFD 0.25 (`a3_cruzamentos[C2]`). That 0.25 is a **model assumption**, not an asset reading (`premissas_do_modelo`); it carries the barrier and therefore carries the pathway. C3 could not quantify window compression — the real window is not measurable at t_now because B1 was never demanded (`a3_cruzamentos[C3].nao_se_aplica`), so the design basis's 67 min tolerable delay (§5) cannot be compared against anything measured. Per C1 the §5 windows are invalidated in any case and must not be cited as current. The design basis states B2's entire margin is perception and decision, not execution, and that its window is a parameter of the operating condition — with the condition changed and unrevalidated, the meaning of B2's PFD is a gap, not a number to adjust.

**Dependence.** C6: detection independent (PT-007 vs ZT-1001), **final element shared** (XV-1001, VLV-006), with the explicit instruction that joint credit must not multiply the two PFDs (design basis §4). The conventional engine chains B1 and B2 multiplicatively along pathway T1; that product assumes an independence the design basis refutes in the actuation arm, so the current top-event figure is, if anything, optimistic for T1 (inferred). No IPL/SIL credit is granted here: none is documented in the supplied basis.

**Dominant path.** Pathway T1 now carries 85.6 % of the top event frequency (conventional) against 70.1 % at design; fuzzy 89.6 % against 74.2 % (`motores`). The T2 barriers B3/B4 are fed to the engines at their design values (`motores.pfd_atual`), so the whole shift in the split comes from T1.

**B2's demand trigger.** The declared trigger is a command-versus-position discrepancy on ZT-1001 (`a1_base_de_projeto.declarado.barreiras.B2.gatilho`). Phase A's rate table carries XV-1001A–D positions and no ZT-1001 field (`a2_estado_atual.taxas`). Whether that trigger is instrumented was not settled by C5; it is an open question, not a finding.

### 2. Process

PIT-7001 is falling, not escalating. The rate ladder spans −2.76 kPa/min (since 00:00, 414 samples) to −0.94 kPa/min (last 10 min, 121 samples), dispersion 0.34× (`envelope.degraus`). Neither window exceeds the 2.2 kPa/min invalidation limit, and the ladder confirms the single-value trap: the day-window rate is three times the recent one. The design plateau band (2850–2870) was not crossed in the window (`envelope.gatilhos_de_invalidacao`), so the margin distribution the design basis relies on is not observed in this regime.

C7, all declared targets: LO crossed by −0.45 kPa; LOLO 2450 at 99.55 kPa / 170.8 min (computed); SIS trip 2900 at +350.45 kPa, not approached; physical limit 3000 at +450.45 kPa. Supporting tags are quiet and stable: TIT-9001 120.37 °C (+0.0043 °C/min, 14.63 °C below HI), TIT-2101 96.76 °C (−0.0101 °C/min), LIT-8001 76.46 % falling 0.0726 %/min, 639.9 min to LO (`a2_estado_atual.margem`). The trajectory is a sustained low-side deviation with the feed at zero, consistent with the new low-load regime and with the three prior LO episodes since 11-28.

The C8 classification of T1 is unavailable — the removal test was never run (`a3_cruzamentos[C8].lacuna`, design basis §6). Observed behaviour: feed flat at zero with rate −0.0000 kscmh/min, i.e. behaviour consistent with a threat that is not clearing on its own. That is evidence, not a classification.

### 3. Context

**Management of change.** The 2025-11-28 condition change (load 15 %, feed setpoint scale 1.15) shifted the voted regime by −148.86 kPa with `revalidacao_registrada: false` and no work order after that date (`envelope.gatilhos_de_invalidacao`). This is simultaneously an integrity finding and an envelope invalidation trigger (risk-analysis-reference §4). Whether the change went through the facility's MOC rule is not in the supplied data — absence of a record is a gap, not a demonstrated non-conformance. Notably, the design constraint that HI must not fall below ~2750 kPa was derived from a 2708 kPa base pressure (design basis §3); the whole protection ladder was sized around a regime the plant has left.

**Mechanical integrity.** Three open items on the T1 barriers: WO-RUN_A-CH-B open 94 d (channel failure with finding), WO-RUN_A-TEST overdue 184 d, WO-RUN_A-TRAIN overdue 124 d (`a2_estado_atual.ordens_servico`). WO-RUN_A-CH-A closed with a finding on channel A in April — a second channel of the same voted group failing within five months is a repeat-defect signal on PT-007 worth a separate look (inferred).

**Recorded contradiction, unresolved.** The PFD creep clock reads 334 d since the last test; the calendar reads the proof test 184 d overdue (`a2_estado_atual.contradicoes`). Phase A carries both: item PFD 2.405e-03 (model clock) vs 3.953e-03 (calendar clock, 1.64×), which moves B1 by 1.07× and B2 by 1.01×. The disagreement is material for the item and immaterial for the barriers; which clock governs is a team decision, not an analyst's.

**Human factors.** The overdue competence renewal is a task/organisation finding, not operator fault. Under a window whose current value is unknown (C1/C3), credit for B2 rests on indication, time and competence being compatible with the scenario — time is undemonstrated and competence is overdue.

**Gap (C5).** "Is there a common cause affecting channels A and C?" The majority already identifies B as divergent; what cannot be ruled out is a shared error in the agreeing pair. External check: an independent field measurement of vessel pressure.

## Risk judgement

Top event frequency, both engines (`motores`): conventional design 1.754e-03 /yr → current 3.636e-03 /yr, ratio 2.07×; fuzzy design 2.496e-04 /yr → current 4.941e-04 /yr, ratio 1.98×, label Moderate → Moderate. Cite the conventional engine for magnitude and the fuzzy engine for the propagation of linguistic uncertainty; neither checks the other. The unchanged fuzzy label is a quantisation artefact of the five-term scale, not evidence of stability — the erosion is in the ratio and in the pathway split (T1 70.1 % → 85.6 % conventional).

Consequence, receptors and tolerability criterion are not declared in the supplied bowtie or design basis. The correct conclusion is therefore: **barrier erosion demonstrated (2.07× on the conventional engine); risk tolerability not determined.**

Uncertainty, in order of influence: (i) OP-B2 PFD 0.25 is a model assumption and carries 92 % of B2, which carries the dominant pathway — the current frequency is assumption-driven, not data-driven; (ii) the C6 shared final element means the engines' multiplicative chaining of B1×B2 overstates the available protection; (iii) the PT-007 clock contradiction (1.64× at item level, ≤1.07× at barrier level); (iv) T1 unclassified under C8, so the success criterion for both barriers is undefined; (v) the C5 common-cause gap on A/C, which would move the voted value itself.

Urgency **immediate**, not emergency. No safety-limit escalation condition in SKILL.md is met at t_now: no active loss of containment, no approach to a trip (350.45 kPa from SIS trip, moving away), no barrier in bypass. Time available is large on every declared target (≥170.8 min to LOLO, computed). What justifies acting this shift rather than at leisure is that the plant is operating outside the condition under which both T1 barriers were validated, with the group's arbiter overdue 184 d and one channel dead 94 d — a state in which a future demand would be answered by equipment whose sufficiency is undemonstrated. Note the distinction: what C1 invalidates is the **barrier validity envelope**; whether the current regime is inside the plant's approved *safe operating* envelope is not determined by the supplied data.

## Recommendation

**Immediate containment:** no process manoeuvre, setpoint, bypass or logic change is recommended from this analysis — authorised people decide and execute. Escalate to shift supervision and process safety: (a) commission the C5 external check — an independent field measurement of vessel pressure — to bound common cause on channels A and C, which are currently the sole basis of every voted reading; (b) have engineering rule explicitly on whether PT-007 is to be formally reconfigured to 2oo2 or the campaign restricted, since the 2oo2 fallback is presently a model assumption, not a recorded configuration; (c) confirm whether the 2025-11-28 condition change was processed under the facility's MOC rule.

**Restoration:** close WO-RUN_A-CH-B (channel B, 94 d in backlog) with a post-repair test covering the frozen-reading failure mode; execute WO-RUN_A-TEST (proof test of `reator.T1.B1`, 184 d overdue) — this is the check that also settles the C5 pair; execute WO-RUN_A-TRAIN (OP-B2 competence, 124 d overdue), after which the assumed 0.25 must be replaced by the asset value rather than carried forward.

**Definitive solution:** revalidate the barrier windows under the current condition (15 % load, feed setpoint scale 1.15) following `references/producing-a-design-basis.md` steps 2–6, including where the available time now sits — the design plateau was not observed in this regime; run the threat-removal test to close the C8 classification (design basis §6); resolve the PT-007 clock contradiction by declaring which record resets the creep clock; confirm that B2's declared demand trigger (ZT-1001 command-versus-position discrepancy) is instrumented and retrievable, since a demand that cannot be observed cannot be credited or audited (risk-analysis-reference §6).

**Before any action involving B1's final element:** C6 records that closing XV-1001D removes the actuator of the LIC-8001 level cascade, driving level to about −2.5 % and a low-level trip roughly 1 h later. LIT-8001 is at 76.46 % falling 0.0726 %/min. Any recommendation that ends in B1 actuating prevents the T1 top event and initiates a shutdown by an unmapped route; it must be assessed against that, not only against pressure.

**Suggested owner / deadline:** operations shift lead for the field check and the reconfiguration ruling (this shift); maintenance planning for the three work orders (priority above routine backlog, given they are the dominant contributors to the 2.07×); process safety for revalidation and MOC triage (before the campaign continues at the new load).

**Expected return / leading indicator:** channel spread on PIT-7001 back below the 17.5 kPa limit after the channel B repair; PT-007 component multiplier returning toward 1× after the proof test; OP-B2 back to its asset PFD; recurrence count of PIT-7001 LO episodes per day; the rate ladder recomputed after revalidation.

**Closure criteria:** condition controlled; B1 and B2 functions restored **and tested**; no temporary change left unmanaged; the 2oo3 arrangement either restored or the reduced arrangement formally accepted; design basis windows revalidated under the current operating condition; residual risk reassessed against an approved tolerability criterion; C5 and C8 gaps either closed or tracked as open items. The pressure returning inside band does **not** close this occurrence.

**Residual risk / accepting authority:** not determined — no tolerability criterion or consequence basis exists in the supplied documents; acceptance belongs to the facility's designated process safety authority.

**Human decision:** pending

## Evidence and assumptions

- [demonstrated] `envelope.gatilhos_de_invalidacao` / design basis §7, 2025-12-01 — operating-condition change of 2025-11-28 without revalidation; envelope invalidated; §5 windows (202/162/67 min) must not be cited as current.
- [demonstrated] `a2_estado_atual.regime`, 2025-11-28 → 2025-12-01 — voted PIT-7001 median moved from 2708.37 to 2559.51 kPa (−148.86 kPa), n=1986 → n=17; `revalidacao_registrada: false`.
- [corroborated] `a2_estado_atual.canais` + WO-RUN_A-CH-B + `grupo_votado.congelamento` — channel B failed/detected/unrepaired since 2025-08-29, flat at 2708.41 kPa (sd 0.2) at the pre-change regime value; record and series agree.
- [demonstrated] `a3_cruzamentos[C4]` — spread 159.11 kPa vs 17.5 limit; A/C agree within 5.79 kPa; B divergent by majority; repair backlog 94 d.
- [demonstrated] `a3_cruzamentos[C2]` — B1 ×1.11 barrier / PT-007 ×34.36 component, dominant XV-1001 48 %; B2 ×2.27 barrier / PT-007 ×34.36 component, dominant OP-B2 92 %.
- [demonstrated] `motores.conventional` / `motores.fuzzy` — top event 1.754e-03 → 3.636e-03 /yr (2.07×); 2.496e-04 → 4.941e-04 /yr (1.98×), Moderate → Moderate; T1 share 70.1 → 85.6 % (conventional).
- [demonstrated] `a2_estado_atual.ordens_servico` — WO-RUN_A-TEST overdue 184 d; WO-RUN_A-TRAIN overdue 124 d; WO-RUN_A-CH-A closed with finding 2025-04-02.
- [demonstrated] `a2_estado_atual.margem.PIT-7001` + `envelope.degraus` — LO crossed by 0.45 kPa; 170.8 min to LOLO (computed); SIS trip +350.45 kPa; rate ladder −2.76 to −0.94 kPa/min, no window above 2.2.
- [demonstrated] `a3_cruzamentos[C6]` / design basis §4 — detection independent, final element shared (XV-1001, VLV-006); joint credit must not multiply the two PFDs; declared side effect: loss of LIC-8001 inventory control, level ≈ −2.5 %, low-level trip ≈ 1 h later.
- [inferred] conventional engine chains B1×B2 along T1 while C6 refutes actuation independence — the current T1 frequency is optimistic; magnitude of the optimism not quantified here (no approved method).
- [inferred / assumption] `premissas_do_modelo.human_barrier_pfd_with_overdue_competence` = 0.25 — model assumption, not asset data; it supplies 92 % of B2 and therefore drives the dominant pathway.
- [inferred / assumption] `premissas_do_modelo.voted_group_without_reconfiguration` — fall to 2oo2 is assumed, not a recorded configuration change.
- [undetermined] `a2_estado_atual.contradicoes` — PT-007 creep clock (334 d) vs calendar (184 d overdue); item PFD 2.405e-03 vs 3.953e-03 (1.64×); barrier effect ≤1.07×; governing clock is a team decision.
- [undetermined] `a3_cruzamentos[C5]` — common cause on channels A and C cannot be ruled out; external check: independent field pressure measurement.
- [undetermined] `a3_cruzamentos[C8]` / design basis §6 — T1 persistent vs removable not classified; removal test never executed; FIT-1001 flat at zero (rate −0.0000 kscmh/min) is behaviour consistent with a non-clearing threat, not a classification.
- [undetermined] `a3_cruzamentos[C3]` — window compression not measurable: no demand on B1 up to t_now; B2's real window in the current regime is unknown.
- [undetermined] consequence, receptors and tolerability criterion — absent from the bowtie and the design basis; risk not determined.