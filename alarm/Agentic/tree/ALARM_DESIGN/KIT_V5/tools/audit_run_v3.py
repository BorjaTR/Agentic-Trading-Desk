#!/usr/bin/env python3
"""audit_run_v3.py (SCOUT for ALARM_DESIGN KIT_V5, 30 Oct 2026; edition 3 of audit_run_v2.py 7e533d36e0dd9132; TEST, NOT REVIEWED). The
scorecard of one KIT_V5 run. Runs from the Alarm package on any machine. Reads registers, receipts, the run's files and its board; writes
only RUN/audit/AUDIT_<stamp>.txt with --write.

  python3 -B <Alarm>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/audit_run_v3.py --settings <settings file> <RUN> [--write]

Edition 3 changes only where things are (the owner 30 Oct 2026 22:21 Berlin: "Let's make sure everything can run from the release folder";
CLEAN_RELEASE_V1 section 6). The checks, the lines, the AUDIT file and the exit codes are audit_run_v2.py's (the first line now
names audit_run_v3.py):
  --settings <file>  required: this machine's settings file (<Alarm>/settings/SETTINGS_<MACHINE>.env), read by the package's own
                     _tools/settings_v1.py: the runs and the claims under <RESEARCH_ROOT>/ALARM_DESIGN, the board under BOARD (the hb
                     folder), the queues under RUNNER_QUEUES (empty: the queues are not read, as when v2 could not see the runner)
  the Alarm folder   settings_v1.alarm_root(this file); A6 computes each decision again with decide_v2.py (configured with the same
                     settings file: its price-path reader inside the Alarm folder) and decide_forward_v2.py, both next to this file
  audit_run_v2.py found the dev tree, the board, the runner and the scratch drive itself (_roots()) and ran decide_v1.py and
  decide_forward_v1.py; this edition names no machine path.

Checks (each PASS, WARN or FAIL, with what failed; LEARNINGS_V5 rows in brackets):
  A1 REGISTERS   the 8 registers exist, headers as KIT_V5 says, every row full width (V5-27)
  A2 CLAIMS      every idea with a variant, job or decision has its claim file (V5-04); a CLEAN job's IDEA is a label, not an idea
  A3 SEALED      each GRADE/ENTRY/MONTH job: its variants registered before it was queued; PREREG and definitions unchanged (V5-07, V5-20)
  A4 BUDGET      at most 3 graded variants an idea (V5-07)
  A5 FORECASTS   each MONTH job: Jan-Apr forecasts registered before it was queued (V5-16)
  A6 SOURCED     each DECISIONS row equals what decide_v2.py (decide_v1.py's rule) computes again from the receipts now (V5-28)
  A7 PICKUP      each finished job read (a DECISIONS or POSTMORTEMS row naming it) within 20 minutes of its end (V5-05)
  A8 DISK        each job wrote no more than its WRITES_MB (receipts DISK.tsv and STORE_PLACES.tsv) (V5-21)
  A9 POSTMORTEM  each decided variant has a POSTMORTEMS row (warn for 20 minutes after the decision)
  A10 FINDINGS   each decided idea has ideas/<IDEA>/FINDINGS_<IDEA>.md (warn for 30 minutes after its first decision)
  A11 BOARD      your board lines: stamp first, under 578 characters, no em dash; a START line (V5-30)
  A12 WORDS      no 'does not exist' and no em dash in your ideas/ markdown (V5-09)
  A13 STUCK      a second failed job of the same kind for one idea has a PROBLEMS row and a STUCK board line (V5-08)
  A14 LEARN      LEARNINGS_PROPOSED rows: kind RULE, TOOL, CHECK or SKILL; the evidence file exists with its sha16 (V5-34)
  A15 TOOLS      TOOLS_BUILT rows: the tool and its test exist with their sha16 (V5-36)
  A16 JOBS       every job twin in RUN/jobs has its RUNS row; your jobs in the Q_V queues are all in RUNS (V5-20)
  A17 CLEAN      a cleaned GRADE job kept its fire lists on dev with their sha16 (FAIL if not); a decided job still uncleaned 60 minutes
                 after its last decision or postmortem is a WARN; the run's uncleaned scratch over 10,000 MB is a FAIL (V5-41; 8,000 from round 2, 10,000 from round 3 19:40Z)
"""
import sys, os, re, glob, hashlib, datetime, importlib.util

