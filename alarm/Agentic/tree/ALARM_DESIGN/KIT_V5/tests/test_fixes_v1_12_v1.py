#!/usr/bin/env python3
"""test_fixes_v1_12_v1.py (SCOUT, 31 Oct 2026, ALARM_V1_12; TEST, NOT REVIEWED): the fixes edition, each fix run on the code that
ships it, and each case also run on the past edition where it must fail (red), so the test proves the fix and not only the new text.
  F1 JOB_ENTRY_V7's own lines (marked V1_12 F1): the chain folder is the one the store run made, even when another job's folder is newer;
     none or two new folders: stage chain_<V> 8 and no folder. V6's line (ls -dt | head -1) takes the newer foreign folder (red).
  F3 the end lines (V1_12 F3) of JOB_COUNT_V7, JOB_GRADE_V13, JOB_ENTRY_V7, JOB_MONTH_V13: a failed stage 3 -> end 3 and exit 3; all 0 -> 0.
     The past templates' end lines exit 0 after the failed stage (red).
  F4 the gate lines (V1_12 F4) of the same four: FEED_GATE naming a missing file -> stage gate 8, end 8, exit 8; an existing file and an
     empty FEED_GATE go on. The past templates have no such lines (a missing gate went on to gate_wait's PAUSE).
  F2 decide_forward_v3.read_month on a line "15m ... gap na | other side gap +3.2" reads na; v2 reads +3.2 (red); on lines without
     na both read the same.
  S1 decide_v3.run_budget_mb reads queue_job_v11.py next to it (10000); decide_v2 reads queue_job_v5.py: alone beside queue_job_v11
     it reads nothing (red).
The template lines run in bash with only st() and small stand-ins (fmb, W, du); every file is planted in a new temporary folder.
  python3 -B <Alarm>/Agentic/tree/ALARM_DESIGN/KIT_V5/tests/test_fixes_v1_12_v1.py      exit 0 all pass, 1 a check failed"""
import importlib.util, os, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__)); KIT = os.path.dirname(HERE)
JOBS, TOOLS = os.path.join(KIT, 'jobs'), os.path.join(KIT, 'tools')
NEW = {'COUNT': 'JOB_COUNT_V7', 'GRADE': 'JOB_GRADE_V13', 'ENTRY': 'JOB_ENTRY_V7', 'MONTH': 'JOB_MONTH_V13'}
OLD = {'COUNT': 'JOB_COUNT_V6', 'GRADE': 'JOB_GRADE_V12', 'ENTRY': 'JOB_ENTRY_V6', 'MONTH': 'JOB_MONTH_V12'}
FAILS = []


def ck(ok, what):
    print('%s %s' % ('PASS' if ok else 'FAIL', what))
    if not ok:
        FAILS.append(what)


def tpl(name):
    return open(os.path.join(JOBS, name + '.job.sh.txt')).read().split('\n')


def st_line(lines):
    return [l for l in lines if l.startswith('st(){')][0]


