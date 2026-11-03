# 아이실드21 MAX DEVIL POWER! (NDS) 비공식 한글패치

닌텐도 DS 일본판 **アイシールド21 MAX DEVIL POWER!** (`AE4J`) 비공식 한국어 패치입니다. 이 저장소에는 제작 도구와 기술 문서만 있고, 패치 파일은 [Releases](../../releases)에서 받을 수 있습니다. 게임 원본·일본어 원문·번역 대본은 포함하지 않습니다.

## 릴리즈 파일
| 파일 | 용도 |
| --- | --- |
| `Eyeshield21MDP_NDS_KO_v1.0.xdelta` | 본편 패치 — 일본판 `.nds` 롬용 |

## 적용 방법 (에뮬레이터)
1. 아래 해시와 일치하는 **원본 롬**(64MB)을 준비합니다.
   - PowerShell: `Get-FileHash -Algorithm MD5 -LiteralPath '.\Eyeshield 21 - Max Devil Power! (Japan).nds'`
2. xdeltaUI 등으로 원본에 xdelta를 적용합니다.
   - 명령줄: `xdelta3 -d -s "Eyeshield 21 - Max Devil Power! (Japan).nds" Eyeshield21MDP_NDS_KO_v1.0.xdelta "Eyeshield 21 - Max Devil Power! (Korean).nds"`
3. 만들어진 `.nds`를 DeSmuME·melonDS 등 DS 에뮬레이터에서 실행합니다.

> DS 실기·플래시 카트에서는 확인하지 않았습니다.

## 해시
| 항목 | 값 |
| --- | --- |
| 원본 크기 | 67,108,864 바이트 |
| 원본 MD5 | `8f542d7696de824dfe5b75fcc898c84b` |
| 원본 SHA-256 | `de41574fdbe7d8ecbbfbe03fc87befa673ca20f8537a09187036c1df2aefc248` |
| 결과 NDS 크기 / SHA-256 | 64,829,608 바이트 / `252540e9f9660fdb4d3068128e8153c7b9c744fe0517ba874816b97f8c6af21e` |

릴리즈 첨부 파일의 SHA-256은 [release_manifest.json](release_manifest.json)에 있습니다.

## 한글화 내용
- 학교 RPG 대사, 시합 실황 중계, 작전·포메이션, 아이템·기술 설명, 메뉴·시스템 메시지 등 문자열 약 8,150개
- 그림 글자: 타이틀 로고(「아이실드」)·원작 표기, 모드 선택·시합 모드·팀 선택·규칙 설정·세이브/로드·필드 메뉴, 장 제목 카드 9장, 미니게임 제목·룰 설명
- 시합 중 배너(킥오프!·터치다운!·인터셉트!·퍼스트 다운!·하프타임 등), 남은 야드 안내, 하단 화면 안내 배너(중심을 슬라이드!·중심을 터치!·화면을 문질러라!), 스코어·골라인·야드 표시, 결과 화면, '에디트' 태그
- 글꼴: 게임 폰트에 Galmuri11/9 한글 글리프 추가

## 그대로 둔 것
- 영어 로고(EYESHIELD 21 등)와 영어 표기 그림
- 하단 경기 화면 '야드' 옆에 다른 글자와 공유하는 타일 때문에 원본 획이 조금 남을 수 있음
- 모드 선택 화면 검은 띠의 흰 점 하나

## 검증 범위
DeSmuME에서 부팅·타이틀·시합 진입 화면과 그림 글자 미리보기를 확인했습니다. 전체 플레이 검증은 하지 않았습니다. 문제를 발견하면 Issues에 알려 주세요.

## 문서
- [CHANGELOG.md](CHANGELOG.md) — 변경 기록
- [docs/TECHNICAL.md](docs/TECHNICAL.md) — 파일 형식과 한글화 방법
- [docs/BUILD.md](docs/BUILD.md) — 직접 빌드하는 방법
- [docs/FONT_CREDITS.md](docs/FONT_CREDITS.md) — 글꼴
- [RIGHTS.md](RIGHTS.md) — 권리 및 외부 자료
