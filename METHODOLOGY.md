# Safety Copilot — methodology

Full description of the stages, the data handling and the experimental protocol.
Reference document for the paper.

> **Not agent-facing.** This document contains the ablation map and names the
> source benchmark. It must stay out of the agent's read path and out of
> `/api/doc`. The Astra runner rejects a session whose environment prompt
> mentions this file.

Revision of 2026-09-17. Sections 2 to 4 describe the current agentic process
(v2: streaming replay, deterministic phase A, one isolated analyst). The first
configuration, a five-role panel on `kimi-k3`, is kept in Appendix A with its
calibration record, because some of its lessons shaped v2.

---

## 1. The problem

Process risk studies — HAZOP, LOPA, bowtie — are photographs. The plant they
describe changes continuously: equipment is replaced by a similar but
unapproved part, a campaign is extended, a functional test is rescheduled, a
certified technician leaves the contract. Each of those changes erodes the
protection without raising an alarm, because none of them is a process
deviation. When the demand finally arrives, the barrier the study credited is no
longer the barrier that exists.

Safety Copilot attacks the window between the erosion and the study's scheduled
revision.

---

## 2. Agentic process (v2)

```
masked database → stream replay → trigger grouping → phase A (Python)
               → phase B (isolated model session) → report.html + log.html
```

| Stage | Module | What it does |
|---|---|---|
| Masked feed | `blind_feed.py` | Only path from the database: translates tags, filters ground truth, cuts every field at `t_now` |
| Stream | `stream.py` | Replays a run point by point and watches process series and plant records |
| Trigger | `stream.py` | Groups what happened at one moment into one dated analysis |
| Phase A | `contexto.py` | Assembles and cross-checks the context. Code, no model |
| Phase B | `agente.py` (Claude), `astra.py` (GPT-6 Astra) | One analyst, governed by the `analise-seguranca` skill, interprets phase A |
| Report | `relatorio.py` | Two views over the same frozen context |

The method itself lives in `SKILL.md` and its four references
(`cross-checks.md`, `design-basis-barriers.md`, `producing-a-design-basis.md`,
`risk-analysis-reference.md`). The code implements what the skill specifies.

### 2.1 Stream and triggers

`stream.py` walks the series in time order as if it were live acquisition. The
horizon is sampled every 4 h and the episode every 5 s; RUN_A has 3,808 points
from 2025-01-01 to 2025-12-01T02:30:20. The virtual clock stops while an
analysis runs, so the analyst reads a coherent instant instead of a moving
target, and no sample is lost because the source is a table.

The detector watches two sides:

- **Process.** Alarm crossings from `alarm_config` without hysteresis, which
  reproduces `alarm_events` exactly (a test checks it), and spread between the
  channels of a voted group above 5 % of the tag's LOLO–HIHI range.
- **Records.** A work order opened, falling overdue or closed; a channel failure
  detected or repaired; a visible process event, such as the operating-condition
  change. Each record is dated at the instant operations would learn it
  (`blind_feed.eventos_de_registro`).

The second side exists because barrier erosion by the maintenance calendar never
appears in the process series. In RUN_A no alarm fired between January and 28
November; the five analyses of that period were opened by records alone.

Grouping rules. Triggers within 120 s form one analysis (the interlock event at
02:07:22 and the HIHI alarm at 02:07:30 are one demand). Groups made only of
records merge over one hour (a work order opened at 00:00 and the channel
failure it records, detected at 00:30, are one fact). An alarm type requests an
analysis once per tag per day; a channel discrepancy once per run. The end of the
record closes the stream with a final analysis. Each analysis gets an immutable
ID, `INC-BT-REATOR-<YYYYMMDD>-<n>`, and its own frozen phase A.

### 2.2 Phase A: context assembled by code

The skill says the phase A block "can be audited by inspection: either the figure
matches the database or it does not." That is only true if no language model
writes the block. `contexto.montar()` builds it in Python, with no network and no
writes, and every value carries its origin: direct reading, `computed` (with
formula and inputs), `assumption`, or `absent`. The module reimplements no
formula; it reads `blind_feed` and the BowTie v3 engines.

