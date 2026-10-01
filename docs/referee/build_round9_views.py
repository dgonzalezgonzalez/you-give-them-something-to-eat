"""Optional small public inspection aliases from published LF Git objects.

No alias is a scientific input; default master never reads these files.
Run from the repository root after publishing the scientific source.
"""
from pathlib import Path
import hashlib,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
SOURCE='559dd4552e7b1897063c0e880ea8325439e794e8'
DEST=ROOT/'docs/referee/round-9-review';DEST.mkdir(parents=True,exist_ok=True)
def published(path):
    return subprocess.check_output(['git','show',SOURCE+':'+path],cwd=ROOT)
canonical='output/community-decision.json';source_bytes=published(canonical)
report=json.loads(source_bytes);files=[]
def write(name,value,origin):
    data=(json.dumps(value,ensure_ascii=True,separators=(',',':'))+'\n').encode('utf8')
    if len(data)>16000:raise ValueError('View exceeds retrieval size: '+name)
    (DEST/name).write_bytes(data)
    files.append({'file':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'source':origin})
keys=['scope','family_size','alpha','normative_weight_scope','asymptotic_scope','input_hashes','baseline_diagnostics','baseline_eligible_weight_share_exact','baseline_eligible_weight_share','quota_mean_test_family','quota_mean_test_cap','mean_boxes','quota_mean_boxes','menus','causal_welfare_ranking_identified','general_interest_importance_established','fitted_frontiers','ancova_multiplicity']
write('population-metadata.json',{k:report[k] for k in keys},canonical+' selected named fields')
for i,case in enumerate(report['decisions'],1):write(f'game-{i:02d}.json',case,canonical+f' decisions[{i-1}]')
for i,case in enumerate(report['quota_mean_normalizers'],1):write(f'moment-{i:02d}.json',case,canonical+f' quota_mean_normalizers[{i-1}]')
for g in [0,1]:
    for arm in ['Control','Gikuriro','Lower','Middle','Upper','Large']:
        write(f'classical-{g}-{arm.lower()}.json',[x for x in report['finite_primitives'] if x['eligible']==g and x['arm']==arm],canonical+f' finite_primitives eligible={g}, arm={arm}')
for path in ['output/community_arm_estimates.csv','output/community_policy_comparisons.csv','output/community_ancova.csv','paper/community-results.tex']:
    data=published(path)
    if len(data)>16000:raise ValueError('Published alias exceeds size')
    name=Path(path).name;(DEST/name).write_bytes(data)
    files.append({'file':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'source':path})
code_files=['code/community_decision.py','code/validate_community_decision.py','code/build_community_exhibits.py']
for path in code_files:
    data=published(path);lines=data.splitlines(keepends=True);chunks=[];chunk=b'';first=1
    for number,line in enumerate(lines,1):
        if len(chunk)+len(line)>14000:
            chunks.append((first,number-1,chunk));first=number;chunk=b''
        chunk+=line
    if chunk:chunks.append((first,len(lines),chunk))
    if b''.join(x[2] for x in chunks)!=data:raise ValueError('Code partition changes bytes')
    for i,(first,last,chunk) in enumerate(chunks,1):
        name=Path(path).stem+f'-part-{i:02d}.txt';(DEST/name).write_bytes(chunk)
        files.append({'file':name,'bytes':len(chunk),'sha256':hashlib.sha256(chunk).hexdigest(),'source':path,'first_line':first,'last_line':last})
manifest={'scope':'Small public inspection aliases of the stated scientific commit. Not scientific inputs, new observations, external replication, assignment-law evidence or a ninth submission. Code chunks concatenate to the exact published LF object. JSON aliases retain complete selected subobjects.','source_commit':SOURCE,'canonical_output':canonical,'canonical_sha256':hashlib.sha256(source_bytes).hexdigest(),'canonical_code_sha256':{p:hashlib.sha256(published(p)).hexdigest() for p in code_files},'files':files}
(DEST/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8',newline='\n')
# Exact selective replay proves these aliases preserve published values/bytes.
for i,case in enumerate(report['decisions'],1):
    if json.loads((DEST/f'game-{i:02d}.json').read_bytes())!=case:raise ValueError('Game alias mismatch')
for i,case in enumerate(report['quota_mean_normalizers'],1):
    if json.loads((DEST/f'moment-{i:02d}.json').read_bytes())!=case:raise ValueError('Moment alias mismatch')
for g in [0,1]:
    for arm in ['Control','Gikuriro','Lower','Middle','Upper','Large']:
        expected=[x for x in report['finite_primitives'] if x['eligible']==g and x['arm']==arm]
        if json.loads((DEST/f'classical-{g}-{arm.lower()}.json').read_bytes())!=expected:raise ValueError('Classical alias mismatch')
if json.loads((DEST/'population-metadata.json').read_bytes())!={k:report[k] for k in keys}:raise ValueError('Metadata alias mismatch')
for path in code_files:
    parts=[z for z in files if z['source']==path]
    if b''.join((DEST/z['file']).read_bytes() for z in parts)!=published(path):raise ValueError('Published code reconstruction mismatch')
for path in ['output/community_arm_estimates.csv','output/community_policy_comparisons.csv','output/community_ancova.csv','paper/community-results.tex']:
    if (DEST/Path(path).name).read_bytes()!=published(path):raise ValueError('Published byte alias mismatch')
for record in files:
    if hashlib.sha256((DEST/record['file']).read_bytes()).hexdigest()!=record['sha256']:raise ValueError('Alias hash mismatch')
print(json.dumps({'files':len(files),'largest_bytes':max(z['bytes'] for z in files),'source_commit':SOURCE,'verified_games':12,'verified_moment_cases':12,'verified_classical_primitives':36,'reconstructed_code_files':3,'exact_byte_aliases':4}))
