"""TEST2 run_teeth_exit_v25 (23 Oct 2026): mutants for test_exit_engine_v25 on PATCHED TEMP COPIES of exit_engine_v1.py (the engine is
never edited). Each disables one V2.5 2b guard; the suite must FAIL on each and PASS on the unpatched base. One process at a time."""
import os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.realpath(__file__))
TOOL = os.path.dirname(HERE)
SRC = os.path.join(TOOL, 'exit_engine_v1.py')


def off(prefix):
    return (prefix, prefix.replace('raise ', 'None and ', 1))


MUTANTS = {
    'hole_never_uncertain': ("uncertain = (out['path_gap'] & levels) | monitor_fill_gap", "uncertain = monitor_fill_gap"),
    'levels_ignored': ("uncertain = (out['path_gap'] & levels) | monitor_fill_gap", "uncertain = out['path_gap'] | monitor_fill_gap"),
    'noprice_not_unresolved': ("np.where(out['kind'] == 'noprice', 'UNRESOLVED',", "np.where(out['kind'] == 'noprice_x', 'UNRESOLVED',"),
    'census_ge': ("(n - c['clean']) / n > incomplete_share", "(n - c['clean']) / n >= incomplete_share"),
    'census_drops_noprice': ("'noprice': int((e == 'UNRESOLVED').sum())}", "'noprice': 0}"),
    'monitor_gap_clean': ("uncertain = (out['path_gap'] & levels) | monitor_fill_gap", "uncertain = (out['path_gap'] & levels)"),
    'schema_unchecked': off("raise ValueError('exit registry schema differs"),
    'row_memory_unchecked': off("raise ValueError('the row passed differs"),
    'row_sha_unchecked': off("raise ValueError('exit row %s sha16 is not the frozen"),
    'cost_unchecked': off("raise ValueError('cost table %s sha16 is not the frozen"),
    'module_unchecked': off("raise ValueError('exit_engine module sha16"),
    'manifest_optional': off("raise ValueError('run_frozen needs the frozen manifest"),
    'inventory_optional': off("raise ValueError('dependency inventory required"),
    'inventory_incomplete_ok': off("raise ValueError('dependency inventory lacks"),
    'dependency_changed_ok': off("raise ValueError('dependency %s differs"),
}


def build(tmp, name, src):
    s = src.replace("HERE = os.path.dirname(os.path.abspath(__file__))", "HERE = %r" % TOOL)
    if name:
        a, b = MUTANTS[name]
        if a not in s:
            return None
        s = s.replace(a, b, 1)
    p = os.path.join(tmp, 'exit_v25_%s.py' % (name or 'base')); open(p, 'w').write(s)
    return p


def run(path):
    env = dict(os.environ, EXIT_ENGINE=path, EXIT_TARGET='engine', PYTHONDONTWRITEBYTECODE='1')
    p = subprocess.run([sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', 'test_exit_engine_v25.py'], cwd=HERE, env=env,
                       capture_output=True, text=True)
    return p.returncode, sorted(set(re.findall(r'FAILED \S+::(\S+)', p.stdout))), (p.stdout.strip().splitlines() or [''])[-1]


def main():
    src = open(SRC).read(); tmp = tempfile.mkdtemp(prefix='test2_exit25_teeth_'); ok = True; caught = 0
    for name in [''] + list(MUTANTS):
        p = build(tmp, name, src)
        if p is None:
            print('%-24s MISSING patch target (the code changed): update this mutant' % name); ok = False; continue
        rc, failed, tail = run(p)
        good = rc == 0 if not name else (rc != 0 and bool(failed)); ok &= good; caught += bool(name and good)
        print('%-24s %s rc=%d caught_by=%s | %s' % (name or 'BASE', 'OK ' if good else 'BAD', rc, ','.join(failed[:3]) or '-', tail))
    print('TEETH', 'PASS' if ok else 'FAIL', '(base passes, %d of %d mutants caught)' % (caught, len(MUTANTS)))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
