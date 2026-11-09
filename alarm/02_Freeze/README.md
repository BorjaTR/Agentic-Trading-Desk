# 02 Freeze: the card and forecasts are locked before any grade

Before any outcome is read, the alarm is frozen: its card (the idea, the exact rule as a definition file, the side, the horizons), each
variant and each forecast are written as rows of the run's registers (VARIANTS, FORECASTS) that name the card, definition and PREREG
files by sha16. A tool appends the rows, takes the time from the clock and never rewrites a row; every variant counts as a try. The job
queue then refuses to grade a variant that is not registered, or whose definition or PREREG changed since ("a sealed file never changes;
a change is a new variant"), and refuses a month check without its sealed Jan-Apr forecasts; the run audit checks both again (A3 SEALED,
A5 FORECASTS). This is what makes a later PASS believable: the rule cannot be fitted to the result. Sources: KIT_V5/PROCESS_V7.md step 4
and section 6 command 2; KIT_V6/skills/alarm-design-v6/SKILL.md rule 2 ("Freeze before you look") and step D; the code named below.

This part has no tool folder of its own, so nothing is copied here: its tools are in [../Agentic](../Agentic), released with this package. What is unproven: the kits say "TEST, NOT REVIEWED" on their first line (KIT_V5 README.md, MANIFEST_SHA16.txt, SKILL.md, PROCESS_V7.md; KIT_V6
README.md, MANIFEST_SHA16.txt, SKILL.md), and reg_append_v1.py says the same in its header. REMOVE.tsv lists the 91 files that were
copied here before; SCOUT deletes them before the commit.

The alarm kit itself (KIT_V5 and KIT_V6: the templates, the run registers, the job queue, the audit; and the register writer it
pins) is kept in one folder, [../Agentic](../Agentic): in use by the alarm agents, TEST, NOT REVIEWED (the owner, 30 Oct 13:5x
Berlin: "everything that is agentic we keep it in one folder at the top level of ALARM"). The kit rows below are there.

## Earlier editions in the dev tree
State on 30 Oct 2026, kept as history; the editions in use now are in ../AGENTS.md. In <RELEASE_ROOT> means released: what follows says what each piece is and what is unproven.
Dev tree: `<LAB_REPO>/forensics/team/RESEARCH/ALARM_DESIGN/`. sha16 on 30 Oct 2026.
| tool | what it does | where (dev tree) | owner | status |
|---|---|---|---|---|
| the register writer | appends one row to VARIANTS, FORECASTS (and THOUGHTS, DECISIONS ...): stamp from the clock, unknown columns, tabs, newlines and em dashes refused, append only | `runs/CLAUDE1_20261028/tools/reg_append_v1.py` (c301c5977ecd6860), tests `test_reg_append_v1.py` | CLAUDE1 run | TEST in TOOLS_BUILT.tsv; header "TEST, NOT REVIEWED" |
| the job queue | queues COUNT, GRADE, ENTRY, MONTH and CLEAN jobs; refuses a variant not in VARIANTS, a definition or PREREG changed since, more than one PREREG a job, a MONTH job without sealed forecasts | `KIT_V5/tools/queue_job_v4.py` (dccce8e5e119fe48) | SCOUT | KIT_V5: TEST, NOT REVIEWED |
| the run audit | 17 checks after every job read; A3 SEALED, A5 FORECASTS | `KIT_V5/tools/audit_run_v2.py` (0593141fa5f9e166) | SCOUT | KIT_V5: TEST, NOT REVIEWED |
| the card templates | idea card, alarm card, PREREG, forecast (KIT_V5); one card per idea, sealed by sha16 in VARIANTS and FORECASTS (KIT_V6) | `KIT_V5/templates/IDEA_CARD_V5.md` (22548c37d2d2c679), `ALARM_CARD_V4.md` (17847a7cc615df2f), `PREREG_V5.md` (16b6224e4eab5551), `FORECAST_V5.md` (6b1fd677bc5d11ae); `KIT_V6/templates/CARD_V6.md` (1df0cab7716611a8) | SCOUT | TEST, NOT REVIEWED |
| the registers | the 8 register files with their headers, copied into each run | `KIT_V5/runs/TEMPLATE_V3/registers/` (VARIANTS d3e98152ed88f391, FORECASTS 208551bd24ae7c68) | SCOUT | KIT_V5: TEST, NOT REVIEWED |
| the alarm card of the CLAUDE1 run | the card PROCESS_V7 step 3 names | `runs/CLAUDE1_20261028/KIT_V4_PROPOSAL/templates/ALARM_CARD_V3.md` (cc7a3e9f97d43858) | CLAUDE1 run | a proposal, no release |
| the tries ledger | one PREREG row before a result is read, one RESULT row after (the lab's other freeze, used by alarm_design's card command) | `team/RESEARCH/tools/ledger/ledger_add_v5.py`, `ledger_add_v6.py` | SCOUT, reviewer QUANT | DRAFT in its BASELINE.tsv (v1, v2 rows only) |
Not this part: freeze_judge (`team/RESEARCH/tools/freeze_judge`, release records up to V2_8) freezes STRATEGY's strategy cards, not
alarm cards; it belongs under Strategy.

## Run from this folder
Nothing to run: no tool is copied. `python3 -B _tools/sync_from_dev_v1.py <dev forensics root> 02_Freeze --check` prints
`rows 0, not same 0` (RUN_PROOF.md).

## Data and settings (state on 30 Oct 2026)
- Keys: `RESEARCH_ROOT` (the runs and their registers: ALARM_DESIGN/runs/<RUN>/registers), `RUNNER_QUEUES` (the job queue), `SCRATCH`
  (job work folders on SCRATCH_DISK), `PYTHON`.
- Built into the TEST editions today (the earlier copies' scan, 90 rows): every KIT_V5 job template sets the dev forensics root and the
  analyst interpreter on line 8 and the run folder `$R/ALARM_DESIGN/runs/<RUN>` below it, and names <SCRATCH_DISK>; queue_job_v4.py and
  audit_run_v2.py (line 31) name the dev tree; the test sandbox `KIT_V5/tests/sim_env.py:5` names SCOUT's VM folder
  `<VM_UPLOADS>/uploads/dev/_scratch_scout/kit5_test`. A released edition must read these from the settings file.
