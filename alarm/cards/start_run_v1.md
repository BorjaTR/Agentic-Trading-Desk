# start_run_v1: tool card

Starts your run folder from the kit's run template, writable by you. Released in ALARM_V1_21 (V1_21 fixes, run SCOUTR12_20261103); TEST, NOT REVIEWED.
Why: AGENTS.md said `cp -R -n <INSTALL>/.../TEMPLATE_V4 <run>`; cp keeps the install's read-only modes, so the run folder could not be written (run SCOUTR12_20261103, PROBLEMS row 1).
Code: [start_run_v1.py](../Agentic/tree/ALARM_DESIGN/KIT_V5/tools/start_run_v1.py).
```
python3 -B <INSTALL>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/start_run_v1.py --settings <S> <RUN> [--dry]
```
- RUN: `<SEAT>_<YYYYMMDD>`, SEAT a capital letter then capitals and digits, at most 12, no underscore; the date a real day. A refused tag prints the tag to use when one can be made (SCOUT_R12_20261103: write SCOUTR12_20261103).
- Writes only RESEARCH_ROOT/ALARM_DESIGN/runs/<RUN>/: README_RUN.md and the 8 registers, byte for byte (sha16 checked), folders 0755, files 0644. Reads the template; never writes, chmods or opens for writing anything in the install.
- Refused (exit 2, `REFUSED: why`): a bad tag, a folder that exists (never merged), a run folder inside the Alarm folder, a template that lacks a register, no runs folder. Exit 0 STARTED.
