"""labcore.gates (BUILD2, 23 Oct 2026): the window and outcome gates, ONE gate for every outcome read. MOVED verbatim from
team/RESEARCH/tools/bucket_proof/bucket_proof.py 2b615f53396155d0 (month_last_day, check_window, ledger_rows, outcome_allowed; QUANT's,
LAB1 07:32:48Z). load_law() reads THE seal table team/LAB3/code/lab3/law.py (never a copy of its dates)."""
import importlib.util, os, re
import numpy as np

HERE = os.path.dirname(os.path.realpath(__file__))
LAW = os.path.realpath(os.path.join(HERE, '..', '..', '..', 'LAB3', 'code', 'lab3', 'law.py'))


def load_law(path=None):
    p = path or LAW
    sp = importlib.util.spec_from_file_location('lab3_law', p); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m


def month_last_day(m):
    y, mo = int(m[:4]), int(m[4:])
    nxt = (y + (mo == 12), 1 if mo == 12 else mo + 1)
    return '%04d%02d%02d' % (y, mo, (np.datetime64('%04d-%02d-01' % nxt) - np.timedelta64(1, 'D')).astype(object).day)


def check_window(s, law):
    """every settings month must be readable under lab3/law.py (its last day not refused); outcome, fit and judge months inside months"""
    for m in s['months']:
        why = law.research_refusal(month_last_day(m))
        if why:
            raise ValueError('month %s refused by lab3/law.py: %s' % (m, why))
    for k in ('outcome_months', 'fit_months', 'judge_months'):
        bad = [m for m in s[k] if m not in s['months']]
        if bad:
            raise ValueError('%s %s not in months' % (k, bad))


def ledger_rows(path):
    out = []
    for l in open(path):
        if l.startswith('#') or l.startswith('try_utc') or '\t' not in l:
            continue
        f = l.rstrip('\n').split('\t'); out.append(f)
    return out


WINDOWS = os.path.realpath(os.path.join(HERE, '..', 'freeze_judge', 'WINDOWS_V1.tsv'))


def windows(path=None):
    """the ONE window table (freeze_judge WINDOWS_V1: BUILD, CHECK, BLIND) -> [(name, first YYYYMMDD, last YYYYMMDD or None)]"""
    out = []
    for l in open(path or WINDOWS):
        f = l.rstrip('\n').split('\t')
        if l.startswith('#') or f[0] == 'window' or len(f) < 3:
            continue
        out.append((f[0], f[1], None if f[2] == 'open_ended' else f[2]))
    return out


def window_of(month, wins):
    """the central class of a YYYYMM month: the window holding its first and last day; a month across two windows is refused"""
    a, b = month + '01', month_last_day(month)
    hit = [w for w, lo, hi in wins if lo <= a and (hi is None or b <= hi)]
    if len(hit) != 1:
        raise PermissionError('month %s is not inside exactly one window of WINDOWS_V1 (%s): refused' % (month, hit))
    return hit[0]


