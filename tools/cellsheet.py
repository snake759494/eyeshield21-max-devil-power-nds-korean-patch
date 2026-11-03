import sys;sys.path.insert(0,'tools')
from cell import *
from PIL import ImageDraw
from pathlib import Path
O=Path('gfxcell');O.mkdir(exist_ok=True);F=Path('ext/fs/file')
def sheet(ncer):
  c=NCER(open(ncer,'rb').read())
  gp=ncer.with_suffix('.NCGR');lin=False
  if not gp.exists():gp=ncer.with_suffix('.NCBR');lin=True
  if not gp.exists():return
  g=NCGR(open(gp,'rb').read());lin=lin or g.tiled==1
  pp=ncer.with_suffix('.NCLR')
  if not pp.exists():
    l=sorted(ncer.parent.glob(ncer.stem.split('_')[0]+'*.NCLR')) or sorted(ncer.parent.glob('*.NCLR'))
    if not l:return
    pp=l[0]
  pal=nclr(open(pp,'rb').read())
  ims=[]
  for i in range(len(c.cells)):
    try:im,_=render(g,c,pal,i,lin)
    except Exception:im=None
    if im and im.width<=256 and im.height<=256:ims.append((i,im))
  if not ims:return
  W=max(i.width for _,i in ims)+24;H=sum(i.height+3 for _,i in ims)
  if H>4000:H=4000
  out=Image.new('RGB',(W,H),(255,0,255));d=ImageDraw.Draw(out);y=0
  for n,i in ims:
    if y>H-10:break
    out.paste(i,(22,y),i);d.text((0,y),str(n),fill=(0,0,0));y+=i.height+3
  out.save(O/(ncer.parent.name+'__'+ncer.stem+'.png'))
for p in sorted(F.rglob('*.NCER')):
  try:sheet(p)
  except Exception as e:print('ERR',p,e)
