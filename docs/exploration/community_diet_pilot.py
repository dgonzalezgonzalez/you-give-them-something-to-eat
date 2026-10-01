from pathlib import Path
import sys,json
import numpy as np,pandas as pd
r=Path(__file__).resolve().parents[2];sys.path.insert(0,str(r/'code'))
from estimate import ARMS,TX,policy_vertices
from referee_revision import GROUPS,score_interval,policy_vector
from blocked_inference import hajek_block
d=pd.read_csv(r/'data/input/households.csv');aux=pd.read_csv(r/'data/input/revision_households.csv')
d=d.merge(aux[['hhid','round','nEligible','nIneligible']],on=['hhid','round'],validate='one_to_one')
d['arm']='Control'
for a,t in zip(ARMS[1:],TX):d.loc[d[t].eq(1),'arm']=a
b=d[d['round'].eq(1)].copy();food=['m9_'+k for g in GROUPS for k in g]
e=d[d['round'].eq(2)][['hhid',*food]]
full=b.drop(columns=food).merge(e,on='hhid',how='left',validate='one_to_one')
lo,hi=score_interval(full);point=(lo+hi)/2;point[lo!=hi]=np.nan
villages=d.drop_duplicates('vid');q=pd.crosstab(villages.block,villages.arm).reindex(columns=ARMS);prob=q.div(q.sum(axis=1),axis=0)
assignment={a:prob[a].to_dict() for a in ARMS}
W=b.groupby('eligible').samp_wgt.sum();shares=W/W.sum()
diagnostics=[]
for g in [0,1]:
    s=b[b.eligible.eq(g)];field='nEligible' if g else 'nIneligible'
    reference=s[field]/s.groupby('vid').hhid.transform('count')
    diagnostics.append({'eligible':g,'baseline_n':len(s),'baseline_weight_sum':float(W[g]),'population_share_from_baseline_weights':float(shares[g]),'max_abs_weight_frame_discrepancy':float(abs(s.samp_wgt-reference).max()),'missing_frame_counts':int(reference.isna().sum())})
moments={};influence={};accounting=[]
for g in [0,1]:
    selected=full.eligible.eq(g).to_numpy();s=full[selected].copy()
    for name,values in [('identified',point),('lower_endpoint',lo),('upper_endpoint',hi)]:
        mu,I,info=hajek_block(s,values[selected],assignment,ARMS);moments[g,name]=mu;influence[g,name]=I
        for ai,a in enumerate(ARMS):accounting.append({'eligible':g,'scope':name,'arm':a,'mean':float(mu[ai]),'identified_count':int(np.isfinite(point[selected])[s.arm.eq(a).to_numpy()].sum())})
costs=json.loads((r/'output/policies.json').read_text());vertices=costs['vertices'];rows=[]
for label,v in vertices.items():
    c=policy_vector({'Gikuriro':1.})-policy_vector(v);cp=np.maximum(c,0);cn=np.minimum(c,0)
    for scope,g in [('eligible',1),('ineligible',0),('community',None)]:
        if g is None:
            mu=sum(shares[t]*moments[t,'identified'] for t in [0,1]);I=sum(shares[t]*influence[t,'identified'] for t in [0,1]);L=sum(shares[t]*moments[t,'lower_endpoint'] for t in [0,1]);H=sum(shares[t]*moments[t,'upper_endpoint'] for t in [0,1])
        else:mu=moments[g,'identified'];I=influence[g,'identified'];L=moments[g,'lower_endpoint'];H=moments[g,'upper_endpoint']
        rows.append({'population':scope,'policy':label,'gikuriro_minus_policy_identified_mean':float(c@mu),'exploratory_block_se':float(np.linalg.norm(I@c)),'gikuriro_minus_policy_missingness_lower':float(cp@L+cn@H),'gikuriro_minus_policy_missingness_upper':float(cp@H+cn@L)})
result={'scope':'Exploratory pilot from existing public data, prompted after eighth rejection. No new observations. Point ratios select identified diets. Endpoint estimates retain full baseline membership but have sampling error; these are not finite confidence bounds. Community aggregation uses fixed released baseline expansion-weight shares and maintained assignment model. No verified institutional welfare function, new spillover mechanism or leading-journal importance claimed. Frozen eighth science unchanged.','weight_diagnostics':diagnostics,'arm_means':accounting,'policy_comparisons':rows}
(r/'docs/exploration/community-diet-pilot.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
pd.DataFrame(rows).to_csv(r/'docs/exploration/community-diet-pilot.csv',index=False,lineterminator='\n')
print(json.dumps(diagnostics,indent=2));print(pd.DataFrame(rows)[pd.DataFrame(rows).policy.eq('Lower+Large')].to_string(index=False))
