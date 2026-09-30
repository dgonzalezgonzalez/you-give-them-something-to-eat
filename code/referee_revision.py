"""Exploratory analyses added after the genuine first referee report.

No new field observations. Positive-weight Hájek distributions explicitly use
block assignment probabilities. Endpoint uncertainty is cluster asymptotic,
not an exact finite-design or missing-at-random guarantee.
"""
from pathlib import Path
import itertools, json
import numpy as np
import pandas as pd
from scipy.stats import t
from estimate import ARMS, TX, policy_vertices, regress, contrast, policy_c, simultaneous, holm
from blocked_inference import hajek_block,bounded_hajek_outer

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'output'
REVISION_DRAWS=99999
GROUPS=[['cereals'],['tubers'],['vitaveg','leafyveg','otherveg'],['vitaafruits','otherfruits'],
        ['organmeat','fleshmeat'],['eggs'],['fish'],['legumes'],['milk'],['oils'],['sweets'],['spices']]

def score_interval(frame):
    lo=np.zeros(len(frame));hi=np.zeros(len(frame))
    for names in GROUPS:
        x=frame[['m9_'+k for k in names]]
        lo+=x.eq(1).any(axis=1).to_numpy()
        hi+=~x.eq(0).all(axis=1).to_numpy()
    return lo,hi

def objective(score,name):
    score=np.asarray(score)
    if name=='mean':return score
    k=int(name.split('_')[-1])
    if name.startswith('survival'):return (score>=k).astype(float)
    return -np.maximum(k-score,0)/k

def hajek(sample,values,assignment):
    """One distribution, shared block scores, and retained cross-arm covariance."""
    means,influence,_=hajek_block(sample,values,assignment,ARMS)
    return means,influence

def row_from(means,inf,c,**labels):
    df=inf.shape[0]-1
    b=float(c@means);u=inf@c;s=float(np.linalg.norm(u));critical=float(t.ppf(.975,df))
    row={**labels,'estimate':b,'se':s,'p':float(2*t.sf(abs(b/s),df)) if s>1e-12 else 1.,
         'lo':b-critical*s,'hi':b+critical*s,'inference_blocks':inf.shape[0],'pointwise_df':df}
    if s<=1e-12 and abs(c.sum())<1e-12:
        radius=(12. if labels.get('outcome')=='mean' else 1.)*np.maximum(c,0.).sum()
        row['lo'],row['hi']=-radius,radius
    return row,u

def policy_vector(q):return np.array([q.get(a,0.) for a in ARMS])

