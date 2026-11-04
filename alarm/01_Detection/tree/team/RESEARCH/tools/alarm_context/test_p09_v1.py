"""test_p09_v1 (BUILD2, 23 Oct 2026; STRATEGY-143328, OX-SKEPTIC P09): P09-01 the A6 wall veto holds at READ time for stored parts built
before the ban (keys kept, values NaN, reason in alarm_context.DISABLED); P09-02 a list with no size column (A02N) leaves burst_log_usd,
burst_rel_prior and days_since_bigger_alarm unknown, never filled from another size. Mutants killed: drop the read veto; fill S with 1."""
import os, sys, tempfile, unittest
import numpy as np
HERE = os.path.dirname(os.path.realpath(__file__)); sys.path.insert(0, HERE)
import alarm_context as AC  # noqa: E402
from test_alarm_context import ALL, D0, FakeSrc, run  # noqa: E402


class StoredDays:
    """a planted research root as alarm_context.read sees it: one day, one EVENT part, an OLD finite wall value and hour_utc"""
    def __init__(self):
        self.d = '20251015'

    def days(self):
        return [self.d]

    def parts(self, day):
        return ['CTX.A02N.EVENT']

    def index(self, day, part):
        return {'coins': ['AAA']}

    def rows(self, code, day, coins):
        v = {'CTX.A02N.wall_ahead_log_1pct': 5.0, 'CTX.A02N.hour_utc': 12.0}[code]
        return {'AAA': {'value_bits': [int(np.array([v], '<f8').view('<u8')[0])], 'as_of_us': [1], 'known_at_us': [1]}}


class T(unittest.TestCase):
    def test_read_veto_on_old_parts(self):
        x = AC.read('/r', '/c', 'A02N', '20251015', '20251015', ['wall_ahead_log_1pct', 'hour_utc'], days_reader=StoredDays())
        self.assertEqual(len(x['wall_ahead_log_1pct']), 1); self.assertTrue(np.isnan(x['wall_ahead_log_1pct'][0]))
        self.assertEqual(x['hour_utc'][0], 12.0)
        self.assertEqual(len(AC.DISABLED), 6); self.assertTrue(all(r.startswith('SOURCE_USE_PROHIBITED') for r in AC.DISABLED.values()))

    def test_no_size_column_stays_unknown(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 'N0_EVENTS.tsv'); t = D0 + 600 * 60
            open(p, 'w').write('coin\tt\tside\tonset_t\nAAA\t%d\t1\t%d\nAAA\t%d\t1\t%d\n' % (t - 7200, t - 7240, t, t - 40))
            ev = AC.load_events(p)
        self.assertTrue(np.isnan(ev['S']).all())
        e = AC.expand(ev, (0.0,)); x = run(e, FakeSrc(['AAA'], before=31), hist={k: ev[k] for k in ('coin', 't', 'S')})
        for k in ('burst_log_usd', 'burst_rel_prior', 'days_since_bigger_alarm'):
            self.assertTrue(np.isnan(x[k]).all(), k)


if __name__ == '__main__':
    unittest.main()
