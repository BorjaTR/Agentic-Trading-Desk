#!/usr/bin/env python3
"""decide_v3.py (SCOUT, ALARM_V1_12, from decide_v2.py 05bd59978373c69c): the run budget is read from queue_job_v11.py, the current
queue (decide_v2 read queue_job_v5.py's text, a past edition; plan S1); its messages name queue_job_v11. Nothing else.
decide_v2.py (SCOUT for ALARM_DESIGN KIT_V5, 30 Oct 2026; edition 2 of decide_v1.py 7a127fe63e199eec; TEST, NOT REVIEWED). The decision
of one variant, from its job receipts only. Runs from the Alarm package on any machine; reads text receipts under the settings key
RESEARCH_ROOT (no market data, no scratch); writes one DECISIONS row with --write, nothing else.

  python3 -B <Alarm>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/decide_v3.py --settings <settings file> <RUN> <IDEA> <V> --grade <GRADE JOB>
             [--entry <ENTRY JOB> | --entry-too-big] [--write]

Edition 2 changes only where things are (the owner 30 Oct 2026 22:21 Berlin: "Let's make sure everything can run from the release folder";
CLEAN_RELEASE_V1 section 6). The rule, the checks, the printed lines, the DECISIONS row and the exit codes are decide_v1.py's:
  --settings <file>  required: this machine's settings file (<Alarm>/settings/SETTINGS_<MACHINE>.env), read by the package's own
                     _tools/settings_v1.py; the run is <RESEARCH_ROOT>/ALARM_DESIGN/runs/<RUN>
  the Alarm folder   settings_v1.alarm_root(this file); the register writer and the price-path reader run from inside it
                     (Agentic/tree/ALARM_DESIGN/runs/CLAUDE1_20261028/tools, pinned by sha16 as before); the run budget is read from
                     queue_job_v5.py next to this file (the owner 30 Oct 23:54 Berlin: past editions go to archive/)
  decide_v1.py found the dev tree and the scratch drive itself (_roots()); this edition names no machine path.

The rule (PROCESS_V7 step 8; the owner 29 Oct 2026 14:23 Berlin: "for now we keep them separate and report both"):
  INVALID            the grade or the hand-off of V did not finish with rc 0, a receipt is missing, or the hand-off's status is not OK
                     or its gate (the card equality check) is not PASS
  INSUFFICIENT       fewer than 3 counted months (30+ waves) on Sep-Dec: the study cannot be read; not a NO
  STOP               hand-off R1 missed (the LEAD +3 in at least 2 of every 3 counted months, at 15 m or 1 h)
  NEEDS MORE MONTHS  R1 passed, R2 missed (R2 = R1 and t of at least 3)
  PASS               R2 passed
  CLEAR (the price path: STRATEGY's markout, wait 0, 15 m or 1 h, Sep-Dec 95 pct range above 0 and both halves above 0) is
  reported next to the label for every variant with R1 and never changes it. The ENTRY job is required before a decision with R1.
  NO ENTRY          (--entry-too-big; round 3, 29 Oct 20:35Z, V6-40/V6-41) R1 passed but the variant's ENTRY job would declare more than the
                    run disk budget (300 MB per 1,000 fires, as queue_job_v5.py), so it can never run: the hand-off is recorded, the
                    variant is NOT decided (no CLEAR, no MONTH), and its GRADE job can be cleaned. Refused when the ENTRY fits.
Receipts read: receipts/<GRADE>/STAGES.tsv, HANDOFF/SUMMARY.tsv, HANDOFF/REAL_SEALED/REAL_RULES_<V>.tsv and REAL_<V>.tsv;
receipts/<ENTRY>/STAGES.tsv and <V>/MARKOUT/{CURVE.tsv, GATES.json, TABLE_W0.tsv} through read_stratentry_v1.read_version (pinned).
"""
import sys, os, re, json, math, hashlib, subprocess, importlib.util

