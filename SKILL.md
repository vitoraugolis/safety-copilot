---
name: analise-seguranca
description: Assembles and interprets the risk context of a quantitative bowtie — cross-checks process, reliability and maintenance data, assesses barrier degradation from PFD and MTTF against a declared design basis, and produces a traceable report plus a separate audit log covering scenario, evidence, risk judgement, uncertainty and recommended response. Use when investigating a bowtie bridge trigger, an alarm or a demand on a barrier; when checking whether barriers still hold in the plant's current operating condition; when assessing the impact of a management-of-change on existing barriers; when analysing an episode recorded in the database; and when closing an open occurrence. Does not replace PHA/HAZOP, LOPA, formal investigation, emergency response, or risk acceptance by the facility's authority.
---

# Process safety occurrence analysis

Turn a signal of risk erosion into a traceable operational decision. Preserve
the chain `process → measurement → condition → threat → barrier → top event →
consequence`. The result is a technical analysis, not automatic root cause and
not authorisation to operate.

The work has two phases, and the order between them is not negotiable:

| Phase | Nature | Produces |
|-------|--------|----------|
| **A — Context** | recover, cross-check, organise, expose gaps | a block auditable by inspection |
| **B — Analysis** | interpret, judge, recommend | the report, plus the audit log |

The separation is deliberate. A block that only organises and cross-checks data
can be audited by inspection: either the figure matches the database or it does
not. There is no reasoning to question. That auditability is what lets phase B
operate with confidence.

**Gate A→B:** do not write a line of judgement before phase A is closed and its
gaps are listed. Concluding over data nobody cross-checked is the most common way
to go wrong here.

Phase A is executed by `safety_copilot/contexto.py`, in Python. The text below
specifies what that module must produce; the agent receives it already closed and
runs phase B only. Audit phase A by inspection with:

```bash
python3 -m safety_copilot.contexto --run <run> --at <t_now>
```

## Analyses over time

The stream replays a run point by point and watches two sides: the process
series, and the plant's records — a work order opened or falling overdue, a
channel failure detected or repaired, a visible process event. Barrier erosion
by the maintenance calendar never shows up in the series, so a detector that
only watches process values is blind to the mechanism this method exists to
catch.

Each qualifying trigger opens **its own dated analysis**, with its own immutable
ID and its own phase A frozen at that instant. Rules:

- An analysis knows nothing that happens after its `t_now`. Do not use a later
  fact to explain an earlier instant.
- Say what **this** trigger changed. An analysis that repeats the previous one
  without naming the change wastes the reader's attention.
- Never rewrite an earlier analysis. The sequence is the evidence that the
  judgement tracked the plant, and a corrected past hides the moment the
  information arrived.
- The occurrence's report is the latest analysis; the log keeps the sequence.

## Safety limits

These outrank any analytical conclusion.

- **The plant outranks the report.** On active loss of containment, approach to a
  trip, a condition outside the safe envelope, several critical barriers
  unavailable, or a plausible catastrophic scenario with uncertain data,
  recommend immediate escalation to operations and application of the standing
  emergency procedures. Do not wait for certainty, and do not wait for phase A to
  close.
- **Do not act.** Do not improvise manoeuvres and do not change setpoints, logic,
  alarms, bypasses, bowties, work orders or equipment. Authorised people decide
  and execute.
- **Do not fabricate a parameter.** Do not invent tolerability, SIL, PFD, MTTF,
  frequency, consequence or barrier credit. Use the approved basis; where it is
  missing, write `not demonstrated` and move on.
- **The bowtie organises, it does not prove.** It demonstrates neither causality,
  nor barrier independence, nor the adequacy of risk credit, nor regulatory
  compliance.

## Honesty rules

These hold in both phases and outrank any presentational convenience.

- **Declare the gap, do not fill it.** If a required parameter does not exist,
  say it does not exist. Do not substitute a typical value without marking it.
- **Distinguish reading from calculation.** A value read from the database and a
  value derived from a formula have different status and must be distinguishable
  in the output.
