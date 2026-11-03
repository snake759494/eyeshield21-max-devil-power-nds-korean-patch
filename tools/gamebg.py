"""bg/game.bin(경기 상단 화면 BG0) 글자: VRAM 스냅샷의 맵으로 타일 위치를 잡아 직접 고침"""
import sys,struct,collections
sys.path.insert(0,str(__import__('pathlib').Path(__file__).parent))
from pathlib import Path
from gtext import textmask
W=Path(__file__).resolve().parents[1];P=W/'ext/fs/file/bg/game.bin'
TB=0x1e0  # 타일 데이터 시작
# (화면 사각형, 글자, 높이, 테두리)  맵은 경기 화면 스냅샷에서 뽑은 값(BG0, 4bpp, 팔레트 뱅크는 맵 엔트리)
MAP=json_map=None
SPECS=[((113,1,143,8),'스코어',7,0),((2,129,58,136),'골라인',8,0),((32,145,56,158),'야드',10,1)]
def run(files=None):
  import json
  files={} if files is None else files
  m=json.load(open(W/'tools/gamebg_map.json'))
  ents=m['ents'];pal=[tuple(c) for c in m['pal']]
  d=bytearray(files.get(P) or P.read_bytes())
  use=collections.Counter(e&0x3ff for e in ents)
  def addr(x,y):
    e=ents[(y//8)*32+x//8];t=e&0x3ff;hf=(e>>10)&1;vf=(e>>11)&1
    sx=7-x%8 if hf else x%8;sy=7-y%8 if vf else y%8
    return TB+t*32+sy*4+sx//2,sx&1,e>>12,t
  def get(x,y):
    a,nb,pb,_=addr(x,y);v=(d[a]>>(4*nb))&15;return pal[pb*16+v] if v else None
  for (X0,Y0,X1,Y1),text,h,ol in SPECS:
    P_={(x,y):get(x,y) for y in range(Y0,Y1) for x in range(X0,X1)}
    cnt=collections.Counter(P_.values());bg=cnt.most_common(1)[0][0]
    fg=(248,248,248);olc=(0,0,0)
    new={q:bg for q in P_}
    mk=textmask(text,h,'NanumSquareNeo-eHv.ttf',X1-X0-2)
    ox=X0+(X1-X0-mk.width)//2;oy=Y0+(Y1-Y0-mk.height)//2
    on={(ox+x,oy+y) for y in range(mk.height) for x in range(mk.width) if mk.getpixel((x,y))}
    if ol:
      for x,y in on:
        for a in(-1,0,1):
          for b in(-1,0,1):
            if (x+a,y+b) in new:new[(x+a,y+b)]=olc
    for q in on:
      if q in new:new[q]=fg
    for (x,y),cl in new.items():
      a,nb,pb,t=addr(x,y)
      if use[t]>1:continue
      v=0 if cl is None else min(range(1,16),key=lambda i:sum((pal[pb*16+i][j]-cl[j])**2 for j in range(3)))
      d[a]=(d[a]&0xf0)|v if nb==0 else (d[a]&0x0f)|(v<<4)
  files[P]=bytes(d);return files
