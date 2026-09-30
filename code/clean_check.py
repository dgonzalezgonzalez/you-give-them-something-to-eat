"""Cold-output reproduction in a fresh source copy, using the current interpreter."""
from pathlib import Path
import datetime, hashlib, json, shutil, subprocess, sys
import pymupdf

root=Path(__file__).resolve().parents[1]
name=datetime.datetime.now().strftime('clean-%Y%m%d-%H%M%S')
dest=root/'tmp'/name
dest.mkdir(parents=True,exist_ok=False)
for folder in ['code','data/input']:
    shutil.copytree(root/folder,dest/folder,ignore=shutil.ignore_patterns('__pycache__'))
(dest/'paper').mkdir()
for file in ['run.py','requirements.txt','paper/paper.tex']:
    shutil.copy2(root/file,dest/file)
subprocess.run([sys.executable,str(dest/'run.py'),'--pdf'],check=True,cwd=dest)
files=list((root/'output').glob('*.csv'))
files=[p for p in files if p.name!='stata-validation.csv']
files+=list((root/'output/tables').glob('*.tex'))
files+=list((root/'output/figures').glob('*.png'))
files+=[root/'output/policies.json',root/'output/numbers.json',root/'output/revision-numbers.json',root/'output/decision-numbers.json',root/'paper/results.tex',root/'paper/revision-results.tex',root/'paper/decision-results.tex',root/'docs/output-map.csv']
checks={}
for file in files:
    relative=file.relative_to(root)
    checks[str(relative).replace('\\','/')]=hashlib.sha256(file.read_bytes()).hexdigest()==hashlib.sha256((dest/relative).read_bytes()).hexdigest()
original=pymupdf.open(root/'paper/paper.pdf');copy=pymupdf.open(dest/'paper/paper.pdf')
checks['paper_pdf_page_text']=len(original)==len(copy) and all(a.get_text()==b.get_text() for a,b in zip(original,copy))
report={'scope':'Fresh copy with no prior outputs; same installed interpreter and pinned statistical package versions, not a fresh package installation',
        'checked_files':len(files),'checks':checks,'all_passed':all(checks.values()),
        'pdf_pages':len(copy),'excluded_from_byte_comparison':['runtime metadata','PDF creation timestamps','optional Stata reference'],
        'master':json.loads((dest/'output/master_run.json').read_text())}
(root/'output/clean-run.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('Clean-copy reproducibility:',sum(checks.values()),'/',len(checks),'passed')
if not report['all_passed']:raise AssertionError(report)
