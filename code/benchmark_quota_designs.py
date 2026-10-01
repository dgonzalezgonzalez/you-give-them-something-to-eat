"""Baseline-only design comparisons, not simulated field observations.

Compare one normalized scalar tail radius for 22 identical independent
blocks at the production family penalty log(5520). Every listed design is
reported. No empirical coverage tuning or method-wise allocation claim.
"""
from pathlib import Path
import json,time
import numpy as np,pandas as pd
from quota_benchmarks import range_coefficient
from quota_moments import quota_upper_log_moment

ROOT=Path(__file__).resolve().parents[1]

def main():
    start=time.time();penalty=np.log(5520.);rows=[]
    for n in [6,10,12]:
        quotas=sorted(set([1,n//4,n//2,n-1]))
        for k in quotas:
            for shape in ['equal','alternating','concentrated']:
                weights=np.ones(n,dtype=int)
                if shape=='alternating':weights[1::2]=3
                if shape=='concentrated':weights[-1]=10
                blocks=22;total=blocks*int(weights.sum());maximum=int(weights.max())
                proxies={method:blocks*float(range_coefficient(n,k,method))*maximum**2 for method in ['hoeffding','serfling','harmonic_martingale']}
                radii={method:float(np.sqrt(v*penalty/2)/total) for method,v in proxies.items()}
                base=np.sqrt(8*penalty/proxies['harmonic_martingale']);grid=[]
                for scale in [.5,.75,1.,1.25,1.5,2.]:
                    lam=float(base*scale);B,_=quota_upper_log_moment(weights,k,lam)
                    radius=(blocks*B+penalty)/(lam*total)
                    grid.append({'scale':scale,'lambda':lam,'block_log_moment_upper':B,'radius':radius})
                best=min(grid,key=lambda x:x['radius'])
                row={'n':n,'k':k,'weight_shape':shape,'blocks':blocks,'quota_radius':best['radius'],
                     **{method+'_radius':radius for method,radius in radii.items()},
                     'quota_over_martingale':best['radius']/radii['harmonic_martingale'],'selected_scale':best['scale'],
                     'quota_grid':grid}
                rows.append(row);print(json.dumps({key:value for key,value in row.items() if key!='quota_grid'}),flush=True)
    result={'scope':'Deterministic design catalogue; 22 identical independent blocks and log(5520) scalar tail penalty. Radii normalize by total fixed weight. Classical quadratic moments use analytically optimized lambda; quota moments use a common six-point baseline-only grid around the harmonic-martingale lambda. These are untruncated analytic tail radii, not joint-region allocation bounds or simulated coverage. Production scales and event are unchanged.',
            'rows':rows,'seconds':time.time()-start}
    (ROOT/'output/quota-design-benchmarks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    pd.DataFrame([{k:v for k,v in row.items() if k!='quota_grid'} for row in rows]).to_csv(ROOT/'output/quota_design_benchmarks.csv',index=False)
    print('Design benchmark seconds',result['seconds'])

if __name__=='__main__':main()
