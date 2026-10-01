"""Retrospective population-objective pilot with two reported cost conventions.

Separate from default canonical science and the main finite confidence event.
These source average costs do not identify marginal mixed-rollout costs.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'code'))
from estimate import ARMS,policy_vertices

def frontier(policies,means):
    intercept={k:sum(v*means[0][ARMS.index(a)] for a,v in q.items()) for k,q in policies.items()}
    slope={k:sum(v*(means[1][ARMS.index(a)]-means[0][ARMS.index(a)]) for a,v in q.items()) for k,q in policies.items()}
    roots={0.,1.}
    for a in policies:
        for b in policies:
            if abs(slope[a]-slope[b])>1e-12:
                theta=(intercept[b]-intercept[a])/(slope[a]-slope[b])
                if 0<theta<1:roots.add(theta)
    roots=sorted(roots);segments=[]
    for left,right in zip(roots[:-1],roots[1:]):
        theta=(left+right)/2;best=max(policies,key=lambda k:intercept[k]+theta*slope[k])
        if segments and segments[-1]['policy']==best:segments[-1]['theta_upper']=right
        else:segments.append({'theta_lower':left,'theta_upper':right,'policy':best})
    return segments,intercept,slope

def main():
    destination=ROOT/'docs/exploration'
    pilot=json.loads((destination/'community-diet-pilot.json').read_text())
    means={g:np.array([next(t['mean'] for t in pilot['arm_means'] if t['eligible']==g and t['scope']=='identified' and t['arm']==a) for a in ARMS]) for g in [0,1]}
    tau=pilot['weight_diagnostics'][1]['population_share_from_baseline_weights']
    raw=pd.read_csv(ROOT/'data/input/costs.csv').set_index('treatment');aliases={'Gikuriro':'Gikuriro','Lower':'GD_Lower','Middle':'GD_Mid','Upper':'GD_Upper','Large':'GD_Large'}
    rows=[];diagnostics=[]
    for column in ['cost_eligible','cost_population']:
        costs={'Control':0.,**{a:float(raw.loc[k,column]) for a,k in aliases.items()}}
        budget=costs['Gikuriro'];policies={'Gikuriro':{'Gikuriro':1.},**policy_vertices(costs,budget)}
        for label,q in policies.items():
            expenditure=sum(q[a]*costs[a] for a in q)
            if abs(sum(q.values())-1)>1e-12 or min(q.values())<0 or expenditure>budget+1e-9:raise ValueError('Pilot policy feasibility failure')
            rows.append({'cost_column':column,'policy':label,'budget':budget,'expected_cost':expenditure,'eligible_mean':sum(q[a]*means[1][ARMS.index(a)] for a in q),'ineligible_mean':sum(q[a]*means[0][ARMS.index(a)] for a in q),'baseline_weight_aggregate_mean':sum(q[a]*(tau*means[1][ARMS.index(a)]+(1-tau)*means[0][ARMS.index(a)]) for a in q),'shares':q})
        segments,intercept,slope=frontier(policies,means)
        diagnostics.append({'cost_column':column,'budget':budget,'fitted_frontier':segments,'baseline_weight_fitted_best':max(policies,key=lambda k:intercept[k]+tau*slope[k]),'lower_large_cash_share':policies['Lower+Large']['Large']})
    output={'scope':'Exploratory fitted identified-diet benchmark. Recomputes the menu under each published source average-cost column. cost_population is not inferred by scaling cost_eligible by released baseline eligible share. Neither convention establishes marginal rollout costs, real institutional preferences, exact expenditure caps or full-target causal ranking. No uncertainty interval for frontier switches is asserted.','baseline_eligible_expansion_weight_share':tau,'scaled_original_eligible_budget':float(raw.loc['Gikuriro','cost_eligible'])*tau,'reported_source_population_budget':float(raw.loc['Gikuriro','cost_population']),'menus':diagnostics,'policy_rows':rows}
    (destination/'community-cost-frontier.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:v for k,v in output.items() if k!='policy_rows'},indent=2))

if __name__=='__main__':main()
