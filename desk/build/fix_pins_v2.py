#!/usr/bin/env python3
"""fix_pins_v2.py (SCOUT, 4 Nov 2026): the second build step after scrub_v1.py. It repairs the three release-pin faults that made every
GRADE in this repo refuse (found by the first fresh-agent trial, CLEANT01_20261104, job 1002_GRADE_WINDFALL rc 6), keeps every other pin
true, and writes PIN_MAP_V2.tsv beside itself.

  python3 -B desk/build/fix_pins_v2.py <release folder> <alarm folder>            dry: what would change, and the release check after
  python3 -B desk/build/fix_pins_v2.py <release folder> <alarm folder> --write    write (a twin of every changed file first)

The faults and the fixes (decided by SCOUT, written down why):
 E1 interpreter pins: scrub_v1 turned the lab's interpreter path into '<PYTHON>' in 43 RELEASE_*.json 'runtime' blocks, so the release
    check (labcore/release.py: runtime 'interpreter' must equal sys.executable) refuses every interpreter. Fix: the 'interpreter' key is
    dropped from those runtime blocks (labcore's own rule: a manifest without the key is not checked on it). The python and numpy
    version pins stay exact: a desk runs the engine on the Python and numpy it was released on, on any path. No code changes.
 E2 value pins: labcore pins team/LAB3/METRICS_V1.tsv by the sha16 of 28 value columns; scrub_v1 changed two of them (card_sha16 = pins
    of the scrubbed card files; file_col = path text), and the scrub's pin chain only re-points whole-file sha16s. Fix: every value pin
    is recomputed with labcore's own value_sha16 on the repo file and replaced where it differs. No firing value changes.
 E3 a pinned table left out: EXCLUDES.tsv leaves out team/RESEARCH/alarms/* (the lab's found alarms), but the fairness_bar release pins
    team/RESEARCH/alarms/ALARMS_V1.tsv (its family builder reads it; the bar itself does not). Fix: the repo ships ALARMS_V1.tsv with the
    release's header row only (same schema sha16) and a note line: a fresh desk has no alarms; the lab's found alarms stay out.
Then the chain: every file that names an old sha16 or sha256 of a changed file gets the new one, repeated until nothing changes; pages
(.md) keep the release's numbers as records (scrub_v1's rule). Only files inside <alarm folder> are written; nothing is deleted."""
import hashlib, json, os, re, shutil, sys, time

sys.dont_write_bytecode = True                       # importing the repo's labcore must never leave a __pycache__ in alarm/

HEX16 = re.compile(r'(?<![0-9a-f])[0-9a-f]{16}(?![0-9a-f])')
HEX64 = re.compile(r'(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])')
INTERP = re.compile(r'\n[ \t]*"interpreter": "<PYTHON>",[ \t]*(?=\n)')
ALARMS_REL = '01_Detection/tree/team/RESEARCH/alarms/ALARMS_V1.tsv'
LABCORE = '01_Detection/tree/team/RESEARCH/tools'
NOTE = ('# ALARMS_V1.tsv of the clean desk repo (desk/build/fix_pins_v2.py): the lab\'s found alarms are not shipped, so this table holds\n'
        '# the release\'s header row only. A fresh desk has no alarms; a desk\'s own alarms live in its registry.\n')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def files(root):
    out = []
    for d, ds, fs in os.walk(root):
        ds.sort()
        for f in sorted(fs):
            out.append(os.path.join(d, f))
    return out


def labcore(root):
    p = os.path.join(root, LABCORE)
    if p not in sys.path:
        sys.path.insert(0, p)
    from labcore import release as R     # noqa: E402  (the repo's own copy)
    return R


def plan(rel_root, root):
    """-> (texts before, texts after, reasons {path: [E1|E2|E3|PIN]}, extra old->new sha maps)"""
    texts = {p: open(p, encoding='utf-8').read() for p in files(root)}
    new = dict(texts); why = {}
    for p, t in texts.items():                                                      # E1
        if os.path.basename(p).startswith('RELEASE_') and p.endswith('.json') and '"interpreter": "<PYTHON>"' in t:
            t2 = INTERP.sub('', t)
            j = json.loads(t2)
            if 'interpreter' in (j.get('runtime') or {}):
                raise SystemExit('E1: %s still pins an interpreter after the edit: refused' % p)
            new[p] = t2; why.setdefault(p, []).append('E1')
    R = labcore(root)
    for p, t in list(new.items()):                                                  # E2
        if not (os.path.basename(p).startswith('RELEASE_') and p.endswith('.json')):
            continue
        man = json.loads(t); t2 = t
        tree = p[:p.index('/tree/') + len('/tree/')] if '/tree/' in p else None
        for rel, pin in sorted((man.get('files') or {}).items()):
            if not isinstance(pin, dict) or 'value_sha16' not in pin or tree is None:
                continue
            q = os.path.join(tree, rel)
            if not os.path.exists(q):
                continue
            v = R.value_sha16(q, pin['value_columns'])
            if v != pin['value_sha16']:
                if t2.count('"%s"' % pin['value_sha16']) != 1:
                    raise SystemExit('E2: %s names value pin %s more than once: refused' % (p, pin['value_sha16']))
                t2 = t2.replace('"%s"' % pin['value_sha16'], '"%s"' % v)
        if t2 != t:
            new[p] = t2; why.setdefault(p, []).append('E2')
    extra16, extra64 = {}, {}                                                       # E3
    rel_alarms = os.path.join(rel_root, ALARMS_REL)
    a = os.path.join(root, ALARMS_REL)
    if not os.path.exists(a):
        raw = open(rel_alarms, encoding='utf-8').read()
        header = next(l for l in raw.splitlines(True) if not l.startswith('#'))
        new[a] = NOTE + header; texts[a] = None; why[a] = ['E3']
        old = sha(raw.encode())
        extra64[old] = sha(new[a].encode()); extra16[old[:16]] = extra64[old][:16]
    return texts, new, why, (extra16, extra64)


