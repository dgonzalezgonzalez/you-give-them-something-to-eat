"""All estimands and cluster influence functions for the budget-mixture comparison."""
from pathlib import Path
import json, platform, time
import numpy as np
import pandas as pd
import scipy
from scipy.stats import t as student_t

ROOT = Path(__file__).resolve().parents[1]
ARMS = ['Control','Gikuriro','Lower','Middle','Upper','Large']
TX = ['treat_GK','treat_GD_lower','treat_GD_mid','treat_GD_upper','treat_GD_huge']
SEED = 20260930
BOOT = 9999

def regress(df, y, base=None, weighting='survey', interactions=None):
    """WLS ANCOVA, CR1 village sandwich, G-1 t inference.

    Returned scores have a common 248-village index for joint multiplier inference.
    """
    keep = np.isfinite(y) & np.isfinite(df.samp_wgt) & (df.samp_wgt > 0)
    d = df.loc[keep]
    y = np.asarray(y)[keep]
    w = d.samp_wgt.to_numpy().copy()
    if weighting=='equal': w[:] = 1
    if weighting=='village':
        w /= d.groupby('vid').samp_wgt.transform('sum').to_numpy()
    columns = [np.ones(len(d)), *[d[k].to_numpy() for k in TX]]
    if base is not None:
        b = np.asarray(base)[keep].copy()
        missing = ~np.isfinite(b)
        global_mean=np.average(b[~missing],weights=w[~missing]) if (~missing).any() else 0.
        for group in d.block.unique():
            ix=(d.block.to_numpy()==group)
            valid=ix & ~missing
            b[ix & missing]=np.average(b[valid],weights=w[valid]) if valid.any() else global_mean
        if np.ptp(b)>1e-12: columns.append(b)
        if missing.any(): columns.append(missing.astype(float))
    block = pd.get_dummies(d.block,drop_first=True,dtype=float)
    columns += [block[k].to_numpy() for k in block]
    if interactions is not None:
        h=np.asarray(interactions)[keep]
        columns += [h,*[h*d[k].to_numpy() for k in TX]]
    X=np.column_stack(columns)
    rank=np.linalg.matrix_rank(X)
    if rank != X.shape[1]: raise ValueError('Rank deficient design')
    bread=np.linalg.inv(X.T@(w[:,None]*X))
    beta=bread@(X.T@(w*y))
    resid=y-X@beta
    row_scores=X*(w*resid)[:,None]
    groups=d.vid.astype(int).to_numpy()-1
    scores=np.zeros((248,X.shape[1]))
    np.add.at(scores,groups,row_scores)
    G=d.vid.nunique(); N=len(d); K=X.shape[1]
    correction=G/(G-1)*(N-1)/(N-K)
    influence=scores@bread*np.sqrt(correction)
    vcov=influence.T@influence
    return {'beta':beta,'vcov':vcov,'influence':influence,'N':N,'G':G,'K':K,'df':G-1}

def contrast(fit,c):
    c=np.asarray(c)
    b=float(c@fit['beta']); s=float(np.sqrt(max(c@fit['vcov']@c,0)))
    p=float(2*student_t.sf(abs(b/s),fit['df'])) if s>1e-12 else 1.
    crit=float(student_t.ppf(.975,fit['df']))
    return {'estimate':b,'se':s,'p':p,'lo':b-crit*s,'hi':b+crit*s,
            'N':fit['N'],'villages':fit['G']}

def policy_vertices(costs,budget):
    """Vertices of the cash/control simplex intersected with expected-cost cap."""
    names=['Control','Lower','Middle','Upper','Large']; vertices={}
    for a in names:
        if costs[a] <= budget:
            vertices[a]={a:1.}
    for i,a in enumerate(names):
        for b in names[i+1:]:
            ca,cb=costs[a],costs[b]
            if ca < budget < cb:
                q=(budget-ca)/(cb-ca)
                vertices[f'{a}+{b}']={a:1-q,b:q}
    return vertices

def policy_c(fit,policy):
    c=np.zeros(len(fit['beta']));c[1]=1.
    for a,q in policy.items():
        if a!='Control':c[ARMS.index(a)]-=q
    return c

def holm(p):
    p=np.asarray(p);order=np.argsort(p);adj=np.empty(len(p))
    adj[order]=np.minimum(1,np.maximum.accumulate((len(p)-np.arange(len(p)))*p[order]))
    return adj

