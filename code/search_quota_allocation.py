"""Optional exploratory exchange search for allocation proposals.

All tangent cuts are outer. Feasible interpolated adversaries supply a lower
optimization bound; outer LP support values supply an upper one. The shared
sum of exponential terms is retained instead of taking its scalar box image.
"""
from pathlib import Path
import json,itertools,time,argparse
import numpy as np
from scipy.linalg import block_diag
from scipy.optimize import linprog,minimize,minimize_scalar
from scipy.special import logsumexp
r=Path(__file__).resolve().parents[1];start=time.time()
from quota_models import build_models,ARMS
from referee_revision import objective
parser=argparse.ArgumentParser()
parser.add_argument('--moment-method',choices=['quota','harmonic_martingale'],default='quota')
args=parser.parse_args()
if args.moment_method=='quota':moment_rows=json.loads((r/'output/quota-normalizers.json').read_text())['rows']
else:
    from quota_benchmarks import classical_rows
    moment_rows=classical_rows(args.moment_method)
models,names=build_models(moment_rows);arms=ARMS;n=78
T=np.array([objective(np.arange(13),name) for name in names])
mean_map=block_diag(*[T[0][None,:]]*6)
A=block_diag(*[m['A'] for m in models]);bb=np.concatenate([m['b'] for m in models])
E=block_diag(*[np.ones((1,13))]*6);ee=np.ones(6)
bounds=[(float(x),1.) for m in models for x in m['floor']]
seed=np.concatenate([m['seed'] for m in models])
cap=5520.;logcap=np.log(cap)
def fun(p):
    items=[m['function'](p[i*13:(i+1)*13]) for i,m in enumerate(models)]
    values=np.array([x[0] for x in items]);logF=float(logsumexp(values))
    grad=np.concatenate([np.exp(values[i]-logF)*items[i][1] for i in range(6)])
    return logF,grad
assert fun(seed)[0]<logcap
cuts=[];rhs=[];calls=[]
def support(direction):
    cache={}
    def dual(tau):
        tau=float(tau)
        if tau in cache:return cache[tau][0]
        points=[];upper=tau;statuses=[]
        for i,m in enumerate(models):
            d=direction[i*13:(i+1)*13];ff=m['function']
            def objective(p):
                val,grad=ff(p);F=np.exp(val-logcap)
                return -d@p+tau*F,-d+tau*F*grad
            constraints=[{'type':'eq','fun':lambda p:p.sum()-1,'jac':lambda p:np.ones(13)},
                         {'type':'ineq','fun':lambda p,m=m:m['b']-m['A']@p,'jac':lambda p,m=m:-m['A']}]
            pp=minimize(lambda p:objective(p)[0],m['seed'],jac=lambda p:objective(p)[1],
                        constraints=constraints,bounds=[(x,1.) for x in m['floor']],method='SLSQP',
                        options={'maxiter':300,'ftol':1e-11})
            value,grad=objective(pp.x)
            ll=linprog(grad,A_ub=m['A'],b_ub=m['b'],A_eq=[np.ones(13)],b_eq=[1.],
                       bounds=[(x,1.) for x in m['floor']],method='highs')
            if not ll.success:raise ValueError(ll.message)
            # Convex objective tangent gives its global minimum lower bound.
            minimum_lower=value-grad@pp.x+ll.fun-1e-8
            upper-=minimum_lower
            feasible=max(abs(pp.x.sum()-1),float(np.maximum(m['A']@pp.x-m['b'],0).max()),float(np.maximum(m['floor']-pp.x,0).max()))
            points.append(pp.x if feasible<1e-8 else m['seed'])
            statuses.append({'success':bool(pp.success),'nit':int(pp.nit),'feasibility':feasible})
        cache[tau]=(float(upper),np.concatenate(points),statuses)
        return float(upper)
    # Every tau>=0 gives a valid Lagrangian upper bound. Scalar optimization
    # only chooses a tighter such bound; global minimization is unnecessary.
    trial=minimize_scalar(dual,bounds=(.001,30.),method='bounded',options={'xatol':1e-5,'maxiter':24})
    tau=min(cache,key=lambda x:cache[x][0]);upper,point,status=cache[tau]
    left=0.;right=1.
    for _ in range(50):
        weight=(left+right)/2;candidate=weight*point+(1-weight)*seed
        if fun(candidate)[0]<=logcap-1e-9:left=weight
        else:right=weight
    witness=left*point+(1-left)*seed
    assert fun(witness)[0]<=logcap
    lower=float(direction@witness)
    calls.append({'dual_tau':tau,'outer_inner_gap':upper-lower,'tau_evaluations':len(cache),
                  'inner_statuses':status,'log_witness_constraint':fun(witness)[0]-logcap})
    return upper+1e-7,witness

policies_file=json.loads((r/'output/policies.json').read_text());policies={'Gikuriro':{'Gikuriro':1.},**policies_file['vertices']};comp=np.array([[q.get(a,0.) for a in arms] for q in policies.values()])
costs=np.array([policies_file['costs'][a] for a in arms]);budget=policies_file['budget']
scenarios=[]
for name in ['mean','shortfall_6']:
    values=objective(np.arange(13),name)
    value_map=block_diag(*[values[None,:]]*6)
    witnesses=[value_map@seed];receipt=[]
    for iteration in range(30):
        # Every stored mean vector belongs to the shared confidence set.
        constraints=np.array([np.r_[-mu,-1.] for mu in witnesses for c in comp])
        targets=np.array([-c@mu for mu in witnesses for c in comp])
        fit=linprog(np.r_[np.zeros(6),1.],A_ub=np.r_[constraints,[np.r_[costs,0.]]],
                    b_ub=np.r_[targets,budget],A_eq=[np.r_[np.ones(6),0.]],b_eq=[1.],
                    bounds=[(0.,1.)]*6+[(0.,None)],method='highs')
        if not fit.success:raise ValueError(fit.message)
        q=fit.x[:6];upper=0.
        for comparator in comp:
            bound,witness=support((comparator-q)@value_map)
            upper=max(upper,bound);witnesses.append(value_map@witness)
        gap=upper-fit.fun
        receipt.append({'iteration':iteration+1,'lower':float(fit.fun),'upper':upper,'gap':gap,'cuts':len(cuts)})
        print(name,'iteration',iteration+1,'upper',upper,'gap',gap,flush=True)
        if gap<3e-4:break
    scenario={'objective':name,'lower_optimization_bound':float(fit.fun),'upper_loss_bound':upper,
              'optimization_gap':gap,'q':dict(zip(arms,q.tolist())),'expected_cost':float(q@costs),
              'iterations':receipt,'last_comparator_support_scales':dict(zip(policies,[x['dual_tau'] for x in calls[-len(comp):]]))}
    scenarios.append(scenario);print(name,'direct joint',upper,'lower',fit.fun,'gap',gap,flush=True)
report={'scope':'Approximate exchange-search receipt on the quota mixture region. Floating tangents, support cushions and witness feasibility are diagnostics, not formal numerical enclosures. The separately enclosed production verification certifies allocation upper bounds; this search does not certify minimax optimality. No sharpness or novelty claim.',
        'moment_method':args.moment_method,'moment_rows':moment_rows,'scenarios':scenarios,'total_cuts':len(cuts),'support_calls':calls,'seconds':time.time()-start}
destination='quota-search.json' if args.moment_method=='quota' else 'harmonic-allocation-search.json'
(r/'output'/destination).write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print('Seconds',report['seconds'])
