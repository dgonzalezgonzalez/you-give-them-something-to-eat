"""Optional exact author-side replay of 50 archived floating-point draw differences.
Run from repository root. Writes only ignored tmp output. No new independent referee execution.
"""
from pathlib import Path
from fractions import Fraction
from decimal import Decimal
import sys, io, itertools, json, subprocess, zipfile
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'code'))
import designed_decisions as decisions
source='aa8667ccde0e00d4c5aa182a89d88b4065a6dda6'
original=subprocess.check_output(['git','show',source+':code/designed_decisions.py']).decode()
assert original == Path('code/designed_decisions.py').read_text(encoding='utf-8')
archive=zipfile.ZipFile('docs/referee/round-8-received-audit/referee_round8_audit_v0.8.0.zip')
author=pd.read_csv(io.BytesIO(subprocess.check_output(['git','show',source+':output/designed_decision_draws.csv']))).set_index(['case','repetition'])
referee=pd.read_csv(io.BytesIO(archive.read('referee_round8/synthetic_draws.csv'))).set_index(['case','repetition'])
settings=json.loads(subprocess.check_output(['git','show',source+':output/designed-decisions.json']))['baseline_moment_settings']
grid=list(itertools.product([8,24,64],[8,32],['equal','concentrated'],[-160,0,40,160],['complete','coarse_interval','assignment_dependent']))
rows=[]
for method in ['harmonic_martingale','weight_sensitive_product']:
    differences=author[method]-referee[method]
    bad=differences[abs(differences)>1e-14]
    for case in sorted(set(bad.index.get_level_values('case'))):
        n,B,shape,effect,reporting=grid[case]
        w=np.ones(n,dtype=int)
        if shape=='concentrated':w[-1]=10
        total=B*int(w.sum());k=n//2
        setting=next(s for s in settings if (s['n'],s['blocks'],s['weight_shape'],s['method'])==(n,B,shape,method))
        radius=Fraction(Decimal(setting['radius_numerator_upper']))/total
        base=200+5*((np.arange(B)[:,None]*17+np.arange(n)[None,:]*37)%101)
        potential=np.stack([base,base+effect])
        rng=np.random.default_rng(np.random.SeedSequence([20261001,case]))
        targets=set(bad.loc[case].index)
        for repetition in range(max(targets)+1):
            treated=[rng.choice(n,k,replace=False).tolist() for _ in range(B)]
            controls=[np.flatnonzero(~np.isin(np.arange(n),slots)).tolist() for slots in treated]
            if repetition not in targets:continue
            bounds=[decisions.observed_bounds(w,selected,potential[a],reporting,a,total,radius)[0] for a,selected in enumerate([controls,treated])]
            (l0,h0),(l1,h1)=bounds
            U=max(Fraction(0),h1-l0);L=max(Fraction(0),h0-l1)
            optimal=U/(U+L) if U+L else Fraction(1,2)
            scaled=optimal*1_000_000
            q,upper,lower,rounding=decisions.rectangle_decision(bounds)
            real_regret=Fraction(-effect,1000)*q if effect<0 else Fraction(effect,1000)*(1-q)
            assert abs(float(real_regret)-author.loc[(case,repetition),method])<1e-14
            rows.append({'method':method,'case':int(case),'repetition':int(repetition),'scaled_exact_optimal':str(scaled),'exact_half_grid_tie':scaled.denominator==2,'author_probability':str(q),'author_regret':float(real_regret),'referee_regret':float(referee.loc[(case,repetition),method]),'absolute_regret_difference':abs(float(differences.loc[(case,repetition)])),'exact_rounding_bound':str(rounding)})
result={'scope':'Author-side exact replay of the 50 discrepant archived floating-point draw outputs against the unchanged frozen eighth rectangle_decision/observed_bounds code and stored directed radius. It is not new referee execution.','discrepant_draw_values_above_1e_14':len(rows),'all_exact_half_grid_ties':all(r['exact_half_grid_tie'] for r in rows),'rows':rows}
Path('tmp/round8-received-audit-rounding-replay.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({k:v for k,v in result.items() if k!='rows'}))
