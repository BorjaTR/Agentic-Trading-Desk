# 04 Month check: what changed (newest first)

| when (UTC) | what changed | source |
|---|---|---|
| 30 Oct, 13:0x | the kit (MONTH job, queue, forward-only decision, tests, fixtures, harness) moved from this part to Alarm/Agentic; this part keeps documents only | SCOUT's task; the owner, 30 Oct 13:5x Berlin |
| 30 Oct 00:23:54 | `JOB_MONTH_V5` f19e13c55a2aa283 (was 6b656ab71ff5c5e5): the Sep-Apr grade runs chain v2_2 in 26 coin parts (was v2_1 in 2 halves), each part's memory and data and code sha16 kept; `queue_job_v4.py` dccce8e5e119fe48 pins it. Why: detect_aw1.py refused at its 2 GiB cap over Sep-Apr (MONTH jobs 20264053, 20264064). Review 1B PASS and review 2 PASS on 468b38fbfca1b13d; the deployed file differs only in its comment line 1 | 03_Grading BASELINE.tsv last row; kit MANIFEST_SHA16.txt line 2 |
| 29 Oct 21:11:42 | `queue_job_v4.py` MONTH `--forward-only`; new `decide_forward_v1.py` (b6c153cf4b304bf9) | the owner 29 Oct 22:02 Berlin; kit MANIFEST_SHA16.txt |
| 29 Oct 14:18:33 | the kit's first manifest, with the MONTH kind | kit README |

The kit's whole history: [../Agentic/KIT_V5/CHANGELOG.md](../Agentic/KIT_V5/CHANGELOG.md).
