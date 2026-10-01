"""Author-side independent least-squares and block-score checks.

Does not import the new estimator/comparison functions. Implementation checks
do not validate nominal sampling coverage or establish historical replication.
"""
from pathlib import Path
import json,itertools
from fractions import Fraction
import numpy as np
import pandas as pd
from scipy.stats import t

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'
ARMS=['Control','Gikuriro','Lower','Middle','Upper','Large']
TX=['treat_GK','treat_GD_lower','treat_GD_mid','treat_GD_upper','treat_GD_huge']
GROUPS=[['cereals'],['tubers'],['vitaveg','leafyveg','otherveg'],['vitaafruits','otherfruits'],
        ['organmeat','fleshmeat'],['eggs'],['fish'],['legumes'],['milk'],['oils'],['sweets'],['spices']]
checks={}
def check(name,value):
    checks[name]=bool(value)
    if not value:raise AssertionError(name)

def direct_wls(d,y,columns):
    X=np.column_stack(columns);good=np.isfinite(X).all(axis=1)&np.isfinite(y)
    X=X[good];y=y[good];w=d.loc[good,'samp_wgt'].to_numpy()
    # Weighted SVD on scaled columns handles duplicated source lag columns.
    scale=np.linalg.norm(np.sqrt(w)[:,None]*X,axis=0);scale[scale==0]=1
    Z=X/scale; beta_scaled,_,rank,_=np.linalg.lstsq(np.sqrt(w)[:,None]*Z,np.sqrt(w)*y,rcond=None)
    beta=beta_scaled/scale; residual=y-X@beta
    bread=np.linalg.pinv(np.sqrt(w)[:,None]*Z) / np.sqrt(w)[None,:]
    # The derivative of beta with respect to y is (X'WX)^+ X'W;
    # each cluster's residual-weighted derivative supplies its score.
    derivative=bread*w[None,:]/scale[:,None]
    influence=np.zeros((248,len(beta)))
    for village in sorted(d.loc[good,'vid'].unique()):
        ix=d.loc[good,'vid'].eq(village).to_numpy()
        influence[int(village)-1]=derivative[:,ix]@residual[ix]
    G=d.loc[good,'vid'].nunique();N=len(y)
    influence*=np.sqrt(G/(G-1)*(N-1)/(N-rank))
    return beta,influence,good

