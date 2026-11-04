# queue_job_v11: tool card

The way a kit agent queues every job since ALARM_V1_12 (COUNT, GRADE, ENTRY, MONTH), from the release folder. The code: [queue_job_v11.py](../Agentic/tree/ALARM_DESIGN/KIT_V5/tools/queue_job_v11.py). Exact commands: [TOOL.json](queue_job_v11.TOOL.json). Every output column: [dictionary](../dictionaries/queue_job_v11_COLUMNS.tsv). Its past editions, never used now: [queue_job_v9](queue_job_v9.md), [queue_job_v8](queue_job_v8.md), [queue_job_v7](queue_job_v7.md), [queue_job_v6](queue_job_v6.md), [queue_job_v5](queue_job_v5.md).

archive/ holds past editions: read only, never run; to rerun one, use the old release install.

`<INSTALL>` is the Alarm release folder: on the owner's Mac <RELEASE_ROOT>/Alarm/alarm/current (a Cowork VM sees it under ~/mnt/volat_release/Alarm/alarm/current). Status in the code: TEST, NOT REVIEWED.

## What it does
- Checks a job against the kit rules, fills a job template with the paths of the machine that runs it, and puts the job in a runner queue: queue_job_v11 with GRADE and MONTH on their V13 templates (D4: one edition of detect, idea_to_grade and the card for GRADE and MONTH; D2: Outcomes write the compact evt1 store, about 8 files a day in place of about 1,355; the outputs are byte for byte the V11 ones), KIND CLEAN refused, and the disk budget counting only scratch still on SCRATCH_DISK.
- COUNT: the Sep-Dec 2025 fire, wave and coin counts of up to 3 definitions (JOB_COUNT_V7, detect_v2).
- GRADE: the grade of 1 to 3 variants on Sep-Dec 2025 (JOB_GRADE_V13, the chain v2_0_7: v2_0_6 with the gm editions (detect_gm1, idea_to_grade_gm1, alarm_card_gm1, event_outcomes_gm2 writing the evt1 store) and d1_reports_v3; perfire and the hand-off read the kept rows; 3 cores; MEM_MB 2879 for 1 variant, 3000 for 2 or 3, each a measured peak + 20 percent); its hand-off decides with decide_v3.
- ENTRY: the entry grade of a variant whose GRADE passed R1 (JOB_ENTRY_V7), `--from-job <its GRADE job>`.
- MONTH: the Jan-Apr 2026 reads of a decided variant (JOB_MONTH_V13, the chain v2_2_7: v2_2_6 with the same gm editions and the evt1 store, perfire from the kept rows; MEM_MB 3813, job 20265289's tree peak 3131 MB + 20 percent), `--from-job <its GRADE job>`.
- GRADE and MONTH give their chain the feed gate (FEED_GATE) and the research days (RESEARCH_STORE) of the machine that runs them. Job 20265337 (BUILD5, the candidate of this release): V12 GRADE and MONTH re-ran the past jobs 20264127 and 20264202 byte for byte, GRADE in 55 s (V11 131 s, job 20265289), MONTH in 134 s (V11 225 s). A killed Outcomes process (the memory guard, a crash) ends the chain at once with exit 6 (test K1).
- KIND CLEAN is refused: `CLEAN REMOVED: the owner 31 Oct 2026 10:51 Berlin; scratch cleanup is DSK's, on the owner's word`. Never delete anything yourself.

## When to use it
- Step 5 COUNT, step 6 GRADE (after the SEAL: your variants' VARIANTS rows), step 8 ENTRY (when decide_v3 asks for it; decide_v3's text still names queue_job_v5: use this tool) and step 10 MONTH (a variant decided PASS or NEEDS MORE MONTHS, or the other side of a STOP with `--forward-only`) of AGENTS.md.
- Always run with `--dry` first; then the same line without it.

## Run it
```
python3 -B <INSTALL>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/queue_job_v11.py --settings <INSTALL>/settings/SETTINGS_LOCAL.env AD1_20261029 COUNT FORCEDBREAK FB5=ideas/FORCEDBREAK/defs/FB5.json --dry
python3 -B <INSTALL>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/queue_job_v11.py --settings <INSTALL>/settings/SETTINGS_LOCAL.env AD1_20261029 GRADE FORCEDBREAK FB5 --dry
python3 -B <INSTALL>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/queue_job_v11.py --settings <INSTALL>/settings/SETTINGS_LOCAL.env AD1_20261029 ENTRY FORCEDBREAK FB5 --from-job 20263757_GRADE_FORCEDBREAK --dry
python3 -B <INSTALL>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/queue_job_v11.py --settings <INSTALL>/settings/SETTINGS_LOCAL.env AD1_20261029 MONTH FORCEDBREAK FB5 --from-job 20263757_GRADE_FORCEDBREAK --dry
```
- RUN: the run tag; its folder is RESEARCH_ROOT/ALARM_DESIGN/runs/RUN; the seat is the part before `_`.
- IDEA: capitals and digits. ITEMS: COUNT `V=ideas/<IDEA>/defs/<V>.json` (up to 3); GRADE 1 to 3 variant names; ENTRY and MONTH one variant; each registered in VARIANTS before its GRADE.
- `--from-job <GRADE job>` (ENTRY, MONTH); `--forward-only` (MONTH: the other side of a STOP variant, decided by [decide_forward_v3](decide_forward_v3.md)).
- `--queue Q_Vn`: a chosen queue (default: the first empty one of Q_V1..Q_V21). `--behind`: wait behind your own job (your 3rd job).
- `--job-settings <file>`: the runner machine's settings file, when you queue for another machine (default: `--settings`).
- After queueing: check every 5 minutes; the job is done when receipts/<N>_<KIND>_<IDEA>/STAGES.tsv has its `end` line.

## What it gives
- Printed with `--dry`: the filled job, then `DRY RUN OK: <RUN> <KIND> <IDEA> <items> on <Q>; WRITES_MB .., MEM_MB ..; nothing claimed or queued`.
- Printed when queued: `QUEUED <Q> <N> <job> twin .. sha16 .. IN .. | RUNS <stamp> RUNS`, then a `NEXT:` line.
- Files when queued: the job twin RUN/jobs/<N>_judge_<SEAT>_<KIND>_<IDEA>.job.sh, one row of RUN/registers/RUNS.tsv, the job in <RUNNER_QUEUES>/<Q>/IN.
- The COUNT job writes RUN/receipts/<N>_COUNT_<IDEA>/: STAGES.tsv, COUNT_<V>.tsv (fires, waves and coins per Sep-Dec month), FIRST20_<V>.tsv, DISK.tsv and SHA16.txt.
- The GRADE job writes RUN/receipts/<N>_GRADE_<IDEA>/: STAGES.tsv (stage, rc, seconds, utc, note), per variant CARD_<V>.txt, SUM_<V>.tsv, STATUS_<V>.tsv, INPUTS_<V>.txt (the code it ran by sha16, the gate file and the research days), MENU_<V>_om.txt, the per-fire test, FIRES.tsv, the hand-off HANDOFF/ for decide_v3, DISK.tsv and SHA16.txt.
- The MONTH job writes RUN/receipts/<N>_MONTH_<IDEA>/: as GRADE, plus MONTH_READ_<V>_<2601..2604>.txt (one read per Jan-Apr month), CONDITIONS_<V>_15m.txt and _1h.txt, DETECT_PARTS_<V>.tsv (the chain's parts), the fire list and the detection's log and memory.
- The ENTRY job writes what [queue_job_v5](queue_job_v5.md) says for it; every column, with its meaning, unit and when it is known: the dictionary.

## Limits and refusals
- exit 0: queued, or the dry run passed.
- exit 2: refused, `REFUSED: <reason>` on stderr, nothing queued:
  - KIND CLEAN (`CLEAN REMOVED: the owner 31 Oct 2026 10:51 Berlin`);
  - no `--settings`, or a key it needs is empty (RESEARCH_STORE one of them, for the job); a bad run tag, kind or name; no run folder; a FEED_GATE that is not a plain path;
  - the idea not claimed; a variant with no VARIANTS row, or already graded (a variant is graded once: a change is a new variant); a MONTH or ENTRY whose GRADE job has no receipts yet;
  - your job budget (2 jobs in IN or RUN, 3 with `--behind`); no empty queue;
  - SCRATCH free under 60,000 MB plus the job's WRITES_MB; the run's scratch still on SCRATCH_DISK over 10,000 MB (a finished job counts only while its folder SCRATCH/work_<RUN>/<JOB> is there, so DSK's sweep frees it: ask DSK on the board);
  - a template or reg_append_v1.py whose sha16 changed; a placeholder left; a refused word; `bash -n` failed; the allocator failed.
- No `--help`: with no arguments it prints `REFUSED: --settings <file> IS REQUIRED` (exit 2).
- Never deletes and never overwrites. Reads no market data. When SCRATCH is not visible from this machine it prints a NOTE and goes on (the job checks the 60 GB floor itself), and the disk budget then counts every finished job's measured scratch.

## Where its data comes from
- RESEARCH_ROOT: the run folder ALARM_DESIGN/runs/<RUN> (registers, ideas, receipts, jobs) and the claims ALARM_DESIGN/runs/IDEAS_CLAIMED.
- FEED_GATE (of --job-settings, the runner machine): the feed's stop gate file; GRADE and MONTH give it to their chain (detect, the grade and Outcomes wait on it), COUNT to detect_v2 as `--gate=`; empty: no gate.
- RESEARCH_STORE (of --job-settings): the research days; GRADE and MONTH give it to their chain, whose Outcomes reads them there.
- RUNNER_QUEUES: the queues Q_V1..Q_V21 (IN and RUN). RUNNER_ALLOC: the runner's job number allocator (job_alloc.py), run where it is.
- SCRATCH: its free space, and whether a finished job's scratch folder SCRATCH/work_<RUN>/<JOB> is still there.
- Filled into the job from `--job-settings` (default `--settings`): PYTHON (the interpreter jobs use), LAB_DAYS (the lab days detect reads), SCRATCH, RESEARCH_ROOT, RESEARCH_STORE. The job's code folder is RUNNER_RELEASE (empty: this Alarm folder).
- Code: only this Alarm folder: the templates (JOB_COUNT_V7, JOB_GRADE_V13, JOB_ENTRY_V7, JOB_MONTH_V13) and reg_append_v1.py, each pinned by sha16.
