# Process risk analysis reference

Use this as an adaptable checklist. Do not turn every item into a report
section; record only those that change the decision or qualify your confidence
in it.

## 1. Scenario quality

A useful scenario contains a specific initiating threat, a defined top event, and
a consequence with a receptor. Avoid vague events such as "system failure".

Check:

- physical limits, inventory and hazardous properties;
- operating phase: normal, start-up, shutdown, cleaning, maintenance or
  emergency;
- internal, external, natural and cyber causes, and plausible domino effects;
- consequence for people, environment, community and critical assets;
- geographic scope, duration and weather conditions where applicable.

Different bowties can share a threat, a utility, a control system, a crew, a
location or a consequence. Treat that as dependence until demonstrated otherwise.

## 2. Barrier performance

For each barrier, look for a verifiable requirement:

- **functionality:** what it must detect, prevent, control or mitigate;
- **availability and reliability:** when it must be ready and with what credit;
- **response time:** whether it acts before the scenario becomes irreversible;
- **capacity:** whether it withstands the predicted demand;
- **survivability:** whether it stays effective in the accident environment;
- **human dependence:** the real time, information, access, workload and
  competence;
- **verification:** the test, inspection or indicator that demonstrates the
  function.

For barrier state, use the three states declared in SKILL.md — `healthy`,
`degraded`, `critical`. Where a demand has occurred but its outcome is not yet
classifiable, say so explicitly in the text rather than inventing a fourth state:
the distinction between "demanded, outcome unknown" and "demonstrated failure"
changes the conclusion and must survive into the report.

An existing barrier is not automatically an IPL. For quantitative credit, use
only the decision documented in the approved analysis, and confirm independence,
specificity, effectiveness and auditability. Review:

- common sensor, logic, actuator, power or utility;
- the same person or procedure in more than one layer;
- basic process control shared with protection;
- common vulnerability to fire, flood, explosion or blocked access;
- simultaneous maintenance, bypass or testing;
- degradation affecting several barriers at once.

Where the design basis distinguishes independence in detection from independence
in actuation, carry that distinction into the credit decision. Shared detection
and a shared final element fail in different ways and are not interchangeable.

## 3. Quantification and uncertainty

Keep these separate:

- initiating threat frequency;
- barrier probability of failure;
- top event frequency;
- conditional probability and severity of each consequence;
- the risk measure the organisation uses.

Record units and exposure period. Do not mix per-demand, per-hour and per-year
frequencies without a justified conversion. Do not use more precision than the
input data carries.

Run a sensitivity check when the classification depends on an uncertain
assumption. Prefer a range, or bounded/base/conservative scenarios, to a falsely
precise point. Uncertainty does not reduce risk; it reduces confidence in the
decision and can raise the need for caution.

The monitor's attention threshold is not necessarily the risk acceptance
criterion. Acceptance, ALARP or equivalent requires a method and an authority
defined by the facility.

Where two engines produce different magnitudes for the same quantity, do not
average them and do not present one as a check on the other. Say which engine
produced which figure and what each is for.

## 4. Integrity and change

Look for a connection between the scenario and:

- inspection and functional or proof testing, calibration, and test coverage;
- damage mechanism, age, service environment and degradation rate;
- recurring defect, temporary repair, overdue maintenance and backlog;
- non-equivalent parts, obsolescence and supplier changes;
- altered logic, software, tuning, alarms and interlocks;
- changed feedstock, catalyst, inventory, rate or operating envelope;
- changed crew, responsibilities, budget, maintenance frequency or supervision;
- the deadline and reversion condition of a temporary change;
- the pre-start-up or return-to-service safety review.

Informal change and persistent operational deviation deserve management-of-change
triage. Do not declare MOC mandatory, or a non-conformance, without checking the
applicable rule.

A load or setpoint change without revalidation of the barrier windows belongs
here and in C1: it is both an integrity finding and an envelope invalidation
trigger.

## 5. Human and organisational factors

Avoid "human error" as a terminal cause. Examine:

- procedure clarity, availability and realistic adherence;
- fit of training and experience to the task;
- actionable alarms, prioritisation, flooding and interface quality;
- diagnosis and response time under realistic conditions;
- workload, fatigue, staffing, communication and shift handover;
- ergonomics, access, lighting, noise and PPE use;
- goal conflicts, incentives, supervision and normalisation of deviance;
- task design for error prevention, detection and recovery.

Credit a human action only where indication, time, competence, access and means
of actuation are all compatible with the scenario. Where the design basis states
that the whole margin of a human barrier is perception and decision rather than
execution, a compressed window removes the margin even with competence current.

## 6. Response hierarchy

Before recommending, test whether the measure:

1. reduces the hazard or merely displaces the risk;
2. acts on the threat, the top event or the consequence;
3. depends on an already degraded barrier or on a common cause;
4. creates a transient, a maintenance exposure or a new scenario;
5. requires MOC, hazard review, training or operational readiness;
6. has an owner, a deadline, an indicator and an effectiveness criterion.

Compensatory measures need explicit validity, owner, monitoring, withdrawal
condition and residual risk. Long-term recommendations do not replace the
immediate decision about safe operation.

Instrumenting an uninstrumented demand trigger belongs at the top of this
hierarchy, not the bottom: a barrier whose demand cannot be observed cannot be
credited or audited, whatever its PFD.

## 7. Strength of the conclusion

- `demonstrated`: a primary source and an applicable model support the link;
- `corroborated`: two or more independent sources converge;
- `inferred`: the mechanism is consistent but depends on an identified
  assumption;
- `undetermined`: relevant hypotheses remain equivalent;
- `refuted`: the evidence is incompatible with the hypothesis.

Overall confidence must never exceed that of the weakest decisive link. A
low-confidence conclusion can justify conservative action, but must state why.

## 8. Closure evidence

Require evidence proportional to the safety function:

- post-repair testing covering the relevant failure mode;
- documented restoration of any bypass, isolation or configuration;
- a stable trend over a technically justified window;
- document and training updates where a change occurred;
- residual risk review and acceptance by the competent function;
- revalidation of the design basis windows where the operating condition changed;
- tracking of systemic actions, without hiding them behind closure of the
  immediate condition.
