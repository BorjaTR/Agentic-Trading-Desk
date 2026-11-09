#!/usr/bin/env python3
# route_check_v9.py (SCO-A61, SCOUT 2026-11-05, PROVISIONAL playground tool, not adopted).
# Lists every reference to START_, PROCESS_, QUESTIONS_, GATES_, PROMPT_, CURATED_, DOC_CONFLICTS_ files
# in the current files named by a manifest, and FAILS if a non-history line names a file not in the
# manifest, or names a manifest file with a sha16 that differs from the manifest.
# Line classes: HISTORY = a text line whose first word (after list, table or heading marks) is "History",
# a JSON line whose key is "history", a TSV field under a column whose name starts with "history";
# QFIELD = a QUESTIONS_ file line from its first ```json fence on (the lossless question fields, provenance);
# CARRIED = a line of a file whose manifest role is carried_table (immutable rows carried by sha16);
# ROUTE = every other line (must name only manifest files, with matching sha16 when one follows the name).
# Usage: python3 -B route_check_v9.py <folder> <manifest.tsv>   (manifest columns: role, file, sha16)
# Exit 0 PASS, 1 FAIL, 2 usage or missing file.
import sys, os, re, hashlib
PAT = re.compile(r'\b((?:START|PROCESS|QUESTIONS|GATES|PROMPT|CURATED|DOC_CONFLICTS)_V\d+)((?:\.(?:md|tsv|json|py))?)(?:\s*(?:\(|:)?\s*(?:sha256|sha16)?\s*([0-9a-f]{16,64})\b)?')
HIST_TXT = re.compile(r'^[\s#\-\|\*>0-9.]*History\b')
HIST_JSON = re.compile(r'^\s*"history"\s*:')
def sha16(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
def main(a):
    if len(a) != 3: print('usage: route_check_v9.py <folder> <manifest.tsv>'); return 2
    D, M = a[1], a[2]
    rows = [l.split('\t') for l in open(M, encoding='utf-8').read().splitlines() if l and not l.startswith('#')]
    if rows and rows[0][:3] == ['role', 'file', 'sha16']: rows = rows[1:]
    man = {}; role = {}
    for r in rows:
        man[r[1]] = r[2]; role[r[1]] = r[0]
    stems = {}
    for f in man:
        stems.setdefault(os.path.splitext(f)[0], []).append(f)
    fails = 0; n = {'ROUTE': 0, 'HISTORY': 0, 'QFIELD': 0, 'CARRIED': 0}
    for f in man:
        p = os.path.join(D, f)
        if not os.path.exists(p): print('FAIL MISSING', f); fails += 1; continue
        if sha16(p) != man[f]: print('FAIL SHA', f, 'manifest', man[f], 'actual', sha16(p)); fails += 1
        lines = open(p, encoding='utf-8').read().split('\n')
        is_tsv = f.endswith('.tsv'); hdr = None; qf = False
        for i, l in enumerate(lines, 1):
            if f.startswith('QUESTIONS_') and l.startswith('```json'): qf = True
            if is_tsv and hdr is None and not l.startswith('#') and '\t' in l: hdr = l.split('\t'); fields = [(c, c) for c in hdr]
            elif is_tsv and hdr is not None: fields = list(zip(hdr + ['?'] * 99, l.split('\t')))
            else: fields = [('', l)]
            for col, txt in fields:
                for m in PAT.finditer(txt):
                    name, ext, h = m.group(1), m.group(2), m.group(3)
                    if role.get(f) == 'carried_table': cls = 'CARRIED'
                    elif qf: cls = 'QFIELD'
                    elif (f.endswith('.json') and HIST_JSON.match(l)) or (not is_tsv and not f.endswith('.json') and HIST_TXT.match(l)) or (is_tsv and col.lower().startswith('history')): cls = 'HISTORY'
                    else: cls = 'ROUTE'
                    n[cls] += 1
                    ref = name + ext
                    if cls != 'ROUTE':
                        print('%s %s:%d %s%s' % (cls, f, i, ref, (' ' + h[:16]) if h else '')); continue
                    target = ref if ext else (stems.get(name, [None])[0])
                    if target not in man:
                        print('FAIL ROUTE %s:%d names %s, not in the manifest' % (f, i, ref)); fails += 1
                    elif h and h[:16] != man[target]:
                        print('FAIL ROUTE %s:%d names %s %s, manifest %s' % (f, i, ref, h[:16], man[target])); fails += 1
                    else:
                        print('OK ROUTE %s:%d %s%s' % (f, i, ref, (' ' + h[:16]) if h else ''))
    print('SUMMARY files %d refs ROUTE %d HISTORY %d QFIELD %d CARRIED %d fails %d -> %s' % (len(man), n['ROUTE'], n['HISTORY'], n['QFIELD'], n['CARRIED'], fails, 'PASS' if fails == 0 else 'FAIL'))
    return 0 if fails == 0 else 1
if __name__ == '__main__': sys.exit(main(sys.argv))
