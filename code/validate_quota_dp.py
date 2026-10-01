"""Independent high-precision full enumeration of the polynomial recurrence."""
from pathlib import Path
from decimal import Decimal,localcontext
import itertools,json,time,random
from quota_moments import quota_upper_log_moment_dp,decimal_weight,quota_log_moment_dp_float
from weighted_product_moments import product_log_upper
from quota_benchmarks import range_coefficient

ROOT=Path(__file__).resolve().parents[1]
checks={};slacks=[];start=time.time();rng=random.Random(20261001)

def reference(weights,k,lam):
    with localcontext() as ctx:
        ctx.prec=160
        w=[decimal_weight(x) for x in weights];n=len(w);L=decimal_weight(lam);best=Decimal(0)
        subsets=list(itertools.combinations(range(n),k))
        for bits in itertools.product([0,1],repeat=n):
            x=[v*Decimal(y) for v,y in zip(w,bits)];total=sum(x)
            for sign in [-1,1]:
                mean=sum((Decimal(sign)*L*(Decimal(n)*sum(x[j] for j in subset)/Decimal(k)-total)).exp() for subset in subsets)/Decimal(len(subsets))
                best=max(best,mean.ln())
        return best

fixtures=[]
for n in range(2,7):
    fixtures.extend([[1.]*n,[rng.uniform(.2,5) for _ in range(n)],[float(rng.randrange(1,8)) for _ in range(n)]])
fixtures.append([Decimal('1.00000000000000000000000000000000000000000000000000000000000000000000000000000001'),Decimal('1.99999999999999999999999999999999999999999999999999999999999999999999999999999998'),Decimal('3')])
for i,w in enumerate(fixtures):
    for k in range(1,len(w)):
        for lam in [.01,.2,.6]:
            upper,detail=quota_upper_log_moment_dp(w,k,lam);truth=reference(w,k,lam)
            checks[f'full_population_and_subset_enclosure_{i}_{k}_{lam}']=decimal_weight(upper)>=truth
            slacks.append(float(decimal_weight(upper)-truth))
            checks[f'polynomial_population_count_{i}_{k}_{lam}']=detail['threshold_populations']==2*(len(w)+1)
            checks[f'floating_recurrence_diagnostic_{i}_{k}_{lam}']=abs(quota_log_moment_dp_float(w,k,lam)-float(truth))<=2e-12*max(1.,abs(float(truth)))
            checks[f'weighted_product_enclosure_{i}_{k}_{lam}']=decimal_weight(product_log_upper(w,k,lam))>=truth
            checks[f'product_harmonic_enclosure_{i}_{k}_{lam}']=decimal_weight(product_log_upper(w,k,lam,range_coefficient(len(w),k,'harmonic_martingale')))>=truth
    checks[f'full_census_{i}']=quota_upper_log_moment_dp(w,len(w),.6)[0]==0.
    checks[f'zero_scale_{i}']=quota_upper_log_moment_dp(w,1,0.)[0]==0.
for i,args in enumerate([([],1,.2),([0.,2.],1,.2),([1.,2.],.5,.2),([1.,2.],3,.2),([1.,float('nan')],1,.2),([1.,2.],1,float('nan'))]):
    try:quota_upper_log_moment_dp(*args);checks[f'invalid_{i}']=False
    except ValueError:checks[f'invalid_{i}']=True
report={'scope':'Independent 160-digit full binary populations and quota subsets versus directed sorted-threshold recurrence; supporting verification, not field coverage or algorithmic novelty.',
        'checks':checks,'all_passed':all(checks.values()),'minimum_upper_slack':min(slacks),'seconds':time.time()-start}
(ROOT/'output/quota-dp-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(sum(checks.values()),'/',len(checks),'checks; minimum upper slack',min(slacks),'seconds',report['seconds'],flush=True)
if not report['all_passed']:raise AssertionError([k for k,v in checks.items() if not v])
