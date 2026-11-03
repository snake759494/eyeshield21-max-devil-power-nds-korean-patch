"""python tools/csheet.py NCER경로(확장자X) NCGR경로 NCLR경로 출력 : 셀 번호 시트"""
import sys;sys.path.insert(0,'tools')
from cell import *
from PIL import ImageDraw
from pathlib import Path
F=Path('ext/fs/file')
f,gf,pf,out=sys.argv[1:5]
gp=F/(gf+'.NCGR')
if not gp.exists():gp=F/(gf+'.NCBR')
g=NCGR(gp.read_bytes());c=NCER((F/(f+'.NCER')).read_bytes());pal=nclr((F/(pf+'.NCLR')).read_bytes())
ims=[]
for k in range(len(c.cells)):
  try:im=render(g,c,pal,k,g.tiled==1)[0]
  except Exception:im=None
  if im and im.width<=256:ims.append((k,im))
cols=2;W=2*(256+30)
H=0;rows=[]
for i in range(0,len(ims),cols):
  r=ims[i:i+cols];rows.append(r);H+=max(x.height for _,x in r)+4
o=Image.new('RGB',(W,H),(255,0,255));d=ImageDraw.Draw(o);y=0
for r in rows:
  for j,(k,im) in enumerate(r):
    o.paste(im,(j*286+28,y),im);d.text((j*286,y),str(k),fill=(0,0,0))
  y+=max(x.height for _,x in r)+4
o.save(out)