def bash(script, cwd):
    p = subprocess.run(['bash', '-c', script], cwd=cwd, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    return p.returncode, p.stdout + p.stderr


def stages(d):
    return [l.split('\t')[:2] for l in open(os.path.join(d, 'STAGES.tsv')).read().split('\n')[1:] if l]


HEAD = "set -u\nST=$PWD/STAGES.tsv; printf 'stage\\trc\\tseconds\\tutc\\tnote\\n' > $ST\n"


def gate_case(name, lines, gate):
    d = tempfile.mkdtemp(prefix='f4_')
    f4 = [l for l in lines if l.rstrip().endswith('# V1_12 F4')]
    body = HEAD + st_line(lines) + '\n' + '\n'.join(f4).replace('@@FEED_GATE@@', gate.replace('@D', d)) + '\necho WENT_ON\n'
    if gate.startswith('@D/real'):
        open(os.path.join(d, 'real'), 'w').write('RUN\n')
    rc, out = bash(body, d)
    return rc, out, stages(d), len(f4)


def end_case(lines, rcs):
    d = tempfile.mkdtemp(prefix='f3_')
    i = [k for k, l in enumerate(lines) if l.startswith('E=$(awk') and 'V1_12 F3' in l]
    tail = lines[i[0]:i[0] + 3] if i else [l for l in lines if l.startswith('st end 0 0')][-1:] + ['exit 0']
    pre = HEAD + st_line(lines) + '\n' + 'fmb(){ echo 123; }; W=$PWD; FMB=1; WMB=1\n'
    pre += ''.join("st s%d %s 0 x\n" % (k, r) for k, r in enumerate(rcs))
    rc, out = bash(pre + '\n'.join(tail) + '\n', d)
    return rc, stages(d)


for kind in ('COUNT', 'GRADE', 'ENTRY', 'MONTH'):
    new, old = tpl(NEW[kind]), tpl(OLD[kind])
    ck(NEW[kind] in new[0], 'header names %s' % NEW[kind])
    i_f4 = [k for k, l in enumerate(new) if l.rstrip().endswith('# V1_12 F4')]
    i_start = [k for k, l in enumerate(new) if l.startswith('f=$(fmb); st start 0 0')]
    ck(len(i_f4) == 2 and len(i_start) == 1 and i_f4[-1] < i_start[0], '%s F4: 2 gate lines before the start line' % kind)
    rc, out, sg, n = gate_case(kind, new, '@D/missing_gate.txt')
    ck(rc == 8 and ['gate', '8'] in sg and ['end', '8'] in sg and 'WENT_ON' not in out, '%s F4: a missing FEED_GATE stops with 8' % kind)
    rc, out, sg, n = gate_case(kind, new, '@D/real')
    ck(rc == 0 and 'WENT_ON' in out and not sg, '%s F4: an existing gate file goes on' % kind)
    rc, out, sg, n = gate_case(kind, new, '')
    ck(rc == 0 and 'WENT_ON' in out, '%s F4: an empty FEED_GATE (no gate) goes on' % kind)
    rc, out, sg, n = gate_case(kind, old, '@D/missing_gate.txt')
    ck(n == 0 and rc == 0 and 'WENT_ON' in out, '%s F4 red: %s has no gate check (a missing gate went on to wait)' % (kind, OLD[kind]))
    rc, sg = end_case(new, ['0', '3', '0', '5'])
    ck(rc == 3 and sg[-1] == ['end', '3'], '%s F3: the first failed stage (3) is the end code and the exit code' % kind)
    rc, sg = end_case(new, ['0', '0'])
    ck(rc == 0 and sg[-1] == ['end', '0'], '%s F3: every stage 0 -> end 0, exit 0' % kind)
    rc, sg = end_case(old, ['0', '3'])
    ck(rc == 0 and sg[-1] == ['end', '0'], '%s F3 red: %s ends 0 after a failed stage' % (kind, OLD[kind]))
    ck(not [l for l in new if l.startswith('st end 0 0')], '%s F3: no end line with a fixed 0 is left' % kind)

# F1: ENTRY's chain folder
new, old = tpl('JOB_ENTRY_V7'), tpl('JOB_ENTRY_V6')
f1 = [l for l in new if l.rstrip().endswith('# V1_12 F1') or 'V1_12 F1:' in l]
ck(len(f1) == 3, 'F1: 3 marked lines in JOB_ENTRY_V7')


def f1_case(lines, made):
    d = tempfile.mkdtemp(prefix='f1_'); ch = os.path.join(d, 'scratch', 'work_TOOLTRIAL', 'chain'); os.makedirs(ch); os.makedirs(os.path.join(d, 'K'))
    foreign = os.path.join(ch, 'ALM_S_V1_SD_20250910_20251231_20261031T100000Z'); os.makedirs(foreign)    # another job's folder, there before
    before = [l for l in lines if 'chain_before.txt' in l and l.lstrip().startswith('ls -d')]
    after = [l for l in lines if l.lstrip().startswith('CD=$(ls')] + [l for l in lines if l.lstrip().startswith('NC=')]
    run = ''.join('mkdir -p %s/ALM_S_V1_SD_20250910_20251231_20261031T12%02d00Z\n' % (ch, k) for k in range(made))
    run += 'touch -t 203001010000 %s\n' % foreign                                                           # the foreign folder is the newest
    body = HEAD + st_line(lines) + '\nAID=ALM_S_V1_SD; K=$PWD/K; V=V1\n' + '\n'.join(before) + '\n' + run + '\n'.join(after) + '\necho "CD=$CD"\n'
    rc, out = bash(body.replace('@@SCRATCH@@', os.path.join(d, 'scratch')), d)
    cd = [l[3:] for l in out.split('\n') if l.startswith('CD=')]
    return (cd[-1] if cd else None), stages(d), foreign


cd, sg, foreign = f1_case(new, 1)
ck(cd and cd.endswith('_20261031T120000Z') and not sg, 'F1: the folder this run made, though another job\'s folder is newer')
cd, sg, foreign = f1_case(new, 2)
ck(cd == '' and ['chain_V1', '8'] in sg, 'F1: two new folders -> stage chain_V1 8 and no folder')
cd, sg, foreign = f1_case(new, 0)
ck(cd == '' and ['chain_V1', '8'] in sg, 'F1: no new folder -> stage chain_V1 8 and no folder')
cd, sg, foreign = f1_case(old, 1)
ck(cd == foreign, 'F1 red: JOB_ENTRY_V6 takes the newest folder, another job\'s')


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path)
    assert sp is not None and sp.loader is not None, path
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


