"""그래픽 글자 교체 사양"""
SP=[]
def add(f,cells,rect,text,h,pal=None,**k):
  for c in (cells if isinstance(cells,(list,tuple)) else [cells]):
    d=dict(f=f,cells=[c],text=text,h=h,**k)
    if rect:d['rect']=rect
    if pal:d['pal']=pal
    SP.append(d)
M='obj/main_menu/m_menu_l'
add(M,1,[44,12,152,34],'시나리오 모드',14,shadow=1)
add(M,3,[44,12,152,34],'시합 모드',14,shadow=1)
add(M,[6,24],[44,12,152,34],'덤 모드',14,shadow=1)
add(M,18,[0,0,120,20],'모드 선택',13,align='l')
E='rpg/2d/entry';EP='rpg/2d/entry_l_obj'
for c,t in [(0,'파일1:'),(1,'파일1:'),(2,'파일2:'),(3,'파일2:'),(4,'파일3:'),(5,'파일3:')]:add(E,c,[0,0,48,16],t,10,EP,align='l')
add(E,[6,7],[0,0,18,16],'제',10,EP);add(E,[6,7],[28,0,46,16],'장',10,EP)
add(E,[6,7],[78,0,112,16],'일째',9,EP,align='r',noline=1)
add(E,[8,9],[0,0,104,16],'데이터 없음',10,EP,align='l')
add(E,14,[0,0,56,26],'세이브',14,EP,align='l')
add(E,15,[0,0,56,26],'로드',14,EP,align='l')
add(E,73,[0,0,112,26],'파일 삭제',14,EP,align='l')
add(E,74,[0,0,128,26],'파일 선택',14,EP,align='l')
add(E,89,[0,0,80,26],'엔트리',14,EP,align='l')
add(E,75,[0,0,104,16],'처음부터 시작',10,EP,align='l')
add(E,[16,66,85],[30,8,64,25],'뒤로',12,EP,bgat=[65,16],snap=1)
add(E,[37,38],[6,6,58,26],'아니오',11,EP,shadow=1)
add(E,[39,40],[6,6,58,26],'예',11,EP,shadow=1)
add(E,[76,77],[10,10,152,37],'처음부터',16,EP,shadow=1)
add(E,[78,79],[10,10,152,37],'이어서',16,EP,shadow=1)
def hdr(f,c,t,w,pal=None):add(f,c,[0,0,w,26],t,14,pal,align='l')
def back(f,cs,w,pal=None):add(f,cs,[30,8,w-8,25],'뒤로',12,pal,bgat=[w-7,16],snap=1)
# 시합 모드 선택
S='obj/shiai_select/s_select_l'
add(S,[0,1],[6,54,122,86],'COM 대전',12)
add(S,[3,4,18],[6,54,98,86],'친구 대전',12)
back(S,[9,12],72);hdr(S,10,'모드 선택',104);hdr(S,19,'시합 모드',80)
# 규칙 설정
R='obj/teamselect/rule_l'
hdr(R,0,'설정',64)
#for cs,t in [([1,35],'COM 강도'),([10,39],'쿼터 수'),([15,42],'쿼터당 시간')]:add(R,cs,[0,0,104,16],t,10,align='l')
for cs,t in [([2,3,36],'보통'),([4,5,37],'강함'),([6,7,38],'최강')]:add(R,cs,[8,6,72,26],t,11)
for cs,t in [([16,17,43],'5분'),([18,19,44],'10분'),([20,21,45],'15분')]:add(R,cs,[8,6,72,26],t,11)
add(R,[22,23],[8,10,64,26],'결정',12,bgat=[65,16],snap=1,fg=[248,248,248],ol=[0,24,64],shadow=0);back(R,[27,28],80)
add(R,34,[0,0,144,16],'호스트의 결정을 기다리는 중',10,align='l')
# 팀 선택
T='obj/teamselect/t_sele_l'
hdr(T,0,'팀 선택',112);add(T,[23,27],[30,8,64,25],'뒤로',12,bgat=[65,16],snap=1)
add(T,[24,28],[28,5,90,28],'취소',11)
add(T,[25,26,41],[8,10,64,26],'결정',12,bgat=[65,16],snap=1,fg=[248,248,248],ol=[0,24,64],shadow=0)
add(T,29,[10,6,134,26],'팀을 고르자!',11)
hdr(T,33,'에디트 팀',128)
add(T,34,[10,6,182,26],'에디트할 팀을 고르자!',11)
add(T,42,[10,8,230,40],'대전 상대를 기다리는 중',11,font='galmuri')
add(T,[44,46],[6,6,58,26],'예',11,shadow=1)
add(T,[45,47],[6,6,58,26],'아니오',11,shadow=1)
# 필드 메뉴
MN='rpg/2d/menu';MG='rpg/2d/menu_l_obj'
add(MN,0,[6,4,62,22],'메뉴',12,g=MG)
for cs,t in [([1,2],'아이템'),([13,14],'시스템'),([15,16,46],'스테이터스')]:add(MN,cs,[12,62,82,78],t,11,g=MG)
back(MN,[3,4],72,);SP[-1]['g']=MG;SP[-2]['g']=MG
add(MN,30,[0,0,64,24],'이동',14,g=MG,align='l')
add(MN,40,[0,0,80,24],'메뉴',14,g=MG,align='l')
# 타이틀
TI='obj/title/sita_obj'
add(TI,[8,9],[26,1,112,21],'터치해서 시작',11,bg=[0,0,0],noline=1)
add(TI,10,[26,3,108,23],'터치해서 시작',11,bg=[0,0,0],noline=1)
add(TI,11,[2,0,102,13],'터치해서 시작',10)
# 장 제목 카드
SD='rpg/2d/sub_dwn_obj'
for c,t,w,h in [(0,'광속의 다리를\n가진 남자',256,160),(1,'이기기 위한\n싸움',224,128),(2,'캐치의 달인',224,160),(3,'싸우는\n이유',192,160),
  (4,'BAD & BAD',224,128),(5,'새로운 동료',224,160),(6,'파워풀',224,128),(7,'최강의 왕국',224,160),(8,'미일 결전',192,160)]:
  add(SD,c,[0,0,w,h],t,30 if chr(10) in t else 38,thick=2,clear=1,ol=[0,0,0],fg=[248,248,248],textrect=[4,h-90,w-36,h-8])
