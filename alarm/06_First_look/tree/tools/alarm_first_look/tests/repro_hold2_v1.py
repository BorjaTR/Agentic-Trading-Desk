"""repro_hold2_v1.py (SCOUT 2 Nov 2026): GPT's gpt_fl12_result_scope.py admission case (HOLD 2, 10:30:53Z): a one-row A/R pair, a true manifest, only the A file's threshold changed 1.2 -> 9.0. Reader's and ladder's route is bars_of.
Exit 1 = the changed table is accepted (the hold reproduces), 0 = refused before any verdict.   python3 -B tests/repro_hold2_v1.py"""
import gzip, hashlib, json, os, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import bar_v1 as B, fl_read_v12 as E, numpy as np
dg = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
SET = {'exhausted_max': B.EXHAUSTED_MAX, 'fee_bp': B.FEE_BP, 'gap_bp': B.GAP_BP, 'h_min': B.H_MIN, 'k_cost': B.K_COST, 'line_days': B.LINE_DAYS, 'line_min_n': B.LINE_MIN_N, 'line_q': B.LINE_Q, 'valued_min': B.VALUED_MIN}
with tempfile.TemporaryDirectory() as d:
    lst = {'coin': np.array(['TEST']), 't': np.array([123])}; man = {'version': 'bar_v1', 'settings': SET, 'lists': {}}; hdr = '\t'.join(B.HEAD) + '\n'

    def put(k, b):
        p = os.path.join(d, 'BAR_%s_T00.tsv.gz' % k)
        with gzip.open(p, 'wt') as f:
            f.write(hdr + 'TEST\t123\t0.2\t1\t336\t%s\t\n' % b)
        return p
    for k in 'AR':
        p = put(k, 1.2); man['lists'][k + '_T00'] = {'list': ['fixture', k], 'rows': 1, 'why': {'KNOWN': 1}, 'out': [os.path.basename(p), dg(p)]}
    mf = os.path.join(d, 'BAR_V1.json'); json.dump(man, open(mf, 'w')); fixed = dg(mf)
    get = lambda: E.bars_of('T00', {'A_sha16': 'A', 'R_sha16': 'R'}, d, lst, lst)[0]['A'][0][0]
    print('genuine', get()); assert get() == 1.2
    p = put('A', 9); assert dg(mf) == fixed
    try:
        print('changed table ACCEPTED at', get(), 'manifest unchanged', fixed, '\nHOLD 2 REPRODUCES'); sys.exit(1)
    except E.M.Refused as e:
        print('changed table REFUSED:', e, '\nHOLD 2 FIXED')
