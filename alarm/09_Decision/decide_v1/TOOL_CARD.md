# decide_v1 (ALARM_V1_19): tool card

Per fire, TAKE or SKIP with a reason, from frozen cards and a rulebook. A money-stage tool: it does not give the alarm's PASS or STOP, which is the decide tool of the kit (AGENTS.md step 7). It never reads a price. The code: tree/team/RESEARCH/tools/decide_v1/decide_v1.py (release DECIDE_V1_0_1). More: README.md beside this card. This card is here, not in cards/, because the name decide_v1 is the kit tool decide's there.
Read from the code and README for ALARM_V1_19 (SCOUT helper, 2 Nov 2026); not run for this card. Status in the code: TEST, unless it says otherwise.

## Run it
```
python3 -B <INSTALL>/09_Decision/tree/team/RESEARCH/tools/decide_v1/decide_v1.py --universe U --alarm-id A --first F --last L --research-window W --rulebook R --safety S --ctx-cards C --prof-cards P --pmm-cards M --lab-tools T --admitted AD --root ROOT --out OUT --mode <mode> [--coins C] [--volumes-root V]
```
- Every refusal: `REFUSED <CODE>: why` on stderr, exit 2, before any output (includes RULEBOOK_INVALID, BAD_INPUT_FILE). All flags above without brackets are required.
