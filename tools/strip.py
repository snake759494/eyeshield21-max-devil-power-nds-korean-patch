import sys
from PIL import Image
from pathlib import Path
W=Path(__file__).resolve().parents[1]/'shots'
ims=[Image.open(W/(n+'.png')) for n in sys.argv[2:]]
o=Image.new('RGB',(sum(i.width for i in ims),ims[0].height));x=0
for i in ims:o.paste(i,(x,0));x+=i.width
o.save(W/(sys.argv[1]+'.png'))
