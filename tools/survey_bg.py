"""NSCR 화면 전수조사 시트 -> survey/bNNN.png"""
import sys,json
sys.path.insert(0,'tools')
from pathlib import Path
from PIL import Image,ImageDraw
from g2d import NCGR,nclr
from nscr import NSCR,render
F=Path('ext/fs/file');O=Path('survey')
ims=[]
for p in sorted(F.rglob('*.NSCR')):
  s=p.with_suffix('')
  import re
  n=s.name;gp=None
  while n and not gp:
    gp=next((x for x in [s.parent/(n+'.NCGR'),s.parent/(n+'.NCBR')] if x.exists()),None)
    if not gp:n=re.sub(r'(_[^_]*|\d)$','',n) if re.search(r'(_[^_]*|\d)$',n) else ''
  if not gp:print('no g',p);continue
  lp=s.parent/(n+'.NCLR')
  if not lp.exists():lp=next(iter(sorted(s.parent.glob(n.split('_')[0]+'*.NCLR'))),lp)
  try:
    g=NCGR(gp.read_bytes());sc=NSCR(p.read_bytes())
    pal=nclr(lp.read_bytes()) if lp.exists() else [(i*16%256,)*3 for i in range(256)]
    im=render(g,sc,pal)
  except Exception as e:print('err',p,e);continue
  if im.width>512:im=im.crop((0,0,512,im.height))
  if im.height>384:im=im.crop((0,0,im.width,384))
  ims.append((s.relative_to(F).as_posix(),im))
idx={};pg=0;i=0
while i<len(ims):
  cur=Image.new('RGB',(1040,1220),(255,0,255));d=ImageDraw.Draw(cur);x=y=rh=0;idx[pg]=[]
  while i<len(ims):
    f,im=ims[i];w=im.width+8;h=im.height+12
    if x+w>1040:x=0;y+=rh;rh=0
    if y+h>1220:break
    cur.paste(im,(x,y+10));d.text((x,y),f,fill=(0,0,0));idx[pg].append(f);x+=w;rh=max(rh,h);i+=1
  cur.save(O/f'b{pg:03d}.png');pg+=1
json.dump(idx,open(O/'index_bg.json','w'),indent=0);print(len(ims),pg)
