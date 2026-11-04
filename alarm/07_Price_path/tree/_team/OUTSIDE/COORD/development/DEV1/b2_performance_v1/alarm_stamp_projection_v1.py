"""Generic STAMP projection successor; original55 fields and default full work.
No original module globals are modified. All other public functions/constants
are reused from the original STAMP module and bound in the source manifest.
"""
from alarm_stamp import *
import alarm_stamp as PROJECTION_BASE
import heat_offer_projection_v1 as HO

def one_entry(pv, FV, LD, loaded, t_alarm, side, direction, wait_s, delay, hold, *, entry_projection='full'):
    """-> {name: (value or None, reason)} of one alarm x decision x direction"""
    r = HO.entry_row(pv, FV, LD, t_alarm, side, delay, direction, hold, wait_s, projection=entry_projection)
    out = {'move_wait_pct': (r.get('move_wait_pct'), '')}
    if r['status'] != 'FILLED':
        out['filled'] = (0.0, r['status'])
        for nm in NAMES:
            if nm not in out:
                out[nm] = (None, r['status'])
        return out
    t_dec_us = int(round(float(t_alarm) * 1e6)) + int(round(wait_s * 1e6)) + int(round(delay * 1e6))
    known = min(float(hold), (known_end_us(loaded, r['t_fill']) - r['t_fill']) / 1e6)
    out.update(filled=(1.0, ''), fill_wait_s=((r['t_fill'] - t_dec_us) / 1e6, ''), known_s=(known, ''), fill_px=(float(r['px_fill']), ''))
    for k, L in enumerate(LEVELS):
        for key, nm in (('o', 'ot_%02d'), ('h', 'ht_%02d')):
            s = r[key][k]
            out[nm % round(L * 10)] = (float(s), '') if 0 <= s <= known else (None, NOT_REACHED)
    return out
