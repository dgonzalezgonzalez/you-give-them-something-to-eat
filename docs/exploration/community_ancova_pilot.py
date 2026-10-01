from pathlib import Path
import sys,json
import numpy as np,pandas as pd
r=Path(__file__).resolve().parents[2];sys.path.insert(0,str(r/'code'))
from estimate import ARMS,regress,contrast,policy_c
from referee_revision import GROUPS,score_interval
d=pd.read_csv(r/'data/input/households.csv');b=d[d['round'].eq(1)].set_index('hhid');e=d[d['round'].eq(2)&d.sample_panel.eq(1)].copy()
lo,hi=score_interval(e);e['score']=(lo+hi)/2;e.loc[lo!=hi,'score']=np.nan
rows=[];vertices=json.loads((r/'output/policies.json').read_text())['vertices']
for g in [0,1]:
    s=e[e.eligible.eq(g)].copy();lag=s.hhid.map(b.dietarydiversity)
    for usebase in [False,True]:
        f=regress(s,s.score.to_numpy(),lag.to_numpy() if usebase else None)
        for name,q in vertices.items():rows.append({'eligible':g,'baseline_control':usebase,'policy':name,**contrast(f,policy_c(f,q))})
pd.DataFrame(rows).to_csv(r/'docs/exploration/community-ancova-pilot.csv',index=False,lineterminator='\n')
print(pd.DataFrame(rows)[pd.DataFrame(rows).policy.isin(['Lower+Large','Upper','Control'])].to_string(index=False))
