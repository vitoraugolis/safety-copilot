# The eight cross-checks, in detail

The table in SKILL.md is the trigger — the rule that fires the cross-check. This
reference is the reason: the failure mode each one exists to catch. Read the
relevant entry before executing a cross-check for the first time, when it fires,
or when the result is ambiguous.

No cross-check produces judgement. Each produces a pair of compared values and,
where applicable, a named gap. Interpreting is phase B.

## C1 — Envelope: current versus validated dynamics

**Rule.** Compare the measured rate of change against the rate declared in the
design basis, **over several windows, each declared**, and evaluate every
invalidation trigger the basis states.

**Why.** Barrier windows are measured under a specific condition; they are not
intrinsic properties. Changing the operating condition changes the window without
touching any equipment. A barrier with every item sound, no overdue work order
and its design PFD intact can be outside its envelope, and no reading of
equipment state shows that.

**Why a ladder and not one number.** This is the part that is easy to get wrong.
The rate measured over a whole episode and the rate measured in the window where
the decision is taken can fall on opposite sides of the invalidation criterion.
An episode-wide rate that includes an initial fall can sit just below the
threshold while the rate between the demand threshold and the last automated
layer is several times the design rate. A single average and a single
instantaneous value both tell the wrong story, in opposite directions. Measure the same
variable over the episode, from the valley, between thresholds, and after any
actuation; declare the window on every line.

**Output.** The ladder, with the window and sample count per line; the design
rate and its source section; each invalidation trigger with observed/not observed
and its evidence; and the verdict. When the basis does not declare a reference
rate, the result is a gap, not "within envelope".

## C2 — PFD decomposition: component versus barrier

**Rule.** When a component degrades, report **both** multipliers: the
component's and the whole barrier's. Identify and name the element that dominates
the PFD.

**Why.** If one element dominates the total, a component can get dozens of times
worse and move the barrier very little. The two numbers can differ by orders of
magnitude. Reporting only the component's produces over-reaction; reporting only
the barrier's hides the degradation and produces under-reaction.

**Output.** `design → current` for the barrier, the same pair for the component,
both multipliers, and the dominant element with its share of the total.

## C3 — Barrier class under window compression

**Rule.** Compare the design window against the measured one, then separate
barriers by actuation time. Automatic barriers (seconds) survive compression;
human barriers (minutes) do not.

**Why.** A window that halves does not affect the two classes equally. A human
PFD calibrated for a wide window does not describe the same person facing a
narrow one — the number survives on the spreadsheet, its meaning does not. This
is the failure mode where the arithmetic stays correct and the conclusion goes
wrong.

**How to quantify it.** Take the window the design basis declares between the
demand threshold and the last automated layer, and the same interval as measured
in the episode. Their ratio is the compression. Then compare the human barrier's
tolerable delay against the *measured* window, not the design one. If the
tolerable delay exceeds the whole measured window, the barrier has no time to
act, whatever its PFD says.

**Output.** Per barrier: class, design window, measured window, compression
factor, and whether the compression invalidates the declared PFD. A human barrier
under a compressed window yields a gap, not an adjusted PFD — adjusting requires
an approved method.

## C4 — State and observability of redundant groups

**Rule.** For each voted group, determine the state — **intact**, **known
degraded** or **hidden degraded** — and apply the corresponding PFD.

**Why.** What separates the two degraded states is not the PFD: it is the clock.
Known degraded has a work order and a repair horizon in hours to days. Hidden
degraded runs to the next functional test, weeks to months away. The same
instantaneous PFD, integrated over different exposure horizons, gives very
different exposures.

**The observable, not just the record.** A voted group's degradation is often
visible in the data before it is visible in the maintenance record: the spread
between channels departs from noise. Report the measured spread against a
declared limit and the deviation of each channel from the median, next to the
state the record claims. Where reading and record disagree, that disagreement is
the finding.

**Output.** Per group: voting arrangement, channels by state, group state, PFD
applied, and the relevant clock — planned repair date, or next test date and the
date of the last one.

