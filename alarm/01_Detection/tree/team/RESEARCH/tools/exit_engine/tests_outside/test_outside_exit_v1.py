# SECOND TEST SET (BUILD1 23 Oct 2026, STRATEGY must-fix via the coordinator 13:14Z): a byte copy of OX-CODE1's
# team/OUTSIDE/CODE1/tests/exit_engine/test_outside_exit.py sha16 871e5281fcbf284f (independent plants from README V2.4, written before the source).
# Kept here permanent; a change to it is OX-CODE1's, copied again with its new sha16. Run: pytest -q in this folder.
"""Independent plants written from README V2.4 and public interface before source/test inspection."""
import os
import importlib.util
import sys
import numpy as np
import pytest
TOOLS='<LAB_REPO>/forensics/team/RESEARCH/tools'
sys.path.insert(0,TOOLS)
spec=importlib.util.spec_from_file_location('outside_exit_target',os.environ.get('OX_EXIT_SOURCE',TOOLS+'/exit_engine/exit_engine_v1.py'))
eng=importlib.util.module_from_spec(spec); spec.loader.exec_module(eng)

def run(c, h=None, l=None, side=1, units=None, monitor=None, t0=0, **kw):
    c=np.asarray(c,float); h=c.copy() if h is None else np.asarray(h,float); l=c.copy() if l is None else np.asarray(l,float)
    r=dict(id='OUTSIDE',kind='B',unit='pct',stop=None,take=None,arm=None,give=None,time_limit_min=(len(c)-1)*.05,min_hold_min=None,early_stop=None,early_min=None,monitor='none',note='synthetic')
    r.update(kw)
    return eng.simulate(c,h,l,np.array([0]),np.array([100.]),np.array([side]),r,units=units,monitor=monitor,t0_us=t0)

def val(o,k): return o[k][0]

def test_adverse_first():
    o=run([100,100],h=[100,102],l=[100,98],stop=1,take=1)
    assert val(o,'kind')=='stop' and val(o,'exit_px')==99

def test_stop_worse_close():
    o=run([100,97],stop=1)
    assert val(o,'exit_px')==97 and val(o,'gap_bp')==pytest.approx(200)

def test_take_touch_only():
    o=run([100,101,100],take=1)
    assert val(o,'kind')=='time' and val(o,'touched_not_filled')==1

def test_take_through():
    o=run([100,102],take=1)
    assert val(o,'kind')=='take' and val(o,'exit_px')==101

def test_trail_next_bar():
    o=run([100,102,101],h=[100,103,102],l=[100,100,100],kind='T',stop=5,arm=2,give=1)
    assert val(o,'kind')=='trail' and val(o,'exit_bar')==2 and val(o,'exit_px')==101

def test_hole_not_price():
    o=run([100,np.nan,100],stop=1)
    assert val(o,'exit_px')==100

def test_hole_adverse_gap():
    o=run([100,np.nan,97],stop=1)
    assert val(o,'exit_px')==97 and val(o,'gap_len_bars')==1

def test_monitor_next():
    o=run([100,102,103,104],kind='M',monitor=np.array([1]))
    assert val(o,'kind')=='monitor' and val(o,'exit_bar')==2 and val(o,'exit_px')==103

def test_monitor_pending_hole():
    o=run([100,102,np.nan,97,100],kind='M',monitor=np.array([1]))
    assert (val(o,'kind')=='monitor' and val(o,'exit_bar')==3) or val(o,'kind')=='noprice'

def test_time_limit():
    o=run([100,101,102,103],time_limit_min=.1)
    assert val(o,'exit_bar')==2

def test_grid_ends_early():
    assert val(run([100,101],time_limit_min=1),'kind')=='noprice'

def test_min_hold_take():
    o=run([100,102,102],take=1,min_hold_min=.1)
    assert val(o,'exit_bar')==2

def test_min_hold_stop_active():
    o=run([100,98,100],stop=1,min_hold_min=.1)
    assert val(o,'exit_bar')==1 and val(o,'kind')=='stop'

