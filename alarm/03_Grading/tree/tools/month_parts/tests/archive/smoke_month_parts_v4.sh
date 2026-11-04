#!/bin/bash
# smoke_month_parts_v4.sh (SCOUT 30 Oct 2026; TEST, NOT REVIEWED): the first run of the 26-part chain on the Mac. Review 2 (delta,
# 29 Oct 23:30Z): "The 26-part code has never run on the Mac": smoke v1 and v2 used 8 parts or called detect directly, smoke v3 ran
# single coin lists. This runs the chain's OWN block, alarm_grade_chain_v2_2_to20260430.sh from line 1 to its first line "fi" (pins,
# env, the PARTS guard, the slicer, the detect calls, the merge and the fire list; nothing after the list), with PARTS=26, twice, for LG4:
#  S1 Sep-Dec: a copy whose window line says LAST=20251231 (no other change; the diff is printed): its fire list must be byte-equal
#     to the GRADE list (receipts/20264037_GRADE_LIQGAP/LG4_FIRES_V1_LIST.tsv, 97635b1e0f18a17a, 7717 rows).
#  S2 Sep-Apr: the block as it is: each part's status, peak memory (cap 2147483648 bytes), seconds, and the sha16 of its data sources
#     and of its code (one value each over the 26 parts = one data and one code version); its rows before 2026-01-01 must be
#     byte-equal to the GRADE list (the check SCOUT runs on every MONTH, sepdec_check.py).
# The block runs under `bash` from PATH, as the MONTH job calls the chain; both bash versions are printed (the Mac's is 3.2.57).
# Exit 0 when every check holds, 3 when one fails, 2 on a bad input. Never deletes.
#   bash smoke_month_parts_v4.sh <DEFINITION.json> <GRADE_LIST.tsv> <W on SCRATCH_DISK> <OUT on dev>
set -uo pipefail
DEF=$1; GL=$2; W=$3; OUT=$4
PY=<PYTHON>; F=<LAB_REPO>/forensics; R=$F/team/RESEARCH
CH=$R/tools/month_parts/alarm_grade_chain_v2_2_to20260430.sh; CAP=2147483648; JAN=1767225600
[ "$(shasum -a 256 $CH | cut -c1-16)" = c24bd949b32c8e24 ] || { echo "SHA_MISMATCH chain"; exit 2; }
[ "$(shasum -a 256 $DEF | cut -c1-16)" = 94c2d5188ef9d715 ] || { echo "SHA_MISMATCH definition"; exit 2; }
[ "$(shasum -a 256 $GL | cut -c1-16)" = 97635b1e0f18a17a ] || { echo "SHA_MISMATCH grade list"; exit 2; }
[ ! -e "$W" ] && [ ! -e "$OUT/S1.tsv" ] || { echo "USED W or OUT"; exit 2; }
mkdir -p "$W" "$OUT" || exit 2
echo "start $(date -u +%FT%TZ); this script under bash $BASH_VERSION; bash in PATH $(command -v bash): $(bash -c 'echo $BASH_VERSION')"
sed -n '1,/^fi$/p' $CH > $W/blk_sepapr.sh
sed 's/^FIRST=20250910; LAST=20260430 /FIRST=20250910; LAST=20251231 /' $W/blk_sepapr.sh > $W/blk_sepdec.sh
[ "$(tail -n 1 $W/blk_sepapr.sh)" = fi ] && [ "$(grep -c '^FIRST=20250910; LAST=20251231 ' $W/blk_sepdec.sh)" = 1 ] || { echo "BLOCK COPY FAILED"; exit 2; }
echo "block: lines 1 to $(grep -c '' $W/blk_sepapr.sh) of the chain (sha16 $(shasum -a 256 $W/blk_sepapr.sh | cut -c1-16)); the Sep-Dec copy differs in:"
diff $W/blk_sepapr.sh $W/blk_sepdec.sh
ok=1
# one row per part: letter, coins, rc, seconds (the block's STATUS file), status, worker peak, parent peak, events, data and code sha16
parts(){ $PY - "$1" <<'EOF'
import json, sys, os, hashlib, csv
W = sys.argv[1]
hs = lambda o: hashlib.sha256(json.dumps(o, sort_keys=True).encode()).hexdigest()[:16]
sec = {}
for r in csv.DictReader(open(os.path.join(W, 'STATUS_LG4.tsv')), delimiter='\t'):
    if r['step'].startswith('detect_'):
        sec[r['step'][7:]] = (r['rc'], r['seconds'])
print('part\tcoins\trc\tseconds\tstatus\tworker_peak_bytes\tparent_peak_bytes\tevents\tsources_sha16\tcode_sha16')
for h in sorted(sec):
    p = os.path.join(W, 'det_LG4_v1_%s' % h, 'DETECT_RUN.json')
    if os.path.exists(p):
        m = json.load(open(p)); mm = m.get('memory', {})
        wp = mm.get('worker_peak_rss_bytes'); wp = max(wp) if isinstance(wp, list) and wp else wp
        c = m.get('coins'); c = ','.join(c) if isinstance(c, list) else str(c)[:60]
        print('\t'.join(str(x) for x in (h, c, sec[h][0], sec[h][1], m.get('status'), wp, mm.get('parent_peak_rss_bytes'), m.get('events'),
                                         hs(m.get('sources')), hs(m.get('code_sha16')))))
    else:
        print('\t'.join((h, '-', sec[h][0], sec[h][1], 'NO_DETECT_RUN_JSON', '-', '-', '-', '-', '-')))
EOF
}
# S1 Sep-Dec
t0=$(date +%s); PARTS=26 bash $W/blk_sepdec.sh LG4 "$DEF" $W/sepdec < /dev/null > $W/sepdec.out 2>&1; r=$?
echo "S1 rc $r seconds $(( $(date +%s)-t0 ))"; tail -n 3 $W/sepdec.out
cp -n $W/sepdec/STATUS_LG4.tsv $OUT/S1_STATUS.tsv
parts $W/sepdec > $OUT/S1.tsv; cat $OUT/S1.tsv
L1=$W/sepdec/LG4_FIRES_V1_LIST.tsv
if [ $r -eq 0 ] && [ -f $L1 ]; then echo "S1 rows $(grep -c '' $L1) vs GRADE list rows $(grep -c '' $GL) (with the header)"
  if cmp -s $L1 $GL; then echo "S1 EXACT: byte-equal to the GRADE list"; else echo "S1 DIFFERENT"; diff $L1 $GL | head -20; ok=0; fi
