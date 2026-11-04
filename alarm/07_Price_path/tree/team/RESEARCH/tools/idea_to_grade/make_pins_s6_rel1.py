"""make_pins_s6_rel1.py: Owner STRATEGY/LEAD (the grader thread). New edition by SCOUT for the clean release (K6, 31 Oct 2026; the owner 30 Oct 2026 23:07 Berlin: "All alarm tools should work from the
release folder only"). Old file: make_pins_s6.py ca4632c07a1c99cf,
never edited. Changed: the rel1 chain (idea_to_grade_v3_2_s6_rel1, release_pins_v3_2_rel1, idea_to_grade_rel1); the pins name paths
relative to the tree root. Writes I2G_PINS_V3_2_S6_REL1.json:  python3 -B make_pins_s6_rel1.py <new pins file>.
The rest of this text is make_pins_s6.py's.
make_pins_s6.py (speed twin S6, grader thread, 26 Oct 2026): release_pins_v3_2.py's pins file for idea_to_grade_v3_2_s6 (the S2 and S6 engines, the S3 and S6 drivers, i2g_rules_fast_v3, i2g_patch_s6_v1, V3.4 vectors and grade, i2g_rules_fast_v2, i2g_patch_s4_v1
and i2g_rules_fast_v1 added; release_pins_v3_2 is imported unchanged, its warm swapped). Never overwrites.
    python3 -B make_pins_s5.py <new pins file>"""
import os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.realpath(__file__)); sys.path.insert(0, HERE)
import idea_to_grade_v3_2_s6_rel1 as S6               # swaps warm and grade3
import release_pins_v3_2_rel1 as RP
import idea_to_grade_rel1 as I2

if __name__ == '__main__':
    path = sys.argv[1]
    RP.main(path)
    import json
    doc = json.load(open(path))
    need = [os.path.relpath(os.path.realpath(os.path.join(HERE, f)), I2.F) for f in ('i2g_engine_v3_2_s2_rel1.py', 'i2g_rules_fast_v1.py', 'idea_to_grade_v3_2_s2_rel1.py', 'idea_to_grade_v3_2_s3_rel1.py', 'idea_to_grade_v3_2_s6_rel1.py', 'i2g_engine_v3_2_s6_rel1.py', 'i2g_rules_fast_v2.py', 'i2g_rules_fast_v3.py', 'i2g_patch_s4_v1.py', 'i2g_patch_s6_rel1.py', '../i2g_v3_3/i2g_v3_4_vectors.py', '../i2g_v3_3/i2g_v3_4_grade.py')]
    print('S6 files pinned:', {os.path.basename(q): doc['pins'].get(q) for q in need})
