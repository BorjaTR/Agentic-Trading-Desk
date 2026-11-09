#!/usr/bin/env python3
"""mutants_v1.py (SCO-A153): one mutant per refusal and per rule of alarm_pipeline_v1 / card_v1 / mechanism_v1; each mutant is a copy of
the tool folder under tests/mutants/<id>/ (kept) with one edit, run against the one test that names the refusal. KILLED = the test fails.
  python3 -B mutants_v1.py [first last]      (1-based, inclusive; each call stays under 60 s by taking a range)"""
import sys
sys.dont_write_bytecode = True
import os, shutil, subprocess

T = os.path.dirname(os.path.realpath(__file__)); HERE = os.path.dirname(T)
FILES = ('alarm_pipeline_v1.py', 'card_v1.py', 'mechanism_v1.py', 'CARD_JOB_TEMPLATE.sh')


def stop(code):
    return ('alarm_pipeline_v1.py', "raise Stop('%s'," % code, "(lambda *a: None)(")


M = [('m01', stop('BAD_INPUT'), 't23'), ('m02', stop('BAD_WINDOW'), 't35'), ('m03', stop('WINDOW_CLOSED'), 't08'),
     ('m04', stop('NO_FILE'), 't34'), ('m05', stop('DEF_CHANGED'), 't09'), ('m06', stop('CARD_CHANGED'), 't24'),
     ('m07', stop('TOOL_RC'), 't26'), ('m08', stop('NO_OUTPUT'), 't04'), ('m09', stop('NO_VERDICT'), 't20'),
     ('m10', stop('TG_REFUSED'), 't22'), ('m11', stop('FILE_REFUSED'), 't25'), ('m12', stop('DRY_REFUSED'), 't05'),
     ('m13', stop('JOB_EXIT'), 't03'), ('m14', stop('OPDONE'), 't12'), ('m15', stop('MENU_REFUSED'), 't21'),
     ('m16', stop('NO_VARIANTS_ROW'), 't29'), ('m17', stop('NO_FIELDS'), 't30'), ('m18', stop('NO_PREREG_ROW'), 't18'),
     ('m19', stop('NO_RESULT_ROW'), 't32'), ('m20', stop('RESULT_DIFFERS'), 't27'), ('m21', stop('PERFIRE_DIFFERS'), 't17'),
     ('m22', stop('NO_DECISION'), 't33'), ('m23', stop('BAD_DECISION'), 't19'), ('m24', stop('MAP_CHANGED'), 't38'),
     ('m25', stop('NO_TRIED_ROW'), 't31'), ('m26', stop('TRIED_DIFFERS'), 't13'), ('m27', stop('TRIED_EXISTS'), 't28'),
     ('m28', ('alarm_pipeline_v1.py', "                if not t:\n                    return 3, write_stop", "                if False:\n                    return 3, write_stop"), 't36'),
     ('m29', ('alarm_pipeline_v1.py', "raise Wait('no free rel queue", "(lambda *a: None)('no free rel queue"), 't39'),
     ('m30', ('alarm_pipeline_v1.py', "    if kv is None:\n        raise Wait(", "    if False:\n        raise Wait("), 't11'),
     ('m31', ('card_v1.py', "raise Refused('SIDE_WORD',", "(lambda *a: None)("), 't14'),
     ('m32', ('card_v1.py', "raise Refused('NO_ROWS',", "(lambda *a: None)("), 't37'),
     ('m33', ('mechanism_v1.py', "    if sha16(a.map) != MAP_PIN:", "    if False:"), 't15'),
     ('m34', ('alarm_pipeline_v1.py', "    fire = d['word'] == 'PASS' or", "    fire = False and"), 't07'),
     ('m35', ('alarm_pipeline_v1.py', "REPLAY_SKIP_FILE = {10, 21}", "REPLAY_SKIP_FILE = set()"), 't01'),
     ('m36', ('mechanism_v1.py', "THRESHOLD = 0.90", "THRESHOLD = 0.40"), 't10'),
     ('m37', ('card_v1.py', "        if os.path.exists(dm) and sha16(dm) == cs:", "        if False:"), 't16'),
     ('m38', ('alarm_pipeline_v1.py', "            if lean == 'FADE' and", "            if True or"), 't10')]
M[-1] = ('m38', ('mechanism_v1.py', "            if lean == 'FADE' and", "            if True or"), 't10')
M.append(('m39', ('alarm_pipeline_v1.py', "if p.I['registry_mode'] == 'replay' and old and re.search", "if old and re.search"), 't41'))
M.append(('m40', ('alarm_pipeline_v1.py', "    if pend.get('adopted') == 'yes':\n        N['adopted'] = 'yes'", "    if False:\n        N['adopted'] = 'yes'"), 't40'))


def main(a):
    lo, hi = (int(a[0]), int(a[1])) if len(a) == 2 else (1, len(M))
    killed = 0; n = 0
    for mid, (fn, old, new), test in M[lo - 1:hi]:
        d = os.path.join(T, 'mutants', mid)
        if os.path.exists(d):
            d = d + '_' + str(os.getpid())
        os.makedirs(d)
        for f in FILES:
            shutil.copyfile(os.path.join(HERE, f), os.path.join(d, f))
        src = open(os.path.join(d, fn)).read()
        if old not in src:
            print('NOT_APPLIED %s %s: pattern missing' % (mid, fn)); n += 1; continue
        open(os.path.join(d, fn), 'w').write(src.replace(old, new))
        env = dict(os.environ, PIPE_UNDER_TEST=os.path.join(d, 'alarm_pipeline_v1.py'))
        r = subprocess.run([sys.executable, '-B', os.path.join(T, 'test_pipeline_v1.py'), test], env=env, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, universal_newlines=True, timeout=50)
        k = 'RESULT 0 of 1' in r.stdout
        killed += k; n += 1
        print('%s %s %s (%s): %s' % ('KILLED' if k else 'SURVIVED', mid, fn, test, [l for l in r.stdout.splitlines() if l.startswith(('PASS', 'FAIL'))][:1]))
        sys.stdout.flush()
    print('MUTANTS killed %d of %d' % (killed, n))
    return 0 if killed == n else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
