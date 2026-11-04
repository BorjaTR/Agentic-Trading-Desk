# RUN <RUN> (ALARM_DESIGN KIT_V5, run template TEMPLATE_V4). TEST, NOT REVIEWED.
Copied from <INSTALL>/Agentic/tree/ALARM_DESIGN/KIT_V5/runs/TEMPLATE_V4 with cp -R -n. New edition by SCOUT helper K13 for ALARM_V1_5
(31 Oct 2026): TEMPLATE_V3's README_RUN.md (3f1e3fb46430a5c5) named past editions; the 8 registers are TEMPLATE_V3's, byte for byte.
Read <INSTALL>/AGENTS.md first: where this file and AGENTS.md differ, AGENTS.md wins. Your board: hb/<SEAT>.txt, one line per event.

## The tools (paths under <INSTALL>/Agentic/tree/ALARM_DESIGN/ unless named; each takes --settings; each has a card in <INSTALL>/cards/)
- Queue a job (COUNT, GRADE, ENTRY, MONTH, CLEAN; --dry first): KIT_V5/tools/queue_job_v5.py. It writes RUNS and jobs/.
- Decide a variant: KIT_V5/tools/decide_v2.py (--write records it in DECISIONS); a STOP's other side: KIT_V5/tools/decide_forward_v2.py.
- Every other register: runs/CLAUDE1_20261028/tools/reg_append_v1.py (example at the end).
- Check the run: KIT_V5/tools/audit_run_v3.py (--write at each checkpoint and before DONE); time per step: KIT_V6/tools/idea_time_v2.py;
  board lines: KIT_V5/tools/board_line_v2.py.
- New or a copy: <INSTALL>/08_Registry/tree/ALARM_DESIGN/REGISTRY/tools/novelty_v2.py, on the GRADE job's fire list.
- The definition: <INSTALL>/01_Detection/tree/team/RESEARCH/ALARM_DESIGN/KIT_V2/templates/DEF_TEMPLATE_V4.json (DEF_TEMPLATE_V4.md explains
  every field and rule). The card, which is the prereg: KIT_V6/templates/CARD_V7.md. The report: KIT_V6/templates/REPORT_V6.md.

## What a run holds (as round 7's runs did)
- registers/   8 registers, append-only: RUNS (queue_job_v5), DECISIONS (decide_v2 --write), the other 6 only with reg_append_v1.py.
- ideas/<IDEA>/   CARD_<IDEA>.md (the prereg, from CARD_V7.md), defs/<V>.json, hc/ (hand check and memory probe prints),
  FINDINGS_<IDEA>.md, and the prints you keep (dry runs, metric briefs, DECIDE_<V>.txt).
- jobs/        job twins, written by queue_job_v5.py only.
- receipts/<JOB>/   written by each job: STAGES.tsv (every stage with its rc; an end line when done), SHA16.txt, DISK.tsv and the job's
  outputs (COUNT: COUNT_<V>.tsv, FIRST20_<V>.tsv; GRADE: STATUS_<V>.tsv, <V>_FIRES_V1_LIST.tsv, the card and the hand-off).
- audit/       AUDIT_<stamp>.txt from audit_run_v3.py --write; the idea_time_v2.py prints.
- REPORT.md    at the end, from REPORT_V6.md.

## Seal before any GRADE
The card file is the prereg. One VARIANTS row per variant: def_rel = ideas/<IDEA>/defs/<V>.json, def_sha16, prereg_rel =
ideas/<IDEA>/CARD_<IDEA>.md, prereg_sha16. The queue refuses a GRADE of a variant with no VARIANTS row.

## Register columns (copy them exactly; the first column is the stamp, filled from the clock)
- VARIANTS: idea, V, lean (FADE or FOLLOW: the lean lives only here, never in the definition's fire.side), def_rel, def_sha16,
  prereg_rel, prereg_sha16, reason.
- FORECASTS (optional for COUNT, GRADE and ENTRY; audit_run_v3 A5 asks for the four Jan-Apr rows before a MONTH job): idea, V, scope (2601, 2602, 2603 or 2604), gap15_lo, gap15_hi, gap1h_lo, gap1h_hi
  (numbers), file_rel, file_sha16, note.
- POSTMORTEMS: idea, V, job, scope (COUNT, SEPDEC, ENTRY or a month), forecast, result, result_file, result_sha16, why, unexplained.
- LEARNINGS_PROPOSED: id, kind (RULE, TOOL, CHECK or SKILL), section, change, evidence_file, evidence_sha16, scope, status.
- PROBLEMS: kind, where, what_is_wrong, evidence, severity (STOP, HIGH or LOW), action, proposed_fix, reported_to_lead.
- TOOLS_BUILT: tool_rel, sha16, range, test_rel, test_sha16, why.
- RUNS (queue_job_v5) and DECISIONS (decide_v2): never by hand.
Example: echo '{"idea":"FLOWX","V":"FX1","lean":"FADE","def_rel":"ideas/FLOWX/defs/FX1.json","def_sha16":"...","prereg_rel":"ideas/FLOWX/CARD_FLOWX.md","prereg_sha16":"...","reason":"first variant"}' | python3 -B <INSTALL>/Agentic/tree/ALARM_DESIGN/runs/CLAUDE1_20261028/tools/reg_append_v1.py <RUN folder> VARIANTS -