else echo "S1 FAILED"; ok=0; fi
# S2 Sep-Apr
t0=$(date +%s); PARTS=26 bash $W/blk_sepapr.sh LG4 "$DEF" $W/sepapr < /dev/null > $W/sepapr.out 2>&1; r=$?
echo "S2 rc $r seconds $(( $(date +%s)-t0 ))"; tail -n 3 $W/sepapr.out
cp -n $W/sepapr/STATUS_LG4.tsv $OUT/S2_STATUS.tsv
parts $W/sepapr > $OUT/S2.tsv; cat $OUT/S2.tsv
n=$(tail -n +2 $OUT/S2.tsv | grep -c '')
bad=$(awk -F'\t' -v c=$CAP 'NR>1 && ($3!="0" || $5!="COMPLETE" || $6+0>=c)' $OUT/S2.tsv | grep -c '')
mx=$(awk -F'\t' 'NR>1 && $6+0>m {m=$6+0} END {printf "%d\n", m}' $OUT/S2.tsv)
nsrc=$(awk -F'\t' 'NR>1 {print $9}' $OUT/S2.tsv | sort -u | grep -c ''); ncode=$(awk -F'\t' 'NR>1 {print $10}' $OUT/S2.tsv | sort -u | grep -c '')
echo "S2 parts $n, failed or over the cap $bad, max worker peak $mx bytes (cap $CAP, margin $((CAP-mx)) bytes), data versions $nsrc, code versions $ncode"
[ $r -eq 0 ] && [ $n -eq 26 ] && [ $bad -eq 0 ] && [ $nsrc -eq 1 ] && [ $ncode -eq 1 ] || ok=0
L2=$W/sepapr/LG4_FIRES_V1_LIST.tsv
if [ $r -eq 0 ] && [ -f $L2 ]; then awk -F'\t' -v j=$JAN 'NR==1 || $2+0 < j' $L2 > $W/sepapr_sepdec.tsv
  echo "S2 rows $(grep -c '' $L2), before 2026-01-01 $(grep -c '' $W/sepapr_sepdec.tsv) vs GRADE list $(grep -c '' $GL) (with the header)"
  if cmp -s $W/sepapr_sepdec.tsv $GL; then echo "S2 SEP-DEC EXACT: byte-equal to the GRADE list"; else echo "S2 SEP-DEC DIFFERENT"; diff $W/sepapr_sepdec.tsv $GL | head -20; ok=0; fi
else echo "S2 FAILED"; ok=0; fi
echo "end $(date -u +%FT%TZ) ok $ok"
[ $ok -eq 1 ] && exit 0 || exit 3
