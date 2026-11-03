"""bg/*.bin 레이어 렌더: bgtrace.json 의 (pal, map, tile) 오프셋 사용"""
import json,struct,ast
from pathlib import Path
from PIL import Image
W=Path(__file__).resolve().parents[1];F=W/'ext/fs/file/bg'
T=json.load(open(W/'survey/bgtrace.json'))
def P(x):
  try:v=ast.literal_eval(x)
  except Exception:return None
  return v
def layers(name):
  """[(bg, mapoff, tileoff, tilesize, palsel, paloff)]"""
  out=[];pal={}
  for e in T.get(name,[]):
    cur={}
    for c in e['calls']:
      f=c[0];a=[P(x) for x in c[1:5]]
      if f in('palM','palS') and a[0] and a[0][0]=='b':pal[f]=a[0][1]
      elif f=='map' and a[0] and a[2] and a[2][0]=='b':cur[a[0][1]]=dict(bg=a[0][1],map=a[2][1])
      elif f=='tile' and a[0] and a[1] and a[1][0]=='b' and a[0][1] in cur:
        L=cur.pop(a[0][1]);L.update(tile=a[1][1],tsize=a[2][1] if a[2] else 0,pal=pal.get('palM' if L['bg']<4 else 'palS'))
        out.append(L)
  return out
def colors(d,o):
  return [((v&31)<<3,((v>>5)&31)<<3,((v>>10)&31)<<3) for v in struct.unpack_from('<256H',d,o)] if o is not None else [(i,i,i) for i in range(256)]
def render(name,L,bpp=None):
  d=(F/(name+'.bin')).read_bytes();pal=colors(d,L['pal'])
  ents=struct.unpack_from('<768H',d,L['map'])
  mx=max(e&0x3ff for e in ents)
  if bpp is None:bpp=4 if (mx+1)*32<=L['tsize']+32 and (mx+1)*64>L['tsize']+64 else (8 if (mx+1)*64<=L['tsize']+64 else 4)
  im=Image.new('RGB',(256,192))
  ts=32 if bpp==4 else 64
  for i,e in enumerate(ents):
    t=e&0x3ff;hf=(e>>10)&1;vf=(e>>11)&1;pb=e>>12
    for yy in range(8):
      for xx in range(8):
        sx=7-xx if hf else xx;sy=7-yy if vf else yy
        if bpp==4:
          o=L['tile']+t*32+(sy*8+sx)//2
          v=(d[o]>>(4*(sx&1)))&15 if o<len(d) else 0;c=pal[pb*16+v] if v else None
        else:
          o=L['tile']+t*64+sy*8+sx;v=d[o] if o<len(d) else 0;c=pal[v] if v else None
        if c:im.putpixel(((i%32)*8+xx,(i//32)*8+yy),c)
  return im,bpp
if __name__=='__main__':
  import sys
  from PIL import ImageDraw
  names=sorted(T);O=W/'survey/bgbin';O.mkdir(exist_ok=True);ims=[]
  for n in names:
    if not (F/(n+'.bin')).exists():continue
    for k,L in enumerate(layers(n)):
      try:im,b=render(n,L)
      except Exception as e:print('err',n,k,e);continue
      if im.getbbox():ims.append((f'{n}#{k} bg{L["bg"]} {b}bpp',im))
  pg=0;i=0
  while i<len(ims):
    cur=Image.new('RGB',(1056,1224),(255,0,255));dr=ImageDraw.Draw(cur);x=y=0
    while i<len(ims) and y+204<=1224:
      t,im=ims[i];cur.paste(im,(x,y+10));dr.text((x,y),t,fill=(0,0,0));x+=264
      if x+256>1056:x=0;y+=204
      i+=1
    cur.save(O/f'r{pg:03d}.png');pg+=1
  print(len(ims),pg)
