#!/usr/bin/env python3
"""test_build_run_v2.py (SCO-A182): planted tests of build_run_v2.py, seconds, no market data, no Mac job. Each run makes a new folder
dry_test_v2/teeth_<utc>/ (copies of the dry series files and the dry config; nothing else is written).  python3 -B test_build_run_v2.py"""
import json, os, re, shutil, subprocess, sys, unittest
from datetime import datetime, timezone
LS = os.path.expanduser('~/mnt/dev/TradingPlatform_repo/volat-agent/forensics/team/SCOUT/loop_day_20261105/learning_series')
LS = os.environ.get('ALARM_SERIES_DIR', LS)   # C225: the series folder on the Mac host (the VM ~/mnt path)
D = LS + '/dry_test_v2'; B = os.environ.get('B_UNDER_TEST', LS + '/build/build_run_v2.py')
TT = D + '/teeth_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
FILES = ['HUNTER_PROMPT_TEMPLATE_V2.md', 'PIPE_MAC_JOB_TEMPLATE_V2.sh', 'CURATED_SERIES.tsv', 'SERIES.tsv', 'PROMPT_ADD.tsv', 'UNTESTED.md',
         'TRIED_BY.tsv', 'SERIES_V2.tsv', 'CURATED_SERIES_V2.tsv', 'PROMPT_ADD_V2.tsv', 'SERIES_V2_CONFIG_DRY.json', 'STATE_SPLIT_JOB_TEMPLATE_V2.sh']


def mk(name, edit=None, cfg_edit=None):
    d = os.path.join(TT, name); os.makedirs(d)
    for f in FILES:
        shutil.copyfile(os.path.join(D, f), os.path.join(d, f))
    if edit:
        p = os.path.join(d, 'HUNTER_PROMPT_TEMPLATE_V2.md'); t = open(p).read(); open(p, 'w').write(edit(t))
    if cfg_edit:
        p = os.path.join(d, 'SERIES_V2_CONFIG_DRY.json'); c = json.load(open(p)); cfg_edit(c); open(p, 'w').write(json.dumps(c))
    return d


def brief(d, task, extra=''):
    p = os.path.join(d, 'BRIEF_%s.md' % task); open(p, 'w').write('# Brief %s: planted\nplanted line %s\n' % (task, extra)); return p


def run(d, *args, config=None, dry=True):
    cmd = [sys.executable, '-B', B] + list(args) + ['--ls', d, '--config', config or os.path.join(d, 'SERIES_V2_CONFIG_DRY.json')]
    if dry:
        cmd.append('--dry-test')
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def build(d, arm, n, extra='', task=None):
    task = task or 'SCT-A%d' % ((300 if arm == 'L' else 400) + n)
    runf = os.path.join(d, 'runs_v2', '%s%02d' % (arm, n)); os.makedirs(os.path.join(runf, 'library', 'ALARM_BUILD'), exist_ok=True)
    os.makedirs(os.path.join(runf, 'root'), exist_ok=True); os.makedirs(os.path.join(runf, 'ops'), exist_ok=True)
    open(os.path.join(runf, 'ops', 'PIPE_SETTINGS_RUN.json'), 'w').write('{}\n')
    return run(d, 'build', '--arm', arm, '--run', str(n), '--task', task, '--brief', brief(d, task, extra), '--out',
               os.path.join(runf, 'HUNTER_PROMPT.md'), '--runf', runf, '--run-key', 'SCOUT_20261107')


