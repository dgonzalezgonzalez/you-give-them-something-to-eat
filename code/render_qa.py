"""Render PDF pages for manual visual inspection; optional PyMuPDF/Pillow."""
from pathlib import Path
import pymupdf
from PIL import Image, ImageDraw

root=Path(__file__).resolve().parents[1]
dest=root/'tmp/pdf'; dest.mkdir(parents=True,exist_ok=True)
doc=pymupdf.open(root/'paper/paper.pdf')
thumbs=[]
for n,page in enumerate(doc):
    pix=page.get_pixmap(matrix=pymupdf.Matrix(1.4,1.4),alpha=False)
    pix.save(dest/f'page-{n+1:02d}.png')
    img=Image.open(dest/f'page-{n+1:02d}.png')
    img.thumbnail((270,360))
    cell=Image.new('RGB',(285,395),'#eeeeee')
    cell.paste(img,((285-img.width)//2,25))
    ImageDraw.Draw(cell).text((12,7),str(n+1),fill='black')
    thumbs.append(cell)
    print(n+1, page.get_text().splitlines()[0],len(page.get_text()))
for start in range(0,len(thumbs),8):
    sheet=Image.new('RGB',(1140,790),'white')
    for j,img in enumerate(thumbs[start:start+8]):sheet.paste(img,((j%4)*285,(j//4)*395))
    sheet.save(dest/f'contact-{start//8+1}.png')
