"""test_agent_docs_v1.py (SCOUT's K9, 30 Oct 2026; TEST, NOT REVIEWED): the agent docs (cards/<tool>.md, cards/<tool>.TOOL.json,
dictionaries/<tool>_COLUMNS.tsv) against the code of the Alarm folder that holds this file. Smallest first:
  T01 the generator's readers on planted code (no tool, no docs)
  T02 every tool has its card, TOOL.json and dictionary, each with the archive line, nothing left to write by hand, no em dash; no
      machine path in a TOOL.json or in the generator and its tests (machine_paths_v2 reads JSON and Python strings as CODE)
  T03 the docs are in step with the code: every listed column exists in the code, every column the code writes is listed (the
      generator's --check); every source_line names a line that holds its column; every quote in backticks is in the code
  T04 TOOL.json: every argument is one the code reads, every option the code reads is documented, every exit is one the code names
  T05 every command runs from this Alarm folder in its documented dry or read-only mode (or into planted temp data only) and exits as
      documented; each tool's refusal exits as documented
  T06 every card: its six sections, its links resolve, its command, its settings keys and its exit codes
The commands run against a planted world in a new temp folder (a run AD1_20261029 with the idea FLOWX, its registers, receipts, claim,
board, queues, a small registry and two small part folders) named by a planted settings file; nothing outside the temp folder is read
or written, no job is queued. No data needed. In a TOOL.json dry run, {SETTINGS} is the planted settings file, {WORLD} the planted
world and {ALARM} this Alarm folder.
  python3 -B <Alarm>/_tools/tests/test_agent_docs_v1.py          (docs in <Alarm>/cards and <Alarm>/dictionaries;
                                                                  AGENT_DOCS_DIR=<folder> names another folder that holds them)"""
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
TOOLS_DIR = os.path.dirname(HERE)
sys.path.insert(0, TOOLS_DIR)
import settings_v1  # noqa: E402
import agent_docs_v1 as G  # noqa: E402

ALARM = settings_v1.alarm_root(__file__)
DOCS = os.path.abspath(os.environ.get('AGENT_DOCS_DIR') or ALARM)
RUN, IDEA = 'AD1_20261029', 'FLOWX'
LINK = re.compile(r'\[[^\]]*\]\(([^)\s]+)\)')
QUOTE = re.compile(r'`([^`]+)`')
EM = '\u2014'


