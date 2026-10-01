"""Round-eight inspection views; never default scientific inputs."""
from pathlib import Path
import hashlib,json
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]
dest=ROOT/'docs/referee/round-8-review';dest.mkdir(exist_ok=True)
report=json.loads((ROOT/'output/designed-decisions.json').read_text())
draws=pd.read_csv(ROOT/'output/designed_decision_draws.csv')
files=[]
def published_sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
def write(name,value):
    p=dest/name
    p.write_text(json.dumps(value,separators=(',',':'),ensure_ascii=False)+'\n',encoding='utf8',newline='\n')
    assert json.loads(p.read_text())==value
    files.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':published_sha(p)})
for case in range(144):
    leaf=f'case-{case:03d}.json'
    write(leaf,{'rows':[x for x in report['rows'] if x['case']==case],
                'benchmarks':[x for x in report['benchmark_rows'] if x['case']==case],
                'paired':[x for x in report['paired_rows'] if x['case']==case],
                'draw_files':[f'draws-{case:03d}-{part}.json' for part in range(4)]})
    selected=draws[draws.case==case]
    for part in range(4):
        values=selected.iloc[part*64:(part+1)*64].to_dict('records')
        write(f'draws-{case:03d}-{part}.json',{'case':case,'rows':values})
effect_summary=pd.read_csv(ROOT/'output/designed_decision_effect_summary.csv')
for reporting,values in effect_summary.groupby('reporting'):
    write('effects-'+reporting+'.json',values.to_dict('records'))
write('summary.json',{'grid':report['grid'],'seed':report['seed'],'repetitions':report['repetitions_per_case'],
    'monte_carlo_scope':report['monte_carlo_scope'],'benchmark_scope':report['benchmark_scope'],
    'effect_summary_files':['effects-'+pattern+'.json' for pattern in report['grid']['reporting']],
    'quota_minus_empbern_effect_pairs':pd.read_csv(ROOT/'output/designed_decision_effect_pairs.csv').query("first_method == 'quota' and second_method == 'empirical_bernstein_fixed_forecast'").to_dict('records'),
    'scope':'Known-population inspection views. Case files retain all seven rules and every pair; four draw parts per case retain 256 actual-regret draws. All 144 cells remain. Field models, witnesses and regional duals remain in round-7-review; their published historical canonical hashes apply to the frozen seventh source. No microdata execution, original assignment-law verification or economic importance follows from aliases.'})
manifest={'files':files,'canonical_sources':{name:published_sha(ROOT/name) for name in [
    'output/designed-decisions.json','output/designed_decision_draws.csv','output/designed_decision_effect_summary.csv','output/designed_decision_effect_pairs.csv']},
    'hash_convention':'SHA256 of UTF-8 LF published bytes; CRLF is explicitly normalized for canonical sources.',
    'scope':'Inspection copies, separate from default scientific inputs. JSON numbers round-trip their source CSV parser, within the declared numerical replication tolerance; original CSV bytes are canonical. Historical round-seven views are not rewritten.'}
(dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8',newline='\n')
(dest/'README.md').write_text('# Eighth-revision decision inspection views\n\nStart with summary.json and manifest.json. All 144 case files retain five certified-region rules, two simple rules without comparable certificates, every paired comparison and links to four draw parts. Per-draw regret supports independent Monte Carlo checks; it does not prove coverage or supply field observations.\n\n'+manifest['scope']+'\n',encoding='utf8',newline='\n')
print('Round-eight aliases:',len(files),'maximum bytes:',max(x['bytes'] for x in files))
