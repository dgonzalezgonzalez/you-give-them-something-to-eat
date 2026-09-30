"""Diversified allocations over confidence regions, including cost accounting.

Finite regions are conditional on explicit exchangeable assignment and fixed
weighted baseline observations. Block approximations failed stress diagnostics
and are retained only as sensitivity calculations. No statistical finite-sample
minimax-regret rule, donor preference, or transport invariance is claimed.
"""
from pathlib import Path
import itertools,json
import numpy as np
import pandas as pd
from scipy.optimize import linprog
from estimate import ARMS,policy_vertices

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'


def vector(policy):
    return np.array([policy.get(a,0.) for a in ARMS])


def region(objective,method,scope,base):
    """A mu <= b in six common arm means, rather than unrelated comparisons."""
    low,high=(0.,12.) if objective=='mean' else (-1.,0.)
    A=[];b=[]
    if method=='finite':
        source=pd.read_csv(OUT/'finite_arm_regions.csv')
        source=source[source.outcome==objective]
        if scope=='identified_diets':
            selected=source[source.scope==scope].set_index('arm')
            lower=selected.reindex(ARMS).finite_lower.to_numpy()
            upper=selected.reindex(ARMS).finite_upper.to_numpy()
        else:
            lower=source[source.scope=='lower_endpoint'].set_index('arm').reindex(ARMS).finite_lower.to_numpy()
            upper=source[source.scope=='upper_endpoint'].set_index('arm').reindex(ARMS).finite_upper.to_numpy()
        for ai,unit in enumerate(np.eye(6)):
            A.extend([unit,-unit]);b.extend([upper[ai],-lower[ai]])
    else:
        source=pd.read_csv(OUT/('policy_pairwise.csv' if scope=='identified_diets' else 'population_bounds.csv'))
        for row in source[source.outcome==objective].itertuples():
            c=vector(base[row.left])-vector(base[row.right])
            if scope=='identified_diets':
                A.extend([c,-c]);b.extend([row.sim_hi,-row.sim_lo])
            elif row.endpoint=='upper':A.append(c);b.append(row.sim_hi)
            else:A.append(-c);b.append(-row.sim_lo)
        for unit in np.eye(6):A.extend([unit,-unit]);b.extend([high,-low])
    A=np.array(A);b=np.array(b)
    feasible=linprog(np.zeros(6),A_ub=A,b_ub=b,bounds=[(None,None)]*6,method='highs')
    if not feasible.success:
        raise ValueError('Empty confidence region; no allocation certificate permitted')
    return A,b


def solve_allocation(A,b,comparators,costs,budget,*,fixed=None,GK_share=None):
    """Dual robust LP, independently checked against each primal adversary."""
    Q=np.array([vector(q) for q in comparators.values()]);m=len(b);n=len(Q)
    # Six chosen arm probabilities, certificate t, and n nonnegative dual vectors.
    size=7+n*m;equations=np.zeros((1+6*n,size));rhs=np.zeros(1+6*n)
    equations[0,:6]=1.;rhs[0]=1.;inequalities=np.zeros((1+n,size))
    inequalities[0,:6]=[costs[a] for a in ARMS];limit=np.r_[budget,np.zeros(n)]
    for j in range(n):
        dual=slice(7+j*m,7+(j+1)*m);rows=slice(1+6*j,1+6*(j+1))
        equations[rows,:6]=np.eye(6);equations[rows,dual]=A.T;rhs[rows]=Q[j]
        inequalities[1+j,6]=-1.;inequalities[1+j,dual]=b
    objective=np.zeros(size);objective[6]=1.;bounds=[(0,None)]*size
    if fixed is not None:
        for ai,v in enumerate(vector(fixed)):bounds[ai]=(v,v)
    if GK_share is not None:bounds[ARMS.index('Gikuriro')]=(GK_share,GK_share)
    solution=linprog(objective,A_ub=inequalities,b_ub=limit,A_eq=equations,b_eq=rhs,bounds=bounds,method='highs')
    if not solution.success:raise ValueError(solution.message)
    q=solution.x[:6];adversaries=[]
    for comparator in Q:
        primal=linprog(-(comparator-q),A_ub=A,b_ub=b,bounds=[(None,None)]*6,method='highs')
        if not primal.success:raise ValueError(primal.message)
        adversaries.append(-primal.fun)
    gap=abs(max(0.,max(adversaries))-solution.fun)
    residual=float(np.max(np.abs(equations@solution.x-rhs)))
    assert gap<1e-8 and residual<1e-8
    assert np.min(q)>=-1e-10 and abs(q.sum()-1)<1e-9
    expense=float(q@np.array([costs[a] for a in ARMS]))
    assert expense<=budget+1e-8
    return {'certificate':float(solution.fun),'probabilities':dict(zip(ARMS,q.tolist())),
            'expected_cost':expense,'primal_dual_gap':gap,'equality_residual':residual}