- **Cite the recovery rule.** When presenting a set of work orders or a context
  window, say which criterion selected them.
- **Do not conclude from an instantaneous value.** Always pair it with a rate.
- **Record contradictions.** When two sources disagree, present both. Divergence
  between channels of a voted group is data, not an error to correct.
- **Separate field truth from script truth.** In datasets containing simulation
  data, events marked as not visible exist for later scoring and must not enter
  the presented context.

## Input and identity

Use the package named by the user. If none is named, select the most recent JSON
in `triggers/`; that is the source of truth and the sibling Markdown is derived.
Record path, timestamp and version or hash where available.

If there is no trigger, run a single sweep:

```bash
python3 -m safety_copilot.bridge --once
```

If there is still no package, report that no monitored bowtie crossed its
criterion in this sweep. That does not demonstrate the absence of risk outside
the monitored scope.

Set an immutable ID `INC-<bowtie_id>-<YYYYMMDD>-<sequence>`. Do not group
independent threats, top events or operating windows under one ID.

### Inputs

Confirm these exist before starting:

1. **A database with three temporal layers** — *process* (seconds to hours: tag
   series, alarm configuration and events, process events); *reliability* (months
   to years: channel and item state, failure events, MTTF and test interval per
   asset); *maintenance* (continuous: preventive and corrective work orders).
2. **The bowtie graph** — threats, barriers per pathway, top event, and the
   logical structure (AND within a pathway, OR between pathways).
3. **The barrier design basis** — for each barrier, its elements and the
   operating condition under which it was validated:
   [design basis](references/design-basis-barriers.md). If none exists, produce
   one first: [procedure](references/producing-a-design-basis.md).

If an input is missing, declare the absence and proceed with what exists, marking
explicitly what could not be verified. Never substitute a missing input with an
assumption.

## Reading the engine's numbers

The trigger package carries figures produced by one of the bowtie's two engines.
Read the `engine` field before interpreting any value.

**Effective frequency from MTTF.** For a node with a declared MTTF the engine
uses `f = 1 − exp(−t / MTTF)`, with `t` the exposure window in years
(`bowtie.time` in `config.toml`, typically 1.0). When the bridge re-evaluates a
barrier's PFD from process data it writes the re-evaluated PFD as the frequency
and **zeroes the node's MTTF**: from then on that barrier's figure no longer
comes from MTTF. Say which of the two paths produced each value you cite.

**The fuzzy engine.** Mamdani inference over two systems, each with two inputs,
matching the physics of the diagram:

| Node | Input 1 | Input 2 | Identity it approximates |
|------|---------|---------|--------------------------|
| **AND** | frequency | **PFD** | `f_out = f_in × PFD` |
| **OR** | frequency | frequency | `f_top = f_1 + f_2` |

Both work on the decade scale `u = −log₁₀(x)`, where those identities become
addition and a log-sum. Universes: frequency `[0, 20]`, PFD `[0, 6]`, output
`[0, 20]`. Five terms each — `VL`, `L`, `M`, `H`, `VH` — reported as Very low,
Low, Moderate, High, Very high. `VH` means frequent, or a poor barrier; `VL`
means remote, or an excellent one.

The rule matrices are **derived** from the two identities at each term's
representative value, not typed by hand, so any cell can be checked against one
line of arithmetic.

A pathway folds as the diagram reads: start from the initiating event's
frequency, then apply the AND node once per preventive barrier with that
barrier's PFD as the second input. Pathways are then combined pairwise by the OR
node.

Rules for using the label:

- The label qualifies a **frequency**, not the state of a barrier and not risk.
  Barrier state uses the phase B vocabulary; risk requires a consequence.
- A fuzzy label is not an acceptance criterion. Moving from `Low` to `Moderate`
  is a sign of erosion, not a breach of tolerability.
- **Fuzzy is an approximation of the exact product, and the difference is
  material.** With five terms across twenty decades, each AND operation is
  quantised to roughly one decade, so the fuzzy top event frequency can differ
  from the conventional one by several times.
  The pathway contribution split survives; the absolute frequency does not. Cite
  the conventional engine for magnitude and the fuzzy engine for the propagation
  of linguistic uncertainty — never one as a check on the other.
