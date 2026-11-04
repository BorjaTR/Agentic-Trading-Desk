#!/usr/bin/env python3
"""mutants_menu_gate_v1.py (SCOUT, 3 Nov 2026): planted bugs in menu_gate_v1.py, queue_job_v16.py and decide_v6.py; test_menu_gate_v1.py
must fail on each. Each mutant replaces one exact text (found once) in a copy of the three tools and runs the suite with MENU_FIX on the
copy; the unpatched copy must pass first. Prints one line per mutant, then MUTANTS <killed> of <n> killed; exit 0 only when all are killed.
  python3 -B mutants_menu_gate_v1.py            (MENU_FIX: the tools folder, default KIT_V5/tools of this package; ALARM_BASE as the suite)"""
import os, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.environ.get('MENU_FIX') or os.path.normpath(os.path.join(HERE, '..', 'tools'))
TEST = os.path.join(HERE, 'test_menu_gate_v1.py')
NEW = ('menu_gate_v1.py', 'queue_job_v16.py', 'decide_v6.py')
M = [
    ('M01 pickable NO passes', 'menu_gate_v1.py', "        if row['pickable'] == 'YES':\n            continue\n", "        if row['pickable'] in ('YES', 'NO'):\n            continue\n"),
    ('M02 exception not recorded passes', 'menu_gate_v1.py', "        if reason is not None and code not in rec:\n", "        if False:\n"),
    ('M03 no reason needed', 'menu_gate_v1.py', "MIN_REASON = 12\n", "MIN_REASON = 0\n"),
    ('M04 a code twice on the card', 'menu_gate_v1.py', "        if code in out:\n            raise Refused('BAD_EXCEPTION'", "        if False:\n            raise Refused('BAD_EXCEPTION'"),
    ('M05 the TRUE label not read', 'menu_gate_v1.py', "    dc = def_codes(def_path, T); lc = claim_codes(claim_path, T) if claim_path else set()\n", "    dc = def_codes(def_path, T); lc = set()\n"),
    ('M06 a changed menu read', 'menu_gate_v1.py', "    if want and sha16(path) != want:\n", "    if False:\n"),
    ('M07 any exception covers', 'menu_gate_v1.py', "        if code not in exc:\n", "        if not exc:\n"),
    ('M08 exception lines not printed', 'menu_gate_v1.py', "        out.append('MENU EXCEPTION %s (%s): %s' % (c, s, why))\n", "        pass\n"),
    ('M09 unknown op read as nothing', 'menu_gate_v1.py', "    except T.Refused as e:\n        raise Refused('UNREADABLE_DEF'", "    except T.Refused as e:\n        return set()\n        raise Refused('UNREADABLE_DEF'"),
    ('M18 a reader from the environment', 'menu_gate_v1.py', "TG1 = os.path.join(PKG, '03_Grading/tree/tools/true_gate/true_gate_v1.py')\n", "TG1 = os.environ.get('MENU_GATE_TG') or os.path.join(PKG, '03_Grading/tree/tools/true_gate/true_gate_v1.py')\n"),
    ('M19 any reader bytes', 'menu_gate_v1.py', "        if hashlib.sha256(src).hexdigest()[:16] != want:\n", "        if False:\n"),
    ('M20 a claim of any shape', 'menu_gate_v1.py', "    if not isinstance(c, dict):\n        raise Refused('UNREADABLE_CLAIM'", "    if False:\n        raise Refused('UNREADABLE_CLAIM'"),
    ('M21 decide: lines after the write', 'decide_v6.py', "    lines = safe_menu_lines(sys.argv[1:])\n    try:\n        rc = D.main(sys.argv[1:])\n", "    try:\n        rc = D.main(sys.argv[1:])\n        lines = menu_lines(os.path.join(D.CFG['H'], 'runs', sys.argv[3]), sys.argv[4], sys.argv[5])\n"),
    ('M22 decide: a fault in the lines stops it', 'decide_v6.py', "    except Exception as e:                                   # a diagnostic", "    except ZeroDivisionError as e:                           # a diagnostic"),
    ('M10 queue: TRUE not gated', 'queue_job_v16.py', "GATED = ('GRADE', 'TRUE', 'ENTRY', 'MONTH', 'FIRSTLOOK')\n", "GATED = ('GRADE', 'ENTRY', 'MONTH', 'FIRSTLOOK')\n"),
    ('M11 queue: GRADE reads no claim', 'queue_job_v16.py', "    if kind == 'GRADE':\n", "    if False:\n"),
    ('M12 queue: refusal only printed', 'queue_job_v16.py', "                raise Q.Refused('MENU GATE %s: %s%s' %", "                print('MENU GATE %s: %s%s' %"),
    ('M13 queue: any v15 runs', 'queue_job_v16.py', "if not os.path.isfile(V15) or _sha16(V15) != V15_SHA:\n", "if not os.path.isfile(V15):\n"),
    ('M14 queue: COUNT gated', 'queue_job_v16.py', "    if kind not in GATED:\n", "    if kind not in GATED + ('COUNT',):\n"),
    ('M15 decide: no menu lines', 'decide_v6.py', "    for l in lines:\n        print(l)\n", "    for l in []:\n        print(l)\n"),
    ('M16 decide: a refused gate stops the decision', 'decide_v6.py', "            out.append('MENU GATE %s: REFUSED %s (printed only; the decision above stands)' % (name, e))\n", "            raise SystemExit(3)\n"),
    ('M17 decide: any v5 runs', 'decide_v6.py', "if not os.path.isfile(V5) or _sha16(V5) != V5_SHA:\n", "if not os.path.isfile(V5):\n"),
]


def suite(d):
    return subprocess.run([sys.executable, '-B', TEST], capture_output=True, text=True, env=dict(os.environ, MENU_FIX=d)).returncode


def main():
    src = {n: open(os.path.join(FIX, n)).read() for n in NEW}
    with tempfile.TemporaryDirectory() as t:
        plain = os.path.join(t, 'plain'); os.makedirs(plain)
        for n in NEW:
            shutil.copyfile(os.path.join(FIX, n), os.path.join(plain, n))
        if suite(plain) != 0:
            print('UNPATCHED COPY FAILS: no mutant is meaningful'); return 3
        killed = 0
        for i, (name, f, a, b) in enumerate(M):
            if src[f].count(a) != 1:
                print('%s\tNOT FOUND (%d)' % (name, src[f].count(a))); continue
            d = os.path.join(t, 'm%02d' % i); os.makedirs(d)
            for n in NEW:
                with open(os.path.join(d, n), 'w') as g:
                    g.write(src[n].replace(a, b) if n == f else src[n])
            rc = suite(d); killed += rc != 0
            print('%s\t%s' % (name, 'KILLED' if rc else 'SURVIVED'))
    print('MUTANTS %d of %d killed' % (killed, len(M)))
    return 0 if killed == len(M) else 3


if __name__ == '__main__':
    sys.exit(main())
