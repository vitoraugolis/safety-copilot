# Restore PT‑007 to its design credit and keep BT‑REATOR/T1 under routine monitoring: the corrective work order on channel A is closed with a finding, all barrier PFDs are back at design, and no residual condition requires operational action — but do not treat the episode as closed until the envelope and the 2oo3 proof test are evidenced independently of the work‑order narrative.

## Fact

Two record‑side triggers, both at `t_now` = 2025‑04‑02T00:00:00 (`identidade.gatilho`): `record:wo_closed:WO-RUN_A-CH-A` (corrective, item PT‑007, barrier `reator.T1.B1`, `falha_encontrada = 1`) and `record:channel_repaired:PT-007.A`. No process parameter crossed any criterion: `a2_estado_atual.alarmes_ativos` is empty and `a2_estado_atual.demandas.B1.demandada = false`.

Exposure interval of the channel failure, from `a2_estado_atual.canais[PT-007.A]`: failure 2025‑04‑01T00:00:00, detection 2025‑04‑01T00:30:00, repair 2025‑04‑02T00:00:00 — a **detected**, not hidden, degradation, with the work order opened the same day (`a2_estado_atual.ordens_servico[WO-RUN_A-CH-A].data_abertura`). No other work order is open or overdue in the window.

Current state at `t_now`: all five flagged tags below their next threshold, none crossed (`a2_estado_atual.margem`), with PIT‑7001, TIT‑9001, LIT‑8001 and FIT‑1001 sitting essentially at the declared design base case (`a1_base_de_projeto.declarado.condicao_de_projeto`). `a2_estado_atual.regime.mudanca = null`.

**Data quality.** The rate ladder is empty — `envelope.lacuna = "serie insuficiente na janela"` — so every line of `a2_estado_atual.margem` carries distance with `taxa_por_min = null` and `tempo_ate_limiar_min = null`. The crossing that opened this analysis is a record event and is reproducible from the work‑order and channel tables; the process side of the trigger is not in question because there is no process excursion. The absence of a rate means no trajectory claim can be made here (SKILL.md, honesty rules: "do not conclude from an instantaneous value").

## Scenario and mechanism

Qualitative chain (`a1_base_de_projeto`, diagram `BT-REATOR`): threat T1, loss of stream 1 feed → preventive barriers B1 (automatic high‑pressure interlock, demand `voted PIT-7001 ≥ HIHI`) then B2 (manual operator action, demand = command‑versus‑position discrepancy on ZT‑1001, i.e. only after B1 has tried and failed) → top event "loss of reactor control" → consequence not declared in the supplied basis.

Quantitative chain for **this** trigger, which is a *restoration*, not an escalation:

`PT-007.A channel discrepancy (a2_estado_atual.canais)` → detection element of B1 and shared detection input of the group → `a1_base_de_projeto.barreiras[B1].detalhe_componentes[PT-007].fator = 1.0` and `barreiras[B2].detalhe_componentes[PT-007].fator = 1.0` at `t_now` → `c2.multiplicador_barreira = 1.0` for both barriers → `motores.conventional.razao = 1.0` and `motores.fuzzy.razao = 1.0`.

**What this trigger changed.** The corrective work order that carried PT‑007 through the degraded interval is closed with a finding and channel A is repaired, so the exposure clock opened on 2025‑04‑01 stops at `t_now`, the voted group returns to intact by record *and* by reading (`a3_cruzamentos[C4].resultado`), and B1's detection element returns to its design contribution. Nothing else in the pathway moved.

Strength of the links: the channel repair and the closure with finding are **demonstrated** (primary records); the statement that the group is now intact is **corroborated** (record and reading agree, `a2_estado_atual.discrepancia_canais` and `a2_estado_atual.grupo_votado` converge); the claim that the repair fixed the failure mode rests on the work‑order narrative alone ("reteste OK", `a2_estado_atual.ordens_servico[…].descricao`) and is **inferred** — no independent proof‑test record is in the context.

## Analysis

### 1. Bowtie

**B1 — `healthy`.** Requirement demonstrated and within validity: `a1_base_de_projeto.barreiras[B1].c2.multiplicador_barreira = 1.0`, worst component PT‑007 also at `1.0×`. Both C2 multipliers are therefore unity — the component's and the barrier's. Dominant element remains **XV‑1001**, `c2.elemento_dominante.fracao_do_total = 0.536`; the repaired detection element contributes `detalhe_componentes[PT-007].pfd = 7e-05`, more than two orders of magnitude below it. The intervention restored a minor contributor: B1's PFD is still governed by the final element, which this work order did not touch.

