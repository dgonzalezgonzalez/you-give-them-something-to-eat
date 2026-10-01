"""Population choice under separate conditional assignment events.

Baseline eligibility is not receipt. Fitted and asymptotic results are separate
from the finite event; reported average costs do not identify mixed-rollout cost.
The 36 fixed primitives protect every policy and every stipulated welfare weight.
"""
from pathlib import Path
from fractions import Fraction
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
import hashlib, itertools, json, sys
import numpy as np
import pandas as pd
from scipy.optimize import linprog
from scipy.stats import t as student_t
from estimate import ARMS, TX, regress, contrast, holm
from referee_revision import GROUPS, score_interval
from blocked_inference import hajek_block
from quota_arithmetic import I, calc
from weighted_product_moments import ilog
from quota_allocation import exact_vertices
from quota_moments import quota_upper_log_moment_dp

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'
FAMILY=36
ALPHA=Fraction(1,20)
UNIT=10**12

def fraction_interval(x):
    return I(x.numerator)/I(x.denominator)

def sqrt_interval(x):
    if x.lo<0:raise ValueError('Nonnegative square root required')
    return I(calc(ROUND_FLOOR,lambda:x.lo.sqrt().next_minus()),calc(ROUND_CEILING,lambda:x.hi.sqrt().next_plus()))

def load_population():
    references={}
    for name in ['input-reference.json','revision-reference.json']:
        references.update(json.loads((ROOT/'data/input'/name).read_text())['files'])
    verified={}
    for name in ['households.csv','revision_households.csv','costs.csv']:
        digest=hashlib.sha256((ROOT/'data/input'/name).read_bytes()).hexdigest()
        if digest!=references[name]:raise ValueError('Immutable population input mismatch: '+name)
        verified[name]=digest
    d=pd.read_csv(ROOT/'data/input/households.csv')
    aux=pd.read_csv(ROOT/'data/input/revision_households.csv')
    d=d.merge(aux[['hhid','round','nEligible','nIneligible']],on=['hhid','round'],validate='one_to_one')
    d['arm']='Control'
    for a,t in zip(ARMS[1:],TX):d.loc[d[t].eq(1),'arm']=a
    baseline=d[d['round'].eq(1)].copy()
    foods=['m9_'+name for group in GROUPS for name in group]
    endline=d[d['round'].eq(2)][['hhid','sample_panel',*foods]].rename(columns={'sample_panel':'endline_panel'})
    full=baseline.drop(columns=foods).merge(endline,on='hhid',how='left',validate='one_to_one')
    if len(full)!=len(baseline) or full.hhid.duplicated().any():raise ValueError('Baseline membership changed')
    lower,upper=score_interval(full);point=(lower+upper)/2;point[lower!=upper]=np.nan
    villages=baseline.drop_duplicates('vid')
    if baseline.groupby('vid')[TX].nunique().max().max()!=1:raise ValueError('Assignment not village constant')
    counts=pd.crosstab(villages.block,villages.arm).reindex(columns=ARMS)
    if counts.isna().any().any() or (counts<=0).any().any():raise ValueError('Positive quota for each arm/block required')
    probabilities=counts.div(counts.sum(axis=1),axis=0)
    assignment={a:probabilities[a].to_dict() for a in ARMS}
    return full,lower,upper,point,counts,assignment,verified

def exact_weight_sum(values):
    return sum((Fraction(float(w)) for w in values),Fraction(0))