class T(unittest.TestCase):
    def test_01_real_config_not_ready(self):
        d = mk('t01')                                                      # SCO-A184: the real config is READY now; a WAITING copy of it
        c = json.load(open(LS + '/SERIES_V2_CONFIG.json')); c['status'] = 'WAITING_V26'; open(d + '/CFG_WAITING.json', 'w').write(json.dumps(c))
        rc, out = run(d, 'build', '--arm', 'L', '--run', '1', '--task', 'SCT-A301', '--brief', 'x', '--out', d + '/o.md',
                      config=d + '/CFG_WAITING.json', dry=False)
        self.assertEqual(rc, 2); self.assertIn('REFUSED CONFIG_NOT_READY', out)

    def test_02_c_leak_part(self):
        d = mk('t02', edit=lambda t: t.replace('## What this run is for', 'see KNOWLEDGE_SCOUT_V1.tsv\n## What this run is for'))
        rc, out = build(d, 'C', 1); self.assertEqual(rc, 2); self.assertIn('REFUSED C_LEAK', out)

    def test_15_c_brief_neutralized_L_unchanged(self):
        d = mk('t15')
        extra = ('\nYARDSTICK: FDONLY +5.88 at 15 min; history: K1-11 Sep-Dec +8.01.\n'
                 '- KNOW = /x/team/RESEARCH/KNOWLEDGE/ALARM/KNOWLEDGE_SCOUT_V1.tsv (the KNOWLEDGE table)\n'
                 '- TRIED = /x/team/RESEARCH/PROCESS/2_ALARMS/TRIED_ALARMS_V1.tsv (the tried table)\n'
                 '   (e) Answer each qid. Use row T00-01 (loop_find) on your words and grep TRIED for them.\n'
                 'First sentence stays. The curated KNOWLEDGE page and UNTESTED.md are your start. Last sentence stays.\n')
        rc, out = build(d, 'C', 1, extra=extra); self.assertEqual(rc, 0, out); self.assertIn('brief_lines_neutralized 5', out)
        C = open(d + '/runs_v2/C01/HUNTER_PROMPT.md').read()
        for k in ('K1-11', 'KNOWLEDGE_SCOUT_V1', 'TRIED_ALARMS_V1', 'loop_find', 'UNTESTED.md', 'grep TRIED'):
            self.assertNotIn(k, C)
        for k in ('+5.88', '+8.01', 'First sentence stays.', 'Last sentence stays.', '- KNOW = not available in this arm', 'copy search'):
            self.assertIn(k, C)
        self.assertTrue(os.path.isfile(d + '/runs_v2/C01/prep/BRIEF_ARM_C.md'))
        rc, out = build(d, 'L', 1, extra=extra); self.assertEqual(rc, 0, out)
        L = open(d + '/runs_v2/L01/HUNTER_PROMPT.md').read()
        self.assertTrue(L.startswith(open(d + '/BRIEF_SCT-A301.md').read()))   # arm L: the brief word for word (the run kit checks it; C58b)

    def test_03_no_forecast(self):
        d = mk('t03', edit=lambda t: t.replace('FORECAST_R3', 'FORECAST_RX'))
        rc, out = build(d, 'L', 1); self.assertEqual(rc, 2); self.assertIn('REFUSED NO_FORECAST', out)

    def test_04_scout_only_window(self):
        d = mk('t04', edit=lambda t: t.replace('## What this run is for', 'look window Apr 2026 to Jul 2026\n## What this run is for'))
        rc, out = build(d, 'C', 1); self.assertEqual(rc, 2); self.assertIn('REFUSED SCOUT_ONLY_WINDOW', out)

    def test_05_bad_task(self):
        d = mk('t05'); rc, out = build(d, 'C', 1, task='SCT-A301'); self.assertEqual(rc, 2); self.assertIn('REFUSED BAD_TASK', out)

    def test_06_unfilled_slot(self):
        d = mk('t06', edit=lambda t: t.replace('## What this run is for', '{FOO_BAR}\n## What this run is for'))
        rc, out = build(d, 'L', 1); self.assertEqual(rc, 2); self.assertIn('REFUSED SLOT', out)

    def test_07_good_L_and_C(self):
        d = mk('t07'); rcl, outl = build(d, 'L', 2); rcc, outc = build(d, 'C', 2)
        self.assertEqual(rcl, 0, outl); self.assertEqual(rcc, 0, outc)
        L = open(d + '/runs_v2/L02/HUNTER_PROMPT.md').read(); C = open(d + '/runs_v2/C02/HUNTER_PROMPT.md').read()
        for t in (L, C):
            for k in ('FORECAST_R1.md', 'FORECAST_R2', 'FORECAST_R3', 'FORECASTS.tsv', '+8.09', '4 of 5', 'FUONLY +10.99', 'Sep 2025 to Mar 2026', 'CURRENT at build', 'STATE_SPLIT_JOB_TEMPLATE_V2.sh', '--yardstick15', 'TradingPlatform/volat-agent/forensics/tools/job_alloc.py'):
                self.assertIn(k, t)
            self.assertEqual(re.findall(r'(?<!\$)\{[A-Z][A-Z0-9_]*\}', t), [])
        self.assertIn('V2AL01-01', L); self.assertNotIn('V2AL01-02', L)            # applies_from_run 2 in, 5 out
        self.assertNotIn('V2AL01', C); self.assertNotIn('K1-', C); self.assertNotIn('KNOWLEDGE_SCOUT_V1', C)
        self.assertIn('KNOWLEDGE_EMPTY_V1.tsv', C); self.assertIn('none apply to this run', C)
        self.assertEqual(open(d + '/runs_v2/C02/ops/KNOWLEDGE_EMPTY_V1.tsv').read().count('\n'), 1)
        cv = open(d + '/runs_v2/L02/ops/CURATED_VIEW.tsv').read()
        self.assertIn('PLANTED_L_ROW', cv); self.assertNotIn('PLANTED_C_ROW', cv)

    def test_16_knowledge_brief_L_only(self):                              # DOCS-K1: brief copied for L with sha16, never for C
        d = mk('t16'); os.makedirs(d + '/knowledge_v1'); kbs = d + '/knowledge_v1/KNOWLEDGE_BRIEF.md'
        open(kbs, 'w').write('# KNOWLEDGE BRIEF planted\n- F0001 planted finding\n')
        rcl, outl = build(d, 'L', 3); rcc, outc = build(d, 'C', 3)
        self.assertEqual(rcl, 0, outl); self.assertEqual(rcc, 0, outc)
        kb = d + '/runs_v2/L03/ops/KNOWLEDGE_BRIEF.md'; sha = __import__('hashlib').sha256(open(kbs, 'rb').read()).hexdigest()[:16]
        self.assertEqual(open(kb).read(), open(kbs).read()); self.assertIn('kbrief ' + sha, outl); self.assertIn('kbrief none', outc)
        L = open(d + '/runs_v2/L03/HUNTER_PROMPT.md').read(); C = open(d + '/runs_v2/C03/HUNTER_PROMPT.md').read()
        self.assertIn('%s (%s, the knowledge brief' % (kb, sha), L)
        for k in ('KNOWLEDGE_BRIEF', 'knowledge_v1', 'F0001'):
            self.assertNotIn(k, C)
        self.assertFalse(os.path.exists(d + '/runs_v2/C03/ops/KNOWLEDGE_BRIEF.md'))
        d2 = mk('t16b', edit=lambda t: t.replace('## What this run is for', 'read knowledge_v1/KNOWLEDGE_BRIEF.md\n## What this run is for'))
        rc, out = build(d2, 'C', 1); self.assertEqual(rc, 2); self.assertIn('REFUSED C_LEAK', out)
        d3 = mk('t16c'); rc, out = build(d3, 'L', 1); self.assertEqual(rc, 0, out); self.assertIn('kbrief none', out)
        self.assertIn('knowledge brief: none built yet', open(d3 + '/runs_v2/L01/HUNTER_PROMPT.md').read())

    def test_08_order_rule(self):
        d = mk('t08')
        rc, out = run(d, 'check-launch', '--arm', 'C', '--run', '1'); self.assertEqual(rc, 2); self.assertIn('needs L01 prepared', out)
        os.makedirs(d + '/runs_v2/L01/ops'); open(d + '/runs_v2/L01/ops/PART_A_DONE_UTC.txt', 'w').write('x\n')
        rc, out = run(d, 'check-launch', '--arm', 'C', '--run', '1'); self.assertEqual(rc, 0, out)
        rc, out = run(d, 'check-launch', '--arm', 'L', '--run', '2'); self.assertEqual(rc, 2); self.assertIn('SERIES_V2 RUN row of L01', out)

    def test_09_job_limit(self):                                           # SCO-A184: the marker is current now, so every limit is 2
        d = mk('t09', cfg_edit=lambda c: c['job_limit'].update({'limit_before': 2, 'limit_after': 2, 'limit_after_behind': 2}))
        os.makedirs(d + '/runs_v2/L01/ops'); open(d + '/runs_v2/L01/ops/PART_A_DONE_UTC.txt', 'w').write('x\n')
        rc, out = run(d, 'check-launch', '--arm', 'C', '--run', '1'); self.assertEqual(rc, 2); self.assertIn('JOB LIMIT', out)


    def test_10_def_last_day_filled(self):                                 # SCO-A184: the slot fills the DEF field, the scan lets it pass
        d = mk('t10'); rc, out = build(d, 'L', 2); self.assertEqual(rc, 0, out)
        L = open(d + '/runs_v2/L02/HUNTER_PROMPT.md').read()
        self.assertEqual(L.count('"window": {"first": "20250901", "last": "20260731"}'), 1)

    def test_11_def_last_day_in_prose_refused(self):                       # the same value outside the DEF field is still a closed month
        d = mk('t11', edit=lambda t: t.replace('## What this run is for', 'the DEF runs to 20260731\n## What this run is for'))
        rc, out = build(d, 'L', 2); self.assertEqual(rc, 2); self.assertIn('REFUSED CLOSED_MONTH', out)

    def test_12_def_last_day_missing_in_config(self):
        d = mk('t12', cfg_edit=lambda c: c['windows'].pop('def_last_day'))
        rc, out = build(d, 'C', 2); self.assertEqual(rc, 2); self.assertIn('REFUSED DEF_LAST_DAY', out)

    def test_13_def_field_not_in_part(self):
        d = mk('t13', edit=lambda t: t.replace('"last": "{DEF_LAST_DAY}"', '"last": "{DESIGN_INPUT}"'))
        rc, out = build(d, 'L', 2); self.assertEqual(rc, 2); self.assertIn('REFUSED DEF_LAST_DAY', out)


    def test_14_def_last_day_from_config(self):                            # the value comes from the config, not from the code
        d = mk('t14', cfg_edit=lambda c: c['windows'].update({'def_last_day': '20251231'}))
        rc, out = build(d, 'L', 2); self.assertEqual(rc, 0, out)
        self.assertIn('"last": "20251231"}', open(d + '/runs_v2/L02/HUNTER_PROMPT.md').read())



