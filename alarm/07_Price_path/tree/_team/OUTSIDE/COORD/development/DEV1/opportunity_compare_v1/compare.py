"""WP3: pure, one-cohort comparison of canonical-derived reach/heat/time.

No reads, wave clustering, measurement reconstruction or inferential claims.
DEV2 supplies complete eligible edges and the frozen full-population wave map.
"""
import math
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path
import numpy as np

TOOLS = Path('<LAB_REPO>/forensics/team/RESEARCH/tools')
if str(TOOLS) not in sys.path: sys.path.insert(0, str(TOOLS))
from labcore.waves import wave_weights


def _need(ok, reason):
    if not ok: raise ValueError(reason)


def _number(x):
    if x is None: return None
    try: v = float(x)
    except (TypeError, ValueError) as e: raise ValueError('NON_NUMERIC_MEASUREMENT') from e
    if math.isnan(v): return None
    _need(math.isfinite(v), 'INFINITE_MEASUREMENT')
    return v


def _wire(x):
    if isinstance(x, np.generic): return x.item()
    if isinstance(x, tuple): return [_wire(v) for v in x]
    return x


def _identity(x):
    _need(x is not None and x != '', 'EMPTY_IDENTITY')
    try: hash(x)
    except TypeError as e: raise ValueError('UNHASHABLE_IDENTITY') from e
    return x


def _base_mass(ids, frozen_wave_ids):
    if not ids: return []
    # Encode labels only for the shared primitive; never recompute clustering.
    labels = {}; codes = []
    for pid in ids:
        label = _identity(frozen_wave_ids[pid])
        if label not in labels: labels[label] = len(labels)
        codes.append(labels[label])
    return (wave_weights(np.asarray(codes)) / len(labels)).tolist()


def _exact_base_mass(ids, frozen_wave_ids):
    """Keep the declared equal-wave/parent ratios before float conversion."""
    counts = Counter(frozen_wave_ids[p] for p in ids)
    return [Fraction(1, len(counts)*counts[frozen_wave_ids[p]]) for p in ids]


def _quantile(values, masses, q):
    """Inverse CDF over exact mass fractions; q uses its declared decimal form."""
    pairs = sorted(zip(values, masses), key=lambda x:x[0])
    if not pairs: return None
    target = Fraction(str(q)) * sum((w for _,w in pairs), Fraction(0))
    partial = Fraction(0)
    for value, weight in pairs:
        partial += weight
        if partial >= target: return value
    raise AssertionError('EXACT_CDF_ENDPOINT_NOT_REACHED')


def _profile(reach, values, mass, quantiles, exact_mass):
    known = [i for i,r in enumerate(reach) if r is not None]
    hit = [i for i,r in enumerate(reach) if r == 1]
    no = [i for i,r in enumerate(reach) if r == 0]
    missing = [i for i,r in enumerate(reach) if r is None]
    total = math.fsum(mass); known_mass = math.fsum(mass[i] for i in known)
    hit_mass = math.fsum(mass[i] for i in hit)
    out = {'rows':len(reach), 'base_mass':total, 'known_reach_mass':known_mass,
        'reached_mass':hit_mass, 'known_nonreach_mass':math.fsum(mass[i] for i in no),
        'unknown_reach_mass':math.fsum(mass[i] for i in missing),
        'reach_probability':hit_mass/known_mass if known_mass else None,
        'reached_rows':len(hit), 'known_nonreach_rows':len(no), 'unknown_reach_rows':len(missing),
        'conditional':{}}
    for name, column in values.items():
        observed = [i for i in hit if column[i] is not None]
        unknown = missing + [i for i in hit if column[i] is None]
        observed_mass = math.fsum(mass[i] for i in observed)
        unknown_mass = math.fsum(mass[i] for i in unknown)
        status = ('EMPTY' if not reach else 'PARTIAL_UNKNOWN' if unknown_mass else
                  'OBSERVED' if observed_mass else 'NO_REACH')
        out['conditional'][name] = {'status':status, 'base_mass':total,
            'reached_mass':hit_mass, 'known_reached_mass':observed_mass,
            'not_applicable_mass':out['known_nonreach_mass'], 'unknown_mass':unknown_mass,
            'observed_rows':len(observed), 'unknown_rows':len(unknown),
            'quantiles':{str(q):_quantile([column[i] for i in observed],[exact_mass[i] for i in observed],q)
                         for q in quantiles}, 'quantile_uncertainty':'NOT_ESTABLISHED'}
    return out


