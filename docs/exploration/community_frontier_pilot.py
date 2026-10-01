from pathlib import Path
import json
import numpy as np,pandas as pd
r=Path(__file__).resolve().parents[2]
x=json.loads((r/'docs/exploration/community-diet-pilot.json').read_text())
means={g:np.array([next(t['mean'] for t in x['arm_means'] if t['eligible']==g and t['scope']=='identified' and t['arm']==a) for a in ['Control','Gikuriro','Lower','Middle','Upper','Large']]) for g in [0,1]}
names=['Control','Gikuriro','Lower','Middle','Upper','Large']
p=json.loads((r/'output/policies.json').read_text());policies={'Gikuriro':{'Gikuriro':1},**p['vertices']}
intercepts={label:sum(q*means[0][names.index(a)] for a,q in v.items()) for label,v in policies.items()}
slopes={label:sum(q*(means[1][names.index(a)]-means[0][names.index(a)]) for a,q in v.items()) for label,v in policies.items()}
roots={0.,1.}
for a in policies:
    for b in policies:
        if abs(slopes[a]-slopes[b])>1e-12:
            theta=(intercepts[b]-intercepts[a])/(slopes[a]-slopes[b])
            if 0<theta<1:roots.add(theta)
roots=sorted(roots);segments=[]
for a,b in zip(roots[:-1],roots[1:]):
    t=(a+b)/2;best=max(policies,key=lambda k:intercepts[k]+t*slopes[k])
    if segments and segments[-1]['policy']==best:segments[-1]['theta_upper']=b
    else:segments.append({'theta_lower':a,'theta_upper':b,'policy':best})
tau=x['weight_diagnostics'][1]['population_share_from_baseline_weights']
for s in segments:
    for key in ['theta_lower','theta_upper']:
        theta=s[key];s[key+'_relative_eligible_household_weight']=theta/(1-theta)*(1-tau)/tau if theta<1 else None
out={'scope':'Exploratory fitted identified-diet objective only, using original eligible-household cost menu and published point ratios. Theta is a stipulated total eligible welfare share, not an estimated preference or household population proportion. Switches have sampling and missingness uncertainty. Same source village-package delivery and no cross-village interference/transport conditions remain assumed. Earlier parent manuscripts already studied broader-population effects; this frontier is not a new externality discovery.','eligible_baseline_expansion_share':tau,'segments':segments,'gikuriro_vs_lower_large_crossing_theta':None}
for c in x['policy_comparisons']:
    if c['policy']=='Lower+Large' and c['population']=='eligible':de=c['gikuriro_minus_policy_identified_mean']
    if c['policy']=='Lower+Large' and c['population']=='ineligible':di=c['gikuriro_minus_policy_identified_mean']
out['gikuriro_vs_lower_large_crossing_theta']=di/(di-de)
(r/'docs/exploration/community-frontier-pilot.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8');print(json.dumps(out,indent=2))
