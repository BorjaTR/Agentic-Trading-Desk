"""tests for ledger_add_v5 = v4 tests (run on v5) + the WITHDRAW mode: withdraw needs a prereg, not after a result, not twice; a withdrawn
try refuses any result; count is unchanged by a withdraw (the try still counts once); mutants of each new guard FAIL."""
import os, sys, types, unittest
HERE = os.path.dirname(os.path.realpath(__file__)); sys.path.insert(0, HERE)
import ledger_add_v5 as L
import test_ledger_add_v4 as T4
import ledger_strict_env as SE


def refused(f):
    try:
        f(); return False
    except (SystemExit, ValueError):                 # the strict reader (C08-02) refusing a duplicate is a refusal too
        return True


def run_w(M):
    led, s, r = SE.env(M); ok = []
    ok.append(refused(lambda: M.withdraw('PREREG_Y_20261023T063000Z', 'no prereg', path=led, clock=T4.C1)))
    aid = M.prereg('Y', 'test', s, path=led, clock=T4.C1); n0 = M.count('Y', path=led)
    ok.append(M.withdraw(aid, 'hold', path=led, clock=T4.C2) == aid + '_W')
    ok.append(refused(lambda: M.withdraw(aid, 'again', path=led, clock=T4.C2)))                 # twice
    ok.append(refused(lambda: M.result(aid, r, 'PASS', s, path=led, clock=T4.C2)))             # result after withdraw
    ok.append(M.count('Y', path=led) == n0 == 1)                                                # still one try
    aid2 = M.prereg('Y', 'test2', s, path=led, clock=T4.C2); M.result(aid2, r, 'FAIL', s, path=led, clock=T4.C2)
    ok.append(refused(lambda: M.withdraw(aid2, 'late', path=led, clock=T4.C2)))                # after a result
    return ok


class T(unittest.TestCase):
    def test_v4_guards_on_v5(self):
        self.assertTrue(all(SE.run_all(L)), SE.run_all(L))

    def test_withdraw(self):
        ok = run_w(L); self.assertTrue(all(ok), ok)

    def test_mutants(self):
        src = open(L.__file__).read()
        for old, new in (("        if any(r['ask_id'] == aid + '_W' for r in R):\n            raise SystemExit('REFUSED %s: the try was WITHDRAWN; it never runs' % aid)\n", ''),
                         ("not in ('RESULT', 'WITHDRAWN')", "!= 'RESULT'"),
                         ("            raise SystemExit('REFUSED %s: already WITHDRAWN' % aid)", "            pass"),
                         ("            raise SystemExit('REFUSED %s: a RESULT row exists; a read try cannot be withdrawn' % aid)", "            pass")):
            self.assertEqual(src.count(old), 1, old)
            m = types.ModuleType('ledger_add_v5'); m.__file__ = L.__file__; exec(compile(src.replace(old, new), 'm', 'exec'), m.__dict__)
            try:
                caught = not all(run_w(m))
            except (SystemExit, ValueError):           # the strict reader refuses what the mutant let through
                caught = True
            self.assertTrue(caught, 'mutant survived: %s' % new)


if __name__ == '__main__':
    unittest.main()
