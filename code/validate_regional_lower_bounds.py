"""Exact dual replay plus independent 160-digit event membership checks."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal,localcontext
import itertools,json
import numpy as np
from quota_models import build_models,ARMS
from quota_allocation import exact_vertices
from regional_lower_bounds import finite_adversary_lower,enclosed_event

ROOT=Path(__file__).resolve().parents[1]
report=json.loads((ROOT/'output/regional-minimax-brackets.json').read_text())
bench=json.loads((ROOT/'output/quota-benchmarks.json').read_text())
policy=json.loads((ROOT/'output/policies.json').read_text())
cost=[F(policy['costs'][a]) for a in ARMS];budget=F(policy['budget']);labels,vertices=exact_vertices(cost,budget)
checks={};cache={};minimum_slack=Decimal(5520)
for receipt in report['receipts']:
    key=(receipt['method'],receipt['bin_floors'])
    if key not in cache:
        item=next(x for x in bench['receipts'] if (x['method'],x['bin_floors'])==key and x['event']=='shared')
        models,_=build_models(item['moments'])
        if not key[1]:models=[{**m,'floor':np.zeros(13)} for m in models]
        populations=[[[F(x) for x in point] for point in pop] for pop in receipt['exact_feasible_populations']]
        for index,population in enumerate(populations):
            name=str(key)+'_'+str(index)
            checks[name+'_unit_mass_and_floors']=all(sum(p)==1 and all(x>=F(float(f)) for x,f in zip(p,m['floor'])) for m,p in zip(models,population))
            checks[name+'_logical_rows']=all(sum(F(float(a))*x for a,x in zip(row,p))<=F(float(b)) for m,p in zip(models,population) for row,b in zip(m['A'],m['b']))
            checks[name+'_directed_event']=enclosed_event(models,population)<=5520
            with localcontext() as ctx:
                ctx.prec=160
                event=Decimal(0)
                for m,p in zip(models,population):
                    x=[Decimal(q.numerator)/Decimal(q.denominator) for q in p]
                    for row,constant in zip(m['C'],m['intercept']):
                        event+=(sum(Decimal.from_float(float(a))*value for a,value in zip(row,x))+Decimal.from_float(float(constant))).exp()
                checks[name+'_independent_160_digit_event']=event<=5520
                minimum_slack=min(minimum_slack,Decimal(5520)-event)
        cache[key]=(models,populations,item)
    models,populations,item=cache[key];score=[F(s) if receipt['objective']=='mean' else -F(max(6-s,0),6) for s in range(13)]
    means=[[sum(x*y for x,y in zip(p,score)) for p in pop] for pop in populations]
    dual=receipt['dual'];prob=[F(x) for x in dual['probabilities']];eta=F(dual['nonnegative_cost_multiplier']);sources=dual['source_indices']
    name=str(key)+'_'+receipt['objective']
    checks[name+'_exact_arm_means']=means==[[F(x) for x in row] for row in receipt['exact_arm_means']]
    checks[name+'_feasible_dual']=len(prob)==len(sources) and min(prob)>=0 and sum(prob)==1 and eta>=0 and all(0<=i<len(means) and 0<=j<len(vertices) for i,j in sources)
    v=[sum(w*means[i][j] for w,(i,k) in zip(prob,sources)) for j in range(6)]
    a=sum(w*sum(x*y for x,y in zip(vertices[k],means[i])) for w,(i,k) in zip(prob,sources))
    lower=max(F(0),a-eta*budget-max(value-eta*c for value,c in zip(v,cost)))
    checks[name+'_exact_dual_value']=lower==F(receipt['exact_lower'])
    scenario=next(x for x in item['scenarios'] if x['objective']==receipt['objective'])
    checks[name+'_same_source_upper']=F(scenario['conditional_loss_upper'])==F(receipt['exact_proposal_upper'])
    checks[name+'_optimization_bracket']=lower<=F(receipt['exact_proposal_upper'])

intervals=[(F(0),F(1,4)),(F(0),F(1,2)),(F(1,4),F(3,4)),(F(1,2),F(1)),(F(0),F(1)),(F(1,4),F(1,4))]
for index,(a,b) in enumerate(itertools.product(intervals,repeat=2)):
    means=[list(x) for x in itertools.product(a,b)]
    lower,dual=finite_adversary_lower(means,[[F(1),F(0)],[F(0),F(1)]],[F(1),F(1)],F(1))
    U=max(F(0),b[1]-a[0]);L=max(F(0),a[1]-b[0]);expected=U*L/(U+L) if U+L else F(0)
    checks[f'independent_two_arm_closed_form_{index}']=0<=expected-lower<=F(1,10**12)
for index,(c,budget) in enumerate([(2,1),(3,1),(3,2),(3,3)]):
    lower,dual=finite_adversary_lower([[F(0),F(1)]],[[F(1),F(0)],[F(1)-F(budget,c),F(budget,c)]],[F(0),F(c)],F(budget))
    # With a known single population, the decision can equal the best
    # feasible comparator. Loss is zero, not its loss against an infeasible
    # pure costly arm. The positive cost dual verifies the binding budget.
    checks[f'exact_binding_budget_{index}']=lower==0 and (budget==c or F(dual['nonnegative_cost_multiplier'])>0)
    lower,dual=finite_adversary_lower([[F(0),F(1)],[F(1),F(0)]],[[F(1),F(0)],[F(1)-F(budget,c),F(budget,c)]],[F(0),F(c)],F(budget))
    checks[f'budget_menu_symmetric_uncertainty_{index}']=0<=F(budget,2*c)-lower<=F(1,10**12)
result={'scope':'Regenerate all eight implemented field regions from unchanged microdata/method moments; exact rational unit-mass/floor/logical membership and directed plus independent 160-digit event tests for 19 adversarial populations per region. Independently replay exact policy dual probabilities/cost multipliers and bracket identities. Compare 36 two-arm rectangular cases and four binding-budget cases with analytic exact solutions. Checks concern implemented outer-region optimization, not sharp potential populations, all confidence methods or actual true regret.',
    'checks':checks,'all_passed':all(checks.values()),'minimum_160_digit_event_slack':str(minimum_slack)}
(ROOT/'output/regional-minimax-validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(sum(checks.values()),'/',len(checks),'regional minimax checks',flush=True)
if not result['all_passed']:raise ValueError([k for k,v in checks.items() if not v])