- Do not convert a label into a number, or a number into a label, outside the
  engine.

---

# Phase A — Context

Recover, cross-check and display. Do not conclude.

**Assembling context is still deciding.** Which work orders belong to a barrier,
which window around an alarm counts as relevant, which tags belong to a bowtie
node — each choice shapes what phase B will see. That is why the recovery rules
are explicit and cited in the output, never implicit.

## A1. Load the bowtie and the design basis

Load the graph and the design basis **in full before looking at any process
data**. The order matters: knowing the declared envelope before seeing the
current condition prevents anchoring the reading on what is happening now.

For each barrier, extract:

- **Elements**, on the *detect–decide–act* model
- **Design PFD** and each component's contribution
- **Actuation time** — seconds (automatic) or minutes (human); feeds C3
- **Validity envelope** — the condition under which performance was measured, and
  the time windows measured in that condition
- **Demand trigger** — which signal, exactly, constitutes a demand on this
  barrier. Watch for backup barriers: their trigger is usually the failure of the
  preceding barrier, not the same process alarm
- **Success criterion** — what counts as the barrier having worked, and which
  layer sits beyond it. Load the protection ladder as well: each layer, its
  setpoint and its role. A barrier and the layer downstream of it are different
  equipment with different demands

## A2. Establish the current state

Three sweeps, in this order. Cite the query used in each.

**What is failed.** Items with a recorded failure not yet repaired. For each:
*detected or hidden* (a hidden failure means nobody knows, and the exposure clock
runs to the next test); *has an associated work order* (the absence of one on a
failure is itself a finding); *elapsed time* since the failure, since detection
and since the planned repair.

**Active alarms and their evolution.** Alarms with no return time. For each,
besides the current value: how long it has been active; whether it constitutes a
demand on a barrier and whether actuation was recorded; and the **rate of change
of the tag over the recent window — mandatory, not optional**. An alarm active
for 4 h with a stable variable is a different situation from one active for
20 min with the variable climbing fast, and the instantaneous value does not
distinguish them. Compute the rate over a window long enough not to capture noise
and short enough to reflect the current trend; declare the window used.

**Demand outcome, barrier by barrier.** For every barrier demanded up to
`t_now`, anchored on **that barrier's own demand instant** — never on a later
layer's action:

- *detect* — the values of the voting channels at the demand, and whether the
  declared vote was satisfied;
- *decide* — the record of the logic's output: an event, a work order, or
  nothing;
- *act* — the final element's signature in the window **after that demand**:
  which tags should move, in which direction, and what they did;
- *outcome* — the design basis success criterion, the next declared layer, and
  whether that layer was reached.

A downstream layer acting is evidence that the barrier upstream did **not**
arrest the excursion. It is never evidence that the barrier acted.

**Work orders in context.** Work orders for the assets of the barriers involved,
classified as: *open* (backlog, under repair); *overdue and not executed* —
functional tests, calibrations, training, each one a degradation with a cause
traceable in the calendar; *closed with a finding* — evidence of failure on
demand.

## A3. Mandatory cross-checks

These eight are the core of the method. Execute **all of them**; where one does
not apply, declare why. None produces judgement — each produces a pair of
compared values and, where applicable, a named gap.

