Written by SCOUT for the repo on 30 Oct 2026 from README.md, README_V3.md, README_V3_2.md, ARCHITECTURE.md, INTERFACE_V1.md and tree/tools/idea_to_grade/RELEASE_idea_to_grade_V3_2.json; not the owner's document (owner seat: STRATEGY/LEAD, per idea_to_grade.py; V3 to V3.2 built by the ALARMLIB seat).

# idea_to_grade: scope (edition V3.2, the released one)

## Purpose and user
- The question (ARCHITECTURE.md section 1): after the alarms of one idea, how often and how fast does the price move in the chosen
  direction, how much does it first go against you, and how does that compare with matched moments of the same coin where nothing fired?
- Users: STRATEGY and LEAD grade alarms with it. In the alarm pipeline it is the price path's store run: STRATEGY's markout re-reads a
  V3.2 run folder (the markout is a TEST edition, not here).

## In scope
- Input: a registered alarm's event list pinned by its sha16 (--events, --events-sha16), or a registered idea definition (--idea, fresh
  detection by detect.py); a coin selector (all roster coins, a set, a group); --first/--last days; a research window of BUILD months.
- Matched calm moments per fire (as of the fire: no alarm or parent of the coin in the 4 h before), and up to 10 TOUGH moments per fire
  (same coin, same signed 15 min move and 5 min volatility).
- One fixed grid for every alarm: returns at 10 s, 1, 5, 15 min, 1 h, 4 h after the fill; eight exits; three entry types (TT taker,
  RT resting entry, RR resting entry and target); costs per coin (one static number from the cost table) at an honest and a stress gap,
  and GROSS.
- Each event counted once: wave weights from a frozen universe (--universe); 95% intervals with the cluster as the unit; per month.
- Admission and records: the tries ledger ask (--ledger-ask), the registry id (--alarm-id), every input pinned by sha16 and rechecked
  before publishing; one run folder published at once, RUN.json last.

## Out of scope
- Money: which fires to take, exits chosen per alarm, size. The grade describes opportunity only; no profit claim, no cause, no trade.
- Months outside BUILD (WINDOWS_V1): refused. Never May 2026 onward.
- Building or editing the universe, the registry or the ledger (read only; the universe is built before by i2g_universe_v1.py).
- A cost as of the entry time (costs are one number per coin).

## What success means
- A run ends COMPLETE and VERIFIED (idea_to_grade_v3_2.verify_run): every file listed with its sha16 in RUN.json, inputs unchanged.
- run_class GRADED only with the canonical ledger and registry, a universe and no compatibility mode; anything else is TEST.
- The release bar (RELEASE_idea_to_grade_V3_2.json): pure tests 26 of 26, mutants 43 of 43 killed, real-data tests 13 passed on the
  Mac, the full population of ALM_M_V1 (52 coins, Sep-Dec 2025, 10,764 parents) COMPLETE and verified in 421 s (tree peak 4.16 GB), the
  external review's regression cases PASSED.
