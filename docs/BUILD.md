# 빌드 방법

번역 대본·원문은 저장소에 없으므로, 아래는 자신이 가진 원본과 번역 파일로 다시 빌드하는 절차입니다.

## 준비물
- 원본 `Eyeshield 21 - Max Devil Power! (Japan).nds` (MD5 `8f542d7696de824dfe5b75fcc898c84b`)
- Python 3.12+ : `pip install ndspy pillow` (에뮬레이터 확인용 `py-desmume` 선택)
- 글꼴 `NanumSquareNeo-*.ttf`, `Galmuri*.bdf`

## 폴더 구성
```
<작업 폴더>/                  원본 .nds, NanumSquareNeo-*.ttf
  <이 저장소>/
    tools/
    fonts/                    Galmuri*.bdf
    ext/                      추출물 (arm9, 오버레이, NitroFS 파일)
    trans/src/bNN.json        원문 목록 [{id, ja, note?}]
    trans/ko/bNN.json         번역 (원문과 같은 순서의 한국어 배열)
    survey/                   그림 글자 조사 결과 (survey.py 출력)
```

## 순서
1. 추출: `python tools/unpack.py`, `python tools/extract.py` → `ext/`, `trans/src`. 번역을 `trans/ko`에 작성하고 `python tools/check_trans.py`로 검사
2. 그림 글자 조사: `python tools/survey.py`, `tools/survey_bg.py` → `survey/`. 좌표와 문구는 `gfxspec.py`·`gfxov.py`·`bgspec.py`·`rawbg.py`·`mestext.py`·`s8text.py`·`gamebg.py`에 있음
3. 빌드: `python -X utf8 tools/build.py` → `Eyeshield 21 - Max Devil Power! (Korean).nds`
4. 차분: `xdelta3 -e -0 -S none -s 원본.nds 한글.nds 패치.xdelta` (압축 옵션 없이)
