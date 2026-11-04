#!/usr/bin/env python3
"""test_inputs_read_v1.py (SCOUT, 31 Oct 2026; TEST, NOT REVIEWED): inputs_read_v1.py on a planted registry and planted metric tables
with known answers. The test builds a sandbox Alarm package (the settings reader and example of the package that holds this file, the
registry tools novelty_v2, scoreboard_v2 and inputs_read_v1 in the release layout, metric_brief_v2.py in its layout, four planted
metric tables) and a sandbox settings file whose RESEARCH_ROOT names planted research data in a temp folder. The tool runs from the
sandbox package by its own path, from a decoy working folder, and must write only where it is told. Temp files only.

  python3 -B <REGISTRY>/tests/test_inputs_read_v1.py [--alarm <Alarm package>]
      --alarm: the package whose _tools/settings_v1.py, settings/SETTINGS_EXAMPLE.env and metric_brief_v2.py the sandbox copies;
      default: the Alarm package that holds this file (name one when this file runs from the team's dev tree)
Exit 0: every test passed. Planted bugs: mutants_inputs_read_v1.py (each must make this file fail).
"""
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REG_HOME = os.path.dirname(HERE)                  # the REGISTRY folder of this file (tools/)
TOOLS = ('novelty_v2.py', 'scoreboard_v2.py', 'inputs_read_v1.py')
LAYOUT = os.path.join('08_Registry', 'tree', 'ALARM_DESIGN', 'REGISTRY', 'tools')
MB_REL = os.path.join('01_Detection', 'tree', 'team', 'RESEARCH', 'LEAD', 'skills', 'reading-metrics', 'scripts', 'metric_brief_v2.py')
DT = os.path.join('01_Detection', 'tree', 'team')
ALARM = None                                      # set in __main__: --alarm, or the package that holds this file
TOOL_SRC = None                                   # the folder the three tools are copied from (set in __main__)

METRICS = [('A1.S01', 'ef_liq_long_5s', 'usd', 'coin', '5'), ('A1.S02', 'ef_liq_short_5s', 'usd', 'coin', '5'),
           ('A1.S03', 'ef_liq_long_30s', 'usd', 'coin', '5'), ('A1.S07.grid_off', 'largest_long_grid_off', 'usd', 'coin', '5'),
           ('E2.S04', 'oi_change_1m', 'ratio', 'coin', '60'), ('E2.S05', 'oi_change_hl', 'ratio', 'coin', '60'),
           ('X1.LIQX.S01', 'liq_print_seconds_share_60s', 'share_0_1', 'coin', '5'), ('Z9.S01', 'no_status_row', 'usd', 'coin', '60')]
TRAPS = [('A1.S01', 'PROVEN'), ('A1.S02', 'PROVEN, READ BY THE RULE'), ('A1.S03', 'NOT YET CHECKED'), ('A1.S07.grid_off', 'PROVEN'),
         ('E2.S04', 'PROVEN'), ('E2.S05', 'WITHDRAWN (A DROPPED MODEL)'), ('X1.LIQX.S01', 'COMPUTED RIGHT, MEANING NOT YET TESTED')]
REG_COLS = ['alarm_id', 'kind', 'seat', 'run', 'idea', 'V', 'state', 'lean', 'novelty_verdict', 'forward_months', 'def_rel', 'def_sha16']


def find_alarm(start):
    d = os.path.dirname(os.path.abspath(start))
    while True:
        if os.path.isfile(os.path.join(d, '_tools', 'settings_v1.py')) and os.path.isdir(os.path.join(d, 'settings')):
            return d
        if os.path.dirname(d) == d:
            return None
        d = os.path.dirname(d)


