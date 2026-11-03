"""파일별 SJIS 일본어 밀도 조사"""
import re,sys
from pathlib import Path
import ndspy.lz10
W=Path(__file__).resolve().parents[1];E=W/'ext'
pat=re.compile(rb'(?:[\x82\x83\x88-\x9f\xe0-\xea][\x40-\xfc]|\x81[\x40-\xac]){3,}')
res=[]
for p in sorted(E.rglob('*')):
  if not p.is_file():continue
  d=p.read_bytes()
  tag=''
  if d[:1] in (b'\x10',b'\x11') and len(d)>4:
    try:d2=ndspy.lz10.decompress(d);d=d2;tag='lz'
    except Exception:pass
  m=pat.findall(d);n=sum(len(x) for x in m)
  if n>40:res.append((n,len(m),tag,p.relative_to(E).as_posix()))
for r in sorted(res,reverse=True):print(*r)