| # | Cross-check | Rule |
|---|-------------|------|
| C1 | Envelope: current versus validated dynamics | Compare the measured rate against the design basis rate, over **several declared windows**, and evaluate each invalidation trigger the basis declares. A single value tells the wrong story in opposite directions |
| C2 | PFD decomposition: component versus barrier | Report **both** multipliers, the component's and the whole barrier's, and name the element that dominates the PFD |
| C3 | Barrier class under window compression | Compare the design window against the measured one. Automatic barriers (seconds) survive compression; human barriers (minutes) do not |
| C4 | State and observability of redundant groups | Per voted group: **intact** / **known degraded** / **hidden degraded**, with the corresponding PFD and the clock that applies. Name the failure mode the data supports — a frozen channel is told from a drifting one by its own variance, not by the spread — and compare a frozen reading against the regime it is stuck at |
| C5 | Decidability gap | Name the questions that available instrumentation and records cannot answer, each with the external check that would settle it. Where two of three channels agree within the noise band, the majority already identifies the divergent one: what stays open is a common cause in the agreeing pair, not which channel is correct |
| C6 | Side effect of the barrier action | Check whether the final element is shared with another loop or barrier, and record the design basis's declared side effects as secondary consequences |
| C7 | Static indicator versus dynamic margin | Present **distance and rate side by side**, against every declared target — alarm thresholds, trip setpoints and physical limits — never distance alone |
| C8 | Persistent versus removable threat | Classify the threat. If it is the permanent loss of something the process needs, no barrier produces a stable state |

Read [the cross-checks in detail](references/cross-checks.md) before executing
any of them for the first time, when one fires, or when the result is ambiguous.
The table above is the trigger, not the explanation.

## A4. The report and the log

Phase A produces two views over the same frozen context. Neither originates a
number: both read `contexto.json`.

**`report.html` — the decision.** For an operations reader. In this order:

1. **Safety limit banner** — the escalation statement, before anything else
2. **Required decision** — the phase B text
3. **Process variables** — charts of the flagged tags with alarm bands shaded and
   thresholds drawn as labelled dashed lines; every chart carries value *and*
   rate; actuation events marked on the time axis; below each chart, distance and
   time to every declared target
4. **Barrier impact** — the macro bowtie with each barrier coloured by its
   multiplier against its own design, or by its demand outcome where it was
   demanded, with any layer beyond the pathway named as such and not as a
   barrier; then one card per barrier: elements, PFD as `design → current` with
   both C2 multipliers, the dominant element, and the voted group's channels
   showing deviation and variance next to recorded state
5. **Demand outcome** — per demanded barrier: detect, decide, act, outcome
6. **Top event frequency** — design against current, both engines, with the ratio
7. **Validity envelope** — design rate against the decision window's rate, and
   each invalidation trigger with its evidence
8. **Gaps bearing on the decision** — the C5 questions with their external checks
9. **Analyses over time** — the dated sequence of analyses in this stream

**`log.html` — the audit chain.** For a reviewer checking the report line by
line: identity and provenance of every input, the recovery rules as executed, the
full rate ladder, the demand outcome in full, the voted group's statistics, the
regime and its precursors, both engines on design and current, all eight
cross-checks with the values
compared, every gap with its full reasoning, the recorded contradictions, and the
model assumptions. It closes with the A→B gate.

Mark the origin of every value:

| Marking | Meaning |
|---------|---------|
| no mark | direct reading from the database |
| `computed` | derived from a declared formula |
| `assumption` | assumed by the model, not read |
| `absent` | a field that does not exist in the source |

**Close phase A** with the list of what went unverified and why. That list is
input to phase B, not an appendix.

---

# Phase B — Analysis

Now interpret. Before any inference, confirm unit and operating mode, time
window, top event, threat, consequences, measurement quality and
synchronisation, bowtie version, approved criteria, and which barriers are in
bypass, test, maintenance or temporary change.

Read [the risk analysis reference](references/risk-analysis-reference.md) when the
case involves IPL/SIL credit, quantification or tolerability, dependent barriers,
management of change, human or organisational factors, evidence of systemic
failure, or closure after an intervention. For simple confirmation of a trigger,
stay in this flow.

Do not retype phase A's figures. Cite them by field name. A figure retyped by a
language model is a figure that can diverge from the database.

## B1. Fact

Record only what was observed: parameter or event, value, criterion crossed,
first instant, duration, current state, operating mode, sources, window and data
quality. Keep top event frequency, consequence and risk separate.

Check clocks, units, instrument range, signal quality, freezing, saturation,
manual override and channel divergence. Do not include cause or action.

**Gate:** if the crossing is not reproducible, stop inferring here and record
`inconsistent trigger` or `insufficient data quality`. A report that declares the
data bad is worth more than one that interprets it.

