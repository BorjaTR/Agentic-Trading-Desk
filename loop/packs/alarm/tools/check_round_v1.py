#!/usr/bin/env python3
"""check_round_v1.py (SCOUT 2026-11-08; the owner 08:38Z "how are we making sure the agents in each part of the process are doing the
correct thing?"): the orchestrator runs it on a live run folder after each round; it flags a missing step while the run goes on.
Checks (from lean_v1/HUNTER_RULES_V2.md):
  R0  step 0 block in CLAIMS before the R1 line (pro-practice + stuck check + "without step 0 I would pick")
  per round k with a job in work/MAC_JOBS.tsv: a CLAIMS line "R<k> |" and a FORECASTS row R<k>, both timed before the round's first job
  R2  a power line (the words "gap needed" or "power") and, when the gap needed is over 10, a broad parent split
  R3  a placebo R3P CLAIMS line and FORECASTS row (from L09)
  C152: card lead15 cells equal their STEP_11 receipts (same variant); CARD.md equals the sha16 RESULT quotes; FORECASTS row(s) equal
  the sha16 each MAC_JOBS row quotes (C219: the round's own rows, as JOB_SHEET_V1 (b); old '(file X)' quotes: a start of the file)
  card (when CARD.md exists): NEXT TESTS, CAUSES block (from L10), held-out left "<filled by orchestrator>", no Feb/Mar 2026 number words
Prints one line per check: OK or MISSING <what>; exit 0 when nothing is missing, 3 otherwise.
  python3 -B check_round_v1.py <RUNF> [--run-number 9]"""
import argparse, csv, os, re, sys

