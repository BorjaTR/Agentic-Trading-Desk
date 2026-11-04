#!/usr/bin/env python3
"""test_template_v4_run.py: a run started from KIT_V5/runs/TEMPLATE_V4 is accepted by queue_job_v5.py (COUNT --dry, then GRADE --dry
after the seal with CARD_V7.md as the prereg) and by audit_run_v3.py; TEMPLATE_V4's registers are TEMPLATE_V3's byte for byte; its
README_RUN.md and CARD_V7.md name only current tools and files that exist in this Alarm folder; planted bugs are caught. Seconds; the
planted run lives in a temp RESEARCH_ROOT under TMPDIR; no lab data, no runner and no scratch drive is read (the queue's free-space
reader is planted, as test_kit5_v6.py plants it).
Owner: SCOUT (the alarm kit). New by SCOUT helper K13 for ALARM_V1_3 (31 Oct 2026). Run it inside an Alarm folder:
  python3 -B test_template_v4_run.py    -> TESTS PASS and PLANTED n of n caught; exit 0 only when both hold"""
import contextlib, hashlib, importlib.util, io, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def alarm_folder():
    d = HERE
    while not os.path.isfile(os.path.join(d, '_tools', 'settings_v1.py')):
        if os.path.dirname(d) == d:
            raise SystemExit('REFUSED: run this test inside an Alarm folder')
        d = os.path.dirname(d)
    sys.path.insert(0, os.path.join(d, '_tools'))
    import settings_v1
    sys.path.pop(0)
    return settings_v1, settings_v1.alarm_root(__file__)


SV, AL = alarm_folder()
AD = os.path.join(AL, 'Agentic', 'tree', 'ALARM_DESIGN')
T3, T4 = os.path.join(AD, 'KIT_V5', 'runs', 'TEMPLATE_V3'), os.path.join(AD, 'KIT_V5', 'runs', 'TEMPLATE_V4')
CARD7 = os.path.join(AD, 'KIT_V6', 'templates', 'CARD_V7.md')
DEF4 = os.path.join(AL, '01_Detection', 'tree', 'team', 'RESEARCH', 'ALARM_DESIGN', 'KIT_V2', 'templates', 'DEF_TEMPLATE_V4.json')
QPATH, AUDIT = os.path.join(AD, 'KIT_V5', 'tools', 'queue_job_v5.py'), os.path.join(AD, 'KIT_V5', 'tools', 'audit_run_v3.py')
REG = os.path.join(AD, 'runs', 'CLAUDE1_20261028', 'tools', 'reg_append_v1.py')
CURRENT = ('queue_job_v5.py', 'decide_v2.py', 'audit_run_v3.py', 'board_line_v2.py', 'idea_time_v2.py', 'novelty_v2.py', 'REPORT_V6.md',
           'CARD_V7.md', 'DEF_TEMPLATE_V4.json', 'reg_append_v1.py')
PAST = ('queue_job_v4', 'decide_v1', 'audit_run_v2', 'REPORT_V5', 'alarm-design-v5', 'novelty_v1', 'PREREG_<IDEA>', 'FORECAST_<IDEA>',
        'IDEA_CARD.md', 'ALARM_CARD.md', 'DEF_TEMPLATE_V3', 'CARD_V6.md', 'raw-row')
RUN = 'K13_20261031'


def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def copy_tree(src, dst):
    for root, dirs, files in os.walk(src):
        os.makedirs(os.path.join(dst, os.path.relpath(root, src)), exist_ok=True)
        for f in files:
            shutil.copyfile(os.path.join(root, f), os.path.join(dst, os.path.relpath(root, src), f))


def registers_equal(t4):
    a = sorted(os.listdir(os.path.join(T3, 'registers'))); b = sorted(os.listdir(os.path.join(t4, 'registers')))
    return a == b and len(a) == 8 and all(open(os.path.join(T3, 'registers', n), 'rb').read() == open(os.path.join(t4, 'registers', n), 'rb').read() for n in a)


