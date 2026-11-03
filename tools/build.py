"""한글 ROM 빌드: 폰트(갈무리11/9) + arm9·오버레이 문자열 + omake/half/credit/errors."""
import re,json,struct,sys,hashlib
from pathlib import Path
import ndspy.rom
W=Path(__file__).resolve().parents[1];ROOT=W.parent;E=W/'ext';T=W/'trans'
sys.path.insert(0,str(W/'tools'))
from nftr import NFTR
from bdf import bdf
SRC=ROOT/'Eyeshield 21 - Max Devil Power! (Japan).nds'
OUT=ROOT/'Eyeshield 21 - Max Devil Power! (Korean).nds'
BASE={'arm9':0x2000000,'ov000':0x2131220}
for i in range(1,10):BASE[f'ov{i:03d}']=0x21619c0
ARENA0=0x21d3680  # 원래 힙(arena) 시작 = 공용 오버레이 영역 끝
XBASE=0x21e0000   # 오버레이 확장 상한 = arm9 추가 문자열(autoload 섹션) 시작
EXTRA=bytearray()
ARENA_LIT=(0xd54,0xbe6ac)
BSS={}

# ---- 번역 사전
TR={}
for p in sorted((T/'src').glob('*.json')):
  q=T/'ko'/p.name
  if not q.exists():continue
  s=json.load(open(p,encoding='utf8'));k=json.load(open(q,encoding='utf8'))
  if len(s)!=len(k):continue
  for a,b in zip(s,k):
    if isinstance(b,str):TR[a['id']]=(a['ja'],b)
def untag(s):
  s=re.sub(r'\[w(-?\d*)\]',lambda m:'\x0c '+m[1],s)
  s=re.sub(r'\[c(.)\]',lambda m:'\x0d'+m[1],s)
  return re.sub(r'\[x(\d+):( ?-?\d*)\]',lambda m:chr(int(m[1]))+m[2],s)
def tag(s):
  s=re.sub(r'\x0c ?(-?\d*)',lambda m:'[w'+m[1]+']',s)
  s=re.sub(r'\x0d(.)',lambda m:'[c'+m[1]+']',s)
  return re.sub(r'([\x02-\x09\x0b])( ?-?\d*)',lambda m:'[x%d:%s]'%(ord(m[1]),m[2]),s)
JA2KO={ja:ko for ja,ko in TR.values()}
STR=[r for r in json.load(open(E/'strings.json',encoding='utf8')) if r['ptr']]

# ---- 음절 -> 한자 코드 배정
alltext=[ko for ja,ko in TR.values()]
syl=sorted({c for t in alltext for c in t if '가'<=c<='힣'})
f12=NFTR((E/'fs/file/obj/font/font12.NFTR').read_bytes())
keep=set()  # 번역 후에도 남는 원문 한자(쓰레기 문자열 등)
for t in alltext:
  for c in t:
    if '一'<=c<='鿿':keep.add(int.from_bytes(c.encode('cp932'),'big'))
codes=sorted(k for k in f12.map if k>=0x889f and k not in keep)
assert len(syl)<=len(codes),(len(syl),len(codes))
ENC={ch:c.to_bytes(2,'big') for ch,c in zip(syl,codes)}
NORM={'·':'・','‘':"'",'’':"'",'“':'"','”':'"','–':'-','—':'-','♥':'♪','〜':'～','‥':'…'}
BAD=set()
def enc(s):
  s=untag(s);out=bytearray()
  for ch in s:
    if ch in ENC:out+=ENC[ch]
    else:
      ch=NORM.get(ch,ch)
      try:out+=ch.encode('cp932')
      except UnicodeEncodeError:BAD.add(ch);out+=b'?'
  return bytes(out)

