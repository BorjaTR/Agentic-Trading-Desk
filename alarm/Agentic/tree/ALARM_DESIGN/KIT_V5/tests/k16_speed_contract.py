"""k16_speed_contract.py (SCOUT K16, 31 Oct 2026; TEST, NOT REVIEWED): the contract of the V1_7 speed editions, K16 T5, T6 and T8
(SCOUT 31 Oct, after the reviews REV1 and REV2; team/SCOUT/K16/SPEED_ASSESSMENT_V1.md). Each new file is its V1_6 parent with only the
edits below. A text edit (old, new, n) needs old found exactly n times. A span edit ('SPAN', head, tail, sha16, new) replaces the lines
from the line that starts with head to the first line after it equal to tail, and needs that span's sha16. <<SHA16:<path>>> in a new
text is the sha16 of that new file (a later file pins an earlier one). build(root) remakes the seven files from their parents under
root (a V1_6 package, or the staging folder K12_FEEDGATE_V1); test_k16_speed_v1.py C1 checks them against the package byte for byte.
  T5  alarm_grade_chain_v2_0_4_to20251231.sh: v2_0_3 with Outcomes in 3 worker processes (run 3), GRADE only
  T6  alarm_grade_chain_v2_2_4_to20260430.sh: v2_2_3 with the detection parts by the chain's rule (2, or 26 up front for a SERIAL_FORCED
      definition), a part refused with WORKER_RSS_CAP re-split alone into new folders, a coin census before the merge, LC_ALL=C
  T8  JOB_GRADE_V9 and JOB_MONTH_V9: one du at the end; both declare 3 cores; JOB_MONTH_V9 sets no part count (PARTS empty)
      queue_job_v7.py: the V9 templates, MONTH's MEM_MB 4030 (the measured peak + 20 percent)
      test_job_grade_v9.py and test_job_month_v9.py: K12's V8 tests for V9, with the new checks and their planted bugs
  SCOUT (31 Oct; the owner 10:51 Berlin: CLEAN removed): queue_job_v7.py also refuses KIND CLEAN (in no table), counts a finished job's
      scratch in the disk budget only while its folder is on SCRATCH_DISK, and gives GRADE MEM_MB 2710 (the measured V9 peak + 20 percent);
      test_job_grade_v9.py checks MEM_MB 2710 (the SCOUT block at the end of the edits)
  python3 -B k16_speed_contract.py <root of the parents> <out folder>    # writes the seven files under <out folder>, open mode 'x'"""
import hashlib, os, re, sys

J = lambda *p: '/'.join(p)
CH3 = J('03_Grading', 'tree', 'tools', 'alarm_process', 'alarm_grade_chain_v2_0_3_to20251231.sh')
CH4 = J('03_Grading', 'tree', 'tools', 'alarm_process', 'alarm_grade_chain_v2_0_4_to20251231.sh')
CM3 = J('03_Grading', 'tree', 'tools', 'month_parts', 'alarm_grade_chain_v2_2_3_to20260430.sh')
CM4 = J('03_Grading', 'tree', 'tools', 'month_parts', 'alarm_grade_chain_v2_2_4_to20260430.sh')
KIT = J('Agentic', 'tree', 'ALARM_DESIGN', 'KIT_V5')
JG8, JG9 = J(KIT, 'jobs', 'JOB_GRADE_V8.job.sh.txt'), J(KIT, 'jobs', 'JOB_GRADE_V9.job.sh.txt')
JM8, JM9 = J(KIT, 'jobs', 'JOB_MONTH_V8.job.sh.txt'), J(KIT, 'jobs', 'JOB_MONTH_V9.job.sh.txt')
Q6, Q7 = J(KIT, 'tools', 'queue_job_v6.py'), J(KIT, 'tools', 'queue_job_v7.py')
TG8, TG9 = J(KIT, 'tests', 'test_job_grade_v8.py'), J(KIT, 'tests', 'test_job_grade_v9.py')
TM8, TM9 = J(KIT, 'tests', 'test_job_month_v8.py'), J(KIT, 'tests', 'test_job_month_v9.py')
PARENTS = {CH4: (CH3, 'a454510a574b830c'), CM4: (CM3, 'b6329f781acd749d'), JG9: (JG8, 'e4a9c7555c17879e'),
           JM9: (JM8, '54cf0fa5f92fcfd3'), Q7: (Q6, '4d75cfc98d5ad34e'), TG9: (TG8, 'b462750e4c831eeb'), TM9: (TM8, 'fe30bb7cf5e44318')}
ORDER = (CH4, CM4, JG9, JM9, Q7, TG9, TM9)
TOKEN = re.compile(r'<<SHA16:([^>]+)>>')

HDR_CH4 = r"""# alarm_grade_chain_v2_0_4_to20251231.sh (SCOUT K16, 31 Oct 2026, home team/RESEARCH/tools/alarm_process; TEST, NOT REVIEWED):
# alarm_grade_chain_v2_0_3_to20251231.sh a454510a574b830c with only Outcomes (step 5) changed (K16 T5; SCOUT 31 Oct: "T5 goes back into
# V1_7, for GRADE only"): event_outcomes_rel1.py runs in 3 worker processes (run 3) in place of 1 (run 1), on the alarm list and on the
# random list; the job declares 3 cores (JOB_GRADE_V9; WORKING_SESSION_V16 section 0.7: a job declares its cores). Why: job 20264959 x2
# (team/SCOUT/receipts/20264959_K16PROF/x2/PARTS_EQUAL.txt 23b6b94481fa2cfa): one Outcomes root in 24.2 s against 34.6 s (its worker
# phase 15.3 s against 28.7 s). The gate (REV2): every day's index readings, the REASONS and the WORDS files equal to run 1's, built_utc
# (the build's wall clock) excluded. x2 compared the manifest's parts: the 17,680 REASONS and WORDS files equal, the 104 index.json files
# not byte-equal; REV2 found them different only in built_utc and the 123,032 value blocks of their readings equal by sha16
# (team/SCOUT/REV2/evidence/T5_INDEX_COMPARE_V1.txt 2baf3ed0cd60c78a). The rest of this header is v2_0_3's.
#   AL=<Alarm> PY=<python> LAB_DAYS=<lab days> FEED_GATE=<gate file or empty> RESEARCH_STORE=<research days> [LEAN=..] [BASE=..] [SCREEN=1] bash alarm_grade_chain_v2_0_4_to20251231.sh <V> <DEF.json|FIRES.tsv> <W> [MENU.json]
"""

