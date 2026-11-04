"""test_compare_v2.py: test_compare.py run against compare_v2.py. Owner OUTSIDE (COORD development DEV1, opportunity_compare_v1). New
edition by SCOUT for the clean release (30 Oct 2026). Old file: test_compare.py 8ed11c901b606007, never edited; only the import changed
(compare_v2). The rest of this text is test_compare.py's.
Literal WP3 acceptance cases. Execute only inside COORD's reserved batch.

CODE1 source: OUTSIDE/CODE1/tests/opportunity_architecture_cases.json (bridge,
known nonreach, weighted inverse CDF). Three-parent reference: COORD 12:27Z
message. Five-parent unknown/unmatched reference: approved DEV2 unit oracle.
Expected numbers below are literal arithmetic references, never helper output.
"""
import unittest
from compare_v2 import summarize


class CompareLiterals(unittest.TestCase):
    def test_exact_equal_wave_parent_ninety_percent_boundary(self):
        # Four waves with sizes1,7,1,2; reached mass20/28, <=.1 mass18/28.
        # Exact conditional CDF(.1)=18/20=.9, hence inverse CDF(.9)=.1.
        ids = ['A','B','C','D','E','F','G','H','I','J','K']
        waves = dict(zip(ids, [0,1,1,1,1,1,1,1,2,3,3]))
        reach = [1,1,1,1,1,1,1,0,1,0,0]
        hb = [.1,0,.2,0,0,0,.2,None,0,None,None]
        s = summarize(ids,waves,reach,{'hb':hb},ids,
            ['c'+p for p in ids],[1]*11,[0]*11,{'hb':[None]*11})
        self.assertEqual(s['standalone']['conditional']['hb']['quantiles']['0.9'], .1)
        self.assertEqual(s['paired']['parent']['conditional']['hb']['quantiles']['0.9'], .1)

    def test_genuinely_below_boundary_does_not_use_epsilon(self):
        # Exactly representable binary input perturbation, well below1e-14.
        # The declared decimal first mass remains strictly below half total.
        s = summarize(['A'],{'A':0},[1],{'hb':[0]},
            ['A','A'],['x','y'],[.5-2**-48,.5+2**-48],[1,1],{'hb':[0,1]})
        self.assertEqual(s['paired']['control']['conditional']['hb']['quantiles']['0.5'], 1)

    def test_three_parents_two_waves(self):
        s = summarize(['A','B','C'], {'A':'W1','B':'W1','C':'W2'},
            [1,0,1], {'hb':[.2,None,.8]}, ['A','B','C'], ['x','y','z'],
            [1,1,1], [0,0,0], {'hb':[None,None,None]})
        self.assertEqual(s['paired']['parent_base_mass'], [.25,.25,.5])
        self.assertEqual(s['standalone']['reach_probability'], .75)
        self.assertEqual(s['paired']['reach_gap'], .75)
        self.assertEqual(s['paired']['waves'], 2)
        self.assertEqual(s['paired']['parent']['conditional']['hb']['quantiles']['0.5'], .8)
        self.assertEqual(s['paired']['control']['conditional']['hb']['status'], 'NO_REACH')

    def test_known_nonreach_is_not_unknown(self):
        s = summarize(['A'], {'A':'W'}, [1],
            {'hb':[.4], 'offer_s':[40], 'alarm_offer_s':[46]},
            ['A','A'], ['x','y'], [.9,.1], [0,1],
            {'hb':[None,.4], 'offer_s':[None,40], 'alarm_offer_s':[None,46]})
        c = s['paired']['control']
        self.assertAlmostEqual(c['reach_probability'], .1)
        for key, expected in [('hb',.4),('offer_s',40),('alarm_offer_s',46)]:
            p = c['conditional'][key]
            self.assertEqual(p['unknown_mass'], 0)
            self.assertAlmostEqual(p['not_applicable_mass'], .9)
            self.assertAlmostEqual(p['known_reached_mass'], .1)
            self.assertEqual(p['quantiles'], {'0.5':expected,'0.75':expected,'0.9':expected})
        self.assertEqual(s['status'], 'COMPLETED')

    def test_weighted_inverse_cdf(self):
        s = summarize(['A'], {'A':'W'}, [1], {'hb':[.3]},
            ['A','A'], ['x','y'], [.9,.1], [1,1], {'hb':[0,.8]})
        q = s['paired']['control']['conditional']['hb']['quantiles']
        self.assertEqual(q, {'0.5':0,'0.75':0,'0.9':0})
        self.assertEqual(s['paired']['conditional_quantile_differences']['hb']['0.75'], .3)

    def test_omitted_bridge_keeps_frozen_wave(self):
        # Full times 0,1200,2400 with gap1800 form one wave; middle outcome absent.
        s = summarize(['left','right'], {'left':0,'bridge':0,'right':0},
            [1,0], {'hb':[.2,None]}, ['left','right'], ['x','y'],
            [1,1], [0,0], {'hb':[None,None]})
        self.assertEqual(s['wave_population']['selected_wave_ids'], [0,0])
        self.assertEqual(s['wave_population']['frozen_parents'], 3)
        self.assertEqual(s['paired']['waves'], 1)
        self.assertEqual(s['paired']['parent_base_mass'], [.5,.5])
        self.assertIs(s['wave_population']['reclustered'], False)

    def test_unknown_edge_and_unmatched_parent(self):
        s = summarize(['P1','P2','P3','P4','P5'],
            {'P1':'W1','P2':'W2','P3':'W1','P4':'W2','P5':'W3'},
            [1,0,1,0,1], {'hb':[.2,None,.4,None,.6]},
            ['P1','P1','P2','P2','P3','P4'], ['a','b','c','d','e','f'],
            [.75,.25,.5,.5,1,1], [0,1,1,None,0,0],
            {'hb':[None,.2,.3,None,None,None]})
        self.assertEqual(s['paired']['parent_ids'], ['P1','P3','P4'])
        self.assertEqual(s['paired']['parent_base_mass'], [.25,.25,.5])
        self.assertEqual(s['paired']['reach_gap'], .4375)
        self.assertEqual(s['coverage']['unknown_eligible_edge_mass'], .5)
        self.assertEqual(s['coverage']['unmatched_parents'], 1)
        self.assertEqual(s['coverage']['control_incomplete_parents'], 1)
        self.assertIsNone(s['parents'][1]['control_reach'])
        self.assertEqual(s['parents'][1]['unknown_eligible_fraction'], .5)
        self.assertEqual(s['standalone']['rows'], 5)
        self.assertAlmostEqual(s['standalone']['reach_probability'], 2/3)
        self.assertEqual(s['status'], 'COMPLETED_WITH_SCOPE_GAPS')

    def test_missing_reached_heat_keeps_reach_pair(self):
        s = summarize(['A'], {'A':'W'}, [1], {'hb':[.2]},
            ['A','A'], ['x','y'], [.9,.1], [0,1], {'hb':[None,None]})
        c = s['paired']['control']['conditional']['hb']
        self.assertEqual(s['paired']['parents'], 1)
        self.assertAlmostEqual(s['paired']['reach_gap'], .9)
        self.assertAlmostEqual(c['unknown_mass'], .1)
        self.assertEqual(c['status'], 'PARTIAL_UNKNOWN')
        self.assertEqual(c['quantiles'], {'0.5':None,'0.75':None,'0.9':None})
        self.assertEqual(s['status'], 'COMPLETED_WITH_SCOPE_GAPS')

    def test_unknown_parent_retains_standalone_mass(self):
        s = summarize(['A','B'], {'A':0,'B':0}, [None,1], {'hb':[None,.2]},
            ['A','B'], ['x','y'], [1,1], [0,0], {'hb':[None,None]})
        self.assertEqual(s['standalone']['unknown_reach_mass'], .5)
        self.assertEqual(s['standalone']['reach_probability'], 1)
        self.assertEqual(s['standalone']['conditional']['hb']['unknown_mass'], .5)
        self.assertEqual(s['paired']['parent_ids'], ['B'])
        self.assertEqual(s['paired']['parent_base_mass'], [1])

    def test_duplicate_edge_refuses(self):
        with self.assertRaisesRegex(ValueError, 'DUPLICATE_ELIGIBLE_EDGE'):
            summarize(['A'], {'A':0}, [1], {'hb':[.2]},
                ['A','A'], ['x','x'], [.5,.5], [0,0], {'hb':[None,None]})

    def test_reused_control_is_disclosed(self):
        s = summarize(['A','B'], {'A':0,'B':1}, [1,0], {'hb':[.2,None]},
            ['A','B'], ['x','x'], [1,1], [0,0], {'hb':[None,None]})
        self.assertEqual(s['dependence']['reused_control_ids'], ['x'])
        self.assertEqual(s['dependence']['independence'], 'NOT_ESTABLISHED')
        self.assertEqual(s['paired']['scalar_uncertainty'], 'UNAVAILABLE_DEPENDENCE_NOT_ESTABLISHED')
        self.assertEqual(s['paired']['quantile_uncertainty'], 'NOT_ESTABLISHED')


if __name__ == '__main__':
    unittest.main(verbosity=2)
