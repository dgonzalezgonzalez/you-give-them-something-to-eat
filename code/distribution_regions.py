"""Coherent distributional projections of existing finite-family intervals.

Fourth-referee revision in progress. No new observations or coverage event.
The true arm distribution lies in this outer polytope on the previously proved
conditional event. Moment-wise logical consistency constraints can tighten it
but do not establish a sharp joint identification region. Scalar projections
are exact for the specified polytope, not for all finite potential outcomes.
"""
from pathlib import Path
import json,itertools
import numpy as np
import pandas as pd
from scipy.optimize import linprog
from estimate import ARMS,TX
from referee_revision import GROUPS,score_interval,objective
from policy_allocation import solve_allocation

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'
OBJECTS=['mean',*[f'survival_{k}' for k in range(1,13)],*[f'shortfall_{k}' for k in range(1,13)]]
SCORES=np.arange(13,dtype=float)

def logical_interval(weights,assigned,lower,upper,identified,support,scope):
    """Valid scalar consistency bounds; score observability fixed explicitly."""
    L,H=support;unassigned=float(weights[~assigned].sum())
    if scope=='weighted_baseline':
        D=float(weights.sum())
        return ((float(weights[assigned]@lower[assigned])+L*unassigned)/D,
                (float(weights[assigned]@upper[assigned])+H*unassigned)/D)
    if scope!='identified_diets':raise ValueError('Unknown target scope')
    known=assigned&identified;D=float(weights[known].sum())+unassigned
    if not D:return L,H
    N=float(weights[known]@lower[known])
    return (N+L*unassigned)/D,(N+H*unassigned)/D

def primitive_limits(source,arm,scope):
    selected=source[source.arm==arm]
    if scope=='weighted_baseline':
        lower=selected[selected.scope=='lower_endpoint'].set_index('outcome').finite_lower
        upper=selected[selected.scope=='upper_endpoint'].set_index('outcome').finite_upper
    elif scope=='identified_diets':
        selected=selected[selected.scope==scope].set_index('outcome')
        lower=selected.finite_lower;upper=selected.finite_upper
    else:raise ValueError('Unknown target scope')
    return {name:(float(lower.loc[name]),float(upper.loc[name])) for name in OBJECTS}

def distribution_constraints(limits):
    A=[];b=[]
    for name,(lo,hi) in limits.items():
        if lo>hi+1e-10:raise ValueError('Incompatible primitive endpoints')
        v=objective(SCORES,name)
        A.extend([v,-v]);b.extend([hi,-lo])
    return np.array(A),np.array(b)

def project(A,b,name):
    """Two independent primal LPs, retained endpoint distribution witnesses."""
    v=objective(SCORES,name);results=[]
    for sign in (1.,-1.):
        fit=linprog(sign*v,A_ub=A,b_ub=b,A_eq=np.ones((1,13)),b_eq=[1.],
                    bounds=[(0,None)]*13,method='highs')
        if not fit.success:
            raise ValueError('Empty/unsolved coherent distribution region: '+fit.message)
        residual=max(0.,float(np.max(A@fit.x-b)),abs(float(fit.x.sum()-1)),float(-fit.x.min()))
        if residual>1e-8:raise ValueError('Distribution LP witness is infeasible')
        results.append((float(v@fit.x),fit.x.tolist(),residual))
    return results[0][0],results[1][0],{'lower_witness':results[0][1],
                                      'upper_witness':results[1][1],
                                      'max_feasibility_residual':max(x[2] for x in results)}

