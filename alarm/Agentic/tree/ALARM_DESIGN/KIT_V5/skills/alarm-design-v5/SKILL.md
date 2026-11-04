---
name: alarm-design-v5
description: Find trading alarms in the owner's volat-agent team with ALARM_DESIGN KIT_V5 (PROCESS_V7) - from an idea to a decision (PASS, NEEDS MORE MONTHS, STOP) that the strategy stage can use, with every number taken from a tool file.
---

# Alarm design V5 (KIT_V5, PROCESS_V7). TEST, NOT REVIEWED.

## 0. The goal, and why the last agents found nothing
Your goal: take each idea you are given to a decision by PROCESS_V7 and report it. A decision is PASS, NEEDS MORE MONTHS or STOP (or
INSUFFICIENT, INVALID when the study could not be done). A good run decides every idea it claims, with numbers from tool files.
An alarm is a moment named from data known at that moment, with a side (FADE or FOLLOW). It is good when its side wins the race
(+2c before -1c) more often than at 3 matched random moments AND more than the other side does (the LEAD, at 15 m and 1 h), in most
months, with t of at least 3. Direction alone is enough; money is the strategy stage's job.
The machinery is proven: on made-up alarms it finds planted edges and rejects empty ones (K/PROCESS_V7.md section 4). Some of your
ideas are controls with known answers; treat every idea the same.
On 28-29 Oct two agents ran 25 versions and 28+ jobs and found nothing. Why (K/LEARNINGS_V5.tsv has the rest):
1. They compared ideas with other alarms instead of with matched random. 2. They added gates nobody asked for and closed 18 of 25
versions before any outcome. 3. They built tools and wrote documents instead of running their own tests. 4. They watched the board
instead of working. 5. They ran unsized jobs; the shared drive filled twice. Everything below exists to stop these five.

Names: F = <LAB_REPO>/forensics, R = F/team/RESEARCH, H = R/ALARM_DESIGN, K = H/KIT_V5,
T = H/runs/CLAUDE1_20261028/tools, RUN = H/runs/<RUN> (your run tag, e.g. AD1_20261029; your seat is the part before _).
On the Cowork VM, <DEV> is $HOME/mnt/dev. Your board: F/hb/<SEAT>.txt. Set up once: cp -R -n K/runs/TEMPLATE_V3 RUN.

## 1. Seven rules that never bend
1. **Source every number.** Every number you write is copied from a tool output file named next to it with its sha16. Never
   compute, round or remember a result. Decisions are written by decide_v1.py, never typed. Unsure: write UNKNOWN.
2. **Freeze before you look.** Rule, side and forecast are sealed in a PREREG (its sha16 in VARIANTS) before any job reads an
   outcome. A sealed file never changes; a change is a new variant. Only PROCESS_V7's lines decide (R1, R2); any other line you think
   of goes to LEARNINGS_PROPOSED and never decides your idea.
3. **Budgets.** At most 3 graded variants per idea; the 2nd and 3rd name a result you already read as their reason. At most 2 of
   your jobs in the queues, or 3 with the 3rd waiting behind your own (--behind). Your run holds at most 15,000 MB of its own
   uncleaned scratch on SCRATCH_DISK: decide, then CLEAN (step J). queue_job_v4.py enforces all three.
4. **Months.** Count, grade and hand-off read 10 Sep-31 Dec 2025 only. Jan-Apr 2026 only through the MONTH job, after its forecasts
   are sealed. May 2026 on: never. Read only your own receipts and the files this skill names, never another run's outputs.
5. **Stuck or unclear.** The same failure twice, or a rule you can read two ways: stop that path, write a PROBLEMS row (both
   readings), post STUCK, take the next idea. Never raise a resource cap or cut the coin list to get past a refusal.
6. **Only the kit's tools** (section 6), by sha16. An idea that needs a new reading or tool goes on your BLOCKED list with what it
   needs; take the next idea. Never edit K, another run's files or a tool you did not write.
