"""make_record_v1 (BUILD2 for LAYERS, 23 Oct 2026; T04, README 069a8e993ea449cb sec 2): builds receipts/COSTS_OF_RECORD_V1.tsv ONCE from
the two cost tables named in settings/COSTS_SETTINGS_V1.json (each checked against its sha16 first): one row per (coin, hour_utc) with
book_bp = the DEARER of V1 and V4 (cost_bp - fee), its source; a coin in one table only has no row and is named in the header. The header
names both sources by sha16 and says the APPROXIMATION. Same tables, same file (sha16 printed). Uses costs_v3.make_record (labcore.costs V3 landed in this folder).
Written whole (tmp + fsync + replace).  Run: python3 make_record_v1.py"""
import json, os, sys

F = '<LAB_REPO>/forensics'
HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(F, 'team', 'RESEARCH', 'tools')); sys.path.insert(0, HERE)
import costs_v3 as costs  # noqa: E402  (labcore.costs V3, landed here)
from labcore import ids  # noqa: E402


def main():
    s = json.load(open(os.path.join(HERE, 'settings', 'COSTS_SETTINGS_V1.json')))
    v1, v4 = (os.path.join(F, s[k]['path']) for k in ('table_v1', 'table_v4'))
    for k, p in (('table_v1', v1), ('table_v4', v4)):
        if ids.sha16_file(p) != s[k]['sha16']:
            raise SystemExit('%s %s: sha16 %s, settings pin %s: refused' % (k, p, ids.sha16_file(p), s[k]['sha16']))
    rows, only = costs.make_record(v1, v4, fee_bp=2 * 100.0 * s['fee_side_pct'])
    out = os.path.join(F, s['record']['path']); tmp = out + '.tmp'
    head = ['# COSTS_OF_RECORD_V1 (make_record_v1 %s, settings %s): book_bp = the DEARER of V1 %s and V4 %s (cost_bp - fee), STRATEGY Q1'
            % (ids.sha16_file(__file__), ids.sha16_file(os.path.join(HERE, 'settings', 'COSTS_SETTINGS_V1.json')), s['table_v1']['sha16'], s['table_v4']['sha16']),
            '# APPROXIMATION: %s' % s['approximation'], '# %s' % only]
    with open(tmp, 'w') as f:
        f.write('\n'.join(head) + '\ncoin\thour_utc\tbook_bp\tsource\n')
        f.write(''.join('%s\t%d\t%.3f\t%s\n' % (c, h, b, src) for (c, h), (b, src) in sorted(rows.items())))
        f.flush(); os.fsync(f.fileno())
    os.replace(tmp, out)
    v4n = sum(1 for v in rows.values() if v[1] == 'V4')
    print('COSTS_OF_RECORD_V1.tsv', ids.sha16_file(out), 'rows', len(rows), 'V4 dearer', v4n, 'V1 dearer', len(rows) - v4n, '|', only)


if __name__ == '__main__':
    main()
