"""One-command reproduction: python run.py [--from-source] [--pdf]."""
from pathlib import Path
import argparse, hashlib, json, os, platform, shutil, subprocess, sys, time

ROOT=Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--from-source',action='store_true',help='Re-extract directly from the verified data/raw/source.zip.')
    parser.add_argument('--pdf',action='store_true',help='Compile manuscript with pdflatex.')
    args=parser.parse_args();begin=time.time()
    os.chdir(ROOT)
    if args.from_source:
        for script in ['code/prepare_data.py','code/prepare_revision_data.py']:
            subprocess.run([sys.executable,script],check=True)
    manifest=json.loads((ROOT/'data/input/provenance.json').read_text())
    for filename,expected in manifest['files'].items():
        actual=hashlib.sha256((ROOT/'data/input'/filename).read_bytes()).hexdigest()
        if actual!=expected:raise RuntimeError('Input hash mismatch: '+filename)
    reference=json.loads((ROOT/'data/input/input-reference.json').read_text())
    for filename,expected in reference['files'].items():
        if hashlib.sha256((ROOT/'data/input'/filename).read_bytes()).hexdigest()!=expected:
            raise RuntimeError('Immutable reference mismatch: '+filename)
    revision=json.loads((ROOT/'data/input/revision-reference.json').read_text())
    for filename,expected in revision['files'].items():
        if hashlib.sha256((ROOT/'data/input'/filename).read_bytes()).hexdigest()!=expected:
            raise RuntimeError('Supplementary reference mismatch: '+filename)
    for script in ['code/estimate.py','code/referee_revision.py','code/finite_cluster.py','code/build_exhibits.py','code/build_revision_exhibits.py','code/validate.py','code/validate_revision.py']:
        subprocess.run([sys.executable,script],check=True)
    if args.pdf:
        compiler=os.environ.get('PDFLATEX') or shutil.which('pdflatex')
        if compiler is None:
            candidate=Path.home()/'AppData/Local/Programs/MiKTeX/miktex/bin/x64/pdflatex.exe'
            if candidate.exists():compiler=str(candidate)
        if compiler is None:raise RuntimeError('pdflatex missing: install a TeX distribution or set PDFLATEX.')
        for _ in range(3):
            result=subprocess.run([compiler,'-interaction=nonstopmode','-halt-on-error','paper.tex'],cwd=ROOT/'paper',capture_output=True,text=True)
            (ROOT/'output/latex-console.txt').write_text(result.stdout+result.stderr,encoding='utf8')
            if result.returncode:raise RuntimeError('LaTeX failed; see output/latex-console.txt')
    report={'python':platform.python_version(),'platform':platform.platform(),'seconds':time.time()-begin,
            'pdf_compiled':args.pdf,'source_reextracted':args.from_source}
    (ROOT/'output/master_run.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print('Master run successful:',json.dumps(report))

if __name__=='__main__':main()