HDR_CM4 = r"""# alarm_grade_chain_v2_2_4_to20260430.sh (SCOUT K16, 31 Oct 2026, home team/RESEARCH/tools/month_parts; TEST, NOT REVIEWED):
# alarm_grade_chain_v2_2_3_to20260430.sh b6329f781acd749d with only the detection (step 1) changed (K16 T6; SCOUT 31 Oct, with the fixes
# of the reviews REV1 and REV2): the part count is the chain's rule, never the job's: 2 parts, or 26 up front for a SERIAL_FORCED
# definition (detect_aw1_rel1.py's own parallel_mode: one process for all days; LG4's halves, see v2_2's header below); a part the
# detector refuses with WORKER_RSS_CAP is re-split alone into new folders, its own folder kept and never merged; a coin census before
# the merge; the merge sorts with LC_ALL=C; DETECT_PARTS_<V>.tsv names every try and the STATUS rows detect_plan, resplit_<part> and
# census say which way it went. Why: job 20264959 (team/SCOUT/receipts/20264959_K16PROF): MONTH's 26 parts took 93 s, 2 parts 11 + 12 s
# (x1, with a merge typed for that test: the same fire list, 01b21824046afc8d); a 2-part tree peaked at 3,355,115,520 bytes (x1
# DETECT_RUN_B.json sum_peak_rss_bytes; its workers 0.96 to 1.25 GB, under the 2 GiB cap). Detection is per coin, so the fire list does
# not depend on the parts (v2_2's header). INPUTS_<V>.txt is unchanged. The rest of this header is v2_2_3's.
#   AL=<Alarm> PY=<python> LAB_DAYS=<lab days> FEED_GATE=<gate file or empty> RESEARCH_STORE=<research days> [PARTS=2..26] [LEAN=..] [BASE=..] [SCREEN=1] bash alarm_grade_chain_v2_2_4_to20260430.sh <V> <DEF.json|FIRES.tsv> <W> [MENU.json]
"""

