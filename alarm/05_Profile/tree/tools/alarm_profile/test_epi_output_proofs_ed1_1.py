# test_epi_output_proofs_ed1_1.py: new edition by SCOUT for the clean release (30 Oct 2026; the owner 23:07 Berlin: "All alarm tools should work from the release
# folder only"). Owner QUANT. Old file: test_epi_output_proofs.py dbd34c052b8e7570, never edited. Changed: only its import (test_alarm_profile_ed1_1).
"""OUTPUT PROOFS of the 36 profile readings (ASK STRATEGY-145941a; OUTSIDE A09 rule: a reading is PROVEN only with its OWN proof): every
value against its hand answer on the planted episode of test_alarm_profile (push up and its mirror), known at the alarm (1e12 planted
after it changes nothing), and the EMPTY rule of each reading on planted cases (no print in the onset window, silent forcing, a short
burst, a hole in the hour before, a flat price, an unknown A01 bar). The cards are EPI_OUTPUT_PROOFS_V1.tsv; a test here names the card
rows it proves (proof O1_PLANT). Defect EPI-D1 (QUANT 23 Oct): a price GAP (no bin) carries the last close of any age into the 15 min and
1 min grids; its test is an expected failure until episode_blocks reads a close older than 60 s as a hole."""
import csv, math, os, sys, unittest
import numpy as np
HERE = os.path.dirname(os.path.realpath(__file__)); sys.path.insert(0, HERE)
_argv = sys.argv[:]; sys.argv = sys.argv[:1]
import test_alarm_profile_ed1_1 as TP                                       # noqa: E402  (its argv hook takes a lab3 dir; none here)
sys.argv = _argv
import episode_blocks as EB                                          # noqa: E402

T, T0, T5 = TP.T, TP.T0, TP.T5
K0 = (T0 - T5) // 5; KT = (T - T5) // 5
CARDS = os.path.join(HERE, 'EPI_OUTPUT_PROOFS_V1.tsv')
BURST = ['active_share', 'burst_move_pct', 'burst_s', 'burst_speed_pct_min', 'burst_speed_vs_normal', 'burst_vs_oi_bp', 'forced_share',
         'forced_usd_log', 'growth', 'hl_forced_usd_log', 'hl_lead_s', 'hl_other_usd_log', 'max_move_60s_pct', 'oi_chg_burst_pct', 'other_share',
         'other_usd_log', 'peak_s', 'pre_forced_usd_log', 'pre_move_pct', 'pre_speed_pct_min', 'size_vs_week', 'speed_ratio', 'top5s_share']


def nans(v):
    return sorted(k for k, x in v.items() if math.isnan(x))


def with_rows(lo, hi, value):
    a = list(TP.planted()); xf = a[5].copy(); xf[lo:hi] = value; a[5] = xf; return TP.ep_values(a)


class Values(unittest.TestCase):
    def test_hand_answers_both_sides(self):
        for side in (+1, -1):
            got, want = TP.ep_values(TP.planted(side)), TP.expected(side)
            self.assertEqual(sorted(got), sorted(want))
            self.assertEqual({k: (got[k], w) for k, w in want.items() if not TP.same(got[k], w)}, {})

    def test_known_at_the_alarm(self):
        a, b = TP.ep_values(TP.planted(+1)), TP.ep_values(TP.planted(+1, after=True))
        self.assertEqual({k: (v, b[k]) for k, v in a.items() if not TP.same(v, b[k], 0)}, {})