class TAdopt(unittest.TestCase):
    def test_adopt_spelling_is_read(self):
        """C21: V2AL05-01 and V2AL06-01 were written ADOPT and left out of L06/L07 prompts"""
        import tempfile
        d = tempfile.mkdtemp()
        hdr = "add_id\tfrom_run\tutc\tkind\ttext\tevidence\tapplies_from_run\tstatus\n"
        open(os.path.join(d, "PROMPT_ADD_V2.tsv"), "w").write(hdr + "X1\tL1\tu\tPROCESS\tt\te\t2\tADOPT\nX2\tL1\tu\tPROCESS\tt\te\t2\tADOPTED\nX3\tL1\tu\tPROCESS\tt\te\t9\tADOPT\nX4\tL1\tu\tPROCESS\tt\te\t2\tREJECTED\n")
        import importlib.util; sp = importlib.util.spec_from_file_location("bru2", B); M = importlib.util.module_from_spec(sp); sp.loader.exec_module(M)
        self.assertEqual([r["add_id"] for r in M.prompt_adds(d, 3)], ["X1", "X2"])


class THeldout(unittest.TestCase):
    def test_heldout_scan(self):
        """C24: Feb-Mar markers or numbers refuse a build (both arms); rule text without numbers passes"""
        import importlib.util; sp = importlib.util.spec_from_file_location("bru2h", B); M = importlib.util.module_from_spec(sp); sp.loader.exec_module(M)
        for bad in ("FDONLY Feb-Mar +3.14 at 15 min", "lead_2603 2.2", "yardstick_heldout_febmar", "February to March 2026 lead -0.52"):
            self.assertTrue(M.heldout_scan(bad), bad)
        for ok in ("Never read Feb or Mar 2026 numbers", "Held-out Feb-Mar (orchestrator): <filled by orchestrator>.", "design months Sep 2025 to Jan 2026"):
            self.assertEqual(M.heldout_scan(ok), [], ok)

