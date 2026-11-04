# novelty_v3: tool card

novelty_v2 plus two things (SCOUT, 1 Nov 2026, ALARM_V1_16; why: team/RESEARCH/plans/PLAN_SCOUT_TOOLS_V1_16_20261101.md). The code:
[novelty_v3.py](../08_Registry/tree/ALARM_DESIGN/REGISTRY/tools/novelty_v3.py). Everything else, the measures, the columns and the
refusals: [novelty_v2.md](novelty_v2.md). Status in the code: TEST, NOT REVIEWED.

## What changed from v2
- NEAR also when a registry alarm's waves near minus its baseline is 40 points or more. The baseline is the chance level of waves
  near (the share of that alarm's span within 1800 s of one of its fires): a dense alarm is near everything by chance, so waves near
  alone says little. This is event coincidence analysis (Donges et al. 2016): a coincidence rate read against its expected rate.
- Each nearest line ends with `excess <points> pts` (waves near minus baseline).
- `--show <ALARM_ID>` prints one more line, `show: ...`, for the alarm you name (your sibling), wherever it ranks.

## Run it
```
python3 -B <INSTALL>/08_Registry/tree/ALARM_DESIGN/REGISTRY/tools/novelty_v3.py --settings <S> <FIRE_LIST.tsv> --lean FADE --self <SEAT>_<IDEA> [--show <ALARM_ID>]
```
- Real output (SCOUT's VM, 1 Nov 2026, SIDEDHOUR V1, GRADE 20265495 fire list 50b13f884c63ad7f): 4643 fires, 1319 waves against 108
  alarms; `show: AD2_OIFLUSH_OF1 (OWN, PASS, lean FADE): ... waves near 81.0 pct (its baseline 71.3 pct); excess 9.7 pts`, then
  `VERDICT NEW: every overlap under 40 pct and every excess under 40 pts`.
- Exit 0 done; 2 refused (v2's refusals, and a --show alarm with no fire list in the registry).
