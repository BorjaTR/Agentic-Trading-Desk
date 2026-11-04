#!/usr/bin/env python3
"""test_feedgate_rel1.py (SCOUT K12, 31 Oct 2026; TEST, NOT REVIEWED): tests of the feed-gate editions of GRADE's and MONTH's Outcomes
step (event_outcomes_rel1.py, run_parallel_rel1.py, event_outcomes_aw1_rel1.py, RELEASE_event_outcomes_V3_REL1.json and _AW1_REL1.json,
chains v2_0_3 and v2_2_3, JOB_GRADE_V8, JOB_MONTH_V8, queue_job_v6.py), all in this Alarm folder:
  C1 the contract: feedgate_rel1_contract.build(<this Alarm folder>) remakes the ten files from the old ones (listed, counted text
     replacements, each old file checked by its sha16 first) and each one equals the file here byte for byte;
  B1 no gate call of the old kind is left: the three call sites of each Outcomes edition call its own gate_wait, run_lab calls
     feed_gate_wait, and the old research-days expression is only inside research_store;
  B2 the helpers, executed from each edition's text with a recording jobgate (never a real gate): FEED_GATE unset is refused
     NO_FEED_GATE (no call); empty is no gate (0, no call, nothing read); a file is waited on by that path, never the built-in GATE;
     research_store is RESEARCH_STORE when it is set and not empty, else research_days beside the lab days;
  B3 the wiring: RUN_PARALLEL is run_parallel_rel1.py, whose EO is event_outcomes_rel1.py; RELEASE names each edition's own record;
  B4 the release records: V3_REL1 is V3_CANDIDATE with the two editions in place of the two old files (every other file, release and
     the runtime the same), AW1_REL1 is AW1 with aw1_rel1 in place of aw1 and V3_REL1 in place of V3_CANDIDATE; each pin is the sha16
     of the file here;
  B5 the chains run the editions, check them by sha16, export FEED_GATE and RESEARCH_STORE and refuse a missing or relative
     RESEARCH_STORE before any step (run with bash, here, until that refusal: no data is read);
  B6 JOB_GRADE_V8 and JOB_MONTH_V8 pin the new chains by sha16, give them FEED_GATE and RESEARCH_STORE, and hold no refused word;
  B7 queue_job_v6.py names the V8 templates by sha16 (COUNT, CLEAN, ENTRY unchanged) and needs RESEARCH_STORE in the job settings.
Then planted bugs (mutants of the texts in memory): each must make a behaviour check fail with the sha16 pins left out, so a bug is
caught by what it breaks, not by its changed bytes. Reads only this Alarm folder; writes only a temp folder (removed); no market data.
  python3 -B <Alarm>/Agentic/tree/ALARM_DESIGN/KIT_V5/tests/test_feedgate_rel1.py"""
import ast, hashlib, importlib.util, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ALARM = HERE
while not os.path.isfile(os.path.join(ALARM, '_tools', 'settings_v1.py')):
    if os.path.dirname(ALARM) == ALARM:
        raise SystemExit('REFUSED: not inside an Alarm folder: %s' % HERE)
    ALARM = os.path.dirname(ALARM)
sp = importlib.util.spec_from_file_location('feedgate_rel1_contract', os.path.join(HERE, 'feedgate_rel1_contract.py'))
C = importlib.util.module_from_spec(sp); sp.loader.exec_module(C)
NEW = (C.EO_NEW, C.RP_NEW, C.AW_NEW, C.V3_NEW, C.AR_NEW, C.C_NEW, C.M_NEW, C.G8, C.M8, C.Q6)
WORDS = re.compile(r'(?<![A-Za-z0-9_])(rm|dd|git|sudo|sleep|timeout|alarm)(?![A-Za-z0-9_])')
OLD_RESEARCH = "os.path.join(os.path.dirname(os.path.abspath(lab_root)), 'research_days')"


def s16(t):
    return hashlib.sha256(t.encode('utf-8')).hexdigest()[:16]


def rd(rel):
    return open(os.path.join(ALARM, rel), encoding='utf-8').read()


class JG:
    """a recording jobgate: the built-in GATE is a name only; gate_wait records the gate it was given (DEFAULT when none)"""
    GATE = '/the/built/in/team/BACKFILL_GATE.txt'

    def __init__(self):
        self.calls = []

    def gate_wait(self, gate=None, log=None, **k):
        self.calls.append(gate if gate is not None else 'DEFAULT ' + self.GATE); return 5

    def state(self, gate=None):
        self.calls.append(gate if gate is not None else 'DEFAULT ' + self.GATE); return 'RUN'