## B2. Scenario and mechanism

State the qualitative chain:

`threat → preventive barriers → top event → mitigating barriers →
consequence/receptor`

Then, over the tree linking tags, barriers and bowtie nodes, walk the
quantitative chain:

`tag/condition → failure mode or escalation factor → barrier state and PFD →
top event frequency → consequence frequency and severity`

List the links that support the breach of the frequency criterion, each with its
source. A link without a source is a hypothesis: mark it as one. Temporal
correlation is not root cause.

## B3. Three readings

### Bowtie

Compare design basis, current state and criterion. For each relevant barrier,
check function, required performance, PFD, state, evidence, escalation factor and
dependencies.

Use exactly these three states:

| State | What demonstrates it |
|-------|----------------------|
| `healthy` | requirement demonstrated and within validity |
| `degraded` | partially met, or met with reduced margin |
| `critical` | function removed, isolated, expired or unable to be met — includes bypass and isolation, even without a demand |

**A demand settles the state.** A barrier that was demanded and whose success
criterion was not met is `critical` — failed on demand — whatever its PFD says.
PFD is the probability before the demand; the outcome is an observation, and an
observation outranks a probability. Say which element the record implicates
(detection, logic or final element) and which the data cannot separate. If the
demand is still open at `t_now`, say so and do not settle the state.

Bring the C3 and C4 findings into the state. A human barrier under a compressed
window (C3) is not `healthy` at its design PFD: the number survives, its meaning
does not — record it as a gap, and do not adjust the PFD without an approved
method. A voted group that is hidden degraded (C4) has the same instantaneous PFD
as a known degraded one and a far larger integrated exposure, because the clock
is the test interval and not the repair interval.

Do not grant IPL/SIL credit merely because the barrier appears in the bowtie. Do
not multiply PFDs without demonstrated independence — and treat a shared final
element (C6) as evidence against it. Consider common cause, simultaneous
maintenance and domino effects.

Where you need barrier doctrine rather than plant data, the consultable source is
CCPS/Energy Institute, *Bow Ties in Risk Management: A Concept Book for Process
Safety* (CCPS–EI, 2018). Cite chapter or section; do not invoke it generically to
authorise a conclusion.

### Process

Analyse the trajectory, not just the last value. Compare the dominant process
variables against the safe envelope, setpoints, alarms and approved trips.
Examine persistence, rate of change, physical balances, control and interlock
response, alarm sequence, transients, regime changes and coherence between tags.
Apply C7: distance and rate side by side. An isolated temporal coincidence does
not demonstrate causality.

### Context

Query operational memory and the approved basis separately:

```bash
python3 -m safety_copilot.corpus search "<barrier> <equipment> <tag>" \
  --kind wo,turno,historico,moc -k 12
python3 -m safety_copilot.corpus search "<scenario> <barrier> alarm PFD SIL test" \
  --kind oficial,literatura -k 8
```

Check the design basis and PHA, mechanical integrity, tests, repeated failures,
procedures, operational readiness, technical or organisational management of
change, human factors and incident learning. Cite document, revision and date.

The absence of a record is a gap, not proof of non-compliance. Do not assign
blame to the operator; assess task, equipment, environment and organisation.

## B4. Risk judgement

Phase A computes the top event frequency on the design diagram and on the
current PFDs, with both engines; cite that pair and the ratio. Do not declare it
not computed, and do not cite the design figure as the current one.

Top event frequency is not risk. Present, per scenario: frequency, consequence,
receptors, approved criterion, residual risk and uncertainty. Do not add
incompatible consequences and do not convert categories into numbers without an
approved method.

If consequence or tolerability is missing, the correct conclusion is `barrier
erosion demonstrated; risk tolerability not determined`. That is a result, not a
failure of the analysis.

Classify urgency from plausible consequence, proximity of the event, time
available, remaining barriers and confidence in the data. Time available comes
from C7 — time to the declared target, not distance — and the exposure horizon of
a degraded barrier comes from the C4 clock. Do not discard high consequence and
low frequency by averaging, rounding or absence of history.

