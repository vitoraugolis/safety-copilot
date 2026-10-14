## Phase A context · INC-BT-REATOR-20250401-1

`run=RUN_A` · `t_now=2025-04-01T00:30:00` · `window_from=2025-03-02T00:30:00` · `bowtie=BT-REATOR` · pathway `T1` · database `safety_copilot_v2.db`
Horizon from 2025-01-01T00:00:00. Design basis: `references/design-basis-barriers.md`.

**Trigger(s) that opened this analysis:** `record:wo_opened:WO-RUN_A-CH-A`; `record:channel_failure_detected:PT-007.A`

### Active alarms

None.

### Distance and rate, side by side (C7)

| Tag | Value | Crossed | Next threshold | Distance | Rate /min | Declared targets |
|---|---|---|---|---|---|---|
| PIT-7001 | 2704.8758 kPa | — | HI 2750.0 | 45.12 | — | SIS trip 2900: +195.12 [alarm_config.trip_sis]; model physical limit 3000: +295.12 [design basis, section 3] |
| TIT-9001 | 120.3891 C | — | HI 135.0 | 14.61 | — | — |
| LIT-8001 | 74.9657 % | — | HI 85.0 | 10.03 | — | — |
| FIT-1001 | 0.2128 kscmh | — | —  | — | — | — |
| TIT-2101 | 94.5489 C | — | HI 100.0 | 5.45 | — | — |

### Voted group PIT-7001 (C4)

- `PT-007.A` record: **failed_detected_unrepaired**, detected 2025-04-01T00:30:00 (WO-RUN_A-CH-A)
- `PT-007.B` record: **no_discrepancy_reported**
- `PT-007.C` record: **no_discrepancy_reported**
- reading at t_now: {'A': 2704.64, 'B': 2704.43, 'C': 2704.93} · spread **0.5** kPa against a limit of 17.5 (5% da faixa lolo..hihi de alarm_config) · deviation from median {'A': 0.0, 'B': -0.21, 'C': 0.29}
- per-channel statistics over 2025-03-02T00:30:00 → 2025-04-01T00:30:00 (computed): A mean 2708.38 sd 1.8 range 2703.55–2713.5; B mean 2708.41 sd 1.81 range 2703.44–2713.24; C mean 2708.43 sd 1.85 range 2702.85–2713.03
- agreement at t_now within 5.79 kPa (3× design noise 1.93 kPa, design basis §3): pairs [('A', 'B'), ('A', 'C'), ('B', 'C')]; divergent by majority: None

### Demand outcome per barrier (anchored on each barrier's own demand)

- **B1**: no demand on B1 recorded up to t_now

### Work orders

| WO | Type | Item | Class | Opened | Due | Overdue (d) | Description |
|---|---|---|---|---|---|---|---|
| WO-RUN_A-CH-A | corretiva | PT-007 | open | 2025-04-01T00:00:00 | — | — | Narrative unavailable at t_now (no time-versioned source) |

### Barriers (A1 + C2)

| Barrier | Design PFD | Current PFD | Barrier × | Worst component | Dominant element |
|---|---|---|---|---|---|
| B1 High-pressure interlock | 2.053e-02 | 2.309e-02 | **1.12×** | PT-007 37.54× | XV-1001 (48%) |
| B2 Manual operator action | 1.199e-01 | 1.224e-01 | **1.02×** | PT-007 37.54× | OP-B2 (82%) |
- B1: PT-007: 37.5x - no test record for this item; declared interval taken as met; voted group running 2oo2 without reconfiguration — 1 detected channel failure(s) not repaired
- B2: PT-007: 37.5x - no test record for this item; declared interval taken as met; voted group running 2oo2 without reconfiguration — 1 detected channel failure(s) not repaired

### Top event frequency, design versus current, both engines (computed)

| Engine | Design /yr | Current /yr | Ratio | Label design → current | Pathway % current |
|---|---|---|---|---|---|
| conventional | 1.754e-03 | 1.937e-03 | 1.1× | — → — | [73.0, 27.0] |
| fuzzy | 2.496e-04 | 2.906e-04 | 1.16× | Moderate → Moderate | [79.3, 20.7] |
- current barrier PFDs fed to the engines: {'B1': 0.023088, 'B2': 0.122428, 'B3': 0.01178, 'B4': 0.11112}. conventional engine for magnitude; fuzzy engine for the propagation of linguistic uncertainty (SKILL.md, 'The fuzzy engine'). Never one as a check on the other.

### Cross-checks

| # | Result | Gap / not applicable |
|---|---|---|
| C1 Envelope: current versus validated dynamics | no escalation window at t_now | — |
| C2 PFD decomposition: component versus barrier | both multipliers reported per barrier | — |
| C3 Barrier class under window compression | real window not measurable at t_now | no demand on B1 up to t_now |
| C4 State and observability of redundant groups | known degraded: PT-007.A failure detected 2025-04-01T00:30:00 (WO-RUN_A-CH-A, not repaired) | — |
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