def sha16(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def w(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w') as f:
        f.write(s)
    return p


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


def rd(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


def jload(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def tool_json(t):
    return jload(os.path.join(DOCS, 'cards', '%s.TOOL.json' % t))


def card(t):
    return rd(os.path.join(DOCS, 'cards', '%s.md' % t))


def sections(md):
    out, cur = {}, None
    for l in md.split('\n'):
        if l.startswith('## '):
            cur = l[3:].strip()
            out[cur] = ''
        elif cur:
            out[cur] += l + '\n'
    return out


# ---------------------------------------------------------------- the planted world (temp folder only)
def tsv_rows(header, rows):
    return '\t'.join(header) + '\n' + ''.join('\t'.join(r.get(c, '-') for c in header) + '\n' for r in rows)


def build_world(root):
    """a run AD1_20261029 with the idea FLOWX (V1 STOP, V2 PASS with its ENTRY, V3 the forward-only other side of V1, held 4 of 4),
    its COUNT job finished and read; a board, empty queues, a small registry; returns the planted settings file"""
    rr = os.path.join(root, 'research')
    H = os.path.join(rr, 'ALARM_DESIGN')
    run = os.path.join(H, 'runs', RUN)
    regdir = os.path.join(ALARM, G.REGISTERS)
    hdr = {}
    for n in sorted(os.listdir(regdir)):
        with open(os.path.join(regdir, n)) as f:
            hdr[n[:-4]] = f.readline().rstrip('\n').split('\t')
    I = 'ideas/%s' % IDEA
    d1 = w(os.path.join(run, I, 'defs', 'V1.json'), '{"window": {"first": "20250901", "last": "20260531"}, "note": "planted"}\n')
    d2 = w(os.path.join(run, I, 'defs', 'V2.json'), '{"window": {"first": "20250901", "last": "20260531"}, "note": "planted 2"}\n')
    pre = w(os.path.join(run, I, 'PREREG_%s.md' % IDEA), '# PREREG FLOWX (planted)\n')
    w(os.path.join(run, I, 'CARD_%s.md' % IDEA), '# CARD FLOWX (planted)\n## The idea\nflows push the price.\n## Rule\nplanted rule.\n')
    w(os.path.join(run, I, 'FINDINGS_%s.md' % IDEA), '# FINDINGS FLOWX\nVERDICT: planted\n')
    fc = w(os.path.join(run, I, 'FORECAST_%s_V3.md' % IDEA), '# FORECAST V3 (planted)\n')
    w(os.path.join(H, 'runs', 'IDEAS_CLAIMED', '%s_%s.txt' % (RUN, IDEA)), 'FLOWX: a planted idea for the docs test. More words.\n')
    var = [dict(utc='2026-10-29T10:10:00Z', idea=IDEA, V='V1', lean='FADE', def_rel=I + '/defs/V1.json', def_sha16=sha16(d1),
                prereg_rel=I + '/PREREG_FLOWX.md', prereg_sha16=sha16(pre), reason='first variant'),
           dict(utc='2026-10-29T10:10:01Z', idea=IDEA, V='V2', lean='FOLLOW', def_rel=I + '/defs/V2.json', def_sha16=sha16(d2),
                prereg_rel=I + '/PREREG_FLOWX.md', prereg_sha16=sha16(pre), reason='second variant'),
           dict(utc='2026-10-29T12:00:00Z', idea=IDEA, V='V3', lean='FOLLOW', def_rel=I + '/defs/V1.json', def_sha16=sha16(d1),
                prereg_rel=I + '/PREREG_FLOWX.md', prereg_sha16=sha16(pre), reason='FORWARD ONLY OF V1 (the other side)')]
    fcs = [dict(utc='2026-10-29T12:01:00Z', idea=IDEA, V='V3', scope=m, gap15_lo='-5', gap15_hi='5', gap1h_lo='-5', gap1h_hi='5',
                file_rel=I + '/FORECAST_FLOWX_V3.md', file_sha16=sha16(fc), note='planted') for m in ('2601', '2602', '2603', '2604')]
    jobs = [('20263690', 'COUNT', 'V1', '2026-10-29T10:05:00Z', '-'), ('20263700', 'GRADE', 'V1,V2', '2026-10-29T10:20:00Z', '-'),
            ('20263710', 'ENTRY', 'V2', '2026-10-29T11:00:00Z', '20263700_GRADE_FLOWX'),
            ('20263720', 'MONTH', 'V3', '2026-10-29T12:05:00Z', '20263700_GRADE_FLOWX')]
    runs = [dict(utc_queued=u, job='jobs/%s_judge_AD1_%s_%s.job.sh' % (n, k, IDEA), job_sha16='0' * 16, kind=k, idea=IDEA, variants=v,
                 queue='Q_V1', prereg_rel='-', prereg_sha16='-', writes_mb='300', mem_mb='6000', minutes='10', template_sha16='0' * 16,
                 from_job=fj, receipts_rel='receipts/%s_%s_%s' % (n, k, IDEA)) for n, k, v, u, fj in jobs]
    rec = lambda j: os.path.join(run, 'receipts', j)
    stage = lambda rows: 'stage\trc\tseconds\tutc\tnote\n' + ''.join('%s\t0\t60\t%s\tplanted\n' % r for r in rows)
    for n, k, v, u, fj in jobs:
        j = '%s_%s_%s' % (n, k, IDEA)
        st = [('start', u)]
        if k == 'COUNT':
            st += [('count_V1', u)]
            w(os.path.join(rec(j), 'COUNT_V1.tsv'), '# COUNT V1 (planted)\nmonth\tfires\twaves\tcoins\tmax_fires_in_a_wave\tfires_on_BTC\n'
              '2509\t40\t35\t5\t2\t3\nALL\t40\t35\t5\t2\t3\n')
        if k == 'GRADE':
            st += [('grade_V1', u), ('grade_V2', u), ('handoff', u)]
            fl = {}
            for vv, side in (('V1', '1'), ('V2', '-1')):
                fl[vv] = w(os.path.join(rec(j), '%s_FIRES_V1_LIST.tsv' % vv), 'coin\tt\tside\n' + ''.join(
                    '%s\t%d\t%s\n' % (('BTC', 'ETH', 'SOL')[i % 3], 1757500000 + i * 7200, side) for i in range(30)))
            w(os.path.join(rec(j), 'FIRES.tsv'), ''.join('%s\t30\t%s\t%s\n' % (vv, sha16(p), os.path.join(root, 'scratch_absent', 'work_' + RUN, j,
                                                           os.path.basename(p))) for vv, p in sorted(fl.items())))
            w(os.path.join(rec(j), 'HANDOFF', 'SUMMARY.tsv'), 'V\tlean\tstatus\tgate\twaves\tmonths_counted_any\nV1\tFADE\tOK\tPASS\t120\t4\n'
              'V2\tFOLLOW\tOK\tPASS\t130\t4\n')
            for vv, r1, r2, pas in (('V1', 'no', 'no', 1), ('V2', 'PASS', 'PASS', 4)):
                w(os.path.join(rec(j), 'HANDOFF', 'REAL_SEALED', 'REAL_RULES_%s.tsv' % vv),
                  'key\tvalue\nR1\t%s\nR2\t%s\ncounted\t4\nneed\t3\npassing\t%d\n' % (r1, r2, pas))
                w(os.path.join(rec(j), 'HANDOFF', 'REAL_SEALED', 'REAL_%s.tsv' % vv),
                  'horizon\twaves\tdays\tlead\tse\tt\n15m\t120\t40\t3.5\t1.5\t2.3\n1h\t120\t40\t7.0\t2.0\t3.5\n')
        if k == 'ENTRY':
            st += [('store_V2', u), ('markout_V2', u)]
        if k == 'MONTH':
            st += [('grade_V3', u)]
            for m in ('2601', '2602', '2603', '2604'):
                st += [('month_V3_%s' % m, u)]
                w(os.path.join(rec(j), 'MONTH_READ_V3_%s.txt' % m), 'V3 month %s lean FOLLOW: fires 300 waves 120\n  15m  a 30.0 r 25.0 gap '
                  '+5.0 | other side gap -1.0\n  1h   a 32.0 r 26.0 gap +6.0 | other side gap -2.0\n  VERDICT HELD\n' % m)
        st += [('end', u)]
        w(os.path.join(rec(j), 'STAGES.tsv'), stage(st))
        w(os.path.join(rec(j), 'SHA16.txt'), 'planted\n')
        w(os.path.join(rec(j), 'DISK.tsv'), 'du_mb_W\t1\nfree_mb_end\t100000\n')
    dec = [dict(utc='2026-10-29T10:50:00Z', idea=IDEA, V='V1', state='STOP', r1='no', r2='no', months_counted='4', months_passing='1',
                waves='120', grade_job='20263700_GRADE_FLOWX', entry_job='-'),
           dict(utc='2026-10-29T11:30:00Z', idea=IDEA, V='V2', state='PASS', r1='PASS', r2='PASS', months_counted='4', months_passing='4',
                waves='130', grade_job='20263700_GRADE_FLOWX', entry_job='20263710_ENTRY_FLOWX'),
           dict(utc='2026-10-29T13:00:00Z', idea=IDEA, V='V3', state='FORWARD PASS', label_rule='FORWARD ONLY (planted)',
                grade_job='20263700_GRADE_FLOWX', entry_job='-')]
    pm = [dict(utc='2026-10-29T10:12:00Z', idea=IDEA, V='V1', job='20263690_COUNT_FLOWX', scope='COUNT', forecast='-', result='35 waves',
               result_file='-', result_sha16='-', why='planted', unexplained='-')]
    rows = {'VARIANTS': var, 'FORECASTS': fcs, 'RUNS': runs, 'DECISIONS': dec, 'POSTMORTEMS': pm}
    for n, h in hdr.items():
        w(os.path.join(run, 'registers', n + '.tsv'), tsv_rows(h, rows.get(n, [])))
    hb = os.path.join(root, 'hb')
    w(os.path.join(hb, 'AD1.txt'), '2026-10-29T10:00:00Z AD1 START the planted run\n2026-10-29T10:01:00Z AD1 CLAIM FLOWX: theme flows; '
      'planted\n2026-10-29T13:30:00Z AD1 DONE the planted run\n')
    for q in ('Q_V1', 'Q_V2'):
        for sub in ('IN', 'RUN'):
            os.makedirs(os.path.join(root, 'runner', q, sub))
    alloc = w(os.path.join(root, 'runner_tools', 'job_alloc.py'), 'raise SystemExit("the docs test never claims a number")\n')
    cols = [c for c, _, _ in G.ex_seq(ALARM, G.RG + '/tools/registry_build_v2.py', 'COLS')]
    k1 = w(os.path.join(H, 'REGISTRY', 'fire_lists', 'K1_FIRES_V1_LIST.tsv'), 'coin\tt\tside\n' + ''.join(
        '%s\t%d\t1\n' % (('BTC', 'ETH')[i % 2], 1757600000 + i * 9000) for i in range(20)))
    reg = [dict(alarm_id='KNOWN_K1', kind='KNOWN', seat='KNOWN', run='CLAUDE1_20261028', idea='K1FAM', V='K1', state='PASS (KEPT)',
                lean='FADE', one_line='Known alarm K1 (planted)', novelty_verdict='KNOWN', fire_list_rel='REGISTRY/fire_lists/K1_FIRES_V1_LIST.tsv',
                fire_list_sha16=sha16(k1), fires='20'),
           dict(alarm_id='AD1_FLOWX_V2', kind='OWN', seat='AD1', run=RUN, idea=IDEA, V='V2', state='PASS', lean='FOLLOW',
                one_line='FLOWX: a planted idea', novelty_verdict='NEW', nearest_before='KNOWN_K1', nearest_same_fires_pct='0.0',
                lead_1h='+7.00', t_1h='+3.50', waves='130', forward_months='2601 HELD; 2602 HELD; 2603 HELD; 2604 WEAKER',
                fire_list_rel='runs/%s/receipts/20263700_GRADE_FLOWX/V2_FIRES_V1_LIST.tsv' % RUN, fires='30')]
    w(os.path.join(H, 'REGISTRY', 'ALARM_REGISTRY_V1.tsv'), '# planted registry (docs test)\n' + tsv_rows(cols, reg))
    w(os.path.join(H, 'REGISTRY', 'FAMILY_TAGS_V1.tsv'), 'alarm_id\tfamily\nKNOWN_K1\tFLOWS\nAD1_FLOWX_V2\tFLOWS\n')
    w(os.path.join(root, 'part_clean', 'tool.py'), 'import os\nprint(os.getcwd())\n')
    w(os.path.join(root, 'part_dirty', 'tool.py'), "DATA = '/Users/someone/data'\n")  # machine-path-ok: test data for machine_paths_v2's dry run
    os.makedirs(os.path.join(root, 'forbidden'))
    vals = {'PYTHON': sys.executable, 'LAB_DAYS': os.path.join(root, 'lab_days'), 'SCRATCH': os.path.join(root, 'scratch_absent'),
            'RESEARCH_ROOT': rr, 'BOARD': hb, 'RUNNER_QUEUES': os.path.join(root, 'runner'), 'RUNNER_ALLOC': alloc, 'RESEARCH_STORE': os.path.join(root, 'research_days')}
    return w(os.path.join(root, 'SETTINGS_DOCS_TEST.env'), '# planted settings of the docs test\n' + ''.join(
        '%s=%s\n' % (k, vals.get(k, '')) for k in settings_v1.keys()))


def run_tool(t, args, settings, cwd):
    world = os.path.dirname(settings)
    argv = [a.replace('{SETTINGS}', settings).replace('{WORLD}', world).replace('{ALARM}', ALARM) for a in args]
    r = subprocess.run([sys.executable, '-B', os.path.join(ALARM, t['file'])] + argv, cwd=cwd, capture_output=True, text=True,
                       timeout=120)
    return r.returncode, r.stdout + r.stderr


# ---------------------------------------------------------------- T01 the generator's readers, on planted code
class T01Readers(unittest.TestCase):
    def setUp(self):
        self.a = tempfile.mkdtemp(prefix='agent_docs_t01_')

    def tearDown(self):
        shutil.rmtree(self.a)

    def put(self, rel, s):
        return w(os.path.join(self.a, rel), s)

    def test_seq_gives_each_string_with_its_line(self):
        self.put('x.py', "A = 1\nCOLS = ('a', 'b',\n        'c')\n")
        self.assertEqual(G.ex_seq(self.a, 'x.py', 'COLS'), [('a', 'x.py', 2), ('b', 'x.py', 2), ('c', 'x.py', 3)])
        with self.assertRaises(G.Stale):
            G.ex_seq(self.a, 'x.py', 'NOPE')

    def test_literal_headers_in_python_printf_and_awk(self):
        self.put('a.sh', "x=1\nprintf 'stage\\trc\\tnote\\n' > $ST\nprint \"m\\tn\"\n")
        self.put('b.sh', "printf 'stage\\trc\\tnote\\n' > $ST\n")
        self.assertEqual(G.ex_literal(self.a, ['a.sh', 'b.sh'], r'stage\trc'), [('stage', 'a.sh', 2), ('rc', 'a.sh', 2), ('note', 'a.sh', 2)])
        self.assertEqual([c for c, _, _ in G.ex_literal(self.a, ['a.sh'], r'm\tn')], ['m', 'n'])
        self.put('c.sh', "printf 'stage\\trc\\tother\\n' > $ST\n")
        with self.assertRaises(G.Stale):
            G.ex_literal(self.a, ['a.sh', 'c.sh'], r'stage\trc')

    def test_markdown_header(self):
        self.put('m.py', "L = ['| ID | LEAD 1h (t) | what it is |', '|---|']\n")
        self.assertEqual([c for c, _, _ in G.ex_md(self.a, 'm.py', '| ID |')], ['ID', 'LEAD 1h (t)', 'what it is'])

    def test_format_fields_must_match_the_names(self):
        self.put('f.py', "print('x %s pct, %d waves, %.1f%% (%-4s)' % (a, b, c, d))\n")
        self.assertEqual([c for c, _, _ in G.ex_fmt(self.a, 'f.py', 'x %s', ['a', 'b', 'c', 'd'])], ['a', 'b', 'c', 'd'])
        with self.assertRaises(G.Stale):
            G.ex_fmt(self.a, 'f.py', 'x %s', ['a', 'b', 'c'])
        self.put('j.py', "print('one %s '\n      'two %d' % (a, b))\nq = 'one more'\n")
        self.assertEqual(G.ex_fmt(self.a, 'j.py', 'one %s', ['a', 'b']), [('a', 'j.py', 1), ('b', 'j.py', 1)])
        with self.assertRaises(G.Stale):
            G.ex_fmt(self.a, 'j.py', 'one', ['a', 'b'])

    def test_keys_and_dict_keys(self):
        self.put('k.sh', 'awk \'{print "du\\t"$1}\'\n')
        self.assertEqual(G.ex_keys(self.a, 'k.sh', [r'"du\t"'], ['du']), [('du', 'k.sh', 1)])
        with self.assertRaises(G.Stale):
            G.ex_keys(self.a, 'k.sh', ['"gone"'], ['gone'])
        self.put('d.py', "row = {'a': 1}\nfields = dict(row)\nfields.update({'b': 2, 'c': 3})\nother = {'z': 0}\n")
        self.assertEqual(G.ex_dict_keys(self.a, 'd.py', ['row', 'fields']), ['a', 'b', 'c'])

    def test_options_exits_and_usage(self):
        src = ('"""t.py: a tool; --dry in a sentence is no option.\n\n  python3 -B <Alarm>/x/t.py --settings <f> <RUN>\n'
               '      [--write] [--entry-too-big]\n  --settings  the file\n"""\nimport sys\n'
               "def main(a):\n    if '--write' in a or '--entry-too-big' in a:\n        return 3\n    if not a:\n"
               "        raise SystemExit('USAGE')\n    return 0\nsys.exit(2)\n")
        self.assertEqual(G.code_options(src), ['--entry-too-big', '--write'])
        self.assertEqual(G.code_exits(src), [0, 1, 2, 3])
        self.assertEqual(G.usage_from_code(src, 't.py'), 'python3 -B <Alarm>/x/t.py --settings <f> <RUN> [--write] [--entry-too-big]')
        with self.assertRaises(G.Stale):
            G.usage_from_code(src, 'other.py')
        self.assertEqual(G.code_options("x = take_settings(a)\n"), ['--settings'])

    def tool(self):
        self.put('t/tool.py', '"""tool.py\n\n  python3 -B <Alarm>/t/tool.py --settings <f>\n"""\n'
                 "COLS = ('a', 'b')\nkey = 'RESEARCH_ROOT'\nif '--write' in []:\n    pass\n")
        return {'tool': 'tool', 'file': 't/tool.py', 'reads': [], 'outputs': [{'file': 'OUT.tsv', 'columns': ['seq', 't/tool.py', 'COLS']}]}

    def write_all(self, t, docs):
        for p, new, _ in G.plan_tool(self.a, docs, t):
            w(p, new)

    def test_refresh_keeps_hand_cells_adds_new_columns_and_drops_gone_ones(self):
        t, docs = self.tool(), os.path.join(self.a, 'docs')
        self.write_all(t, docs)
        dp = os.path.join(docs, 'dictionaries', 'tool_COLUMNS.tsv')
        rows = G.read_dict(dp)
        self.assertEqual(sorted(rows), [('OUT.tsv', 'a'), ('OUT.tsv', 'b')])
        self.assertEqual(rows[('OUT.tsv', 'a')]['meaning'], G.NOT_DOC)
        self.assertEqual(rows[('OUT.tsv', 'a')]['source_line'], 't/tool.py:5')
        txt = rd(dp).replace('OUT.tsv\ta\t%s' % G.NOT_DOC, 'OUT.tsv\ta\tthe a: `COLS`')
        w(dp, txt)
        jp = os.path.join(docs, 'cards', 'tool.TOOL.json')
        j = jload(jp)
        j['step'] = 'a hand-written step'
        j['outputs'][0]['where'] = 'hand-written where'
        w(jp, json.dumps(j))
        self.assertEqual(G.plan_tool(self.a, docs, t)[0][0], jp)          # only the layout of the TOOL.json differs
        self.write_all(t, docs)
        self.assertEqual(G.plan_tool(self.a, docs, t), [])
        self.put('t/tool.py', rd(os.path.join(self.a, 't/tool.py')).replace("COLS = ('a', 'b')", "COLS = ('a', 'c')"))
        todo = G.plan_tool(self.a, docs, t)
        self.assertTrue(any('new columns' in x[2] and 'DROPPED' in x[2] for x in todo), todo)
        self.write_all(t, docs)
        rows = G.read_dict(dp)
        self.assertEqual(sorted(rows), [('OUT.tsv', 'a'), ('OUT.tsv', 'c')])
        self.assertEqual(rows[('OUT.tsv', 'a')]['meaning'], 'the a: `COLS`')
        self.assertEqual(rows[('OUT.tsv', 'c')]['meaning'], G.NOT_DOC)
        j = jload(jp)
        self.assertEqual((j['step'], j['outputs'][0]['where'], j['outputs'][0]['columns']), ('a hand-written step', 'hand-written where', ['a', 'c']))
        self.assertEqual(j['file_sha16'], sha16(os.path.join(self.a, 't/tool.py')))
        self.assertEqual(j['settings_keys'], ['RESEARCH_ROOT'])

    def test_an_option_no_command_names_is_added(self):
        t, docs = self.tool(), os.path.join(self.a, 'docs')
        self.write_all(t, docs)
        jp = os.path.join(docs, 'cards', 'tool.TOOL.json')
        j = jload(jp)
        j['commands'][0]['args'] = []
        w(jp, json.dumps(j))
        self.write_all(t, docs)
        self.assertIn({'name': '--write', 'required': False, 'meaning': G.NOT_DOC, 'example': G.BY_HAND}, jload(jp)['commands'][0]['args'])

    def test_a_register_writer_must_match_its_register(self):
        os.makedirs(os.path.join(self.a, G.REGISTERS))
        w(os.path.join(self.a, G.REGISTERS, 'R.tsv'), 'utc\ta\tb\n')
        self.put('t/tool.py', '"""x\n\n  python3 -B <Alarm>/t/tool.py\n"""\nrow = {\'a\': 1, \'b\': 2}\n')
        t = {'tool': 'tool', 'file': 't/tool.py', 'reads': [],
             'outputs': [{'file': 'R.tsv', 'columns': ['register', 'R'], 'writer': ['dict_keys', 't/tool.py', ['row']]}]}
        self.assertEqual([c for c, _, _ in G.generated(self.a, t)[1][0]['columns']], ['utc', 'a', 'b'])
        self.put('t/tool.py', '"""x\n\n  python3 -B <Alarm>/t/tool.py\n"""\nrow = {\'a\': 1, \'z\': 2}\n')
        with self.assertRaises(G.Stale):
            G.generated(self.a, t)

    def test_check_exits_3_when_stale_and_0_when_in_step(self):
        docs = tempfile.mkdtemp(prefix='agent_docs_t01_docs_')
        try:
            only = ['--tool', 'board_line_v2', '--docs', docs]
            with open(os.devnull, 'w') as dn:
                old, sys.stdout = sys.stdout, dn
                try:
                    self.assertEqual(G.main(['--check'] + only), 3)
                    self.assertEqual(G.main(['--write'] + only), 0)
                    self.assertEqual(G.main(['--check'] + only), 0)
                    jp = os.path.join(docs, 'cards', 'board_line_v2.TOOL.json')
                    j = jload(jp)
                    j['file_sha16'] = '0' * 16
                    w(jp, json.dumps(j))
                    self.assertEqual(G.main(['--check'] + only), 3)
                    self.assertEqual(G.main(['--write'] + only), 0)
                    tw = [n for n in os.listdir(os.path.join(docs, 'cards')) if n.startswith('board_line_v2.TOOL.json.pre_agent_docs_')]
                    self.assertEqual(len(tw), 1)
                    self.assertEqual(jload(os.path.join(docs, 'cards', tw[0]))['file_sha16'], '0' * 16)
                    self.assertEqual(G.main(['--check'] + only), 0)
                finally:
                    sys.stdout = old
            with self.assertRaises(G.Refused):
                G.main(['--check', '--write'])
            with self.assertRaises(G.Refused):
                G.main(['--check', '--tool', 'nope'])
        finally:
            shutil.rmtree(docs)


# ---------------------------------------------------------------- T02 to T06: the real docs against the real code
class Docs(unittest.TestCase):
    pass


class T02Inventory(Docs):
    def test_every_tool_has_its_card_json_and_dictionary(self):
        for t in G.TOOLS:
            for rel in ('cards/%s.md' % t['tool'], 'cards/%s.TOOL.json' % t['tool'], 'dictionaries/%s_COLUMNS.tsv' % t['tool']):
                self.assertTrue(os.path.isfile(os.path.join(DOCS, rel)), 'MISSING %s' % rel)

    def test_nothing_left_to_write_by_hand_the_archive_line_and_no_em_dash(self):
        for t in G.TOOLS:
            for rel in ('cards/%s.md' % t['tool'], 'cards/%s.TOOL.json' % t['tool'], 'dictionaries/%s_COLUMNS.tsv' % t['tool']):
                txt = rd(os.path.join(DOCS, rel))
                self.assertNotIn(G.BY_HAND, txt, rel)
                self.assertNotIn(EM, txt, rel)
                self.assertIn(G.ARCHIVE_LINE, txt, '%s: the archive line' % rel)

    def test_no_machine_path_in_json_or_code(self):
        mp = os.path.join(TOOLS_DIR, 'machine_paths_v2.py')
        if not os.path.isfile(mp):
            self.skipTest('no _tools/machine_paths_v2.py in this Alarm folder')
        sys.path.insert(0, TOOLS_DIR)
        import machine_paths_v2 as MP
        files = [os.path.join(DOCS, 'cards', '%s.TOOL.json' % t['tool']) for t in G.TOOLS]
        files += [os.path.join(TOOLS_DIR, 'agent_docs_v1.py'), os.path.join(HERE, 'test_agent_docs_v1.py'), os.path.join(HERE, 'mutants_agent_docs_v1.py')]
        for f in files:
            if os.path.isfile(f):
                self.assertEqual([r for r in MP.file_rows(f) if r[2] == 'CODE'], [], f)


class T03InStep(Docs):
    def test_the_generator_finds_nothing_to_change(self):
        for t in G.TOOLS:
            todo = G.plan_tool(ALARM, DOCS, t)
            self.assertEqual([(os.path.relpath(p, DOCS), y) for p, _, y in todo], [], t['tool'])

    def test_listed_columns_equal_the_columns_the_code_writes(self):
        for t in G.TOOLS:
            gen, outs = G.generated(ALARM, t)
            rows = G.read_dict(os.path.join(DOCS, gen['dictionary']))
            j = tool_json(t['tool'])
            for o in outs:
                want = [c for c, _, _ in o['columns']]
                self.assertEqual([k[1] for k in rows if k[0] == o['file']], want, '%s %s dictionary' % (t['tool'], o['file']))
                jo = [x for x in j['outputs'] if x['file'] == o['file']]
                self.assertEqual(len(jo), 1, '%s %s in TOOL.json' % (t['tool'], o['file']))
                self.assertEqual(jo[0]['columns'], want, '%s %s TOOL.json' % (t['tool'], o['file']))
            self.assertEqual(sorted({k[0] for k in rows}), sorted(o['file'] for o in outs), t['tool'])

    def test_each_source_line_holds_its_column(self):
        for t in G.TOOLS:
            fmt = {o['file'] for o in t['outputs'] if o['columns'][0] == 'fmt'}
            for (f, c), r in G.read_dict(os.path.join(DOCS, 'dictionaries', '%s_COLUMNS.tsv' % t['tool'])).items():
                rel, n = r['source_line'].rsplit(':', 1)
                lines = rd(os.path.join(ALARM, rel)).split('\n')
                line = lines[int(n) - 1]
                self.assertIn('%' if f in fmt else c, line, '%s %s %s: %s' % (t['tool'], f, c, r['source_line']))

    def test_every_quote_is_in_the_code_and_every_meaning_quotes_it(self):
        for t in G.TOOLS:
            code = norm(' '.join(rd(os.path.join(ALARM, p)) for p in [t['file']] + t['reads']
                                 + ['%s/%s.tsv' % (G.REGISTERS, o['columns'][1]) for o in t['outputs'] if o['columns'][0] == 'register']))
            for (f, c), r in G.read_dict(os.path.join(DOCS, 'dictionaries', '%s_COLUMNS.tsv' % t['tool'])).items():
                if r['meaning'] != G.NOT_DOC:
                    self.assertTrue(QUOTE.search(r['meaning']), '%s %s %s: a meaning quotes the code in backticks' % (t['tool'], f, c))
                for k in ('meaning', 'unit', 'known_at', 'empty_means'):
                    self.assertTrue(r[k].strip(), '%s %s %s: %s empty' % (t['tool'], f, c, k))
                    for q in QUOTE.findall(r[k]):
                        self.assertIn(norm(q), code, '%s %s %s %s: `%s` is not in the code' % (t['tool'], f, c, k, q))


class T04Arguments(Docs):
    def test_arguments_and_exits_are_the_codes(self):
        for t in G.TOOLS:
            j = tool_json(t['tool'])
            gen, _ = G.generated(ALARM, t)
            named = set()
            for c in j['commands']:
                self.assertTrue(c.get('dry_runs'), '%s %s: no dry run' % (t['tool'], c['name']))
                for a in c['args']:
                    named.add(a['name'])
                    for k in ('required', 'meaning', 'example'):
                        self.assertIn(k, a, '%s %s %s' % (t['tool'], c['name'], a['name']))
                    if a['name'].startswith('--'):
                        self.assertIn(a['name'], gen['code_options'], '%s: %s is not an option of the code' % (t['tool'], a['name']))
                    else:
                        self.assertIn(a['name'], gen['usage_from_code'], '%s: %s is not in the usage line' % (t['tool'], a['name']))
                for x in c['refuses'] + c['dry_runs']:
                    self.assertIn(x['exit'], gen['code_exits'], '%s %s: exit %s is not one the code names' % (t['tool'], c['name'], x['exit']))
                head = 'python3 -B %s/%s ' % (G.INSTALL, t['file'])
                if '--settings' in gen['code_options']:
                    head += '--settings %s/settings/SETTINGS_' % G.INSTALL
                self.assertTrue(c['example'].startswith(head), '%s %s example: %s' % (t['tool'], c['name'], c['example']))
            self.assertEqual(sorted(o for o in gen['code_options'] if o not in named), [], '%s: options of the code no command names' % t['tool'])
            self.assertTrue(j['refusal_probes'], t['tool'])
            for p in j['refusal_probes']:
                self.assertIn(p['exit'], gen['code_exits'], t['tool'])
                self.assertNotEqual(p['exit'], 0, t['tool'])


class T05Commands(Docs):
    @classmethod
    def setUpClass(cls):
        cls.root = tempfile.mkdtemp(prefix='agent_docs_world_')
        cls.settings = build_world(cls.root)
        cls.cwd = os.path.join(cls.root, 'cwd')
        os.makedirs(cls.cwd)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root)

    def test_every_command_runs_dry_and_exits_as_documented(self):
        n = 0
        for t in G.TOOLS:
            for c in tool_json(t['tool'])['commands']:
                for d in c['dry_runs']:
                    rc, out = run_tool(t, d['args'], self.settings, self.cwd)
                    self.assertEqual(rc, d['exit'], '%s %s %s: rc %d\n%s' % (t['tool'], c['name'], d['args'], rc, out[-1500:]))
                    self.assertIn(d['prints'], out, '%s %s %s\n%s' % (t['tool'], c['name'], d['args'], out[-1500:]))
                    n += 1
        self.assertGreaterEqual(n, len(G.TOOLS))
        left = [p for q in ('Q_V1', 'Q_V2') for s in ('IN', 'RUN') for p in os.listdir(os.path.join(self.root, 'runner', q, s))]
        self.assertEqual(left, [], 'a dry run queued a job')

    def test_each_tools_refusals_exit_as_documented(self):
        for t in G.TOOLS:
            for p in tool_json(t['tool'])['refusal_probes']:
                rc, out = run_tool(t, p['args'], self.settings, self.cwd)
                self.assertEqual(rc, p['exit'], '%s %s: rc %d\n%s' % (t['tool'], p['args'], rc, out[-800:]))
                self.assertIn(p['prints'], out, '%s %s' % (t['tool'], p['args']))


class T06Cards(Docs):
    def test_sections_links_command_keys_and_exits(self):
        for t in G.TOOLS:
            md, j = card(t['tool']), tool_json(t['tool'])
            s = sections(md)
            self.assertEqual([k for k in s if k in G.CARD_SECTIONS], G.CARD_SECTIONS, '%s: the six sections in order' % t['tool'])
            for k in G.CARD_SECTIONS:
                self.assertTrue(s[k].strip(), '%s: %s is empty' % (t['tool'], k))
            base = os.path.join(DOCS, 'cards')
            links = LINK.findall(md)
            for target in links:
                if re.match(r'^[a-z]+://', target) or target.startswith('#'):
                    continue
                self.assertTrue(os.path.exists(os.path.normpath(os.path.join(base, target.split('#')[0]))),
                                '%s: the link %s does not resolve' % (t['tool'], target))
            for must in ('%s.TOOL.json' % t['tool'], '../dictionaries/%s_COLUMNS.tsv' % t['tool'], '../' + t['file']):
                self.assertIn(must, links, '%s: no link to %s' % (t['tool'], must))
            run = 'python3 -B <INSTALL>/%s ' % t['file'] + ('--settings <INSTALL>/settings/SETTINGS_' if '--settings' in j['code_options'] else '')
            self.assertIn(run, s['Run it'], t['tool'])
            for k in j['settings_keys']:
                self.assertIn(k, s['Where its data comes from'], '%s: settings key %s' % (t['tool'], k))
            for e in j['code_exits']:
                self.assertIn('exit %d' % e, s['Limits and refusals'], '%s: exit %d' % (t['tool'], e))


if __name__ == '__main__':
    unittest.main(verbosity=1)
