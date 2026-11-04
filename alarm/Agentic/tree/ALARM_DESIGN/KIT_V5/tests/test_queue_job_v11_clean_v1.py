#!/usr/bin/env python3
"""test_queue_job_v11_clean_v1.py (SCOUT, ALARM_V1_12, from test_queue_job_v10_clean_v1.py ffb96687c0dc7b54: queue_job_v11, MONTH 3813). test_queue_job_v10_clean_v1.py (BUILD5 for ALARM_V1_10, by make_jobs_v12.py from test_queue_job_v9_clean_v1.py 58d71ae6: queue_job_v10, MONTH 3758, load() checks its spec; the rest is SCOUT's text): test_queue_job_v8_clean_v1.py 64da7d0316f7f11f on queue_job_v10.py (ALARM_V1_9 D1; v8's: ALARM_V1_8,
speed stage 1), Q5 with GRADE's two measured values. v7's tests: its changes after the owner 31 Oct
2026 10:51 Berlin (of CLEAN: "remove it"; scratch cleanup is DSK's, on the owner's word):
  Q1  KIND CLEAN is refused by name: exit 2, stderr 'REFUSED: CLEAN REMOVED: the owner 31 Oct 2026 10:51 Berlin; ...', nothing on stdout,
      before any settings file is read (the --settings file named does not exist); an unknown KIND names the four kinds, no CLEAN.
  Q2  CLEAN is in none of KINDS, TEMPLATE_SHA, TEMPLATE_NAME; COUNT, GRADE, ENTRY and MONTH keep one template each.
  Q3  the disk budget (scratch_used) on a planted run: a finished job counts its DISK.tsv du_mb_W plus its STORE_PLACES du_mb while its
      scratch folder SCRATCH/work_<RUN>/<JOB> is on SCRATCH_DISK, 0 once that folder is gone, and its measured MB again when SCRATCH_DISK is not
      visible from here (or not set); a job not finished counts its declared writes_mb; a CLEAN row and a CLEANED_BY job count nothing.
  Q4  the DISK BUDGET refusal names DSK and no longer asks for CLEAN.
  Q5  GRADE's MEM_MB is 2879 for 1 variant and 3000 for 2 or 3 (job 20265194: tree peaks 2399 and 2500 MB
      + 20 percent; V11, D1), COUNT's 6000, MONTH's 3758 (job 20265205: its tree peak 3131 MB + 20 percent, job 20265289; DSK's review M1).
Then planted bugs in copies of queue_job_v10.py, each in a planted Alarm package (its _tools/settings_v1.py and settings/): each must
fail a test. Temp folders only, removed after; reads no market data; seconds.
  python3 -B <Alarm>/Agentic/tree/ALARM_DESIGN/KIT_V5/tests/test_queue_job_v11_clean_v1.py"""
import importlib.util, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
QFILE = os.path.join(HERE, '..', 'tools', 'queue_job_v11.py')
PKG = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..'))
SV = os.path.join(PKG, '_tools', 'settings_v1.py')
RUN = 'AD1_20261029'
N = [0]


def load(qfile):
    N[0] += 1
    sp = importlib.util.spec_from_file_location('queue_job_v11_clean_test_%d' % N[0], qfile)
    assert sp is not None and sp.loader is not None, qfile           # v10 (SCOUT 14:54:32Z): pyright Optional
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def plant_run(root):
    """a run with a finished GRADE (DISK.tsv 1000, STORE_PLACES 50), a COUNT not finished (writes_mb 300), a CLEAN row with a DISK.tsv"""
    run = os.path.join(root, 'runs', RUN)
    g = os.path.join(run, 'receipts', '1_GRADE_X')
    os.makedirs(os.path.join(g, 'V1'))
    open(os.path.join(g, 'DISK.tsv'), 'w').write('du_mb_W\t1000\t/w\ndu_mb_receipts\t9\n')
    open(os.path.join(g, 'V1', 'STORE_PLACES.tsv'), 'w').write('du_mb\t50\t/s\n')
    os.makedirs(os.path.join(run, 'receipts', '2_COUNT_X'))
    c = os.path.join(run, 'receipts', '3_CLEAN_X')
    os.makedirs(c)
    open(os.path.join(c, 'DISK.tsv'), 'w').write('du_mb_W\t700\n')
    rows = [{'kind': 'GRADE', 'receipts_rel': 'receipts/1_GRADE_X', 'writes_mb': '1800'},
            {'kind': 'COUNT', 'receipts_rel': 'receipts/2_COUNT_X', 'writes_mb': '300'},
            {'kind': 'CLEAN', 'receipts_rel': 'receipts/3_CLEAN_X', 'writes_mb': '10'}]
    return run, {'RUNS': rows}


