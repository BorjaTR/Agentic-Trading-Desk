#!/usr/bin/env python3
"""mutants_v1.py (SCO-A9, 5 Nov 2026): one mutant per rule of alarm_understand_v1.py (the brief's six: word rule, BLOCK_CLOSED,
SOURCE_CHANGED, wave rule, AFTER tag, ZERO_MOVE; five more: STOP code, forced side, concentration, single bucket, forced share). Each mutant is one
exact text change (it must occur exactly once) written as a copy under ../mutants/<stamp>/; the test it must fail is run on the copy
(AU_TOOL). KILLED = that test fails. The tool itself is never edited. Usage: python3 -B mutants_v1.py"""
import sys
sys.dont_write_bytecode = True
import datetime as dt, hashlib, os, subprocess

HERE = os.path.dirname(os.path.realpath(__file__))
TOOL = os.path.join(HERE, 'alarm_understand_v1.py')
TEST = os.path.join(HERE, 'test_alarm_understand_v1.py')
MUTANTS = (
    ('M1_word_rule', 'U7', "and abs(a['z']) >= zc)", "and abs(a['z']) >= 1.96)"),
    ('M2_block_closed', 'U1', "        if why:\n            raise Refused('BLOCK_CLOSED'", "        if False:\n            raise Refused('BLOCK_CLOSED'"),
    ('M3_source_changed', 'U1', "        if s != want:", "        if False:"),
    ('M4_wave_rule', 'U2', "U = R.RU.build_clusters(open_f) if open_f else []", "U = R.RU.build_clusters(open_f, gap_s=600) if open_f else []"),
    ('M5_after_tag', 'U8', "        after = k > t\n", "        after = k > t + 3600\n"),
    ('M6_zero_move', 'U6', "if (np.isfinite(mv) and mv > 0 and np.isfinite(BACK[h][i]))", "if (np.isfinite(mv) and mv >= 0 and np.isfinite(BACK[h][i]))"),
    ('M7_stop_code', 'U1', "        if f.startswith('STOP'):", "        if f.startswith('NEVER'):"),
    ('M8_forced_side', 'U5', "side = 'longs' if lg > sh else 'shorts' if sh > lg", "side = 'shorts' if lg > sh else 'longs' if sh > lg"),
    ('M9_concentration', 'U3', "t1 = R.GG.top_waves(x, w, c, 1)", "t1 = R.GG.top_waves(x, w, c, 2)"),
    ('M10_single_bucket', 'U4', "SB = np.array(['1' if s == 1 else", "SB = np.array(['1' if s <= 3 else"),
    ('M11_forced_share', 'U5', "FORCED_SHARE = 2.0 / 3.0", "FORCED_SHARE = 0.5"),
)


def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def main():
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out = os.path.join(os.path.dirname(HERE), 'mutants', stamp)
    os.makedirs(out)
    src = open(TOOL).read()
    print('date -u %s; tool %s sha16 %s; test sha16 %s' % (stamp, TOOL, sha16(TOOL), sha16(TEST)))
    base = subprocess.run([sys.executable, '-B', TEST], capture_output=True, text=True, timeout=300)
    print('BASELINE (unmutated) rc %d: %s' % (base.returncode, base.stdout.strip().splitlines()[-1]))
    killed = 0
    for name, test, old, new in MUTANTS:
        if src.count(old) != 1:
            print('%s NOT APPLIED: the text occurs %d times' % (name, src.count(old)))
            continue
        p = os.path.join(out, name + '.py')
        open(p, 'x').write(src.replace(old, new))
        env = dict(os.environ, AU_TOOL=p)
        r = subprocess.run([sys.executable, '-B', TEST, test], capture_output=True, text=True, timeout=300, env=env)
        fail = [l for l in r.stdout.splitlines() if l.startswith('FAIL')]
        ok = r.returncode != 0 and bool(fail)
        killed += ok
        print('%s %s by %s (sha16 %s): %s' % (name, 'KILLED' if ok else 'SURVIVED', test, sha16(p),
                                              (fail[0][:300] if fail else r.stdout.strip().splitlines()[-1][:200])))
    print('MUTANTS KILLED %d of %d' % (killed, len(MUTANTS)))
    return 0 if killed == len(MUTANTS) and base.returncode == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
