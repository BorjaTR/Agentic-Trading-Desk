#!/usr/bin/env python3
"""test_speed_s1_v1.py (SCOUT, 31 Oct 2026; TEST, NOT REVIEWED): V2_0 stage 1 (team/SCOUT/SPEED_V2_0_DESIGN_V1.md Q1-Q3) in the Alarm package:
  S1  in each chain (GRADE v2_0_5, MONTH v2_2_5) steps 5-7 run as written, with planted tools in place of Outcomes, the menu and the
      card (each sleeps 0.3 s and logs its start and end): the two Outcomes runs overlap, the menu and the card overlap, the menu and card
      start only after both Outcomes runs ended; the STATUS lines come in v2_0_4's order (outcomes_alarm, outcomesRND, menu, card, done)
      and the chain exits 0;
  S2  an Outcomes run that fails: both runs still end, then exit 6, with the alarm's STATUS line first; no menu, no card;
  S3  SCREEN=1: one Outcomes run (ALARM), no menu, the card with --screen;
  S5  a card that fails: the chain exits with the card's code and its STATUS line has it (the card's own process is waited for);
  S4  JOB_GRADE_V10: chain v2_0_5 pinned at the file's sha16 and run; # CORES 6; perfire and its test in the background, waited for
      in variant order after the hand-off, then their STAGES lines and the FIRES row; every disk stop waits first;
      JOB_MONTH_V10: chain v2_2_5 pinned at its sha16 and run, the rest V9's.
Then planted bugs in copies of the chains and templates: each must fail a test; the unpatched copies pass. Temp folders only; seconds.
  python3 -B <Alarm>/Agentic/tree/ALARM_DESIGN/KIT_V5/tests/test_speed_s1_v1.py"""
import hashlib, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..'))
GCH = os.path.join(PKG, '03_Grading', 'tree', 'tools', 'alarm_process', 'alarm_grade_chain_v2_0_5_to20251231.sh')
MCH = os.path.join(PKG, '03_Grading', 'tree', 'tools', 'month_parts', 'alarm_grade_chain_v2_2_5_to20260430.sh')
GJ = os.path.join(PKG, 'Agentic', 'tree', 'ALARM_DESIGN', 'KIT_V5', 'jobs', 'JOB_GRADE_V10.job.sh.txt')
MJ = os.path.join(PKG, 'Agentic', 'tree', 'ALARM_DESIGN', 'KIT_V5', 'jobs', 'JOB_MONTH_V10.job.sh.txt')

FAKE = r'''#!/bin/bash
# a planted tool: logs "<name> start <ns>" and "<name> end <ns>", sleeps 0.3 s, exits with $FAKE_FAIL_<name> or 0
case "$*" in
  *" run "*IDEA2*RNDMENU*) n=OM_RND;; *" run "*IDEA2*MENU*) n=OM_ALARM;; *menu_v2_1.py*) n=MENU;; *alarm_card_v1_*) n=CARD;; *) n=OTHER;; esac
echo "$n start $(python3 -c 'import time;print(time.time_ns())') $*" >> "$FAKE_LOG"
sleep 0.3
echo "$n end $(python3 -c 'import time;print(time.time_ns())')" >> "$FAKE_LOG"
v=FAKE_FAIL_$n; exit ${!v:-0}
'''


def block(chain):
    """steps 5-7 of the chain, as written: from '# 5 Outcomes' to its last line"""
    t = open(chain).read()
    i = t.index('# 5 Outcomes')
    return t[i:]


def run_block(chain, t, screen='0', fail=None):
    w = os.path.join(t, 'W'); os.makedirs(w)
    fake = os.path.join(t, 'fakepy'); open(fake, 'w').write(FAKE); os.chmod(fake, 0o755)
    log = os.path.join(t, 'fake.log'); st = os.path.join(t, 'STATUS.tsv')
    h = os.path.join(t, 'harness.sh')
    open(h, 'w').write('set -u\nV=PB3; W=%s; PY=%s; EO=/x/event_outcomes.py; LAB_DAYS=/x; F=/x; G=/x/menu.json; FIRST=20250910; LAST=20251231\n'
                       'T=/x/tools; AP=/x/tools/alarm_process; LIST=$W/PB3_FIRES_V1_LIST.tsv; BASE=; LEAN=FADE; SCREEN=%s\n'
                       'if [ "$SCREEN" = 1 ]; then XS="ALARM"; else XS="ALARM RND"; fi\n'
                       'st(){ printf \'%%s\\t%%s\\t%%s\\t%%s\\n\' "$1" "$2" "$3" "$4" >> %s; }\nrc=0\n' % (w, fake, screen, st)
                       + block(chain))
    env = dict(os.environ, FAKE_LOG=log)
    if fail:
        env['FAKE_FAIL_' + fail] = '7'
    r = subprocess.run(['bash', h], capture_output=True, text=True, env=env, timeout=60)
    ev = {}
    for l in (open(log).read().split('\n') if os.path.exists(log) else []):
        x = l.split(' ')
        if len(x) >= 3:
            ev[(x[0], x[1])] = int(x[2])
    rows = [l.split('\t')[0] for l in open(st).read().split('\n') if l] if os.path.exists(st) else []
    return r.returncode, ev, rows, open(log).read() if os.path.exists(log) else ''


