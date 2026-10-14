# Producing a design basis that does not exist

Load this reference when a bowtie has no declared design basis. The procedure is
experimental and applies to any simulable process. Produce the basis **before**
assembling context: without a declared envelope, cross-check C1 has nothing to
compare against, and C3 cannot quantify window compression.

A worked example, for the reactor bowtie, is in
[design-basis-barriers.md](design-basis-barriers.md).

## Procedure

1. **Declare the base case** — operating mode, steady-state values of the
   relevant tags, and the source of that declaration.
2. **Inject the threat** into the base case and record the crossing time of each
   threshold, plus the local rate of change at each. Use at least two seeds.
3. **Derive the windows** between each threshold and the final limit. These are
   the reference windows for every barrier on the pathway.
4. **Measure each barrier's maximum tolerable delay**: vary the delay of the
   action until you find the tipping point. This is the **effectiveness
   envelope**, distinct from the PFD and frequently forgotten.
5. **Note where the available time sits.** If the trajectory has a plateau, most
   of the barriers' margin is concentrated there, and that distribution is a
   property of the base case. Record it explicitly, so a later analysis can test
   whether the plateau still exists.
6. **Repeat under the relevant alternative condition** (different load,
   different mode) and tabulate the sensitivity.
7. **Test threat removal** to classify it under C8.
8. **Declare the invalidation criteria** — the conditions under which the basis
   must be treated as unverified. A rate threshold above which the measured
   windows no longer hold is the minimum; add any change that would move the
   windows, such as a base-case change without revalidation, a threshold change
   in the alarm configuration, or a change of voting arrangement or test
   interval.

Step 8 is what makes the document usable in an analysis rather than only in a
review. Without declared invalidation criteria, an analyst comparing current data
against the basis has to invent the threshold at which the comparison stops being
valid, which is exactly the fabricated parameter the method forbids.

## Beware the success criterion

Define each barrier's success criterion **explicitly, before the measurements**.
Different criteria over the same data support opposite conclusions. These three
are not equivalent and can disagree:

- "no shutdown"
- "the threshold was not reached"
- "the variable reverted"

Record which one was used, in each measurement. Where the barrier action causes a
shutdown by another route — a coupling of the kind C6 looks for — say whether
that counts as a failure of the barrier against the top event, or as a declared
secondary consequence.

## Document template

Fill one block per barrier. A field with no data gets `not demonstrated` — never
a typical value.

```markdown
# Design basis — <bowtie_id> / <barrier>

## Identity
- bowtie_id:
- pathway:
- barrier:
- revision / date:
- source of the declaration:

## Base case
- operating mode:
- relevant tags and steady-state values:
- source:

## Elements (detect–decide–act)
| Role | Item / tag | Contribution to PFD | Source |
|------|-----------|---------------------|--------|
| detect | | | |
| decide | | | |
| act    | | | |

- design PFD of the barrier:
- dominant element:

## Actuation time
- class: automatic (seconds) | human (minutes)
- declared actuation time:

## Demand trigger
- signal that constitutes a demand:
- is this a backup barrier? whose failure is its trigger?
- is that signal instrumented in the dataset?

## Validity envelope
- operating condition under which it was measured:
- reference rate of change (per threshold):
- measured windows (threshold → final limit):
- where the available time sits (plateau, if any):
- maximum tolerable delay (effectiveness envelope):
- invalidation criteria:

## Sensitivity
| Alternative condition | Window | Max tolerable delay | Note |
|-----------------------|--------|---------------------|------|

## Declared side effects
- shared final element:
- effect of actuation on other loops:

## Threat classification (C8)
- persistent | removable
- evidence from the removal test:

## Success criterion used in the measurements
- exact wording:

## Gaps
- <parameter> — not demonstrated, because:
```