# ---- 폰트
def put_font(path,bdfpath,cell):
  n=NFTR(path.read_bytes());g,asc=bdf(bdfpath)
  def draw(gi,e,adv=None):
    rows=[[0]*n.cw for _ in range(n.ch)]
    top=cell-e['by']-e['bh']  # 베이스라인=셀 바닥
    if top+e['bh']>n.ch:top=n.ch-e['bh']
    top=max(top,0)
    for y,r in enumerate(e['rows']):
      for x,p in enumerate(r):
        X=x+max(e['bx'],0);Y=top+y
        if p and X<n.cw and Y<n.ch:rows[Y][X]=1
    n.setglyph(gi,rows)
    n.setwidth(gi,(0,max(e['bw']+max(e['bx'],0),1),adv if adv is not None else e['dw']))
  for ch,code in ENC.items():
    e=g.get(ord(ch))
    if e is None:print('글리프 없음',ch);continue
    draw(n.map[int.from_bytes(code,'big')],e)
  for a in range(0x21,0x7f):  # 반각 ASCII는 비례폭
    e=g.get(a)
    if e and a in n.map:draw(n.map[a],e)
  if 0x20 in n.map:n.setwidth(n.map[0x20],(0,0,g[0x20]['dw']))
  return bytes(n.d)

# ---- 바이너리 문자열 교체
def patch_bins(bins,arena):
  stats={}
  by={}
  for r in STR:by.setdefault(r['bin'],[]).append(r)
  for name,rs in by.items():
    d=bins[name];base=BASE[name]
    free=[];reloc=[]
    for r in rs:
      ko=JA2KO.get(tag(r['ja']))
      if ko is None or ko==tag(r['ja']):continue
      b=enc(ko)
      slot=min(r['slot'],((r['off']+r['len']+1+3)&~3)-r['off'])
      if len(b)+1<=slot:
        d[r['off']:r['off']+slot]=b+bytes(slot-len(b))
        if slot-len(b)-1>=8:free.append([r['off']+len(b)+1,r['off']+slot])
      else:
        d[r['off']:r['off']+slot]=bytes(slot);free.append([r['off'],r['off']+slot])
        reloc.append((r,b))
    # 재배치: 큰 것부터 first-fit
    reloc.sort(key=lambda x:-len(x[1]))
    grow=name not in ('arm9','ov000')
    tail=(len(d)+BSS.get(name,0)+3)&~3 if grow else len(d)  # 기존 BSS 주소 위에 쓰지 않도록 그 뒤부터
    lim=arena-base-BSS.get(name,0) if grow else len(d)
    nfail=0
    for r,b in reloc:
      need=len(b)+1
      for f in free:
        if f[1]-f[0]>=need:
          at=f[0];f[0]+=need;break
      else:
        if name in ('arm9','ov000'):
          ea=len(EXTRA);EXTRA.extend(b+bytes(1))
          for pb,po in r['ptr']:struct.pack_into('<I',bins[pb],po,XBASE+ea)
          continue
        if tail+need<=lim:
          if len(d)<tail:d.extend(bytes(tail-len(d)))
          at=tail;d.extend(bytes(need));tail+=need
        else:
          nfail+=1;continue
      d[at:at+len(b)]=b;d[at+len(b)]=0
      for pb,po in r['ptr']:
        struct.pack_into('<I',bins[pb],po,base+at)
    stats[name]=(len(reloc),nfail,len(d)-len(rs and d))
    print(name,'재배치',len(reloc),'실패',nfail,'크기',hex(len(d)))
    if nfail:print('!!! 공간 부족',name,nfail)
    while len(d)%4:d.append(0)
  return sum(v[1] for k,v in stats.items() if k not in ('arm9','ov000'))

# ---- 고정 위치 파일
def fixed_records(raw,prefix,sep):
  d=bytearray(raw);pos=0
  for m in re.finditer(sep,bytes(raw)+b'\x00'):
    s=raw[pos:m.start()]
    if s.strip(b'\x00'):
      k=TR.get(f'{prefix}:{pos:x}')
      if k:
        b=enc(k[1].replace('\n','\r\n'))
        if prefix=='half' and not b.endswith(b'Z'):b+=b'Z'
        n=m.start()-pos
        if len(b)>n:print('길이 초과',prefix,hex(pos),len(b),n);b=b[:n]
        d[pos:pos+n]=b+bytes(n-len(b))
    pos=m.end()
  return bytes(d)

