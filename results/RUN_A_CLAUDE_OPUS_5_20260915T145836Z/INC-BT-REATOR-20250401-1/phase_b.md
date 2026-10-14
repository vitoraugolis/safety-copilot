---
incident_id: INC-BT-REATOR-20250401-1
bowtie_id: BT-REATOR
opened_at: 2025-04-01T00:30:00
engine: conventional
status: action_required
urgency: planned
confidence: medium
---

# Repair PT-007.A under the open corrective work order and confirm how the voting logic reconfigured, while the process itself stays at base-case steady state and requires no operational intervention.

## Fact

A detected, unrepaired channel failure on `PT-007.A` (`a2_estado_atual.canais[0]`: failure 2025-04-01T00:00:00, detection 2025-04-01T00:30:00) with corrective work order `WO-RUN_A-CH-A` open on item PT-007, barrier `reator.T1.B1` (`a2_estado_atual.ordens_servico[0]`). These are the two triggers that opened this analysis (`identidade.gatilho`).

No process criterion was crossed. No active alarms (`a2_estado_atual.alarmes_ativos` empty); no demand on B1 up to `t_now` (`a2_estado_atual.demandas.B1.demandada = false`); no operating-condition change (`a2_estado_atual.regime`). PIT-7001 sits at `a2_estado_atual.margem.PIT-7001.valor`, below HI with `distancia = 45.12` kPa and 195.12 kPa to the SIS trip (`...alvos_declarados[0]`), against a declared base-case steady pressure of 2708 kPa (design basis §2).

Data quality: the voted group agrees — spread `a2_estado_atual.discrepancia_canais[0].spread` = 0.5 kPa against a 17.5 kPa limit, all three pairs within 3× design noise, no divergent channel by majority (`a2_estado_atual.grupo_votado.concordancia_no_ultimo_instante`), no frozen channel (`...canais_parados` empty), per-channel means and standard deviations over the 30-day window mutually indistinguishable (`...estatistica_por_canal`). **The failed channel is therefore not identifiable from the reading**: the record, not the signal, is the evidence of failure. Two limitations on the fact: the rate ladder could not be built (`envelope.lacuna` = "serie insuficiente na janela"), so no rate accompanies any distance in C7; and the work-order narrative is unavailable at `t_now` (`a2_estado_atual.ordens_servico[0].descricao`), so the failure mode of PT-007.A is not stated. The crossing is reproducible as a records event; it is not a process event.

**What this trigger changed** (first analysis in this stream): PT-007 moves from an intact 2oo3 group to **known degraded**, running 2oo2 without reconfiguration (`a3_cruzamentos[C4].resultado`; model assumption `premissas_do_modelo.voted_group_without_reconfiguration`). The item's PFD rises 37.54× against design (`a1_base_de_projeto.barreiras[B1].c2.componente_pior`), and the top event frequency rises by `motores.conventional.razao`.

## Scenario and mechanism

Qualitative chain (pathway T1, `diagrams/BT-REATOR.txt`): loss of stream 1 feed → B1 high-pressure interlock → B2 manual operator action → loss of reactor control (top event) → mitigation and consequence not declared in the loaded bowtie.

Quantitative chain, link by link:

- `PT-007.A` detected failure, unrepaired [`a2_estado_atual.canais[0]`] → **demonstrated** (record).
- Voted group falls from 2oo3 to 2oo2 without reconfiguration → **inferred**: this is a model assumption (`premissas_do_modelo.voted_group_without_reconfiguration`), not a read logic state. Whether UZ-007 actually reconfigured the vote is not in the loaded data.
- PT-007 PFD ×37.54 → barrier PFD `a1_base_de_projeto.barreiras[B1].pfd_atual` versus `pfd_projeto`, barrier multiplier `c2.multiplicador_barreira` = 1.12× [**computed** from `blind_feed.pfd_confiabilidade`]. The component moves two orders of magnitude and the barrier moves 12 %, because the dominant element is the final element XV-1001 at 47.6 % of the total (`...c2.elemento_dominante`), not the sensor. Same mechanism on B2: component 37.54×, barrier 1.02×, dominated by OP-B2 at 81.7 %.
- Top event frequency: design `motores.conventional.projeto.evento_topo_por_ano` → current `motores.conventional.atual.evento_topo_por_ano`, ratio `motores.conventional.razao`; T1's share of the top event rises from 70.1 % to 73.0 % (`motores.conventional.*.pathways[0].contribuicao_pct`).
- Consequence and receptor: **not declared** in the loaded inputs. The chain stops at top event frequency.

