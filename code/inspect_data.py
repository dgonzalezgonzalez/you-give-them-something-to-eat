"""Inspect source documentation and metadata without examining outcome realizations."""
from pathlib import Path
import json
import pandas as pd
import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'data/raw/source/McIntosh and Zeitlin'
for p in [SRC/'1-paper/20220682_accepted.pdf', SRC/'2-appendix/20220682_online_appendix.pdf', SRC/'3-replication/ReadMe.pdf']:
    text = '\n'.join(page.get_text() for page in fitz.open(p))
    (ROOT/'docs/sources'/f'{p.stem}.txt').write_text(text, encoding='utf8')
for p in (SRC/'3-replication/data').glob('*.dta'):
    reader = pd.io.stata.StataReader(p, convert_categoricals=False)
    meta = {'file': p.name, 'labels':reader.variable_labels(), 'value_labels':{k:{str(a):b for a,b in v.items()} for k,v in reader.value_labels().items()}}
    (ROOT/'docs/sources'/f'{p.stem}-metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf8')
    print(p.name, 'variables', len(meta['labels']))
    if 'household' in p.name:
        print(json.dumps(meta['labels'],indent=2))
