# 09 Decision: a PASS goes to STRATEGY with its package

After the grade and the hand-off test, each alarm variant gets one label from its receipts: PASS (the hand-off R2), NEEDS MORE MONTHS (R1
only), STOP (R1 missed), INSUFFICIENT (fewer than 3 counted months) or INVALID (a stage failed or a file is missing); STRATEGY's price
path (CLEAR) is reported beside it and never changes it. A PASS goes to STRATEGY with its package: the frozen card and definition sha16,
the fire list and its sha16, the sealed forecasts and the try count, the grade cards by month, the hand-off result, and STRATEGY's own
first steps already run on it (S0, their grader on the fire list; S2, the markout). Sources: KIT_V5/PROCESS_V7.md sections 2, 3 and 6;
KIT_V5/README.md "The decision" (the owner, 29 Oct 14:23 Berlin: "for now we keep them separate and report both").

Only released editions are here (the owner, 30 Oct 2026, option a). The tools that make this step's label and package are in [../Agentic](../Agentic) (the decide tool: ../AGENTS.md step 7). What is unproven: the alarm kit KIT_V5 says "TEST, NOT REVIEWED. PROPOSED for the owner." in its README, MANIFEST_SHA16.txt and PROCESS_V7.md, and the
CLAUDE1 run tools are TEST in their TOOLS_BUILT.tsv. Their earlier editions: below.
The alarm kit is kept in one folder: [../Agentic](../Agentic) (KIT_V5's decide_v1.py, decide_forward_v1.py, audit_run_v2.py
and templates, and the CLAUDE1 run tools the kit pins: reg_append_v1.py, lead_null_v1_to20251231.py, read_stratentry_v1.py,
run_alarm_store_v10_3_noladder.sh); the owner, 30 Oct 13:5x Berlin: "everything that is agentic we keep it in one folder".

Released and copied here: DECIDE_V1, a different tool with a similar name. It decides per fire, for any alarm, TAKE or SKIP from frozen
library cards and a rulebook; the grader then grades those decisions. That is the money stage's question ("which fires to take, exits,
size is the strategy stage's job", PROCESS_V7 section 1), not the alarm's PASS or STOP label.

## Layout
- [decide_v1/](decide_v1): README.md and SCOPE.md are byte copies of the tool's README_DECIDE_V1.md and SCOPE_DECIDE_V1.md;
  ARCHITECTURE.md and CHANGELOG.md say on their first line that SCOUT wrote them for the repo.
- `tree/team/RESEARCH/tools/decide_v1/`: the 41 files of release DECIDE_V1_0_1 and its two release records, byte copies in the dev layout.
- `MANIFEST.tsv`, `SOURCES.tsv`, `MACHINE_PATHS.tsv`, `RUN_PROOF.md`, `CHANGELOG.md`, `REMOVE.tsv` (files SCOUT deletes before the commit).

## Tools
| tool | what it does | owner | edition here | status |
|---|---|---|---|---|
| [decide_v1](decide_v1) (`tree/team/RESEARCH/tools/decide_v1/`) | per fire: TAKE or SKIP with a reason, side, entry and exit names, from the context, profile and pre-move cards and the alarm's rulebook; writes TAKE and SKIP event lists for the grader (idea_to_grade V3.1); never reads a price | DECIDE | release DECIDE_V1_0_1 (26 Oct 07:23Z), decide_v1.py d8cd9acfd7b126d5 | released: the candidate reviewed READY by an independent reviewer, builder signed; V1_0_1 changes documents and the M rulebook only |
What changed in each release: [CHANGELOG.md](CHANGELOG.md).

