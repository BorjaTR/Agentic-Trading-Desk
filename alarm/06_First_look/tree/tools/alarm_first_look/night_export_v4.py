# night_export_v4.py (SCOUT 2 Nov 2026, V1_19_FIRSTLOOK): night_export_v3.py 76d823544593ef84 with only the outcome module taken from the path given.
"""night_export_v3.py (STRATEGY, 30 Oct 2026; v1 compared numpy arrays with ==, which raised; v2 wrote numpy floats as np.float64(x); v3 writes plain numbers). TEST, NOT REVIEWED. Reads one committed outcome run (event_outcomes_aw1) with the tool's own
reader and writes one wide TSV, one row per fire: coin, as_of_us, then every catalog column's value (FADE and FOLLOW labels, unit columns),
plus <column>__why for empty cells. Never edits the run.
  python3 night_export_v3.py <om_root> <lab3 code dir> <event_outcomes_aw1.py> <SUBJECT> <out.tsv>"""
import importlib, os, sys, math


def main(root, code, eo, subject, outp):
    if os.path.exists(outp):
        raise SystemExit('OUTPUT EXISTS %s' % outp)
    sys.path.insert(0, os.path.dirname(eo))
    E = importlib.import_module(os.path.basename(eo)[:-3])   # V1_19: the edition named by <event_outcomes.py>, event_outcomes_aw1_rel1 in the release
    d = E.read(root, code, subject, None)
    cols = sorted(d)
    n = len(d[cols[0]]['coin'])
    for c in cols:
        assert len(d[c]['coin']) == n and list(d[c]['coin']) == list(d[cols[0]]['coin']) and list(d[c]['as_of_us']) == list(d[cols[0]]['as_of_us']), c
    lines = []
    for i in range(n):
        row = [d[cols[0]]['coin'][i], str(int(d[cols[0]]['as_of_us'][i]))]
        for c in cols:
            v = d[c]['value'][i]
            if isinstance(v, float):
                row.append('' if not math.isfinite(v) else repr(float(v))); row.append('' if math.isfinite(v) else str(d[c]['reason'][i]))
            else:
                row.append(str(v)); row.append(str(d[c]['reason'][i]) if v == '' else '')
        lines.append('\t'.join(row) + '\n')
    with open(outp, 'w') as f:
        f.write('\t'.join(['coin', 'as_of_us'] + [x for c in cols for x in (c, c + '__why')]) + '\n')
        f.writelines(lines)
    print('rows %d columns %d -> %s' % (n, len(cols), outp))


if __name__ == '__main__':
    main(*sys.argv[1:6])
