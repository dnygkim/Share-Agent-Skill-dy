# guides — 작성 규칙 로컬 정본

에이전트가 PRD와 SB를 무슨 내용으로 채울지 정하는 작성 규칙 4종. 원래 ETRIBE 사내 서버에만 있어 토큰이 필요하던 규칙을 토큰 없이도 쓰도록 이 리포에 둔 정본

> **Owner** 황다혜 프로 · **Resource** https://github.com/starryetribe-droid/AX-Pilot/tree/main

## 폴더 용도

- PRD · SB 작성 규칙의 로컬 정본 · 토큰이 없을 때 `scripts/fetch_guide.py`의 읽기 대상
- 역할 분담 = 절차는 `SKILL.md` · 채울 내용은 이 폴더
- 토큰 보유자는 서버 최신본 계속 수신 · 토큰 없는 사용자도 같은 단계로 사용

## 들어 있는 것

| <div align="center"><sub>파일</sub></div> | <sub>내용</sub> | <sub>쓰는 단계</sub> |
|:---|:---:|:---:|
| <sub>`features-list.md`</sub> | <sub>기능 ID ↔ 기능명 · 설명 · 우선순위 · 카테고리 디렉토리 (14분류 91개 · 사용자 기능 13분류 69개 + 어드민 확장 22개)</sub> | <sub>기능 ID 요청 시 맨 먼저 조회</sub> |
| <sub>`prd-structure.md`</sub> | <sub>PRD 9섹션 구조 · 섹션별 작성 규칙 · 화면 타입 17종 체크리스트</sub> | <sub>`SKILL.md` §3 Step 3 · 3.5</sub> |
| <sub>`flowchart-rules.md`</sub> | <sub>Mermaid 6도형 · 화살표 · 색상 · 작성 원칙 7가지</sub> | <sub>`SKILL.md` §3 Step 2.5 · 프로젝트 착수 플로우차트 단계</sub> |
| <sub>`sb-writing.md`</sub> | <sub>화면 분리 원칙 · Description 작성 규칙 · HTML-to-Figma 호환</sub> | <sub>`SKILL.md` §4 Step 2~3</sub> |

### 여기 없는 것 (이미 리포에 구현)

원본 가이드의 시트 레이아웃 · CSS 토큰 · 메타 헤더 구조 · KRDS 컴포넌트 카탈로그는 이미 리포에 구현돼 미수록 · 규칙 위치가 한 곳이라 수정도 한 곳

| <div align="center"><sub>원본에 있던 것</sub></div> | <sub>이 리포에서의 위치</sub> |
|:---|:---:|
| <sub>시트 레이아웃 · 메타 헤더 · 캔버스 치수 · 푸터 CSS</sub> | <sub>`templates/sb-style-block.html` (생성기가 자동 적용)</sub> |
| <sub>KRDS 컴포넌트 · 색상 · 타이포</sub> | <sub>`templates/Commom-sb-styleguide.md`</sub> |
| <sub>챗봇 컴포넌트 카탈로그</sub> | <sub>`scripts/chatbot_components.py` (규칙 문서 `rules/chatbot-sb.md`는 2026.08.03 삭제 · 메모리 아카이브)</sub> |
| <sub>생성 프로세스</sub> | <sub>`SKILL.md` §4</sub> |

## 쓰는 법

### 규칙을 가져오는 순서

`fetch_guide.py`의 자동 선택 순서

1. `~/.etribe/config.json`에 서버 URL · 토큰 보유 → 서버 최신본
2. 설정 부재 또는 서버 접속 실패 → 이 폴더의 파일

- 어느 쪽이든 사용자가 밟는 단계 동일
- 서버를 건너뛰려면 `--offline` · 로컬 사용 시 stderr에 `[INFO] 로컬 가이드 사용` 표시
- 서버에서 받은 규칙은 메모리에서만 사용 · 이 폴더 파일은 리포 포함 파일이라 그 제약과 무관

### 모드별로 읽는 파일

| <div align="center"><sub>`--mode`</sub></div> | <sub>읽는 파일</sub> |
|:---|:---:|
| <sub>`prd`</sub> | <sub>`prd-structure.md` · `flowchart-rules.md` · `features-list.md`</sub> |
| <sub>`sb` · `sb-mobile` · `sb-pc`</sub> | <sub>`sb-writing.md` · `features-list.md`</sub> |
| <sub>`feature-list` · `feature-asset`</sub> | <sub>`features-list.md`</sub> |
| <sub>`all`</sub> | <sub>4종 전부</sub> |

### 고칠 때

- 이 폴더 수정 = 토큰 없는 사용자에게 즉시 반영
- 서버 쪽 원본도 함께 바꿔야 토큰 사용자에게 반영 · 규칙 변경 시 양쪽 동기화
