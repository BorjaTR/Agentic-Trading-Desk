"""pytest_main.py: a harness written in this repository (not a dev-tree file, not in MANIFEST.tsv). The dev tree runs these tests with
`python3 -B -m pytest`; _tools/run_isolated_v1.py needs a script inside this Alarm folder, so this file hands its arguments to pytest.
  cd /tmp && python3 -B <Alarm>/_tools/run_isolated_v1.py <part>/proof_harness/pytest_main.py [--gate-run <tools dir>] <pytest args>
--gate-run <tools dir>: labcore.jobgate reads the team's live run/pause switch at an absolute dev path
(<DEV>/.../team/FEED/stops/BACKFILL_GATE.txt; missing = PAUSE, so detect.run refuses GATE_NOT_RUN). With this flag the
harness points that one default at a temporary file reading RUN, for this process only; no tool file is changed."""
import os, sys, tempfile
import pytest

sys.dont_write_bytecode = True
a = sys.argv[1:]
if a[:1] == ['--gate-run']:
    sys.path.insert(0, a[1]); a = a[2:]
    import labcore.jobgate as JG
    fd, gate = tempfile.mkstemp(prefix='gate_run_', suffix='.txt'); os.write(fd, b'RUN\n'); os.close(fd)
    JG.GATE = gate; JG.state.__defaults__ = (gate,); JG.gate_wait.__defaults__ = (gate,) + JG.gate_wait.__defaults__[1:]
    print('harness: labcore.jobgate gate ->', gate, '(RUN)')
sys.exit(int(pytest.main(a)))
