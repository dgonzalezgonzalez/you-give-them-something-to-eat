"""Compact public views of verified comparison receipts and model constants.

Receipt views round-trip canonical JSON. Model views regenerate constants
from the unchanged public microdata and recorded moment rows. Inspection
aliases are not new observations or independent replication evidence.
"""
from pathlib import Path
import hashlib,json,sys,numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'code'))
from quota_models import build_models
dest=ROOT/'docs/referee/round-6-review';dest.mkdir(exist_ok=True)
data=json.loads((ROOT/'output/quota-benchmarks.json').read_text());files=[];summaries=[]

def write(name,value):
    p=dest/name;p.write_text(json.dumps(value,separators=(',',':'),ensure_ascii=False)+'\n',encoding='utf8')
    files.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})

for item in data['receipts']:
    label=item['method']+'-'+item['event']+('-floors' if item['bin_floors'] else '-no-floors')
    summary={k:item[k] for k in ['method','event','bin_floors','moments','selected_proposals']};summary['scenarios']=[]
    summary['moments']=[{k:v for k,v in row.items() if k in ['arm','fixed_lambda_normalized','certified_upper_log_normalizer','variance_proxy_upper','method','scale','selection_threshold']} for row in item['moments']]
    if item['event']=='shared':
        models,_=build_models(item['moments'])
        for m in models:
            model={'arm':m['arm'],'lambda':m['lambda'],'normalizer_upper':m['normalizer'],
                   'C':m['C'].tolist(),'intercept':m['intercept'].tolist(),'A':m['A'].tolist(),'b':m['b'].tolist(),
                   'bin_floors':m['floor'].tolist() if item['bin_floors'] else [0.]*13}
            write('model-'+label+'-'+m['arm']+'.json',model)
    for scenario in item['scenarios']:
        row={k:v for k,v in scenario.items() if k!='comparators'};row['comparators']=[]
        for comparator in scenario['comparators']:
            leaf='witness-'+label+'-'+scenario['objective']+'-'+comparator['comparator'].replace('+','-')+'.json'
            write(leaf,comparator)
            assert json.loads((dest/leaf).read_text())==comparator
            row['comparators'].append({'comparator':comparator['comparator'],'support_upper':comparator['support_upper'],'witness_file':leaf})
        summary['scenarios'].append(row)
    write('summary-'+label+'.json',summary);summaries.append(label)
write('summary.json',{'scope':data['scope'],'rows':data['rows'],'methods':summaries,
                     'design_catalogue':'output/quota-design-benchmarks.json','source_note':'Receipt aliases are exact JSON round trips; model constants are regenerated from existing microdata/recorded moments. No new data or independent execution asserted.'})
manifest={'canonical_source':'output/quota-benchmarks.json','canonical_sha256':hashlib.sha256((ROOT/'output/quota-benchmarks.json').read_bytes()).hexdigest(),
          'scope':'Public inspection aliases; original master inputs unchanged. Every comparator view round-trips its canonical JSON. Model views regenerate the same constants used by the internal receipt replay.',
          'files':files}
(dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
(dest/'README.md').write_text('# Sixth-revision inspection views\n\n'+manifest['scope']+'\n\nStart with summary.json and manifest.json. Separate method summaries identify all arm models and comparator witnesses. The default master uses canonical microdata and recomputes the comparison; these files are not scientific inputs. The models/receipts describe fixed-proposal comparisons, not certified method-wise minimax optima.\n',encoding='utf8')
print('Public views',len(files),'maximum bytes',max(x['bytes'] for x in files))
