# guides — 작성 규칙 로컬 정본

> **Owner** 황다혜 프로 · **Resource** https://github.com/starryetribe-droid/AX-Pilot/tree/main

에이전트가 PRD와 SB를 **무슨 내용으로** 채울지 정하는 규칙이다.
원래는 ETRIBE 사내 서버에만 있어 토큰이 있어야 동작했는데, **토큰 없이도 쓸 수 있도록** 이 리포에 정본을 두었다.

## 어떻게 동작하나

`fetch_guide.py`가 이 순서로 규칙을 가져온다.

1. `~/.etribe/config.json`에 **서버 URL·토큰이 있으면** → 서버 최신본을 받아 쓴다.
2. 없거나 서버에 못 닿으면 → **이 폴더의 파일**을 쓴다.

어느 쪽이든 사용자가 밟는 단계는 같다. 토큰이 있는 사람은 서버 업데이트를 계속 받고, 없는 사람도 그냥 쓴다.

## 무엇이 들어 있나

| 파일 | 내용 | 쓰는 단계 |
|---|---|---|
| `features-list.md` | 기능 ID ↔ 기능명·설명·우선순위·카테고리 디렉토리 (14분류 69개) | 기능 ID로 요청이 오면 맨 먼저 조회 |
| `prd-structure.md` | PRD 9섹션 구조·섹션별 작성 규칙·화면 타입 17종 체크리스트 | `SKILL.md` §3 Step 3·3.5 |
| `flowchart-rules.md` | Mermaid 6도형·화살표·색상·작성 원칙 7가지 | `SKILL.md` §3 Step 2.5 |
| `sb-writing.md` | 화면 분리 원칙·Description 작성 규칙·HTML-to-Figma 호환 | `SKILL.md` §4 Step 2~3 |

## 중복은 담지 않았다

원본 가이드에는 시트 레이아웃·CSS 토큰·메타 헤더 구조·KRDS 컴포넌트 카탈로그도 들어 있지만,
그건 **이미 이 리포에 구현돼 있어서** 옮기지 않았다.

| 원본에 있던 것 | 이 리포에서의 위치 |
|---|---|
| 시트 레이아웃·메타 헤더·캔버스 치수·푸터 CSS | `templates/sb-style-block.html` (생성기가 자동 적용) |
| KRDS 컴포넌트·색상·타이포 | `templates/Commom-sb-styleguide.md` |
| 챗봇 컴포넌트 카탈로그 | `rules/chatbot-sb.md` + `scripts/chatbot_components.py` |
| 생성 프로세스 | `SKILL.md` §4 |

규칙이 한 곳에만 있으니 고칠 때도 한 곳만 보면 된다.

## 고칠 때

이 폴더의 파일을 고치면 **토큰 없는 사용자에게 바로 반영**된다.
서버 쪽 원본도 함께 바꿔야 토큰 쓰는 사용자에게 반영되므로, 규칙을 바꿀 때는 양쪽을 맞춘다.
