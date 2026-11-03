"""NCER 셀 렌더/역기록 (4bpp 1D)"""
import struct
from PIL import Image
from g2d import blocks,NCGR,nclr
SH=[[(8,8),(16,16),(32,32),(64,64)],[(16,8),(32,8),(32,16),(64,32)],[(8,16),(8,32),(16,32),(32,64)]]
class NCER:
  def __init__(s,d):
    p,_=blocks(d)[b'KBEC'];s.d=d
    n,attr,off,s.mapmode=struct.unpack_from('<HHII',d,p+8)
    es=16 if attr==1 else 8;base=p+8+off;oamb=base+n*es
    s.cells=[]
    for i in range(n):
      no,ca,oo=struct.unpack_from('<HHI',d,base+i*es)
      oams=[]
      for k in range(no):
        a0,a1,a2=struct.unpack_from('<HHH',d,oamb+oo+6*k)
        y=a0&0xff;y=y-256 if y>=128 else y
        x=a1&0x1ff;x=x-512 if x>=256 else x
        w,h=SH[(a0>>14)&3][(a1>>14)&3]
        rs=(a0>>8)&1
        oams.append(dict(x=x,y=y,w=w,h=h,tile=a2&0x3ff,pal=a2>>12,hf=0 if rs else (a1>>12)&1,vf=0 if rs else (a1>>13)&1,bpp8=(a0>>13)&1))
      s.cells.append(oams)
def objpix(g,o,shift,linear):
  """OAM 하나의 (x,y)->(파일오프셋, 니블) 목록"""
  t0=o['tile']<<shift;tw=o['w']//8;out={}
  for yy in range(o['h']):
    for xx in range(o['w']):
      if linear:  # NCBR: 객체 단위 선형 비트맵
        k=t0*64+yy*o['w']+xx
      else:
        k=(t0+(yy//8)*tw+xx//8)*64+(yy%8)*8+xx%8
      X=o['w']-1-xx if o['hf'] else xx;Y=o['h']-1-yy if o['vf'] else yy
      out[(X,Y)]=k
  return out
def render(g,c,pal,cell,linear=False):
  oams=c.cells[cell]
  if not oams:return None,None
  x0=min(o['x'] for o in oams);y0=min(o['y'] for o in oams)
  x1=max(o['x']+o['w'] for o in oams);y1=max(o['y']+o['h'] for o in oams)
  im=Image.new('RGBA',(x1-x0,y1-y0),(0,0,0,0));idx={}
  for oi,o in reversed(list(enumerate(oams))):
    for (X,Y),k in objpix(g,o,c.mapmode,linear).items():
      b=g.d[g.o+k//2] if g.o+k//2<len(g.d) else 0;v=(b>>(4*(k&1)))&15
      if v:
        im.putpixel((o['x']-x0+X,o['y']-y0+Y),pal[(o['pal']*16+v)%len(pal)]+(255,))
      idx[(o['x']-x0+X,o['y']-y0+Y)]=(k,o['pal'],v,oi)
  return im,(x0,y0,idx)
def write(g,c,cell,ix,linear=False,written=None):
  """ix: {(x,y):v} 셀 좌표 기준 4bpp 값 -> 해당 OAM 픽셀에 기록(맨 위 OAM 우선)"""
  oams=c.cells[cell];x0=min(o['x'] for o in oams);y0=min(o['y'] for o in oams)
  done=set()
  for o in oams:
    for (X,Y),k in objpix(g,o,c.mapmode,linear).items():
      p=(o['x']-x0+X,o['y']-y0+Y)
      if p in ix and p not in done:
        done.add(p)
        if written is not None:
          if k in written:continue
          written.add(k)
        a=g.o+k//2;b=g.d[a]
        g.d[a]=(b&0xf0)|ix[p] if k&1==0 else (b&0x0f)|(ix[p]<<4)
