# Barrier Design Basis — Reactor Bowtie

> Converted from `base_de_projeto_barreiras.md.docx` (2026-09-11) and masked for
> the agent: source-benchmark nomenclature replaced by the plant tags in
> `safety_copilot/blind_feed.py` (`ALIAS`). Content otherwise unchanged.

**Agent input.** Declares *what each barrier is*, *what it does*, and *under
which operating condition it was validated*. Every performance figure here was
measured in a simulation campaign, with the source named.

> **Deliberate scope.** This document describes **only the design base case**.
> It contains no measurements under alternative operating conditions. If the
> plant is running outside the base case declared in Section 2, the performance
> in Section 5 **does not apply**, and determining how far it fails to apply is
> analysis work, not lookup. Section 7 declares the criteria for recognising
> that situation.

---

## 1. How to use this document

This is the **declared design basis**. It answers the question PFD alone does
not: *is acting still sufficient in the condition the plant is in now?*

Two uses:

1. **Barrier dictionary** — which elements make up each barrier, which tag
   detects what, which action is expected of whom, and within what time.
2. **Validity envelope** — compare the plant's current condition against the
   condition under which the barrier was validated. A divergence between the
   two is a finding, even with every item sound and every PFD at its design
   value.

PFD answers "will the equipment act?"; the design basis answers "is acting
still enough?". These are independent questions, and a barrier can fail the
second while scoring full marks on the first.

---

## 2. Design base case

The single condition under which every barrier was sized and validated.

| Parameter | Design value |
|---|---|
| Operating mode | Mode 1 — standard campaign, base throughput |
| Steady reactor pressure | 2708 kPa (measured: 2709.1 and 2698.5 on two seeds) |
| Steady reactor level | 74.4 % |
| Steady reactor temperature | 120.4 °C |
| Stream 1 feed flow | 0.252 kscmh |
| **Escalation rate under threat T1** | **1.1 kPa/min** |

> **Distribution of available time.** In the base case, pressure nearly settles
> between 2850 and 2870 kPa for about 1.7 h before rising again; the local rate
> over that stretch drops to 0.27 kPa/min. Much of the barriers' margin sits in
> that plateau. **This distribution is a property of the base case and must not
> be assumed under other operating conditions.**

---

## 3. Protection ladder

| Layer | Value | Role |
|---|---|---|
| LOLO / LO | 2450 / 2550 kPa | Low deviation |
| **HI** | **2750 kPa** | Alert — start of the response window |
| **HIHI** | **2800 kPa** | **Formal demand on B1** (`e_demanda = 1`) |
| **SIS trip** | **2900 kPa** | Last automated layer (field `trip_sis` in `alarm_config`) |
| Model physical limit | 3000 kPa | Simulation boundary — must not be reached |

**Design constraint:** HI does not go below ~2750 kPa. Base pressure is 2708 kPa
and the PIT-7001 noise has a standard deviation of 1.93 kPa; a lower threshold
would sit in permanent alarm.

---

## 4. Barriers of pathway T1 (pressure)

### B1 — Automatic high-pressure interlock
`reator.T1.B1`

| Element | Asset | Function |
|---|---|---|
| Detection | PT-007 (2oo3, channels A/B/C) | Compares voted PIT-7001 against HIHI |
| Logic | UZ-007 (1oo1) | Resolves the vote and commands the action |
| Final element | XV-1001 (feed valves XV-1001A–D) + VLV-006 (purge valve FCV-0601) | Closes feeds, opens purge |

- **Design PFD:** 2.05×10⁻² (sum of the four components)
- **Dominant component:** XV-1001 (1.1×10⁻²) — the voted sensor contributes
  7.0×10⁻⁵, more than two orders of magnitude below
- **Actuation time:** seconds — negligible against the process dynamics
- **Demand trigger:** voted PIT-7001 ≥ HIHI

