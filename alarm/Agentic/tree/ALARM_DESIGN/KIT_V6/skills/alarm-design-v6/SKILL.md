---
name: alarm-design-v6
description: Find a NEW trading alarm for the owner's volat-agent team with ALARM_DESIGN KIT_V6 (PROCESS_V8) - one card, the KIT_V5 jobs, a decision by decide_v1.py, a copy check against the alarm registry, then stop.
---

# Alarm design V6 (KIT_V6, PROCESS_V8; round 6 edition, 30 Oct 2026). TEST, NOT REVIEWED.

## 0. The goal, and when you stop
Find ONE new alarm that passes, then stop. New = PASS by decide_v1.py (hand-off R2) AND novelty_v1.py says NEW or NEW SIDE. Then:
FINDINGS, REPORT (with your minutes per step), audit, board DONE. If no new PASS by the DONE time in your prompt, the same wrap-up.
Time is measured: round 1 agents reached their first PASS after 58 to 86 minutes and then wasted hours (V6-01); in round 2 GPT2 found
a new PASS in 52 minutes, and a hand-off with R2 PASS sat unread 32 minutes after launch (V6-24).
**The clock (from round 3; V6-25).** Your prompt gives six times: two ideas claimed (launch +10 min), first COUNT queued (+15), both
ideas counted and one graded or grading (+30), target: a new PASS (+45 from round 4; +60 in round 3), nothing new queued (+70),
DONE (+75). A missed time: a board
NOTE with the reason (your REPORT's time table uses it). The round ends at its DONE time for everyone.
An alarm = a moment named from data known at that moment + a side (FADE or FOLLOW). Good = its side wins the race (+2c before -1c) more
often than at 3 matched random moments AND more than the other side (the LEAD, at 15 m and 1 h), in most months. Direction is enough.

Names: F = <LAB_REPO>/forensics, R = F/team/RESEARCH, H = R/ALARM_DESIGN, K5 = H/KIT_V5 (the job
tools and templates, unchanged and proven), K6 = H/KIT_V6 (this kit's docs), G = H/REGISTRY, T = H/runs/CLAUDE1_20261028/tools,
RUN = H/runs/<RUN> (seat = the part before _). On the Cowork VM <DEV> is $HOME/mnt/dev. Board: F/hb/<SEAT>.txt.
Set up once: cp -R -n K5/runs/TEMPLATE_V3 RUN.

## 1. Read first (about 5 minutes, no more; V6-31)
This file; K6/IDEA_GUIDE_V4.md (what passed, what held on Jan-Apr, what failed and why, and six questions before you claim); G/SCOREBOARD.md; the rows of
G/ALARM_REGISTRY_V1.tsv near your two ideas and their pages in G/alarms/; K5/IDEA_TO_ALARM_V4.md (the six quick checks);
K5/METRIC_FAMILIES_V1.md (your rows); the V6- rows of K6/LEARNINGS_V6.tsv (the V5 rows are built into the tools). Open
K5/QUICK_CHECK_EXAMPLES_V2.md only when a check is unclear. Never read H/REVIEW/, another run's folder or anything on SCRATCH_DISK except the log of a failed step of your own job (rule 7).

## 2. Seven rules that never bend
1. **Source every number** from a tool file named next to it with its sha16. Decisions only by decide_v1.py. Unsure: UNKNOWN.
2. **Freeze before you look.** Rule, side and forecast sealed in the card (its sha16 in VARIANTS) before any job reads an outcome.
3. **Budgets** (queue_job_v4.py enforces them): 3 graded variants per idea; 2 of your jobs at once (a 3rd behind your own with
   --behind); 10,000 MB of your own uncleaned scratch (CLEAN as soon as a job is decided). A variant whose job failed runs again under its
   name, no extra try.
4. **Months.** Count, grade and hand-off read 10 Sep-31 Dec 2025. Jan-Apr 2026 only through the MONTH job. May 2026 on: never.
5. **Stuck.** The same failure twice, or a rule you can read two ways: PROBLEMS row, board STUCK, next idea. Never raise a cap.
6. **Only the kit's tools**, by sha16; never edit K5, K6, G, another run's files or any shared tool (a shared tool may sit inside a
   signed release: one edit stopped every agent's grading for 25 minutes on 29 Oct, V6-23).
7. **House rules.** Twin before edit (cp -n f f.pre_<RUN>_<stamp>); never delete by hand (CLEAN jobs only); no find, grep -r or du
   from the VM; SCRATCH_DISK: write only inside jobs, read only the .log of a FAILED step of your own job (the owner 29 Oct 23:30 Berlin); jobs can be queued at any hour (the quiet window was removed by the owner 30 Oct 2026 23:32 Berlin: "All jobs can be queued. Please do not stop queueing jobs"); stamps from the clock; no em dashes; names in capitals and
   digits; a VM shell call is cut at about 60 s: never wait more than 50 s in one call (V6-08).

## 3. The path of one idea
| # | Do | Writes |
|---|---|---|
| A | Pick TWO ideas, one in each family your prompt names, not in the registry; run the six questions of K6/IDEA_GUIDE_V4.md section 5 on each; read the pages of each one's 3 nearest alarms. Claim both: cp -n of a one-line text to H/runs/IDEAS_CLAIMED/<RUN>_<IDEA>.txt. Board CLAIM for each (V6-26) | 2 claim files |
| B | COUNT first (V6-48): the definition from H/KIT_V2/templates/DEF_TEMPLATE_V2.json (window 20250901 to 20260531), the helper on one coin-day for its memory (section 6; V6-06), then the COUNT job at once (a COUNT reads no outcome). While it runs, one card per idea: K6/templates/CARD_V6.md (idea with its family and what is new, six quick checks, inputs, rule, hand check plus one raw row, variants, forecasts, what proves it wrong); only SUPPORT waits for the COUNT | defs/<V>.json, ideas/<IDEA>/CARD_<IDEA>.md |
| C | The COUNT jobs (up to 3 definitions an idea; your 2 jobs at once). Fill SUPPORT; under 30 waves in 2 or more months: SUPPORT FAIL (not a NO), next idea. Over about 20,000 fires: grade it only if the card says why (grades take 4 min at 3,000 fires and 25 min or more at 55,000; V6-37) | receipts/<JOB>/COUNT_<V>.tsv |
| D | Seal BOTH ideas as soon as their COUNTs are back, then queue BOTH GRADEs before you read either (V6-48; round 4 lost 6 to 23 min an idea sealing one idea at a time; round 5 AD15 had both graded 14 min after START): one VARIANTS row per variant (prereg_rel = the card), board PREREG, your best variant ALONE in its own GRADE job (about 5 min; a job grades its variants one after the other: V6-33); a 2nd or 3rd variant only after you read the first | the VARIANTS rows |
| E | Read the hand-off (receipts/<JOB>/HANDOFF/REAL_SEALED/). R1 missed: decide (STOP) now. R1 passed: link the card the store registers (`cd RUN/ideas/<IDEA> && ln -s CARD_<IDEA>.md ALARM_CARD.md`, the card holding that variant; V6-32), ENTRY job, then decide: `python3 -B K5/tools/decide_v1.py RUN IDEA V --grade <JOB> [--entry <JOB>] --write` | DECISIONS row |
| F | PASS: CLEAN the GRADE job (it keeps the fire list on dev; CLEAN needs every variant of the job decided, so one variant per job is fastest: V6-39), then `python3 -B G/tools/novelty_v1.py RUN/receipts/<GRADE JOB>/<V>_FIRES_V1_LIST.tsv --lean <FADE or FOLLOW>`. NEW or NEW SIDE: your goal is met; COPY, MIRROR or NEAR: it does not count, next idea. A STOP whose OTHER side won is not a new alarm: that side was read, so a variant of it graded on Sep-Dec is a retry, not a test (V6-35); write `NEXT IDEA: FORWARD ONLY <V0> <side>`: SCOUT seals and tests it on Jan-Apr only (V6-43) | NOVELTY line in FINDINGS |
| G | New PASS: forecasts Jan-Apr (card section 8 or K5/templates/FORECAST_V5.md) and 4 FORECASTS rows, then the MONTH job at once (it regrades Sep-Apr: 15 to 30 min); read it into a Forward months table in FINDINGS. Jan-Apr is the real test: of 10 new alarms read, the side beat random in 39 of 40 months but only 4 held the 5-point bar in 3 or more months (V6-47). An idea claimed after reading another result needs this read before you call it new (V6-45) | MONTH receipts |
| H | Every decided or dropped idea: one POSTMORTEMS row and K5/templates/FINDINGS_V5.md (a STOP too: a no is a result) with two lines: `WHY FAILED: <the mechanism, with the number that shows it>` (a PASS: `WHY IT PASSED: ...`) and `NEXT IDEA: <what to try instead, or next in this family>`; the same text in the POSTMORTEMS why column (V6-27). CLEAN every decided job | FINDINGS_<IDEA>.md |
| I | Wrap-up: RUN/REPORT.md (K6/templates/REPORT_V6.md, with minutes per step), audit --write, board DONE | REPORT.md |
Keep two ideas moving: while one idea's job runs, work on the other; after a STOP, claim the next idea at once so two stay moving.
Decision: PASS = hand-off R2; NEEDS MORE MONTHS = R1 only; STOP = R1 missed; INSUFFICIENT = under 3 counted months; INVALID = a stage
failed. CLEAR is reported beside the label and never changes it.
Example of the two lines (AD1 GB1, round 1): `WHY FAILED: both sides beat random after a thin-book move (FADE +3.9, FOLLOW +2.9 at
15m): a volatility marker, no direction.` `NEXT IDEA: keep the thin-book moment only where a forced trader is leaving (e.g. open
interest falling), so one side must lose.`

## 4. Jobs
- Only `python3 -B K5/tools/queue_job_v4.py <RUN> <KIND> <IDEA> <ITEMS> [--from-job <JOB>] [--behind] [--dry]` (--dry first).
  COUNT: ITEMS `V1=ideas/<IDEA>/defs/V1.json[,...]`. GRADE: `V1[,V2,V3]`. ENTRY and MONTH: `V1` with `--from-job <GRADE JOB>`.
  CLEAN: ITEMS = job names (a failed job too). Never write a job by hand.
- Check every 1 to 2 minutes with short calls (ls the queue's RUN and IN, then RUN/receipts/<JOB>/STAGES.tsv); read a finished job
  before anything else (V6-10). A job is done at its `end` line; read it only when every stage has rc 0; else FAILED: PROBLEMS row,
  read that step's log yourself: `tail -20 $HOME/mnt/SCRATCH_DISK/judge_scratch/work_<RUN>/<JOB>/<step log>` (the failed step's log only;
  V6-50); a refusal like WORKER_RSS_CAP means memory: ASK SCOUT before running it again.
- At every check also read the END of hb/SCOUT.txt (every line, not only FOR <SEAT>; V6-09) and hb/DSK.txt.

## 5. Registers, board, audit
- RUN/registers (append-only, `python3 -B T/reg_append_v1.py RUN <REGISTER> -` with a JSON row): VARIANTS, FORECASTS, POSTMORTEMS,
  LEARNINGS_PROPOSED, PROBLEMS, TOOLS_BUILT by you; RUNS and DECISIONS by the tools.
- Board only with `python3 -B K5/tools/board_line_v1.py <RUN> <KIND> "<what, with files and sha16>"` (START CLAIM COUNT PREREG JOB
  DECISION STUCK ASK ANSWER CHECKPOINT DONE NOTE). CHECKPOINT at the times in your prompt.
- Audit `python3 -B K5/tools/audit_run_v2.py <RUN> --write` at each CHECKPOINT and before DONE only (V6-18).

## 6. Tools and setup
| tool | what |
|---|---|
| K5/tools/queue_job_v4.py | the only way to queue a job |
| K5/tools/decide_v1.py | the decision from the receipts; writes DECISIONS |
| K5/tools/board_line_v1.py, K5/tools/audit_run_v2.py | board line; the scorecard |
| G/tools/novelty_v1.py | the copy check of a fire list against every alarm in the registry |
| T/reg_append_v1.py (c301c5977ecd6860) | append one register row |
| T/hc_defs_v1_to20251231.py (edc444f943ea155c) | hand-check helper: DEF FIRST LAST COINS N INPUTS; on the VM add `$HOME/mnt/volat_store/lab_days $HOME/mnt/dev/TradingPlatform_repo/volat-agent/forensics`; coin names from the PRICE index (not BTCUSDT; V6-14) |
| R/LEAD/skills/reading-metrics/scripts/metric_brief.py (77d2f63edd3b07bf) | how to read a metric code |
On the Cowork VM, once: `python3 -m pip install --user pyarrow scipy` (V6-07). metric_brief.py on the VM, always with this env (V6-04):
`F=$HOME/mnt/dev/TradingPlatform_repo/volat-agent/forensics; METRICS_V1=$F/team/LAB3/METRICS_V1.tsv METRIC_TRAPS=$F/team/LAB3/LAB4/proposals/metric_traps/METRIC_TRAPS_V3.tsv CATALOGS=$F/team/RESEARCH/tools/alarm_context/CTX_CATALOG_V1.tsv:$F/team/RESEARCH/tools/alarm_profile/EPI_CATALOG_V1.tsv python3 -B $F/team/RESEARCH/LEAD/skills/reading-metrics/scripts/metric_brief.py CODES`
Memory: the jobs' detect workers stop at 2 GiB; measure the helper on half B for 8 days and keep it at or under 732 MB (V6-06).
Disk: queue_job_v4.py declares and guards it; CLEAN every decided job; ENTRY store places are protected and left for DSK.

## 7. Learning
- POSTMORTEMS after every job read: forecast, result (file, sha16), why, UNEXPLAINED.
- LEARNINGS_PROPOSED only for a RULE, TOOL, CHECK or SKILL change, with its evidence file. REPORT's time table says where minutes went.
- WHY FAILED and NEXT IDEA lines are how the next round picks better ideas: the lead copies them into K6/IDEA_GUIDE (patterns of what
  passes and what fails) and the scoreboard.
- The lead harvests every round's rows into the next LEARNINGS and the registry (PROCESS_V8 section 4): what you learn, the next
  agents know.
