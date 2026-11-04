"""Generic entry-row output projection; full remains the default.
STAMP projection excludes only trail_* keys, unused by the55 STAMP fields.
Fill and ladder calls and every returned requested calculation stay unchanged.
"""
import numpy as np
import heat_offer_v2 as PROJECTION_BASE
US=PROJECTION_BASE.US
TRAILS=PROJECTION_BASE.TRAILS
px_at=PROJECTION_BASE.px_at

def entry_row(pv, FV, LD, t, sd, lag, act, hold_s, wait_s=0, *, projection='full'):
    """t = the alarm (s); the decision at t + wait_s; the order after the execution delay lag"""
    if projection not in ('full','stamp'):raise ValueError('ENTRY_OUTPUT_PROJECTION')
    side = -sd if act == 'FADE' else sd
    t_al = int(round(float(t) * US)); t_dc = t_al + int(round(wait_s * US))
    tdec = t_dc + int(round(lag * US))
    f = FV.fill(pv, tdec, side, 'taker')
    pa, pd = px_at(pv, t_al), px_at(pv, t_dc)
    r = dict(side=side, status=f.status, t_fill=f.t_us, px_fill=f.px, wait_s=wait_s,
             move_wait_pct=side * 100.0 * (pd / pa - 1.0) if (pa == pa and pd == pd and pa > 0) else float('nan'))
    if f.status != 'FILLED':
        return r
    L = LD.ladder(pv, f, side, hold_s)
    ot = np.asarray(L['offer_t'], np.int64); ht = np.asarray(L['heat_t'], np.int64)
    r['o'] = [int((x - f.t_us) // US) if x >= 0 else -1 for x in ot]
    r['h'] = [int((x - f.t_us) // US) if x >= 0 else -1 for x in ht]
    r['end'] = bool(L.get('end', False))
    for T in (TRAILS if projection=='full' else ()):
        tr = LD.trailing(pv, f, side, T, hold_s)
        if tr['touch_t'] >= 0:
            r['trail_%g' % T] = tr['anchor'] - T
        else:
            j = int(np.searchsorted(pv.tl, f.t_us + hold_s * US, 'right')) - 1
            r['trail_%g' % T] = side * 100.0 * (pv.px[j] / f.px - 1.0) if j > f.i else 0.0
    return r