def main():
  rom=ndspy.rom.NintendoDSRom.fromFile(str(SRC))
  ovs=rom.loadArm9Overlays()
  for i,o in ovs.items():BSS[f'ov{i:03d}']=o.bssSize
  bins={'arm9':bytearray((E/'arm9.bin').read_bytes())}
  for i in range(10):bins[f'ov{i:03d}']=bytearray((E/f'ov{i:03d}.bin').read_bytes())
  EXTRA.clear()
  assert patch_bins(bins,XBASE)==0
  while len(EXTRA)%32:EXTRA.append(0)
  arena=max(ARENA0,XBASE+len(EXTRA)+0x20)
  print('arm9 추가 영역',hex(XBASE),hex(len(EXTRA)),'arena',hex(arena))
  for o in ARENA_LIT:
    assert struct.unpack_from('<I',bins['arm9'],o)[0]==ARENA0
    struct.pack_into('<I',bins['arm9'],o,arena)
  # arm9: ndspy로 다시 넣기(무압축)
  a9=rom.loadArm9()
  a9.sections[0].data=bytes(bins['arm9'][:len(a9.sections[0].data)])
  if EXTRA:a9.sections.append(ndspy.code.MainCodeFile.Section(bytes(EXTRA),XBASE,0,implicit=False))
  rom.arm9=a9.save(compress=False)
  for i,o in ovs.items():
    o.data=bytes(bins[f'ov{i:03d}']);o.compressed=False
    o.ramSize=len(o.data)
  rom.arm9OverlayTable=ndspy.code.saveOverlayTable(ovs)
  for i,o in ovs.items():rom.files[o.fileID]=o.save(compress=False)
  fid=lambda n:rom.filenames.idOf(n)
  for fn,bd,cell in [('file/obj/font/font12.NFTR','Galmuri11',11),('file/rpg/2d/LC12.NFTR','Galmuri11',11),
                     ('file/obj/font/font.NFTR','Galmuri9',9),('file/rpg/2d/LC10.NFTR','Galmuri9',9)]:
    p=E/'fs'/fn;rom.files[fid(fn)]=put_font(p,W/'fonts'/(bd+'.bdf'),cell)
  rom.files[fid('file/omake/omake_txt.bin')]=fixed_records(rom.files[fid('file/omake/omake_txt.bin')],'omake',rb'\x00+')
  rom.files[fid('file/half/half.bin')]=fixed_records(rom.files[fid('file/half/half.bin')],'half',rb'\x00')
  if 'credit' in TR:rom.files[fid('file/ending/credit.txt')]=enc(TR['credit'][1].replace('\n','\r\n'))
  for p in sorted((E/'fs/file/rpg/errors').glob('*.txt')):
    k=TR.get('err:'+p.name)
    if k:rom.files[fid('file/rpg/errors/'+p.name)]=enc(k[1].replace('\n','\r\n'))
  import gtext
  from gfxauto import final
  for gp,b in gtext.run(final()).items():rom.files[fid(gp.resolve().relative_to(E/'fs').as_posix())]=b
  import bgtext,bgspec,rawbg,mestext,gamebg,s8text
  for gp,b in s8text.run().items():rom.files[fid(gp.resolve().relative_to(E/'fs').as_posix())]=b
  for gp,b in mestext.run().items():rom.files[fid(gp.resolve().relative_to(E/'fs').as_posix())]=b
  for gp,b in gamebg.run().items():rom.files[fid(gp.resolve().relative_to(E/'fs').as_posix())]=b
  for gp,b in rawbg.run().items():rom.files[fid(gp.resolve().relative_to(E/'fs').as_posix())]=b
  for gp,b in bgtext.run(bgspec.BS).items():rom.files[fid(gp.resolve().relative_to(E/'fs').as_posix())]=b
  if BAD:print('인코딩 불가 문자',BAD)
  data=rom.save()
  OUT.write_bytes(data)
  print('음절',len(syl),'출력',OUT.name,len(data),hashlib.sha256(data).hexdigest()[:16])
import ndspy.code
if __name__=='__main__':main()
