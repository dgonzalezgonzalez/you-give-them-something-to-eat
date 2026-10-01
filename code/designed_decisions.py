"""Known-population decision experiment; never fabricated field observations.

The two-arm, single-mean Bonferroni procedure differs from the field's shared
276-term event. Four fixed exponential tests at cap 80 give failure <= .05.
The exact rational rectangular-region decision solves its own minimax
problem, up to a reported rounding bound. No field minimax claim follows.
"""
from pathlib import Path
from fractions import Fraction
from decimal import Decimal
import itertools,json,time
import numpy as np,pandas as pd
from design_moments import METHODS,select_scalar_moment
from empbern_quota import select_empbern_scale,coefficients,endpoint_dyadic_lower,DYADIC
from weighted_product_moments import ilog
from quota_arithmetic import I

ROOT=Path(__file__).resolve().parents[1]
SEED=20261001
REPETITIONS=256
DENOMINATOR=1000000
DECISION_METHODS=METHODS+['empirical_bernstein_fixed_forecast']
GRID={'n':[8,24,64],'blocks':[8,32],'weight_shape':['equal','concentrated'],
      'effect_thousandths':[-160,0,40,160],'reporting':['complete','coarse_interval','assignment_dependent']}

def rectangle_decision(bounds,denominator=DENOMINATOR):
    """Exact minimax mixture for a product of two mean intervals.

    U=max(0,H1-L0), L=max(0,H0-L1). The loss of assigning treatment 1
    with probability q is max((1-q)U,qL). Its minimum is UL/(U+L).
    """
    (l0,h0),(l1,h1)=bounds
    if not 0<=l0<=h0<=1 or not 0<=l1<=h1<=1:raise ValueError('Ordered unit intervals required')
    U=max(Fraction(0),h1-l0);L=max(Fraction(0),h0-l1)
    optimal=U/(U+L) if U+L else Fraction(1,2)
    scaled=optimal*denominator;integer=(2*scaled.numerator+scaled.denominator)//(2*scaled.denominator)
    q=Fraction(integer,denominator);upper=max((1-q)*U,q*L)
    lower=U*L/(U+L) if U+L else Fraction(0)
    rounding=max(U,L)*abs(q-optimal)
    if not lower<=upper<=lower+rounding:raise AssertionError('Exact decision certificate failed')
    return q,upper,lower,rounding

