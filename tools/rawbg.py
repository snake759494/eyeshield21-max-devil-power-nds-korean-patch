"""bg/*.bin (헤더 없는 BG) 글자 교체"""
import sys,struct,collections
sys.path.insert(0,str(__import__('pathlib').Path(__file__).parent))
from bgbin import F,layers,colors,render
from gtext import textmask
from pathlib import Path
RS=[]
def add(n,k,rect,text,h,**kw):RS.append(dict(n=n,k=k,rect=rect,text=text,h=h,**kw))
for i,(t,y) in enumerate([('터치다운',63),('필드골',82),('트라이 포 포인트',101),('세이프티',120),('토탈',142)]):
  add('result',2,[72,y-6,184,y+6],t,12,fg=[248,248,248],bgat=[73,y-5],noline=1)
add('quiz',0,[23,122,46,133],'정답',11,noline=1,bgat=[23,122],fg=[248,248,248])
add('quiz',0,[78,146,101,156],'문제',10,noline=1,bgat=[100,147],fg=[248,248,248])
def credits(P):
  new={q:None for q in P}
  def put(t,h,x0,x1,y0):
    m=textmask(t,h,'NanumSquareNeo-eHv.ttf',x1-x0);ox=x0+(x1-x0-m.width)//2
    for y in range(m.height):
      for x in range(m.width):
        if m.getpixel((x,y)):new[(ox+x,y0+y)]=(248,248,248)
  put('원작·이나가키 리이치로',7,32,128,81);put('만화·무라타 유스케',7,144,224,81)
  put('(슈에이샤 「주간 소년 점프」 연재)',9,40,216,99)
  return new
def logo(P):
  from PIL import Image,ImageDraw,ImageFont
  from gtext import FONTS as F_
  xs=[x for x,_ in P];ys=[y for _,y in P];X0,Y0,X1,Y1=min(xs),min(ys),max(xs)+1,max(ys)+1
  f=ImageFont.truetype(str(F_/'NanumSquareNeo-eHv.ttf'),44)
  t='아이실드';bb=f.getbbox(t);m=Image.new('L',(bb[2]-bb[0]+40,bb[3]-bb[1]+8),0)
  ImageDraw.Draw(m).text((20-bb[0],4-bb[1]),t,font=f,fill=255)
  m=m.transform(m.size,Image.AFFINE,(1,0.25,-0.25*m.height/2,0,1,0),Image.BILINEAR).point(lambda v:255 if v>110 else 0)
  m=m.crop(m.getbbox());W,H=98,36
  m=m;m=m.resize((W,H),Image.NEAREST)
  on={(48+x,81+y) for y in range(H) for x in range(W) if m.getpixel((x,y))}
  G=[(216,8,16),(224,8,8),(232,32,16),(232,64,8),(232,88,0),(240,128,0),(240,168,0),(240,184,0)]
  new={}
  for q,c in P.items():
    star=c and ((c[0]>190 and c[1]>195 and c[2]<80 and (q[1]<114 or q[0]<52)) or (c[1]>c[0]+30 and q[0]>140) or q[0]>=162 or (q[0]>=146 and q[1]>=88))
    new[q]='keep' if star else None
  ring=lambda S:{(x+a,y+b) for x,y in S for a in(-1,0,1) for b in(-1,0,1)}-S
  w=ring(on);k=ring(on|w)
  for q in k:
    if q in new:new[q]=(0,0,0)
  for q in w:
    if q in new:new[q]=(248,248,248)
  for q in on:
    if q in new:new[q]='warm'
  return new
