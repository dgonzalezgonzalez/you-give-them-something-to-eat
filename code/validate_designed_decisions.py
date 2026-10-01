"""Independent endpoint-loss enumeration and exact logical-bound checks.

The Monte Carlo coverage proportion is deliberately not a pass criterion.
"""
from pathlib import Path
from fractions import Fraction as F
import itertools,json
import numpy as np
from designed_decisions import rectangle_decision,observed_bounds

ROOT=Path(__file__).resolve().parents[1];checks={}
intervals=[(F(a,4),F(b,4)) for a in range(5) for b in range(a,5)]
for case,bounds in enumerate(itertools.product(intervals,repeat=2)):
    q,upper,lower,rounding=rectangle_decision(bounds)
    def loss(prob):
        return max(max(x,y)-(1-prob)*x-prob*y for x,y in itertools.product(*bounds))
    checks[f'endpoint_support_{case}']=loss(q)==upper
    checks[f'analytic_lower_{case}']=all(lower<=loss(F(j,100)) for j in range(101))
    checks[f'rational_rounding_{case}']=0<=upper-lower<=rounding<=F(1,2000000)

weights=[1,2,3,4];potential=np.array([[200,400,600,800],[300,500,700,900]])
total=2*sum(weights);mean=F(sum(weights[j]*int(potential[b,j]) for b in range(2) for j in range(4)),1000*total)
subsets=list(itertools.combinations(range(4),2))
for assignment,selected in enumerate(itertools.product(subsets,repeat=2)):
    for reporting,arm in itertools.product(['complete','coarse_interval','assignment_dependent'],[0,1]):
        bounds,logical=observed_bounds(weights,selected,potential,reporting,arm,total,F(1))
        # A radius of one isolates deterministic endpoint and logical-mass
        # arithmetic, rather than making a probabilistic coverage assertion.
        checks[f'logical_contains_fixed_target_{assignment}_{reporting}_{arm}']=logical[0]<=mean<=logical[1]
        checks[f'large_radius_intersection_{assignment}_{reporting}_{arm}']=bounds==logical

report=json.loads((ROOT/'output/designed-decisions.json').read_text())
checks['all_predeclared_cells_reported']=len(report['rows'])==144*5
checks['no_coverage_pass_threshold']='coverage' not in report.get('pass_criterion','')
checks['all_counts_and_roundings_valid']=all(0<=r['joint_mean_interval_coverage_count']<=256 and 0<=r['empty_region_fallback_count']<=256 and r['maximum_rational_policy_rounding_bound']<=.0000005 for r in report['rows'])
checks['historical_quota_search_not_misattributed']=all('exploratory_search_upper' not in p and 'exploratory_search_gap' not in p for receipt in json.loads((ROOT/'output/quota-benchmarks.json').read_text())['receipts'] for p in receipt['selected_proposals'])
result={'scope':'225 exact interval pairs: independently enumerate four endpoint losses, compare analytic lower to 101 rational policy candidates, and check exact rounding bounds. Enumerate 36 blocked assignments with three reporting patterns and two arm-dependent reporting rules to verify deterministic full-population bounds. Monte Carlo coverage is retained as a diagnostic, never a pass criterion.',
        'checks':checks,'all_passed':all(checks.values())}
(ROOT/'output/designed-decision-validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(sum(checks.values()),'/',len(checks),'designed decision checks',flush=True)
if not result['all_passed']:raise ValueError([k for k,v in checks.items() if not v])