def finite_primitives(full,lower,upper,point,counts):
    """Directed Hoeffding inversion of fixed potential observation ratios.

    For each block, sampling without replacement is bounded by with-replacement
    draws of village residuals of width 12*Wmax. No order or observation-MAR
    assumption enters. Conditional uniform quotas and independent blocks enter.
    """
    rows=[];boxes={};weights={};diagnostics=[]
    threshold_log=ilog(fraction_interval(Fraction(2*FAMILY)/ALPHA))
    for g in [0,1]:
        keep=full.eligible.eq(g).to_numpy();sample=full[keep].copy()
        population_weight=exact_weight_sum(sample.samp_wgt);weights[g]=population_weight
        village={}
        for (block,vid),v in sample.groupby(['block','vid']):village.setdefault(block,{})[vid]=exact_weight_sum(v.samp_wgt)
        frame='nEligible' if g else 'nIneligible'
        expected=sample[frame]/sample.groupby('vid').hhid.transform('count')
        if expected.isna().any() or (sample.samp_wgt<=0).any():raise ValueError('Invalid fixed frame weights')
        diagnostics.append({'eligible':g,'baseline_households':len(sample),'identified_diets':int(np.isfinite(point[keep]).sum()),'baseline_weight_sum_exact':str(population_weight),'max_abs_source_frame_discrepancy':float(abs(sample.samp_wgt-expected).max())})
        for a in ARMS:
            proxy=Fraction(0);blocks=[]
            for block,w in village.items():
                n=int(counts.loc[block].sum());k=int(counts.loc[block,a])
                if len(w)!=n:raise ValueError('Each stratum must cover every baseline village')
                maximum=max(w.values());proxy+=Fraction(n*n,k)*maximum*maximum
                blocks.append({'block':int(block),'n':n,'k':k,'maximum_village_weight_exact':str(maximum)})
            threshold=I(12)*sqrt_interval(fraction_interval(proxy)/I(2)*threshold_log)
            arm=sample.arm.eq(a).to_numpy()
            for scope,values in [('identified_diets',point[keep]),('lower_endpoint',lower[keep]),('upper_endpoint',upper[keep])]:
                selected=arm&np.isfinite(values);numerator=Fraction(0);denominator=Fraction(0)
                for w,y,block in zip(sample.loc[selected,'samp_wgt'],values[selected],sample.loc[selected,'block']):
                    factor=Fraction(float(w))*Fraction(int(counts.loc[block].sum()),int(counts.loc[block,a]))
                    numerator+=factor*Fraction(float(y));denominator+=factor
                if denominator<=0:
                    flo,fhi=0.,12.;center=None
                else:
                    center=float(numerator/denominator)
                    flo=max(0.,((fraction_interval(numerator)-threshold)/fraction_interval(denominator)).lower_float())
                    fhi=min(12.,((fraction_interval(numerator)+threshold)/fraction_interval(denominator)).upper_float())
                rows.append({'eligible':g,'arm':a,'scope':scope,'estimate':center,'finite_lower':flo,'finite_upper':fhi,'exact_observed_numerator':str(numerator),'exact_observed_denominator':str(denominator),'exact_range_proxy':str(proxy),'threshold_lower':str(threshold.lo),'threshold_upper':str(threshold.hi),'family_size':FAMILY,'conditional_failure_probability':str(ALPHA),'blocks':blocks})
            # Factual potential-diet information is deterministic; no extra event.
            exact_lo=sum((Fraction(float(w))*int(y) for w,y in zip(sample.loc[arm,'samp_wgt'],lower[keep][arm])),Fraction(0))
            assigned_weight=exact_weight_sum(sample.loc[arm,'samp_wgt'])
            exact_hi=sum((Fraction(float(w))*int(y) for w,y in zip(sample.loc[arm,'samp_wgt'],upper[keep][arm])),Fraction(0))+12*(population_weight-assigned_weight)
            logical_lo=max(0.,fraction_interval(exact_lo/population_weight).lower_float())
            logical_hi=min(12.,fraction_interval(exact_hi/population_weight).upper_float())
            mean_lo=max(logical_lo,next(z['finite_lower'] for z in rows if z['eligible']==g and z['arm']==a and z['scope']=='lower_endpoint'))
            mean_hi=min(logical_hi,next(z['finite_upper'] for z in rows if z['eligible']==g and z['arm']==a and z['scope']=='upper_endpoint'))
            if mean_lo>mean_hi:raise ValueError('Empty finite/logical population region')
            boxes[g,a]={'lower':mean_lo,'upper':mean_hi,'logical_lower':logical_lo,'logical_upper':logical_hi,'exact_logical_lower':str(exact_lo/population_weight),'exact_logical_upper':str(exact_hi/population_weight)}
    return rows,boxes,weights,diagnostics

