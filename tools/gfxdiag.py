"""전체 그래픽 사양 적용 후 의도한 그림과 실제 결과 비교: 잘림(lost)/불일치(bad)"""
import sys,json
sys.path.insert(0,'tools')
import gtext
from gtext import F
from g2d import NCGR,nclr
from cell import NCER,render
from gfxauto import final
specs=final();files=gtext.run(specs);out=[]
for d in gtext.DIAG:
  s=next(x for x in specs if x.get('key',x['f'])==d['key'])
  c=NCER((F/(d['f']+'.NCER')).read_bytes());pal=nclr((F/(s.get('pal',s.get('g',s['f']))+'.NCLR')).read_bytes())
  g=NCGR(files[d['gp']]);im,_=render(g,c,pal,d['cell'],g.tiled==1);px=im.load()
  bad=0
  for (x,y),cl in d['new'].items():
    v=px[x,y];v=v[:3] if v[3] else None
    if (v is None)!=(cl is None) or (v and sum((v[j]-cl[j])**2 for j in range(3))>60**2):bad+=1
  out.append((d['key'],d['cell'],d['lost'],bad,d['non']))
out.sort(key=lambda t:-(t[2]*3+t[3]))
json.dump(out,open('survey/diag.json','w'),ensure_ascii=False)
for o in out[:80]:print(*o)
print(len(out),sum(1 for o in out if o[2] or o[3]>5))
