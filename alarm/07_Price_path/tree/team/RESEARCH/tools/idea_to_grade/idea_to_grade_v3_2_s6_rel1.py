"""idea_to_grade_v3_2_s6_rel1.py: Owner STRATEGY/LEAD (the grader thread). New edition by SCOUT for the clean release (K6, 31 Oct 2026; the owner 30 Oct 2026 23:07 Berlin: "All alarm tools should work from the
release folder only"). Old file: idea_to_grade_v3_2_s6.py 7f8d935faf1034f8, never edited. Changed: it imports the rel1 editions (V3.2, S3, the S6 engine and patch); --pins
names I2G_PINS_V3_2_S6_REL1.json (make_pins_s6_rel1.py; paths relative to the tree root); idea_to_grade_v3_2_rel1 says the new
data arguments (--lab-root, --gate, --research-root).
rel1 = release edition 1: the files of one chain that run from the Alarm release folder (code found relative to this file, in the
team/ layout of the dev tree; data from arguments); no value, rule, seal or output format changes.
The rest of this text is idea_to_grade_v3_2_s6.py's.
idea_to_grade_v3_2_s6.py (speed twin S6, grader thread, 26 Oct 2026, TEST): S3 (grade3 from V3.4's vector path) with the per-coin engine
i2g_engine_v3_2_s6 (written by make_engine_s6.py from the S5 engine: S5 plus the array setup of the walk, the day text memo and the sliced tough day window; S5 = the compiled exit walk, the calendar memo and STAMP-only ladder of
i2g_patch_s4_v1, the tough grid's part mask once per UTC day; each the same values bit for bit). coin_job is a module function of that
engine, so each spawned worker imports it and gets every change. Every other step and file is S3's.
Same command line as idea_to_grade_v3_2.py; --pins must name the S6 pins file (make_pins_s6.py)."""
import os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.realpath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import idea_to_grade_v3_2_rel1 as G
import idea_to_grade_v3_2_s3_rel1 as S3                                 # noqa: F401 (S2's warm and S3's grade3)

_warm_s3 = G.warm


def warm():
    _warm_s3()
    import i2g_engine_v3_2_s6_rel1, i2g_rules_fast_v2, i2g_rules_fast_v3, i2g_patch_s4_v1, i2g_patch_s6_rel1   # noqa: F401 (executed files are pinned)
    return i2g_engine_v3_2_s6_rel1


G.warm = warm

if __name__ == '__main__':
    G.main()