def quota_mean_boxes(full,lower,upper,counts,logical_boxes):
    """A second standalone event: 24 one-sided endpoint tests, cap 480.

    Sorted-threshold moments are existing attributed machinery. Every scale is
    baseline-only, and this event is never intersected with the 36-primitive
    classical event or selected by whichever realized certificate is smaller.
    """
    cap=Fraction(24)/ALPHA;logcap=ilog(fraction_interval(cap));cache={};rows=[];boxes={}
    for g in [0,1]:
        keep=full.eligible.eq(g).to_numpy();sample=full[keep];village={}
        for (block,vid),v in sample.groupby(['block','vid']):village.setdefault(block,[]).append(exact_weight_sum(v.samp_wgt))
        decimal_weights={}
        with localcontext() as ctx:
            ctx.prec=120
            for block,w in village.items():
                converted=[Decimal(x.numerator)/Decimal(x.denominator) for x in w]
                if any(Fraction(d)!=f for d,f in zip(converted,w)):raise ValueError('Baseline Decimal weight not exact')
                decimal_weights[block]=converted
        for a in ARMS:
            proxy=sum((Fraction(int(counts.loc[b].sum())**2,int(counts.loc[b,a]))*max(w)**2 for b,w in village.items()),Fraction(0))
            base=float(np.sqrt(8*np.log(float(cap))/float(proxy)));candidates=[]
            for multiplier in [1.,1.25,1.5,2.]:
                lam=float(base*multiplier);B=I(0);block_rows=[]
                for block,w in decimal_weights.items():
                    k=int(counts.loc[block,a]);key=(g,int(block),k,lam)
                    if key not in cache:cache[key]=quota_upper_log_moment_dp(w,k,lam)
                    bound,detail=cache[key];B+=I(bound)
                    block_rows.append({'block':int(block),'n':len(w),'k':k,'certified_upper_log_moment':bound})
                upper_B=B.upper_float()
                threshold=I(12)*(I(upper_B)+logcap)/I(lam)
                candidates.append({'scale_multiplier':multiplier,'fixed_lambda_normalized':lam,'log_normalizer_upper':upper_B,'threshold_lower':str(threshold.lo),'threshold_upper':str(threshold.hi),'baseline_selection_metric':float(threshold.hi),'blocks':block_rows})
            chosen=min(candidates,key=lambda z:z['baseline_selection_metric'])
            lam=chosen['fixed_lambda_normalized'];threshold=I(12)*(I(chosen['log_normalizer_upper'])+logcap)/I(lam)
            arm=sample.arm.eq(a).to_numpy();denominator=Fraction(0);Nlo=Fraction(0);Nhi=Fraction(0)
            for w,l,h,block in zip(sample.loc[arm,'samp_wgt'],lower[keep][arm],upper[keep][arm],sample.loc[arm,'block']):
                factor=Fraction(float(w))*Fraction(int(counts.loc[block].sum()),int(counts.loc[block,a]));denominator+=factor;Nlo+=factor*int(l);Nhi+=factor*int(h)
            if denominator<=0:raise ValueError('Positive quota endpoint denominator required')
            raw_lower=max(0.,((fraction_interval(Nlo)-threshold)/fraction_interval(denominator)).lower_float())
            raw_upper=min(12.,((fraction_interval(Nhi)+threshold)/fraction_interval(denominator)).upper_float())
            lower_bound=max(raw_lower,logical_boxes[g,a]['logical_lower']);upper_bound=min(raw_upper,logical_boxes[g,a]['logical_upper'])
            if lower_bound>upper_bound:raise ValueError('Empty quota mean-only population region')
            boxes[g,a]={'lower':lower_bound,'upper':upper_bound,'logical_lower':logical_boxes[g,a]['logical_lower'],'logical_upper':logical_boxes[g,a]['logical_upper']}
            rows.append({'eligible':g,'arm':a,'one_sided_test_family':24,'test_cap':str(cap),'exact_observed_denominator':str(denominator),'exact_lower_numerator':str(Nlo),'exact_upper_numerator':str(Nhi),'quota_lower_before_logical':raw_lower,'quota_upper_before_logical':raw_upper,'chosen':chosen,'baseline_grid':candidates})
    return rows,boxes

