Written by SCOUT for the repo on 30 Oct 2026 from KIT_V5/README.md and tree/ALARM_DESIGN/KIT_V5/ (PROCESS_V7.md, MANIFEST_SHA16.txt,
skills/alarm-design-v5/SKILL.md, jobs/, tools/queue_job_v4.py, tools/decide_forward_v1.py, templates/FORECAST_V5.md, tests/) and
../03_Grading/month_parts/README.md; not the owner's document (owner seat: SCOUT).

# SCOPE: ALARM_DESIGN KIT_V5

**Purpose and user.** Let an alarm agent (Claude or any other model) take an idea to a decision (PASS, NEEDS MORE MONTHS, STOP,
INSUFFICIENT or INVALID) the same way every time, with every number taken from a tool file, and test it on Jan-Apr 2026 only after its
forecast is sealed. the owner's goal (29 Oct 23:13 Berlin, month_parts README): an alarm counts as FOUND only when its Jan-Apr months hold.
Users: the alarm agents, SCOUT and the lead (launch, watch, audit), the owner (the results).

**In scope.**
- The way of working: PROCESS_V7 (steps 1-8, the package for STRATEGY, the proof the machinery works), the skill, LEARNINGS_V5, the
  launch prompt, the front end (six quick checks, metric menu and families), the templates (idea card, alarm card, PREREG, forecast,
  findings, report) and the run template (8 registers).
- The jobs, queued only by `queue_job_v4.py`: COUNT (fires, waves, coins per month), GRADE (Sep-Dec grade and hand-off: part 03),
  ENTRY (STRATEGY's grader store and markout: part 07), MONTH (Sep-Apr grade and the 4 month reads: part 04), CLEAN (a run's own
  scratch). The queue checks names, the claim, the try budget (3 graded variants an idea), sealed definitions, PREREG and forecasts,
  the decision a MONTH job needs, own jobs, an empty queue, the quiet window, SCRATCH_DISK space, the run's disk budget, the template sha16.
- The GRADE job: up to 3 variants; per variant the chain v2_0 on 10 Sep-31 Dec 2025 (every fire against 3 matched random moments, the
  race +2c before -1c at 5 m, 15 m, 1 h, by month), the per-fire file and its check, the FIRES.tsv row; then the hand-off test
  (10,000 day-block flips) on every variant that finished.
- The MONTH job: per variant the grade over 10 Sep 2025-30 Apr 2026 (chain v2_2 in 26 coin parts), each part's memory and data and code
  versions, the per-fire file, month_read_v3 for 2601-2604 at 15 m and 1 h against the sealed ranges, the conditions (descriptive).
- The decisions: `decide_v1.py` (the label from the GRADE and ENTRY receipts), `decide_forward_v1.py` (a forward-only variant: FORWARD
  PASS when 3 or more of the 4 months read HELD or STRONGER); the audit (`audit_run_v2.py`, 17 checks); board lines; CLEAN.
- Every job: pins (sha16) of every tool it runs, no start near the quiet window, a stop under 60,000 MB free on SCRATCH_DISK, receipts with
  their sha16.

**Out of scope.** The lab tools the jobs run (detect, the grade chains, Outcomes, the card, the per-fire file, the hand-off test, the
markout: their parts and the dev tree; the run tools they pin are copied in `tree/ALARM_DESIGN/runs/`); the data; money (which fires to
take, exits, size: the strategy stage); May 2026 and later (sealed).

**Success.** A job is queued only when its inputs are sealed and its budget fits, or refused with a message naming why; it stops before
any step when a pinned file changed; every decision can be recomputed from the receipts (audit A6); the kit tests pass (59 tests,
RUN_PROOF.md of Agentic).
