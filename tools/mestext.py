"""gam/mes.NCBR 경기 배너(インターセプト! 등): 일본어 부분을 지우고 같은 스타일의 한글로 다시 그림"""
import sys,collections
sys.path.insert(0,str(__import__('pathlib').Path(__file__).parent))
from mes import F,NCER,NCGR,nclr,bases,pixmap
from gtext import FONTS
from PIL import Image,ImageDraw,ImageFont
DARK=(0,0,8);WHITE=(248,248,248)
# 셀: [(영역 또는 'top', 한글)]
SP={0:38,1:21,2:38,3:38,4:25,7:23,8:20,9:25,10:27,11:21,12:38,13:23,14:24,15:23,16:23,17:22,18:25}
S={0:'인터셉트!',1:'킥오프!',2:'터치다운!',3:'골!',4:'퍼스트 다운!',7:'세이프티!',8:'터치백',9:'트라이 포 포인트',
  10:'필드골',11:'펀트',12:'펌블!',13:'턴오버',14:'패스 실패',15:'야드 게인!',16:'야드 로스!',17:'하프타임',18:'게임 세트'}
for k in (19,20,21,22):S[k]=[((34,0,112,32),'다운')]
for k in (25,26,27,28):S[k]=[((30,0,142,18),'쿼터')]
S[29]=[((0,0,256,38),'퍼스트 다운까지'),((54,38,106,72),'남은'),((150,38,256,72),'야드')]
S[30]=[((0,0,255,38),'터치다운까지'),((54,38,106,72),'남은'),((150,38,255,72),'야드')]
S[31]=[((0,0,240,64),'공수 교대!')]
def mask(t,w,h,sh=0.22):
  """기울인 굵은 한글 마스크(폭 w, 높이 h 이내)"""
  f=ImageFont.truetype(str(FONTS/'NanumSquareNeo-eHv.ttf'),64)
  bb=f.getbbox(t);m=Image.new('L',(bb[2]-bb[0]+80,bb[3]-bb[1]+20),0)
  ImageDraw.Draw(m).text((40-bb[0],10-bb[1]),t,font=f,fill=255)
  m=m.transform(m.size,Image.AFFINE,(1,sh,-sh*m.height/2,0,1,0),Image.BILINEAR)
  m=m.crop(m.getbbox())
  W_=int(m.width*h/m.height);H_=h
  if W_>w:H_=max(1,min(h,int(h*w/W_*1.3)));W_=w
  elif W_<w*0.85:W_=min(int(w*0.85),int(W_*1.8))
  return m.resize((W_,H_),Image.LANCZOS).point(lambda v:255 if v>120 else 0)
def ring(S,r):
  out=set()
  for x,y in S:
    for a in range(-r,r+1):
      for b in range(-r,r+1):
        if abs(a)+abs(b)<=r+r//2:out.add((x+a,y+b))
  return out-S
def apply(g,c,b,pal,k,spec):
  oams=c.cells[k];pm=pixmap(c,k,b[k]*2)
  def get(q):
    n,o=pm[q];a=g.o+n//2;v=(g.d[a]>>(4*(n&1)))&15;return v,o
  W=max(o['x']+o['w'] for o in oams)-min(o['x'] for o in oams);H=max(o['y']+o['h'] for o in oams)-min(o['y'] for o in oams)
  cols=collections.Counter(pal[(o['pal']*16+v)] for q in pm for v,o in [get(q)] if v)
  fill=next(cl for cl,_ in cols.most_common() if cl not in (DARK,WHITE) and max(cl)-min(cl)>60)
  new={}
  if isinstance(spec,str):
    sp=SP[k]
    # 영어 판 바깥(일본어 판이 아래로 삐져나온 부분) 지우기
    yy=min(H-1,sp+6);xs=[x for x in range(W) if (x,yy) in pm and get((x,yy))[0]]
    if xs:
      lo,hi=min(xs),max(xs)
      for y in range(sp,H):
        for x in range(W):
          if (x,y) in pm and (x<lo-1 or x>hi+1):new[(x,y)]=None
    spec=[((0,0,W,sp),spec)]
  for (x0,y0,x1,y1),t in spec:
    if y1=='top':
      ws=[]
      for y in range(H):
        xs=[x for x in range(x0,x1) if (x,y) in pm and get((x,y))[0]]
        ws.append(max(xs)-min(xs) if xs else 0)
      mx=max(ws[:H*2//3]);top=ws.index(mx);y1=next((y for y in range(top,H) if ws[y]<mx*0.8),H)
    for y in range(y0,y1):
      for x in range(x0,x1):
        if (x,y) in pm:new[(x,y)]=None
    yt=next((y for y in range(y0,y1) if sum(1 for x in range(x0,x1) if (x,y) in pm)>(x1-x0)*0.6),y0)
    rr=4 if y1-yt>=24 else 2;th=y1-yt-2*rr;sm=rr==2
    m=mask(t,x1-x0-14,th)
    ox=x0+(x1-x0-m.width)//2;oy=yt+rr+(th-m.height)
    on={(ox+x,oy+y) for y in range(m.height) for x in range(m.width) if m.getpixel((x,y))}
    r1=ring(on,1);r2=ring(on|r1,1 if sm else 2);r3=ring(on|r1|r2,1 if sm else 2)
    for q in r3:
      if q in pm and q not in new or (q in new and new[q] is None):new[q]=DARK
    for q in r2:
      if q in pm:new[q]=WHITE
    for q in r1:
      if q in pm:new[q]=DARK
    for q in on:
      if q in pm:new[q]=fill
  for q,cl in new.items():
    n,o=pm[q];a=g.o+n//2
    if cl is None:v=0
    else:v=min(range(1,16),key=lambda i:sum((pal[o['pal']*16+i][j]-cl[j])**2 for j in range(3)))
    g.d[a]=(g.d[a]&0xf0)|v if n&1==0 else (g.d[a]&0x0f)|(v<<4)
def run(files=None):
  files={} if files is None else files
  p=F/'mes.NCBR';g=NCGR(files.get(p) or p.read_bytes());c=NCER((F/'mes.NCER').read_bytes());b=bases(c)
  pal=nclr((F/'game_cmn.NCLR').read_bytes())
  for k,s in S.items():apply(g,c,b,pal,k,s)
  files[p]=bytes(g.d);return files
if __name__=='__main__':
  from mes import render
  fs=run();g=NCGR(fs[F/'mes.NCBR']);c=NCER((F/'mes.NCER').read_bytes());b=bases(c);pal=nclr((F/'game_cmn.NCLR').read_bytes())
  g0=NCGR((F/'mes.NCBR').read_bytes())
  o=Image.new('RGB',(1100,2200),(120,120,120));x=y=rh=0
  for k in sorted(S):
    a=render(g0,c,pal,k,b);n=render(g,c,pal,k,b)
    w=a.width+n.width+16
    if x+w>1100:x=0;y+=rh+6;rh=0
    o.paste(a,(x,y),a);o.paste(n,(x+a.width+8,y),n);x+=w+12;rh=max(rh,a.height)
  o.crop((0,0,1100,y+rh)).save(sys.argv[1] if len(sys.argv)>1 else 'shots/mes2.png')
