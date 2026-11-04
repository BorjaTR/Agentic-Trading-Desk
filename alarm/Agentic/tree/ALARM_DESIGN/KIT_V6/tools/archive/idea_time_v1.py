#!/usr/bin/env python3
"""idea_time_v1.py (SCOUT, KIT_V6, 29 Oct 2026; TEST, NOT REVIEWED). Where an agent's time went, from files only (never from what the
agent says): its board stamps, registers (RUNS, VARIANTS, DECISIONS), job receipts (STAGES.tsv) and claim files.
the owner 29 Oct 18:55 Berlin: "if they don't we need to log why and where they are wasting time".

  python3 -B KIT_V6/tools/idea_time_v1.py <RUN> [<RUN> ...] [--launch SEAT=YYYY-MM-DDTHH:MM:SSZ ...] [--now YYYY-MM-DDTHH:MM:SSZ]
  (run from team/RESEARCH/ALARM_DESIGN; on the Cowork VM or the Mac)

Per idea (minutes): claim to first job queued (card and hand check), job run times, the agent's lag from a job's end to the next step,
claim to first decision. Per seat: launch to first claim, the share of time with no job of its own running, with 2 running, the minutes
to the first PASS. A missing stamp prints '-'. Read-only: prints a table; writes nothing.
"""
import sys, os, csv, glob, datetime as dt

def _roots():
    if os.path.isdir('<LAB_REPO_ROOT>'):
        return '<DEV>'
    return os.path.expanduser('~/mnt/dev')

F = _roots() + '/TradingPlatform_repo/volat-agent/forensics'
H = F + '/team/RESEARCH/ALARM_DESIGN'
P = lambda s: dt.datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ') if s and len(s) == 20 else None


def rows(p):
    if not os.path.isfile(p):
        return []
    return list(csv.DictReader((l for l in open(p) if not l.startswith('#')), delimiter='\t'))


def mins(a, b):
    return '%.0f' % ((b - a).total_seconds() / 60.0) if a and b else '-'


def stages(run, rel):
    st = rows(os.path.join(run, rel or '', 'STAGES.tsv'))
    if not st:
        return None, None, None
    a = next((P(x.get('utc')) for x in st if x.get('stage') == 'start'), None) or P(st[0].get('utc'))
    e = next((P(x.get('utc')) for x in st if x.get('stage') == 'end'), None)
    ok = all(x.get('rc') == '0' for x in st if x.get('stage') not in ('stage',))
    return a, e, ok


def board(seat):
    out = []
    p = os.path.join(F, 'hb', seat + '.txt')
    if os.path.isfile(p):
        for l in open(p, errors='replace'):
            x = l.split(' ', 3)
            if len(x) >= 3 and P(x[0]):
                out.append((P(x[0]), x[2], x[3] if len(x) > 3 else ''))
    return out


