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

def reported_interval(value,reporting,arm):
    if reporting=='complete':lower=upper=value
    elif reporting=='coarse_interval':lower=(value//200)*200;upper=min(1000,lower+200)
    elif reporting=='assignment_dependent':
        reported=(value<=500) if arm==0 else (value>=500)
        lower,upper=(value,value) if reported else (0,1000)
    else:raise ValueError('Unknown reporting pattern')
    if not lower<=value<=upper:raise AssertionError('Truth outside reported interval')
    return lower,upper

def empirical_best_probability(weights,selected,potential,reporting):
    """HT reported-interval midpoints; missing intervals use midpoint 0.5.

    Common HT denominator cancels in the comparison. No confidence or
    welfare certificate is asserted for this deterministic selection rule.
    """
    scores=[sum(int(weights[slot])*sum(reported_interval(int(potential[a][b,slot]),reporting,a))
                for b,slots in enumerate(selected[a]) for slot in slots) for a in [0,1]]
    return Fraction(1 if scores[1]>scores[0] else 0) if scores[1]!=scores[0] else Fraction(1,2)

def monte_carlo_summary(draws):
    draws=np.asarray(draws,dtype=float)
    return {'mean_actual_regret':float(draws.mean()),
            'mc_standard_error':0.0 if np.ptp(draws)==0 else float(draws.std(ddof=1)/np.sqrt(len(draws)))}

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
            lower,upper=reported_interval(value,reporting,arm)
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
            lower,upper=reported_interval(value,reporting,arm)
            lo+=w*lower;hi+=w*upper
            for sign in [-1,1]:g[sign]+=min(table[w,position,lower,sign],table[w,position,upper,sign])
    logical=(Fraction(lo,1000*total),Fraction(hi+1000*(total-assigned_mass),1000*total))
    logcap=Fraction(ilog(I(80)).hi);denominator=Fraction(lam)*total
    return (max(logical[0],(Fraction(g[1],DYADIC)-logcap)/denominator),
            min(logical[1],(logcap-Fraction(g[-1],DYADIC))/denominator)),logical

def main():
    start=time.perf_counter();rows=[];settings=[];cache={};benchmark_rows=[];paired_rows=[];draw_rows=[]
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
        case_fields={'case':case_index,'n':n,'blocks':blocks,'weight_shape':shape,
                     'effect_thousandths':effect,'reporting':reporting,'repetitions':REPETITIONS}
        regret_draws={}
        benchmark_probabilities={'no_learning_half':[Fraction(1,2)]*REPETITIONS,
            'empirical_best_midpoint':[empirical_best_probability(weights,selected,potential,reporting) for selected in samples]}
        for benchmark,probabilities in benchmark_probabilities.items():
            draws=[float(max(means)-(1-q)*means[0]-q*means[1]) for q in probabilities]
            regret_draws[benchmark]=draws
            benchmark_rows.append({**case_fields,'method':benchmark,**monte_carlo_summary(draws),
                                   'comparable_certificate':False})
        for method in DECISION_METHODS:
            begin=time.perf_counter();moment=cache[key][method]
            # Stored Decimal upper is converted to an exact rational, so all
            # subsequent interval and policy calculations avoid float error.
            radius=Fraction(Decimal(moment['radius_numerator_upper']))/total if method!='empirical_bernstein_fixed_forecast' else None
            losses=[];actual=[];coverages=[];fallbacks=[];roundings=[];q_values=[];counts={Fraction(1,20):0,Fraction(1,10):0}
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
                for tolerance in counts:counts[tolerance]+=int(upper<=tolerance)
                losses.append(float(upper));actual.append(float(regret));roundings.append(float(rounding));q_values.append(float(q))
            regret_draws[method]=actual
            rows.append({**case_fields,'method':method,
                'true_effect':float(means[1]-means[0]),'mean_actual_regret':float(np.mean(actual)),
                'mc_standard_error':monte_carlo_summary(actual)['mc_standard_error'],
                'p95_actual_regret':float(np.quantile(actual,.95)),'mean_certified_loss_upper':float(np.mean(losses)),
                'certificates_at_most_005':counts[Fraction(1,20)],
                'certificates_at_most_010':counts[Fraction(1,10)],
                'joint_mean_interval_coverage_count':int(sum(coverages)),'empty_region_fallback_count':int(sum(fallbacks)),
                'maximum_rational_policy_rounding_bound':max(roundings),'mean_probability_arm_1':float(np.mean(q_values)),
                'baseline_setup_seconds':moment['baseline_setup_seconds'],'decision_seconds':time.perf_counter()-begin})
        for first,second in itertools.combinations(regret_draws,2):
            differences=np.asarray(regret_draws[first])-np.asarray(regret_draws[second])
            summary=monte_carlo_summary(differences)
            paired_rows.append({**case_fields,'first_method':first,'second_method':second,
                               'mean_regret_difference':summary['mean_actual_regret'],
                               'paired_mc_standard_error':summary['mc_standard_error']})
        draw_rows.extend({'case':case_index,'repetition':i,**{method:values[i] for method,values in regret_draws.items()}}
                         for i in range(REPETITIONS))
        print('Designed decision case',case_index+1,'/',len(all_cases),flush=True)
    report={'scope':'Designed, known bounded potential outcomes; no new field observations. All 144 cells fixed in code, 256 uniform half-quota draws each, seed 20261001. Two arms, one normalized mean, equal costs, four Bonferroni exponential tests at cap 80 (failure <= .05), fixed weighted population target, arbitrary reporting endpoints. Baseline-only scales and directed moments followed by exact rational interval and minimax rectangular-region decisions. Coverage counts are diagnostics, not a proof or tuned pass criterion. Empty pre-fallback regions and all cases are retained. This is a different procedure from the field shared distributional event and establishes neither field minimax optimality nor superiority over all variance-adaptive or betting methods.',
        'seed':SEED,'grid':GRID,'repetitions_per_case':REPETITIONS,'methods':DECISION_METHODS,
        'event_terms':4,'event_cap':80,'failure_bound':'4/80 = 0.05',
        'decision_probability_denominator':DENOMINATOR,'baseline_moment_settings':settings,
        'empirical_bernstein_scope':'Established WoR empirical-Bernstein process with fixed baseline forecast and telescoping predictable scales, baseline-only heuristic variance proxy, explicitly randomized sample order, and directed endpoint minima quantized downward to dyadic 2**-50. Compensation uses realized scores. All subsequent interval/decision arithmetic is exact rational. This restricted adaptation is not the full optimized variance-adaptive or betting family.',
        'monte_carlo_scope':'Per-cell MC standard errors use sample standard deviation / sqrt(256). Paired differences use the same assignments for both rules. Equal-cell summaries combine independent cell variances and divide by the square of cell count; they condition on the declared grid, not a sampled population of policy problems. No multiple-comparison or coverage certificate follows from these simulation standard errors.',
        'benchmark_scope':'No-learning assigns each arm probability 1/2: exact regret abs(effect)/2, with equal-effect-grid average 0.045. Empirical-best-arm compares HT reported-interval midpoints, including midpoint 0.5 for unreported [0,1]; ties use probability 1/2. Both use the same potential population and assignment draws, and have no comparable loss certificate.',
        'rows':rows,'benchmark_rows':benchmark_rows,'paired_rows':paired_rows,'seconds':time.perf_counter()-start}
    (ROOT/'output/designed-decisions.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    # Machine timings are retained in JSON, outside the deterministic CSV.
    pd.DataFrame([{k:v for k,v in row.items() if not k.endswith('_seconds')} for row in rows]).to_csv(ROOT/'output/designed_decisions.csv',index=False)
    pd.DataFrame(benchmark_rows).to_csv(ROOT/'output/designed_decision_benchmarks.csv',index=False)
    pd.DataFrame(paired_rows).to_csv(ROOT/'output/designed_decision_pairs.csv',index=False)
    pd.DataFrame(draw_rows).to_csv(ROOT/'output/designed_decision_draws.csv',index=False)
    print('Designed decision experiment:',len(rows),'rows;',report['seconds'],'seconds',flush=True)

if __name__=='__main__':main()
