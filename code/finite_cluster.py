"""CR2/Satterthwaite and leave-out sensitivity for the original WLS model.

All block indicators are explicit. Whitening uses an inverse-sampling-weight
working error covariance. This is a working-model small-sample correction,
not a sharp-null permutation or exact design guarantee.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.stats import t
from estimate import ARMS,TX,regress,contrast,policy_c

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'

def cr2_fit(d,y,base):
    keep=np.isfinite(y);d=d.loc[keep].copy();y=np.asarray(y)[keep];base=np.asarray(base)[keep].copy()
    w=d.samp_wgt.to_numpy();missing=~np.isfinite(base)
    globalmean=np.average(base[~missing],weights=w[~missing])
    for block in d.block.unique():
        ix=d.block.to_numpy()==block;valid=ix&~missing
        base[ix&missing]=np.average(base[valid],weights=w[valid]) if valid.any() else globalmean
    X=[np.ones(len(d)),*[d[k].to_numpy() for k in TX],base]
    if missing.any():X.append(missing.astype(float))
    block=pd.get_dummies(d.block,drop_first=True,dtype=float);X += [block[k].to_numpy() for k in block]
    X=np.column_stack(X)*np.sqrt(w)[:,None];y=y*np.sqrt(w)
    B=np.linalg.inv(X.T@X);beta=B@(X.T@y);resid=y-X@beta
    parts=[];influence=np.zeros((248,X.shape[1]));leverage=[]
    for vid,ix in d.groupby('vid').indices.items():
        Xg=X[ix];H=Xg@B@Xg.T
        lam,U=np.linalg.eigh(np.eye(len(ix))-H)
        assert lam.min()>1e-10,'Singular CR2 cluster residual covariance'
        A=(U/np.sqrt(lam))@U.T
        influence[int(vid)-1]=(Xg.T@(A@resid[ix]))@B
        parts.append((ix,Xg,A))
        leverage.append({'vid':vid,'arm':d.iloc[ix[0]].arm,'N':len(ix),'hat_trace':np.trace(H),
                         'max_hat_eigenvalue':1-lam.min()})
    return {'beta':beta,'influence':influence,'B':B,'X':X,'parts':parts,'leverage':leverage,'N':len(d),'G':d.vid.nunique()}

def cr2_contrast(f,c):
    c=np.asarray(c);v=f['B']@c;XV=[];norms=[]
    for ix,Xg,A in f['parts']:
        u=A@(Xg@v);XV.append(Xg.T@u);norms.append(u@u)
    XV=np.column_stack(XV)
    gram=np.diag(norms)-XV.T@f['B']@XV
    trace=np.trace(gram);df=float(trace**2/(gram*gram).sum())
    # Under the stated working model CR2 has the exact sandwich expectation.
    assert np.isclose(trace,c@f['B']@c,rtol=1e-8,atol=1e-12)
    b=float(c@f['beta']);u=f['influence']@c;se=float(np.linalg.norm(u))
    shares=u*u/(u@u)
    return {'estimate':b,'se_cr2':se,'df_satterthwaite':df,'p_cr2':float(2*t.sf(abs(b/se),df)),
            'lo_cr2':b-t.ppf(.975,df)*se,'hi_cr2':b+t.ppf(.975,df)*se,
            'effective_score_clusters':float(1/(shares@shares)),'largest_variance_share':float(shares.max()),
            'N':f['N'],'villages':f['G']}

def main():
    d=pd.read_csv(ROOT/'data/input/households.csv');d['arm']='Control'
    for a,k in zip(ARMS[1:],TX):d.loc[d[k]==1,'arm']=a
    base=d[(d['round']==1)&(d.eligible==1)].set_index('hhid')
    e=d[(d['round']==2)&(d.eligible==1)&(d.sample_panel==1)].copy()
    e['base']=e.hhid.map(base.dietarydiversity)
    policies=json.loads((OUT/'policies.json').read_text())['vertices']
    rows=[];loo=[];leverage=[];concentration=[]
    for a in ARMS:
        s=e[(e.arm==a)&e.dietarydiversity.notna()];wg=s.groupby('vid').samp_wgt.sum().to_numpy()
        concentration.append({'arm':a,'villages':len(wg),'effective_weight_villages':wg.sum()**2/(wg@wg),
                              'max_village_weight_share':wg.max()/wg.sum(),'households':len(s)})
    for name in ['diet_mean','shortfall_6']:
        y=e.dietarydiversity.to_numpy();b=e['base'].to_numpy()
        if name=='shortfall_6':y=-np.maximum(6-y,0)/6;b=-np.maximum(6-b,0)/6
        f=cr2_fit(e,y,b)
        if name=='diet_mean':leverage=f['leverage']
        for a in ARMS[1:]:
            c=np.zeros(len(f['beta']));c[ARMS.index(a)]=1
            rows.append({'outcome':name,'comparison':a,**cr2_contrast(f,c)})
        for label,q in policies.items():rows.append({'outcome':name,'comparison':'GK_minus_'+label,**cr2_contrast(f,policy_c(f,q))})
        for kind in ['vid','block']:
            for removed in sorted(e[kind].unique()):
                keep=(e[kind]!=removed).to_numpy();s=e.loc[keep]
                fit=regress(s,y[keep],b[keep])
                for label,q in policies.items():loo.append({'outcome':name,'drop_unit':kind,'dropped':removed,'policy':label,
                                                            **contrast(fit,policy_c(fit,q))})
    pd.DataFrame(rows).to_csv(OUT/'cr2_sensitivity.csv',index=False)
    pd.DataFrame(loo).to_csv(OUT/'leave_out_sensitivity.csv',index=False)
    pd.DataFrame(leverage).to_csv(OUT/'cluster_leverage.csv',index=False)
    pd.DataFrame(concentration).to_csv(OUT/'weight_concentration.csv',index=False)
    print('CR2 working-model expectation identities verified; leave-out fits:',len(loo))
    print(pd.DataFrame(rows).query("outcome=='diet_mean'").to_string(index=False))

if __name__=='__main__':main()
