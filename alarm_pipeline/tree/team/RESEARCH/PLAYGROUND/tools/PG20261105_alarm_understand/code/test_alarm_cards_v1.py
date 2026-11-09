#!/usr/bin/env python3
"""test_alarm_cards_v1.py (SCO-A150, 6 Nov 2026): C1-C9 on PLANTED data only (no real data read). Written before the first real card.
C1 contract (TSV columns, 8 Q rows + AFTER + GRADE per card)  C2 missing input -> UNKNOWN naming it  C3 Q6 UNKNOWN names the absorber
C4 no look-ahead (readings with known_at > t never move Q1-Q5)  C5 the Q3 rule (BTC-led / market)  C6 SOLID needs every month's sign
C7 a trade-side word anywhere -> REFUSED SIDE_WORD, nothing written  C8 window (JANAPR refused)  C9 the after-the-fire line stays out of Q1/Q5
C10 readings_builder FORCED: log 0 = no liquidation (0 USD)."""
import sys
sys.dont_write_bytecode = True
import csv, datetime as dt, importlib.util, io, os, contextlib, random, shutil, time
HERE = os.path.dirname(os.path.realpath(__file__))
sp = importlib.util.spec_from_file_location('alarm_cards_t', os.path.join(HERE, 'alarm_cards_v1.py'))
AC = importlib.util.module_from_spec(sp); sp.loader.exec_module(AC)
SCR = os.path.join(HERE, '..', 'scratch', 'cards_%s_%d' % (time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()), os.getpid()))
MONTHS = [(2025, 9), (2025, 10), (2025, 11), (2025, 12)]


def ts(y, m, d, h, mi=0):
    return int(dt.datetime(y, m, d, h, mi, tzinfo=dt.timezone.utc).timestamp())


def plant(name, forced_good=(1, 1, 1, 1), btc_hi=False, basket_hi=False, readings=True, forced=True, after_junk=False, seed=1):
    rnd = random.Random(seed); d = os.path.join(SCR, name); os.makedirs(d)
    fires = []
    for mi, (y, m) in enumerate(MONTHS):
        for k in range(40):
            t = ts(y, m, 12 + k % 15, (k * 5) % 24, (k * 7) % 60)
            fires.append(('C%d' % (k % 9), t, -1, mi))
            if k % 4 == 0:
                fires.append(('D%d' % (k % 5), t + 120, -1, mi))      # same event, second coin
    with open(os.path.join(d, 'FIRES.tsv'), 'w') as f:
        f.write('alarm_id\tcoin\tt\tside\n'); [f.write('X\t%s\t%d\t%d\n' % (c, t, s)) for c, t, s, _ in fires]
    with open(os.path.join(d, 'MONEY.tsv'), 'w') as f:
        f.write('coin\tt\tside\texit\tfade_gross_15m\tfade_gross_1h\tfade_gross_4h\tnet\tedge_tough\tknown_at\tafter\n')
        for c, t, s, _ in fires:
            f.write('%s\t%d\t%d\tHOLD_1h\t0\t%r\t0\t%r\t\t%d\t1\n' % (c, t, s, rnd.uniform(0, 1.5), rnd.gauss(0.05, 0.5), t + 7200))
    if readings:
        with open(os.path.join(d, 'READINGS.tsv'), 'w') as f, open(os.path.join(d, 'MATCH_PARENT.tsv'), 'w') as g:
            f.write('who\tcoin\tt\tcode\tvalue\tknown_at\n'); g.write('coin\tt\tparent_t\n')
            for c, t, s, mi in fires:
                good = forced_good[mi]
                vals = dict(forced_log_usd_15m=rnd.gauss(5.0 if good else 2.0, 0.3), btc_move_15m=rnd.gauss(3 if btc_hi else 0, 0.3),
                            basket_move_15m=rnd.gauss(3 if basket_hi else 0, 0.3), basis_push_bp=rnd.gauss(0, 1), move_15m=rnd.uniform(1, 2),
                            fills_one_sided=rnd.uniform(0.5, 1), fires_other_60m=rnd.randint(0, 9))
                for code, v in vals.items():
                    f.write('FIRE\t%s\t%d\tCTX.%s\t%r\t%d\n' % (c, t, code, v, t))
                    if after_junk:
                        f.write('FIRE\t%s\t%d\tCTX.%s\t%r\t%d\n' % (c, t, code, 1e9, t + 60))
                for j in range(5):
                    mt = t - 86400 * (j + 1) + 0.5
                    g.write('%s\t%r\t%d\n' % (c, mt, t))
                    mv = dict(forced_log_usd_15m=rnd.gauss(3.5, 0.3), btc_move_15m=rnd.gauss(0, 0.3), basket_move_15m=rnd.gauss(0, 0.3),
                              basis_push_bp=rnd.gauss(0, 1), move_15m=rnd.uniform(0, 1), fills_one_sided=rnd.uniform(0.4, 1), fires_other_60m=rnd.randint(0, 9))
                    for code, v in mv.items():
                        f.write('MATCH\t%s\t%r\tCTX.%s\t%r\t%r\n' % (c, mt, code, v, mt))
    if forced:
        with open(os.path.join(d, 'FORCED.tsv'), 'w') as f:
            f.write('coin\tt\tlong_usd\tshort_usd\tknown_at\n')
            for c, t, s, mi in fires:
                f.write('%s\t%d\t%r\t%r\t%d\n' % (c, t, 9000.0, 100.0 if forced_good[mi] else 20000.0, t))
    return d


