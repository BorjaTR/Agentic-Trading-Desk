"""OUTSIDE A36 (OX-SKEPTIC, APPROVAL_fairness_bar_V2_2; STRATEGY-202600): F01 an untyped ledger row is refused unless an explicit migration
record covers its ledger, its stamp predates the cut and the record's legacy set is exactly what is found; F02 the result binds the census,
typed source, migration record, family map, settings, every receipt and the shared partition by sha16. Planted data only; analyst venv."""
import os, sys, tempfile, types, unittest
import numpy as np
HERE = os.path.dirname(os.path.realpath(__file__)); sys.path.insert(0, HERE)
import test_fairness_bar_v2_a30 as A  # noqa: E402  (the planted receipts, families and ledgers of the A30 suite)
F = A.F; D = tempfile.mkdtemp(); N = [0]
TYPED = 'ask_id\ttype\tfamily\tparent_ask_id\ttry_utc\n'


def ledger(rows, types_rows=''):
    N[0] += 1; p = os.path.join(D, 'L%d' % N[0]); os.makedirs(p); led = os.path.join(p, 'TRIES_LEDGER_V1.tsv')
    open(led, 'w').write('try_utc\task_id\tidea\tpurpose\tstatus\n' + ''.join('%s\t%s\t%s\ttest\tPREREG\n' % r for r in rows))
    if types_rows:
        open(os.path.join(p, 'TRIES_TYPES_V1.tsv'), 'w').write(TYPED + types_rows)
    return led, os.path.join(p, 'CUT.json')


def read(led, cut):
    return F.V1.read_tries({'ledger': led, 'typing_cut': cut})


OLD = [('20261023T080000Z', 'O1', 'ALPHA'), ('20261023T081000Z', 'O2', 'BETA')]


class Migration(unittest.TestCase):
    def test_no_record_refuses_untyped(self):
        led, cut = ledger(OLD)
        with self.assertRaises(ValueError):
            read(led, cut)                                          # absence of a record never makes a row legacy

    def test_record_makes_pre_cut_rows_legacy(self):
        led, cut = ledger(OLD); F.V1.make_typing_cut(led, cut, '20261023T090000Z', 'test', 'plant')
        tr = read(led, cut); self.assertTrue(all(t.get('_legacy_by_cut') for t in tr))
        with self.assertRaises(ValueError):
            F.V1.make_typing_cut(led, cut, '20261023T090000Z', 'test', 'again')   # written once

    def test_untyped_row_after_the_cut_refused(self):
        led, cut = ledger(OLD); F.V1.make_typing_cut(led, cut, '20261023T090000Z', 'test', 'plant')
        open(led, 'a').write('20261023T093000Z\tNEW\tALPHA\ttest\tPREREG\n')
        with self.assertRaisesRegex(ValueError, 'at or after the typing cut .*ledger_add_v6'):     # the seat is told what to do
            read(led, cut)

    def test_backdated_untyped_row_refused(self):
        led, cut = ledger(OLD); F.V1.make_typing_cut(led, cut, '20261023T090000Z', 'test', 'plant')
        open(led, 'a').write('20261023T082000Z\tSNEAK\tALPHA\ttest\tPREREG\n')
        with self.assertRaises(ValueError):
            read(led, cut)

    def test_typed_row_after_the_cut_passes(self):
        led, cut = ledger(OLD + [('20261023T093000Z', 'NEW', 'ALPHA')], 'NEW\tCHART_READ\tBETA\t\t20261023T093000Z\n')
        F.V1.make_typing_cut(led, cut, '20261023T090000Z', 'test', 'plant')
        tr = {t['ask_id']: t for t in read(led, cut)}; self.assertEqual(tr['NEW']['_typed_families'], ['BETA'])

    def test_complete_typing_needs_no_record(self):
        led, cut = ledger([('20261023T093000Z', 'X', 'ALPHA')], 'X\tCHART_READ\tALPHA\t\t20261023T093000Z\n')
        self.assertEqual(len(read(led, cut)), 1)

    def test_record_for_another_ledger_does_not_cover(self):
        led, cut = ledger(OLD); F.V1.make_typing_cut(led, cut, '20261023T090000Z', 'test', 'plant')
        led2, _ = ledger(OLD)
        with self.assertRaises(ValueError):
            read(led2, cut)


class Identity(unittest.TestCase):
    def test_result_binds_inputs_and_partition(self):
        a = A.receipt(A.V); b = A.receipt(A.V); renamed = A.receipt(A.V, prefix='other'); moved = A.receipt(A.V, offset=7200)
        e1, e2, e3 = A.bar(a, b)['evidence'], A.bar(a, renamed)['evidence'], A.bar(a, moved)['evidence']
        self.assertEqual(e1['schema'], 'FAIRNESS_INPUT_IDENTITY_V1')
        for k in ('census_sha16', 'typed_source_sha16s', 'typing_cut_sha16s', 'family_map_sha16', 'settings_sha16', 'roster_sha16s', 'shared_partition_sha16'):
            self.assertIn(k, e1)
        self.assertEqual(e1['shared_partition_sha16'], e2['shared_partition_sha16'])      # label renaming: same partition
        self.assertNotEqual(e1['shared_partition_sha16'], e3['shared_partition_sha16'])   # distinct fires: a new identity
        self.assertEqual(set(e1['roster_sha16s']), {'A', 'B'})


class Mutants(unittest.TestCase):
    def test_mutants(self):
        path = F.V1.__file__; src = open(path).read()
        for old, new, case in (("        if late:\n", "        if False:\n", 'test_untyped_row_after_the_cut_refused'),
                               ("        if len(found) != cut['legacy_ids'] or legacy_sha16(found) != cut['legacy_ids_sha16']:\n", "        if False:\n",
                                'test_backdated_untyped_row_refused'),
                               ("        if cut is None or led != cut['ledger_path']:\n", "        if False:\n", 'test_no_record_refuses_untyped')):
            self.assertEqual(src.count(old), 1, old[:60])
            m = types.ModuleType('fbv1_mut'); m.__file__ = path; exec(compile(src.replace(old, new), path, 'exec'), m.__dict__)
            keep = F.V1; F.V1 = m
            try:
                r = unittest.TextTestRunner(stream=open(os.devnull, 'w')).run(Migration(case))
                self.assertFalse(r.wasSuccessful(), 'mutant survived: ' + case)
            finally:
                F.V1 = keep


if __name__ == '__main__':
    unittest.main()
