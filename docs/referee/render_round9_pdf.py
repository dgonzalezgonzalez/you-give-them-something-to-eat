"""Optional public page images of the already-public immutable paper PDF.

These help review by ordinary public links. They are author-side renderings,
not ChatGPT uploads, independent referee rendering or default science inputs.
Requires optional PyMuPDF; no change to the compiled PDF or master.
"""
from pathlib import Path
import hashlib,json,subprocess
import pymupdf

ROOT=Path(__file__).resolve().parents[2]
SOURCE='559dd4552e7b1897063c0e880ea8325439e794e8'
DEST=ROOT/'docs/referee/round-9-review/pdf';DEST.mkdir(parents=True,exist_ok=True)
data=subprocess.check_output(['git','show',SOURCE+':paper/paper.pdf'],cwd=ROOT)
doc=pymupdf.open(stream=data,filetype='pdf');records=[]
for index,page in enumerate(doc,1):
    pix=page.get_pixmap(matrix=pymupdf.Matrix(1.4,1.4),alpha=False)
    content=pix.tobytes('png');name=f'page-{index:02d}.png'
    (DEST/name).write_bytes(content)
    records.append({'file':name,'page':index,'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest(),'width':pix.width,'height':pix.height})
manifest={'scope':'Author-generated public raster renderings of the exact stated already-public PDF. A referee may inspect these by ordinary public links, but their existence is not evidence the referee inspected them, independently rendered the PDF, authenticated image bytes or executed the master. Not local uploads to ChatGPT.','source_commit':SOURCE,'pdf_path':'paper/paper.pdf','pdf_sha256':hashlib.sha256(data).hexdigest(),'pymupdf_version':pymupdf.VersionBind,'scale':1.4,'pages':len(doc),'files':records}
(DEST/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8',newline='\n')
lines=['# Public paper page images\n\n','Author-side renderings of scientific source `'+SOURCE+'`; [exact public PDF](https://github.com/dgonzalezgonzalez/you-give-them-something-to-eat/raw/'+SOURCE+'/paper/paper.pdf). [Manifest](manifest.json) records the PDF/image hashes and rendering scope. No ninth submission or independent PDF review is claimed.\n\n']
for row in records:lines.append(f"- [Page {row['page']}]({row['file']})\n")
(DEST/'README.md').write_text(''.join(lines),encoding='utf8',newline='\n')
print(json.dumps({'pages':len(doc),'total_png_bytes':sum(z['bytes'] for z in records),'largest_png_bytes':max(z['bytes'] for z in records),'pdf_sha256':manifest['pdf_sha256']}))