def estimates(full,lower,upper,point,assignment):
    rows=[];mus={};influences={}
    for g in [0,1]:
        keep=full.eligible.eq(g).to_numpy();sample=full[keep]
        for scope,y in [('identified_diets',point),('lower_endpoint',lower),('upper_endpoint',upper)]:
            mu,influence,info=hajek_block(sample,y[keep],assignment,ARMS)
            mus[g,scope]=mu;influences[g,scope]=influence
            for i,a in enumerate(ARMS):rows.append({'eligible':g,'scope':scope,'arm':a,'estimate':float(mu[i]),'block_se':float(np.linalg.norm(influence[:,i]))})
    # This entire family is an asymptotic sensitivity, never the finite event.
    critical=float(student_t.ppf(1-float(ALPHA)/(2*FAMILY),len(full.block.unique())-1))
    for z in rows:
        z['asymptotic_bonferroni_lower']=max(0.,z['estimate']-critical*z['block_se'])
        z['asymptotic_bonferroni_upper']=min(12.,z['estimate']+critical*z['block_se'])
        z['asymptotic_critical']=critical
    return rows,mus,influences

def menus():
    d=pd.read_csv(ROOT/'data/input/costs.csv',dtype=str).set_index('treatment')
    aliases={'Gikuriro':'Gikuriro','Lower':'GD_Lower','Middle':'GD_Mid','Upper':'GD_Upper','Large':'GD_Large'}
    out={}
    for column in ['cost_eligible','cost_population']:
        cost=[Fraction(0) if a=='Control' else Fraction(d.loc[aliases[a],column]) for a in ARMS]
        labels,vertices=exact_vertices(cost,cost[1])
        out[column]={'costs':cost,'budget':cost[1],'labels':labels,'vertices':vertices}
    return out

def fitted_frontier(means,vertices,labels):
    """Point ranking only; exact arithmetic on the stored fitted floats.

    Theta is a total eligible welfare share. It is not a receipt rate, estimated
    institutional preference, or identified full-baseline causal ranking.
    """
    intercept=[sum((r[a]*Fraction(float(means[0][a])) for a in range(len(r))),Fraction(0)) for r in vertices]
    slope=[sum((r[a]*(Fraction(float(means[1][a]))-Fraction(float(means[0][a]))) for a in range(len(r))),Fraction(0)) for r in vertices]
    roots={Fraction(0),Fraction(1)}
    for a in range(len(vertices)):
        for b in range(a):
            if slope[a]!=slope[b]:
                root=(intercept[b]-intercept[a])/(slope[a]-slope[b])
                if 0<root<1:roots.add(root)
    roots=sorted(roots);segments=[]
    for left,right in zip(roots[:-1],roots[1:]):
        midpoint=(left+right)/2;best=max(range(len(vertices)),key=lambda a:intercept[a]+midpoint*slope[a])
        if segments and segments[-1]['policy']==labels[best]:segments[-1].update(theta_upper=float(right),theta_upper_exact=str(right))
        else:segments.append({'theta_lower':float(left),'theta_upper':float(right),'theta_lower_exact':str(left),'theta_upper_exact':str(right),'policy':labels[best]})
    return segments

