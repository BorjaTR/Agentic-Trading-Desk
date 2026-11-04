# first_look: tool card

Does this moment offer enough movement, and which way, against equally busy random moments? One variant, one job, through the queue
(KIND FIRSTLOOK of queue_job_v14, JOB_FIRSTLOOK_V1). Released in ALARM_V1_19; this page is ALARM_V1_21_1 (queue_job_v15 runs FIRSTLOOK as v14 did); status TEST. Reader by default: edition 11 (fl_read_v11), the rule in force edition 9. Edition 12 (fl_read_v12) with `--reader v12`: see "Change the reader"; it prints RULE_12 and RULE_9 side by side.

## When
After 7 DECIDE or 9 NOVELTY, for any decided state: a STOP on decide_v4's race can still pass SIZE. Again after 10 MONTH with `--month-job`.

## Run it (S = `--settings <INSTALL>/settings/SETTINGS_LOCAL.env`)
```
python3 -B Agentic/tree/ALARM_DESIGN/KIT_V5/tools/queue_job_v14.py S <RUN> FIRSTLOOK <IDEA> <V> --from-job <GRADE job> --dry
python3 -B Agentic/tree/ALARM_DESIGN/KIT_V5/tools/queue_job_v14.py S <RUN> FIRSTLOOK <IDEA> <V> --from-job <GRADE job>
```
Add `--month-job <MONTH job>` after that variant's MONTH. Nothing else is typed: the job chains every step.