RUN_TOOLS = ('Agentic', 'tree', 'ALARM_DESIGN', 'runs', 'CLAUDE1_20261028', 'tools')   # the run tools, inside the Alarm folder
CFG = {
    'H': None,     # <RESEARCH_ROOT>/ALARM_DESIGN; configure() fills H, REG and RSE from the settings file and the Alarm folder
    'REG': None, 'REG_SHA': 'c301c5977ecd6860',
    'RSE': None, 'RSE_SHA': 'f3c6dc8c110dd067',
    'RUN_BUDGET_MB': None,   # None: read from queue_job_v11.py next to this file (tests set a number)
}
NAME = re.compile(r'^[A-Z][A-Z0-9]{0,23}$')
RUNTAG = re.compile(r'^([A-Z][A-Z0-9]{0,11})_([0-9]{8})$')
RULE = 'PROCESS_V7 step 8; R2 and CLEAR kept separate, both reported (the owner 29 Oct 14:23 Berlin)'


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
    """CFG from the settings file (the run data under RESEARCH_ROOT) and the Alarm folder (the register writer, the price-path reader)"""
    S = settings_reader()
    try:
        alarm = S.alarm_root(__file__)
        research = S.get(settings, 'RESEARCH_ROOT')
    except S.Refused as e:
        raise Refused('SETTINGS: %s' % e)
    t1 = os.path.join(alarm, *RUN_TOOLS)
    CFG.update({'H': os.path.join(research, 'ALARM_DESIGN'), 'REG': os.path.join(t1, 'reg_append_v1.py'),
                'RSE': os.path.join(t1, 'read_stratentry_v1.py')})


def sha16(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def tsv(p):
    with open(p) as f:
        lines = [l.rstrip('\n') for l in f if l.strip() and not l.startswith('#')]
    if not lines:
        return []
    h = lines[0].split('\t')
    return [dict(zip(h, l.split('\t'))) for l in lines[1:]]


def stages(d):
    p = os.path.join(d, 'STAGES.tsv')
    if not os.path.isfile(p):
        raise Refused('NO RECEIPTS %s' % p)
    rows = tsv(p)
    if not any(r.get('stage') == 'end' for r in rows):
        raise Refused('JOB NOT FINISHED: no end line in %s' % p)
    return {r['stage']: r for r in rows}


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return float('nan')


def f2(x):
    return 'nan' if x != x else '%+.2f' % x


def load_rse():
    if sha16(CFG['RSE']) != CFG['RSE_SHA']:
        raise Refused('read_stratentry_v1.py CHANGED (want %s)' % CFG['RSE_SHA'])
    spec = importlib.util.spec_from_file_location('read_stratentry_v1', CFG['RSE'])
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def run_budget_mb():
    if CFG.get('RUN_BUDGET_MB'):
        return int(CFG['RUN_BUDGET_MB'])
    qp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'queue_job_v11.py')
    m = re.search(r"'RUN_BUDGET_MB':\s*([0-9]+)", open(qp).read()) if os.path.isfile(qp) else None
    return int(m.group(1)) if m else None


def entry_size(gd, v):
    """(fires, MB) the ENTRY job of V would declare: queue_job_v11.py's rule, 300 MB per 1,000 fires, at least 1,000"""
    fp = os.path.join(gd, 'FIRES.tsv')
    if os.path.isfile(fp):
        for l in open(fp):
            x = l.rstrip('\n').split('\t')
            if len(x) == 4 and x[0] == v and x[1].isdigit():
                n = int(x[1])
                return n, max(1000, 300 * int(math.ceil(n / 1000.0)))
    return None, None