## B5. Recommendation and closure

Recommend immediate containment, restoration and a definitive solution where
these differ. Prefer the most robust control available, in this order:
elimination or reduction of the hazard, inherently safer design, passive barrier,
active barrier, administrative control, and last personal protective equipment
for individual exposure. An administrative control does not permanently
compensate for engineering without a demonstration of adequacy.

Check the couplings recorded in C6 before recommending a barrier action: the
action may prevent the top event and cause another by an unmapped route. Under a
persistent threat (C8), recovery comes from removing the threat, and "the barrier
worked" means "we reached the repair alive".

Declare the suggested owner, priority, risks introduced by the action itself, any
further analysis required, expected return, leading indicator, closure criteria
and the authority that accepts the residual risk. Where there is evidence of
systemic failure, recommend a separate formal investigation.

**Closure gate.** Only mark `closed` when the condition is controlled, the
barrier function is restored **and tested**, temporary changes are managed,
residual risk is reassessed, the design basis windows are revalidated under the
current condition, and open items are traceable. The process variable returning
to band does not, on its own, close the occurrence.

If an intervention has already happened, compare the observed result against the
expected return and look for adverse effects. Do not retrospectively rewrite a
prediction as an observation.

---

## Mistakes not to make

Re-read before delivering.

- Writing judgement before closing phase A and listing the gaps.
- Treating a fuzzy label as a barrier state, or as risk.
- Citing a fuzzy engine frequency as if it matched the conventional engine.
- Calling a barrier `critical` when it is merely degraded, or the reverse.
- Multiplying the PFDs of barriers that share a sensor, logic, actuator, utility,
  procedure or person.
- Concluding from an instantaneous value, without a rate.
- Reporting only one of C2's two multipliers.
- Citing a design basis window after C1 has declared the envelope invalidated.
- Reading the actuation of a downstream layer — a SIS trip — as the upstream
  barrier's actuation, or calling a demand "met" because a later layer acted.
- Looking for an actuation signature in a window that is not the barrier's own
  demand window.
- Saying a check "would have exposed" a failure without comparing the check's
  due date against the failure date.
- Calling "which channel is correct" undecidable when two of three agree within
  the noise band.
- Calling a channel divergent without naming the failure mode the data supports.
- Declaring the top event frequency not computed when phase A carries it.
- Filling a missing parameter with a typical value without marking it as an
  estimate.
- Retyping a phase A figure instead of citing its field.
- Closing the occurrence because the process variable returned to band.
- Presenting more precision than the input data carries.

## Output

Write `reports/<incident_id>.md` alongside the two HTML views. Preserve units,
timestamps, identifiers and evidence links. State the conclusion first, then the
minimum evidence. The phase A context block belongs to the log; the report cites
it.

```markdown
---
incident_id: INC-...
bowtie_id: ...
opened_at: ...
engine: conventional | fuzzy
status: action_required | monitoring | closed
urgency: emergency | immediate | planned | routine
confidence: high | medium | low
---

# <required decision in one sentence>

## Fact
<value, criterion, instant, duration, state and data quality>

## Scenario and mechanism
<threat → prevention → top event → mitigation → consequence>
<quantitative chain, the source of each link, and the strength of the evidence>

## Analysis
### 1. Bowtie
<state per barrier, performance, dependencies, escalation factors, dominant path>
### 2. Process
<trajectory, envelope, distance and rate, controls and precursor signals>
### 3. Context
<design basis, integrity, management of change, human and organisational factors, gaps>

## Risk judgement
<frequency, consequence, tolerability or the limit of the conclusion, uncertainty, urgency>

## Recommendation
**Immediate containment:** ...
**Restoration:** ...
**Definitive solution:** ...
**Suggested owner / deadline:** ...
**Expected return / leading indicator:** ...
**Closure criteria:** ...
**Residual risk / accepting authority:** ...
**Human decision:** pending

## Evidence and assumptions
- [demonstrated|corroborated|inferred|undetermined|refuted] <source, date, finding>
```