def names_current(text, current, past=PAST, min_paths=5):
    """every current tool named, no past edition named, every <INSTALL>/... or KIT_V*/... path it names exists in this Alarm folder"""
    miss = [c for c in current if c not in text]; past = [p for p in past if p in text]
    paths = re.findall(r'<INSTALL>/([A-Za-z0-9_./-]+\.(?:py|md|json))', text) + \
        ['Agentic/tree/ALARM_DESIGN/' + p for p in re.findall(r'(?<![/A-Za-z0-9_])((?:KIT_V5|KIT_V6|runs/CLAUDE1_20261028)/[A-Za-z0-9_./-]+\.(?:py|md|json))', text)]
    gone = [p for p in paths if not os.path.isfile(os.path.join(AL, p))]
    return not miss and not past and not gone and len(paths) >= min_paths, 'missing %s; past %s; paths not in the Alarm folder %s' % (miss, past, gone)


class Sandbox:
    """a temp RESEARCH_ROOT holding one run copied from a template, its claim and a definition; a settings file for it"""
    def __init__(self, template, tmp):
        self.root = tmp; v = {k: os.path.join(tmp, k.lower()) for k in SV.keys()}
        v.update(PYTHON=sys.executable, FEED_GATE='', FORBID='')        # RUNNER_RELEASE: the runner machine's install, outside this folder
        for k in ('LAB_DAYS', 'SCRATCH', 'BOARD', 'RESEARCH_STORE', 'HL_FILLS', 'RUNNER_RELEASE'):
            os.makedirs(v[k], exist_ok=True)
        for i in range(1, 22):
            for s in ('IN', 'RUN'):
                os.makedirs(os.path.join(v['RUNNER_QUEUES'], 'Q_V%d' % i, s))
        os.makedirs(os.path.dirname(v['RUNNER_ALLOC']), exist_ok=True)
        with open(v['RUNNER_ALLOC'], 'w') as f:
            f.write('raise SystemExit("the allocator is never called by --dry")\n')
        self.run = os.path.join(v['RESEARCH_ROOT'], 'ALARM_DESIGN', 'runs', RUN); copy_tree(template, self.run)
        cl = os.path.join(v['RESEARCH_ROOT'], 'ALARM_DESIGN', 'runs', 'IDEAS_CLAIMED'); os.makedirs(cl)
        with open(os.path.join(cl, '%s_PLANTED.txt' % RUN), 'w') as f:
            f.write('PLANTED: a planted idea of test_template_v4_run.py\n')
        os.makedirs(os.path.join(self.run, 'ideas', 'PLANTED', 'defs'))
        shutil.copyfile(DEF4, os.path.join(self.run, 'ideas', 'PLANTED', 'defs', 'V1.json'))
        shutil.copyfile(CARD7, os.path.join(self.run, 'ideas', 'PLANTED', 'CARD_PLANTED.md'))
        self.settings = os.path.join(tmp, 'SETTINGS_SANDBOX.env')
        with open(self.settings, 'w') as f:
            f.write('# the sandbox machine of test_template_v4_run.py\n' + ''.join('%s=%s\n' % (k, v[k]) for k in SV.keys()))
        sp = importlib.util.spec_from_file_location('queue_job_v5_t4', QPATH); self.Q = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(self.Q); self.Q.CFG.update({'free_mb': lambda: 200000})

    def q(self, *a):
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                self.Q.main(['--settings', self.settings] + list(a))
            return True, buf.getvalue()
        except SystemExit as e:
            return e.code in (0, None), buf.getvalue() + ' EXIT %s' % e.code
        except Exception as e:
            return False, buf.getvalue() + ' REFUSED %s' % e

    def seal(self):
        d = os.path.join(self.run, 'ideas', 'PLANTED')
        row = {'idea': 'PLANTED', 'V': 'V1', 'lean': 'FADE', 'def_rel': 'ideas/PLANTED/defs/V1.json', 'def_sha16': sha16(os.path.join(d, 'defs', 'V1.json')),
               'prereg_rel': 'ideas/PLANTED/CARD_PLANTED.md', 'prereg_sha16': sha16(os.path.join(d, 'CARD_PLANTED.md')), 'reason': 'planted first variant'}
        r = subprocess.run([sys.executable, '-B', REG, self.run, 'VARIANTS', '-'], input=json.dumps(row), capture_output=True, text=True)
        return r.returncode == 0, (r.stdout + r.stderr)[-300:]

    def audit(self):
        r = subprocess.run([sys.executable, '-B', AUDIT, '--settings', self.settings, RUN], capture_output=True, text=True)
        a1 = [l for l in r.stdout.splitlines() if re.search(r'\bA1\b', l)]
        return r.returncode, a1, r.stdout