def main():
    source=pd.read_csv(OUT/'finite_arm_regions.csv')
    d=pd.read_csv(ROOT/'data/input/households.csv');d['arm']='Control'
    for arm,tx in zip(ARMS[1:],TX):d.loc[d[tx]==1,'arm']=arm
    b=d[(d['round']==1)&(d.eligible==1)].copy()
    e=d[(d['round']==2)&(d.eligible==1)&(d.sample_panel==1)]
    food=[f'm9_{k}' for g in GROUPS for k in g]
    full=b.drop(columns=food).merge(e[['hhid',*food]],on='hhid',how='left',validate='one_to_one')
    lo,hi=score_interval(full);identified=lo==hi;w=full.samp_wgt.to_numpy()
    rows=[];receipts=[];logical=[]
    for scope,arm in itertools.product(['weighted_baseline','identified_diets'],ARMS):
        finite=primitive_limits(source,arm,scope);consistency={}
        for name in OBJECTS:
            L,H=(0.,12.) if name=='mean' else ((0.,1.) if name.startswith('survival') else (-1.,0.))
            bounds=logical_interval(w,full.arm.eq(arm).to_numpy(),objective(lo,name),objective(hi,name),
                                    identified,(L,H),scope)
            consistency[name]=bounds
            logical.append({'arm':arm,'scope':scope,'outcome':name,
                            'logical_lower':bounds[0],'logical_upper':bounds[1]})
        support={name:((0.,12.) if name=='mean' else (0.,1.) if name.startswith('survival') else (-1.,0.)) for name in OBJECTS}
        for method,limits in [('support_only',support),('finite_distribution',finite),('logical_distribution',consistency),
                               ('finite_consistency_distribution',{name:(max(finite[name][0],consistency[name][0]),
                                                                         min(finite[name][1],consistency[name][1])) for name in OBJECTS})]:
            A,bb=distribution_constraints(limits)
            for name in OBJECTS:
                lower,upper,receipt=project(A,bb,name)
                rows.append({'method':method,'scope':scope,'arm':arm,'outcome':name,
                             'projected_lower':lower,'projected_upper':upper})
                if name in ('mean','shortfall_6'):receipts.append({'method':method,'scope':scope,'arm':arm,'outcome':name,**receipt})
    regions=pd.DataFrame(rows);regions.to_csv(OUT/'distribution_projected_regions.csv',index=False)
    pd.DataFrame(logical).to_csv(OUT/'logical_arm_regions.csv',index=False)
    p=json.loads((OUT/'policies.json').read_text());base={'Gikuriro':{'Gikuriro':1.},**p['vertices']}
    allocations=[]
    for method,scope,name in itertools.product(regions.method.unique(),regions.scope.unique(),['mean','shortfall_6']):
        sub=regions[(regions.method==method)&(regions.scope==scope)&(regions.outcome==name)].set_index('arm').reindex(ARMS)
        A=[];bb=[]
        for unit,row in zip(np.eye(6),sub.itertuples()):
            A.extend([unit,-unit]);bb.extend([row.projected_upper,-row.projected_lower])
        result=solve_allocation(np.array(A),np.array(bb),base,p['costs'],p['budget'])
        allocations.append({'method':method,'scope':scope,'objective':name,
                            'certificate':result['certificate'],'expected_cost':result['expected_cost'],
                            **{a+'_probability':x for a,x in result['probabilities'].items()},
                            'primal_dual_gap':result['primal_dual_gap']})
    pd.DataFrame(allocations).to_csv(OUT/'distribution_allocation_certificates.csv',index=False)
    (OUT/'distribution-projection-validation.json').write_text(json.dumps({
        'scope':'Projection of an outer coherent score-distribution polytope; finite methods inherit existing conditional family coverage, logical method is fixed-sample consistency only. No additional multiplicity or joint sharpness claim.',
        'projection_rows':len(rows),'primitive_display_transformations':25,'distinct_transformations':23,
        'main_projection_witnesses':receipts,'allocation_rows':len(allocations),
        'maximum_witness_residual':max(r['max_feasibility_residual'] for r in receipts),
        'maximum_allocation_primal_dual_gap':max(r['primal_dual_gap'] for r in allocations)},indent=2),encoding='utf8')
    print(pd.DataFrame(allocations)[['method','scope','objective','certificate']].to_string(index=False))

if __name__=='__main__':main()