| Block | Content |
|---|---|
| **A1 · Design basis** | Barrier elements (detect–decide–act), design PFD per component, alarm ladder, and the declared basis: base case, windows, success criterion, invalidation criteria, threat classification |
| **A2 · Current state** | Active alarms with rate; distance and rate to every declared target (C7); rate by linear regression over 300 s (minimum span 60 s, reset across sampling gaps); a rate ladder for the same tag over declared windows (since 00:00, valley to t_now or to the trip, HI→HIHI, HIHI→SIS, after the SIS, last 10 min); voted-group statistics over at least 30 days, majority outlier and flat-channel test (±1.5 kPa band against the pre-change regime); regime before and after the last operating-condition change; work orders by class; contradictions between sources, reported under both readings |
| **Demand outcome** | Per barrier, anchored on its own demand: detect (channel values against the vote), decide (logic event or work order), act (final-element signature 5 min before versus after, 5 pp deadband), outcome (success criterion and whether the next layer was reached) |
| **A3 · Cross-checks** | All eight, each with the compared pair and a result or a declared non-applicability (table below) |
| **Engines** | Top event frequency on the design diagram and on current PFDs, with the conventional and the fuzzy engine, and the ratio |
| **Model assumptions** | Overdue competence sets a human PFD of 0.25; channel PFD λ_DU·t/2 from the last closed test; detected channel failure turns 2oo3 into 2oo2; an open corrective order on a 1oo1 item sets PFD = 1; items without test records stay at design PFD |
| **Recovery rules** | Alarms with start ≤ t_now, future end nulled, peaks recomputed up to t_now; work orders opened ≤ t_now with future closure, narrative and findings omitted; undetected channel failures masked; only known failures enter the PFD; only visible events |

| # | Cross-check | Output |
|---|---|---|
| C1 | Envelope: measured rate against the design rate, over several windows, plus each invalidation trigger | Ladder, triggers observed or not, verdict |
| C2 | PFD decomposition | Component and barrier multipliers, dominant element |
| C3 | Barrier class under window compression | Design versus measured window; human delay against the measured window |
| C4 | State and observability of voted groups | Intact, known degraded or hidden degraded, with the clock that applies |
| C5 | Decidability gap | Questions the data cannot answer, each with an external check |
| C6 | Side effect of the barrier action | Shared final elements and declared couplings |
| C7 | Distance and rate side by side | Every declared target, with computed time |
| C8 | Persistent versus removable threat | Classification status and observed behaviour |

Phase A never concludes. It closes with the list of what it could not verify,
which is input to phase B.

### 2.3 Phase B: one analyst, governed by the skill

The analyst receives phase A closed and writes only the judgement, in the skill's
order: fact, scenario and mechanism, three readings (bowtie, process, context),
risk judgement, recommendation, and evidence with a strength label
(`demonstrated`, `corroborated`, `inferred`, `undetermined`, `refuted`). The skill
fixes three barrier states (`healthy`, `degraded`, `critical`), lets an observed
demand outcome override a PFD, forbids fabricating tolerability, SIL or
consequence data, and forbids acting: the output is a recommendation with the
human decision left `pending`.

The invocation message carries what belongs to the experiment, not to the
method: the plant is anonymous and speculation about its origin stays out; cite
phase A fields instead of retyping figures; return markdown only; this is one
analysis in a stream, dated at `t_now`, and it knows nothing later; every
sentence needs a source; write in English. The message contains the phase A block
twice, as markdown and as JSON with the exact field paths.

### 2.4 Structural isolation of phase B

Instruction is advice; absence is a guarantee. Each analysis runs in a fresh,
text-only session with nothing available beyond the text the orchestrator sends.

