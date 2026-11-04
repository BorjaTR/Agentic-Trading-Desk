# REQUIREMENTS: tools/month_parts (SCOUT, 29 Oct 2026; revised after reviews 1 and 2). TEST, NOT REVIEWED.
R1 Same fire list as v2_1 for every definition: detection is per coin (review 1: no value is computed across the --coins list;
   refractory is per coin; event_id = sha16(def|coin|t|side)), parts are contiguous roster slices, the merge sorts rows by t
   (numeric) then coin, so the list (rows without '#') does not depend on the parts. PARTS=2 gives v2_1's halves exactly.
R2 Memory: every part of a Sep-Apr MONTH stays under the 2 GiB cap. LG4 measured: parts A to E of 8 1.81 to 1.89 GiB, part F refused
   at 2150924288 bytes, G and H not run (smoke 20264080); 1 or 2 coins 1.57 to 1.65 GiB, 3 of the 26 pairs (smoke 20264081): 26 parts
   of 2 coins. Proved for all 26 parts by smoke v4 S2 (job 20264083: 1.56 to 1.66 GiB, max 1780858880 bytes), then by every part's
   DETECT_RUN.json kept in the MONTH receipts (DETECT_MEM_<V>.tsv).
R3 PARTS from 2 to 26, default 26; anything else stops the chain (BAD_PARTS, exit 2); an empty part stops it (EMPTY_PART, exit 3); a
   part's detect refusal stops it (exit 3), as in v2_1.
R4 Every other line of v2_1 unchanged: pins (detect, grade, outcomes, card, windows, release), window 20250910 to 20260430, steps 2 to 7.
R5 Tests in about 2 minutes on the chain's own text (tests/test_month_parts_v1.py), every planted bug caught; never deletes; writes only under <W>.
R6 Exactness on lab data before the full run (smoke v1 S2 with 8 parts; smoke v4 S1 with 26): the chain's own block with LAST=20251231 gives a list
   byte-equal to the GRADE job's kept list (LG4: receipts/20264037_GRADE_LIQGAP/LG4_FIRES_V1_LIST.tsv 97635b1e0f18a17a). After the full
   run, the MONTH list's rows with t < 1767225600 (2026-01-01) must equal the same reference, checked by SCOUT before its CLEAN (the
   MONTH job keeps <V>_FIRES_V1_LIST.tsv in its receipts). Smoke 20264079 S2 (8 parts): EXACT, byte-equal (7717 rows, 97635b1e0f18a17a).
R7 Data versions (review 1 delta): parts run one after another (about 4 min for 26), so SCOUT checks that every day/part key has one
   sha16 across the parts' DETECT_RUN.json sources and that code_sha16 matches (a lab change mid-job would mix data). The wired MONTH
   job writes each part's sha16 of its sources and of its code_sha16 into DETECT_MEM_<V>.tsv (columns 5 and 6: one value each = one
   data and one code version); smoke v4 S2 checks the same (smoke 20264081: 4 parts, one value each).