# 시스템
SY='rpg/2d/system_obj2';SG='rpg/2d/system_obj'
for cs,t in [([0,1],'느림'),([2,3],'빠름'),([4,5],'보통')]:add(SY,cs,[8,20,64,38],t,11,SG,g=SG)
add(SY,[6,7,40],[32,5,78,32],'세이브',11,SG,g=SG);add(SY,[8,9,41],[32,5,78,32],'로드',11,SG,g=SG)
for cs in ([10],[27]):back(SY,cs,72,SG);SP[-1]['g']=SG
add(SY,11,[0,0,96,16],'메시지 속도:',10,SG,g=SG,align='l')
add(SY,11,[0,70,40,86],'데이터:',10,SG,g=SG,align='l')
add(SY,[12,13],[3,10,109,31],'타이틀로 돌아가기',11,SG,g=SG)
add(SY,[20,21],[6,6,58,26],'아니오',11,SG,g=SG,shadow=1);add(SY,[22,23],[6,6,58,26],'예',11,SG,g=SG,shadow=1)
hdr(SY,26,'시스템',72,SG);SP[-1]['g']=SG
# 아이템
IT='rpg/2d/item';IG='rpg/2d/item_l_obj'
back(IT,14,72,IG);SP[-1]['g']=IG
add(IT,[24,25],[8,10,64,26],'사용',12,IG,g=IG,bgat=[65,16],snap=1,fg=[248,248,248],ol=[0,24,64],shadow=0)
hdr(IT,26,'아이템',72,IG);SP[-1]['g']=IG
add(IT,35,[0,0,32,12],'페이지',10,IG,g=IG,align='l')
# 세이브/로드
SL='rpg/2d/save_load';SLG='rpg/2d/save_load_obj'
for c,t in [(0,'파일1:'),(1,'파일1:'),(2,'파일2:'),(3,'파일2:'),(4,'파일3:'),(5,'파일3:')]:add(SL,c,[0,0,48,16],t,10,SLG,g=SLG,align='l')
add(SL,[6,7],[0,0,18,16],'제',10,SLG,g=SLG);add(SL,[6,7],[28,0,46,16],'장',10,SLG,g=SLG);add(SL,[6,7],[78,0,112,16],'일째',9,SLG,g=SLG,align='r',noline=1)
add(SL,[8,9],[0,0,104,16],'데이터 없음',10,SLG,g=SLG,align='l')
add(SL,14,[0,0,56,26],'세이브',14,SLG,g=SLG,align='l');add(SL,15,[0,0,56,26],'로드',14,SLG,g=SLG,align='l')
add(SL,73,[0,0,112,26],'파일 삭제',14,SLG,g=SLG,align='l');add(SL,74,[0,0,128,26],'파일 선택',14,SLG,g=SLG,align='l')
add(SL,75,[0,0,104,16],'처음부터 시작',10,SLG,g=SLG,align='l')
for cs in ([16],[66]):back(SL,cs,72,SLG);SP[-1]['g']=SLG
add(SL,[37,38],[6,6,58,26],'아니오',11,SLG,g=SLG,shadow=1);add(SL,[39,40],[6,6,58,26],'예',11,SLG,g=SLG,shadow=1)
# 스테이터스
PA='rpg/2d/parameta_l1';PG='rpg/2d/parameta_l1_obj'
for cs in ([8],):back(PA,cs,72,PG);SP[-1]['g']=PG
hdr(PA,14,'스테이터스',112,PG);SP[-1]['g']=PG
for _s in SP:
  if _s['f']=='rpg/2d/menu' and _s['text'] in ('아이템','시스템','스테이터스'):_s.update(fg=[248,248,248],noline=1,rect=[12,64,82,78],bgmajor=1,snap=0)
  if _s['f']=='rpg/2d/system_obj2' and _s['text'] in ('세이브','로드'):_s.update(rect=[36,9,76,28],bgmajor=1,snap=0,fg=[0,24,80],shadow=1,h=12)
  if _s['f']=='rpg/2d/system_obj2' and _s['text']=='타이틀로 돌아가기':_s.update(rect=[6,12,106,29],bgat=[104,14],font='Galmuri11-Bold',snap=0,fg=[248,248,248],ol=[0,24,64],shadow=0,h=12)