def simultaneous(rows, influences):
    """Joint max-t Rademacher multiplier bands, shared cluster draws."""
    I=np.column_stack(influences);se=np.sqrt((I*I).sum(axis=0))
    active=se>1e-12
    Z=I[:,active]/se[active]
    rng=np.random.default_rng(SEED)
    maxima=[]
    for start in range(0,BOOT,400):
        B=min(400,BOOT-start)
        e=rng.choice([-1.,1.],size=(B,248))
        maxima.extend(np.max(np.abs(e@Z),axis=1))
    maxima=np.asarray(maxima)
    crit=float(np.quantile(maxima,.95,method='higher'))
    for row,s in zip(rows,se):
        row['sim_lo']=row['estimate']-crit*s;row['sim_hi']=row['estimate']+crit*s
        row['p_max_t']=float((1+(maxima>=abs(row['estimate']/s)).sum())/(BOOT+1)) if s>1e-12 else 1.
        row['joint_critical']=crit
    for row,p in zip(rows,holm([r['p'] for r in rows])): row['p_holm']=float(p)
    return rows

def main():
    begin=time.time()
    out=ROOT/'output';out.mkdir(exist_ok=True)
    d=pd.read_csv(ROOT/'data/input/households.csv')
    assert not d.duplicated(['hhid','round']).any()
    assert d.vid.nunique()==248
    assert d.groupby('vid')[TX].nunique().max().max()==1
    assert d.groupby('vid').block.nunique().max()==1
    d['arm']='Control'
    for a,k in zip(ARMS[1:],TX):d.loc[d[k]==1,'arm']=a
    baseline=d[(d['round']==1)&(d.eligible==1)].copy()
    end=d[(d['round']==2)&(d.eligible==1)&(d.sample_panel==1)].copy()
    assert baseline.hhid.nunique()==len(baseline)
    # Original preconstructed baseline variables supplement any absent panel rows.
    base=baseline.set_index('hhid')
    for k in ['dietarydiversity','consumption_asinh','productiveassets_asinh','savingsstock_asinh',
              'borrowingstock_asinh','health_knowledge','sanitation_practices','foodexpenditure','foodownconsumption']:
        end['base_'+k]=end.hhid.map(base[k])
    costsdf=pd.read_csv(ROOT/'data/input/costs.csv')
    cost_names=['Gikuriro','GD_Lower','GD_Mid','GD_Upper','GD_Large']
    costs={'Control':0.,**{a:float(costsdf.set_index('treatment').loc[b,'cost_eligible']) for a,b in zip(ARMS[1:],cost_names)}}
    budget=costs['Gikuriro'];vertices=policy_vertices(costs,budget)
    (out/'policies.json').write_text(json.dumps({'costs':costs,'budget':budget,'vertices':vertices},indent=2))
    valid=end.dietarydiversity.dropna()
    assert valid.between(0,12).all() and np.allclose(valid,np.rint(valid))
    attrs=[];desc=[]
    for a in ARMS:
        b=baseline[baseline.arm==a];e=end[end.arm==a]
        retained=b.hhid.isin(e.loc[e.dietarydiversity.notna(),'hhid'])
        attrs.append({'arm':a,'baseline_n':len(b),'endline_n':len(e),'diet_observed':int(retained.sum()),
                      'retention_weighted':float(np.average(retained,weights=b.samp_wgt))})
        for k in ['dietarydiversity','consumption_asinh','hhmember','hhfemale']:
            z=b[k].dropna();w=b.loc[z.index,'samp_wgt']
            desc.append({'arm':a,'variable':k,'n':len(z),'mean':float(np.average(z,weights=w)),
                         'sd':float(np.sqrt(np.average((z-np.average(z,weights=w))**2,weights=w)))})
    pd.DataFrame(attrs).to_csv(out/'attrition.csv',index=False)
    pd.DataFrame(desc).to_csv(out/'descriptives.csv',index=False)
    fits={};arm_rows=[];arm_ifs=[];policy_rows=[];ifs=[]
    outcomes={'diet_mean':(end.dietarydiversity.to_numpy(),end.base_dietarydiversity.to_numpy())}
    for z in [4,6,8]:
        outcomes[f'shortfall_{z}']=(-np.maximum(z-end.dietarydiversity,0).to_numpy()/z,
                                     -np.maximum(z-end.base_dietarydiversity,0).to_numpy()/z)
    outcomes['shortfall_sq_6']=(outcomes['shortfall_6'][0]**2*-1,outcomes['shortfall_6'][1]**2*-1)
    for z in range(1,13):
        y=np.where(end.dietarydiversity.notna(),(end.dietarydiversity>=z).astype(float),np.nan)
        b=np.where(end.base_dietarydiversity.notna(),(end.base_dietarydiversity>=z).astype(float),np.nan)
        outcomes[f'diet_atleast_{z}']=(y,b)
    for name,(y,b) in outcomes.items():
        fit=regress(end,y,b);fits[name]=fit
        for a in ARMS[1:]:
            c=np.zeros(len(fit['beta']));c[ARMS.index(a)]=1
            arm_rows.append({'outcome':name,'arm':a,**contrast(fit,c)})
            arm_ifs.append(fit['influence']@c)
        for label,policy in vertices.items():
            c=policy_c(fit,policy)
            policy_rows.append({'outcome':name,'policy':label,**contrast(fit,c)})
            ifs.append(fit['influence']@c)
    # One family includes every primary outcome and every feasible cash vertex.
    simultaneous(arm_rows+policy_rows,arm_ifs+ifs)
    pd.DataFrame(arm_rows).to_csv(out/'arm_effects.csv',index=False)
    pd.DataFrame(policy_rows).to_csv(out/'policy_effects.csv',index=False)
    secondary=[]
    for k in ['consumption_asinh','productiveassets_asinh','savingsstock_asinh','borrowingstock_asinh',
              'health_knowledge','sanitation_practices','foodexpenditure','foodownconsumption']:
        y=end[k].to_numpy();b=end['base_'+k].to_numpy()
        if k in ['foodexpenditure','foodownconsumption']:
            y=np.arcsinh(y);b=np.arcsinh(b)
        fit=regress(end,y,b)
        for a in ARMS[1:]:
            c=np.zeros(len(fit['beta']));c[ARMS.index(a)]=1
            secondary.append({'outcome':k,'arm':a,**contrast(fit,c)})
        for label,policy in vertices.items():
            secondary.append({'outcome':k,'arm':f'GK_minus_{label}',**contrast(fit,policy_c(fit,policy))})
    for row,p in zip(secondary,holm([r['p'] for r in secondary])):row['p_holm']=p
    pd.DataFrame(secondary).to_csv(out/'secondary.csv',index=False)
    robust=[]
    for spec,adjust,weight in [('unadjusted',False,'survey'),('equal_households',True,'equal'),('equal_villages',True,'village')]:
        for name in ['diet_mean','shortfall_6']:
            y,b=outcomes[name];fit=regress(end,y,b if adjust else None,weighting=weight)
            for label,policy in vertices.items():
                robust.append({'spec':spec,'outcome':name,'policy':label,**contrast(fit,policy_c(fit,policy))})
    for spec in ['source_score','complete_baseline']:
        sample=end.copy()
        if spec=='source_score':
            sample['dietarydiversity']=sample.diet_source
            sample['base_dietarydiversity']=sample.hhid.map(base.diet_source)
        else:sample=sample.loc[sample.base_dietarydiversity.notna()].copy()
        for name in ['diet_mean','shortfall_6']:
            y=sample.dietarydiversity.to_numpy();b=sample.base_dietarydiversity.to_numpy()
            if name=='shortfall_6':y=-np.maximum(6-y,0)/6;b=-np.maximum(6-b,0)/6
            fit=regress(sample,y,b)
            for label,policy in vertices.items():
                robust.append({'spec':spec,'outcome':name,'policy':label,**contrast(fit,policy_c(fit,policy))})
    pd.DataFrame(robust).to_csv(out/'robustness.csv',index=False)
    hetero=[]
    for split in ['dietarydiversity','consumption_asinh']:
        cutoff=float(base[split].median())
        sample=end.loc[end['base_'+split].notna()].copy()
        h=(sample['base_'+split]<cutoff).astype(float).to_numpy()
        fit=regress(sample,sample.dietarydiversity.to_numpy(),sample.base_dietarydiversity.to_numpy(),interactions=h)
        for a in ARMS[1:]:
            c=np.zeros(len(fit['beta']));c[-5+ARMS.index(a)-1]=1
            hetero.append({'split':split,'cutoff':cutoff,'arm':a,**contrast(fit,c)})
    for row,p in zip(hetero,holm([r['p'] for r in hetero])):row['p_holm']=p
    pd.DataFrame(hetero).to_csv(out/'heterogeneity.csv',index=False)
    foods=[]
    for k in [k for k in end if k.startswith('m9_')]:
        y=np.where(end[k].isin([0,1]),end[k],np.nan)
        b0=end.hhid.map(base[k]);b=np.where(b0.isin([0,1]),b0,np.nan)
        fit=regress(end,y,b)
        for a in ARMS[1:]:
            c=np.zeros(len(fit['beta']));c[ARMS.index(a)]=1
            foods.append({'food':k,'arm':a,**contrast(fit,c)})
    for row,p in zip(foods,holm([r['p'] for r in foods])):row['p_holm']=p
    pd.DataFrame(foods).to_csv(out/'food_groups.csv',index=False)
    # Bounds use full baseline sample, no monotonicity of attrition assumption.
    bounds=[]
    for name,z in [('diet_mean',None),('shortfall_6',6)]:
        low,high=(0.,12.) if z is None else (-1.,0.)
        means={}
        for a in ARMS:
            b=baseline[baseline.arm==a];e=end[end.arm==a].set_index('hhid')
            y=b.hhid.map(e.dietarydiversity)
            if z is not None:y=-np.maximum(z-y,0)/z
            means[a]=(float(np.average(y.fillna(low),weights=b.samp_wgt)),float(np.average(y.fillna(high),weights=b.samp_wgt)))
        for label,policy in vertices.items():
            bounds.append({'outcome':name,'policy':label,
                           'lo':means['Gikuriro'][0]-sum(q*means[a][1] for a,q in policy.items()),
                           'hi':means['Gikuriro'][1]-sum(q*means[a][0] for a,q in policy.items())})
    pd.DataFrame(bounds).to_csv(out/'attrition_bounds.csv',index=False)
    # Weighted empirical distributions for transparent raw CDF displays.
    distributions=[]
    for a in ARMS:
        e=end[(end.arm==a)&end.dietarydiversity.notna()]
        for z in range(13):
            distributions.append({'arm':a,'threshold':z,'cdf':float(np.average(e.dietarydiversity<=z,weights=e.samp_wgt))})
    pd.DataFrame(distributions).to_csv(out/'distributions.csv',index=False)
    balance=[]
    for k in ['dietarydiversity','consumption_asinh','hhmember','hhfemale','hhage','hh_head_schooling']:
        fit=regress(baseline,baseline[k].to_numpy())
        for a in ARMS[1:]:
            c=np.zeros(len(fit['beta']));c[ARMS.index(a)]=1
            balance.append({'variable':k,'arm':a,**contrast(fit,c)})
    for row,p in zip(balance,holm([r['p'] for r in balance])):row['p_holm']=p
    pd.DataFrame(balance).to_csv(out/'balance.csv',index=False)
    # Differential attrition is estimated on baseline eligibles, never survivors.
    retained=baseline.hhid.isin(end.loc[end.dietarydiversity.notna(),'hhid']).to_numpy(dtype=float)
    fit=regress(baseline,retained)
    ar=[]
    for a in ARMS[1:]:
        c=np.zeros(len(fit['beta']));c[ARMS.index(a)]=1
        ar.append({'arm':a,**contrast(fit,c)})
    for row,p in zip(ar,holm([r['p'] for r in ar])):row['p_holm']=p
    pd.DataFrame(ar).to_csv(out/'attrition_effects.csv',index=False)
    meta={'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,
          'scipy':scipy.__version__,'seed':SEED,'bootstrap_draws':BOOT,'baseline_eligible':len(baseline),
          'endline_eligible_panel':len(end),'blocks':int(d.block.nunique()),'villages':248,
          'seconds':time.time()-begin,'family_size':len(arm_rows)+len(policy_rows)}
    (out/'run_metadata.json').write_text(json.dumps(meta,indent=2))
    print(json.dumps(meta,indent=2))
    print(pd.DataFrame(policy_rows).query("outcome in ['diet_mean','shortfall_6']")[['outcome','policy','estimate','se','p','p_holm','sim_lo','sim_hi']].to_string(index=False))

if __name__=='__main__':main()
