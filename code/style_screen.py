"""Optional requested detector screen; never used to create scientific outcomes.

Clone paulgp/econ-ai-detector under .detector/source. This only runs the
logistic-regression component; it does not manufacture a full ensemble score.
"""
from pathlib import Path
import hashlib, importlib.metadata, json, subprocess, sys
root=Path(__file__).resolve().parents[1]
source=root/'.detector/source'
sys.path.insert(0,str(source))
from econ_ai_detector.detector import Detector
from econ_ai_detector.preprocess import cut_references, pdf_text, prose_ok, windows

paper=root/'paper/paper.pdf'
text=cut_references(pdf_text(str(paper)))
wins=windows(text);kept=[w for w in wins if prose_ok(w)]
det=Detector();scores=det.lr_scores(kept);second=det._k2(scores)
threshold=det.thr['lr_k2_min']
report={'scope':'Official PDF extraction, reference cut, 250-word windows and prose gate; logistic-regression component only',
        'source':'https://github.com/paulgp/econ-ai-detector',
        'source_commit':subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip(),
        'paper_sha256':hashlib.sha256(paper.read_bytes()).hexdigest(),
        'model_sha256':hashlib.sha256((source/'models/lr_v3.joblib').read_bytes()).hexdigest(),
        'versions':{k:importlib.metadata.version(k) for k in ['numpy','scipy','scikit-learn','joblib','pysbd','pymupdf']},
        'windows_total':len(wins),'windows_scored':len(kept),'lr_k2':second,
        'lr_k2_threshold':threshold,'lr_necessary_condition_met':bool(second>=threshold),
        'nn_margins':None,'full_ensemble_measured':False,'window_lr_probs':scores.tolist(),
        'interpretation':'A non-flag is not evidence of human authorship. If the LR necessary condition fails, the documented AND rule cannot flag this PDF on these windows; no neural margins are inferred.'}
(root/'output/style-lr.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k not in ['window_lr_probs','interpretation']},indent=2))
