Written by SCOUT for the repo on 30 Oct 2026 from tree/tools/month_parts/BASELINE.tsv, README.md, ARCHITECTURE.md ("Versions"), the chain's
header and ../Agentic/tree/ALARM_DESIGN/KIT_V5/MANIFEST_SHA16.txt (line 2); not the owner's document (owner seat: SCOUT).

# CHANGELOG: month_parts, the grade chain v2_2 (newest first)

The dev tree has no CHANGELOG for this tool. Its release record is `BASELINE.tsv` (58c62fa609ed216d): each file's sha16, both reviews
and the test receipts. Its own files still say "TEST, NOT REVIEWED until BASELINE.tsv shows 2 PASS"; BASELINE.tsv shows both.

| when (UTC) | what changed | why | source |
|---|---|---|---|
| 30 Oct 00:24 | released: review 2 final PASS | the smoke v4 receipts (job 20264083): 26 parts on the Mac, every part under the 2 GiB cap (max 1780858880 bytes), one data and one code version, Sep-Dec rows byte-equal to the GRADE list; ok 1, rc 0 | BASELINE.tsv, column review_2 |
| 30 Oct 00:23:54 | the KIT_V5 MONTH job runs this chain with PARTS=26 (template f19e13c55a2aa283, kit manifest 76b46b91edeffc3c) | wired only after smoke v4 and both reviews (review 1B PASS 23:58Z on the template) | BASELINE.tsv, last row; KIT_V5 MANIFEST_SHA16.txt line 2 |
| 29 Oct 23:43:27 | README, SCOPE, REQUIREMENTS, ARCHITECTURE: doc fixes | review 2 (delta) asked for them | BASELINE.tsv, column landed_utc |
| 29 Oct 23:37:49 | new: tests/smoke_month_parts_v4.sh (c80482579635c0a2) | review 2 (delta FAIL 23:43Z): the 26-part code had never run on the Mac's bash 3.2.57 | BASELINE.tsv |
| 29 Oct 23:17:48 | chain 583672d036d2ad85: detection in 26 parts of 2 coins (PARTS 2 to 26, default 26); tests: 19 of 19 planted bugs caught | over Sep-Apr an eighth of the roster still hit the cap (part F refused at 2150924288 bytes, smoke 20264080); 1 or 2 coins peaked 1.57 to 1.65 GiB (smoke 20264081) | BASELINE.tsv; README.md |
| 29 Oct 23:08-23:09 | the 8-part version: review 1 PASS 23:08Z, review 2 PASS 23:09Z | review 1's memory model: a per-day index cache (about 6.6 MB a day) plus a share that grows with the coins; parts cut only the coin share | BASELINE.tsv; ARCHITECTURE.md "Memory" |
| 29 Oct, before 22:57 | first draft: v2_1 with the detection in 4 parts | detect_aw1.py refused AD13 LIQGAP LG4 at its 2 GiB worker cap over Sep-Apr (MONTH jobs 20264053, 20264064); the owner: an alarm counts as FOUND only when its Jan-Apr MONTH holds | README.md; ARCHITECTURE.md "Versions"; the twin alarm_grade_chain_v2_2_to20260430.sh.pre_SCOUT_20261029T225650Z in the dev tree |

Base: `team/RESEARCH/tools/alarm_process/alarm_grade_chain_v2_1_to20260430.sh` (99e8a229617cb2e2, STRATEGY 28 Oct): every line but step 1
is unchanged (REQUIREMENTS R4). It is a TEST edition, not in the repo (part README, "In development").

Small runs on the Mac (runner jobs, AD13 LIQGAP LG4; BASELINE.tsv and README.md): v1 job 20264079 (Sep-Dec in 8 parts byte-equal to the
GRADE list, 7717 rows, 97635b1e0f18a17a); v2 job 20264080 (parts A-E 1.81-1.89 GiB, F refused; a Jan-Apr window alone is not exact: 1 of
522 rows moved); v3 job 20264081 (1 or 2 coins, 1.57-1.65 GiB); v4 job 20264083 (above). Receipts: `team/RESEARCH/tools/month_parts/receipts/`.
