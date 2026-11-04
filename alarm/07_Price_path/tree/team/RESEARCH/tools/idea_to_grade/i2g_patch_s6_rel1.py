"""i2g_patch_s6_rel1.py: Owner STRATEGY/LEAD (the grader thread). New edition by SCOUT for the clean release (K6, 31 Oct 2026; the owner 30 Oct 2026 23:07 Berlin: "All alarm tools should work from the
release folder only"). Old file: i2g_patch_s6_v1.py ecf29a60cd40ed1e, never edited. Changed: patch() imports i2g_engine_rel1 in place of i2g_engine; its check names
alarm_stamp_projection_v2 and alarm_stamp_ed1_1.
rel1 = release edition 1: the files of one chain that run from the Alarm release folder (code found relative to this file, in the
team/ layout of the dev tree; data from arguments); no value, rule, seal or output format changes.
The rest of this text is i2g_patch_s6_v1.py's.
i2g_patch_s6_v1.py (speed twin S6, grader thread, 26 Oct 2026, TEST): the day-text work of the store build's measurements, memoised per
process, each the same values bit for bit; applied by patch(k, eng) to the modules K.load() returns and to the engine module eng (no file
is changed; the signed modules are read, and their own functions compute every memoised value once):
  1 shift     i2g_engine.shift and alarm_context.shift ((d, k) -> the day k days after the day text d, strptime + strftime) memoised per
              (d, k) when d is a str and k an int; anything else goes to the module's own function. The engine's own name shift too.
  2 day text  i2g_engine.day_of and alarm_context.utc_day (fromtimestamp(t).strftime) memoised per UTC day with i2g_patch_s4_v1.cal_memo
              (the same rule as the matcher's calendar in S4: the part after the whole second below 0.999999, else the module's own).
  3 known end alarm_stamp_projection_v1's known_end_us (alarm_stamp.known_end_us, imported there with *): the same steps with the
              memoised day helpers, and its last step, 00:00 UTC of the day text as integer microseconds (alarm_stamp's own expression),
              computed once per day text.
No date, coin or alarm is held here."""
import i2g_patch_s4_v1 as P4

DONE = '_i2g_patch_s6_v1'


def shift_memo(orig):
    memo = {}

    def f(d, k):
        if type(d) is str and type(k) is int:
            key = (d, k)
            v = memo.get(key)
            if v is None:
                v = memo[key] = orig(d, k)
            return v
        return orig(d, k)
    f.orig = orig
    return f


def known_end_memo(AS):
    """alarm_stamp.known_end_us(loaded, t_from_us) with its day helpers read from its own AC module at call time and its last step once
    per day text"""
    AC = AS.AC
    ends = {}

    def known_end_us(loaded, t_from_us):
        d = AC.utc_day(t_from_us / 1e6)
        while d in loaded:
            d = AC.shift(d, 1)
        v = ends.get(d)
        if v is None:
            v = ends[d] = int(AC.dt.datetime.strptime(d, '%Y%m%d').replace(tzinfo=AC.dt.timezone.utc).timestamp()) * 1_000_000
        return v
    known_end_us.orig = AS.known_end_us
    return known_end_us


def patch(k, eng):
    """k: K.load()'s namespace; eng: the engine module (its own day_of and shift names are rebound to the memoised ones)"""
    import i2g_engine_rel1 as E2
    S = k.S
    if getattr(S, DONE, False):
        return
    AS = S.PROJECTION_BASE
    AC = AS.AC
    if S.known_end_us is not AS.known_end_us:
        raise RuntimeError('PATCH_S6: alarm_stamp_projection_v2.known_end_us is not alarm_stamp_ed1_1.known_end_us')
    E2.shift = shift_memo(E2.shift); E2.day_of = P4.cal_memo(E2.day_of)
    AC.shift = shift_memo(AC.shift); AC.utc_day = P4.cal_memo(AC.utc_day)
    eng.shift = E2.shift; eng.day_of = E2.day_of
    S.known_end_us = known_end_memo(AS)
    setattr(S, DONE, True)
