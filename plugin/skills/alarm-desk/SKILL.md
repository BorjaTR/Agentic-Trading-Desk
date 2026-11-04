---
name: alarm-desk
description: Use before any work on an alarm in the Crypto Alarm Desk repo - what an alarm is, the fixed loop from idea to a decided and audited try (desk.py commands), the rules that keep the verdict honest (seal before reading, verdicts only from the engine, TRUE required, waves not fires, no money), and the mistakes the lab already made.
---

# Alarm desk: how to design and test one alarm

The repo root holds `desk/desk.py`, `alarm/` (the engine) and `loop/` (the learning loop). Pages of `alarm/` that name the lab's FOUND list, scoreboard, registry index or other seats' material describe the lab: those files are
not shipped, so skip those reads; the desk's registry starts empty (made by `desk.py setup`), and every copy or novelty check is relative
to this desk's own registry, claims and logged tries only. Read, in this order, before your first try:
`README.md`, `CLAIMS.md`, `alarm/AGENTS.md` (the step table; where it names lab seats, boards or the lab disk keeper, the desk words below
apply), `loop/LESSONS_GENERAL_V1.tsv` (G rows hold anywhere, M rows are alarm method), `alarm/playbook/ALARM_GOALS_V1.md`,
`alarm/playbook/PLAYBOOK.md`. Then load the learning-loop skill.

## 1. What an alarm is
An alarm is a sealed, point-in-time detector of a stated event of forced trading: it marks a moment (a coin, a minute, and a side if
claimed) using only data known at that minute. It is valid when an independent label of that event, from data the rule does not read,
shows more at its fires than at matched comparison moments, counted by market event (wave), on the build months, then on later months
with the rule frozen. Firing often proves nothing.
An alarm is not a trade signal, is never judged on money, and a narrower version of an alarm you have is a variant, not a new alarm.

## 2. The words
- wave: fires on any coin whose successive gaps are at most 30 minutes form one market event; every count is in waves, never fires.
- seal: the definition, the card and the expected result are fixed (sha16 in a register row) before any outcome is read.
- TRUE: the claimed event shows on a label the rule does not read, beating matched busy moments and its own mirror (true_gate_v3).
- run: a folder `OUTPUT_ROOT/research/ALARM_DESIGN/runs/<NAME>_<YYYYMMDD>`, NAME capitals and digits, at most 12, no underscore.
  The engine calls NAME the "seat"; the "board" is a plain run log, `OUTPUT_ROOT/runlog/<NAME>.txt`.

