"""arm9/오버레이에서 포인터로 참조되는 일본어 문자열 추출 -> ext/strings.json"""
import re,json,struct
from pathlib import Path
W=Path(__file__).resolve().parents[1];E=W/'ext'
BASE={'arm9':0x2000000,'ov000':0x2131220}
for i in range(1,10):BASE[f'ov{i:03d}']=0x21619c0
BINS={k:(E/(k+'.bin')).read_bytes() for k in BASE}
tok=re.compile(rb'(?:[\x81-\x9f\xe0-\xfc][\x40-\x7e\x80-\xfc]|\x0c[ \-0-9]+|\x0d[\x20-\x7e]|[\x02-\x09\x0b] ?[\-0-9]*|[\x0a\x20-\x7e])+')
IDX={}
for b,d in BINS.items():
  for i in range(0,len(d)-3,4):
    v=struct.unpack_from('<I',d,i)[0]
    if 0x2000000<=v<0x2400000:IDX.setdefault(v,[]).append((b,i))
def ptrs(name,addr):
  # 같은 공간에서 보이는 바이너리: arm9 <-> 모든 것, 오버레이 자신
  ok={'arm9',name} if name!='arm9' else set(BASE)
  return [x for x in IDX.get(addr,[]) if x[0] in ok]
res=[]
def cands(name,d):
  seen=set()
  for m in tok.finditer(d):
    if m.start()>0 and d[m.start()-1]!=0:continue
    seen.add(m.start());yield m
  # 포인터 표 바로 뒤처럼 앞이 0이 아닌 문자열: 포인터가 가리키는 위치에서 직접 매칭
  b=BASE[name]
  for v,l in IDX.items():
    st=v-b
    if 0<st<len(d) and st not in seen and d[st-1]!=0 and any(x[0] in ({'arm9',name} if name!='arm9' else set(BASE)) for x in l):
      m=tok.match(d,st)
      if m:seen.add(st);yield m
for name,d in BINS.items():
  for m in cands(name,d):
    s=m.group();st=m.start()
    if m.end()>=len(d) or d[m.end()]!=0:continue
    try:t=s.decode('cp932')
    except UnicodeDecodeError:continue
    if not re.search('[぀-ヿ一-鿿！-～　-〿]',t):continue
    # 깨진 바이트 배제: 한자/가나 비율
    jp=sum(1 for c in t if ord(c)>0x3000);
    if jp<1:continue
    p=ptrs(name,BASE[name]+st)
    # 슬롯 크기: 다음 non-zero까지
    e=m.end()
    while e<len(d) and d[e]==0:e+=1
    res.append(dict(bin=name,off=st,len=len(s),slot=e-st,ptr=p,ja=t))
# 다른 문자열 안쪽을 가리키는 (가짜/공유) 포인터 시작 문자열 제외
rng={}
for r in res:rng.setdefault(r['bin'],[]).append((r['off'],r['off']+r['len']))
def inside(r):return any(a<r['off']<b for a,b in rng[r['bin']])
res=[r for r in res if not inside(r)]
json.dump(res,open(E/'strings.json','w',encoding='utf8'),ensure_ascii=False,indent=0)
import collections
c=collections.Counter((r['bin'],bool(r['ptr'])) for r in res)
for k in sorted(c):print(k,c[k])
print(len(res),sum(len(r['ja']) for r in res if r['ptr']))
