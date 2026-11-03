"""그래픽 글자 교체: trans/gfx.json 사양대로 셀 영역을 지우고 한글을 그림.
사양: {"f":"obj/main_menu/m_menu_l","cells":[0,1],"rect":[x0,y0,x1,y1],"text":"시나리오 모드",
       "h":11,"font":"NanumSquareNeo-eHv.ttf","fg":null,"ol":null,"bg":null,"align":"c"}
fg/ol/bg가 null이면 영역에서 자동 추정. 결과 바이트는 dict 경로->bytes 로 반환."""
import json,collections
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from g2d import NCGR,nclr
from cell import NCER,render,write
W=Path(__file__).resolve().parents[1];F=W/'ext/fs/file';FONTS=W.parent
_BDF={}
def bdfmask(text,name):
  from bdf import bdf
  if name not in _BDF:_BDF[name]=bdf(str(W/'fonts'/(name+'.bdf')))
  g,asc=_BDF[name];w=sum(g[ord(c)]['dw'] for c in text);H=asc+3
  im=Image.new('L',(w+2,H),0);x=0
  for c in text:
    e=g[ord(c)]
    for y,r in enumerate(e['rows']):
      for xx,v in enumerate(r):
        if v:im.putpixel((x+e['bx']+xx,asc-e['by']-e['bh']+y),255)
    x+=e['dw']
  bx=im.getbbox();return im.crop(bx)