7. **House rules.** Twin before edit (cp -n f f.pre_<RUN>_<stamp>), drafts too; never delete by hand (no rm, git, sudo, dd): the CLEAN
   job is the only way anything is removed, and only your own job scratch after its proof is on dev; no find,
   grep -r or du from the VM (ls of a named folder, head or grep on named files only); SCRATCH_DISK only inside jobs; nothing queued at or
   after 23:20Z (quiet window 23:30-00:15Z); stamps from the clock; no em dashes; device commands under 6,000 characters (write
   files in parts); names in capitals and digits only.

## 2. The path of one idea (PROCESS_V7 step numbers in brackets)
| # | Do | Writes | Stop when |
|---|---|---|---|
| A [1] | Read team/RESEARCH/alarms/ALARMS_V1.tsv, H/KIT_V2/cards/ALARMS_INDEX.tsv, H/runs/IDEAS_CLAIMED/. Claim: cp -n of a one-line text to H/runs/IDEAS_CLAIMED/<RUN>_<IDEA>.txt (never overwrite). Board CLAIM | the claim file | someone claimed it; it matches an existing trigger (then REUSE: grade that one, credit its author) |
| B [2] | Idea card (K/templates/IDEA_CARD_V5.md) with the six quick checks (K/IDEA_TO_ALARM_V4.md, K/QUICK_CHECK_EXAMPLES_V2.md), each with one number or file. Readings: python3 -B R/LEAD/skills/reading-metrics/scripts/metric_brief.py <CODES> and K/METRIC_MENU_V1.tsv. A trader story without an identifying reading is HYPOTHESIZED: grade anyway | ideas/<IDEA>/IDEA_CARD.md | FAIL on METRIC CONTRACT |
| C [3] | Alarm card (K/templates/ALARM_CARD_V4.md) and definition JSON from H/KIT_V2/templates/DEF_TEMPLATE_V2.json (example: H/runs/CLAUDE1_20261028/ideas/LOOP2/defs/LP2_DAYPOKE_DEF_V2.json). Hand check: 3 cases worked by hand from raw rows (fire, boundary, missing input); helper python3 -B T/hc_defs_v1_to20251231.py DEF FIRST LAST COINS N INPUTS (on the VM add `$HOME/mnt/volat_store/lab_days $HOME/mnt/dev/TradingPlatform_repo/volat-agent/forensics`) | ideas/<IDEA>/ALARM_CARD.md, defs/<V>.json | the engine disagrees with a hand case (fix the definition; no outcome was read, so it is not a try) |
| D [2] | COUNT job (up to 3 definitions): fires, waves, coins per month on Sep-Dec, no outcome. Fill SUPPORT from COUNT_<V>.tsv; POSTMORTEMS row (scope COUNT) | receipts/<JOB>/COUNT_<V>.tsv | under 30 waves in 2 or more of the 4 months: SUPPORT FAIL (the study stops, the idea is not disproved); fires only on BTC (a scope trap) |
| E [4] | PREREG (K/templates/PREREG_V5.md): variants, definition sha16s, lean, the Sep-Dec forecast (LEAD at 15 m and 1 h, R1, R2, CLEAR), what would prove it wrong. Then one VARIANTS row per variant (reg_append_v1.py). Board PREREG | ideas/<IDEA>/PREREG_<IDEA>.md | |
| F [5a, 7] | GRADE job (up to 3 variants): Sep-Dec grade against 3 matched random moments per fire, then the hand-off test (lead_null) | receipts/<JOB>/ | |
| G [5b] | ENTRY job for every variant whose hand-off R1 passed (queue_job_v4.py refuses the others): STRATEGY's grader store (no exit ladder) and markout, Sep-Dec | receipts/<JOB>/<V>/MARKOUT/ | |
| H [8] | Decide: python3 -B K/tools/decide_v1.py <RUN> <IDEA> <V> --grade <JOB> [--entry <JOB>] --write. Then a POSTMORTEMS row (forecast against result, why, UNEXPLAINED), FINDINGS (K/templates/FINDINGS_V5.md), board DECISION | the DECISIONS row (written by the tool) | |
| I [6] | For PASS and NEEDS MORE MONTHS only: one forecast file per variant (K/templates/FORECAST_V5.md) and its 4 FORECASTS rows (2601-2604), then a MONTH job (Sep-Apr grade, month reads, conditions). A weak month's reason is a FINDING for later, never an edit or a new variant | POSTMORTEMS rows per month; FINDINGS updated | |
| J | CLEAN: once the variants of a job are decided (GRADE, ENTRY) or it is read (COUNT, MONTH: a POSTMORTEMS row names it), queue a CLEAN job for it. It first copies the fire lists and per-fire files to your receipts on dev, then removes the job's SCRATCH_DISK scratch and logs each path and size; an ENTRY job's store places are protected (DISK_RULES_V1) and are logged as left for DSK | receipts/<CLEAN JOB>/CLEANED.tsv; CLEANED_BY.txt in each job's receipts | |

