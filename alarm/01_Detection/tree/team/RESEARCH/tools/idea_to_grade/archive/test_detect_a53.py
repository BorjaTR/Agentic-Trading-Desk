"""test_detect_a53.py: COPY of the outside review A53's regressions (team/OUTSIDE/A53/i2g_detect_review_v1/test_faults.py, sha16 3a808786804e88ec),
adapted only by passing the required research window (research_window=W) to every detect.run call. Assertions unchanged."""
import json, sys
from pathlib import Path
import numpy as np
import pytest
F=Path('<LAB_REPO>/forensics')
sys.path.insert(0,str(F/'team/RESEARCH/tools/idea_to_grade'))
import detect as D
import test_detect as fixtures
W = fixtures.W                    # i2g_detector adaptation: the research window is a required run setting since c536f0bc

def config(tmp_path,grid=60):
    d=json.loads(fixtures.DEF_OI.read_text()); d['grid_s']=grid
    d['window']={'first':'20250901','last':'20260228'}
    p=tmp_path/'definition.json'; p.write_text(json.dumps(d))
    r=tmp_path/'roster.tsv'; r.write_text('coin\nXX\n')
    return p,r

def clean():
    f=fixtures.FakeDays()
    for day in f.v:
        f.v[day][:]=0
        for fld in ['e','a','o']: f.q[day][fld][:]=0
        f.q[day]['k'][:]=(fixtures.day0(day)+60*np.arange(1440))*1000000
    return f

def test_grid_70_keeps_last_valid_step(tmp_path):
    p,r=config(tmp_path,70); f=clean(); f.v[fixtures.D1][0,-1]=-2
    m=D.run(p,fixtures.D1,fixtures.D1,tmp_path/'run',r,workers=1,_reader=f,research_window=W)
    want=[('XX',fixtures.day0(fixtures.D1)+86380,-1)]
    assert fixtures.events(m)==want, 'grid 70 loses the valid 23:59:40 decision'

def test_grid_70_midnight_uses_actual_predecessor(tmp_path):
    p,r=config(tmp_path,70); f=clean()
    # At D2-70s, D1's native minute 1438 is true.  Grid truncation instead
    # samples native minute 1437 and invents an onset at D2 midnight.
    f.v[fixtures.D1][0,1438]=-2; f.v[fixtures.D2][0,0]=-2
    m=D.run(p,fixtures.D2,fixtures.D2,tmp_path/'run',r,workers=1,_reader=f,research_window=W)
    assert ('XX',fixtures.day0(fixtures.D2),-1) not in fixtures.events(m)

def test_complete_manifest_must_require_output_pins(tmp_path):
    run=tmp_path/'incomplete'; run.mkdir()
    (run/'DETECT_RUN.json').write_text(json.dumps({'status':'COMPLETE','files':{}}))
    with pytest.raises((D.Refusal,ValueError,KeyError,FileNotFoundError)):
        D.read_run(run)

def test_downstream_must_reject_missing_coverage_pin(tmp_path):
    p,r=config(tmp_path); f=clean()
    m=D.run(p,fixtures.D1,fixtures.D1,tmp_path/'run',r,workers=1,_reader=f,research_window=W)
    run=Path(m).parent
    doc=json.loads(Path(m).read_text()); doc['files'].pop('COVERAGE.tsv')
    Path(m).write_text(json.dumps(doc))
    (run/'COVERAGE.tsv').write_text('coin\tday\tstatus\n')
    import idea_to_grade as pipeline
    with pytest.raises((D.Refusal,ValueError,KeyError)):
        pipeline.read_detect(str(run),False)

def test_admission_refuses_invalid_operand_before_output(tmp_path):
    p,r=config(tmp_path); d=json.loads(p.read_text())
    d['inputs']['broken']={'op':'neg','of':'NOT_BOUND'}
    d['conditions'][0]['lhs']='broken'; p.write_text(json.dumps(d))
    with pytest.raises(D.Refusal):
        D.run(p,fixtures.D1,fixtures.D1,tmp_path/'run',r,workers=1,_reader=clean(),research_window=W)
    assert not (tmp_path/'run').exists()

def test_price_reader_corruption_must_stop_run(tmp_path):
    from lab3 import bins, days
    p,r=config(tmp_path); d=json.loads(p.read_text())
    d['inputs']={'metric':{'op':'price'}}
    d['conditions'][0].update(cmp='>',rhs=0); p.write_text(json.dumps(d))
    root=tmp_path/'store'
    t=(fixtures.day0(fixtures.D1)+3)*1000000
    data={'te':np.array([t],dtype='int64'),'tl':np.array([t-1000],dtype='int64'),
          'px':np.array([100.]),'hi':np.array([100.]),'lo':np.array([100.]),
          'n':np.array([1],dtype='int32'),'buy':np.array([1.]),'sell':np.array([0.])}
    bins.write_bins(str(root),fixtures.D1,['XX'],{'XX':data})
    block=root/('day='+fixtures.D1)/'PRICE/BIN.px.lz4'
    assert block.is_file(); block.write_bytes(b'BROKEN_A53_FIXTURE')
    with pytest.raises(Exception):
        bins.read_bins(days.Days(str(root),'research'),fixtures.D1,['XX'])
    with pytest.raises((D.Refusal,days.BlockChanged,ValueError,OSError)):
        D.run(p,fixtures.D1,fixtures.D1,tmp_path/'run',r,workers=1,lab_root=str(root),research_window=W)
