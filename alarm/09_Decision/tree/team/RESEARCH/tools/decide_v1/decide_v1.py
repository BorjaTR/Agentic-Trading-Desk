"""decide_v1.py (DECIDE seat, 26 Oct 2026): decision tool V1, one generic command for any alarm, any coin set, any day range.

It reads, joined by the fire key (alarm id, coin, second, push side):
  - the fire list: a frozen universe (alarm_id, coin, t, side, parent_id, cluster_id, weight, ...), whose header names each alarm's
    source event list with its sha16 (the onset_t, trigger and event_id of every event are copied from it unchanged);
  - the frozen cards of the three libraries: context (ctx.), profile (prof.), pre-move (pmm.);
  - the alarm's rulebook (or the default rulebook), the safety file, the lab tools file and the admitted inputs file;
and writes one decision row per fire (decide_rules_v1.decide), plus the TAKE and SKIP event lists in the grader's format
(idea_to_grade V3.1 --events ... --events-subset). It never reads a price or an outcome and never runs a producer.
Every per-fire output has a fixed header that does not depend on the data or the rulebook, and starts with the fire key
alarm_id, coin, t, side (side = the push side of the fire; the trade side is its own column).
No alarm, coin or date is held in this code: every one of them is the caller's.

Admission (one function, admit(), for every input file, before anything is decided): the universe and every card file must have a
sha16 that its library's release record names (directly, or in a receipt file the release names); each used field's library status
column, when the library declares one, must hold an admitted status for every selected fire; every evidence file and lab tool release
(and its code) must be at its pinned sha16. Every refusal is 'REFUSED <CODE>: why' on stderr, exit 2, before any output is written.
A finished run is checked by verify_run() (one shared check for every consumer): RUN.json, every output at its sha16, no file missing,
no stray file.

  python3 -B decide_v1.py --universe U.tsv --alarm-id ID --first YYYYMMDD --last YYYYMMDD --research-window FIRST:LAST
      --rulebook R.json --safety S.json --lab-tools L.json --admitted A.json --root <forensics> --mode research
      --ctx-cards F.tsv --prof-cards F1.tsv,F2.tsv --pmm-cards F.tsv [--coins A,B] [--volumes-root /Volumes] --out <new folder>
  python3 -B decide_v1.py --verify <run folder>"""
import argparse, csv, datetime as dt, hashlib, json, math, os, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.realpath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import decide_rules_v1 as DR

VERSION = 'DECIDE_V1'
SCHEMA_ADMITTED = 'DECIDE_ADMITTED_V1'
# where each library keeps the fire key (library facts, the same for every alarm)
LIBS = {'ctx.': ('registry_id', 'coin', 't', 'side'),
        'prof.': ('registry_id', 'coin', 'emission_t', 'side'),
        'pmm.': ('registry_id', 'coin', 'emission_t', 'side')}
UNIVERSE_COLS = ('alarm_id', 'coin', 't', 'side', 'parent_id', 'cluster_id', 'weight')
SOURCE_COLS = ('coin', 't', 'side', 'onset_t', 'trigger')
KEY_COLS = {c for k in LIBS.values() for c in k}
# the fixed output headers (pipeline contract: the fire key first, nothing that depends on the data)
DECISIONS_HEAD = ['alarm_id', 'coin', 't', 'side', 'utc', 'parent_id', 'cluster_id', 'weight', 'action', 'slot', 'reason', 'detail',
                  'trade_side', 'entry', 'exit', 'size', 'card_ctx', 'card_prof', 'card_pmm', 'used_values']
EVENTS_HEAD = ['alarm_id', 'coin', 't', 'side', 'onset_t', 'trigger', 'event_id']
VALUE_COUNTS_HEAD = ['alarm_id', 'field', 'value', 'kind', 'fires']
OUTPUTS = ('DECISIONS.tsv', 'TAKE_EVENTS.tsv', 'SKIP_EVENTS.tsv', 'VALUE_COUNTS.tsv')


class Refused(Exception):
    def __init__(self, code, why):
        Exception.__init__(self, '%s: %s' % (code, why))
        self.code = code


