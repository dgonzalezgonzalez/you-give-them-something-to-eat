"""Replay shared-event benchmark tangents and exact LP-dual feasibility."""
from pathlib import Path
from fractions import Fraction
from decimal import Decimal
import json,numpy as np
from quota_models import build_models
from quota_arithmetic import I,tangent_support_upper
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'
report=json.loads((OUT/'quota-benchmarks.json').read_text());checks={}
for item in report['receipts']:
    if item['event']!='shared':continue
    models,_=build_models(item['moments'])
    if not item['bin_floors']:models=[{**m,'floor':np.zeros(13)} for m in models]
    prefix=item['method']+'_'+str(item['bin_floors'])
    for scenario in item['scenarios']:
        for comparator in scenario['comparators']:
            total=I(comparator['tau'])
            for arm,m in zip(comparator['arms'],models):
                bound,receipt=tangent_support_upper(arm['direction'],arm['candidate'],m['C'],m['intercept'],comparator['tau'],5520,m['A'],m['b'],m['floor'],arm['LP_dual']['nonpositive_multipliers'])
                name=prefix+'_'+scenario['objective']+'_'+comparator['comparator']+'_'+arm['arm']
                checks[name+'_replay']=bound<=arm['support_upper']
                dual=receipt['LP_dual'];ell=[Fraction(x) for x in dual['nonpositive_multipliers']]
                zeta=Fraction(Decimal(dual['equality_multiplier']));g=[Fraction(x) for x in receipt['tangent_gradient']]
                reduced=[g[j]-sum(Fraction(float(m['A'][i,j]))*v for i,v in enumerate(ell))-zeta for j in range(13)]
                checks[name+'_dual']=max(ell)<=0 and min(reduced)>=0
                total+=I(bound)
            total+=I(Decimal(comparator['direction_rounding_upper']))
            checks[prefix+'_'+scenario['objective']+'_'+comparator['comparator']+'_sum']=total.upper_float()<=comparator['support_upper']
        checks[prefix+'_'+scenario['objective']+'_maximum']=scenario['conditional_loss_upper']>=max(x['support_upper'] for x in scenario['comparators'])
result={'scope':'Shared-event benchmark receipt replay without searching support multipliers/candidates; model constants regenerated from existing microdata. Exact rational LP-dual feasibility and directed comparator sums. Separate Bonferroni LP receipts are not replayed here. This is an internal verification, not an independent external replication.',
        'checks':checks,'all_passed':bool(checks) and all(checks.values())}
(OUT/'quota-benchmark-receipt-validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print('Shared benchmark receipt checks',sum(checks.values()),'/',len(checks))
if not result['all_passed']:raise ValueError('Benchmark receipt replay failed')
