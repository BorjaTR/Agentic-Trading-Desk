"""Exact-window activity reuse; no prefix sums or changed caliper arithmetic.

Fast use requires the same finite, positive, readonly float64 price/time arrays.
Other inputs use the original function. Each covariance keeps np.sum over the
same squared-return slice; diagnostic audit compares original float bits.
"""
import hashlib,math,struct,sys
from pathlib import Path
import numpy as np
REFERENCE_PATH=Path('<LAB_REPO>/forensics/team/RESEARCH/tools/alarm_match/draw_v3.py')
REFERENCE_SHA='91279359fb4a08155b82d64b34191e593527d628b6c478d629c9e809b24f142c'
if hashlib.sha256(REFERENCE_PATH.read_bytes()).hexdigest()!=REFERENCE_SHA:raise ValueError('ACTIVITY_REFERENCE_DRIFT')
if str(REFERENCE_PATH.parent) not in sys.path:sys.path.insert(0,str(REFERENCE_PATH.parent))
import draw_v3 as REFERENCE
if Path(REFERENCE.__file__).resolve()!=REFERENCE_PATH:raise ValueError('ACTIVITY_REFERENCE_MODULE')

def immutable(array):
    return np.frombuffer(array.tobytes(),dtype=array.dtype).reshape(array.shape)
class PreparedPreActivity:
    def __init__(self,ts,px,*,audit=False):
        if type(audit) is not bool:raise ValueError('ACTIVITY_AUDIT_FLAG')
        self.ts=ts;self.px=px;self.audit=audit;self.calls=0;self.checks=0
        self.fast=isinstance(ts,np.ndarray) and isinstance(px,np.ndarray) and ts.ndim==px.ndim==1 and ts.shape==px.shape and ts.dtype==px.dtype==np.dtype('float64') and ts.flags.c_contiguous and px.flags.c_contiguous and not ts.flags.writeable and not px.flags.writeable and np.all(np.isfinite(ts)) and np.all(np.isfinite(px)) and np.all(px>0)
        self.shape=getattr(ts,'shape',None)
        if self.fast:
            returns=np.diff(np.log(px));self.squared=immutable(returns*returns);self.gaps=immutable(np.diff(ts))
    def compute(self,ts,px,t,s):
        self.calls+=1
        if not self.fast or ts is not self.ts or px is not self.px or ts.shape!=self.shape or px.shape!=self.shape or ts.flags.writeable or px.flags.writeable:
            return REFERENCE.pre_activity(ts,px,t,s)
        hi=t-s['pre_end_s'];lo=hi-s['pre_len_s']
        if not np.isfinite(hi) or not np.isfinite(lo):return REFERENCE.pre_activity(ts,px,t,s)
        a,b=int(np.searchsorted(ts,lo,'right'))-1,int(np.searchsorted(ts,hi,'right'))
        if a<0 or b-a-1<s['min_closes']:result=np.nan
        elif b<=a:return REFERENCE.pre_activity(ts,px,t,s)
        else:
            gaps=self.gaps[a:b-1]
            if (len(gaps) and np.max(gaps)>s['gap_s']) or hi-ts[b-1]>s['gap_s']:result=np.nan
            else:result=float(np.sum(self.squared[a:b-1]))
        if self.audit:
            expected=REFERENCE.pre_activity(ts,px,t,s);self.checks+=1
            if not ((math.isnan(result) and math.isnan(expected)) or struct.pack('=d',result)==struct.pack('=d',expected)):raise AssertionError('ACTIVITY_FLOAT_BITS_DIFFER')
        return result
