"""Scientific invariants, independent LP checks and adversarial input audit."""
from pathlib import Path
import datetime,hashlib,json,shutil,subprocess,sys
import numpy as np
import pandas as pd
from scipy.optimize import linprog
from estimate import ARMS,policy_vertices
from referee_revision import score_interval

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output';checks={}
dist=pd.read_csv(OUT/'coherent_distributions.csv')
arm=pd.read_csv(OUT/'hajek_arm_effects.csv')
for a in ARMS:
    s=dist[dist.arm==a].sort_values('threshold')
    checks['cdf_valid_'+a]=bool(s.cdf.between(0,1+1e-12).all() and (np.diff(s.cdf)>=-1e-12).all() and abs(s.cdf.iloc[-1]-1)<1e-12)
    checks['cdf_bounds_order_'+a]=bool(((s.cdf_lower<=s.cdf_upper+1e-12)&s.cdf_lower.between(0,1+1e-12)&s.cdf_upper.between(0,1+1e-12)).all())
    if a!='Control':
        control=dist[dist.arm=='Control'].sort_values('threshold')
        implied=float((control.cdf.iloc[:-1].to_numpy()-s.cdf.iloc[:-1].to_numpy()).sum())
        actual=arm[(arm.arm==a)&(arm.outcome=='mean')].estimate.iloc[0]
        checks['mean_survival_identity_'+a]=bool(np.isclose(implied,actual,atol=1e-12))
        for k in range(1,13):
            implied=float((control.cdf.iloc[:k].to_numpy()-s.cdf.iloc[:k].to_numpy()).sum()/k)
            actual=arm[(arm.arm==a)&(arm.outcome==f'shortfall_{k}')].estimate.iloc[0]
            checks[f'shortfall_identity_{a}_{k}']=bool(np.isclose(implied,actual,atol=1e-12))
design=pd.read_csv(OUT/'assignment_probabilities.csv')
checks['assignment_probs_sum_to_one']=bool(np.allclose(design.groupby('block').probability.sum(),1))
checks['assignment_counts_248']=bool(design.villages.sum()==248)
checks['small_cash_one_per_block']=bool(design[design.arm.isin(['Lower','Middle','Upper'])].villages.eq(1).all())
obs=pd.read_csv(OUT/'diet_observation_intervals.csv')
checks['full_cohort_interval_partition']=bool((obs[['identified_diets','partially_identified','unobserved']].sum(axis=1)==obs.baseline_N).all() and obs.baseline_N.sum()==1793)
checks['more_information_than_complete_module']=bool(obs.identified_diets.sum()==1730)
regions=pd.read_csv(OUT/'population_bounds.csv').pivot(index=['outcome','left','right'],columns='endpoint',values='estimate')
checks['population_bound_order']=bool((regions.lower<=regions.upper+1e-12).all())
regret=pd.read_csv(OUT/'policy_regret.csv')
checks['regret_nonnegative_ordered']=bool((regret.fitted_regret>=-1e-12).all() and (regret.regret_lower_95<=regret.regret_upper_95).all())
meta=json.loads((OUT/'revision_metadata.json').read_text())
checks['deduplicated_revision_families']=bool((meta['point_family_size'],meta['pair_family_size'],meta['endpoint_family_size'])==(184,828,1656))
checks['original_primary_family_204']=json.loads((OUT/'run_metadata.json').read_text())['family_size']==204
checks['secondary_family_96']=json.loads((OUT/'run_metadata.json').read_text())['secondary_family_size']==96
# Check vertices against a separately implemented constrained optimizer, including
# cost-order reversals, equal costs, zero budget and exactly binding pure arms.
rng=np.random.default_rng(20260930);lp_errors=[]
names=['Control','Lower','Middle','Upper','Large']
for j in range(100):
    costs=dict(zip(names,[0.,*rng.uniform(1,600,4)]));budget=float(rng.uniform(0,600))
    if j%10==0:budget=costs[names[1+j%4]]
    if j%11==0:costs['Lower']=costs['Large']
    values=dict(zip(names,rng.normal(size=5)))
    vertices=policy_vertices(costs,budget)
    best=max(sum(values[a]*q for a,q in v.items()) for v in vertices.values())
    fit=linprog(-np.array([values[a] for a in names]),A_ub=[list(costs.values())],b_ub=[budget],A_eq=[np.ones(5)],b_eq=[1],bounds=(0,None),method='highs')
    assert fit.success;lp_errors.append(abs(best+fit.fun))
checks['vertices_match_100_independent_LPs']=max(lp_errors)<1e-9
# Tampered data + rewritten generated manifest must still fail against the frozen
# reference. Isolated fixture avoids changing the research inputs or Git state.
fixture=ROOT/'tmp'/('provenance-audit-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
(fixture/'data').mkdir(parents=True);shutil.copytree(ROOT/'data/input',fixture/'data/input');shutil.copy2(ROOT/'run.py',fixture/'run.py')
bad=fixture/'data/input/households.csv';bad.write_bytes(bad.read_bytes()+b'\n')
manifest=json.loads((fixture/'data/input/provenance.json').read_text());manifest['files']['households.csv']=hashlib.sha256(bad.read_bytes()).hexdigest()
(fixture/'data/input/provenance.json').write_text(json.dumps(manifest))
run=subprocess.run([sys.executable,str(fixture/'run.py')],capture_output=True,text=True)
checks['tamper_and_rewritten_manifest_rejected']=run.returncode!=0 and 'Immutable reference mismatch' in run.stderr
# Source corruption must fail before the extractor creates data/input.
(fixture/'code').mkdir();shutil.copy2(ROOT/'code/prepare_data.py',fixture/'code/prepare_data.py');(fixture/'data/raw').mkdir()
(fixture/'data/raw/source.zip').write_bytes(b'corrupted source')
run=subprocess.run([sys.executable,str(fixture/'code/prepare_data.py')],capture_output=True,text=True)
checks['corrupt_source_rejected']=run.returncode!=0 and 'source archive MD5 mismatch' in run.stderr
children=pd.read_csv(ROOT/'data/input/children.csv')
checks['child_keys_unique']=not children.duplicated(['childid','round']).any()
checks['child_extract_numeric_only']=all(pd.api.types.is_numeric_dtype(children[k]) for k in children)
report={'checks':{k:bool(v) for k,v in checks.items()},'max_LP_error':float(max(lp_errors)),
        'all_passed':all(checks.values()),'inference_limit':'Invariants do not validate an asymptotic approximation or selection ignorability.'}
(OUT/'revision-validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('Revision validation:',sum(checks.values()),'/',len(checks),'passed')
if not report['all_passed']:raise AssertionError(report)