DETECT_V2_2_4 = r"""# 1 detect (K16 T6, v2_2_4): the part count is the chain's rule, never the job's. detect_aw1_rel1.py's own parallel_mode on this
#   definition: SERIAL_FORCED (one process for all days) takes 26 parts up front, any other mode 2 parts; PARTS=2..26 in the environment
#   overrides the rule (tests and reruns; JOB_MONTH_V9 passes PARTS empty). Parts are contiguous slices of the roster in roster order. A
#   part the detector refuses with WORKER_RSS_CAP (rc 2, the log line 'REFUSED WORKER_RSS_CAP: ...') is re-split, alone, into new folders
#   <part>1 to <part>k (k: its coins over the 26-part slice, rounded up); its own folder and log are kept and never merged. Any other
#   failure, a re-split part that fails, or a part refused at the 26-part size stops the chain (exit 3), as v2_2_3 did. DETECT_PARTS_<V>.tsv
#   has a row per try (part, folder, rc, n_coins, use, coins). Before the merge, a coin census: every merged part is a COMPLETE run, their
#   coin lists are disjoint, their union is the roster, and every fire's coin is in its part's list. The merge sorts with LC_ALL=C.
NF=26; LET=(A B C D E F G H I J K L M N O P Q R S T U V W X Y Z); PT=$W/DETECT_PARTS_${V}.tsv
MODE=$($PY -B -c "import importlib.util as u,sys;s=u.spec_from_file_location('detect_aw1_rel1_mode',sys.argv[1]);m=u.module_from_spec(s);s.loader.exec_module(m);print(m.parallel_mode(m.load_definition(sys.argv[2])[0])[0])" $DET "$DEF" 2> $W/detect_mode_${V}.log); rc=$?
[ $rc -eq 0 ] && [ -n "$MODE" ] || { st detect_plan 2 0 "MODE_UNREADABLE $DEF: $(tail -n 1 $W/detect_mode_${V}.log | cut -c1-160)"; exit 3; }
if [ -n "${PARTS:-}" ]; then NP=$PARTS; WHY="PARTS=$PARTS from the caller (parallel_mode $MODE)"
elif [ "$MODE" = SERIAL_FORCED ]; then NP=$NF; WHY="SERIAL_FORCED (detect_aw1_rel1 parallel_mode): $NF parts up front"
else NP=2; WHY="parallel_mode $MODE"; fi
[[ "$NP" =~ ^([2-9]|1[0-9]|2[0-6])$ ]] || { st detect_plan 2 0 "BAD_PARTS $NP (2 to 26)"; exit 2; }
st detect_plan 0 0 "$NP parts: $WHY"
ALLC=$($PY -c "import json,sys;print(','.join(json.load(open(sys.argv[1]))['coins']))" $ROSTER); NALL=$(echo "$ALLC" | tr ',' '\n' | grep -c .)
slice(){ $PY -c "import sys;c=sys.argv[1].split(',');n,i=int(sys.argv[2]),int(sys.argv[3]);k=len(c);print(','.join(c[i*k//n:(i+1)*k//n]))" "$1" $2 $3; }
ncoins(){ echo "$1" | tr ',' '\n' | grep -c .; }
row(){ printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$1" "${D}_$1" "$2" "$(ncoins "$4")" "$3" "$4" >> $PT; }
try(){ local t0; t0=$(date +%s)
  nice -n 10 $PY -B $DET --definition "$DEF" --roster $ROSTER --coins $2 --first $FIRST --last $LAST --research-window 20250901:$LAST --lab-root "$LAB_DAYS" --gate="$FEED_GATE" --out ${D}_$1 --workers 3 > ${D}_$1.log 2>&1; TRC=$?
  st detect_$1 $TRC $(( $(date +%s)-t0 )) ${D}_$1; [ $TRC -ne 0 ] || [ -f ${D}_$1/EVENTS.tsv ] || TRC=3; }
cap(){ [ $TRC -eq 2 ] && grep -q '^REFUSED WORKER_RSS_CAP:' ${D}_$1.log; }
printf 'part\tfolder\trc\tn_coins\tuse\tcoins\n' > $PT
for i in $(seq 0 $((NP-1))); do h=${LET[$i]}; C=$(slice "$ALLC" $NP $i)
  [ -n "$C" ] || { st detect_$h 2 0 "EMPTY_PART $i of $NP"; exit 3; }
  try $h $C; [ $TRC -eq 0 ] && { row $h 0 merged $C; continue; }
  n=$(ncoins $C); k=$(( (n * NF + NALL - 1) / NALL ))
  cap $h || { row $h $TRC failed $C; exit 3; }
  [ $k -ge 2 ] || { row $h $TRC failed $C; st resplit_$h 2 0 "WORKER_RSS_CAP in part $h ($n coins) at the 26-part size: no finer split"; exit 3; }
  row $h $TRC refused_kept_unmerged $C
  st resplit_$h 0 0 "WORKER_RSS_CAP in part $h ($n coins): ${D}_$h kept, never merged; re-split into $k parts ${h}1 to ${h}$k"
  for j in $(seq 1 $k); do hh=$h$j; CC=$(slice $C $k $((j-1)))
    [ -n "$CC" ] || { st detect_$hh 2 0 "EMPTY_PART $j of $k (part $h)"; exit 3; }
    try $hh $CC; [ $TRC -eq 0 ] || { row $hh $TRC failed $CC; exit 3; }
    row $hh 0 merged $CC; done
done
# the coin census of the merged parts, then the merge (rows sorted by t then coin, LC_ALL=C)
$PY -B - $PT "$ALLC" > $W/census_${V}.txt 2>&1 <<'CENSUS'
import csv, json, os, sys
rows = [r for r in csv.DictReader(open(sys.argv[1]), delimiter='\t') if r['use'] == 'merged']
roster = sys.argv[2].split(','); seen = {}; bad = []
for r in rows:
    own = r['coins'].split(',')
    for c in own:
        if c in seen:
            bad.append('coin %s in parts %s and %s' % (c, seen[c], r['part']))
        seen[c] = r['part']
    run = os.path.join(r['folder'], 'DETECT_RUN.json')
    if not os.path.isfile(run) or json.load(open(run)).get('status') != 'COMPLETE':
        bad.append('part %s is not a COMPLETE run' % r['part']); continue
    own = set(own); hdr = None
    for line in open(os.path.join(r['folder'], 'EVENTS.tsv')):
        if line.startswith('#'):
            continue
        f = line.rstrip('\n').split('\t')
        if hdr is None:
            hdr = f
            if 'coin' not in hdr:
                bad.append('part %s: no coin column' % r['part']); break
            ci = hdr.index('coin'); continue
        if f[ci] not in own:
            bad.append('a fire of coin %s in part %s' % (f[ci], r['part'])); break
miss = [c for c in roster if c not in seen]; extra = sorted(set(seen) - set(roster))
if miss:
    bad.append('in no merged part: ' + ','.join(miss[:5]))
if extra:
    bad.append('not in the roster: ' + ','.join(extra[:5]))
if not rows:
    bad.append('no merged part')
print('CENSUS_FAILED ' + '; '.join(bad[:5]) if bad else '%d coins in %d merged parts: COMPLETE, disjoint, their union is the roster, every fire in its part' % (len(seen), len(rows)))
sys.exit(1 if bad else 0)
CENSUS
rc=$?; st census $rc 0 "$(tail -n 1 $W/census_${V}.txt | cut -c1-300)"; [ $rc -eq 0 ] || exit 3
ML=$(tail -n +2 $PT | awk -F'\t' '$5=="merged"{printf "%s ", $1}'); P1=${ML%% *}
mkdir -p $D && { grep '^#' ${D}_$P1/EVENTS.tsv; echo "# merged by alarm_grade_chain_v2_2_4_to20260430.sh: parts ${ML}(DETECT_PARTS_${V}.tsv, $NP planned), rows sorted by t then coin (LC_ALL=C)"
  grep -v '^#' ${D}_$P1/EVENTS.tsv | head -1
  { for h in $ML; do grep -v '^#' ${D}_$h/EVENTS.tsv | tail -n +2; done; } | LC_ALL=C sort -t$'\t' -k2,2n -k1,1; } > $D/EVENTS.tsv
grep -v '^#' $D/EVENTS.tsv > $LIST
"""

DU_OLD = r"""du -sm $W | awk '{print "du_mb_W\t"$1}' > $DV/DISK.tsv; printf 'free_mb_end\t%s\n' "$(fmb)" >> $DV/DISK.tsv
"""
DU_NEW = r"""WMB=$(du -sm $W | cut -f1); FMB=$(fmb); printf 'du_mb_W\t%s\nfree_mb_end\t%s\n' "$WMB" "$FMB" > $DV/DISK.tsv   # K16 T8: one du, one df
"""
END_OLD = 'st end 0 0 "SCRATCH_DISK free $(fmb) MB; W $(du -sm $W | cut -f1) MB"'
END_NEW = 'st end 0 0 "SCRATCH_DISK free $FMB MB; W $WMB MB"'
CORES = ('# MEM_MB: @@MMB@@\n', '# MEM_MB: @@MMB@@\n# CORES 3\n', 1)

