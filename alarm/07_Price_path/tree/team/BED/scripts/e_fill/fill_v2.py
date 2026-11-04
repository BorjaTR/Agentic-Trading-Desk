"""E-FILL v2 (BED, 16 Oct 2026; EDGE1's tester must 09:42:30Z; tests test_fill_v2.py first) = v1 with: money_pct(side, px_in, px_out, fee,
slip_in, slip_out): the entry's slippage as of the entry decision and the EXIT's as of the exit decision (D5 ed. 4, BED-H6: the book at a
settle is thinner); 'slip' (v1) still gives both the same; PriceView checks equal lengths and t_end >= t_last; load_px3s2 reads files
unguarded, for BED's cloud build only (the lab reads prices through SP2 and its guard); a maker ask when no close comes in time is
NO_FILL, not REFUSED (the checks run in order). v1's text follows.
E-FILL v1: THE FILL AND ITS COSTS (BED, 16 Oct 2026; LAB_ARCH_V6 ed. 5 D5, D10, 13.5 EXECUTION; R40 to R42, R57, R58; tests first:
test_fill_v1.py). Built and tested on PX3S v2 arrays (E-PX2); the lab runs the same functions on the store's arrays (SP2).
TIME: int64 microseconds at every boundary (ed. 3 row 106); PX3S's ms only inside the files (load_px3s2 converts).
FILL (D5): the first close whose LAST TRADE time is strictly after tau + delay (never the bin end). Checks, in order:
  NO_DATA  no prices for the coin;
  STALE    the last trade at or before tau is older than stale_us (60 s);
  NO_FILL  no close within max_wait_us (60 s) after tau + delay;
  GAP      two consecutive closes more than 40 s apart between the last close at or before tau + delay and the fill;
  REFUSED  mode 'maker' (D10: refused until trade data shows a trade THROUGH the limit);
  FILLED   else, at that close's price.
EXITS (D5 ed. 5): an exit always fills, at the first close after its decision + delay however late: LATE_EXIT when later than max_wait or
  across a gap, END when no close follows (the data ends: the trade is CUT, counted). A TOUCH IS NOT A FILL: a stop or a target touched at
  t_touch fills as a taker at the first close after t_touch + delay (fill_after_touch), whatever the level was.
BENCH ENTRY (KA1, mode 'bench'): the last close at or before t (the bench's opportunity()).
COSTS (D10 ed. 5): fee per side 0.045% (taker); slippage x1 until measured = the coin's median 3 s bin range (hi - lo) / close over the
  bins whose last trade is in (t - 1 h, t] (as of the decision), applied against the trade at each fill; x2 shown by the caller.
MONEY in percent of the entry notional: long 100 x (exit / entry - 1), short -100 x (exit / entry - 1), fees on both sides' notional."""
import gzip, os
from dataclasses import dataclass
import numpy as np

US = 1_000_000
GAP_US = 40 * US
FEE_TAKER = 0.00045


@dataclass(frozen=True)
class Fill:
    status: str
    t_us: int = None
    px: float = None
    i: int = None
    wait_us: int = None


class PriceView:
    """one coin's 3 s bins over a span of days: te_us (bin end), tl_us (last trade), px (close), hi, lo; int64 us, float64 prices"""
    def __init__(self, coin, te_us, tl_us, px, hi, lo):
        self.coin = coin
        self.te = np.asarray(te_us, np.int64); self.tl = np.asarray(tl_us, np.int64)
        self.px = np.asarray(px, np.float64); self.hi = np.asarray(hi, np.float64); self.lo = np.asarray(lo, np.float64)
        if not (len(self.te) == len(self.tl) == len(self.px) == len(self.hi) == len(self.lo)):
            raise ValueError(f'{coin}: arrays of different lengths')
        if len(self.tl) and np.any(self.te < self.tl):
            raise ValueError(f'{coin}: a bin ends before its last trade')
        if len(self.tl) and np.any(np.diff(self.tl) < 0):
            raise ValueError(f'{coin}: last-trade times not in order')

    @classmethod
    def empty(cls, coin):
        z = np.zeros(0)
        return cls(coin, z.astype(np.int64), z.astype(np.int64), z, z, z)

    def __len__(self):
        return len(self.tl)