def main():
    d=pd.read_csv(ROOT/'data/input/households.csv')
    aux=pd.read_csv(ROOT/'data/input/revision_households.csv')
    d=d.merge(aux,on=['hhid','round'],suffixes=('','_source'),validate='one_to_one')
    d['arm']='Control'
    for a,k in zip(ARMS[1:],TX):d.loc[d[k]==1,'arm']=a
    villages=d.drop_duplicates('vid')
    quota=pd.crosstab(villages.block,villages.arm).reindex(columns=ARMS)
    probabilities=quota.div(quota.sum(axis=1),axis=0)
    design=quota.stack().rename('villages').reset_index().rename(columns={'level_1':'arm'})
    design['block_villages']=design.block.map(quota.sum(axis=1))
    design['probability']=design.villages/design.block_villages
    design.to_csv(OUT/'assignment_probabilities.csv',index=False)
    assignment={a:probabilities[a].to_dict() for a in ARMS}
    b=d[(d['round']==1)&(d.eligible==1)].copy()
    e=d[(d['round']==2)&(d.eligible==1)&(d.sample_panel==1)].copy()
    # Frame/count weights are verified separately; no invented tracking factor.
    discrepancy=np.max(np.abs(b.samp_wgt-b.nEligible/b.groupby('vid').hhid.transform('count')))
    assert discrepancy<1e-5
    baseline=b.set_index('hhid')
    full=b.drop(columns=['dietarydiversity',*[f'm9_{k}' for g in GROUPS for k in g]]).merge(
        e[['hhid','dietarydiversity',*[f'm9_{k}' for g in GROUPS for k in g]]],on='hhid',how='left',validate='one_to_one')
    lower,upper=score_interval(full)
    score=(lower+upper)/2;score[lower!=upper]=np.nan
    full['identified_diet']=score
    objects=['mean',*[f'survival_{k}' for k in range(1,13)],*[f'shortfall_{k}' for k in range(1,13)]]
    p=json.loads((OUT/'policies.json').read_text());vertices=p['vertices']
    allpol={'Gikuriro':{'Gikuriro':1.},**vertices}
    points=[];pointinf=[];bounds=[];boundinf=[];distributions=[];hajek_arm=[];pairrows=[];pairinf=[]
    fitted={};endpoint_fits={};finite_rows=[];finite_pairs=[]
    for name in objects:
        vals=objective(score,name);vals[~np.isfinite(score)]=np.nan
        mu,I=hajek(full,vals,assignment);fitted[name]=(mu,I)
        if name=='mean':
            pd.DataFrame(I,columns=ARMS,index=sorted(full.block.unique())).rename_axis('block').to_csv(OUT/'block_scores_mean.csv')
            pd.DataFrame(I.T@I,columns=ARMS,index=ARMS).rename_axis('arm').to_csv(OUT/'block_covariance_mean.csv')
        mlo,Ilo=hajek(full,objective(lower,name),assignment)
        mhi,Ihi=hajek(full,objective(upper,name),assignment)
        endpoint_fits[name]=(mlo,Ilo,mhi,Ihi)
        support_range=(0.,12.) if name=='mean' else ((0.,1.) if name.startswith('survival') else (-1.,0.))
        finite={}
        for scope,observed,family in [('identified_diets',vals,138),('lower_endpoint',objective(lower,name),276),('upper_endpoint',objective(upper,name),276)]:
            center,lc,uc,info=bounded_hajek_outer(full,observed,assignment,ARMS,full,support_range,multiplicity=family)
            finite[scope]=(lc,uc)
            for ai,a in enumerate(ARMS):
                finite_rows.append({'outcome':name,'arm':a,'scope':scope,'estimate':center[ai],
                                    'finite_lower':lc[ai],'finite_upper':uc[ai],'alpha':.05,
                                    'primitive_family_size':family})
        for ai,a in enumerate(ARMS[1:]):
            c=np.zeros(6);c[ai+1]=1;c[0]=-1
            rr,uu=row_from(mu,I,c,outcome=name,arm=a);hajek_arm.append(rr)
        for label,q in vertices.items():
            c=policy_vector({'Gikuriro':1.})-policy_vector(q)
            rr,uu=row_from(mu,I,c,outcome=name,policy=label);points.append(rr);pointinf.append(uu)
        for left,right in itertools.combinations(allpol,2):
            c=policy_vector(allpol[left])-policy_vector(allpol[right])
            cp=np.maximum(c,0.);cn=np.minimum(c,0.)
            for scope,(lc,uc) in [('identified_diets',finite['identified_diets']),
                                   ('weighted_baseline', (finite['lower_endpoint'][0],finite['upper_endpoint'][1]))]:
                finite_pairs.append({'outcome':name,'left':left,'right':right,'scope':scope,
                                     'finite_lower':float(cp@lc+cn@uc),'finite_upper':float(cp@uc+cn@lc),
                                     'alpha':.05})
            rr,uu=row_from(mu,I,c,outcome=name,left=left,right=right);pairrows.append(rr);pairinf.append(uu)
            pos=np.maximum(c,0);neg=np.minimum(c,0)
            for side,aa,bb,IA,IB in [('lower',mlo,mhi,Ilo,Ihi),('upper',mhi,mlo,Ihi,Ilo)]:
                r,u=row_from(aa*pos+bb*neg,IA*pos+IB*neg,np.ones(6),outcome=name,left=left,right=right,endpoint=side)
                bounds.append(r);boundinf.append(u)
    def canonical(name):return {'shortfall_1':'survival_1','shortfall_12':'mean'}.get(name,name)
    pointkeys=[(canonical(r['outcome']),r['policy']) for r in points]
    pairkeys=[(canonical(r['outcome']),r['left'],r['right']) for r in pairrows]
    boundkeys=[(canonical(r['outcome']),r['left'],r['right'],r['endpoint']) for r in bounds]
    def support(rows):
        limits=[]
        for row in rows:
            left='Gikuriro' if 'policy' in row else row['left']
            right=row.get('policy',row.get('right'))
            c=policy_vector(allpol[left])-policy_vector(allpol[right])
            radius=(12. if row['outcome']=='mean' else 1.)*np.maximum(c,0.).sum()
            limits.append((-radius,radius))
        return limits
    critical_diagnostics=[]
    for rr,ii,kk in [(points,pointinf,pointkeys),(pairrows,pairinf,pairkeys),(bounds,boundinf,boundkeys)]:
        simultaneous(rr,ii,kk,draws=REVISION_DRAWS,mc_upper=True,zero_bounds=support(rr),critical_diagnostics=critical_diagnostics)
    pd.DataFrame(critical_diagnostics).to_csv(OUT/'multiplier_quantile_sensitivity.csv',index=False)
    pd.DataFrame(points).to_csv(OUT/'hajek_policy_effects.csv',index=False)
    pd.DataFrame(finite_rows).to_csv(OUT/'finite_arm_regions.csv',index=False)
    pd.DataFrame(finite_pairs).to_csv(OUT/'finite_policy_regions.csv',index=False)
    pd.DataFrame(hajek_arm).to_csv(OUT/'hajek_arm_effects.csv',index=False)
    pairs=pd.DataFrame(pairrows);pairs.to_csv(OUT/'policy_pairwise.csv',index=False)
    bounded=pd.DataFrame(bounds);bounded.to_csv(OUT/'population_bounds.csv',index=False)
    # Coherent eCDFs, all-eligible endpoint distributions, and algebraic identities.
    for k in range(13):
        values=(score<=k).astype(float);values[~np.isfinite(score)]=np.nan
        cdf,_=hajek(full,values,assignment)
        cdf_lo,_=hajek(full,(upper<=k).astype(float),assignment)
        cdf_hi,_=hajek(full,(lower<=k).astype(float),assignment)
        for i,a in enumerate(ARMS):distributions.append({'arm':a,'threshold':k,'cdf':cdf[i],'cdf_lower':cdf_lo[i],'cdf_upper':cdf_hi[i]})
    pd.DataFrame(distributions).to_csv(OUT/'coherent_distributions.csv',index=False)
    # Regret is max over competitors; uniform pairwise bands cover selection.
    regrets=[]
    for name in ['mean','shortfall_6']:
        mu,_=fitted[name];values={a:float(policy_vector(q)@mu) for a,q in allpol.items()}
        for a in allpol:
            relevant=[]
            for r in pairs[pairs.outcome==name].itertuples():
                if r.right==a:relevant.append((r.estimate,r.sim_lo,r.sim_hi))
                if r.left==a:relevant.append((-r.estimate,-r.sim_hi,-r.sim_lo))
            lower_reg=max(0.,max(x[1] for x in relevant));upper_reg=max(0.,max(x[2] for x in relevant))
            # Population interval endpoints across all other policies, same bands.
            raw=[];conf=[];lowerconf=[]
            for r in bounded[bounded.outcome==name].itertuples():
                if r.right==a and r.endpoint=='upper':raw.append(r.estimate);conf.append(r.sim_hi)
                if r.left==a and r.endpoint=='lower':raw.append(-r.estimate);conf.append(-r.sim_lo)
                if r.right==a and r.endpoint=='lower':lowerconf.append(r.sim_lo)
                if r.left==a and r.endpoint=='upper':lowerconf.append(-r.sim_hi)
            regrets.append({'outcome':name,'policy':a,'fitted_value':values[a],
                            'fitted_regret':max(values.values())-values[a],
                            'regret_lower_95':lower_reg,'regret_upper_95':upper_reg,
                            'not_ruled_out_optimal_95':lower_reg<=1e-12,
                            'population_worstcase_regret':max(0.,max(raw)),
                            'population_regret_lower_95':max(0.,max(lowerconf)),
                            'population_not_ruled_out_optimal_95':max(0.,max(lowerconf))<=1e-12,
                            'population_regret_upper_95':max(0.,max(conf))})
    reg=pd.DataFrame(regrets);reg.to_csv(OUT/'policy_regret.csv',index=False)
    tolerances=[]
    for tolerance in [.25,.5,1.]:
        for r in reg[reg.outcome=='mean'].itertuples():
            tolerances.append({'tolerance_groups':tolerance,'policy':r.policy,
                               'observed_satisfies_exploratory_bound':r.regret_upper_95<=tolerance,
                               'weighted_baseline_satisfies_exploratory_bound':r.population_regret_upper_95<=tolerance,
                               'coverage_validated':False,'scope':'Illustrative block-region tolerance arithmetic, not a reliable finite-design certificate'})
    pd.DataFrame(tolerances).to_csv(OUT/'policy_tolerances.csv',index=False)
    # Explicit missing-mean sensitivity stays within each individual's observed interval.
    sensitivity=[]
    for fraction in np.linspace(0,1,11):
        vals=lower+fraction*(upper-lower);mu,_=hajek(full,vals,assignment)
        for label,q in vertices.items():
            sensitivity.append({'missing_interval_fraction':fraction,'policy':label,
                                'GK_minus_cash':float((policy_vector({'Gikuriro':1.})-policy_vector(q))@mu)})
    pd.DataFrame(sensitivity).to_csv(OUT/'missing_mean_sensitivity.csv',index=False)
    # Cost scenarios are assumptions, not estimated cost confidence intervals.
    scenarios=[]
    costframe=pd.read_csv(ROOT/'data/input/costs.csv').set_index('treatment')
    costlabels=dict(zip(ARMS[1:],['Gikuriro','GD_Lower','GD_Mid','GD_Upper','GD_Large']))
    anc=pd.read_csv(OUT/'arm_effects.csv');effects={'Control':0.,**anc[anc.outcome=='diet_mean'].set_index('arm').estimate.to_dict()}
    settings=[]
    for gf,cf in itertools.product([.75,.9,1.,1.1,1.25],repeat=2):
        cc={a:c*(gf if a=='Gikuriro' else cf) for a,c in p['costs'].items()};settings.append((f'relative_g{gf}_cash{cf}',cc))
    for takeup in [.6,.8,1.]:
        cc={'Control':0.}
        for a,label in costlabels.items():
            r=costframe.loc[label]
            cc[a]=float(r.cost_beneficiary*(1-r.share_averted+r.share_averted*takeup))
        settings.append((f'common_takeup_{takeup}',cc))
    for avert in [0.,.3,.6,1.]:
        cc=p['costs'].copy();r=costframe.loc['Gikuriro']
        cc['Gikuriro']=float(r.cost_beneficiary*(1-avert+avert*r.compliance_eligibles))
        settings.append((f'GK_avertable_share_{avert}',cc))
    (OUT/'cost_inputs.json').write_text(json.dumps({label:{'costs':cc,'budget':cc['Gikuriro']} for label,cc in settings},indent=2),encoding='utf8')
    for label,cc in settings:
        vv=policy_vertices(cc,cc['Gikuriro'])
        gain={a:sum(effects[k]*q for k,q in mix.items()) for a,mix in vv.items()}
        best=max(gain,key=gain.get)
        for name,mix in vv.items():scenarios.append({'scenario':label,'budget':cc['Gikuriro'],'policy':name,
            'cash_gain':gain[name],'GK_minus_cash':effects['Gikuriro']-gain[name],'fitted_best':name==best,
            'cost':sum(cc[k]*q for k,q in mix.items()),'large_share':mix.get('Large',0.)})
    pd.DataFrame(scenarios).to_csv(OUT/'cost_scenarios.csv',index=False)
    # Closest original Table 3, corrected data, fixed source-selected controls.
    ladder=[]
    sourcecontrols=['Ldietarydiversity','dietarydiversity_R1','Lhh_wealth_asinh','Lvill_eligible_ratio','Lsavingsstock_asinh3','Lconsumpti_x_Lproductiv','Lconsumpti_x_Lselfcostd']
    for label,pool,controls,reconstruct in [('source_pooled',True,True,False),('source_split',False,True,False),
                                          ('lag_only_source',False,False,False),('lag_only_integer',False,False,True)]:
        y=e.dietarydiversity.to_numpy() if reconstruct else e.diet_source.to_numpy()
        X=[np.ones(len(e)),e.treat_GK.to_numpy()]
        X += [e[TX[1:4]].sum(axis=1).to_numpy(),e.treat_GD_huge.to_numpy()] if pool else [e[k].to_numpy() for k in TX[1:]]
        keys=sourcecontrols if controls else ['dietarydiversity_R1']
        X += [e[k].to_numpy() for k in keys]
        block=pd.get_dummies(e.block,drop_first=True,dtype=float);X += [block[k].to_numpy() for k in block]
        X=np.column_stack(X);keep=np.isfinite(y)&np.isfinite(X).all(axis=1)
        X=X[keep];y=y[keep];w=e.loc[keep,'samp_wgt'].to_numpy()
        selected=[]
        for i in range(X.shape[1]):
            if np.linalg.matrix_rank(X[:,selected+[i]])>len(selected):selected.append(i)
        X=X[:,selected];bread=np.linalg.inv(X.T@(w[:,None]*X))
        beta=bread@(X.T@(w*y));u=np.zeros((248,len(beta)))
        np.add.at(u,e.loc[keep,'vid'].to_numpy(dtype=int)-1,X*(w*(y-X@beta))[:,None]);I=u@bread*np.sqrt(248/247*(len(y)-1)/(len(y)-len(beta)))
        for a,ix in [('Gikuriro',1),('Large',3 if pool else 5)]:ladder.append({'spec':label,'arm':a,'estimate':beta[ix],'se':np.linalg.norm(I[:,ix]),'N':len(y),'rank':len(beta)})
    pd.DataFrame(ladder).to_csv(OUT/'original_crosswalk.csv',index=False)
    # Available ineligible households: assignment effects, no baseline-eligibility retargeting.
    spill=[]
    be=d[(d['round']==1)&(d.eligible==0)].set_index('hhid')
    ee=d[(d['round']==2)&(d.eligible==0)&(d.sample_panel==1)].copy()
    for k in ['dietarydiversity','consumption_asinh','savingsstock_asinh']:
        fit=regress(ee,ee[k].to_numpy(),ee.hhid.map(be[k]).to_numpy())
        for a in ARMS[1:]:
            c=np.zeros(len(fit['beta']));c[ARMS.index(a)]=1
            spill.append({'outcome':k,'arm':a,**contrast(fit,c)})
    for r,pp in zip(spill,holm([r['p'] for r in spill])):r['p_holm']=pp
    pd.DataFrame(spill).to_csv(OUT/'ineligible_effects.csv',index=False)
    # Child outcomes retain original eligibility/age construction, source scores.
    children=pd.read_csv(ROOT/'data/input/children.csv')
    ce=children[(children['round']==2)&(children.eligible==1)&(children.anthro_shouldbe==1)].copy()
    tx=d.drop_duplicates('hhid').set_index('hhid')
    for k in TX:ce[k]=ce.hhid.map(tx[k])
    childrows=[]
    for k in ['haz06','waz06','muacz']:
        fit=regress(ce,ce[k].to_numpy(),ce[k+'_R1'].to_numpy())
        for a in ARMS[1:]:
            c=np.zeros(len(fit['beta']));c[ARMS.index(a)]=1
            childrows.append({'outcome':k,'arm':a,**contrast(fit,c)})
    for r,pp in zip(childrows,holm([r['p'] for r in childrows])):r['p_holm']=pp
    pd.DataFrame(childrows).to_csv(OUT/'child_effects.csv',index=False)
    # Counts include separately fully identified partial modules.
    counts=[]
    for a in ARMS:
        ix=full.arm==a
        counts.append({'arm':a,'baseline_N':int(ix.sum()),'identified_diets':int(np.isfinite(score[ix]).sum()),
                       'partially_identified':int(((lower<upper)&(upper-lower<12)&ix).sum()),
                       'unobserved':int(((upper-lower==12)&ix).sum())})
    pd.DataFrame(counts).to_csv(OUT/'diet_observation_intervals.csv',index=False)
    metadata={'population':'baseline eligible households, source sampling expansion weights; no invented intensive-tracking factor',
              'assignment_adjusted':True,'max_frame_weight_discrepancy':float(discrepancy),
              'identified_diet_N':int(np.isfinite(score).sum()),'baseline_N':len(full),
              'point_family_size':len(set(pointkeys)),'pair_family_size':len(set(pairkeys)),
              'endpoint_family_size':len(set(boundkeys)),
              'display_point_rows':len(points),'display_pair_rows':len(pairs),'display_endpoint_rows':len(bounds),
              'fitted_mean_best':reg[reg.outcome=='mean'].sort_values('fitted_regret').iloc[0].policy,
              'inference_blocks':int(full.block.nunique()),'bootstrap_draws':REVISION_DRAWS,
              'zero_variance_rows_guarded':sum(r['zero_variance_guard'] for r in points+pairrows+bounds),
              'assignment_probability_scope':'Conditional within-block exchangeability given realized counts; original randomization program unavailable',
              'mc_critical_scope':'99% Monte Carlo upper order statistic for the 95% multiplier quantile, within each declared family',
              'inference':'Exploratory independent-block ratio max-t; finite-block stress undercoverage documented. Separate finite conditional-assignment outer regions supplied.',
              'finite_region_scope':'Fixed weighted released baseline sample under independent, conditional exchangeable quota assignment; not unconditional proof of full-frame sampling representativeness'}
    (OUT/'revision_metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf8')
    print(json.dumps(metadata,indent=2));print(reg.to_string(index=False))

if __name__=='__main__':main()
