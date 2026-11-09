# Playground queue tool: held-out re-grade outside the try budget (SCOUT C202, 8 Nov 2026)

TEST, NOT REVIEWED. Playground only. Nothing under <RELEASE_ROOT> was edited.

## Why

the owner, 8 Nov 16:10Z: "we do not need to release anything. we are in the playground and in a playground we can do whatever we want".

The kit's job filing tool allows at most 3 graded variants per idea per run folder (TRY BUDGET). A memory run spends all 3 on R1, R3
and R3P. The held-out step (alarm_pack/HELDOUT.md step 2 and 3) then seals a new variant with the SAME definition and grades it on the
Sep-Mar path, and the kit refuses it: TRY BUDGET. This copy lets exactly that one case through.

## Source copied

- <RELEASE_ROOT>/Alarm/alarm/ALARM_V1_22_2/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/queue_job_v15.py (sha16 d90e7cfd28cfaedc)
- and, because the held-out path files through them, queue_job_v16.py (menu gate wrapper, same folder) and
  pipe_mac_v3.py of ALARM_PIPELINE_V1_4_2 (sha16 06824d36c183c982; not copied, loaded by its path, pinned).

## Files here

| file | what |
|---|---|
| queue_job_v15_scout.py | the copy with the one rule changed (sha16 0c21e8d60e3105ce) |
| queue_job_v16_scout.py | queue_job_v16 with only its v15 (the copy above, pinned) and its menu gate folder (released KIT_V5/tools) changed (sha16 e292ce832ba73513) |
| pipe_mac_v3_heldout.py | runs the released pipe_mac_v3.py as it is, with only its kit queue pointed at queue_job_v16_scout.py |
| test_queue_job_v15_scout.py | the small tests |

## The diff in plain words

1. Where the kit lives: the copy reads its settings, templates and Alarm folder from the released KIT_V5/tools (or QJ_SCOUT_KIT_TOOLS),
   not from its own folder. Read only.
2. The one rule: a GRADE variant is not counted in the try budget when ALL of these hold, else it is refused with
   "HOLDOUT RE-GRADE <V> OF <IDEA> REFUSED: <why>":
   - its VARIANTS row carries the HELDOUT.md label "HOLDOUT re-grade of <IDEA> <V0>, same definition" (any field, the reason as today);
   - V0 is a graded variant of the same idea in the same run folder, and is not itself a held-out re-grade;
   - its sealed def_sha16 equals V0's def_sha16;
   - the job grades the held-out block: the block is read from the job text (the end day of the grade chain line
     `bash $MP/alarm_grade_chain_..._to<day>.sh`), for this job from the GRADE template it is filled from, for V0 from V0's filed
     job twin. The new job's block must end after V0's. No day is written in the code.
   A held-out re-grade already graded (with a mark that held) is also not counted, so the second and third re-grades (best round,
   R3, R3P) file too. Every normal variant still counts: a 4th normal try is still refused.
3. Nothing else changed: every other check, refusal, template pin, job text and register write is queue_job_v15's.

## Test command and result

```
python3 -B <LAB_REPO>/forensics/team/SCOUT/loop_day_20261105/learning_series/build/playground/test_queue_job_v15_scout.py
```

Synthetic run folder in a temporary folder under <SCRATCH_DISK>/tmp_SCOUT (removed by the test at its end); only plan() is called,
nothing is claimed, filed or queued. 8 Nov 2026: 7 tests OK in 0.04 s:

- (a) a 4th normal variant: refused, TRY BUDGET
- (b) a held-out re-grade with identical def_sha16: allowed (same file, and a byte-identical copy; after one is graded a second still files and a normal 4th is still refused)
- (c) a held-out re-grade with a different def_sha16: refused
- (d) a held-out mark on a non-held-out block (same block as the twin's grade): refused, NON-HELD-OUT BLOCK
- (e) a mark naming an ungraded twin: refused
- (f) queue_job_v16_scout.py and pipe_mac_v3_heldout.py load with their pins and point at the copy

Mutant check: with the exemption removed, 5 of the 7 tests fail (all but (a) and (f)).

## The line the orchestrator changes (held-out step, HELDOUT.md step 3)

The grade on the Sep-Mar path is run with the released pipe_mac_v3.py. Change only that command:

```
python3 -B <RELEASE_ROOT>/Alarm/alarm_pipeline/ALARM_PIPELINE_V1_4_2/tree/team/SCOUT/pack_kit/alarm_pipeline_v1/pipe_mac/pipe_mac_v3.py run <pipe folder> --until 11
```

becomes

```
python3 -B <LAB_REPO>/forensics/team/SCOUT/loop_day_20261105/learning_series/build/playground/pipe_mac_v3_heldout.py run <pipe folder> --until 11
```

(the same options; a direct filing without the pipeline uses `python3 -B .../build/playground/queue_job_v16_scout.py` in place of
KIT_V5/tools/queue_job_v16.py, same arguments). Step 2's VARIANTS label must stay exactly as HELDOUT.md writes it. The HELDOUT.md
caveat "each held-out regrade uses one of the idea's graded tries" no longer holds on this path. Hunters and memory rounds keep the
released tools.
