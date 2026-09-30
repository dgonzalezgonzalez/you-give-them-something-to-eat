"""Independent corner LPs and exact feasible-set geometry checks."""
from pathlib import Path
import itertools,json
import numpy as np
import pandas as pd
from scipy.optimize import linprog
from institutional_allocations import feasible_class,vertices,mean_box
from estimate import ARMS

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'

def independent(A_low,A_high,P,p,E,e,Q,costs,value=0.):
    inequalities=[];limits=[]
    for r,mu in itertools.product(Q,itertools.product(*zip(A_low,A_high))):
        mu=np.array(mu)
        inequalities.append(np.r_[-mu+value*costs,-1.])
        limits.append(-float(r@mu)+value*float(costs@r))
    inequalities.extend(np.c_[P,np.zeros(len(p))]);limits.extend(p)
    fit=linprog(np.r_[np.zeros(6),1.],A_ub=inequalities,b_ub=limits,
                A_eq=np.c_[E,np.zeros(len(e))],b_eq=e,bounds=[(0,None)]*7,method='highs')
    if not fit.success:raise AssertionError(fit.message)
    return float(fit.fun)

def main():
    checks=[]
    def check(name,condition):
        if not condition:raise AssertionError(name)
        checks.append(name)
    definitions=json.loads((OUT/'institutional-sensitivity-definition.json').read_text())
    costs=np.array([definitions['costs'][a] for a in ARMS]);budget=definitions['base_budget']
    base=json.loads((OUT/'policies.json').read_text())
    P,p,E,e=feasible_class(costs,budget);Q=vertices(P,p,E,e)
    expected=np.array([[q.get(a,0.) for a in ARMS] for q in [{'Gikuriro':1.},*base['vertices'].values()]])
    check('Generic active-set enumeration recovers all nine original vertices',
          len(Q)==len(expected)==9 and all(any(np.max(np.abs(q-r))<1e-8 for r in expected) for q in Q))
    Pb,pb,Eb,eb=feasible_class(costs,budget,binding=True);Qb=vertices(Pb,pb,Eb,eb)
    check('Binding-budget class has five expected budget-face vertices',
          len(Qb)==5 and np.allclose(Qb@costs,budget))
    Pg,pg,Eg,eg=feasible_class(costs,budget,GK_minimum=.25);Qg=vertices(Pg,pg,Eg,eg)
    translated=.75*Q;translated[:,1]+=.25
    check('Minimum-Gikuriro class is exact homothetic menu',
          len(Qg)==len(Q) and all(any(np.max(np.abs(q-r))<1e-8 for r in translated) for q in Qg))
    regions=pd.read_csv(OUT/'distribution_projected_regions.csv')
    rows=pd.read_csv(OUT/'institutional_allocation_sensitivity.csv');errors=[]
    for row in rows.itertuples():
        definition=definitions['classes'][row._asdict()['class'] if 'class' in row._asdict() else row[1]]
        P=np.array(definition['constraints_P']);p=np.array(definition['constraints_p'])
        E=np.array(definition['equalities_E']);e=np.array(definition['equalities_e']);Qi=np.array(definition['vertices'])
        _,_,lo,hi=mean_box(regions,row.method,row.objective)
        for label,comparator,target in [('own',Qi,row.certificate),('common',Q,row.optimized_loss_against_unrestricted_comparators)]:
            value=independent(lo,hi,P,p,E,e,comparator,costs);error=abs(value-target);errors.append(error)
            check('Independent corner LP '+str(row[1])+'/'+row.method+'/'+row.objective+'/'+label,error<1e-8)
        q=np.array([getattr(row,a+'_probability') for a in ARMS])
        qc=np.array([getattr(row,a+'_common_comparator_probability') for a in ARMS])
        check('Both institutional choices feasible '+str(row[1])+'/'+row.method+'/'+row.objective,
              max(np.max(P@q-p),np.max(P@qc-p),np.max(np.abs(E@q-e)),np.max(np.abs(E@qc-e)))<1e-8)
        check('Own-menu loss is no greater than common-menu loss '+str(row[1])+'/'+row.method+'/'+row.objective,
              row.certificate<=row.unrestricted_comparator_loss_of_class_optimum+1e-8 and
              row.optimized_loss_against_unrestricted_comparators<=row.unrestricted_comparator_loss_of_class_optimum+1e-8)
    for method,name in itertools.product(['finite_distribution','finite_consistency_distribution'],['mean','shortfall_6']):
        relevant=rows[(rows.method==method)&(rows.objective==name)].set_index('class')
        check('Homothetic regret scales mechanically '+method+'/'+name,
              abs(relevant.loc['at_least_25percent_Gikuriro'].certificate-.75*relevant.loc['expected_cost_ceiling'].certificate)<1e-8)
        check('Restricting choices cannot improve common-comparator optimum '+method+'/'+name,
              bool((relevant.optimized_loss_against_unrestricted_comparators>=relevant.loc['expected_cost_ceiling'].certificate-1e-8).all()))
    P,p,E,e=feasible_class(costs,budget);_,_,lo,hi=mean_box(regions,'finite_consistency_distribution','mean')
    resource=pd.read_csv(OUT/'unused_resource_sensitivity.csv')
    for row in resource.itertuples():
        value=independent(lo,hi,P,p,E,e,Q,costs,row.hypothetical_groups_per_unused_USD)
        error=abs(value-row.certificate_in_augmented_objective_units);errors.append(error)
        check('Independent resource-value corner LP '+str(row.hypothetical_groups_per_unused_USD),error<1e-8)
    settings=json.loads((OUT/'cost_inputs.json').read_text())
    scenarios=pd.read_csv(OUT/'distribution_cost_sensitivity.csv')
    check('All 32 aligned cost cases for both finite projections',len(scenarios)==64 and scenarios.scenario.nunique()==32)
    for row in scenarios.itertuples():
        setting=settings[row.scenario];cc=np.array([setting['costs'][a] for a in ARMS]);bb=setting['budget']
        P,p,E,e=feasible_class(cc,bb);Qi=vertices(P,p,E,e)
        _,_,lo,hi=mean_box(regions,row.method,'mean')
        value=independent(lo,hi,P,p,E,e,Qi,cc);error=abs(value-row.certificate);errors.append(error)
        check('Independent aligned cost corner LP '+row.scenario+'/'+row.method,error<1e-8)
    result={'scope':'Hypothetical feasible-set/resource-value implementation checks; no observed mandate, value estimation or new coverage guarantee.',
            'checks_passed':len(checks),'checks':checks,'maximum_independent_corner_lp_error':max(errors),
            'own_comparator_scaling_is_mechanical':True}
    (OUT/'institutional-validation.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print(f'Institutional sensitivities: {len(checks)}/{len(checks)} meaningful checks passed; independent maximum LP error {max(errors):.3g}.')

if __name__=='__main__':main()
