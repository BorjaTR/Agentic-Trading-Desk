# alarm_match: tool card

The matched-moment baseline: for each parent, moments of the same coin (within 7 days, UTC hour +-1, same split part) with similar activity and no alarm available at that time. The code: [draw_v3.py](../07_Price_path/tree/tools/alarm_match/draw_v3.py) (QUANT). The folder's README describes match_events.py, which is not in this folder. The loop's GRADE draws its random with make_random, not with this.
Read from the code and README for ALARM_V1_19 (SCOUT helper, 2 Nov 2026); not run for this card. Status in the code: TEST, unless it says otherwise.

## Run it
```
python3 -B <INSTALL>/07_Price_path/tree/tools/alarm_match/draw_v3.py <parents.tsv> <alarms.tsv> <lab_days> <out_dir> <first> <last>
```
- No usage check: 6 positional arguments. Writes MANIFEST_V3.json and its lists in out_dir, prints one DRAW V3 line.