def ancillary_ancova(full,point,menu):
    rows=[];frontiers=[]
    for baseline_control in [False,True]:
        treatment_effects={}
        fits={}
        for g in [0,1]:
            keep=full.eligible.eq(g).to_numpy()&full.endline_panel.eq(1).to_numpy();sample=full[keep]
            fit=regress(sample,point[keep],sample.dietarydiversity.to_numpy() if baseline_control else None)
            treatment_effects[g]=np.r_[0.,fit['beta'][1:6]];fits[g]=fit
        for column,model in menu.items():
            frontiers.append({'estimator':'baseline_ancova' if baseline_control else 'block_wls','cost_convention':column,'segments':fitted_frontier(treatment_effects,model['vertices'],model['labels'])})
            for g,fit in fits.items():
                for name,v in zip(model['labels'],model['vertices']):
                    c=np.zeros(len(fit['beta']));c[1]=1.
                    for ai in range(1,6):c[ai]-=float(v[ai])
                    rows.append({'eligible':g,'baseline_control':baseline_control,'cost_convention':column,'policy':name,**contrast(fit,c)})
    tests=[z for z in rows if z['policy']!='Gikuriro']
    if len(tests)!=64:raise ValueError('All 64 exploratory ANCOVA contrasts required')
    for row,p in zip(tests,holm([z['p'] for z in tests])):row['p_holm_64']=float(p)
    for row in rows:
        if row['policy']=='Gikuriro':row['p_holm_64']=1.
    return rows,frontiers

def rational_simplex(values):
    values=np.maximum(np.asarray(values,dtype=float),0.)
    if not np.isfinite(values).all() or values.sum()<=0:raise ValueError('Invalid simplex proposal')
    scaled=values/values.sum()*UNIT;integers=np.floor(scaled).astype(np.int64)
    remainder=UNIT-int(integers.sum())
    if not 0<=remainder<=len(values):raise ValueError('Rational rounding failed')
    order=np.argsort(-(scaled-integers),kind='stable');integers[order[:remainder]]+=1
    return [Fraction(int(x),UNIT) for x in integers]

