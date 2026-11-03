"""조사 결과(survey/found_*.json) -> 자동 영역 사양. OV: 키별 수정값"""
import json,sys
sys.path.insert(0,str(__import__('pathlib').Path(__file__).parent))
from pathlib import Path
W=Path(__file__).resolve().parents[1]
from gfxov import OV
SKIP_PREFIX=('gam/mes','rpg/2d/entry','rpg/2d/sub_dwn_obj')
def load():
  out=[]
  for n in ['found_a','found_b']:
    p=W/'survey'/(n+'.json')
    if not p.exists():continue
    for x in json.load(open(p,encoding='utf8')):
      f,c=x['key'].rsplit(':',1);c=int(c)
      if f.startswith(SKIP_PREFIX) or not x.get('ko'):continue
      o=OV.get(x['key'],{})
      if o is None or o.get('skip'):continue
      d=dict(f=f,cells=[c],text=x['ko'],rect='auto',key=x['key'])
      st=W/'ext/fs/file'/f
      if not st.with_suffix('.NCLR').exists():
        n=st.name;cand=[]
        while n and not cand:cand=sorted(st.parent.glob(n+'*.NCLR'));n=n[:-1]
        if not cand and f.startswith('obj/omake/'):cand=[W/'ext/fs/file/obj/omake/omake_l.NCLR']
        if not cand and f.startswith('gam/'):cand=[W/'ext/fs/file/gam/game_cmn.NCLR']
        if not cand:print('팔레트 없음',f);continue
        if cand:d['pal']=cand[0].relative_to(W/'ext/fs/file').with_suffix('').as_posix()
      d.update(o)
      if d.get('rect') is None:d['rect']='auto'
      if isinstance(d.get('rect'),list) and not d.get('nopanel') and d.get('mode')!='ring' and 'snap' not in d:d['snap']=1
      out.append(d)
  return out
SPA=load()
def final():
  import gfxspec
  ks={(s['f'],c) for s in SPA for c in s['cells']}
  return SPA+[s for s in gfxspec.SP if not all((s['f'],c) in ks for c in s['cells'])]
