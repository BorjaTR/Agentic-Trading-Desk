#!/usr/bin/env python3
"""test_novelty_v3.py (SCOUT, 1 Nov 2026, ALARM_V1_16; why: team/RESEARCH/plans/PLAN_SCOUT_TOOLS_V1_16_20261101.md): planted fire lists
for novelty_v3's two changes (NEAR on excess, --show) and v2 equality where the excess rule does not fire. Pure functions only (judge,
show_line, line); the path contract stays test_registry_v2's. Reads tools/novelty_v3.py and tools/novelty_v2.py beside tests/, or the
folder given by NOVELTY_TOOLS. No data, no network, no files written.
  python3 -B test_novelty_v3.py"""
import importlib.util, os, random, sys, unittest

D = os.environ.get('NOVELTY_TOOLS') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools')


def load(name):
    spec = importlib.util.spec_from_file_location(name + '_t', os.path.join(D, name + '.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


V3 = load('novelty_v3')
V2 = load('novelty_v2')
T0 = 1757500000   # 2025-09-10


def row(aid, fires, lean='FADE', kind='ALARM', state='STOP'):
    return {'alarm_id': aid, 'seat': 'X', 'idea': aid, 'kind': kind, 'state': state, 'lean': lean, 'fires': sorted(fires)}


def spaced(n, step, start=T0, coin='BTC', side=1):
    return [(start + i * step, coin, side) for i in range(n)]


class Excess(unittest.TestCase):
    def test_sparse_sibling_near_by_excess(self):
        # sibling: one fire a day for 60 days (baseline about 2*1800/86400 = 4 pct); new list: a fire 600 s after each, other coin
        sib = spaced(60, 86400)
        new = [(t + 600, 'ETH', 1) for t, c, s in sib]
        v, basis, res = V3.judge(new, 'FADE', [row('SIB', sib)])
        self.assertEqual(v, 'NEAR')
        self.assertIn('excess', basis)
        self.assertAlmostEqual(res[0][2]['near'], 1.0)
        self.assertLess(res[0][2]['base'], 0.05)
        v2, _, _ = V2.judge(new, 'FADE', [row('SIB', sib)])
        self.assertEqual(v2, 'NEW')   # v2 missed it: the point of v3

    def test_dense_alarm_not_near(self):
        # dense: a fire every 1800 s (baseline 1.0): waves near 1.0 reads nothing
        dense = spaced(2000, 1800)
        new = [(T0 + 7 * 86400 + 900, 'ETH', 1)]
        v, basis, res = V3.judge(new, 'FADE', [row('DENSE', dense)])
        self.assertEqual(v, 'NEW')
        self.assertAlmostEqual(res[0][2]['base'], 1.0)
        self.assertIn('every excess under 40 pts', basis)

    def test_excess_boundary(self):
        m = {'near': 0.70, 'base': 0.30}
        self.assertAlmostEqual(V3.excess(m), 0.40)
        self.assertEqual(V3.EXCESS_AT, 0.40)

    def test_copy_still_first(self):
        sib = spaced(50, 86400)
        v, basis, _ = V3.judge(list(sib), 'FADE', [row('SIB', sib)])
        self.assertEqual(v, 'COPY')

    def test_line_is_v2_line_plus_excess(self):
        sib = spaced(60, 86400)
        new = [(t + 600, 'ETH', 1) for t, c, s in sib]
        _, _, res = V3.judge(new, 'FADE', [row('SIB', sib)])
        name, rep, m = res[0]
        l = V3.line('nearest 1', name, rep, m)
        v2 = ('nearest 1: %s (%s, %s, lean %s): same fires %s pct, same side %s pct, other side %s pct; waves near %s pct (its baseline %s pct)'
              % (name, rep.get('kind'), rep.get('state'), rep.get('lean'), V2.pct(m['same']), V2.pct(m['same_side']),
                 V2.pct(m['other_side']), V2.pct(m['near']), V2.pct(m['base'])))
        self.assertEqual(l, v2 + '; excess %s pts' % V2.pct(m['near'] - m['base']))


class Show(unittest.TestCase):
    def setUp(self):
        self.rows = [row('A1', spaced(40, 86400)), row('B2', spaced(40, 86400, start=T0 + 40000, coin='SOL')),
                     row('C3', spaced(40, 86400, start=T0 + 20000)), row('D4', spaced(40, 86400, start=T0 + 60000, coin='XRP'))]
        self.new = spaced(40, 86400, start=T0 + 30)
        _, _, self.res = V3.judge(self.new, 'FADE', self.rows)

    def test_show_any_rank(self):
        last = self.res[-1][0]
        l = V3.show_line(self.res, last)
        self.assertTrue(l.startswith('show: %s (' % last))

    def test_show_unknown_refused(self):
        with self.assertRaises(V3.Refused):
            V3.show_line(self.res, 'NOPE')

    def test_show_group_member_by_representative(self):
        rows = [row('P1', spaced(10, 86400), state='PASS'), row('P2', spaced(10, 86400))]   # same fires and lean: one group, named P1
        _, _, res = V3.judge(spaced(10, 86400, start=T0 + 5), 'FADE', rows)
        self.assertTrue(V3.show_line(res, 'P1').startswith('show: P1 (+1 with the same fires and lean)'))


class SameAsV2(unittest.TestCase):
    def test_random_lists_same_verdict_when_excess_low(self):
        rnd = random.Random(7)
        n_cmp = 0
        for k in range(150):
            regs = []
            for j in range(3):
                n = rnd.randint(5, 80)
                regs.append(row('R%d' % j, [(T0 + rnd.randint(0, 60 * 86400), rnd.choice('AB'), rnd.choice((1, -1))) for _ in range(n)],
                                lean=rnd.choice(('FADE', 'FOLLOW', '-'))))
            pool = [f for r in regs for f in r['fires']]
            new = sorted(set([rnd.choice(pool) for _ in range(rnd.randint(1, 40))] +
                             [(T0 + rnd.randint(0, 60 * 86400), 'C', 1) for _ in range(rnd.randint(0, 40))]))
            lean = rnd.choice(('FADE', 'FOLLOW', '-'))
            v3, b3, r3 = V3.judge(new, lean, regs)
            v2, b2, r2 = V2.judge(new, lean, regs)
            self.assertEqual([x[0] for x in r3], [x[0] for x in r2])
            self.assertEqual([x[2] for x in r3], [x[2] for x in r2])
            if max(V3.excess(x[2]) for x in r3) < V3.EXCESS_AT:
                n_cmp += 1
                self.assertEqual(v3, v2)
                if v2 != 'NEW':
                    self.assertEqual(b3, b2)
            elif v2 in ('COPY', 'NEW SIDE', 'MIRROR', 'NEAR'):
                self.assertEqual((v3, b3), (v2, b2))
            else:
                self.assertEqual(v3, 'NEAR')
        self.assertGreater(n_cmp, 30)


if __name__ == '__main__':
    unittest.main(verbosity=1)
