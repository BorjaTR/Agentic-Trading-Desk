#!/usr/bin/env python3
"""alarm_pipeline_v1_4.py (SCO-A179, SCOUT, 7 Nov 2026; the owner 7 Nov 08:54 Berlin "yes", 09:13 "I allow the months"): alarm_pipeline_v1_3
with the data windows of ALARM_V1_22_0 in step 01 INPUT, nothing else:
  block SEPMAR = 20250910..20260331 (months 2509-2603), graded: the kit's GRADE (JOB_GRADE_V15) is the Sep-Mar grade, so steps 11 GRADE,
  13 TRUE (JOB_TRUE_V2, true_gate_v4), 15 FIRSTLOOK (months to 20260331) and 17 CARD read the Sep-Mar grade; SEPDEC stays a graded block
  (its months are read from the same Sep-Mar GRADE by month); JANMAR stays not graded (hc_defs_v4 reads 20250910..20251231 only: use SEPMAR);
  a window month in 2026-08..2026-11 is STOP NEVER_SEEN (refused by name, the owner opens once), in 2026-04..2026-07 STOP OUT_OF_SAMPLE (the
  holdout route only: holdout_month, one look per alarm), both before WINDOW_CLOSED; hc first..last must also lie in 20250910..20251231
  (STOP HC_OUTSIDE_TOOL: the range hc_defs_v4_to20251231 reads).
  Every step reads the INPUT's variant v (steps 06, 11, 19 named V1's files COUNT_V1, REAL_V1, CARD_V1: a control V2 and a revision V3
  stopped STOP 06 COUNT NO_OUTPUT, learning series run 7, jobs 20270544 and 20270546; coordinator to SCO-A179).
alarm_pipeline_v1_3.py (SCO-A162R, SCOUT, 6 Nov 2026 23:xxZ; the owner 22:53 Berlin "The pipeline has to work for any date and any alarm"):
alarm_pipeline_v1_1 with only the window made true (the E2E matrix found the window was checked against the open months and then not
used: step 11 GRADE always grades the kit's block, 10 Sep to 31 Dec 2025, chain *_to20251231, whatever the window said):
  step 01 INPUT: the block names the graded days (SEPDEC = 20250910..20251231, GRADE kind; JANMAR = 20260101..20260331); every window
  month must be a month of the block (else STOP WINDOW_OUTSIDE_BLOCK: one run reads one block); the window must hold at least one graded
  day (else STOP WINDOW_NOT_GRADED); hc first..last must lie inside the window (else STOP HC_OUTSIDE_WINDOW); JANMAR stops BLOCK_NOT_GRADED
  (the pack grades Jan-Mar only by a MONTH job on a frozen rule, START_V23 "Sep-Dec 2025 only, unless the brief names Jan-Apr 2026 with
  a frozen rule"; this pipeline files GRADE, and GRADE and hc_defs_v4 read Sep-Dec only). STEP_01 numbers: block, graded_days,
  window_graded (window cut to the graded days), window_months.
  step 08 SEAL_MENU: the gate's refusal (rc 2, REFUSED MENU_...) is STOP MENU_REFUSED with the gate's own line (v1_1 said TOOL_RC
  "menu rc 2" and hid the reason; matrix case F01 WINDFALL, job 20270411).
  replay: a kit refusal ALREADY of a kind the input's replay_jobs does not name (FIRSTLOOK) adopts the run's one earlier receipts folder of
  that kind (replay_old); none or two: the refusal stands (DRY_REFUSED).
  step 15 FIRSTLOOK rule: R1 counts when decide_v6 prints 'R1 PASS' (v1_1 tested 'yes', the planted word; real R1 passes never looked:
  matrix PERPHOUR and WICKBACK, NEEDS MORE MONTHS with R1 PASS, job 20270411).
  step 11 GRADE: numbers window_read, per horizon the GRADE's own by-month numbers (lead_YYMM, waves_YYMM, counted_YYMM) of the window's
  months, copied, never recomputed; window_grain 'month' (the GRADE reads by month; a window shorter than its months is read at month
  grain, said in window_note). DECIDE still reads the whole block (the race counts months of the block). Nothing else changed.
alarm_pipeline_v1_1.py (SCO-A162, SCOUT, 6 Nov 2026 22:5xZ; the owner 22:52 Berlin "We need tools that work"): alarm_pipeline_v1 with step 20
LOG_TRIED fitted to the released add_row (ADD_ROW_V1): thought_file is the sealed card's path (run folder + card), fail_layer named from the
verdict (WORKED NONE, NOT_MEASURABLE and INVALID_TEST MEASURE, else PREMISE), failed_stage 'none' for WORKED, closest_existing the step 16 nearest line, the 16 learning
columns 'unknown' or 'none' (drill K STOP_20: add_row refused the v1 row, missing columns); and step 21 LOG_LEDGER runs
before step 20 (ORDER): the TRIED row names the ledger result row, which add_row checks is in the ledger. Nothing else changed.
alarm_pipeline_v1.py (SCO-A153 for SCOUT, 6 Nov 2026; PLAYGROUND, TEST, NOT REVIEWED; built test first, tests/test_pipeline_v1.py).
ALARM_BUILD V18: the tools run the whole alarm design process from ONE agent-written input; agents only analyze.
  python3 -B alarm_pipeline_v1.py init <run folder> --input INPUT.json --settings PIPE_SETTINGS.json
  python3 -B alarm_pipeline_v1.py next <run folder>      one move: check the pending job, finish it, or start the next step
  python3 -B alarm_pipeline_v1.py run <run folder>       next until DONE, a WAIT or a STOP, inside a 45 s budget (each call < 60 s)
  python3 -B alarm_pipeline_v1.py status <run folder>    the step table
  python3 -B alarm_pipeline_v1.py retry <run folder>     moves the STOP file aside (never deleted) so the stopped step runs again
Each step writes STEP_<nn>_<NAME>.json: step, name, kind, job id and exit (job steps), the command, output paths with sha16, and the
numbers the analysis needs, copied from the tool's own output (never typed). A job step files its job (the kit's own commands: bridge
mac_desk_v48 rel and kitq with the typed INTENT ledger, ops_jobs_v1 nextop/relq/add/done), writes PENDING_<nn>.json, and returns
WAIT; the next call reads <runner>/<Q>/logs/<job>.status (exit=): absent -> WAIT, exit not 0 -> STOP, exit 0 -> opdone (bridge) and the
output is parsed. A cut between filing and PENDING is resumed from the filing's own output file (FILING_<nn>.json + logs/S<nn>_file.out).
Steps (V18 PROCESS; the agent's steps are QUESTIONS, CLAIM, RUN, ANALYZE, CARD REVIEW, PROPOSE):
 01 INPUT 02 COPY_SEARCH 03 COPY_SEARCH_DEF 04 HC_FIRES 05 NOVELTY_HC 06 COUNT 07 SEAL_TG 08 SEAL_MENU 09 SEAL_VARIANTS 10 SEAL_PREREG
 11 GRADE 12 TRUE_FILL 13 TRUE 14 DECIDE 15 FIRSTLOOK (only when the rule fires) 16 NOVELTY 17 CARD (runner job: alarm_understand
 bundle --from-job GRADE, mech_cards_run_v1 one-alarm config, mechanism_v1) 18 MECHANISM 19 CLASSIFY 20 LOG_TRIED 21 LOG_LEDGER
 22 HANDOFF (card_v1: ALARM_CARD_<ALARM>.md/.tsv, ALARM_CARDS/<MECHANISM>/<ALARM>/, HANDOFF.json, INDEX.tsv row).
registry_mode 'write' appends the registry rows (VARIANTS, prereg, DECISIONS --write, TRIED, ledger result); 'replay' (an alarm already
graded, re-run to compare) reads the existing rows back and STOPs when they are missing or differ: a replay never adds a try.
REPLAY ADOPT (added 2026-11-06 after the kit refused the proof's GRADE dry: queue_job_v16 "REFUSED: ALREADY GRADED ['V1']: never re-run;
a change is a new variant"): in replay mode only, when a kitq --dry is refused with the word ALREADY and the input's replay_jobs names
that kind's earlier job number, the step adopts that job (its status file exit= and its receipts, parsed as a new job would be; no op,
no opdone: the op was never ours) and records adopted=yes. The kit's refusal is never bypassed: nothing is filed.
Refusals: STOP <nn> <NAME> <CODE>: <why>; rc 0 DONE, 10 WAIT, 3 STOP, 2 usage. No rm, no git; nothing outside the run folder is
written except by the kit tools themselves and step 22 (twin of INDEX.tsv first)."""
import sys
sys.dont_write_bytecode = True
import hashlib, json, os, re, shutil, subprocess, time

