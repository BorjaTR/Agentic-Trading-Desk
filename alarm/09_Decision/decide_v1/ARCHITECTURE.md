Written by SCOUT for the repo on 30 Oct 2026 from tree/team/RESEARCH/tools/decide_v1/decide_v1.py (docstring and arguments), decide_rules_v1.py, run_decide_all_v1.sh, README_DECIDE_V1.md, SCOPE_DECIDE_V1.md (section Architecture) and RELEASE_DECIDE_V1_0_1.json; not the owner's document (owner seat: DECIDE).

# ARCHITECTURE: DECIDE_V1, the per-fire decision (release DECIDE_V1_0_1)

## Inputs (all named on the command line; nothing is built into the code)
| input | format | from |
|---|---|---|
| the fires | the frozen universe TSV (alarm_id, coin, t, side, parent_id, cluster_id, weight ...); its header names each alarm's source event list with its sha16 | `--universe`, e.g. RESEARCH_ROOT/LIBRARY/UNIVERSE_ALARMS_V1.tsv |
| context cards (`ctx.` fields) | TSV, one row per fire key, field status columns `<field>__status` | `--ctx-cards` (LIBRARY/context_split, release V4.1) |
| profile cards (`prof.`) | TSV, three files | `--prof-cards` (on the scratch disk, cards_v5_1; release V5.1) |
| pre-move cards (`pmm.`) | TSV | `--pmm-cards` (LIBRARY/cause_lib, release V1.2) |
| the rulebook | JSON: side, at most 3 skip lines (each with its field's states and reasons, status CANDIDATE, FROZEN or FAILED), size, entry, exit | `--rulebook` (rulebooks/) |
| SAFETY_V1.json, LAB_TOOLS_V1.json, ADMITTED_INPUTS_V1.json | JSON: off days and states (empty), the entry and exit names a rulebook may use, which signed release admits each input | `--safety`, `--lab-tools`, `--admitted` |
| the forensics root | a folder: the release records and lab tool code named in the JSON files are read under it | `--root`; `--volumes-root` maps the Mac's /Volumes paths |

## Steps
1. `admit()` (one function for every input): each file at a sha16 its library's release names; each used field's status admitted;
   every pinned evidence file and lab tool release (and its code) at its sha16. Any failure: `REFUSED <CODE>: why`, exit 2, no output.
2. `decide_rules_v1.decide()` per fire, the slots in order, the first that decides wins: data gate (a declared reason gives SKIP
   BAD_DATA), regime gate (SAFETY: SKIP OFF_STATE), side (FADE, FOLLOW or UNSET), skip lines (the first true one: SKIP SKIP_RULE; none:
   TAKE).
3. Write the run folder whole: DECISIONS.tsv, TAKE_EVENTS.tsv, SKIP_EVENTS.tsv, VALUE_COUNTS.tsv, then RUN.json last.
4. `--verify <run folder>` / `verify_run()`: a consumer refuses RUN_NOT_COMMITTED or RUN_CHANGED_AFTER_COMMIT.

## Outputs (a new folder per run; fixed headers; per-fire files start alarm_id, coin, t, side)
DECISIONS.tsv (one row per fire: action, slot, reason, trade side, entry, exit, size, used values), TAKE_EVENTS.tsv and SKIP_EVENTS.tsv
(the grader's event format: idea_to_grade V3.1 `--events ... --events-subset`), VALUE_COUNTS.tsv, RUN.json (every input sha16, the
code, the admitting releases, the tally, the phase times).

## Files (tree/team/RESEARCH/tools/decide_v1/)
| file | what |
|---|---|
| decide_v1.py, decide_rules_v1.py | the command and the pure rules |
| rulebooks/RULES_DEFAULT_V1.json, RULES_ALM_M_V1.json, RULES_ALM_S3W_V1.json | take-all baseline; M (S1 FAILED, never decides); S3W |
| SAFETY_V1.json, LAB_TOOLS_V1.json, ADMITTED_INPUTS_V1.json, SETTINGS_DECIDE_V1.tsv | the safety placeholders, the lab tool names, the admissions, the settings |
| tests_decide_v1.py, mutants_decide_v1.py, edges_decide_v1.py + EDGES_DECIDE_V1.tsv, meaning_decide_v1.py | 25 tests, 51 planted bugs, 33 edge cases, the meaning checker (recomputes every row without importing the tool) |
| run_decide_all_v1.sh | the real run: six alarms with the default rulebook, M and S3W with their own |
| loop_v1/ | the outcome loop for M: PREREG V1, V1.1 and its addendum, settings, group split, the reader and its test, run scripts |
| receipts_kit_v1/ | the release's evidence: tests, mutants, edges, old vs new probes |
| CARD, KIT, SCOPE, README, FINAL_NOTE, SPEED_BUDGET, LAB_TOOLS_INVENTORY (.md); RELEASE_DECIDE_V1_0_1.json, RELEASE_DECIDE_V1_CANDIDATE.json | documents and the two release records |

## Settings keys a real run needs
`PYTHON` (stdlib only); `RESEARCH_ROOT` (the universe and the context and pre-move cards under LIBRARY; `--root` is its `../..`);
`SCRATCH` (the profile cards, cards_v5_1, and the receipts ADMITTED_INPUTS_V1.json names on <SCRATCH_DISK>). `--root` must hold the
lab tool release named in LAB_TOOLS_V1.json (idea_to_grade V3.1) and its code, because every entry and exit id is checked in that code.
The outcome loop (loop_v1/run_decide_loop_v1*.sh) has the dev tree, the interpreter and scratch folders built in (MACHINE_PATHS.tsv).

## Tests
tests_decide_v1.py (25; the no-names test reads the library registry and the frozen universe: DECIDE_FORENSICS), edges_decide_v1.py
(33), loop_v1/test_decide_loop_read_v1.py (13, planted run folders), mutants_decide_v1.py (51). RUN_PROOF.md of the part shows them run
from the repo and from a copy.
