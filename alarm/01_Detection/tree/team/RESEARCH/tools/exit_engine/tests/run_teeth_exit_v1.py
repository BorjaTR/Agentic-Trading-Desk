"""TEST2 run_teeth_exit_v1 (23 Oct 2026): proves the T03 tests have teeth. Runs the suite (not engine_only) on the oracle: the CONTROL
(no mutant) must PASS every test; each MUTANT of oracle_exit_v1.MUTANTS must FAIL at least one test. Prints one line per run and a verdict.
At most 3 processes (TOOL_DESIGN V4.2 section 7); call it under taskpolicy -b nice -n 10. Writes nothing but its stdout."""
import os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE)
import oracle_exit_v1 as O


def run(m):
    env = dict(os.environ, EXIT_TARGET='oracle', EXIT_MUTANT=m, PYTHONDONTWRITEBYTECODE='1')
    t = time.time()
    p = subprocess.run([sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', '-m', 'not engine_only', HERE],
                       cwd=HERE, env=env, capture_output=True, text=True)
    failed = sorted(set(re.findall(r'FAILED \S+::(\S+)', p.stdout)))
    tail = (p.stdout.strip().splitlines() or [''])[-1]
    return m or 'CONTROL', p.returncode, failed, tail, time.time() - t


def main():
    with ThreadPoolExecutor(3) as ex:
        res = list(ex.map(run, [''] + list(O.MUTANTS)))
    ok = True
    for name, rc, failed, tail, dt in res:
        good = (rc == 0) if name == 'CONTROL' else (rc != 0 and len(failed) > 0)
        ok &= good
        print('%-22s %s rc=%d %5.1fs caught_by=%s | %s' % (name, 'OK ' if good else 'BAD', rc, dt, ','.join(failed) or '-', tail))
    print('TEETH', 'PASS' if ok else 'FAIL', '(control passes, %d of %d mutants caught)' %
          (sum(1 for n, rc, f, _, _ in res if n != 'CONTROL' and rc != 0 and f), len(O.MUTANTS)))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
