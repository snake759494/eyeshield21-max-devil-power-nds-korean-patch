"""8bpp OBJ(gam/scene2d_*, score_no) 글자 교체"""
import sys,collections
sys.path.insert(0,str(__import__('pathlib').Path(__file__).parent))
from cell import NCER
from g2d import NCGR,nclr
from c8 import pix8
from gtext import textmask
from mestext import mask,ring
from pathlib import Path
F=Path(__file__).resolve().parents[1]/'ext/fs/file/gam'
# (파일, 셀, 글자 영역(셀 좌표), 한글, 방식)
S=[('scene2d_kick',2,(58,9,236,39),'중심을 슬라이드!','ban'),
   ('scene2d_touch',0,(58,9,236,39),'중심을 터치!','ban'),
   ('scene2d_scratch',1,(56,9,200,39),'화면을 문질러라!','ban'),
   ('score_no',13,(0,0,48,16),'에디트','tag')]
def pmap(g,c,k):
  oams=c.cells[k];x0=min(o['x'] for o in oams);y0=min(o['y'] for o in oams);m={}
  for o in oams:
    for q,a in pix8(g,c,o).items():
      Q=(o['x']-x0+q[0],o['y']-y0+q[1])
      if Q not in m:m[Q]=a
  return m
def apply(g,c,pal,k,rect,t,mode):
  pm=pmap(g,c,k);ext=c.cells[k][0]['pal']*256
  get=lambda q:g.d[g.o+pm[q]]
  col=lambda v:pal[(ext+v)%len(pal)]
  X0,Y0,X1,Y1=rect;R=[(x,y) for y in range(Y0,Y1) for x in range(X0,X1) if (x,y) in pm]
  vs=collections.Counter(get(q) for q in R if get(q))
  lum=lambda v:sum(col(v))
  white=max(vs,key=lum);dark=min(vs,key=lum)
  new={}
  if mode=='ban':
    red=[v for v in vs if col(v)[0]>150 and col(v)[1]<90]
    bg=white
    for y in range(Y0,Y1):
      xs=[x for x in range(X0-40,X1+40) if (x,y) in pm and get((x,y)) in red]
      for x in range(X0,X1):
        if (x,y) not in pm:continue
        new[(x,y)]=red[0] if xs and min(xs)<=x<=max(xs) else bg
    m=mask(t,999,Y1-Y0-10,0.25)
    if m.width>X1-X0-8:m=m.resize((X1-X0-8,m.height))
    ox=X0+(X1-X0-m.width)//2;oy=Y0+(Y1-Y0-m.height)//2
    on={(ox+x,oy+y) for y in range(m.height) for x in range(m.width) if m.getpixel((x,y))}
    r1=ring(on,1);r2=ring(on|r1,1)
    for q in r2:new[q]=dark
    for q in r1:new[q]=white
    for q in on:new[q]=dark
  else:
    for q in R:new[q]=dark if get(q) else 0
    m=textmask(t,7,'Galmuri7',X1-X0-2)
    ox=X0+(X1-X0-m.width)//2;oy=Y0+2
    on={(ox+x,oy+y) for y in range(m.height) for x in range(m.width) if m.getpixel((x,y))}
    for q in ring(on,1):new[q]=dark
    for q in on:new[q]=white
  for q,v in new.items():
    if q in pm:g.d[g.o+pm[q]]=v
def run(files=None):
  files={} if files is None else files
  for f,k,rect,t,mode in S:
    p=F/(f+'.NCGR');g=NCGR(files.get(p) or p.read_bytes());c=NCER((F/(f+'.NCER')).read_bytes())
    g.d=bytearray(g.d);apply(g,c,nclr((F/'game_ext.NCLR').read_bytes()),k,rect,t,mode);files[p]=bytes(g.d)
  return files
if __name__=='__main__':
  from c8 import render8
  from PIL import Image
  fs=run();o=Image.new('RGB',(260,400),(255,0,255));y=0
  for f,k,*_ in S:
    p=F/(f+'.NCGR');c=NCER((F/(f+'.NCER')).read_bytes());pal=nclr((F/'game_ext.NCLR').read_bytes())
    for i,d in enumerate([p.read_bytes(),fs[p]]):
      g=NCGR(d);im=render8(g,c,pal,k,True);im=im.resize((im.width*3//2*2//2*1,im.height),0)
      o.paste(im,(0,y+i*50),im)
    y+=100
  o.resize((780,1200),0).save(sys.argv[1] if len(sys.argv)>1 else 'shots/s8.png')