def block(text, start, last_def):
    """the source from `start` to the end of the function `last_def` (the edition's class and helpers)"""
    a = text.index(start); b = text.index(last_def, a); c = text.index('\n\n\n', b)
    return text[a:c]


class Env:
    def __init__(self, **kv):
        self.kv = kv

    def __enter__(self):
        self.old = {k: os.environ.get(k) for k in self.kv}
        for k, v in self.kv.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def __exit__(self, *a):
        for k, v in self.old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def gate_cases(call, refusal):
    """(failures) of one gate entry point: call(jobgate) under FEED_GATE unset, empty and a file"""
    f = []
    jg = JG()
    with Env(FEED_GATE=None):
        try:
            call(jg); f.append('FEED_GATE unset was not refused')
        except refusal as e:
            if getattr(e, 'code', None) != 'NO_FEED_GATE':
                f.append('FEED_GATE unset refused as %r, not NO_FEED_GATE' % getattr(e, 'code', None))
        except Exception as e:
            f.append('FEED_GATE unset raised %s' % type(e).__name__)
    if jg.calls:
        f.append('FEED_GATE unset still called the gate: %s' % jg.calls)
    jg = JG()
    with Env(FEED_GATE=''):
        r = call(jg)
    if r != 0 or jg.calls:
        f.append('FEED_GATE empty: returned %r, gate calls %s (want 0 and none)' % (r, jg.calls))
    jg = JG()
    with Env(FEED_GATE='/a/copy/GATE.txt'):
        r = call(jg)
    if jg.calls != ['/a/copy/GATE.txt'] or r != 5:
        f.append('FEED_GATE a file: gate calls %s, returned %r (want the file once)' % (jg.calls, r))
    return f


def check_outcomes(name, text, release):
    f = []
    sites = re.findall(r'(?<![.\w])gate_wait\(log=log\)', text)
    if len(sites) != 3 or 'jobgate.gate_wait(log=' in text:
        f.append('%s B1: %d call sites of its gate_wait (want 3), an old jobgate.gate_wait(log=..) call %s' % (name, len(sites), 'left' if 'jobgate.gate_wait(log=' in text else 'none'))
    if len(re.findall(r'research_root or research_store\(lab_root\)', text)) != 2 or text.count(OLD_RESEARCH) != 1:
        f.append('%s B1: research_store at %d places (want 2), the old expression %d times (want 1, inside research_store)' % (
            name, len(re.findall(r'research_root or research_store\(lab_root\)', text)), text.count(OLD_RESEARCH)))
    try:
        src = block(text, 'class Refused(PermissionError):', '\ndef research_store(lab_root):')
        ns = {'os': os}
        exec(compile(src, name, 'exec'), ns)
    except Exception as e:
        return f + ['%s B2: its helpers could not be read: %s: %s' % (name, type(e).__name__, e)]
    def call(jg):
        ns['jobgate'] = jg; return ns['gate_wait'](log=lambda s: None)
    f += ['%s B2: %s' % (name, x) for x in gate_cases(call, ns['Refused'])]
    for env, want in ((None, '/x/research_days'), ('/r/store', '/r/store'), ('', '/x/research_days')):
        with Env(RESEARCH_STORE=env):
            got = ns['research_store']('/x/lab_days')
        if got != want:
            f.append('%s B2: research_store with RESEARCH_STORE=%r gave %r (want %r)' % (name, env, got, want))
    m = re.search(r"^RELEASE = os\.path\.join\(HERE, '([^']+)'\)", text, re.M)
    if not m or m.group(1) != release:
        f.append('%s B3: RELEASE is %s (want %s)' % (name, m.group(1) if m else 'missing', release))
    m = re.search(r"^RUN_PARALLEL = os\.path\.join\(TOOLS, 'event_profile', '([^']+)'\)", text, re.M)
    if not m or m.group(1) != 'run_parallel_rel1.py':
        f.append('%s B3: RUN_PARALLEL is %s (want run_parallel_rel1.py)' % (name, m.group(1) if m else 'missing'))
    return f


