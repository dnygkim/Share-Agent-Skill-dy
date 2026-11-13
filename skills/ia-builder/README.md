# ia-builder — IA(사이트 구조 및 기능정의) 엑셀 생성 스킬

서비스 설명이나 기존 IA 양식을 넣으면 1~5단계 메뉴 트리를 제안 · 확정한 뒤 페이지 정의 · 개발구분 · 페이지 수 · 역할별 권한까지 채운 IA(정보구조도 · 기능정의서) 엑셀이 나오는 스킬

## 한눈에 보기

| <div align="center"><sub>항목</sub></div> | <sub>내용</sub> |
|:---|:---:|
| <sub>목적</sub> | <sub>서비스(웹/앱)의 메뉴 · 뎁스 구조(사이트맵 · 정보구조 IA)와 기능정의를 한 엑셀로 정리 · PRD · WBS보다 먼저 만드는 서비스의 뼈대</sub> |
| <sub>이럴 때 사용</sub> | <sub>새 서비스 메뉴 구조 설계 · 필요한 화면 목록 정리 · 사내 · 고객 양식대로 IA 작성 · 기존 IA의 빈 컬럼 디벨롭</sub> |
| <sub>넣는 것</sub> | <sub>프로젝트명 · 서비스 개요(1~3문장) · 대상 사용자 · 화면/플랫폼 구분 · (선택) 기획서 · PRD · 기존 IA 양식 엑셀 · 경쟁 서비스 레퍼런스</sub> |
| <sub>나오는 것</sub> | <sub>`프로젝트명_IA_YYYYMMDD.xlsx` — 표지 · 사용안내 · 개정이력 + 정보구조도 시트(Front/Admin · 플랫폼별)</sub> |
| <sub>부르는 법</sub> | <sub>`IA 만들어줘` · `사이트맵 만들어줘` · `메뉴 구조 잡아줘` · `이 양식대로 IA 만들어줘` 등 · 슬래시 명령 `/ia-builder`</sub> |
| <sub>제작</sub> | <sub>신지은 (GitHub [jieun994](https://github.com/jieun994)) · 이 리포 이관 2026.07.21 · 보강 김단영(헤더 양식 가변 · 순차 디벨롭 · 플랫폼형 실전 예시 · 기본형 결과 예시)</sub> |
| <sub>출처</sub> | <sub>[jieun994/zinis_claude_skills](https://github.com/jieun994/zinis_claude_skills) · 원본 경로 `skills/ia-builder/`</sub> |
| <sub>연계 하네스</sub> | <sub>[`agent/feature-spec-sb`](../../agent/feature-spec-sb/README.md) 프로젝트 착수 모드 Step 2에서 호출 · 뒤 단계 = [`agent/screen-spec-id`](../../agent/screen-spec-id/README.md)(IA 엑셀 → 화면명세서) · [`requirements-generator`](../requirements-generator/README.md)(IA 엑셀 → 요구사항 정의서)</sub> |

## 이렇게 요청

| <div align="center"><sub>상황</sub></div> | <sub>요청 예시</sub> | <sub>나오는 것</sub> |
|:---|:---:|:---:|
| <sub>새 서비스 기획</sub> | <sub>`프리랜서 매칭 플랫폼 IA 만들어줘`</sub> | <sub>대분류(1depth) 제안부터 시작하는 IA 엑셀</sub> |
| <sub>화면 목록이 막막할 때</sub> | <sub>`쇼핑몰 앱 만드는데 어떤 화면 필요한지 사이트맵 짜줘`</sub> | <sub>서비스 유형 관례 메뉴 기반 트리 초안</sub> |
| <sub>기획서가 있을 때</sub> | <sub>(PRD 붙여넣고) `이거 보고 메뉴 구조 잡아줘`</sub> | <sub>핵심 기능 영역 5~7개로 압축한 메뉴 트리</sub> |
| <sub>사내 · 기존 양식이 있을 때</sub> | <sub>(엑셀 첨부하고) `이 양식대로 IA 만들어줘`</sub> | <sub>컬럼 정의표 확인 후 같은 양식의 IA</sub> |
| <sub>관리자 화면 포함</sub> | <sub>`사용자/관리자 화면 나눠서 정보구조도 그려줘`</sub> | <sub>Front · Admin 시트 분리 + 역할별 권한</sub> |
| <sub>기존 IA 디벨롭</sub> | <sub>(파일 첨부하고) `구조는 유지하고 Description만 채워줘`</sub> | <sub>골격 유지 · 지정 컬럼만 채운 새 버전</sub> |

## 진행 단계

진행 원칙 2가지

1. **헤더 양식은 프로젝트 기준** — Depth 구조 원칙은 어디서나 같지만 헤더행(컬럼)은 프로젝트 · 플랫폼 · 서비스마다 상이 → 기존 IA · 사내 양식 첨부 시 헤더행을 읽고 각 컬럼의 정의 · 맥락 · 의도를 표로 확인받은 뒤 그 양식 그대로 생성, 양식이 없을 때만 기본형 컬럼 제안
2. **골격 먼저, 컬럼별 순차 디벨롭** — 1차로 구조 컬럼(번호 · Depth · 유형)만 채운 골격 파일(v0.1)로 구조 확정 → Description → 권한 → Page 수 같은 내용 컬럼을 그룹 단위로 순차 입력 · 단계마다 검토 → 구조 검토와 내용 검토 분리로 리뷰 부담 감소

```
① 시작 인터뷰 → ② 헤더 양식 확정 → ③ 메뉴 트리 설계 → ④ 트리 미리보기(GATE) → ⑤ 골격 v0.1(GATE) → ⑥ 컬럼별 디벨롭 → ⑦ 결과 안내
```

| <div align="center"><sub>단계</sub></div> | <sub>하는 일</sub> | <sub>사용자 할 일</sub> | <sub>결과물</sub> |
|:---|:---:|:---:|:---:|
| <sub>① 시작 인터뷰</sub> | <sub>아래 5문항을 하나씩 질문 · 첨부한 기획서 · PRD 선독 · 모르면 제안 · 기본값 제시</sub> | <sub>답변 · (선택) 기획서 첨부</sub> | <sub>프로젝트 정보</sub> |
| <sub>② 헤더 양식 확정</sub> | <sub>기존 양식이 있으면 헤더행 · 데이터 몇 행을 읽고 컬럼 정의표 제시 / 없으면 컬럼 선택 질문(복수 선택)</sub> | <sub>**컬럼 정의 · 뺄/더할 컬럼 · 컬럼별 「채움 단계」(골격 · 디벨롭) 확인**</sub> | <sub>확정 컬럼 구성</sub> |
| <sub>③ 메뉴 트리 설계</sub> | <sub>대분류(1depth) 초안 표 → 하위 2~5depth 제안(Head · Footer 등 공통 영역 포함) → 페이지 유형 · 개발구분 · page 수 등 컬럼 값 제안</sub> | <sub>대분류 · 하위 메뉴 수정 · 확정</sub> | <sub>메뉴 트리</sub> |
| <sub>**④ 트리 미리보기 (GATE)**</sub> | <sub>대화창에 들여쓰기 트리 표시 + 수정 요청 예시 안내</sub> | <sub>**트리 확정** · 수정 예 `Depth 하나 더 추가해줘` · `관리자 화면 빼줘` · `공지사항은 2차로 빼줘`</sub> | <sub>확정 트리</sub> |
| <sub>**⑤ 골격 생성 (GATE)**</sub> | <sub>구조 컬럼(No/Code · Depth · 유형)만 채운 엑셀 생성 · 내용 컬럼은 빈칸</sub> | <sub>**구조 검토 · 확정**</sub> | <sub>골격 엑셀 v0.1</sub> |
| <sub>⑥ 컬럼별 디벨롭</sub> | <sub>Description(화면 정의) → 권한 → Page 수 · 개발구분 순(스키마 확정 때 정한 「채움 단계」 기준) 그룹 단위 입력 · 그룹마다 파일 갱신 · 요약</sub> | <sub>그룹별 검토</sub> | <sub>디벨롭 엑셀(v0.2 …)</sub> |
| <sub>⑦ 결과 안내</sub> | <sub>생성 경로 · 시트 구성 안내 · 필요 시 「이 IA로 PRD를 만들까요?」 같은 다음 단계 제안</sub> | <sub>엑셀 확인</sub> | <sub>최종 IA 엑셀</sub> |

### 시작 인터뷰

| <div align="center"><sub>질문</sub></div> | <sub>답 예시</sub> | <sub>기본값 · 비고</sub> |
|:---|:---:|:---:|
| <sub>1 프로젝트명</sub> | <sub>`테스트커머스`</sub> | <sub>제목 반영</sub> |
| <sub>2 서비스 개요</sub> | <sub>무엇을 하는 서비스인지 1~3문장 · 기획서 · PRD 첨부</sub> | <sub>메뉴 분해 기준 · 가장 중요</sub> |
| <sub>3 대상 사용자 · 화면/플랫폼 구분</sub> | <sub>`일반 사용자 + 관리자` · 역할 목록</sub> | <sub>관리자 화면이 있으면 Front/Admin 시트 분리 · 플랫폼이 여럿이면(통합관리자/일반사용자 등) 플랫폼별 시트 · 역할별 권한이 다르면 권한 칸(CRUD 4칸 또는 역할당 O 1칸)</sub> |
| <sub>4 헤더 양식</sub> | <sub>기존 IA 파일 첨부 또는 `없어요`</sub> | <sub>있으면 컬럼 정의표 확인 · 없으면 컬럼 선택 질문</sub> |
| <sub>5 작성자 · 버전(선택)</sub> | <sub>`홍길동` · `v0.1`</sub> | <sub>작성일 = 오늘 자동 · 표지 · 개정이력 반영</sub> |

- 입력이 한 줄뿐(`쇼핑몰 만들어줘`)이면 생성 전 서비스 성격 · 대상 사용자 · 핵심 기능 1~2개 추가 질문 · 임의 생성 금지

### 컬럼 선택 (양식이 없을 때 · 복수 선택)

| <div align="center"><sub>선택지</sub></div> | <sub>내용</sub> |
|:---|:---:|
| <sub>페이지 정의/요구사항 (추천)</sub> | <sub>각 화면의 유형(디자인 페이지 · 게시판 · 폼 등) · 요구사항</sub> |
| <sub>개발구분 (추천)</sub> | <sub>디자인 · 퍼블리싱 · 개발 담당 ● 표시 · 페이지 유형 기준 자동 제안</sub> |
| <sub>Page(페이지 수) + 총계</sub> | <sub>화면별 페이지 수 · 맨 아래 총계 자동 합산</sub> |
| <sub>세부 사항</sub> | <sub>화면 안 세부 항목 · 분기(입력 필드 · 상태 구분 등)</sub> |
| <sub>Tab/서브 플로우</sub> | <sub>한 화면 안 탭 · 서브 흐름</sub> |
| <sub>권한(역할별 CRUD)</sub> | <sub>관리자 화면용 역할별 C/R/U/D 가능 여부 · Admin 시트 적용</sub> |

- Code(첫 열) · Depth · 비고 = 항상 포함

### 파일 관리 방식 (시작할 때 확인)

| <div align="center"><sub>방식</sub></div> | <sub>설명</sub> | <sub>언제</sub> |
|:---|:---:|:---:|
| <sub>버전업 새 파일</sub> | <sub>단계마다 v0.1 → v0.2 … 새 파일 생성</sub> | <sub>기본값</sub> |
| <sub>정본 제자리 수정</sub> | <sub>정본 파일 직접 수정 · **수정 전 백업 필수**</sub> | <sub>프로젝트 규칙이 그럴 때</sub> |

- 버전 번호 임의 상향 금지 · 이미 있는 IA를 디벨롭할 때도 Depth 구조(골격) 유지 · 지정 컬럼만 입력 · 수정

## 산출물

엑셀 시트 순서: 표지 → 사용안내 → 개정이력 → 정보구조도(시트 여러 개 가능)

| <div align="center"><sub>시트</sub></div> | <sub>내용</sub> |
|:---|:---:|
| <sub>표지</sub> | <sub>프로젝트명 · 작성자 · 작성일 · 버전</sub> |
| <sub>사용안내</sub> | <sub>파일 보는 법(컬럼 의미 · 행 색 · 권한 표시)</sub> |
| <sub>개정이력</sub> | <sub>버전 · 날짜 · 작성자 · 변경 내용</sub> |
| <sub>정보구조도</sub> | <sub>실제 IA 표 · Front/Admin 또는 플랫폼별 시트 분리</sub> |

- 파일명 `프로젝트명_IA_YYYYMMDD.xlsx` 형식
- 기존 양식을 따를 때는 부속 시트(표지 · 변경이력) 구성도 그 양식 기준

### 헤더 양식 — 프리셋 3종 + 자유 양식

**기본형** (프리셋 A · 양식이 없을 때의 기본값)

| <div align="center"><sub>항상 포함</sub></div> | <sub>선택 포함</sub> |
|:---|:---:|
| <sub>Code(첫 열) · Depth1~5 · 비고</sub> | <sub>페이지 정의/요구사항 · 개발구분(디자인/퍼블/개발 ●) · Page 수 + 총계 · 세부 사항 · Tab/서브 플로우 · 권한(역할별 CRUD)</sub> |

**플랫폼형** (프리셋 B · 비즈니스 플랫폼 · SaaS — 실전 예시: references의 신승 IA 파일)

| <div align="center"><sub>컬럼</sub></div> | <sub>내용</sub> |
|:---|:---:|
| <sub>No</sub> | <sub>Depth 경로 번호 (0, 0.1, 0.1.1 …)</sub> |
| <sub>Page/UI Type</sub> | <sub>행의 성격 (Page / Conceptual Menu / Popup / Tab …)</sub> |
| <sub>Depth 0~4</sub> | <sub>메뉴 계층 (0부터 시작)</sub> |
| <sub>역할 컬럼(들)</sub> | <sub>역할별 접근 권한 — 역할당 O 1칸 (시트마다 상이)</sub> |
| <sub>Description</sub> | <sub>화면 정의 · 요구사항 (「- 」 bullet, 정책 주석 포함 가능)</sub> |

**관리자 권한형** (프리셋 C) — 기본형 + 역할 목록 → 역할마다 C/R/U/D 4칸(Admin 화면의 등록 · 조회 · 수정 · 삭제 구분)

**자유 양식** — 프리셋이 아니어도 첨부 엑셀의 헤더(컬럼 순서 · 이름 · Depth 시작 번호 · 권한 표시 방식) 그대로 재현

### 표 규칙

- **Depth는 서비스에 맞게 유연** — 얕으면 1~2단계, 복잡하면 4~5단계, 억지로 맞추기 금지 · Depth 0 시작 지원
- **권한 표시 2종** — 역할별 CRUD 4칸(C = 등록 · R = 조회 · U = 수정 · D = 삭제) 또는 역할당 O 1칸, 양식에 맞게 선택
- **나중에 할 기능(2차)** = 회색 행
- **Page 수 총계** = 자동 합산(SUM 수식) · 정보구조도 시트 눈금선 비표시
- **내용 품질** — 「게시판」 같은 한 단어가 아니라 「리스트 게시판 — 공지 목록 · 상세, 상단 고정」처럼 기획자가 바로 쓸 수준
- **스타일** — 컬럼 헤더 검정 + 흰 글씨 · Depth1 진회색 · Depth2 연노랑 · 맑은 고딕(wbs-generator 샘플과 같은 디자인 언어)

결과 미리보기: [samples/결과_예시.xlsx](samples/결과_예시.xlsx) (기본형) · [references의 신승 IA 파일](references) (플랫폼형)

### 다른 기획 산출물과의 순서

| <div align="center"><sub>스킬 · 하네스</sub></div> | <sub>만드는 것</sub> | <sub>순서</sub> |
|:---|:---:|:---:|
| <sub>**ia-builder** (이 스킬)</sub> | <sub>서비스 **구조**(메뉴 · 화면)</sub> | <sub>① 먼저</sub> |
| <sub>[`agent/feature-spec-sb`](../../agent/feature-spec-sb/README.md)</sub> | <sub>기능 **명세**(PRD) · SB</sub> | <sub>② 다음</sub> |
| <sub>[`agent/screen-spec-id`](../../agent/screen-spec-id/README.md)</sub> | <sub>**화면명세서**(화면ID 채번)</sub> | <sub>②' IA 확정 후</sub> |
| <sub>[`wbs-generator`](../wbs-generator/README.md)</sub> | <sub>작업 **일정**(WBS)</sub> | <sub>③ 마지막</sub> |

- IA로 뼈대 → PRD · 화면명세로 정의 → WBS로 일정 수립 순서 (PRD = 기능 명세 · WBS = 일정 · IA = 구조)

## 설치 · 단독 사용

```bash
cp -r skills/ia-builder ~/.claude/skills/ia-builder
```

- 리포 루트 기준 명령 · 스킬 일괄 설치는 원본 리포 `bash install-global.sh` · 공유 리포 `share/update.sh`
- 의존성: Python 3 + `pip install openpyxl`(엑셀 생성) · Windows PowerShell은 `$env:PYTHONUTF8=1` · `python`이 없으면 `py -3`
- 엑셀 생성이 끝내 안 되는 환경 = 들여쓰기 트리 · 마크다운 표로 대체 제공(엑셀에 붙여넣기 가능)
- 입력 JSON(`layout` · `labels` · `depth_min` · `roles_style` 등)은 Claude가 작성 · 실행 · 스키마는 SKILL.md 「입력 JSON 구조」
- 하네스 안에서: [`agent/feature-spec-sb`](../../agent/feature-spec-sb/README.md) 프로젝트 착수 모드(`rules/project-kickoff.md` Step 2)
  - 하네스가 서비스명 · 개요 · 대상 사용자 · 디바이스를 넘겨 인터뷰 1~3번 생략 → 「헤더 양식 확인」부터 진행
  - 골격(v0.1) 먼저 → 컬럼별 디벨롭 순서는 하네스 안에서도 동일
  - 저장 `output/{slug}/01. IA/{서비스명}_IA_v0.1_{YYYYMMDD}.xlsx` · IA 확정 전 다음 단계(플로우차트) 진행 보류
  - 사전 준비: 리포 루트에서 `./sync-skills.ps1`(또는 `bash ./sync-skills.sh`) 1회 → `agent/feature-spec-sb/.claude/skills/`로 복사

## 폴더 구성

```
skills/ia-builder/
├── SKILL.md                    Claude 작동용 정본 (사람 열람 불필요)
├── README.md                   사람용 안내 · 사용법 (이 문서)
├── references/
│   ├── page-types.md           페이지 유형 · 개발구분(●) 추천 기준 · 권한 · 공통 영역 · 2차 표시 규칙
│   ├── header-presets.md       헤더 양식 프리셋(기본형 · 플랫폼형 · 관리자 권한형) · 컬럼 정의표 양식 · 채움 단계
│   └── 신승-비즈니스AI플래너_IA(메뉴구조도)_v0.01_260721.xlsx   플랫폼형 양식 실전 예시 (사람 · Claude 참조)
├── samples/
│   ├── 결과_예시.xlsx           기본형 결과 미리보기
│   └── sample_input.json       입력 JSON 예시
├── scripts/build_ia.py         JSON → IA 엑셀 생성 (내부용 · 수정 금지)
└── .claude-plugin/plugin.json  플러그인 정보 (v0.1.0 · 제작자 신지은)
```

## 주의

- 긴 PRD 첨부 = 핵심 기능 영역 5~7개로 압축 후 메뉴 재구성
- 역할이 섞인 서비스(소비자 · 관리자 등) = Front/Admin 시트 분리 여부 먼저 확인
- 경쟁사 URL은 실시간 접근이 어려워 「○○ 같은 쇼핑몰」식 레퍼런스로 받아 관례 구조 적용
- 같은 메뉴명이 여러 곳에 반복되면 비고에 구분 메모 제안
- 기존 양식 파싱 시 헤더명만으로 단정하지 않고 실제 데이터 행으로 컬럼 용도 판단

## 릴리즈노트

| <div align="center"><sub>요약내용</sub><img width="1" height="1"></div> | <sub>업데이트 일자</sub><img width="1" height="1"> | <sub>소유자</sub><img width="45" height="1"> |
|:---|:---:|:---:|
| <sub>README 전면 개편 — 목적 · 넣는 것 · 산출물 형태 · 요청 예시 · 진행 단계 순으로 재구성, 릴리즈노트 맨 아래로 이동</sub> | <sub>2026.11.13</sub> | <sub>김단영</sub> |
| <sub>기본형 결과 예시(samples/결과_예시.xlsx) 업데이트</sub> | <sub>2026.08.04</sub> | <sub>김단영</sub> |
| <sub>플랫폼형 실전 예시(신승 IA v0.01) 레퍼런스 등록·README 전면 개편</sub> | <sub>2026.07.21</sub> | <sub>김단영</sub> |
| <sub>헤더 양식 가변 지원(layout·labels·depth_min·roles_style) + 골격→컬럼 순차 디벨롭 워크플로</sub> | <sub>2026.07.21</sub> | <sub>김단영</sub> |
| <sub>최초 등록 — 신지은 스킬 이관 (jieun994/zinis_claude_skills)</sub> | <sub>2026.07.21</sub> | <sub>신지은</sub> |
