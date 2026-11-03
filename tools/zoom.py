"""셀 확대 + 8px 격자: python tools/zoom.py out.png f:cell [f:cell ...]  (팔레트는 gfxauto 규칙)"""
import sys;sys.path.insert(0,'tools')
from PIL import Image,ImageDraw
from gtext import F
from g2d import NCGR,nclr
from cell import NCER,render
from gfxauto import SPA
pals={s['key']:s.get('pal',s['f']) for s in SPA}
S=4;ims=[]
for k in sys.argv[2:]:
  f,c=k.rsplit(':',1);c=int(c)
  gp=next(p for p in [F/(f+'.NCGR'),F/(f+'.NCBR')] if p.exists());g=NCGR(gp.read_bytes())
  pf=pals.get(k,f)
  im=render(g,NCER((F/(f+'.NCER')).read_bytes()),nclr((F/(pf+'.NCLR')).read_bytes()),c,g.tiled==1)[0]
  b=Image.new('RGB',im.size,(255,0,255));b.paste(im,(0,0),im);b=b.resize((im.width*S,im.height*S),0)
  d=ImageDraw.Draw(b)
  for x in range(0,im.width,8):d.line([(x*S,0),(x*S,b.height)],fill=(0,255,0) if x%32 else (0,120,0))
  for y in range(0,im.height,8):d.line([(0,y*S),(b.width,y*S)],fill=(0,255,0) if y%32 else (0,120,0))
  ims.append((k,b))
W=max(b.width for _,b in ims)+4;H=sum(b.height+14 for _,b in ims)
o=Image.new('RGB',(W,H),(255,255,255));d=ImageDraw.Draw(o);y=0
for k,b in ims:d.text((0,y),k+'  (grid 8px)',fill=(0,0,0));o.paste(b,(0,y+12));y+=b.height+14
o.save(sys.argv[1])