EDITS = {
    CH4: [('#!/bin/bash\n', '#!/bin/bash\n' + HDR_CH4, 1),
          ('nice -n 10 $PY -B $EO run 1 "$LAB_DAYS"', 'nice -n 10 $PY -B $EO run 3 "$LAB_DAYS"', 1)],
    CM4: [('#!/bin/bash\n', '#!/bin/bash\n' + HDR_CM4, 1),
          ('SPAN', '# 1 detect in PARTS parts (roster order, contiguous slices), merged, rows sorted by t then coin',
           "grep -v '^#' $D/EVENTS.tsv > $LIST", '07b6737d0f2ff9b0', DETECT_V2_2_4)],
    JG9: [('(ALARM_DESIGN KIT_V5 JOB_GRADE_V8, template @@TPLSHA@@): ',
           '(ALARM_DESIGN KIT_V5 JOB_GRADE_V9, template @@TPLSHA@@; JOB_GRADE_V8 with chain v2_0_4 (v2_0_3 with Outcomes in 3 worker '
           'processes, K16 T5), 3 cores declared (# CORES 3) and one du at the end (K16 T8), SCOUT K16, 31 Oct): ', 1),
          ('(alarm_grade_chain_v2_0_3_to20251231: v2_0_2 with Outcomes event_outcomes_rel1,',
           '(alarm_grade_chain_v2_0_4_to20251231: v2_0_3 with Outcomes in 3 worker processes; v2_0_3: v2_0_2 with Outcomes event_outcomes_rel1,', 1),
          CORES,
          ('ck $CH/alarm_grade_chain_v2_0_3_to20251231.sh a454510a574b830c', 'ck $CH/alarm_grade_chain_v2_0_4_to20251231.sh <<SHA16:%s>>' % CH4, 1),
          ('bash $CH/alarm_grade_chain_v2_0_3_to20251231.sh $V $D $W', 'bash $CH/alarm_grade_chain_v2_0_4_to20251231.sh $V $D $W', 1),
          ('"chain v2_0_3 Sep-Dec, lean $L"', '"chain v2_0_4 Sep-Dec, lean $L"', 1),
          (DU_OLD, DU_NEW, 1), (END_OLD, END_NEW, 1)],
    JM9: [('(ALARM_DESIGN KIT_V5 JOB_MONTH_V8, template @@TPLSHA@@; chain v2_2_3 in 26 coin parts: v2_2_2 with',
           '(ALARM_DESIGN KIT_V5 JOB_MONTH_V9, template @@TPLSHA@@; JOB_MONTH_V8 with chain v2_2_4 (v2_2_3 with the detection in the parts '
           "the chain's rule gives: 2, or 26 up front for a SERIAL_FORCED definition; a part refused at the 2 GiB worker cap re-split alone; a "
           'coin census before the merge; DETECT_PARTS_<V>.tsv in the receipts; K16 T6), no part count set by the job, 3 cores declared '
           '(# CORES 3), MEM_MB the measured peak + 20 percent (queue_job_v7) and one du at the end (K16 T8), SCOUT K16, 31 Oct; chain '
           'v2_2_3: v2_2_2 with', 1),
          CORES,
          ('ck $MP/alarm_grade_chain_v2_2_3_to20260430.sh b6329f781acd749d', 'ck $MP/alarm_grade_chain_v2_2_4_to20260430.sh <<SHA16:%s>>' % CM4, 1),
          ('PARTS=26 LEAN=$L bash $MP/alarm_grade_chain_v2_2_3_to20260430.sh $V $D $W', 'PARTS= LEAN=$L bash $MP/alarm_grade_chain_v2_2_4_to20260430.sh $V $D $W', 1),
          ('  st grade_$V $r $(( $(date +%s)-t0 )) "chain v2_2_3 Sep-Apr in 26 coin parts, lean $L"',
           "  NPM=$(tail -n +2 $W/DETECT_PARTS_$V.tsv 2>/dev/null | cut -f5 | grep -c '^merged$'); "
           'st grade_$V $r $(( $(date +%s)-t0 )) "chain v2_2_4 Sep-Apr in ${NPM:-0} coin parts, lean $L"', 1),
          ('  for h in A B C D E F G H I J K L M N O P Q R S T U V W X Y Z; do [ -f $W/det_${V}_v1_$h/DETECT_RUN.json ]',
           '  for h in $(tail -n +2 $W/DETECT_PARTS_$V.tsv 2>/dev/null | cut -f1); do [ -f $W/det_${V}_v1_$h/DETECT_RUN.json ]', 1),
          ('  for x in CARD_$V.txt SUM_$V.tsv STATUS_$V.tsv INPUTS_$V.txt', '  for x in CARD_$V.txt SUM_$V.tsv STATUS_$V.tsv DETECT_PARTS_$V.tsv INPUTS_$V.txt', 1),
          (DU_OLD, DU_NEW, 1), (END_OLD, END_NEW, 1)],
    Q7: [('"""queue_job_v6.py (SCOUT K12 for ALARM_DESIGN KIT_V5, 31 Oct 2026; TEST, NOT REVIEWED): queue_job_v5.py 51864a030f5cfb20 with only',
          '"""queue_job_v7.py (SCOUT K16 for ALARM_DESIGN KIT_V5, 31 Oct 2026; TEST, NOT REVIEWED): queue_job_v6.py 4d75cfc98d5ad34e with only\n'
          'GRADE and MONTH on their V9 templates and MONTH\'s MEM_MB changed: JOB_GRADE_V9 (<<SHA16:%s>>: chain v2_0_4, Outcomes in 3 worker\n'
          'processes, 3 cores declared, one du at the end) and JOB_MONTH_V9 (<<SHA16:%s>>: chain v2_2_4, the detection parts by the chain\'s\n'
          'rule, 3 cores declared, one du at the end), K16 T5, T6 and T8; MONTH\'s MEM_MB 4030, the measured peak + 20 percent (WORKING_SESSION_V16\n'
          'section 0.7; job 20264959 x1: a 2-part tree up to 3,355,115,520 bytes, DETECT_RUN_B.json sum_peak_rss_bytes; was 8000). The docstring\n'
          'of queue_job_v6.py follows.\n'
          'queue_job_v6.py (SCOUT K12 for ALARM_DESIGN KIT_V5, 31 Oct 2026; TEST, NOT REVIEWED): queue_job_v5.py 51864a030f5cfb20 with only' % (JG9, JM9), 1),
         ('python3 -B <Alarm>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/queue_job_v6.py --settings', 'python3 -B <Alarm>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/queue_job_v7.py --settings', 1),
         ('(run queue_job_v6.py from the Alarm folder)', '(run queue_job_v7.py from the Alarm folder)', 1),
         ("'settings_v1_of_queue_job_v6'", "'settings_v1_of_queue_job_v7'", 1),
         ("'USAGE queue_job_v6.py --settings", "'USAGE queue_job_v7.py --settings", 1),
         ("'GRADE': 'e4a9c7555c17879e', 'MONTH': '54cf0fa5f92fcfd3',", "'GRADE': '<<SHA16:%s>>', 'MONTH': '<<SHA16:%s>>'," % (JG9, JM9), 1),
         ('# days from RESEARCH_STORE, SCOUT K12, 31 Oct); a KIND without one is NOT CLEAN YET',
          '# days from RESEARCH_STORE, SCOUT K12, 31 Oct; GRADE V9 and MONTH V9: chains v2_0_4 (Outcomes in 3 worker processes) and v2_2_4 (the\n'
          "# detection parts by the chain's rule), 3 cores declared, one du at the end, SCOUT K16, 31 Oct); a KIND without one is NOT CLEAN YET", 1),
         ("'GRADE': 'JOB_GRADE_V8.job.sh.txt',", "'GRADE': 'JOB_GRADE_V9.job.sh.txt',", 1),
         ("'MONTH': 'JOB_MONTH_V8.job.sh.txt',", "'MONTH': 'JOB_MONTH_V9.job.sh.txt',", 1),
         ("sub.update({'@@WMB@@': str(3000 * n), '@@MMB@@': '8000', '@@MINUTES@@': str(60 * n)})",
          "sub.update({'@@WMB@@': str(3000 * n), '@@MMB@@': '4030', '@@MINUTES@@': str(60 * n)})   # K16: MEM_MB = the measured peak + 20 "
          "percent (job 20264959 x1: a 2-part tree 3,355,115,520 bytes); was 8000", 1)],
}