| | Claude Opus 5 (`agente.py`) | GPT-6 Astra (`astra.py`) |
|---|---|---|
| Runtime | `claude -p` in a dedicated empty profile (`~/.claude-blind`), empty temporary directory, environment stripped of `CLAUDE*`/`ANTHROPIC*` | Codex CLI with a temporary `CODEX_HOME` holding only the credential, empty temporary directory, environment stripped of `CODEX_*`/`OPENAI_*` |
| Disabled | Tools, MCP, slash commands, session persistence, plugins, hooks, memory (`--safe-mode --tools "" --strict-mcp-config`) | Shell, apps, plugins, memories, browser, computer use, image tools, hooks, skill discovery, web search; read-only sandbox |
| Pre-run check | Preflight session must answer with the requested model and no isolation break | `debug prompt-input` probe must not contain memory summaries, `gabarito/`, the protocol or this file |
| Acceptance gates | Exit code 0; init event lists no tools, MCP, skills, plugins or commands; no tool use; only the requested model; all six sections; no provenance term in the output | Exit code 0; turn completed; no tool items; model confirmed in the session log; all six sections; no provenance term in the output |
| Inputs | System text: the same `approved_material()` for both (SKILL.md, four references, bowtie diagram), passed through `scrub()` | Same |

Both runtimes receive byte-identical system and user text for every analysis.
Any failed gate rejects the analysis: the attempt is archived in
`audit/failed_attempts/` and retried in a new session. A resumed run keeps an
accepted answer only if its inputs are unchanged: phase A and system text byte
for byte (Claude), or the recorded hashes of phase A, prompt and database
(Astra).
Each analysis folder keeps `context.json`, `context.md`, `system.md`,
`prompt.md`, the raw transcript, stderr, `meta.json` (hashes of every input,
model, usage, CLI version, isolation findings), `phase_b.md` and both HTML views.

### 2.5 Report and log

`relatorio.py` renders two views of the same `context.json`, and neither
originates a number. `report.html` is the decision for an operations reader:
safety banner, the phase B decision, charts with alarm bands and actuation
events, barrier cards `design → current`, demand outcome, top event frequency,
envelope, gaps and the dated sequence of analyses. `log.html` is the audit chain
for a reviewer: provenance of every input, recovery rules, the full rate ladder,
all eight cross-checks, contradictions and model assumptions.

### 2.6 Why one analyst replaced the panel

- **The A→B gate became a process boundary.** In v1, context curation was a
  model role (the curator). The skill's claim that phase A can be audited by
  inspection holds only if code builds it; the model is left with the judgement.
- **One method document.** The skill carries the cross-checks, the barrier
  states and the list of mistakes that every analysis applies, in place of
  separate role prompts.
- **Dated analyses instead of one cut.** v1 evaluated one instant at the end of
  the horizon. The stream opens an analysis at each qualifying trigger, so the
  sequence shows when the judgement changed and what changed it.
- **Isolation by construction.** The 2026-09-14 run, whose phase B was written
  inside the development session, leaked (section 4.4). The fix removed access
  instead of adding instructions.

---

## 3. Data

### 3.1 Origin

`data/blind/safety_copilot_v2.db`, a 19.5 MB SQLite database generated from a
scenario script over the Tennessee Eastman process, opened read-only. Three
layers with incompatible time scales, stitched together by calendar:

| Layer | Scale | Content |
|---|---|---|
| Process | seconds to hours | Tag series, alarms, deviation escalation |
| Reliability | months to years | Sensor channel state, PFD over time |
| Maintenance | continuous | Preventive orders (schedule) and corrective ones (failure) |

Eight tables: `series`, `alarm_config`, `alarm_events`, `process_events`,
`ativos`, `sensor_channels`, `failure_events`, `work_orders`. The 2026-09-11
revision added the feed flows and feed valve positions; without them the
actuation signature of B1 (closing the feeds) was invisible.

### 3.2 Experimental design — paired ablation

Four runs in two pairs. Each pair shares **the same physical reality** — the
same channel failures, the same threat injection — and differs **only in the
maintenance calendar**:

| Run | Pathway | Calendar | Expected outcome |
|---|---|---|---|
| RUN_A | pressure · PIT-7001 | degraded | trigger |
| RUN_B | pressure · PIT-7001 | current | no trigger (control) |
| RUN_C | temperature · TIT-9001 | degraded | trigger |
| RUN_D | temperature · TIT-9001 | current | no trigger (control) |

If the analyst escalates in all four, or in none, the experiment fails, however
good the reports look. The negative controls give the result its validity, and
the skill treats "barrier erosion not demonstrated" as a legitimate conclusion.

RUN_A, as generated: channel PT-007.A fails on 1 April and is repaired in 24 h;
the B1 functional test falls due on 31 May and is not executed; operator
competence for B2 falls due on 30 July and is not renewed; channel PT-007.B
freezes at the regime pressure on 29 August and its corrective order stays in
backlog; on 28 November load rises 15 % with no revalidation of the barrier
windows; on 1 December stream 1 feed is lost, pressure falls, then rises through
HI (01:57), HIHI (02:07, B1 demanded, logic commands nothing) and the SIS trip
(02:25), and the record ends at 2923 kPa (02:30).

Parameters: 12-month horizon, transmitters in 2oo3 with common-cause factor β,
functional test interval 8760 h, operator competence renewed every 4380 h.

### 3.3 Provenance masking and temporal cut

An LLM trained on technical literature recognises the benchmark's nomenclature
at once: receiving `XMEAS_7` is receiving the answer. Four layers, in
`blind_feed.py`:

**Nomenclature translation.** A declared, auditable table preserving the physical
function:

| Database | Anonymous plant | Function |
|---|---|---|
| XMEAS_7 | PIT-7001 | reaction vessel pressure |
| XMEAS_9 | TIT-9001 | reaction vessel temperature |
| XMEAS_8 | LIT-8001 | reaction vessel level |
| XMEAS_1 | FIT-1001 | stream 1 feed flow |
| XMEAS_2 / 3 / 4 | FIT-1002 / 1003 / 1004 | stream 2, 3 and 4 (A+C) feed flow |
| XMEAS_21 | TIT-2101 | cooling water outlet temperature |
| XMV_1 / 2 / 3 / 4 | XV-1001A / B / C / D | stream 2, 3, 1 and 4 feed valve opening |
| XMV_6 | FCV-0601 | purge valve |
| XMV_10 | FCV-1002 | cooling water valve |
| XMV-FEED | XV-1001 | feed block valve set (asset identifier) |

The campaign mass ratio and the scenario vocabulary of the load-change event
(`mudanca_caso_base`, `aplicado_na_simulacao`) are substituted as well; the event
reaches the analyst as `operating_condition_change`.

**Ground truth filter.** `process_events.visivel_copiloto = 0` never leaves the
module, and `failure_events`, which names the undetected failures, is never
queried. A channel failure not yet detected at
`t_now` is reported as `no_discrepancy_reported`, with no failure instant.

**Temporal cut.** Every published field is cut at `t_now`: future alarm ends are
nulled and open-alarm peaks recomputed up to `t_now`; a work order's closure,
final narrative and finding stay hidden until its closure date. Streaming made
this layer necessary. In batch mode the only instant queried was the end of the
horizon, where no future exists; at each stream point three queries leaked, and
one of them (future work-order closures) exposed the whole ablation from January.

**Check that fails loudly.** `scrub()` bars the benchmark's prefixes as families
(`XMEAS*`, `XMV*`, `IDV*`), its names and the scenario vocabulary, and raises on
any match. The same pattern runs over the exact prompt, the system text and the
model's answer. A contaminated blind test is worse than none, because it looks
valid.

**Adversarial validation (v1, `kimi-k3`, 2026-08-17).** Asked directly whether
it recognised the provenance of the masked data, the model listed plausible
candidates, including the correct benchmark by name, and discarded them all as
a proprietary synthetic dataset. This probe has not been repeated on the v2 feed
or models.

### 3.4 What the analyst receives and what it does not