# F2
d = tempfile.mkdtemp(prefix='f2_')
na = os.path.join(d, 'na.txt'); open(na, 'w').write('VERDICT HOLDS\nwaves 12\n  15m  a 1.0 r 2.0 gap na | other side gap +3.2\n  1h  a 1.0 r 2.0 gap -0.5\n')
ok = os.path.join(d, 'ok.txt'); open(ok, 'w').write('VERDICT HELD\nwaves 31\n  15m  a 1.0 r 2.0 gap +1.25 | other side gap +3.2\n  1h  a 1.0 r 2.0 gap -0.5\n')
v3 = load(os.path.join(TOOLS, 'decide_forward_v3.py'), 'dfv3'); v2 = load(os.path.join(TOOLS, 'decide_forward_v2.py'), 'dfv2')
ck(v3.read_month(na)[2] == 'na' and v3.read_month(na)[3] == '-0.5', 'F2: "gap na" reads na; the 1h gap stays its own')
ck(v2.read_month(na)[2] == '+3.2', 'F2 red: decide_forward_v2 reads the other side\'s +3.2')
ck(v3.read_month(ok) == v2.read_month(ok) == ('HELD', 31, '+1.25', '-0.5'), 'F2: without na, v3 reads what v2 reads')

# S1
d = tempfile.mkdtemp(prefix='s1_')
for n in ('decide_v2.py', 'decide_v3.py', 'queue_job_v11.py'):
    shutil.copy(os.path.join(TOOLS, n), os.path.join(d, n))
d3 = load(os.path.join(d, 'decide_v3.py'), 'dv3'); d2 = load(os.path.join(d, 'decide_v2.py'), 'dv2')
d3.CFG['RUN_BUDGET_MB'] = None; d2.CFG['RUN_BUDGET_MB'] = None
ck(d3.run_budget_mb() == 10000, 'S1: decide_v3 reads the run budget 10000 from queue_job_v11.py')
ck(d2.run_budget_mb() is None, 'S1 red: decide_v2 reads queue_job_v5.py: beside queue_job_v11 alone it reads nothing')
ck('queue_job_v5' not in open(os.path.join(TOOLS, 'decide_v3.py')).read().split('"""', 2)[2], 'S1: decide_v3\'s code names no queue_job_v5')

print('FIXES V1_12: %s' % ('ALL PASS' if not FAILS else '%d FAILED' % len(FAILS)))
sys.exit(1 if FAILS else 0)
