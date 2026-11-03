"""ROM 전체를 ext/ 아래로 풀기 (arm9, 오버레이 압축 해제 포함)"""
import ndspy.rom,ndspy.code
from pathlib import Path
W=Path(__file__).resolve().parents[1];ROOT=W.parent
r=ndspy.rom.NintendoDSRom.fromFile(str(ROOT/'Eyeshield 21 - Max Devil Power! (Japan).nds'))
E=W/'ext';E.mkdir(exist_ok=True)
a9=r.loadArm9();(E/'arm9.bin').write_bytes(a9.save(compress=False))
for i,o in r.loadArm9Overlays().items():
  (E/f'ov{i:03d}.bin').write_bytes(o.data)
for i,f in enumerate(r.files):
  n=r.filenames.filenameOf(i)
  if n is None:continue
  p=E/'fs'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(f)
