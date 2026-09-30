"""Numeric supplementary extract for the recorded referee-driven revision.

Reads only the hash-verified corrected archive. Original frozen core inputs stay
unchanged. Child keys are arbitrary; no dates, names or geographic labels export.
"""
from pathlib import Path
import hashlib, io, json, zipfile
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
raw=(ROOT/'data/raw/source.zip').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='84ce805316fef0d36466e75844afe521fb9a6dfe1fe33f454e1aa2dc71413a7e'
z=zipfile.ZipFile(io.BytesIO(raw));prefix='McIntosh and Zeitlin/3-replication/data/'
members={}
def read(name):
    payload=z.read(prefix+name);members[name]=hashlib.sha256(payload).hexdigest()
    return payload
h=pd.read_stata(io.BytesIO(read('household_panel.dta')),convert_categoricals=False)
maps={k:{v:i+1 for i,v in enumerate(sorted(h[k].dropna().unique()))} for k in ['hhid','vid','block']}
aux=h[['hhid','round','nEligible','nIneligible','samplingprobability','samp_wgt','dietarydiversity_R1',
       'Ldietarydiversity','Lhh_wealth_asinh','Lvill_eligible_ratio','Lsavingsstock_asinh3',
       'Lconsumpti_x_Lproductiv','Lconsumpti_x_Lselfcostd','foodexpenditure_asinh','foodownconsumption_asinh']].copy()
aux.hhid=aux.hhid.map(maps['hhid'])
payloads={'revision_households.csv':aux.to_csv(index=False,float_format='%.12g',lineterminator='\n').encode('utf8')}
c=pd.read_stata(io.BytesIO(read('individual_panel.dta')),convert_categoricals=False)
fields=['roster_id','round','hhid','vid','block','eligible','samp_wgt','female','agemonths',
        'anthro_shouldbe','anthro_present','anthro_baseline','anthro_panel','anthro_attrites',
        'haz06','waz06','muacz','haz06_R1','waz06_R1','muacz_R1']
c=c[fields].copy()
c=c[(c.anthro_shouldbe==1)|(c.anthro_baseline==1)|(c.anthro_present==1)].copy()
ids={v:i+1 for i,v in enumerate(sorted(c.roster_id.dropna().unique()))}
c.roster_id=c.roster_id.map(ids);c=c.rename(columns={'roster_id':'childid'})
for k in maps:c[k]=c[k].map(maps[k])
assert c[['hhid','vid','block','childid']].notna().all().all()
assert not c.duplicated(['childid','round']).any()
payloads['children.csv']=c.to_csv(index=False,float_format='%.12g',lineterminator='\n').encode('utf8')
files=['revision_households.csv','children.csv']
manifest={'source_doi':'10.5281/zenodo.15881329','license':'CC-BY-4.0','source_sha256':hashlib.sha256(raw).hexdigest(),
          'members':members,'files':{k:hashlib.sha256(payloads[k]).hexdigest() for k in files}}
reference=ROOT/'data/input/revision-reference.json'
if reference.exists():assert json.loads(reference.read_text())==manifest,'Supplementary extraction differs from immutable reference'
else:reference.write_text(json.dumps(manifest,indent=2),encoding='utf8',newline='\n')
for name,payload in payloads.items():(ROOT/'data/input'/name).write_bytes(payload)
print('Supplementary extraction verified:',len(aux),'household rows;',len(c),'child rows')
