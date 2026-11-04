"""kit5_tests_main.py: a harness written in this repository (H2, 30 Oct 2026; not a dev-tree file, not in MANIFEST.tsv; moved here from
04_Month_check when the kit moved to Alarm/Agentic, 30 Oct; it finds the kit from its own folder, so the code did not change). KIT_V5's tests/sim_env.py (line 5) holds REAL =
'<VM_UPLOADS>/uploads/dev/_scratch_scout/kit5_test': a folder on the machine where SCOUT ran the tests, holding the 5 files the sandbox
copies (reg_append_v1.py, read_stratentry_v1.py, DP2_CURVE.tsv, DP2_GATES.json, DP2_TABLE_W0.tsv). Without it every test errors in setUp.
This harness points sim_env.REAL at Agentic's tree/fixtures/kit5_test (the same bytes: MANIFEST.tsv, SOURCES.tsv), in this process only,
then runs tests/test_kit5_tools.py as __main__. No tool or test file is changed.
Each test leaves one k5sim_* folder in TMPDIR (59 a run, about 1 MB and 200 files each): set TMPDIR to a disk with room, run it once.
tests/mutants_v1.py is not run by this harness (it runs the whole suite once per mutant: 36 x 59 folders).
  cd /tmp && TMPDIR=<a folder with room> python3 -B -W ignore <Alarm>/_tools/run_isolated_v1.py <Alarm>/Agentic/proof_harness/kit5_tests_main.py
  or through the driver (a fresh TMPDIR per test, removed after): python3 -B <Alarm>/_tools/run_all_tests_v1.py <settings file> --part Agentic"""
import os, runpy, sys

sys.dont_write_bytecode = True
PART = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS = os.path.join(PART, 'tree', 'ALARM_DESIGN', 'KIT_V5', 'tests')
sys.path.insert(0, TESTS)
import sim_env  # noqa: E402

sim_env.REAL = os.path.join(PART, 'tree', 'fixtures', 'kit5_test')
print('harness: sim_env.REAL ->', sim_env.REAL, flush=True)
sys.argv = [os.path.join(TESTS, 'test_kit5_tools.py')] + sys.argv[1:]
runpy.run_path(sys.argv[0], run_name='__main__')
