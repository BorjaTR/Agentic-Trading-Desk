#!/usr/bin/env python3
"""classify_line_v2.py (SCO-A151 for SCOUT, 6 Nov 2026; PLAYGROUND, TEST, NOT REVIEWED; built test first, tests/test_classify_line_v2.py):
classify_line_v1.py b9939105c0ee9a72 plus one fix, fault H2 of team/RESEARCH/GPT/receipts/V16_HELPER_REVIEW_20261106 (REPORT
e479f0baf773abce): v1's novelty pattern backtracked from NEW SIDE to NEW, so "VERDICT NEW SIDEWAYS: ..." printed novelty NEW rc 0, and
it lacked novelty_v5's MIRROR. v2 takes every line that starts "VERDICT" (then a space, a colon or the line end) as a verdict line,
needs exactly one (NO_VERDICT), and reads its whole verdict field in novelty_v5 4ac3b0b1a0a46e9f's own forms (judge(), lines 242-266):
"COPY|NEW SIDE|MIRROR [of <name>]:", "NEAR [<name>]:" or "NEW:", where <name> is an alarm id with an optional
" (+<n> with the same fires and lean)"; any other word or form is refused BAD_WORD. Nothing else changed. v1's text follows.
classify_line_v1.py (SCO-A137 for SCOUT, 6 Nov 2026; PLAYGROUND, TEST, NOT REVIEWED; built test first, tests/test_classify_line_v1.py).
The CLASSIFY card line of ALARM_BUILD step 13 (gap GV15-06), copied from the kit's own receipts, never typed:
  python3 -B classify_line_v1.py --idea IDEA --v V --lean FADE|FOLLOW --claim-kind SIDE|SIZE --decide work/DECIDE_V1.txt
      --true-row RUN/receipts/<TRUE job>/TRUE_<V>_<LABEL>/TRUE_ROW.tsv --novelty work/RELWAIT_NOVELTY.txt --open "<what is still open>"
      [--firstlook RUN/receipts/<FIRSTLOOK job>/FIRST_LOOK.md] [--count RUN/receipts/<COUNT job>/COUNT_V1.tsv]
race: decide_v6's line "DECISION <IDEA> <V>: <word> | ... | <reason>" (word PASS, NEEDS MORE MONTHS, STOP, INSUFFICIENT or INVALID; the
reason is its last | field); TRUE: the one TRUE_ROW.tsv row of that idea and V (verdict TRUE, NOT SUPPORTED, UNSURE or REFUSED, with
its id); novelty: the one "VERDICT <word>:" line of the novelty_v5 output (COPY, NEAR, NEW SIDE or NEW); first look: the line
"# First look of <IDEA>_<V>: RULE_9 = <words>", else "not run"; --count adds COUNT's max_fires_in_a_wave by month (Q47, PROCESS step 13).
Prints one CLASSIFY line and one SOURCES line (each file with its sha16). Refusals: NO_FILE, NO_DECISION, BAD_WORD, TRUE_MISMATCH,
NO_VERDICT, FL_MISMATCH, BAD_COUNT. rc 0 printed, 3 refused, 2 usage. Writes nothing: the agent redirects stdout into its receipt."""
import hashlib, os, re, sys
RACE = ('PASS', 'NEEDS MORE MONTHS', 'STOP', 'INSUFFICIENT', 'INVALID')
TRUEW = ('TRUE', 'NOT SUPPORTED', 'UNSURE', 'REFUSED')
NAME = r'[^\s:()]+(?: \(\+[0-9]+ with the same fires and lean\))?'
NOVW = ('COPY', 'NEW SIDE', 'MIRROR', 'NEAR', 'NEW')   # novelty_v5 4ac3b0b1a0a46e9f judge()
NOVL = re.compile(r'^VERDICT(?=[ :]|$)')
NOV = re.compile(r'^VERDICT (?:(COPY|NEW SIDE|MIRROR)(?: of %s)?|(NEAR)(?: %s)?|(NEW)):(?: |$)' % (NAME, NAME))
USAGE = ('USAGE classify_line_v2.py --idea IDEA --v V --lean FADE|FOLLOW --claim-kind SIDE|SIZE --decide F --true-row F --novelty F '
         '--open TEXT [--firstlook F] [--count F]')
class Refused(Exception):
    def __init__(self, word, why): Exception.__init__(self, word); self.word, self.why = word, why
def text(p):
    if not os.path.isfile(p): raise Refused('NO_FILE', 'no file %s' % p)
    b = open(p, 'rb').read()
    return b.decode('utf-8', errors='replace'), hashlib.sha256(b).hexdigest()[:16]
def race(o):
    t, s = text(o['--decide']); pre = 'DECISION %s %s: ' % (o['--idea'], o['--v'])
    L = [l for l in t.split('\n') if l.startswith(pre)]
    if len(L) != 1: raise Refused('NO_DECISION', '%d lines start "%s" in %s, expected 1' % (len(L), pre.strip(), o['--decide']))
    parts = [x.strip() for x in L[0][len(pre):].split('|')]
    if parts[0] not in RACE: raise Refused('BAD_WORD', 'race word %r is not one of %s' % (parts[0], ', '.join(RACE)))
    return parts[0], parts[-1], s