def suite(qfile):
    f = []
    def ck(name, ok):
        if not ok:
            f.append(name)
    r = subprocess.run([sys.executable, '-B', qfile, '--settings', '/nonexistent_scout/SETTINGS_X.env', RUN, 'CLEAN', 'LABEL',
                        '20263700_GRADE_FLOWX'], capture_output=True, text=True)
    ck('Q1 rc 2', r.returncode == 2)
    ck('Q1 refused by name', r.stderr.startswith("REFUSED: CLEAN REMOVED: the owner 31 Oct 2026 10:51 Berlin; scratch cleanup is DSK's"))
    ck('Q1 nothing on stdout', r.stdout == '')
    r = subprocess.run([sys.executable, '-B', qfile, '--settings', '/nonexistent_scout/SETTINGS_X.env', RUN, 'FOO', 'LABEL', 'X'],
                       capture_output=True, text=True)
    ck('Q1 unknown kind names the four', r.returncode == 2 and "KIND 'FOO': one of COUNT, GRADE, ENTRY, MONTH\n" in r.stderr)
    m = load(qfile)
    ck('Q2 KINDS', tuple(m.KINDS) == ('COUNT', 'GRADE', 'ENTRY', 'MONTH'))
    ck('Q2 no CLEAN template', 'CLEAN' not in m.TEMPLATE_SHA and 'CLEAN' not in m.TEMPLATE_NAME)
    ck('Q2 one template a kind', set(m.TEMPLATE_SHA) == set(m.TEMPLATE_NAME) == set(m.KINDS))
    with tempfile.TemporaryDirectory() as t:
        run, regs = plant_run(t)
        wdb = os.path.join(t, 'wdb')
        w = os.path.join(wdb, 'work_' + RUN, '1_GRADE_X')
        os.makedirs(w)
        m.CFG['WDB'] = wdb
        ck('Q3 there: measured + declared', m.scratch_used(run, regs) == 1350)
        ck('Q3 there, regs read from the run argument', m.scratch_gone(run + '/', os.path.join(run, 'receipts', '1_GRADE_X') + '/') is False)
        os.rename(w, w + '_swept')
        ck('Q3 gone: 0 + declared', m.scratch_used(run, regs) == 300)
        m.CFG['WDB'] = os.path.join(t, 'not_visible')
        ck('Q3 not visible: counted', m.scratch_used(run, regs) == 1350)
        m.CFG['WDB'] = None
        ck('Q3 not set: counted', m.scratch_used(run, regs) == 1350)
        m.CFG['WDB'] = wdb
        os.rename(w + '_swept', w)
        open(os.path.join(run, 'receipts', '1_GRADE_X', 'CLEANED_BY.txt'), 'w').write('x\n')
        ck('Q3 CLEANED_BY: 0 + declared', m.scratch_used(run, regs) == 300)
    src = open(qfile).read()
    line = [l for l in src.split('\n') if "raise Refused('DISK BUDGET:" in l]
    ck('Q4 one DISK BUDGET refusal', len(line) == 1)
    ck('Q4 names DSK, not CLEAN', len(line) == 1 and 'DSK' in line[0] and 'CLEAN' not in line[0])
    ck('Q5 GRADE 2879 or 3000', src.count("sub.update({'@@WMB@@': str(1800 * n), '@@MMB@@': '2879' if n == 1 else '3000', ") == 1)
    ck('Q5 COUNT 6000', src.count("sub.update({'@@WMB@@': str(300 * n), '@@MMB@@': '6000', ") == 1)
    ck('Q5 MONTH 3813', src.count("sub.update({'@@WMB@@': str(3000 * n), '@@MMB@@': '3813', ") == 1)
    return f