def chain(texts, new, why, extra):
    """re-point every pin of a changed file until nothing changes (scrub_v1's loop); an old sha that two files now answer differently
    is refused (it would be re-pointed to one of them at random)"""
    hist = {p: ({sha(t.encode())} if t is not None else set()) for p, t in texts.items()}
    for it in range(60):
        cur = {p: sha(t.encode()) for p, t in new.items()}
        m64 = dict(extra[1]); owner = {}
        for p in new:
            for h in hist[p]:
                if h != cur[p]:
                    if h in m64 and m64[h] != cur[p]:
                        raise SystemExit('chain: old sha %s is now %s (%s) and %s (%s): refused'
                                         % (h[:16], m64[h][:16], owner.get(h, '?'), cur[p][:16], p))
                    m64[h] = cur[p]; owner[h] = p
        m16 = {a[:16]: b[:16] for a, b in m64.items()}
        changed = 0
        for p, t in new.items():
            if p.endswith('.md'):
                continue
            t2 = HEX64.sub(lambda m: m64.get(m.group(0), m.group(0)), t)
            t2 = HEX16.sub(lambda m: m16.get(m.group(0), m.group(0)), t2)
            if t2 != t:
                new[p] = t2; changed += 1
                if not set(why.get(p, [])) & {'E1', 'E2', 'E3', 'PIN'}:
                    why.setdefault(p, []).append('PIN')
        for p in new:
            hist[p].add(cur[p])
        if not changed:
            return it + 1
    raise SystemExit('the pin chain did not settle in 60 rounds: refused')


def check(root, which=('GRADE', 'MONTH')):
    """the release check of the GRADE and MONTH records, with the runtime the releases pin (python, numpy) standing in for this
    interpreter, so the VM can run it; the real runtime check runs on the desk's PYTHON (desk tests)"""
    R = labcore(root)
    pins = json.load(open(os.path.join(root, LABCORE, 'event_outcomes', 'RELEASE_event_outcomes_GM2.json'))).get('runtime', {})
    real = R.runtime
    R.runtime = lambda: {'python': pins.get('python'), 'numpy': pins.get('numpy'), 'interpreter': None}
    out = {}
    try:
        for w, rel in (('GRADE', 'event_outcomes/RELEASE_event_outcomes_GM2.json'), ('MONTH', 'alarm_process/RELEASE_event_outcomes_GM2_MONTH.json')):
            if w not in which:
                continue
            try:
                R.check(os.path.join(root, LABCORE, rel), os.path.join(root, '01_Detection/tree')); out[w] = 'OK'
            except R.ReleaseRefused as e:
                out[w] = 'REFUSED ' + str(e)
    finally:
        R.runtime = real
    return out


def main(argv):
    if len(argv) < 2:
        print(__doc__); return 2
    rel_root, root = os.path.abspath(argv[0]), os.path.abspath(argv[1]); write = '--write' in argv
    texts, new, why, extra = plan(rel_root, root)
    rounds = chain(texts, new, why, extra)
    rows = [(os.path.relpath(p, root), (sha(texts[p].encode())[:16] if texts[p] is not None else '-'), sha(new[p].encode())[:16],
             ','.join(why.get(p, ['PIN']))) for p in sorted(new) if new[p] != texts[p]]
    n = {k: sum(1 for r in rows if k in r[3].split(',')) for k in ('E1', 'E2', 'E3', 'PIN')}
    print('rounds %d, files changed %d (E1 %d, E2 %d, E3 %d, chain %d)' % (rounds, len(rows), n['E1'], n['E2'], n['E3'], n['PIN']))
    if not write:
        return 0
    stamp = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    repo = os.path.dirname(root)
    tw = os.path.join(repo, '.twins', 'fix_pins_v2_' + stamp)
    for p in sorted(new):
        if new[p] != texts[p] and texts[p] is not None:
            d = os.path.join(tw, os.path.relpath(p, repo)); os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(p, d)
    for p in sorted(new):
        if new[p] != texts[p]:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, 'w', encoding='utf-8') as f:
                f.write(new[p])
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, 'PIN_MAP_V2.tsv'), 'x') as f:
        f.write('# PIN_MAP_V2.tsv (fix_pins_v2.py, %s): every file of alarm/ this step changed; twins in .twins/fix_pins_v2_%s\n' % (stamp, stamp))
        f.write('file\tbefore_sha16\tafter_sha16\twhy\n')
        for r in rows:
            f.write('\t'.join(r) + '\n')
    for w, v in sorted(check(root).items()):
        print('release check %s: %s' % (w, v[:600]))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