Decision (PROCESS_V7 step 8; decide_v1.py applies it): PASS = hand-off R2. NEEDS MORE MONTHS = R1 only. STOP = R1 missed.
INSUFFICIENT = fewer than 3 counted months (not a NO). INVALID = a stage failed, a file is missing or the hand-off gate failed.
CLEAR (the price path) is reported next to the label for every variant with R1 and never changes it (the owner 29 Oct: "for now we keep
them separate and report both"). NEEDS MORE MONTHS is the normal verdict for a real but small alarm (a true +5 LEAD passes R2 only
32-49 pct of the time on our months): never add a stricter bar. Money after cost and TOUGH are reported, never decide here.

## 3. Jobs (one way only)
- Every job: `python3 -B K/tools/queue_job_v4.py <RUN> <KIND> <IDEA> <ITEMS> [--queue Q_Vn] [--from-job <JOB>] [--behind] [--dry]`.
  COUNT: ITEMS `V1=ideas/<IDEA>/defs/V1.json[,V2=...]` (definitions start from DEF_TEMPLATE_V2.json: window 20250901 to 20260531).
  GRADE: `V1[,V2,V3]` (in VARIANTS, one PREREG). ENTRY and MONTH: `V1[,...]` with `--from-job <the GRADE job, e.g.
  20263700_GRADE_FLOWX>`. CLEAN: ITEMS = job names, e.g. `20263700_GRADE_FLOWX,20263702_ENTRY_FLOWX` (IDEA is a label; CLEAN is not
  counted in the job budget). Use --dry first to see the filled job. A job that failed (its variant's stage rc not 0, or stopped before it) gave no
  result: queue that variant again under its name; it is no extra try. The tool checks names, budgets,
  pins, forecasts, the disk and the queue, claims the number from the live allocator, writes the twin to RUN/jobs/ and the RUNS row,
  and copies the job into an empty Q_V queue. Never write a job by hand.
- Check every 5 minutes with short calls: `ls` the queue's RUN and IN, then RUN/receipts/<JOB>/STAGES.tsv. Never wait inside a shell
  call. Set a wake-up every 5 minutes if your session can. While a job runs, do your next idea's steps A-E. Read hb/DSK.txt at every
  check; if DSK warns about SCRATCH_DISK, queue nothing until it clears.
- A job is done when STAGES.tsv has its `end` line. Read it only if every stage has rc 0; else it FAILED: write its first error in
  PROBLEMS (the same failure twice: rule 5). A finished job is read before your next check.
- After every job you read: `python3 -B K/tools/audit_run_v2.py <RUN> --write`; fix or explain every FAIL before your next job.

## 4. Registers (RUN/registers/, append-only; `python3 -B T/reg_append_v1.py RUN <REGISTER> -` with the row as JSON on stdin)
VARIANTS (every variant, before its job), FORECASTS (each forward month, before its job), RUNS (written by queue_job_v4.py),
DECISIONS (written by decide_v1.py), POSTMORTEMS (after every job you read), LEARNINGS_PROPOSED (section 7), PROBLEMS (a STOP one goes
to the lead at once), TOOLS_BUILT (any tool you write, with its passing test). Columns: RUN/README_RUN.md.

## 5. Board and reporting
- Board lines only with `python3 -B K/tools/board_line_v1.py <RUN> <KIND> "<what, with files and sha16>"`; KIND is START, CLAIM, COUNT,
  PREREG, JOB, DECISION, STUCK, ASK, ANSWER, CHECKPOINT, DONE or NOTE. Post CHECKPOINT after each decision and at each checkpoint time
  in your launch prompt: ideas claimed, decided, jobs run, open problems, the audit score.
- Read every ASK addressed to you before your next decision; answer by the due time.
- One FINDINGS_<IDEA>.md per idea, also for STOP (a no is a result): verdict first, the numbers with their files.
- At the end: RUN/REPORT.md (K/templates/REPORT_V5.md), then board DONE. To the owner only through the lead: verdict first, about 5 short
  bullets, plain words, the exact command, no time estimates, a mistake said at once.

## 6. Tools (the job templates pin every tool they run by sha16; K/MANIFEST_SHA16.txt lists the kit's own files)
| tool | what |
|---|---|
| K/tools/queue_job_v4.py | the only way to queue a job |
| K/tools/decide_v1.py | the decision from the receipts; writes DECISIONS |
| K/tools/board_line_v1.py | one board line, checked |
| K/tools/audit_run_v2.py | the scorecard of your run |
| K/tools/clean_scratch_v1.py | inside CLEAN jobs only: keeps the proof on dev, removes your own scratch, logs it |
| T/reg_append_v1.py (c301c5977ecd6860) | append one register row (stamp from the clock) |
| T/hc_defs_v1_to20251231.py (edc444f943ea155c) | hand-check helper (it prints from the engine; your hand calculation is the proof) |
| R/LEAD/skills/reading-metrics/scripts/metric_brief.py (77d2f63edd3b07bf) | how to read a metric code |
Inside the jobs only: detect.py 83c52bfd27166f76; grade chains v2_0_to20251231 94273faf1e927ddc and v2_1_to20260430 99e8a229617cb2e2;
perfire 2072f03fba520e72; lead_null 22b58c1c72aab4f2; store without ladder 45ac17404e5dc762; markout_v1_1 3239e4685080894e;
read_stratentry efe30de7fdfd2c59; month_read_v3 b3480cfd670b28f4; conditions_v1 2f4aaebe1f259278.
Disk (queue_job_v4.py declares it): COUNT 300 MB a definition; GRADE 1,800 MB a variant; ENTRY 300 MB per 1,000 fires (at least
1,000; measured 29 Oct: 550 MB for 5,042 fires); MONTH 3,000 MB a variant; CLEAN 10 MB. Every job stops when SCRATCH_DISK has under 60 GB free; your run's uncleaned scratch stays
under 15,000 MB (measured from finished receipts, declared for the rest). Never run STRATEGY's run_alarm_store_v10_3.sh
whole: its exit ladder wrote 8-21 GB a job and filled SCRATCH_DISK on 29 Oct.

## 7. Learning (after every decision)
- POSTMORTEMS: what you forecast, what came out (file, sha16), why, what is UNEXPLAINED.
- LEARNINGS_PROPOSED only when it changes a RULE (how you work), a TOOL (a fix or a gap), a CHECK (a test or scorecard item) or this
  SKILL: the exact change, its evidence file and where you saw it. One alarm's result is a postmortem line, not a learning.
- Read K/LEARNINGS_V5.tsv before your first idea. Its rows are rules.

## 8. Skill improvement
- A proposed change to this skill is a LEARNINGS_PROPOSED row with kind SKILL: the section, the exact new text, the evidence.
- The lead batches accepted rows into the next version (V5.1, ...) after the owner's OK. A change is judged on later ideas, never on the
  one it came from; it never applies to an idea already sealed. Re-read the changed section when the lead posts SKILL V5.<n>.