**B2 — `healthy` by the record, with a standing qualification.** `barreiras[B2].c2.multiplicador_barreira = 1.0`, dominant element **OP‑B2** at `fracao_do_total = 0.834`. The design basis states that OP‑B2's whole margin is perception and decision, not execution (design basis §5), so its PFD is a function of the available window, and the window is a property of the operating condition. At `t_now` there is no excursion, so C3 records `real window not measurable at t_now` (`a3_cruzamentos[C3].resultado`, `nao_se_aplica = "no demand on B1 up to t_now"`). B2's design PFD is therefore carried unverified against the current condition rather than verified — a known limit of this analysis, not a degradation.

**Voted group (C4).** 2oo3 on PT‑007, `intact by record and reading`; spread 0.81 kPa against a declared limit of 17.5 (`a2_estado_atual.discrepancia_canais`), all three pairs agreeing within the 5.79 kPa tolerance and `divergente_pela_maioria = null` (`a2_estado_atual.grupo_votado.concordancia_no_ultimo_instante`). Per‑channel statistics over the 30‑day window are mutually consistent (sd 1.79/1.80/1.84 against design noise 1.93 kPa), `canais_parados` empty and `congelamento = null` — no frozen or drifting channel is supported by the data. The applicable clock is now the **test interval** (`a3_cruzamentos[C4].relogio`), not a repair horizon.

**Demand.** None on B1 up to `t_now` (`a2_estado_atual.demandas.B1`), so no outcome settles either state; the states above are PFD‑and‑record based, as they must be.

**Independence (C6) — the material bowtie finding of this analysis.** `a3_cruzamentos[C6]`: detection independent (PT‑007 versus ZT‑1001), **actuation shared** (XV‑1001 and VLV‑006), with the explicit consequence that *joint credit must not multiply the two PFDs*. The conventional engine nonetheless folds B1 and B2 as successive AND nodes on pathway T1 (`motores.conventional.atual.pathways[0].nos`). The cited top‑event frequency is therefore computed on an independence assumption the design basis denies, and it is **non‑conservative** for that pathway. Per SKILL.md B3, no IPL/SIL credit should be granted on the strength of the diagram alone, and the shared final element is evidence against independence.

**Declared side effect (C6).** B1's action closes the A+C feed valve, which is the actuator of the LIC‑8001 level cascade; inventory control is lost, level goes to about −2.5 % and a low‑level trip follows roughly 1 h later. This coupling is unmapped in the bowtie and must be carried as a declared secondary consequence of any B1 actuation — relevant to any recommendation that would exercise B1.

**Recorded contradiction.** For both barriers the design basis document PFD and the asset‑table sum disagree: `barreiras[B1].pfd_documento.valor = 0.01` versus `pfd_projeto.valor = 0.02053`; `barreiras[B2].pfd_documento.valor = 0.1` versus `pfd_projeto.valor = 0.11987`. Both sources are presented; the engines were fed the asset‑sum values (`motores.pfd_atual`). Which of the two is the approved basis is not settled by the supplied context.

### 2. Process

Trajectory cannot be analysed: `envelope.degraus = []` with `lacuna = "serie insuficiente na janela"`, so `a2_estado_atual.escada_de_taxas` carries no step and C1 returns `no escalation window at t_now`. C7 is therefore reported as distance only, with `taxa_por_min = null` on every tag — I present it that way and draw no trend conclusion from it.

Static position against the envelope (`a2_estado_atual.margem` versus `a1_base_de_projeto.declarado.condicao_de_projeto`): PIT‑7001 2707.46 kPa against a declared steady 2708 kPa, 42.54 kPa below HI 2750, 192.54 below the SIS trip 2900 (`alarm_config.trip_sis`) and 292.54 below the model physical limit 3000 (design basis §3); TIT‑9001 120.42 °C against a declared 120.4; LIT‑8001 74.17 % against 74.4; FIT‑1001 0.2568 kscmh against 0.252 — feed present, so the T1 threat is not manifest; TIT‑2101 94.49 °C, 5.51 below HI 100 and above LO 88. No threshold crossed anywhere (`limiares_ja_cruzados` empty on all tags).

Invalidation triggers (design basis §7, `a1_base_de_projeto.declarado.invalidacao`): no operating‑condition change recorded (`a2_estado_atual.regime`), no threshold change and no voting‑arrangement change appear in the context; the rate trigger (>2.2 kPa/min) **cannot be evaluated** because no rate exists in the window. The envelope is therefore *not contradicted* at `t_now`, which is not the same as *verified*.

### 3. Context

