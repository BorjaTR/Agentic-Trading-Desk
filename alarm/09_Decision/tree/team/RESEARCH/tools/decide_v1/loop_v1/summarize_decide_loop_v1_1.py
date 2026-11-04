"""summarize_decide_loop_v1_1.py (DECIDE seat, 26 Oct 2026 ~07:08Z, written before any outcome of the loop is read; = v1 with the raised bar of
DECIDE_LOOP_PREREG_V1_1_ADDENDUM_1.md: 22 tries, so one passing cell is UNSURE, best of 22): the last step of the
decision tool's outcome loop (DECIDE_LOOP_PREREG_V1_1.md). It reads nothing but the loop folder that run_decide_loop_v1_1.sh wrote:
  1. RUNS.txt must hold the release check, the 4 groups with their ask ids, 4 VERIFIED lines and DONE;
  2. every graded run is checked again with idea_to_grade_v3.verify_run(), and must be GRADED with its own ask id;
  3. the reader's verdict and cells (read/DECIDE_LOOP_VERDICT_V1.md, read/DECIDE_LOOP_CELLS_V1.tsv) give the ledger status of each ask by
     the rule below, fixed now, before any outcome is read (no reader judgement):
       TAKE and SKIPRULE: PASS when S1 passes in >= 11 of the 22 choosable cells, in >= 2 of the 3 entries and in at least one 1 h and
       one 4 h exit; UNSURE (best of 22) when it passes in 1-10 cells or misses that spread; FAIL when it passes nowhere;
       VALUED: the same bar on "taking every valued fire pays";
       BADDATA: UNSURE always (described only, no prediction).
  4. it prints the result; with --write it writes LOOP_RESULT_V1.md beside the runs (verdict, statuses, sha16s, the 4 ledger commands) and
appends the 4 RESULT rows (ledger_add_v6.py result <ask> <verdict file> <status> <settings>), once each.
  python3 -B summarize_decide_loop_v1_1.py <loop out folder> [--write]"""
import hashlib, json, os, subprocess, sys
HERE = os.path.dirname(os.path.realpath(__file__))
F = os.path.realpath(os.path.join(HERE, '..', '..', '..', '..', '..'))
T = os.path.join(F, 'team/RESEARCH/tools/idea_to_grade'); LEDGER = os.path.join(F, 'team/RESEARCH/tools/ledger/ledger_add_v6.py')
SET = os.path.join(HERE, 'DECIDE_LOOP_SETTINGS_V1.json'); RELEASE = '9c83cf0306d20410'
GROUPS = ('VALUED', 'TAKE', 'SKIPRULE', 'BADDATA')


def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def statuses(cells):
    """the fixed rule: cells = rows of DECIDE_LOOP_CELLS_V1.tsv as dicts -> {group: status}"""
    ch = [r for r in cells if r['choosable'] == 'True']
    if len(ch) != 22:
        raise SystemExit('REFUSED: %d choosable cells, the PREREG fixes 22' % len(ch))
    def bar(col):
        hit = [r for r in ch if r[col] == 'True']
        if not hit:
            return 'FAIL'
        spread = (len(hit) >= 11 and len({r['scheme'] for r in hit}) >= 2 and any(r['measure'].endswith('_1h') for r in hit)
                  and any(r['measure'].endswith('_4h') for r in hit))
        return 'PASS' if spread else 'UNSURE'
    s1 = bar('S1_ok')
    return {'VALUED': bar('pays_all'), 'TAKE': s1, 'SKIPRULE': s1, 'BADDATA': 'UNSURE'}


def spread(cells, col):
    hit = [r for r in cells if r['choosable'] == 'True' and r[col] == 'True']
    by = lambda k: ', '.join('%s %d' % (v, sum(r[k] == v for r in hit)) for v in sorted({r[k] for r in hit})) or 'none'
    return '%d of 22 cells; by entry: %s; by exit: %s' % (len(hit), by('scheme'), by('measure'))


