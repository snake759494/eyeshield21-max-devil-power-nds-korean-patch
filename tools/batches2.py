"""추가 번역 배치: 기존 번역에 없는 문자열만 trans/src/b27..json 으로"""
import json,re
from pathlib import Path
W=Path(__file__).resolve().parents[1];E=W/'ext';T=W/'trans'
def tag(s):
  s=re.sub(r'\x0c ?(-?\d*)',lambda m:'[w'+m[1]+']',s)
  s=re.sub(r'\x0d(.)',lambda m:'[c'+m[1]+']',s)
  return re.sub(r'([\x02-\x09\x0b])( ?-?\d*)',lambda m:'[x%d:%s]'%(ord(m[1]),m[2]),s)
have=set()
for p in sorted((T/'src').glob('b*.json')):
  n=int(p.stem[1:])
  if n<27:have|={u['ja'] for u in json.load(open(p,encoding='utf8'))}
R=[r for r in json.load(open(E/'strings.json',encoding='utf8')) if r['ptr']]
order=['arm9','ov000']+[f'ov{i:03d}' for i in range(1,10)]
R.sort(key=lambda r:(order.index(r['bin']),r['off']))
seen=set();units=[]
for r in R:
  t=tag(r['ja'])
  if t in have or t in seen:continue
  seen.add(t);units.append({'id':f"{r['bin']}:{r['off']:x}",'ja':t})
B=[];cur=[];n=0
for u in units:
  cur.append(u);n+=len(u['ja'])
  if n>=2700:B.append(cur);cur=[];n=0
if cur:B.append(cur)
for p in (T/'src').glob('b*.json'):
  if int(p.stem[1:])>=27:p.unlink()
for i,b in enumerate(B):json.dump(b,open(T/'src'/f'b{27+i:02d}.json','w',encoding='utf8'),ensure_ascii=False,indent=0)
print(len(units),len(B),[sum(len(u['ja']) for u in b) for b in B])
