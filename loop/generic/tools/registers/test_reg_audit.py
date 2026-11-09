#!/usr/bin/env python3
"""test_reg_audit.py (SCOUT 2026-11-08, C89 from AUD1_a): planted ledger and drill rows for reg.unverified(); no files written.
python3 -B test_reg_audit.py"""
import importlib.util, os, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('reg', os.path.join(HERE, 'reg.py')); reg = importlib.util.module_from_spec(spec); spec.loader.exec_module(reg)
def L(i, utc, c, v='pending_x'): return {'led_id': i, 'utc': utc, 'change_id': c, 'verified_by': v}
def D(utc, mins, finding, drill='READER'): return {'utc': utc, 'minutes': str(mins), 'finding': finding, 'drill_id': drill}
class T(unittest.TestCase):
    def ids(self, led, dr): return [r['led_id'] for r in reg.unverified(led, dr)]
    def test_started_after_change_closes(self):
        self.assertEqual(self.ids([L('G1', '2026-11-08T10:00:00Z', 'C87')], [D('2026-11-08T10:10:00Z', 5, 'verifies C87')]), [])
    def test_started_before_change_stays_open(self):        # REAS-A/B case: logged after the change, started before it
        self.assertEqual(self.ids([L('G1', '2026-11-08T10:00:00Z', 'C87')], [D('2026-11-08T10:03:00Z', 6, 'verifies C87')]), ['G1'])
    def test_whole_id_only(self):                             # C8 must not match C87, G012 must not match G0124
        self.assertEqual(self.ids([L('G0124', '2026-11-08T10:00:00Z', 'C87')], [D('2026-11-08T11:00:00Z', 1, 'verifies C8 and G012')]), ['G0124'])
    def test_list_of_ids(self):
        self.assertEqual(self.ids([L('G1', '2026-11-08T10:00:00Z', 'C72'), L('G2', '2026-11-08T10:00:00Z', 'C86')],
                                  [D('2026-11-08T11:00:00Z', 1, 'verifies C72, C86 and G0099')]), [])
    def test_superseded_only_from_loop_audit(self):
        led = [L('G1', '2026-11-08T10:00:00Z', 'C51')]
        self.assertEqual(self.ids(led, [D('2026-11-08T11:00:00Z', 1, 'superseded G1 by C80')]), ['G1'])
        self.assertEqual(self.ids(led, [D('2026-11-08T11:00:00Z', 1, 'superseded G1 by C80', 'LOOP_AUDIT')]), [])
    def test_named_verifier_not_pending_is_closed(self):
        self.assertEqual(self.ids([L('G1', '2026-11-08T10:00:00Z', 'C1', v='H08')], []), [])
if __name__ == '__main__':
    unittest.main(verbosity=1)