def main(O, write):
    runs_txt = open(os.path.join(O, 'RUNS.txt')).read().splitlines()
    if not any(l.startswith('release %s checked' % RELEASE) for l in runs_txt) or not runs_txt[-1].startswith('DONE'):
        raise SystemExit('REFUSED: RUNS.txt has no release %s check or no DONE line' % RELEASE)
    ask = {}
    for l in runs_txt:
        w = l.split()
        if len(w) > 6 and w[0] in GROUPS and w[1] == 'events' and w[4] == 'ask':
            ask[w[0]] = w[5]
    if sorted(ask) != sorted(GROUPS) or len(set(ask.values())) != 4:
        raise SystemExit('REFUSED: RUNS.txt asks %s' % ask)
    sys.path.insert(0, T)
    import idea_to_grade_v3 as I
    for g in GROUPS:
        I.verify_run(os.path.join(O, g))
        b = json.load(open(os.path.join(O, g, 'RUN.json')))
        if b.get('run_class') != 'GRADED' or b['ledger']['ask_id'] != ask[g]:
            raise SystemExit('REFUSED: %s is %s with ask %s, RUNS.txt says %s' % (g, b.get('run_class'), b['ledger']['ask_id'], ask[g]))
        if not any(l.startswith('%s VERIFIED GRADED' % g) for l in runs_txt):
            raise SystemExit('REFUSED: RUNS.txt has no VERIFIED line for %s' % g)
    vp = os.path.join(O, 'read', 'DECIDE_LOOP_VERDICT_V1.md'); cp = os.path.join(O, 'read', 'DECIDE_LOOP_CELLS_V1.tsv')
    L = [l.rstrip('\n').split('\t') for l in open(cp)]
    cells = [dict(zip(L[0], r)) for r in L[1:]]; st = statuses(cells)
    verdict = [l for l in open(vp) if l.startswith('**Verdict.**')][0].strip()
    cmds = ['python3 -B %s result %s %s %s %s' % (LEDGER, ask[g], vp, st[g], SET) for g in GROUPS]
    md = ['# Decision tool V1 outcome loop, ALM_M_V1: result (summarize_decide_loop_v1_1.py, bar of DECIDE_LOOP_PREREG_V1_1_ADDENDUM_1.md)', '', verdict, '',
          'S1 passes in ' + spread(cells, 'S1_ok') + '.', 'Taking every valued fire pays in ' + spread(cells, 'pays_all') + '.',
          'Ledger status bar: PASS needs >= 11 of 22 cells, >= 2 entries, a 1 h and a 4 h exit; 1-10 cells is UNSURE (best of 22). On UNSURE the chosen cell is not adopted: entry and exit stay UNSET.', '',
          'Release graded: %s. Settings %s. Verdict file %s, cells %s.' % (RELEASE, sha16(SET), sha16(vp), sha16(cp)), '',
          '| group | ask | status (fixed rule) | run TABLE sha16 |', '|---|---|---|---|']
    md += ['| %s | %s | %s | %s |' % (g, ask[g], st[g], sha16(os.path.join(O, g, 'grade3', 'TABLE.tsv'))) for g in GROUPS]
    md += ['', 'Ledger RESULT rows:', '```'] + cmds + ['```', '', 'Every number is a row of an idea_to_grade V3.1 table (FADE, Sep-Dec 2025, taken vs skipped on 24 Sep - 31 Dec). It is not live parity.']
    print('\n'.join(md))
    if not write:
        print('(dry run: nothing written)'); return 0
    out = os.path.join(O, 'LOOP_RESULT_V1.md')
    if os.path.exists(out):
        raise SystemExit('REFUSED: %s exists' % out)
    open(out, 'w').write('\n'.join(md) + '\n')
    if write:
        for c in cmds:
            r = subprocess.run([sys.executable] + c.split()[1:], capture_output=True, text=True, timeout=60)
            print(c.split()[4], r.returncode, (r.stdout + r.stderr).strip()[-200:])
            if r.returncode:
                return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], '--write' in sys.argv[2:]))
