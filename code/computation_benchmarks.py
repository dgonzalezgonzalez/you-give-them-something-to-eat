"""Actual wall-clock costs on declared designs; all cases and limits retained."""
from pathlib import Path
import json,math,platform,time
import numpy as np
from quota_moments import quota_upper_log_moment,quota_upper_log_moment_dp
from weighted_product_moments import product_log_upper
from quota_benchmarks import range_coefficient

ROOT=Path(__file__).resolve().parents[1]
def measure(fn):
    elapsed=[];values=[]
    for _ in range(3):
        start=time.perf_counter();values.append(fn());elapsed.append(time.perf_counter()-start)
    return values[0],{'seconds_all_three_runs':elapsed,'median_seconds':float(np.median(elapsed))}

def main():
    start=time.perf_counter();rows=[]
    for n in [12,24,48,96]:
        for k in [n//4,n//2]:
            for shape in ['equal','concentrated']:
                w=np.ones(n,dtype=int)
                if shape=='concentrated':w[-1]=10
                lam=.1/float(max(w));coef=range_coefficient(n,k,'harmonic_martingale')
                (value,receipt),timing=measure(lambda:quota_upper_log_moment_dp(w,k,lam))
                product,product_timing=measure(lambda:product_log_upper(w,k,lam,coef))
                implicit=(2**n)*math.comb(n,k)
                reference=None
                if implicit<=4000000:
                    (old,detail),old_timing=measure(lambda:quota_upper_log_moment(w,k,lam))
                    reference={'upper_log_moment':old,'directed_difference':old-value,**old_timing}
                rows.append({'n':n,'k':k,'weight_shape':shape,'fixed_lambda':lam,
                    'quota_upper_log_moment':value,'quota_moment_receipt':receipt,'quota_timing':timing,
                    'weight_sensitive_hybrid_upper_log_moment':product,'weight_sensitive_hybrid_timing':product_timing,
                    'implicit_population_subset_pairs':implicit,'enumerated_reference':reference,
                    'enumeration_guard':'Exhaustive reference is timed only if 2**n * choose(n,k) <= 4,000,000; skipped cases are not attempted or estimated.'})
                print('Computation case',n,k,shape,'DP median',timing['median_seconds'],flush=True)
    report={'scope':'Declared 16 cases with three actual serial wall-clock calls each; fixed lambda .1/max(weight), positive integer weights. Existing exhaustive certified implementation is attempted only under the stated size guard. Dynamic-program and hybrid timings concern moment calculation, not end-to-end inference or optimized decisions. Larger cases become computationally accessible; the symmetric-convex reduction and symmetric-mean recurrence are adaptations of established ideas, not new general algorithms.',
        'python':platform.python_version(),'platform':platform.platform(),'rows':rows,'seconds':time.perf_counter()-start}
    (ROOT/'output/quota-computation-benchmarks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print('Computation benchmarks seconds',report['seconds'],flush=True)

if __name__=='__main__':main()