HERE = os.path.dirname(os.path.realpath(__file__))
STEPS = [(1, 'INPUT', 'own'), (2, 'COPY_SEARCH', 'own'), (3, 'COPY_SEARCH_DEF', 'own'), (4, 'HC_FIRES', 'rel'), (5, 'NOVELTY_HC', 'rel'),
         (6, 'COUNT', 'kitq'), (7, 'SEAL_TG', 'rel'), (8, 'SEAL_MENU', 'own'), (9, 'SEAL_VARIANTS', 'own'), (10, 'SEAL_PREREG', 'rel'),
         (11, 'GRADE', 'kitq'), (12, 'TRUE_FILL', 'own'), (13, 'TRUE', 'kitq'), (14, 'DECIDE', 'own'), (15, 'FIRSTLOOK', 'kitq'),
         (16, 'NOVELTY', 'rel'), (17, 'CARD', 'job'), (18, 'MECHANISM', 'own'), (19, 'CLASSIFY', 'own'), (20, 'LOG_TRIED', 'own'),
         (21, 'LOG_LEDGER', 'rel'), (22, 'HANDOFF', 'own')]
# v1_1: the order the steps RUN in: 21 LOG_LEDGER before 20 LOG_TRIED, because the TRIED row names the ledger's result row
# (PREREG_<..>_R) and the released add_row refuses a ledger_row the ledger does not hold yet (E2E and drill K STOP_20). Numbers and
# names stay; 21 reads nothing of 20.
ORDER = [s for s in STEPS if s[0] < 20] + [s for s in STEPS if s[0] == 21] + [s for s in STEPS if s[0] == 20] + [s for s in STEPS if s[0] == 22]
REPLAY_SKIP_FILE = {10, 21}          # replay: these read the ledger back instead of filing
INPUT_KEYS = ('task', 'seat', 'run', 'idea', 'v', 'lean', 'claim_kind', 'def', 'def_sha16', 'card', 'card_sha16', 'claim', 'label',
              'window', 'block', 'words', 'hc', 'mechanism_hypothesis', 'registry_mode', 'open')
OPEN_MONTHS = ('202509', '202510', '202511', '202512', '202601', '202602', '202603')   # Sep 2025 to Mar 2026 only
BUDGET_S = 45.0
BLOCKS = {   # v1_4: the kit's grading blocks (ALARM_V1_22_0: GRADE = JOB_GRADE_V15, the MONTH chain stopped at 20260331)
    'SEPMAR': dict(first='20250910', last='20260331', months=('202509', '202510', '202511', '202512', '202601', '202602', '202603'), graded=True, why=''),
    'SEPDEC': dict(first='20250910', last='20251231', months=('202509', '202510', '202511', '202512'), graded=True, why=''),
    'JANMAR': dict(first='20260101', last='20260331', months=('202601', '202602', '202603'), graded=False,
                   why='hc_defs_v4 reads 20250910..20251231 only, so a Jan-Mar window cannot hold the hand check: use block SEPMAR '
                       '(the GRADE of ALARM_V1_22_0 grades 20250910..20260331 and is read by month)')}
NEVER_SEEN_MONTHS = ('202608', '202609', '202610', '202611')        # v1_4: lab3/law.py 0802358832de2b23 NEVER_SEEN, refused by name
OUT_OF_SAMPLE_MONTHS = ('202604', '202605', '202606', '202607')     # v1_4: the holdout, one look per alarm through holdout_month only
HC_TOOL_FIRST, HC_TOOL_LAST = '20250910', '20251231'                # v1_4: hc_defs_v4_to20251231's own range


def window_read(real, months):
    """v1_3: the GRADE's own by-month numbers of the window's months, per horizon, copied (REAL_V1 columns lead_YYMM, waves_YYMM, counted_YYMM)"""
    R = []
    for r in real:
        x = dict(horizon=r.get('horizon', ''))
        for m in months:
            k = m[2:]
            for c in ('lead', 'waves', 'counted'):
                if '%s_%s' % (c, k) in r:
                    x['%s_%s' % (c, k)] = r['%s_%s' % (c, k)]
        R.append(x)
    return R


class Stop(Exception):
    def __init__(self, code, why):
        Exception.__init__(self, code); self.code, self.why = code, why


class Wait(Exception):
    def __init__(self, why):
        Exception.__init__(self, why); self.why = why