def observed_bounds(weights,selected,y,reporting,arm,total,radius):
    """Exact HT endpoints and deterministic full-population logical mass."""
    lo=0;hi=0;assigned_mass=0
    for block,slots in enumerate(selected):
        for slot in slots:
            w=int(weights[slot]);value=int(y[block,slot]);assigned_mass+=w
            if reporting=='complete':lower=upper=value
            elif reporting=='coarse_interval':lower=(value//200)*200;upper=min(1000,lower+200)
            elif reporting=='assignment_dependent':
                # Reporting depends on assigned arm and its observed potential
                # outcome. Unreported units remain in the fixed target.
                reported=(value<=500) if arm==0 else (value>=500)
                lower,upper=(value,value) if reported else (0,1000)
            else:raise ValueError('Unknown reporting pattern')
            if not lower<=value<=upper:raise AssertionError('Truth outside reported interval')
            lo+=w*lower;hi+=w*upper
    logical=(Fraction(lo,1000*total),Fraction(hi+1000*(total-assigned_mass),1000*total))
    # Every design has k=n/2 in both arms, so the HT expansion factor is 2.
    lower=max(logical[0],Fraction(2*lo,1000*total)-radius)
    upper=min(logical[1],Fraction(2*hi,1000*total)+radius)
    return (lower,upper),logical

def empbern_tables(weights,k,lam):
    coeff=coefficients(weights,k,lam);table={}
    # Every predeclared potential score and coarse endpoint is a multiple of
    # five thousandths. This finite lookup is exact for the published grid.
    for weight in sorted(set(int(w) for w in weights)):
        for position,score,sign in itertools.product(range(k),range(0,1001,5),[-1,1]):
            table[(weight,position,score,sign)]=endpoint_dyadic_lower(weight,score,position,sign,coeff)
    return table

def empirical_bounds(weights,selected,y,reporting,arm,total,lam,table):
    lo=0;hi=0;assigned_mass=0;g={-1:0,1:0}
    for block,slots in enumerate(selected):
        for position,slot in enumerate(slots):
            w=int(weights[slot]);value=int(y[block,slot]);assigned_mass+=w
            if reporting=='complete':lower=upper=value
            elif reporting=='coarse_interval':lower=(value//200)*200;upper=min(1000,lower+200)
            else:
                reported=(value<=500) if arm==0 else (value>=500)
                lower,upper=(value,value) if reported else (0,1000)
            lo+=w*lower;hi+=w*upper
            for sign in [-1,1]:g[sign]+=min(table[w,position,lower,sign],table[w,position,upper,sign])
    logical=(Fraction(lo,1000*total),Fraction(hi+1000*(total-assigned_mass),1000*total))
    logcap=Fraction(ilog(I(80)).hi);denominator=Fraction(lam)*total
    return (max(logical[0],(Fraction(g[1],DYADIC)-logcap)/denominator),
            min(logical[1],(logcap-Fraction(g[-1],DYADIC))/denominator)),logical

def main():
    start=time.perf_counter();rows=[];settings=[];cache={}
    all_cases=list(itertools.product(*(GRID[name] for name in GRID)))
    for case_index,(n,blocks,shape,effect,reporting) in enumerate(all_cases):
        weights=np.ones(n,dtype=np.int64)
        if shape=='concentrated':weights[-1]=10
        total=blocks*int(weights.sum());k=n//2
        baseline=200+5*((np.arange(blocks)[:,None]*17+np.arange(n)[None,:]*37)%101)
        potential=[baseline,baseline+effect]
        means=[Fraction(int((y*weights).sum()),1000*total) for y in potential]
        if min(y.min() for y in potential)<0 or max(y.max() for y in potential)>1000:raise AssertionError('Unbounded fixture')
        key=(n,blocks,shape)
        if key not in cache:
            cache[key]={}
            for method in DECISION_METHODS:
                begin=time.perf_counter()
                if method=='empirical_bernstein_fixed_forecast':
                    moment=select_empbern_scale([(weights,k)]*blocks,80)
                    moment['lookup_table']=empbern_tables(weights,k,moment['lambda'])
                else:moment=select_scalar_moment(weights,k,blocks,80,method)
                cache[key][method]={**moment,'baseline_setup_seconds':time.perf_counter()-begin}
                settings.append({'n':n,'blocks':blocks,'weight_shape':shape,**{key:value for key,value in cache[key][method].items() if key!='lookup_table'}})
        rng=np.random.default_rng(np.random.SeedSequence([SEED,case_index]))
        order_rng=np.random.default_rng(np.random.SeedSequence([SEED,case_index,1]))
        samples=[]
        for repetition in range(REPETITIONS):
            treated=[rng.choice(n,size=k,replace=False).tolist() for _ in range(blocks)]
            controls=[np.flatnonzero(~np.isin(np.arange(n),slots)).tolist() for slots in treated]
            # Separate RNG preserves the original assignment draws. Both arm
            # samples receive an independent conditional uniform ordering.
            samples.append([[order_rng.permutation(slots).tolist() for slots in controls],
                            [order_rng.permutation(slots).tolist() for slots in treated]])
        for method in DECISION_METHODS:
            begin=time.perf_counter();moment=cache[key][method]
            # Stored Decimal upper is converted to an exact rational, so all
            # subsequent interval and policy calculations avoid float error.
            radius=Fraction(Decimal(moment['radius_numerator_upper']))/total if method!='empirical_bernstein_fixed_forecast' else None
            losses=[];actual=[];coverages=[];fallbacks=[];roundings=[];q_values=[]
            for selected in samples:
                if method=='empirical_bernstein_fixed_forecast':
                    results=[empirical_bounds(weights,selected[a],potential[a],reporting,a,total,moment['lambda'],moment['lookup_table']) for a in [0,1]]
                else:results=[observed_bounds(weights,selected[a],potential[a],reporting,a,total,radius) for a in [0,1]]
                bounds=[x[0] for x in results]
                covered=all(l<=m<=h for (l,h),m in zip(bounds,means));coverages.append(covered)
                fallback=any(l>h for l,h in bounds);fallbacks.append(fallback)
                if fallback:bounds=[x[1] for x in results]
                q,upper,lower,rounding=rectangle_decision(bounds)
                regret=max(means)-(1-q)*means[0]-q*means[1]
                if regret<0 or (covered and regret>upper):raise AssertionError('Decision guarantee failed on covered draw')
                losses.append(float(upper));actual.append(float(regret));roundings.append(float(rounding));q_values.append(float(q))
            rows.append({'case':case_index,'n':n,'blocks':blocks,'weight_shape':shape,
                'effect_thousandths':effect,'reporting':reporting,'method':method,'repetitions':REPETITIONS,
                'true_effect':float(means[1]-means[0]),'mean_actual_regret':float(np.mean(actual)),
                'p95_actual_regret':float(np.quantile(actual,.95)),'mean_certified_loss_upper':float(np.mean(losses)),
                'certificates_at_most_005':int(sum(x<=.05 for x in losses)),
                'certificates_at_most_010':int(sum(x<=.10 for x in losses)),
                'joint_mean_interval_coverage_count':int(sum(coverages)),'empty_region_fallback_count':int(sum(fallbacks)),
                'maximum_rational_policy_rounding_bound':max(roundings),'mean_probability_arm_1':float(np.mean(q_values)),
                'baseline_setup_seconds':moment['baseline_setup_seconds'],'decision_seconds':time.perf_counter()-begin})
        print('Designed decision case',case_index+1,'/',len(all_cases),flush=True)
    report={'scope':'Designed, known bounded potential outcomes; no new field observations. All 144 cells fixed in code, 256 uniform half-quota draws each, seed 20261001. Two arms, one normalized mean, equal costs, four Bonferroni exponential tests at cap 80 (failure <= .05), fixed weighted population target, arbitrary reporting endpoints. Baseline-only scales and directed moments followed by exact rational interval and minimax rectangular-region decisions. Coverage counts are diagnostics, not a proof or tuned pass criterion. Empty pre-fallback regions and all cases are retained. This is a different procedure from the field shared distributional event and establishes neither field minimax optimality nor superiority over all variance-adaptive or betting methods.',
        'seed':SEED,'grid':GRID,'repetitions_per_case':REPETITIONS,'methods':DECISION_METHODS,
        'event_terms':4,'event_cap':80,'failure_bound':'4/80 = 0.05',
        'decision_probability_denominator':DENOMINATOR,'baseline_moment_settings':settings,
        'empirical_bernstein_scope':'Established WoR empirical-Bernstein process with fixed baseline forecast and telescoping predictable scales, baseline-only heuristic variance proxy, explicitly randomized sample order, and directed endpoint minima quantized downward to dyadic 2**-50. Compensation uses realized scores. All subsequent interval/decision arithmetic is exact rational. This restricted adaptation is not the full optimized variance-adaptive or betting family.',
        'rows':rows,'seconds':time.perf_counter()-start}
    (ROOT/'output/designed-decisions.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    # Machine timings are retained in JSON, outside the deterministic CSV.
    pd.DataFrame([{k:v for k,v in row.items() if not k.endswith('_seconds')} for row in rows]).to_csv(ROOT/'output/designed_decisions.csv',index=False)
    print('Designed decision experiment:',len(rows),'rows;',report['seconds'],'seconds',flush=True)

if __name__=='__main__':main()