SANDBOX_V7 = [   # K12's sandbox for the V8 tests, with queue_job_v7.py
    ("\"\"\"K4's sandbox with queue_job_v6.py in place of queue_job_v5.py", "\"\"\"K4's sandbox with queue_job_v7.py in place of queue_job_v5.py", 1),
    ('(queue_job_v6 needs it in the job settings)', '(queue_job_v7 needs it in the job settings)', 1),
    ("dst = os.path.join(self.P, *K4.KIT, 'tools', 'queue_job_v6.py'); shutil.copyfile(os.path.join(KIT5, 'tools', 'queue_job_v6.py'), dst)",
     "dst = os.path.join(self.P, *K4.KIT, 'tools', 'queue_job_v7.py'); shutil.copyfile(os.path.join(KIT5, 'tools', 'queue_job_v7.py'), dst)", 1),
    ("spec_from_file_location('queue_job_v6_k12', dst)", "spec_from_file_location('queue_job_v7_k16', dst); assert sp and sp.loader", 1),
]
CHECKS_TAIL = "    return f\n\n\ndef one_"
CHECKS_GRADE = r"""    if not re.search(r'^# CORES 3$', body, flags=re.M): f.append('the job does not declare # CORES 3')
    if not re.search(r'^# MEM_MB: 6000$', body, flags=re.M): f.append('the job does not declare MEM_MB 6000')
    if len(re.findall(r'\bdu -sm\b', body)) != 1: f.append('du runs %d times, not once' % len(re.findall(r'\bdu -sm\b', body)))
"""
CHECKS_MONTH = r"""    if not re.search(r'^# CORES 3$', body, flags=re.M): f.append('the job does not declare # CORES 3')
    if not re.search(r'^# MEM_MB: 4030$', body, flags=re.M): f.append('the job does not declare MEM_MB 4030, the measured peak + 20 percent')
    if len(re.findall(r'\bdu -sm\b', body)) != 1: f.append('du runs %d times, not once' % len(re.findall(r'\bdu -sm\b', body)))
    if 'for h in $(tail -n +2 $W/DETECT_PARTS_$V.tsv 2>/dev/null | cut -f1); do' not in body: f.append('the detection memory rows do not follow the chain parts table')
    if 'STATUS_$V.tsv DETECT_PARTS_$V.tsv INPUTS_$V.txt' not in body: f.append('the chain parts table is not kept in the receipts')
"""
DOC_G = ('"""test_job_grade_v9.py (SCOUT K16, 31 Oct 2026; TEST, NOT REVIEWED): test_job_grade_v8.py (K12) for JOB_GRADE_V9 and queue_job_v7.py:\n'
         'the chain v2_0_4, and three checks more: the filled job declares # CORES 3 and MEM_MB 6000 and runs du once, each with its planted\n'
         'bug. The docstring of test_job_grade_v8.py follows.\n')
DOC_M = ('"""test_job_month_v9.py (SCOUT K16, 31 Oct 2026; TEST, NOT REVIEWED): test_job_month_v8.py (K12) for JOB_MONTH_V9 and queue_job_v7.py:\n'
         'the chain v2_2_4 with no part count from the job (PARTS empty: the chain\'s rule), and five checks more: the filled job declares\n'
         '# CORES 3 and MEM_MB 4030, runs du once, writes the detection memory rows from the chain\'s parts table DETECT_PARTS_<V>.tsv and keeps\n'
         'that table in the receipts, each with its planted bug. The docstring of test_job_month_v8.py follows.\n')