**The source is checked first (GPT's hold, 2 Nov).** Before a number is claimed or a byte copied: the job's one RUNS row, its twin's sha16, the sealed variant's card and definition; a MONTH's `from_job` is this GRADE and all four months ended 0; no failed stage of this variant; the PERFIRE's sha16 and counts equal `PERFIRE_SEAL.tsv` (GRADE and MONTH V14 write it when the test passes); every row inside the period (a GRADE to 31 Dec 2025, a MONTH to 30 Apr 2026, read from `kind`, `coin`, `t`, `side` only); the fires equal the job's recorded fire list. A job from before V14 has no seal: `--unsealed-source` accepts the file, checks its counts against the job's log, and FIRST_LOOK.md says the source is not authenticated (old MONTH jobs recorded no fire list digest either: the list, when still there, is compared by row only). An older job with its PERFIRE in receipts and in SHA16.txt reads RECEIPT_SHA16.

| | no `--month-job` (SEPDEC) | with `--month-job` (FULL) |
|---|---|---|
| days read | 10 Sep to 31 Dec 2025; no Jan-Apr outcome is opened | 10 Sep 2025 to 30 Apr 2026 |
| best label | NEEDS MORE MONTHS (bars) | SIZE, SIDE or SIZE+SIDE |
| PERFIRE from | the GRADE job | the MONTH job |

## What you get: `RESEARCH_ROOT/ALARM_DESIGN/runs/<RUN>/receipts/<JOB>/`
- `FIRST_LOOK.md`: the label and each bar, one page. Read this first.
- `FL_RULE9_ROW.tsv`: the row of FL_RULE9 (the rule file is a setting; an edition 12 names its own).
- `FL/`: all the reader's output: FL_RULE9.tsv, FL_<V>_RULE8.tsv (month by month, each bar), FL_<V>_MONTHS.tsv, FL_<V>_WINDOWS.tsv (offer and heat 1-180 min), FL_SUMMARY.tsv, FL_<V>.json.
- `PERFIRE_<V>.tsv` (kept here, since the scratch copy is swept), `inputs/`, `outcomes/`, `profile/`, `busy/`, `PROVE_BZ.tsv`, `PEAKS.tsv`, `DISK.tsv`, `STAGES.tsv` (done when it has its `end` line).

## How to read the label (RULE_9)
| label | meaning |
|---|---|
| SIZE | busy fires move 4c either way within 1 h more often than equally busy random moments, in both periods |
| SIDE | the variant's lean wins its 1 h race (offer 4c before heat 4c) more than random, in both periods |
| SIZE+SIDE | both bars, both periods |
| NEEDS MORE MONTHS (bars) | the bars pass Sep-Dec only. In SEPDEC mode this is the best possible label |
| NOT PASS | no bar passes Sep-Dec. A bar not run (no BZ tables) also reads here: check `SIZE_SepDec_fail` |

A bar passes a period when: above 0 in 3 of 4 months (a month under 10 waves is THIN); z at least 2 on Sep-Dec, at least 1 on Jan-Apr (Jan-Apr confirms); still above 0
without the 2 coins that add most and without the 5 best days; 30 waves with a 1 h value in every month. c = the coin's cost_bp/100 + 0.032. Waves: 30 min, any coin.

**Size and side answer different questions.** SIZE: is it a moment when price moves far enough to pay, either way? It says nothing on direction. SIDE: is the lean right?

## "PASS" has two meanings
| where | word | means |
|---|---|---|
| decide_v4 DECISIONS `state` | PASS | R2: R1 (LEAD +3 or more at 15 min or 1 h in 2 of every 3 counted months) plus a pooled t of 3 or more. A race of +2c before -1c on the lean's side, against 3 matched random moments, Sep-Dec |
| first look `SIZE_SepDec`, `SIDE_JanApr`... | PASS | that one bar held on that period. Not a label |
| first look `RULE_9` | never bare PASS | SIZE, SIDE, SIZE+SIDE, NEEDS MORE MONTHS, NOT PASS |
| first look `FL_SUMMARY.tsv` `FIRST_LOOK` | PASS | the old rule of editions 3 to 6, kept beside. Not in force: never quote it |

SIDE and R1/R2 both ask about the lean, but differ: 4c/4c at 1 h on the first-look random, against +2c/-1c at 15 min and 1 h with LEAD. They can disagree: AD8 RC2 is PASS in the registry, and its rule 9 is SIZE, SIDE NOT PASS (results/TRY4_FL1_20264600/FL_RULE9.tsv dbe4f2d4927c398b). Say which you mean: "decide_v4 PASS" or "first look SIZE".

A first look label changes no register: decide_v4, the registry and SCOREBOARD do not read it, and it is not a money result; the job's money columns are beside, never a rule.

## Refusals (exit 2, each with a NEXT line)
`NEEDS --from-job`, `HAS NO RECEIPTS`, `NOT FINISHED`, `NO GOOD GRADE` or `NO GOOD MONTH` (grade_V, perfire_V, perfire_test_V must each end rc 0), `NO PERFIRE`, `PERFIRE HAS`,
`SOURCE ...` (the PERFIRE, fire list or job is not what the job left), `SOURCE LEAN` (the job ran this variant with another lean: a side needs its own variant and GRADE), `SOURCE SEAL LOST` (this job had a seal: `--unsealed-source` does not apply), `OUTSIDE THE PERIOD` (a row before the look's first day, 10 Sep, or after its last), `READER`, `NO SOURCE SEAL`, `FAILED STAGE`, `FIRSTLOOK TAKES ONE VARIANT`, `NAME TOO LONG` (over 20), `ALREADY LOOKED` (the same variant from the same job; a failed look may run again), `FIRSTLOOK SETTINGS` (the release is broken), `--month-job MUST BE`, the queue's usual ones.

**NO PERFIRE**: GRADE and MONTH keep `PERFIRE_<V>.tsv` only in the job scratch on SCRATCH_DISK, and DSK's sweep removes it. So queue the look soon after GRADE. Once swept, the look cannot run: ask DSK and SCOUT; never write a PERFIRE by hand, and a variant is graded once.

## Job exits
0 done; 3 a pin changed, or a Sep-Dec look read a pass label (a fault); 7 under 60 GB free; 8 the feed gate file is missing; another code = the first failed step, whose `<stage>.tail.txt` is in the receipts. A failed step stops the job before the reader, so a failed look writes no label.

## Speed and sizes
Measured from a copy of the release: FB5, 5,255 fires and 14,916 random, Sep-Apr: 537 s, W 1,958 MB (job 20266478). CLOSEHOUR V1, 1,175 and 3,022, Sep-Dec: W 927 MB (job 20266479). Peak of any step 1,983 MB (the profile); on 47,962 fires 2,040 MB (job 20266489); outcomes 1,219 MB on the largest stored list. MEM_MB 2448 = 2,040 + 20 percent. WRITES_MB = 1000 + events / 15, an upper line from those two jobs. About 100,000 events pass 60 declared minutes (the queue prints a NOTE; no split yet); about 135,000 pass the run's 10,000 MB budget and are refused DISK BUDGET.

## Change the reader
`--reader v11` or `--reader v12`; no argument = `default_reader` of `06_First_look/FIRSTLOOK_SETTINGS_V1.json` (v11, the bar in force). Each block of `readers` names `rel`, `sha16`, `rule_file`, `label_column`, `extra_args`; it must stay under 06_First_look/ and take `<TARGETS_FL.tsv> <H> <costs> <out> <outcomes dir> <profile dir> <BZ dir>`. A second reader on the same source may run beside the first; the same reader twice is `ALREADY LOOKED`.
Edition 12 (`RULE_12`, not in force here): `--reader v12`. A block with `bar_tool` adds stage `bar` before the reader: `bar_v1.py build` on this look's two lists and days into `<receipts>/BAR/`, then `--bar`; the tables are built inside the job, so their manifest comes from their producer. Its table holds `RULE_9` too, and the page shows both as retrospective. It replaces no label and is no reason to choose an alarm. Its reader and ladder refuse a threshold table whose bytes, producer or rows differ from BAR_V1.json.