def summarize(parent_ids, frozen_wave_ids, parent_reach, parent_values,
              edge_parent_ids, control_ids, eligible_edge_weights, control_reach,
              control_values, *, quantiles=(.5,.75,.9)):
    """Return standalone and complete-reach-paired summaries for one cohort.

    Parent arrays have length N; control arrays have one row per eligible edge M.
    Value mappings carry hb, offer_s, alarm_offer_s (any nonempty matching subset).
    None/NaN means unknown. Reach zero makes conditional values NOT_APPLICABLE.
    Unlinked eligible edges MUST remain with unknown measurements. Original draw
    and rule-excluded masses are upstream; these weights are eligible mass only.
    """
    pids = [_identity(x) for x in parent_ids]; ep = [_identity(x) for x in edge_parent_ids]
    cids = [_identity(x) for x in control_ids]; n,m = len(pids),len(ep)
    _need(len(set(pids)) == n, 'DUPLICATE_PARENT')
    _need(len(cids)==len(eligible_edge_weights)==len(control_reach)==m, 'EDGE_LENGTH')
    _need(len(parent_reach)==n, 'PARENT_LENGTH')
    _need(all(p in frozen_wave_ids for p in pids), 'MISSING_FROZEN_WAVE_ID')
    _need(set(ep) <= set(pids), 'EDGE_PARENT_OUTSIDE_COHORT')
    _need(len(set(zip(ep,cids))) == m, 'DUPLICATE_ELIGIBLE_EDGE')
    keys = sorted(parent_values)
    _need(bool(keys) and set(keys)==set(control_values) and
          set(keys)<={'hb','offer_s','alarm_offer_s'}, 'DERIVED_VALUE_KEYS')
    _need(all(len(parent_values[k])==n and len(control_values[k])==m for k in keys), 'VALUE_LENGTH')
    qs = [float(q) for q in quantiles]
    _need(qs and len(qs)==len(set(qs)) and all(math.isfinite(q) and 0<=q<=1 for q in qs), 'QUANTILES')
    pr = [_number(v) for v in parent_reach]; cr = [_number(v) for v in control_reach]
    _need(all(v in (None,0,1) for v in pr+cr), 'REACH_MUST_BE_ZERO_ONE_OR_UNKNOWN')
    pv = {k:[_number(v) for v in parent_values[k]] for k in keys}
    cv = {k:[_number(v) for v in control_values[k]] for k in keys}
    _need(all(v is None or v>=0 for col in [*pv.values(),*cv.values()] for v in col), 'NEGATIVE_HEAT_OR_TIME')
    weights = [_number(w) for w in eligible_edge_weights]
    _need(all(w is not None and w>0 for w in weights), 'POSITIVE_FINITE_ELIGIBLE_WEIGHT_REQUIRED')
    # Numeric edge weights are interpreted by their declared decimal forms.
    # Never infer rationals from already-rounded normalized/base masses.
    exact_weights = [Fraction(str(w)) for w in weights]
    reused = {}
    for j,c in enumerate(cids):
        observation = (cr[j],*(cv[k][j] for k in keys))
        _need(c not in reused or reused[c]==observation, 'CONFLICTING_CONTROL_IDENTITY')
        reused[c] = observation
    edges = {p:[] for p in pids}
    for j,p in enumerate(ep): edges[p].append(j)
    normalized = [0.0]*m; exact_normalized = [Fraction(0)]*m; complete=[]; parent_rows=[]
    for i,p in enumerate(pids):
        ix=edges[p]; total=math.fsum(weights[j] for j in ix)
        unknown=math.fsum(weights[j] for j in ix if cr[j] is None)
        exact_total = sum((exact_weights[j] for j in ix), Fraction(0))
        for j in ix:
            normalized[j]=weights[j]/total
            exact_normalized[j]=exact_weights[j]/exact_total
        controls_known=bool(ix) and all(cr[j] is not None for j in ix)
        paired=pr[i] is not None and controls_known
        if paired: complete.append(i)
        cmean=math.fsum(normalized[j]*cr[j] for j in ix) if controls_known else None
        status=('UNMATCHED' if not ix else 'PARENT_REACH_UNKNOWN' if pr[i] is None else
                'CONTROL_REACH_UNKNOWN' if not controls_known else 'PAIRED')
        parent_rows.append({'parent_id':_wire(p),'wave_id':_wire(frozen_wave_ids[p]),'status':status,
            'eligible_edges':len(ix),'eligible_mass':total,'known_eligible_mass':total-unknown,
            'unknown_eligible_mass':unknown,'unknown_eligible_fraction':unknown/total if total else None,
            'parent_reach':pr[i],'control_reach':cmean,
            'paired_reach_gap':pr[i]-cmean if paired else None})
    standalone_mass=_base_mass(pids,frozen_wave_ids)
    standalone_exact=_exact_base_mass(pids,frozen_wave_ids)
    paired_ids=[pids[i] for i in complete]; paired_mass=_base_mass(paired_ids,frozen_wave_ids)
    paired_exact=_exact_base_mass(paired_ids,frozen_wave_ids)
    base_by_parent=dict(zip(paired_ids,paired_mass)); kept=[j for j,p in enumerate(ep) if p in base_by_parent]
    exact_by_parent=dict(zip(paired_ids,paired_exact))
    control_mass=[base_by_parent[ep[j]]*normalized[j] for j in kept]
    control_exact=[exact_by_parent[ep[j]]*exact_normalized[j] for j in kept]
    alarm=_profile([pr[i] for i in complete],{k:[pv[k][i] for i in complete] for k in keys},paired_mass,qs,paired_exact)
    control=_profile([cr[j] for j in kept],{k:[cv[k][j] for j in kept] for k in keys},control_mass,qs,control_exact)
    gap=(alarm['reach_probability']-control['reach_probability']) if complete else None
    differences={k:{str(q):(alarm['conditional'][k]['quantiles'][str(q)]-
                              control['conditional'][k]['quantiles'][str(q)])
                        if alarm['conditional'][k]['quantiles'][str(q)] is not None and
                           control['conditional'][k]['quantiles'][str(q)] is not None else None for q in qs}
                 for k in keys}
    counts=Counter(cids); reused_ids=[_wire(c) for c in counts if counts[c]>1]
    standalone=_profile(pr,pv,standalone_mass,qs,standalone_exact)
    conditional_gaps=any(v['unknown_mass'] > 0 for profile in (standalone,alarm,control)
                         for v in profile['conditional'].values())
    return {'status':'COMPLETED' if len(complete)==n and n and not conditional_gaps else 'COMPLETED_WITH_SCOPE_GAPS',
        'standalone':standalone,
        'paired':{'parent_ids':[_wire(p) for p in paired_ids],'parents':len(complete),
            'waves':len({frozen_wave_ids[p] for p in paired_ids}),
            'parent_base_mass':paired_mass,'control_inherited_mass':control_mass,
            'parent':alarm,'control':control,'reach_gap':gap,
            'conditional_quantile_differences':differences,
            'difference_estimand':'DESCRIPTIVE_CONDITIONAL_QUANTILE_DIFFERENCE',
            'scalar_uncertainty':'UNAVAILABLE_DEPENDENCE_NOT_ESTABLISHED',
            'quantile_uncertainty':'NOT_ESTABLISHED'},
        'coverage':{'parents':n,'eligible_edges':m,'paired_parents':len(complete),
            'unmatched_parents':sum(r['status']=='UNMATCHED' for r in parent_rows),
            'parent_unknown':sum(r is None for r in pr),
            'control_incomplete_parents':sum(bool(edges[p]) and any(cr[j] is None for j in edges[p]) for p in pids),
            'eligible_edge_mass':math.fsum(weights),
            'unknown_eligible_edge_mass':math.fsum(weights[j] for j in range(m) if cr[j] is None)},
        'parents':parent_rows,
        'wave_population':{'source':'FROZEN_FULL_POPULATION_MAPPING','frozen_parents':len(frozen_wave_ids),
            'selected_wave_ids':[_wire(frozen_wave_ids[p]) for p in pids],
            'selected_waves':len({frozen_wave_ids[p] for p in pids}),'reclustered':False},
        'dependence':{'reused_control_ids':reused_ids,'independence':'NOT_ESTABLISHED',
            'note':'Global wave IDs remain fixed; cohort/month splits do not establish independent replication.'}}