EDITS[TG9] = [('"""test_job_grade_v8.py (SCOUT K12', DOC_G + 'test_job_grade_v8.py (SCOUT K12', 1),
              ('KIT_V5/tests/test_job_grade_v8.py"""', 'KIT_V5/tests/test_job_grade_v9.py"""', 1),
              ("'alarm_process', 'alarm_grade_chain_v2_0_3_to20251231.sh')", "'alarm_process', 'alarm_grade_chain_v2_0_4_to20251231.sh')", 1)] + SANDBOX_V7 + [
              (r"LEAN=\$L bash \$CH/alarm_grade_chain_v2_0_3_to20251231\.sh ", r"LEAN=\$L bash \$CH/alarm_grade_chain_v2_0_4_to20251231\.sh ", 1),
              (CHECKS_TAIL, CHECKS_GRADE + CHECKS_TAIL, 1),
              ("if 'chain v2_0_3 Sep-Dec' not in st: fails.append('%s the grade stage does not name the chain v2_0_3' % v)",
               "if 'chain v2_0_4 Sep-Dec' not in st: fails.append('%s the grade stage does not name the chain v2_0_4' % v)", 1),
              ("'the template pins %s, the package chain v2_0_3 is %s'", "'the template pins %s, the package chain v2_0_4 is %s'", 1),
              ("('ck $CH/alarm_grade_chain_v2_0_3_to20251231.sh a454510a574b830c', 'ck $CH/alarm_grade_chain_v2_0_2_to20251231.sh 3628339f9fefb7cd'),",
               "('ck $CH/alarm_grade_chain_v2_0_4_to20251231.sh <<SHA16:%s>>', 'ck $CH/alarm_grade_chain_v2_0_3_to20251231.sh a454510a574b830c')," % CH4, 1),
              ("('alarm_grade_chain_v2_0_3_to20251231.sh a454510a574b830c', 'alarm_grade_chain_v2_0_3_to20251231.sh 0000000000000000'),",
               "('alarm_grade_chain_v2_0_4_to20251231.sh <<SHA16:%s>>', 'alarm_grade_chain_v2_0_4_to20251231.sh 0000000000000000')," % CH4, 1),
              ("('bash $CH/alarm_grade_chain_v2_0_3_to20251231.sh $V', 'bash $CH/alarm_grade_chain_v2_0_2_to20251231.sh $V'),",
               "('bash $CH/alarm_grade_chain_v2_0_4_to20251231.sh $V', 'bash $CH/alarm_grade_chain_v2_0_3_to20251231.sh $V'),", 1),
              ("('\"chain v2_0_3 Sep-Dec, lean $L\"', '\"chain v2_0_2 Sep-Dec, lean $L\"'),", "('\"chain v2_0_4 Sep-Dec, lean $L\"', '\"chain v2_0_3 Sep-Dec, lean $L\"'),", 1),
              ("    (' The quiet window was removed by the owner 30 Oct 2026 23:32 Berlin', ' Stops before the quiet window'),\n]",
               "    (' The quiet window was removed by the owner 30 Oct 2026 23:32 Berlin', ' Stops before the quiet window'),\n"
               "    ('# CORES 3\\n', ''), ('\"SCRATCH_DISK free $FMB MB; W $WMB MB\"', '\"SCRATCH_DISK free $FMB MB; W $(du -sm $W | cut -f1) MB\"'),   # K16: V9's checks\n]", 1),
              ("text = open(os.path.join(KIT5, 'jobs', 'JOB_GRADE_V8.job.sh.txt')).read()", "text = open(os.path.join(KIT5, 'jobs', 'JOB_GRADE_V9.job.sh.txt')).read()", 1)]
