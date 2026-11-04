"""labcore.costs (BUILD2, 23 Oct 2026): ONE c (spec LEAD/LABCORE_STEP2_SPEC_V1.md b75998c5 sec 2; STRATEGY 12:08:08Z M2: label c = gate c =
exit c). cost_c MOVED verbatim from team/RESEARCH/tools/bucket_proof (load_cost; the same body in bucket_proof.py f6c5f994 and in its
oracle 2b615f53, the version step 1 moved): the cost table named in the settings (today COSTS_PER_COIN_V1) + gap_pct; a coin not in the
table takes the median and is counted. TEAM is the folder the settings' cost table path is relative to (as in bucket_proof)."""
import os
import numpy as np

HERE = os.path.dirname(os.path.realpath(__file__))
TEAM = os.path.realpath(os.path.join(HERE, '..', '..', '..'))


def load_cost(s, coins):
    """full cost c per fire in pct = coin HL cost of record (cost table) + the gap; a coin not in the table takes the median (counted)"""
    cost = {}
    for l in open(os.path.join(os.path.dirname(TEAM), s['cost']['table'])):
        if l.startswith('#') or l.startswith('coin\t'):
            continue
        f = l.rstrip('\n').split('\t'); cost[f[0]] = float(f[4]) / 100.0
    cmed = float(np.median(list(cost.values())))
    return np.array([cost.get(x, cmed) for x in coins]) + s['cost']['gap_pct'], int(sum(1 for x in coins if x not in cost))


cost_c = load_cost                                    # the spec's name; the body is bucket_proof's, line for line
