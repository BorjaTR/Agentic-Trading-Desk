#!/usr/bin/env python3
"""leak_scan_v1.py (SCOUT 2026-11-08, drill LEAK_SCAN, part P33; C104). Is any held-out (Feb-Mar 2026) marker or number in a file that a
hunter, assessor or curator reads? Orchestrator only: it reads the held-out results itself and never prints them.
  python3 -B leak_scan_v1.py --pattern-file <the pack's held-out pattern file> --secrets <orchestrator-only files ...> --targets <files or dirs ...> [--out report.tsv]
- secrets: every signed number with 2 decimals (e.g. +1.84, -0.52) and every 'n waves' in the given held-out files (T8_RESULT.md,
  HELDOUT_YARDSTICK_FEBMAR_V1.json ...). Unsigned JSON values are read from keys lead15 / lead1h / waves.
- allow: files of design-month numbers (knowledge_v1/EVIDENCE.tsv, SERIES_V2.tsv, SERIES_V2_CONFIG.json): a secret that also appears
  there is a Sep-Jan number quoted beside the held-out one (the T8 page repeats them), not a held-out number, and is dropped.
- targets: files, or folders scanned for .md .tsv .json .txt (no other files; folders named jobs, pipe*, split*, library, root, prep,
  setup are skipped: they are tool output, not reading material).
- a hit = the pack's held-out marker regex (--pattern-file; alarm pack HELDOUT_PATTERN.txt = build_run_v2 HELDOUT_RX: lead_2602, yardstick_heldout_febmar, 'Feb-Mar ... +n.nn' ...) or a secret number
  with its sign at a word boundary. The report gives file, line number and the KIND of hit only (MARKER or NUMBER), never the number.
Exit 0 = no hit, 3 = hits, 2 = refused (no pattern file and no build_run_v2.py beside the tool) (each to be opened by hand: a number can match by chance)."""
import argparse, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
MARKER_RX = None   # RC2 (C215): the held-out marker pattern is the pack's (--pattern-file or env LEAK_SCAN_PATTERN_FILE; alarm pack: packs/alarm/HELDOUT_PATTERN.txt)

def load_pattern(path):
    """one regular expression per file (lines joined, '#' lines skipped); sets MARKER_RX"""
    global MARKER_RX
    txt = ''.join(l.rstrip('\n') for l in open(path, encoding='utf-8') if not l.startswith('#'))
    if not txt.strip(): raise SystemExit('REFUSED EMPTY_PATTERN %s' % path)
    MARKER_RX = re.compile(txt); return MARKER_RX

BESIDE_BUILDER = os.path.join(HERE, 'build_run_v2.py')   # C218: the alarm seat default as before: the builder beside the tool (a release copy has none)
def load_builder(path):
    global MARKER_RX
    import importlib.util
    s = importlib.util.spec_from_file_location('brv2', path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); MARKER_RX = m.HELDOUT_RX; return MARKER_RX
if os.path.isfile(BESIDE_BUILDER): load_builder(BESIDE_BUILDER)
EXT = ('.md', '.tsv', '.json', '.txt')
SKIP = re.compile(r'^(jobs|pipe.*|split.*|library|root|prep|setup|curator_scripts|time_log.*)$')
NUM_RX = re.compile(r'(?<![0-9.])[+-]\d+\.\d\d(?![0-9])')


def secrets(paths):
    out = set()
    for p in paths:
        txt = open(p, encoding='utf-8', errors='replace').read()
        out |= set(NUM_RX.findall(txt))
        out |= set('%d waves' % int(w) for w in re.findall(r'(\d{3,6}) waves', txt))
        if p.endswith('.json'):
            def walk(v):
                if isinstance(v, dict):
                    for k, x in v.items():
                        if k in ('lead15', 'lead1h') and isinstance(x, (int, float)):
                            out.update({'+%.2f' % x if x >= 0 else '%.2f' % x})
                        elif k == 'waves' and isinstance(x, int):
                            out.add('%d waves' % x)
                        else:
                            walk(x)
                elif isinstance(v, list):
                    for x in v: walk(x)
            walk(json.load(open(p)))
    return out


def allowed(paths):
    out = set()
    for p in paths:
        txt = open(p, encoding='utf-8', errors='replace').read()
        out |= set(NUM_RX.findall(txt)) | set('+' + x for x in re.findall(r'(?<![0-9.+-])(\d+\.\d\d)(?![0-9])', txt))
        out |= set('%d waves' % int(w) for w in re.findall(r'(?<![0-9.])(\d{3,6})(?![0-9.])', txt))   # wave counts sit in TSV columns without the word
    return out


def files(targets):
    for t in targets:
        if os.path.isfile(t):
            yield t
        elif os.path.isdir(t):
            for root, dirs, fs in os.walk(t):
                dirs[:] = [d for d in dirs if not SKIP.match(d)]
                for f in fs:
                    if f.endswith(EXT) and '.pre_' not in f:
                        yield os.path.join(root, f)


def scan(targets, sec):
    hits = []
    for f in files(targets):
        for i, line in enumerate(open(f, encoding='utf-8', errors='replace'), 1):
            num = any((s in line) if s.endswith('waves') else re.search(r'(?<![0-9.])' + re.escape(s) + r'(?![0-9])', line) for s in sec)
            mk = bool(MARKER_RX.search(line))          # C109: a line with a marker AND a number was reported as MARKER only (HELDOUT.md line 7)
            if num or mk:
                hits.append((f, i, '+'.join(k for k, v in (('NUMBER', num), ('MARKER', mk)) if v)))
    return hits


def main(argv):
    ap = argparse.ArgumentParser(); ap.add_argument('--secrets', nargs='+', required=True); ap.add_argument('--targets', nargs='+', required=True)
    ap.add_argument('--allow', nargs='*', default=[]); ap.add_argument('--out'); ap.add_argument('--pattern-file', default=os.environ.get('LEAK_SCAN_PATTERN_FILE'))
    a = ap.parse_args(argv)
    if a.pattern_file: load_pattern(a.pattern_file)
    elif MARKER_RX is None:
        print('REFUSED NO_PATTERN: give --pattern-file <the pack held-out pattern file> (alarm pack: packs/alarm/HELDOUT_PATTERN.txt)'); return 2
    sec = secrets(a.secrets) - allowed(a.allow); n = sum(1 for _ in files(a.targets)); hits = scan(a.targets, sec)
    if a.out:
        with open(a.out, 'w') as fh:
            fh.write('file\tline\tkind\n'); fh.writelines('%s\t%d\t%s\n' % h for h in hits)
    for h in hits[:200]: print('HIT %s:%d %s' % h)
    print('LEAK_SCAN %s files %d secrets %d hits %d' % ('PASS' if not hits else 'HITS', n, len(sec), len(hits)))
    return 0 if not hits else 3


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
