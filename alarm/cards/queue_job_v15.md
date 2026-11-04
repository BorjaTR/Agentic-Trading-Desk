# queue_job_v15: tool card

queue_job_v14 plus KIND TRUE (AGENTS.md step 5c), nothing else: COUNT, GRADE, ENTRY, MONTH and FIRSTLOOK run the same templates with the same checks ([queue_job_v14.md](queue_job_v14.md)). A bad run tag now says the seat rule. Released in ALARM_V1_21 (V1_21 fixes, run SCOUTR12_20261103); TEST, NOT REVIEWED.
Code: [queue_job_v15.py](../Agentic/tree/ALARM_DESIGN/KIT_V5/tools/queue_job_v15.py); job: KIT_V5/jobs/JOB_TRUE_V1.job.sh.txt.
```
python3 -B <INSTALL>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/queue_job_v15.py --settings <S> [--job-settings <MAC S>] <RUN> TRUE <IDEA> <V>=ideas/<IDEA>/TRUE_<V>_<LABEL>.json --from-job <NUM>_GRADE_<IDEA> [--dry]
```
- Same claim file, twin (jobs/, opened 'x') and RUNS row (reg_append_v1) as every kind, so audit A16 passes. The job pins true_gate_v1/v2/v3 and the claim by sha16, runs `true_gate_v3.py check`, then `run` into receipts/<JOB>/TRUE_<V>_<LABEL>/, writes STAGES.tsv (check_<V>, true_<V>, end), PEAKS.tsv and SHA16.txt. WRITES_MB 50, MEM_MB 3000 (declared; measured in playground job 20267324: peak 1230 MB, 29 s, so the next edition can set 1476 = peak + 20 pct), 10 declared minutes.
- Refused before any number is claimed: a claim not named ideas/<IDEA>/TRUE_<V>_<LABEL>.json or not JSON; NO GOOD GRADE (grade_, perfire_, perfire_test_<V> rc 0); the GRADE not in RUNS or its twin not pinning this definition and lean; `TRUE CLAIM ...: <field> IS ..., MUST BE ...` for idea, V, lean, def_sha16, def (as the runner sees it), lab_days (of --job-settings), perfire (as the runner sees it), perfire_sha16 (the variant's row of PERFIRE_SEAL.tsv); TRUE LABEL NOT SEALED (the card lacks the true_label= or true_mirror= digest); SOURCE SEAL LOST, NO SOURCE SEAL (a GRADE before JOB_GRADE_V14), SOURCE DIGEST (the PERFIRE there now differs: swept or changed); ALREADY TRUE (a TRUE job of this variant from this GRADE queued, running or ended well; a failed one may run again). Each refusal prints a NEXT line.
- After the job: write one POSTMORTEMS row naming it (audit A7).

ALARM_V1_21_4: `--from-job` takes the GRADE job's receipts folder name, `<NUM>_GRADE_<IDEA>` (e.g. `20267780_GRADE_WINDFALL`), not a bare job number; use the full GRADE receipts folder name even after the job finishes. A queue that resolves a bare number is for a later edition.