**Receives:** the phase A block of its instant (markdown and JSON), which covers
14 masked tags with rates, the individual channels of the voted transmitter,
active and normalised alarms, work orders with the text known at `t_now`,
reported channel state, visible operational events, the asset-derived PFDs, both
engines' top event frequencies, model assumptions and recovery rules; and, as
system text, the skill, its four references and the bowtie diagram.

**Does not receive:** which threat was injected, when, or that one exists;
`failure_events`; invisible process events; anything dated after `t_now`; the
earlier analyses of the stream; the answer key, the protocol or this document.

---

## 4. Evaluation protocol

### 4.1 What is measured

v2 measures interpretation quality over a deterministic phase A, not autonomous
detection. The deterministic layers compute the numbers; the model is judged on
what it concludes from them. The 4/4 discrimination result of v1 (Appendix A)
belongs to the previous configuration and must not be reported as a v2 result.

### 4.2 Blind runs

Each model replays the same run through the same stream, phase A and approved
material, in its own output folder
(`state/analises/RUN_A_<MODEL>_<UTC stamp>/`). Accepted runs on RUN_A:

| Run folder | Model | Analyses | Notes |
|---|---|---|---|
| `RUN_A_GPT6_ASTRA_20260914T225032Z` | GPT-6 Astra, reasoning effort high | 14, 0 tool calls | Nine early entries built on a previous input version were superseded and redone in new sessions |
| `RUN_A_CLAUDE_OPUS_5_20260915T145836Z` | Claude Opus 5 | 14, text-only | Resumed once after a session-limit rejection at analysis 8 |

Comparability is checked by hash: for every analysis, `context.md`, `system.md`
and `prompt.md` are identical across the two runs.

### 4.3 Rubric

Scored against the dated narrative of the run and the phase A of each instant:

| Dimension | What to evaluate | Scoring |
|---|---|---|
| Factuality | Correct usage of tags, alarms, trends and SOPs | 0–2 per item |
| Critical coverage | Inclusion of mandatory causes, mechanisms and risks | Binary checklist + score |
| Causal coherence | Step-by-step logical progression without leaps | 0–2 per step |
| Grounding | Support of each claim by case evidence | Percentage of supported claims |
| Action safety | Compliance of recommendations with limits, SOPs or barriers | Pass/fail + severity |
| Operational appropriateness | Suitability of the action for the real-world context | 1–5 per expert |

The rubric defines no weights, so dimensions are reported separately. Item lists,
steps and severity levels are fixed before scoring and applied identically to
both models. Grounding combines an automated check (figures and cited field
paths resolved against `context.json`, with a perturbation control for chance
matches) with a manual list of unsupported interpretive claims. When the
evaluator is itself a model under test, the conflict is declared and the 1–5
score is left to the expert panel. The filled rubric for both RUN_A runs is in a
separate evaluation document.

### 4.4 Known limitations and discarded runs

- **Contaminated run, 2026-09-14.** Discarded. Leaks: phase B written by the
  development session; the load-change event reaching the agent with scenario
  vocabulary; an alarm peak and a work-order closure text from the future; a
  report timeline listing later decisions; `cross-checks.md` carrying episode
  figures; the asset name `XMV-FEED`. Each leak now has a fix and, where it can
  regress silently, a test.
- **Example command in SKILL.md.** Line 37 carried `--run RUN_A --at
  2025-12-01T02:30:20`, the end of the record, and reached all 28 sessions of
  both accepted runs. It was found after the Opus run and fixed on 2026-09-15; a
  test now rejects any timestamp or run label in the approved material. No
  phase B cites a timestamp later than its own `t_now`. Whether the string
  influenced the reasoning cannot be determined; a clean rerun or a declared
  limitation is still to be decided.
- **Phase A defects visible to the analyst.** On the day of the load change the
  regime shift is printed as `None kPa`, and the voted-group revalidation flag is
  fixed at `false` rather than read from records.
- **Masking probe.** The adversarial provenance probe predates v2 (section 3.3).

