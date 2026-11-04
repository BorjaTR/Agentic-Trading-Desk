# mutants_alarm_profile_ed1_1.py: new edition by SCOUT for the clean release (30 Oct 2026; the owner 23:07 Berlin: "All alarm tools should work from the release
# folder only"). Owner QUANT. Old file: mutants_alarm_profile.py ea9216dcdabcf139, never edited. Changed: the mutants are planted in alarm_profile_ed1_1.py and judged by test_alarm_profile_ed1_1.py (the file names).
"""mutants for tools/alarm_profile (QUANT 22 Oct 2026): each plants one bug in a copy of the tool and runs test_alarm_profile.py; every
mutant must be KILLED (a test fails). A mutant that survives means a value could be wrong without any test seeing it.
  python3 -B mutants_alarm_profile.py [lab3 code dir]"""
import os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.realpath(__file__))
MUTANTS = [
    ('episode_blocks.py', 'one row after the alarm kept', "[lo:kt + 1].copy(); self.xo", "[lo:kt + 2].copy(); self.xo"),
    ('episode_blocks.py', 'one price bin after the alarm kept', "hi = int(np.searchsorted(te_us, self.t * 1_000_000, side='right'))",
     "hi = int(np.searchsorted(te_us, self.t * 1_000_000, side='right')) + 1"),
    ('episode_blocks.py', 'the burst starts at the LAST print of the onset window', "k1 = lo + int(hit[0])", "k1 = lo + int(hit[-1])"),
    ('episode_blocks.py', 'a new wave after 10 s of quiet', "HIGH, QUIET, QUIET_STEPS = 0.5, 0.10, 3", "HIGH, QUIET, QUIET_STEPS = 0.5, 0.10, 2"),
    ('episode_blocks.py', "the coin's normal day includes the burst's own day", "for d in (shift(b, -j) for j in range(1, WEEK_DAYS + 1))",
     "for d in (shift(b, -j) for j in range(0, WEEK_DAYS))"),
    ('episode_blocks.py', 'a carried open interest accepted', "and e.oi_c[ia] == 0:", ":"),
    ('episode_blocks.py', 'the Hyperliquid side read the wrong way', "usd[w & (sd == e.sgn)].sum())); out['hl_other_usd_log'] = lg(float(usd[w & (sd == -e.sgn)]",
     "usd[w & (sd == -e.sgn)].sum())); out['hl_other_usd_log'] = lg(float(usd[w & (sd == e.sgn)]"),
    ('episode_blocks.py', 'the giveback signed the wrong way', "out['giveback_pct'] = (ext - xt) * 100.0", "out['giveback_pct'] = (xt - ext) * 100.0"),
    ('episode_blocks.py', 'the run start without the flat-bottom tolerance', "i0, turned = run_start_index(xg, h, nm)",
     "i0, turned = run_start_index(xg, h, 0.0)"),
    ('episode_blocks.py', 'the normal move as a mean', "self._c['nm'] = float(np.median(m))", "self._c['nm'] = float(np.mean(m))"),
    ('episode_blocks.py', 'the hour before the burst one row too long', "w = e.xf[k1 - PRE_S // STEP:k1]", "w = e.xf[k1 - PRE_S // STEP - 1:k1]"),
    ('episode_blocks.py', 'the burst speed over the wrong minutes', "out['burst_speed_pct_min'] = (xt - xb) * 100.0 / (bs / 60.0)",
     "out['burst_speed_pct_min'] = (xt - xb) * 100.0 / (bs / 50.0)"),
    ('episode_blocks.py', 'the 60 s moves over 55 s', "np.log(e.closes(ends - 60))", "np.log(e.closes(ends - 55))"),
    ('episode_blocks.py', 'the bar read at the step after the onset', "bar = A01.bar_at(S60, e.k0)[0]", "bar = A01.bar_at(S60, e.k0 + 1)[0]"),
    ('episode_blocks.py', 'the open interest before the burst read one minute late', "ib = int(np.searchsorted(e.oi_t, tb, side='right')) - 1",
     "ib = int(np.searchsorted(e.oi_t, tb + 60, side='right')) - 1"),
    ('alarm_profile_ed1_1.py', 'the forced side swapped in the builder', "fz = 'short' if side > 0 else 'long'; ot = 'long' if side > 0 else 'short'",
     "fz = 'long' if side > 0 else 'short'; ot = 'short' if side > 0 else 'long'"),
    ('alarm_profile_ed1_1.py', 'a sealed day built', "        if sealed_read(day, table):\n            done[day] = 'REFUSED'", "        if False:\n            done[day] = 'REFUSED'"),
    ('alarm_profile_ed1_1.py', 'a sealed day read', "        if sealed(day, table):\n            raise PermissionError", "        if False:\n            raise PermissionError"),
    ('alarm_profile_ed1_1.py', 'rebuilt every time (never UP TO DATE)', "if old.get('seal') == seal and old.get('sources') == sources:", "if False:"),
    ('episode_twin.py', 'the twin counts the burst from the onset', "                k1 = k; tb = float(int(T5) + 5 * k - 5); break", "                k1 = k0; tb = float(int(T5) + 5 * k0 - 5); break"),
    ('episode_blocks.py', 'the run search to the alarm (v1), not to the run end', "h = max(H_MULT * nm, H_FLOOR); te = self.run_end()[0]",
     "h = max(H_MULT * nm, H_FLOOR); te = float(self.t)"),
    ('episode_blocks.py', 'the run end at the FIRST of equal extremes', "i = int(np.flatnonzero(ok & (xs == m))[-1])", "i = int(np.flatnonzero(ok & (xs == m))[0])"),
    ('episode_blocks.py', 'the run end measured from the onset, not the burst start', "w0 = tb if np.isfinite(tb) else float(self.t0 - 60)",
     "w0 = float(self.t0)"),
    ('episode_twin.py', 'the twin ends the run search at the alarm', "end = t if (not _fin(far) or (_fin(xt_) and xt_ >= far)) else far_t", "end = t"),
    ('episode_blocks.py', 'a pause of 60 min, not 30', "PAUSE_S = 1800 ", "PAUSE_S = 3600 "),
    ('episode_blocks.py', 'progress at any new high (no normal move of tolerance)', "        if v > ref + eps:", "        if v > ref:"),
    ('episode_blocks.py', 'the FIRST pause, not the last', "            if ts[i] - ts[iref] >= min_s:\n                last = (iref, i - 1)",
     "            if ts[i] - ts[iref] >= min_s and last is None:\n                last = (iref, i - 1)"),
    ('episode_blocks.py', "the start at the pause's FIRST low, not its last", "    return a + int(near[-1]), True", "    return a + int(near[0]), True"),
    ('episode_twin.py', 'the twin without the pause rule', "            paused = len(pauses) > 0", "            paused = False"),
]