def true(o):
    t, s = text(o['--true-row']); L = [l.split('\t') for l in t.split('\n') if l]
    if not L or not all(k in L[0] for k in ('id', 'verdict', 'idea', 'V')): raise Refused('TRUE_MISMATCH', '%s header lacks id, verdict, idea, V' % o['--true-row'])
    h = L[0]; R = [dict(zip(h, r)) for r in L[1:] if len(r) == len(h)]
    R = [r for r in R if r['idea'] == o['--idea'] and r['V'] == o['--v']]
    if len(R) != 1 or len(L) != 2: raise Refused('TRUE_MISMATCH', '%s holds %d rows, %d of %s %s; expected exactly one' % (o['--true-row'], len(L) - 1, len(R), o['--idea'], o['--v']))
    if R[0]['verdict'] not in TRUEW: raise Refused('BAD_WORD', 'TRUE verdict %r is not one of %s' % (R[0]['verdict'], ', '.join(TRUEW)))
    return R[0]['verdict'], R[0]['id'], s
def novelty(o):
    t, s = text(o['--novelty']); V = [l[:-1] if l.endswith('\r') else l for l in t.split('\n')]
    V = [l for l in V if NOVL.match(l)]
    if len(V) != 1: raise Refused('NO_VERDICT', '%d "VERDICT <word>" lines in %s, expected 1' % (len(V), o['--novelty']))
    m = NOV.match(V[0])
    if not m: raise Refused('BAD_WORD', 'novelty line %r is not one of novelty_v5\'s forms (%s)' % (V[0][:120], ', '.join(NOVW)))
    w = [g for g in m.groups() if g][0]
    if w not in NOVW: raise Refused('BAD_WORD', 'novelty word %r is not one of %s' % (w, ', '.join(NOVW)))
    return w, s
def firstlook(o):
    t, s = text(o['--firstlook']); pre = '# First look of %s_%s: RULE_9 = ' % (o['--idea'], o['--v'])
    L = [l for l in t.split('\n') if l.startswith(pre)]
    if len(L) != 1: raise Refused('FL_MISMATCH', '%d lines start "%s" in %s, expected 1' % (len(L), pre.strip(), o['--firstlook']))
    return L[0][len(pre):].strip(), s
def count(o):
    t, s = text(o['--count']); L = [l.split('\t') for l in t.split('\n') if l and not l.startswith('#')]
    if not L or 'month' not in L[0] or 'max_fires_in_a_wave' not in L[0]: raise Refused('BAD_COUNT', '%s has no month and max_fires_in_a_wave columns' % o['--count'])
    i, k = L[0].index('month'), L[0].index('max_fires_in_a_wave')
    pairs = ['%s %s' % (r[i], r[k]) for r in L[1:] if len(r) == len(L[0]) and re.fullmatch(r'[0-9]{4}', r[i])]
    if not pairs: raise Refused('BAD_COUNT', '%s has no month rows' % o['--count'])
    return ', '.join(pairs), s
NEED = ('--idea', '--v', '--lean', '--claim-kind', '--decide', '--true-row', '--novelty', '--open'); OPT = ('--firstlook', '--count')
def main(a):
    if len(a) % 2 or not a: print(USAGE); return 2
    o = dict(zip(a[0::2], a[1::2]))
    if len(o) * 2 != len(a) or any(k not in o for k in NEED) or any(k not in NEED + OPT for k in o) or o['--lean'] not in ('FADE', 'FOLLOW') or o['--claim-kind'] not in ('SIDE', 'SIZE') or '\n' in o['--open']:
        print(USAGE); return 2
    try:
        rw, why, rs = race(o); tw, tid, ts = true(o); nw, ns = novelty(o)
        fl, fs = firstlook(o) if '--firstlook' in o else (None, None)
        cn, cs = count(o) if '--count' in o else (None, None)
    except Refused as e:
        print('REFUSED %s: %s' % (e.word, e.why)); return 3
    line = 'CLASSIFY %s %s %s: race %s (decide_v6: %s) | TRUE %s (%s, true_gate_v3) | novelty %s (novelty_v5) | first look %s | claim %s (%s)' % (
        o['--idea'], o['--v'], o['--lean'], rw, why, tw, tid, nw, ('%s (first_look RULE_9)' % fl) if fl else 'not run', o['--claim-kind'], o['--lean'])
    if cn: line += ' | COUNT max_fires_in_a_wave by month: %s' % cn
    line += ' | open: %s' % o['--open']
    print(line)
    src = ['decide %s %s' % (o['--decide'], rs), 'true_row %s %s' % (o['--true-row'], ts), 'novelty %s %s' % (o['--novelty'], ns)]
    if fl: src.append('firstlook %s %s' % (o['--firstlook'], fs))
    if cn: src.append('count %s %s' % (o['--count'], cs))
    print('SOURCES ' + ' | '.join(src)); return 0
if __name__ == '__main__': sys.exit(main(sys.argv[1:]))