def textmask(text,h,font,maxw):
  if chr(10) in text:
    ms=[textmask(t,h,font,maxw) for t in text.split(chr(10))];gap=max(1,h//6)
    im=Image.new('L',(max(m.width for m in ms),sum(m.height for m in ms)+gap*(len(ms)-1)),0);y=0
    for m in ms:im.paste(m,((im.width-m.width)//2,y));y+=m.height+gap
    return im
  if font.startswith('Galmuri') and not font.endswith('.ttf'):return bdfmask(text,font)
  if h<=14 or font=='galmuri':
    # 픽셀 폰트: 높이 h 이하 중 폭이 맞는 가장 큰 것
    for n,fh in [('Galmuri14',14),('Galmuri11-Bold',11),('Galmuri11',11),('Galmuri11-Condensed',11),('Galmuri9',9),('Galmuri7',7)]:
      if fh>max(h,7):continue
      m=bdfmask(text,n)
      if n=='Galmuri14':
        # 가는 14px 픽셀폰트는 1px 굵게
        b=Image.new('L',(m.width+1,m.height),0);b.paste(m,(0,0));b.paste(255,(1,0),m.convert('1'));m=b
      if m.width<=maxw:return m
    if h<=10:return m
    h=max(h,9)
  # 큰 크기로 그려 높이 h에 맞게 축소 후 이진화
  # 힌팅된 흑백 렌더(안티에일리어싱 없이 또렷하게): 높이 h, 폭 maxw 안에 드는 가장 큰 크기
  best=None
  for sz in range(h+3,6,-1):
    f=ImageFont.truetype(str(FONTS/font),sz);bb=f.getbbox(text)
    im=Image.new('1',(bb[2]-bb[0]+8,sz*2),0);d=ImageDraw.Draw(im);d.fontmode='1';d.text((4-bb[0],0),text,font=f,fill=1)
    ref=f.getbbox('가');gh=ref[3]-ref[1]
    m=im.convert('L');bx=m.getbbox();m=m.crop(bx) if bx else m
    best=m
    if gh<=h and m.width<=maxw:return m
  return best
DONE={};DIAG=[]
def autorect(im,spec):
  """판(테두리로 둘러싼 단색 영역)이 있으면 판 안쪽, 없으면 셀 전체"""
  W,H=im.size;px=im.load()
  op=[(x,y) for y in range(H) for x in range(W) if px[x,y][3]]
  if not op:return 0,0,W,H
  full=(0,0,W,H)
  if spec.get('nopanel'):return full
  cnt=collections.Counter(px[p][:3] for p in op);P,n=cnt.most_common(1)[0]
  if n<len(op)*0.25:return full
  ps=[p for p in op if px[p][:3]==P];bx0=min(x for x,_ in ps);bx1=max(x for x,_ in ps)+1;by0=min(y for _,y in ps);by1=max(y for _,y in ps)+1
  ring=set()
  for x in range(bx0-1,bx1+1):
    for y in (by0-1,by1):
      if 0<=x<W and 0<=y<H and px[x,y][3]:ring.add(px[x,y][:3])
  for y in range(by0-1,by1+1):
    for x in (bx0-1,bx1):
      if 0<=x<W and 0<=y<H and px[x,y][3]:ring.add(px[x,y][:3])
  if len(ring)>4 or (bx1-bx0)*(by1-by0)<W*H*0.2:return full
  e=spec.get('edge',1)
  return bx0+e,by0+e,bx1-e,by1-e
def apply(spec,files):
  for key in ['NCGR','NCBR']:
    gp=F/(spec.get('g',spec['f'])+'.'+key)
    if not gp.exists():continue
    raw=files.get(gp) or gp.read_bytes()
    g=NCGR(raw);c=NCER((F/(spec['f']+'.NCER')).read_bytes());lin=g.tiled==1
    pal=nclr((F/(spec.get('pal',spec.get('g',spec['f']))+'.NCLR')).read_bytes())
    for cell in spec['cells']:
      r=render(g,c,pal,cell,lin)
      if r[0] is None:print('빈 셀',spec['f'],cell);continue
      im,(x0,y0,idx)=r
      if spec.get('onlypal') is not None:
        oa=[o for o in c.cells[cell] if o['pal']==spec['onlypal']];mx=min(o['x'] for o in c.cells[cell]);my=min(o['y'] for o in c.cells[cell])
        spec=dict(spec,rect=[min(o['x'] for o in oa)-mx,min(o['y'] for o in oa)-my,max(o['x']+o['w'] for o in oa)-mx,max(o['y']+o['h'] for o in oa)-my],clear=0 if spec.get('bg') else 1,snap=0)
        if spec.get('cliprect'):spec=dict(spec,rect=[max(a,b) if i<2 else min(a,b) for i,(a,b) in enumerate(zip(spec['rect'],spec['cliprect']))])
      if spec.get('rect')=='auto':X0,Y0,X1,Y1=autorect(im,spec)
      elif 'rect' in spec:X0,Y0,X1,Y1=spec['rect']
      else:
        i=spec.get('inset',0);ib=spec.get('insetb',i);X0,Y0,X1,Y1=i,i,im.width-i,im.height-ib
      _px=im.load()
      def vis(p):
        c_=_px[p];return c_[:3] if c_[3] else None
      def col(v):return pal[(v[1]*16+v[2])%len(pal)] if v[2] else None
      if spec.get('snap') and isinstance(spec.get('rect'),list):
        # 대략 영역을 주변 배경색 기준으로 실제 글자 경계에 맞춤
        if spec.get('bgat'):b0=vis(tuple(spec['bgat'])) if tuple(spec['bgat']) in idx else None
        else:
          rg=collections.Counter(vis((x,y)) for (x,y),v in idx.items() if X0<=x<X1 and Y0<=y<Y1)
          b0=rg.most_common(1)[0][0] if rg else None
        ex,ey=spec.get('snapx',2),spec.get('snapy',4)
        pts=[(x,y) for (x,y),v in idx.items() if X0-ex<=x<X1+ex and Y0-ey<=y<Y1+ey and vis((x,y))!=b0]
        # 영역 밖으로 이어진 테두리선 제외: 원래 영역과 겹치는 행/열만
        pts=[(x,y) for x,y in pts if X0-ex<=x<X1+ex and Y0-ey<=y<Y1+ey]
        if pts:
          xs=[x for x,_ in pts];ys=[y for _,y in pts]
          # 행 단위로 거의 꽉 찬(테두리) 행은 제외
          rows=collections.Counter(ys);w=X1-X0+2*ex
          ys2=[y for y in ys if rows[y]<w*0.9];ys=ys2 or ys
          cols_=collections.Counter(xs);hh=Y1-Y0+2*ey
          xs2=[x for x in xs if cols_[x]<hh*0.9];xs=xs2 or xs
          X0,Y0,X1,Y1=max(X0-ex,min(xs)-1),max(Y0-ey,min(ys)-1),min(X1+ex,max(xs)+2),min(Y1+ey,max(ys)+2)
          if spec.get('debug'):print('snap',X0,Y0,X1,Y1,'bg',b0)
        if spec.get('bg') is None:spec=dict(spec,bg=list(b0) if b0 else None,clear=0 if b0 else 1)
      inr=[(p,vis(p)) for p,v in idx.items() if X0<=p[0]<X1 and Y0<=p[1]<Y1]
      border=[v for (x,y),v in inr if x in (X0,X1-1) or y in (Y0,Y1-1)]
      rawb=collections.Counter(idx[(x,y)][2] for (x,y),v in inr if x in (X0,X1-1) or y in (Y0,Y1-1))
      def at(q):
        return vis(tuple(q)) if tuple(q) in idx else None
      for kk in ('bg','fg','ol'):
        if spec.get(kk+'at'):spec=dict(spec,**{kk:at(spec[kk+'at']) or [0,0,0]})
      bg=spec.get('bg');bg=collections.Counter(border).most_common(1)[0][0] if bg is None else tuple(bg)
      if spec.get('bgmajor'):bg=collections.Counter(v for _,v in inr if v is not None).most_common(1)[0][0]
      if spec.get('nopanel') and spec.get('bg') is None and spec.get('mode')!='ring':bg=None
      cnt=collections.Counter(v for _,v in inr if v!=bg).most_common()
      fg=spec.get('fg');ol=spec.get('ol')
      fg=tuple(fg) if fg else None;ol=tuple(ol) if ol else None
      if fg is None or ol is None:
        P=dict(inr);touch=collections.Counter()
        for (x,y),v in inr:
          if v!=bg and any(P.get((x+a,y+b))==bg for a,b in((1,0),(-1,0),(0,1),(0,-1))):touch[v]+=1
        if ol is None:ol=touch.most_common(1)[0][0] if touch else None
        if fg is None:fg=next((v for v,_ in cnt if v not in (ol,None)),ol)
      if ol is None:ol=next((v for v,_ in cnt if v not in (None,bg,fg)),None)
      colbg=None
      if spec.get('mode')=='ring':
        # 테두리 링에 (거의) 없는 색 = 글자색, 열마다 글자색 아닌 최빈색으로 배경 복원
        P=dict(inr);PA={p:vis(p) for p,v in idx.items()}
        # 열 배경: 영역 바로 위/아래(최대 3px) 픽셀의 최빈색(투명 포함)
        colbg={}
        for x in range(X0,X1):
          cc=collections.Counter(PA.get((x,y),'o') for y in list(range(max(0,Y0-3),Y0))+list(range(Y1,min(im.height,Y1+3))) if 0<=y<im.height)
          cc.pop('o',None)
          if cc:colbg[x]=cc.most_common(1)[0][0]
        if len(colbg)==X1-X0 and spec.get('colmode'):
          T={v for (x,y),v in inr if v!=colbg[x]}
          for v in spec.get('ntc',[]):T.discard(tuple(v))
          touch=collections.Counter()
          for (x,y),v in inr:
            if v in T and any(P.get((x+a,y+b),colbg.get(x+a,'x'))==colbg.get(x+a,'y') for a,b in((1,0),(-1,0),(0,1),(0,-1))):touch[v]+=1
          tc=collections.Counter(v for (x,y),v in inr if v in T)
          if not spec.get('ol'):ol=touch.most_common(1)[0][0] if touch else None
          if not spec.get('fg'):fg=next((v for v,_ in tc.most_common() if v!=ol and v is not None),ol)
          if spec.get('debug'):print('colbg-mode fg',fg,'ol',ol)
          spec=dict(spec,mode='done')
        ring=collections.Counter(v for (x,y),v in inr if x in (X0,X1-1) or y in (Y0,Y1-1))
        nr=sum(ring.values()) or 1
      if spec.get('mode')=='ring':
        allc=collections.Counter(v for _,v in inr)
        T={v for v in allc if v is not None and ring.get(v,0)<=nr*spec.get('ringtol',0.03)}
        if spec.get('fg'):T.add(tuple(spec['fg']))
        if spec.get('ol'):T.add(tuple(spec['ol']))
        for v in spec.get('tc',[]):T.add(tuple(v))
        for v in spec.get('ntc',[]):T.discard(tuple(v))
        if spec.get('white'):T={v for v in allc if v and min(v)>=spec['white']}
        touch=collections.Counter()
        for (x,y),v in inr:
          if v in T and any(P.get((x+a,y+b),'x') not in T for a,b in((1,0),(-1,0),(0,1),(0,-1))):touch[v]+=1
        tc=collections.Counter(v for _,v in inr if v in T)
        if not spec.get('ol'):ol=touch.most_common(1)[0][0] if touch else None
        if not spec.get('fg'):fg=next((v for v,_ in tc.most_common() if v!=ol),ol)
        if spec.get('fg') and not spec.get('ol') and ol==tuple(spec['fg']):ol=next((v for v,_ in touch.most_common() if v!=ol),None)
        colbg={}
        for x in range(X0,X1):
          cc=collections.Counter(P.get((x,y)) for y in range(Y0,Y1) if (x,y) in P and P[(x,y)] not in T)
          if cc and sum(cc.values())>=(Y1-Y0)*0.4:colbg[x]=cc.most_common(1)[0][0]
        for x in range(X0,X1):
          if x not in colbg:
            near=min(colbg,key=lambda q:abs(q-x)) if colbg else None
            colbg[x]=colbg[near] if near is not None else bg
        for x in range(X0+1,X1-1):
          # 한두 열짜리 튀는 값(원래 글자 세로획) 제거
          for w in (1,2,3):
            a_,b_,c_=colbg.get(x-1),colbg.get(x+w),colbg[x]
            near_=lambda p,q:p is not None and q is not None and sum((p[j]-q[j])**2 for j in range(3))<45**2
            if X0<=x-1 and x+w<X1 and near_(a_,b_) and not near_(c_,a_):
              for q in range(x,x+w):colbg[q]=colbg[x-1]
        if spec.get('debug'):print('T',T,'fg',fg,'ol',ol)
      if 'shadow' not in spec and fg and ol and fg!=ol:
        # 외곽선인지 오른쪽 아래 그림자인지 원본 모양으로 판별
        P2=dict(inr);dr=ul=0
        for (x,y),v in inr:
          if v==ol:
            if P2.get((x-1,y-1))==fg or P2.get((x-1,y))==fg or P2.get((x,y-1))==fg:dr+=1
            if P2.get((x+1,y+1))==fg or P2.get((x+1,y))==fg or P2.get((x,y+1))==fg:ul+=1
        if dr>0 and ul<dr*0.35:spec=dict(spec,shadow=1)
        if spec.get('debug'):print('shadow?',dr,ul)
      if spec.get('noline'):ol=None
      if spec.get('clear'):bg=None
      if spec.get('debug'):print('bg',bg,'fg',fg,'ol',ol,cnt[:5])
      new={p:(colbg[p[0]] if colbg else bg) for p,_ in inr}
      if spec.get('overlay'):_bs={c for c,_ in collections.Counter(border).most_common(spec.get('overlay')+0) if c};new={p:(v if v in _bs else bg) for p,v in inr}
      if 'textrect' in spec:X0,Y0,X1,Y1=spec['textrect']
      hh=spec.get('h') or (Y1-Y0-2)
      if not spec.get('nofit'):
        # 실제로 쓸 수 있는(공유되지 않은 타일이 덮는) 영역에 글자 상자를 맞춤
        from cell import objpix
        oa=c.cells[cell];mx=min(o['x'] for o in oa);my=min(o['y'] for o in oa);wr=set()
        for o in oa:
          if spec.get('onlypal') is not None and o['pal']!=spec['onlypal']:continue
          for (X,Y),k in objpix(g,o,c.mapmode,lin).items():
            q=(o['x']-mx+X,o['y']-my+Y)
            if X0<=q[0]<X1 and Y0<=q[1]<Y1 and len(OWN.get(gp,{}).get(k//64,()))<=1:wr.add(q)
        if wr:
          bx0=min(x for x,_ in wr);bx1=max(x for x,_ in wr)+1;by0=min(y for _,y in wr);by1=max(y for _,y in wr)+1
          X0,Y0,X1,Y1=max(X0,bx0),max(Y0,by0),min(X1,bx1),min(Y1,by1)
          lim=(Y1-Y0)-(2*spec.get('thick',1) if ol and not spec.get('shadow') else (1 if ol else 0))
          nl=spec['text'].count(chr(10))+1
          if nl>1:lim=(lim-(nl-1))//nl
          if hh>lim:hh=max(7,lim)
          if spec.get('debug'):print('fit',X0,Y0,X1,Y1,'h',hh)
      m=textmask(spec['text'],hh,spec.get('font','NanumSquareNeo-eHv.ttf'),X1-X0-(2*spec.get('thick',1) if ol else 0))
      av=(Y1-Y0)-(2*spec.get('thick',1) if ol and not spec.get('shadow') else (1 if ol else 0))
      while m.height>av and hh>7 and not spec.get('nofit'):
        hh-=1;m=textmask(spec['text'],hh,spec.get('font','NanumSquareNeo-eHv.ttf'),X1-X0-(2*spec.get('thick',1) if ol else 0))
      pad=1 if ol else 0
      al=spec.get('align','c')
      ox=X0+pad+spec.get('ml',0) if al=='l' else (X1-pad-spec.get('mr',0)-m.width if al=='r' else X0+(X1-X0-m.width)//2)
      oy=Y0+(Y1-Y0-m.height)//2+spec.get('dy',0)
      on={(ox+x,oy+y) for y in range(m.height) for x in range(m.width) if m.getpixel((x,y))}
      if ol and spec.get('shadow'):
        for (x,y) in list(on):
          q=(x+1,y+1)
          if q in new and q not in on:new[q]=ol
      elif ol:
        for (x,y) in list(on):
          R=spec.get('thick',1)
          for a in range(-R,R+1):
            for b in range(-R,R+1):
              q=(x+a,y+b)
              if q in new and q not in on:new[q]=ol
      if spec.get('ol2'):
        R=spec.get('thick',1)+spec.get('thick2',1);inner=set(on)
        for (x,y) in list(on):
          for a in range(-spec.get('thick',1),spec.get('thick',1)+1):
            for b in range(-spec.get('thick',1),spec.get('thick',1)+1):inner.add((x+a,y+b))
        for (x,y) in list(on):
          for a in range(-R,R+1):
            for b in range(-R,R+1):
              q=(x+a,y+b)
              if q in new and q not in inner:new[q]=tuple(spec['ol2'])
      gr=spec.get('grad')
      if gr and on:
        ya=min(y for _,y in on);yb=max(y for _,y in on) or 1
      for q in on:
        if q in new:
          if gr:
            t=(q[1]-ya)/max(1,yb-ya);c_=[];n=len(gr)-1;i_=min(int(t*n),n-1);u=t*n-i_
            new[q]=tuple(int(gr[i_][j]*(1-u)+gr[i_+1][j]*u) for j in range(3))
          else:new[q]=fg
      # 겹별 기록: 위 겹부터, 원래 투명하던 겹은 배경이면 투명 유지하고 아래 겹에 배경을 씀
      from cell import objpix
      oams=c.cells[cell];x0=min(o['x'] for o in oams);y0=min(o['y'] for o in oams)
      L=[]  # 겹별 {p:(k,v)}
      for o in oams:
        if spec.get('onlypal') is not None and o['pal']!=spec['onlypal']:continue
        m={}
        for (X,Y),k in objpix(g,o,c.mapmode,lin).items():
          q=(o['x']-x0+X,o['y']-y0+Y)
          if q in new:
            bb=g.d[g.o+k//2];m[q]=(k,(bb>>(4*(k&1)))&15)
        L.append((o,m))
      cm=collections.defaultdict(collections.Counter);hasz=set()
      for oi,(o,m) in enumerate(L):
        for q,(k,v) in m.items():
          if v:cm[(o['pal'],pal[(o['pal']*16+v)%len(pal)])][v]+=1
          else:hasz.add(oi)
      def mapv(pb,cl):
        if cm.get((pb,cl)):return cm[(pb,cl)].most_common(1)[0][0]
        row=[(i,pal[(pb*16+i)%len(pal)]) for i in range(1,16)]
        return min(row,key=lambda t:sum((t[1][j]-cl[j])**2 for j in range(3)))[0]
      cov=set().union(*[set(m) for _,m in L]) if L else set()
      DIAG.append(dict(key=spec.get('key',spec['f']),f=spec['f'],cell=cell,gp=gp,new=dict(new),lost=sum(1 for q in on if q not in cov),non=len(on),rect=(X0,Y0,X1,Y1)))
      W_=DONE.setdefault(gp,set())
      for q,cl in new.items():
        layers=[(o,m[q]) for o,m in L if q in m]
        if not layers:continue
        for li,(o,(k,v)) in enumerate(layers):
          if spec.get('onlypal') is not None and o['pal']!=spec['onlypal']:continue
          if li and not v:continue  # 아래 겹: 원래 불투명한 곳만 같은 색으로 덮어 잔재 제거
          below=next((pal[(o2['pal']*16+v2)%len(pal)] for o2,(k2,v2) in layers[li+1:] if v2),None)
          if cl is None:val=0
          elif below is not None and below==cl and not spec.get('opaque'):val=0  # 아래 겹이 이미 그 색이면 투명
          elif v and pal[(o['pal']*16+v)%len(pal)]==cl and (li>0 or below is None):val=v  # 원래 색 그대로면 원래 인덱스 유지
          else:val=mapv(o['pal'],cl)
          if k in W_:continue
          if len(OWN.get(gp,{}).get(k//64,()))>1:continue  # 다른 글자 셀과 공유하는 타일(테두리 등)은 건드리지 않음
          W_.add(k);aa=g.o+k//2;bb=g.d[aa]
          g.d[aa]=(bb&0xf0)|val if k&1==0 else (bb&0x0f)|(val<<4)
    files[gp]=bytes(g.d)
  return files
OWN={}
def owners(specs):
  from cell import objpix
  OWN.clear();cache={}
  for sp in specs:
    for key in ['NCGR','NCBR']:
      gp=F/(sp.get('g',sp['f'])+'.'+key)
      if not gp.exists():continue
      if (gp,sp['f']) not in cache:
        g=NCGR(gp.read_bytes());c=NCER((F/(sp['f']+'.NCER')).read_bytes());cache[(gp,sp['f'])]=(g,c)
      g,c=cache[(gp,sp['f'])];D=OWN.setdefault(gp,{})
      for cl in sp['cells']:
        if cl>=len(c.cells):continue
        x0=min(o['x'] for o in c.cells[cl]) if c.cells[cl] else 0;y0=min(o['y'] for o in c.cells[cl]) if c.cells[cl] else 0
        R=sp.get('rect') if isinstance(sp.get('rect'),list) and not sp.get('onlypal') else None
        for o in c.cells[cl]:
          for (X,Y),k in objpix(g,o,c.mapmode,g.tiled==1).items():
            if R and not (R[0]<=o['x']-x0+X<R[2] and R[1]<=o['y']-y0+Y<R[3]):continue
            D.setdefault(k//64,set()).add(sp['text'])
def run(specs):
  files={};DONE.clear();DIAG.clear();owners(specs)
  for s in specs:apply(s,files)
  return files
def preview(spec,out):
  files=apply(spec,{})
  for gp,b in files.items():
    g=NCGR(b);c=NCER((F/(spec['f']+'.NCER')).read_bytes());pal=nclr((F/(spec.get('pal',spec['f'])+'.NCLR')).read_bytes())
    ims=[render(g,c,pal,k,g.tiled==1)[0] for k in spec['cells']]
    o=Image.new('RGBA',(max(i.width for i in ims),sum(i.height+2 for i in ims)),(255,0,255,255));y=0
    for i in ims:o.paste(i,(0,y),i);y+=i.height+2
    o.resize((o.width*3,o.height*3),0).save(out);return
