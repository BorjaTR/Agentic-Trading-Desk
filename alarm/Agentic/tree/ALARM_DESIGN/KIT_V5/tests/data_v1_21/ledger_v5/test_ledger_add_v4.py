"""tests for ledger_add_v4 (QUANT review 06:48:45Z): result needs a prereg, one result each, the setting file REQUIRED and checked, a result
file older than its prereg refused, status from STATUSES, old rows kept byte for byte, count = prereg + door rows; two processes writing at
once lose no row (the lock); mutants of every guard FAIL."""
import datetime, multiprocessing as mp, os, sys, tempfile, time, types, unittest
HERE = os.path.dirname(os.path.realpath(__file__)); sys.path.insert(0, HERE)
import ledger_add_v4 as L

C1 = datetime.datetime(2026, 10, 23, 6, 30, 0, tzinfo=datetime.timezone.utc); C2 = C1 + datetime.timedelta(minutes=5)


def env(M):
    d = tempfile.mkdtemp(); led = os.path.join(d, 'L.tsv'); s = os.path.join(d, 's.md'); r = os.path.join(d, 'r.txt')
    open(s, 'w').write('rule v1'); open(r, 'w').write('result')
    open(led, 'w').write(M.HEADER + '\t'.join(M.COLS) + '\nOLD\trow\tX\tp\tdoor\n'); return led, s, r


def refused(f):
    try:
        f(); return False
    except SystemExit:
        return True


def run_all(M):
    led, s, r = env(M); ok = []
    ok.append(refused(lambda: M.result('PREREG_X_20261023T063000Z', r, 'PASS', s, path=led, clock=C1)))
    aid = M.prereg('X', 'test', s, path=led, clock=C1); ok.append(aid == 'PREREG_X_20261023T063000Z')
    old = os.path.join(os.path.dirname(led), 'old.txt'); open(old, 'w').write('stale'); os.utime(old, (C1.timestamp() - 3600,) * 2)
    ok.append(refused(lambda: M.result(aid, old, 'PASS', s, path=led, clock=C2)))       # result older than the prereg
    ok.append(refused(lambda: M.result(aid, r, 'GREAT', s, path=led, clock=C2)))        # status not in the list
    M.result(aid, r, 'FAIL', s, path=led, clock=C2)
    ok.append(refused(lambda: M.result(aid, r, 'PASS', s, path=led, clock=C2)))         # second result
    aid2 = M.prereg('X', 'test2', s, path=led, clock=C2); open(s, 'w').write('rule v2')
    ok.append(refused(lambda: M.result(aid2, r, 'PASS', s, path=led, clock=C2)))        # changed setting
    ok.append(open(led).read().splitlines()[2] == 'OLD\trow\tX\tp\tdoor')               # old row kept
    ok.append(M.count('X', path=led) == 3)                                              # 2 prereg + 1 door row
    return ok


def _writer(mod_path, led, s, k, n, mut):
    src = open(mod_path).read()
    for old, new in mut:
        src = src.replace(old, new)
    M = types.ModuleType('w'); M.__file__ = mod_path; exec(compile(src, 'w', 'exec'), M.__dict__)
    for i in range(n):
        M.prereg('P%d_%d' % (k, i), 'c', s, path=led, clock=C1 + datetime.timedelta(seconds=k * 1000 + i))


def concurrent(mut=()):
    d = tempfile.mkdtemp(); led = os.path.join(d, 'L.tsv'); s = os.path.join(d, 's.md'); open(s, 'w').write('x')
    open(led, 'w').write(L.HEADER + '\t'.join(L.COLS) + '\n')
    ps = [mp.Process(target=_writer, args=(L.__file__, led, s, k, 40, mut)) for k in range(3)]
    [p.start() for p in ps]; [p.join() for p in ps]
    return len(L.rows(led)) == 120 and all(p.exitcode == 0 for p in ps)


LOCK_MUT = (("fcntl.flock(lk.fileno(), fcntl.LOCK_EX)", "pass"), ("if line not in open(path).read().splitlines():", "if False:"))


class T(unittest.TestCase):
    def test_all(self):
        self.assertTrue(all(run_all(L)), run_all(L))

    def test_two_processes(self):
        self.assertTrue(concurrent())

    def test_lock_mutant(self):
        self.assertFalse(any(concurrent(LOCK_MUT) for _ in range(3)))

    def test_mutants(self):
        src = open(L.__file__).read()
        for old, new in (("if not p:\n            raise SystemExit('REFUSED %s: no PREREG row", "if False:\n            raise SystemExit('REFUSED %s: no PREREG row"),
                         ("if any(r['ask_id'] == aid + '_R' for r in R):", "if False:"),
                         ("if sha16(setting) != p['setting_sha16']:", "if False:"),
                         ("if os.path.getmtime(result_file) < t_pre:", "if False:"),
                         ("if status not in STATUSES:", "if False:")):
            self.assertEqual(src.count(old), 1, old)
            m = types.ModuleType('m'); m.__file__ = L.__file__; exec(compile(src.replace(old, new), 'm', 'exec'), m.__dict__)
            try:
                res = all(run_all(m))
            except BaseException:                                   # a mutant that crashes (SystemExit too) is caught
                res = False
            self.assertFalse(res, 'mutant not caught: ' + new)


if __name__ == '__main__':
    mp.set_start_method('fork', force=True)
    unittest.main()
