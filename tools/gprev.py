"""gfx.json 적용 결과를 파일별 셀 시트로 미리보기: python tools/gprev.py 출력폴더"""
import sys,json;sys.path.insert(0,'tools')
import gtext
from cell import *
from PIL import ImageDraw
from pathlib import Path
from gfxspec import SP as sp;files=gtext.run(sp)
O=Path(sys.argv[1]);O.mkdir(exist_ok=True)
by={}
for s in sp:by.setdefault((s['f'],s.get('pal',s.get('g',s['f'])),s.get('g',s['f'])),set()).update(s['cells'])
for (f,p,gf),cs in by.items():
  gp=gtext.F/(gf+'.NCGR')
  if gp not in files:gp=gtext.F/(gf+'.NCBR')
  g=NCGR(files[gp]);c=NCER((gtext.F/(f+'.NCER')).read_bytes());pal=nclr((gtext.F/(p+'.NCLR')).read_bytes())
  ims=[i for i in (render(g,c,pal,k,g.tiled==1)[0] for k in sorted(cs)) if i]
  o=Image.new('RGBA',(max(i.width for i in ims),sum(i.height+2 for i in ims)),(255,0,255,255));y=0
  for i in ims:o.paste(i,(0,y),i);y+=i.height+2
  o.resize((o.width*2,o.height*2),0).save(O/(f.replace('/','_')+'.png'))