## Earlier editions in the dev tree
State on 30 Oct 2026, kept as history; the editions in use now are in ../AGENTS.md. In <RELEASE_ROOT> means released: what follows says what each piece is and what is unproven.
Dev tree: `<LAB_REPO>/forensics/team/RESEARCH/ALARM_DESIGN/`. sha16 on 30 Oct 2026.
| tool | what it does | where (dev tree) | status |
|---|---|---|---|
| the variant decision | the label from the receipts (PASS, NEEDS MORE MONTHS, STOP, INSUFFICIENT, INVALID; NO ENTRY with --entry-too-big) | `KIT_V5/tools/decide_v1.py` (8c345946c673530a) | KIT_V5: TEST, NOT REVIEWED |
| the forward-only decision | FORWARD PASS = HELD or STRONGER in 3 of the 4 Jan-Apr months | `KIT_V5/tools/decide_forward_v1.py` (b6c153cf4b304bf9) | KIT_V5: TEST, NOT REVIEWED |
| the audit | 17 checks; A6 recomputes every decision from the receipts | `KIT_V5/tools/audit_run_v2.py` (0593141fa5f9e166) | KIT_V5: TEST, NOT REVIEWED |
| the DECISIONS row and the FOR STRATEGY line | appends one register row, stamped by the clock | `runs/CLAUDE1_20261028/tools/reg_append_v1.py` (c301c5977ecd6860); register header `KIT_V5/runs/TEMPLATE_V3/registers/DECISIONS.tsv` | TEST (TOOLS_BUILT.tsv) |
| the hand-off test | R1 and R2: the LEAD per wave, t of at least 3 | `runs/CLAUDE1_20261028/tools/lead_null_v1_to20251231.py` (22b58c1c72aab4f2) | TEST (TOOLS_BUILT.tsv; PROCESS_V7 section 4 shows it on made-up alarms) |
| the package's price path | STRATEGY's grader store (S0, no exit ladder) and markout (S2) as one runner job, and its reader | `runs/CLAUDE1_20261028/tools/file_entry_job_v2.py` (12f508e3fc6e447f), `run_alarm_store_v10_3_noladder.sh` (45ac17404e5dc762), `read_stratentry_v1.py` (efe30de7fdfd2c59) | TEST, NOT REVIEWED |
| the write-ups | FINDINGS per idea, REPORT per run | `KIT_V5/templates/FINDINGS_V5.md` (ac4bfd7a1c3deaba), `REPORT_V5.md` (e4386b13af4726af) | KIT_V5: TEST, NOT REVIEWED |
| the process | step 8 (decision), section 3 (the package), section 6 (commands) | `KIT_V5/PROCESS_V7.md` (0b368cabce30bbe5); KIT_V6/PROCESS_V8.md step 6 | PROPOSED, TEST, NOT REVIEWED |
Not this part: the novelty check of a new PASS against the registry (part 08).

## Run from this folder (Alarm/09_Decision)
The tests need no tool data. One test reads every coin and alarm name from the library registry and the frozen universe, which are data
(not copied): copy them from RESEARCH_ROOT into a new folder first.
```
S=../settings/SETTINGS_<MACHINE>.env; RR=$(python3 -B ../_tools/settings_v1.py get $S RESEARCH_ROOT)
F=$(mktemp -d); mkdir -p $F/team/RESEARCH/LIBRARY/alarm_library
cp $RR/LIBRARY/UNIVERSE_ALARMS_V1.tsv $F/team/RESEARCH/LIBRARY/; cp $RR/LIBRARY/alarm_library/ALARM_REGISTRY_V1.tsv $F/team/RESEARCH/LIBRARY/alarm_library/
T=tree/team/RESEARCH/tools/decide_v1
DECIDE_FORENSICS=$F python3 -B ../_tools/run_isolated_v1.py $T/tests_decide_v1.py                     # 25/25 passed
python3 -B ../_tools/run_isolated_v1.py $T/edges_decide_v1.py                                           # 33 cases, 0 failed
python3 -B ../_tools/run_isolated_v1.py $T/loop_v1/test_decide_loop_read_v1.py $(mktemp -d)/loop       # 13 tests, 0 failed
DECIDE_FORENSICS=$F python3 -B ../_tools/run_isolated_v1.py $T/mutants_decide_v1.py                    # 51/51 mutants killed
```
Proof that they run from here and from a copy of the Alarm folder elsewhere: [RUN_PROOF.md](RUN_PROOF.md).

A real run (the six frozen alarms, Sep 10 - Dec 31 2025; about 5 s):
`bash tree/team/RESEARCH/tools/decide_v1/run_decide_all_v1.sh <forensics root> <profile cards root> <new out folder> [where /Volumes is mounted]`.
It reads its inputs under `<forensics root>`: the universe and the library cards (data), the library release records, and the code of
the lab tool its rulebooks name (idea_to_grade V3.1, LAB_TOOLS_V1.json), which is not copied here (part 07 holds V3.2). So today a real
run needs the forensics root of the machine (RESEARCH_ROOT/../..), not this folder. The outcome loop (loop_v1) grades through idea_to_grade
V3.1 and is not run from here.

## Data and settings
Settings keys (`../settings/SETTINGS_<MACHINE>.env`): the tests need `RESEARCH_ROOT` (LIBRARY/UNIVERSE_ALARMS_V1.tsv and
LIBRARY/alarm_library/ALARM_REGISTRY_V1.tsv); a real run needs `PYTHON`, `RESEARCH_ROOT` (its `../..` is `--root`) and `SCRATCH` (the
profile cards cards_v5_1 and the receipts ADMITTED_INPUTS_V1.json names on <SCRATCH_DISK>; `--volumes-root` maps them).
Still built into the code (`MACHINE_PATHS.tsv`, status BUILT_IN): only the outcome loop's scripts, `loop_v1/run_decide_loop_v1.sh` and
`run_decide_loop_v1_1.sh` (lines 9-29: the interpreter, the dev tree, the ledger tool, the universe and scratch folders). The decision
command itself takes every path as an argument.
Nothing from May 2026 onward is read: the runs and tests cover Sep 10 - Dec 31 2025.
