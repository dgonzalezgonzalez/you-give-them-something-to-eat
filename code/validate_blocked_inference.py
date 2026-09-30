"""Exact falsifier plus finite-block stress simulations under released quotas.

These are synthetic design diagnostics, not actual coverage certification.
The multiplier diagnostic uses 4,999 draws, not the headline 99,999.
"""
from pathlib import Path
import itertools,json,hashlib
import numpy as np
import pandas as pd
from scipy.stats import beta,binom
from estimate import ARMS,TX
from blocked_inference import hajek_block,referee_counterexample

ROOT=Path(__file__).resolve().parents[1]
SEED=20261001;REPLICATIONS=800;DRAWS=4999

def main():
    d=pd.read_csv(ROOT/'data/input/households.csv')
    d['arm']='Control'
    for a,k in zip(ARMS[1:],TX):d.loc[d[k]==1,'arm']=a
    base=d[(d['round']==1)&(d.eligible==1)]
    frame=base.groupby('vid',sort=True).agg(block=('block','first'),arm=('arm','first'),weight=('samp_wgt','sum')).reset_index()
    blocks=sorted(frame.block.unique());B=len(blocks)
    quota=pd.crosstab(frame.block,frame.arm).reindex(index=blocks,columns=ARMS)
    probability=quota.div(quota.sum(axis=1),axis=0)
    assignment={a:probability[a].to_dict() for a in ARMS}
    actual_weights=frame.weight.to_numpy();block_rows=[np.flatnonzero(frame.block.to_numpy()==b) for b in blocks]
    rng=np.random.default_rng(SEED)
    labels=np.zeros((REPLICATIONS,len(frame)),dtype=int)
    for ix,b in zip(block_rows,blocks):
        template=np.repeat(np.arange(6),quota.loc[b].to_numpy(dtype=int))
        order=np.argsort(rng.random((REPLICATIONS,len(ix))),axis=1)
        labels[:,ix]=template[order]
    contrasts=np.array([np.eye(6)[j]-np.eye(6)[k] for j,k in itertools.combinations(range(6),2)])
    signs=rng.choice([-1.,1.],size=(DRAWS,B))
    rank=min(DRAWS,int(binom.ppf(.99,DRAWS,.95))+1)
    cases=[];direct_error=None
    for scenario in ['balanced_equal_weights','block_heterogeneity','unequal_frame_weights','rare_positive_effect']:
        weights=actual_weights if scenario=='unequal_frame_weights' else np.ones(len(frame))
        values=np.zeros((len(frame),6))
        for bi,ix in enumerate(block_rows):
            low=np.r_[np.full(len(ix)//2,4.),np.full(len(ix)//2,6.),[5.] if len(ix)%2 else []]
            if scenario in ['block_heterogeneity','unequal_frame_weights']:
                low=3.+4.*bi/(B-1)+.7*(low-5.)
            values[ix]=low[:,None]
        width=12.
        if scenario=='rare_positive_effect':
            values[:]=0.;values[np.array([0,39,91,178]),ARMS.index('Lower')]=1.;width=1.
        true_arm=(weights[:,None]*values).sum(axis=0)/weights.sum()
        truth=contrasts@true_arm
        means=np.zeros((REPLICATIONS,6));scores=np.zeros((REPLICATIONS,B,6))
        for ai,a in enumerate(ARMS):
            invp=frame.block.map(assignment[a]).to_numpy()
            contribution=(labels==ai)*(weights/invp)[None,:]
            denominator=contribution.sum(axis=1)
            means[:,ai]=(contribution*values[:,ai][None,:]).sum(axis=1)/denominator
            raw=contribution*(values[:,ai][None,:]-means[:,ai,None])/denominator[:,None]
            for bi,ix in enumerate(block_rows):scores[:,bi,ai]=raw[:,ix].sum(axis=1)
        scores*=np.sqrt(B/(B-1))
        if scenario=='balanced_equal_weights':
            sample=frame.copy();sample['arm']=np.array(ARMS)[labels[0]];sample['samp_wgt']=weights
            observed=values[np.arange(len(frame)),labels[0]]
            direct,I,_=hajek_block(sample,observed,assignment,ARMS)
            direct_error=max(np.max(np.abs(direct-means[0])),np.max(np.abs(I-scores[0])))
            assert direct_error<1e-12
        covered=[];zero_guarded=0
        for ri in range(REPLICATIONS):
            perturbation=scores[ri]@contrasts.T
            se=np.linalg.norm(perturbation,axis=0);active=se>1e-12
            if active.any():
                maxima=np.max(np.abs(signs@(perturbation[:,active]/se[active])),axis=1)
                critical=np.partition(maxima,rank-1)[rank-1]
            else:critical=0.
            effect=contrasts@means[ri]
            low=effect-critical*se;high=effect+critical*se
            low[~active]=-width;high[~active]=width;zero_guarded+=int((~active).sum())
            covered.append(bool(np.all((truth>=low-1e-12)&(truth<=high+1e-12))))
        success=sum(covered);n=len(covered)
        ci=[float(beta.ppf(.025,success,n-success+1)) if success else 0.,
            float(beta.ppf(.975,success+1,n-success)) if success<n else 1.]
        cases.append({'scenario':scenario,'replications':n,'joint_coverage_count':success,
                      'joint_coverage':success/n,'coverage_binomial_95_interval':ci,
                      'zero_variance_contrasts_guarded':zero_guarded,
                      'ratio_bias_by_arm':dict(zip(ARMS,(means.mean(axis=0)-true_arm).tolist()))})
        print(scenario,success,'/',n,'joint coverage',flush=True)
    example=referee_counterexample()
    report={'scope':'Synthetic 15-arm-pair mean family under actual 22-block quota structure; independent conditional exchangeable assignment and fixed weighted baseline target. Not a proof of actual 25-objective endpoint-family coverage.',
            'seed':SEED,'diagnostic_multiplier_draws':DRAWS,'headline_multiplier_draws':99999,
            'quota_file_sha256':hashlib.sha256((ROOT/'output/assignment_probabilities.csv').read_bytes()).hexdigest(),
            'exact_referee_counterexample':example,'vectorized_vs_module_max_error':float(direct_error),
            'simulation_cases':cases,'all_implementation_checks_passed':bool(direct_error<1e-12),
            'coverage_certified':False}
    (ROOT/'output/blocked-validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print('Exact counterexample and independent implementation agreement verified; finite-block diagnostics recorded.')

if __name__=='__main__':main()
