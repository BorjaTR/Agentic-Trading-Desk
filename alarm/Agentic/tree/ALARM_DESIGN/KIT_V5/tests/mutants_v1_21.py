#!/usr/bin/env python3
"""mutants_v1_21.py (SCOUT, 3 Nov 2026, V1_21 fixes, playground): planted faults on the changed lines only. Each mutant: a copy of the fixes
folder (tools, job, pages) with one text replaced (found exactly once), then test_v1_21_fixes.py run on it (V121_FIX). Killed = the suite
fails. A template mutant re-pins the template's sha16 in the queue copy, so the fault itself is what the tests see. One process at a time.
  python3 -B mutants_v1_21.py [<out.tsv>]
ALARM_V1_21 (SCOUT 3 Nov 2026): runs from the install: each mutant copies Agentic/ and the pages (AGENTS.md, playbook/, cards/) at
the package's own paths; the suite reads every other file from this package (ALARM_BASE); the table goes to the working folder."""
import hashlib, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); FIX = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', '..'))
K = 'Agentic/tree/ALARM_DESIGN/KIT_V5'; TOOLS = K + '/tools/'; TPL = K + '/jobs/JOB_TRUE_V2.job.sh.txt'; Q = TOOLS + 'queue_job_v15.py'
M = [  # (id, file, old, new)
    ('S1a', TOOLS + 'start_run_v1.py', 'DIR_MODE, FILE_MODE = 0o755, 0o644', 'DIR_MODE, FILE_MODE = 0o755, 0o444'),
    ('S1b', TOOLS + 'start_run_v1.py', 'DIR_MODE, FILE_MODE = 0o755, 0o644', 'DIR_MODE, FILE_MODE = 0o555, 0o644'),
    ('S1c', TOOLS + 'start_run_v1.py', '    if os.path.lexists(run):', '    if False:'),
    ('S1d', TOOLS + 'start_run_v1.py', '    if rr == ra or rr.startswith(ra + os.sep):', '    if False:'),
    ('S1e', TOOLS + 'start_run_v1.py', "        if sha16(dst) != s:", "        if False:"),
    ('S1f', TOOLS + 'start_run_v1.py', "        os.chmod(dst, FILE_MODE)\n", "        pass\n"),
    ('S2a', TOOLS + 'start_run_v1.py', "            hint = ': write %s_%s' % (seat, mm.group(2))", "            hint = ''"),
    ('S2b', TOOLS + 'start_run_v1.py', "            datetime.datetime.strptime(m.group(2), '%Y%m%d')", "            int(m.group(2))"),
    ('S2c', Q, "at most 12, no underscore (SCOUT_R12 is written SCOUTR12)' % runtag)", "at most 12 (SCOUT_R12 is written SCOUTR12)' % runtag)"),
    ('S2d', 'playbook/LAUNCH_PROMPT_ALARM_V1.md', 'at most 12, no underscore (seat SCOUT_R12', 'at most 12 (seat SCOUT_R12'),
    ('S3a', Q, "KINDS = ('COUNT', 'GRADE', 'ENTRY', 'MONTH', 'FIRSTLOOK', 'TRUE')", "KINDS = ('COUNT', 'GRADE', 'ENTRY', 'MONTH', 'FIRSTLOOK')"),
    ('S3b', Q, "        if '%s=%s' % (n, true_digest(cl[k])) not in card:", "        if False:"),
    ('S3c', Q, "        if cl.get(k) != w:", "        if False:"),
    ('S3d', Q, "    if cl.get('perfire_sha16') != seal:", "    if False:"),
    ('S3e', Q, "    if sha16(here) != seal:", "    if False:"),
    ('S3f', Q, "and stage_ok(run, r.get('receipts_rel'), v, 'TRUE') is not False for r in runs):", "and False for r in runs):"),
    ('S3g', Q, "['true_' + v] if kind == 'TRUE'", "['grade_' + v] if kind == 'TRUE'"),
    ('S3h', Q, "r'^ideas/%s/TRUE_%s_([A-Z][A-Z0-9]{0,23})\\.json$' % (re.escape(idea), re.escape(v))", "r'^ideas/%s/TRUE_[A-Z0-9]+_([A-Z][A-Z0-9]{0,23})\\.json$' % (re.escape(idea),)"),
    ('S3i', Q, "        if lost:\n            raise Refused('SOURCE SEAL LOST FOR %s IN %s: %s' %", "        if False:\n            raise Refused('SOURCE SEAL LOST FOR %s IN %s: %s' %"),
    ('S3j', Q, "        there = there.replace(k, x)", "        pass"),
    ('S3k', TPL, 'one true_$V $PY', 'one truex_$V $PY'),
    ('S3l', TPL, '  if [ $r -ne 0 ]; then stop $r "$S failed"; fi; }', '  true; }'),
    ('S3m', TPL, 'ck $PFSRC $PFSHA\n', '\n'),
    ('S3n', TPL, 'ck $CL $CSHA\n', '\n'),
    ('S4a', TOOLS + 'decide_v5.py', "        out['note'] += '; money not read (no --entry): money is information only, the strategy stage'", "        raise Refused('%s HAS R1: run its ENTRY job first' % v)"),
    ('S4b', TOOLS + 'decide_v5.py', "'; money not read (no --entry)", "'; (no --entry)"),
    ('S4c', TOOLS + 'decide_v5.py', "    elif out['state'] in ('PASS', 'NEEDS MORE MONTHS'):", "    if out['state'] in ('PASS', 'NEEDS MORE MONTHS'):"),
    ('S4d', TOOLS + 'audit_run_v5.py', "V3.CFG['DECIDE'] = os.path.join(", "V3.CFG['DECIDE_X'] = os.path.join("),
    ('S5a', TOOLS + 'ledger_add_v7.py', "            if OWN_ID.match(f[1]):", "            if False:"),
    ('S5b', TOOLS + 'ledger_add_v7.py', "            WARNINGS.append('%s line %d repeats", "            raise ValueError('%s line %d repeats"),
    ('S5c', TOOLS + 'ledger_add_v7.py', "        if len(f) != len(COLS):", "        if False:"),
    ('S5d', TOOLS + 'ledger_add_v7.py', "            print(msg, file=sys.stderr); return 2", "            print(msg, file=sys.stderr); return 1"),
    ('S5e', TOOLS + 'ledger_add_v7.py', "        print('REFUSED %s' % e, file=sys.stderr); return 2", "        raise"),
    ('S5f', TOOLS + 'ledger_add_v7.py', "LEDGER = os.path.join(S.get(settings, 'RESEARCH_ROOT'), 'TRIES_LEDGER_V1.tsv')", "LEDGER = os.path.join(S.get(settings, 'RESEARCH_ROOT'), 'TRIES_LEDGER.tsv')"),
    ('S5g', TOOLS + 'ledger_add_v7.py', "return 0 if ok else 3", "return 0"),
    ('S5h', TOOLS + 'ledger_add_v7.py', "        if a and a[0] == 'door':", "        if False:"),
    ('S5i', TOOLS + 'ledger_add_v7.py', "    except OSError as e:\n        print('REFUSED FILE: %s' % e, file=sys.stderr); return 2", "    except ZeroDivisionError as e:\n        print('REFUSED FILE: %s' % e, file=sys.stderr); return 2"),
]


