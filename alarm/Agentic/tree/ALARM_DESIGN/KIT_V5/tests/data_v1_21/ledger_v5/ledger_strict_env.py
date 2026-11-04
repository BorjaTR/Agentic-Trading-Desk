"""fixtures for the strict ledger readers (OUTSIDE C08-02: exact width, valid stamps, unique ask_id): like test_ledger_add_v4.env and
run_all, but the old door row is a full 19-column row with a real stamp (the real ledger has no short rows: checked 23 Oct, 95 rows)."""
import os, tempfile
import test_ledger_add_v4 as T4
C1, C2 = T4.C1, T4.C2
OLD = '\t'.join(['20261020T120000Z', 'row', 'X', 'p', 'door'] + [''] * 14)


def env(M):
    d = tempfile.mkdtemp(); led = os.path.join(d, 'L.tsv'); s = os.path.join(d, 's.md'); r = os.path.join(d, 'r.txt')
    open(s, 'w').write('rule v1'); open(r, 'w').write('result')
    open(led, 'w').write(M.HEADER + '\t'.join(M.COLS) + '\n' + OLD + '\n'); return led, s, r


def run_all(M):
    led, s, r = env(M); ok = []; refused = T4.refused
    ok.append(refused(lambda: M.result('PREREG_X_20261023T063000Z', r, 'PASS', s, path=led, clock=C1)))
    aid = M.prereg('X', 'test', s, path=led, clock=C1) if 'ttype' not in M.prereg.__code__.co_varnames else \
        M.prereg('X', 'test', s, path=led, clock=C1, ttype='GROUPING', family='A02P', types_path=os.path.join(os.path.dirname(led), 'T.tsv'))
    ok.append(aid == 'PREREG_X_20261023T063000Z')
    old = os.path.join(os.path.dirname(led), 'old.txt'); open(old, 'w').write('stale'); os.utime(old, (C1.timestamp() - 3600,) * 2)
    ok.append(refused(lambda: M.result(aid, old, 'PASS', s, path=led, clock=C2)))
    ok.append(refused(lambda: M.result(aid, r, 'GREAT', s, path=led, clock=C2)))
    M.result(aid, r, 'FAIL', s, path=led, clock=C2)
    ok.append(refused(lambda: M.result(aid, r, 'PASS', s, path=led, clock=C2)))
    ok.append(open(led).read().splitlines()[2] == OLD)
    return ok
