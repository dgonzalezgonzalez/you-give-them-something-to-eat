"""Small public views of existing CC BY extracts for file-size-limited readers.

These are exact row partitions with repeated original headers, not new inputs.
Default scientific computation continues to read the immutable input CSVs.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'data/public-views'
NAMES=['households.csv','revision_households.csv','children.csv']

def sha(data):return hashlib.sha256(data).hexdigest()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--verify',action='store_true');args=parser.parse_args()
    references={}
    for name in ['input-reference.json','revision-reference.json']:
        references.update(json.loads((ROOT/'data/input'/name).read_text())['files'])
    if not args.verify:
        DEST.mkdir(parents=True,exist_ok=True);manifest={}
        for name in NAMES:
            data=(ROOT/'data/input'/name).read_bytes();assert sha(data)==references[name]
            lines=data.splitlines(keepends=True);parts=[]
            for start in range(1,len(lines),1000):
                chunk=lines[0]+b''.join(lines[start:start+1000]);number=len(parts)+1
                part=f'{Path(name).stem}-{number:03d}.csv';(DEST/part).write_bytes(chunk)
                parts.append({'path':part,'data_rows':min(1000,len(lines)-start),'sha256':sha(chunk)})
            manifest[name]={'original_sha256':sha(data),'original_rows':len(lines)-1,'parts':parts}
        (DEST/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
    manifest=json.loads((DEST/'manifest.json').read_text())
    count=0
    for name in NAMES:
        item=manifest[name];assert item['original_sha256']==references[name]
        chunks=[];headers=[]
        for part in item['parts']:
            chunk=(DEST/part['path']).read_bytes();assert sha(chunk)==part['sha256']
            lines=chunk.splitlines(keepends=True);assert len(lines)-1==part['data_rows']
            headers.append(lines[0]);chunks.append(b''.join(lines[1:]));count+=1
        assert all(h==headers[0] for h in headers)
        reconstructed=headers[0]+b''.join(chunks)
        assert sha(reconstructed)==references[name]
        assert reconstructed==(ROOT/'data/input'/name).read_bytes()
    print(f'{count} public CSV parts reconstruct all three immutable source extracts byte for byte.')
    subprocess.run([sys.executable,str(ROOT/'code/public_review_bytes.py'),'--verify'],check=True)

if __name__=='__main__':main()