class TForbidden(unittest.TestCase):
    def test_forbidden_numbers(self):
        """C58: the Sep-Mar yardstick (pools Feb-Mar) and the Feb-Mar block never reach a hunter prompt; Sep-Jan numbers do"""
        import importlib.util, json; sp = importlib.util.spec_from_file_location("bru2f", B); M = importlib.util.module_from_spec(sp); sp.loader.exec_module(M)
        cfg = {'yardstick': {'lead15': 5.88, 'lead1h': 6.87, 't15': 3.42, 't1h': 3.72, 'waves': 1786},
               'yardstick_heldout_febmar': {'lead15': 3.1415, 'lead1h': 2.7182, 'waves': 777}}      # C95: planted values, never the real block
        self.assertEqual(M.forbidden_scan('FDONLY lead +5.88 at 15 min', cfg), ['5.88'])
        self.assertTrue(M.forbidden_scan('1786 waves', cfg)); self.assertTrue(M.forbidden_scan('Feb-Mar +3.14', cfg))
        hf = os.path.join(TT, 'HELDOUT_PLANT.json'); os.makedirs(TT, exist_ok=True)                          # C95: the block read from its own file
        json.dump({'yardstick_heldout_febmar': {'lead15': 3.1415, 'lead1h': 2.7182, 'waves': 777}}, open(hf, 'w'))
        cfg2 = {'yardstick': cfg['yardstick'], 'yardstick_heldout_file': {'path': hf}}
        self.assertTrue(M.forbidden_scan('Feb-Mar +3.14', cfg2)); self.assertTrue(M.forbidden_scan('777 waves', cfg2))
        sf = os.path.join(TT, 'SEPMAR_PLANT.json')                                                        # C225: the pooled Sep-Mar block from its own file
        json.dump({'yardstick': {'lead15': 4.4444, 'lead1h': 5.5555, 'waves': 888}}, open(sf, 'w'))           # planted values, never the real block
        cfg3 = {'yardstick_sepmar_file': {'path': sf}}
        self.assertEqual(M.forbidden_scan('FDONLY lead +4.44 at 15 min', cfg3), ['4.44']); self.assertTrue(M.forbidden_scan('888 waves', cfg3))
        with self.assertRaises(SystemExit): M.forbidden_scan('x', {'yardstick_sepmar_file': {'path': sf + '.missing'}})
        self.assertEqual(M.forbidden_scan('FDONLY Sep-Jan +8.09 (t 3.70, 1235 waves); FUONLY +10.99; R1 +15.88', cfg), [])
        real = M.load_cfg(os.path.join(os.path.dirname(B), '..', 'SERIES_V2_CONFIG.json'), os.path.join(os.path.dirname(B), '..'), False)
        S = M.slots_common(real)
        self.assertEqual((S['{Y15}'], S['{YU15}'], S['{YARD_LEAD15}']), ('8.09', '10.99', '+8.09'))

