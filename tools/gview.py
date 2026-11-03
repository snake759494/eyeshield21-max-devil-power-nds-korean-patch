"""python tools/gview.py 파일(확장자X) 팔레트 셀,셀,.. 출력.png  : 눈금(8px) 확대 보기"""
import sys;sys.path.insert(0,'tools')
from cell import *
from PIL import ImageDraw
from pathlib import Path
F=Path('ext/fs/file')
f,p,cs,out=sys.argv[1:5]
gf=sys.argv[5] if len(sys.argv)>5 else f
gp=F/(gf+'.NCGR')
if not gp.exists():gp=F/(gf+'.NCBR')
g=NCGR(gp.read_bytes());c=NCER((F/(f+'.NCER')).read_bytes());pal=nclr((F/(p+'.NCLR')).read_bytes())
ims=[]
for k in map(int,cs.split(',')):
  im,_=render(g,c,pal,k,g.tiled==1)
  if im:ims.append((k,im))
S=3;W=max(i.width for _,i in ims)*S+30;H=sum(i.height*S+6 for _,i in ims)
o=Image.new('RGB',(W,H),(255,0,255));d=ImageDraw.Draw(o);y=0
for k,i in ims:
  bg=Image.new('RGBA',i.size,(255,0,255,255));bg.alpha_composite(i)
  o.paste(bg.resize((i.width*S,i.height*S),0),(30,y))
  for x in range(0,i.width+1,8):d.line([(30+x*S,y),(30+x*S,y+i.height*S)],fill=(0,160,0))
  for yy in range(0,i.height+1,8):d.line([(30,y+yy*S),(30+i.width*S,y+yy*S)],fill=(0,160,0))
  d.text((0,y),f'{k}\n{i.width}x{i.height}',fill=(0,0,0));y+=i.height*S+6
o.save(out)
