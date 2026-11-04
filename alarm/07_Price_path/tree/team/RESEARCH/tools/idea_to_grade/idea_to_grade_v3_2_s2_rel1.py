"""idea_to_grade_v3_2_s2_rel1.py: Owner STRATEGY/LEAD (the grader thread). New edition by SCOUT for the clean release (K6, 31 Oct 2026; the owner 30 Oct 2026 23:07 Berlin: "All alarm tools should work from the
release folder only"). Old file: idea_to_grade_v3_2_s2.py d5c9ebdd3a1d7f0f, never edited. Changed: it imports idea_to_grade_v3_2_rel1 and i2g_engine_v3_2_s2_rel1.
rel1 = release edition 1: the files of one chain that run from the Alarm release folder (code found relative to this file, in the
team/ layout of the dev tree; data from arguments); no value, rule, seal or output format changes.
The rest of this text is idea_to_grade_v3_2_s2.py's.
idea_to_grade_v3_2_s2.py (speed twin S2, grader thread, 26 Oct 2026, TEST): idea_to_grade_v3_2 (signed, imported unchanged) with its
per-coin engine swapped for i2g_engine_v3_2_s2 (the one-pass exit walk; byte-equal by test_rules_fast_v1.py and by the store compare).
Same command line as idea_to_grade_v3_2.py; --pins must name the S2 pins file (make_pins_s2.py), as the run checks every executed file.
    nice -n 10 $PY -B idea_to_grade_v3_2_s2.py <idea_to_grade_v3_2 arguments> --pins I2G_PINS_V3_2_S2.json"""
import os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.realpath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import idea_to_grade_v3_2_rel1 as G


def warm():
    G.I2.warm()
    import i2g_engine_v3_2_s2_rel1, i2g_rules_fast_v1, i2g_grade3_v3_2      # noqa: F401 (executed files are pinned)
    return i2g_engine_v3_2_s2_rel1


G.warm = warm

if __name__ == '__main__':
    G.main()
