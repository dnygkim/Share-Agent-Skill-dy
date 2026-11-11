# 화면설계 에이전트 (PRD → SB 화면설계서)

이 폴더는 **PC/모바일 B2C 웹사이트의 PRD(명세서)와 SB(화면설계서·와이어프레임)** 를 생성·수정하는 에이전트 하네스다. 이 폴더에서 Claude Code를 열면 이 파일이 자동 로딩된다. (모든 경로는 이 폴더 기준 상대경로.)

> **Owner** 황다혜 프로 · **Resource** https://github.com/starryetribe-droid/AX-Pilot/tree/main

## 정본은 SKILL.md

동작 규칙 전체가 **`SKILL.md`** 에 있다. 요청을 받으면 먼저 `SKILL.md`를 읽고 그 절차를 그대로 따른다. 이 파일은 진입 안내일 뿐 규칙을 중복해서 적지 않는다.

## 이 에이전트가 하는 일

| 모드 | 입력 | 산출물 |
|---|---|---|
| (0) 프로젝트 착수 | 신규 서비스 전체 정의 ("OO 서비스 기획해줘") | 서비스정의서 → IA → PRD N개 → SB M개 |
| (1) PRD | 기능 ID + "PRD만" | 9섹션 PRD `.md` |
| (2) SB | PRD `.md` 경로 | 화면별 SB HTML (ETRIBE 2560px 시트 양식) |
| (3) 통합 | 기능 ID/이름만 | PRD → 확인 → SB |
| 부분 수정 | 기존 파일 + "수정/추가" | Edit로 직접 반영 |

**기능 ID가 없는, 완전히 새로운 서비스 요청**은 (0) 프로젝트 착수로 간다 — 아래 첫 번째
단계별 실행 표를 본다. 기능 ID가 있으면 (1)/(2)/(3) 기본 모드다.

**기본 대상은 PC/모바일 B2C 웹사이트다.** 챗봇·어드민은 그 위에 얹는 특수 분기이며, 해당 키워드가 명시된 요청일 때만 `rules/`의 문서를 읽는다 (`SKILL.md` §8).

## 작성 규칙은 어디서 오나 — 토큰 없이도 된다

`fetch_guide.py`가 두 곳 중에서 자동으로 고른다.

1. `~/.etribe/config.json`에 서버 URL·토큰이 **있으면** → ETRIBE 사내 서버 최신본
2. **없거나 서버에 못 닿으면** → 리포의 `guides/` 로컬 정본

**토큰이 없어도 같은 단계로 같은 산출물이 나온다.** 사용자에게 토큰 설정을 요구하지 말 것.
어느 쪽을 썼는지는 stderr에 `[INFO] 로컬 가이드 사용` 또는 서버 응답으로 표시된다.
서버를 건너뛰려면 `--offline`을 붙인다.

fetch 출력이 비어 있을 때만 사용자에게 알린다. **규칙을 지어내지 않는다.**

## 단계별 실행 (신규 서비스 정의 — 프로젝트 착수)

사용자가 "OO 서비스 기획해줘"처럼 **기능 ID 없이 새 서비스 자체**를 요청하면 이 순서로
진행한다. 상세 절차는 `rules/project-kickoff.md`.

```
Step 0   서비스명(프로젝트명)을 묻는다        ← 답 받기 전 다음 단계 금지
Step 0.1 디바이스를 확인한다 (PC/모바일 웹/둘 다) ← 이 답을 IA·SB 양쪽에 재사용, 다시 안 물음
Step 0.2 작성자명을 묻는다
Step 1   서비스 정의서(경량) 작성 — 개요·목표·대상 사용자·범위
Step 2   ia-builder 스킬 호출 — Step 0·1 정보를 넘겨 중복 질문 없이 IA 생성
Step 3   IA 화면을 플로우 단위로 묶어 플로우차트 생성(승인) + 필요 시 §3 9섹션 PRD
Step 4   화면별 SB 추출 (§4 재사용, 화면 분리는 IA 결과 사용 — §4 Step 2 생략)
```

`ia-builder`가 이 폴더에서 로드되지 않으면(최초 클론 직후) `./sync-skills.ps1` 또는
`sync-skills.sh`를 안내한다.

## 단계별 실행 (SB 만들기 — 기존 기능 ID)

사용자가 "A-01 SB 만들어줘" 또는 "A-02 기획해줘"라고 하면 이 순서로 진행한다.
각 단계는 앞 단계가 끝나야 시작한다.

```
Step 0   작성자명을 묻는다               ← 답 받기 전 다음 단계 금지
Step 0.5 모바일 / PC 중 무엇인지 확인      ← 한 번에 하나만. 둘 다면 순차로
Step 1   fetch_guide.py --mode sb-mobile|sb-pc --author "{작성자}"
Step 2   PRD를 읽고 화면을 나눈다          ← 분리 원칙은 가이드 sb-writing
Step 3   화면별 body HTML 작성            ← §4.2 골격 필수, 캔버스 치수는 손대지 않는다
Step 4   screens.json 작성 (§4.5 형식)
Step 5   generate_sb.py --variant {mobile|pc} --input … --output …
Step 6   생성 결과를 사용자에게 보고        ← 화면 수·경로·경고 유무
```

**PRD부터 만드는 경우**는 위 앞에 이 단계가 붙는다.

