"""ledger_add_v7.py (SCOUT, 3 Nov 2026, V1_21 fixes, playground; TEST, NOT REVIEWED): ledger_add_v5.py a8039ae0f4f23e31 (team/RESEARCH/tools/ledger)
made ready for the Alarm kit. Why: on the real ledger v5 refused every call with 'ValueError: malformed or duplicate ledger row' (a
traceback, no line named), so agents had no released way to register a try and wrote ledger_row=NOT_RECORDED. The cause: TRIES_LEDGER_V1.tsv
line 513 repeats ask_id SCOUT-RECUT of line 512 (RUNNING, then OK, 1 Nov 2026), a row another writer added; v5's reader refuses any
repeated ask_id in the whole file. Changes, nothing else:
  - --settings <file>: the ledger is <RESEARCH_ROOT>/TRIES_LEDGER_V1.tsv of the settings file (v5 found it beside its own folder, which
    inside an install would be the read-only release); no environment variable redirects it.
  - the reader names the line, the ask_id and the fault. A short or long row, or a bad stamp, still refuses every call (code
    MALFORMED_LEDGER). A repeated ask_id refuses only when it is this tool's own (PREREG_<idea>_<stamp>, with _R or _W): those are the ids
    its rules look up. A repeated id of another writer (a door or status row) is printed as a WARN for the ledger's owner and the call
    goes on: this tool never reads those rows by id, and count() is unchanged (it counts kind PREREG and door rows as before).
  - every refusal is one line 'REFUSED <CODE>: why' on stderr, exit 2, never a traceback.
  - new: `check` (every problem of the ledger, exit 0 none, 3 warnings only, 2 malformed) and `has <ask_id>` (exit 0 the row exists, 3 not).
  - `door` (ledger_add_v2.py, not in the kit) is refused DOOR_NOT_IN_KIT.
  python3 -B ledger_add_v7.py --settings <file> prereg|result|withdraw|count|check|has ...   (the arguments of v5)
v5's text follows.
SCOUT ledger_add_v5 (23 Oct 2026) = v4 + a WITHDRAW mode (STRATEGY 10:20:52Z: a declared try that must never run stays in the
ledger marked WITHDRAWN and still counts as a try). v4 (23 Oct 2026; v3 + QUANT review 06:48:45Z: MUST 1 the setting file is REQUIRED at result and checked always;
MUST 2 one exclusive lock (fcntl.flock on <ledger>.lock) around read + rewrite, the new row re-read after the replace; SHOULDs: a result
file older than its prereg is refused, count() also counts the idea's door rows, status from STATUSES). Was: v3 (TOOL_DESIGN V3 section 10).
ONE tries ledger: team/RESEARCH/TRIES_LEDGER_V1.tsv (same columns as v1/v2; v2's door mode is kept unchanged: `door` passes to ledger_add_v2).
  prereg <idea> <purpose> <setting file> [<days_from> <days_to>] : appends ONE row BEFORE any outcome is read: try_utc = the clock (UTC),
      ask_id = PREREG_<idea>_<try_utc>, kind = PREREG, setting_sha16 = sha16 of the setting file, status = PREREG. Prints the ask_id.
  result <ask_id> <result file> <status> <setting file> : appends ONE row AFTER the result is read: the prereg row's idea / purpose / setting_sha16 / days,
      ask_id = <ask_id>_R, kind = RESULT, result_sha16 = sha16 of the result file, status = the given word. Refused when the ask_id has no
      PREREG row, when it already has a RESULT row, when the setting file (REQUIRED) differs from the prereg's sha16, when the result file
      is older than the prereg (mtime before try_utc), or when status is not in STATUSES.
  withdraw <ask_id> <reason> : appends ONE row ask_id = <ask_id>_W, kind = WITHDRAWN, status = WITHDRAWN, purpose = the reason, the prereg's
      idea / setting_sha16 / days. Refused without a PREREG row, after a RESULT row, or twice. A withdrawn ask_id refuses any later result.
  count <idea> : the idea's tries = its PREREG rows + its door rows (kind not PREREG / RESULT / WITHDRAWN): a withdrawn try still counts once.
The file is rewritten whole (tmp + os.replace); rows are never edited or removed. The try time comes from the clock, never typed."""
import calendar, contextlib, datetime, fcntl, hashlib, importlib.util, os, re, sys, time