def test_future_unit_rejected():
    with pytest.raises(ValueError): run([100,101],unit='nm',stop=1,units={'nm':[1.], 'known_at_us':[1]})

def test_missing_unit_rejected():
    with pytest.raises(ValueError): run([100,101],unit='nm',stop=1)

def test_missing_unit_clock_rejected():
    with pytest.raises(ValueError): run([100,101],unit='nm',stop=1,units={'nm':[1.]})

def test_nan_unit_rejected():
    with pytest.raises(ValueError): run([100,101],unit='nm',stop=1,units={'nm':[np.nan],'known_at_us':[0]})

def test_mirror():
    a=run([100,102,97],stop=1,take=1)
    b=run([100,98,103],side=-1,stop=1,take=1)
    assert val(a,'kind')==val(b,'kind') and val(a,'ret_pct')==pytest.approx(val(b,'ret_pct'))

def test_midnight_clock():
    t=86400000000-3000000
    o=run([100,101],t0=t)
    assert val(o,'exit_us')==86400000000 and val(o,'known_at_us')==val(o,'exit_us')

def test_tiny_take_touch():
    o=run([100,100.000001,100],take=.000001)
    assert val(o,'kind')=='time'

def test_early_stop():
    o=run([100,98,100],stop=5,early_stop=1,early_min=.1)
    assert val(o,'kind')=='stop' and val(o,'exit_bar')==1

def test_nan_close_finite_extremes():
    o=run([100,np.nan,100],h=[100,105,100],l=[100,95,100],stop=1,take=1)
    assert val(o,'exit_bar')!=1

def test_entry_bar_ignored():
    o=run([100,100],h=[200,100],l=[1,100],stop=1,take=1)
    assert val(o,'kind')=='time'

def test_prefix_future_plant():
    a=run([100,102,98],take=1)
    b=run([100,102,99999],take=1)
    for k in ['exit_bar','exit_px','kind','ret_pct','heat_pct','best_pct']: assert val(a,k)==val(b,k)

# Source-review follow-up plants (distinct from the 24 pre-source tests).
def test_fractional_future_clock_rejected():
    with pytest.raises(ValueError): run([100,101],unit='nm',stop=1,units={'nm':[1.],'known_at_us':[.5]})

def test_missing_clock_sentinel_rejected():
    with pytest.raises(ValueError): run([100,101],unit='nm',stop=1,units={'nm':[1.],'known_at_us':[-1]})

@pytest.mark.parametrize('bad_side',[0,2,.5])
def test_invalid_side_rejected(bad_side):
    with pytest.raises(ValueError): run([100,101],side=bad_side)

def test_inconsistent_ohlc_rejected():
    with pytest.raises(ValueError): run([100,100],h=[100,90],l=[100,110],stop=1,take=1)

def test_negative_price_rejected():
    with pytest.raises(ValueError): run([100,-1],stop=1)

def test_nonfinite_threshold_rejected():
    with pytest.raises(ValueError): run([100,90],stop=float('nan'))

def test_recovered_hole_flagged():
    o=run([100,np.nan,102],take=1)
    assert val(o,'path_gap') and val(o,'hole_bars')==1

def test_extreme_requires_clock():
    with pytest.raises(ValueError): run([100,99],stop=1,stop_from='extreme',units={'extreme_px':[100.]})

# C01b: boundary cases added after the C1 fixes.
def test_entry_bar_fraction_refused():
    r=dict(id='P',kind='B',unit='pct',stop=1,time_limit_min=.05)
    with pytest.raises(ValueError): eng.simulate([100,100],[100,100],[100,100],[.5],[100],[1],r)

def test_fractional_monitor_refused():
    with pytest.raises(ValueError): run([100,101,102,103],monitor=[1.9])

def test_extreme_price_positive():
    with pytest.raises(ValueError): run([100,99],stop_from='extreme',stop=1,units={'extreme_px':[-100.], 'extreme_known_at_us':[0]})
