#!/usr/bin/env python3
"""mutants_tried_search_v1.py (SCOUT, 3 Nov 2026): planted bugs in tried_search_v1.py; test_tried_search_v1.py must fail on each.
Each mutant replaces one exact text (found once) in a copy of the tool and runs the suite with TOOL_UNDER_TEST on the copy; the unpatched
copy must pass first. Prints one line per mutant, then MUTANTS <killed> of <n> killed; exit 0 only when all are killed.
  python3 -B mutants_tried_search_v1.py"""
import os, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, '..', 'tools', 'tried_search_v1.py')
TEST = os.path.join(HERE, 'test_tried_search_v1.py')
M = [
    ('M01 no turn round of < and <=', "        if op in ('<', '<='):\n", "        if False:\n"),
    ('M02 no a - b > 0 as a > b', "        if R == zero and L[0] == 'sub':\n", "        if False:\n"),
    ('M03 numbers always masked', "        return '#' if mask else v\n", "        return '#'\n"),
    ('M04 fire side ignored', "    side_eq = mine['side'] == other['side']\n", "    side_eq = True\n"),
    ('M05 compared by input names', "        if isinstance(x, str) and x in inp:\n", "        if False:\n"),
    ('M06 --self ignored for claims', "        if self_ri and (run, idea) == self_ri:\n", "        if False:\n"),
    ('M07 the def file itself kept', "            if dp and os.path.realpath(p) == os.path.realpath(dp):\n", "            if False:\n"),
    ('M08 substring words', "    return term in toks or (", "    return any(term in t for t in toks) or ("),
    ('M09 def codes not words', "    terms = [w for w in dict.fromkeys(words + sorted(codes))", "    terms = [w for w in dict.fromkeys(words)"),
    ('M10 COPY on codes only', "    if a == b and side_eq:\n", "    if mine['codes'] == other['codes'] and side_eq:\n"),
    ('M11 half rule strict', "eq * 2 >= max(len(a), len(b))", "eq * 2 > max(len(a), len(b))"),
    ('M12 add and mul not sorted', "                a, b = sorted((a, b), key=text)\n", "                pass\n"),
    ('M13 tokens without dots', "TOK = re.compile(r'[a-z0-9]+(?:\\.[a-z0-9]+)*')", "TOK = re.compile(r'[a-z0-9]+')"),
    ('M14 TRIED not searched', "(('REGISTRY', reg), ('CLAIMS', cl), ('TRIED', tr))", "(('REGISTRY', reg), ('CLAIMS', cl))"),
    ('M15 NEAR wins over COPY', "    if copies:\n", "    if copies and not nears:\n"),
    ('M16 subset rule gone', "    if side_eq and (a < b or b < a) and small['codes'] - {'price'}:\n", "    if False:\n"),
    ('M20 timing ignored', "    time_eq = mine['timing'] == other['timing']\n", "    time_eq = True\n"),
    ('M21 onset default false', "bool(f.get('onset', True))", "bool(f.get('onset', False))"),
    ('M22 numbers rounded', "    return repr(float(x))", "    return format(float(x), '.3g')"),
    ('M23 INCOMPLETE dropped', "    elif unread_paths or not any(v is not None for v in cache.values()):\n", "    elif False:\n"),
    ('M24 trigger event lists by name', "                    kv.append((k, ('$', json.dumps({'list': ev.get(v[k]), 'cover': cv.get(v[k])}, sort_keys=True))))", "                    kv.append((k, ('$', v[k])))"),
    ('M26 trigger event list file ignored', "json.dumps({'list': ev.get(v[k]), 'cover': cv.get(v[k])}, sort_keys=True)", "json.dumps({'cover': cv.get(v[k])}, sort_keys=True)"),
    ('M25 comparison base in the rule', "    return {'lines': lines, 'skel': skel, 'side': side, 'codes': codes, 'timing': timing, 'base': cmpbase}",
     "    lines.add(cmpbase)\n    return {'lines': lines, 'skel': skel, 'side': side, 'codes': codes, 'timing': timing, 'base': cmpbase}"),
    ('M19 a price-only rule is NEAR everything', " and small['codes'] - {'price'}:\n", ":\n"),
    ('M17 no refusal of an empty def', "    if not isinstance(inp, dict) or not isinstance(conds, list) or not conds:\n", "    if not isinstance(inp, dict):\n"),
    ('M18 other side is a COPY', "    if a == b:\n        return 'NEAR'", "    if a == b and False:\n        return 'NEAR'"),
]


def suite(tool):
    nov = os.environ.get('TRIED_SEARCH_NOVELTY') or os.path.join(os.path.dirname(os.path.abspath(TOOL)), 'novelty_v4.py')   # the copy sits in a temp folder
    p = subprocess.run([sys.executable, '-B', TEST], capture_output=True, text=True, env=dict(os.environ, TOOL_UNDER_TEST=tool, TRIED_SEARCH_NOVELTY=nov))
    return p.returncode


def main():
    src = open(TOOL).read()
    with tempfile.TemporaryDirectory() as d:
        plain = os.path.join(d, 'tried_search_v1.py')
        shutil.copyfile(TOOL, plain)
        if suite(plain) != 0:
            print('UNPATCHED COPY FAILS: no mutant is meaningful'); return 3
        killed = 0
        for name, a, b in M:
            if src.count(a) != 1:
                print('%s\tNOT FOUND (%d)' % (name, src.count(a))); continue
            mp = os.path.join(d, 'm.py')
            with open(mp, 'w') as f:
                f.write(src.replace(a, b))
            rc = suite(mp)
            killed += rc != 0
            print('%s\t%s' % (name, 'KILLED' if rc else 'SURVIVED'))
    print('MUTANTS %d of %d killed' % (killed, len(M)))
    return 0 if killed == len(M) else 3


if __name__ == '__main__':
    sys.exit(main())