class TConfigNoHeldout(unittest.TestCase):
    def test_config_holds_no_number_reaching_feb2026(self):
        """C225: SERIES_V2_CONFIG.json (assessors and other roles read it) holds no measured number whose window reaches Feb 2026: no pooled
        Sep-Mar yardstick, no Feb-Mar block, no held-out month key; every block with a measured number names a window ending by 2026-01-31.
        Scans every window/month key of every block. Failure messages name key paths only, never values."""
        p = os.path.join(os.path.dirname(os.path.abspath(B)), '..', 'SERIES_V2_CONFIG.json'); c = json.load(open(p, encoding='utf-8'))
        self.assertNotIn('yardstick', c); self.assertNotIn('yardstick_heldout_febmar', c)
        self.assertIn('yardstick_sepmar_file', c); self.assertIn('yardstick_heldout_file', c)
        WORD = re.compile(r'(?i)sep[ -]?mar|feb[ -]?mar|febmar|sepmar|(feb|mar)[a-z]* 2026')
        def reach(s):     # a held-out window word, or a real date from 2026-02-01 on (job ids like 2027xxxx are not dates of 2025-2026)
            if WORD.search(s): return True
            return any(y in ('2025', '2026') and '01' <= m <= '12' and '01' <= d <= '31' and y + m + d >= '20260201'
                       for y, m, d in re.findall(r'(?<!\d)(20\d\d)(\d\d)(\d\d)(?!\d)', s))
        def measured(k, v):
            if isinstance(v, bool): return False
            if isinstance(v, float): return True
            if isinstance(v, int): return k in ('waves', 'months_pass') or 'lead' in k
            if isinstance(v, list): return any(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v)
            return False
        WK = re.compile(r'window|month|label|input|block|receipt|^name$')
        bad = []
        def walk(o, path):
            if isinstance(o, dict):
                nums = [k for k, v in o.items() if measured(k, v)]
                for k, v in o.items():
                    if re.search(r'(?i)260[2-7]|febmar|_feb|_mar', k) and (measured(k, v) or isinstance(v, dict)): bad.append(path + '.' + k + ' (held-out key)')
                if nums:
                    win = o.get('window')
                    if not isinstance(win, str): bad.append(path + ' (measured %s, no window key)' % ','.join(nums))
                    for k, v in o.items():
                        if isinstance(v, str) and WK.search(k) and reach(v): bad.append(path + '.' + k + ' (window reaches Feb 2026; measured %s)' % ','.join(nums))
                for k, v in o.items(): walk(v, path + '.' + k)
            elif isinstance(o, list):
                for i, x in enumerate(o): walk(x, '%s[%d]' % (path, i))
        walk(c, 'cfg')
        self.assertEqual(bad, [])
        P = {'window': '20250910:20260331', 'lead15': 1.0}; bad.clear(); walk({'x': P}, 'plant'); self.assertTrue(bad)      # the scan has teeth
        bad.clear(); walk({'x': {'receipt': 'Y_SEPMAR.tsv', 'lead15': 1.0, 'window': '20250910:20260131'}}, 'plant'); self.assertTrue(bad)
        bad.clear(); walk({'x': {'lead_2602': 1.0}}, 'plant'); self.assertTrue(bad)

if __name__ == '__main__':
    os.makedirs(TT)
    unittest.main(verbosity=1)