def solve_box_decision(bounds,vertices,theta_interval):
    """Exact feasible primal/dual replay of a finite zero-sum regional game.

    Theta can vary continuously, but convex regret attains its maximum at an
    endpoint. Every arm-box support has a corner maximizer. These are outer
    regional values, not statistical minimax risk or jointly sharp populations.
    """
    theta=[Fraction(str(x)) for x in theta_interval]
    if len(theta)!=2 or not 0<=theta[0]<=theta[1]<=1:raise ValueError('Valid weight interval required')
    n=len(vertices[0]);states=[];payoffs=[]
    for t in sorted(set(theta)):
        lower=[t*bounds[1][a][0]+(1-t)*bounds[0][a][0] for a in range(n)]
        upper=[t*bounds[1][a][1]+(1-t)*bounds[0][a][1] for a in range(n)]
        for bits in itertools.product([0,1],repeat=n):
            mu=[upper[a] if bits[a] else lower[a] for a in range(n)]
            comparator_values=[sum((r[a]*mu[a] for a in range(n)),Fraction(0)) for r in vertices]
            # Once mu is fixed, its highest-valued comparator is exact.
            best=max(range(len(vertices)),key=lambda i:comparator_values[i])
            payoffs.append([comparator_values[best]-v for v in comparator_values])
            states.append({'theta':str(t),'corner_bits':list(bits),'comparator_index':best})
    A=np.array([[float(v) for v in row]+[-1.] for row in payoffs]);m=len(vertices)
    fit=linprog(np.r_[np.zeros(m),1.],A_ub=A,b_ub=np.zeros(len(A)),A_eq=[np.r_[np.ones(m),0.]],b_eq=[1.],bounds=[(0,None)]*(m+1),method='highs')
    if not fit.success:raise ValueError('Population regional game candidate failed')
    x=rational_simplex(fit.x[:m]);dual=np.maximum(-fit.ineqlin.marginals,0.)
    if not np.isfinite(dual).all():raise ValueError('Nonfinite game dual proposal')
    # At a zero optimum the t>=0 bound can carry all dual mass. Any state
    # probability remains feasible for a lower bound; exact replay, not solver
    # status, determines its value and whether the bracket is informative.
    if dual.sum()<=0:dual=np.r_[1.,np.zeros(len(states)-1)]
    w=rational_simplex(dual)
    q=[sum((x[j]*vertices[j][a] for j in range(m)),Fraction(0)) for a in range(n)]
    upper=max(sum((x[j]*row[j] for j in range(m)),Fraction(0)) for row in payoffs)
    lower=min(sum((w[s]*payoffs[s][j] for s in range(len(states))),Fraction(0)) for j in range(m))
    if lower>upper or min(q)<0 or sum(q)!=1:raise ValueError('Exact regional game replay failed')
    return {'theta_interval':[str(t) for t in theta],'allocation':[str(v) for v in q],'primal_vertex_weights':[str(v) for v in x],'dual_state_weights':[str(v) for v in w],'states':states,'exact_regional_lower':str(lower),'exact_proposal_upper':str(upper),'exact_bracket_gap':str(upper-lower),'regional_lower':float(lower),'proposal_upper':float(upper),'candidate_solver_objective':float(fit.fun),'scope':'Feasible exact rational player/state mixtures bracket the implemented mean-box game. Field bounds are standalone; no intersection or outcome-selected minimum with earlier confidence events. No attained finite-potential-outcome, actual regret or statistical minimax-risk lower bound.'}

