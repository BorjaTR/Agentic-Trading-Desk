# money_direction: tool card

md_v1 holds the waves, months, costs and table reader that the first look reader imports, and the older MD test: does the lean side get a raw move of a useful size, month after month. Raw move, not money. The code: [md_v1.py](../06_First_look/tree/tools/money_direction/md_v1.py). The MD test's 15 min waves are not the grade's 30 min waves: for an alarm's answer use first look.
Read from the code and README for ALARM_V1_19 (SCOUT helper, 2 Nov 2026); not run for this card. Status in the code: TEST, unless it says otherwise.

## Run it
```
python3 -B <INSTALL>/06_First_look/tree/tools/money_direction/md_v1.py batch <targets> <costs> <out> <result dirs...>
python3 -B <INSTALL>/06_First_look/tree/tools/money_direction/md_v1.py null <post> <costs> <seeds> <out>
```
- Exit 2 `REFUSED` with USAGE, OUT EXISTS and table errors.
