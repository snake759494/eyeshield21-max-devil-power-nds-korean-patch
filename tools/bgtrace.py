"""bg/*.bin 로딩 코드 추적: 파일명 문자열을 쓰는 함수에서 팔레트/타일/맵 로드 호출 인자(파일 내 오프셋)를 뽑음"""
import struct,re,json,capstone
from pathlib import Path
W=Path(__file__).resolve().parents[1];E=W/'ext'
BASE={'arm9':0x2000000,'ov000':0x2131220}
for i in range(1,10):BASE[f'ov{i:03d}']=0x21619c0
BINS={k:(E/(k+'.bin')).read_bytes() for k in BASE}
md=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM);md.detail=False
A9=BINS['arm9']
names={}
for m in re.finditer(rb'bg/([a-z0-9_]+)\.bin\x00',A9):names[0x2000000+m.start()]=m.group(1).decode()
FN={0x2079a98:'tile',0x2078ed4:'map',0x2079908:'palM',0x20798e8:'palS'}
def run(bn,start,fname,n=400):
  d=BINS[bn];b=BASE[bn];R={};G={};out=[];stk={};MEM={}
  base_known=False
  for a in range(start,min(start+n*4,len(d)),4):
    ins=next(md.disasm(d[a:a+4],b+a),None)
    if not ins:continue
    m=ins.mnemonic;ops=[o.strip() for o in ins.op_str.split(',')]
    try:
      if m=='ldr' and 'pc' in ins.op_str:
        off=int(ins.op_str.split('#')[-1].rstrip(']'),16) if '#' in ins.op_str else 0
        v=struct.unpack_from('<I',d,a+8+off)[0];R[ops[0]]=('c',v)
      elif m=='mov' and ops[1].startswith('#'):R[ops[0]]=('c',int(ops[1][1:],0))
      elif m=='mov' and ops[1] in R:R[ops[0]]=R[ops[1]]
      elif m=='mvn' and ops[1].startswith('#'):R[ops[0]]=('c',~int(ops[1][1:],0)&0xffffffff)
      elif m=='ldr' and ops[1].startswith('['):
        rb=ops[1].strip('[]');o=int(ops[2].strip('#]'),0) if len(ops)>2 else 0
        src=R.get(rb)
        if src and src[0]=='c' and src[1] in G:R[ops[0]]=G[src[1]]
        elif src and src[0]=='fh' and o==0x20:R[ops[0]]=('b',0)
        elif not src and (rb,o) in MEM:R[ops[0]]=MEM[(rb,o)]
        else:R.pop(ops[0],None)
      elif m=='str' and ops[1].startswith('['):
        rb=ops[1].strip('[]');src=R.get(rb)
        if ops[1]=='[sp' or ops[1]=='[sp]':stk[int(ops[2].strip('#]'),0) if len(ops)>2 else 0]=R.get(ops[0])
        elif src and src[0]=='c' and R.get(ops[0]) and R[ops[0]][0]=='b':G[src[1]]=R[ops[0]]
        elif not src and R.get(ops[0]):MEM[(rb,int(ops[2].strip('#]'),0) if len(ops)>2 else 0)]=R[ops[0]]
      elif m=='add' and len(ops)==3:
        x=R.get(ops[1]);y=R.get(ops[2]) if not ops[2].startswith('#') else ('c',int(ops[2][1:],0))
        if x and y:
          if x[0]=='b' and y[0]=='c':R[ops[0]]=('b',x[1]+y[1])
          elif y[0]=='b' and x[0]=='c':R[ops[0]]=('b',y[1]+x[1])
          elif x[0]=='c' and y[0]=='c':R[ops[0]]=('c',x[1]+y[1])
          else:R.pop(ops[0],None)
        else:R.pop(ops[0],None)
      elif m=='bl':
        t=int(ops[0][1:],0)
        if t in FN:out.append((FN[t],R.get('r0'),R.get('r1'),R.get('r2'),R.get('r3'),dict(stk)))
        if R.get('r0',(0,0))[0]=='c' and R.get('r0')[1] in names and R['r0'][1]==fname:
          R={'r0':('fh',0)};MEM.clear();continue
        for r in ['r0','r1','r2','r3','ip']:R.pop(r,None)
      elif m in('pop','ldm') and 'pc' in ins.op_str:break
      elif m=='bx' and ops[0]=='lr':break
      elif len(ops) and ops[0] in R and m not in('cmp','tst','str','strb','strh','push','stm','b','bne','beq','blt','bgt','bge','ble'):R.pop(ops[0],None)
    except Exception:R.pop(ops[0] if ops else None,None)
  return out
res={}
for bn,d in BINS.items():
  b=BASE[bn]
  for i in range(0,len(d)-3,4):
    v=struct.unpack_from('<I',d,i)[0]
    if v in names:
      # 이 리터럴을 쓰는 ldr 찾기
      for a in range(max(0,i-0x1000),i,4):
        w=struct.unpack_from('<I',d,a)[0]
        if (w&0x0f7f0000)==0x051f0000 and a+8+(w&0xfff)==i:
          # 그 지점부터 실행(파일 열기 bl 다음에 r0=핸들)
          o=run(bn,a,v)
          res.setdefault(names[v],[]).append({'at':hex(b+a),'bin':bn,'calls':[[str(x) for x in c[:5]]+[str(c[5])] for c in o]})
json.dump(res,open(W/'survey/bgtrace.json','w'),indent=1)
for k,v in sorted(res.items()):
  print(k,len(v),[len(x['calls']) for x in v])
