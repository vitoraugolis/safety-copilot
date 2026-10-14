## Phase A context · INC-BT-REATOR-20250730-1

`run=RUN_A` · `t_now=2025-07-30T00:00:00` · `window_from=2025-06-30T00:00:00` · `bowtie=BT-REATOR` · pathway `T1` · database `safety_copilot_v2.db`
Horizon from 2025-01-01T00:00:00. Design basis: `references/design-basis-barriers.md`.

**Trigger(s) that opened this analysis:** `record:wo_opened:WO-RUN_A-TRAIN`; `record:wo_overdue:WO-RUN_A-TRAIN`

### Active alarms

None.

### Distance and rate, side by side (C7)

| Tag | Value | Crossed | Next threshold | Distance | Rate /min | Declared targets |
|---|---|---|---|---|---|---|
| PIT-7001 | 2704.9992 kPa | — | HI 2750.0 | 45.00 | — | SIS trip 2900: +195 [alarm_config.trip_sis]; model physical limit 3000: +295 [design basis, section 3] |
| TIT-9001 | 120.3866 C | — | HI 135.0 | 14.61 | — | — |
| LIT-8001 | 75.0621 % | — | HI 85.0 | 9.94 | — | — |
| FIT-1001 | 0.2501 kscmh | — | —  | — | — | — |
| TIT-2101 | 94.6167 C | — | HI 100.0 | 5.38 | — | — |

### Voted group PIT-7001 (C4)

- `PT-007.A` record: **ok**, detected 2025-04-01T00:30:00, repaired 2025-04-02T00:00:00 (WO-RUN_A-CH-A)
- `PT-007.B` record: **no_discrepancy_reported**
- `PT-007.C` record: **no_discrepancy_reported**
- reading at t_now: {'A': 2704.61, 'B': 2705.01, 'C': 2704.96} · spread **0.4** kPa against a limit of 17.5 (5% da faixa lolo..hihi de alarm_config) · deviation from median {'A': -0.35, 'B': 0.05, 'C': 0.0}
- per-channel statistics over 2025-06-30T00:00:00 → 2025-07-30T00:00:00 (computed): A mean 2708.21 sd 1.86 range 2703.46–2712.6; B mean 2708.23 sd 1.9 range 2703.75–2712.78; C mean 2708.22 sd 1.92 range 2703.36–2713.53
- agreement at t_now within 5.79 kPa (3× design noise 1.93 kPa, design basis §3): pairs [('A', 'B'), ('A', 'C'), ('B', 'C')]; divergent by majority: None

### Demand outcome per barrier (anchored on each barrier's own demand)

- **B1**: no demand on B1 recorded up to t_now

### Work orders

| WO | Type | Item | Class | Opened | Due | Overdue (d) | Description |
|---|---|---|---|---|---|---|---|
| WO-RUN_A-CH-A | corretiva | PT-007 | closed_with_finding | 2025-04-01T00:00:00 | — | — | Discrepancia do canal A do PT-007; rele/canal substituido e reteste OK. |
| WO-RUN_A-TEST | teste_funcional | PT-007 | overdue_not_executed | 2025-05-31T00:00:00 | 2025-05-31T00:00:00 | 60 | Teste funcional do intertravamento (reator.T1.B1) VENCIDO e nao executado. |
| WO-RUN_A-TRAIN | treinamento | OP-B2 | overdue_not_executed | 2025-07-30T00:00:00 | 2025-07-30T00:00:00 | 0 | Treinamento periodico de competencia (reator.T1.B2) VENCIDO; WO aberta automaticamente. |

### Barriers (A1 + C2)

| Barrier | Design PFD | Current PFD | Barrier × | Worst component | Dominant element |
|---|---|---|---|---|---|
| B1 High-pressure interlock | 2.053e-02 | 2.050e-02 | **1.0×** | UZ-007 1.0× | XV-1001 (54%) |
| B2 Manual operator action | 1.199e-01 | 2.698e-01 | **2.25×** | OP-B2 2.5× | OP-B2 (93%) |
- B2: OP-B2: 2.5x - test overdue by 28 d (interval 182 d); competence renewal overdue and open; PFD assumed 0.25 (model assumption, not declared in the asset)

