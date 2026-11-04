# SCOPE: tools/month_parts (SCOUT, 29 Oct 2026). TEST, NOT REVIEWED.
In: the Sep-Apr grade chain called by the ALARM_DESIGN KIT_V5 MONTH job (Jan-Apr forward months of PASS, NEEDS MORE MONTHS and
forward-only variants), split into coin parts so each detect stays under the 2 GiB worker cap; the wiring of the KIT_V5 MONTH job
template to it (pin the live chain sha16 in BASELINE.tsv, PARTS=26, each part's DETECT_RUN.json memory and the MONTH fire list copied
to the receipts) and queue_job_v4.py's template sha16; the small runs (tests/smoke_month_parts_v1.sh to v4.sh) before the first
full MONTH.
Out: detect_aw1.py and every released or pinned tool it calls (unchanged); the COUNT, GRADE and ENTRY chains; any other window; the
outcome readers (month_read_v3.py); deciding anything.
