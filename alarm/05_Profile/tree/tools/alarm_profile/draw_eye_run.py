"""tools/alarm_profile: draw a FRESH P4_EYE_RUN sample from the built EPI.A02 values (QUANT 22 Oct 2026; the owner 15:3x Berlin: a new
fresh sample, the rule unchanged, the line set before the draw). 3 alarms a month (Sep to Dec, 10-11 Oct out), drawn by seed, never one
already judged (the exclude files: any TSV with coin and t columns); the drawn order shuffled by the same seed. Writes EYE_RUN_SAMPLE.tsv
(chart, coin, t, side, minute, x_pct, start_t, burst_t, onset_t: the 24 h of minute closes before each alarm, push-signed) and
EYE_RUN_KEY.tsv (chart, coin, t, group FRESH, run_age_min, run_pct). Reads research_days (EPI.A02) and lab_days (prices); no outcome.
  python3 -B draw_eye_run.py <lab_days> <lab3 code dir> <alarms tsv> <out root> <out dir> <seed> <exclude tsv> [<exclude tsv> ...]"""
import csv, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.realpath(__file__)); sys.path.insert(0, HERE)
import alarm_profile as AP
import proof_alarm_profile as PP


def main(lab_root, code_dir, alarms_path, out_root, out_dir, seed, *excludes):
    seed = int(seed); os.makedirs(out_dir, exist_ok=True)
    ev = AP.load_alarms(alarms_path, AP.SUBJECTS['A02'][0]); evk = {(ev['coin'][i], int(ev['t'][i])): i for i in range(len(ev['t']))}
    x = AP.read(out_root, code_dir, 'A02', '20250901', '20251231'); n = len(x['coin'])
    skip = set(PP.SEEN_V1)
    for p in excludes:
        with open(p) as fh:
            skip |= {(r['coin'], int(r['t'])) for r in csv.DictReader((l for l in fh if not l.startswith('#')), delimiter='\t')}
    g = np.random.default_rng(seed); pick = []
    for mo in ('09', '10', '11', '12'):
        pool = [j for j in range(n) if PP.utc_day(x['t_alarm'][j])[4:6] == mo and PP.utc_day(x['t_alarm'][j]) not in PP.OUT_DAYS
                and np.isfinite(x['run_age_min'][j]) and np.isfinite(x['burst_s'][j]) and (x['coin'][j], int(round(x['t_alarm'][j]))) not in skip]
        pick += [pool[q] for q in g.choice(len(pool), size=min(3, len(pool)), replace=False)]
    pick = [pick[q] for q in np.random.default_rng(seed).permutation(len(pick))]
    L = PP.Loader(lab_root, code_dir)
    with open(os.path.join(out_dir, 'EYE_RUN_SAMPLE.tsv'), 'x') as fh, open(os.path.join(out_dir, 'EYE_RUN_KEY.tsv'), 'x') as fk:
        fh.write('chart\tcoin\tt\tside\tminute\tx_pct\tstart_t\tburst_t\tonset_t\n'); fk.write('chart\tcoin\tt\tgroup\trun_age_min\trun_pct\n')
        for c_i, j in enumerate(pick, 1):
            coin, t = x['coin'][j], int(round(x['t_alarm'][j])); i = evk[(coin, t)]
            side = int(ev['side'][i]); a = L.args(coin, t, int(ev['onset_t'][i]), side); te, px = a[7], a[8]
            st = t - x['run_age_min'][j] * 60; bt = t - x['burst_s'][j]; ot = t - x['onset_to_alarm_s'][j]
            for mm in range(1441):
                s_ = t - 86400 + 60 * mm; q = int(np.searchsorted(te, int(s_ * 1e6), 'right')) - 1
                xv = side * math.log(px[q]) * 100 if q >= 0 and px[q] > 0 else float('nan')
                fh.write('%d\t%s\t%d\t%d\t%d\t%.5f\t%d\t%d\t%d\n' % (c_i, coin, t, side, s_, xv, st, bt, ot))
            fk.write('%d\t%s\t%d\tFRESH\t%.1f\t%.4f\n' % (c_i, coin, t, x['run_age_min'][j], x['run_pct'][j]))
    print('EYE RUN sample: %d fresh alarms (seed %d), excluded %d already judged' % (len(pick), seed, len(skip)))


if __name__ == '__main__':
    main(*sys.argv[1:])