CFG = {'H': None, 'HB': None, 'RUNNER': None,   # configure() fills H, HB, RUNNER and SETTINGS
       'SETTINGS': None,                        # the settings file, handed to decide_v2.py in A6
       'DECIDE': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'decide_v2.py'), 'DECIDE_CFG': {},
       'now': lambda: datetime.datetime.now(datetime.timezone.utc)}
HDR = {
    'VARIANTS': ['utc', 'idea', 'V', 'lean', 'def_rel', 'def_sha16', 'prereg_rel', 'prereg_sha16', 'reason'],
    'FORECASTS': ['utc', 'idea', 'V', 'scope', 'gap15_lo', 'gap15_hi', 'gap1h_lo', 'gap1h_hi', 'file_rel', 'file_sha16', 'note'],
    'RUNS': ['utc_queued', 'job', 'job_sha16', 'kind', 'idea', 'variants', 'queue', 'prereg_rel', 'prereg_sha16', 'writes_mb', 'mem_mb', 'minutes',
             'template_sha16', 'from_job', 'receipts_rel'],
    'DECISIONS': ['utc', 'idea', 'V', 'state', 'label_rule', 'r1', 'r2', 'months_counted', 'months_passing', 'waves', 'lead_15m', 't_15m', 'lead_1h',
                  't_1h', 'gate_handoff', 'clear', 'clear_at', 'price_gate', 'tough_15m', 'tough_1h', 'money_tt', 'money_rr', 'grade_job', 'entry_job',
                  'sources', 'note'],
    'POSTMORTEMS': ['utc', 'idea', 'V', 'job', 'scope', 'forecast', 'result', 'result_file', 'result_sha16', 'why', 'unexplained'],
    'LEARNINGS_PROPOSED': ['utc', 'id', 'kind', 'section', 'change', 'evidence_file', 'evidence_sha16', 'scope', 'status'],
    'PROBLEMS': ['utc', 'kind', 'where', 'what_is_wrong', 'evidence', 'severity', 'action', 'proposed_fix', 'reported_to_lead'],
    'TOOLS_BUILT': ['utc', 'tool_rel', 'sha16', 'range', 'test_rel', 'test_sha16', 'why'],
}
RUNTAG = re.compile(r'^([A-Z][A-Z0-9]{0,11})_([0-9]{8})$')
STAMP = re.compile(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})Z ')


class Refused(Exception):
    pass


