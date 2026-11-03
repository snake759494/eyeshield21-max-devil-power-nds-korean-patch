def bdf(path):
  g={};lines=open(path,encoding='utf8').read().splitlines();i=0
  asc=0
  for l in lines:
    if l.startswith('FONT_ASCENT'):asc=int(l.split()[1])
  while i<len(lines):
    l=lines[i]
    if l.startswith('ENCODING'):enc=int(l.split()[1])
    elif l.startswith('DWIDTH'):dw=int(l.split()[1])
    elif l.startswith('BBX'):bw,bh,bx,by=map(int,l.split()[1:])
    elif l=='BITMAP':
      rows=[]
      for j in range(bh):rows.append(int(lines[i+1+j],16))
      nb=((bw+7)//8)*8
      g[enc]=dict(dw=dw,bw=bw,bh=bh,bx=bx,by=by,rows=[[(r>>(nb-1-x))&1 for x in range(bw)] for r in rows])
      i+=bh
    i+=1
  return g,asc