> **Structural side effect, measured.** XV-1001D (stream 4, A+C feed) is the
> actuator of the reactor level cascade (LIC-8001: LIT-8001 → A+C setpoint →
> XV-1001D). B1's action closes that valve along with the other feeds and
> **destroys inventory control**: level goes to ≈ −2.5 % and a low-level trip
> follows about 1 h later. B1 prevents the top event of pathway T1 and causes a
> shutdown by another route. This coupling is not mapped in the bowtie — treat
> it as a declared secondary consequence of B1's action.

### B2 — Manual operator action
`reator.T1.B2`

| Element | Asset | Function |
|---|---|---|
| Detection | ZT-1001 (feed valve position) | Command-versus-position discrepancy reveals that B1's final element did not respond |
| Decision | OP-B2 (human competence) | Diagnosis and decision to intervene |
| Final element | XV-1001 + VLV-006 | Manual closure of the feeds |

- **Design PFD:** 1.24×10⁻¹
- **Dominant component:** OP-B2 (0.10) — about 81 % of the total
- **Actuation time:** minutes — depends on perception, diagnosis and execution
- **Training interval:** 4380 h (six-monthly)
- **Demand trigger:** command-versus-position discrepancy on ZT-1001

> **B2 is not triggered by the pressure alarm.** Design decision: if B2 fired on
> PT-007's HIHI it would share the detector with B1, and both would fall
> together by common cause. B2's demand arises from the command-versus-position
> discrepancy, which means **only after B1 has tried and failed**. B2's real
> window is the HIHI→SIS window minus B1's attempt time and the latency of
> detecting the discrepancy.

> **Partial independence.** B1 and B2 have independent detection (PT-007 versus
> ZT-1001) but **share the final element** (XV-1001 and VLV-006). Joint credit
> must reflect this: the dependency is in the actuation arm, not the detection
> arm.

---

## 5. Performance measured **in the base case**

Threat T1 (loss of stream 1 feed), injected after stabilisation, two seeds
(42 and 123). **Values valid only under the condition of Section 2.**

| Metric | Base case | Source |
|---|---|---|
| Window HI (2750) → SIS (2900) | **202 min** | `bands.py` |
| Window HIHI (2800) → SIS (2900) | **162 min** | `bands.py` |
| Maximum tolerable delay for B2 | **≈ 67 min** | `b2_envelope.py` |
| Escalation rate | 1.1 kPa/min (plateau: 0.27) | `bands.py` |

**Composition of B2's maximum delay:** the tolerable delay was measured to be
practically equal to the whole window — the action executes too fast to consume
any time budget. **All of B2's margin is human perception and decision**, none
is execution. The PFD of 0.10 should be read as "probability that the operator
fails to notice, diagnose and act within the available window", and that window
is a parameter of the operating condition, not a constant.

**Success criterion used in the measurements:** the barrier is effective when
pressure reverts without reaching the SIS trip. A shutdown from another cause
(low level, Section 4) is a secondary consequence, not a failure of the barrier
against the top event of pathway T1.

---

## 6. Threat classification

| Threat | Classification | Status |
|---|---|---|
| T1 — loss of stream 1 feed | not classified | requires a threat-removal test |

The persistent-versus-removable classification determines what should be
expected of the barrier, and requires its own experimental campaign (removing
the threat at different instants, with and without barrier action). **Not
executed for this bowtie.**

---

## 7. Invalidation criteria

The design basis must be treated as **unverified** when any of the following is
observed:

- **Measured escalation rate above 2.2 kPa/min** — twice the design rate of
  Section 2. Above that, the windows in Section 5 do not describe the current
  condition, whatever the declared cause
- A recorded change of the operating condition of Section 2 (load, feed
  setpoints, operating mode) without subsequent revalidation of the windows
- A change of thresholds in `alarm_config` without recomputing the windows
- A change of voting arrangement or test interval in `ativos`

When invalidated, the real actuation window **is not known** and must be derived
from current data, not estimated from Section 5.

---

### Provenance of the data in this basis

| Script | What it produces |
|---|---|
| `bands.py` | Time from each threshold to the limit, and local rise rate, in the base case |
| `b2_envelope.py` | Maximum tolerable delay for the operator action |
| `moc_run.py` | HI/HIHI→trip windows, two seeds |
