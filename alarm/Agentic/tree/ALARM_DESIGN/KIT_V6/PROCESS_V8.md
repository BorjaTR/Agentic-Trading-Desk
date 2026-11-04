# PROCESS_V8: from an idea to a new alarm, faster every round (SCOUT, 29 Oct 2026). TEST, NOT REVIEWED. PROPOSED for the owner.
the owner 29 Oct 2026 (18:01 Berlin): "Sessions to find alarms should be faster and faster, learning loops should be faster and faster
continuously. And we should keep a registry of alarms with idea card, alarm card and how it was found so agents can get inspired and
also know what not to copy anymore." V8 changes HOW agents work and learn. What makes an alarm good stays PROCESS_V7's (KIT_V5/PROCESS_V7.md).

## 1. What stays from PROCESS_V7
- An alarm = a moment known at that moment + a side (FADE or FOLLOW). The test: its side wins the race (+2c before -1c) against 3
  matched random moments per fire, and more than the other side (the LEAD, 15 m and 1 h), month by month, Sep-Dec 2025.
- Decision (decide_v1.py): PASS = hand-off R2; NEEDS MORE MONTHS = R1 only; STOP = R1 missed; INSUFFICIENT, INVALID. CLEAR (the price
  path) is reported beside it and never changes it (the owner 29 Oct 14:23 Berlin). Jan-Apr 2026 only through the MONTH job; May on never.
- Budgets and safety: 3 graded variants an idea, 2 jobs an agent, 15,000 MB of own scratch, SCRATCH_DISK floor 60 GB; no quiet window (removed by the owner 30 Oct 2026 23:32 Berlin: "All jobs can be queued. Please do not stop queueing jobs").

## 2. One idea, start to end (the agent; KIT_V6 skill alarm-design-v6)
| step | what | tool |
|---|---|---|
| 1 Pick | an idea in the theme that the registry does not hold; read the 3 nearest alarm pages | REGISTRY |
| 2 Card | ONE card: idea, six quick checks, inputs, rule, hand check, forecasts, what proves it wrong | templates/CARD_V6.md |
| 3 Count | fires, waves, coins per month; support | COUNT job |
| 4 Grade | Sep-Dec against matched random, then the hand-off (R1, R2) | GRADE job |
| 5 Money path | for R1 variants: STRATEGY's store and markout (CLEAR) | ENTRY job |
| 6 Decide | the label from the receipts | decide_v1.py |
| 7 New? | the PASS's fire list against every alarm in the registry: NEW or NEW SIDE counts; COPY or NEAR does not | novelty_v1.py |
| 8 Forward | Jan-Apr, for a new PASS | MONTH job |
| 9 Stop | at the first new PASS (or 23:15Z): FINDINGS, REPORT with minutes per step, audit, DONE | |
Cut from V7's way of working (round 1 evidence): four cards per idea became one; the audit runs at checkpoints and at the end, not
after every job; agents stop at the goal instead of working on for hours.

## 3. The alarm registry (never lose an alarm)
- Where: team/RESEARCH/ALARM_DESIGN/REGISTRY/. ALARM_REGISTRY_V1.tsv is the index: one row per alarm (every decided variant of every
  round, plus the known STRATEGY alarms and desk triggers) with its state, numbers, how it was found, novelty and its page. Each alarm
  has a page alarms/<ID>.md: what it is, definition, how it was found, grading, Jan-Apr, when it works, overlap, do not, lessons, files.
- Built by REGISTRY/tools/registry_build_v1.py from the runs' files (rebuildable; nothing typed by hand). Never deleted: each round
  adds rows. The index is also kept in the Trading project.
- Agents read it before claiming (inspiration, and what not to copy or retry); novelty_v1.py checks every PASS against it.

## 4. The learning loop (the lead, every round, same day)
1. Launch: the prompt and kit of this round (LAUNCH_PROMPT_V6, KIT_V6).
2. Watch: answer every ASK SCOUT on hb/SCOUT.txt; fix a kit defect at once (twin, tests, mutants, MANIFEST, a FOR ALL line).
3. Wrap-up: agents stop at their first new PASS; the lead stops the round when every seat is DONE.
4. Harvest: every PROBLEMS and LEARNINGS_PROPOSED row and every REPORT time table, accepted or rejected with a reason, into the next
   LEARNINGS file (each row: what happened with numbers, the change, where enforced, the source) and the skill, card or tools.
5. Registry rebuild and the speed table (ROUNDS.tsv).
6. The next round's agents read the new rules and the registry first. That is how they know where the last ones failed.

## 5. Speed, measured each round (ROUNDS.tsv; runs/CLAUDE1_20261028/tools/agent_time_v1.py)
Minutes from launch to the first new PASS per seat; the share of that time with no job running; time lost and why; new PASS count;
copies caught; kit failures; agent tokens. Round 1 (29 Oct, KIT_V5): first PASS after 58, 73, 81 and 86 minutes; 28 to 53 pct of
it with no job running; 25 minutes lost to SCOUT's error; about 730,000 tokens per Claude agent. Each round must beat the last.

## 6. Next (KIT_V7)
One job per idea (count, grade, money path and Jan-Apr back to back); failing step logs and worker memory copied into receipts; a
hand-check tool. Each needs its own check on the real runner before agents use it.

## Sources
Round 1 runs: H/runs/AD1_20261029, AD2_20261029, AD3_20261029, GPT1_20261029 (REPORT.md, registers, receipts); KITCHECK_20261029;
LEARNINGS_V6.tsv; hb/SCOUT.txt 29 Oct; JOURNAL_SCOUT.
