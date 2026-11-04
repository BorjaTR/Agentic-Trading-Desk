"""SCOUT ledger_add_v6 (23 Oct 2026; OUTSIDE P1 OXP1-03) = v5 + TYPED tries: prereg needs --type and --family (and may name --parent);
under the same lock it appends a row to TRIES_TYPES_V1.tsv (ask_id, type, family, parent_ask_id). type in TYPES; family must be a family of
FAMILIES_V2.tsv (tools/fairness_bar); an outcome-informed choice of any kind is a try. The ledger format itself is unchanged.
  prereg <idea> <purpose> <setting file> [<from> <to>] --type T --family F [--parent ASK_ID]
v5 text follows. SCOUT ledger_add_v5 (23 Oct 2026) = v4 + a WITHDRAW mode (STRATEGY 10:20:52Z: a declared try that must never run stays in the
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
import calendar, contextlib, datetime, fcntl, hashlib, os, subprocess, sys, time

HERE = os.path.dirname(os.path.realpath(__file__))
LEDGER = os.environ.get('SCOUT_LEDGER') or os.path.join(HERE, '..', '..', 'TRIES_LEDGER_V1.tsv')
COLS = ['try_utc', 'ask_id', 'idea', 'purpose', 'kind', 'days_from', 'days_to', 'setting_sha16', 'result_sha16', 'status', 'moments',
        'taken', 'usd_seen', 'per_trade_gross', 'per_trade_seen', 'G1', 'G6', 'G8', 'out_sha16']
STATUSES = ('PASS', 'FAIL', 'UNSURE', 'KILL')
TYPES = ('GROUPING', 'LABEL_SCHEME', 'UNIVERSE', 'SETTING_CHOICE', 'ALARM_TRUTH', 'STRATEGY_MONEY', 'CHART_READ', 'DESCRIBE_ONLY', 'ABANDONED')
TYPES_FILE = os.environ.get('SCOUT_TYPES') or os.path.join(HERE, '..', '..', 'TRIES_TYPES_V1.tsv')
FAMILIES_FILE = os.path.join(HERE, '..', 'fairness_bar', 'FAMILIES_V2.tsv')
TYPES_COLS = ['ask_id', 'type', 'family', 'parent_ask_id', 'try_utc']


def known_families(path=None):
    path = path or FAMILIES_FILE
    return {l.split('\t')[2] for l in open(path) if not l.startswith('#') and not l.startswith('pattern\t') and l.count('\t') >= 3}
HEADER = '# TRIES_LEDGER_V1 (research desk; append only; every door ask is a try, counted, failures too; rows by SCOUT ledger_add_v1.py from the spool files)\n'


def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def now_utc(clock=None):
    return (clock or datetime.datetime.now(datetime.timezone.utc)).strftime('%Y%m%dT%H%M%SZ')


def rows(path=None):
    path = path or LEDGER
    if not os.path.exists(path):
        return []
    out = []; seen = set()
    for l in open(path):
        if l.startswith('#') or l.startswith('try_utc') or '\t' not in l:
            continue
        f = l.rstrip('\n').split('\t')
        if len(f) != len(COLS) or f[1] in seen:
            raise ValueError('malformed or duplicate ledger row')
        datetime.datetime.strptime(f[0], '%Y%m%dT%H%M%SZ')
        seen.add(f[1]); out.append(dict(zip(COLS, f)))
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


def prereg(idea, purpose, setting, days_from='', days_to='', path=None, clock=None, ttype=None, family=None, parent='', types_path=None, families_path=None):
    path = path or LEDGER; types_path = types_path or TYPES_FILE; t = now_utc(clock); aid = 'PREREG_%s_%s' % (idea, t)
    if ttype not in TYPES:
        raise SystemExit('REFUSED: --type %r not in %s' % (ttype, TYPES))
    if family not in known_families(families_path):
        raise SystemExit('REFUSED: --family %r is not a FAMILIES_V2 family' % family)
    with _locked(path):
        R = rows(path)
        if any(r['ask_id'] == aid for r in R):
            raise SystemExit('REFUSED %s: already registered' % aid)
        if parent and not any(r['ask_id'] == parent for r in R):
            raise SystemExit('REFUSED: --parent %s is not a ledger row' % parent)
        _append_unlocked(dict(try_utc=t, ask_id=aid, idea=idea, purpose=purpose, kind='PREREG', days_from=days_from, days_to=days_to,
                              setting_sha16=sha16(setting), status='PREREG'), path)
        old = open(types_path).read() if os.path.exists(types_path) else '\t'.join(TYPES_COLS) + '\n'
        tmp = types_path + '.tmp.%d' % os.getpid()
        with open(tmp, 'w') as f:
            f.write(old + '\t'.join([aid, ttype, family, parent or '', t]) + '\n'); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, types_path)
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


def main(a):
    if a and a[0] == 'door':
        with _locked():                                                # v2 writes without a lock: hold ours while it runs
            return subprocess.call([sys.executable, '-B', os.path.join(HERE, 'ledger_add_v2.py')] + a[1:])
    if a and a[0] == 'prereg':
        opt = {k: a[a.index(k) + 1] for k in ('--type', '--family', '--parent') if k in a}
        pos = [x for i, x in enumerate(a[1:], 1) if x not in opt.values() and not x.startswith('--')]
        if len(pos) not in (3, 5):
            print(__doc__); return 2
        aid = prereg(*pos, ttype=opt.get('--type'), family=opt.get('--family'), parent=opt.get('--parent', ''))
        print(aid, 'tries for %s: %d' % (pos[0], count(pos[0]))); return 0
    if a and a[0] == 'result' and len(a) == 5:
        print(result(a[1], a[2], a[3], a[4])); return 0
    if a and a[0] == 'withdraw' and len(a) == 3:
        print(withdraw(a[1], a[2])); return 0
    if a and a[0] == 'count' and len(a) == 2:
        print(count(a[1])); return 0
    print(__doc__); return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