EDITS[TM9] = [('"""test_job_month_v8.py (SCOUT K12', DOC_M + 'test_job_month_v8.py (SCOUT K12', 1),
              ('KIT_V5/tests/test_job_month_v8.py"""', 'KIT_V5/tests/test_job_month_v9.py"""', 1),
              ("'month_parts', 'alarm_grade_chain_v2_2_3_to20260430.sh')", "'month_parts', 'alarm_grade_chain_v2_2_4_to20260430.sh')", 1)] + SANDBOX_V7 + [
              (r"PARTS=26 LEAN=\$L bash \$MP/alarm_grade_chain_v2_2_3_to20260430\.sh ", r"PARTS= LEAN=\$L bash \$MP/alarm_grade_chain_v2_2_4_to20260430\.sh ", 1),
              (CHECKS_TAIL, CHECKS_MONTH + CHECKS_TAIL, 1),
              ("if 'chain v2_2_3 Sep-Apr in 26 coin parts' not in st: fails.append('%s the grade stage does not name the chain v2_2_3' % v)",
               "if not re.search(r'chain v2_2_4 Sep-Apr in \\d+ coin parts', st): fails.append('%s the grade stage does not name the chain v2_2_4' % v)", 1),
              ("or cs.get('PARTS') != '26' or cs.get('w') != W", "or cs.get('PARTS') != '' or cs.get('w') != W", 1),
              ("'the template pins %s, the package chain v2_2_3 is %s'", "'the template pins %s, the package chain v2_2_4 is %s'", 1),
              ("('ck $MP/alarm_grade_chain_v2_2_3_to20260430.sh b6329f781acd749d', 'ck $MP/alarm_grade_chain_v2_2_2_to20260430.sh d2bc556e5adaa1a4'),",
               "('ck $MP/alarm_grade_chain_v2_2_4_to20260430.sh <<SHA16:%s>>', 'ck $MP/alarm_grade_chain_v2_2_3_to20260430.sh b6329f781acd749d')," % CM4, 1),
              ("('alarm_grade_chain_v2_2_3_to20260430.sh b6329f781acd749d', 'alarm_grade_chain_v2_2_3_to20260430.sh 0000000000000000'),",
               "('alarm_grade_chain_v2_2_4_to20260430.sh <<SHA16:%s>>', 'alarm_grade_chain_v2_2_4_to20260430.sh 0000000000000000')," % CM4, 1),
              ("('bash $MP/alarm_grade_chain_v2_2_3_to20260430.sh $V', 'bash $MP/alarm_grade_chain_v2_2_2_to20260430.sh $V'),",
               "('bash $MP/alarm_grade_chain_v2_2_4_to20260430.sh $V', 'bash $MP/alarm_grade_chain_v2_2_3_to20260430.sh $V'),", 1),
              ("('\"chain v2_2_3 Sep-Apr in 26 coin parts, lean $L\"', '\"chain v2_2_2 Sep-Apr in 26 coin parts, lean $L\"'),",
               "('\"chain v2_2_4 Sep-Apr in ${NPM:-0} coin parts, lean $L\"', '\"chain v2_2_3 Sep-Apr in ${NPM:-0} coin parts, lean $L\"'),", 1),
              ("('PARTS=26 LEAN=$L', 'PARTS=8 LEAN=$L'),", "('PARTS= LEAN=$L', 'PARTS=26 LEAN=$L'),", 1),
              ("    ('F=$AL/01_Detection/tree', 'F=$AL/03_Grading/tree'),\n]",
               "    ('F=$AL/01_Detection/tree', 'F=$AL/03_Grading/tree'),\n"
               "    ('# CORES 3\\n', ''), ('\"SCRATCH_DISK free $FMB MB; W $WMB MB\"', '\"SCRATCH_DISK free $FMB MB; W $(du -sm $W | cut -f1) MB\"'),   # K16: V9's checks\n"
               "    ('$(tail -n +2 $W/DETECT_PARTS_$V.tsv 2>/dev/null | cut -f1)', 'A B C D E F G H I J K L M N O P Q R S T U V W X Y Z'),\n"
               "    ('STATUS_$V.tsv DETECT_PARTS_$V.tsv INPUTS_$V.txt', 'STATUS_$V.tsv INPUTS_$V.txt'),\n]", 1),
              ("text = open(os.path.join(KIT5, 'jobs', 'JOB_MONTH_V8.job.sh.txt')).read()", "text = open(os.path.join(KIT5, 'jobs', 'JOB_MONTH_V9.job.sh.txt')).read()", 1)]



