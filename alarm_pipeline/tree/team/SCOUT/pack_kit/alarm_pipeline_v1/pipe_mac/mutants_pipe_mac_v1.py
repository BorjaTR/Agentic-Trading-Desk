#!/usr/bin/env python3
"""mutants_pipe_mac_v1.py (SCO-A162, 6 Nov 2026). Planted faults in pipe_mac_v1.py, each run under test_pipe_mac_v1.py from a copy
(as pipe_mac_v1.py in its own folder); all must be caught, the clean copy green.  python3 -B mutants_pipe_mac_v1.py <new out> [mutant names]"""
import sys
sys.dont_write_bytecode = True
import os, shutil, subprocess
HERE = os.path.dirname(os.path.realpath(__file__))
M = [('cwd_lost', "cwd=p.rd, stdin=subprocess.DEVNULL", "cwd='/', stdin=subprocess.DEVNULL"),
     ('rel_rc_ignored', "            if pend['rc'] != 0:\n", "            if False:\n"),
     ('no_dry', "            if rc != 0 or 'DRY RUN OK' not in t:\n                raise Stop('DRY_REFUSED'", "            if False:\n                raise Stop('DRY_REFUSED'"),
     ('exit_ignored', "        if kv['exit'].strip() != '0':\n            raise Stop('JOB_EXIT'", "        if False:\n            raise Stop('JOB_EXIT'"),
     ('no_wait', "        if kv is None:\n            raise Wait(", "        if kv is None:\n            kv = {'exit': '0'}; sp = '-'\n        if False:\n            raise Wait("),
     ('retry_off', "    if a.retry_stop:", "    if False:"),
     ('map_off', "            return mac_home + v[len(vm_prefix):] if v.startswith(vm_prefix) else v", "            return v"),
     ('budget_off', "            if clock() - t0 > a.budget_s:", "            if False:"),
     ('stop_ignored', "        if rc == 3:\n            break", "        if rc == 3:\n            pass"),
     ('stop_file_kept', "    if os.path.exists(os.path.join(d, 'runner.stop')) or", "    if"),
     ('busy_ok', "        if not busy and not inq:", "        if not inq:"),
     ('view_off', "    if '\\n# TITLE: ' in text:\n        return None", "    return None"),
     ('view_always_none', "    return v\n\n\ndef install", "    return None\n\n\ndef install"),
     ('kitq_child_off', "cfg.get('kitq_child', KITQ_CHILD), os.path.join(cfg['install'], QJ16)", "os.path.join(cfg['install'], QJ16)"),
     ('k_no_title', "        '# TITLE: ' + head[0][len('# JOB '):], '# TASK: ' + task", "        '# TASK: ' + task", 'pipe_kitq_v1.py'),
     ('k_op_lost', "'# OP: ' + op]", "'# OP: -']", 'pipe_kitq_v1.py'),
     ('refile_exit0', "            if kv is None or kv['exit'].strip() == '0':", "            if kv is None:"),
     ('tpl_v1_1', "ALARM_UNDERSTAND_V1_2/tree", "ALARM_UNDERSTAND_V1_1/tree"),
     ('rel_name', "            lg = p.log(n, 'relwait')", "            lg = p.log(n, 'macrel')"),
     ('times_off', "            w.write('%s\\t%02d", "            0 and w.write('%s\\t%02d"),
     ('rel_paths_relative', "else os.path.join(p.rd, x) for x in args]", "else x for x in args]"),
     ('no_adopt', "                if p.I['registry_mode'] == 'replay' and old and re.search(r'REFUSED: ALREADY', t):", "                if False:"),
     ('k_hook_off', "            return Twin(f, str(path))", "            return f", 'pipe_kitq_v1.py')]
def main(out, only=()):
    os.makedirs(out); bad = 0
    shutil.copyfile(os.path.join(HERE, '..', 'alarm_pipeline_v1_1.py'), os.path.join(out, 'alarm_pipeline_v1_1.py'))   # the pipeline beside each copy's folder
    srcs = {f: open(os.path.join(HERE, f)).read() for f in ('pipe_mac_v1.py', 'pipe_kitq_v1.py')}
    def one(name, text, fn='pipe_mac_v1.py'):
        d = os.path.join(out, name); os.makedirs(d)
        for f, t in srcs.items():
            open(os.path.join(d, f), 'w').write(text if f == fn else t)
        for c in ('test_pipe_mac_v1.py',):
            shutil.copyfile(os.path.join(HERE, c), os.path.join(d, c))
        try:
            return subprocess.run([sys.executable, '-B', os.path.join(d, 'test_pipe_mac_v1.py')], env=dict(os.environ, MAC_SCRATCH=os.path.join(d, 's')),
                                  capture_output=True, text=True, timeout=120)
        except subprocess.TimeoutExpired:                       # a hang (e.g. no budget) is a caught fault
            return subprocess.CompletedProcess([], 124, 'FAIL TIMEOUT\n', '')
    r = one('clean', srcs['pipe_mac_v1.py']); print('CLEAN rc %d' % r.returncode); bad += r.returncode != 0
    for x in [x for x in M if not only or x[0] in only]:
        n, a, b = x[:3]; fn = x[3] if len(x) > 3 else 'pipe_mac_v1.py'; src = srcs[fn]
        if src.count(a) != 1:
            print('MUTANT %s NOT_APPLIED %d' % (n, src.count(a))); bad += 1; continue
        r = one(n, src.replace(a, b), fn); f = [l.split()[1] for l in r.stdout.splitlines() if l.startswith('FAIL ')]
        print('MUTANT %s %s %s' % (n, 'CAUGHT' if r.returncode else 'SURVIVED', ','.join(f))); bad += r.returncode == 0
    print('RESULT %d mutants, %s' % (len(M), 'all caught, clean green' if not bad else '%d problems' % bad)); return 1 if bad else 0
if __name__ == '__main__':
    sys.exit(main(sys.argv[1], tuple(sys.argv[2:])))
