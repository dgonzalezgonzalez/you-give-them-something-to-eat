"""Seventh inspection aliases with explicit published-LF hash convention.

Canonical microdata remain the default inputs. Models regenerate the same
constants; JSON receipt/population aliases round-trip their canonical objects.
They enable inspection, not independent upstream data execution.
"""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'code'))
from quota_models import build_models

dest=ROOT/'docs/referee/round-7-review';dest.mkdir(exist_ok=True)
data=json.loads((ROOT/'output/quota-benchmarks.json').read_text());files=[];summaries=[]

def published_sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()

def write(name,value):
    p=dest/name;p.write_text(json.dumps(value,separators=(',',':'),ensure_ascii=False)+'\n',encoding='utf8',newline='\n')
    assert json.loads(p.read_text(encoding='utf8'))==value
    files.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':published_sha(p)})

for item in data['receipts']:
    label=item['method']+'-'+item['event']+('-floors' if item['bin_floors'] else '-no-floors')
    summary={k:item[k] for k in ['method','event','bin_floors','moments','selected_proposals']};summary['scenarios']=[]
    summary['moments']=[{k:v for k,v in row.items() if k in ['arm','fixed_lambda_normalized','certified_upper_log_normalizer','variance_proxy_upper','method','scale','selection_threshold','baseline_scale_selection','normalizer_scope']} for row in item['moments']]
    if item['event']=='shared':
        models,_=build_models(item['moments'])
        for m in models:
            row=next(x for x in item['moments'] if x['arm']==m['arm'])
            model={'arm':m['arm'],'lambda':m['lambda'],'normalizer_upper':m['normalizer'],
                   'moment_model':row.get('method',item['method']),
                   'normalizer_scope':row.get('normalizer_scope','Fixed baseline upper log moment summed across independent blocks.'),
                   'C':m['C'].tolist(),'intercept':m['intercept'].tolist(),'A':m['A'].tolist(),'b':m['b'].tolist(),
                   'bin_floors':m['floor'].tolist() if item['bin_floors'] else [0.]*13}
            write('model-'+label+'-'+m['arm']+'.json',model)
    for scenario in item['scenarios']:
        row={k:v for k,v in scenario.items() if k!='comparators'};row['comparators']=[]
        for comparator in scenario['comparators']:
            leaf='witness-'+label+'-'+scenario['objective']+'-'+comparator['comparator'].replace('+','-')+'.json'
            write(leaf,comparator)
            row['comparators'].append({'comparator':comparator['comparator'],'support_upper':comparator['support_upper'],'witness_file':leaf})
        summary['scenarios'].append(row)
    write('summary-'+label+'.json',summary);summaries.append(label)

brackets=json.loads((ROOT/'output/regional-minimax-brackets.json').read_text());seen=set();regions=[]
for item in brackets['receipts']:
    label=item['method']+('-floors' if item['bin_floors'] else '-no-floors')
    population_files=[]
    for index,population in enumerate(item['exact_feasible_populations']):
        leaf=f'population-{label}-{index:03d}.json';population_files.append(leaf)
        if leaf not in seen:
            write(leaf,{'exact_rational_probabilities':population,'origin':item['population_origins'][index],
                        'stored_event_upper':item['enclosed_event_values'][index],
                        'scope':'Feasible implemented outer-region distribution; not a claimed jointly sharp finite potential population.'})
            seen.add(leaf)
    leaf='regional-dual-'+label+'-'+item['objective']+'.json'
    write(leaf,{'method':item['method'],'bin_floors':item['bin_floors'],'objective':item['objective'],
                'population_files':population_files,**{k:item[k] for k in ['exact_arm_means','dual','exact_lower','exact_proposal_upper']}})
    regions.append({'method':item['method'],'bin_floors':item['bin_floors'],'objective':item['objective'],'dual_file':leaf})

decisions=json.loads((ROOT/'output/designed-decisions.json').read_text())
for index in sorted(set(x['case'] for x in decisions['rows'])):
    write(f'decision-case-{index:03d}.json',{'rows':[x for x in decisions['rows'] if x['case']==index],
        'scope':'Known designed potential populations, not field observations. Four-term/cap-80 rectangular procedure, 256 draws, fixed seed. Timing is machine-specific; coverage is not a pass criterion.'})
write('summary.json',{'scope':data['scope'],'rows':data['rows'],'methods':summaries,
    'regional_minimax_rows':brackets['rows'],'regional_duals':regions,
    'design_catalogue':'output/quota-design-benchmarks.json','computation_catalogue':'output/quota-computation-benchmarks.json',
    'decision_grid':decisions['grid'],'decision_methods':decisions['methods'],'decision_seed':decisions['seed'],
    'decision_repetitions':decisions['repetitions_per_case'],
    'source_note':'Aliases round-trip canonical JSON; field models regenerate constants from existing microdata/moment settings. Exact regional memberships/duals concern stored outer sets. Neither aliases nor counts demonstrate independent upstream execution.'})
manifest={'canonical_sources':{name:published_sha(ROOT/name) for name in ['output/quota-benchmarks.json','output/regional-minimax-brackets.json','output/designed-decisions.json']},
          'hash_convention':'SHA256 of the published UTF-8 LF byte stream. Windows CRLF is normalized explicitly before canonical hashes; every alias is written LF. Historical sixth aliases remain frozen and are not rewritten.',
          'scope':'Inspection aliases only; canonical immutable microdata remain default scientific inputs. Models regenerated; all receipt/population/case objects round-trip canonical JSON.',
          'files':files}
(dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8',newline='\n')
(dest/'README.md').write_text('# Seventh-revision inspection views\n\nStart with summary.json and manifest.json. Method summaries identify models/support witnesses; regional-dual files identify exact feasible populations and exact policy duals; decision-case files report all five method rows for each predeclared known-population cell.\n\n'+manifest['scope']+'\n\n'+manifest['hash_convention']+'\n\nThe empirical-Bernstein normalizer field is a placeholder zero, explicitly labeled: its actual affine tests are rebuilt using directed observed compensation and all-order averaging, with fixed population weight. No fixed moment constant of zero is being asserted. Historical quota search diagnostics are labeled as source-quota provenance.\n',encoding='utf8',newline='\n')
print('Public seventh aliases',len(files),'maximum bytes',max(x['bytes'] for x in files),flush=True)