def consume_look(ledger, prereg_ask_id, months, now_utc):
    """the ONE look, consumed atomically at authorization (OUTSIDE C2-01, CHECK_WINDOW_RULE_V2 1): a record LOOKS_V1/<prereg>.look beside
    the ledger is CREATED with O_EXCL (two callers cannot both create it); if it exists the look was spent: refused. A look abandoned
    before its RESULT is still spent (exposure). A04-01 (OX-SKEPTIC): NOT an authorization path any more; outcome_allowed never calls it
    (a PREREG name never supplies a family allowance). Kept for isolated synthetic tests only; it writes a state marker, never a value."""
    if not ledger:
        raise PermissionError('CHECK months %s: no ledger to record the one look in: refused' % (months,))
    d = os.path.join(os.path.dirname(os.path.abspath(ledger)), 'LOOKS_V1'); os.makedirs(d, exist_ok=True)
    p = os.path.join(d, '%s.look' % re.sub(r'[^A-Za-z0-9_.-]', '_', prereg_ask_id or 'none'))
    try:
        fd = os.open(p, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
    except FileExistsError:
        raise PermissionError('CHECK months %s: PREREG %s already used its one look (%s): refused' % (months, prereg_ask_id, p))
    try:
        os.write(fd, ('%s\t%s\t%s\n' % (now_utc, prereg_ask_id, ','.join(months))).encode()); os.fsync(fd)
    finally:
        os.close(fd)
    return p


def prereg_family(ledger, pr):
    """the idea family of a PREREG row: its row in TRIES_TYPES_V1.tsv beside the ledger (ledger_add_v6 --family), else the row's idea column
    (OUTSIDE D01b-02: a grant for another family never authorizes this one)"""
    p = os.path.join(os.path.dirname(os.path.abspath(ledger)), 'TRIES_TYPES_V1.tsv') if ledger else None
    if p and os.path.exists(p):
        for l in open(p):
            f = l.rstrip('\n').split('\t')
            if len(f) > 2 and f[0] == pr[1]:
                return f[2]
    return pr[2] if len(pr) > 2 else ''


def opens_rows(path):
    """freeze_judge OPENS_V1.tsv rows: [granted_utc, card_sha16, window, family, open_id] (written by freeze_judge open, the CONSUMING
    authorization: one CHECK look per family, CHECK_WINDOW_RULE_V2 item 1)"""
    if not path or not os.path.exists(path):
        return []
    return [l.rstrip('\n').split('\t') for l in open(path) if l.strip() and not l.startswith('#')]


def outcome_allowed(s, months, ledger=None, now_utc=None, law=None, wins=None, opens=None):
    """v2 (SKEPTIC REVIEW 02-04, 02-05; STRATEGY ask 125528): ONE outcome authorization. Moved from bucket_proof 2b615f53 (QUANT, LAB1
    07:32:48Z) and hardened:
      - now_utc is REQUIRED (the PREREG must be older than it);
      - every requested month passes THE seal (law.py research_refusal of its last day) here, not only in check_window;
      - every month is classed by THE window table (WINDOWS_V1), not by the settings: a BUILD month may be read when the settings open it
        in outcome_months; a CHECK month needs the judge path (an older PREREG naming the fit settings sha16) EVEN IF the settings do not
        list it in judge_months; a BLIND month is refused;
      - contradictory settings are refused (a month both in fit_months and judge_months; a CHECK month in fit_months);
      - single look: a PREREG whose RESULT row (<ask_id>_R) is already in the ledger has been used; a second read is refused.
    v3 (OUTSIDE C2-01, C2-02): the requested judge months must lie inside the PREREG row's own days_from..days_to; a CHECK read
    CONSUMES the one look at authorization: either through freeze_judge open (opens_judge_with.open_id, a CHECK grant row of
    OPENS_V1.tsv given as opens=, before now, for this card: its two judges read under it).
    v4 (OX-SKEPTIC A04-01, CHECK_WINDOW_RULE_V3 item 1): ONE path. A CHECK read needs open_id naming the FAMILY's one CHECK grant: the
    earliest CHECK row of OPENS_V1 for the PREREG's family (by grant time, never file order), stamped before now, for this card sha16.
    No open_id, no grant, a later grant of the same family, another family's grant or a changed card hash: refused. The PREREG-name
    marker fallback is gone; nothing is written here."""
    if now_utc is None:
        raise PermissionError('outcome_allowed: now_utc is required (the PREREG must be older than the read)')
    law = law or load_law(); wins = wins or windows()
    both = sorted(set(s.get('fit_months', [])) & set(s.get('judge_months', [])))
    if both:
        raise PermissionError('settings put months %s in both fit_months and judge_months: refused' % both)
    bad = sorted(set(months) - set(s['outcome_months']))
    if bad:
        raise PermissionError('outcome of months %s is not opened by these settings' % bad)
    for m in months:
        why = law.research_refusal(month_last_day(m))
        if why:
            raise PermissionError('month %s refused by lab3/law.py: %s' % (m, why))
    cls = {m: window_of(m, wins) for m in months}
    for m in s.get('fit_months', []):
        if window_of(m, wins) != 'BUILD':
            raise PermissionError('fit month %s is in the %s window, not BUILD: refused' % (m, window_of(m, wins)))
    blind = sorted(m for m, c in cls.items() if c == 'BLIND')
    if blind:
        raise PermissionError('months %s are BLIND (proof only): refused' % blind)
    judge = sorted(m for m, c in cls.items() if c == 'CHECK') + sorted(m for m in set(months) & set(s.get('judge_months', []))
                                                                      if cls[m] != 'CHECK')
    if judge:
        o = s.get('opens_judge_with') or {}
        rows = ledger_rows(ledger) if ledger else []
        ok = [r for r in rows if len(r) > 7 and r[1] == o.get('prereg_ask_id') and r[4] == 'PREREG' and r[7] == o.get('fit_sha16')
              and r[0] < now_utc]
        if not ok:
            raise PermissionError('judge months %s: no older PREREG row naming the fit settings sha16 %s' % (judge, o.get('fit_sha16')))
        pr = ok[0]                                                          # C2-02: the PREREG row binds its own days
        lo, hi = (pr[5] if len(pr) > 5 else ''), (pr[6] if len(pr) > 6 else '')
        if not (lo and hi) or any(not (lo <= m + '01' and month_last_day(m) <= hi) for m in judge):
            raise PermissionError('judge months %s are not inside the PREREG row\'s days %s-%s: refused (one PREREG, its own window)' % (
                judge, lo or '?', hi or '?'))
        check = [m for m in judge if cls[m] == 'CHECK']
        if check:                                                           # C2-01: the look is CONSUMED at authorization
            oid = o.get('open_id')
            if not oid:                                                     # A04-01: no grant named, no read (no PREREG-name fallback)
                raise PermissionError('CHECK months %s: no open_id: a CHECK read needs the one grant of its family (freeze_judge open): refused'
                                      % (check,))
            fam = prereg_family(ledger, pr)                                 # D01b-02: the grant must be the PREREG's own family
            fg = sorted((r for r in opens_rows(opens) if len(r) > 4 and r[2] == 'CHECK' and r[3] == fam), key=lambda r: (r[0], r[4]))
            if not fg or fg[0][4] != oid or fg[0][1] != o.get('fit_sha16') or not fg[0][0] < now_utc:
                raise PermissionError('CHECK months %s: open_id %r is not the one CHECK grant of family %s (first in OPENS_V1: %s) for card %s '
                                      'before %s: refused' % (check, oid, fam, fg[0][4] + ' ' + fg[0][1] if fg else 'none', o.get('fit_sha16'),
                                                               now_utc))
        gone = [r for r in rows if len(r) > 4 and r[1] == '%s_W' % o.get('prereg_ask_id') and r[4] == 'WITHDRAWN']
        if gone:                                                            # OUTSIDE A15-03 (LAB1): a withdrawn try never runs, grant or not
            raise PermissionError('judge months %s: PREREG %s was WITHDRAWN (%s): the try never runs, refused' % (
                judge, o.get('prereg_ask_id'), gone[0][0]))
        used = [r for r in rows if len(r) > 4 and r[1] == '%s_R' % o.get('prereg_ask_id') and r[4] == 'RESULT']
        if used:
            raise PermissionError('judge months %s: PREREG %s already has its RESULT row (%s): one look only, refused' % (
                judge, o.get('prereg_ask_id'), used[0][0]))
    return True
