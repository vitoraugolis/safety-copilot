## Phase A context · INC-BT-REATOR-20251130-1

`run=RUN_A` · `t_now=2025-11-30T08:00:00` · `window_from=2025-11-30T00:00:00` · `bowtie=BT-REATOR` · pathway `T1` · database `safety_copilot_v2.db`
Horizon from 2025-01-01T00:00:00. Design basis: `references/design-basis-barriers.md`.

**Trigger(s) that opened this analysis:** `alarme:PIT-7001:LO`

### Active alarms

| Tag | Type | Since | Active (min) | Peak | Demand | Rate /min |
|---|---|---|---|---|---|---|
| PIT-7001 | LO | 2025-11-30T08:00:00 | 0.0 | 2547.9858 | no | — |

### Distance and rate, side by side (C7)

| Tag | Value | Crossed | Next threshold | Distance | Rate /min | Declared targets |
|---|---|---|---|---|---|---|
| PIT-7001 | 2547.9858 kPa | LO (-2.01) | HI 2750.0 | 202.01 | — | SIS trip 2900: +352.01 [alarm_config.trip_sis]; model physical limit 3000: +452.01 [design basis, section 3] |
| TIT-9001 | 120.4313 C | — | HI 135.0 | 14.57 | — | — |
| LIT-8001 | 70.986 % | — | HI 85.0 | 14.01 | — | — |
| FIT-1001 | 0.371 kscmh | — | —  | — | — | — |
| TIT-2101 | 94.0284 C | — | HI 100.0 | 5.97 | — | — |

### Voted group PIT-7001 (C4)

- `PT-007.A` record: **ok**, detected 2025-04-01T00:30:00, repaired 2025-04-02T00:00:00 (WO-RUN_A-CH-A)
- `PT-007.B` record: **failed_detected_unrepaired**, detected 2025-08-29T00:30:00 (WO-RUN_A-CH-B)
- `PT-007.C` record: **no_discrepancy_reported**
- reading at t_now: {'A': 2547.72, 'B': 2708.42, 'C': 2547.64} · spread **160.78** kPa against a limit of 17.5 (5% da faixa lolo..hihi de alarm_config) · deviation from median {'A': 0.0, 'B': 160.7, 'C': -0.08}
- per-channel statistics over 2025-10-31T08:00:00 → 2025-11-30T08:00:00 (computed): A mean 2696.5 sd 39.88 range 2518.14–2713.36; B mean 2708.41 sd 0.21 range 2707.99–2709.2; C mean 2696.51 sd 39.81 range 2518.98–2713.73
- agreement at t_now within 5.79 kPa (3× design noise 1.93 kPa, design basis §3): pairs [('A', 'C')]; divergent by majority: B
- flat channel (computed): **B** at 2708.41 kPa (band ±1.5) since about 2025-08-29T00:00:00; reference regime 2708.37 kPa (median voted PIT-7001 2025-01-01T00:00:00 → 2025-11-28T00:00:00); difference 0.04 kPa. computed from the series; the start is the first sample of the final stretch inside the band, not a recorded failure time

### Demand outcome per barrier (anchored on each barrier's own demand)

- **B1**: no demand on B1 recorded up to t_now

### Regime and precursors since the last operating-condition change

- `2025-11-28T00:00:00` **operating_condition_change** {"modo": "campanha padrao", "carga_pct": 15, "escala_setpoints_alimentacao": 1.15}
- voted PIT-7001 before: median 2708.37 kPa, range 2702.66–2715.78 (2025-01-01T00:00:00 → 2025-11-28T00:00:00, n=1986) (computed)
- voted PIT-7001 after: median 2566.13 kPa, range 2518.25–2602.79 (2025-11-28T00:00:00 → 2025-11-30T00:00:00, n=12) (computed)
- regime shift: -142.24 kPa; revalidation recorded: False
- alarm PIT-7001 LO 2025-11-28T00:00:00 → 2025-11-28T08:00:00, peak 2518.25
- alarm PIT-7001 LO 2025-11-29T04:00:00 → 2025-11-29T08:00:00, peak 2535.64

### Work orders

| WO | Type | Item | Class | Opened | Due | Overdue (d) | Description |
|---|---|---|---|---|---|---|---|
| WO-RUN_A-CH-A | corretiva | PT-007 | closed_with_finding | 2025-04-01T00:00:00 | — | — | Discrepancia do canal A do PT-007; rele/canal substituido e reteste OK. |
| WO-RUN_A-TEST | teste_funcional | PT-007 | overdue_not_executed | 2025-05-31T00:00:00 | 2025-05-31T00:00:00 | 183 | Teste funcional do intertravamento (reator.T1.B1) VENCIDO e nao executado. |
| WO-RUN_A-TRAIN | treinamento | OP-B2 | overdue_not_executed | 2025-07-30T00:00:00 | 2025-07-30T00:00:00 | 123 | Treinamento periodico de competencia (reator.T1.B2) VENCIDO; WO aberta automaticamente. |
| WO-RUN_A-CH-B | corretiva | PT-007 | open | 2025-08-29T00:30:00 | — | — | Discrepancia do canal B do PT-007 detectada; grupo votado operando degradado (2oo2). Reparo pendente em backlog. |

