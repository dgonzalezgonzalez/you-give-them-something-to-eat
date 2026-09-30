"""Explicit hypothetical institutional constraints and unused-resource values.

No CRS donor mandate, mixed-rollout marginal costs or opportunity value is
observed. These are normative sensitivities to the published benchmark menu.
Own-menu calculations impose the same class on choice and comparator.
Common-menu calculations restrict choice while retaining the original comparator.
"""
from pathlib import Path
import itertools,json
import numpy as np
import pandas as pd
from scipy.optimize import linprog
from estimate import ARMS
from policy_allocation import fitted_arm

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'

def feasible_class(costs,budget,*,assistance=0.,GK_minimum=0.,binding=False):
    P=[*-np.eye(6),costs];p=[*np.zeros(6),budget]
    if assistance:
        unit=np.zeros(6);unit[0]=1.;P.append(unit);p.append(1-assistance)
    if GK_minimum:
        unit=np.zeros(6);unit[1]=-1.;P.append(unit);p.append(-GK_minimum)
    E=[np.ones(6)];e=[1.]
    if binding:E.append(costs);e.append(budget)
    return np.array(P),np.array(p),np.array(E),np.array(e)

def vertices(P,p,E,e):
    """Enumerate all independent active-constraint intersections in six arms."""
    dimension=6-np.linalg.matrix_rank(E);result=[]
    for active in itertools.combinations(range(len(p)),dimension):
        matrix=np.r_[E,P[list(active)]];rhs=np.r_[e,p[list(active)]]
        if np.linalg.matrix_rank(matrix)<6:continue
        q=np.linalg.solve(matrix,rhs)
        if np.max(P@q-p)>1e-8 or np.max(np.abs(E@q-e))>1e-8:continue
        q[np.abs(q)<1e-12]=0.
        if not any(np.max(np.abs(q-old))<1e-8 for old in result):result.append(q)
    if not result:raise ValueError('Empty feasible institutional class')
    return np.array(result)

def solve(A,b,P,p,E,e,Q,costs,*,resource_value=0.):
    """Robust dual LP with optional common linear value of unspent resources."""
    m=len(b);n=len(Q);size=7+n*m
    eq=np.zeros((len(e)+6*n,size));rhs=np.r_[e,np.zeros(6*n)]
    eq[:len(e),:6]=E
    ub=np.zeros((len(p)+n,size));limit=np.r_[p,np.zeros(n)]
    ub[:len(p),:6]=P
    for j,r in enumerate(Q):
        dual=slice(7+j*m,7+(j+1)*m);rows=slice(len(e)+6*j,len(e)+6*(j+1))
        eq[rows,:6]=np.eye(6);eq[rows,dual]=A.T;rhs[rows]=r
        ub[len(p)+j,:6]=resource_value*costs
        ub[len(p)+j,6]=-1.;ub[len(p)+j,dual]=b
        limit[len(p)+j]=resource_value*float(costs@r)
    objective=np.zeros(size);objective[6]=1.
    fit=linprog(objective,A_ub=ub,b_ub=limit,A_eq=eq,b_eq=rhs,bounds=[(0,None)]*size,method='highs')
    if not fit.success:raise ValueError(fit.message)
    q=fit.x[:6];adversaries=[]
    for r in Q:
        primal=linprog(-(r-q),A_ub=A,b_ub=b,bounds=[(None,None)]*6,method='highs')
        if not primal.success:raise ValueError(primal.message)
        adversaries.append(-float(primal.fun)+resource_value*float(costs@(q-r)))
    gap=abs(max(0.,max(adversaries))-float(fit.fun))
    if gap>1e-8:raise AssertionError('Institutional primal/dual disagreement')
    return {'certificate':float(fit.fun),'q':q,'expected_cost':float(costs@q),'primal_dual_gap':gap}


def worst_loss(q,A,b,Q):
    """Evaluate a fixed allocation against a separately specified common menu."""
    values=[]
    for r in Q:
        fit=linprog(-(r-q),A_ub=A,b_ub=b,bounds=[(None,None)]*6,method='highs')
        if not fit.success:raise ValueError(fit.message)
        values.append(-float(fit.fun))
    return max(0.,max(values))

def mean_box(regions,method,name):
    sub=regions[(regions.method==method)&(regions.scope=='weighted_baseline')&(regions.outcome==name)].set_index('arm').reindex(ARMS)
    A=[];b=[]
    for unit,row in zip(np.eye(6),sub.itertuples()):A.extend([unit,-unit]);b.extend([row.projected_upper,-row.projected_lower])
    return np.array(A),np.array(b),sub.projected_lower.to_numpy(),sub.projected_upper.to_numpy()

