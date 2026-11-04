"""labcore.tick_stores (QUANT, 23 Oct 2026; LAB1 12:21:19Z: one reader each, into labcore, for the four stores QUANT owns; TOOL_DESIGN V4.1
0c(c)). The ONE reader of: hl_mark_2025, hl_funding_2025, hl_oi_2025 (Hyperliquid, from Tardis derivative_ticker by exact file name) and
oi6_2025 (Binance open interest about every 6 s). Each file: <DATA_ROOT>/<store>/<COIN>_<YYYYMMDD>.npz with t_us (int64,
microseconds, exchange stamp) and one value array. TRAP (KIT_V1 gap line): the v1 extracts of hl_mark_2025 and hl_funding_2025 hold their
value under the key 'oi' although it is the MARK PRICE resp. the FUNDING RATE (not open interest); this reader returns it under its true
name. Days refused by lab3/law.py are refused here (read from law.py). A missing file is EMPTY (NaN), never 0."""
import os
import numpy as np
from . import gates

ROOT = '<DATA_ROOT>'
STORES = {   # store: (key in the file, true name, unit, coin naming, first day, last day)
    'hl_mark_2025': ('oi', 'mark_px', 'USD price', 'Hyperliquid coin (kSHIB style)', '20250911', '20251231'),
    'hl_funding_2025': ('oi', 'funding_rate', 'fraction per hour (Hyperliquid)', 'Hyperliquid coin', '20250912', '20251231'),
    'hl_oi_2025': ('open_interest', 'open_interest', 'coins (Tardis as given; unit undocumented by Hyperliquid)', 'Hyperliquid coin', '20250911', '20251231'),
    'oi6_2025': ('oi', 'open_interest', 'coins (Binance USDT-M, about every 6 s)', 'Binance symbol (1000BONKUSDT style)', '20250911', '20251231'),
}


def path_of(store, coin, day, root=ROOT):
    return os.path.join(root, store, '%s_%s.npz' % (coin, day))


def read_day(store, coin, day, root=ROOT, law=None):
    """-> (t_us int64, value float64, true name) sorted by time; empty arrays when the file is missing; refused (PermissionError) when
    lab3/law.py refuses the day"""
    key, name = STORES[store][0], STORES[store][1]
    law = law or gates.load_law(); why = law.research_refusal(day)
    if why:
        raise PermissionError('%s %s: refused by lab3/law.py: %s' % (store, day, why))
    p = path_of(store, coin, day, root)
    if not os.path.exists(p):
        return np.zeros(0, np.int64), np.zeros(0, float), name
    z = np.load(p); t = np.asarray(z['t_us'], np.int64); v = np.asarray(z[key], float); o = np.argsort(t, kind='mergesort')
    return t[o], v[o], name


def value_at(store, coin, ts_s, delay_s=None, max_age_s=None, root=ROOT, law=None):
    """as-of values under a MODELLED availability: the last row with exchange time e <= t - delay_s for each second in ts_s (SKEPTIC 02-06:
    exchange time is not known time; A04-03: exchange time + a delay is MODEL_AVAILABLE_AT, not observed availability; decision code uses
    value_at_checked, which records the model and refuses uses that need observed availability). delay_s is required (seconds, finite,
    >= 0); None is refused. NaN when no row is known that day (or the
    known row's exchange time is older than max_age_s); reads each day once"""
    if delay_s is None or not np.isfinite(float(delay_s)) or float(delay_s) < 0:
        raise ValueError('%s: delay_s %r: availability unknown: refused (state the delay; exchange time is not known time)' % (store, delay_s))
    ts_s = np.asarray(ts_s, float); out = np.full(len(ts_s), np.nan); dus = int(round(float(delay_s) * 1e6))
    days = np.array([np.datetime_as_string(np.datetime64(int(t), 's'), unit='D').replace('-', '') for t in ts_s])
    law = law or gates.load_law()
    for d in np.unique(days):
        t, v, _ = read_day(store, coin, d, root, law); sel = np.flatnonzero(days == d)
        if len(t) == 0:
            continue
        tu = np.round(ts_s[sel] * 1e6).astype(np.int64); j = np.searchsorted(t + dus, tu, side='right') - 1; ok = j >= 0
        if max_age_s is not None:
            ok &= (tu - t[np.maximum(j, 0)]) <= max_age_s * 1e6
        out[sel[ok]] = v[j[ok]]
    return out


RECEIPT_CLOCK = {s: None for s in STORES}      # A04-03 rule 3: none of the four extracts kept a receipt (arrival) clock: exchange time only
MODEL_KEYS = ('delay_s', 'scope', 'breach_policy', 'source')


def value_at_checked(store, coin, ts_s, model, require='MODEL', max_age_s=None, root=ROOT, law=None):
    """A04-03 (OUTSIDE APPROVAL labcore 36029bb9, rule 3): values with their availability kind. These stores have no receipt clock, so a
    value is MODEL_AVAILABLE_AT (exchange time + the model's delay: a conditional simulation, never observed availability). model: {delay_s,
    scope (calibration scope), breach_policy, source (the measured receipt it comes from, by sha16)}; missing keys are refused.
    require='OBSERVED' (a use that needs observed per-row availability) is refused while RECEIPT_CLOCK[store] is None.
    -> (values, meta) with meta = {availability, model}"""
    if require not in ('MODEL', 'OBSERVED'):
        raise ValueError('require must be MODEL or OBSERVED: refused')
    miss = [k for k in MODEL_KEYS if k not in (model or {})]
    if miss:
        raise ValueError('%s: availability model lacks %s: refused (rule 3: delay, calibration scope, breach policy, source)' % (store, miss))
    for key in ('scope', 'breach_policy', 'source'):
        if not isinstance(model[key], str) or not model[key].strip():
            raise ValueError('availability model %s must be a nonempty description/identity: refused' % key)
    if require == 'OBSERVED' and RECEIPT_CLOCK.get(store) is None:
        raise PermissionError('%s: no receipt clock recorded: observed availability UNKNOWN, refused for this use' % store)
    v = value_at(store, coin, ts_s, delay_s=model['delay_s'], max_age_s=max_age_s, root=root, law=law)
    return v, {'availability': 'MODEL_AVAILABLE_AT', 'model': dict(model)}


def late_stress(store, coin, ts_s, model, extra_s, max_age_s=None, root=ROOT, law=None):
    """rule 3 tail stress: the same read with the delay raised by extra_s (late arrivals beyond the model) -> values"""
    return value_at(store, coin, ts_s, delay_s=float(model['delay_s']) + float(extra_s), max_age_s=max_age_s, root=root, law=law)
