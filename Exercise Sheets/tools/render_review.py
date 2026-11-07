"""Render all deliverables with Poppler and prepare contact sheets for visual QA."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import subprocess
import json
from datetime import datetime
from PIL import Image, ImageDraw
from pypdf import PdfReader
from cache_paths import CACHE_ROOT

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=CACHE_ROOT/'visual_review'/datetime.now().strftime('%Y%m%d_%H%M%S_%f')


def render():
    OUTPUT.mkdir(parents=True,exist_ok=True)
    index=[]
    for variant in ('de','de_solutions'):
        for pdf in sorted((ROOT/'build'/variant).glob('*.pdf')):
            # Combined files repeat these pages unchanged; verify their page order separately.
            if pdf.name.startswith('_'):
                continue
            folder=OUTPUT/variant/pdf.stem
            folder.mkdir(parents=True,exist_ok=True)
            subprocess.run(['pdftoppm','-scale-to','1400','-png',str(pdf),str(folder/'page')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            pages=sorted(folder.glob('page-*.png'))
            assert len(pages)==len(PdfReader(pdf).pages)
            # Text pages: four per sheet. Preserved PDF pages: six per sheet.
            count=4 if variant=='de' else 6
            columns=2 if variant=='de' else 3
            thumb_width=650 if variant=='de' else 520
            thumb_height=round(thumb_width*2**.5)
            for start in range(0,len(pages),count):
                panel=Image.new('RGB',(columns*thumb_width,2*(thumb_height+28)), '#dddddd')
                draw=ImageDraw.Draw(panel)
                for i,path in enumerate(pages[start:start+count]):
                    im=Image.open(path).convert('RGB')
                    im.thumbnail((thumb_width-8,thumb_height))
                    x=(i%columns)*thumb_width+4; y=(i//columns)*(thumb_height+28)
                    draw.text((x,y+5),f'{variant}/{pdf.stem} | {start+i+1}',fill='black')
                    panel.paste(im,(x,y+26))
                dest=folder/f'contact_{start//count+1:02}.png'
                panel.save(dest)
                index.append(str(dest))
    (OUTPUT/'index.json').write_text(json.dumps(index,indent=2),encoding='utf-8')
    (CACHE_ROOT/'visual_review/latest.json').write_text(json.dumps(str(OUTPUT)),encoding='utf-8')
    print(f'Rendered all pages; {len(index)} contact sheets under {OUTPUT}.')


if __name__=='__main__': render()