PLANTS = [
    ("    if kind == 'CLEAN':\n        raise Refused(CLEAN_REMOVED)\n", ""),
    ("KINDS = ('COUNT', 'GRADE', 'ENTRY', 'MONTH')\n", "KINDS = ('COUNT', 'GRADE', 'ENTRY', 'MONTH', 'CLEAN')\n"),
    ("TEMPLATE_SHA = {'COUNT': '9acb9c0c2b241320', ", "TEMPLATE_SHA = {'COUNT': '9acb9c0c2b241320', 'CLEAN': '604cbe0b9254a8b1', "),
    ("    return bool(w) and os.path.isdir(w) and not os.path.isdir(", "    return False and not os.path.isdir("),
    ("    return bool(w) and os.path.isdir(w) and not os.path.isdir(", "    return bool(w) and not os.path.isdir("),
    ("                                                                       os.path.basename(d.rstrip('/'))))",
     "                                                                       os.path.basename(run.rstrip('/'))))"),
    ("        dk = os.path.join(d, 'DISK.tsv')\n        if os.path.isfile(dk):\n            if scratch_gone(run, d):\n",
     "        if scratch_gone(run, d):\n            continue\n        dk = os.path.join(d, 'DISK.tsv')\n        if os.path.isfile(dk):\n            if False:\n"),
    ("scratch cleanup is done by DSK (the owner 31 Oct 2026 10:51 Berlin): ask DSK on the board (hb/DSK.txt) and wait for its sweep'",
     "decide your finished jobs and CLEAN them first'"),
    ("'@@MMB@@': '2879' if n == 1 else '3000', ", "'@@MMB@@': '2879', "),
]


def planted_package(t, text):
    a = os.path.join(t, 'Alarm')
    os.makedirs(os.path.join(a, '_tools')); os.makedirs(os.path.join(a, 'settings'))
    shutil.copyfile(SV, os.path.join(a, '_tools', 'settings_v1.py'))
    q = os.path.join(a, 'Agentic', 'tree', 'ALARM_DESIGN', 'KIT_V5', 'tools', 'queue_job_v11.py')
    os.makedirs(os.path.dirname(q))
    open(q, 'w').write(text)
    return q


if __name__ == '__main__':
    fails = suite(QFILE)
    print('TESTS %s %s' % ('PASS' if not fails else 'FAIL', ' | '.join(fails)))
    src = open(QFILE).read()
    killed = 0
    with tempfile.TemporaryDirectory() as t:
        ctl = suite(planted_package(os.path.join(t, 'control'), src))
        print('CONTROL (the real text in a planted package) %s' % ('PASS' if not ctl else 'FAIL ' + ' | '.join(ctl)))
    for i, (a, b) in enumerate(PLANTS, 1):
        if src.count(a) != 1:
            print('PLANT %d: its text is found %d times, want 1' % (i, src.count(a))); continue
        with tempfile.TemporaryDirectory() as t:
            try:
                g = suite(planted_package(t, src.replace(a, b)))
            except Exception as ex:
                g = ['a crash (%s)' % type(ex).__name__]
        killed += bool(g)
        print('PLANT %d %s' % (i, ('killed by ' + g[0]) if g else 'ALIVE'))
    print('PLANTED BUGS %d of %d killed' % (killed, len(PLANTS)))
    sys.exit(0 if not fails and not ctl and killed == len(PLANTS) else 1)
