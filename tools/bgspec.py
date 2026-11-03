"""BG 글자 교체 사양"""
BS=[]
def add(f,rect,text,h,**k):BS.append(dict(f=f,rect=rect,text=text,h=h,**k))
for r,t in [([10,176,56,184],'코인:'),([148,176,186,184],'베팅:'),([204,176,246,184],'승리:')]:add('obj/srot/bg_h',r,t,9,bg=[0,16,24],fg=[8,240,40],noline=1)
for i,t in enumerate(['셔틀\n~불량배들~','불량배들한테서\n도망쳐라','타운지 배달\n~이시마루 돕기~','포스터 붙이기','셔틀\n~하바시라 루이~','셔틀\n~세이부 감독~',
  '토목 공사','덤프를 밀어라!','40야드 달리기','슬레드 머신','벤치프레스']):
  BS.append(dict(f=f'rpg/2d/mg_{i:03d}_bg_s0',rect='T',text=t,h=16 if '\n' in t else 22,thick=2))
  add(f'rpg/2d/mg_{i:03d}_bg_s1',[2,0,98,18],'룰 설명',13,fg=[248,200,48],ol=[16,32,80],bgat=[3,1])
add('rpg/2d/parameta_h1_bg0',[28,114,126,140],'능력',14,noline=1)
add('rpg/2d/rbg_021_0',[44,24,224,50],'봄 상공회 축제',18,noline=1)
import json
from pathlib import Path
_R={x['key']:x['rect'] for x in json.load(open(Path(__file__).resolve().parents[1]/'survey/found_bg.json',encoding='utf8')) if x['key'].endswith('_bg_s0')}
for b in BS:
  if b['rect']=='T':r=_R[b['f']];b['rect']=[r[0]-6,r[1]-4,r[2]+6,r[3]+10]