## C5 — Decidability gap

**Rule.** Name the questions that cannot be answered with the instrumentation and
records available now.

**Why.** This is the most actionable information context assembly produces,
because it points at a concrete external check — a field measurement, an
inspection, a test. A named gap is worth more than a fabricated estimate, and it
is the only honest output when the data does not exist.

**Where gaps come from.** Three recurring sources, each worth checking
explicitly:

- **No arbiter.** A voted group running degraded has no intact channel left to
  settle which reading is right.
- **An uninstrumented trigger.** A barrier whose demand trigger has no
  instrument cannot be shown to have been demanded, to have responded, or to have
  failed. Check that every declared demand trigger corresponds to something the
  dataset actually carries.
- **A missing layer.** When the last declared automated layer has acted and the
  excursion continues, the question is what lies downstream. If the design basis
  declares no layer between that one and the physical limit, say so.

**Output.** Per gap: the question, why current instrumentation does not answer
it, and the external check that would. Without the third part the gap is not
actionable.

## C6 — Side effect of the barrier action

**Rule.** Check whether the barrier's final element is shared with another
control loop or another barrier. Record the couplings the design basis declares
as secondary consequences.

**Why.** Barriers are designed against one specific top event. The action can
prevent that event and cause another by an unmapped route — and the route is
absent from the bowtie precisely because the bowtie is organised around the first
event.

**Independence is not all-or-nothing.** Read the design basis carefully here: a
pair of barriers can have independent *detection* and a shared *final element*.
The intuitive reading — "the operator reads the same transmitter" — is often
wrong, and the design basis is the only source that settles it. Where the
dependency sits changes the conclusion: shared detection means both barriers fall
to one sensor failure; a shared final element means both fall to one valve
failure, but a sensor failure takes only one.

**Output.** Per barrier: final element, what else uses it, the declared effect of
actuation on that loop, and where independence holds and where it does not.
Shared elements are evidence against independence: carry the finding into the IPL
check in phase B.

## C7 — Static indicator versus dynamic margin

**Rule.** Always present **distance and rate side by side**, against every
declared target. Never present distance alone.

**Why.** A variable can be further from a threshold and climbing faster — the
condition in which every conventional panel shows comfort while the real margin
shrinks. Time to the target, not distance, is the quantity that matters to a
barrier with a finite window.

**Every declared target, not just the alarm.** Alarm thresholds come from the
alarm configuration, but they are not the only targets that matter. Trip
setpoints and physical limits usually live in the design basis, and once a
variable has crossed the highest alarm threshold the alarm configuration has
nothing left to offer. Enumerate the targets from every declared source, and for
each report distance, whether it is already crossed, and time at the current
rate.

**Output.** Per flagged tag: value, thresholds already crossed with the
exceedance, the next target ahead with its source, distance, rate, the window
over which the rate was computed, and estimated time to the target. Time to
target is a calculation, not a reading — mark it, and suppress it when the rate
is small enough that the projection is noise.

## C8 — Persistent versus removable threat

**Rule.** Classify the threat. If it is the permanent loss of something the
process needs, no barrier produces a stable state: barriers buy time until the
upstream repair, and recovery comes from removing the threat.

**Why.** It changes what should be expected of the barrier, and therefore the
success criterion. Under a persistent threat, "the barrier worked" means "we
reached the repair alive", not "the process returned to normal". Judging a
persistent-threat barrier by the return-to-normal criterion fails it unfairly —
and the reverse, treating a removable threat as persistent, accepts a degraded
state as the best available.

**When the classification is not available.** Formal classification requires its
own experimental campaign, and the design basis will say whether it was run. If
it was not, the classification stays a gap. What can still be reported is the
observed behaviour: whether the affected variable recovers, whether it recovers
after the last automated layer acted, and whether the trend is within noise.
Behaviour consistent with a persistent threat is evidence, not a classification.

**Output.** The classification with its status, the evidence available, and the
success criterion that follows from it.