def check_launcher(text):
    f = []
    m = re.search(r"^EO = os\.path\.join\(HERE, '\.\.', 'event_outcomes', '([^']+)'\)", text, re.M)
    if not m or m.group(1) != 'event_outcomes_rel1.py':
        f.append('run_parallel_rel1 B3: EO is %s (want event_outcomes_rel1.py)' % (m.group(1) if m else 'missing'))
    if 'jobgate.gate_wait(log=' in text or 'waited = feed_gate_wait(jobgate, log=' not in text:
        f.append('run_parallel_rel1 B1: run_lab does not wait through feed_gate_wait')
    try:
        src = block(text, 'class Refusal(Exception):', '\ndef feed_gate_wait(jobgate, log):')
        ns = {'os': os}
        exec(compile(src, 'run_parallel_rel1', 'exec'), ns)
    except Exception as e:
        return f + ['run_parallel_rel1 B2: its helper could not be read: %s: %s' % (type(e).__name__, e)]
    f += ['run_parallel_rel1 B2: %s' % x for x in gate_cases(lambda jg: ns['feed_gate_wait'](jg, lambda s: None), ns['Refusal'])]
    return f


def check_records(t, pins):
    f = []
    old3, new3 = json.loads(rd(C.V3_OLD)), json.loads(t[C.V3_NEW])
    o, n = C.tree_rel(C.EO_OLD), C.tree_rel(C.EO_NEW); po, pn = C.tree_rel(C.RP_OLD), C.tree_rel(C.RP_NEW)
    want = sorted([k for k in old3['files'] if k not in (o, po)] + [n, pn])
    if sorted(new3['files']) != want:
        f.append('B4 V3_REL1 files %s (want V3_CANDIDATE with the editions in place of the old)' % sorted(set(new3['files']) ^ set(want)))
    if any(new3['files'].get(k) != v for k, v in old3['files'].items() if k not in (o, po)):
        f.append('B4 V3_REL1 changes a file pin of V3_CANDIDATE')
    for k in ('releases', 'runtime'):
        if new3.get(k) != old3.get(k):
            f.append('B4 V3_REL1 %s differ from V3_CANDIDATE' % k)
    oa, na = json.loads(rd(C.AR_OLD)), json.loads(t[C.AR_NEW])
    a_o, a_n = C.tree_rel(C.AW_OLD), C.tree_rel(C.AW_NEW)
    if sorted(na['files']) != sorted([k for k in oa['files'] if k != a_o] + [a_n]) or any(na['files'].get(k) != v for k, v in oa['files'].items() if k != a_o):
        f.append('B4 AW1_REL1 files differ from AW1 with aw1_rel1 in place of aw1')
    if sorted(na.get('releases', {})) != [C.tree_rel(C.V3_NEW)]:
        f.append('B4 AW1_REL1 releases %s (want V3_REL1 only)' % sorted(na.get('releases', {})))
    if pins:
        for k, p in ((n, C.EO_NEW), (pn, C.RP_NEW)):
            if new3['files'].get(k, {}).get('sha16') != s16(t[p]):
                f.append('B4 V3_REL1 pins %s %s, the file is %s' % (k, new3['files'].get(k, {}).get('sha16'), s16(t[p])))
        if na['files'].get(a_n, {}).get('sha16') != s16(t[C.AW_NEW]):
            f.append('B4 AW1_REL1 pins aw1_rel1 %s, the file is %s' % (na['files'].get(a_n, {}).get('sha16'), s16(t[C.AW_NEW])))
        if na.get('releases', {}).get(C.tree_rel(C.V3_NEW)) != s16(t[C.V3_NEW]):
            f.append('B4 AW1_REL1 names V3_REL1 %s, the file is %s' % (na.get('releases', {}).get(C.tree_rel(C.V3_NEW)), s16(t[C.V3_NEW])))
    return f


def shavar(text, name):
    m = re.search(r'\b%s=([0-9a-f]{16})\b' % name, text)
    return m.group(1) if m else None