add('title',1,[36,60,160,126],'',0,fn=logo)
add('title',2,[32,72,224,112],'',0,fn=credits)
def apply(sp,files):
  n=sp['n'];p=F/(n+'.bin');d=bytearray(files.get(p) or p.read_bytes())
  L=layers(n)[sp['k']];_,bpp=render(n,L);pal=colors(d,L['pal'])
  ents=struct.unpack_from('<768H',d,L['map']);use=collections.Counter(e&0x3ff for e in ents)
  def addr(x,y):
    e=ents[(y//8)*32+x//8];t=e&0x3ff;hf=(e>>10)&1;vf=(e>>11)&1;pb=e>>12
    sx=7-x%8 if hf else x%8;sy=7-y%8 if vf else y%8
    if bpp==4:return L['tile']+t*32+(sy*8+sx)//2,sx&1,pb,t
    return L['tile']+t*64+sy*8+sx,None,0,t
  def get(x,y):
    a,nb,pb,_=addr(x,y);v=d[a] if nb is None else (d[a]>>(4*nb))&15
    return pal[pb*16+v] if v else None
  X0,Y0,X1,Y1=sp['rect']
  ins=collections.Counter(ents[(ty)*32+tx]&0x3ff for ty in range(Y0//8,(Y1+7)//8) for tx in range(X0//8,(X1+7)//8))
  if sp.get('unshare'):
    ts=32 if bpp==4 else 64;nt=L['tsize']//ts;free=[t for t in range(nt-1,0,-1) if not use[t]]
    for t in [t for t in list(ins) if use[t]>ins[t]]:
      if not free:break
      f=free.pop(0);d[L['tile']+f*ts:L['tile']+(f+1)*ts]=d[L['tile']+t*ts:L['tile']+(t+1)*ts]
      el=list(ents)
      for ty in range(Y0//8,(Y1+7)//8):
        for tx in range(X0//8,(X1+7)//8):
          i=ty*32+tx
          if el[i]&0x3ff==t:el[i]=(el[i]&0xfc00)|f;struct.pack_into('<H',d,L['map']+2*i,el[i])
      ents=tuple(el);use[t]-=ins[t];use[f]=ins[t];ins[f]=ins.pop(t)
    print('unshare free left',len(free))
  P={(x,y):get(x,y) for y in range(Y0,Y1) for x in range(X0,X1)}
  if sp.get('fn'):
    new=sp['fn'](P)
  else:
   bg=get(*sp['bgat']) if sp.get('bgat') else collections.Counter(P.values()).most_common(1)[0][0]
   fg=tuple(sp['fg']) if sp.get('fg') else next((c for c,_ in collections.Counter(P.values()).most_common() if c!=bg),bg)
   new={q:bg for q in P}
   m=textmask(sp['text'],sp['h'],'NanumSquareNeo-eHv.ttf',X1-X0-2)
   ox=X0+(X1-X0-m.width)//2;oy=Y0+(Y1-Y0-m.height)//2
   for y in range(m.height):
     for x in range(m.width):
       if m.getpixel((x,y)) and (ox+x,oy+y) in new:new[(ox+x,oy+y)]=fg
  for (x,y),cl in new.items():
    a,nb,pb,t=addr(x,y)
    if use[t]>ins[t]:continue
    if cl=='keep':continue
    if cl=='warm':
      v=max(range(1,16),key=lambda i:(pal[pb*16+i][0]>140)*1000+pal[pb*16+i][0]+pal[pb*16+i][1]*0.4-pal[pb*16+i][2]*2)
    elif cl is None:v=0
    elif bpp==4 and cl!='warm':v=min(range(1,16),key=lambda i:sum((pal[pb*16+i][j]-cl[j])**2 for j in range(3)))
    elif cl!='warm':v=min(range(1,256),key=lambda i:sum((pal[i][j]-cl[j])**2 for j in range(3)))
    if nb is None:d[a]=v
    else:d[a]=(d[a]&0xf0)|v if nb==0 else (d[a]&0x0f)|(v<<4)
  files[p]=bytes(d)
def run(specs=RS,files=None):
  files={} if files is None else files
  for s in specs:apply(s,files)
  return files
if __name__=='__main__':
  from PIL import Image
  fs=run();out=Image.new('RGB',(1024,400),(255,0,255));x=0
  for n,k in [('title',1),('title',2)]:
    L=layers(n)[k];a,_=render(n,L)
    p=F/(n+'.bin');orig=p.read_bytes();p_=fs[p]
    import bgbin
    bgbin_d=p.read_bytes
    # 결과 렌더: 임시로 파일 내용 교체
    p.write_bytes(p_)
    try:b,_=render(n,L)
    finally:p.write_bytes(orig)
    out.paste(a.resize((512,384)) if False else a,(x,0));out.paste(b,(x,200));x+=260
  out.save(sys.argv[1] if len(sys.argv)>1 else 'survey/rawbg.png')