Maintenance record: one work order in the window, `WO-RUN_A-CH-A`, corrective on PT‑007, opened 2025‑04‑01, closed 2025‑04‑02, `classe = closed_with_finding`, narrative "Discrepancia do canal A do PT‑007; rele/canal substituido e reteste OK". A failure found on demand‑capable detection hardware is evidence of a real failure mode, and the response time — detection within 30 min, repair within 24 h — is the behaviour of a functioning corrective loop. No overdue test, calibration or training work order appears, and no operational event is recorded (`a2_estado_atual.eventos_operacionais = []`).

Recovery rules that bound what I can see (`a2_estado_atual.regra_de_recuperacao`): channel state comes from `blind_feed.canais_visiveis`, so a failure not yet detected at `t_now` is masked; reliability PFDs include only failures known by `t_now`. The absence of a second degraded channel in the record is therefore not proof that none exists.

Model assumptions that bear on the reading (`premissas_do_modelo`): `items_without_test_records` keeps items at design PFD where no test record exists — so a design‑value PFD here may reflect an absent record rather than a demonstrated test; and `single_channel_item_with_known_failure` sets PFD = 1 only while the work order is open, which is why the closure at `t_now` returns the item to design in one step. Both are assumptions, not asset data.

Human and organisational factors: OP‑B2 dominates B2 at 83 % of its PFD, with a declared six‑monthly training interval (design basis §4). No training record — met or overdue — is present in this context, so competence currency is carried on the `items_without_test_records` assumption rather than on evidence.

Open gaps, although C5 named none (`a3_cruzamentos[C5].resultado = "0 named gap(s)"`):

- **Threat classification T1** — `a3_cruzamentos[C8].lacuna`: the removal test (design basis §6) was not executed. Persistent versus removable is undetermined, so the success criterion expected of B1/B2 under a real T1 remains unsettled.
- **No rate in the window** — `envelope.lacuna`. External check: retrieve the PIT‑7001 series at a sampling interval sufficient to compute the C1 ladder over the declared windows.
- **Proof test of the 2oo3 vote after repair** — the only evidence is the work‑order narrative. External check: a functional test record covering the vote resolution, not only the replaced relay/channel.
- **Which PFD basis is approved** — `pfd_documento` versus `pfd_projeto` diverge for both barriers.

## Risk judgement

Top event frequency, cited from phase A and not recomputed: conventional `motores.conventional.projeto.evento_topo_por_ano` → `motores.conventional.atual.evento_topo_por_ano`, `razao = 1.0`; fuzzy `motores.fuzzy.projeto.evento_topo_por_ano` → `motores.fuzzy.atual.evento_topo_por_ano`, label `Moderate → Moderate`, `razao = 1.0`. The conventional figure is the magnitude; the fuzzy figure carries the propagation of linguistic uncertainty and is not a check on the other (`motores.nota`). Pathway split at current: conventional `[70.1, 29.9]`, fuzzy `[74.2, 25.8]` — pathway T1 remains the dominant contributor under both engines.

The current figure equals the design figure because every barrier multiplier is `1.0×`. Two qualifications attach to it: it is computed on independence between B1 and B2 that C6 denies, so it is a lower bound for pathway T1; and it is computed on PFDs whose document values disagree with the asset values (see the recorded contradiction).

Consequence and receptors are **not declared** in the supplied context, and no tolerability criterion is supplied. Following SKILL.md B4, the correct conclusion is: **barrier state restored to design; risk tolerability not determined.** The label `Moderate` qualifies a frequency, not a barrier state and not risk.

Urgency: **routine**. Basis — no active alarm, no demand, every tag inside its band with the nearest declared target 42.54 kPa away on PIT‑7001, and both preventive barriers at design PFD. Time available cannot be computed from C7 because no rate exists; that limits confidence, not the classification, since no excursion is in progress. The C4 clock is now the test interval, the long horizon, which is appropriate for an intact group.

Status: **monitoring** — not `closed`. The closure gate requires the barrier function restored *and tested*, and the design basis windows revalidated under the current condition. The test evidence here is a work‑order narrative and the envelope is unevaluated for want of a rate.

Confidence: **medium**, bounded by the weakest decisive link — the post‑repair test evidence is `inferred`, and the masking rule on channel visibility means an undetected second‑channel failure would not appear.

## Recommendation

**Immediate containment:** none required. No condition at `t_now` warrants operational intervention (`a2_estado_atual.alarmes_ativos` empty, `demandas.B1.demandada = false`, no threshold crossed in `a2_estado_atual.margem`). Do not exercise B1 as a verification step: its declared side effect (C6) destroys inventory control and leads to a low‑level trip roughly 1 h later.

**Restoration:** already executed and recorded — `WO-RUN_A-CH-A` closed with finding, `PT-007.A` repaired. Confirm it with evidence independent of the narrative: a functional test record of the 2oo3 vote resolution (not only the replaced channel), attached to the work order, and a proof‑test date that restarts the C4 test clock explicitly.