def load_px3s2(folder, coin, days):
    """PriceView from PX3S2_<coin>_<day>.tsv(.gz) files of the given days (in order; a missing day is skipped and returned in 'missing')"""
    parts, missing = [], []
    for d in days:
        p = os.path.join(folder, f'PX3S2_{coin}_{d}.tsv')
        p = p + '.gz' if os.path.exists(p + '.gz') else p
        if not os.path.exists(p):
            missing.append(d); continue
        with (gzip.open(p, 'rt') if p.endswith('.gz') else open(p)) as f:
            head = f.readline().rstrip('\n').split('\t')
            if head != ['t_end', 't_last_ms', 'px', 'n', 'buy_usd', 'sell_usd', 'hi', 'lo']:
                raise ValueError(f'{p}: header {head}')
            a = np.loadtxt(f, delimiter='\t', dtype=np.float64, ndmin=2)
        if len(a):
            parts.append(a)
    if not parts:
        return PriceView.empty(coin), missing
    a = np.concatenate(parts)
    te = a[:, 0].astype(np.int64) * US; tl = a[:, 1].astype(np.int64) * 1000
    return PriceView(coin, te, tl, a[:, 2], a[:, 6], a[:, 7]), missing


def _int_us(t):
    if not isinstance(t, (int, np.integer)) or isinstance(t, bool):
        raise TypeError(f'times are int64 microseconds, got {type(t).__name__}')
    return int(t)


def _first_after(pv, t_us):
    return int(np.searchsorted(pv.tl, t_us, side='right'))


def _gap_between(pv, i0, i1):
    """a gap over 40 s between consecutive closes i0 .. i1 (i0 may be -1: then from the first close)"""
    a = max(i0, 0)
    return i1 > a and bool(np.any(np.diff(pv.tl[a:i1 + 1]) > GAP_US))


def fill(pv, tau_us, side, mode='taker', delay_us=3 * US, max_wait_us=60 * US, stale_us=60 * US):
    tau = _int_us(tau_us); delay = _int_us(delay_us)
    if side not in (1, -1):
        raise ValueError('side is +1 or -1')
    if len(pv) == 0:
        return Fill('NO_DATA')
    k = _first_after(pv, tau) - 1                                       # the last close at or before tau
    if k < 0 or tau - pv.tl[k] > stale_us:
        return Fill('STALE')
    i = _first_after(pv, tau + delay)
    if i >= len(pv) or pv.tl[i] - (tau + delay) > max_wait_us:
        return Fill('NO_FILL')
    j = _first_after(pv, tau + delay) - 1                               # the last close at or before tau + delay
    if _gap_between(pv, j, i):
        return Fill('GAP')
    if mode == 'maker':
        return Fill('REFUSED')
    if mode != 'taker':
        raise ValueError(f'mode {mode!r}')
    return Fill('FILLED', int(pv.tl[i]), float(pv.px[i]), i, int(pv.tl[i] - (tau + delay)))


def fill_exit(pv, t_dec_us, side, delay_us=3 * US, max_wait_us=60 * US):
    """an exit always fills: the first close after t_dec + delay, however late (LATE_EXIT), END when the data ends"""
    t = _int_us(t_dec_us); delay = _int_us(delay_us)
    i = _first_after(pv, t + delay)
    if i >= len(pv):
        return Fill('END')
    j = i - 1
    late = pv.tl[i] - (t + delay) > max_wait_us or _gap_between(pv, j, i)
    return Fill('LATE_EXIT' if late else 'FILLED', int(pv.tl[i]), float(pv.px[i]), i, int(pv.tl[i] - (t + delay)))


def fill_after_touch(pv, t_touch_us, side, level_px=None, delay_us=3 * US, max_wait_us=60 * US):
    """a stop or a target touched at t_touch fills as a taker after the touch + delay (D5: a touch is not a fill); level_px is shown, never used"""
    return fill_exit(pv, t_touch_us, side, delay_us, max_wait_us)


def entry_bench(pv, t_us):
    """the bench's entry (mode 'bench', KA1): the last close at or before t"""
    k = _first_after(pv, _int_us(t_us)) - 1
    if k < 0:
        return Fill('NO_DATA')
    return Fill('FILLED', int(pv.tl[k]), float(pv.px[k]), k, 0)


def slippage_x1(pv, t_us, window_us=3600 * US):
    """the median (hi - lo) / close over the bins whose last trade is in (t - 1 h, t]; NaN when there are none"""
    t = _int_us(t_us)
    a, b = _first_after(pv, t - window_us), _first_after(pv, t)
    if b <= a:
        return float('nan')
    return float(np.median((pv.hi[a:b] - pv.lo[a:b]) / pv.px[a:b]))


def money_pct(side, px_in, px_out, fee=FEE_TAKER, slip=0.0, slip_in=None, slip_out=None):
    """percent of the entry notional, after slippage against the trade at each fill (slip_in at the entry, slip_out at the exit, each
    as of its own decision; 'slip' gives both when they are not given) and a fee on both sides' notional"""
    si = slip if slip_in is None else slip_in; so = slip if slip_out is None else slip_out
    pe = px_in * (1 + side * si); px = px_out * (1 - side * so)
    ratio = px / pe
    return side * 100.0 * (ratio - 1.0) - 100.0 * fee * (1.0 + ratio)
