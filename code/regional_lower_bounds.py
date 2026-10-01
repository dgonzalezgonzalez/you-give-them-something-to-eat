"""Certified minimax lower bounds for the implemented shared outer regions.

Feasible exact-rational distributions form a finite adversarial subset. An
exact feasible dual for its policy LP supplies a lower bound. Paired existing
proposal upper certificates bracket each region's optimized loss. This is
not a lower bound for all confidence procedures, statistical minimax risk,
sharp potential-outcome populations, or the narrower conceptual event.
"""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal
import json,time
import numpy as np
from scipy.optimize import linprog
from quota_models import build_models,ARMS
from quota_arithmetic import I,mixture_upper
from quota_benchmarks import fraction_interval
from quota_allocation import exact_vertices

ROOT=Path(__file__).resolve().parents[1]
GRID=10**10

def rationalize(point,floor):
    f=[F(float(x)) for x in floor];mass=1-sum(f)
    free=np.maximum(np.asarray(point)-np.asarray(floor),0.)
    if free.sum()==0:free=np.ones(len(free))
    ideal=GRID*free/free.sum();integer=np.floor(ideal).astype(np.int64)
    # Deterministic largest remainder makes unit mass exact.
    for j in np.argsort(-(ideal-integer),kind='stable')[:GRID-int(integer.sum())]:integer[j]+=1
    if sum(integer)!=GRID:raise ValueError('Rational population grid failed')
    return [f[j]+mass*F(int(integer[j]),GRID) for j in range(len(f))]

def logical_member(model,point):
    return sum(point)==1 and all(x>=F(float(f)) for x,f in zip(point,model['floor'])) and all(
        sum(F(float(a))*p for a,p in zip(row,point))<=F(float(b)) for row,b in zip(model['A'],model['b']))

def enclosed_event(models,points):
    return mixture_upper(models,[[fraction_interval(p) for p in point] for point in points])

def interior_population(models):
    points=[]
    for m in models:
        A=np.c_[m['A'],np.ones(len(m['b']))]
        floor_rows=np.c_[-np.eye(13),np.ones(13)]
        fit=linprog(np.r_[np.zeros(13),-1.],A_ub=np.r_[A,floor_rows],b_ub=np.r_[m['b'],-m['floor']],
                    A_eq=[np.r_[np.ones(13),0.]],b_eq=[1.],bounds=[(0.,1.)]*14,method='highs')
        if not fit.success or fit.x[-1]<=0:raise ValueError('No strict logical centre')
        centre=fit.x[:13]
        for fraction in [.001,.0001,.00001,.000001]:
            point=rationalize((1-fraction)*m['seed']+fraction*centre,m['floor'])
            if logical_member(m,point):break
        else:raise ValueError('Could not enclose a logical seed')
        points.append(point)
    if enclosed_event(models,points)>=5520:raise ValueError('Rational interior seed outside event')
    return points

def feasible_candidate(models,seed,proposed):
    points=[]
    for m,p,s in zip(models,proposed,seed):
        # A small exact convex displacement into the seed handles a candidate
        # on a logical boundary; no feasibility tolerance is admitted.
        for fraction in [.0001,.001,.01,.1,1.]:
            point=rationalize((1-fraction)*np.asarray(p)+fraction*np.asarray([float(x) for x in s]),m['floor'])
            if logical_member(m,point):break
        else:raise ValueError('Exact logical candidate not found')
        points.append(point)
    if enclosed_event(models,points)<=5520:return points,F(1)
    low=0;high=2**36
    def blend(integer):
        a=F(integer,2**36)
        return [[(1-a)*s+a*p for s,p in zip(srow,prow)] for srow,prow in zip(seed,points)]
    def diagnostic(integer):
        # Floating evaluation selects a candidate only. Its final inclusion
        # is checked by directed arithmetic below, independent of this root.
        a=integer/2**36
        return sum(float(np.exp(m['C']@np.asarray([(1-a)*float(s)+a*float(p) for s,p in zip(srow,prow)])+m['intercept']).sum())
                   for m,srow,prow in zip(models,seed,points))
    while high-low>1:
        mid=(low+high)//2
        if diagnostic(mid)<=5520:low=mid
        else:high=mid
    result=blend(low)
    # A diagnostic near the boundary may have rounded to the wrong side.
    # Move into the certified seed, retaining exact rational coordinates.
    while enclosed_event(models,result)>5520:
        low=max(0,low-1);result=blend(low)
    if not all(logical_member(m,p) for m,p in zip(models,result)) or enclosed_event(models,result)>5520:raise ValueError('Feasible population enclosure failed')
    return result,F(low,2**36)