def check_chains(t, pins):
    f = []
    g = t[C.C_NEW]
    for s in ('EO=$T/event_outcomes/event_outcomes_rel1.py;', 'RP=$T/event_profile/run_parallel_rel1.py;',
              'REL=$T/event_outcomes/RELEASE_event_outcomes_V3_REL1.json', 'ckf $EO $EO_SHA; ckf $RP $RP_SHA; ckf $REL $REL_SHA',
              '$PY -B $EO run 1 ', 'export FEED_GATE RESEARCH_STORE', 'NO_RESEARCH_STORE', '"$RESEARCH_STORE" >> "$W/INPUTS_${V}.txt"'):
        if s not in g:
            f.append('B5 chain v2_0_3 lacks %r' % s)
    if 'event_outcomes/event_outcomes.py run' in g:
        f.append('B5 chain v2_0_3 still runs event_outcomes.py')
    m = t[C.M_NEW]
    for s in ('EO=$AP/event_outcomes_aw1_rel1.py;', 'ckf event_outcomes_aw1_rel1.py $EO_SHA; ckf RELEASE_event_outcomes_AW1_REL1.json $REL_SHA',
              '$PY -B $EO run 0 ', 'export FEED_GATE RESEARCH_STORE', 'NO_RESEARCH_STORE', '"$AP/RELEASE_event_outcomes_AW1_REL1.json"',
              "printf 'research\\t%s\\n' \"$RESEARCH_STORE\""):
        if s not in m:
            f.append('B5 chain v2_2_3 lacks %r' % s)
    if 'EO=$AP/event_outcomes_aw1.py;' in m:
        f.append('B5 chain v2_2_3 still runs event_outcomes_aw1.py')
    for text, name in ((g, 'v2_0_3'), (m, 'v2_2_3')):
        i, j = text.find('NO_RESEARCH_STORE'), text.find('export FEED_GATE RESEARCH_STORE')
        k = text.find('mkdir -p "$W"')
        if not (0 <= i < k and 0 <= j < k):
            f.append('B5 chain %s: the RESEARCH_STORE check or the export is not before its work folder is made' % name)
    if pins:
        for text, name, var, p in ((g, 'v2_0_3', 'EO_SHA', C.EO_NEW), (g, 'v2_0_3', 'RP_SHA', C.RP_NEW), (g, 'v2_0_3', 'REL_SHA', C.V3_NEW),
                                   (m, 'v2_2_3', 'EO_SHA', C.AW_NEW), (m, 'v2_2_3', 'REL_SHA', C.AR_NEW)):
            if shavar(text, var) != s16(t[p]):
                f.append('B5 chain %s %s=%s, the file is %s' % (name, var, shavar(text, var), s16(t[p])))
    return f


def run_chain_refusals():
    """B5 for real, on the chain files here: RESEARCH_STORE missing, then relative: the chain must stop with NO_RESEARCH_STORE (exit 2)
    before its first step (every variable it checks first is given, and a definition file that holds no definition)"""
    f = []
    tmp = tempfile.mkdtemp(prefix='k12_feedgate_')
    try:
        with open(os.path.join(tmp, 'DEF.json'), 'x') as fh:          # the chains check that the definition exists before anything else
            fh.write('{}\n')
        for rel in (C.C_NEW, C.M_NEW):
            for store in (None, 'relative/research_days'):
                env = dict(os.environ, AL=ALARM, PY=sys.executable, LAB_DAYS=os.path.join(tmp, 'lab_days'), FEED_GATE='')
                env.pop('RESEARCH_STORE', None)
                if store is not None:
                    env['RESEARCH_STORE'] = store
                r = subprocess.run(['bash', os.path.join(ALARM, rel), 'PB0', os.path.join(tmp, 'DEF.json'), os.path.join(tmp, 'W_' + os.path.basename(rel))],
                                   capture_output=True, text=True, env=env, stdin=subprocess.DEVNULL, timeout=60)
                out = (r.stdout + r.stderr).strip().splitlines()
                if r.returncode != 2 or not out or not out[-1].startswith('NO_RESEARCH_STORE'):
                    f.append('B5 run %s with RESEARCH_STORE=%r: exit %d, last line %r (want exit 2 NO_RESEARCH_STORE)' % (
                        os.path.basename(rel), store, r.returncode, out[-1][:120] if out else ''))
                if os.path.exists(os.path.join(tmp, 'W_' + os.path.basename(rel))):
                    f.append('B5 run %s made its work folder before refusing' % os.path.basename(rel))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return f


