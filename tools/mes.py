"""gam/mes.NCBR: 셀마다 자기 블록(타일 0부터)이 순서대로 붙은 선형 4bpp 비트맵"""
import sys;sys.path.insert(0,'tools')
from cell import NCER
from g2d import NCGR,nclr
from pathlib import Path
from PIL import Image,ImageDraw
F=Path('ext/fs/file/gam')
def bases(c):
  b=[];o=0
  for cl in c.cells:
    b.append(o)
    if cl:o+=max(x['tile']*128+x['w']*x['h']//2 for x in cl);o=(o+127)//128*128
  return b
def pixmap(c,k,base):
  """셀 좌표 (x,y)->(바이트오프셋(데이터 기준), 니블, oam)  위 OAM 우선"""
  oams=c.cells[k];x0=min(o['x'] for o in oams);y0=min(o['y'] for o in oams);m={}
  for o in oams:
    for yy in range(o['h']):
      for xx in range(o['w']):
        X=o['w']-1-xx if o['hf'] else xx;Y=o['h']-1-yy if o['vf'] else yy
        q=(o['x']-x0+X,o['y']-y0+Y)
        if q in m:continue
        n=base+o['tile']*256+yy*o['w']+xx  # 니블 단위
        m[q]=(n,o)
  return m
def render(g,c,pal,k,b):
  oams=c.cells[k]
  if not oams:return None
  W=max(o['x']+o['w'] for o in oams)-min(o['x'] for o in oams);H=max(o['y']+o['h'] for o in oams)-min(o['y'] for o in oams)
  im=Image.new('RGBA',(W,H),(0,0,0,0))
  for q,(n,o) in pixmap(c,k,b[k]*2).items():
    a=g.o+n//2;v=(g.d[a]>>(4*(n&1)))&15 if a<len(g.d) else 0
    if v:im.putpixel(q,pal[(o['pal']*16+v)%len(pal)]+(255,))
  return im
if __name__=='__main__':
  g=NCGR((F/'mes.NCBR').read_bytes());c=NCER((F/'mes.NCER').read_bytes());b=bases(c);print([hex(x) for x in b],hex(g.size))
  pal=nclr((F/((sys.argv[1] if len(sys.argv)>1 else 'game_cmn')+'.NCLR')).read_bytes())
  ims=[(k,render(g,c,pal,k,b)) for k in range(len(c.cells))]
  W=1024;x=y=rh=0;o=Image.new('RGB',(W,2000),(255,0,255));d=ImageDraw.Draw(o)
  for k,i in ims:
    if i is None:continue
    if x+i.width+24>W:x=0;y+=rh+4;rh=0
    o.paste(i,(x+20,y),i);d.text((x,y),str(k),fill=(0,0,0));x+=i.width+24;rh=max(rh,i.height)
  o.crop((0,0,W,y+rh+4)).save('shots/mes.png')