## 3. The loop (every command from the repo root; `S` is a bare word that desk.py turns into `--settings <the alarm settings file>`)
| step | question | command |
|---|---|---|
| 0 setup | is the desk ready? | `python3 -B desk/desk.py setup`, then `python3 -B desk/desk.py check` |
| 1 IDEA | who must trade now, and was it tried? | `python3 -B desk/desk.py run 08_Registry/tree/ALARM_DESIGN/REGISTRY/tools/tried_search_v1.py S <words>` (the desk registry and claims) and `python3 -B loop/scripts/loop_find.py loop loop <words>` (the loop's TRIED rows and lessons: tried_search never reads them). On a fresh desk the registry is empty, so the copy search (and novelty, step 9) compares with nothing: `VERDICT DEF INCOMPLETE: 0 definitions could not be read and none of the 0 read ... no definition to compare` means there is nothing here to compare, not that something is wrong; read `alarm/playbook/PLAYBOOK.md`'s recipes and their Fails at lines, and run loop_find again with `--any` (without it every word must sit in one row, so HITS 0 does not mean never tried); name the closest recipe and any past try of the same moment with its verdict (or none) in your thought file, on the card as the forecast basis, and in your report; if you chose the idea yourself, a past STOP needs a new mechanism before a retry (V1.1) |
| start | a run folder | `python3 -B desk/desk.py start <RUN> --dry`, then without `--dry`; then `python3 -B desk/desk.py run Agentic/tree/ALARM_DESIGN/KIT_V5/tools/board_line_v2.py S <RUN> START "<idea in one line>"` |
| 2 METRICS, CLAIM | which code says it, in which unit, known when? | read `alarm/Agentic/tree/ALARM_DESIGN/KIT_V5/FORCED_TRADE_MAP_V1.md`, `METRIC_FAMILIES_V1.md`, pick from `METRIC_MENU_V2.tsv` (pickable YES, kind CLOCK), then `desk.py run 01_Detection/tree/team/LAB3/LAB1/tools/where_v2/where_v3.py <words> --kind metric --n 50` and `desk.py run 01_Detection/tree/team/RESEARCH/LEAD/skills/reading-metrics/scripts/metric_brief_v2.py <CODE>`; claim: a one-line text in `OUTPUT_ROOT/research/ALARM_DESIGN/runs/IDEAS_CLAIMED/<RUN>_<IDEA>.txt` |
| 3 DEFINE | the rule as a file | copy `alarm/01_Detection/tree/team/RESEARCH/ALARM_DESIGN/KIT_V2/templates/DEF_TEMPLATE_V4.json` to `<run>/ideas/<IDEA>/defs/V1.json`; the format is `DEF_TEMPLATE_V4.md` beside it |
| 4 HAND CHECK | does it fire, and fit in memory? | `desk.py run 01_Detection/tree/team/RESEARCH/ALARM_DESIGN/runs/CLAUDE1_20261028/tools/hc_defs_v4_to20251231.py S <DEF> 20251001 20251002 BTC,ETH 5 <INPUT>`, then `hc_mem_probe_v3.py S <DEF>` and `hc_size_v1.py S <DEF>` (same folder) |
| 5 COUNT | 30 or more waves in 3 of 4 build months? | `python3 -B desk/desk.py job <RUN> COUNT <IDEA> V1=ideas/<IDEA>/defs/V1.json --dry`, then without `--dry` |
| 5b SEAL | fixed before any outcome? | card from `alarm/Agentic/tree/ALARM_DESIGN/KIT_V6/templates/CARD_V7.md`, `menu_gate_v1.py check`, one VARIANTS row per variant with `reg_append_v1.py` (alarm/AGENTS.md step 5b) |
| 5c TRUE | is the claim true on a label it does not read? | label file from `alarm/03_Grading/tree/tools/true_gate/CLAIM_TEMPLATE.json`, `true_gate_v3.py check <claim>` at SEAL; after GRADE: `desk.py job <RUN> TRUE <IDEA> V1=ideas/<IDEA>/TRUE_V1_<LABEL>.json --from-job <NUM>_GRADE_<IDEA>`. Before GRADE the per-fire file does not exist: at SEAL write `"perfire": "/PENDING_GRADE/PERFIRE_V1.tsv"` and `"perfire_sha16": "PENDING_GRADE"` (the check needs the name to end PERFIRE_<V>.tsv); after GRADE, before queuing TRUE, set both to the GRADE job's PERFIRE_<V>.tsv and its sha16 from `receipts/<NUM>_GRADE_<IDEA>/PERFIRE_SEAL.tsv`; label, mirror, activity, lean and definition stay as sealed (V1.1) |
| 6 GRADE | beats matched random moments? | `desk.py job <RUN> GRADE <IDEA> V1 --dry`, then without |
| 7 DECIDE | PASS, NEEDS MORE MONTHS, STOP, INSUFFICIENT, INVALID? | `desk.py run Agentic/tree/ALARM_DESIGN/KIT_V5/tools/decide_v6.py S <RUN> <IDEA> V1 --grade <GRADE job>` (`--write` to record) |
| 9 NOVELTY, FIRST LOOK | new? enough movement, which side? | alarm/AGENTS.md steps 9 and 9b; NEW means new to this desk's registry only (empty on a fresh desk), never new to the world |
| check | is the run complete? | `desk.py run Agentic/tree/ALARM_DESIGN/KIT_V5/tools/audit_run_v5.py S <RUN>` (`--write` before you call it done) |
Jobs run here, in the foreground, one at a time (`desk.py job`). Results: `<run>/receipts/<JOB>/`, its `STAGES.tsv` has every stage's code.
Audit A7 (PICKUP) fails a finished job that no DECISIONS or POSTMORTEMS row names within 20 minutes of its end. Right after each job ends, before you seal or read on, append one POSTMORTEMS row naming the job, its result file and sha16 with `reg_append_v1.py` (scope COUNT for a COUNT job; for FIRST LOOK the build-months scope, SEPDEC in this edition); a DECISIONS row from decide `--write` also counts. Where stdin is closed (a bridge job), pass the row as a JSON file, not `-`.

## 4. Rules that keep the verdict honest
1. Verdicts come only from the engine (decide, true_gate, audit). You never compute or round a verdict yourself, and you never edit
   anything inside `alarm/`.
2. Seal before you read: a variant's definition and reasons are sealed before any outcome of it. A changed rule is a new variant; a
   variant is graded once; at most 3 graded variants per idea.
3. Months (this edition, on the lab's data): build on Sep-Dec 2025 only. Jan-Feb 2026 is EXPOSED: it may be read once, only on the
   owner's explicit word, under a frozen protocol logged before the read, every number from it labelled EXPOSED. Every other date is
   closed. MONTH reads Jan-Apr: never run it under a Jan-Feb-only authorization. A later date alone does not make a result blind.
   Luck (any sign-flip or SPA print) is information only, never a bar.
4. TRUE is required: a decision without its TRUE row is not finished (the audit says FINISHED NO). UNSURE, NOT SUPPORTED or REFUSED
   are results, never reasons to change the label after seeing them.
5. Never money: the alarm's label is never profit; ENTRY numbers are information for a later strategy stage.
6. Waves, never fires, in every count you write; every number carries its file and sha16, or is called an opinion.
7. A refusal by any tool is reported word for word and the try stops there. Never work around a refusal, never change a sealed file to
   make it pass.
8. Log every try with the learning-loop skill, including failed and refused ones.

## 5. Mistakes already made (check each before you post a result)
- Late detector: a rule that fires after the forced flow is done can be TRUE and leave nothing ahead. Aim at the build-up.
- Fires counted as independent: thousands of fires can be a few hundred waves; per-fire statistics overstate everything.
- One target on all fires (a bucket test): never take all fires and change one parameter to see if it works now.
- Crash-day illusion: show results without the best days and the top coins.
- Calm or unfair bases: compare with matched busy moments that share every condition except the one the claim is about.
- A side flipped after reading it is a new idea with already-seen months.
- A rule widened to reach a count without saying what it does to the claim.
- A new test that stops ideas before it passed known good cases and failed known bad ones.

## 6. Report (under 15 lines)
Idea, claim, forced trader and how measured, def sha16, waves, the TRUE word with gap and claim minus mirror, first look label with SIZE
and SIDE apart, LEAD 15 min and 1 h with t and months if graded, the other side's gap, novelty and its basis, what the tools got wrong,
one change you would make. Every number with its file and sha16.