No process link exists in this episode: pressure is not escalating and B1 was not demanded. The mechanism here is reliability erosion visible only in the maintenance and channel records — exactly the mechanism a process-value detector cannot see.

## Analysis

### 1. Bowtie

**B1 — high-pressure interlock: `degraded`.** Not `critical`: it was not demanded (`a2_estado_atual.demandas.B1`), it is not bypassed or isolated, and its PFD is within 1.12× of design. Not `healthy`: the 2oo3 detection group has lost a channel and, under the declared arrangement, has no fault tolerance left before a second channel failure defeats or spuriously actuates the vote. C4 classifies it **known degraded**, and the applicable clock is the repair backlog — `a3_cruzamentos[C4].relogio` = 0 d since detection — not a test interval. That distinction is the good news of this trigger: had the failure been hidden, exposure would run to the next functional test.

**B2 — manual operator action: `degraded`**, at a barrier multiplier of 1.02× (`a1_base_de_projeto.barreiras[B2].c2.multiplicador_barreira`), driven by the same PT-007 contribution. **Recorded contradiction:** the reliability model lists PT-007 among B2's components (`a1_base_de_projeto.barreiras[B2].componentes`, `detalhe_componentes`), while the design basis declares B2's detection to be ZT-1001 and explicitly independent of B1's detector (design basis §4; `a1_base_de_projeto.declarado.independencia.deteccao`). Both sources are presented; the divergence is not resolvable from the loaded data and it matters, because if B2 truly carries PT-007 the two barriers share detection as well as actuation.

**Independence / IPL credit.** C6 is unambiguous on what *is* known: detection independent (PT-007 vs ZT-1001), **actuation shared** (XV-1001 and VLV-006), and "joint credit must not multiply the two PFDs" (`a3_cruzamentos[C6].comparado.declared_independence`). A single failure of XV-1001 or VLV-006 removes both barriers on pathway T1. No IPL or SIL credit is granted here: the loaded inputs carry no approved credit decision (risk-analysis reference §2).

**Declared side effect (C6).** B1's action closes the A+C feed valve, which actuates the LIC-8001 level cascade; inventory control is lost, level goes to about −2.5 % and a low-level trip follows roughly 1 h later (`a3_cruzamentos[C6].comparado.declared_side_effect`). B1 prevents the T1 top event and causes a shutdown by an unmapped route. This is a declared secondary consequence, not a barrier failure (design basis §5, success criterion).

**C3** is not applicable at `t_now` — no demand on B1, so the real HIHI→SIS window is not measurable (`a3_cruzamentos[C3]`). Consequently B2's 67 min tolerable delay against the 162 min design window (`a3_cruzamentos[C3].comparado`) remains a design-basis figure that this episode has neither confirmed nor invalidated.

### 2. Process

All five flagged tags are inside band and no threshold has been crossed (`a2_estado_atual.margem.*.limiares_ja_cruzados` empty). PIT-7001 at 2704.88 kPa sits essentially at the declared base-case steady value of 2708 kPa (design basis §2); TIT-9001 at 120.39 °C against 120.4 °C declared; LIT-8001 at 74.97 % against 74.4 %. FIT-1001 at 0.2128 kscmh is below the declared base-case feed of 0.252 kscmh but above the LO threshold of 0.15 (`a1_base_de_projeto.limiares`), and with no rate available this single value supports no trend conclusion.

**C7 is incomplete by data, not by omission:** every distance is reported without a rate, because `taxa_por_min` is null for all tags and the rate ladder is empty (`envelope.degraus`). Per the skill's honesty rules, no conclusion is drawn from these instantaneous values beyond "no threshold crossed"; in particular, no time-to-target is asserted.

**C1** returns "no escalation window at t_now" with no rate ladder and no design rate compared (`a3_cruzamentos[C1].comparado`). The envelope is therefore **not demonstrated valid**, merely untested: none of the four invalidation triggers of design basis §7 was evaluated against data in this window. Citing the §5 windows (202 / 162 / 67 min) as currently applicable would be unsupported.

### 3. Context

The design basis is loaded and complete for pathway T1 (`a1_base_de_projeto.base_de_projeto_declarada = true`, `references/design-basis-barriers.md`, converted 2026-09-11).

Integrity and testing: PT-007 has **no test record**; the declared test interval is taken as met by model assumption (`a1_base_de_projeto.barreiras[B1].motivos`; `premissas_do_modelo.items_without_test_records`). The credited PFD therefore rests on assumed proof-test compliance, with no evidence in the loaded data either way. Absence of a record is a gap, not proof of non-compliance.