def decide(run, idea, v, grade, entry, too_big=False):
    out = {'idea': idea, 'V': v, 'grade_job': grade, 'entry_job': entry or '-', 'label_rule': RULE}
    var = [r for r in tsv(os.path.join(run, 'registers', 'VARIANTS.tsv')) if r.get('idea') == idea and r.get('V') == v]
    if not var:
        raise Refused('%s OF %s NOT IN VARIANTS' % (v, idea))
    lean = var[-1].get('lean')
    if not re.match(r'^[0-9]+_GRADE_%s$' % idea, grade or ''):
        raise Refused('--grade MUST BE A GRADE JOB OF %s (e.g. 20263700_GRADE_%s)' % (idea, idea))
    gd = os.path.join(run, 'receipts', grade)
    st = stages(gd)
    src = []
    why = []
    g = st.get('grade_%s' % v)
    if g is None:
        raise Refused('%s WAS NOT GRADED IN %s' % (v, grade))
    if g.get('rc') != '0':
        why.append('grade rc %s' % g.get('rc'))
    h = st.get('handoff')
    if h is None or h.get('rc') != '0':
        why.append('hand-off rc %s' % (None if h is None else h.get('rc')))
    hd = os.path.join(gd, 'HANDOFF')
    sp = os.path.join(hd, 'SUMMARY.tsv')
    srow = None
    if os.path.isfile(sp):
        src.append('SUMMARY %s' % sha16(sp))
        rows = [r for r in tsv(sp) if r.get('V') == v]
        srow = rows[-1] if rows else None
    if srow is None:
        why.append('no SUMMARY row')
    else:
        if srow.get('status') != 'OK':
            why.append('status %s' % srow.get('status'))
        if srow.get('gate') != 'PASS':
            why.append('gate %s' % srow.get('gate'))
        out['waves'] = srow.get('waves', '')
    rp = os.path.join(hd, 'REAL_SEALED', 'REAL_RULES_%s.tsv' % v)
    ep = os.path.join(hd, 'REAL_SEALED', 'REAL_%s.tsv' % v)
    rules, real = {}, {}
    if os.path.isfile(rp):
        src.append('REAL_RULES %s' % sha16(rp))
        rules = {r['key']: r['value'] for r in tsv(rp) if 'key' in r}
    else:
        why.append('no REAL_RULES')
    if os.path.isfile(ep):
        src.append('REAL %s' % sha16(ep))
        real = {r['horizon']: r for r in tsv(ep) if 'horizon' in r}
    else:
        why.append('no REAL')
    out['r1'] = rules.get('R1', ''); out['r2'] = rules.get('R2', '')
    out['months_counted'] = rules.get('counted', ''); out['months_passing'] = rules.get('passing', '')
    for hz in ('15m', '1h'):
        r = real.get(hz, {})
        out['lead_%s' % hz] = f2(num(r.get('lead'))); out['t_%s' % hz] = f2(num(r.get('t')))
    out['gate_handoff'] = '' if srow is None else srow.get('gate', '')
    if why:
        out['state'] = 'INVALID'; out['note'] = '; '.join(why)
    elif int(num(rules.get('counted')) if rules.get('counted') else 0) < 3:
        out['state'] = 'INSUFFICIENT'; out['note'] = 'counted months %s of 4 (30+ waves each)' % rules.get('counted')
    elif rules.get('R1') != 'PASS':
        out['state'] = 'STOP'; out['note'] = 'R1 missed: passing %s of %s counted (need %s)' % (rules.get('passing'), rules.get('counted'), rules.get('need'))
    else:
        out['state'] = 'PASS' if rules.get('R2') == 'PASS' else 'NEEDS MORE MONTHS'
        out['note'] = 'R1 passed; R2 %s' % rules.get('R2')
    for k in ('clear', 'clear_at', 'price_gate', 'tough_15m', 'tough_1h', 'money_tt', 'money_rr'):
        out[k] = '-'
    if out['state'] in ('PASS', 'NEEDS MORE MONTHS') and not entry and too_big:
        n, mb = entry_size(gd, v)
        b = run_budget_mb()
        if n is None or b is None:
            raise Refused('%s: CANNOT SIZE ITS ENTRY (no FIRES.tsv row for it, or no run budget)' % v)
        if mb <= b:
            raise Refused('%s: ITS ENTRY FITS (%d MB for %d fires, budget %d MB): run it, then decide with --entry' % (v, mb, n, b))
        out['note'] = 'R1 %s, R2 %s in the hand-off (it would be %s); its ENTRY would declare %d MB for %d fires, over the %d MB run budget: not decided, no CLEAR, no MONTH (V6-40)' % (
            rules.get('R1'), rules.get('R2'), out['state'], mb, n, b)
        out['state'] = 'NO ENTRY'
    elif too_big:
        raise Refused('--entry-too-big IS ONLY FOR A VARIANT WITH R1 AND NO --entry')
    if out['state'] in ('PASS', 'NEEDS MORE MONTHS'):
        if not entry:
            raise Refused('%s HAS R1: run its ENTRY job first (queue_job_v11.py ... ENTRY ... --from-job %s), then decide with --entry' % (v, grade))
        if not re.match(r'^[0-9]+_ENTRY_%s$' % idea, entry):
            raise Refused('--entry MUST BE AN ENTRY JOB OF %s' % idea)
        ed = os.path.join(run, 'receipts', entry)
        es = stages(ed)
        mk = es.get('markout_%s' % v)
        if mk is None:
            raise Refused('%s WAS NOT IN ENTRY JOB %s' % (v, entry))
        rse = load_rse()
        rv = rse.read_version({'V': v, 'lean': lean, 'group': 'KEPT', 'handoff_sepdec': ''}, ed)
        out['clear'] = rv.get('clear', 'MISSING') if mk.get('rc') == '0' else 'MISSING (markout rc %s)' % mk.get('rc')
        out['clear_at'] = ','.join(rv.get('clear_hits') or []) or '-'
        out['price_gate'] = '%s (%d of %d)' % (rv.get('gate'), len(rv.get('gate_cells') or []), rv.get('gate_seen') or 0)
        for hz in ('ret_15m', 'ret_1h'):
            t = rv.get('tough_' + hz)
            out['tough_' + hz.replace('ret_', '')] = rse.fmt(t)
        out['money_tt'] = rse.fmt(rv.get('money_TT')); out['money_rr'] = rse.fmt(rv.get('money_RR'))
        for x in ('CURVE.tsv', 'TABLE_W0.tsv', 'GATES.json'):
            p = os.path.join(ed, v, 'MARKOUT', x)
            if os.path.isfile(p):
                src.append('%s %s' % (x, sha16(p)))
    out['sources'] = 'grade %s: %s | entry %s' % (grade, ', '.join(src), entry or '-')
    return out


