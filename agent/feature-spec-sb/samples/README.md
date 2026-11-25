# samples — HTML로 추출된 화면설계 파일

새 화면을 그릴 때 패턴으로 참고하는 완성 예시 폴더. 작성 규칙 자체는 `SKILL.md` · `rules/` · `guides/`, 이 폴더는 그 규칙이 실제로 적용된 결과물

## 폴더 용도

- 새 화면 작성 시 마크업 · 번호 부여 · Description 작성 수준의 기준선
- PC/모바일 양식 차이 · 긴 화면 · 모달 서브 캔버스 처리의 실물 확인
- 작성 규칙 미포함 · 규칙 확인은 `SKILL.md` · `rules/` · `guides/`

## 들어 있는 것

| <div align="center"><sub>폴더</sub></div> | <sub>형태</sub> | <sub>쓰는 법</sub> |
|:---|:---:|:---:|
| <sub>`admin/`</sub> | <sub>**화면 본문만** (`*.src.html`) · 시트 골격 · 템플릿 CSS 미포함</sub> | <sub>`build_admin_sb.py`가 템플릿과 결합해 완성 SB 생성 · 새 어드민 화면은 이 마크업을 본떠 작성</sub> |
| <sub>`b2c/`</sub> | <sub>**완성된 화면설계서** (단독 HTML) · 브라우저에서 바로 열람 가능</sub> | <sub>결과물 확인용 · 양식 · 번호 부여 · Description 작성 수준의 기준선</sub> |

### admin/ — 어드민 화면 본문 12장

- KT AX 화면만 수록 · 원본 AX-Pilot의 타 고객 샘플 미포함
- 새 어드민 화면 패턴 = `KTAX-AD-MN01-0000.src.html` (영역마다 `.adm-num` 배지 1:1)

| <div align="center"><sub>파일</sub></div> | <sub>내용</sub> |
|:---|:---:|
| <sub>`KTAX-AD-MN01-0000` ~ `KTAX-AD-MN02-2000` (9장)</sub> | <sub>메인 관리 화면(배너 목록 · 등록 · 수정 / 메인 콘텐츠 3종 / 메인 팝업 목록 · 등록 · 수정) · `build_admin_sb.py` 레지스트리 등록 화면 · 공통 어드민 템플릿(`--template common`) 기준</sub> |
| <sub>`ADM-MAIN-001` ~ `ADM-MAIN-003` (3장)</sub> | <sub>2026.07.22 IA 재구성 전 구 채번 체계 화면 · 레지스트리 미등록</sub> |

### b2c/ — 범용 B2C 예시

회원가입 4단계(약관 동의 → 본인 인증 → 정보 입력 → 완료)를 모바일 · PC 양쪽으로 추출한 예시. 같은 `A-01_screens.json` 하나로 두 벌을 만들어 내용 동일 · 양식만 차이, PC/모바일 차이 비교용 쌍

| <div align="center"><sub>경로</sub></div> | <sub>내용</sub> |
|:---|:---:|
| <sub>`b2c/A-01_screens.json`</sub> | <sub>입력 원본 · 아래 결과를 언제든 재생성 가능</sub> |
| <sub>`b2c/mobile/`</sub> | <sub>모바일 4장 (캔버스 390px)</sub> |
| <sub>`b2c/pc/`</sub> | <sub>PC 4장 (캔버스 1440px)</sub> |
| <sub>`b2c/long-page/`</sub> | <sub>공지 80행짜리 긴 화면 1장(`C-01-001`) · **캔버스 세로 상한 미설정** 확인용</sub> |

- `A-01-003`(정보 입력)에 이탈 확인 모달 포함 · 모달을 별도 파일로 빼지 않고 메인 캔버스 우측 서브 캔버스로 붙이는 방식(`SKILL.md` §4.3)의 실물 예시

## 쓰는 법

### 재생성

폴더(`agent/feature-spec-sb/`) 기준 명령

```bash
python scripts/generate_sb.py --variant mobile --input samples/b2c/A-01_screens.json --output <출력폴더>
python scripts/generate_sb.py --variant pc     --input samples/b2c/A-01_screens.json --output <출력폴더>
python scripts/build_admin_sb.py 배너목록 --template common
```

- `build_admin_sb.py` = 레지스트리 키로 호출 · 키 9종 `배너목록` · `배너등록` · `배너수정` · `메인도입사례` · `메인인사이트` · `신뢰지표` · `메인팝업목록` · `메인팝업등록` · `메인팝업수정`
- 어드민 출력 위치 = `~/Downloads/SB_어드민/{화면ID}.html` (환경변수 `ADMIN_OUT`으로 변경)
- `--template` 생략 시 스크립트 기본값에 해당하는 템플릿 파일이 없어 중단 · `common` · `chatbot` · `krds` 중 명시

### 검증 상태

- `b2c/` 예시 = 화면당 24개 항목(시트 골격 · 메타 헤더 값 · 캔버스 치수 · 로고 무결성 · 배지와 Description 번호 1:1 · HTML-to-Figma 규칙) 검사 전 항목 통과 상태
