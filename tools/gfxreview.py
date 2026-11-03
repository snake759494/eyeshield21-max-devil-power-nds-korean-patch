"""사양 적용 전/후 비교 시트: python tools/gfxreview.py 출력폴더 [키접두사]"""
import sys,collections
sys.path.insert(0,'tools')
from pathlib import Path
from PIL import Image,ImageDraw
import gtext
from gtext import F
from g2d import NCGR,nclr
from cell import NCER,render
from gfxauto import final
out=Path(sys.argv[1]);out.mkdir(exist_ok=True);pre=sys.argv[2] if len(sys.argv)>2 else ''
specs=[s for s in final() if s.get('key',s['f']).startswith(pre)]
files=gtext.run(specs)
pairs=[]
for s in specs:
  for key in ['NCGR','NCBR']:
    gp=F/(s.get('g',s['f'])+'.'+key)
    if gp.exists():break
  c=NCER((F/(s['f']+'.NCER')).read_bytes());pal=nclr((F/(s.get('pal',s.get('g',s['f']))+'.NCLR')).read_bytes())
  a=render(NCGR(gp.read_bytes()),c,pal,s['cells'][0],NCGR(gp.read_bytes()).tiled==1)[0]
  g2=NCGR(files.get(gp,gp.read_bytes()));b=render(g2,c,pal,s['cells'][0],g2.tiled==1)[0]
  pairs.append((s.get('key',s['f']+':'+str(s['cells'][0]))+' '+s['text'],a,b))
PW,PH=1024,1400;pg=0;i=0
while i<len(pairs):
  im=Image.new('RGB',(PW,PH),(255,0,255));d=ImageDraw.Draw(im);x=y=rh=0
  while i<len(pairs):
    t,a,b=pairs[i];sc=2 if a.width<=200 else 1
    A=a.resize((a.width*sc,a.height*sc),0);B=b.resize((b.width*sc,b.height*sc),0)
    w=A.width*2+12;h=A.height+12
    if x+w>PW:x=0;y+=rh;rh=0
    if y+h>PH:break
    im.paste(A,(x,y+11),A);im.paste(B,(x+A.width+6,y+11),B);d.text((x,y),t,fill=(0,0,0))
    x+=max(w,len(t)*7)+8;rh=max(rh,h);i+=1
  im.save(out/f'v{pg:03d}.png');pg+=1
print(len(pairs),pg)
