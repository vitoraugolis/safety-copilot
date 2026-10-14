# Blind test protocol — anonymous chemical plant

**Model:** `kimi-k3` via `api.moonshot.ai/v1` · **Started:** 2026-08-17

> **Not agent-facing.** This document names the source benchmark on purpose, to
> record what the masking layer hides. It must stay out of the agent's read path
> and out of `/api/doc`.

---

## Experiment design (from `banco_dados_spec_v05` and `roteiros_cenarios_v08`)

Four runs, paired ablation. Each pair shares **the same physical reality** — the
same channel failures and the same threat injection — and differs **only in the
maintenance calendar**. That difference is the thesis.

| Run | Pathway | Calendar | Expected outcome |
|---|---|---|---|
| RUN_A | pressure (PIT-7001) | degraded | trigger |
| RUN_B | pressure (PIT-7001) | current | no trigger (control) |
| RUN_C | temperature (TIT-9001) | degraded | trigger |
| RUN_D | temperature (TIT-9001) | current | no trigger (control) |

The full ground truth is in `gabarito/`, outside git and outside any prompt.

---

## Masking barriers

Three independent layers, in `safety_copilot/blind_feed.py`:

**1 · Nomenclature translation.** The database uses the variable nomenclature of
a public benchmark (`XMEAS_*`, `XMV_*`), which any LLM recognises immediately.
The `ALIAS` table translates it into generic-plant ISA-5.1 tags, preserving the
physical function:

| Database | Anonymous plant | Function |
|---|---|---|
| XMEAS_7 | PIT-7001 | reaction vessel pressure |
| XMEAS_9 | TIT-9001 | reaction vessel temperature |
| XMEAS_8 | LIT-8001 | reaction vessel level |
| XMEAS_1 | FIT-1001 | stream 1 feed flow |
| XMEAS_21 | TIT-2101 | cooling water outlet temperature |
| XMV_10 | FCV-1002 | cooling water valve |
| XMV_6 | FCV-0601 | relief valve |

Also substituted: `{"modo": "G/H 50-50"}` → `"campanha padrao"` (the G/H mass
ratio is a benchmark signature).

**2 · Ground truth filter.** `process_events.visivel_copiloto = 0` never leaves
the module. A sensor channel whose failure has not yet been detected is reported
as `sem_discrepancia_reportada` with a null `ts_falha` — real operations would
not know about it, and publishing it would hand over the answer.

**3 · Leak check.** `scrub()` runs a list of forbidden terms over everything
that leaves and **raises** if anything escapes. Failing loudly is deliberate: a
contaminated blind test is worse than none, because it looks valid.

### Audit — all runs

```
RUN_A: CLEAN |  5138 bytes exposed | 1 ground-truth record withheld | 10 tags
RUN_B: CLEAN |  5572 bytes exposed | 1 ground-truth record withheld | 10 tags
RUN_C: CLEAN |  6513 bytes exposed | 1 ground-truth record withheld | 10 tags
RUN_D: CLEAN |  6947 bytes exposed | 1 ground-truth record withheld | 10 tags
```

### Adversarial probe (kimi-k3, 2026-08-17)

Asked directly whether it recognised the provenance of the masked data:

> **nao identifico procedencia** — the tag nomenclature (FIT/PIT/LIT/TIT with
> four digits) generically resembles the ISA style of SWaT, but does not
> correspond to any known public dataset (SWaT, WADI, BATADAL, **Tennessee
> Eastman**, HAI) […] indicates a proprietary synthetic dataset.

The model had the correct benchmark among its candidates and **discarded it**.
That is the strongest validation available without running the blind test twice.

---

## Provider operating constraints

Found by diagnosis, not documented in the request:

| Constraint | Effect on the design |
|---|---|
| `kimi-k3` accepts **only `temperature=1`** | Any other value is HTTP 400. The panel cannot vary temperature between agents |
| **3 requests/minute** per organisation | Prevents parallelism. The panel is serialised by a global `RateLimiter` (20 s between calls) |
| Reasoning model: `content` + `reasoning_content` | On a tight budget the reasoning consumes everything and `content` comes back **empty** — it looks like a blank answer. Generous `max_tokens` plus retry with automatic expansion |
| The endpoint is `api.moonshot.**ai**` | `.cn` answers 401 with the same key. The panel was pointing at `.cn` |

Cost implication: one complete panel round (5 agents) takes at least ~100 s of
queueing alone, before inference time. Refinement loops multiply that.

---

## What the panel receives

Per run and instant:

- **Readings** — 10 masked tags, including the three individual channels of the
  voted transmitter (it is the discrepancy between channels that reveals
  degradation).
- **Context** — alarms that occurred, work orders with free text, reported
  channel state, visible operational events, and the asset table with
  arrangement, MTTF, β, test interval and design PFD.

What it does **not** receive: which threat was injected, when, or that one
exists at all.
