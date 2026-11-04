"""test_prepared_activity_v2.py: the tests of prepared_activity_v2.py (planted, seconds). Owner OUTSIDE (COORD development DEV1,
b2_performance_v1). New edition by SCOUT for the clean release (30 Oct 2026). prepared_activity_v1.py (aba7ea04de649037) had no test file
(its checks are recorded runs: t2_prepared_activity_boundaries_v1, t2_prepared_activity_saved_parity_v1). It proves: (1) the reference is
<team>/RESEARCH/tools/alarm_match/draw_v3.py counted from the module's own file (the dev layout) and the module came from there; (2) on
planted prices the prepared fast path gives the reference's float bits at every call (audit mode compares each one, including NaN windows
and a gap), and an input it cannot prepare goes to the reference itself.
Run: cd <this folder> && python3 -B test_prepared_activity_v2.py"""
import math, struct, sys, unittest
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import prepared_activity_v2 as PA                                     # noqa: E402

S = {'pre_end_s': 60, 'pre_len_s': 600, 'min_closes': 10, 'gap_s': 30}


def bits(x):
    return 'nan' if math.isnan(x) else struct.pack('=d', x)


def planted(gap_at=None):
    ts = np.arange(0.0, 7200.0, 5.0)
    if gap_at is not None:
        ts = np.r_[ts[ts < gap_at], ts[ts >= gap_at + 120] ]                      # a 120 s hole
    px = 100.0 * np.exp(np.cumsum(np.sin(np.arange(len(ts)) * 0.37) * 1e-3))
    ts.flags.writeable = False; px.flags.writeable = False
    return ts, px


class Reference(unittest.TestCase):
    def test_reference_found_from_this_file(self):
        want = (HERE.parents[4] / 'RESEARCH' / 'tools' / 'alarm_match' / 'draw_v3.py').resolve()
        self.assertEqual(PA.REFERENCE_PATH, want)
        self.assertEqual(Path(PA.REFERENCE.__file__).resolve(), want)

    def test_fast_path_equals_reference_bits(self):
        for gap in (None, 3000.0):
            ts, px = planted(gap)
            P = PA.PreparedPreActivity(ts, px, audit=True)
            self.assertTrue(P.fast)
            got = [P.compute(ts, px, t, S) for t in (10.0, 700.0, 1234.5, 3100.0, 3700.0, 7100.0)]
            want = [PA.REFERENCE.pre_activity(ts, px, t, S) for t in (10.0, 700.0, 1234.5, 3100.0, 3700.0, 7100.0)]
            self.assertEqual([bits(x) for x in got], [bits(x) for x in want])
            self.assertTrue(any(math.isnan(x) for x in got) and any(not math.isnan(x) for x in got))
            self.assertEqual(P.checks, P.calls)

    def test_reference_follows_the_file_and_refuses_a_drifted_copy(self):
        """the module and the draw copied to another place in the same layout: the copy's own draw is read (sha256 checked): the same
        bytes import, one changed byte is REFUSED ACTIVITY_REFERENCE_DRIFT"""
        import shutil, subprocess, tempfile
        for drift, ok in ((False, True), (True, False)):
            root = Path(tempfile.mkdtemp()) / 'team'; mod = root / 'OUTSIDE' / 'COORD' / 'development' / 'DEV1' / 'b2_performance_v1'
            ref = root / 'RESEARCH' / 'tools' / 'alarm_match'; mod.mkdir(parents=True); ref.mkdir(parents=True)
            shutil.copy(PA.__file__, mod); data = Path(PA.REFERENCE_PATH).read_bytes()
            (ref / 'draw_v3.py').write_bytes(data + (b'# drift\n' if drift else b''))
            r = subprocess.run([sys.executable, '-B', '-c', 'import prepared_activity_v2 as P; print(P.REFERENCE_PATH)'], cwd=str(mod),
                               capture_output=True, text=True)
            self.assertEqual(r.returncode == 0, ok, r.stderr[-300:])
            if ok:
                self.assertEqual(r.stdout.strip(), str((ref / 'draw_v3.py').resolve()))
            else:
                self.assertIn('ACTIVITY_REFERENCE_DRIFT', r.stderr)

    def test_unprepared_input_goes_to_the_reference(self):
        ts, px = planted(); w = np.array(px)                                # a writeable copy: not the prepared arrays
        P = PA.PreparedPreActivity(ts, px)
        self.assertEqual(bits(P.compute(ts, w, 1234.5, S)), bits(PA.REFERENCE.pre_activity(ts, w, 1234.5, S)))


if __name__ == '__main__':
    unittest.main(verbosity=1)
