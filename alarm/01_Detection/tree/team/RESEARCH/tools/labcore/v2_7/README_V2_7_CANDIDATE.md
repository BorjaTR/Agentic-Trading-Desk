# labcore V2_7 CANDIDATE (labcore/v2_7) — NOT RELEASED

Built by ctxprof_shared for STRATEGY/LEAD, 25 Oct 2026 (A46R REL-01). Owner of labcore: LAB1. Promotion needs a LAB1 release
cycle; LAB1 is stopped, so that authorization is **PENDING** (never done). The released labcore stays V2_6, unchanged: every
V2_6 file and pin is the same, and its own tests still pass. These modules sit in the sub-package `labcore/v2_7` so the V2_6
registry test (L11) and no-write test (L12) stay true; promotion moves them into `labcore/` in one step with their
`FUNCTIONS_V2.tsv` rows.

```python
sys.path.insert(0, '<forensics>/team/RESEARCH/tools')
from labcore.v2_7 import selection, runs, cache, series, rows, quality
```

## Set list additions

| item | module | what it does | used by now |
|---|---|---|---|
| population selector | `selection.select` | `list`, `coin:X`, `coins:A,B`, `all`, `group:NAME` (+ group file), `roster` (weekly roster of record), over a caller range | run_parallel (Profile, Context) |
| situations' selector interface | `selection.resolve_selection` | `--coins A,B\|ALL`, `--group-file F --group NAME`, membership checked | ready for event_situations |
| checked whole run | `runs.check_stage`, `plan_identity`, `find_resumable`, `adopt_for_resume`, `replay_diff`, `adopt` | expected day-parts, seals, source pins, lab vintages; resume; replay; consumer door | run_parallel (Profile, Context) |
| run publication (imported) | `runs.stage/commit/abort/load_complete/verify_committed` | re-exported from `event_decisions/run_manifest_candidate.py` (decisions_fixer), never copied | run_parallel, event_decisions, event_outcomes |
| cache identity | `cache.IdentityCache`, `key`, `vintage` | in-memory cache served only for the same kind, code, entity, dates, clock, settings and source vintage | alarm_context_ed2 (index sha16 cache keyed by vintage) |
| typed clock-series reader | `series.read_day_typed`, `parts_holding`, `ClockSeries`, ... | RE-EXPORT of event_profile/clock_series.py (owner event_profile; the physical move waits for LAB1) | event_profile |
| store-side roster rule | `selection.roster_unknown` | REGISTERED from alarm_context_ed2's rule: coins no PRICE index of a readable built day up to last names, inside the caller window | Context keeps its frozen copy until LAB1's promotion switches its import (F1 open) |
| **THE one quality rule (S2)** | `quality.known`, `quality.counts` (LAB1) | a lab3 clock cell is KNOWN only when v is finite, e == 0 (a reason id, or the ABSENT byte beside a finite value, is not known), a >= 0, o >= 0, and k is set and <= its column time; a field the part does not list is passed as None. Every reader masks v with it: import it from here, never write a local copy | Profile clock_series, Context ed2 layer, Outcomes EPI units, idea_to_grade detect (adoption by each owner, FIX_ROUND3 S2) |
| window first (S3) | `selection.check_window`, `in_window`, `roster_universe`; `window=` on `select`, `resolve_selection`, `roster_unknown`, `weekly_roster` | the caller window is checked before any file opens; every roster, listing or index scan opens only days inside it, never the day before; the first step's predecessor is unknown (SHARED_S3_NOTE_V2.md) | Outcomes (A51R2-01), Cause (R2-03), Context, the dispatcher |
| canonical rows (fixed) | `rows.canon_rows` | labcore/_rows.py's form with a NaN or None cell beside a number sortable (V2_6 raises TypeError); LAB1 request for V3 | Context H2 controls |

## Selection rules

- The date range is always the caller's. Every requested day must pass `lab3/law.py`, else `SEALED_REQUEST`.
- Membership, not syntax: a coin is valid only when the canonical roster names it. The canonical roster is DEV2's
  `ROSTER_BUILD.json` (the union of the lab PRICE indexes, each pinned by sha256; its pins for the requested days are rechecked)
  plus the members of the roster-of-record weeks in the range. Unknown coin or group: refused by code.
- A valid selection with no event is `EMPTY_SELECTED_POPULATION`, a successful result with its coverage.
- The resolver is DEV2's `shared_population_v2/population.py` (OX-CODE1 approved) and `event_selection.py`, imported by pinned path.
- Coverage: requested (kind, members, dated intervals, group gaps, roster weeks read, aliases), list rows in and out of range,
  excluded rows by reason, observed events by day and coin, and the source state of every selected event
  (`IN_SOURCE`, `NOT_IN_SOURCE`, `SOURCE_NOT_DECLARED`). Never `PRELISTING`: there is no listing source here.
- A week with no roster file is `GROUP_NOT_EFFECTIVE`. The one declared alias (`ROSTER_WEEK_ALIASES_V1.json`: the week of 29 Sep 2025
  uses the 6 Oct roster) comes from the roster's own receipt.

## Measured cost (full A02P size, read-only on OX-CODE1's saved outputs; receipt OVERHEAD_FULL_A02P_V1.json)

| step | Profile (170 day-parts) | Context (510 day-parts) |
|---|---:|---:|
| selection | 0.13 s | 0.12 s |
| check_stage (incl. rehash of 860 / 1,369 lab indexes) | 0.45 s | 0.69 s |
| commit part digest (run_manifest_candidate, every block hashed) | 26.7 s | 18.8 s |
| the same digest without payload blocks (the blocks stay pinned by sha16 in index.json) | 0.84 s | 0.68 s |

The commit digest is the one large cost; its fix is a patch request to decisions_fixer (hand-back).

## Open review items

- labcore's no-write contract: `runs` re-exports the run-publication writers and moves parts aside on resume (inside a run folder
  the caller names, never a value store). LAB1 architecture review before promotion.
- `run_manifest_candidate.py`, DEV2 `population.py`, `event_selection.py` and `ROSTER_BUILD.json` are pinned by sha16 in
  `RELEASE_labcore_V2_7_CANDIDATE.json`; any change refuses the candidate until it is re-cut (`python3 -B v2_7/release_v27.py <reason>`).

Tests: `labcore/tests/test_v27_candidate.py` (selection S1-S10, runs R1-R3, cache C1-C4, registry), and
`event_profile/test_run_parallel.py` (the dispatcher on small real inputs).