def overlap(ev, a, b):
    return (a, 'start') in ev and (b, 'start') in ev and ev[(a, 'start')] < ev[(b, 'end')] and ev[(b, 'start')] < ev[(a, 'end')]


def suite(gch, mch, gj, mj, parts='gmJ'):
    f = []
    ck = lambda name, ok: None if ok else f.append(name)
    for tag, ch in [x for k, x in (('g', ('GRADE', gch)), ('m', ('MONTH', mch))) if k in parts]:
        with tempfile.TemporaryDirectory() as t:
            rc, ev, rows, log = run_block(ch, t)
            ck('S1 %s exit 0' % tag, rc == 0)
            ck('S1 %s Outcomes runs overlap' % tag, overlap(ev, 'OM_ALARM', 'OM_RND'))
            ck('S1 %s menu and card overlap' % tag, overlap(ev, 'MENU', 'CARD'))
            ck('S1 %s menu and card after both Outcomes' % tag, ('MENU', 'start') in ev and ('CARD', 'start') in ev and
               min(ev[('MENU', 'start')], ev[('CARD', 'start')]) > max(ev.get(('OM_ALARM', 'end'), 0), ev.get(('OM_RND', 'end'), 0)))
            ck('S1 %s STATUS order' % tag, rows == ['outcomes_alarm', 'outcomesRND', 'menu', 'card', 'done'])
        with tempfile.TemporaryDirectory() as t:
            rc, ev, rows, log = run_block(ch, t, fail='OM_ALARM')
            ck('S2 %s exit 6' % tag, rc == 6)
            ck('S2 %s both runs ended' % tag, ('OM_ALARM', 'end') in ev and ('OM_RND', 'end') in ev)
            ck('S2 %s alarm line first, no menu, no card' % tag, rows == ['outcomes_alarm'] and ('MENU', 'start') not in ev and ('CARD', 'start') not in ev)
        with tempfile.TemporaryDirectory() as t:
            rc, ev, rows, log = run_block(ch, t, screen='1')
            ck('S3 %s one run, no menu, card --screen' % tag, rc == 0 and ('OM_RND', 'start') not in ev and ('MENU', 'start') not in ev
               and '--screen' in log and rows == ['outcomes_alarm', 'card', 'done'])
        with tempfile.TemporaryDirectory() as t:
            rc, ev, rows, log = run_block(ch, t, fail='CARD')
            ck('S5 %s a failed card: exit 7, its line has 7' % tag, rc == 7 and rows[-2:] == ['card', 'done'])
    if 'J' not in parts:
        return f
    g = open(gj).read(); m = open(mj).read()
    sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
    ck('S4 GRADE pin', 'ck $CH/alarm_grade_chain_v2_0_5_to20251231.sh %s;' % sha(gch) in g)
    ck('S4 GRADE runs v2_0_5', 'bash $CH/alarm_grade_chain_v2_0_5_to20251231.sh $V $D $W' in g and 'ck $CH/alarm_grade_chain_v2_0_4' not in g
       and 'bash $CH/alarm_grade_chain_v2_0_4' not in g)
    ck('S4 GRADE cores 6', '\n# CORES 6\n' in g)
    ck('S4 GRADE perfire in the background', re.search(r'\( t0=\$\(date \+%s\); \$PY -B \$T/perfire_v1_1_to20260430\.py .*\) &\n    PF\[\$i\]=\$!', g, re.S) is not None)
    ck('S4 GRADE pf_done writes the perfire lines', 'pf_done(){ local V=$1 i=$2 r s n; wait ${PF[$i]}\n' in g and g.count('st perfire_$V $r $s') == 1)
    pd = '[ -n "$PV" ] && pf_done $PV $PI;'
    ck('S4 GRADE V9 order: perfire lines before the next grade line', g.index(pd) < g.index('st grade_$V $r') and pd + ' PV=\n  st grade_$V' in g)
    ck('S4 GRADE V9 order: before the hand-off line and every stop', g.count(pd) == 5 and '& HO=$!' in g and 'wait $HO; r=$?' in g and g.index('& HO=$!') < g.rindex(pd + ' PV=') < g.index('wait $HO; r=$?') < g.index('st handoff $r')
       and pd + ' st disk_$V' in g and pd + ' st disk_handoff' in g and 'else ' + pd + ' st handoff 5' in g)
    ck('S4 GRADE disk stops wait', g.count('wait; st end 7 0 "disk"; exit 7; fi') == 2 and g.count('st end 7 0 "disk"') == 2)
    ck('S4 MONTH pin and run', 'ck $MP/alarm_grade_chain_v2_2_5_to20260430.sh %s;' % sha(mch) in m and 'bash $MP/alarm_grade_chain_v2_2_5_to20260430.sh $V $D $W' in m)
    return f