### Top event frequency, design versus current, both engines (computed)

| Engine | Design /yr | Current /yr | Ratio | Label design → current | Pathway % current |
|---|---|---|---|---|---|
| conventional | 1.754e-03 | 3.289e-03 | 1.88× | — → — | [84.1, 15.9] |
| fuzzy | 2.496e-04 | 4.323e-04 | 1.73× | Moderate → Moderate | [87.8, 12.2] |
- current barrier PFDs fed to the engines: {'B1': 0.020499, 'B2': 0.269839, 'B3': 0.01178, 'B4': 0.11112}. conventional engine for magnitude; fuzzy engine for the propagation of linguistic uncertainty (SKILL.md, 'The fuzzy engine'). Never one as a check on the other.

### Contradictions between sources (recorded, not resolved)

- `PT-007` — PFD creep clock: "210 d since the last test (interval 365 d)" **versus** maintenance calendar (WO-RUN_A-TEST): "teste_funcional overdue by 60 d". Rule A: resets on the last CLOSED test/calibration/training work order; a corrective order does not reset it. Sensitivity (computed): last test implied by the calendar 2024-05-31T00:00:00 (due date minus the declared test interval (365 d); an assumption, not a record); item PFD 3.935e-05 by the model clock versus 8.284e-05 by the calendar (2.11×); per barrier {'B1': {'pfd_relogio_do_modelo': 0.020499, 'pfd_relogio_do_calendario': 0.020543, 'razao': 1.0}, 'B2': {'pfd_relogio_do_modelo': 0.269839, 'pfd_relogio_do_calendario': 0.269883, 'razao': 1.0}}. Both readings come from the same database and disagree. Phase A reports the PFD under each; which clock governs is a decision for the team.

### Cross-checks

| # | Result | Gap / not applicable |
|---|---|---|
| C1 Envelope: current versus validated dynamics | no escalation window at t_now | — |
| C2 PFD decomposition: component versus barrier | both multipliers reported per barrier | — |
| C3 Barrier class under window compression | real window not measurable at t_now | no demand on B1 up to t_now |
| C4 State and observability of redundant groups | intact by record and reading | — |
| C5 Decidability gap | 0 named gap(s) | — |
| C6 Side effect of the barrier action | detection independent (PT-007 versus ZT-1001); actuation shared (XV-1001 and VLV-006). joint credit must not multiply the two PFDs. Declared side effect of B1's action: closes the A+C feed valve, which is the actuator of the level cascade LIC-8001; inventory control is lost, level goes to about -2.5 % and a low-level trip follows roughly 1 h later | — |
| C7 Static indicator versus dynamic margin | distance and rate side by side against every declared target | — |
| C8 Persistent versus removable threat | classification requires the threat-removal test | The removal test (design basis, section 6) was not executed for this bowtie. |

### Named gaps (C5)


### Recovery rules

- `alarms`: alarm_events with ts_inicio <= t_now; future ts_fim nulled; active peaks from voted series through t_now
- `work orders`: work_orders with data_abertura <= t_now; future closure, final narrative and findings omitted
- `channels`: blind_feed.canais_visiveis — a failure undetected by t_now is masked
- `reliability`: blind_feed.pfd_confiabilidade — only failures known by t_now enter the PFD
- `events`: process_events with visivel_copiloto=1 and ts <= t_now

### Model assumptions (not asset data)

- `human_barrier_pfd_with_overdue_competence`: 0.25 — replaces the human barrier's design PFD from the training due date, while the work order stays open
- `mean_channel_pfd_between_tests`: lambda_du * t / 2 — grows from the last closed test; with no test record the declared interval is taken as met
- `voted_group_without_reconfiguration`: 2oo3 = 3[(1-beta)*PFD1]^2 + beta*PFD1; with a detected channel failure, 2oo2 = 2*PFD1 — from the detected channel failure on, growth is linear in t, without the beta factor
- `single_channel_item_with_known_failure`: 1.0 — the item is unavailable (PFD = 1) from the work order's opening until it closes
- `items_without_test_records`:  — items with no test, calibration or training record are kept at their design PFD; absence of a record is not treated as absence of maintenance