def fitted_arm(objective):
    cdf=pd.read_csv(OUT/'coherent_distributions.csv')
    result=[]
    for a in ARMS:
        values=cdf[cdf.arm==a].sort_values('threshold').cdf.to_numpy()
        result.append(12-values[:-1].sum() if objective=='mean' else -values[:6].sum()/6)
    return np.array(result)


def main():
    p=json.loads((OUT/'policies.json').read_text());costs=p['costs'];budget=p['budget']
    base={'Gikuriro':{'Gikuriro':1.},**p['vertices']}
    certificates=[];receipts=[];frontier=[];scenarios=[]
    for objective,method,scope in itertools.product(['mean','shortfall_6'],['finite','block_approximation'],['identified_diets','weighted_baseline']):
        A,b=region(objective,method,scope,base)
        solved=solve_allocation(A,b,base,costs,budget)
        fixed={name:solve_allocation(A,b,base,costs,budget,fixed=q)['certificate'] for name,q in base.items()}
        mu=fitted_arm(objective);values={name:float(vector(q)@mu) for name,q in base.items()};best=max(values,key=values.get)
        record={'objective':objective,'method':method,'scope':scope,
                'optimized_certificate':solved['certificate'],'best_vertex_certificate':min(fixed.values()),
                'fitted_best_vertex':best,'fitted_best_vertex_certificate':fixed[best],
                'GK_certificate':fixed['Gikuriro'],'expected_cost':solved['expected_cost'],
                **{a+'_probability':v for a,v in solved['probabilities'].items()}}
        certificates.append(record);receipts.append({**record,'primal_dual_gap':solved['primal_dual_gap'],
                                                     'equality_residual':solved['equality_residual']})
        if objective=='mean' and scope=='weighted_baseline':
            for share in np.linspace(0,1,21):
                result=solve_allocation(A,b,base,costs,budget,GK_share=float(share))
                frontier.append({'method':method,'GK_share':share,'certificate':result['certificate'],
                                 **{a+'_probability':v for a,v in result['probabilities'].items()}})
            settings=json.loads((OUT/'cost_inputs.json').read_text())
            for label,setting in settings.items():
                cc=setting['costs'];bb=setting['budget'];qq={'Gikuriro':{'Gikuriro':1.},**policy_vertices(cc,bb)}
                result=solve_allocation(A,b,qq,cc,bb)
                point_values={name:float(vector(q)@mu) for name,q in qq.items()};point_best=max(point_values,key=point_values.get)
                scenarios.append({'scenario':label,'method':method,'budget':bb,
                                  'optimized_certificate':result['certificate'],
                                  'fitted_observed_best':point_best,'fitted_observed_value':point_values[point_best],
                                  'upper_cash_pure_feasible':cc['Upper']<=bb,
                                  'upper_cash_margin':bb-cc['Upper'],'expected_cost':result['expected_cost'],
                                  **{a+'_probability':v for a,v in result['probabilities'].items()}})
    pd.DataFrame(certificates).to_csv(OUT/'allocation_certificates.csv',index=False)
    pd.DataFrame(frontier).to_csv(OUT/'allocation_frontier.csv',index=False)
    pd.DataFrame(scenarios).to_csv(OUT/'allocation_cost_sensitivity.csv',index=False)
    report={'scope':'Optimization over finite conditional-assignment outer regions or explicitly unvalidated block approximations; expected standardized unit costs and stable original delivery assumed.',
            'main_certificates':receipts,'cost_scenarios_per_method':len(settings),
            'max_main_primal_dual_gap':max(x['primal_dual_gap'] for x in receipts),
            'not_a_statistical_minimax_regret_rule':True,'full_frame_representativeness_proven':False}
    (OUT/'allocation-validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print(pd.DataFrame(certificates)[['objective','method','scope','optimized_certificate','best_vertex_certificate']].to_string(index=False))
    print('Diversification, 42 share-frontier points and 64 aligned cost scenarios computed; primal adversaries agree.')

if __name__=='__main__':main()
