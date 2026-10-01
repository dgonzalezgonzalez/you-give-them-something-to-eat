"""Package the already-public v0.9.0 Git source for ordinary referee retrieval.

No scientific execution, new data extract or private upload. The frozen source
must exist in local Git history. Run from the repository root with Python 3.12.
"""
from pathlib import Path
import hashlib
import io
import json
import subprocess
import zipfile

FREEZE = 'f44a2f6cee1c19f86a6925c4b5685f8c468d58e4'
TAG_OBJECT = '826a4ece8fdb90f5d5d16bf3be2ad210bc8742ff'
ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'tmp/public-review-v0.9.0'
INPUTS = ['households.csv', 'costs.csv', 'codebook.json',
          'revision_households.csv', 'children.csv', 'analytical-codebook.json',
          'provenance.json', 'input-reference.json', 'revision-reference.json']

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)
def digest(data):
    return hashlib.sha256(data).hexdigest()

try:
    git('rev-parse', '--verify', 'refs/tags/v0.9.0')
except subprocess.CalledProcessError:
    # The existing hosted checkout is shallow. Fetch only the already-public
    # frozen tag, then authenticate both immutable identities below.
    subprocess.run(['git', 'fetch', '--no-tags', '--depth=1',
                    'https://github.com/dgonzalezgonzalez/you-give-them-something-to-eat.git',
                    'refs/tags/v0.9.0:refs/tags/v0.9.0'], cwd=ROOT, check=True)
assert git('rev-parse', 'v0.9.0^{}').decode().strip() == FREEZE
assert git('rev-parse', 'v0.9.0').decode().strip() == TAG_OBJECT
source = git('archive', '--format=zip', '--prefix=source/', FREEZE)
archive = zipfile.ZipFile(io.BytesIO(source))
assert archive.testzip() is None
checks = []
for name in INPUTS:
    path = 'data/input/' + name
    raw = git('show', FREEZE + ':' + path)
    assert archive.read('source/' + path) == raw
    checks.append({'path': path, 'bytes': len(raw), 'sha256': digest(raw)})
pdf = archive.read('source/paper/paper.pdf')
assert digest(pdf) == '583197f5deb609d59582b7ba7d513b5d6de6a13a526942390ed60dc1e5e9db6e'
manifest = {
    'scope': 'Already-public frozen Git source archive, including all nine canonical inputs, default code/output, dependencies, LaTeX/PDF and documentation. Packaging only, not new scientific execution or independent referee replication.',
    'ref': 'v0.9.0', 'commit': FREEZE, 'annotated_tag_object': TAG_OBJECT,
    'source_zip_bytes': len(source), 'source_zip_sha256': digest(source),
    'archive_members': len(archive.namelist()), 'canonical_inputs': checks,
    'all_nine_input_bytes_equal_frozen_git_blobs': True,
    'local_frozen_pdf_sha256': digest(pdf),
    'source_licensing': 'Unchanged frozen README: research extracts CC BY 4.0; original code MIT; manuscript for reading/review. No full original donor archive is added.',
    'retention': 'GitHub workflow artifact expires after 30 days; this is not DOI preservation. Frozen public Git source remains the scientific reference.',
    'extraction': 'Unzip the outer GitHub artifact, then source.zip. Read source/README.md before running source/run.py. The source archive contains inputs; previous cold-run artifacts contained only outputs.',
}
DEST.mkdir(parents=True, exist_ok=True)
(DEST / 'source.zip').write_bytes(source)
(DEST / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps(manifest, indent=2))
