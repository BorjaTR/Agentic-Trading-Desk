# month_read_v3.py (CLAUDE1_20261028, 28 Oct 2026). TEST, NOT REVIEWED. v2 plus CODEX1 13:17Z: every decision number (races, gaps, other-side
# gaps, fires, waves) must be FINITE, else NO READ; a non-finite sealed range is refused. v2 header follows. v1 plus CODEX1's review (13:06Z): every required number (each
# pass-horizon gap AND each other-side gap) must be present, else NO READ (never HELD); and a LEGACY CARD warning: the kit card's population
# is not the parent-linked one, so verdicts are descriptive until reconciled. Original v1 header follows. A READER of finished grader outputs (CARD_<V>.txt and SUM_<V>.tsv):
# reads no lab data, so no date range of its own; it reads only the month it is asked for (a month the run has opened).
# For one variant and one month YYMM it prints, at each pass horizon: the lean race a / r / gap (from SUM, unrounded), the other side's
# gap for that month (from the CARD's month column of the opposite lean), and the month's fires and waves, then the verdict of the
# prereg scheme against a sealed range.
# Usage: python3 -B month_read_v1.py <W> <V> <YYMM> <LEAN FADE|FOLLOW> <H1,H2 e.g. 15m,1h> [LO1:HI1,LO2:HI2 (the sealed ranges)]
# Verdict (PREREG_MONTH_2601.md): NO READ if waves < 30; BROKE if a pass-horizon gap <= 0; WEAKER if a gap < 5 or the other side >= 5;
# STRONGER if every gap is above its sealed HI; else HELD.
import sys, re, os, math
def fin(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None
def sumkeys(p):
    k = {}
    for l in open(p):
        x = l.rstrip('\n').split('\t')
        if len(x) >= 2: k[x[0]] = x[1]
    return k
def card_month(p, lean, h, m):
    pat = re.compile(r'^\s+%s\s+2c<1c %s\s' % (lean, re.escape(h)))
    for l in open(p):
        if pat.match(l):
            parts = l.split('|')
            if len(parts) < 3: return None
            t = parts[1].split()
            for i in range(0, len(t) - 1, 2):
                if t[i] == m or t[i] == m[2:]:
                    return float(t[i + 1])
    return None
def main(a):
    if len(a) not in (5, 6): raise SystemExit('USAGE month_read_v1.py W V YYMM LEAN H1,H2 [LO:HI,LO:HI]')
    W, V, m, lean, hs = a[:5]; hs = hs.split(',')
    if not re.fullmatch(r'\d{4}', m): raise SystemExit('BAD MONTH ' + m)
    if lean not in ('FADE', 'FOLLOW'): raise SystemExit('BAD LEAN ' + lean)
    rng = [tuple(float(y) for y in x.split(':')) for x in a[5].split(',')] if len(a) == 6 else None
    if rng and any(not math.isfinite(y) for p in rng for y in p): raise SystemExit('BAD RANGE (non-finite) ' + a[5])
    if rng and len(rng) != len(hs): raise SystemExit('RANGES DO NOT MATCH HORIZONS')
    S = os.path.join(W, 'SUM_%s.tsv' % V); C = os.path.join(W, 'CARD_%s.txt' % V)
    k = sumkeys(S); other = 'FOLLOW' if lean == 'FADE' else 'FADE'
    fires, waves = k.get('fires %s' % m), k.get('waves %s' % m)
    print('%s month %s lean %s: fires %s waves %s' % (V, m, lean, fires, waves))
    gaps, oth = [], []
    for h in hs:
        av, rv = k.get('2c<1c %s a %s' % (h, m)), k.get('2c<1c %s r %s' % (h, m))
        fa, fr = fin(av), fin(rv)
        g = (fa - fr) if fa is not None and fr is not None else None
        o = fin(card_month(C, other, h, m)) if os.path.isfile(C) else None
        gaps.append(g); oth.append(o)
        print('  %-4s a %s r %s gap %s | other side gap %s' % (h, av, rv, 'na' if g is None else '%+.1f' % g, 'na' if o is None else '%+.1f' % o))
    if fin(waves) is None or fin(fires) is None or fin(waves) < 30: v = 'NO READ'
    elif any(g is None for g in gaps) or any(o is None for o in oth): v = 'NO READ'
    elif any(g <= 0 for g in gaps): v = 'BROKE'
    elif any(g < 5 for g in gaps) or any(o >= 5 for o in oth): v = 'WEAKER'
    elif rng and all(g > hi for g, (lo, hi) in zip(gaps, rng)): v = 'STRONGER'
    else: v = 'HELD'
    print('  VERDICT', v)
    print('  LEGACY CARD: kit card population (not parent-linked); descriptive until reconciled with an original-parent reader')
    return v
if __name__ == '__main__':
    main(sys.argv[1:])
