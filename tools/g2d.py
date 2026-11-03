"""Nitro 2D (NCLR/NCGR/NCER/NSCR) 읽기·쓰기"""
import struct
from PIL import Image
def blocks(d):
  hs=struct.unpack_from('<H',d,0xc)[0];nb=struct.unpack_from('<H',d,0xe)[0];p=hs;out={}
  for _ in range(nb):
    t=bytes(d[p:p+4]);sz=struct.unpack_from('<I',d,p+4)[0];out[t]=(p,sz);p+=sz
  return out
def nclr(d):
  p,_=blocks(d)[b'TTLP'];bpp=3 if struct.unpack_from('<I',d,p+8)[0]==3 else 4
  sz=struct.unpack_from('<I',d,p+0x10)[0];o=p+0x18+0
  off=struct.unpack_from('<I',d,p+0x14)[0];o=p+8+off
  cols=[]
  for i in range(min(sz,len(d)-o)//2):
    v=struct.unpack_from('<H',d,o+2*i)[0];cols.append(((v&31)<<3,((v>>5)&31)<<3,((v>>10)&31)<<3))
  return cols
class NCGR:
  def __init__(s,d):
    s.d=bytearray(d);p,_=blocks(d)[b'RAHC'];s.p=p
    s.th,s.tw,s.fmt=struct.unpack_from('<HHI',d,p+8)
    s.bpp=4 if s.fmt==3 else 8
    s.map=struct.unpack_from('<I',d,p+0x10)[0]
    s.tiled=struct.unpack_from('<I',d,p+0x14)[0]
    s.size=struct.unpack_from('<I',d,p+0x18)[0];s.o=p+8+struct.unpack_from('<I',d,p+0x1c)[0]
    s.tsz=32 if s.bpp==4 else 64;s.n=s.size//s.tsz
  def tile(s,i):
    o=s.o+i*s.tsz;t=s.d[o:o+s.tsz]
    if s.bpp==4:return [ (t[k>>1]>>(4*(k&1)))&15 for k in range(64)]
    return list(t)
  def settile(s,i,px):
    o=s.o+i*s.tsz
    if s.bpp==4:s.d[o:o+32]=bytes(px[2*k]|(px[2*k+1]<<4) for k in range(32))
    else:s.d[o:o+64]=bytes(px)
def sheet(g,pal,cols=32,pb=0):
  n=g.n;rows=(n+cols-1)//cols;im=Image.new('RGB',(cols*8,rows*8),(255,0,255))
  for i in range(n):
    t=g.tile(i);x0=(i%cols)*8;y0=(i//cols)*8
    for k,v in enumerate(t):
      c=pal[(pb*16+v)%len(pal)] if pal else (v*16,)*3
      im.putpixel((x0+k%8,y0+k//8),c if v else (40,40,40))
  return im
