# queue_job_v12: tool card

queue_job_v11 plus three things (SCOUT, 1 Nov 2026, ALARM_V1_16; why: team/RESEARCH/plans/PLAN_SCOUT_TOOLS_V1_16_20261101.md); the
same templates, MEM_MB, checks and job text. The code: [queue_job_v12.py](../Agentic/tree/ALARM_DESIGN/KIT_V5/tools/queue_job_v12.py).
Everything else (kinds, arguments, checks, columns): [queue_job_v11.md](queue_job_v11.md). Status in the code: TEST, NOT REVIEWED.

## What changed from v11
- `--dry` first prints the prerequisites, all of them, as `DRY CHECK <what>: OK|MISSING <detail>`: the run folder, its registers,
  the claim file, for ENTRY the card, for MONTH the 4 FORECASTS rows (2601-2604) of each variant. Each MISSING line is followed by
  `NEXT: <what to do>`. Any MISSING ends the dry run with exit 2.
- Every refusal it knows prints `NEXT: <what to do>` after its REFUSED line.
- ENTRY: the job reads ideas/<IDEA>/ALARM_CARD.md. When only the sealed ideas/<IDEA>/CARD_<IDEA>.md is there, the queue copies it
  byte for byte to ALARM_CARD.md (never over a file) after every check passed and before it claims a number; `--dry` says it would.

## Run it
```
python3 -B <INSTALL>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/queue_job_v12.py --settings <S> [--job-settings <MAC S>] <RUN> <KIND> <IDEA> <ITEMS> [--from-job <GRADE job>] --dry
```
then the same without `--dry`.
