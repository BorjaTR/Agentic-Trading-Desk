"""OUTSIDE A30 (OX-SKEPTIC, APPROVAL_fairness_bar_V2_1): F01 one shared wave partition across receipts, F02 the typed census. The ten
cases of OX-SKEPTIC's tests/a30/test_fairness.py ported to run on the landed code (theirs build an in-memory candidate from the old sha16),
plus the writer in force (ledger_add_v6: a 5-column types file, a legacy untyped parent) and two mutants. Planted data only; analyst venv."""
import datetime as dt, hashlib, os, sys, tempfile, types, unittest
import numpy as np
HERE = os.path.dirname(os.path.realpath(__file__)); FB = os.path.realpath(os.path.join(HERE, '..')); TOOLS = os.path.realpath(os.path.join(FB, '..'))
sys.path.insert(0, FB); sys.path.insert(0, TOOLS)
import fairness_bar_v2 as F  # noqa: E402
D = tempfile.mkdtemp(); T0 = 1760097600
FAMS = os.path.join(D, 'FAMILIES_PLANT.tsv')
open(FAMS, 'w').write('pattern\tsource\tfamily\twhy\nALPHA\tany\tALPHA\tplant\nBETA\tany\tBETA\tplant\nGAMMA\tany\tGAMMA\tplant\n')
SET = dict(flips=100, day_boot=100, families_path=FAMS, seed=17); N = [0]
WSHA = hashlib.sha256(open(os.path.join(TOOLS, 'labcore', 'waves.py'), 'rb').read()).hexdigest()[:16]
V = np.random.default_rng(3).normal(0.3, 1, 24)


def receipt(vals, prefix='w', offset=0, step=86400):
    N[0] += 1; p = os.path.join(D, 'receipt_%d.tsv' % N[0]); lines = ['# wave_module_sha16=' + WSHA, 'wave_id\tvalue\tmonth\tday\tn_fires\tfires']
    for i, v in enumerate(vals):
        t = T0 + offset + step * i; day = dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime('%Y%m%d')
        lines.append('%s%d\t%s\t%s\t%s\t1\tSYNTH@%d' % (prefix, i, v, day[:6], day, t))
    open(p, 'w').write('\n'.join(lines) + '\n'); return p


def tries():
    return [dict(try_utc='20261023T090000Z', ask_id='A', text='ALPHA', source='ledger'), dict(try_utc='20261023T080000Z', ask_id='B', text='ALPHA', source='ledger')]


def bar(a, b, mod=None):
    return (mod or F).bar(a, 'A', settings=SET, tries=tries(), roster={'B': b})


def plant(ledger_rows, types_text):
    N[0] += 1; p = os.path.join(D, 'L%d' % N[0]); os.makedirs(p); led = os.path.join(p, 'TRIES_LEDGER_V1.tsv'); tp = os.path.join(p, 'TRIES_TYPES_V1.tsv')
    open(led, 'w').write('try_utc\task_id\tidea\tpurpose\tstatus\n' + ''.join('%s\t%s\t%s\ttest\tPREREG\n' % r for r in ledger_rows)); open(tp, 'w').write(types_text)
    return led, tp


def census(led, tp=None, mod=None):
    m = mod or F; tr = m.V1.read_tries({'ledger': led, 'types': tp} if tp else {'ledger': led})
    return m.census_v2(tr, m.family_rows(FAMS), {}, '20261023T100000Z')


class Waves(unittest.TestCase):                                   # A30-F01, Rule 1
    def test_same_fires_relabeling_is_irrelevant(self):
        a = receipt(V); b = receipt(V); renamed = receipt(V, prefix='other')
        self.assertEqual(bar(a, b)['sr_star_flips'], bar(a, renamed)['sr_star_flips'])

    def test_different_fires_aliasing_labels_is_irrelevant(self):
        a = receipt(V); b = receipt(-V, offset=4000); renamed = receipt(-V, prefix='other', offset=4000)
        self.assertEqual(bar(a, b)['sr_star_flips'], bar(a, renamed)['sr_star_flips'])

    def test_close_fires_share_one_market_wave(self):
        a = receipt(V); b = receipt(-V, prefix='other', offset=60); exact = receipt(-V)
        self.assertEqual(bar(a, b)['sr_star_flips'], bar(a, exact)['sr_star_flips'])

    def test_identical_fires_and_values_control(self):
        self.assertTrue(np.isfinite(bar(receipt(V), receipt(V))['sr_star_flips']))

    def test_joint_partition_bridge_requires_rebuilt_values(self):
        with self.assertRaises(ValueError):
            bar(receipt([1, 2], step=3600), receipt([1], offset=1800))

    def test_incorrect_day_still_refused(self):
        a = receipt(V); open(a, 'w').write(open(a).read().replace('20251010', '20251009'))
        with self.assertRaises(ValueError):
            F.read_receipt(a)