def seat_report(tag, launch, now):
    run = os.path.join(H, 'runs', tag)
    seat = tag.split('_')[0]
    b = board(seat)
    start = next((t for t, k, _ in b if k == 'START'), None)
    t0 = launch or start
    done = next((t for t, k, _ in b if k == 'DONE'), None)
    end = done or now
    R = rows(os.path.join(run, 'registers', 'RUNS.tsv'))
    V = rows(os.path.join(run, 'registers', 'VARIANTS.tsv'))
    D = rows(os.path.join(run, 'registers', 'DECISIONS.tsv'))
    ideas = []
    for t, k, txt in b:
        if k == 'CLAIM':
            w = txt.split()
            name = w[0].rstrip(':,') if w else '?'
            if name not in [i for i, _ in ideas]:
                ideas.append((name, t))
    for r in R:
        i = r.get('idea')
        if r.get('kind') != 'CLEAN' and i and i not in [x for x, _ in ideas]:
            cf = os.path.join(H, 'runs', 'IDEAS_CLAIMED', '%s_%s.txt' % (tag, i))
            ideas.append((i, dt.datetime.utcfromtimestamp(os.path.getmtime(cf)).replace(microsecond=0) if os.path.isfile(cf) else None))
    print('== %s  launch %s  START %s  DONE %s' % (tag, t0, start, done))
    print('idea\tclaimed\tclaim_to_first_job\tcount_run\tgrade_queued_after_count_end\tgrade_run\tread_lag_after_grade\tentry_run\tdecided_after_entry_end\tclaim_to_first_decision\tstates')
    iv = []
    first_pass = None
    for i, tc in ideas:
        jobs = [r for r in R if r.get('idea') == i and r.get('kind') != 'CLEAN']
        cf = os.path.join(H, 'runs', 'IDEAS_CLAIMED', '%s_%s.txt' % (tag, i))
        if os.path.isfile(cf):
            m = dt.datetime.utcfromtimestamp(os.path.getmtime(cf)).replace(microsecond=0)
            tc = min(tc, m) if tc else m
        name = lambda r: os.path.basename((r.get('receipts_rel') or '').rstrip('/'))
        def first(kind, pred=lambda r: True):
            x = [r for r in jobs if r.get('kind') == kind and pred(r)]
            if not x:
                return None, None, None, None
            a, e, ok = stages(run, x[0].get('receipts_rel'))
            return P(x[0].get('utc_queued')), a, e, name(x[0])
        cq, ca, ce, _ = first('COUNT')
        gq, ga, ge, gj = first('GRADE')
        eq, ea, ee, ej = first('ENTRY', lambda r: r.get('from_job') == gj) if gj else (None, None, None, None)
        dg = sorted(P(d.get('utc')) for d in D if d.get('idea') == i and d.get('grade_job') == gj and P(d.get('utc')))
        de = sorted(P(d.get('utc')) for d in D if d.get('idea') == i and ej and d.get('entry_job') == ej and P(d.get('utc')))
        dec = sorted(P(d.get('utc')) for d in D if d.get('idea') == i and P(d.get('utc')))
        st = ','.join('%s %s' % (d.get('V'), d.get('state')) for d in D if d.get('idea') == i)
        for d in D:
            if d.get('idea') == i and d.get('state') == 'PASS' and P(d.get('utc')) and not i.startswith('GIVEN'):
                first_pass = min(first_pass or P(d['utc']), P(d['utc']))
        firstjob = min([x for x in (cq, gq) if x] or [None]) if (cq or gq) else None
        nxt = min([x for x in (eq, dg[0] if dg else None) if x] or [None]) if (eq or dg) else None
        print('\t'.join(str(x) for x in (i, tc.strftime('%H:%M:%SZ') if tc else '-', mins(tc, firstjob), mins(ca, ce), mins(ce, gq), mins(ga, ge),
                                          mins(ge, nxt), mins(ea, ee), mins(ee, de[0] if de else None), mins(tc, dec[0] if dec else None), st or '-')))
        for r in jobs:
            a, e, _ = stages(run, r.get('receipts_rel'))
            if a:
                iv.append((max(a, t0), min(e or end, end)))
    # time with 0, 1, 2+ of its own jobs running
    pts = sorted([(a, 1) for a, e in iv if e > a] + [(e, -1) for a, e in iv if e > a])
    cur, last, share = 0, t0, {0: 0.0, 1: 0.0, 2: 0.0}
    for t, d in pts:
        if t > last:
            share[min(cur, 2)] += (t - last).total_seconds()
            last = t
        cur += d
    if end > last:
        share[min(cur, 2)] += (end - last).total_seconds()
    tot = max((end - t0).total_seconds(), 1)
    fc = min([t for _, t in ideas if t] or [None]) if ideas else None
    print('seat %s: launch to first claim %s min; no job running %.0f pct, one %.0f pct, two or more %.0f pct of %s min; first own PASS after %s min'
          % (seat, mins(t0, fc), 100 * share[0] / tot, 100 * share[1] / tot, 100 * share[2] / tot, mins(t0, end), mins(t0, first_pass)))
    print()


def main(argv):
    tags, launch, now = [], {}, dt.datetime.utcnow().replace(microsecond=0)
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == '--launch':
            s, t = argv[i + 1].split('=', 1); launch[s] = P(t); i += 2; continue
        if a == '--now':
            now = P(argv[i + 1]); i += 2; continue
        tags.append(a); i += 1
    if not tags:
        print(__doc__); return 2
    for t in tags:
        seat_report(t, launch.get(t.split('_')[0]), now)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