def settings_reader():
    """the settings reader of the Alarm package this file is in (<Alarm>/_tools/settings_v1.py), loaded from that file"""
    d = os.path.dirname(os.path.abspath(__file__))
    while not os.path.isfile(os.path.join(d, '_tools', 'settings_v1.py')):
        if os.path.dirname(d) == d:
            raise Refused('NOT INSIDE AN ALARM PACKAGE: %s (run the copy in the Alarm folder)' % os.path.abspath(__file__))
        d = os.path.dirname(d)
    spec = importlib.util.spec_from_file_location('settings_v1', os.path.join(d, '_tools', 'settings_v1.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def configure(settings):
    """CFG from the settings file: the runs and claims under RESEARCH_ROOT, the board under BOARD, the queues under RUNNER_QUEUES"""
    S = settings_reader()
    try:
        S.alarm_root(__file__)
        research, board = S.get(settings, 'RESEARCH_ROOT'), S.get(settings, 'BOARD')
        runner = S.load(settings).get('RUNNER_QUEUES', '')
    except S.Refused as e:
        raise Refused('SETTINGS: %s' % e)
    CFG.update({'H': os.path.join(research, 'ALARM_DESIGN'), 'HB': board, 'RUNNER': runner, 'SETTINGS': os.path.abspath(settings)})


def sha16(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def ts(s):
    try:
        return datetime.datetime.strptime(s[:19], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=datetime.timezone.utc)
    except (ValueError, TypeError):
        return None


def read(p):
    if not os.path.isfile(p):
        return None, []
    with open(p) as f:
        lines = [l.rstrip('\n') for l in f if l.strip() and not l.startswith('#')]
    if not lines:
        return [], []
    h = lines[0].split('\t')
    return h, [l.split('\t') for l in lines[1:]]


def stages(d):
    h, rows = read(os.path.join(d, 'STAGES.tsv'))
    return {} if not h else {r[0]: dict(zip(h, r)) for r in rows if r}


class Audit:
    def __init__(self, runtag):
        self.runtag = runtag; self.seat = RUNTAG.match(runtag).group(1)
        self.run = os.path.join(CFG['H'], 'runs', runtag); self.now = CFG['now']()
        self.res = []; self.R = {}
        for n, hh in HDR.items():
            h, rows = read(os.path.join(self.run, 'registers', n + '.tsv'))
            self.R[n] = (h, [dict(zip(h or hh, r)) for r in rows])

    def add(self, cid, name, fails, warns=()):
        st = 'FAIL' if fails else ('WARN' if warns else 'PASS')
        self.res.append((cid, name, st, list(fails)[:8], list(warns)[:8], len(fails), len(warns)))

    def rows(self, n):
        return self.R[n][1]

    def a1(self):
        f = []
        for n, hh in HDR.items():
            h, rows = read(os.path.join(self.run, 'registers', n + '.tsv'))
            if h is None:
                f.append('%s missing' % n); continue
            if h != hh:
                f.append('%s header differs' % n)
            f += ['%s row %d has %d fields, header %d' % (n, i + 2, len(r), len(hh)) for i, r in enumerate(rows) if len(r) != len(hh)]
        self.add('A1', 'REGISTERS', f)

    def ideas(self):
        s = set()
        for n in ('VARIANTS', 'RUNS', 'DECISIONS'):
            s |= {r.get('idea') for r in self.rows(n) if r.get('idea') and not (n == 'RUNS' and r.get('kind') == 'CLEAN')}
        return sorted(s)

    def a2(self):
        f = [i for i in self.ideas() if not os.path.isfile(os.path.join(CFG['H'], 'runs', 'IDEAS_CLAIMED', '%s_%s.txt' % (self.runtag, i)))]
        self.add('A2', 'CLAIMS', ['no claim file for %s' % i for i in f])

    def a3_a4_a5(self):
        f3, f4, f5 = [], [], []
        var = self.rows('VARIANTS'); fc = self.rows('FORECASTS')
        graded = {}
        for r in self.rows('RUNS'):
            k, idea, q = r.get('kind'), r.get('idea'), ts(r.get('utc_queued', ''))
            vs = [v for v in r.get('variants', '').split(',') if v]
            if k == 'GRADE':
                graded.setdefault(idea, set()).update(vs)
            if k in ('GRADE', 'ENTRY', 'MONTH'):
                for v in vs:
                    first = [x for x in var if x.get('idea') == idea and x.get('V') == v]
                    if not first or ts(first[0].get('utc', '')) is None or q is None or ts(first[0]['utc']) > q:
                        f3.append('%s %s %s: variant not registered before the job' % (r.get('job'), idea, v)); continue
                    d = os.path.join(self.run, first[-1].get('def_rel', ''))
                    if not os.path.isfile(d) or sha16(d) != first[-1].get('def_sha16'):
                        f3.append('%s %s: definition missing or changed' % (idea, v))
                p = os.path.join(self.run, r.get('prereg_rel', ''))
                if not os.path.isfile(p) or sha16(p) != r.get('prereg_sha16'):
                    f3.append('%s: PREREG %s missing or changed since the job' % (r.get('job'), r.get('prereg_rel')))
            if k == 'MONTH':
                for v in vs:
                    for m in ('2601', '2602', '2603', '2604'):
                        ok = [x for x in fc if x.get('idea') == idea and x.get('V') == v and x.get('scope') == m and ts(x.get('utc', '')) and q and ts(x['utc']) <= q]
                        if not ok:
                            f5.append('%s %s %s: no forecast for %s before the job' % (r.get('job'), idea, v, m))
        f4 = ['%s: %d graded variants %s' % (i, len(s), sorted(s)) for i, s in graded.items() if len(s) > 3]
        self.add('A3', 'SEALED', f3); self.add('A4', 'BUDGET', f4); self.add('A5', 'FORECASTS', f5)

    def a6(self):
        f = []
        dec = self.rows('DECISIONS')
        if dec:
            try:
                spec = importlib.util.spec_from_file_location('decide_v2', CFG['DECIDE']); D = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(D)
                if CFG['SETTINGS']:
                    D.configure(CFG['SETTINGS'])      # its price-path reader inside the Alarm folder
                D.CFG['H'] = CFG['H']; D.CFG.update(CFG['DECIDE_CFG'])
            except Exception as e:
                self.add('A6', 'SOURCED', ['%s could not load: %s' % (os.path.basename(CFG['DECIDE']), e)]); return
            Fw = None
            for r in dec:
                if (r.get('label_rule') or '').startswith('FORWARD ONLY'):   # decide_forward_v2.py (the owner 29 Oct 22:02 Berlin)
                    try:
                        if Fw is None:
                            spec = importlib.util.spec_from_file_location('decide_forward_v2', os.path.join(os.path.dirname(CFG['DECIDE']), 'decide_forward_v2.py'))
                            Fw = importlib.util.module_from_spec(spec); spec.loader.exec_module(Fw); Fw.CFG['H'] = CFG['H']
                        mj = re.match(r'^month ([0-9]+_MONTH_[A-Z0-9]+):', r.get('sources', ''))
                        d = Fw.decide(self.run, r['idea'], r['V'], mj.group(1) if mj else '')
                    except Exception as e:
                        f.append('%s %s: cannot recompute the forward-only decision (%s)' % (r.get('idea'), r.get('V'), e)); continue
                    for k in ('state', 'months_counted', 'months_passing'):
                        if str(d.get(k, '')) != r.get(k, ''):
                            f.append('%s %s: %s is %r, receipts say %r' % (r.get('idea'), r.get('V'), k, r.get(k), d.get(k)))
                    continue
                if r.get('label_rule') != D.RULE:
                    f.append('%s %s: not written by decide_v1.py' % (r.get('idea'), r.get('V'))); continue
                try:
                    d = D.decide(self.run, r['idea'], r['V'], r['grade_job'], None if r.get('entry_job') in ('', '-') else r['entry_job'],
                                 r.get('state') == 'NO ENTRY')   # V6-41: a NO ENTRY row is recomputed with --entry-too-big
                except Exception as e:
                    f.append('%s %s: cannot recompute (%s)' % (r.get('idea'), r.get('V'), e)); continue
                for k in ('state', 'r1', 'r2', 'lead_15m', 't_15m', 'lead_1h', 't_1h', 'clear', 'months_counted', 'waves'):
                    if str(d.get(k, '')) != r.get(k, ''):
                        f.append('%s %s: %s is %r, receipts say %r' % (r.get('idea'), r.get('V'), k, r.get(k), d.get(k)))
        self.add('A6', 'SOURCED', f)

    def jobs(self, clean=False):
        out = []
        for d in sorted(glob.glob(os.path.join(self.run, 'receipts', '*'))):
            if ('_CLEAN_' in os.path.basename(d)) != clean:
                continue
            st = stages(d)
            if 'end' in st:
                out.append((os.path.basename(d), st))
        return out

    def a7_a8_a13(self):
        f7, w7, f8, f13 = [], [], [], []
        runs = {r.get('receipts_rel', '').replace('receipts/', ''): r for r in self.rows('RUNS')}
        named = {}
        for r in self.rows('POSTMORTEMS'):
            named.setdefault(r.get('job'), []).append(ts(r.get('utc', '')))
        for r in self.rows('DECISIONS'):
            for j in (r.get('grade_job'), r.get('entry_job')):
                named.setdefault(j, []).append(ts(r.get('utc', '')))
        fails = {}
        for j, st in self.jobs():
            end = ts(st['end'].get('utc', ''))
            reads = sorted(t for t in named.get(j, []) if t)
            if end:
                lag = ((reads[0] if reads else self.now) - end).total_seconds() / 60.0
                if lag > 20:
                    (f7 if not reads else w7).append('%s: %s %.0f min after its end' % (j, 'read' if reads else 'NOT READ', lag))
            bad = [s for s, x in st.items() if x.get('rc') not in ('0', None) and s not in ('quiet',)]
            if bad:
                m = re.match(r'^\d+_([A-Z]+)_([A-Z0-9]+)$', j)
                if m:
                    fails.setdefault((m.group(2), m.group(1)), []).append(j)
            r = runs.get(j)
            if r:
                try:
                    lim = int(r.get('writes_mb', '0'))
                except ValueError:
                    lim = 0
                used = 0
                h, rows = read(os.path.join(self.run, 'receipts', j, 'DISK.tsv'))
                for x in [h] + rows if h else []:
                    if x and x[0] == 'du_mb_W':
                        used += int(x[1])
                for p in glob.glob(os.path.join(self.run, 'receipts', j, '*', 'STORE_PLACES.tsv')):
                    for l in open(p):
                        x = l.rstrip('\n').split('\t')
                        if x[0] == 'du_mb' and len(x) > 1 and x[1].isdigit():
                            used += int(x[1])
                if lim and used > lim:
                    f8.append('%s wrote %d MB, declared %d' % (j, used, lim))
        board = self.board()
        for (idea, kind), js in fails.items():
            if len(js) >= 2:
                prob = any(idea in (p.get('where', '') + p.get('what_is_wrong', '') + p.get('evidence', '')) for p in self.rows('PROBLEMS'))
                stuck = any(' STUCK ' in l and idea in l for l in board)
                if not (prob and stuck):
                    f13.append('%s %s failed %d times (%s): PROBLEMS row %s, STUCK line %s' % (idea, kind, len(js), ', '.join(js), prob, stuck))
        self.add('A7', 'PICKUP', f7, w7); self.add('A8', 'DISK', f8); self.add('A13', 'STUCK', f13)

    def a9_a10(self):
        f9, w9, f10, w10 = [], [], [], []
        pm = {(r.get('idea'), r.get('V')) for r in self.rows('POSTMORTEMS')}
        first = {}
        for r in self.rows('DECISIONS'):
            t = ts(r.get('utc', '')); key = (r.get('idea'), r.get('V'))
            first.setdefault(r.get('idea'), t)
            if key not in pm:
                age = (self.now - t).total_seconds() / 60.0 if t else 999
                (f9 if age > 20 else w9).append('%s %s: no POSTMORTEMS row (%.0f min)' % (key[0], key[1], age))
        for idea, t in first.items():
            if not os.path.isfile(os.path.join(self.run, 'ideas', idea, 'FINDINGS_%s.md' % idea)):
                age = (self.now - t).total_seconds() / 60.0 if t else 999
                (f10 if age > 30 else w10).append('%s: no FINDINGS_%s.md (%.0f min)' % (idea, idea, age))
        self.add('A9', 'POSTMORTEM', f9, w9); self.add('A10', 'FINDINGS', f10, w10)

    def board(self):
        p = os.path.join(CFG['HB'], self.seat + '.txt')
        return [l.rstrip('\n') for l in open(p)] if os.path.isfile(p) else []

    def a11(self):
        f = []
        mine = [l for l in self.board() if re.match(r'^\S+ %s ' % self.seat, l)]
        for l in mine:
            if not STAMP.match(l):
                f.append('no stamp: %s' % l[:60])
            if len(l) >= 578:
                f.append('%d characters: %s' % (len(l), l[:60]))
            if '\u2014' in l:
                f.append('em dash: %s' % l[:60])
        if not any(' START ' in l for l in mine):
            f.append('no START line on hb/%s.txt' % self.seat)
        self.add('A11', 'BOARD', f)

    def a12(self):
        f = []
        for p in glob.glob(os.path.join(self.run, 'ideas', '*', '*.md')) + glob.glob(os.path.join(self.run, '*.md')):
            t = open(p, errors='replace').read()
            if 'does not exist' in t.lower():
                f.append('%s says "does not exist"' % os.path.relpath(p, self.run))
            if '\u2014' in t:
                f.append('%s has an em dash' % os.path.relpath(p, self.run))
        self.add('A12', 'WORDS', f)

    def a14_a15(self):
        f14, f15 = [], []
        for r in self.rows('LEARNINGS_PROPOSED'):
            if r.get('kind') not in ('RULE', 'TOOL', 'CHECK', 'SKILL'):
                f14.append('%s: kind %r' % (r.get('id'), r.get('kind')))
            p = r.get('evidence_file', '')
            q = p if os.path.isabs(p) else os.path.join(self.run, p)
            if not p or not os.path.isfile(q) or sha16(q) != r.get('evidence_sha16'):
                f14.append('%s: evidence %s missing or changed' % (r.get('id'), p))
        for r in self.rows('TOOLS_BUILT'):
            for k, s in (('tool_rel', 'sha16'), ('test_rel', 'test_sha16')):
                p = os.path.join(self.run, r.get(k, ''))
                if not r.get(k) or not os.path.isfile(p) or sha16(p) != r.get(s):
                    f15.append('%s: %s missing or changed' % (r.get('tool_rel'), k))
        self.add('A14', 'LEARN', f14); self.add('A15', 'TOOLS', f15)

    def a16(self):
        f = []
        reg = {r.get('job'): r.get('job_sha16') for r in self.rows('RUNS')}
        for p in sorted(glob.glob(os.path.join(self.run, 'jobs', '*.job.sh'))):
            rel = os.path.relpath(p, self.run)
            if rel not in reg:
                f.append('%s has no RUNS row' % rel)
            elif sha16(p) != reg[rel]:
                f.append('%s changed since its RUNS row' % rel)
        names = {os.path.basename(k) for k in reg}
        if os.path.isdir(CFG['RUNNER']):
            for q in sorted(os.listdir(CFG['RUNNER'])):
                if not q.startswith('Q_V'):
                    continue
                for sub in ('IN', 'RUN'):
                    d = os.path.join(CFG['RUNNER'], q, sub)
                    if os.path.isdir(d):
                        f += ['%s/%s/%s not made by queue_job_v5.py' % (q, sub, x) for x in os.listdir(d)
                              if x.endswith('.job.sh') and '_judge_%s_' % self.seat in x and x not in names]
        self.add('A16', 'JOBS', f)

    def used_mb(self):
        used = 0
        for r in self.rows('RUNS'):
            if r.get('kind') not in ('COUNT', 'GRADE', 'ENTRY', 'MONTH'):
                continue
            d = os.path.join(self.run, r.get('receipts_rel', ''))
            if os.path.exists(os.path.join(d, 'CLEANED_BY.txt')):
                continue
            h, rows = read(os.path.join(d, 'DISK.tsv'))
            if h is None:
                try:
                    used += int(r.get('writes_mb', '0'))
                except ValueError:
                    pass
                continue
            for x in [h] + rows:
                if x and x[0] == 'du_mb_W' and len(x) > 1 and x[1].isdigit():
                    used += int(x[1])
            for p in glob.glob(os.path.join(d, '*', 'STORE_PLACES.tsv')):
                for l in open(p):
                    x = l.rstrip('\n').split('\t')
                    if x[0] == 'du_mb' and len(x) > 1 and x[1].isdigit():
                        used += int(x[1])
        return used

    def a17(self):
        f, w = [], []
        last = {}
        for r in self.rows('DECISIONS'):
            for j in (r.get('grade_job'), r.get('entry_job')):
                last[j] = max(filter(None, [last.get(j), ts(r.get('utc', ''))]), default=None)
        for r in self.rows('POSTMORTEMS'):
            j = r.get('job'); last[j] = max(filter(None, [last.get(j), ts(r.get('utc', ''))]), default=None)
        for r in self.rows('RUNS'):
            if r.get('kind') not in ('COUNT', 'GRADE', 'ENTRY', 'MONTH'):
                continue
            j = r.get('receipts_rel', '').replace('receipts/', '', 1); d = os.path.join(self.run, 'receipts', j)
            cleaned = os.path.exists(os.path.join(d, 'CLEANED_BY.txt'))
            if cleaned and r.get('kind') == 'GRADE':
                h, rows = read(os.path.join(d, 'FIRES.tsv'))
                for x in ([h] + rows if h else []):
                    if len(x) == 4:
                        p = os.path.join(d, '%s_FIRES_V1_LIST.tsv' % x[0])
                        if not os.path.isfile(p) or sha16(p) != x[2]:
                            f.append('%s cleaned but %s fire list not kept on dev' % (j, x[0]))
            elif not cleaned and last.get(j) and (self.now - last[j]).total_seconds() > 3600:
                w.append('%s decided or read %.0f min ago and not cleaned' % (j, (self.now - last[j]).total_seconds() / 60.0))
        u = self.used_mb()
        if u > 10000:
            f.append('the run holds %d MB of uncleaned scratch (budget 10,000)' % u)
        self.add('A17', 'CLEAN', f, w)

    def left_mb(self):
        mb = 0
        for p in glob.glob(os.path.join(self.run, 'receipts', '*_CLEAN_*', 'CLEANED.tsv')):
            h, rows = read(p)
            for x in rows:
                r = dict(zip(h, x))
                if r.get('result', '').startswith('LEFT') and r.get('bytes', '').isdigit():
                    mb += int(r['bytes']) // 1048576
        return mb

    def counts(self):
        claimed = len(glob.glob(os.path.join(CFG['H'], 'runs', 'IDEAS_CLAIMED', '%s_*.txt' % self.runtag)))
        kinds = {}
        for r in self.rows('RUNS'):
            kinds[r.get('kind')] = kinds.get(r.get('kind'), 0) + 1
        last = {}
        for r in self.rows('DECISIONS'):
            last[(r.get('idea'), r.get('V'))] = r.get('state')
        states = {}
        for s in last.values():
            states[s] = states.get(s, 0) + 1
        return 'ideas claimed %d; variants registered %d; jobs %s; decisions (latest per variant) %s; problems %d; learnings proposed %d; uncleaned scratch %d MB; left for DSK (protected store places) %d MB' % (
            claimed, len({(r.get('idea'), r.get('V')) for r in self.rows('VARIANTS')}),
            ', '.join('%s %d' % kv for kv in sorted(kinds.items())) or '0', ', '.join('%s %d' % kv for kv in sorted(states.items())) or '0',
            len(self.rows('PROBLEMS')), len(self.rows('LEARNINGS_PROPOSED')), self.used_mb(), self.left_mb())

    def runall(self):
        for f in (self.a1, self.a2, self.a3_a4_a5, self.a6, self.a7_a8_a13, self.a9_a10, self.a11, self.a12, self.a14_a15, self.a16, self.a17):
            try:
                f()
            except Exception as e:
                self.add('A?', f.__name__, ['audit step failed: %s: %s' % (type(e).__name__, e)])
        order = {('A%d' % i): i for i in range(1, 18)}
        self.res.sort(key=lambda x: order.get(x[0], 99))
        lines = ['AUDIT %s (audit_run_v3.py, %s). TEST, NOT REVIEWED.' % (self.runtag, self.now.strftime('%Y-%m-%dT%H:%M:%SZ'))]
        for cid, name, st, fails, warns, nf, nw in self.res:
            lines.append('%-4s %-11s %s%s' % (cid, name, st, '' if st == 'PASS' else ' (%d)' % (nf or nw)))
            lines += ['       - %s' % x for x in (fails or warns)]
        lines.append('COUNTS ' + self.counts())
        n = {s: sum(1 for x in self.res if x[2] == s) for s in ('PASS', 'WARN', 'FAIL')}
        lines.append('SCORE %d PASS, %d WARN, %d FAIL' % (n['PASS'], n['WARN'], n['FAIL']))
        return lines, n['FAIL']


def main(argv):
    a = list(argv)
    write = '--write' in a
    a = [x for x in a if x != '--write']
    settings = None
    if '--settings' in a:
        i = a.index('--settings')
        settings = a[i + 1] if i + 1 < len(a) else None
        del a[i:i + 2]
    if len(a) != 1 or not RUNTAG.match(a[0]) or not settings:
        raise SystemExit('USAGE audit_run_v3.py --settings <settings file> RUN [--write]')
    try:
        configure(settings)
    except Refused as e:
        raise SystemExit('REFUSED: %s' % e)
    au = Audit(a[0])
    if not os.path.isdir(au.run):
        raise SystemExit('NO RUN FOLDER %s' % au.run)
    lines, nfail = au.runall()
    print('\n'.join(lines))
    if write:
        d = os.path.join(au.run, 'audit'); os.makedirs(d, exist_ok=True)
        p = os.path.join(d, 'AUDIT_%s.txt' % au.now.strftime('%Y%m%dT%H%M%SZ'))
        with open(p, 'x') as f:
            f.write('\n'.join(lines) + '\n')
        print('WRITTEN', p, sha16(p))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