def finite_adversary_lower(means,vertices,cost,budget):
    constraints=[];constants=[];sources=[]
    for index,mu in enumerate(means):
        for comparator,v in enumerate(vertices):
            constraints.append([-float(x) for x in mu]+[-1.])
            constants.append(-float(sum(x*y for x,y in zip(v,mu))))
            sources.append((index,comparator))
    fit=linprog([0.]*len(cost)+[1.],A_ub=constraints+[[float(x) for x in cost]+[0.]],
                b_ub=constants+[float(budget)],A_eq=[[1.]*len(cost)+[0.]],b_eq=[1.],
                bounds=[(0.,None)]*len(cost)+[(None,None)],method='highs')
    if not fit.success:raise ValueError(fit.message)
    raw=[max(F(0),-F(float(x))) for x in fit.ineqlin.marginals[:-1]]
    total=sum(raw)
    if total<=0:raise ValueError('Nonzero adversarial probability required')
    probability=[x/total for x in raw];eta=max(F(0),-F(float(fit.ineqlin.marginals[-1])))
    average=[sum(w*means[index][j] for w,(index,comparator) in zip(probability,sources)) for j in range(len(cost))]
    constant=sum(w*sum(x*y for x,y in zip(vertices[comparator],means[index])) for w,(index,comparator) in zip(probability,sources))
    lower=constant-eta*budget-max(v-eta*c for v,c in zip(average,cost))
    return max(F(0),lower),{'probabilities':[str(x) for x in probability],'source_indices':sources,
                         'nonnegative_cost_multiplier':str(eta),'exact_dual_lower':str(lower),
                         'floating_candidate_objective':float(fit.fun),
                         'scope':'Exact nonnegative probabilities normalized to one; exact nonnegative cost multiplier. No solver dual-feasibility tolerance or floating objective certifies the lower bound.'}

def main():
    start=time.time();benchmark=json.loads((ROOT/'output/quota-benchmarks.json').read_text())
    policy=json.loads((ROOT/'output/policies.json').read_text());cost=[F(policy['costs'][a]) for a in ARMS];budget=F(policy['budget'])
    labels,vertices=exact_vertices(cost,budget);rows=[];receipts=[]
    for item in benchmark['receipts']:
        if item['event']!='shared':continue
        models,_=build_models(item['moments'])
        if not item['bin_floors']:models=[{**m,'floor':np.zeros(13)} for m in models]
        seed=interior_population(models);populations=[seed];origins=[{'type':'rational_interior_seed'}]
        for scenario in item['scenarios']:
            for comparator in scenario['comparators']:
                point,shrink=feasible_candidate(models,seed,[a['candidate'] for a in comparator['arms']])
                populations.append(point);origins.append({'objective':scenario['objective'],'comparator':comparator['comparator'],'event_shrink_fraction':str(shrink)})
        exact_populations=[[[str(x) for x in point] for point in population] for population in populations]
        event_values=[enclosed_event(models,population) for population in populations]
        for scenario in item['scenarios']:
            objective=scenario['objective'];score=[F(s) if objective=='mean' else -F(max(6-s,0),6) for s in range(13)]
            means=[[sum(x*y for x,y in zip(point,score)) for point in population] for population in populations]
            lower,dual=finite_adversary_lower(means,vertices,cost,budget)
            upper=F(scenario['conditional_loss_upper'])
            if lower>upper:raise ValueError('Region lower exceeds proposal upper')
            row={'method':item['method'],'bin_floors':item['bin_floors'],'objective':objective,
                 'regional_minimax_lower':fraction_interval(lower).lower_float(),
                 'fixed_proposal_loss_upper':scenario['conditional_loss_upper'],
                 'certified_upper_minus_lower':fraction_interval(upper-lower).upper_float(),
                 'feasible_outer_populations':len(populations)}
            rows.append(row);print(json.dumps(row),flush=True)
            receipts.append({'method':item['method'],'bin_floors':item['bin_floors'],'objective':objective,
                'exact_feasible_populations':exact_populations,'population_origins':origins,
                'enclosed_event_values':event_values,'exact_arm_means':[[str(x) for x in mu] for mu in means],
                'dual':dual,'exact_lower':str(lower),'exact_proposal_upper':str(upper)})
    report={'scope':'Exact-rational feasible probability distributions inside each implemented shared-event outer region and a finite-adversary feasible policy-LP dual certify a regional minimax lower bound. Existing exact-rational proposal certificates give upper bounds for the same region, hence a certified optimization bracket. Lower bounds concern these implemented outer regions only: not the narrower conceptual e-tests, joint-sharp finite potential populations, actual true regret, sampling minimax risk or all valid inference procedures. Candidate populations and all exact dual probabilities are retained; floating optimization values do not certify anything.',
            'rows':rows,'receipts':receipts,'seconds':time.time()-start}
    (ROOT/'output/regional-minimax-brackets.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print('Regional brackets seconds',report['seconds'],flush=True)

if __name__=='__main__':main()