class TypedCensus(unittest.TestCase):                             # A30-F02, Rule 2
    def test_typed_family_overrides_legacy_name(self):
        led, tp = plant([('20261023T090000Z', 'X', 'ALPHA')], 'ask_id\ttype\tfamily\tparent_ask_id\nX\tCHART_READ\tBETA\t\n')
        got = census(led, tp); self.assertIn('BETA', got); self.assertNotIn('X', [t['ask_id'] for t in got.get('ALPHA', [])])

    def test_unknown_typed_family_refused(self):
        led, tp = plant([('20261023T090000Z', 'Y', 'ALPHA')], 'ask_id\ttype\tfamily\tparent_ask_id\nY\tCHART_READ\tUNKNOWN_FAMILY\t\n')
        with self.assertRaises(ValueError):
            census(led, tp)

    def test_typed_parent_is_also_counted(self):
        led, tp = plant([('20261023T090000Z', 'CHILD', 'BETA'), ('20261023T080000Z', 'PARENT', 'ALPHA')],
                        'ask_id\ttype\tfamily\tparent_ask_id\nPARENT\tSTRATEGY_MONEY\tALPHA\t\nCHILD\tCHART_READ\tBETA\tPARENT\n')
        self.assertEqual(len(census(led, tp)['ALPHA']), 2)

    def test_cycle_refused(self):
        led, tp = plant([('20261023T090000Z', 'X', 'ALPHA')], 'ask_id\ttype\tfamily\tparent_ask_id\nX\tCHART_READ\tALPHA\tX\n')
        with self.assertRaises(ValueError):
            F.V1.read_tries({'ledger': led, 'types': tp})

    # ---- the writer in force (ledger_add_v6)
    def test_v6_five_column_file_and_adjacent_discovery(self):
        led, tp = plant([('20261023T090000Z', 'X', 'ALPHA')], 'ask_id\ttype\tfamily\tparent_ask_id\ttry_utc\nX\tCHART_READ\tBETA\t\t20261023T090000Z\n')
        self.assertIn('BETA', census(led))                       # found beside the ledger, no 'types' key needed

    def test_v6_legacy_parent_history_inherited(self):
        led, tp = plant([('20261023T090000Z', 'CHILD', 'BETA'), ('20261023T080000Z', 'OLD', 'GAMMA idea')],
                        'ask_id\ttype\tfamily\tparent_ask_id\ttry_utc\nCHILD\tCHART_READ\tBETA\tOLD\t20261023T090000Z\n')
        cut = os.path.join(os.path.dirname(led), 'CUT.json')                  # A36-F01: the untyped parent is legacy only under a record
        F.V1.make_typing_cut(led, cut, '20261023T085000Z', 'test', 'plant')
        tr = F.V1.read_tries({'ledger': led, 'types': tp, 'typing_cut': cut})
        got = F.census_v2(tr, F.family_rows(FAMS), {}, '20261023T100000Z'); self.assertEqual(sorted(t['ask_id'] for t in got['GAMMA']), ['CHILD', 'OLD'])

    def test_unresolved_parent_refused_and_bad_schema_refused(self):
        led, tp = plant([('20261023T090000Z', 'X', 'ALPHA')], 'ask_id\ttype\tfamily\tparent_ask_id\nX\tCHART_READ\tALPHA\tNOWHERE\n')
        with self.assertRaises(ValueError):
            F.V1.read_tries({'ledger': led, 'types': tp})
        led, tp = plant([('20261023T090000Z', 'X', 'ALPHA')], 'ask_id\tkind\tfamily\tparent_ask_id\nX\tCHART_READ\tALPHA\t\n')
        with self.assertRaises(ValueError):
            F.V1.read_tries({'ledger': led, 'types': tp})

    def test_reader_constants_equal_the_writer(self):
        sys.path.insert(0, os.path.join(TOOLS, 'ledger')); import ledger_add_v6 as L6
        self.assertEqual(F.V1.TYPED_COLS, L6.TYPES_COLS[:4]); self.assertEqual(tuple(F.V1.TYPED_TYPES), tuple(L6.TYPES))


class Mutants(unittest.TestCase):
    def test_mutants(self):
        for path, old, new, case in (
                (F.__file__, "    aligned = align_receipt_waves([W] + list(other.values()), s['gap_s'])\n    W = aligned[0]\n    other = dict(zip(other, aligned[1:]))\n",
                 "", (Waves, 'test_same_fires_relabeling_is_irrelevant')),
                (F.__file__, "    if '_typed_families' in t:", "    if False:", (TypedCensus, 'test_typed_family_overrides_legacy_name'))):
            src = open(path).read(); self.assertEqual(src.count(old), 1, old[:60])
            m = types.ModuleType('fb_mut'); m.__file__ = path; exec(compile(src.replace(old, new), path, 'exec'), m.__dict__)
            keep = globals()['F']; globals()['F'] = m
            try:
                r = unittest.TextTestRunner(stream=open(os.devnull, 'w')).run(case[0](case[1]))
                self.assertFalse(r.wasSuccessful(), 'mutant survived: ' + case[1])
            finally:
                globals()['F'] = keep


if __name__ == '__main__':
    unittest.main()
