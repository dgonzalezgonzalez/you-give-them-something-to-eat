"""Independent fixtures and corner LP checks for fourth-revision projections."""
from pathlib import Path
import itertools,json
import numpy as np
import pandas as pd
from scipy.optimize import linprog
from distribution_regions import OBJECTS,SCORES,distribution_constraints,project,logical_interval,primitive_limits
from referee_revision import objective
from estimate import ARMS

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'

def corner_lp(lower,upper,comparators,costs,budget):
    """Direct epigraph over all 64 corners; does not call published dual helper."""
    corners=np.array(list(itertools.product(*zip(lower,upper))))
    rows=[];rhs=[]
    for r in comparators:
        for mu in corners:rows.append(np.r_[-mu,-1.]);rhs.append(-float(r@mu))
    rows.append(np.r_[costs,0.]);rhs.append(budget)
    fit=linprog(np.r_[np.zeros(6),1.],A_ub=rows,b_ub=rhs,
                A_eq=[np.r_[np.ones(6),0.]],b_eq=[1.],bounds=[(0,None)]*7,method='highs')
    if not fit.success:raise AssertionError(fit.message)
    return float(fit.fun)

def main():
    checks=[]
    def check(label,value):
        if not value:raise AssertionError(label)
        checks.append(label)
    A,b=distribution_constraints({'mean':(0.,12.)})
    low,high,_=project(A,b,'mean');check('Full-support simplex endpoints',np.allclose([low,high],[0,12]))
    A,b=distribution_constraints({'survival_6':(1.,1.)})
    low,high,_=project(A,b,'mean');check('Threshold probability implies six-group mean lower bound',np.allclose([low,high],[6,12]))
    A,b=distribution_constraints({'survival_6':(0.,.2),'survival_7':(.8,1.)})
    failed=False
    try:project(A,b,'mean')
    except ValueError:failed=True
    check('Incompatible CDF constraints fail rather than being dropped',failed)
    check('Affine duplicate transformations agree',
          np.allclose(objective(SCORES,'shortfall_12'),SCORES/12-1) and
          np.allclose(objective(SCORES,'shortfall_1'),objective(SCORES,'survival_1')-1))
    w=np.array([1.,3.,2.]);assigned=np.array([True,False,False]);identified=np.array([True,False,False])
    lo=np.array([4.,0.,0.]);hi=np.array([4.,12.,12.])
    possible_full=[];possible_observed=[]
    for y1,y2,r1,r2 in itertools.product(range(13),range(13),range(2),range(2)):
        possible_full.append((4+3*y1+2*y2)/6)
        possible_observed.append((4+3*r1*y1+2*r2*y2)/(1+3*r1+2*r2))
    for scope,values in [('weighted_baseline',possible_full),('identified_diets',possible_observed)]:
        limits=logical_interval(w,assigned,lo,hi,identified,(0.,12.),scope)
        check('Exhaustive 676-completion scalar endpoints '+scope,np.allclose(limits,[min(values),max(values)]))
        check('Logical positive weight-scale invariance '+scope,
              np.allclose(limits,logical_interval(7*w,assigned,lo,hi,identified,(0.,12.),scope)))
    # Equal shortfall endpoints must not turn an unidentified diet into R=1.
    lo=np.array([6.,0.,0.]);hi=np.array([12.,12.,12.]);identified=np.array([False,False,False])
    transformed_lo=objective(lo,'shortfall_6');transformed_hi=objective(hi,'shortfall_6')
    limits=logical_interval(w,assigned,transformed_lo,transformed_hi,identified,(-1.,0.),'identified_diets')
    check('Transform equality does not alter diet observability',np.allclose(limits,[-1,0]))
    regions=pd.read_csv(OUT/'distribution_projected_regions.csv')
    check('Complete projection grid',len(regions)==4*2*6*25 and not regions.duplicated(['method','scope','arm','outcome']).any())
    check('All projected intervals ordered',bool((regions.projected_lower<=regions.projected_upper+1e-10).all()))
    indexed=regions.set_index(['method','scope','arm','outcome'])
    for method in ['finite_distribution','logical_distribution']:
        old=indexed.loc[method];new=indexed.loc['finite_consistency_distribution']
        check('Intersection projection nested in '+method,
              bool((new.projected_lower>=old.projected_lower-1e-8).all() and
                   (new.projected_upper<=old.projected_upper+1e-8).all()))
    p=json.loads((OUT/'policies.json').read_text());policies=[{'Gikuriro':1.},*p['vertices'].values()]
    Q=np.array([[q.get(a,0.) for a in ARMS] for q in policies]);costs=np.array([p['costs'][a] for a in ARMS])
    certificates=pd.read_csv(OUT/'distribution_allocation_certificates.csv');corner_errors=[]
    for row in certificates.itertuples():
        sub=regions[(regions.method==row.method)&(regions.scope==row.scope)&(regions.outcome==row.objective)].set_index('arm').reindex(ARMS)
        independent=corner_lp(sub.projected_lower.to_numpy(),sub.projected_upper.to_numpy(),Q,costs,p['budget'])
        error=abs(independent-row.certificate);corner_errors.append(error)
        check('Independent 64-corner epigraph LP '+row.method+'/'+row.scope+'/'+row.objective,error<1e-8)
    referee=certificates[(certificates.method=='finite_distribution')&(certificates.scope=='weighted_baseline')&(certificates.objective=='mean')].certificate.item()
    check('Independent reproduction of referee rounded 8.151078',abs(referee-8.151078)<5e-7)
    # Verify retained endpoint witnesses against original primitive limits.
    audit=json.loads((OUT/'distribution-projection-validation.json').read_text())
    finite=pd.read_csv(OUT/'finite_arm_regions.csv');logical=pd.read_csv(OUT/'logical_arm_regions.csv')
    maximum_error=0.
    for receipt in audit['main_projection_witnesses']:
        f=primitive_limits(finite,receipt['arm'],receipt['scope'])
        l=logical[(logical.arm==receipt['arm'])&(logical.scope==receipt['scope'])].set_index('outcome')
        limits={name:(float(l.loc[name].logical_lower),float(l.loc[name].logical_upper)) for name in OBJECTS}
        if receipt['method']=='support_only':limits={name:((0.,12.) if name=='mean' else (0.,1.) if name.startswith('survival') else (-1.,0.)) for name in OBJECTS}
        elif receipt['method']=='finite_distribution':limits=f
        elif receipt['method']=='finite_consistency_distribution':limits={name:(max(f[name][0],limits[name][0]),min(f[name][1],limits[name][1])) for name in OBJECTS}
        A,b=distribution_constraints(limits)
        for key in ['lower_witness','upper_witness']:
            witness=np.array(receipt[key]);maximum_error=max(maximum_error,abs(witness.sum()-1),max(0.,float(np.max(A@witness-b))),max(0.,-float(witness.min())))
    check('All 192 retained endpoint witnesses independently feasible',maximum_error<1e-8)
    result={'scope':'Implementation and mathematical-fixture checks, not coverage validation, microdata external replication or a sharpness theorem.',
            'checks_passed':len(checks),'checks':checks,'maximum_independent_corner_lp_error':max(corner_errors),
            'maximum_independent_witness_error':maximum_error,'referee_mean_projection_reproduced':referee}
    (OUT/'distribution-validation.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print(f'Distribution revision: {len(checks)}/{len(checks)} meaningful checks passed. Maximum independent corner-LP error {max(corner_errors):.3g}.')

if __name__=='__main__':main()
