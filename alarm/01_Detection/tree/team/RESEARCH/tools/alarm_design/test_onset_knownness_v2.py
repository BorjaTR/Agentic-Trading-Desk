"""test_onset_knownness_v2.py: A54-FINAL-01, preserve a decided OFF predecessor without inventing knowledge; run against alarm_design_v3.py.
Owner ALARM. New edition by SCOUT for the clean release (30 Oct 2026). Old file: test_onset_knownness.py a2515ca5b70f300a, never edited;
only the import changed (the fixtures of test_alarm_design_v3, which imports alarm_design_v3)."""
import numpy as np
from test_alarm_design_v3 import AD, COINS, D2, Plant, dfn, setxy, zeros


def test_false_shared_with_unknown_claim_is_a_known_off_predecessor():
    codes=setxy([(120,132,1)],[(0,120,np.nan),(120,132,1)])
    ctx=AD.Ctx(dfn(),Plant(codes),D2,COINS,{})
    fires,sh,cl,kn,side=AD.find_fires(ctx,{})
    assert not sh[0,ctx.i0+119] and kn[0,ctx.i0+119]
    assert [(i,r-ctx.i0) for i,r in fires]==[(0,120)]


def test_unknown_predecessor_stays_unknown():
    codes=setxy([(0,132,1)],[(0,120,np.nan),(120,132,1)])
    ctx=AD.Ctx(dfn(),Plant(codes),D2,COINS,{})
    fires,sh,cl,kn,side=AD.find_fires(ctx,{})
    assert sh[0,ctx.i0+119] and not kn[0,ctx.i0+119]
    assert fires==[]


def test_false_shared_survives_skipped_percentile_minute():
    codes={('X',D2):zeros()};codes['X',D2][0,720:732]=30
    d=dfn();d['inputs']['threshold']={'op':'trail_pct','of':'x','w_s':3600,'q':99.9}
    d['conditions']=[{'name':'prefilter','lhs':'x','cmp':'>=','rhs':20,'role':'shared'},
                     {'name':'claim','lhs':'x','cmp':'>','rhs':'threshold','role':'claim'}]
    ctx=AD.Ctx(d,Plant(codes),D2,COINS,{})
    fires,sh,cl,kn,side=AD.find_fires(ctx,{})
    assert not sh[0,ctx.i0+719] and kn[0,ctx.i0+719]
    assert [(i,r-ctx.i0) for i,r in fires]==[(0,720)]
