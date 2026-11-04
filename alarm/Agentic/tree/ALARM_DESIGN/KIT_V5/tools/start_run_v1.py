#!/usr/bin/env python3
"""start_run_v1.py (SCOUT, 3 Nov 2026, V1_21 fixes, playground; TEST, NOT REVIEWED). Starts one KIT_V5 run folder from the run template
of the Alarm package that holds this file, writable by you. Why: AGENTS.md "The folder" said `cp -R -n <INSTALL>/.../TEMPLATE_V4 <run>`;
cp keeps the install's read-only modes (dr-x------, r--------), so the new run folder and its registers could not be written (run
SCOUTR12_20261103, PROBLEMS row 1: "mkdir ideas: Permission denied").

  python3 -B <Alarm>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/start_run_v1.py --settings <settings file> <RUN> [--dry]

  RUN      <SEAT>_<YYYYMMDD>: SEAT is a capital letter then capitals and digits, at most 12 (no underscore: SCOUT_R12 is written
           SCOUTR12), the date a real calendar day. The same rule as queue_job, decide, board_line and audit_run (RUNTAG).
  --dry    every check, then prints what it would copy; writes nothing.

It reads the template (Agentic/tree/ALARM_DESIGN/KIT_V5/runs/TEMPLATE_V4: README_RUN.md and the 8 registers) and writes only the new
folder RESEARCH_ROOT/ALARM_DESIGN/runs/<RUN>: every folder 0755, every file 0644 (owner may write), bytes equal to the template's
(sha16 checked after the copy). It never writes, chmods or opens for writing anything inside the Alarm folder; it refuses a run
folder that exists (never merges, never overwrites) and a run folder inside the Alarm folder. Exit 0 done, 2 refused.
"""
import datetime, hashlib, importlib.util, os, re, sys

RUNTAG = re.compile(r'^([A-Z][A-Z0-9]{0,11})_([0-9]{8})$')        # the kit's one run tag rule (queue_job_v14, decide_v4, board_line_v2, audit_run_v3)
TEMPLATE = ('Agentic', 'tree', 'ALARM_DESIGN', 'KIT_V5', 'runs', 'TEMPLATE_V4')
REGISTERS = ('VARIANTS', 'FORECASTS', 'RUNS', 'DECISIONS', 'POSTMORTEMS', 'LEARNINGS_PROPOSED', 'PROBLEMS', 'TOOLS_BUILT')
DIR_MODE, FILE_MODE = 0o755, 0o644


class Refused(Exception):
    pass


