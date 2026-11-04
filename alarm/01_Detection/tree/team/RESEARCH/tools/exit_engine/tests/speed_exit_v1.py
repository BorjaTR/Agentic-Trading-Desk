"""TEST2 speed_exit_v1 (23 Oct 2026): the SPEED row of T03 exit_engine (README V2.4 section 8). Times the ENGINE on the real store:
every A02N trade of the given window (entry = fire + 6 s, side +1: speed does not depend on the side) under one exit row (EXIT_T1), on
1 process: bar < 180 s. Coin-days are read once each (engine.bars), trades grouped by coin-day, the walk vectorised over them.
Prints ONLY counts and seconds: no return, no kind count, no outcome value is printed or written (an engineering timing, read by no
decision). Run under taskpolicy -b nice -n 10. Usage: speed_exit_v1.py <lab_days> <research_days> <lab3 code> <first YYYYMMDD> <last>"""
import os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE)
import engine_iface_v1 as E

BAR_US = 3_000_000; DAY_US = 86_400_000_000; BAR_S = 180.0


def main(lab, rdays, code, first, last):
    sys.path.insert(0, os.path.join(E.TOOLS, 'alarm_profile')); sys.path.insert(0, code)
    import alarm_profile as AP
    eng = E.engine(); row = eng.load_exits(os.path.join(E.TOOL, 'EXITS_V1.tsv'))['EXIT_T1']
    t = time.time()
    F = AP.read(rdays, code, 'A02N', first, last, values=['normal_move_pct'])
    t_read = time.time() - t
    coin = np.asarray(F['coin']); ta = np.round(np.asarray(F['t_alarm'], float)).astype(np.int64) * 1_000_000
    nm = np.asarray(F['normal_move_pct'], float); ok = np.isfinite(nm)
    coin, ta, nm = coin[ok], ta[ok], nm[ok]
    entry_us = ta + 6_000_000; day0 = entry_us // DAY_US * DAY_US
    hold = int(round(float(row['time_limit_min']) * 20)) + 2
    t = time.time(); n_tr = 0; n_grp = 0; refused = 0
    for key in sorted(set(zip(coin.tolist(), day0.tolist()))):
        sel = np.nonzero((coin == key[0]) & (day0 == key[1]))[0]
        g0 = key[1]; g1 = int(entry_us[sel].max()) + hold * BAR_US
        try:
            te, c, h, l = eng.bars(lab, key[0], g0 + BAR_US, g1)
        except Exception:
            refused += len(sel); continue
        eb = ((entry_us[sel] - (g0 + BAR_US)) // BAR_US).astype(np.int64)
        good = np.isfinite(c[eb])
        if not good.any():
            continue
        s = sel[good]; eb = eb[good]
        eng.simulate(c, h, l, eb, c[eb], np.ones(len(s), int), row, units={'nm': nm[s], 'known_at_us': ta[s]},
                     t0_us=int(te[0]), signal_us=ta[s])
        n_tr += len(s); n_grp += 1
    t_walk = time.time() - t
    print('SPEED T03 A02N %s..%s EXIT_T1: trades %d, coin-days %d, refused or unread %d, read EPI %.1f s, bars+walk %.1f s, total %.1f s,'
          ' bar %.0f s: %s' % (first, last, n_tr, n_grp, refused, t_read, t_walk, t_read + t_walk, BAR_S,
                                'PASS' if t_read + t_walk < BAR_S else 'FAIL'))


if __name__ == '__main__':
    main(*sys.argv[1:6])