class Empty(unittest.TestCase):
    def test_no_print_in_the_onset_window(self):
        """no burst start: every burst value is EMPTY (never 0); onset, run, peaks and flushes stay valued"""
        v = with_rows(K0 - 11, K0 + 1, 0.0)
        self.assertEqual(nans(v), sorted(BURST))
        for k in ('onset_to_alarm_s', 'normal_move_pct', 'run_pct', 'giveback_pct', 'peak15_usd_log', 'peak60_usd_log', 'size_vs_bar', 'n_flushes'):
            self.assertFalse(math.isnan(v[k]), k)

    def test_silent_forcing(self):
        """no forced print from the onset window to the alarm: n_flushes EMPTY; the peaks are 0 (nothing seen), never EMPTY"""
        v = with_rows(K0 - 11, KT + 1, 0.0)
        self.assertEqual(nans(v), sorted(BURST + ['n_flushes'])); self.assertEqual((v['peak15_usd_log'], v['peak60_usd_log']), (0.0, 0.0))

    def test_short_burst(self):
        """a burst under 60 s: the speeds and the biggest 60 s move are EMPTY, burst_s is valued (55 s)"""
        a = list(TP.planted()); a[2] = T - 10; v = TP.ep_values(a)
        self.assertEqual(v['burst_s'], 55.0)
        for k in ('burst_speed_pct_min', 'burst_speed_vs_normal', 'max_move_60s_pct', 'speed_ratio'):
            self.assertTrue(math.isnan(v[k]), k)

    def test_hole_in_the_hour_before(self):
        v = with_rows(K0 - 5 - 100, K0 - 5 - 99, np.nan)
        self.assertEqual(nans(v), ['pre_forced_usd_log'])

    def test_flat_price(self):
        """a flat price: the run, its giveback and the normal move are 0; every ratio over them is EMPTY"""
        a = list(TP.planted()); a[8] = np.full(len(a[8]), 100.0); v = TP.ep_values(a)
        self.assertEqual((v['normal_move_pct'], v['run_pct'], v['giveback_pct']), (0.0, 0.0, 0.0))
        for k in ('run_norm', 'forced_share', 'giveback_share', 'speed_ratio', 'burst_speed_vs_normal', 'pre_speed_pct_min'):
            self.assertTrue(math.isnan(v[k]), k)

    def test_bar_unknown(self):
        """holes over the onset's 6 h look-back: the A01 bar is unknown, size_vs_bar EMPTY"""
        v = with_rows(max(0, K0 - 4300), K0 - 200, np.nan)
        self.assertTrue(math.isnan(v['size_vs_bar'])); self.assertFalse(math.isnan(v['peak60_usd_log']))


class Defects(unittest.TestCase):
    def test_epi_d1_a_price_gap_is_a_hole(self):                         # LAYERS 23 Oct (STRATEGY-153335): fixed, no longer expected to fail
        """EPI-D1: with no price bin from F - 24 h to F - 10 h, 56 of the 96 normal-move closes would be older than 60 s: fewer than 48
        known moves, so normal_move_pct must be EMPTY. Today the last close before the gap is carried and the normal move reads 0."""
        a = list(TP.planted()); te = a[7]; keep = (te < (T - 24 * 3600) * 1_000_000) | (te >= (T - 10 * 3600) * 1_000_000)
        a[7], a[8] = te[keep], a[8][keep]
        self.assertTrue(math.isnan(TP.ep_values(a)['normal_move_pct']))
        self.assertTrue(math.isnan(TP.twin_values(a)['normal_move_pct']))       # the twin carries the same rule

    def test_stale_price_both_sides(self):
        """STALE_PRICE at MAX_PRICE_AGE_S = 60 s: the alarm's close from a bin 55 s old is the price; 65 s old is NaN"""
        for age, stale in ((55, False), (65, True)):
            a = list(TP.planted()); te, px = a[7], a[8]; k = (te <= (T - age) * 1_000_000) | (te > T * 1_000_000)
            e = EB.Ep(*[x if j not in (7, 8) else (te[k] if j == 7 else px[k]) for j, x in enumerate(a[:13])], hl=a[13])
            self.assertEqual(math.isnan(e.close(T)), stale, age); self.assertEqual(math.isnan(e.closes([T])[0]), stale, age)


class Cards(unittest.TestCase):
    def test_every_card_has_its_test_and_a_catalog_row(self):
        rows = list(csv.DictReader((l for l in open(CARDS) if not l.startswith('#')), delimiter='\t'))
        names = [c[2] for c in EB.doc_columns()]; mod = sys.modules[__name__]
        self.assertEqual(sorted(r['value'] for r in rows), sorted(names)); self.assertEqual(len(rows), 36)
        for r in rows:
            for t in r['test'].split(','):
                cls, meth = t.strip().split('.'); self.assertTrue(hasattr(mod, cls) and hasattr(getattr(mod, cls), meth), t)
            for k in ('definition', 'known_at', 'empty_rule'):
                self.assertTrue(r[k].strip(), (r['value'], k))


if __name__ == '__main__':
    unittest.main()