def main(lab3):
    killed = 0
    for i, (f, what, old, new) in enumerate(MUTANTS, 1):
        with tempfile.TemporaryDirectory() as d:
            tools = os.path.join(d, 'tools'); dst = os.path.join(tools, 'alarm_profile')
            shutil.copytree(HERE, dst, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            for sib in ('alarms', 'alarm_context'):
                shutil.copytree(os.path.join(HERE, '..', sib), os.path.join(tools, sib), ignore=shutil.ignore_patterns('__pycache__'))
            p = os.path.join(dst, f); s = open(p).read()
            if s.count(old) != 1:
                print('MUTANT %2d %-55s NOT APPLIED (the text is there %d times)' % (i, what, s.count(old))); continue
            open(p, 'w').write(s.replace(old, new))
            r = subprocess.run([sys.executable, '-B', os.path.join(dst, 'test_alarm_profile_ed1_1.py')] + ([lab3] if lab3 else []),
                               capture_output=True, text=True, timeout=900)
            dead = r.returncode != 0; killed += dead
            print('MUTANT %2d %-55s %s' % (i, what, 'KILLED' if dead else 'SURVIVED'), flush=True)
    print('KILLED %d of %d' % (killed, len(MUTANTS)))
    return killed == len(MUTANTS)


if __name__ == '__main__':
    sys.exit(0 if main(sys.argv[1] if len(sys.argv) > 1 else '') else 1)