HERE = os.path.dirname(os.path.realpath(__file__))
LEDGER = None            # v7: configure() sets <RESEARCH_ROOT>/TRIES_LEDGER_V1.tsv from --settings; tests pass path=
OWN_ID = re.compile(r'^PREREG_[^\t]+_[0-9]{8}T[0-9]{6}Z(_R|_W)?$')     # the ids this tool writes and looks up
WARNINGS = []            # v7: foreign repeated ids seen by the last rows() call, for the owner


class LedgerError(ValueError):
    """v7: a ledger the rules cannot read; code and the line named"""
    def __init__(self, code, why):
        ValueError.__init__(self, '%s: %s' % (code, why)); self.code = code
COLS = ['try_utc', 'ask_id', 'idea', 'purpose', 'kind', 'days_from', 'days_to', 'setting_sha16', 'result_sha16', 'status', 'moments',
        'taken', 'usd_seen', 'per_trade_gross', 'per_trade_seen', 'G1', 'G6', 'G8', 'out_sha16']
STATUSES = ('PASS', 'FAIL', 'UNSURE', 'KILL')
HEADER = '# TRIES_LEDGER_V1 (research desk; append only; every door ask is a try, counted, failures too; rows by SCOUT ledger_add_v1.py from the spool files)\n'


def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def now_utc(clock=None):
    return (clock or datetime.datetime.now(datetime.timezone.utc)).strftime('%Y%m%dT%H%M%SZ')


def rows(path=None):
    """every row; v7: a malformed row refuses with its line; a repeated ask_id refuses when it is this tool's own id, else it is a WARN"""
    path = path or LEDGER
    if path is None:
        raise LedgerError('NO_LEDGER', 'no --settings: the ledger is <RESEARCH_ROOT>/TRIES_LEDGER_V1.tsv')
    del WARNINGS[:]
    if not os.path.exists(path):
        return []
    out = []; seen = {}
    for n, l in enumerate(open(path), 1):
        if l.startswith('#') or l.startswith('try_utc') or '\t' not in l:
            continue
        f = l.rstrip('\n').split('\t')
        if len(f) != len(COLS):
            raise LedgerError('MALFORMED_LEDGER', '%s line %d has %d fields, the ledger has %d (ask_id %r)' % (path, n, len(f), len(COLS), f[1] if len(f) > 1 else ''))
        try:
            datetime.datetime.strptime(f[0], '%Y%m%dT%H%M%SZ')
        except ValueError:
            raise LedgerError('MALFORMED_LEDGER', '%s line %d: try_utc %r is not YYYYMMDDTHHMMSSZ (ask_id %r)' % (path, n, f[0], f[1]))
        if f[1] in seen:
            if OWN_ID.match(f[1]):
                raise LedgerError('DUPLICATE_OWN_ID', '%s line %d repeats ask_id %s of line %d' % (path, n, f[1], seen[f[1]]))
            WARNINGS.append('%s line %d repeats ask_id %s of line %d (not written by ledger_add; for the ledger owner)' % (path, n, f[1], seen[f[1]]))
        else:
            seen[f[1]] = n
        out.append(dict(zip(COLS, f)))
    return out


@contextlib.contextmanager
def _locked(path=None):
    """one exclusive lock for every writer of the ledger (MUST 2)"""
    path = path or LEDGER
    with open(path + '.lock', 'a') as lk:
        fcntl.flock(lk.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lk.fileno(), fcntl.LOCK_UN)


