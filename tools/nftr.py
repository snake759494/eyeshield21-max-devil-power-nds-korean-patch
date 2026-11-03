"""NFTR 읽기/쓰기 (2bpp, SJIS cmap)"""
import struct
class NFTR:
  def __init__(s,d):
    s.d=bytearray(d)
    p=0x10;s.blocks={}
    s.cmaps=[]
    while p<len(d):
      tag=bytes(d[p:p+4]);sz=struct.unpack_from('<I',d,p+4)[0]
      if tag==b'PLGC':s.cglp=p
      elif tag==b'HDWC':s.cwdh=p
      elif tag==b'PAMC':s.cmaps.append(p)
      p+=sz
    c=s.cglp;s.cw,s.ch,s.tsz=d[c+8],d[c+9],struct.unpack_from('<H',d,c+10)[0];s.bpp=d[c+14]
    s.gbase=c+0x10;s.n=(struct.unpack_from('<I',d,c+4)[0]-0x10)//s.tsz
    s.map={}
    for p in s.cmaps:
      lo,hi,t=struct.unpack_from('<HHH',d,p+8)
      if t==0:
        b=struct.unpack_from('<H',d,p+0x14)[0]
        for k in range(lo,hi+1):s.map[k]=b+k-lo
      elif t==1:
        for k in range(lo,hi+1):
          g=struct.unpack_from('<H',d,p+0x14+2*(k-lo))[0]
          if g!=0xffff:s.map[k]=g
      else:
        cnt=struct.unpack_from('<H',d,p+0x14)[0]
        for i in range(cnt):k,g=struct.unpack_from('<HH',d,p+0x16+4*i);s.map[k]=g
    w=s.cwdh;s.wfirst=struct.unpack_from('<H',d,w+8)[0]
  def glyph(s,i):
    o=s.gbase+i*s.tsz;bits=int.from_bytes(s.d[o:o+s.tsz],'big');tot=s.tsz*8
    px=[]
    for k in range(s.cw*s.ch):px.append((bits>>(tot-(k+1)*s.bpp))&((1<<s.bpp)-1))
    return [px[r*s.cw:(r+1)*s.cw] for r in range(s.ch)]
  def setglyph(s,i,rows):
    v=0;k=0
    for r in rows:
      for p in r:v=(v<<s.bpp)|p;k+=1
    tot=s.tsz*8;v<<=tot-k*s.bpp
    o=s.gbase+i*s.tsz;s.d[o:o+s.tsz]=v.to_bytes(s.tsz,'big')
  def width(s,i):
    o=s.cwdh+0x10+3*(i-s.wfirst);return tuple(s.d[o:o+3])
  def setwidth(s,i,t):
    o=s.cwdh+0x10+3*(i-s.wfirst);s.d[o:o+3]=bytes(t)