Records consistency: the corrective work order is timestamped 2025-04-01T00:00:00, the same instant as the failure and 30 min **before** the recorded detection at 00:30 (`a2_estado_atual.ordens_servico[0].data_abertura` vs `a2_estado_atual.canais[0].ts_deteccao`). Both are presented; the ordering is not explicable from the loaded data, and the WO narrative that might explain it is unavailable at `t_now`.

Management of change: none recorded — no operating-condition change up to `t_now` (`a2_estado_atual.regime.nota`), no threshold or voting-arrangement change reported.

Human factors: B2's PFD is 81.7 % OP-B2, and the design basis states that essentially all of B2's margin is perception and decision, not execution (design basis §5). Nothing in this trigger bears on operator competence; the six-monthly training interval is declared (design basis §4) and no overdue training work order exists in `a2_estado_atual.ordens_servico`.

Threat classification: **gap**. T1 is not classified persistent vs removable; the removal test was not executed (`a3_cruzamentos[C8].lacuna`, design basis §6). The success criterion that should be applied to B1 and B2 in a real T1 event therefore rests on an unverified assumption.

## Risk judgement

Top event frequency, both engines, design → current (`motores`):

| Engine | Design /yr | Current /yr | Ratio |
|---|---|---|---|
| conventional | `motores.conventional.projeto.evento_topo_por_ano` | `motores.conventional.atual.evento_topo_por_ano` | `motores.conventional.razao` = 1.1× |
| fuzzy | `motores.fuzzy.projeto.evento_topo_por_ano` | `motores.fuzzy.atual.evento_topo_por_ano` | `motores.fuzzy.razao` = 1.16× |

The conventional figure is the magnitude; the fuzzy figure carries linguistic uncertainty only, and the two must not be read as checks on each other (`motores.nota`). The fuzzy label stays `Moderate → Moderate` (`motores.fuzzy.*.rotulo`) — a label qualifying a frequency, not a barrier state and not risk, and not an acceptance criterion.

Pathway T1's contribution rises from 70.1 % to 73.0 % of the top event (conventional, `motores.conventional.*.pathways[0].contribuicao_pct`), i.e. this trigger shifts the dominant path further towards T1.

**Consequence, receptors and tolerability are not declared in the loaded inputs.** Therefore the conclusion is: *barrier erosion demonstrated; risk tolerability not determined.* That is the result, not a failure of the analysis.

Uncertainty, and why confidence is `medium` rather than high: (i) the 2oo2 fall is an assumption, not a read logic state; (ii) PT-007's credited PFD assumes an unrecorded proof test; (iii) no rate exists in this window, so C1 and C7 are informational only; (iv) the B2 component list contradicts the design basis on whether PT-007 is in B2's detection path; (v) the T1 threat classification is missing. Uncertainty does not lower the risk — it lowers confidence and argues for the conservative reading of (iv).

**Urgency: planned.** No excursion, no demand, no active alarm, 45.12 kPa to HI and 195.12 kPa to the SIS trip, and the C4 clock is a repair backlog at 0 d — not a test interval. Nothing here meets a safety-limit condition of SKILL.md ("Safety limits"): no loss of containment, no approach to a trip, no condition outside the safe envelope, no plausible catastrophic scenario at this instant. The counterweight is that redundancy, not just margin, has been consumed: a second PT-007 channel failure before repair would change the class of this occurrence.

## Recommendation

**Immediate containment:** none on the process — the process requires no intervention at `t_now`. Treat PT-007 as running without detection redundancy until repaired, and avoid any planned maintenance, test or bypass that would touch PT-007.B, PT-007.C, XV-1001 or VLV-006 while `WO-RUN_A-CH-A` is open (C6: XV-1001 and VLV-006 are shared by B1 and B2).

**Restoration:** repair PT-007.A under `WO-RUN_A-CH-A` and restore the 2oo3 arrangement, with a post-repair functional test covering the failure mode found; confirm from the logic configuration whether UZ-007 actually reconfigured to 2oo2, since the current PFD rests on that assumption; record the failure mode in the work order, which is currently unavailable.

**Definitive solution:** establish and retain proof-test/calibration records for PT-007 so the credited PFD stops depending on an assumption; resolve the contradiction between the B2 component list and design basis §4 on PT-007 vs ZT-1001, and reflect the outcome in the joint-credit decision for B1+B2; execute the threat-removal test to close the C8 classification (design basis §6); revalidate the §5 windows, which this episode could not test. Note the response hierarchy: these are administrative and verification measures; the shared final element (XV-1001, VLV-006) remains the structural single point of failure on pathway T1 and is the engineering item worth a separate study.

