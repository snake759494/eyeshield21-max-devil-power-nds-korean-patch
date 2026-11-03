"""NSCR(BG 화면) 렌더/역기록"""
import struct
from PIL import Image
from g2d import blocks
class NSCR:
  def __init__(s,d):
    s.d=bytearray(d);p,_=blocks(d)[b'NRCS']
    s.w,s.h=struct.unpack_from('<HH',d,p+8);s.sz=struct.unpack_from('<I',d,p+0x10)[0];s.o=p+0x14
  def ent(s,i):return struct.unpack_from('<H',s.d,s.o+2*i)[0]
  def pos(s,tx,ty):
    """화면 타일 좌표 -> 맵 인덱스 (256폭 초과 시 32x32 블록 배치)"""
    W=s.w//8
    if W<=32:return ty*W+tx
    return (ty//32)*(W*32)+(tx//32)*1024+(ty%32)*32+tx%32
def pix(g,s,x,y):
  """화면 픽셀 -> (그래픽 바이트 오프셋, 니블/바이트, 팔레트뱅크)"""
  e=s.ent(s.pos(x//8,y//8));t=e&0x3ff;hf=(e>>10)&1;vf=(e>>11)&1;pb=e>>12
  xx=x%8;yy=y%8
  if hf:xx=7-xx
  if vf:yy=7-yy
  if g.bpp==4:k=t*64+yy*8+xx;return g.o+k//2,k&1,pb
  return g.o+t*64+yy*8+xx,None,0
def render(g,s,pal):
  im=Image.new('RGB',(s.w,s.h))
  for y in range(s.h):
    for x in range(s.w):
      a,n,pb=pix(g,s,x,y)
      if a>=len(g.d):continue
      v=g.d[a] if n is None else (g.d[a]>>(4*n))&15
      im.putpixel((x,y),pal[(pb*16+v)%len(pal)] if v else pal[0])
  return im