def tests(tmp):
    ok = []
    ok.append(('t_registers_byte_equal_to_template_v3', registers_equal(T4)))
    good, why = names_current(open(os.path.join(T4, 'README_RUN.md')).read(), CURRENT)
    ok.append(('t_readme_run_names_the_current_tools_only', good)); good or print('    README_RUN: %s' % why)
    card = open(CARD7).read()
    good, why = names_current(card, ('queue_job_v5', 'decide_v2.py', 'novelty_v2.py', 'hc_defs_v2_to20251231', 'hc_mem_probe_v1', 'metric_brief_v2', 'DEF_TEMPLATE_V4.md'),
                               past=tuple(p for p in PAST if p != 'CARD_V6.md'), min_paths=1)   # its header names its old file, the team's convention
    good = good and 'THIS FILE IS THE PREREG' in card and 'FORECASTS rows are optional' in card
    ok.append(('t_card_v7_is_the_prereg_and_names_current_tools', good)); good or print('    CARD_V7: %s' % why)
    sb = Sandbox(T4, os.path.join(tmp, 'ok'))
    good, out = sb.q(RUN, 'COUNT', 'PLANTED', 'V1=ideas/PLANTED/defs/V1.json', '--dry')
    ok.append(('t_queue_count_dry_accepts_the_run', good and 'COUNT' in out)); print('    COUNT --dry: %s' % ' '.join(out.split())[-220:])
    s_ok, s_out = sb.seal()
    good, out = sb.q(RUN, 'GRADE', 'PLANTED', 'V1', '--dry')
    ok.append(('t_queue_grade_dry_accepts_it_after_the_seal', s_ok and good and 'GRADE' in out)); print('    GRADE --dry: %s' % ' '.join(out.split())[-220:])
    rc, a1, txt = sb.audit()
    ok.append(('t_audit_run_v3_accepts_the_run', rc == 0 and a1 and 'PASS' in a1[0])); print('    audit rc %s: %s' % (rc, a1[:1]))
    return ok


def planted(tmp):
    """bugs in a planted template: each must be caught by a check above"""
    out = []
    bad = os.path.join(tmp, 'bad_readme'); copy_tree(T4, bad)
    with open(os.path.join(bad, 'README_RUN.md'), 'a') as f:
        f.write('- jobs: queue_job_v4.py\n')
    out.append(('README names queue_job_v4', not names_current(open(os.path.join(bad, 'README_RUN.md')).read(), CURRENT)[0]))
    bad = os.path.join(tmp, 'bad_path'); copy_tree(T4, bad)
    with open(os.path.join(bad, 'README_RUN.md'), 'a') as f:
        f.write('- the report: KIT_V6/templates/REPORT_V9.md\n')
    out.append(('README names a file the release lacks', not names_current(open(os.path.join(bad, 'README_RUN.md')).read(), CURRENT)[0]))
    bad = os.path.join(tmp, 'bad_regs'); copy_tree(T4, bad)
    p = os.path.join(bad, 'registers', 'VARIANTS.tsv'); s = open(p).read()
    with open(p, 'w') as f:
        f.write(s.replace('\tlean', ''))
    out.append(('a VARIANTS header without lean is not TEMPLATE_V3s', not registers_equal(bad)))
    sb = Sandbox(bad, os.path.join(tmp, 'bad_run'))
    s_ok, _ = sb.seal(); g_ok, g_out = sb.q(RUN, 'GRADE', 'PLANTED', 'V1', '--dry'); rc, a1, _ = sb.audit()
    out.append(('a run from it: GRADE --dry or the audit refuses', not (s_ok and g_ok) or rc != 0 or not (a1 and 'PASS' in a1[0])))
    return out


def main():
    with tempfile.TemporaryDirectory() as tmp:
        res = tests(tmp)
        for n, v in res:
            print('%s %s' % ('PASS' if v else 'FAIL', n))
        fails = [n for n, v in res if not v]
        print('TESTS %s (%d of %d pass)' % ('PASS' if not fails else 'FAIL', len(res) - len(fails), len(res)))
        bugs = planted(tmp)
        for n, c in bugs:
            print('PLANTED %s: %s' % (n, 'CAUGHT' if c else 'MISSED'))
        caught = sum(c for _, c in bugs)
        print('PLANTED %d of %d caught' % (caught, len(bugs)))
    sys.exit(0 if not fails and caught == len(bugs) else 1)


if __name__ == '__main__':
    main()