def config(name, rows):
    p = os.path.join(SCR, name + '.tsv')
    with open(p, 'w') as f:
        f.write('alarm\tblock\tbundle\treadings\tgrade_key\n'); [f.write('\t'.join(r) + '\n') for r in rows]
    return p


def go(out, mech, cfg, grades=''):
    b = io.StringIO()
    with contextlib.redirect_stdout(b):
        rc = AC.main([out, '--mechanism', mech, '--config', cfg] + (['--grades', grades] if grades else []))
    return rc, b.getvalue()


def rows_of(out, mech):
    return list(csv.DictReader(open(os.path.join(out, 'ALARM_CARDS_%s.tsv' % mech)), delimiter='\t'))


RES = []


def check(name, ok, detail=''):
    RES.append((name, bool(ok))); print('%s %s %s' % ('PASS' if ok else 'FAIL', name, detail))


def main():
    os.makedirs(SCR)
    a = plant('A'); b = plant('B', forced_good=(1, 1, 1, 0), seed=2); c = plant('C', readings=False, forced=False, seed=3)
    g = os.path.join(SCR, 'GRADES.tsv')
    with open(g, 'w') as f:
        f.write('alarm\tstate\tlead_15m\tt_15m\tlead_1h\tt_1h\twaves\tmonths_counted\tmonths_passing\tgrade_job\n')
        f.write('A\tPASS\t+10\t+3.5\t+9\t+3.1\t100\t4\t4\tJ1\nB\tPASS\t+5\t+2.0\t+4\t+1.9\t100\t4\t3\tJ2\n')
    cf = config('cfg1', [('PG_A', 'SEPDEC', a, a, 'A'), ('PG_B', 'SEPDEC', b, b, 'B'), ('PG_C', 'SEPDEC', c, '-', '-')])
    out = os.path.join(SCR, 'out1'); rc, txt = go(out, 'MECH', cf, g)
    check('C1 runs', rc == 0, txt[-300:])
    R = rows_of(out, 'MECH') if rc == 0 else []
    check('C1 columns', R and list(R[0].keys()) == list(AC.TSV_COLS))
    per = {}
    for r in R:
        per.setdefault(r['alarm'], []).append(r['q'])
    check('C1 rows per card', all(v == ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'GRADE'] for v in per.values()) and len(per) == 3, per)
    get = lambda al, q: ([r for r in R if r['alarm'] == al and r['q'] == q] or [dict(strength='', answer='', number='')])[0]
    check('C2 missing READINGS named', all(get('PG_C', q)['strength'] == 'UNKNOWN' and 'READINGS.tsv' in get('PG_C', q)['answer'] for q in ('Q3', 'Q4', 'Q5')))
    check('C2 missing FORCED named', get('PG_C', 'Q1')['strength'] == 'UNKNOWN' and 'FORCED.tsv' in get('PG_C', 'Q1')['answer'])
    check('C2 grade missing', get('PG_C', 'GRADE')['strength'] == 'UNKNOWN')
    check('C3 Q6 UNKNOWN absorber', all(get(x, 'Q6')['strength'] == 'UNKNOWN' and 'absorber' in get(x, 'Q6')['answer'] for x in per))
    check('C6 SOLID all months', get('PG_A', 'Q4')['strength'] == 'SOLID' and get('PG_A', 'Q1')['strength'] == 'SOLID',
          (get('PG_A', 'Q4')['strength'], get('PG_A', 'Q4')['number']))
    check('C6 one month opposite -> WEAK', get('PG_B', 'Q4')['strength'] == 'WEAK' and get('PG_B', 'Q1')['strength'] == 'WEAK',
          (get('PG_B', 'Q4')['strength'], get('PG_B', 'Q1')['strength']))
    check('C9 after line apart', all(not any(w in get(x, q)['answer'].lower() for w in ('retained', 'temporary', 'permanent'))
                                     for x in per for q in ('Q1', 'Q5')) and 'after the fire (description): Impact retained' in open(os.path.join(out, 'ALARM_CARDS_MECH.md')).read())
    # C4 look-ahead
    a2 = plant('A2', after_junk=True)
    cf2 = config('cfg2', [('PG_A', 'SEPDEC', a2, a2, 'A')]); out2 = os.path.join(SCR, 'out2'); rc2, _ = go(out2, 'MECH', cf2, g)
    R2 = rows_of(out2, 'MECH') if rc2 == 0 else []
    same = rc2 == 0 and all([r for r in R2 if r['q'] == q][0]['number'] == get('PG_A', q)['number'] for q in ('Q1', 'Q2', 'Q3', 'Q4', 'Q5'))
    check('C4 AFTER readings never used', same)
    # C5 Q3 rule
    bt = plant('BT', btc_hi=True, seed=4); bk = plant('BK', basket_hi=True, seed=5)
    cf3 = config('cfg3', [('PG_BT', 'SEPDEC', bt, bt, '-'), ('PG_BK', 'SEPDEC', bk, bk, '-')]); out3 = os.path.join(SCR, 'out3'); rc3, _ = go(out3, 'MECH', cf3)
    R3 = rows_of(out3, 'MECH') if rc3 == 0 else []
    q3 = {r['alarm']: r['answer'] for r in R3 if r['q'] == 'Q3'}
    check('C5 Q3 BTC-led', q3.get('PG_BT', '').startswith('The move is mostly BTC-led'), q3.get('PG_BT', '')[:60])
    check('C5 Q3 market', q3.get('PG_BK', '').startswith('The move is mostly market'), q3.get('PG_BK', '')[:60])
    # C7 side word
    cf4 = config('cfg4', [('PG_FOLLOWX', 'SEPDEC', a, a, '-')]); out4 = os.path.join(SCR, 'out4'); rc4, t4 = go(out4, 'MECH', cf4)
    check('C7 side word refused', rc4 == 2 and 'SIDE_WORD' in t4 and not os.path.exists(os.path.join(out4, 'ALARM_CARDS_MECH.tsv')), t4.strip())
    md1 = open(os.path.join(out, 'ALARM_CARDS_MECH.md')).read(); pb = md1.split('## Part B')[1]
    check('C11 Part B 4 lines, no stage 2', sum(1 for l in pb.splitlines() if l[:2] in ('1.', '2.', '3.', '4.', '5.')) == 4 and 'stage 2 questions' not in pb.lower())
    check('C7 real output clean', all(w not in open(os.path.join(out, 'ALARM_CARDS_MECH.md')).read().lower() for w in AC.SIDE_WORDS))
    check('C12 a sha16 holding fade is no side word', AC.side_hits('READINGS.tsv b10252c8fade7ae8 x') == [] and AC.side_hits('fade the move') == ['fade']
          and AC.side_hits('xb10252c8fade7ae8') == ['fade'])
    # C8 window
    cf5 = config('cfg5', [('PG_A', 'JANAPR', a, a, '-')]); rc5, t5 = go(os.path.join(SCR, 'out5'), 'MECH', cf5)
    check('C8 JANAPR refused', rc5 == 2 and 'BAD_BLOCK' in t5, t5.strip())
    # C10 readings builder FORCED
    sp2 = importlib.util.spec_from_file_location('rb_t', os.path.join(HERE, 'readings_builder_v1.py'))
    RB = importlib.util.module_from_spec(sp2); sp2.loader.exec_module(RB)
    src = open(os.path.join(HERE, 'readings_builder_v1.py')).read()
    check('C10 log 0 is none', '(0.0 if x == 0 else 10 ** x)' in src and 'coin_move_15m' in RB.VALUES[3])
    n = sum(ok for _, ok in RES); print('RESULT %d of %d' % (n, len(RES))); return 0 if n == len(RES) else 1


if __name__ == '__main__':
    sys.exit(main())
