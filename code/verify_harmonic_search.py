"""Optional directed verification of independently searched harmonic proposals.

Run search_quota_allocation.py --moment-method harmonic_martingale first.
The search gaps remain numerical diagnostics, not certified minimax gaps.
"""
from pathlib import Path
import json
from quota_models import build_models,ARMS
from quota_allocation import verify_proposals
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'
search=json.loads((OUT/'harmonic-allocation-search.json').read_text())
if search['moment_method']!='harmonic_martingale':raise ValueError('Wrong moment method')
models,names=build_models(search['moment_rows']);proposals=[]
for scenario in search['scenarios']:
    unit=10**12;integers=[round(scenario['q'][a]*unit) for a in ARMS]
    integers[0]+=unit-sum(integers)
    proposals.append({'objective':scenario['objective'],'denominator':unit,'allocation_numerators':integers,
                      'support_dual_taus':scenario['last_comparator_support_scales']})
results=verify_proposals(models,proposals)
report={'scope':'Verified exact-rational proposals selected by a separate harmonic-martingale allocation search, under its own standalone conditional 95% shared event. Supports/costs are enclosed; minimax optimality and the diagnostic search gap are not certified. Optional result, not used in manuscript fixed-proposal comparisons or selected as a minimum over separate events.',
        'moment_method':'harmonic_martingale','event_terms':276,'event_cap':5520,'moment_rows':search['moment_rows'],
        'proposals':proposals,'scenarios':results,'transformations':names,
        'models':[{'arm':m['arm'],'C':m['C'].tolist(),'intercept':m['intercept'].tolist(),'A':m['A'].tolist(),'b':m['b'].tolist(),'bin_floors':m['floor'].tolist()} for m in models]}
(OUT/'harmonic-loss-bound.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