PLANTS = [   # (which file: g m G M, text, planted text)
    ('g', '  OP+=($!); done\n', '  wait; OP+=($!); done\n'),                                   # Outcomes one after another
    ('m', '  OP+=($!); done\n', '  wait; OP+=($!); done\n'),
    ('g', '2>&1 & PC=$!\n', '2>&1; PC=$!\n'),                                                 # the card not in the background: a hang or no overlap
    ('g', 'OR=(); OS=(); for p in "${OP[@]}"; do wait $p; OR+=($?);', 'OR=(); OS=(); for p in "${OP[@]}"; do OR+=(0);'),   # no wait
    ('g', "  st outcomes${x:-_alarm} $rc ${OS[$i]} $W/om_${V}${x}_v1; i=$((i+1)); [ $rc -eq 0 ] || exit 6; done\n",
          "  st outcomes${x:-_alarm} $rc ${OS[$i]} $W/om_${V}${x}_v1; i=$((i+1)); done\n"),        # a failure not stopped
    ('m', "if [ -n \"$PM\" ]; then st menu $rcm $sm $W/MENU_${V}_om.txt; fi\nst card $rc2 $sc $W/CARD_${V}.txt\n",
          "st card $rc2 $sc $W/CARD_${V}.txt\nif [ -n \"$PM\" ]; then st menu $rcm $sm $W/MENU_${V}_om.txt; fi\n"),   # order changed
    ('G', '# CORES 6\n', '# CORES 3\n'),
    ('G', 'wait; st end 7 0 "disk"; exit 7; fi', 'st end 7 0 "disk"; exit 7; fi'),
    ('G', '  [ -n "$PV" ] && pf_done $PV $PI; PV=\n  st grade_$V', '  st grade_$V'),                       # V9's order lost
    ('G', '2>&1 & HO=$!\n', '2>&1; HO=$!\n'),                                                            # the hand-off not beside perfire
]


def main():
    fails = suite(GCH, MCH, GJ, MJ)
    print('TESTS %s %s' % ('PASS' if not fails else 'FAIL', ' | '.join(fails)))
    files = {'g': GCH, 'm': MCH, 'G': GJ, 'M': MJ}
    killed = 0
    for i, (k, a, b) in enumerate(PLANTS, 1):
        src = open(files[k]).read()
        n = src.count(a)
        if n < 1:
            print('PLANT %d: its text is not in %s' % (i, os.path.basename(files[k]))); continue
        with tempfile.TemporaryDirectory() as t:
            cp = {}
            for kk, p in files.items():
                cp[kk] = os.path.join(t, kk + '_' + os.path.basename(p)); shutil.copyfile(p, cp[kk])
            open(cp[k], 'w').write(src.replace(a, b, 1))
            if k in 'gm':         # a planted chain keeps its template's pin pointing at the real file: test the chain block only
                try:
                    g = suite(cp['g'], cp['m'], GJ, MJ, parts=k)
                except Exception as ex:
                    g = ['a crash (%s)' % type(ex).__name__]
                g = [x for x in g if not x.startswith('S4')]
            else:
                try:
                    g = suite(GCH, MCH, cp['G'], cp['M'], parts='J')
                except Exception as ex:
                    g = ['a crash (%s)' % type(ex).__name__]
        killed += bool(g)
        print('PLANT %d %s' % (i, ('killed by ' + g[0]) if g else 'ALIVE'), flush=True)
    print('PLANTED BUGS %d of %d killed' % (killed, len(PLANTS)))
    return 0 if not fails and killed == len(PLANTS) else 1


if __name__ == '__main__':
    sys.exit(main())
