# RUN <RUN> (ALARM_DESIGN KIT_V5). TEST, NOT REVIEWED.
Copied from KIT_V5/runs/TEMPLATE_V3 with cp -R -n. Your skill: KIT_V5/skills/alarm-design-v5/SKILL.md. Your board: hb/<SEAT>.txt.
- registers/   8 registers, append-only, written only with reg_append_v1.py (RUNS by queue_job_v4.py, DECISIONS by decide_v1.py).
- ideas/<IDEA>/   IDEA_CARD.md, ALARM_CARD.md, defs/<V>.json, PREREG_<IDEA>.md, FORECAST_<IDEA>_<V>.md, FINDINGS_<IDEA>.md.
- jobs/        job twins, written by queue_job_v4.py only.
- receipts/<JOB>/   copied by each job: STAGES.tsv (every stage with rc), SHA16.txt, DISK.tsv and the job's text outputs.
- audit/       AUDIT_<stamp>.txt from audit_run_v2.py --write.
- REPORT.md    at the end (KIT_V5/templates/REPORT_V5.md).
Register columns (copy them exactly; the first column is the stamp, filled from the clock):
- VARIANTS: idea, V, lean (FADE or FOLLOW), def_rel (ideas/<IDEA>/defs/<V>.json), def_sha16, prereg_rel, prereg_sha16, reason.
- FORECASTS: idea, V, scope (2601, 2602, 2603 or 2604), gap15_lo, gap15_hi, gap1h_lo, gap1h_hi (numbers), file_rel, file_sha16, note.
- POSTMORTEMS: idea, V, job, scope (COUNT, SEPDEC, ENTRY or a month), forecast, result, result_file, result_sha16, why, unexplained.
- LEARNINGS_PROPOSED: id, kind (RULE, TOOL, CHECK or SKILL), section, change, evidence_file, evidence_sha16, scope, status.
- PROBLEMS: kind, where, what_is_wrong, evidence, severity (STOP, HIGH or LOW), action, proposed_fix, reported_to_lead.
- TOOLS_BUILT: tool_rel, sha16, range, test_rel, test_sha16, why.
Example: echo '{"idea":"FLOWX","V":"FX1","lean":"FADE","def_rel":"ideas/FLOWX/defs/FX1.json","def_sha16":"...","prereg_rel":"ideas/FLOWX/PREREG_FLOWX.md","prereg_sha16":"...","reason":"first variant"}' | python3 -B <T>/reg_append_v1.py <RUN folder> VARIANTS -
