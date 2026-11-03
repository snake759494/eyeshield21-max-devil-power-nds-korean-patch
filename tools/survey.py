"""그래픽 전수조사 시트: 모든 NCER 셀(중복 제거)을 페이지로 모음 -> survey/pNNN.png + survey/index.json"""
import sys,json,hashlib
sys.path.insert(0,'tools')
from pathlib import Path
from PIL import Image,ImageDraw
from cell import NCER,render
from g2d import NCGR,nclr
F=Path('ext/fs/file');O=Path('survey');O.mkdir(exist_ok=True)
PW=1024;PH=1400
def pal_for(s):
  for c in [s.with_suffix('.NCLR')]+sorted(s.parent.glob(s.name.split('_')[0]+'*.NCLR')):
    if c.exists():return nclr(c.read_bytes())
  return [(i*16%256,)*3 for i in range(256)]
items=[];seen=set()
for p in sorted(F.rglob('*.NCER')):
  s=p.with_suffix('');gp=next((x for x in [s.with_suffix('.NCGR'),s.with_suffix('.NCBR')] if x.exists()),None)
  if not gp:continue
  try:g=NCGR(gp.read_bytes());c=NCER(p.read_bytes());pal=pal_for(s)
  except Exception as e:print('skip',p,e);continue
  for k in range(len(c.cells)):
    try:im=render(g,c,pal,k,g.tiled==1)[0]
    except Exception:im=None
    if im is None or im.getbbox() is None:continue
    h=hashlib.md5(im.tobytes()).hexdigest()
    if h in seen:continue
    seen.add(h)
    if im.width>PW:im=im.crop((0,0,PW,im.height))
    items.append((s.relative_to(F).as_posix(),k,im))
pages=[];idx={};x=y=rh=0;cur=Image.new('RGB',(PW,PH),(255,0,255));d=ImageDraw.Draw(cur)
def flush():
  global cur,d
  cur.save(O/f'p{len(pages):03d}.png');pages.append(1);cur=Image.new('RGB',(PW,PH),(255,0,255));d=ImageDraw.Draw(cur)
for f,k,im in items:
  w=im.width+4;h=im.height+12
  if x+w>PW:x=0;y+=rh;rh=0
  if y+h>PH:flush();x=y=rh=0
  cur.paste(im,(x,y+10),im);d.text((x,y),f'{f.split("/")[-1]}:{k}',fill=(0,0,0))
  idx.setdefault(len(pages),[]).append(f'{f}:{k}')
  x+=max(w,len(f.split('/')[-1])*6+20);rh=max(rh,h)
flush()
json.dump(idx,open(O/'index.json','w'),indent=0)
print(len(items),len(pages))
