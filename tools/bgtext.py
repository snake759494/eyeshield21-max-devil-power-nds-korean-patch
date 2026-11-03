"""BG(NSCR) 화면 속 글자 교체"""
import sys,re,collections,struct
sys.path.insert(0,str(__import__('pathlib').Path(__file__).parent))
from pathlib import Path
from g2d import NCGR,nclr
from nscr import NSCR,pix
from gtext import textmask
F=Path(__file__).resolve().parents[1]/'ext/fs/file'
def gfor(p):
  s=p.with_suffix('');n=s.name
  while n:
    for x in [s.parent/(n+'.NCGR'),s.parent/(n+'.NCBR')]:
      if x.exists():
        lp=s.parent/(n+'.NCLR')
        if not lp.exists():lp=next(iter(sorted(s.parent.glob(n.split('_')[0]+'*.NCLR'))),lp)
        return x,lp
    n=re.sub(r'(_[^_]*|\d)$','',n) if re.search(r'(_[^_]*|\d)$',n) else ''
  return None,None
def apply(sp,files):
  p=F/(sp['f']+'.NSCR');gp,lp=gfor(p)
  g=NCGR(files.get(gp) or gp.read_bytes());s=NSCR(files.get(p) or p.read_bytes());pal=nclr(lp.read_bytes())
  # 같은 NCGR을 쓰는 화면 전체에서의 타일 사용 횟수
  use=collections.Counter()
  for q in p.parent.glob('*.NSCR'):
    if gfor(q)[0]!=gp:continue
    ss=NSCR(files.get(q) or q.read_bytes())
    for i in range(ss.sz//2):use[ss.ent(i)&0x3ff]+=1
  X0,Y0,X1,Y1=sp['rect'];ins=collections.Counter()
  for ty in range(Y0//8,(Y1+7)//8):
    for tx in range(X0//8,(X1+7)//8):ins[s.ent(s.pos(tx,ty))&0x3ff]+=1
  # 공유 타일은 안 쓰는 타일로 복제해서 분리
  free=[t for t in range(g.n-1,0,-1) if not use[t]]
  for t in [t for t in ins if use[t]>ins[t]]:
    if not free:break
    f=free.pop(0);g.settile(f,g.tile(t))
    for ty in range(Y0//8,(Y1+7)//8):
      for tx in range(X0//8,(X1+7)//8):
        i=s.pos(tx,ty);e=s.ent(i)
        if e&0x3ff==t:struct.pack_into('<H',s.d,s.o+2*i,(e&0xfc00)|f)
    use[t]-=ins[t];use[f]=ins[t];ins[f]=ins.pop(t)
  files[p]=bytes(s.d)
  def get(x,y):
    a,n,pb=pix(g,s,x,y);v=g.d[a] if n is None else (g.d[a]>>(4*n))&15
    return pal[(pb*16+v)%len(pal)] if v else pal[0]
  P={(x,y):get(x,y) for y in range(Y0,Y1) for x in range(X0,X1)}
  border=[c for (x,y),c in P.items() if x in (X0,X1-1) or y in (Y0,Y1-1)]
  if sp.get('bgat'):sp=dict(sp,bg=get(*sp['bgat']))
  if sp.get('fgat'):sp=dict(sp,fg=get(*sp['fgat']))
  bg=tuple(sp['bg']) if sp.get('bg') else collections.Counter(border).most_common(1)[0][0]
  ol=tuple(sp['ol']) if sp.get('ol') else None;fg=tuple(sp['fg']) if sp.get('fg') else None
  if ol is None and not sp.get('noline'):
    t=collections.Counter(c for (x,y),c in P.items() if c!=bg and any(P.get((x+a,y+b))==bg for a,b in((1,0),(-1,0),(0,1),(0,-1))))
    ol=t.most_common(1)[0][0] if t else None
  if fg is None:fg=next((c for c,_ in collections.Counter(P.values()).most_common() if c not in (bg,ol)),ol)
  new={q:bg for q in P}
  if sp.get('keep'):new={q:(c if c in sp['keep'] else bg) for q,c in P.items()}
  m=textmask(sp['text'],sp['h'],sp.get('font','NanumSquareNeo-eHv.ttf'),X1-X0-2)
  ox=X0+(X1-X0-m.width)//2+sp.get('dx',0);oy=Y0+(Y1-Y0-m.height)//2+sp.get('dy',0)
  on={(ox+x,oy+y) for y in range(m.height) for x in range(m.width) if m.getpixel((x,y))}
  if ol:
    R=sp.get('thick',1)
    for (x,y) in on:
      for a in range(-R,R+1):
        for b in range(-R,R+1):
          q=(x+a,y+b)
          if q in new and q not in on:new[q]=ol
  for q in on:
    if q in new:new[q]=fg
  skipped=0
  if sp.get('debug')==2:
    for y in range(Y0,Y1):print(''.join('#' if new[(x,y)]==fg else '.' for x in range(X0,X1)))
  for (x,y),cl in new.items():
    e=s.ent(s.pos(x//8,y//8));t=e&0x3ff
    if use[t]>ins[t]:skipped+=cl!=P[(x,y)];continue  # 다른 곳과 공유하는 타일
    a,n,pb=pix(g,s,x,y)
    if g.bpp==4:
      row=[(i,pal[(pb*16+i)%len(pal)]) for i in range(1,16)]
      if cl==pal[pb*16] and not P[(x,y)]==cl:v=0
      else:v=min(row,key=lambda r:sum((r[1][j]-cl[j])**2 for j in range(3)))[0] if cl!=pal[0] else 0
      g.d[a]=(g.d[a]&0xf0)|v if n==0 else (g.d[a]&0x0f)|(v<<4)
    else:
      row=[(i,pal[i]) for i in range(1,min(256,len(pal)))]
      g.d[a]=0 if cl==pal[0] else min(row,key=lambda r:sum((r[1][j]-cl[j])**2 for j in range(3)))[0]
  if skipped and sp.get('debug'):print('공유타일로 못 쓴 픽셀',sp['f'],skipped)
  files[gp]=bytes(g.d)
def run(specs,files=None):
  files={} if files is None else files
  for s in specs:apply(s,files)
  return files
def preview(specs,out):
  from PIL import Image,ImageDraw
  from nscr import render
  files=run(specs);ims=[]
  for sp in specs:
    p=F/(sp['f']+'.NSCR');gp,lp=gfor(p);pal=nclr(lp.read_bytes());s0=NSCR(p.read_bytes());s=NSCR(files.get(p) or p.read_bytes())
    X0,Y0,X1,Y1=sp['rect'];X0=max(0,X0-16);Y0=max(0,Y0-8);X1=min(s.w,X1+16);Y1=min(s.h,Y1+8)
    a=render(NCGR(gp.read_bytes()),s0,pal).crop((X0,Y0,X1,Y1));b=render(NCGR(files[gp]),s,pal).crop((X0,Y0,X1,Y1))
    ims.append((sp['f'],a,b))
  W=1024;y=0;H=sum(max(a.height*2,20)+14 for _,a,_ in ims)
  im=Image.new('RGB',(W,H),(255,0,255));d=ImageDraw.Draw(im)
  for f,a,b in ims:
    sc=2 if a.width<=250 else 1
    d.text((0,y),f,fill=(0,0,0));im.paste(a.resize((a.width*sc,a.height*sc)),(0,y+12));im.paste(b.resize((b.width*sc,b.height*sc)),(a.width*sc+8,y+12))
    y+=a.height*sc+14
  im.save(out)