def main():
    full,lo,hi,point,counts,assignment,verified=load_population()
    finite,boxes,weights,diagnostics=finite_primitives(full,lo,hi,point,counts)
    quota_rows,quota_boxes=quota_mean_boxes(full,lo,hi,counts,boxes)
    rows,mus,influences=estimates(full,lo,hi,point,assignment)
    tau=weights[1]/(weights[0]+weights[1]);menu=menus();comparisons=[];decisions=[];frontiers=[]
    ancillary,ancillary_frontiers=ancillary_ancova(full,point,menu)
    for column,model in menu.items():
        frontiers.append({'estimator':'assignment_weighted_ratios','cost_convention':column,'segments':fitted_frontier({g:mus[g,'identified_diets'] for g in [0,1]},model['vertices'],model['labels'])})
        for name,v in zip(model['labels'],model['vertices']):
            c=np.array([float(Fraction(int(a=='Gikuriro'))-v[i]) for i,a in enumerate(ARMS)])
            for population,t in [('eligible',Fraction(1)),('ineligible',Fraction(0)),('baseline_weight_aggregate',tau)]:
                tf=float(t);means=tf*mus[1,'identified_diets']+(1-tf)*mus[0,'identified_diets']
                influence=tf*influences[1,'identified_diets']+(1-tf)*influences[0,'identified_diets']
                l=tf*mus[1,'lower_endpoint']+(1-tf)*mus[0,'lower_endpoint'];h=tf*mus[1,'upper_endpoint']+(1-tf)*mus[0,'upper_endpoint']
                cp=np.maximum(c,0);cn=np.minimum(c,0)
                comparisons.append({'cost_convention':column,'population':population,'policy':name,'gikuriro_minus_policy_identified':float(c@means),'exploratory_block_se':float(np.linalg.norm(influence@c)),'estimated_missingness_lower':float(cp@l+cn@h),'estimated_missingness_upper':float(cp@h+cn@l)})
        for method,source_boxes in [('classical_mean_family',boxes),('quota_mean_only',quota_boxes)]:
            region={g:[(Fraction(source_boxes[g,a]['lower']),Fraction(source_boxes[g,a]['upper'])) for a in ARMS] for g in [0,1]}
            for population,interval in [('eligible',[1,1]),('baseline_weight_aggregate',[str(tau),str(tau)]),('unknown_population_weight',[0,1])]:
                result=solve_box_decision(region,model['vertices'],interval)
                q=[Fraction(s) for s in result['allocation']];expected=sum((c*p for c,p in zip(model['costs'],q)),Fraction(0))
                if expected>model['budget']:raise ValueError('Exact cost infeasibility')
                decisions.append({'method':method,'cost_convention':column,'population':population,'exact_expected_cost':str(expected),'exact_budget':str(model['budget']),**result})
    pd.DataFrame(rows).to_csv(OUT/'community_arm_estimates.csv',index=False,lineterminator='\n')
    pd.DataFrame([{k:v for k,v in z.items() if k not in ['blocks','threshold_lower','threshold_upper']} for z in finite]).to_csv(OUT/'community_finite_primitives.csv',index=False,lineterminator='\n')
    pd.DataFrame(comparisons).to_csv(OUT/'community_policy_comparisons.csv',index=False,lineterminator='\n')
    pd.DataFrame(ancillary).to_csv(OUT/'community_ancova.csv',index=False,lineterminator='\n')
    report={'scope':'Baseline-defined eligible/ineligible released fixed weighted samples. Arbitrary arm-dependent missingness via item endpoints. Two separate standalone conditional 95% events: classical 36-primitive family and quota 24 one-sided endpoint tests. Neither events nor realized certificate minima are combined into joint 95% protection. Uniform quota labels and independent blocks are maintained; broader-frame/national transport and historical assignment law unverified. Baseline eligibility is not receipt; no isolated spillover, Catholic mechanism or institutional preference claim. Source average costs remain conditional accounting. Fitted ratios, asymptotic sensitivities and finite regional certificates are separate.','family_size':FAMILY,'alpha':str(ALPHA),'normative_weight_scope':'Any stated total eligible welfare weight theta in [0,1]; each simultaneous mean event separately protects outcome-selected theta/policy. No actual preference or welfare beyond HDDS is recovered.','asymptotic_scope':'Bonferroni-t block linearization sensitivity only; no finite-coverage claim, combination with finite event or pass criterion. Earlier failed approximation diagnostics remain.','input_hashes':verified,'baseline_diagnostics':diagnostics,'baseline_eligible_weight_share_exact':str(tau),'baseline_eligible_weight_share':float(tau),'finite_primitives':finite,'quota_mean_test_family':24,'quota_mean_test_cap':'480','quota_mean_normalizers':quota_rows,'mean_boxes':[{'eligible':g,'arm':a,**boxes[g,a]} for g in [0,1] for a in ARMS],'quota_mean_boxes':[{'eligible':g,'arm':a,**quota_boxes[g,a]} for g in [0,1] for a in ARMS],'menus':{k:{'costs':[str(x) for x in v['costs']],'budget':str(v['budget']),'labels':v['labels'],'vertices':[[str(x) for x in z] for z in v['vertices']]} for k,v in menu.items()},'decisions':decisions,'causal_welfare_ranking_identified':False,'general_interest_importance_established':False}
    report['fitted_frontiers']=frontiers+ancillary_frontiers
    report['ancova_multiplicity']='Separate exploratory 64-test Holm family: two baseline specifications, two source cost conventions, two baseline strata and eight non-Gikuriro cash/control comparisons. Observed panel diets still select samples; inference is village CR1/G-1 t, distinct from block ratios and finite events.'
    (OUT/'community-decision.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
    print(pd.DataFrame([{k:z[k] for k in ['method','cost_convention','population','regional_lower','proposal_upper']} for z in decisions]).to_string(index=False))

if __name__=='__main__':main()
