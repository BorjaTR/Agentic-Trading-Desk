# wave_gap_v1: tool card

Why COUNT's waves exceed the graded waves, from a GRADE's own files. Released in ALARM_V1_19; status TEST. The code: [wave_gap_v1.py](../Agentic/tree/ALARM_DESIGN/KIT_V5/tools/wave_gap_v1.py). The answer on 4 GRADEs: [WAVE_GAP_ANSWER_V1.md](../playbook/WAVE_GAP_ANSWER_V1.md).

## Run it
```
$PY -B <INSTALL>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/wave_gap_v1.py <W> <V> --real <RUN>/receipts/<GRADE>/HANDOFF/REAL_SEALED/REAL_<V>.tsv
```
<W> is the GRADE's work folder, named in FIRES.tsv. It reads PERFIRE_<V>.tsv, gradeL_<V>_v1/matches/EDGES.tsv and CENSUS.tsv and REAL_<V>.tsv; it writes nothing and opens no market file.

## Exits
0 equal to REAL; 3 not equal; 2 refused (a file is missing).