def sha16(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def day_of(t):
    return dt.datetime.fromtimestamp(int(t), dt.timezone.utc).strftime('%Y%m%d')


def utc_of(t):
    return dt.datetime.fromtimestamp(int(t), dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def real_day(s, what):
    try:
        if len(s) != 8 or not s.isdigit():
            raise ValueError
        dt.datetime.strptime(s, '%Y%m%d')
    except ValueError:
        raise Refused('BAD_DATE', '%s %r is not a real YYYYMMDD day' % (what, s))
    return s


def rel_to(p, root):
    """the path relative to --root when it lies under it, else '' (so a checker on another machine can find it from its own root)"""
    r = os.path.relpath(os.path.abspath(p), os.path.abspath(root))
    return '' if r.startswith('..') else r


def whole(v, what):
    s = str(v).strip()
    if not s.lstrip('+-').isdigit():
        raise Refused('NOT_WHOLE', '%s %r is not a whole number' % (what, v))
    return int(s)


def read_tsv(path):
    with open(path, newline='') as f:
        rd = csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t')
        rows = list(rd)
        return rows, list(rd.fieldnames or [])


def fire_key(alarm_id, coin, t, side):
    k = (alarm_id, coin.strip().upper(), whole(t, 't'), whole(side, 'side'))
    if k[3] not in (-1, 0, 1):
        raise Refused('BAD_SIDE', 'side %r of %s is not -1, 0 or +1' % (side, k[:3]))
    return k


def on_this_machine(path, volumes_root):
    """a path the universe header or the admitted file wrote on the Mac (/Volumes/...) -> the same file under --volumes-root"""
    if volumes_root and path.startswith('/Volumes/'):
        return os.path.join(volumes_root, path[len('/Volumes/'):])
    return path


def source_of(universe, alarm_id):
    """the alarm's source event list named in the universe header: (path, sha16)"""
    with open(universe) as f:
        for l in f:
            if not l.startswith('#'):
                break
            w = l[1:].split()
            if len(w) == 3 and w[0] == 'source' and w[1].startswith(alarm_id + '='):
                return w[1][len(alarm_id) + 1:], w[2]
    raise Refused('NO_SOURCE_LIST', 'the universe header names no source list for %s' % alarm_id)


def admit(kind, path, adm, root, volumes_root):
    """the one admission check of every input file: its sha16 must be named by its library's release record (or by a receipt the
    release names, each at its own sha16). -> (sha16, the release record that admits it)"""
    lib = (adm.get('libraries') or {}).get(kind)
    if not lib:
        raise Refused('NOT_ADMITTED', '%s: no release record is declared for %s inputs' % (path, kind))
    rel = os.path.join(root, lib['release'])
    if not os.path.isfile(rel) or sha16(rel) != lib['sha16']:
        raise Refused('PIN_MISMATCH', 'release record %s is not at %s' % (rel, lib['sha16']))
    with open(rel) as f:
        text = f.read()
    texts = [text]
    for rc in lib.get('receipts') or []:
        if rc['sha16'] not in text:
            raise Refused('NOT_ADMITTED', 'receipt %s is not named by the release %s' % (rc['path'], lib['release']))
        rp = on_this_machine(rc['path'], volumes_root)
        if not os.path.isfile(rp) or sha16(rp) != rc['sha16']:
            raise Refused('PIN_MISMATCH', 'receipt %s is not at %s' % (rp, rc['sha16']))
        with open(rp) as f:
            texts.append(f.read())
    h = sha16(path)
    if not any(h in t for t in texts):
        raise Refused('NOT_ADMITTED', '%s (%s) is not named by its release %s or its receipts' % (path, h, lib['release']))
    return h, lib['release']


def read_cards(paths, prefix, alarm_id):
    """one library's cards (one or more files, read as one set) for this alarm -> (key -> {prefix+column: word}, columns)"""
    kc = LIBS[prefix]; out = {}; fields = None
    for p in paths:
        rows, cols = read_tsv(p)
        if not set(kc) <= set(cols):
            raise Refused('MISSING_COLUMNS', '%s: key columns %s missing' % (p, kc))
        these = [c for c in cols if c not in KEY_COLS]
        if fields is None:
            fields = these
        elif these != fields:
            raise Refused('MISSING_COLUMNS', '%s: columns differ from the first %s file' % (p, prefix))
        for n, r in enumerate(rows, start=2):
            if r[kc[0]] != alarm_id:
                continue
            k = fire_key(r[kc[0]], r[kc[1]], r[kc[2]], r[kc[3]])
            if k in out:
                raise Refused('DUPLICATE_FIRE', '%s line %d: fire %s appears twice in the %s cards' % (p, n, k, prefix))
            out[k] = {prefix + c: (r[c] if r[c] is not None else '') for c in these}
    return out, [prefix + c for c in (fields or [])]


def read_universe(path, alarm_id, first, last, coins):
    rows, cols = read_tsv(path)
    if not set(UNIVERSE_COLS) <= set(cols):
        raise Refused('MISSING_COLUMNS', '%s: universe columns %s missing' % (path, UNIVERSE_COLS))
    out = []; seen = set()
    for n, r in enumerate(rows, start=2):
        if r['alarm_id'] != alarm_id:
            continue
        k = fire_key(r['alarm_id'], r['coin'], r['t'], r['side'])
        if k in seen:
            raise Refused('DUPLICATE_FIRE', '%s line %d: fire %s twice' % (path, n, k))
        seen.add(k)
        try:
            w = float(r['weight'])
        except ValueError:
            w = float('nan')
        if not (math.isfinite(w) and w > 0):
            raise Refused('BAD_WEIGHT', '%s line %d: weight %r' % (path, n, r['weight']))
        if coins is not None and k[1] not in coins:
            continue
        if not first <= day_of(k[2]) <= last:
            continue
        out.append(dict(key=k, parent_id=r['parent_id'], cluster_id=r['cluster_id'], weight=w))
    out.sort(key=lambda x: (x['key'][2], x['key'][1], x['key'][3]))
    return out


def read_source(path, alarm_id, fires):
    """the source event list -> key -> (onset_t, trigger, event_id) for every selected fire; each fire exactly once, else refused"""
    rows, cols = read_tsv(path)
    if not set(SOURCE_COLS) <= set(cols):
        raise Refused('MISSING_COLUMNS', '%s: source list columns %s missing' % (path, SOURCE_COLS))
    want = {fi['key'] for fi in fires}; out = {}
    for n, r in enumerate(rows, start=2):
        k = fire_key(alarm_id, r['coin'], r['t'], r['side'])
        if k not in want:
            continue
        if k in out:
            raise Refused('DUPLICATE_FIRE', '%s line %d: event %s twice in the source list' % (path, n, k))
        on = (r.get('onset_t') or '').strip()
        if on:
            whole(on, 'onset_t')
        out[k] = (on, (r.get('trigger') or '').strip(), (r.get('event_id') or '').strip())
    lost = sorted(want - set(out))
    if lost:
        raise Refused('SOURCE_MISMATCH', '%d fires of the universe are not in the source list, first %s' % (len(lost), lost[:3]))
    return out


def run(a):
    T = {}; t0 = time.perf_counter()
    if os.path.exists(a.out):
        raise Refused('OUT_EXISTS', '--out %s exists: give a new folder' % a.out)
    real_day(a.first, '--first'); real_day(a.last, '--last')
    if a.research_window.count(':') != 1:
        raise Refused('BAD_DATE', '--research-window %r is not FIRST:LAST' % a.research_window)
    w0, w1 = a.research_window.split(':'); real_day(w0, 'research window start'); real_day(w1, 'research window end')
    if not (w0 <= a.first <= a.last <= w1):
        raise Refused('OUTSIDE_WINDOW', 'days %s..%s are not inside the research window %s' % (a.first, a.last, a.research_window))
    with open(a.lab_tools) as f:
        lt = json.load(f)
    tools = DR.check_lab_tools(lt)
    with open(a.rulebook) as f:
        rb = DR.check_rulebook(json.load(f), a.alarm_id, tools)
    with open(a.safety) as f:
        sf = DR.check_safety(json.load(f))
    with open(a.admitted) as f:
        adm = json.load(f)
    if adm.get('schema') != SCHEMA_ADMITTED:
        raise Refused('BAD_INPUT_FILE', 'admitted inputs schema must be %s' % SCHEMA_ADMITTED)
    used = DR.used_fields(rb, sf, a.mode)
    # every evidence file and every lab tool release the run relies on must exist with its pinned sha16 (paths relative to --root)
    pinned = []
    for part in ('side', 'entry', 'exit', 'size'):
        ev = rb[part].get('evidence')
        if ev:
            pinned.append(('%s evidence' % part, ev['source'], ev['sha16']))
    for ln in rb['skip_rules']:
        if ln.get('evidence'):
            pinned.append(('%s evidence' % ln['id'], ln['evidence']['source'], ln['evidence']['sha16']))
    for part in ('entry', 'exit'):
        for tool, d in lt[part].items():
            pinned.append(('lab tool %s/%s' % (part, tool), d['release'], d['sha16']))
    for what, rel, want in pinned:
        p = os.path.join(a.root, rel)
        if not os.path.isfile(p) or sha16(p) != want:
            raise Refused('PIN_MISMATCH', '%s: %s is %s, pinned %s' % (what, p, sha16(p) if os.path.isfile(p) else 'MISSING', want))
    # every entry and exit id must be a quoted word in the code its release names (each code file at its release sha16): no typo passes
    for part in ('entry', 'exit'):
        for tool, d in lt[part].items():
            with open(os.path.join(a.root, d['release'])) as f:
                rel_files = json.load(f).get('files') or {}
            text = ''
            for rp, h in rel_files.items():
                if rp.endswith('.py'):
                    q = os.path.join(a.root, rp)
                    if not os.path.isfile(q) or sha16(q) != h:
                        raise Refused('PIN_MISMATCH', 'lab tool %s/%s: %s is not at its release sha16 %s' % (part, tool, rp, h))
                    with open(q) as f:
                        text += f.read()
            lost = [i for i in d['ids'] if "'%s'" % i not in text and '"%s"' % i not in text]
            if lost:
                raise Refused('LAB_ID_UNKNOWN', 'lab tool %s/%s: ids %s are not in the code of its release' % (part, tool, lost))
    # admission of every input file through admit(), before it is read
    card_paths = {'ctx.': [a.ctx_cards], 'prof.': a.prof_cards.split(','), 'pmm.': [a.pmm_cards]}
    files = {'universe': a.universe, 'rulebook': a.rulebook, 'lab_tools': a.lab_tools, 'safety': a.safety, 'admitted': a.admitted,
             'ctx_cards': a.ctx_cards, 'pmm_cards': a.pmm_cards}
    for i, p in enumerate(card_paths['prof.']):
        files['prof_cards_%d' % i] = p
    admitted = {'universe': admit('universe', a.universe, adm, a.root, a.volumes_root)}
    for pre, paths in card_paths.items():
        for p in paths:
            admitted[p] = admit(pre, p, adm, a.root, a.volumes_root)
    src_path, src_sha = source_of(a.universe, a.alarm_id)
    src_here = on_this_machine(src_path, a.volumes_root)
    if not os.path.isfile(src_here) or sha16(src_here) != src_sha:
        raise Refused('PIN_MISMATCH', 'source list %s is not at the sha16 %s the universe names' % (src_here, src_sha))
    files['source_events'] = src_here
    at_admission = {k: sha16(p) for k, p in files.items()}
    T['admission'] = time.perf_counter() - t0; t0 = time.perf_counter()
    coins = None if not a.coins or a.coins == 'ALL' else {c.strip().upper() for c in a.coins.split(',')}
    fires = read_universe(a.universe, a.alarm_id, a.first, a.last, coins)
    if not fires:
        raise Refused('NO_FIRES', 'no fires of %s in %s..%s' % (a.alarm_id, a.first, a.last))
    source = read_source(src_here, a.alarm_id, fires)
    cards = {}; fields = {}
    for pre, paths in card_paths.items():
        cards[pre], fields[pre] = read_cards(paths, pre, a.alarm_id)
    status_rules = adm.get('field_status') or {}
    for f in used:
        pre = f[:f.index('.') + 1]
        if f not in fields[pre]:
            raise Refused('FIELD_NOT_IN_CARDS', 'field %s is not a column of its library cards' % f)
        sr = status_rules.get(pre)
        if sr and f + sr['suffix'] not in fields[pre]:
            raise Refused('FIELD_NOT_ADMITTED', 'field %s has no status column %s, which its library declares' % (f, sr['suffix']))
    T['read'] = time.perf_counter() - t0; t0 = time.perf_counter()
    # every value a used field holds must be a declared state or a declared reason of that field; a missing card row (the selection is
    # wider than the library), an empty cell (a malformed card), a field status the library does not admit, or any other word refuses
    # the run before anything is decided
    counts = {}; got = []; uncovered = []; empty = []; bad_status = set()
    for fi in fires:
        k = fi['key']
        vals = {}; found = {}
        for pre in LIBS:
            r = cards[pre].get(k)
            found[pre] = 'FOUND' if r is not None else 'MISSING'
            for f in used:
                if f.startswith(pre):
                    if r is None:
                        vals[f] = DR.NO_CARD_ROW; uncovered.append((f, k))
                        continue
                    vals[f] = (r.get(f) or '').strip() or DR.NO_VALUE
                    if vals[f] == DR.NO_VALUE:
                        empty.append((f, k))
                    sr = status_rules.get(pre)
                    if sr and (r.get(f + sr['suffix']) or '').strip() not in sr['admitted']:
                        bad_status.add((f, (r.get(f + sr['suffix']) or '').strip()))
        for f, (st, rs) in used.items():
            v = vals[f]
            if ';' in v or '=' in v:
                raise Refused('BAD_VALUE', '%s: value %r holds ; or = (used_values could not be read back)' % (f, v))
            kind = DR.kind_of(v, st, rs)
            counts[(f, v, kind)] = counts.get((f, v, kind), 0) + 1
        got.append((fi, vals, found))
    if uncovered:
        raise Refused('SELECTION_NOT_COVERED', '%d fire x field reads have no card row (the library does not cover the selection), first %s'
                      % (len(uncovered), uncovered[:3]))
    if empty:
        raise Refused('CARD_MALFORMED', '%d used card cells are empty, first %s' % (len(empty), empty[:3]))
    if bad_status:
        raise Refused('FIELD_NOT_ADMITTED', 'used fields hold a library status that is not admitted: %s' % sorted(bad_status)[:10])
    bad = sorted({(f, v) for (f, v, kind) in counts if kind == 'UNDECLARED'})
    if bad:
        raise Refused('UNDECLARED_VALUE', 'values that are neither a declared state nor a declared reason of their field: %s '
                      '(the declaration is incomplete)' % bad[:10])
    rows = [(fi, vals, found, DR.decide(vals, fi['key'][3], day_of(fi['key'][2]), rb, sf, a.mode)) for fi, vals, found in got]
    T['compute'] = time.perf_counter() - t0; t0 = time.perf_counter()
    changed = [k for k, p in files.items() if sha16(p) != at_admission[k]]
    if changed:
        raise Refused('INPUT_CHANGED', 'inputs changed after admission: %s' % changed)
    os.makedirs(a.out)
    with open(os.path.join(a.out, 'DECISIONS.tsv'), 'w', newline='') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n'); w.writerow(DECISIONS_HEAD)
        for fi, vals, found, d in rows:
            k = fi['key']
            w.writerow([k[0], k[1], k[2], k[3], utc_of(k[2]), fi['parent_id'], fi['cluster_id'], repr(fi['weight']), d['action'], d['slot'],
                        d['reason'], d['detail'], d['trade_side'], d['entry'], d['exit'], d['size'], found['ctx.'], found['prof.'],
                        found['pmm.'], ';'.join('%s=%s' % (fd, vals[fd]) for fd in sorted(used))])
    for act in ('TAKE', 'SKIP'):
        with open(os.path.join(a.out, '%s_EVENTS.tsv' % act), 'w', newline='') as f:
            w = csv.writer(f, delimiter='\t', lineterminator='\n'); w.writerow(EVENTS_HEAD)
            for fi, vals, found, d in rows:
                if d['action'] == act:
                    k = fi['key']; on, trig, eid = source[k]
                    w.writerow([k[0], k[1], k[2], k[3], on, trig, eid])
    with open(os.path.join(a.out, 'VALUE_COUNTS.tsv'), 'w', newline='') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n'); w.writerow(VALUE_COUNTS_HEAD)
        for (fd, v, kind), n in sorted(counts.items()):
            w.writerow([a.alarm_id, fd, v, kind, n])
    tally = {}
    for fi, vals, found, d in rows:
        key = '%s|%s|%s' % (d['action'], d['slot'], d['reason'])
        t = tally.setdefault(key, {'fires': 0, 'weight': 0.0})
        t['fires'] += 1; t['weight'] += fi['weight']
    for t in tally.values():
        t['weight'] = round(t['weight'], 6)
    missing = {pre: sum(1 for r in rows if r[2][pre] == 'MISSING') for pre in LIBS}
    code = {n: sha16(os.path.join(HERE, n)) for n in ('decide_v1.py', 'decide_rules_v1.py')}
    outs = {n: sha16(os.path.join(a.out, n)) for n in OUTPUTS}
    changed = [k for k, p in files.items() if sha16(p) != at_admission[k]]
    if changed:                       # no RUN.json is written, so verify_run() refuses the folder
        raise Refused('INPUT_CHANGED', 'inputs changed while writing: %s (the folder %s is left without RUN.json)' % (changed, a.out))
    T['write'] = time.perf_counter() - t0
    info = dict(version=VERSION, alarm_id=a.alarm_id, mode=a.mode, first=a.first, last=a.last, research_window=a.research_window,
                coins=a.coins or 'ALL', fires=len(rows), tally=tally, missing_card_rows=missing, used_fields=sorted(used),
                rulebook_alarm=rb['alarm_id'], pinned_checked=[{'what': w, 'path': r, 'sha16': h} for w, r, h in pinned], safety_status=sf.get('status'),
                admitted={k if k == 'universe' else rel_to(k, a.root) or k: {'sha16': h, 'release': r} for k, (h, r) in admitted.items()},
                source_list={'named': src_path, 'sha16': src_sha},
                inputs={k: {'path': os.path.abspath(p), 'root_rel': rel_to(p, a.root), 'sha16': at_admission[k]} for k, p in files.items()},
                root=os.path.abspath(a.root), code=code, outputs=outs, timing_s={k: round(v, 3) for k, v in T.items()},
                made_utc=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))
    with open(os.path.join(a.out, 'RUN.json'), 'w') as f:
        json.dump(info, f, indent=1, sort_keys=True)
    return info


def verify_run(folder):
    """the one shared check of a finished run, for every consumer: RUN.json exists, every output is at its sha16, no output is missing
    and no other file is in the folder -> RUN.json as a dict, else Refused"""
    rp = os.path.join(folder, 'RUN.json')
    if not os.path.isfile(rp):
        raise Refused('RUN_NOT_COMMITTED', '%s has no RUN.json' % folder)
    with open(rp) as f:
        info = json.load(f)
    outs = info.get('outputs') or {}
    present = set(os.listdir(folder)) - {'RUN.json'}
    if set(outs) != set(OUTPUTS) or present != set(OUTPUTS):
        raise Refused('RUN_CHANGED_AFTER_COMMIT', '%s holds %s, RUN.json lists %s' % (folder, sorted(present), sorted(outs)))
    bad = [n for n, h in outs.items() if sha16(os.path.join(folder, n)) != h]
    if bad:
        raise Refused('RUN_CHANGED_AFTER_COMMIT', '%s: %s differ from RUN.json' % (folder, bad))
    return info


def parser():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for x in ('--universe', '--alarm-id', '--first', '--last', '--research-window', '--rulebook', '--safety', '--ctx-cards',
              '--prof-cards', '--pmm-cards', '--lab-tools', '--admitted', '--root', '--out'):
        p.add_argument(x, required=True)
    p.add_argument('--mode', required=True, choices=DR.MODES)
    p.add_argument('--coins')
    p.add_argument('--volumes-root', default='', help="where the Mac's /Volumes is mounted on this machine (empty: the paths as written)")
    return p


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        if argv[:1] == ['--verify'] and len(argv) == 2:
            info = verify_run(argv[1])
            print('VERIFIED %s %s fires' % (argv[1], info['fires']))
            return 0
        a = parser().parse_args(argv)
        info = run(a)
    except Refused as e:
        print('REFUSED %s' % e, file=sys.stderr)
        return 2
    except DR.RuleError as e:
        print('REFUSED RULEBOOK_INVALID: %s' % e, file=sys.stderr)
        return 2
    except (OSError, ValueError, KeyError, TypeError) as e:
        print('REFUSED BAD_INPUT_FILE: %s: %s' % (type(e).__name__, e), file=sys.stderr)
        return 2
    print(json.dumps({'fires': info['fires'], 'tally': info['tally'], 'missing_card_rows': info['missing_card_rows']}, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())