def sha16(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()[:16]


def utc():
    return subprocess.run(['date', '-u', '+%Y-%m-%dT%H:%M:%SZ'], stdout=subprocess.PIPE, universal_newlines=True, check=True).stdout.strip()


def stamp():
    return utc().replace('-', '').replace(':', '')


def jload(p):
    with open(p) as f:
        return json.load(f)


def jwrite(p, obj):
    tmp = p + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(obj, f, indent=1, sort_keys=True); f.write('\n')
    os.replace(tmp, p)


def outs(paths):
    """{path: sha16} for every existing file"""
    return {p: sha16(p) for p in paths if p and os.path.isfile(p)}


class P:
    """one pipeline run folder"""
    def __init__(self, folder):
        self.f = os.path.abspath(folder)
        self.I = jload(os.path.join(self.f, 'INPUT.json'))
        self.S = jload(os.path.join(self.f, 'SETTINGS.json'))
        self.fr = self.S['forensics_root']
        self.rd = os.path.join(self.fr, 'team', 'RESEARCH', 'ALARM_DESIGN', 'runs', self.I['run'])
        self.led = os.path.join(self.f, 'ops', 'TYPED_OPS_%s.tsv' % self.I['task'])
        self.jobs = os.path.join(self.f, 'JOBS.tsv')
        self.alarm = '%s_%s' % (self.I['idea'], self.I['v'])

    # ---- files of the run folder
    def p(self, *a):
        return os.path.join(self.f, *a)

    def step_file(self, n, name):
        return self.p('STEP_%02d_%s.json' % (n, name))

    def done(self, n):
        for s in STEPS:
            if s[0] == n:
                q = self.step_file(n, s[1])
                return jload(q) if os.path.exists(q) else None

    def log(self, n, tag):
        return self.p('logs', 'S%02d_%s.out' % (n, tag))

    # ---- commands
    def sh(self, n, tag, argv, env=None, timeout=50, cwd=None):
        """runs a tool, stdout and stderr to logs/S<nn>_<tag>.out; returns (rc, text)"""
        e = dict(os.environ); e.update(env or {})
        lp = self.log(n, tag)
        with open(lp, 'w') as f:
            f.write('# CMD ' + ''.join('%s=%s ' % kv for kv in sorted((env or {}).items())) + ' '.join(argv) + '\n'); f.flush()
            try:
                rc = subprocess.run(argv, stdout=f, stderr=subprocess.STDOUT, env=e, cwd=cwd or self.fr, timeout=timeout,
                                    stdin=subprocess.DEVNULL).returncode
            except subprocess.TimeoutExpired:
                rc = 124
            f.write('\n# RC %d\n' % rc)
        return rc, open(lp).read()

    def py(self, key):
        return [self.S['python'], '-B', self.S[key]]

    def bridge_env(self, op, q=None):
        e = {'LOOP_OPS_LEDGER': self.led, 'LOOP_TASK_ID': self.I['task'], 'LOOP_OP_ID': op}
        if q:
            e['MAC_DESK_QUEUE'] = q
        return e


# ---------------------------------------------------------------- step bodies
def check_input(p):
    I = p.I
    miss = [k for k in INPUT_KEYS if k not in I]
    if miss:
        raise Stop('BAD_INPUT', 'missing keys %s' % ','.join(miss))
    if I['registry_mode'] not in ('write', 'replay'):
        raise Stop('BAD_INPUT', 'registry_mode %r' % I['registry_mode'])
    if I['lean'] not in ('FADE', 'FOLLOW') or I['claim_kind'] not in ('SIDE', 'SIZE'):
        raise Stop('BAD_INPUT', 'lean or claim_kind')
    a, b = (I['window'].split(':') + [''])[:2]
    if not (re.fullmatch(r'\d{8}', a) and re.fullmatch(r'\d{8}', b)) or a > b:
        raise Stop('BAD_WINDOW', I['window'])
    m = a[:6]
    months = []
    while m <= b[:6]:
        months.append(m); y, mm = int(m[:4]), int(m[4:]) + 1
        m = '%04d%02d' % (y + (mm > 12), mm - 12 if mm > 12 else mm)
    never = [x for x in months if x in NEVER_SEEN_MONTHS]          # v1_4: named first, then the holdout, then any other closed month
    if never:
        raise Stop('NEVER_SEEN', 'the window reaches %s: Aug-Nov 2026 is never seen (refused by name to every purpose; the owner opens it once)' % ','.join(never))
    oos = [x for x in months if x in OUT_OF_SAMPLE_MONTHS]
    if oos:
        raise Stop('OUT_OF_SAMPLE', 'the window reaches %s: Apr-Jul 2026 is the holdout, one look per alarm through holdout_month only, never a pipeline run' % ','.join(oos))
    shut = [x for x in months if x not in OPEN_MONTHS]
    if shut:
        raise Stop('WINDOW_CLOSED', 'the window reaches months outside Sep 2025 to Mar 2026 (%d months)' % len(shut))
    blk = BLOCKS.get(I['block'])                                   # v1_3: the window is checked against the block it is graded in
    if not blk:
        raise Stop('BAD_BLOCK', 'block %r, want %s' % (I['block'], ' or '.join(sorted(BLOCKS))))
    out = [x for x in months if x not in blk['months']]
    if out:
        raise Stop('WINDOW_OUTSIDE_BLOCK', 'window %s reaches %s, not months of block %s (%s); one run reads one block: split the window'
                   % (I['window'], ','.join(out), I['block'], ','.join(blk['months'])))
    if not blk['graded']:
        raise Stop('BLOCK_NOT_GRADED', 'block %s: %s' % (I['block'], blk['why']))
    ga, gb = max(a, blk['first']), min(b, blk['last'])
    if ga > gb:
        raise Stop('WINDOW_NOT_GRADED', 'window %s holds no graded day of block %s (%s..%s)' % (I['window'], I['block'], blk['first'], blk['last']))
    h = I['hc']
    hf, hl = str(h.get('first', '')), str(h.get('last', ''))
    if not (re.fullmatch(r'\d{8}', hf) and re.fullmatch(r'\d{8}', hl)) or hf > hl or hf < a or hl > b:
        raise Stop('HC_OUTSIDE_WINDOW', 'hc %s..%s is not inside the window %s' % (hf, hl, I['window']))
    if hf < HC_TOOL_FIRST or hl > HC_TOOL_LAST:                    # v1_4: SEPMAR windows reach past the hand-check tool's range
        raise Stop('HC_OUTSIDE_TOOL', 'hc %s..%s: hc_defs_v4 reads %s..%s only' % (hf, hl, HC_TOOL_FIRST, HC_TOOL_LAST))
    nums = {}
    for k in ('def', 'card', 'claim'):
        q = os.path.join(p.rd, I[k])
        if not os.path.isfile(q):
            raise Stop('NO_FILE', '%s %s' % (k, q))
        nums[k + '_sha16_now'] = sha16(q)
    if nums['def_sha16_now'] != I['def_sha16']:
        raise Stop('DEF_CHANGED', 'def %s is not the input %s' % (nums['def_sha16_now'], I['def_sha16']))
    if nums['card_sha16_now'] != I['card_sha16']:
        raise Stop('CARD_CHANGED', 'card %s is not the input %s' % (nums['card_sha16_now'], I['card_sha16']))
    nums['months'] = months
    nums.update(block=I['block'], graded_days='%s:%s' % (blk['first'], blk['last']), window_graded='%s:%s' % (ga, gb), window_months=months)
    return dict(numbers=nums, outputs=outs([os.path.join(p.rd, I[k]) for k in ('def', 'card', 'claim')]))


def own_tool(p, n, tag, argv, ok=(0,), env=None):
    rc, t = p.sh(n, tag, argv, env=env)
    if rc not in ok:
        raise Stop('TOOL_RC', '%s rc %d (%s)' % (tag, rc, p.log(n, tag)))
    return rc, t


def lines_with(t, pat):
    return [l for l in t.splitlines() if re.search(pat, l)]


def st_copy_search(p, n):
    rc, t = own_tool(p, n, 'tried', p.py('tried_search') + ['--settings', p.S['settings_env']] + p.I['words'].split())
    v = lines_with(t, r'^VERDICT')
    return dict(cmd_log=p.log(n, 'tried'), numbers=dict(rc=rc, verdict=v[-1] if v else 'none printed',
                hits=[l.strip() for l in lines_with(t, r'^(HIT|hit|  )')][:8]), outputs=outs([p.log(n, 'tried')]))


def st_copy_search_def(p, n):
    d = os.path.join(p.rd, p.I['def'])
    rc, t = own_tool(p, n, 'tried_def', p.py('tried_search') + ['--settings', p.S['settings_env'], '--def', d, '--self',
                     '%s_%s' % (p.I['run'], p.I['idea'])])
    v = lines_with(t, r'^VERDICT')
    return dict(numbers=dict(rc=rc, verdict=v[-1] if v else 'none printed'), outputs=outs([p.log(n, 'tried_def')]))


def hc_out(p):
    return 'ideas/%s/HC_FIRES_P18_%s.tsv' % (p.I['idea'], p.I['task'].replace('-', ''))


def rel_args(p, n):
    I = p.I
    if n == 4:
        h = I['hc']
        return ['hc_defs_v4', '--out', hc_out(p), I['def'], h['first'], h['last'], h['coins'], str(h['n']), h['inputs']]
    show = (['--show', I['novelty_show'], '--show-lean', I['lean']] if I.get('novelty_show') else [])
    if n == 5:
        return ['novelty_v5', hc_out(p), '--lean', I['lean'], '--self', '%s_%s' % (I['seat'], I['idea'])] + show
    if n == 7:
        return ['true_gate_check', 'check', I['claim']]
    if n == 10:
        return ['ledger_add_v7', 'prereg', I['idea'], I.get('prereg_purpose', 'GRADE_%s_PIPELINE_V18' % I['v']), I['card']]
    if n == 16:
        g = p.done(11)['numbers']
        return ['novelty_v5', g['fire_list'], '--lean', I['lean'], '--self', '%s_%s' % (I['seat'], I['idea'])] + show
    if n == 21:
        g = p.done(11)['numbers']; pre = p.done(10)['numbers']['prereg_id']
        return ['ledger_add_v7', 'result', pre, g['summary_rel'], race_to_ledger(p.done(14)['numbers']['word']), I['card']]
    raise Stop('NO_ARGS', 'step %d' % n)


def race_to_ledger(word):
    """K37 LEDGER_MAP_V1 (CANDIDATE): PASS -> PASS, STOP -> FAIL, NEEDS MORE MONTHS / INSUFFICIENT -> UNSURE, INVALID -> KILL"""
    return {'PASS': 'PASS', 'STOP': 'FAIL', 'NEEDS MORE MONTHS': 'UNSURE', 'INSUFFICIENT': 'UNSURE', 'INVALID': 'KILL'}[word]


def kitq_args(p, n):
    I = p.I
    if n == 6:
        return ['COUNT', I['idea'], '%s=%s' % (I['v'], I['def'])]
    if n == 11:
        return ['GRADE', I['idea'], I['v']]
    g = p.done(11)['numbers']['job_tag']
    if n == 13:
        return ['TRUE', I['idea'], '%s=%s' % (I['v'], I['claim']), '--from-job', g]
    if n == 15:
        return ['FIRSTLOOK', I['idea'], I['v'], '--from-job', g]
    raise Stop('NO_ARGS', 'step %d' % n)


def firstlook_rule(p):
    """H-PC1 (V14, kept): FIRSTLOOK on a race PASS or an R1 pass, or when both sides beat random at the shortest horizon in every
    month (the GRADE card's 5m lines, k/k)"""
    d = p.done(14)['numbers']; g = p.done(11)['numbers']
    both = g.get('both_sides_5m_every_month', False)
    fire = d['word'] == 'PASS' or d['r1'] in ('yes', 'PASS') or both   # v1_3: decide_v6 prints 'R1 PASS' (matrix: PERPHOUR, WICKBACK R1 PASS, no look)
    return fire, 'race %s, R1 %s, both sides beat random at 5m in every month %s' % (d['word'], d['r1'], 'yes' if both else 'no')


# ---- parsing the kit's own outputs
def parse_kit_receipts(p, n, num, name):
    I = p.I; kind = {6: 'COUNT', 11: 'GRADE', 13: 'TRUE', 15: 'FIRSTLOOK'}[n]
    tag = '%s_%s_%s' % (num, kind, I['idea'])
    r = os.path.join(p.rd, 'receipts', tag)
    if not os.path.isdir(r):
        raise Stop('NO_OUTPUT', 'receipts folder %s missing' % r)
    N = dict(job_tag=tag, receipts=r)
    files = []
    if n == 6:
        c = os.path.join(r, 'COUNT_%s.tsv' % I['v'])      # v1_4: the INPUT's variant (was COUNT_V1: a V2 or V3 stopped NO_OUTPUT, jobs 20270544, 20270546)
        if not os.path.isfile(c):
            raise Stop('NO_OUTPUT', c)
        rows = [l.split('\t') for l in open(c).read().splitlines() if l and not l.startswith('#')]
        h = rows[0]; N['count_rows'] = [dict(zip(h, x)) for x in rows[1:]]
        tail = [l for l in open(c).read().splitlines() if l.startswith('# months with')]
        N['months_line'] = tail[0] if tail else ''
        files.append(c)
    elif n == 11:
        hs = os.path.join(r, 'HANDOFF', 'SUMMARY.tsv'); real = os.path.join(r, 'HANDOFF', 'REAL_SEALED', 'REAL_%s.tsv' % I['v'])
        seal = os.path.join(r, 'PERFIRE_SEAL.tsv'); card = os.path.join(r, 'CARD_%s.txt' % I['v'])
        for q in (hs, real, seal, card):
            if not os.path.isfile(q):
                raise Stop('NO_OUTPUT', q)
        rows = [l.split('\t') for l in open(real).read().splitlines() if l and not l.startswith('#')]
        N['real'] = [dict(zip(rows[0], x)) for x in rows[1:]]
        s = open(seal).read().split()
        N['perfire_sha16'], N['perfire_fires'] = s[1], s[2]
        ct = open(card).read().splitlines()
        N['card_header'] = ct[0] if ct else ''
        f5 = [l for l in ct if re.match(r'^(FADE|FOLLOW)\s+2c<1c 5m', l)]
        N['lines_5m'] = f5
        def kk(l):
            m = re.search(r'\|\s*(\d+)/(\d+)\s*$', l)
            return bool(m) and m.group(1) == m.group(2)
        N['both_sides_5m_every_month'] = len(f5) == 2 and all(kk(l) for l in f5)
        N['summary_rel'] = os.path.relpath(hs, p.rd); N['summary_sha16'] = sha16(hs)
        N['fire_list'] = '%s/work_%s/%s/%s_FIRES_V1_LIST.tsv' % (p.S['scratch_mac'], I['run'], tag, I['v'])
        cut = p.done(1)['numbers'] if p.done(1) else {}
        wm = cut.get('window_months', [])
        N['window_read'] = window_read(N['real'], wm)
        N['window_grain'] = 'month'
        N['window_note'] = ('window %s (graded %s) read from the GRADE of block %s (%s) by month: months %s'
                            % (I['window'], cut.get('window_graded', '?'), I['block'], cut.get('graded_days', '?'), ','.join(wm)))
        files += [hs, real, seal, card]
    elif n == 13:
        d = os.path.join(r, 'TRUE_%s_%s' % (I['v'], I['label']))
        row = os.path.join(d, 'TRUE_ROW.tsv'); tc = os.path.join(d, 'TRUE_CARD.txt')
        for q in (row, tc):
            if not os.path.isfile(q):
                raise Stop('NO_OUTPUT', q)
        L = [l.split('\t') for l in open(row).read().splitlines() if l]
        N['true_row'] = dict(zip(L[0], L[1])); N['true_row_path'] = row
        N['verdict_line'] = ([l for l in open(tc).read().splitlines() if l.startswith('VERDICT')] or [''])[0]
        files += [row, tc]
    else:
        fl = os.path.join(r, 'FIRST_LOOK.md')
        if not os.path.isfile(fl):
            raise Stop('NO_OUTPUT', fl)
        N['rule9'] = ([l for l in open(fl).read().splitlines() if 'RULE_9' in l] or [''])[0]
        files.append(fl)
    return N, files


def parse_rel(p, n, text):
    N = {}
    if 'BRIDGE END rc 0' not in text:
        raise Stop('REL_RC', 'relwait output has no "BRIDGE END rc 0"')
    if n in (5, 16):
        v = lines_with(text, r'^VERDICT')
        if len(v) != 1:
            raise Stop('NO_VERDICT', 'novelty output has %d VERDICT lines' % len(v))
        N['verdict'] = v[0]; N['nearest'] = lines_with(text, r'^nearest \d'); N['show'] = lines_with(text, r'^show:')
    elif n == 4:
        N['lines'] = [l for l in text.splitlines() if l and not l.startswith(('RELBRIDGE', 'BRIDGE'))][-6:]
    elif n == 7:
        N['lines'] = lines_with(text, r'^(OK|FOR THE CARD|REFUSED|VERDICT)')
        if lines_with(text, r'REFUSED'):
            raise Stop('TG_REFUSED', N['lines'][0] if N['lines'] else 'refused')
    elif n == 10:
        m = re.findall(r'PREREG_[A-Z0-9_]+_\d{8}T\d{6}Z(?!_)', text)
        if not m:
            raise Stop('NO_PREREG', 'no PREREG id printed')
        N['prereg_id'] = m[-1]
    elif n == 21:
        m = re.findall(r'PREREG_[A-Z0-9_]+_\d{8}T\d{6}Z_R', text)
        if not m:
            raise Stop('NO_RESULT', 'no _R id printed')
        N['result_id'] = m[-1]
    return N


# ---------------------------------------------------------------- filing and checking jobs
def nextop(p, n):
    rc, t = own_tool(p, n, 'nextop', p.py('ops_jobs') + ['nextop', '--ledger', p.led, '--task', p.I['task'], '--jobs', p.jobs])
    op = t.split('\n')[1].strip() if t.count('\n') > 1 else ''
    m = re.search(r'\b(%s-OP\d+)\b' % re.escape(p.I['task']), t)
    if not m:
        raise Stop('NO_OP', 'nextop printed no op id')
    return m.group(1)


def relq(p, n):
    rc, t = p.sh(n, 'relq', p.py('ops_jobs') + ['relq', '--runner', p.S['rootq'], '--seat', p.I['seat']])
    m = re.search(r'RELQ (Q_\w+)', t)
    if rc != 0 or not m:
        raise Wait('no free rel queue for %s (ops_jobs_v1 relq rc %d: %s)' % (p.I['seat'], rc, t.strip().splitlines()[-2:] if t.strip() else ''))
    return m.group(1)


def file_job(p, n, name, kind):
    fl = p.p('FILING_%02d.json' % n)
    if kind == 'rel':
        q = relq(p, n)
    op = nextop(p, n)
    jwrite(fl, dict(step=n, name=name, kind=kind, op=op, utc=utc()))
    if kind == 'rel':
        argv = p.py('bridge') + ['rel', p.I['run']] + rel_args(p, n)
        rc, t = p.sh(n, 'file', argv, env=p.bridge_env(op, q))
    elif kind == 'kitq':
        a = kitq_args(p, n)
        rc, t = p.sh(n, 'dry', p.py('bridge') + ['kitq', p.I['run']] + a + ['--dry'], env=p.bridge_env(op))
        if rc != 0 or 'DRY RUN OK' not in t:
            os.replace(fl, fl + '.dry_refused_' + stamp())
            old = replay_old(p, a[0])
            if p.I['registry_mode'] == 'replay' and old and re.search(r'REFUSED: ALREADY', t):
                return adopt_old(p, n, name, a[0], str(old), lines_with(t, r'REFUSED: ALREADY')[0])
            raise Stop('DRY_REFUSED', 'kitq --dry rc %d (%s)' % (rc, p.log(n, 'dry')))
        rc, t = p.sh(n, 'file', p.py('bridge') + ['kitq', p.I['run']] + a, env=p.bridge_env(op))
    else:
        rc, t = file_own_job(p, n, op)
    return adopt(p, n, name, kind, op, t, rc)


def adopt(p, n, name, kind, op, t, rc):
    """reads the filing's own output: the job name, number and queue; writes PENDING"""
    if kind == 'rel':
        m = re.search(r'RELBRIDGE QUEUED (\d+)_(\S+) on (Q_\w+)', t)
    elif kind == 'kitq':
        m = re.search(r'QUEUED (Q_\w+) (\d+) (\S+)\.job\.sh', t)
    else:
        m = re.search(r'OWNJOB QUEUED (Q_\w+) (\d+) (\S+)\.job\.sh', t)
    if rc != 0 or not m:
        raise Stop('FILE_REFUSED', '%s filing rc %d, no QUEUED line (%s)' % (kind, rc, p.log(n, 'file')))
    if kind == 'rel':
        num, job, q = m.group(1), '%s_%s' % (m.group(1), m.group(2)), m.group(3)
    else:
        q, num, job = m.group(1), m.group(2), m.group(3)
    if kind in ('rel', 'kitq'):
        own_tool(p, n, 'jobs_add', p.py('ops_jobs') + ['add', '--jobs', p.jobs, '--ledger', p.led, '--op', op, '--step', name,
                 '--purpose', 'alarm_pipeline_v1 step %02d %s for %s' % (n, name, p.alarm), '--out', p.log(n, 'file')])
    pend = dict(step=n, name=name, kind=kind, op=op, job=job, num=num, queue=q, filed=utc(), file_log=p.log(n, 'file'))
    jwrite(p.p('PENDING_%02d.json' % n), pend)
    fl = p.p('FILING_%02d.json' % n)
    if os.path.exists(fl):
        os.replace(fl, p.p('filed', 'FILING_%02d.json' % n))
    return pend


def replay_old(p, kind):
    """v1_3: the earlier job a replay adopts when the kit refuses a re-run (ALREADY): the input's replay_jobs[kind], else, in replay mode, the one
    receipts folder <num>_<KIND>_<IDEA> of the run (a FIRSTLOOK filed by an earlier replay: matrix pass 0 ran FIRSTLOOK for CLOSEOUT, LIQCHAIN,
    MAKERTIDE, and the kit refuses ALREADY LOOKED from then on); none or two folders: None (the refusal stands)"""
    j = (p.I.get('replay_jobs') or {}).get(kind)
    if j:
        return str(j)
    if p.I.get('registry_mode') != 'replay':
        return None
    r = os.path.join(p.rd, 'receipts'); suf = '_%s_%s' % (kind, p.I['idea'])
    hits = sorted(x.split('_')[0] for x in os.listdir(r) if x.endswith(suf) and x.split('_')[0].isdigit()) if os.path.isdir(r) else []
    return hits[0] if len(hits) == 1 else None


def adopt_old(p, n, name, kind, num, why):
    """replay only: the kit refuses a re-run (ALREADY); the earlier job of this kind is adopted, read back, never refiled"""
    hits = []
    for q in sorted(os.listdir(p.S['rootq'])):
        lg = os.path.join(p.S['rootq'], q, 'logs')
        if q.startswith('Q_') and os.path.isdir(lg):
            hits += [(q, x[:-7]) for x in os.listdir(lg) if x.startswith(num + '_') and x.endswith('.status') and ('_%s_%s' % (kind, p.I['idea'])) in x]
    if len(hits) != 1:
        raise Stop('NO_OLD_JOB', 'replay: %d status files of job %s %s %s in the runner' % (len(hits), num, kind, p.I['idea']))
    q, job = hits[0]
    pend = dict(step=n, name=name, kind='kitq', op='-', job=job, num=num, queue=q, filed='-', adopted='yes', refusal=why,
                file_log=p.log(n, 'dry'))
    jwrite(p.p('PENDING_%02d.json' % n), pend)
    return pend


def status_of(p, pend):
    sp = os.path.join(p.S['rootq'], pend['queue'], 'logs', pend['job'] + '.status')
    if not os.path.isfile(sp):
        return None, sp
    kv = dict(l.split('=', 1) for l in open(sp).read().splitlines() if '=' in l)
    if 'exit' not in kv or kv.get('ended', '') == '':
        return None, sp
    return kv, sp


def finish_job(p, n, name, kind, pend):
    kv, sp = status_of(p, pend)
    if kv is None:
        raise Wait('job %s on %s not ended (%s)' % (pend['job'], pend['queue'], sp))
    base = dict(job=pend['job'], job_num=pend['num'], queue=pend['queue'], op=pend['op'], exit=kv['exit'], status_file=sp,
                seconds=kv.get('seconds', ''))
    if kv['exit'].strip() != '0':
        raise Stop('JOB_EXIT', 'job %s exit=%s (%s)' % (pend['job'], kv['exit'], sp))
    N = dict(base)
    files = [sp]
    if pend.get('adopted') == 'yes':
        N['adopted'] = 'yes'; N['refusal'] = pend['refusal']
    if kind in ('rel', 'kitq') and pend.get('adopted') != 'yes':
        rc, t = p.sh(n, 'opdone', p.py('bridge') + ['opdone', pend['op'], pend['num']], env={'LOOP_OPS_LEDGER': p.led,
                     'LOOP_CLOSE_LIB': p.S['close_lib']})
        if rc != 0 or 'SUCCEEDED, exit 0' not in t:
            raise Stop('OPDONE', 'opdone rc %d (%s)' % (rc, p.log(n, 'opdone')))
        N['opdone'] = lines_with(t, r'RELBRIDGE OPDONE')[-1]
        own_tool(p, n, 'jobs_done', p.py('ops_jobs') + ['done', '--jobs', p.jobs, '--op', pend['op'], '--out', p.log(n, 'opdone')])
        files.append(p.log(n, 'opdone'))
    if kind == 'rel':
        rc, t = p.sh(n, 'relwait', p.py('bridge') + ['relwait', pend['job']])
        if rc != 0:
            raise Stop('RELWAIT', 'relwait rc %d (%s)' % (rc, p.log(n, 'relwait')))
        N.update(parse_rel(p, n, t)); files.append(p.log(n, 'relwait'))
    elif kind == 'kitq':
        K, fs = parse_kit_receipts(p, n, pend['num'], pend['job'])
        N.update(K); files += fs
    else:
        K, fs = parse_card_job(p, n, pend)
        N.update(K); files += fs
    return dict(numbers=N, outputs=outs(files))


# ---- step 17: the card runner job (own job, ids from job_alloc)
def mac(p, path):
    for a, b in p.S.get('mac_map', []):
        if path.startswith(a):
            return b + path[len(a):]
    return path


def card_dir(p, num):
    return os.path.join(p.f, 'card_job_%s' % num)


def write_grades(p):
    d = p.done(14)['numbers']; g = p.done(11)['numbers']
    cols = ['alarm', 'state', 'r1', 'r2', 'lead_15m', 't_15m', 'lead_1h', 't_1h', 'waves', 'months_counted', 'months_passing', 'grade_job',
            'result_file', 'result_sha16']
    row = [p.alarm, d['word'], d['r1'], d['r2'], d['lead_15m'], d['t_15m'], d['lead_1h'], d['t_1h'], d['waves'], d['months_counted'],
           d['months_passing'], g['job_tag'], g['summary_rel'], g['summary_sha16']]
    q = p.p('GRADES_%s.tsv' % p.alarm)
    open(q, 'w').write('\t'.join(cols) + '\n' + '\t'.join(str(x) for x in row) + '\n')
    return q


def file_own_job(p, n, op):
    rc, t = p.sh(n, 'alloc', p.S['alloc'] + ['claim', p.I['seat'], '1'], cwd=p.S.get('alloc_cwd', p.fr))
    ids = [l.strip() for l in t.splitlines() if re.fullmatch(r'\d+', l.strip())]
    if rc != 0 or len(ids) != 1:
        raise Stop('ALLOC', 'job_alloc claim rc %d (%s)' % (rc, p.log(n, 'alloc')))
    num = ids[0]; q = p.S['card_queue']
    name = '%s_judge_%s_PIPE_CARD_%s' % (num, p.I['seat'], p.I['idea'])
    gr = write_grades(p)
    g = p.done(11)['numbers']; tr = p.done(13)['numbers']['true_row_path']
    out = card_dir(p, num)
    M = lambda x: mac(p, x)
    body = p.S['card_job_template'] if 'card_job_template' in p.S else open(os.path.join(HERE, 'CARD_JOB_TEMPLATE.sh')).read()
    sub = dict(NAME=name, QUEUE=q, TASK=p.I['task'], OP=op, OUT=M(out), PY=p.S['mac_python'], AU=M(p.S['au_code']), PIPE=M(HERE),
               RN=M(p.S['rootq']), GRADE_NUM=g['job_tag'].split('_')[0], ALARM=p.alarm, BLOCK=p.I['block'], TRUE_ROW=M(tr),
               DEF=M(os.path.join(p.rd, p.I['def'])), DEF_SHA16=p.I['def_sha16'], GRADES=M(gr), MAP=M(p.S['mechanism_map']),
               LEAN=p.I['lean'])
    for k, v in sub.items():
        body = body.replace('{%s}' % k, str(v))
    if re.search(r'\{[A-Z_0-9]+\}', body):
        raise Stop('TEMPLATE', 'unfilled field %s' % re.search(r'\{[A-Z_0-9]+\}', body).group(0))
    os.makedirs(p.p('jobs'), exist_ok=True)
    twin = p.p('jobs', name + '.job.sh')
    open(twin, 'x').write(body)
    rc2 = subprocess.run(['bash', '-n', twin]).returncode
    if rc2 != 0:
        raise Stop('JOB_SYNTAX', 'bash -n rc %d on %s' % (rc2, twin))
    dst = os.path.join(p.S['rootq'], q, 'IN', name + '.job.sh')
    if os.path.exists(dst):
        raise Stop('JOB_EXISTS', dst)
    shutil.copyfile(twin, dst + '.part'); os.replace(dst + '.part', dst)
    t = 'OWNJOB QUEUED %s %s %s.job.sh twin %s sha16 %s\n' % (q, num, name, twin, sha16(twin))
    with open(p.log(n, 'file'), 'w') as f:
        f.write(t)
    return 0, t


def parse_card_job(p, n, pend):
    out = card_dir(p, pend['num'])
    cdir = os.path.join(out, 'CARDS')
    tsv = os.path.join(cdir, 'ALARM_CARDS_%s.tsv' % p.alarm); md = os.path.join(cdir, 'ALARM_CARDS_%s.md' % p.alarm)
    mj = os.path.join(out, 'MECHANISM.json')
    for q in (tsv, md, mj):
        if not os.path.isfile(q):
            raise Stop('NO_OUTPUT', q)
    rows = [l.split('\t') for l in open(tsv).read().splitlines() if l]
    words = {r[1]: r[6] for r in rows[1:] if len(r) > 6}
    return dict(card_tsv=tsv, card_md=md, mechanism_json=mj, strengths=words), [tsv, md, mj]


# ---- own steps after the data
def st_seal_menu(p, n):
    I = p.I
    a = [os.path.join(p.rd, I['def']), os.path.join(p.rd, I['card']), '--claim', os.path.join(p.rd, I['claim'])]
    rc, t = own_tool(p, n, 'menu', p.py('menu_gate') + ['check'] + a, ok=(0, 2))   # v1_3: the gate refuses with rc 2 (matrix F01, job 20270411)
    ok = lines_with(t, r'MENU GATE .*: OK')
    if rc == 2 or not ok:
        ref = lines_with(t, r'^REFUSED') or (t.strip().splitlines() or ['no output'])[-1:]
        raise Stop('MENU_REFUSED', ref[0][:300])
    return dict(numbers=dict(line=ok[0]), outputs=outs([p.log(n, 'menu')]))


def registry_rows(path, *needles):
    if not os.path.isfile(path):
        return []
    return [l for l in open(path).read().splitlines() if all(x in l for x in needles)]


def st_seal_variants(p, n):
    I = p.I
    reg = os.path.join(p.rd, 'registers', 'VARIANTS.tsv')
    rows = registry_rows(reg, I['def_sha16'], I['card_sha16'], I['idea'])
    if I['registry_mode'] == 'replay':
        if len(rows) != 1:
            raise Stop('NO_VARIANTS_ROW', 'replay: %d VARIANTS rows with def %s and card %s' % (len(rows), I['def_sha16'], I['card_sha16']))
        return dict(numbers=dict(mode='replay', row=rows[0][:300]), outputs=outs([reg]))
    if rows:
        return dict(numbers=dict(mode='write', row=rows[0][:300], note='EXISTS: the row is already there, nothing appended'), outputs=outs([reg]))
    if not I.get('variants_fields'):
        raise Stop('NO_FIELDS', 'write mode needs input variants_fields (the VARIANTS fields json, written at CLAIM)')
    rc, t = own_tool(p, n, 'variants', p.py('reg_append') + [p.rd, 'VARIANTS', os.path.join(p.rd, I['variants_fields'])])
    rows = registry_rows(reg, I['def_sha16'], I['card_sha16'], I['idea'])
    if len(rows) != 1:
        raise Stop('VARIANTS_READBACK', '%d rows after the append' % len(rows))
    return dict(numbers=dict(mode='write', row=rows[0][:300]), outputs=outs([reg, p.log(n, 'variants')]))


def ledger_rows(p, *needles):
    return registry_rows(p.S['tries_ledger'], *needles)


def st_replay_ledger(p, n):
    I = p.I
    if n == 10:
        pid = I.get('replay_prereg_id', '')
        rows = ledger_rows(p, pid) if pid else []
        if not pid or not rows:
            raise Stop('NO_PREREG_ROW', 'replay: prereg %r not in %s' % (pid, p.S['tries_ledger']))
        return dict(numbers=dict(mode='replay', prereg_id=pid, rows=len(rows)), outputs=outs([p.S['tries_ledger']]))
    pid = p.done(10)['numbers']['prereg_id']
    want = race_to_ledger(p.done(14)['numbers']['word'])
    rows = [r for r in ledger_rows(p, pid + '_R')]
    if not rows:
        raise Stop('NO_RESULT_ROW', 'replay: %s_R not in the ledger' % pid)
    if not any(('\t%s\t' % want) in ('\t' + r + '\t') for r in rows):
        raise Stop('RESULT_DIFFERS', 'replay: %s_R row does not carry %s' % (pid, want))
    return dict(numbers=dict(mode='replay', result_id=pid + '_R', status=want), outputs=outs([p.S['tries_ledger']]))


def st_true_fill(p, n):
    I = p.I; c = os.path.join(p.rd, I['claim'])
    g = p.done(11)['numbers']
    before = sha16(c)
    if I['registry_mode'] == 'replay':
        perf = json.load(open(c)).get('perfire_sha16', '')
        if perf != g['perfire_sha16']:
            raise Stop('PERFIRE_DIFFERS', 'replay: the sealed claim perfire_sha16 %s is not the new GRADE seal %s' % (perf, g['perfire_sha16']))
        return dict(numbers=dict(mode='replay', claim_sha16=before, unchanged=True, perfire_sha16=perf), outputs=outs([c]))
    twin = c + '.pre_SCO_' + stamp()
    shutil.copy2(c, twin)
    rc, t = own_tool(p, n, 'fill', p.py('claim_fill') + ['fill', '--claim', c, '--grade', g['receipts'], '--v', I['v']], ok=(0,))
    after = sha16(c)
    perf = json.load(open(c)).get('perfire_sha16', '')
    if perf != g['perfire_sha16']:
        raise Stop('PERFIRE_DIFFERS', 'claim perfire_sha16 %s is not the GRADE seal %s' % (perf, g['perfire_sha16']))
    return dict(numbers=dict(claim_before=before, claim_after=after, unchanged=before == after, perfire_sha16=perf, twin=twin),
                outputs=outs([c, twin, p.log(n, 'fill')]))


DEC = re.compile(r'^DECISION (\S+) (\S+): (PASS|NEEDS MORE MONTHS|STOP|INSUFFICIENT|INVALID) \| R1 (\S+) R2 (\S+) \| LEAD 15m (\S+) '
                 r'\(t (\S+)\) 1h (\S+) \(t (\S+)\) \| waves (\d+), months counted (\d+) passing (\d+) \|')


def st_decide(p, n):
    I = p.I; g = p.done(11)['numbers']
    argv = p.py('decide') + ['--settings', p.S['settings_env'], I['run'], I['idea'], I['v'], '--grade', g['job_tag']]
    if I['registry_mode'] == 'write':
        argv.append('--write')
    rc, t = own_tool(p, n, 'decide', argv)
    L = [l for l in t.splitlines() if l.startswith('DECISION ')]
    if len(L) != 1:
        raise Stop('NO_DECISION', '%d DECISION lines' % len(L))
    m = DEC.match(L[0])
    if not m:
        raise Stop('BAD_DECISION', L[0][:200])
    N = dict(line=L[0], word=m.group(3), r1=m.group(4), r2=m.group(5), lead_15m=m.group(6), t_15m=m.group(7), lead_1h=m.group(8),
             t_1h=m.group(9), waves=m.group(10), months_counted=m.group(11), months_passing=m.group(12),
             sources=([l for l in t.splitlines() if l.startswith('SOURCES')] or [''])[0], mode=I['registry_mode'])
    q = p.p('DECIDE_%s.txt' % p.alarm)
    open(q, 'w').write('\n'.join(l for l in t.splitlines() if not l.startswith('# ')) + '\n')
    N['decide_file'] = q
    return dict(numbers=N, outputs=outs([q, p.log(n, 'decide')]))


def st_mechanism(p, n):
    c = p.done(17)['numbers']
    M = jload(c['mechanism_json'])
    for k in ('mechanism', 'share', 'map_sha16', 'shares', 'q3', 'q4'):
        if k not in M:
            raise Stop('BAD_MECHANISM', 'MECHANISM.json lacks %s' % k)
    if M['map_sha16'] != p.S['mechanism_map_sha16']:
        raise Stop('MAP_CHANGED', 'MECHANISM.json map %s, settings %s' % (M['map_sha16'], p.S['mechanism_map_sha16']))
    hyp = p.I['mechanism_hypothesis']
    M['hypothesis'] = hyp
    M['hypothesis_held'] = 'yes' if hyp == M['mechanism'] else 'no'
    return dict(numbers=M, outputs=outs([c['mechanism_json']]))


def st_classify(p, n):
    I = p.I
    nov = p.done(16)['outputs']; novf = [k for k in nov if k.endswith('relwait.out')][0]
    argv = p.py('classify') + ['--idea', I['idea'], '--v', I['v'], '--lean', I['lean'], '--claim-kind', I['claim_kind'],
                              '--decide', p.done(14)['numbers']['decide_file'], '--true-row', p.done(13)['numbers']['true_row_path'],
                              '--novelty', novf, '--open', I['open'], '--count',
                              os.path.join(p.done(6)['numbers']['receipts'], 'COUNT_%s.tsv' % I['v'])]
    fl = p.done(15)
    if fl and fl['numbers'].get('ran') != 'no':
        argv += ['--firstlook', os.path.join(fl['numbers']['receipts'], 'FIRST_LOOK.md')]
    rc, t = own_tool(p, n, 'classify', argv)
    L = [l for l in t.splitlines() if l.startswith('CLASSIFY ')]
    if len(L) != 1:
        raise Stop('NO_CLASSIFY', '%d CLASSIFY lines' % len(L))
    M = p.done(18)['numbers']
    line = L[0] + ' | mechanism %s share %s (map %s)' % (M['mechanism'], M['share'], M['map_sha16'])
    q = p.p('CLASSIFY_%s.txt' % p.alarm)
    open(q, 'w').write(line + '\n' + '\n'.join(l for l in t.splitlines() if l.startswith('SOURCES')) + '\n')
    return dict(numbers=dict(line=line), outputs=outs([q, p.log(n, 'classify')]))


TRIED_WORD = {'PASS': 'WORKED', 'STOP': 'FAILED', 'NEEDS MORE MONTHS': 'UNSURE', 'INSUFFICIENT': 'NOT_MEASURABLE', 'INVALID': 'INVALID_TEST'}


FAIL_LAYER = {'WORKED': 'NONE', 'NOT_MEASURABLE': 'MEASURE', 'INVALID_TEST': 'MEASURE'}   # v1_1: add_row (ADD_ROW_V1) refuses a blank fail_layer
LOOP_COLS = dict(went_well='unknown', failed='unknown', slowed='unknown', gaps='unknown', improve='unknown', faster_next='unknown',
                 not_waste='unknown', minutes_active='unknown', minutes_waiting='unknown', minutes_blocked='unknown', playground_ref='none',
                 prompt_id='none', prompt_fix='none', model='unknown', lesson_id='none', reviewed_by='none')   # v1_1: the TRIED learning columns;
                 # the pipeline does not know them: 'unknown' (add_row: "write none, or unknown, never leave a question blank"); the agent's ANALYZE fills them


def st_log_tried(p, n):
    I = p.I; tid = '%s_%s' % (I['run'], I['idea'])
    reg = p.S['tried_file']
    word = TRIED_WORD[p.done(14)['numbers']['word']]
    rows = [l for l in open(reg).read().splitlines() if l.split('\t')[0] == tid] if os.path.isfile(reg) else []
    if I['registry_mode'] == 'replay':
        if len(rows) != 1:
            raise Stop('NO_TRIED_ROW', 'replay: %d TRIED rows %s' % (len(rows), tid))
        h = open(reg).readline().rstrip('\n').split('\t'); r = dict(zip(h, rows[0].split('\t')))
        if r.get('verdict') != word:
            raise Stop('TRIED_DIFFERS', 'replay: TRIED verdict %s, pipeline %s' % (r.get('verdict'), word))
        return dict(numbers=dict(mode='replay', id=tid, verdict=word), outputs=outs([reg]))
    if rows:
        raise Stop('TRIED_EXISTS', '%s already has a TRIED row' % tid)
    d = p.done(14)['numbers']; t = p.done(13)['numbers']; nv = p.done(16)['numbers']; c = p.done(6)['numbers']
    M = p.done(18)['numbers']
    kv = dict(id=tid, process='2_ALARMS', seat=I['seat'], run=I['run'], what_tried='%s %s (alarm_pipeline_v1): %s' % (I['idea'], I['v'], I.get('claim_text', I['words'])),
              thought_file=os.path.join(p.rd, I['card']), expected='see the sealed card %s %s' % (I['card'], I['card_sha16']),
              actual='%s; TRUE %s; %s; mechanism %s share %s' % (d['line'], t['verdict_line'], nv['verdict'], M['mechanism'], M['share']),
              verdict=word, failed_stage='DECIDE' if word != 'WORKED' else 'none', fail_layer=FAIL_LAYER.get(word, 'PREMISE'), why='see ANALYZE.md in the run folder',
              receipts=';'.join(x['numbers'].get('job_tag', x['numbers'].get('job', '')) for x in (p.done(6), p.done(11), p.done(13), p.done(16))),
              ledger_row=p.done(10)['numbers']['prereg_id'] + '_R', months_read=I['window'], tools_used='alarm_pipeline_v1',
              next_action='CARD REVIEW then PROPOSE',
              closest_existing=(nv.get('nearest') or ['none'])[0], **LOOP_COLS)
    argv = p.py('add_row') + [reg] + ['%s=%s' % (k, v.replace('\t', ' ').replace('\n', ' ')) for k, v in kv.items()]
    rc, out = own_tool(p, n, 'add_row', argv)
    return dict(numbers=dict(mode='write', id=tid, verdict=word), outputs=outs([reg, p.log(n, 'add_row')]))


def st_handoff(p, n):
    c = p.done(17)['numbers']; M = p.done(18)['numbers']
    kit = dict(race=p.done(14)['numbers']['word'], true=p.done(13)['numbers']['true_row'].get('verdict', ''),
               novelty=p.done(16)['numbers']['verdict'].split(':')[0].replace('VERDICT ', ''))
    fl = p.done(15)
    kit['firstlook'] = fl['numbers'].get('rule9', '') if fl and fl['numbers'].get('ran') != 'no' else 'not run: ' + (fl['numbers'].get('rule', '') if fl else '')
    jobs = {s[1]: p.done(s[0])['numbers'].get('job', '') for s in STEPS if s[2] in ('rel', 'kitq', 'job') and p.done(s[0]) and p.done(s[0])['numbers'].get('job')}
    meta = dict(alarm=p.alarm, def_sha16=p.I['def_sha16'], card_sha16=p.I['card_sha16'], kit=kit, jobs=jobs, run_folder=p.f, task=p.I['task'],
                classify=p.done(19)['numbers']['line'], hypothesis=p.I['mechanism_hypothesis'],
                role=p.I.get('role', 'member' if M['mechanism'] != 'NONE' else 'unpooled'))
    mj = p.p('HANDOFF_META.json'); jwrite(mj, meta)
    argv = p.py('card_v1') + ['--alarm', p.alarm, '--cards-tsv', c['card_tsv'], '--cards-md', c['card_md'], '--mechanism-json',
                              c['mechanism_json'], '--meta', mj, '--root', p.S['cards_root'], '--out', p.p('ALARM_CARD')]
    rc, t = own_tool(p, n, 'card', argv)
    L = lines_with(t, r'^HANDOFF ')
    if len(L) != 1:
        raise Stop('NO_HANDOFF', 'card_v1 printed %d HANDOFF lines' % len(L))
    m = re.match(r'^HANDOFF (\S+) (\S+) card (\S+) sha16 (\w+) index (\S+)', L[0])
    if not m:
        raise Stop('NO_HANDOFF', L[0][:200])
    return dict(numbers=dict(line=L[0], mechanism=m.group(2), card=m.group(3), card_sha16=m.group(4), index=m.group(5)),
                outputs=outs([m.group(3), m.group(3).replace('.md', '.tsv'), os.path.join(os.path.dirname(m.group(3)), 'HANDOFF.json'), m.group(5)]))


OWN = {1: lambda p, n: check_input(p), 2: st_copy_search, 3: st_copy_search_def, 8: st_seal_menu, 9: st_seal_variants,
       12: st_true_fill, 14: st_decide, 18: st_mechanism, 19: st_classify, 20: st_log_tried, 22: st_handoff}


# ---------------------------------------------------------------- the moves
def write_step(p, n, name, kind, body):
    rec = dict(step=n, name=name, kind=kind, utc=utc(), alarm=p.alarm, task=p.I['task'])
    rec.update(body)
    jwrite(p.step_file(n, name), rec)
    pend = p.p('PENDING_%02d.json' % n)
    if os.path.exists(pend):
        os.replace(pend, p.p('filed', 'PENDING_%02d.json' % n))
    return rec


def write_stop(p, n, name, code, why):
    q = p.p('STOP_%02d_%s.json' % (n, name))
    jwrite(q, dict(step=n, name=name, code=code, why=why, utc=utc()))
    return 'STOP %02d %s %s: %s' % (n, name, code, why)


def one_move(p):
    """returns (rc, line): 0 a step done (or all DONE), 10 WAIT, 3 STOP"""
    for n, name, kind in ORDER:
        if p.done(n):
            continue
        stops = [x for x in os.listdir(p.f) if x.startswith('STOP_%02d_' % n) and x.endswith('.json')]
        if stops:
            s = jload(p.p(stops[0]))
            return 3, 'STOP %02d %s %s: %s' % (n, name, s['code'], s['why'])
        try:
            if n == 15:
                fire, why = firstlook_rule(p)
                if not fire and not os.path.exists(p.p('PENDING_15.json')):
                    write_step(p, n, name, kind, dict(numbers=dict(ran='no', rule=why), outputs={}))
                    return 0, 'DONE 15 FIRSTLOOK not run: ' + why
            if p.I['registry_mode'] == 'replay' and n in REPLAY_SKIP_FILE:
                write_step(p, n, name, 'own', st_replay_ledger(p, n))
                return 0, 'DONE %02d %s (replay read-back)' % (n, name)
            if kind == 'own':
                write_step(p, n, name, kind, OWN[n](p, n))
                return 0, 'DONE %02d %s' % (n, name)
            pq = p.p('PENDING_%02d.json' % n); fq = p.p('FILING_%02d.json' % n)
            if not os.path.exists(pq) and os.path.exists(fq):
                f = jload(fq)
                lg = p.log(n, 'file')
                t = open(lg).read() if os.path.exists(lg) else ''
                if not t:
                    return 3, write_stop(p, n, name, 'CUT_BEFORE_FILE', 'FILING_%02d.json exists without a filing output: check ledger op %s by hand' % (n, f['op']))
                adopt(p, n, name, kind, f['op'], t, 0)
                return 10, 'WAIT %02d %s adopted after a cut (%s)' % (n, name, f['op'])
            if not os.path.exists(pq):
                pend = file_job(p, n, name, kind)
                if pend.get('adopted') == 'yes':
                    return 10, 'WAIT %02d %s adopted job %s on %s (replay: %s)' % (n, name, pend['job'], pend['queue'], pend['refusal'][:80])
                return 10, 'WAIT %02d %s filed job %s on %s (op %s)' % (n, name, pend['job'], pend['queue'], pend['op'])
            pend = jload(pq)
            body = finish_job(p, n, name, kind, pend)
            if n == 15:
                body['numbers']['ran'] = 'yes'
            write_step(p, n, name, kind, body)
            return 0, 'DONE %02d %s job %s exit %s' % (n, name, pend['job'], body['numbers']['exit'])
        except Wait as w:
            return 10, 'WAIT %02d %s %s' % (n, name, w.why)
        except Stop as s:
            return 3, write_stop(p, n, name, s.code, s.why)
    return 0, 'DONE ALL'


def table(p):
    L = ['step\tname\tkind\tstate\tjob\texit\tnote']
    for n, name, kind in STEPS:
        d = p.done(n)
        stops = [x for x in os.listdir(p.f) if x.startswith('STOP_%02d_' % n) and x.endswith('.json')]
        if d:
            N = d.get('numbers', {})
            L.append('%02d\t%s\t%s\tDONE\t%s\t%s\t%s' % (n, name, d.get('kind', kind), N.get('job', '-'), N.get('exit', '-'),
                     'not run: ' + N['rule'] if N.get('ran') == 'no' else N.get('mode', '')))
        elif stops:
            s = jload(p.p(stops[0])); L.append('%02d\t%s\t%s\tSTOP\t-\t-\t%s %s' % (n, name, kind, s['code'], s['why'][:120]))
        elif os.path.exists(p.p('PENDING_%02d.json' % n)):
            q = jload(p.p('PENDING_%02d.json' % n)); L.append('%02d\t%s\t%s\tWAIT\t%s\t-\t%s' % (n, name, kind, q['job'], q['queue']))
        else:
            L.append('%02d\t%s\t%s\t-\t-\t-\t' % (n, name, kind))
    return '\n'.join(L)


def init(folder, inp, settings):
    if os.path.exists(folder) and os.listdir(folder):
        print('REFUSED EXISTS: %s is not empty' % folder); return 2
    for d in ('', 'ops', 'logs', 'filed', 'jobs'):
        os.makedirs(os.path.join(folder, d), exist_ok=True)
    shutil.copyfile(inp, os.path.join(folder, 'INPUT.json')); shutil.copyfile(settings, os.path.join(folder, 'SETTINGS.json'))
    p = P(folder)
    open(p.led, 'x').write('id\tstatus\tutc\ttext\n')
    print('INIT %s input %s settings %s ledger %s' % (p.f, sha16(p.p('INPUT.json')), sha16(p.p('SETTINGS.json')), p.led))
    return 0


def main(argv):
    if len(argv) < 2 or argv[0] not in ('init', 'next', 'run', 'status', 'retry'):
        print(__doc__.split('\n')[1]); print('usage: alarm_pipeline_v1.py init|next|run|status|retry <run folder> ...'); return 2
    cmd, folder = argv[0], argv[1]
    if cmd == 'init':
        a = dict(zip(argv[2::2], argv[3::2]))
        if '--input' not in a or '--settings' not in a:
            print('usage: init <run folder> --input INPUT.json --settings PIPE_SETTINGS.json'); return 2
        return init(folder, a['--input'], a['--settings'])
    p = P(folder)
    if cmd == 'status':
        print(table(p)); return 0
    if cmd == 'retry':
        for x in sorted(os.listdir(p.f)):
            if x.startswith('STOP_') and x.endswith('.json'):
                os.replace(p.p(x), p.p('filed', x + '.retried_' + stamp())); print('RETRY moved %s aside' % x)
        return 0
    if cmd == 'next':
        rc, line = one_move(p); print(line); return rc
    t0 = time.time(); rc = 0
    while time.time() - t0 < BUDGET_S:
        rc, line = one_move(p); print(line); sys.stdout.flush()
        if rc != 0 or line == 'DONE ALL':
            break
    print(table(p))
    return rc


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
