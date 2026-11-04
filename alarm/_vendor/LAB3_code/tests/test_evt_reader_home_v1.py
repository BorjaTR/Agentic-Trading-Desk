"""test_evt_reader_home_v1.py (BUILD5, D2 landing step 2, 31 Oct 2026; CONDUCTOR review REVIEW_BUILD5_D2_LAB3_EVT.md e4e08b51 M1 HOW (2): "A
planted test in each reader home: an evt1 root reads, an old root reads byte-identical"; TEST, NOT REVIEWED). Run it in a home that READS OUT.*
parts, on the lab3 that home vendors, after its vendor --update and before any current tool writes evt1. Seconds, no data store, temp files only.
  python3 -B test_evt_reader_home_v1.py <the folder holding the home's lab3 package (e.g. <home>/_vendor/LAB3_code)>
Checks: the home's lab3 has evt.py and dispatches an evt1 root to EvtDays; the same planted ROWS parts written in both layouts answer the same
for rows, at (300 s), words, reasons, step, coins_with_rows and part_of; reading never changes a byte of the old root; MIXED_LAYOUT refused.
The planted rows are test_evt_v1.py's (bc217e66524c6033), copied. Exit 0 = PASS."""
import os, shutil, struct, sys, tempfile, unittest

CODE = os.path.realpath(sys.argv.pop(1) if len(sys.argv) > 1 else os.environ['HOME_LAB3_CODE'])
sys.path.insert(0, CODE)
from lab3 import days as DY, write as LW                     # noqa: E402
try:
    from lab3 import evt as EV                               # noqa: E402
except ImportError as e:                                     # the home has not vendored D2: refused by name
    raise SystemExit('REFUSED NO_EVT: %s/lab3 has no evt.py (%s): run vendor --update first' % (CODE, e))

D0, D1 = '20251001', '20251002'
COINS = ['BTC', 'ETH', 'SOL', 'XRP']                                         # XRP: no rows
CAT = {c: {'kind': 'ROWS', 'clock': 'event', 'exact_k': False, 'scope': 'coin'} for c in ('C_NUM', 'C_WORD', 'C_EMPTY', 'C_MIX')}
US = 1_000_000


def bits(x):
    return struct.unpack('<Q', struct.pack('<d', x))[0]


def t0(day):
    return DY._day_start_us(day)


def rows(day, spec):
    """spec: [(as_of s after 00:00 or None, known_at s after as_of, kind, bits, text, reason, stale, which day: 0 this, -1 the day before)]"""
    c = {k: [] for k in LW.COLS}
    for a, k, kind, b, txt, er, st, dd in spec:
        d = day if dd == 0 else DY._prev(day)
        c['day'].append(int(d)); c['as_of_us'].append(None if a is None else t0(d) + a * US)
        c['known_at_us'].append(None if a is None else t0(d) + (a + k) * US); c['value_kind'].append(kind); c['value_bits'].append(b)
        c['value_txt'].append(txt); c['empty_reason'].append(er); c['stale'].append(st)
    return c


def codes_for(day):
    nan = bits(float('nan'))
    num = {'BTC': rows(day, [(30, 3, 1, bits(1.5), None, '', 0, 0), (10, 2, 1, nan, None, 'PATH_GAP', 0, 0), (10, 2, 1, bits(-0.0), None, '', 1, 0),
                             (None, 0, 1, bits(2.0), None, '', 0, 0), (82000, 5, 1, bits(-7.25e-9), None, 'NO_PRICE', 0, -1)]),
           'ETH': rows(day, [(3600, 0, 0, None, None, 'NOT_REACHED', 0, 0), (7200, 60, 2, bits(42.0), None, '', 0, 0)]),
           'SOL': rows(day, [(5, 1, 1, None, 'UP', '', 0, 0)])}
    word = {'BTC': rows(day, [(100, 1, 3, None, 'FADE', '', 0, 0), (200, 1, 3, None, 'FOLLOW', '', 1, 0), (300, 1, 3, None, 'FADE', 'X', 0, 0)]),
            'SOL': rows(day, [(50, 0, 3, None, 'NONE', 'NO_DIRECTION', 0, 0)])}
    mix = {'ETH': rows(day, [(i * 600, i % 3, (1, 3, 0)[i % 3], bits(i / 7) if i % 3 == 0 else None, 'w%d' % (i % 4) if i % 3 == 1 else None,
                              ('', 'NO_UNIT:NO_ROW', 'PATH_GAP')[i % 3], i % 2, 0) for i in range(40)])}
    return {'C_NUM': {'step': 'event', 'kind': 'NUMBER', 'rows': num}, 'C_WORD': {'step': 'event', 'kind': 'WORD', 'rows': word},
            'C_EMPTY': {'step': 'event', 'kind': 'NUMBER', 'rows': {}}, 'C_MIX': {'step': 'event', 'kind': 'NUMBER', 'rows': mix}}


def build(root, writer, part='OUT.TEST'):
    for d in (D0, D1):
        writer(root, d, part, codes_for(d), COINS, catalog=CAT, sources={'events:x.tsv': '0123456789abcdef'}, seal='S')


def answers(DaysCls, root, part='OUT.TEST'):
    rd = DaysCls(root, 'build'); out = {}
    for d in (D0, D1):
        for code in sorted(CAT):
            out[(d, code, 'rows')] = rd.rows(code, d, COINS + ['DOGE'])
            out[(d, code, 'words')] = rd.words(code, d); out[(d, code, 'reasons')] = rd.reasons(code, d)
            out[(d, code, 'step')] = rd.step(code, d); out[(d, code, 'cwr')] = rd.coins_with_rows(code, d)
            out[(d, code, 'part')] = rd.part_of(code, d)
    for code in sorted(CAT):
        a = rd.at(code, [D1], COINS + ['DOGE'], 300)
        out[(D1, code, 'at')] = {k: (v.view('<u8').tolist() if v.dtype == float else v.tolist()) for k, v in a.items()}
    return out


def tree_shas(root):
    out = {}
    for d, _, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            with open(p, 'rb') as fh:
                out[os.path.relpath(p, root)] = DY.sha16_bytes(fh.read())
    return out




class Home(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(); self.old = os.path.join(self.tmp, 'old'); self.evt = os.path.join(self.tmp, 'evt')
        build(self.old, LW.write_part); build(self.evt, EV.write_part)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_the_home_lab3_is_d2(self):
        self.assertIs(type(DY.Days(self.evt, 'build')), EV.EvtDays); self.assertIs(type(DY.Days(self.old, 'build')), DY.Days)
        self.assertTrue(hasattr(DY, 'MixedLayout'))

    def test_every_answer_equal(self):
        a = answers(DY.Days, self.old); b = answers(DY.Days, self.evt)
        self.assertEqual(sorted(a), sorted(b))
        for k in a:
            self.assertEqual(a[k], b[k], k)
        self.assertTrue(a[(D1, 'C_WORD', 'words')])                  # the fixture really has words

    def test_old_root_bytes_unchanged_by_reading(self):
        before = tree_shas(self.old); answers(DY.Days, self.old); self.assertEqual(tree_shas(self.old), before)

    def test_mixed_refused(self):
        shutil.copytree(os.path.join(self.evt, 'day=%s' % D1, 'OUT.TEST'), os.path.join(self.old, 'day=%s' % D1, 'OUT.EVTX'))
        with self.assertRaises(DY.MixedLayout):
            DY.Days(self.old, 'build').index(D1, 'OUT.EVTX')


if __name__ == '__main__':
    unittest.main(verbosity=1)