def _append_unlocked(row, path):
    prior = rows(path)
    if prior and row.get('try_utc','') < max(r['try_utc'] for r in prior):
        raise ValueError('ledger timestamp precedes an existing event')
    old = open(path).read() if os.path.exists(path) else HEADER + '\t'.join(COLS) + '\n'
    if not old.endswith('\n'):
        old += '\n'
    if any(any(ch in str(row.get(c,'')) for ch in ('\t','\r','\n')) for c in COLS):
        raise ValueError('TSV fields must not contain tabs or newlines')
    line = '\t'.join(str(row.get(c, '')) for c in COLS); tmp = path + '.tmp.%d' % os.getpid()
    with open(tmp, 'w') as f:
        f.write(old + line + '\n'); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, path)
    if line not in open(path).read().splitlines():                 # re-read after the replace (MUST 2)
        raise SystemExit('LEDGER WRITE LOST: %s' % row.get('ask_id'))


def _append(row, path=None):
    path = path or LEDGER
    with _locked(path):
        _append_unlocked(row, path)


def prereg(idea, purpose, setting, days_from='', days_to='', path=None, clock=None):
    path = path or LEDGER; t = now_utc(clock); aid = 'PREREG_%s_%s' % (idea, t)
    with _locked(path):
        if any(r['ask_id'] == aid for r in rows(path)):
            raise SystemExit('REFUSED %s: already registered' % aid)
        _append_unlocked(dict(try_utc=t, ask_id=aid, idea=idea, purpose=purpose, kind='PREREG', days_from=days_from, days_to=days_to,
                              setting_sha16=sha16(setting), status='PREREG'), path)
    return aid


def result(aid, result_file, status, setting, path=None, clock=None):
    path = path or LEDGER
    if status not in STATUSES:
        raise SystemExit('REFUSED %s: status %r not in %s' % (aid, status, STATUSES))
    with _locked(path):
        R = rows(path); p = [r for r in R if r['ask_id'] == aid and r['kind'] == 'PREREG']
        if not p:
            raise SystemExit('REFUSED %s: no PREREG row (register before reading the result)' % aid)
        if any(r['ask_id'] == aid + '_R' for r in R):
            raise SystemExit('REFUSED %s: a RESULT row exists already' % aid)
        if any(r['ask_id'] == aid + '_W' for r in R):
            raise SystemExit('REFUSED %s: the try was WITHDRAWN; it never runs' % aid)
        p = p[0]
        if sha16(setting) != p['setting_sha16']:
            raise SystemExit('REFUSED %s: the setting file changed since the prereg (%s vs %s)' % (aid, sha16(setting), p['setting_sha16']))
        t_pre = calendar.timegm(time.strptime(p['try_utc'], '%Y%m%dT%H%M%SZ'))
        if os.path.getmtime(result_file) < t_pre:
            raise SystemExit('REFUSED %s: the result file is older than the prereg' % aid)
        _append_unlocked(dict(try_utc=now_utc(clock), ask_id=aid + '_R', idea=p['idea'], purpose=p['purpose'], kind='RESULT',
                              days_from=p['days_from'], days_to=p['days_to'], setting_sha16=p['setting_sha16'], result_sha16=sha16(result_file),
                              status=status), path)
    return aid + '_R'


def withdraw(aid, reason, path=None, clock=None):
    path = path or LEDGER
    with _locked(path):
        R = rows(path); p = [r for r in R if r['ask_id'] == aid and r['kind'] == 'PREREG']
        if not p:
            raise SystemExit('REFUSED %s: no PREREG row' % aid)
        if any(r['ask_id'] == aid + '_R' for r in R):
            raise SystemExit('REFUSED %s: a RESULT row exists; a read try cannot be withdrawn' % aid)
        if any(r['ask_id'] == aid + '_W' for r in R):
            raise SystemExit('REFUSED %s: already WITHDRAWN' % aid)
        p = p[0]
        _append_unlocked(dict(try_utc=now_utc(clock), ask_id=aid + '_W', idea=p['idea'], purpose=reason, kind='WITHDRAWN', days_from=p['days_from'],
                              days_to=p['days_to'], setting_sha16=p['setting_sha16'], status='WITHDRAWN'), path)
    return aid + '_W'


