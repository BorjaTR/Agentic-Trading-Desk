"""mutants_agent_docs_v1.py (SCOUT's K9, 30 Oct 2026; TEST, NOT REVIEWED): planted bugs; test_agent_docs_v1.py must fail on every one.
Three kinds: bugs in the generator (_tools/agent_docs_v1.py); docs that drift from the code (a card, TOOL.json or dictionary edited
wrong); code that drifts from its docs (a tool changed, its TOOL.json sha16 stamped again so that only the column, option or exit
checks can catch it). Each mutant runs in its own new temp copy of only the files the test reads (the tools, the files they read,
the KIT_V5 run registers, the settings reader and example, the generator, the test, cards/ and dictionaries/), removed after.
  python3 -B <Alarm>/_tools/tests/mutants_agent_docs_v1.py [--only N,N...] [--list] [--workers N]
Exit 0: every mutant killed; 1: one lived (listed); 2: the test fails on the unmutated copy (nothing to measure)."""
import concurrent.futures
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(HERE)
sys.path.insert(0, TOOLS_DIR)
import settings_v1  # noqa: E402
import agent_docs_v1 as G  # noqa: E402

ALARM = settings_v1.alarm_root(__file__)
GEN = '_tools/agent_docs_v1.py'
K5T = G.K5 + '/tools/'
RGT = G.RG + '/tools/'


def js(path, fn):
    """a mutant of a JSON doc: fn changes the loaded object"""
    return ('json', path, fn)


def tx(path, old, new, restamp=False):
    """a mutant of a text file: old (once) becomes new; restamp: the TOOL.json sha16 of that file is stamped again"""
    return ('text', path, (old, new, restamp))


def add_arg(j):
    j['commands'][0]['args'].append({'name': '--bogus', 'required': False, 'meaning': 'planted', 'example': '--bogus'})


def set_dry_exit(j):
    j['commands'][0]['dry_runs'][2]['exit'] = 0


def set_refuse_exit(j):
    j['commands'][0]['refuses'][0]['exit'] = 5


def drop_column(j):
    j['outputs'][0]['columns'].remove('page')


def by_hand(j):
    j['step'] = G.BY_HAND


def machine_path(j):
    j['commands'][0]['example'] += ' /Users/someone/x'  # machine-path-ok: a planted bug of the docs test


M = [
    # the generator
    tx(GEN, "return [(e.value, rel, e.lineno) for e in node.value.elts]", "return [(e.value, rel, e.lineno) for e in node.value.elts[:-1]]"),
    tx(GEN, r"cols = v[:-1].split('\t') if v.endswith('\n') else v.split('\t')", r"cols = v.split('\t')"),
    tx(GEN, "return [(c.strip(), rel, n) for c in v.split('|') if c.strip()]", "return [(c.strip(), rel, n) for c in v.split('|')]"),
    tx(GEN, "        if len(hit) != 1:", "        if not hit:"),
    tx(GEN, "    if len(fields) != len(names):", "    if False:"),
    tx(GEN, "            if miss or unwritten:", "            if False:"),
    tx(GEN, "r = old.get((o['file'], c)) or {k: NOT_DOC", "r = {k: NOT_DOC"),
    tx(GEN, "OPTION = re.compile(r'^--[a-z][a-z0-9-]*$')", "OPTION = re.compile(r'^--[a-z]+$')"),
    tx(GEN, "out.add(arg.value if isinstance(arg, ast.Constant) and isinstance(arg.value, int) else 1)",
       "out.add(arg.value if isinstance(arg, ast.Constant) and isinstance(arg.value, int) else 0)"),
    tx(GEN, "    return 3 if stale else 0", "    return 0"),
    tx(GEN, "    new.update(gen)", "    new.update({k: v for k, v in gen.items() if k not in new})"),
    tx(GEN, "                    out.append(s)", "                    pass"),
    tx(GEN, "    head = text(alarm, rel).split('\\n', 1)[0]", "    head = text(alarm, rel).split('\\n')[-1]"),
    tx(GEN, "'%s:%d' % (rel, n)", "'%s:%d' % (rel, n + 1)"),
    # the docs
    tx('dictionaries/decide_v2_COLUMNS.tsv', 'DECISIONS.tsv\tnote\t', 'DECISIONS.tsv\tk9_planted\t'),
    tx('dictionaries/decide_v2_COLUMNS.tsv', '\nDECISIONS.tsv\tsources\t', '\nDECISIONS.tsv\tsources_twice\t'),
    js('cards/registry_build_v2.TOOL.json', drop_column),
    js('cards/decide_v2.TOOL.json', set_dry_exit),
    tx('cards/board_line_v2.TOOL.json', '"prints": "POSTED"', '"prints": "POSTED TWICE"'),
    tx('cards/novelty_v2.md', '(../dictionaries/novelty_v2_COLUMNS.tsv)', '(../dictionaries/novelty_v2_COLUMN.tsv)'),
    ('remove', 'cards/index_v2.md', None),
    js('cards/decide_forward_v2.TOOL.json', add_arg),
    tx('dictionaries/novelty_v2_COLUMNS.tsv', '`len(new)`', '`len(newer)`'),
    tx('cards/audit_run_v3.md', '- BOARD: your board file BOARD/<SEAT>.txt (A11, A13).', '- the board: your file <SEAT>.txt (A11, A13).'),
    js('cards/board_line_v2.TOOL.json', set_refuse_exit),
    tx('cards/scoreboard_v2.md', '## Run it\n', '## Run it\n—\n'),
    tx('dictionaries/idea_time_v2_COLUMNS.tsv', '# ' + G.ARCHIVE_LINE + '\n', ''),
    js('cards/queue_job_v5.TOOL.json', machine_path),
    tx('cards/decide_v2.md', 'python3 -B <INSTALL>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/decide_v2.py --settings',
       'python3 <INSTALL>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/decide_v2.py --settings'),
    js('cards/queue_job_v5.TOOL.json', by_hand),
    # the code
    tx(RGT + 'registry_build_v2.py', "'do_not', 'page']", "'do_not', 'page', 'k9_planted']", True),
    tx(K5T + 'decide_v2.py', "'grade_job', 'entry_job', 'sources', 'note')", "'grade_job', 'entry_job', 'sources')", True),
    tx(G.K6 + '/tools/idea_time_v2.py', r"print('idea\tclaimed\t", r"print('idea\tclaimed_at\t", True),
    tx(K5T + 'queue_job_v5.py', "print('DRY RUN OK: %s", "print('DRY RUN DONE: %s", True),
    tx(K5T + 'board_line_v2.py', "        print('REFUSED: %s' % e, file=sys.stderr)\n        sys.exit(2)",
       "        print('REFUSED: %s' % e, file=sys.stderr)\n        sys.exit(3)", True),
    tx(RGT + 'novelty_v2.py', "print('VERDICT %s' % basis)", "print('VERDICT %s %s' % (basis, len(rows)))", True),
    tx(K5T + 'decide_forward_v2.py', "    write = '--write' in a\n", "    write = '--write' in a\n    planted = '--k9-planted' in a\n", True),
    tx(G.K5 + '/jobs/JOB_COUNT_V6.job.sh.txt', r"printf 'stage\trc\tseconds\t", r"printf 'stage\trc\tsecs\t", True),   # V1_8: the CLEAN template is in archive/
]


