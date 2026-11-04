#!/usr/bin/env python3
"""decide_forward_v3.py (SCOUT, ALARM_V1_12, from decide_forward_v2.py dfc073289b10a31e): a month_read line's "gap na"
reads na (v2's lazy regex skipped it and took the next "gap <number>" on the line, the other side's; REV2 REVIEW_ARCH_V1.md F1, plan F2).
Nothing else.
decide_forward_v2.py (SCOUT for ALARM_DESIGN KIT_V5, 30 Oct 2026; edition 2 of decide_forward_v1.py bee5a79a5546b7cd; TEST, NOT REVIEWED).
The decision of a FORWARD-ONLY variant from its MONTH job receipts only. the owner 29 Oct 22:02 Berlin approved the route: when a STOP showed
the OTHER side winning, that side is sealed as a new variant (same definition, other lean, VARIANTS reason 'FORWARD ONLY OF <V0>'), never
graded on Sep-Dec again, and tested on Jan-Apr only (queue_job_v5.py MONTH --forward-only). Writes one DECISIONS row with --write, nothing
else.

  python3 -B <Alarm>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/decide_forward_v3.py --settings <settings file> <RUN> <IDEA> <V> --month <MONTH JOB>
             [--write]

Edition 2 changes only where things are (the owner 30 Oct 2026 22:21 Berlin: "Let's make sure everything can run from the release folder";
CLEAN_RELEASE_V1 section 6). The rule, the checks, the printed lines, the DECISIONS row and the exit codes are decide_forward_v1.py's:
  --settings <file>  required: this machine's settings file (<Alarm>/settings/SETTINGS_<MACHINE>.env), read by the package's own
                     _tools/settings_v1.py; the run is <RESEARCH_ROOT>/ALARM_DESIGN/runs/<RUN>
  the Alarm folder   settings_v1.alarm_root(this file); the register writer runs from inside it
                     (Agentic/tree/ALARM_DESIGN/runs/CLAUDE1_20261028/tools/reg_append_v1.py, pinned by sha16 as before)
  decide_forward_v1.py found the dev tree itself (_roots()); this edition names no machine path.

The rule (the 'holds' bar the owner approved: 3 of 4 months):
  INVALID          the MONTH job did not run V, a month stage failed, or a month read is missing
  INSUFFICIENT     fewer than 3 of 2601-2604 could be read (month_read_v3 NO READ: under 30 waves)
  FORWARD PASS     month_read_v3 says HELD or STRONGER in 3 or more of the 4 months
  FORWARD STOP     otherwise
The Sep-Dec numbers of the parent are not used: that side was read after the grade, so they are no test.
"""
import sys, os, re, json, hashlib, subprocess, importlib.util

RUN_TOOLS = ('Agentic', 'tree', 'ALARM_DESIGN', 'runs', 'CLAUDE1_20261028', 'tools')   # the run tools, inside the Alarm folder
CFG = {'H': None, 'REG': None, 'REG_SHA': 'c301c5977ecd6860'}   # configure() fills H and REG
NAME = re.compile(r'^[A-Z][A-Z0-9]{0,23}$')
RUNTAG = re.compile(r'^([A-Z][A-Z0-9]{0,11})_([0-9]{8})$')
RULE = 'FORWARD ONLY (the owner 29 Oct 22:02 Berlin): month_read_v3 HELD or STRONGER in 3 or more of 2601-2604'
MONTHS = ('2601', '2602', '2603', '2604')
HOLDS = ('HELD', 'STRONGER')
COLS = ('idea', 'V', 'state', 'label_rule', 'r1', 'r2', 'months_counted', 'months_passing', 'waves', 'lead_15m', 't_15m', 'lead_1h', 't_1h',
        'gate_handoff', 'clear', 'clear_at', 'price_gate', 'tough_15m', 'tough_1h', 'money_tt', 'money_rr', 'grade_job', 'entry_job', 'sources', 'note')


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
    """CFG from the settings file (the run data under RESEARCH_ROOT) and the Alarm folder (the register writer)"""
    S = settings_reader()
    try:
        alarm = S.alarm_root(__file__)
        research = S.get(settings, 'RESEARCH_ROOT')
    except S.Refused as e:
        raise Refused('SETTINGS: %s' % e)
    CFG.update({'H': os.path.join(research, 'ALARM_DESIGN'), 'REG': os.path.join(alarm, *RUN_TOOLS, 'reg_append_v1.py')})


def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def tsv(p):
    if not os.path.isfile(p):
        return []
    with open(p) as f:
        lines = [l for l in f.read().splitlines() if l and not l.startswith('#')]
    if not lines:
        return []
    hdr = lines[0].split('\t')
    return [dict(zip(hdr, l.split('\t'))) for l in lines[1:]]


def latest(rows, **kw):
    x = [r for r in rows if all(r.get(k) == v for k, v in kw.items())]
    return x[-1] if x else None


def read_month(path):
    """(verdict, waves, gap15, gap1h) from a month_read_v3 file"""
    txt = open(path, errors='replace').read()
    v = re.findall(r'VERDICT\s+([A-Z][A-Z ]*[A-Z])', txt)
    w = re.search(r'waves\s+([0-9]+)', txt)
    g15 = re.search(r'15m [^\n]*?gap (na|[+-]?[0-9.]+)', txt)   # V1_12 F2
    g1h = re.search(r'1h [^\n]*?gap (na|[+-]?[0-9.]+)', txt)   # V1_12 F2
    return (v[-1].strip() if v else None, int(w.group(1)) if w else None,
            g15.group(1) if g15 else '-', g1h.group(1) if g1h else '-')


