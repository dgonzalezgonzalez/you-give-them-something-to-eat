"""Compare the published Git source run in a freshly installed environment."""
from pathlib import Path
import json
import pandas as pd
import pymupdf

root=Path(__file__).resolve().parents[1]
rep=root/'tmp/published-clean'
checks={}
for file in (root/'output').glob('*.csv'):
    if file.name=='stata-validation.csv':continue
    a=pd.read_csv(file);b=pd.read_csv(rep/'output'/file.name)
    pd.testing.assert_frame_equal(a,b,check_exact=False,rtol=1e-10,atol=1e-12)
    checks['output/'+file.name]=True
for file in (root/'output/tables').glob('*.tex'):
    checks['output/tables/'+file.name]=file.read_text()==(rep/'output/tables'/file.name).read_text()
for file in ['output/numbers.json','output/policies.json','paper/results.tex']:
    checks[file]=(root/file).read_text()==(rep/file).read_text()
for file in (root/'output/figures').glob('*.png'):
    checks['output/figures/'+file.name]=file.read_bytes()==(rep/'output/figures'/file.name).read_bytes()
a=pymupdf.open(root/'paper/paper.pdf');b=pymupdf.open(rep/'paper/paper.pdf')
checks['pdf_page_text']=len(a)==len(b) and all(x.get_text()==y.get_text() for x,y in zip(a,b))
report={'scope':'Published Git commit 046ce79 exported with git archive; fresh Python virtual environment installed from requirements.txt via official PyPI',
        'checks':checks,'all_passed':all(checks.values()),'pdf_pages':len(b),
        'master':json.loads((rep/'output/master_run.json').read_text())}
(root/'output/fresh-environment.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('Fresh-environment published-source checks:',sum(checks.values()),'/',len(checks),'passed')
if not report['all_passed']:raise AssertionError(report)