**Suggested owner / deadline:** instrumentation maintenance for the PT-007.A repair and post-repair test, at the standard corrective backlog priority for a detected failure in a voted safety group; process safety / bowtie custodian for the B2 component contradiction, the C8 test and the window revalidation. Deadlines to be set by the facility's authority — not fixed here.

**Risks introduced by the action itself:** work on the PT-007 group while one channel is already failed can cause a spurious actuation of B1, whose declared side effect is loss of inventory control and a low-level trip about 1 h later (C6). Plan the intervention accordingly.

**Expected return / leading indicator:** PT-007 component PFD back to its design value and B1's barrier multiplier back to 1.00×, with the top event frequency returning towards `motores.conventional.projeto.evento_topo_por_ano`; leading indicators — days of open corrective backlog on voted safety channels, and channel spread of PIT-7001 against the 17.5 kPa limit.

**Closure criteria:** PT-007.A repaired **and** functionally tested; 2oo3 arrangement demonstrated restored; `WO-RUN_A-CH-A` closed with the failure mode recorded; PFDs recomputed and the top event frequency reassessed; no temporary change left open. The process being in band does not close this occurrence — the process was never out of band.

**Residual risk / accepting authority:** not determined (no consequence or tolerability criterion in the loaded inputs); acceptance belongs to the facility's designated authority.

**Human decision:** pending

## Evidence and assumptions

- [demonstrated] `a2_estado_atual.canais[0]`, 2025-04-01 — PT-007.A failed, detected 00:30, unrepaired, tied to `WO-RUN_A-CH-A`.
- [demonstrated] `a2_estado_atual.ordens_servico[0]` — one open corrective WO on PT-007, barrier reator.T1.B1; narrative unavailable at `t_now`.
- [demonstrated] `a2_estado_atual.demandas.B1` — no demand on B1 up to `t_now`; C3 therefore not applicable.
- [demonstrated] `a2_estado_atual.grupo_votado` + `discrepancia_canais[0]` — spread 0.5 kPa vs 17.5 limit, all pairs within 3× design noise, no frozen channel, no majority outlier: the failed channel is not identifiable from the signal.
- [demonstrated] `a1_base_de_projeto.barreiras[*].c2` — component 37.54×, barrier 1.12× (B1) and 1.02× (B2); dominant elements XV-1001 (47.6 %) and OP-B2 (81.7 %).
- [demonstrated] `motores.conventional` / `motores.fuzzy` — top event frequency design→current, ratios 1.1× and 1.16×; fuzzy label Moderate→Moderate; T1 share 70.1 %→73.0 %.
- [demonstrated] `a3_cruzamentos[C6]` and design basis §4–§5 — detection independent, actuation shared; joint credit must not multiply the two PFDs; declared side effect on the LIC-8001 level cascade.
- [corroborated] design basis §2 vs `a2_estado_atual.margem` — pressure, temperature and level at `t_now` match the declared base case; feed flow below the declared base-case value, without a rate.
- [inferred] `premissas_do_modelo.voted_group_without_reconfiguration` — the 2oo3→2oo2 fall is a model assumption; the actual logic state is not in the loaded data.
- [inferred] `premissas_do_modelo.items_without_test_records` + `a1_base_de_projeto.barreiras[B1].motivos` — PT-007 kept at design PFD for untested components because the declared interval is assumed met; no test record exists.
- [undetermined] `a1_base_de_projeto.barreiras[B2].componentes` vs `a1_base_de_projeto.declarado.independencia` — PT-007 appears in B2's component list while the design basis declares B2 detection independent via ZT-1001. Contradiction recorded; not resolvable from the loaded data.
- [undetermined] `envelope.lacuna` / `a3_cruzamentos[C1]` — rate ladder empty ("serie insuficiente na janela"); envelope neither confirmed nor invalidated; no invalidation trigger of design basis §7 evaluated against data.
- [undetermined] `a3_cruzamentos[C8].lacuna` — T1 persistent-vs-removable classification not executed; success criterion for a real T1 event rests on an unverified basis.
- [undetermined] `a2_estado_atual.ordens_servico[0].data_abertura` vs `canais[0].ts_deteccao` — WO opened 30 min before the recorded detection; ordering unexplained at `t_now`.
- [undetermined] consequence, receptors and tolerability — not present in the loaded inputs; risk not determined.
- Fuzzy figures are cited only for linguistic-uncertainty propagation, never as a check on the conventional magnitude (`motores.nota`). No IPL/SIL credit is granted in this report; the bowtie organises, it does not prove.