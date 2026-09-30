"""Compare the published Git source run in a freshly installed environment."""
from pathlib import Path
import argparse,json
import pandas as pd
import pymupdf

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--source-dir',default='tmp/published-clean')
parser.add_argument('--commit-file',default='tmp/published-commit.txt')
args=parser.parse_args()
rep=root/args.source_dir
checks={}
for file in (root/'output').glob('*.csv'):
    if file.name=='stata-validation.csv':continue
    a=pd.read_csv(file);b=pd.read_csv(rep/'output'/file.name)
    pd.testing.assert_frame_equal(a,b,check_exact=False,rtol=1e-10,atol=1e-12)
    checks['output/'+file.name]=True
for file in (root/'output/tables').glob('*.tex'):
    checks['output/tables/'+file.name]=file.read_text()==(rep/'output/tables'/file.name).read_text()
for file in ['output/numbers.json','output/revision-numbers.json','output/decision-numbers.json','output/policies.json','paper/results.tex','paper/revision-results.tex','paper/decision-results.tex','docs/output-map.csv']:
    checks[file]=(root/file).read_text()==(rep/file).read_text()
for file in (root/'output/figures').glob('*.png'):
    checks['output/figures/'+file.name]=file.read_bytes()==(rep/'output/figures'/file.name).read_bytes()
a=pymupdf.open(root/'paper/paper.pdf');b=pymupdf.open(rep/'paper/paper.pdf')
checks['pdf_page_text']=len(a)==len(b) and all(x.get_text()==y.get_text() for x,y in zip(a,b))
commit=(root/args.commit_file).read_text().strip()
report={'scope':'Published Git commit '+commit+' exported with git archive and run in the separately installed locked Python environment; environment was originally freshly installed from official PyPI for the first submission, not reinstalled for this revision',
        'source_commit':commit,
        'checks':checks,'all_passed':all(checks.values()),'pdf_pages':len(b),
        'master':json.loads((rep/'output/master_run.json').read_text())}
(root/'output/fresh-environment.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('Fresh-environment published-source checks:',sum(checks.values()),'/',len(checks),'passed')
if not report['all_passed']:raise AssertionError(report)