COLS = ('idea', 'V', 'state', 'label_rule', 'r1', 'r2', 'months_counted', 'months_passing', 'waves', 'lead_15m', 't_15m', 'lead_1h', 't_1h',
        'gate_handoff', 'clear', 'clear_at', 'price_gate', 'tough_15m', 'tough_1h', 'money_tt', 'money_rr', 'grade_job', 'entry_job', 'sources', 'note')


def main(argv):
    a = list(argv)
    write = '--write' in a
    too_big = '--entry-too-big' in a
    a = [x for x in a if x not in ('--write', '--entry-too-big')]
    opts = {'--grade': None, '--entry': None, '--settings': None}
    for k in list(opts):
        if k in a:
            i = a.index(k)
            if i + 1 >= len(a):
                raise Refused('%s NEEDS A VALUE' % k)
            opts[k] = a[i + 1]; del a[i:i + 2]
    if len(a) != 3 or not opts['--grade']:
        raise Refused('USAGE decide_v3.py --settings <settings file> RUN IDEA V --grade <GRADE JOB> [--entry <ENTRY JOB> | --entry-too-big] [--write]')
    if not opts['--settings']:
        raise Refused('--settings <file> IS REQUIRED: the settings file of this machine (<Alarm>/settings/SETTINGS_<MACHINE>.env)')
    if too_big and opts['--entry']:
        raise Refused('--entry AND --entry-too-big TOGETHER: one or the other')
    runtag, idea, v = a
    if not RUNTAG.match(runtag) or not NAME.match(idea) or not NAME.match(v):
        raise Refused('BAD RUN, IDEA OR VARIANT NAME')
    configure(opts['--settings'])
    run = os.path.join(CFG['H'], 'runs', runtag)
    d = decide(run, idea, v, opts['--grade'], opts['--entry'], too_big)
    print('DECISION %s %s: %s | R1 %s R2 %s | LEAD 15m %s (t %s) 1h %s (t %s) | waves %s, months counted %s passing %s | CLEAR %s %s | price gate %s | TOUGH 15m %s 1h %s | money TT %s RR %s | %s' % (
        idea, v, d['state'], d['r1'] or '-', d['r2'] or '-', d['lead_15m'], d['t_15m'], d['lead_1h'], d['t_1h'], d.get('waves', '-'),
        d['months_counted'] or '-', d['months_passing'] or '-', d['clear'], d['clear_at'], d['price_gate'], d['tough_15m'], d['tough_1h'],
        d['money_tt'], d['money_rr'], d.get('note', '')))
    print('SOURCES', d['sources'])
    if write:
        if sha16(CFG['REG']) != CFG['REG_SHA']:
            raise Refused('reg_append_v1.py CHANGED')
        prev = [r for r in tsv(os.path.join(run, 'registers', 'DECISIONS.tsv')) if r.get('idea') == idea and r.get('V') == v]
        if prev and prev[-1].get('state') == d['state'] and prev[-1].get('grade_job') == d['grade_job'] and prev[-1].get('entry_job') == d['entry_job']:
            raise Refused('THIS DECISION IS ALREADY IN DECISIONS (%s)' % prev[-1].get('utc'))
        row = {k: str(d.get(k, '')) for k in COLS}
        r = subprocess.run([sys.executable, '-B', CFG['REG'], run, 'DECISIONS', '-'], input=json.dumps(row), capture_output=True, text=True)
        if r.returncode or 'DECISIONS' not in r.stdout:
            raise Refused('DECISIONS ROW FAILED rc %d %s %s' % (r.returncode, r.stdout.strip(), r.stderr.strip()))
        print('WRITTEN', r.stdout.strip())
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except Refused as e:
        print('REFUSED: %s' % e, file=sys.stderr)
        sys.exit(2)