def sha16(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def copy_package(dst):
    """the files the test reads, at their places in a new Alarm folder"""
    rels = {GEN, '_tools/settings_v1.py', '_tools/tests/test_agent_docs_v1.py'}
    for t in G.TOOLS:
        rels.add(t['file'])
        rels.update(t['reads'])
    for d in ('cards', 'dictionaries', 'settings', G.REGISTERS):
        for n in os.listdir(os.path.join(ALARM, d)):
            if os.path.isfile(os.path.join(ALARM, d, n)):
                rels.add('%s/%s' % (d, n))
    if os.path.isfile(os.path.join(ALARM, '_tools', 'machine_paths_v2.py')):
        rels.add('_tools/machine_paths_v2.py')
    for r in sorted(rels):
        os.makedirs(os.path.dirname(os.path.join(dst, r)), exist_ok=True)
        shutil.copyfile(os.path.join(ALARM, r), os.path.join(dst, r))     # no mode bits: an install is read-only, the copy must take the bug


def plant(a, m):
    kind, rel, arg = m
    p = os.path.join(a, rel)
    if kind == 'remove':
        os.remove(p)
        return
    if kind == 'json':
        with open(p, encoding='utf-8') as f:
            j = json.load(f)
        arg(j)
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(j, f, indent=1, ensure_ascii=False)
            f.write('\n')
        return
    old, new, restamp = arg
    with open(p, encoding='utf-8') as f:
        s = f.read()
    if s.count(old) != 1:
        raise SystemExit('NOT ONCE (%d) in %s: %r' % (s.count(old), rel, old))
    before = sha16(p)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(s.replace(old, new))
    if restamp:                                        # a lazy refresh: only the sha16 in the TOOL.json files is stamped again
        after = sha16(p)
        for n in os.listdir(os.path.join(a, 'cards')):
            if n.endswith('.TOOL.json'):
                q = os.path.join(a, 'cards', n)
                with open(q, encoding='utf-8') as f:
                    t = f.read()
                if before in t:
                    with open(q, 'w', encoding='utf-8') as f:
                        f.write(t.replace(before, after))


def run_one(i, m):
    d = tempfile.mkdtemp(prefix='agent_docs_mut_')
    try:
        a = os.path.join(d, 'Alarm')
        copy_package(a)
        if m is not None:
            plant(a, m)
        env = dict(os.environ)
        env.pop('AGENT_DOCS_DIR', None)
        r = subprocess.run([sys.executable, '-B', os.path.join(a, '_tools', 'tests', 'test_agent_docs_v1.py')], capture_output=True,
                           text=True, timeout=170, env=env, cwd=d)
        return i, r.returncode, (r.stdout + r.stderr)[-400:]
    finally:
        shutil.rmtree(d)


def label(m):
    kind, rel, arg = m
    return '%s %s %s' % (kind, rel, (arg[0].strip()[:60] if kind == 'text' else getattr(arg, '__name__', '')))


def main(argv):
    only, workers = None, 3
    if '--list' in argv:
        for i, m in enumerate(M, 1):
            print('%2d %s' % (i, label(m)))
        return 0
    if '--only' in argv:
        only = {int(x) for x in argv[argv.index('--only') + 1].split(',')}
    if '--workers' in argv:
        workers = int(argv[argv.index('--workers') + 1])
    _, rc, out = run_one(0, None)
    if rc:
        print('THE TEST FAILS ON THE UNMUTATED COPY (rc %d): nothing to measure\n%s' % (rc, out))
        return 2
    todo = [(i, m) for i, m in enumerate(M, 1) if only is None or i in only]
    alive = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        for i, rc, out in sorted(ex.map(lambda x: run_one(*x), todo)):
            print('%-7s %2d %s' % ('KILLED' if rc else 'ALIVE', i, label(M[i - 1])))
            if not rc:
                alive.append(i)
    print('mutants %d, killed %d, alive %d%s' % (len(todo), len(todo) - len(alive), len(alive), (' %s' % alive) if alive else ''))
    return 1 if alive else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
