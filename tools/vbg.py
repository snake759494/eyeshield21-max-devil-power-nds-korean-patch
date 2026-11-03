"""스냅샷(snaps/이름)의 서브 BG(4bpp) 렌더/타일 위치 조회"""
import struct,sys
from pathlib import Path
from PIL import Image
def load(name):
  S=Path('snaps')/name
  return {k:(S/(k+'.bin')).read_bytes() for k in ['ioB','bgB','pal']}
def bgcnt(s,i):
  c=struct.unpack_from('<H',s['ioB'],8+2*i)[0];return ((c>>2)&15)*0x4000,((c>>8)&31)*0x800,(c>>7)&1
def pal(s):
  return [((v&31)<<3,((v>>5)&31)<<3,((v>>10)&31)<<3) for v in struct.unpack_from('<256H',s['pal'],0x400)]
def ent(s,i,tx,ty):
  cb,sb,_=bgcnt(s,i);return struct.unpack_from('<H',s['bgB'],sb+(ty*32+tx)*2)[0]
def render(s,i):
  cb,sb,b8=bgcnt(s,i);P=pal(s);im=Image.new('RGBA',(256,192),(0,0,0,0));v=s['bgB']
  for ty in range(24):
    for tx in range(32):
      e=ent(s,i,tx,ty);t=e&0x3ff;hf=(e>>10)&1;vf=(e>>11)&1;pb=e>>12
      for y in range(8):
        for x in range(8):
          sx=7-x if hf else x;sy=7-y if vf else y
          b=v[cb+t*32+sy*4+sx//2];n=(b>>(4*(sx&1)))&15
          if n:im.putpixel((tx*8+x,ty*8+y),P[pb*16+n]+(255,))
  return im
if __name__=='__main__':
  s=load(sys.argv[1])
  for i in (0,1):render(s,i).save(f'shots/vbg{i}.png')
