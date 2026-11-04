"""SCOUT ledger_add_v4 (23 Oct 2026; v3 + QUANT review 06:48:45Z: MUST 1 the setting file is REQUIRED at result and checked always;
MUST 2 one exclusive lock (fcntl.flock on <ledger>.lock) around read + rewrite, the new row re-read after the replace; SHOULDs: a result
file older than its prereg is refused, count() also counts the idea's door rows, status from STATUSES). Was: v3 (TOOL_DESIGN V3 section 10).
ONE tries ledger: team/RESEARCH/TRIES_LEDGER_V1.tsv (same columns as v1/v2; v2's door mode is kept unchanged: `door` passes to ledger_add_v2).
  prereg <idea> <purpose> <setting file> [<days_from> <days_to>] : appends ONE row BEFORE any outcome is read: try_utc = the clock (UTC),
      ask_id = PREREG_<idea>_<try_utc>, kind = PREREG, setting_sha16 = sha16 of the setting file, status = PREREG. Prints the ask_id.
  result <ask_id> <result file> <status> <setting file> : appends ONE row AFTER the result is read: the prereg row's idea / purpose / setting_sha16 / days,
      ask_id = <ask_id>_R, kind = RESULT, result_sha16 = sha16 of the result file, status = the given word. Refused when the ask_id has no
      PREREG row, when it already has a RESULT row, when the setting file (REQUIRED) differs from the prereg's sha16, when the result file
      is older than the prereg (mtime before try_utc), or when status is not in STATUSES.
  count <idea> : the idea's tries = its PREREG rows + its door rows (kind not PREREG / RESULT).
The file is rewritten whole (tmp + os.replace); rows are never edited or removed. The try time comes from the clock, never typed."""
import calendar, contextlib, datetime, fcntl, hashlib, os, subprocess, sys, time

HERE = os.path.dirname(os.path.realpath(__file__))
LEDGER = os.environ.get('SCOUT_LEDGER') or os.path.join(HERE, '..', '..', 'TRIES_LEDGER_V1.tsv')
COLS = ['try_utc', 'ask_id', 'idea', 'purpose', 'kind', 'days_from', 'days_to', 'setting_sha16', 'result_sha16', 'status', 'moments',
        'taken', 'usd_seen', 'per_trade_gross', 'per_trade_seen', 'G1', 'G6', 'G8', 'out_sha16']
STATUSES = ('PASS', 'FAIL', 'UNSURE', 'KILL')
HEADER = '# TRIES_LEDGER_V1 (research desk; append only; every door ask is a try, counted, failures too; rows by SCOUT ledger_add_v1.py from the spool files)\n'


def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def now_utc(clock=None):
    return (clock or datetime.datetime.now(datetime.timezone.utc)).strftime('%Y%m%dT%H%M%SZ')


def rows(path=None):
    path = path or LEDGER
    if not os.path.exists(path):
        return []
    out = []
    for l in open(path):
        if l.startswith('#') or l.startswith('try_utc') or '\t' not in l:
            continue
        f = l.rstrip('\n').split('\t'); f += [''] * (len(COLS) - len(f)); out.append(dict(zip(COLS, f)))
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
    old = open(path).read() if os.path.exists(path) else HEADER + '\t'.join(COLS) + '\n'
    if not old.endswith('\n'):
        old += '\n'
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


def count(idea, path=None):
    return sum(1 for r in rows(path) if r['idea'] == idea and r['kind'] != 'RESULT')


def main(a):
    if a and a[0] == 'door':
        with _locked():                                                # v2 writes without a lock: hold ours while it runs
            return subprocess.call([sys.executable, '-B', os.path.join(HERE, 'ledger_add_v2.py')] + a[1:])
    if a and a[0] == 'prereg' and len(a) in (4, 6):
        aid = prereg(*a[1:]); print(aid, 'tries for %s: %d' % (a[1], count(a[1]))); return 0
    if a and a[0] == 'result' and len(a) == 5:
        print(result(a[1], a[2], a[3], a[4])); return 0
    if a and a[0] == 'count' and len(a) == 2:
        print(count(a[1])); return 0
    print(__doc__); return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