```
Step 0   작성자명을 묻는다
Step 0.1 프로세스를 어떻게 알려줄지 묻는다 (A~E)   ← 답 받기 전 금지
Step 1   fetch_guide.py --mode prd --author "{작성자}"
Step 2   features-list에서 기능명·카테고리 조회
Step 2.5 Mermaid 플로우차트를 보여주고 승인받는다   ← 승인 전 본문 작성 금지, 반복 가능
Step 3   9섹션 PRD 작성
Step 3.5 화면 타입 17종 체크리스트로 누락 항목을 한 번에 질문   ← 답 받기 전 저장 금지
Step 4   저장
```

멈춰야 하는 지점(Step 0 / 0.1 / 0.5 / 2.5 / 3.5)에서 사용자 답을 받지 않고 진행하지 않는다.

## 지켜야 할 것

- 모든 모드는 **작성자명을 먼저 묻는다**. `fetch_guide.py` 호출 전 필수이며 `--author` 없이 호출하지 않는다.
- PRD 모드는 **프로세스 입력 요청(Step 0.1)** 과 **Mermaid 플로우차트 승인(Step 2.5)** 을 건너뛰지 않는다.
- **Dan Jr. 등급 조회(승인 게이트 공통, 2026-10-22)**: 작성자명·양식·「~할까요?」를 묻기 직전에 `~/.claude/persona/persona.md`(전역 규칙이 없는 환경은 `../../persona/persona.md`)에서 같은 상황을 찾는다. 등급 **A**면 묻지 않고 기본값으로 진행, **B**면 진행 후 완료 보고에 한 줄, **C** 또는 해당 항목 없음이면 지금처럼 묻는다. 건너뛴 게이트는 완료 보고에 「Dan Jr. 적용: D-01(A)」처럼 ID로 적는다. Step 0.1·2.5처럼 persona.md에 없는 결정은 그대로 사용자 승인.
- SB는 한 번에 **한 variant만** 만든다 (모바일 또는 PC). 둘 다 필요하면 순차로.
- 캔버스 치수는 `generate_sb.py --variant`가 주입한다. **높이는 하한만 있고 상한이 없어 긴 화면은 그만큼 늘어난다.**
  본문에 `width:100%`(폭 쭈그러듦)나 `height:…`/`max-height`(긴 화면 잘림) 같은 인라인 치수를 쓰지 않는다.
- Description은 한 항목 = 하나의 `<p class="desc-block">`. `<div>` 분리·CSS `::before` 금지 (HTML-to-Figma 호환).

## 폴더

```
feature-spec-sb/
├── SKILL.md            # 동작 규칙 정본 (기본 = PC/모바일 B2C 화면설계)
├── CLAUDE.md           # 이 파일 (진입 안내)
├── ONBOARDING.md       # 설치·토큰 설정·사용법
├── HISTORY.md          # 구축 맥락·결정사항·트러블슈팅 (인수인계용)
├── UPDATE-GUIDE.md     # 기존 설치 PC 업데이트 절차
├── guides/             # 작성 규칙 정본 (토큰 없을 때 fetch_guide.py가 여기서 읽음)
│   ├── features-list.md    기능 ID ↔ 기능명·카테고리
│   ├── prd-structure.md    PRD 9섹션 + 화면 타입 17종 체크리스트
│   ├── flowchart-rules.md  Mermaid 작성 규칙
│   └── sb-writing.md       화면 분리·Description·Figma 호환
├── rules/              # 특수 분기 규칙 — 해당 요청일 때만 읽음
│   ├── chatbot-sb.md       # C-1 인텐트 워크북 → SB · C-2 컴포넌트 가이드
│   ├── admin-sb.md         # A-1 어드민 SB(템플릿) · A-2 세부기능정의 워크북 → PRD
│   └── project-kickoff.md  # P-1 신규 서비스 정의(서비스명·디바이스 확인→PRD→IA→플로우차트→SB)
├── scripts/            # fetch_guide · generate_sb · 챗봇/어드민 빌더
├── templates/          # SB 출력에 삽입되는 것 — 시트 골격 · 로고(png/base64) · 어드민 템플릿 3종
├── reference/          # 기존 산출물 레퍼런스 — 공통 어드민 디자인 시스템 (생성물에 포함 안 됨)
└── samples/            # HTML로 추출된 화면설계 파일 (samples/README.md 참고)
    ├── admin/              어드민 화면 본문 src (KT AX 화면만)
    └── b2c/                범용 B2C 완성 예시 (모바일·PC 각 4장 + 긴 화면 1장)
```

## 폴더에 무엇을 넣나

새 파일을 어디 둘지 헷갈리면 이 기준으로 판단한다.

- `samples/` — 완성된 **화면설계 HTML**(`*.src.html`). 새 화면을 그릴 때 패턴으로 본다.
- `reference/` — **기존 산출물 레퍼런스**. 사람이 열어보는 참고물이고 생성물에 들어가지 않는다.
- `templates/` — SB 출력에 **실제로 삽입되는** 골격·에셋.
- `rules/` — 에이전트가 읽고 따르는 **규칙 문서**.

`samples/admin/`에는 **KT AX 화면만** 들어 있다(원본에 있던 타 고객 샘플 미포함). 어드민 새 화면은 `KTAX-AD-MN01-0000.src.html`을, 범용 B2C 화면은 `samples/b2c/`의 완성 예시를 패턴으로 본다.
