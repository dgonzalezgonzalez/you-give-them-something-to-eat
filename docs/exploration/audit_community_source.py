from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd
r=Path(__file__).resolve().parents[2]
source=r/'data/raw/source/McIntosh and Zeitlin/3-replication/data/household_panel.dta'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='ae21b9766e303b55667bb5deab26a10b494bd06fc70ed2bc36d245e7df31e4db'
d=pd.read_stata(source,convert_categoricals=False)
groups=[['cereals'],['tubers'],['vitaveg','leafyveg','otherveg'],['vitaafruits','otherfruits'],['organmeat','fleshmeat'],['eggs'],['fish'],['legumes'],['milk'],['oils'],['sweets'],['spices']]
food=['m9_'+n for g in groups for n in g]
b=d[d['round'].eq(1)].copy();e=d[d['round'].eq(2)][['hhid',*food]]
s=b.drop(columns=food).merge(e,on='hhid',how='left',validate='one_to_one')
s['arm']='Control'
for name,col in [('Gikuriro','treat_GK'),('Lower','treat_GD_lower'),('Middle','treat_GD_mid'),('Upper','treat_GD_upper'),('Large','treat_GD_huge')]:s.loc[s[col].eq(1),'arm']=name
villages=s.drop_duplicates('vid');assert len(villages)==248;counts=pd.crosstab(villages.block,villages.arm);prob=counts.div(counts.sum(axis=1),axis=0)
lower=np.zeros(len(s));upper=np.zeros(len(s))
for g in groups:
    x=s[['m9_'+n for n in g]].to_numpy();lower+=(x==1).any(axis=1);upper+=~(x==0).all(axis=1)
score=(lower+upper)/2;score[lower!=upper]=np.nan
pilot=json.loads((r/'docs/exploration/community-diet-pilot.json').read_text())
max_error=0.;checked=0
for g in [0,1]:
    for name,y in [('identified',score),('lower_endpoint',lower),('upper_endpoint',upper)]:
        for a in ['Control','Gikuriro','Lower','Middle','Upper','Large']:
            keep=s.eligible.eq(g).to_numpy()&s.arm.eq(a).to_numpy()&np.isfinite(y)
            w=s.loc[keep,'samp_wgt'].to_numpy(dtype=float)/s.loc[keep,'block'].map(prob[a]).to_numpy()
            value=float(np.sum(w*y[keep])/np.sum(w))
            target=next(z['mean'] for z in pilot['arm_means'] if z['eligible']==g and z['scope']==name and z['arm']==a)
            max_error=max(max_error,abs(value-target));checked+=1
assert max_error<1e-9
baseline_counts=b.groupby('eligible').size().to_dict();assert baseline_counts=={0:995,1:1793}
receipt={'scope':'Author-side independent source-file replay of pilot dietary point/endpoint arm ratios. Original public Stata source read directly; no imports of pilot, scoring or estimator modules. Defined group mapping/estimand are necessarily shared. Not external scientific replication, finite confidence certification, institutional preference identification or novelty evidence.','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'compared_arm_ratios':checked,'maximum_absolute_discrepancy':max_error,'tolerance':1e-9,'baseline_counts':baseline_counts,'source_program_count':248,'passed':True}
(r/'docs/exploration/community-source-audit.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8',newline='\n');print(json.dumps(receipt,indent=2))
