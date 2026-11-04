---
description: Set the desk up on this machine and this data - install check, trading style, data and register, fit, GO / GO WITH GAPS / STOP
argument-hint: [path to the data folder, optional]
---

Set up the Crypto Alarm Desk in this repo. Data folder given: $ARGUMENTS (if empty, read DATA_ROOT from settings/desk.env, or ask).

Load the desk-setup skill and follow its steps in order: install, trading style (ask one question at a time), data and register, fit
and minimums, end. At the data step, when the user's data is not yet in the one format, follow `docs/CONVERT_YOUR_DATA_V2.md` (the
format and its sources: `docs/DATA_FORMAT_V2.md`): the desk ships these instructions, not a converter. Never write inside the data
folder (a conversion writes only a new folder, with the desk's yes) and never download anything without the desk's yes. Report any tool
refusal word for word. Write the report to OUTPUT_ROOT/setup/SETUP_REPORT_<UTC stamp>.md and finish with one line: GO, GO WITH GAPS (each gap named)
or STOP (what is missing and what would fix it). On GO, say that `/new-alarm <idea>` is the next step.
