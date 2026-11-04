# novelty_v5: tool card

Released in ALARM_V1_21_10; TEST, NOT REVIEWED. novelty_v4 plus `--show-lean` for a registry alarm id: `--show <ALARM_ID> --show-lean FOLLOW`
compares that alarm's fires with the lean you give instead of its registry lean, and the show line names both (`<ALARM_ID> with lean FOLLOW
(registry lean FADE)`). novelty_v4 refused it with "--show-lean IS ONLY FOR --show <fire list path>" (desk trial DESKA02, PROCESS ask, 3 Nov).
A shown alarm never enters the verdict or the nearest lines. `--show-lean` without `--show` is refused and says what to add. Nothing else
changed. The code: [novelty_v5.py](../08_Registry/tree/ALARM_DESIGN/REGISTRY/tools/novelty_v5.py). The rest: [novelty_v4](novelty_v4.md), [novelty_v3](novelty_v3.md).

## Run it
```
python3 -B <INSTALL>/08_Registry/tree/ALARM_DESIGN/REGISTRY/tools/novelty_v5.py --settings <S> <FIRE_LIST.tsv> --lean FADE --self <SEAT>_<IDEA> [--show <ALARM_ID or fire list path> [--show-lean FADE|FOLLOW]]
```
- novelty_v4's exits and refusals otherwise. Tests: tests/test_novelty_v5.py (8; 2 of them fail on novelty_v4).