def decide(run, idea, v, month):
    var = tsv(os.path.join(run, 'registers', 'VARIANTS.tsv'))
    dec = tsv(os.path.join(run, 'registers', 'DECISIONS.tsv'))
    vr = latest(var, idea=idea, V=v)
    if vr is None:
        raise Refused('%s OF %s NOT IN VARIANTS' % (v, idea))
    m0 = re.match(r'^FORWARD ONLY OF ([A-Z][A-Z0-9]{0,23})(?![A-Z0-9])', vr.get('reason', ''))
    if not m0:
        raise Refused('%s IS NOT A FORWARD-ONLY VARIANT (VARIANTS reason must start "FORWARD ONLY OF <V0>")' % v)
    v0 = m0.group(1)
    d0 = latest(dec, idea=idea, V=v0)
    if d0 is None or d0.get('state') != 'STOP':
        raise Refused('%s: ITS PARENT %s IS NOT A STOP' % (v, v0))
    if not re.match(r'^[0-9]+_MONTH_%s$' % idea, month or ''):
        raise Refused('--month MUST BE A MONTH JOB OF %s' % idea)
    md = os.path.join(run, 'receipts', month)
    st = {r.get('stage'): r for r in tsv(os.path.join(md, 'STAGES.tsv'))}
    out = {k: '-' for k in COLS}
    out.update({'idea': idea, 'V': v, 'label_rule': RULE, 'grade_job': d0.get('grade_job', '-'), 'entry_job': '-', 'r1': '-', 'r2': '-'})
    why, src, reads = [], [], []
    g = st.get('grade_%s' % v)
    if g is None:
        raise Refused('%s WAS NOT IN MONTH JOB %s' % (v, month))
    if g.get('rc') != '0':
        why.append('grade rc %s' % g.get('rc'))
    for m in MONTHS:
        s = st.get('month_%s_%s' % (v, m))
        p = os.path.join(md, 'MONTH_READ_%s_%s.txt' % (v, m))
        if s is None or s.get('rc') != '0' or not os.path.isfile(p):
            why.append('month %s %s' % (m, 'missing' if s is None or not os.path.isfile(p) else 'rc %s' % s.get('rc')))
            continue
        src.append('MONTH_READ_%s_%s %s' % (v, m, sha16(p)))
        reads.append((m,) + read_month(p))
    readable = [r for r in reads if r[1] and r[1] != 'NO READ']
    holds = [r for r in readable if r[1] in HOLDS]
    out['months_counted'] = str(len(readable)); out['months_passing'] = str(len(holds))
    out['waves'] = str(sum(r[2] or 0 for r in readable))
    out['note'] = '; '.join('%s %s (15m %s, 1h %s, %s waves)' % (r[0], r[1], r[3], r[4], r[2]) for r in reads) + ('; parent %s STOP %s' % (v0, d0.get('utc', '')))
    if why:
        out['state'] = 'INVALID'; out['note'] = '; '.join(why) + '; ' + out['note']
    elif len(readable) < 3:
        out['state'] = 'INSUFFICIENT'
    elif len(holds) >= 3:
        out['state'] = 'FORWARD PASS'
    else:
        out['state'] = 'FORWARD STOP'
    out['sources'] = 'month %s: %s | parent %s grade %s' % (month, ', '.join(src) or '-', v0, d0.get('grade_job', '-'))
    return out


def main(argv):
    a = list(argv)
    write = '--write' in a
    a = [x for x in a if x != '--write']
    month = None
    if '--month' in a:
        i = a.index('--month')
        if i + 1 >= len(a):
            raise Refused('--month NEEDS A VALUE')
        month = a[i + 1]; del a[i:i + 2]
    settings = None
    if '--settings' in a:
        i = a.index('--settings')
        if i + 1 >= len(a):
            raise Refused('--settings NEEDS A VALUE')
        settings = a[i + 1]; del a[i:i + 2]
    if len(a) != 3 or not month:
        raise Refused('USAGE decide_forward_v3.py --settings <settings file> RUN IDEA V --month <MONTH JOB> [--write]')
    if not settings:
        raise Refused('--settings <file> IS REQUIRED: the settings file of this machine (<Alarm>/settings/SETTINGS_<MACHINE>.env)')
    runtag, idea, v = a
    if not RUNTAG.match(runtag) or not NAME.match(idea) or not NAME.match(v):
        raise Refused('BAD RUN, IDEA OR VARIANT NAME')
    configure(settings)
    run = os.path.join(CFG['H'], 'runs', runtag)
    d = decide(run, idea, v, month)
    print('DECISION %s %s: %s | months read %s, holding %s | %s' % (idea, v, d['state'], d['months_counted'], d['months_passing'], d['note']))
    print('SOURCES', d['sources'])
    if write:
        if sha16(CFG['REG']) != CFG['REG_SHA']:
            raise Refused('reg_append_v1.py CHANGED')
        prev = [r for r in tsv(os.path.join(run, 'registers', 'DECISIONS.tsv')) if r.get('idea') == idea and r.get('V') == v]
        if prev and prev[-1].get('state') == d['state'] and prev[-1].get('label_rule') == RULE:
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