def main():
    source=json.loads((OUT/'policies.json').read_text());costs=np.array([source['costs'][a] for a in ARMS]);budget=source['budget']
    regions=pd.read_csv(OUT/'distribution_projected_regions.csv')
    classes={'expected_cost_ceiling':{},'at_least_75percent_assisted':{'assistance':.75},
             'universal_assistance':{'assistance':1.},'binding_expected_spending':{'binding':True},
             'universal_assistance_binding_spending':{'assistance':1.,'binding':True},
             'at_least_25percent_Gikuriro':{'GK_minimum':.25}}
    referenceP,referencep,referenceE,referencee=feasible_class(costs,budget)
    referenceQ=vertices(referenceP,referencep,referenceE,referencee)
    rows=[];definition={};errors=[]
    for label,setting in classes.items():
        P,p,E,e=feasible_class(costs,budget,**setting);Q=vertices(P,p,E,e)
        definition[label]={'settings':setting,'vertices':Q.tolist(),'constraints_P':P.tolist(),
                           'constraints_p':p.tolist(),'equalities_E':E.tolist(),'equalities_e':e.tolist()}
        for method,name in itertools.product(['finite_distribution','finite_consistency_distribution'],['mean','shortfall_6']):
            A,b,_,_=mean_box(regions,method,name);result=solve(A,b,P,p,E,e,Q,costs)
            errors.append(result['primal_dual_gap'])
            common=solve(A,b,P,p,E,e,referenceQ,costs);errors.append(common['primal_dual_gap'])
            rows.append({'class':label,'method':method,'objective':name,'comparator_vertices':len(Q),
                         'certificate':result['certificate'],'expected_cost':result['expected_cost'],
                         'unused_expected_budget':budget-result['expected_cost'],
                         'unrestricted_comparator_loss_of_class_optimum':worst_loss(result['q'],A,b,referenceQ),
                         'optimized_loss_against_unrestricted_comparators':common['certificate'],
                         'common_comparator_optimum_expected_cost':common['expected_cost'],
                         **{a+'_common_comparator_probability':q for a,q in zip(ARMS,common['q'])},
                         **{a+'_probability':q for a,q in zip(ARMS,result['q'])}})
    pd.DataFrame(rows).to_csv(OUT/'institutional_allocation_sensitivity.csv',index=False)
    P,p,E,e=feasible_class(costs,budget);Q=vertices(P,p,E,e);resource=[]
    A,b,_,_=mean_box(regions,'finite_consistency_distribution','mean')
    for value in [0.,.001,.005,.01,.02,.05]:
        result=solve(A,b,P,p,E,e,Q,costs,resource_value=value);errors.append(result['primal_dual_gap'])
        resource.append({'hypothetical_groups_per_unused_USD':value,'certificate_in_augmented_objective_units':result['certificate'],
                         'expected_cost':result['expected_cost'],'unused_expected_budget':budget-result['expected_cost'],
                         **{a+'_probability':q for a,q in zip(ARMS,result['q'])}})
    pd.DataFrame(resource).to_csv(OUT/'unused_resource_sensitivity.csv',index=False)
    scenarios=[];point_mean=fitted_arm('mean')
    settings=json.loads((OUT/'cost_inputs.json').read_text())
    for label,setting in settings.items():
        cc=np.array([setting['costs'][a] for a in ARMS]);bb=setting['budget']
        P,p,E,e=feasible_class(cc,bb);Q=vertices(P,p,E,e)
        fitted=float(np.max(Q@point_mean))
        for method in ['finite_distribution','finite_consistency_distribution']:
            A,b,_,_=mean_box(regions,method,'mean');result=solve(A,b,P,p,E,e,Q,cc)
            errors.append(result['primal_dual_gap'])
            scenarios.append({'scenario':label,'method':method,'budget':bb,'certificate':result['certificate'],
                              'expected_cost':result['expected_cost'],'comparator_vertices':len(Q),
                              'fitted_observed_value':fitted,'upper_cash_margin':bb-cc[4],
                              **{a+'_probability':q for a,q in zip(ARMS,result['q'])}})
    pd.DataFrame(scenarios).to_csv(OUT/'distribution_cost_sensitivity.csv',index=False)
    (OUT/'institutional-sensitivity-definition.json').write_text(json.dumps({
        'scope':'Hypothetical normative restrictions and unspent-resource values, not observed institutional mandates, welfare calibration or operational cost validation. Stable delivery and published average-cost assumptions remain. Own-class certificates change the comparator menu and cannot establish that restrictions improve outcomes; common unrestricted-comparator columns isolate the allocation constraint.',
        'classes':definition,'base_budget':budget,'costs':source['costs'],
        'maximum_primal_dual_gap':max(errors),'resource_values_are_not_estimated':True,
        'cost_scenarios_per_method':len(settings),'cost_scenarios_hold_outcomes_fixed':True},indent=2),encoding='utf8')
    print(pd.DataFrame(rows)[['class','method','objective','certificate','expected_cost']].to_string(index=False))
    print(pd.DataFrame(resource)[['hypothetical_groups_per_unused_USD','expected_cost']].to_string(index=False))

if __name__=='__main__':main()
