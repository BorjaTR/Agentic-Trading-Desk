"""Prepared identical estimands; exact integer CDFs share one sort across quantiles."""
import collections,math
from fractions import Fraction
import numpy as np

def integer_masses(exact):
 denominator=1
 for d in {x.denominator for x in exact}:
  denominator=math.lcm(denominator,d)
  if denominator.bit_length()>4096:return None
 return np.asarray([x.numerator*(denominator//x.denominator) for x in exact],dtype=object)

def quantiles(values,observed,integers,exact,qs,reference):
 ix=np.flatnonzero(observed)
 if not len(ix):return {str(q):None for q in qs}
 if integers is None:return {str(q):reference._quantile([float(values[i]) for i in ix],[exact[i] for i in ix],q) for q in qs}
 order=np.argsort(values[ix],kind='stable');ordered=ix[order]
 cumulative=np.cumsum(integers[ordered],dtype=object);total=int(cumulative[-1]);out={}
 for q in qs:
  ratio=Fraction(str(q));target=(total*ratio.numerator+ratio.denominator-1)//ratio.denominator
  pos=int(np.searchsorted(cumulative,target,side='left'));out[str(q)]=float(values[ordered[pos]])
 return out

def profile(reach,values,mass,exact,integers,qs,reference):
 known=np.isfinite(reach);hit=reach==1;no=reach==0;missing=~known
 fsum=lambda mask:math.fsum(mass[mask])
 total=math.fsum(mass);known_mass=fsum(known);hit_mass=fsum(hit)
 out={'rows':len(reach),'base_mass':total,'known_reach_mass':known_mass,'reached_mass':hit_mass,'known_nonreach_mass':fsum(no),'unknown_reach_mass':fsum(missing),'reach_probability':hit_mass/known_mass if known_mass else None,'reached_rows':int(hit.sum()),'known_nonreach_rows':int(no.sum()),'unknown_reach_rows':int(missing.sum()),'conditional':{}}
 for name,column in values.items():
  observed=hit&np.isfinite(column);unknown=missing|(hit&~np.isfinite(column));observed_mass=fsum(observed);unknown_mass=fsum(unknown)
  out['conditional'][name]={'status':'EMPTY' if not len(reach) else 'PARTIAL_UNKNOWN' if unknown_mass else 'OBSERVED' if observed_mass else 'NO_REACH','base_mass':total,'reached_mass':hit_mass,'known_reached_mass':observed_mass,'not_applicable_mass':out['known_nonreach_mass'],'unknown_mass':unknown_mass,'observed_rows':int(observed.sum()),'unknown_rows':int(unknown.sum()),'quantiles':quantiles(column,observed,integers,exact,qs,reference),'quantile_uncertainty':'NOT_ESTABLISHED'}
 return out

class Prepared:
 def __init__(self,parent_ids,waves,edge_parents,control_ids,weights,reference):
  self.ref=reference;need=reference._need;self.pids=[reference._identity(x) for x in parent_ids];self.waves=waves;self.ep=[reference._identity(x) for x in edge_parents];self.cids=[reference._identity(x) for x in control_ids];self.n=len(self.pids);self.m=len(self.ep)
  need(len(set(self.pids))==self.n,'DUPLICATE_PARENT');need(len(self.cids)==len(weights)==self.m,'EDGE_LENGTH');need(all(p in waves for p in self.pids),'MISSING_FROZEN_WAVE_ID');need(set(self.ep)<=set(self.pids),'EDGE_PARENT_OUTSIDE_COHORT');need(len(set(zip(self.ep,self.cids)))==self.m,'DUPLICATE_ELIGIBLE_EDGE')
  self.weights=np.asarray(weights,dtype=float);need(bool(np.all(np.isfinite(self.weights)&(self.weights>0))),'POSITIVE_FINITE_ELIGIBLE_WEIGHT_REQUIRED')
  positions={p:i for i,p in enumerate(self.pids)};self.epi=np.asarray([positions[p] for p in self.ep],dtype=np.int64);groups=[[] for _ in self.pids]
  for j,i in enumerate(self.epi):groups[i].append(j)
  self.groups=[np.asarray(g,dtype=np.int64) for g in groups];self.counts=np.asarray([len(g) for g in groups]);self.total=np.asarray([math.fsum(self.weights[g]) for g in self.groups]);self.normalized=np.zeros(self.m);self.exact_normalized=[Fraction(0)]*self.m
  exact=[Fraction(str(float(w))) for w in self.weights]
  for i,g in enumerate(self.groups):
   denominator=sum((exact[j] for j in g),Fraction(0))
   for j in g:self.normalized[j]=float(self.weights[j])/float(self.total[i]);self.exact_normalized[j]=exact[j]/denominator
  self.base=np.asarray(reference._base_mass(self.pids,waves));self.base_exact=reference._exact_base_mass(self.pids,waves);self.base_integer=integer_masses(self.base_exact)
  groups_by_control=collections.defaultdict(list)
  for i,c in enumerate(self.cids):groups_by_control[c].append(i)
  self.duplicate_groups={c:g for c,g in groups_by_control.items() if len(g)>1};self.reused=list(self.duplicate_groups);self.known_cache={};self.paired_cache={};self.last_audit=None

 def paired(self,mask):
  key=np.packbits(mask).tobytes()
  if key not in self.paired_cache:
   ix=np.flatnonzero(mask);ids=[self.pids[i] for i in ix];mass=self.ref._base_mass(ids,self.waves);exact=self.ref._exact_base_mass(ids,self.waves);by={int(i):j for j,i in enumerate(ix)};kept=np.flatnonzero(mask[self.epi]);cmass=np.asarray([mass[by[int(self.epi[j])]]*float(self.normalized[j]) for j in kept]);cexact=[exact[by[int(self.epi[j])]]*self.exact_normalized[j] for j in kept]
   self.paired_cache[key]={'parent_ix':ix,'parent_ids':ids,'mass':np.asarray(mass),'exact':exact,'integer':integer_masses(exact),'kept':kept,'control_mass':cmass,'control_exact':cexact,'control_integer':integer_masses(cexact)}
  return self.paired_cache[key]

 def summarize(self,parent_reach,parent_values,control_reach,control_values,quantiles=(.5,.75,.9),detail=True):
  need=self.ref._need;pr=np.asarray(parent_reach,dtype=float);cr=np.asarray(control_reach,dtype=float);keys=sorted(parent_values);qs=[float(q) for q in quantiles]
  need(len(pr)==self.n and len(cr)==self.m,'REACH_LENGTH');need(bool(keys) and set(keys)==set(control_values) and set(keys)<={'hb','offer_s','alarm_offer_s'},'DERIVED_VALUE_KEYS');need(qs and len(qs)==len(set(qs)) and all(math.isfinite(q) and 0<=q<=1 for q in qs),'QUANTILES')
  pv={k:np.asarray(parent_values[k],dtype=float) for k in keys};cv={k:np.asarray(control_values[k],dtype=float) for k in keys}
  need(all(not bool(np.isinf(v).any()) for v in [pr,cr,*pv.values(),*cv.values()]),'INFINITE_MEASUREMENT')
  need(all(len(pv[k])==self.n and len(cv[k])==self.m for k in keys),'VALUE_LENGTH');need(bool(np.all(~np.isfinite(pr)|np.isin(pr,[0,1]))) and bool(np.all(~np.isfinite(cr)|np.isin(cr,[0,1]))),'REACH_MUST_BE_ZERO_ONE_OR_UNKNOWN');need(all(bool(np.all(~np.isfinite(v)|(v>=0))) for v in [*pv.values(),*cv.values()]),'NEGATIVE_HEAT_OR_TIME')
  for group in self.duplicate_groups.values():
   observations=[tuple(self.ref._number(v) for v in (cr[j],*(cv[k][j] for k in keys))) for j in group];need(all(o==observations[0] for o in observations),'CONFLICTING_CONTROL_IDENTITY')
  ck=np.isfinite(cr);known_key=np.packbits(ck).tobytes()
  if known_key not in self.known_cache:
   incomplete=np.bincount(self.epi,weights=(~ck).astype(np.int64),minlength=self.n)>0
   unknown=np.asarray([math.fsum(self.weights[g[~ck[g]]]) for g in self.groups]);self.known_cache[known_key]=(self.counts.astype(bool)&~incomplete,unknown,incomplete)
  controls_known,unknown,incomplete=self.known_cache[known_key];pair=np.isfinite(pr)&controls_known;prepared=self.paired(pair);ix=prepared['parent_ix'];kept=prepared['kept']
  standalone=profile(pr,pv,self.base,self.base_exact,self.base_integer,qs,self.ref);alarm=profile(pr[ix],{k:v[ix] for k,v in pv.items()},prepared['mass'],prepared['exact'],prepared['integer'],qs,self.ref);control=profile(cr[kept],{k:v[kept] for k,v in cv.items()},prepared['control_mass'],prepared['control_exact'],prepared['control_integer'],qs,self.ref)
  gap=alarm['reach_probability']-control['reach_probability'] if len(ix) else None
  differences={k:{str(q):alarm['conditional'][k]['quantiles'][str(q)]-control['conditional'][k]['quantiles'][str(q)] if alarm['conditional'][k]['quantiles'][str(q)] is not None and control['conditional'][k]['quantiles'][str(q)] is not None else None for q in qs} for k in keys}
  cmean=np.full(self.n,np.nan)
  for i in np.flatnonzero(controls_known):cmean[i]=math.fsum(float(self.normalized[j])*float(cr[j]) for j in self.groups[i])
  status=np.where(self.counts==0,0,np.where(~np.isfinite(pr),1,np.where(~controls_known,2,3))).astype('u1');delta=np.where(pair,pr-cmean,np.nan)
  self.last_audit={'status':status,'parent_reach':pr,'control_reach':cmean,'paired_reach_gap':delta,'paired_membership_key':np.packbits(pair).tobytes().hex()}
  rows=[]
  if detail:
   labels=['UNMATCHED','PARENT_REACH_UNKNOWN','CONTROL_REACH_UNKNOWN','PAIRED']
   for i,p in enumerate(self.pids):
    total=float(self.total[i]);u=float(unknown[i]);rows.append({'parent_id':self.ref._wire(p),'wave_id':self.ref._wire(self.waves[p]),'status':labels[status[i]],'eligible_edges':int(self.counts[i]),'eligible_mass':total,'known_eligible_mass':total-u,'unknown_eligible_mass':u,'unknown_eligible_fraction':u/total if total else None,'parent_reach':self.ref._number(pr[i]),'control_reach':self.ref._number(cmean[i]),'paired_reach_gap':self.ref._number(delta[i])})
  conditional_gaps=any(v['unknown_mass']>0 for p in (standalone,alarm,control) for v in p['conditional'].values())
  result={'status':'COMPLETED' if len(ix)==self.n and self.n and not conditional_gaps else 'COMPLETED_WITH_SCOPE_GAPS','standalone':standalone,'paired':{'parents':len(ix),'waves':len({self.waves[p] for p in prepared['parent_ids']}),'parent':alarm,'control':control,'reach_gap':gap,'conditional_quantile_differences':differences,'difference_estimand':'DESCRIPTIVE_CONDITIONAL_QUANTILE_DIFFERENCE','scalar_uncertainty':'UNAVAILABLE_DEPENDENCE_NOT_ESTABLISHED','quantile_uncertainty':'NOT_ESTABLISHED'},'coverage':{'parents':self.n,'eligible_edges':self.m,'paired_parents':len(ix),'unmatched_parents':int((self.counts==0).sum()),'parent_unknown':int((~np.isfinite(pr)).sum()),'control_incomplete_parents':int(incomplete.sum()),'eligible_edge_mass':math.fsum(self.weights),'unknown_eligible_edge_mass':math.fsum(self.weights[~ck])},'wave_population':{'source':'FROZEN_FULL_POPULATION_MAPPING','frozen_parents':len(self.waves),'selected_waves':len({self.waves[p] for p in self.pids}),'reclustered':False},'dependence':{'independence':'NOT_ESTABLISHED','note':'Global wave IDs remain fixed; cohort/month splits do not establish independent replication.'}}
  if detail:
   result['parents']=rows;result['paired'].update(parent_ids=[self.ref._wire(p) for p in prepared['parent_ids']],parent_base_mass=prepared['mass'].tolist(),control_inherited_mass=prepared['control_mass'].tolist());result['wave_population']['selected_wave_ids']=[self.ref._wire(self.waves[p]) for p in self.pids];result['dependence']['reused_control_ids']=[self.ref._wire(c) for c in self.reused]
  return result
