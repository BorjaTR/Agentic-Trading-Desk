"""idea_to_grade_v3_2_s3_rel1.py: Owner STRATEGY/LEAD (the grader thread). New edition by SCOUT for the clean release (K6, 31 Oct 2026; the owner 30 Oct 2026 23:07 Berlin: "All alarm tools should work from the
release folder only"). Old file: idea_to_grade_v3_2_s3.py 544d4e00398ad27f, never edited. Changed: it imports idea_to_grade_v3_2_rel1 and idea_to_grade_v3_2_s2_rel1.
rel1 = release edition 1: the files of one chain that run from the Alarm release folder (code found relative to this file, in the
team/ layout of the dev tree; data from arguments); no value, rule, seal or output format changes.
The rest of this text is idea_to_grade_v3_2_s3.py's.
idea_to_grade_v3_2_s3.py (speed twin S3, grader thread, 26 Oct 2026, TEST): S2 (idea_to_grade_v3_2 with the one-pass exit walk engine
i2g_engine_v3_2_s2) plus the store's grade3 table from V3.4's vector path: i2g_v3_4_vectors.parent_vectors (Step A, once) and
i2g_v3_4_grade.grade_groups (Step B, one ALL group), in place of i2g_grade3_v3_2.grade. So grade3 is V3.2.1's table (the NO_COST RR fix;
the re-grade list asks for V3.2.1), equal to V3.2.1's own grade within 1e-12 x max(1, |b|) and, on M, text-equal to the corrected
oracle (V3.2's table with the 108 reviewed rows; V3.4.0 r01). Every other step and file is S2's.
Same command line as idea_to_grade_v3_2.py; --pins must name the S3 pins file (make_pins_s3.py)."""
import os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.realpath(__file__))
V34 = os.path.join(os.path.dirname(HERE), 'i2g_v3_3')              # V3.4's folder (team/RESEARCH/tools/i2g_v3_3)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
if V34 not in sys.path:
    sys.path.append(V34)                                            # after the idea_to_grade folder: its own files win
import numpy as np
import idea_to_grade_v3_2_rel1 as G
import idea_to_grade_v3_2_s2_rel1 as S2                                 # noqa: F401 (swaps G.warm for the S2 engine)
import i2g_grade3_v3_2 as G3V32
import i2g_v3_4_vectors as VA
import i2g_v3_4_grade as GB

_A = {}


def grade_v34(parents, names3, V3, row_coin, calm, calm_v2, tough, weights, clusters, legs_by_coin, slices=None):
    """i2g_grade3_v3_2.grade's arguments and result shape, from V3.4's Step A (once per run) and Step B (one group of every parent)"""
    k = (id(parents), id(V3), id(calm), id(calm_v2), id(tough), id(legs_by_coin))
    if k not in _A:
        _A.clear(); _A[k] = VA.parent_vectors(parents, names3, V3, row_coin, calm, calm_v2, tough, legs_by_coin)
    gid = np.zeros(len(parents), np.int64)
    return GB.grade_groups(_A[k], gid, 1, [p['day'] for p in parents], weights, clusters, slices)[0]


G3V32.grade = grade_v34

if __name__ == '__main__':
    G.main()
