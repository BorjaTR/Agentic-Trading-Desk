"""RESEARCH tools/alarm_profile episode_twin (QUANT, 22 Oct 2026): PROOF P2, the episode values computed a SECOND time, written apart from
episode_blocks.py from the README's definitions only: plain Python loops and lists, its own closes, sums, bar, percentile, median and run
start; it imports nothing of the tool and nothing of tools/alarms (only math, bisect, datetime). It takes the raw inputs (NOT cut at the
alarm: it cuts them itself) and returns {column: float} for one alarm. The proof run compares it with the values read back from the one
format on every built alarm; the tests compare it on planted and random episodes. v2 (22 Oct 12:4xZ): the run start's search ends at the
RUN END (the README's definition), written here again from that text. v3: the PAUSE rule (the README), again from its text."""
import bisect, datetime, math

NAN = float('nan')


def _fin(v):
    return v is not None and v == v and v not in (float('inf'), float('-inf'))


def _median(v):
    s = sorted(v); n = len(s)
    return s[n // 2] if n % 2 else 0.5 * (s[n // 2 - 1] + s[n // 2])


def _pct(v, q):
    """linear percentile of a list (numpy's default method)"""
    s = sorted(v); n = len(s); pos = (n - 1) * q / 100.0; lo = int(math.floor(pos)); hi = min(lo + 1, n - 1)
    return s[lo] + (s[hi] - s[lo]) * (pos - lo)


def _log10usd(v):
    if not _fin(v) or v < 0:
        return NAN
    return 0.0 if v == 0 else math.log10(v)


def _ratio(a, b):
    return a / b if _fin(a) and _fin(b) and b != 0 else NAN


def _day(t):
    return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime('%Y%m%d')


def _back(d, k):
    return (datetime.datetime.strptime(d, '%Y%m%d') - datetime.timedelta(days=k)).strftime('%Y%m%d')


def twin(coin, t, t0, side, T5, xf, xo, te_us, px, daily, oi_t, oi_v, oi_c, hl=None):
    t = int(t); t0 = int(t0); s_ = 1 if side > 0 else -1
    kt = (t - int(T5)) // 5; k0 = (t0 - int(T5)) // 5
    F = [float(v) for v in list(xf)[:kt + 1]]; O = [float(v) for v in list(xo)[:kt + 1]]
    cut = t * 1000000; TE = []; PX = []
    for a, b in zip(list(te_us), list(px)):
        if int(a) <= cut:
            TE.append(int(a)); PX.append(float(b))
    order = sorted(range(len(TE)), key=lambda i: TE[i]); TE = [TE[i] for i in order]; PX = [PX[i] for i in order]
    OT = []; OV = []; OC = []
    for a, b, c in zip(list(oi_t), list(oi_v), list(oi_c)):
        if float(a) <= t:
            OT.append(float(a)); OV.append(float(b)); OC.append(float(c))

    def close(s):
        u = int(round(s * 1000000)); i = bisect.bisect_right(TE, u) - 1
        if i >= 0 and u - TE[i] > 60 * 1000000:
            return NAN                                                   # STALE_PRICE (STRATEGY-153335): older than 60 s is a hole
        return PX[i] if i >= 0 and PX[i] > 0 else NAN

    def x(s):
        c = close(s)
        return s_ * math.log(c) if _fin(c) else NAN

    out = {}
    # the coin's normal 15 min move
    g = [close(t - 90000 + 900 * j) for j in range(97)]
    mv = [abs(math.log(g[j]) - math.log(g[j - 1])) for j in range(1, 97) if _fin(g[j]) and _fin(g[j - 1])]
    nm = _median(mv) if len(mv) >= 48 else NAN
    out['normal_move_pct'] = nm * 100 if _fin(nm) else NAN
    # the burst start: the first forced row with a print in the onset's 60 s window
    k1 = None; tb = NAN
    if k0 - 11 >= 0 and k0 <= kt:
        for k in range(k0 - 11, k0 + 1):
            if _fin(F[k]) and F[k] > 0:
                k1 = k; tb = float(int(T5) + 5 * k - 5); break
    # the run end (v2): the furthest push-direction close since the burst start (onset - 60 s without a burst), the latest on ties;
    # the alarm when the alarm's close is that furthest one
    w0 = tb if _fin(tb) else float(t0 - 60)
    far = x(w0); far_t = w0; w0_us = int(round(w0 * 1000000))
    for a, b in zip(TE, PX):
        if a > w0_us and b > 0:
            v = s_ * math.log(b)
            if not _fin(far) or v >= far:
                far = v; far_t = a / 1000000.0
    xt_ = x(t)
    end = t if (not _fin(far) or (_fin(xt_) and xt_ >= far)) else far_t
    # the run start: the minute grid from 24 h before the alarm, cut at the run end, plus the run end itself
    st = NAN; turned = False
    if _fin(nm):
        h = max(3.0 * nm, 0.001)
        times = [t - 86400 + 60 * k for k in range(1440) if t - 86400 + 60 * k < end] + [end]
        X = [x(s) for s in times]
        if _fin(X[-1]) and sum(1 for v in X if _fin(v)) > 60:
            hi = None; hi_at = -1; turn = -1; i = 0
            while i < len(X):
                v = X[i]
                if _fin(v):
                    if hi is None or v > hi:
                        hi = v; hi_at = i
                    elif v <= hi - h:
                        turn = hi_at; hi = v; hi_at = i
                i += 1
            seg = [(j, X[j]) for j in range(turn + 1, len(X)) if _fin(X[j])]
            low = min(v for _, v in seg)
            pick = [j for j, v in seg if v <= low + nm][-1]
            # v3 pause: from the swing start, progress = a close more than one normal move above the last progress's close; a pause
            # = 30 min or more between progresses (or from the last one to the end); the start = the last low of the last pause
            ref_j = pick; pauses = []
            for j in range(pick + 1, len(X)):
                if _fin(X[j]) and X[j] > X[ref_j] + nm:
                    if times[j] - times[ref_j] >= 1800:
                        pauses.append((ref_j, j - 1))
                    ref_j = j
            if times[-1] - times[ref_j] >= 1800:
                pauses.append((ref_j, len(X) - 1))
            paused = len(pauses) > 0
            if paused:
                a_, b_ = pauses[-1]
                inside = [(j, X[j]) for j in range(a_, b_ + 1) if _fin(X[j])]
                plow = min(v for _, v in inside)
                pick = [j for j, v in inside if v <= plow + nm][-1]
            st = float(times[pick]); turned = turn >= 0 or paused
    xt = x(t)
    for k in ('run_pct', 'run_norm', 'run_age_min', 'run_capped'):
        out[k] = NAN
    if _fin(st):
        out['run_pct'] = (xt - x(st)) * 100
        out['run_norm'] = _ratio(out['run_pct'], nm * 100)
        out['run_age_min'] = (t - st) / 60.0
        out['run_capped'] = 0.0 if turned else 1.0
    # split, giveback
    out.update(pre_move_pct=NAN, burst_move_pct=NAN, forced_share=NAN, giveback_pct=NAN, giveback_share=NAN)
    if _fin(tb):
        out['burst_move_pct'] = (xt - x(tb)) * 100
    if _fin(st):
        xs = x(st); run = (xt - xs) * 100
        if _fin(tb):
            out['pre_move_pct'] = (x(tb) - xs) * 100
            if run > 0:
                out['forced_share'] = out['burst_move_pct'] / run
        lo_us = int(round(st * 1000000)); ext = None
        for a, b in zip(TE, PX):
            if a >= lo_us and b > 0:
                v = s_ * math.log(b)
                ext = v if ext is None or v > ext else ext
        if ext is not None and _fin(xt):
            out['giveback_pct'] = (ext - xt) * 100
            if ext > xs:
                out['giveback_share'] = (ext - xt) / (ext - xs)
    # speed
    out.update(burst_s=NAN, onset_to_alarm_s=float(t - t0), burst_speed_pct_min=NAN, pre_speed_pct_min=NAN, speed_ratio=NAN,
               burst_speed_vs_normal=NAN, max_move_60s_pct=NAN)
    if _fin(tb):
        bs = t - tb; out['burst_s'] = bs
        if bs >= 60:
            out['burst_speed_pct_min'] = (xt - x(tb)) * 100 / (bs / 60.0)
            if _fin(nm):
                out['burst_speed_vs_normal'] = _ratio(out['burst_speed_pct_min'], nm * 100 / 15.0)
            best = None; s = t
            while s >= tb + 60:
                a, b = close(s), close(s - 60)
                if _fin(a) and _fin(b):
                    m = s_ * (math.log(a) - math.log(b)) * 100
                    best = m if best is None or m > best else best
                s -= 5
            if best is not None:
                out['max_move_60s_pct'] = best
        if _fin(st) and tb - st >= 60:
            out['pre_speed_pct_min'] = (x(tb) - x(st)) * 100 / ((tb - st) / 60.0)
            if out['pre_speed_pct_min'] > 0:
                out['speed_ratio'] = _ratio(out['burst_speed_pct_min'], out['pre_speed_pct_min'])

    # the forced side's sums
    def f15(k):
        if k < 2:
            return NAN
        w = F[k - 2:k + 1]
        return w[0] + w[1] + w[2] if all(_fin(v) for v in w) else NAN

    def s60(k):
        if k < 11:
            return NAN
        w = F[k - 11:k + 1]
        if not all(_fin(v) for v in w):
            return NAN
        tot = 0.0
        for v in w:
            tot += v
        return tot

    def rows_sum(R, a, b):
        w = R[a:b + 1]
        if not all(_fin(v) for v in w):
            return NAN
        tot = 0.0
        for v in w:
            tot += v
        return tot

    p15 = NAN; kp = None; p60 = NAN
    for k in range(k0, kt + 1):
        v = f15(k)
        if _fin(v) and (kp is None or v >= p15):
            p15 = v; kp = k
        w = s60(k)
        if _fin(w) and (not _fin(p60) or w > p60):
            p60 = w
    usd = rows_sum(F, k1, kt) if k1 is not None else NAN
    bar = None
    if k0 <= kt and k0 - 4320 >= 0:
        vals = [s60(k) for k in range(k0 - 4320, k0)]; vals = [v for v in vals if _fin(v)]
        if len(vals) / 4320.0 >= 0.9:
            bar = max(_pct(vals, 99.9), 20000.0)
    pre = rows_sum(F, k1 - 720, k1 - 1) if k1 is not None and k1 - 720 >= 0 else NAN
    wk = NAN
    if _fin(tb):
        b = _day(tb); got = []
        for j in range(1, 8):
            d = _back(b, j)
            if d in daily and daily[d][1] >= 0.9 and _fin(daily[d][0]):
                got.append(daily[d][0])
        if len(got) >= 5:
            wk = _ratio(usd, _median(got))
    s0 = s60(k0) if k0 <= kt else NAN
    out.update(forced_usd_log=_log10usd(usd), peak15_usd_log=_log10usd(p15), peak60_usd_log=_log10usd(p60),
               size_vs_bar=_ratio(p60, bar) if bar else NAN, size_vs_week=wk, growth=_ratio(p60, s0), pre_forced_usd_log=_log10usd(pre))
    # shape
    out.update(peak_s=NAN, peak_to_alarm_s=NAN, n_flushes=NAN, active_share=NAN, top5s_share=NAN)
    if kp is not None:
        tp = int(T5) + 5 * kp; out['peak_to_alarm_s'] = float(t - tp)
        if _fin(tb):
            out['peak_s'] = float(tp - tb)
        if p15 > 0:
            waves = 0; quiet_run = 0; ready = False
            for k in range(k0, kt + 1):
                v = f15(k)
                if not _fin(v):
                    quiet_run = 0
                elif v >= 0.5 * p15:
                    if waves == 0:
                        waves = 1
                    elif ready:
                        waves += 1; ready = False
                    quiet_run = 0
                elif v <= 0.1 * p15:
                    quiet_run += 1
                    if waves > 0 and quiet_run >= 3:
                        ready = True
                else:
                    quiet_run = 0
            out['n_flushes'] = float(waves)
    if k1 is not None and _fin(usd):
        w = F[k1:kt + 1]
        out['active_share'] = sum(1 for v in w if v > 0) / float(len(w))
        if usd > 0:
            out['top5s_share'] = max(w) / usd
    oth = rows_sum(O, k1, kt) if k1 is not None else NAN
    out['other_usd_log'] = _log10usd(oth)
    out['other_share'] = _ratio(oth, usd + oth) if _fin(usd) and _fin(oth) else NAN
    # open interest over the burst
    out['oi_chg_burst_pct'] = NAN; out['burst_vs_oi_bp'] = NAN
    if _fin(tb) and OT:
        ib = bisect.bisect_right(OT, tb) - 1; ia = len(OT) - 1
        if ib >= 0 and _fin(OV[ib]) and OV[ib] > 0:
            c = close(tb)
            out['burst_vs_oi_bp'] = _ratio(usd, OV[ib] * c) * 1e4 if _fin(c) else NAN
            if ia > ib and _fin(OV[ia]) and OV[ia] > 0 and OC[ia] == 0:
                out['oi_chg_burst_pct'] = (OV[ia] / OV[ib] - 1.0) * 100
    # Hyperliquid: the liquidated accounts' fills; the forced side's fill side is the push's (a short closed buys, a long closed sells)
    out['hl_forced_usd_log'] = NAN; out['hl_other_usd_log'] = NAN; out['hl_lead_s'] = NAN
    if hl is not None and _fin(tb) and _day(tb - 180) in hl['days'] and _day(t) in hl['days']:
        same = 0.0; other = 0.0; first = None
        for a, u, d in zip(list(hl['lt']), list(hl['usd']), list(hl['side'])):
            a = float(a)
            if a > t:
                continue
            if a > tb:
                if d == s_:
                    same += float(u)
                elif d == -s_:
                    other += float(u)
            if a > tb - 180 and d == s_ and (first is None or a < first):
                first = a
        out['hl_forced_usd_log'] = _log10usd(same); out['hl_other_usd_log'] = _log10usd(other)
        if first is not None:
            out['hl_lead_s'] = tb - first
    return out
