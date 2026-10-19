"""Package the already-public v0.10.0 Git source for ordinary referee retrieval.

No scientific execution, new data extract or private upload. The frozen source
must exist in local Git history. Run from the repository root with Python 3.12.
"""
from pathlib import Path
import hashlib
import io
import json
import subprocess
import zipfile
import tarfile

FREEZE = 'd43048349402b0eca068ddf01d69c2126a0ac9ad'
TAG_OBJECT = '961a2b66e75be78ec21c887cf1088a6a728baa1f'
ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'tmp/public-review-v0.10.0'
INPUTS = ['households.csv', 'costs.csv', 'codebook.json',
          'revision_households.csv', 'children.csv', 'analytical-codebook.json',
          'provenance.json', 'input-reference.json', 'revision-reference.json']

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)
def digest(data):
    return hashlib.sha256(data).hexdigest()

try:
    git('rev-parse', '--verify', 'refs/tags/v0.10.0')
except subprocess.CalledProcessError:
    # The existing hosted checkout is shallow. Fetch only the already-public
    # frozen tag, then authenticate both immutable identities below.
    subprocess.run(['git', 'fetch', '--no-tags', '--depth=1',
                    'https://github.com/dgonzalezgonzalez/you-give-them-something-to-eat.git',
                    'refs/tags/v0.10.0:refs/tags/v0.10.0'], cwd=ROOT, check=True)
assert git('rev-parse', 'v0.10.0^{}').decode().strip() == FREEZE
assert git('rev-parse', 'v0.10.0').decode().strip() == TAG_OBJECT
source = git('archive', '--format=zip', '--prefix=source/', FREEZE)
archive = zipfile.ZipFile(io.BytesIO(source))
assert archive.testzip() is None
# Compare every regular payload with a separate Git tar archive of this freeze.
with tarfile.open(fileobj=io.BytesIO(git('archive', '--format=tar', FREEZE))) as tar:
    files = {member.name: tar.extractfile(member).read() for member in tar.getmembers() if member.isfile()}
zip_files = {name.removeprefix('source/'): archive.read(name) for name in archive.namelist() if not name.endswith('/')}
assert zip_files.keys() == files.keys()
assert all(zip_files[name] == payload for name, payload in files.items())
checks = []
for name in INPUTS:
    path = 'data/input/' + name
    raw = git('show', FREEZE + ':' + path)
    assert archive.read('source/' + path) == raw
    checks.append({'path': path, 'bytes': len(raw), 'sha256': digest(raw)})
pdf = archive.read('source/paper/paper.pdf')
assert digest(pdf) == 'fce3d4f1e39e1e4384985a18d4e6e77da03dcbd29ed72a95a86f90fa8de206b3'
manifest = {
    'scope': 'Already-public frozen Git source archive, including all nine canonical inputs, default code/output, dependencies, LaTeX/PDF and documentation. Packaging only, not new scientific execution or independent referee replication.',
    'ref': 'v0.10.0', 'commit': FREEZE, 'annotated_tag_object': TAG_OBJECT,
    'source_zip_bytes': len(source), 'source_zip_sha256': digest(source),
    'archive_members': len(archive.namelist()), 'regular_file_count': len(files),
    'all_regular_payloads_equal_frozen_git_tar': True, 'canonical_inputs': checks,
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