### 4.5 Verification suite

`python3 -m pytest test_safety_copilot.py` — nine tests covering the logic that
breaks silently: prefix-family masking; no published timestamp after `t_now`;
the detector reproducing `alarm_events`; alarm peaks and future work-order
narratives not changing an earlier context; approved references free of episode
results; a closed phase A (eight cross-checks, both C2 multipliers, rate beside
every distance, a declared rate ladder); PFD counting only known failures; and
stream triggers on both the calendar and the records.

---

## Appendix A — First configuration: five-role panel (superseded)

Kept as written, for the calibration record. The modules named here (`tep.py`,
`corpus.py`, `mesa.py`, `prompts/`, `trajetoria.py`) are no longer in the tree;
`bridge.py` and `trigger.py` remain for live mode.

### A.1 Seven-stage architecture

The system is a pipeline, and the panel's navigation is the pipeline itself —
not a menu of screens.

```
 process → acquisition → evaluation → trigger → context → panel → report
```

| Stage | Module | What it does |
|---|---|---|
| **Process** | `tep.py`, `blind_feed.py` | Live data source: simulator or experiment database |
| **Acquisition** | `bridge.py` (`read_tags`) | Tag ingestion, on an editable cycle or on demand |
| **Evaluation** | `bridge.py` (`evaluate`) | Each bowtie computed twice — design versus current |
| **Trigger** | `trigger.py` | Freezes the state into a JSON package when the erosion crosses the threshold |
| **Context** | `corpus.py` | BM25 corpus plus normative RAG, separating standards from operational memory |
| **Panel** | `mesa.py`, `prompts/` | Deduction, induction, abduction and synthesis |
| **Report** | `relator` | Diagnosis, chain, barriers, actions, human signature |

#### Why two calculations per bowtie

`evaluate()` runs each diagram **twice**: once with the design frequencies
declared in the `.txt`, once with the PFDs derived from the current process. The
system does not report absolute risk — it reports **erosion**, the distance
between what the study credited and what the plant delivers today.

Erosion is normalised between 0 (design basis) and 1 (trigger), which gives a
figure comparable across bowties of different scales. Three-level state:
nominal, attention (erosion ≥ 0.5), critical (threshold crossed).

One recorded methodological correction: the first version marked "attention" at
the halfway point of the **absolute** threshold, which classified the design
basis itself as attention whenever the threshold was less than 2× the design
value. The correct normalisation is between design and trigger.

#### Why three separate inference modes

This is not epistemological decoration. Each mode fails in a different way, and
separating them makes the failure visible:

- **Deduction** starts from a declared rule and cannot go beyond it. It fails
  through a missing premise — and the prompt forces it to declare the absence
  rather than fill it with general knowledge.
- **Induction** starts from cases and generalises. It fails through a small
  sample — and the prompt forces it to declare `n` and look for a
  counterexample.
- **Abduction** proposes an unrecorded cause, including organisational ones. It
  fails through confirmation bias — and the prompt forces it to generate
  hypotheses along three axes and to name the test that refutes each one.

**Convergence between independent modes is the system's strongest signal;
divergence is where data is missing.** The synthesising agent is forbidden from
dissolving divergence into a middle ground.

#### What the panel received

Readings from 10 masked tags including the individual channels of the voted
transmitter; an 8 h decimated trend window; alarms that occurred with demand
marking; work orders with free text; reported channel state; visible operational
events; the asset table with arrangement, MTTF, β, test interval and design PFD.
Data at that time: a 14 MB database, base series at 60 s with the episode at
1–5 s.

### A.2 LLM engine

`kimi-k3` via `api.moonshot.ai/v1`. Constraints found by diagnosis, not
documented in the request, which shaped the design:

