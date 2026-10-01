"""Small ASCII views of already public inputs, separate from science inputs.

Reassemble gzip/base64 parts and verify original bytes without a large CSV
download. This is a publication convenience, not new data or replication.
"""
from pathlib import Path
import argparse,base64,gzip,hashlib,io,json
ROOT=Path(__file__).resolve().parents[1];DEST=ROOT/'data/review-bytes'
def sha(value):return hashlib.sha256(value).hexdigest()
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--verify',action='store_true')
    parser.add_argument('--reconstruct-to',type=Path)
    args=parser.parse_args()
    if not args.verify and args.reconstruct_to is None:
        DEST.mkdir(exist_ok=True);items={}
        references={}
        for leaf in ['input-reference.json','revision-reference.json']:
            references.update(json.loads((ROOT/'data/input'/leaf).read_text())['files'])
        for source in sorted((ROOT/'data/input').glob('*')):
            if not source.is_file():continue
            local=source.read_bytes()
            if source.name in references and sha(local)!=references[source.name]:raise ValueError('Immutable science input differs')
            original=local.replace(b'\r\n',b'\n');stream=io.BytesIO()
            with gzip.GzipFile(filename='',mode='wb',fileobj=stream,mtime=0) as zipped:zipped.write(original)
            encoded=base64.b64encode(stream.getvalue());parts=[]
            for start in range(0,len(encoded),12000):
                name=source.name+f'.{len(parts):03d}.b64'
                value=encoded[start:start+12000]+b'\n';(DEST/name).write_bytes(value)
                parts.append({'path':name,'bytes':len(value),'sha256':sha(value)})
            items[source.name]={'original_bytes':len(original),'original_sha256':sha(original),'parts':parts}
        manifest={'encoding':'Concatenate base64 text parts in listed order, ignore line whitespace, base64-decode, gzip-decompress. Verify each part and final original byte SHA256.',
                  'scope':'Exact compressed views of the published LF bytes of existing public CC BY inputs; canonical data/input files remain default scientific inputs. Immutable scientific reference hashes are checked before generation. Ancillary local CRLF is normalized to the Git LF stream. No new research observations or anonymization claim.',
                  'files':items}
        (DEST/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8',newline='\n')
        (DEST/'README.md').write_text('# Small public input byte views\n\nEach text part is at most 12,001 bytes. Reassembly instructions and original/part SHA256 values are in manifest.json. This can support readers whose interfaces cannot retrieve large CSVs. All source observations were already public in data/input under CC BY 4.0.\n\nVerify: `python code/public_review_bytes.py --verify`. Reconstruct into a separate destination: `python code/public_review_bytes.py --reconstruct-to tmp/reassembled-inputs`. The script never replaces data/input. These inspection views are outside the default numerical master and do not prove independent replication.\n',encoding='utf8',newline='\n')
    manifest=json.loads((DEST/'manifest.json').read_text());count=0
    if args.reconstruct_to is not None:
        destination=args.reconstruct_to.resolve()
        if destination==(ROOT/'data/input').resolve():raise ValueError('Do not replace immutable inputs')
        destination.mkdir(parents=True,exist_ok=True)
    for name,item in manifest['files'].items():
        if Path(name).name!=name:raise ValueError('Invalid manifest leaf')
        encoded=[]
        for part in item['parts']:
            if Path(part['path']).name!=part['path']:raise ValueError('Invalid part leaf')
            value=(DEST/part['path']).read_bytes()
            if sha(value)!=part['sha256'] or len(value)!=part['bytes']:raise ValueError('Part hash/size mismatch')
            encoded.append(b''.join(value.split()));count+=1
        original=gzip.decompress(base64.b64decode(b''.join(encoded),validate=True))
        if len(original)!=item['original_bytes'] or sha(original)!=item['original_sha256']:raise ValueError('Original hash/size mismatch')
        if original!=(ROOT/'data/input'/name).read_bytes().replace(b'\r\n',b'\n'):raise ValueError('Published LF canonical input differs')
        if args.reconstruct_to is not None:
            target=destination/name
            if target.exists() and target.read_bytes()!=original:raise ValueError('Existing destination differs')
            target.write_bytes(original)
    print(count,'public ASCII parts reconstruct',len(manifest['files']),'canonical inputs exactly')
if __name__=='__main__':main()