def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument('runf'); ap.add_argument('--run-number', type=int, default=99)
    a = ap.parse_args(argv); W = os.path.join(a.runf, 'work'); miss = []; ok = []
    claims = open(os.path.join(W, 'CLAIMS.md')).read() if os.path.isfile(os.path.join(W, 'CLAIMS.md')) else ''
    def cl_utc(tag):
        m = re.search(r'^%s \| (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)' % re.escape(tag), claims, re.M); return m.group(1) if m else None
    fc = {}
    if os.path.isfile(os.path.join(W, 'FORECASTS.tsv')):
        for r in csv.DictReader(open(os.path.join(W, 'FORECASTS.tsv')), delimiter='\t'): fc.setdefault(r.get('round', ''), r.get('utc', ''))
    first_job = {}
    if os.path.isfile(os.path.join(W, 'MAC_JOBS.tsv')):
        for r in csv.DictReader(open(os.path.join(W, 'MAC_JOBS.tsv')), delimiter='\t'):
            m = re.search(r'\b(R\dP?)\b', r.get('round', ''))   # C75: labels like 'SPLIT R2 parent ...' (L10) count for R2
            if m: first_job.setdefault(m.group(1), r.get('utc', ''))
    # R0
    r0 = re.search(r'^## R0', claims, re.M); r1 = re.search(r'^R1 \|', claims, re.M)
    if r0 and (not r1 or r0.start() < r1.start()) and re.search(r'pro-practice|pro_practice', claims, re.I) and re.search(r'stuck', claims, re.I):
        ok.append('R0 step 0 block before R1')
    else: miss.append('R0 step 0 block (pro-practice + stuck check) before the R1 line')
    for rk, job_utc in sorted(first_job.items()):
        c, f = cl_utc(rk), fc.get(rk)
        if not c: miss.append('%s CLAIMS line' % rk)
        elif c > job_utc: miss.append('%s CLAIMS line %s is after its first job %s' % (rk, c, job_utc))
        else: ok.append('%s CLAIMS before job' % rk)
        if not f: miss.append('%s FORECASTS row' % rk)
        elif f > job_utc: miss.append('%s FORECASTS row %s is after its first job %s' % (rk, f, job_utc))
        else: ok.append('%s FORECASTS before job' % rk)
    # C131 (M070): a CLAIMS round line must not quote a receipt (by sha16) that was written after the line's own stamp
    import hashlib, glob, datetime as _dt
    rec = {}
    for f in glob.glob(os.path.join(a.runf, 'pipe*', 'STEP_*.json')) + glob.glob(os.path.join(a.runf, 'work', 'scripts', '*')):
        if os.path.isfile(f):
            rec[hashlib.sha256(open(f, 'rb').read()).hexdigest()[:16]] = (_dt.datetime.fromtimestamp(os.path.getmtime(f), _dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), f)
    late = []
    for m in re.finditer(r'^(R\dP?) \| (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)(.*)$', claims, re.M):
        for h in set(re.findall(r'\b[0-9a-f]{16}\b', m.group(3))):
            if h in rec and rec[h][0] > m.group(2): late.append('%s line %s quotes %s written %s' % (m.group(1), m.group(2), os.path.basename(rec[h][1]), rec[h][0]))
    if late: miss.extend('CLAIMS stamp before its receipt: ' + x for x in late)
    else: ok.append('CLAIMS stamps after the receipts they quote')
    r2 = re.search(r'^R2 \|.*$', claims, re.M)
    if r2:
        line = r2.group(0)
        if re.search(r'gap needed|power', line, re.I): ok.append('R2 power line')
        else: miss.append('R2 power line (gap needed for t 2.5)')
    if 'R3' in first_job and a.run_number >= 9:
        if cl_utc('R3P') or re.search(r'^R3P', claims, re.M): ok.append('R3P placebo claim')
        else: miss.append('R3P placebo claim (C35)')
        if 'R3P' not in fc: miss.append('R3P FORECASTS row')
    card = os.path.join(a.runf, 'CARD.md')
    if os.path.isfile(card):
        t = open(card).read()
        (ok if 'NEXT TESTS' in t else miss).append('card NEXT TESTS')
        if a.run_number >= 10: (ok if 'CAUSES' in t else miss).append('card CAUSES block (C41)')
        (ok if ('<filled by orchestrator>' in t or 'orchestrator only' in t) else miss).append('card held-out placeholder')   # C68 wording
        if re.search(r'lead_260[23]|\b2602\b|\b2603\b', t): miss.append('card names a held-out month column')
        # C66 (PR005; C2:OVERCLAIM in L07 1, L08 2, L09 3): cause sentences belong in the CAUSES block, each with a t
        incaus = False; nexts = False; out_c = []; no_t = []
        for i, ln in enumerate(t.splitlines(), 1):
            if ln.startswith('## '): incaus = 'CAUSES' in ln.upper(); nexts = 'NEXT' in ln.upper(); continue
            if incaus and ln.strip().startswith('-'):
                if not re.search(r'\bt=\s*[-+]?\d', ln) and 'QUESTION' not in ln: no_t.append(i)   # C83: a QUESTION anywhere on the line (L10 style)
            elif nexts: continue                                                                     # C83: test designs in NEXT TESTS are conditionals
            elif not incaus and re.search(r'\bbecause\b|(?<!80% )(?<!80 pct )(?<!forecast )(?<!interval )\bband\b|which waves|failed, not\b', ln, re.I) and not ln.lstrip().startswith(('|', 'Idea', '#')):   # the idea line states the hypothesis; tables have their own reason column
                out_c.append(i)
        if out_c: miss.append('card cause sentence outside the CAUSES block, lines %s' % out_c[:8])
        if no_t: miss.append('card CAUSES line without t= (and not a QUESTION), lines %s' % no_t[:8])
    # C152 (K2 packet: a planted card cell and edited files were found by assessors, not by this tool)
    import json as _json
    def h16(f): return hashlib.sha256(open(f, 'rb').read()).hexdigest()[:16]
    if os.path.isfile(card):
        pipes = {'R1': 'pipe_r1', 'R3': 'pipe_r3', 'R3P': 'pipe_r3p'}; bad_cells = []
        for ln in open(card).read().splitlines():
            c = [x.strip() for x in ln.split('|')]
            if len(c) > 5 and c[1] in pipes:
                g = os.path.join(a.runf, pipes[c[1]], 'STEP_11_GRADE.json'); m = re.search(r'[+-]?\d+(?:\.\d+)?', c[4])
                if not (m and os.path.isfile(g)): continue
                try:
                    d = _json.load(open(g)); r = next(x for x in d['numbers']['real'] if x.get('horizon') == '15m')
                except (ValueError, KeyError, StopIteration, TypeError): continue
                vs = re.findall(r'\bV(\d+)\b', c[3]); va = re.search(r'_V(\d+)$', d.get('alarm', ''))
                if not vs or not va or vs[-1] != va.group(1): continue          # a different variant: not compared
                if abs(float(m.group()) - float(r['lead'])) >= 0.006: bad_cells.append('%s %s vs STEP_11 %.2f' % (c[1], m.group(), float(r['lead'])))
        if bad_cells: miss.append('card lead15 differs from its receipt: ' + '; '.join(bad_cells))
        else: ok.append('card lead15 cells equal their receipts')
    res = sorted(glob.glob(os.path.join(W, 'RESULT_*.md')))
    if res and os.path.isfile(card):
        m = re.search(r'card sha16 ([0-9a-f]{16})', open(res[-1]).read())
        if m and m.group(1) != h16(card): miss.append('CARD.md is %s, RESULT quotes %s: the card changed after RESULT' % (h16(card), m.group(1)))
        elif m: ok.append('card sha16 equals the one RESULT quotes')
    fcf = os.path.join(W, 'FORECASTS.tsv'); mj = os.path.join(W, 'MAC_JOBS.tsv')
    if os.path.isfile(fcf) and os.path.isfile(mj):
        # C219 (L11 assessors): JOB_SHEET_V1 (b) quotes the sha16 of the round's OWN sealed row(s) (grep "^R<k><tab>" | shasum -a 256),
        # so each job is checked against its round's rows now; old '(file X)' quotes (L10) are whole-file hashes: each must be the hash of a
        # start of the file (rows only appended since), and the last quote of the run, when of that form, must equal the whole file (C152)
        fb = open(fcf, 'rb').read(); fl = fb.splitlines(True)
        def rows16(rk): return hashlib.sha256(b''.join(l if l.endswith(b'\n') else l + b'\n' for l in fl if l.startswith(rk.encode() + b'\t'))).hexdigest()[:16]
        starts = {hashlib.sha256(b''.join(fl[:i])).hexdigest()[:16] for i in range(len(fl) + 1)}
        q = []
        for ln in open(mj).read().splitlines():
            m = re.search(r'FORECASTS\.tsv[^\n]*?\b([0-9a-f]{16})\b', ln)
            if not m: continue
            r = re.search(r'FORECASTS\.tsv (R\dP?) rows?\b', ln)
            q.append((r.group(1) if r and '(file ' not in m.group(0) else None, m.group(1), ln.split('\t')[0]))
        bad_r, bad_f, n_r = [], [], 0
        for i, (rk, hx, u) in enumerate(q):
            if rk:
                n_r += 1
                if hx != rows16(rk): bad_r.append('FORECASTS %s row(s) are %s, the job at %s quotes %s: the row changed after the job' % (rk, rows16(rk), u, hx))
            elif i == len(q) - 1:
                if hx != h16(fcf): bad_f.append('FORECASTS.tsv is %s, the last job quotes %s: the file changed after its last job' % (h16(fcf), hx))
                else: ok.append('FORECASTS.tsv equals the sha16 the last job quotes')
            elif hx not in starts: bad_f.append('no start of FORECASTS.tsv hashes to %s (job at %s): a row changed after the job' % (hx, u))
        miss.extend(sorted(set(bad_r)) + sorted(set(bad_f)))
        if n_r and not bad_r: ok.append('FORECASTS row(s) equal the sha16 each of %d jobs quotes' % n_r)
    for o in ok: print('OK', o)
    for m in miss: print('MISSING', m)
    print('ROUND_CHECK %s ok %d missing %d' % ('PASS' if not miss else 'FLAG', len(ok), len(miss)))
    return 0 if not miss else 3

if __name__ == '__main__':
    sys.exit(main())
