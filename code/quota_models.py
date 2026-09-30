"""Conditional full-baseline model with outward moment/observable/logical constants."""
from pathlib import Path
import sys,json
import numpy as np,pandas as pd
from scipy.optimize import minimize
from scipy.special import logsumexp
from quota_arithmetic import observed_residual_constants,outward_affine_tests
from quota_arithmetic import I,dot,mixture_upper
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'code'))
from estimate import ARMS,TX
from referee_revision import GROUPS,score_interval,objective

def build_models(moment_rows):
    names=['mean',*[f'survival_{k}' for k in range(1,13)],*[f'shortfall_{k}' for k in range(2,12)]]
    raw=np.array([objective(np.arange(13),name) for name in names]);zz=(raw-raw.min(axis=1)[:,None])/np.ptp(raw,axis=1)[:,None]
    d=pd.read_csv(root/'data/input/households.csv');d['arm']='Control'
    for arm,tx in zip(ARMS[1:],TX):d.loc[d[tx]==1,'arm']=arm
    b=d[(d['round']==1)&(d.eligible==1)].copy();e=d[(d['round']==2)&(d.eligible==1)&(d.sample_panel==1)]
    foods=[f'm9_{k}' for g in GROUPS for k in g]
    full=b.drop(columns=foods).merge(e[['hhid',*foods]],on='hhid',how='left',validate='one_to_one')
    lo,hi=score_interval(full);w=full.samp_wgt.to_numpy();W=sum((I(x) for x in w),I(0))
    design=pd.read_csv(root/'output/assignment_probabilities.csv');moments={x['arm']:x for x in moment_rows}
    models=[]
    for arm in ARMS:
        assigned=full.arm.eq(arm).to_numpy();ds=design[design.arm==arm].set_index('block')
        ns=full.loc[assigned,'block'].map(ds.block_villages).to_numpy();ks=full.loc[assigned,'block'].map(ds.villages).to_numpy()
        lam=moments[arm]['fixed_lambda_normalized'];B=moments[arm]['certified_upper_log_normalizer'];C=[];inter=[];AA=[];bb=[]
        for z in zz:
            cc=observed_residual_constants(w[assigned],ns,ks,lo[assigned],hi[assigned],z)
            rows,constants=outward_affine_tests(cc,z,lam,B);C.extend(rows);inter.extend(constants)
            # Stored normalized score functions are fixed bounded functions.
            # Deterministic logical constraints use the same exact entries.
            L=dot(w[assigned],z[lo[assigned].astype(int)])/W
            H=(dot(w[assigned],z[hi[assigned].astype(int)])+sum((I(x) for x in w[~assigned]),I(0)))/W
            AA.extend([z,-z]);bb.extend([H.upper_float(),-max(0.,L.lower_float())])
        C=np.array(C);inter=np.array(inter);AA=np.array(AA);bb=np.array(bb)
        floor=np.array([max(0.,(sum((I(x) for x in w[assigned&(lo==hi)&(lo==s)]),I(0))/W).lower_float()) for s in range(13)])
        seed=floor+(1-floor.sum())/13
        def function(p,C=C,inter=inter):
            values=C@p+inter;logF=float(logsumexp(values));gradient=np.exp(values-logF)@C
            return logF,gradient
        constraints=[{'type':'eq','fun':lambda p:p.sum()-1,'jac':lambda p:np.ones(13)},
                     {'type':'ineq','fun':lambda p,A=AA,b=bb:b-A@p,'jac':lambda p,A=AA:-A}]
        fit=minimize(lambda p:function(p)[0],seed,jac=lambda p:function(p)[1],method='SLSQP',bounds=[(f,1.) for f in floor],constraints=constraints,options={'maxiter':1000,'ftol':1e-12})
        residual=max(abs(fit.x.sum()-1),float(np.maximum(AA@fit.x-bb,0).max()),float(np.maximum(floor-fit.x,0).max()))
        if residual>1e-7:raise ValueError('Logical candidate infeasible')
        models.append({'arm':arm,'C':C,'intercept':inter,'A':AA,'b':bb,'floor':floor,'seed':fit.x,'function':function,'lambda':lam,'normalizer':B,'seed_residual':residual})
    if mixture_upper(models,[m['seed'] for m in models])>=5520:raise ValueError('No interior mixture seed')
    return models,names