| Constraint | Consequence |
|---|---|
| Accepts **only `temperature=1`** | HTTP 400 on any other value. No temperature variation between agents |
| **3 requests/minute** per organisation | No parallelism. Panel serialised by a global limiter |
| Reasoning model: `content` + `reasoning_content` | A tight budget makes the reasoning consume everything and `content` come back **empty** — a failure that looks like a blank answer. Retry with automatic expansion |
| The endpoint is `api.moonshot.ai` | `.cn` answers 401 with the same key |

#### Auditability

Each call wrote, into `state/mesa/<run>_<tag>/`:

- `transcript.jsonl` — the prompt, and the complete `content` and
  `reasoning_content`, with token usage, `finish_reason` and attempt number
- `<agent>.md` — the answer
- `<agent>.reasoning.md` — the reasoning
- `dossie.json` — exactly what was injected
- `meta.json` — timings, tokens, sequence

**The reasoning is what makes the blind test measurable.** Without it there is no
way to separate "the agent concluded correctly" from "the agent guessed
correctly" — and in a blind test that difference is the result.

### A.3 Calibration protocol

Prompt calibration was done **before** the blind round, on RUN_A, under a single
rule:

> **The prompt encodes method, never a finding.**

No prompt may mention a frozen channel, an overdue test, a voting discrepancy or
any element of the ground truth. What gets calibrated is form: the discipline of
citing evidence, the output format, the obligation to declare sample size, the
legitimacy of concluding that nothing happened.

That is why re-running RUN_A in the blind phase remains valid: the prompts carry
no RUN_A-specific knowledge. The same rule governs `SKILL.md` and its references
in v2.

### A.4 Calibration rounds

#### Round 1 — baseline

Run on RUN_A with the initial dossier. The curator finished in 275 s (24,054
input tokens, 6,590 of reasoning) and **delivered three defects of the dossier
itself** — the agent auditing the orchestrator:

| # | Defect | How it surfaced | Correction |
|---|---|---|---|
| 1 | `alarm_config` missing from the dossier | The curator **inferred the thresholds by interpolation** between the alarm instant and the series, explicitly marking it as an estimate and not data | Field `limiares_de_alarme` added |
| 2 | 77 % of the prompt was series in verbose JSON (`{"ts":…,"v":…}` × 637) | Measured while sizing the payload | Compact format with pre-computed statistics — dossier 62 % smaller |
| 3 | An 8 h window requested where there were 5 h of data | The curator pointed out that "no series contains points between 21:00 and 00:00" | Window limited to what was available |

Finding 1 is the most instructive: the agent neither stalled nor hallucinated the
threshold — it reconstructed it by interpolation and **declared the method**.
That is the behaviour the citation discipline is meant to produce.

#### Round 2 — termination regression

The optimisation from finding 2 introduced a failure: five consecutive 15 min
timeouts, 75 minutes with no answer. The investigation, possible because the
transcript keeps the full prompt of every call:

| Test | Result | Rules out |
|---|---|---|
| Trivial call, `max_tokens` 200 and 14,000 | OK, 4–10 s | API health |
| New dossier, isolated call after 70 s of silence | timeout at 600 s | Rate limiting |
| **Replay of round 1's exact prompt** | **OK, 200 s** | A change at the provider |

The replay is the decisive test, and it exists only because auditability was
implemented before calibration: the same input that worked before, resent
afterwards, separates "my payload changed" from "the provider changed".

**Recorded method lesson:** reducing tokens is not free. A pure numeric array is
smaller than labelled pairs, but it can cost a reasoning model its
*termination* — the payload gain turned into a total loss of answer. In a
reasoning model, prompt optimisation has to be validated by conclusion, not by
size.

### A.5 Risk trajectory and directed retrieval

Two layers added after the first round, on finding that the implemented flow was
not the designed flow.

#### What was broken

The system evaluated the bowtie at **a single instant** — the analysis cut. The
function `pfd_confiabilidade()` was always a function of time, but every caller
invoked it with one `ts`. The effect: the panel saw *that* a barrier was
degraded and never *when* it became so, nor what made it so.

In parallel, the corpus was **empty**. Work orders reached the panel only as
structured JSON inside the dossier; nothing was retrievable by search. The
system described itself as supported by RAG without having an indexed document.

