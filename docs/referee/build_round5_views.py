"""Lossless small public inspection views of the canonical numerical receipt.

Not inputs to the scientific master, new observations, file-upload fallback
or independent execution evidence. Values reconstruct the public receipt.
"""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[2];dest=root/'docs/referee/round-5-review';dest.mkdir(exist_ok=True)
source=root/'output/quota-loss-bound.json';data=json.loads(source.read_text());files=[]
def write(name,value):
    p=dest/name;p.write_text(json.dumps(value,separators=(',',':'),ensure_ascii=False)+'\n',encoding='utf8')
    files.append({'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
for model in data['models']:write('model-'+model['arm']+'.json',model)
summary={k:data[k] for k in ['scope','event_terms','event_cap','conditional_failure_probability','transformations']};summary['scenarios']=[]
for scenario in data['scenarios']:
    row={k:v for k,v in scenario.items() if k!='comparators'};row['comparators']=[]
    for comp in scenario['comparators']:
        name='witness-'+scenario['objective']+'-'+comp['comparator'].replace('+','-')+'.json';write(name,comp)
        row['comparators'].append({k:comp[k] for k in ['comparator','tau','support_upper','direction_rounding_upper']})
        row['comparators'][-1]['witness_file']=name
    summary['scenarios'].append(row)
moments=json.loads((root/'output/quota-normalizers.json').read_text())
summary['moment_selection']=[{k:row[k] for k in ['arm','scale','fixed_lambda_normalized','certified_upper_log_normalizer','selection_threshold']} for row in moments['rows']]
summary['validation']={}
for name in ['quota-enclosure-validation.json','quota-allocation-validation.json']:
    receipt=json.loads((root/'output'/name).read_text());summary['validation'][name]={'checks':len(receipt['checks']),'passed':sum(receipt['checks'].values()),'all_passed':receipt['all_passed']}
write('summary.json',summary)
manifest={'canonical_source':'output/quota-loss-bound.json','canonical_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'files':files,
          'scope':'Lossless public views for inspection only; default master uses canonical inputs and recomputes the receipt. No independently executed household or referee result is asserted.'}
(dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
# Round-trip JSON comparison, including every arm and comparator witness.
assert [json.loads((dest/('model-'+m['arm']+'.json')).read_text()) for m in data['models']]==data['models']
for s in data['scenarios']:
    for c in s['comparators']:
        name='witness-'+s['objective']+'-'+c['comparator'].replace('+','-')+'.json'
        assert json.loads((dest/name).read_text())==c
print('Lossless public receipt views verified:',len(files),'max bytes',max(x['bytes'] for x in files))
