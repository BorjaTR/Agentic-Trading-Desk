"""labcore.v2_7.series (labcore V2_7 CANDIDATE; ctxprof_shared for STRATEGY/LEAD, 25 Oct 2026; A46R REL-01 F1, LEAD phase-B plan 13:0xZ).
THE TYPED CLOCK-SERIES READER, registered in labcore BY RE-EXPORT: the code stays in team/RESEARCH/tools/event_profile/clock_series.py
(owner: event_profile / profile_fix2; FROZEN bytes 5b5a331ccd81c605, which Decisions V3.1 pins), exactly like labcore.stores re-exports
the tools' readers. No rewrite, no copy, no shim in the tool: the physical move into labcore waits for LAB1 (stopped). A changed
clock_series.py refuses this candidate's release.check until it is re-cut.
What it gives (see clock_series' own docstring): parts_holding (absence from lab3 metadata, before any read), read_day_typed / read_day
(one code-day through the ONE lab3 reader, every reader error propagates), ClockSeries (consecutive days, typed states OK, HOLE,
NOT_IN_SOURCE, NOT_BUILT, NOT_KNOWN, SEALED, OUTSIDE_WINDOW; window / event_window / normal / unavailable_between), STATE_WORD, UNREAD.
  from labcore.v2_7 import series
  series.read_day_typed(R, code, day, coins, step)"""
import importlib.util, os, sys

CS_PATH = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'event_profile', 'clock_series.py'))


def _load():
    """one module object per process: event_profile imports it as 'clock_series' (its folder on sys.path); reuse that object"""
    m = sys.modules.get('clock_series')
    if m is not None and os.path.realpath(getattr(m, '__file__', '')) == CS_PATH:
        return m
    spec = importlib.util.spec_from_file_location('clock_series', CS_PATH); m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    sys.modules.setdefault('clock_series', m)
    return m


CS = _load()
parts_holding = CS.parts_holding
read_day_typed = CS.read_day_typed
read_day = CS.read_day
is_absence = CS.is_absence
ClockSeries = CS.ClockSeries
OK, HOLE, NOT_IN_SOURCE, NOT_BUILT, NOT_KNOWN, SEALED, OUTSIDE_WINDOW = (CS.OK, CS.HOLE, CS.NOT_IN_SOURCE, CS.NOT_BUILT, CS.NOT_KNOWN,
                                                                     CS.SEALED, CS.OUTSIDE_WINDOW)
STATE_WORD = CS.STATE_WORD
UNREAD = CS.UNREAD
