"""번역 검증: python tools/check_trans.py b05 [b06 ...]  (인자 없으면 전체)"""
import json,re,sys
from pathlib import Path
T=Path(__file__).resolve().parents[1]/'trans'
JP=re.compile('[぀-ヿ一-鿿]')
def width(l):return sum(0.5 if ord(c)<0x80 else 1 for c in l)
def check(b):
  src=json.load(open(T/'src'/f'{b}.json',encoding='utf8'))
  p=T/'ko'/f'{b}.json'
  if not p.exists():return [f'{b}: 출력 없음']
  ko=json.load(open(p,encoding='utf8'))
  if len(ko)!=len(src):return [f'{b}: 개수 불일치 {len(ko)}!={len(src)}']
  err=[]
  for s,k in zip(src,ko):
    j=s['ja'];i=s['id']
    if not isinstance(k,str):err.append(f'{i}: 문자열 아님');continue
    if k==j and len(j)<=3:continue
    if re.findall(r'\[w-?\d*\]',j)!=re.findall(r'\[w-?\d*\]',k):err.append(f'{i}: [w] 토큰 불일치')
    if re.findall(r'\[x\d+: ?-?\d*\]',j)!=re.findall(r'\[x\d+: ?-?\d*\]',k):err.append(f'{i}: [x] 토큰 불일치')
    if sorted(re.findall(r'\[c.\]',j))!=sorted(re.findall(r'\[c.\]',k)):err.append(f'{i}: [c] 토큰 불일치')
    if k==j and not JP.search(j):continue
    if k.count('\n')>j.count('\n') and not i.startswith(('omake','credit')):err.append(f'{i}: 줄바꿈 증가')
    if JP.search(k.replace('ー','')):err.append(f'{i}: 일본어 남음 {k!r}')
    lim=20
    if i.startswith('omake'):lim=16
    for l in re.sub(r'\[(w-?\d*|c.|x\d+:-?\d*)\]','',k).split('\n'):
      if width(l)>lim+0.01 and not i.startswith('credit'):err.append(f'{i}: 줄 너무 김({width(l)}) {l!r}')
    a=re.findall(r'%[ds]',j);bb=re.findall(r'%[ds]',k)
    if a!=bb:err.append(f'{i}: %d/%s 불일치')
    # 슬롯 길이(대략): 짧은 명칭류
    nb=len(re.sub(r'\[w-?\d*\]','x',k).encode('utf-16-le'))  # 상한 근사
    jb=len(re.sub(r'\[w-?\d*\]','x',j).encode('cp932',errors='replace'))
    kb=sum(1 if ord(c)<0x80 else 2 for c in re.sub(r'\[w-?\d*\]','x',k))
    if '\n' not in j and jb<=12 and kb>jb+1 and not i.startswith(('omake','half','credit','err')):err.append(f'{i}: 명칭 길이 초과 {jb}->{kb}바이트 {k!r}')
  return err
bs=sys.argv[1:] or sorted(p.stem for p in (T/'src').glob('*.json'))
tot=0
for b in bs:
  e=check(b);tot+=len(e)
  for x in e:print(x)
print('오류',tot)
