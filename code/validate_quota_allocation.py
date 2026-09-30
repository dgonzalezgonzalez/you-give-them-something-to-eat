"""Replay numerical support certificates independently of their optimizer."""
from pathlib import Path
from fractions import Fraction
from decimal import Decimal,localcontext
import itertools,json
import numpy as np
from quota_arithmetic import I,D,tangent_support_upper
from quota_moments import quota_upper_log_moment
from quota_arithmetic import observed_residual_constants,outward_affine_tests

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'
report=json.loads((OUT/'quota-loss-bound.json').read_text());policies=json.loads((OUT/'policies.json').read_text());checks={};max_error=0.
checks['single_standalone_event']=report['event_terms']==276 and report['event_cap']==5520 and len(report['transformations'])==23
for scenario in report['scenarios']:
    name=scenario['objective'];unit=scenario['chosen_allocation_denominator'];q={a:Fraction(v,unit) for a,v in scenario['chosen_allocation_numerators'].items()}
    checks[name+'_exact_allocation']=sum(q.values())==1 and min(q.values())>=0
    checks[name+'_exact_budget']=sum(Fraction(policies['costs'][a])*v for a,v in q.items())<=Fraction(policies['budget'])
    checks[name+'_nine_vertices']=len(scenario['comparators'])==9
    for comp in scenario['comparators']:
        upper=I(comp['tau'])
        for arm,m in zip(comp['arms'],report['models']):
            C=np.array(m['C']);inter=np.array(m['intercept']);A=np.array(m['A']);b=np.array(m['b']);floor=np.array(m['bin_floors'])
            bound,receipt=tangent_support_upper(arm['direction'],arm['candidate'],C,inter,comp['tau'],5520,A,b,floor,arm['LP_dual']['nonpositive_multipliers'])
            error=abs(bound-arm['support_upper']);max_error=max(max_error,error)
            checks[name+'_'+comp['comparator']+'_'+arm['arm']+'_tangent_replay']=bound<=arm['support_upper']
            # Exact Fraction reduced costs check a dual witness from scratch.
            lam=[Fraction(v) for v in receipt['LP_dual']['nonpositive_multipliers']];zeta=Fraction(Decimal(receipt['LP_dual']['equality_multiplier']))
            g=[Fraction(x) for x in receipt['tangent_gradient']]
            reduced=[g[j]-sum(Fraction(float(A[i,j]))*v for i,v in enumerate(lam))-zeta for j in range(13)]
            checks[name+'_'+comp['comparator']+'_'+arm['arm']+'_exact_dual_feasibility']=all(v<=0 for v in lam) and min(reduced)>=0
            upper+=I(bound)
        upper+=I(Decimal(comp['direction_rounding_upper']))
        checks[name+'_'+comp['comparator']+'_support_sum']=upper.upper_float()<=comp['support_upper']
    checks[name+'_outer_maximum']=scenario['conditional_loss_upper']>=max(c['support_upper'] for c in scenario['comparators'])
    checks[name+'_outward_display']=Decimal(scenario['reported_conservative_loss_upper'])>=D(scenario['conditional_loss_upper'])

# Exact small two-arm/two-block quota design with arm-specific missing diet
# intervals. Independent 160-digit evaluation of true weighted distributions.
weights=[[1.,2.,1.,3.],[2.,1.,4.,1.]];diets=[[[1,3,11,2],[7,2,4,6]],[[6,8,2,1],[2,9,5,1]]]
zgrids=[np.arange(13)/12,(np.arange(13)>=6).astype(float),1-np.maximum(6-np.arange(13),0)/6]
lam=.25;B=sum((I(quota_upper_log_moment(w,2,lam)[0]) for w in weights),I(0)).upper_float()
subsets=list(itertools.combinations(range(4),2));totals=[Decimal(0)]*12;coverage=0;count=0;envelope_checks=0
with localcontext() as ctx:
    ctx.prec=160
    true_distributions=[]
    for a in range(2):
        mass=[Decimal(0)]*13
        for block in range(2):
            for j,w in enumerate(weights[block]):mass[diets[a][block][j]]+=D(w)
        true_distributions.append([x/Decimal(15) for x in mass])
    for ss1,ss2 in itertools.product(subsets,repeat=2):
        values=[]
        for a in range(2):
            selected=[]
            for block,ss in enumerate([ss1,ss2]):
                indices=ss if a==0 else tuple(j for j in range(4) if j not in ss)
                selected.extend((block,j) for j in indices)
            w=[weights[b][j] for b,j in selected];lo=[0 if (a+b+j)%3==0 else diets[a][b][j] for b,j in selected];hi=[12 if (a+b+j)%3==0 else diets[a][b][j] for b,j in selected]
            for z in zgrids:
                cc=observed_residual_constants(w,[4]*4,[2]*4,lo,hi,z);C,inter=outward_affine_tests(cc,z,lam,B)
                mean=sum(D(v)*p for v,p in zip(z,true_distributions[a]));residual=sum(2*D(weights[b][j])*(D(z[diets[a][b][j]])-mean) for b,j in selected)
                for sign,row,ii in zip([1,-1],C,inter):
                    loge=sum(D(v)*p for v,p in zip(row,true_distributions[a]))+D(ii)
                    if loge<=sign*D(lam)*residual-D(B):envelope_checks+=1
                    values.append(loge.exp())
        totals=[x+y for x,y in zip(totals,values)];coverage+=sum(values)<=240;count+=1
checks['exact_missing_interval_envelopes']=envelope_checks==36*12
checks['exact_e_expectations']=all(x/Decimal(count)<=1 for x in totals)
checks['exact_small_design_coverage']=Fraction(coverage,count)>=Fraction(95,100)
receipt={'scope':'Support certificates replayed without optimization; exact rational allocation/dual feasibility and outward displays; exhaustive 36-assignment fixed-population missing-diet event at 160-digit precision. A fixture coverage result does not prove nominal coverage for other populations or Rwanda.',
         'checks':{k:bool(v) for k,v in checks.items()},'all_passed':bool(all(checks.values())),'maximum_replay_error':max_error,'exact_design_assignments':count,
         'exact_design_e_expectations':[float(x/Decimal(count)) for x in totals],'exact_design_event_coverage':coverage/count}
(OUT/'quota-allocation-validation.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
print(sum(checks.values()),'/',len(checks),'quota allocation checks; max replay error',max_error,'exact small-design coverage',coverage/count)
if not receipt['all_passed']:raise AssertionError([k for k,v in checks.items() if not v])
