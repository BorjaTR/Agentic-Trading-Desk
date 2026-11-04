# queue_job_v5: tool card

> PAST EDITION. Since ALARM_V1_7 every job goes through [queue_job_v7](queue_job_v7.md). CLEAN is removed (the owner 31 Oct 2026 10:51 Berlin: scratch cleanup is DSK's); since ALARM_V1_8 its template and clean_scratch_v2.py are in archive/, so this queue answers NO TEMPLATE to CLEAN. The CLEAN lines below are history.

The one way a kit agent queues a job, from the release folder. The code: [queue_job_v5.py](../Agentic/tree/ALARM_DESIGN/KIT_V5/tools/queue_job_v5.py). Exact commands: [TOOL.json](queue_job_v5.TOOL.json). Every output column: [dictionary](../dictionaries/queue_job_v5_COLUMNS.tsv). Settings keys: [settings/README.md](../settings/README.md). The job templates: [JOB_COUNT_V6](../Agentic/tree/ALARM_DESIGN/KIT_V5/jobs/JOB_COUNT_V6.job.sh.txt), JOB_CLEAN_V6 (in jobs/archive/ since ALARM_V1_8).

archive/ holds past editions: read only, never run; to rerun one, use the old release install.

`<INSTALL>` is the Alarm release folder: on the owner's Mac <RELEASE_ROOT>/Alarm/alarm/current (a Cowork VM sees it under ~/mnt/volat_release/Alarm/alarm/current). Status in the code: TEST, NOT REVIEWED.

## What it does
- Checks a job against the kit rules, fills a job template with the paths of the machine that runs it, and puts the job in a runner queue.
- Five kinds (31 Oct):
  - COUNT: fires, waves and coins per Sep-Dec 2025 month for up to 3 definitions, by detection only (no outcome is read). It runs
    detect_v2 with the runner machine's feed gate (FEED_GATE; empty: no gate).
  - GRADE: the grade of 1 to 3 variants on Sep-Dec 2025 (JOB_GRADE_V7, the chain v2_0_2; the past edition since ALARM_V1_6, where [queue_job_v6](queue_job_v6.md) queues JOB_GRADE_V8); its hand-off decides with decide_v2.
  - MONTH: the Jan-Apr 2026 reads of a decided variant (JOB_MONTH_V7, the chain v2_2_2; the past edition since ALARM_V1_6, where [queue_job_v6](queue_job_v6.md) queues JOB_MONTH_V8), `--from-job <its GRADE job>`.
  - CLEAN: removes the run's own scratch of finished, decided jobs; their proof (receipts) stays on dev.
  - ENTRY: the entry of a variant whose GRADE passed R1 (decide_v2 asks for it), `--from-job <its GRADE job>` (JOB_ENTRY_V6, the store
    runner v11, the grader V3.2 S6 rel1, markout_v1_2; since ALARM_V1_2); then decide again with `decide_v2 --entry <ENTRY job>`.
- On the Mac, GRADE and MONTH still run some code of other seats from the dev tree (the grader, labcore, Outcomes): their new editions
  come in a later release.

## When to use it
- Step 4 COUNT of the loop (ALARM_PIPELINE_V1 section 1), after the idea is claimed and its definitions are written. It answers: how often does my definition fire, per month, in waves (a fire more than 1800 s after the previous one starts a new wave)?
- CLEAN, after a job is decided (GRADE, ENTRY: a DECISIONS row) or read (COUNT, MONTH: a POSTMORTEMS row). It does not count in your job budget.
- Always run with `--dry` first; then the same line without it.

## Run it
```
python3 -B <INSTALL>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/queue_job_v5.py --settings <INSTALL>/settings/SETTINGS_LOCAL.env AD1_20261029 COUNT FORCEDBREAK FB5=ideas/FORCEDBREAK/defs/FB5.json --dry
python3 -B <INSTALL>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/queue_job_v5.py --settings <INSTALL>/settings/SETTINGS_LOCAL.env AD1_20261029 CLEAN GIVENS 20263694_COUNT_GIVENA,20263695_COUNT_GIVENB --dry
```
- These are the shapes of AD1's real COUNT and CLEAN jobs of 29 Oct (jobs 20263746 and 20263724).
- RUN: the run tag; its folder is RESEARCH_ROOT/ALARM_DESIGN/runs/RUN; the seat is the part before `_`.
- IDEA: capitals and digits. For CLEAN it is only a label in the job name.
- ITEMS: COUNT `V=ideas/<IDEA>/defs/<V>.json`, up to 3, comma separated; CLEAN the receipts names of your jobs, up to 12.
- `--queue Q_Vn`: a chosen queue (default: the first empty one of Q_V1..Q_V21). `--behind`: wait behind your own job (your 3rd job).
- `--job-settings <file>`: the runner machine's settings file, when you queue for another machine (default: `--settings`).
- GRADE, ENTRY and MONTH take `ITEMS` = 1 to 3 variant names, `--from-job <GRADE job>` (ENTRY, MONTH) and `--forward-only` (MONTH: the other side of a STOP variant, decided by [decide_forward_v2](decide_forward_v2.md)).
- After queueing: check every 5 minutes; the job is done when receipts/<N>_<KIND>_<IDEA>/STAGES.tsv has its `end` line.

## What it gives
- Printed with `--dry`: the filled job, then `DRY RUN OK: <RUN> <KIND> <IDEA> <items> on <Q>; WRITES_MB .., MEM_MB ..; nothing claimed or queued`.
- Printed when queued: `QUEUED <Q> <N> <job> twin .. sha16 .. IN .. | RUNS <stamp> RUNS`, then a `NEXT:` line.
- Files when queued: the job twin RUN/jobs/<N>_judge_<SEAT>_<KIND>_<IDEA>.job.sh, one row of RUN/registers/RUNS.tsv, the job in <RUNNER_QUEUES>/<Q>/IN.
- The COUNT job writes RUN/receipts/<N>_COUNT_<IDEA>/:
  - STAGES.tsv: one line per stage (stage, rc, seconds, utc, note).
  - COUNT_<V>.tsv: per month 2509-2512 then ALL: fires, waves, coins, max fires in one wave, fires on BTC; its last line says how many months have 30 or more waves.
  - FIRST20_<V>.tsv: the header and first 20 fires, every column detect.py writes (coin and t first).
  - DISK.tsv (its scratch MB, SCRATCH free MB at the end), SHA16.txt, the tail of each detection log.
- The CLEAN job writes RUN/receipts/<N>_CLEAN_<IDEA>/: STAGES.tsv, DRY.txt, APPLY.txt, CLEANED.tsv (one row a path: REMOVED, or LEFT FOR DSK for a protected store place), SHA16.txt; and CLEANED_BY.txt in each cleaned job's receipts.
- Every column, with its meaning, unit and when it is known: the dictionary.

## Limits and refusals
- exit 0: queued, or the dry run passed.
- exit 2: refused, `REFUSED: <reason>` on stderr, nothing queued:
  - no `--settings`, or a key it needs is empty; a bad run tag, kind or name; no run folder; a FEED_GATE that is not a plain path;
  - the idea not claimed (no runs/IDEAS_CLAIMED/<RUN>_<IDEA>.txt); a definition outside ideas/<IDEA>/, missing, or whose window misses 20250910 to 20260430; more than 3 definitions;
  - your job budget (2 jobs in IN or RUN, 3 with `--behind`); no empty queue;
  - SCRATCH free under 60,000 MB plus the job's WRITES_MB; the run's uncleaned scratch over 10,000 MB (CLEAN your decided jobs first);
  - a template or reg_append_v1.py whose sha16 changed; a placeholder left; a refused word; `bash -n` failed; the allocator failed;
  - CLEAN only: a job not yours, still queued or running, already cleaned, still read by a queued job, not decided, or with no POSTMORTEMS row.
- No `--help`: with no arguments it prints `REFUSED: --settings <file> IS REQUIRED` (exit 2).
- Never deletes and never overwrites. Reads no market data. When SCRATCH is not visible from this machine it prints a NOTE and goes on (the job checks the 60 GB floor itself).

## Where its data comes from
- RESEARCH_ROOT: the run folder ALARM_DESIGN/runs/<RUN> (registers, ideas, receipts, jobs) and the claims ALARM_DESIGN/runs/IDEAS_CLAIMED.
- FEED_GATE (of --job-settings, the runner machine): the feed's stop gate file, filled into the COUNT job as detect_v2 `--gate=`; empty: no gate.
- RUNNER_QUEUES: the queues Q_V1..Q_V21 (IN and RUN). RUNNER_ALLOC: the runner's job number allocator (job_alloc.py), run where it is.
- SCRATCH: its free space; each job's scratch is SCRATCH/work_<RUN>/<JOB>.
- Filled into the job from `--job-settings` (default `--settings`): PYTHON (the interpreter jobs use), LAB_DAYS (the lab days detect reads), SCRATCH, RESEARCH_ROOT. The job's code folder is RUNNER_RELEASE (empty: this Alarm folder).
- Code: only this Alarm folder: the V6 templates and reg_append_v1.py, each pinned by sha16.