def check_templates(t, pins):
    f = []
    for p, chain, line, var in ((C.G8, C.C_NEW, 'FEED_GATE=@@FEED_GATE@@ RESEARCH_STORE=@@RESEARCH_STORE@@ LEAN=$L bash $CH/alarm_grade_chain_v2_0_3_to20251231.sh ', '$CH'),
                                (C.M8, C.M_NEW, 'FEED_GATE=@@FEED_GATE@@ RESEARCH_STORE=@@RESEARCH_STORE@@ PARTS=26 LEAN=$L bash $MP/alarm_grade_chain_v2_2_3_to20260430.sh ', '$MP')):
        text = t[p]; name = os.path.basename(p); cb = os.path.basename(chain)
        if line not in text:
            f.append('B6 %s does not give the chain FEED_GATE and RESEARCH_STORE' % name)
        m = re.search(r'ck \%s/%s ([0-9a-f]{16})' % (var, re.escape(cb)), text)
        if not m:
            f.append('B6 %s does not pin %s' % (name, cb))
        elif pins and m.group(1) != s16(t[chain]):
            f.append('B6 %s pins %s %s, the file is %s' % (name, cb, m.group(1), s16(t[chain])))
        w = WORDS.search(text)
        if w:
            f.append('B6 %s holds the refused word %r' % (name, w.group(0)))
    return f


def check_queue(t, pins):
    f = []
    tree = ast.parse(t[C.Q6]); val = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id in (
                'TEMPLATE_SHA', 'TEMPLATE_NAME', 'JOB_NEED', 'PATHS'):
            val[node.targets[0].id] = ast.literal_eval(node.value)
    old = {}
    for node in ast.parse(rd(C.Q5)).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id in ('TEMPLATE_SHA', 'TEMPLATE_NAME'):
            old[node.targets[0].id] = ast.literal_eval(node.value)
    name = val.get('TEMPLATE_NAME', {}); sha = val.get('TEMPLATE_SHA', {})
    if name.get('GRADE') != 'JOB_GRADE_V8.job.sh.txt' or name.get('MONTH') != 'JOB_MONTH_V8.job.sh.txt':
        f.append('B7 queue_job_v6 names %s and %s (want the V8 templates)' % (name.get('GRADE'), name.get('MONTH')))
    for k in ('COUNT', 'CLEAN', 'ENTRY'):
        if name.get(k) != old['TEMPLATE_NAME'].get(k) or sha.get(k) != old['TEMPLATE_SHA'].get(k):
            f.append('B7 queue_job_v6 changes %s' % k)
    if 'RESEARCH_STORE' not in val.get('JOB_NEED', ()) or 'RESEARCH_STORE' not in val.get('PATHS', ()):
        f.append('B7 queue_job_v6 does not need RESEARCH_STORE in the job settings and fill @@RESEARCH_STORE@@')
    if pins:
        for k, p in (('GRADE', C.G8), ('MONTH', C.M8)):
            if sha.get(k) != s16(t[p]):
                f.append('B7 queue_job_v6 TEMPLATE_SHA %s %s, the file is %s' % (k, sha.get(k), s16(t[p])))
    return f


def checks(t, pins=True):
    return (check_outcomes('event_outcomes_rel1', t[C.EO_NEW], 'RELEASE_event_outcomes_V3_REL1.json') +
            check_outcomes('event_outcomes_aw1_rel1', t[C.AW_NEW], 'RELEASE_event_outcomes_AW1_REL1.json') +
            check_launcher(t[C.RP_NEW]) + check_records(t, pins) + check_chains(t, pins) + check_templates(t, pins) + check_queue(t, pins))