**Definitive solution:** the interventions with real leverage are not the one just completed. In the response hierarchy (risk‑analysis reference §6), and noting that none of these acts on an already degraded barrier:

1. Address **XV‑1001**, 54 % of B1's PFD (`barreiras[B1].c2.elemento_dominante`) — partial‑stroke testing or an equivalent coverage improvement on the final element, as an engineering measure.
2. Resolve the **shared final element** between B1 and B2 (C6). Until then, prohibit multiplying the two PFDs in any credit decision and record the engines' pathway‑T1 figure as non‑conservative.
3. Execute the **threat‑removal test** for T1 (design basis §6) so C8 has a classification and the barrier success criterion is defined rather than assumed.
4. Reconcile `pfd_documento` against `pfd_projeto` for B1 and B2 and declare which is approved.
5. Restore the process history needed for C1: the rate ladder could not be built in this window.

**Suggested owner / deadline:** instrumentation and control maintenance for the proof‑test evidence (with the work‑order closure, so within the current cycle); process safety for items 2–4; the data/historian owner for item 5. Deadlines are for the facility's authority to set.

**Expected return / leading indicator:** PT‑007 channel spread staying within the declared limit of 17.5 kPa (`a2_estado_atual.discrepancia_canais.limite`) with per‑channel sd near the 1.93 kPa design noise; zero recurrence of channel‑A discrepancy before the next scheduled test; B1 barrier multiplier holding at `1.0×`.

**Closure criteria:** (i) functional test of the 2oo3 vote recorded and passed after the repair; (ii) PT‑007 spread and per‑channel variance stable over a technically justified window following the repair; (iii) the C1 rate ladder computable and the design basis windows revalidated against the current condition, or the gap formally accepted; (iv) items 1–4 above tracked as open actions and not hidden behind this closure. The absence of an excursion does not close the occurrence.

**Residual risk / accepting authority:** residual risk is the design‑basis residual plus the non‑conservatism introduced by the independence assumption in the engines (C6) and the undetermined T1 classification (C8). Consequence and tolerability are not declared here; acceptance is for the facility's authority, not this analysis.

**Human decision:** pending

## Evidence and assumptions

- [demonstrated] `a2_estado_atual.ordens_servico[WO-RUN_A-CH-A]`, opened 2025‑04‑01, closed 2025‑04‑02, `classe = closed_with_finding`, `falha_encontrada = 1` — a real failure mode was found and corrected on PT‑007 channel A.
- [demonstrated] `a2_estado_atual.canais[PT-007.A]` — failure 2025‑04‑01T00:00:00, detected 00:30, repaired at `t_now`: detected degradation with a ~24 h repair horizon, not a hidden one.
- [corroborated] `a3_cruzamentos[C4]` with `a2_estado_atual.discrepancia_canais` and `a2_estado_atual.grupo_votado` — group intact by record and by reading; spread 0.81 kPa against 17.5; no divergent channel by majority; no frozen channel.
- [demonstrated] `a1_base_de_projeto.barreiras[B1].c2` and `[B2].c2` — both C2 multipliers at `1.0×`; dominant elements XV‑1001 (53.6 % of B1) and OP‑B2 (83.4 % of B2) unaffected by this intervention.
- [demonstrated] `motores.conventional.razao = 1.0`, `motores.fuzzy.razao = 1.0`, fuzzy label `Moderate → Moderate` — no change in top event frequency between design and current.
- [demonstrated] `a3_cruzamentos[C6]` and design basis §4 — detection independent, actuation shared; joint credit must not multiply the two PFDs; B1's action destroys level control and leads to a low‑level trip roughly 1 h later.
- [inferred] Post‑repair adequacy — supported only by the work‑order narrative "reteste OK"; no independent functional‑test record of the vote is present. Assumption identified: `premissas_do_modelo.single_channel_item_with_known_failure` returns the item to design PFD at closure.
- [undetermined] T1 persistent versus removable — `a3_cruzamentos[C8].lacuna`: removal test not executed (design basis §6).
- [undetermined] Envelope status — `envelope.lacuna = "serie insuficiente na janela"`; C1 returns `no escalation window at t_now`; the >2.2 kPa/min invalidation trigger could not be evaluated.
- [undetermined] Which PFD basis is approved — `pfd_documento` (0.01 / 0.1) versus `pfd_projeto` (0.02053 / 0.11987) for B1 and B2; both recorded, neither settled.
- [assumption] `premissas_do_modelo.items_without_test_records` — items with no test, calibration or training record are held at design PFD, including OP‑B2's competence currency.
- [assumption] `a2_estado_atual.regra_de_recuperacao.channels` — a channel failure not detected by `t_now` is masked; the intact group state is therefore "intact as far as the record can show".