def main():
    core=pd.read_csv(ROOT/'data/input/households.csv');aux=pd.read_csv(ROOT/'data/input/revision_households.csv')
    d=core.merge(aux[['hhid','round',*[k for k in aux if k not in core]]],on=['hhid','round'],validate='one_to_one')
    end=d[d['round'].eq(2)&d.sample_panel.eq(1)].copy()
    lower=np.zeros(len(end));upper=np.zeros(len(end))
    for group in GROUPS:
        x=end[['m9_'+k for k in group]];lower+=x.eq(1).any(axis=1).to_numpy();upper+=(~x.eq(0).all(axis=1)).to_numpy()
    point=(lower+upper)/2;point[lower!=upper]=np.nan
    pairs=pd.read_csv(OUT/'community_cash_pairs.csv');cross=pd.read_csv(OUT/'community_cross_stratum.csv')
    decision=json.loads((OUT/'community-decision.json').read_text());tau=decision['baseline_eligible_weight_share']
    covariance=pd.read_csv(OUT/'community_joint_village_covariance.csv')
    for control,estimator in [(False,'block_wls'),(True,'baseline_ancova')]:
        means={};scores={};dfs=[]
        for g in [0,1]:
            mask=end.eligible.eq(g).to_numpy();sample=end[mask];y=point[mask]
            columns=[np.ones(len(sample)),*[sample[k].to_numpy() for k in TX]]
            if control:
                b=sample.dietarydiversity_R1.to_numpy().copy()
                # The analysis's lag control is reconstructed baseline diet.
                base=core[core['round'].eq(1)].set_index('hhid')
                b=sample.hhid.map(base.dietarydiversity).to_numpy().copy();missing=~np.isfinite(b)
                valid=~missing&np.isfinite(y);w=sample.samp_wgt.to_numpy()
                global_mean=np.average(b[valid],weights=w[valid]) if valid.any() else 0.
                for block in sample.block.unique():
                    ix=sample.block.eq(block).to_numpy();v=ix&valid
                    b[ix&missing]=np.average(b[v],weights=w[v]) if v.any() else global_mean
                columns.append(b)
                if (missing&np.isfinite(y)).any():columns.append(missing.astype(float))
            # The regression drops unobserved y before constructing block levels.
            blocks=pd.get_dummies(sample.loc[np.isfinite(y),'block'],drop_first=True,dtype=float)
            for block in blocks.columns:columns.append(sample.block.eq(block).to_numpy(float))
            beta,I,good=direct_wls(sample,y,columns)
            means[g]=np.r_[0.,beta[1:6]];scores[g]=np.column_stack([np.zeros(248),I[:,1:6]])
            dfs.append(sample.loc[good,'vid'].nunique()-1)
        C=np.column_stack([scores[1],scores[0]]).T@np.column_stack([scores[1],scores[0]])
        stored=covariance[covariance.estimator.eq(estimator)].covariance.to_numpy().reshape(12,12)
        check(estimator+'_joint_covariance',np.allclose(C,stored,rtol=1e-8,atol=1e-10))
        for index,row in cross[cross.estimator.eq(estimator)].iterrows():
            m=decision['menus'][row.cost_convention];v=np.array([float(Fraction(z)) for z in m['vertices'][m['labels'].index(row.policy)]])
            c=np.eye(6)[1]-v;value=c@(means[0]-means[1]);se=np.linalg.norm((scores[0]-scores[1])@c)
            check('cross_'+str(index),np.isclose(value,row.estimate,atol=1e-9)&np.isclose(se,row.se,atol=1e-9))
        for index,row in pairs[pairs.estimator.eq(estimator)].iterrows():
            m=decision['menus'][row.cost_convention]
            a=np.array([float(Fraction(z)) for z in m['vertices'][m['labels'].index(row.left)]])
            b=np.array([float(Fraction(z)) for z in m['vertices'][m['labels'].index(row.right)]])
            we,wn={'eligible':(1,0),'ineligible':(0,1),'baseline_weight_aggregate':(tau,1-tau),'ineligible_minus_eligible':(-1,1)}[row.population]
            value=(a-b)@(we*means[1]+wn*means[0]);se=np.linalg.norm((we*scores[1]+wn*scores[0])@(a-b))
            check('cash_'+str(index),np.isclose(value,row.estimate,atol=1e-9)&np.isclose(se,row.se,atol=1e-9))
    # Full source-control pooled estimator, recovered from a separate scaled SVD.
    controls=json.loads((OUT/'population-crosswalk.json').read_text())['source_controls']
    blocks=pd.get_dummies(end.block,drop_first=True,dtype=float)
    X=[np.ones(len(end)),end.treat_GK.to_numpy(),end[TX[1:4]].sum(axis=1).to_numpy(),end.treat_GD_huge.to_numpy(),
       *[end[k].to_numpy() for k in controls],end.eligible.to_numpy(),*[blocks[k].to_numpy() for k in blocks]]
    beta,I,good=direct_wls(end,end.diet_source.to_numpy(),X)
    bridge=pd.read_csv(OUT/'population_parent_crosswalk.csv')
    for arm,i in [('Gikuriro',1),('Lower',2),('Large',3)]:
        r=bridge[bridge.stage.eq('source_pooled_controls')&bridge.arm.eq(arm)].iloc[0]
        check('pooled_source_'+arm,np.isclose(beta[i],r.effect,atol=1e-8)&np.isclose(np.linalg.norm(I[:,i]),r.village_se,atol=1e-8)&(good.sum()==r.N))
    for method in ['mean_boxes','quota_mean_boxes']:
        check(method+'_equal_five_feasible',all(z['lower']<=5<=z['upper'] for z in decision[method]))
    # Independently reconstruct block-probability ratios on fixed baseline IDs.
    foods=['m9_'+k for group in GROUPS for k in group]
    baseline=core[core['round'].eq(1)].drop(columns=foods)
    full=baseline.merge(core[core['round'].eq(2)][['hhid',*foods]],on='hhid',how='left',validate='one_to_one')
    lower=np.zeros(len(full));upper=np.zeros(len(full))
    for group in GROUPS:
        x=full[['m9_'+k for k in group]];lower+=x.eq(1).any(axis=1).to_numpy();upper+=(~x.eq(0).all(axis=1)).to_numpy()
    y=(lower+upper)/2;y[lower!=upper]=np.nan
    full['arm']='Control'
    for a,k in zip(ARMS[1:],TX):full.loc[full[k].eq(1),'arm']=a
    v=full.drop_duplicates('vid');quotas=pd.crosstab(v.block,v.arm).reindex(columns=ARMS)
    probabilities=quotas.div(quotas.sum(axis=1),axis=0);blocks=sorted(full.block.unique())
    means={};scores={}
    for g in [0,1]:
        means[g]=np.zeros(6);scores[g]=np.zeros((len(blocks),6))
        for i,a in enumerate(ARMS):
            ix=full.eligible.eq(g)&full.arm.eq(a)&np.isfinite(y)
            w=full.loc[ix,'samp_wgt']/full.loc[ix,'block'].map(probabilities[a])
            means[g][i]=np.average(y[ix],weights=w)
            residual=w.to_numpy()*(y[ix]-means[g][i])/w.sum()
            sums=pd.Series(residual,index=full.loc[ix,'block'].to_numpy()).groupby(level=0).sum().reindex(blocks,fill_value=0)
            scores[g][:,i]=sums.to_numpy()*np.sqrt(len(blocks)/(len(blocks)-1))
    for index,row in cross[cross.estimator.eq('assignment_weighted_ratios')].iterrows():
        m=decision['menus'][row.cost_convention];v=np.array([float(Fraction(z)) for z in m['vertices'][m['labels'].index(row.policy)]])
        c=np.eye(6)[1]-v;value=c@(means[0]-means[1]);se=np.linalg.norm((scores[0]-scores[1])@c)
        check('ratio_cross_'+str(index),np.isclose(value,row.estimate,atol=1e-10)&np.isclose(se,row.se,atol=1e-10))
    for index,row in pairs[pairs.estimator.eq('assignment_weighted_ratios')].iterrows():
        m=decision['menus'][row.cost_convention]
        a=np.array([float(Fraction(z)) for z in m['vertices'][m['labels'].index(row.left)]])
        b=np.array([float(Fraction(z)) for z in m['vertices'][m['labels'].index(row.right)]])
        we,wn={'eligible':(1,0),'ineligible':(0,1),'baseline_weight_aggregate':(tau,1-tau),'ineligible_minus_eligible':(-1,1)}[row.population]
        value=(a-b)@(we*means[1]+wn*means[0]);se=np.linalg.norm((we*scores[1]+wn*scores[0])@(a-b))
        check('ratio_cash_'+str(index),np.isclose(value,row.estimate,atol=1e-10)&np.isclose(se,row.se,atol=1e-10))
    cost=pd.read_csv(OUT/'population_cost_bridge.csv')
    check('cash_population_cost_rounding',cost.loc[cost.arm.ne('Gikuriro'),'population_formula_residual'].abs().max()<1e-5)
    check('gikuriro_population_residual_retained',1.48<cost.loc[cost.arm.eq('Gikuriro'),'population_formula_residual'].iloc[0]<1.49)
    check('families_complete',len(cross)==48 and len(pairs)==672)
    for frame in [cross,pairs]:
        for (estimator,size),group in frame.groupby(['estimator','family_size']):
            # Regression families combine the two specifications.
            family=frame[frame.family_size.eq(size)]
            p=family.p.to_numpy();order=np.argsort(p);adj=np.empty(len(p))
            adj[order]=np.minimum(1,np.maximum.accumulate((len(p)-np.arange(len(p)))*p[order]))
            check('holm_'+str(len(frame))+'_'+str(size),np.allclose(adj,family.p_holm,atol=1e-12))
    report={'all_passed':all(checks.values()),'checks':checks,'scope':'Independent author-side scaled-SVD least squares, residual derivatives and joint covariance replay for all new village-regression comparisons and the pooled source estimator; separate fixed-baseline block-ratio reconstruction for all new ratio comparisons. Finite-box tie witness, full family counts, Holm and cost residuals checked. No empirical sampling-coverage validation, historical program replay or referee audit receipt.'}
    (OUT/'population-revision-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
    print('Population revision author checks passed:',len(checks))

if __name__=='__main__':main()