MUTANTS = (
    ('one Outcomes call site back to the built-in gate', C.EO_NEW, '        gate_wait(log=log)\n', '        jobgate.gate_wait(log=log)\n'),
    ('feed_gate falls back to the built-in GATE when FEED_GATE is unset', C.EO_NEW,
     "    if 'FEED_GATE' not in os.environ:\n        raise Refused('NO_FEED_GATE',", "    if False:\n        raise Refused('NO_FEED_GATE',"),
    ('an empty FEED_GATE still waits on the built-in GATE', C.EO_NEW, 'return jobgate.gate_wait(gate=g, log=log) if g else 0',
     'return jobgate.gate_wait(gate=g, log=log) if g else jobgate.gate_wait(log=log)'),
    ('a gate file is ignored for the built-in GATE', C.AW_NEW, 'return jobgate.gate_wait(gate=g, log=log) if g else 0',
     'return jobgate.gate_wait(log=log) if g else 0'),
    ('research_store ignores RESEARCH_STORE', C.EO_NEW, "return os.environ.get('RESEARCH_STORE') or ", 'return '),
    ('aw1 keeps one old research-days expression', C.AW_NEW, '    research_root = research_root or research_store(lab_root)\n',
     "    research_root = research_root or " + OLD_RESEARCH + "\n"),
    ('RUN_PARALLEL back to run_parallel.py', C.EO_NEW, "'event_profile', 'run_parallel_rel1.py')", "'event_profile', 'run_parallel.py')"),
    ('the workers back to event_outcomes.py', C.RP_NEW, "'event_outcomes', 'event_outcomes_rel1.py')", "'event_outcomes', 'event_outcomes.py')"),
    ("run_lab's gate back to the built-in GATE", C.RP_NEW, 'waited = feed_gate_wait(jobgate, log=', 'waited = jobgate.gate_wait(log='),
    ('feed_gate_wait does not refuse an unset FEED_GATE', C.RP_NEW, "    if 'FEED_GATE' not in os.environ:\n        raise Refusal(",
     "    if 'FEED_GATE' not in os.environ:\n        return 0\n        raise Refusal("),
    ('RELEASE back to V3_CANDIDATE', C.EO_NEW, "'RELEASE_event_outcomes_V3_REL1.json')", "'RELEASE_event_outcomes_V3_CANDIDATE.json')"),
    ('V3_REL1 pins the old event_outcomes.py', C.V3_NEW, '"team/RESEARCH/tools/event_outcomes/event_outcomes_rel1.py"',
     '"team/RESEARCH/tools/event_outcomes/event_outcomes.py"'),
    ('AW1_REL1 still names V3_CANDIDATE', C.AR_NEW, '"team/RESEARCH/tools/event_outcomes/RELEASE_event_outcomes_V3_REL1.json":',
     '"team/RESEARCH/tools/event_outcomes/RELEASE_event_outcomes_V3_CANDIDATE.json":'),
    ('chain v2_0_3 still runs event_outcomes.py', C.C_NEW, '$PY -B $EO run 1 ', '$PY -B $T/event_outcomes/event_outcomes.py run 1 '),
    ('chain v2_0_3 does not export the gate and the store', C.C_NEW, 'export FEED_GATE RESEARCH_STORE\n', '\n'),
    ('chain v2_2_3 still runs event_outcomes_aw1.py', C.M_NEW, 'EO=$AP/event_outcomes_aw1_rel1.py;', 'EO=$AP/event_outcomes_aw1.py;'),
    ('JOB_GRADE_V8 does not give RESEARCH_STORE', C.G8, 'RESEARCH_STORE=@@RESEARCH_STORE@@ LEAN=$L', 'LEAN=$L'),
    ('JOB_MONTH_V8 runs chain v2_2_2', C.M8, 'bash $MP/alarm_grade_chain_v2_2_3_to20260430.sh', 'bash $MP/alarm_grade_chain_v2_2_2_to20260430.sh'),
    ('queue_job_v6 does not fill RESEARCH_STORE', C.Q6, ", 'FEED_GATE', 'RESEARCH_STORE')", ", 'FEED_GATE')"),
    ('queue_job_v6 still names JOB_GRADE_V7', C.Q6, "'GRADE': 'JOB_GRADE_V8.job.sh.txt'", "'GRADE': 'JOB_GRADE_V7.job.sh.txt'"),
)


def main():
    out = []
    t = {p: rd(p) for p in NEW}
    made = C.build(ALARM)
    c1 = [p for p in NEW if made.get(p) != t[p]]
    out.append(('C1 the contract remakes the ten files byte for byte', not c1, ', '.join(c1) or '10 of 10 equal'))
    b = checks(t)
    out.append(('B1-B7 behaviour of the files here', not b, '; '.join(b) or 'every check passed'))
    r = run_chain_refusals()
    out.append(('B5 the chains refuse a missing or relative RESEARCH_STORE before any step (bash, here)', not r, '; '.join(r) or '4 of 4 refused'))
    killed = 0
    for name, p, a, z in MUTANTS:
        if t[p].count(a) < 1:
            out.append(('MUTANT %s' % name, False, 'its text is not in %s' % p)); continue
        m = dict(t); m[p] = t[p].replace(a, z, 1)
        f = checks(m, pins=False)
        killed += bool(f)
        out.append(('MUTANT %s' % name, bool(f), (f[0][:160] if f else 'NOT CAUGHT')))
    for name, ok, why in out:
        print('%s  %s: %s' % ('PASS' if ok else 'FAIL', name, why))
    bad = [n for n, ok, _ in out if not ok]
    print('FEEDGATE TESTS %d PASS %d FAIL; MUTANTS %d of %d killed' % (len(out) - len(bad), len(bad), killed, len(MUTANTS)))
    return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main())