def s16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def main(out):
    base_tpl = s16(os.path.join(FIX, TPL)); rows = []
    for mid, rel, old, new in M:
        d = tempfile.mkdtemp(prefix='v121m_%s_' % mid)
        for sub in ('Agentic', 'playbook', 'cards'):
            shutil.copytree(os.path.join(FIX, sub), os.path.join(d, sub), ignore=shutil.ignore_patterns('*.pre_*', '__pycache__'))
        shutil.copyfile(os.path.join(FIX, 'AGENTS.md'), os.path.join(d, 'AGENTS.md'))
        for w, ds, fs in os.walk(d):          # ALARM_V1_21_1: the install is read-only and copytree keeps its modes
            os.chmod(w, 0o755)
            for x in fs:
                os.chmod(os.path.join(w, x), 0o644)
        p = os.path.join(d, rel); t = open(p).read()
        if t.count(old) != 1:
            rows.append((mid, rel, 'NOT FOUND %d' % t.count(old), '')); continue
        open(p, 'w').write(t.replace(old, new))
        if rel == TPL:
            qp = os.path.join(d, Q); q = open(qp).read(); open(qp, 'w').write(q.replace(base_tpl, s16(p)))
        r = subprocess.run([sys.executable, '-B', '-W', 'ignore', os.path.join(d, K, 'tests/test_v1_21_fixes.py')], capture_output=True, text=True,
                           env=dict(os.environ, V121_FIX=d, ALARM_BASE=FIX), cwd=d)
        failed = [l.split(' (')[0] for l in r.stderr.splitlines() if l.endswith('... FAIL') or l.endswith('... ERROR')]
        rows.append((mid, rel, 'KILLED' if r.returncode else 'SURVIVED', ','.join(failed)))
        print(mid, rows[-1][2], ','.join(failed)[:150], flush=True)
    with open(out, 'x') as f:
        f.write('mutant\tfile\tresult\tfailing_tests\n' + ''.join('\t'.join(x) + '\n' for x in rows))
    k = sum(1 for x in rows if x[2] == 'KILLED'); s = sum(1 for x in rows if x[2] == 'SURVIVED'); n = len(rows) - k - s
    print('MUTANTS %d: killed %d, survived %d, not found %d -> %s' % (len(rows), k, s, n, out))
    return 0 if s == 0 and n == 0 else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.getcwd(), 'MUTANTS_v1_21.tsv')))