# SCOUT, 31 Oct 2026 (the owner 10:51 Berlin, of CLEAN: "remove it"; scratch cleanup is DSK's, on the owner's word): appended to K16's edits.
SCOUT_CLEAN = "CLEAN REMOVED: the owner 31 Oct 2026 10:51 Berlin; scratch cleanup is DSK's, on the owner's word"
EDITS[Q7] += [
    ('sum_peak_rss_bytes; was 8000). The docstring\nof queue_job_v6.py follows.\n',
     'sum_peak_rss_bytes; was 8000). SCOUT, 31 Oct 2026 (the owner 10:51 Berlin, of CLEAN: "remove it"; scratch cleanup is DSK\'s, on\n'
     'the owner\'s word): KIND CLEAN is refused (CLEAN REMOVED) and is in no table; a finished job\'s scratch counts in the disk budget only while\n'
     'its folder is on SCRATCH_DISK (DSK\'s sweep frees it); GRADE\'s MEM_MB 2710, the measured V9 peak + 20 percent (job 20265002: the detection\n'
     'part tree 2,255,994,880 bytes, the two parts one after the other; was 6000). The docstring of queue_job_v6.py follows.\n', 1),
    ('           CLEAN  ITEMS = JOB[,JOB...] (receipts names, e.g. 20263700_GRADE_FLOWX); IDEA is a label. Removes your own scratch\n'
     '                  of finished, decided jobs after their proof is on dev (the owner 29 Oct 14:52 Berlin). Not counted in the job budget.\n',
     '           CLEAN  REMOVED (the owner 31 Oct 2026 10:51 Berlin): refused; scratch cleanup is DSK\'s, on the owner\'s word.\n', 1),
    ('RUN_BUDGET_MB of its own uncleaned scratch (measured from finished receipts, declared for the rest); CLEAN your decided jobs to go on.\n',
     'RUN_BUDGET_MB of its own scratch on SCRATCH_DISK (measured from finished receipts while the job\'s scratch folder is there, declared for the\n'
     'rest); scratch cleanup is DSK\'s (the owner 31 Oct 2026 10:51 Berlin).\n', 1),
    ("TEMPLATE_SHA = {'COUNT': '57b5c18ed82061f6', 'CLEAN': '604cbe0b9254a8b1', ", "TEMPLATE_SHA = {'COUNT': '57b5c18ed82061f6', ", 1),
    ("TEMPLATE_NAME = {'COUNT': 'JOB_COUNT_V6.job.sh.txt', 'CLEAN': 'JOB_CLEAN_V6.job.sh.txt', ", "TEMPLATE_NAME = {'COUNT': 'JOB_COUNT_V6.job.sh.txt', ", 1),
    ("KINDS = ('COUNT', 'GRADE', 'ENTRY', 'MONTH', 'CLEAN')\n",
     "KINDS = ('COUNT', 'GRADE', 'ENTRY', 'MONTH')\nCLEAN_REMOVED = %r   # SCOUT, 31 Oct 2026: KIND CLEAN is refused by name\n" % SCOUT_CLEAN, 1),
    ("    if kind not in KINDS:\n        raise Refused('KIND %r: one of %s' % (kind, ', '.join(KINDS)))\n",
     "    if kind == 'CLEAN':\n        raise Refused(CLEAN_REMOVED)\n    if kind not in KINDS:\n        raise Refused('KIND %r: one of %s' % (kind, ', '.join(KINDS)))\n", 1),
    ("        sub.update({'@@WMB@@': str(1800 * n), '@@MMB@@': '6000', '@@MINUTES@@': str(30 * n + 10)})\n",
     "        sub.update({'@@WMB@@': str(1800 * n), '@@MMB@@': '2710', '@@MINUTES@@': str(30 * n + 10)})   # SCOUT: MEM_MB = the measured V9 "
     "peak + 20 percent (job 20265002: the detection part tree 2,255,994,880 bytes); was 6000\n", 1),
    ('def scratch_used(run, regs=None):\n'
     '    """MB of this run\'s own uncleaned scratch: measured (receipts DISK.tsv and STORE_PLACES.tsv) for finished jobs, declared for others"""\n',
     'def scratch_gone(run, d):\n'
     '    """True when this machine sees SCRATCH_DISK (SCRATCH of --settings) and the scratch folder SCRATCH/work_<RUN>/<JOB> of the finished job\n'
     '    whose receipts folder is d is not on it (a job\'s scratch W is named by its receipts name)"""\n'
     "    w = CFG.get('WDB')\n"
     "    return bool(w) and os.path.isdir(w) and not os.path.isdir(os.path.join(w, 'work_%s' % os.path.basename(run.rstrip('/')),\n"
     "                                                                       os.path.basename(d.rstrip('/'))))\n"
     '\n\n'
     'def scratch_used(run, regs=None):\n'
     '    """MB of this run\'s own scratch on SCRATCH_DISK: measured (receipts DISK.tsv and STORE_PLACES.tsv) for finished jobs whose scratch folder\n'
     '    is still there (none for one DSK swept; counted when SCRATCH_DISK is not visible from here), declared for the others"""\n', 1),
    ("        dk = os.path.join(d, 'DISK.tsv')\n        if os.path.isfile(dk):\n            mb = 0\n",
     "        dk = os.path.join(d, 'DISK.tsv')\n        if os.path.isfile(dk):\n            if scratch_gone(run, d):\n"
     "                continue      # its scratch folder is no longer on SCRATCH_DISK (DSK's sweep; the owner 31 Oct 2026 10:51 Berlin): it holds nothing\n"
     "            mb = 0\n", 1),
    ("of uncleaned scratch; with this job\\'s %d MB it would pass %d MB: decide your finished jobs and CLEAN them first'",
     "of scratch on SCRATCH_DISK; with this job\\'s %d MB it would pass %d MB: scratch cleanup is done by DSK (the owner 31 Oct 2026 10:51 Berlin): "
     "ask DSK on the board (hb/DSK.txt) and wait for its sweep'", 1),
]
EDITS[TG9] += [
    ("    if not re.search(r'^# MEM_MB: 6000$', body, flags=re.M): f.append('the job does not declare MEM_MB 6000')\n",
     "    if not re.search(r'^# MEM_MB: 2710$', body, flags=re.M): f.append('the job does not declare MEM_MB 2710, the measured V9 peak + 20 percent')\n", 1),
    ('the filled job declares # CORES 3 and MEM_MB 6000 and runs du once, each with its planted\nbug.',
     'the filled job declares # CORES 3 and MEM_MB 2710 (SCOUT: the measured V9 peak + 20 percent) and runs du once, each with its\nplanted bug.', 1),
]


def sha16b(b):
    return hashlib.sha256(b).hexdigest()[:16]


def apply(text, edits, name, done):
    for i, e in enumerate(edits):
        if e[0] == 'SPAN':
            _, head, tail, want, new = e
            lines = text.split('\n')
            a = [k for k, l in enumerate(lines) if l.startswith(head)]
            if len(a) != 1:
                raise SystemExit('EDIT_COUNT %s edit %d: the span head is found %d times, want 1' % (name, i + 1, len(a)))
            b = [k for k in range(a[0], len(lines)) if lines[k] == tail]
            if not b:
                raise SystemExit('EDIT_SPAN %s edit %d: no tail line after the head' % (name, i + 1))
            span = '\n'.join(lines[a[0]:b[0] + 1]) + '\n'
            if sha16b(span.encode('utf-8')) != want:
                raise SystemExit('EDIT_SPAN %s edit %d: the span is %s, want %s' % (name, i + 1, sha16b(span.encode('utf-8')), want))
            text = '\n'.join(lines[:a[0]]) + '\n' + new + '\n'.join(lines[b[0] + 1:])
            continue
        old, new, n = e
        new = TOKEN.sub(lambda m: sha16b(done[m.group(1)]), new)
        k = text.count(old)
        if k != n:
            raise SystemExit('EDIT_COUNT %s edit %d: found %d times, want %d: %r' % (name, i + 1, k, n, old[:90]))
        text = text.replace(old, new)
    return text


def build(root):
    """-> {new path: bytes}, the seven files remade from their parents under root"""
    done = {}
    for rel in ORDER:
        old, want = PARENTS[rel]
        b = open(os.path.join(root, old), 'rb').read()
        if sha16b(b) != want:
            raise SystemExit('PARENT_CHANGED %s is %s, want %s' % (old, sha16b(b), want))
        done[rel] = apply(b.decode('utf-8'), EDITS[rel], rel, done).encode('utf-8')
    return done


def main(argv):
    if len(argv) != 3:
        raise SystemExit((__doc__ or '').split('\n')[-1])   # V1_13: pyright
    root, out = argv[1], argv[2]
    for rel, b in build(root).items():
        p = os.path.join(out, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'xb') as f:
            f.write(b)
        if rel.endswith('.sh') or rel.endswith('.py'):
            os.chmod(p, os.stat(os.path.join(root, PARENTS[rel][0])).st_mode & 0o777)
        print('%s\t%s\t%d' % (rel, sha16b(b), len(b)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
