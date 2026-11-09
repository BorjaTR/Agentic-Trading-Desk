#!/usr/bin/env python3
# test_classify_line_v2.py (SCO-A151, SCOUT 2026-11-06): the new cases of classify_line_v2.py, written before the tool (red first on v1).
# Fault H2 of team/RESEARCH/GPT/receipts/V16_HELPER_REVIEW_20261106 (CHECKS da0f2a41194e80ab, classify_unknown_prefix_refuses): the
# verdict "VERDICT NEW SIDEWAYS: ..." printed novelty NEW rc 0. The words are novelty_v5 4ac3b0b1a0a46e9f's own (judge(), lines 242-266):
# COPY, NEW SIDE, MIRROR ("<W> of <name>: ..."), NEAR ("NEAR <name>: ..."), NEW ("NEW: ..."). Old cases: tests of classify_line_v1 on v2.
# Usage: python3 -B test_classify_line_v2.py [<tool path>] [<work dir>]; exit 0 when all pass.
import os, sys, subprocess, time
HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'classify_line_v2.py')
W = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'work', 'r_%s_%d' % (time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()), os.getpid()))
os.makedirs(W)
def run(*a):
    p = subprocess.run([sys.executable, '-B', TOOL] + list(a), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    return p.returncode, p.stdout
def wr(n, t):
    p = os.path.join(W, n)
    with open(p, 'w') as f: f.write(t)
    return p
DEC = 'DECISION SAMPLE V1: PASS | synthetic | test reason\n'
TR = 'id\tverdict\tidea\tV\nTSTROW\tTRUE\tSAMPLE\tV1\n'
HEAD = 'NOVELTY /x/V1_FIRES_V1_LIST.tsv (sha16 3d76823e297e0e0e), lean FADE: 10 fires\nnearest 1: A (OWN)\n'
N = [0]
def go(nov):
    N[0] += 1; t = str(N[0])
    return run('--idea', 'SAMPLE', '--v', 'V1', '--lean', 'FADE', '--claim-kind', 'SIZE', '--decide', wr('DEC%s.txt' % t, DEC), '--true-row', wr('TRUE%s.tsv' % t, TR),
               '--novelty', wr('NOV%s.txt' % t, nov), '--open', 'synthetic unresolved question')
CASES = []
def case(f): CASES.append(f); return f
@case
def c01_gpt_unknown_prefix_refused():
    rc, o = go('VERDICT NEW SIDEWAYS: generated unknown word\n')
    assert rc == 3 and o.startswith('REFUSED ') and 'CLASSIFY' not in o, (rc, o)
@case
def c02_every_novelty_v5_form_accepted():
    for line, w in (('VERDICT COPY of CLAUDE1_X_V1: 62.0 pct same fires with the same side', 'COPY'),
                    ('VERDICT NEW SIDE of DESK_T1 (+2 with the same fires and lean): 55.0 pct fires of a trigger with no side', 'NEW SIDE'),
                    ('VERDICT MIRROR of SEAT_IDEA_V2: 51.0 pct same fires with the other side', 'MIRROR'),
                    ('VERDICT NEAR SEAT_IDEA_V3: 45.0 pct (COPY)', 'NEAR'),
                    ('VERDICT NEAR SIDEWAYS: waves near 80.0 pct over its baseline 30.0 pct, excess 50.0 pts (40 or more)', 'NEAR'),
                    ('VERDICT NEW: every overlap under 40 pct and every excess under 40 pts', 'NEW'),
                    ('VERDICT NEW SIDE: v1 test form', 'NEW SIDE'), ('VERDICT COPY: v1 test form', 'COPY')):
        rc, o = go(HEAD + line + '\nBRIDGE END rc 0\n')
        assert rc == 0 and ('novelty %s (novelty_v5)' % w) in o, (line, rc, o)
@case
def c03_unknown_and_malformed_words_refused():
    for line in ('VERDICT NEW SIDE SIDEWAYS: x', 'VERDICT NEW of X: x', 'VERDICT COPYCAT: x', 'VERDICT NEARLY X: x', 'VERDICT new: x',
                 'VERDICT NEW', 'VERDICT NEW SIDE', 'VERDICT : x', 'VERDICT', 'VERDICT MIRRORED of X: x', 'VERDICT COPY of : x', 'VERDICT  NEW: x'):
        rc, o = go(HEAD + line + '\n')
        assert rc == 3 and o.startswith('REFUSED ') and 'CLASSIFY' not in o, (line, rc, o)
@case
def c04_known_plus_unknown_verdict_line_refused():
    rc, o = go(HEAD + 'VERDICT NEW: every overlap under 40 pct\nVERDICT SIDEWAYS: second line\n')
    assert rc == 3 and 'REFUSED NO_VERDICT' in o, (rc, o)
@case
def c05_verdict_not_at_line_start_is_not_a_verdict():
    rc, o = go(HEAD + 'BRIDGE: VERDICT NEW: quoted\nVERDICT MIRROR of A_B: 60.0 pct same fires with the other side\n')
    assert rc == 0 and 'novelty MIRROR (novelty_v5)' in o, (rc, o)
def main():
    ok = 0
    for f in CASES:
        try: f(); ok += 1; print('OK %s' % f.__name__)
        except Exception as e: print('FAIL %s: %r' % (f.__name__, e))
    print('TESTS %d of %d (tool %s)' % (ok, len(CASES), TOOL)); return 0 if ok == len(CASES) else 1
if __name__ == '__main__': sys.exit(main())
