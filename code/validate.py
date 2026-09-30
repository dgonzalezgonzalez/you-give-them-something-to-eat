"""Meaningful checks on data, budgets, transformations, and independent estimates."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
from estimate import ARMS,TX,regress,contrast,policy_vertices

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'
d=pd.read_csv(ROOT/'data/input/households.csv')
checks={}
checks['no_duplicate_household_round']=not d.duplicated(['hhid','round']).any()
checks['no_text_or_direct_identifiers']=all(pd.api.types.is_numeric_dtype(d[k]) for k in d)
checks['diet_integer_support']=d.dietarydiversity.dropna().between(0,12).all() and np.allclose(d.dietarydiversity.dropna(),np.rint(d.dietarydiversity.dropna()))
checks['random_assignment_constant']=d.groupby('vid')[TX].nunique().max().max()==1
checks['single_assignment']=np.isin(d[TX].sum(axis=1),[0,1]).all()
checks['blocks_constant']=d.groupby('vid').block.nunique().max()==1
checks['eligibility_fixed_across_rounds']=bool(d.groupby('hhid').eligible.nunique().le(1).all())
checks['sampling_weights_fixed_across_rounds']=bool(d.groupby('hhid').samp_wgt.nunique().le(1).all())
baseline_ids=d.loc[(d['round']==1)&(d.eligible==1),'hhid']
checks['endline_eligibles_link_to_baseline']=bool(d.loc[(d['round']==2)&(d.eligible==1),'hhid'].isin(baseline_ids).all())
p=json.loads((OUT/'policies.json').read_text());budget=p['budget'];costs=p['costs']
checks['all_policies_feasible']=all(abs(sum(q.values())-1)<1e-10 and min(q.values())>=0 and sum(costs[a]*v for a,v in q.items())<=budget+1e-9 for q in p['vertices'].values())
checks['budget_mixtures_exact']=all(abs(sum(costs[a]*v for a,v in q.items())-budget)<1e-9 for q in p['vertices'].values() if len(q)>1)
checks['eight_cash_vertices']=len(p['vertices'])==8
r=pd.read_csv(OUT/'arm_effects.csv');q=pd.read_csv(OUT/'policy_effects.csv')
checks['expected_primary_family']=len(r)+len(q)==221
checks['simultaneous_bands_contain_pointwise']=bool(((q.sim_lo<=q.lo+1e-10)&(q.sim_hi>=q.hi-1e-10)).all())
checks['missing_diet_eligible_n']=int(r.loc[r.outcome=='diet_mean','N'].iloc[0])==int(d.loc[(d['round']==2)&(d.eligible==1)&(d.sample_panel==1),'dietarydiversity'].notna().sum())
for outcome in ['diet_mean','shortfall_6']:
    b=r[r.outcome==outcome].set_index('arm').estimate.to_dict();b['Control']=0.
    for label,w in p['vertices'].items():
        actual=q.loc[(q.outcome==outcome)&(q.policy==label),'estimate'].iloc[0]
        expected=b['Gikuriro']-sum(v*b[a] for a,v in w.items())
        checks[f'mixture_identity_{outcome}_{label}']=bool(np.isclose(actual,expected,atol=1e-10))
independent={}
stata_path=OUT/'stata-validation.csv'
if stata_path.exists():
    s=pd.read_csv(stata_path)
    mapping={'GK':'Gikuriro','GD_lower':'Lower','GD_mid':'Middle','GD_upper':'Upper','GD_huge':'Large'}
    orig=r[r.outcome=='diet_mean'].set_index('arm')
    for row in s.itertuples():
        a=mapping[row.arm]
        independent[a]={'coefficient_error':float(abs(row.estimate-orig.loc[a,'estimate'])),
                        'se_error':float(abs(row.se-orig.loc[a,'se']))}
    checks['independent_stata_agreement']=all(max(v.values())<1e-6 for v in independent.values()) and len(independent)==5
else:independent['status']='Not run in this environment; optional proprietary validation.'
report={'checks':{k:bool(v) for k,v in checks.items()},'independent_stata':independent,
        'all_passed':all(checks.values())}
(OUT/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('Validation:',sum(checks.values()),'/',len(checks),'passed')
if not report['all_passed']:raise AssertionError(report)
