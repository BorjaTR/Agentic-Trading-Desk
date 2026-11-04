# 03 Grading: what changed in each release (newest first)

Sources: `tree/tools/month_parts/BASELINE.tsv` (the release record of chain v2_2: each file's sha16, both reviews, the test receipts) and
the kit's `MANIFEST_SHA16.txt` (in `../Agentic/tree/ALARM_DESIGN/KIT_V5/`). The tool's own CHANGELOG has the detail:
[month_parts/CHANGELOG.md](month_parts/CHANGELOG.md).

## month_parts: the grade chain v2_2 (owner SCOUT)
| release | when (UTC), by | what changed and why |
|---|---|---|
| v2_2, 26 parts (583672d036d2ad85) | landed 29 Oct 23:17:48 (SCOUT); review 1 delta PASS; review 2 final PASS 30 Oct 00:24 | v2_1 with the detection in 26 coin parts of 2 coins: over Sep-Apr detect_aw1.py hit its 2 GiB worker cap for AD13 LIQGAP LG4 (MONTH jobs 20264053, 20264064); an eighth still hit it (smoke 20264080); all 26 parts measured on the Mac at most 1780858880 bytes, Sep-Dec rows byte-equal to the GRADE list (smoke v4, job 20264083). Docs fixed 23:43:27; MONTH job wired 30 Oct 00:23:54 |
| v2_2, 8 parts | 29 Oct, review 1 PASS 23:08, review 2 PASS 23:09 | the first reviewed version (not kept: replaced by 26 parts the same night) |

## The GRADE job (KIT_V5)
Since 30 Oct the alarm kit, with its GRADE job template (a520be2650b27910, unchanged since 29 Oct 13:51), is in
[../Agentic](../Agentic): its history is [../Agentic/KIT_V5/CHANGELOG.md](../Agentic/KIT_V5/CHANGELOG.md).

Not released, so not here: chains v2_0 and v2_1, the card, the aw1 step tools, matched random, the menu and the per-fire file
([README.md](README.md), "In development").