def sha16(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def rd(p):
    with open(p) as f:
        return f.read()


def w(p, text):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w') as f:
        f.write(text)


def copy(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)                     # bytes only: the source may sit in a read-only install


def example_keys(text):
    return [l.split('=', 1)[0] for l in text.splitlines() if re.match(r'[A-Z][A-Z0-9_]*=', l)]


def make_package(root, traps=True):
    pk = os.path.join(root, 'Alarm')
    copy(os.path.join(ALARM, '_tools', 'settings_v1.py'), os.path.join(pk, '_tools', 'settings_v1.py'))
    copy(os.path.join(ALARM, 'settings', 'SETTINGS_EXAMPLE.env'), os.path.join(pk, 'settings', 'SETTINGS_EXAMPLE.env'))
    for n in TOOLS:
        copy(os.path.join(TOOL_SRC, n), os.path.join(pk, LAYOUT, n))
    copy(os.path.join(ALARM, MB_REL), os.path.join(pk, MB_REL))
    w(os.path.join(pk, DT, 'LAB3', 'METRICS_V1.tsv'), '# planted\ncode\tcard_name\tshort\tunit\tscope\tstep_s\n'
      + ''.join('%s\t%s\t%s\t%s\t%s\t%s\n' % (c, s, s, u, sc, st) for c, s, u, sc, st in METRICS))
    if traps:
        w(os.path.join(pk, DT, 'LAB3', 'LAB4', 'proposals', 'metric_traps', 'METRIC_TRAPS_V3.tsv'),
          'code\tname\tstatus\n' + ''.join('%s\tn_%s\t%s\n' % (c, c, s) for c, s in TRAPS))
    w(os.path.join(pk, DT, 'RESEARCH', 'tools', 'alarm_context', 'CTX_CATALOG_V1.tsv'), 'code\tname\nC99.S01\tctx_planted\n')
    w(os.path.join(pk, DT, 'RESEARCH', 'tools', 'alarm_profile', 'EPI_CATALOG_V1.tsv'), 'code\tname\n')
    return pk


def write_settings(pk, path, research):
    keys = example_keys(rd(os.path.join(pk, 'settings', 'SETTINGS_EXAMPLE.env')))
    w(path, '# sandbox settings (test_inputs_read_v1)\n' + ''.join('%s=%s\n' % (k, research if k == 'RESEARCH_ROOT' else '') for k in keys))
    return path


def defn(codes, market=()):
    ins = {'px': {'op': 'price'}}
    for i, c in enumerate(codes):
        ins['r%d' % i] = {'op': 'raw', 'code': c}
    for i, c in enumerate(market):
        ins['m%d' % i] = {'op': 'market', 'code': c}
    return json.dumps({'id': 'X', 'inputs': ins}, indent=1) + '\n'


def make_research(data):
    """planted research data: RESEARCH_ROOT/ALARM_DESIGN with a registry, its tags and the definitions -> (research, design)"""
    R0 = os.path.join(data, 'research'); H = os.path.join(R0, 'ALARM_DESIGN')
    rows = []

    def alarm(aid, state, nov='-', fwd='-', codes=None, market=(), body=None, rel=None, sha=None):
        if rel is None and (codes is not None or body is not None):
            rel = 'runs/RUN1/ideas/%s/defs/V1.json' % aid
            w(os.path.join(H, rel), body if body is not None else defn(codes, market))
        if rel and sha is None:
            p = os.path.join(H, rel)
            sha = sha16(p) if os.path.isfile(p) else 'aaaaaaaaaaaaaaaa'
        rows.append({'alarm_id': aid, 'kind': 'AGENT', 'seat': 'AD1', 'run': 'RUN1', 'idea': aid, 'V': 'V1', 'state': state,
                     'lean': 'FADE', 'novelty_verdict': nov, 'forward_months': fwd, 'def_rel': rel or '-', 'def_sha16': sha or '-'})
    alarm('AD1_X_V1', 'PASS (KEPT)', 'NEW', '2601 HELD; 2602 HELD; 2603 HELD; 2604 WEAKER', ['A1.S01'], market=['E2.S04'])
    alarm('AD1_X_V2', 'STOP', 'NEW', '-', ['A1.S01'])
    alarm('AD2_Y_V1', 'NEEDS MORE MONTHS', 'NEW', '-', ['E2.S05', 'Q7.S01'])
    alarm('AD3_CH_V1', 'PASS', 'NEW', '-', ['A1.S02'], sha='bbbbbbbbbbbbbbbb')                 # changed since the decision
    alarm('AD3_MS_V1', 'STOP', rel='runs/RUN1/ideas/MISSING/defs/V1.json')                      # missing
    alarm('AD3_BAD_V1', 'STOP', body='{not json\n')                                               # no JSON
    alarm('DESK_A01', 'NOT KEPT')                                                                 # no definition
    w(os.path.join(H, 'REGISTRY', 'ALARM_REGISTRY_V1.tsv'), '# planted registry\n' + '\t'.join(REG_COLS) + '\n'
      + ''.join('\t'.join(r[c] for c in REG_COLS) + '\n' for r in rows))
    w(os.path.join(H, 'REGISTRY', 'FAMILY_TAGS_V1.tsv'), '# planted tags\nalarm_id\tfamily\tbasis\n'
      'AD1_X_V1\tFAM_A\tx\nAD1_X_V2\tFAM_A\tx\nAD2_Y_V1\tFAM_B\ty\n')
    return R0, H


def snapshot(d):
    out = {}
    for a, _, fs in os.walk(d):
        for n in fs:
            out[os.path.relpath(os.path.join(a, n), d)] = sha16(os.path.join(a, n))
    return out


def tsv(p):
    with open(p) as f:
        return {r['code']: r for r in csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t')}


class InputsRead(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.pk = make_package(self.root)
        self.research, self.H = make_research(os.path.join(self.root, 'data'))
        self.st = write_settings(self.pk, os.path.join(self.root, 'SETTINGS_T.env'), self.research)
        self.decoy = os.path.join(self.root, 'decoy')
        w(os.path.join(self.decoy, 'REGISTRY', 'ALARM_REGISTRY_V1.tsv'), 'not the registry\n')

    def tearDown(self):
        shutil.rmtree(self.root)

    def run_tool(self, *args, pk=None):
        return subprocess.run([sys.executable, '-B', os.path.join(pk or self.pk, LAYOUT, 'inputs_read_v1.py')] + list(args),
                              cwd=self.decoy, capture_output=True, text=True, timeout=120)

    def ok(self, *extra):
        r = self.run_tool('--settings', self.st, *extra)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return tsv(os.path.join(self.H, 'REGISTRY', 'INPUTS_READ_V1.tsv')), rd(os.path.join(self.H, 'REGISTRY', 'INPUTS_READ_V1.md'))

    def test_codes_read_and_states(self):
        t, _ = self.ok()
        a = t['A1.S01']
        self.assertEqual((a['flag'], a['alarms_n'], a['states'], a['families'], a['found']), ('OK', '2', 'PASS 1; STOP 1', 'FAM_A', '1'))
        self.assertEqual(a['alarms'], 'AD1_X_V1=PASS, AD1_X_V2=STOP')
        self.assertEqual((t['E2.S04']['alarms_n'], t['E2.S04']['states']), ('1', 'PASS 1'))          # a market input counts
        self.assertEqual((t['E2.S05']['flag'], t['E2.S05']['states']), ('STOP', 'NEEDS MORE MONTHS 1'))

    def test_flags(self):
        t, _ = self.ok()
        got = {c: t[c]['flag'] for c in ('A1.S02', 'A1.S03', 'X1.LIQX.S01', 'Z9.S01', 'C99.S01', 'Q7.S01')}
        self.assertEqual(got, {'A1.S02': 'OK', 'A1.S03': 'CAUTION', 'X1.LIQX.S01': 'CAUTION', 'Z9.S01': 'NO ROW', 'C99.S01': 'NO ROW',
                               'Q7.S01': 'NOT IN TABLES'})
        self.assertEqual(t['Q7.S01']['alarms_n'], '1')

    def test_groups(self):
        t, _ = self.ok()
        self.assertEqual([t[c]['group'] for c in ('A1.S01', 'A1.S07.grid_off', 'X1.LIQX.S01', 'E2.S04')], ['A1', 'A1', 'X1.LIQX', 'E2'])

    def test_skipped_definitions_never_read(self):
        t, page = self.ok()
        self.assertEqual(t['A1.S02']['alarms_n'], '0')                         # the changed definition is not read
        self.assertIn('none 1; missing 1 (AD3_MS_V1); changed 1 (AD3_CH_V1); unreadable 1 (AD3_BAD_V1)', page)
        self.assertIn('7 in the registry; 3 definitions read', page)

    def test_page_families_and_unread(self):
        _, page = self.ok()
        self.assertIn('### FAM_A: 2 alarms (PASS 1; STOP 1), FOUND 1', page)
        self.assertIn('- codes its alarms read: A1.S01 OK (AD1_X_V1=PASS, AD1_X_V2=STOP); E2.S04 OK (AD1_X_V1=PASS)', page)
        self.assertIn('- OK codes no alarm reads, in the same groups: A1: A1.S02 ef_liq_short_5s, A1.S07.grid_off largest_long_grid_off', page)
        self.assertIn('- A1 (2 of 3 OK unread): A1.S02, A1.S07.grid_off', page)
        self.assertNotIn('A1.S03,', page.split('## OK codes no alarm reads, by group')[1])     # a CAUTION code is never offered
        self.assertNotIn('- E2 (', page)                                                    # E2's only OK code is read

    def test_writes_only_where_told_and_twins(self):
        before = snapshot(self.pk)
        self.ok()
        self.assertEqual(snapshot(self.pk), before)                                         # nothing inside the package
        self.assertEqual(sorted(os.listdir(self.decoy)), ['REGISTRY'])                      # nothing in the working folder
        first = rd(os.path.join(self.H, 'REGISTRY', 'INPUTS_READ_V1.tsv'))
        self.ok()
        tw = [n for n in os.listdir(os.path.join(self.H, 'REGISTRY')) if n.startswith('INPUTS_READ_V1.tsv.pre_SCOUT_')]
        self.assertEqual(len(tw), 1)
        self.assertEqual(rd(os.path.join(self.H, 'REGISTRY', tw[0])), first)

    def test_refusals(self):
        r = self.run_tool()
        self.assertEqual(r.returncode, 2, r.stderr)                                         # no --settings
        for opt in ('--out', '--page'):
            r = self.run_tool('--settings', self.st, opt, os.path.join(self.pk, 'X.out'))
            self.assertEqual(r.returncode, 2, opt + r.stderr)
            self.assertIn('INSIDE THE ALARM PACKAGE', r.stderr)
        bare = make_package(os.path.join(self.root, 'bare'), traps=False)
        st2 = write_settings(bare, os.path.join(self.root, 'SETTINGS_B.env'), self.research)
        r = self.run_tool('--settings', st2, pk=bare)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn('MISSING TABLE', r.stderr)
        lone = os.path.join(self.root, 'lone')
        for n in TOOLS:
            copy(os.path.join(TOOL_SRC, n), os.path.join(lone, n))
        r = subprocess.run([sys.executable, '-B', os.path.join(lone, 'inputs_read_v1.py'), '--settings', self.st], cwd=self.decoy,
                           capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 2, r.stderr)                                         # outside an Alarm package
        r = self.run_tool('--settings', self.st, '--bogus', 'x')
        self.assertEqual(r.returncode, 1, r.stderr)


if __name__ == '__main__':
    a = sys.argv[1:]
    if '--alarm' in a:
        i = a.index('--alarm'); ALARM = os.path.abspath(a[i + 1]); del a[i:i + 2]
    else:
        ALARM = find_alarm(__file__)
    if not ALARM:
        sys.exit('NO ALARM PACKAGE: run this file inside an Alarm package, or name one with --alarm')
    TOOL_SRC = os.path.join(REG_HOME, 'tools')
    unittest.main(argv=[sys.argv[0]] + a, verbosity=1)