### Visible operational events

- `2025-11-28T00:00:00` **operating_condition_change** — {"modo": "campanha padrao", "carga_pct": 15, "escala_setpoints_alimentacao": 1.15}

### Barriers (A1 + C2)

| Barrier | Design PFD | Current PFD | Barrier × | Worst component | Dominant element |
|---|---|---|---|---|---|
| B1 High-pressure interlock | 2.053e-02 | 2.286e-02 | **1.11×** | PT-007 34.29× | XV-1001 (48%) |
| B2 Manual operator action | 1.199e-01 | 2.722e-01 | **2.27×** | PT-007 34.29× | OP-B2 (92%) |
- B1: PT-007: 34.3x - 333 d since the last test (interval 365 d); voted group running 2oo2 without reconfiguration — 1 detected channel failure(s) not repaired
- B2: PT-007: 34.3x - 333 d since the last test (interval 365 d); voted group running 2oo2 without reconfiguration — 1 detected channel failure(s) not repaired
- B2: OP-B2: 2.5x - test overdue by 151 d (interval 182 d); competence renewal overdue and open; PFD assumed 0.25 (model assumption, not declared in the asset)

### Top event frequency, design versus current, both engines (computed)

| Engine | Design /yr | Current /yr | Ratio | Label design → current | Pathway % current |
|---|---|---|---|---|---|
| conventional | 1.754e-03 | 3.635e-03 | 2.07× | — → — | [85.6, 14.4] |
| fuzzy | 2.496e-04 | 4.939e-04 | 1.98× | Moderate → Moderate | [89.6, 10.4] |
- current barrier PFDs fed to the engines: {'B1': 0.02286, 'B2': 0.2722, 'B3': 0.01178, 'B4': 0.11112}. conventional engine for magnitude; fuzzy engine for the propagation of linguistic uncertainty (SKILL.md, 'The fuzzy engine'). Never one as a check on the other.

### Contradictions between sources (recorded, not resolved)

- `PT-007` — PFD creep clock: "333 d since the last test (interval 365 d)" **versus** maintenance calendar (WO-RUN_A-TEST): "teste_funcional overdue by 183 d". Rule A: resets on the last CLOSED test/calibration/training work order; a corrective order does not reset it. Sensitivity (computed): last test implied by the calendar 2024-05-31T00:00:00 (due date minus the declared test interval (365 d); an assumption, not a record); item PFD 2.400e-03 by the model clock versus 3.948e-03 by the calendar (1.65×); per barrier {'B1': {'pfd_relogio_do_modelo': 0.02286, 'pfd_relogio_do_calendario': 0.024408, 'razao': 1.07}, 'B2': {'pfd_relogio_do_modelo': 0.2722, 'pfd_relogio_do_calendario': 0.273748, 'razao': 1.01}}. Both readings come from the same database and disagree. Phase A reports the PFD under each; which clock governs is a decision for the team.

### Cross-checks

| # | Result | Gap / not applicable |
|---|---|---|
| C1 Envelope: current versus validated dynamics | rate ranges -0.08 to -0.08 kPa/min across windows (1.0x); envelope invalidated | — |
| C2 PFD decomposition: component versus barrier | both multipliers reported per barrier | — |
| C3 Barrier class under window compression | real window not measurable at t_now | no demand on B1 up to t_now |
| C4 State and observability of redundant groups | known degraded: PT-007.B failure detected 2025-08-29T00:30:00 (WO-RUN_A-CH-B, not repaired); channel B flat at 2708.41 kPa since about 2025-08-29T00:00:00 | — |
| C5 Decidability gap | 1 named gap(s) | — |
| C6 Side effect of the barrier action | detection independent (PT-007 versus ZT-1001); actuation shared (XV-1001 and VLV-006). joint credit must not multiply the two PFDs. Declared side effect of B1's action: closes the A+C feed valve, which is the actuator of the level cascade LIC-8001; inventory control is lost, level goes to about -2.5 % and a low-level trip follows roughly 1 h later | — |
| C7 Static indicator versus dynamic margin | distance and rate side by side against every declared target | — |
| C8 Persistent versus removable threat | classification requires the threat-removal test | The removal test (design basis, section 6) was not executed for this bowtie. |

### Named gaps (C5)

- **Is there a common cause affecting channels A and C?** A and C agree within 5.79 kPa and B diverges, so the majority identifies the divergent channel; what the group cannot rule out is a shared error in the agreeing pair. External check: an independent field measurement of vessel pressure

### Rate ladder PIT-7001 (computed)

| Window | From → to | kPa/min | vs design | > 2.2 |
|---|---|---|---|---|
| since 00:00 of the day | 2025-11-30T00:00:00 → 2025-11-30T08:00:00 | -0.08 | -0.1× | no |
- invalidation trigger (design basis §7) — measured escalation rate above 2.2 kPa/min: not observed (0 of 1 windows above 2.2 kPa/min)
- invalidation trigger (design basis §7) — operating-condition change without subsequent revalidation: OBSERVED (operating-condition change at 2025-11-28T00:00:00; no work order and no window revalidation event after that date)
- invalidation trigger (design basis §7) — design plateau not observed: not observed (plateau band not crossed in the window)

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