def sha16(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def settings_reader():
    d = os.path.dirname(os.path.abspath(__file__))
    while not os.path.isfile(os.path.join(d, '_tools', 'settings_v1.py')):
        if os.path.dirname(d) == d:
            raise Refused('NOT INSIDE AN ALARM PACKAGE: %s (run the copy in the Alarm folder)' % os.path.abspath(__file__))
        d = os.path.dirname(d)
    spec = importlib.util.spec_from_file_location('settings_v1_of_start_run', os.path.join(d, '_tools', 'settings_v1.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def tag_problem(runtag):
    """why a run tag is refused, with the tag to use when one can be made; None when it is good"""
    m = RUNTAG.match(runtag)
    if m:
        try:
            datetime.datetime.strptime(m.group(2), '%Y%m%d')
        except ValueError:
            return 'BAD RUN TAG %r: %s is not a calendar day (YYYYMMDD)' % (runtag, m.group(2))
        return None
    hint = ''
    mm = re.match(r'^(.*)_([0-9]{8})$', runtag)
    if mm:
        seat = re.sub(r'[^A-Z0-9]', '', mm.group(1).upper())
        if seat and seat[0].isalpha() and len(seat) <= 12:
            hint = ': write %s_%s' % (seat, mm.group(2))
    return ('BAD RUN TAG %r: RUN is <SEAT>_<YYYYMMDD>, SEAT a capital letter then capitals and digits, at most 12, no underscore'
            ' (every kit tool splits the tag at its one underscore)%s' % (runtag, hint))


def template_files(tpl):
    """the template's files, relative, sorted; refuses a template that is not the kit's (README_RUN.md and the 8 registers)"""
    if not os.path.isdir(tpl):
        raise Refused('NO RUN TEMPLATE %s' % tpl)
    out = []
    for d, ds, fs in os.walk(tpl):
        ds.sort()
        for f in sorted(fs):
            out.append(os.path.relpath(os.path.join(d, f), tpl))
    need = ['README_RUN.md'] + [os.path.join('registers', n + '.tsv') for n in REGISTERS]
    miss = [n for n in need if n not in out]
    if miss:
        raise Refused('RUN TEMPLATE %s LACKS %s' % (tpl, ', '.join(miss)))
    return out


def start(alarm, research_root, runtag, dry=False):
    """-> (run folder, [(rel, sha16)]); writes only under the new run folder"""
    why = tag_problem(runtag)
    if why:
        raise Refused(why)
    tpl = os.path.join(alarm, *TEMPLATE)
    files = template_files(tpl)
    run = os.path.join(research_root, 'ALARM_DESIGN', 'runs', runtag)
    ra, rr = os.path.realpath(alarm), os.path.realpath(os.path.dirname(run))
    if rr == ra or rr.startswith(ra + os.sep):
        raise Refused('RUN FOLDER INSIDE THE ALARM FOLDER %s: RESEARCH_ROOT must be outside the install' % run)
    if not os.path.isdir(os.path.dirname(run)):
        raise Refused('NO RUNS FOLDER %s (RESEARCH_ROOT/ALARM_DESIGN/runs)' % os.path.dirname(run))
    if os.path.lexists(run):
        raise Refused('RUN FOLDER EXISTS %s: a run is started once; pick another date or seat' % run)
    plan = [(rel, sha16(os.path.join(tpl, rel))) for rel in files]
    if dry:
        return run, plan
    os.mkdir(run, DIR_MODE); os.chmod(run, DIR_MODE)
    for rel, s in plan:
        dst = os.path.join(run, rel)
        for d in reversed([p for p in _parents(rel)]):
            q = os.path.join(run, d)
            if not os.path.isdir(q):
                os.mkdir(q, DIR_MODE); os.chmod(q, DIR_MODE)
        with open(os.path.join(tpl, rel), 'rb') as f, open(dst, 'xb') as g:
            g.write(f.read())
        os.chmod(dst, FILE_MODE)
        if sha16(dst) != s:
            raise Refused('COPY DIFFERS %s (template %s, copy %s)' % (rel, s, sha16(dst)))
    return run, plan


def _parents(rel):
    d = os.path.dirname(rel)
    while d:
        yield d
        d = os.path.dirname(d)


def main(argv):
    a = list(argv); dry = '--dry' in a; a = [x for x in a if x != '--dry']; settings = None
    if '--settings' in a:
        i = a.index('--settings')
        if i + 1 >= len(a):
            raise Refused('--settings NEEDS A VALUE')
        settings = a[i + 1]; del a[i:i + 2]
    if len(a) != 1 or not settings:
        raise Refused('USAGE start_run_v1.py --settings <settings file> <RUN> [--dry]')
    S = settings_reader()
    try:
        alarm = S.alarm_root(__file__)
        research = S.get(settings, 'RESEARCH_ROOT')
    except S.Refused as e:
        raise Refused('SETTINGS: %s' % e)
    run, plan = start(alarm, research, a[0], dry)
    for rel, s in plan:
        print('%s %s %s' % ('WOULD COPY' if dry else 'COPIED', s, rel))
    print('%s %s: %d files, folders 0755, files 0644; next: claim your idea (AGENTS.md step 2)' % ('DRY RUN OK' if dry else 'STARTED', run, len(plan)))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except Refused as e:
        print('REFUSED: %s' % e, file=sys.stderr)
        sys.exit(2)
