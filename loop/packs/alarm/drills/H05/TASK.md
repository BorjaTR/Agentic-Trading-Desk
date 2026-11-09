Drill H05 (round 2: explain). You are a hunter reading round 2 results (paper research). Read ONLY: <LAB_REPO>/forensics/team/SCOUT/loop_day_20261105/learning_series/drills_v2/hunter/H05/MATERIAL/CONTEXT.md and <LAB_REPO>/forensics/team/SCOUT/loop_day_20261105/learning_series/drills_v2/hunter/H05/MATERIAL/SPLIT_1.tsv ... SPLIT_6.tsv (state_split outputs: per state its lead, se, t, waves, by month). Do not open any other file.
Write ONLY <LAB_REPO>/forensics/team/SCOUT/loop_day_20261105/learning_series/drills_v2/hunter/H05/OUT/<your id>.md with one block per split (SPLIT_1 ... SPLIT_6), each exactly:
## SPLIT_n
- separates: yes or no (rule: gap between the highest and lowest state t >= 2.5, same sign at 15 min and 1 h)
- gap and its t: <numbers>
- gap needed for t 2.5 at these waves: <number> (2.5 x sqrt(se_high^2 + se_low^2))
- explanation in one line (works when ... because ...; or "no separation at this power")
- next action: one of: carry to round 3 / split the broad parent alarm / combine with another reading (name it) / drop, with one line why
- anything suspicious: one line or "none"
Then one block "## OVERALL": what round 2 learned about alarm A and alarm B in 3 lines, and what is MISSING to explain better (tools, readings, data) in up to 3 lines.
Max 12 tool calls, 8 minutes.