def count(idea, path=None):
    return sum(1 for r in rows(path) if r['idea'] == idea and r['kind'] not in ('RESULT', 'WITHDRAWN'))


def settings_reader():
    d = HERE
    while not os.path.isfile(os.path.join(d, '_tools', 'settings_v1.py')):
        if os.path.dirname(d) == d:
            raise SystemExit('REFUSED NOT_IN_ALARM: %s is not inside an Alarm package' % __file__)
        d = os.path.dirname(d)
    spec = importlib.util.spec_from_file_location('settings_v1_of_ledger_add', os.path.join(d, '_tools', 'settings_v1.py'))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def configure(settings):
    """v7: LEDGER = <RESEARCH_ROOT>/TRIES_LEDGER_V1.tsv of the settings file"""
    global LEDGER
    S = settings_reader()
    try:
        S.alarm_root(__file__)
        LEDGER = os.path.join(S.get(settings, 'RESEARCH_ROOT'), 'TRIES_LEDGER_V1.tsv')
    except S.Refused as e:
        raise SystemExit('REFUSED SETTINGS: %s' % e)


def check(path=None):
    """v7: (exit code, lines): 0 no problem, 3 warnings only, 2 a row the rules cannot read"""
    try:
        R = rows(path)
    except LedgerError as e:
        return 2, ['REFUSED %s' % e]
    return (3 if WARNINGS else 0), ['WARN ' + w for w in WARNINGS] + ['ROWS %d, own ids %d, warnings %d' % (len(R), sum(1 for r in R if OWN_ID.match(r['ask_id'])), len(WARNINGS))]


def has(aid, path=None):
    return any(r['ask_id'] == aid for r in rows(path))


def main(argv):
    """v7: --settings first; every refusal 'REFUSED <CODE>: why' on stderr, exit 2"""
    a = list(argv)
    try:
        if '--settings' in a:
            i = a.index('--settings')
            if i + 1 >= len(a):
                raise SystemExit('REFUSED USAGE: --settings needs a value')
            configure(a[i + 1]); del a[i:i + 2]
        else:
            raise SystemExit('REFUSED USAGE: --settings <file> is required (the ledger is <RESEARCH_ROOT>/TRIES_LEDGER_V1.tsv)')
        if a and a[0] == 'door':
            raise SystemExit('REFUSED DOOR_NOT_IN_KIT: the door mode runs ledger_add_v2.py, which is not in the Alarm kit')
        if a and a[0] == 'check' and len(a) == 1:
            rc, lines = check(); print('\n'.join(lines)); return rc
        if a and a[0] == 'has' and len(a) == 2:
            ok = has(a[1]); print('%s %s' % ('FOUND' if ok else 'NOT FOUND', a[1])); return 0 if ok else 3
        rc = _main(a)
        for w in WARNINGS:
            print('WARN ' + w, file=sys.stderr)
        return rc
    except LedgerError as e:
        print('REFUSED %s' % e, file=sys.stderr); return 2
    except SystemExit as e:
        if isinstance(e.code, str):
            msg = e.code if e.code.startswith('REFUSED') else 'REFUSED %s' % e.code
            print(msg, file=sys.stderr); return 2
        raise
    except OSError as e:
        print('REFUSED FILE: %s' % e, file=sys.stderr); return 2


def _main(a):
    if a and a[0] == 'prereg' and len(a) in (4, 6):
        aid = prereg(*a[1:]); print(aid, 'tries for %s: %d' % (a[1], count(a[1]))); return 0
    if a and a[0] == 'result' and len(a) == 5:
        print(result(a[1], a[2], a[3], a[4])); return 0
    if a and a[0] == 'withdraw' and len(a) == 3:
        print(withdraw(a[1], a[2])); return 0
    if a and a[0] == 'count' and len(a) == 2:
        print(count(a[1])); return 0
    print(__doc__, file=sys.stderr); return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
