"""Pre-treatment source-flag cohort accounting and exploratory sensitivity.

The fixed cohort is baseline eligible children with source anthro_baseline=1,
not an assertion that every baseline child was measured. Follow-up score
availability still selects regression observations. No observation ignorability
or identified zero nutrition effect is claimed.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from estimate import ARMS,TX,regress,contrast,holm

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'

def main():
    children=pd.read_csv(ROOT/'data/input/children.csv')
    households=pd.read_csv(ROOT/'data/input/households.csv')
    assignment=households[households['round']==1].set_index('hhid')
    baseline=children[(children['round']==1)&(children.eligible==1)&(children.anthro_baseline==1)].copy()
    endline=children[children['round']==2].copy()
    scores=['haz06','waz06','muacz']
    fixed=baseline[['childid','hhid','vid','block','samp_wgt',*scores]].rename(columns={k:'baseline_'+k for k in scores})
    follow=endline[['childid','anthro_shouldbe','anthro_present','anthro_panel',*scores]].copy()
    follow['endline_row']=1
    fixed=fixed.merge(follow,on='childid',how='left',validate='one_to_one')
    for k in TX:fixed[k]=fixed.hhid.map(assignment[k])
    fixed['arm']='Control'
    for a,k in zip(ARMS[1:],TX):fixed.loc[fixed[k]==1,'arm']=a
    due=endline[(endline.eligible==1)&(endline.anthro_shouldbe==1)].copy()
    due['baseline_measured_cohort']=due.childid.isin(baseline.childid)
    due['arm']='Control'
    for a,k in zip(ARMS[1:],TX):due.loc[due.hhid.map(assignment[k])==1,'arm']=a
    counts=[]
    for a in ARMS:
        b=fixed[fixed.arm==a];e=due[due.arm==a]
        counts.append({'arm':a,'baseline_flagged_cohort':len(b),
                       'linked_endline_rows':int(b.endline_row.notna().sum()),
                       'baseline_cohort_due_endline':int(b.anthro_shouldbe.eq(1).sum()),
                       'baseline_cohort_measured_endline':int(b.anthro_present.eq(1).sum()),
                       'all_endline_due':len(e),
                       'endline_due_outside_baseline_cohort':int((~e.baseline_measured_cohort).sum()),
                       **{'baseline_cohort_available_'+k:int(b[k].notna().sum()) for k in scores},
                       **{'all_due_available_'+k:int(e[k].notna().sum()) for k in scores}})
    pd.DataFrame(counts).to_csv(OUT/'child_cohort_accounting.csv',index=False)
    estimates=[]
    for k in scores:
        fit=regress(fixed,fixed[k].to_numpy(),fixed['baseline_'+k].to_numpy())
        for ai,a in enumerate(ARMS[1:],1):
            c=np.zeros(len(fit['beta']));c[ai]=1.
            estimates.append({'cohort':'baseline_eligible_anthro_flag','outcome':k,'arm':a,**contrast(fit,c)})
    for row,p in zip(estimates,holm([x['p'] for x in estimates])):row['p_holm']=float(p)
    pd.DataFrame(estimates).to_csv(OUT/'baseline_child_effects.csv',index=False)
    info={'baseline_flagged_cohort':len(fixed),'all_endline_due':len(due),
          'baseline_cohort_linked_endline':int(fixed.endline_row.notna().sum()),
          'endline_due_baseline_cohort':int(due.baseline_measured_cohort.sum()),
          'endline_due_outside_baseline_cohort':int((~due.baseline_measured_cohort).sum()),
          'scope':'Baseline source anthropometry flag fixes membership and assignment; observed follow-up source scores still select regressions. Not a complete birth cohort or selection-robust nutrition effect.',
          'multiplicity':'Separate fifteen-test Holm family for the exploratory baseline-cohort sensitivity',
          'holm_rejections_05':sum(row['p_holm']<.05 for row in estimates)}
    assert info['baseline_flagged_cohort']==2265 and info['all_endline_due']==3017
    assert info['endline_due_baseline_cohort']+info['endline_due_outside_baseline_cohort']==info['all_endline_due']
    (OUT/'child-cohort-metadata.json').write_text(json.dumps(info,indent=2),encoding='utf8')
    print(json.dumps(info,indent=2))

if __name__=='__main__':main()
