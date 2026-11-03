"""8bpp NCER 셀 렌더: python tools/c8.py gam/파일 팔레트 출력.png [ext]"""
import sys;sys.path.insert(0,'tools')
from cell import NCER
from g2d import NCGR,nclr
from pathlib import Path
from PIL import Image,ImageDraw
F=Path('ext/fs/file')
def pix8(g,c,o):
  t0=o['tile']<<c.mapmode;tw=o['w']//8;out={};lin=getattr(g,'_lin',False)
  for yy in range(o['h']):
    for xx in range(o['w']):
      k=t0*32+yy*o['w']+xx if lin else t0*32+((yy//8)*tw+xx//8)*64+(yy%8)*8+xx%8
      X=o['w']-1-xx if o['hf'] else xx;Y=o['h']-1-yy if o['vf'] else yy
      out[(X,Y)]=k
  return out
def render8(g,c,pal,cell,ext=False):
  oams=c.cells[cell]
  if not oams:return None
  x0=min(o['x'] for o in oams);y0=min(o['y'] for o in oams)
  x1=max(o['x']+o['w'] for o in oams);y1=max(o['y']+o['h'] for o in oams)
  im=Image.new('RGBA',(x1-x0,y1-y0),(0,0,0,0))
  for o in reversed(oams):
    for (X,Y),k in pix8(g,c,o).items():
      v=g.d[g.o+k] if g.o+k<len(g.d) else 0
      if v:im.putpixel((o['x']-x0+X,o['y']-y0+Y),pal[((o['pal']*256 if ext else 0)+v)%len(pal)]+(255,))
  return im
if __name__=='__main__':
  f,pf,out=sys.argv[1:4];ext=len(sys.argv)>4
  gp=F/(f+'.NCGR');lin=not gp.exists()
  if lin:gp=F/(f+'.NCBR')
  g=NCGR(gp.read_bytes());g._lin=lin or g.tiled==1;c=NCER((F/(f+'.NCER')).read_bytes());pal=nclr((F/(pf+'.NCLR')).read_bytes())
  ims=[(k,render8(g,c,pal,k,ext)) for k in range(len(c.cells))];ims=[(k,i) for k,i in ims if i]
  W=1024;x=y=rh=0;pos=[]
  for k,i in ims:
    if x+i.width+30>W:x=0;y+=rh+4;rh=0
    pos.append((k,i,x,y));x+=i.width+34;rh=max(rh,i.height)
  o=Image.new('RGB',(W,y+rh+4),(255,0,255));d=ImageDraw.Draw(o)
  for k,i,x,y in pos:o.paste(i,(x+24,y),i);d.text((x,y),str(k),fill=(0,0,0))
  o.save(out)