#### Trajectory — `safety_copilot/trajetoria.py`

Each run's horizon is swept at a **daily step** (335 points from 2025-01-01 to
2025-12-01). At each point the PFDs of every barrier and the top event frequency
are recomputed, by the same `bridge.evaluate()` that feeds the panel — there is
no second implementation of the bowtie mathematics.

The step is daily because that is the granularity of the maintenance calendar
itself: due dates and closures fall at 00:00. A smaller step refines the curve
without refining the answer; a larger one loses the crossing date. Verified: at
a weekly step RUN_A's second crossing was dated 03 Sep and attributed to "no
event that day"; at a daily step, 29 Aug, coinciding with the PT-007 channel
failure.

Three mechanisms produce three distinct shapes in the curve, and the shape
identifies the mechanism before any text does:

| Shape | Mechanism |
|---|---|
| continuous ramp | ageing between tests, PFD₁ = λ_DU·t/2 |
| step | loss of redundancy: 2oo3 → 2oo2 through a failed channel |
| drop | maintenance executed, interval restarted |

The output is not the raw curve but its reading: the crossing dates of each
threshold, the barrier each crossing is attributed to (largest PFD change in the
step), the calendar events of the same day, the apportionment of the rise by
barrier, and the fraction of the horizon outside criterion.

**Apportionment suppressed in a compliant plant.** When the final ratio falls
below 1.05×, the total rise is numerically noise, and dividing it among four
barriers produced readings such as "B3 accounts for 38 % of the rise" in a
healthy control — the reading that gets a work order opened against a barrier
with no problem. Below the cut-off, the apportionment is `null`.

#### Directed retrieval — RAG

The curator indexes each run's operational records (`corpus planta --run`): work
orders with their free text, visible process events, and alarm history
aggregated by loop, including how many constituted a demand on a barrier.
Everything passes through `scrub()`, which raises on any term from the source
benchmark.

**`failure_events` is not indexed.** It is the scenario's physical truth: it
names the frozen channel nobody detected, with `detectavel=0`. `context()`
spends code hiding it, and indexing it would open a retrieval door around that
masking.

The query **is not generic**. It is built from the trajectory's crossings — the
item, the barrier and the type of event that date each exceedance. The bridge
decides what to ask about, the corpus answers, the panel interprets.

**Scoping by run.** The corpus is a single index over all four runs. Without a
filter, a query starting from RUN_A returned RUN_B's equivalent order — the
ablation's control arm, same item, opposite outcome ("renewed on time"). The RAG
would become a side channel between the arms, bypassing through retrieval the
isolation the dossier maintains. Verified: it was happening. `search(escopo=...)`
filters in SQL, before the `LIMIT` cut.

#### What this changed in the question put to the panel

Before, the dossier **omitted** the computed PFD deliberately, so that the panel
would infer degradation from raw evidence. That was ablation-test discipline, and
under it the panel discriminated 4/4.

With the trajectory in the dossier, the panel does not discover *whether* there
is degradation — it answers **when** the risk stopped being acceptable, **why**
on that date, **what mechanism and vulnerability** the episode exposed, and
**which decision** is feasible. v2 keeps this division of labour: the
deterministic layer quantifies, the model interprets.

#### Cost and what made it feasible

The daily sweep cost 2 s per point (45 min for all four runs). The profile showed
that 93 % of the time sat in a single query — `SELECT MIN(ts) FROM series WHERE
run_id=?`, at 149 ms against 0.1 ms for all the others combined: the existing
index covers `(run_id, tag, canal)` and not `ts`, so the query scans the run's
~45 thousand rows. The value is constant (it is the start of the horizon) and it
was inside the loop.

Memoising it, plus memoising the bowtie's design-state calculation — also
invariant, and reparsed at every evaluation — took the sweep from 95 s to 16 s
per run, with no change of algorithm. Memoising was chosen over creating an
index: the experiment database is opened read-only and the analysis must not
alter it.
