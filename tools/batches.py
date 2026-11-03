"""번역 배치 생성: trans/src/bNN.json = [{"id":..,"ja":..}]"""
import json,re
from pathlib import Path
W=Path(__file__).resolve().parents[1];E=W/'ext';T=W/'trans'
def tag(s):return re.sub(r'\x0c ?(-?\d*)',lambda m:'[w'+m[1]+']',s)
R=[r for r in json.load(open(E/'strings.json',encoding='utf8')) if r['ptr']]
order=['arm9','ov000']+[f'ov{i:03d}' for i in range(1,10)]
R.sort(key=lambda r:(order.index(r['bin']),r['off']))
seen=set();units=[]
for r in R:
  if r['ja'] in seen:continue
  seen.add(r['ja']);units.append({'id':f"{r['bin']}:{r['off']:x}",'ja':tag(r['ja'])})
# 부가 파일
def recs(path,sep):
  d=(E/'fs/file'/path).read_bytes()
  out=[];pos=0
  for m in re.finditer(sep,d+b'\x00'):
    s=d[pos:m.start()]
    if s.strip(b'\x00'):out.append((pos,s))
    pos=m.end()
  return out
ext=[]
for o,s in recs('omake/omake_txt.bin',rb'\x00+'):ext.append({'id':f'omake:{o:x}','ja':s.decode('cp932').replace('\r\n','\n'),'note':'프로필/기술 설명창: 한 줄 최대 전각 9자(프로필) 또는 16자(기술 설명). 줄바꿈 위치는 자유롭게 다시 잡아도 됨'})
for o,s in recs('half/half.bin',rb'\x00'):ext.append({'id':f'half:{o:x}','ja':s.decode('cp932').replace('\r\n','\n'),'note':'끝의 Z는 제어문자이므로 유지'})
ext.append({'id':'credit','ja':(E/'fs/file/ending/credit.txt').read_bytes().decode('cp932').replace('\r\n','\n'),'note':'스태프 크레딧. 인명은 한국어 음역, 회사명은 원문 표기 유지 가능. 행 구조 유지'})
for p in sorted((E/'fs/file/rpg/errors').glob('*.txt')):
  ext.append({'id':'err:'+p.name,'ja':p.read_bytes().decode('cp932').replace('\r\n','\n')})
# 배치 나누기
B=[];cur=[];n=0
for u in units:
  cur.append(u);n+=len(u['ja'])
  if n>=7600:B.append(cur);cur=[];n=0
if cur:B.append(cur)
cur=[];n=0
for u in ext:
  cur.append(u);n+=len(u['ja'])
  if n>=9000:B.append(cur);cur=[];n=0
if cur:B.append(cur)
for p in T.glob('src/*.json'):p.unlink()
for i,b in enumerate(B):json.dump(b,open(T/'src'/f'b{i:02d}.json','w',encoding='utf8'),ensure_ascii=False,indent=0)
print(len(units),len(B),[sum(len(u['ja']) for u in b) for b in B])
