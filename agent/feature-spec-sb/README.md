# feature-spec-sb — PRD → SB 화면설계서 에이전트

## 릴리즈노트

| <div align="center"><sub>요약내용</sub><img width="1" height="1"></div> | <sub>업데이트 일자</sub><img width="1" height="1"> | <sub>소유자</sub><img width="45" height="1"> |
|:---|:---:|:---:|
| <sub>Dan Jr. 등급 조회 추가 — 작성자명·양식 질문 직전 `persona.md` 확인(A 진행·B 보고·C 질문), Step 0.1·2.5 승인은 유지</sub> | <sub>2026.10.22</sub> | <sub>김단영</sub> |
| <sub>**(0) 프로젝트 착수 모드 신설** — 서비스명(프로젝트명)·디바이스(PC/모바일 웹) 확인 → 서비스 정의서(경량 PRD) → IA 생성(`ia-builder` 스킬 호출) → 화면별 플로우차트 → SB 추출까지 잇는 신규 파이프라인. `rules/project-kickoff.md` 신설, `sync-skills`에 이 폴더 추가(ia-builder 자동 로드). IA↔SB 연결 지점 실행 검증 완료</sub> | <sub>2026.08.03</sub> | <sub>김단영</sub> |
| <sub>**토큰 프리 전환** — 작성 규칙 정본을 `guides/` 4종(features-list·prd-structure·flowchart-rules·sb-writing)으로 수록. `fetch_guide.py`가 «토큰 있으면 서버 최신본, 없으면 로컬 정본»으로 자동 폴백(`--offline` 옵션). 이미 리포에 구현된 시트 CSS·KRDS 컴포넌트·챗봇 카탈로그는 중복 수록하지 않음. CLAUDE.md·README에 단계별 사용법 명시. 원작자(황다혜 프로) 표기 전 문서 삽입. 검증: 설정 파일 제거 상태에서 SB 8장 192개 검사 + 어드민 9장 전부 통과</sub> | <sub>2026.08.03</sub> | <sub>김단영</sub> |
| <sub>하네스 실동작 테스트 후 수정 — ① PC 캔버스 세로 Flexible 명시(`height:auto` + `--canvas-min-height`, 인라인 높이 고정 시 경고) ② 챗봇·어드민 워크북 경로 하드코딩 제거(원제작자 macOS 경로·고객 파일명 삭제, 미지정 시 설정 방법 안내) ③ `build_chatbot_sb.py`의 스킬 경로를 스크립트 위치 기준으로 변경</sub> | <sub>2026.08.03</sub> | <sub>김단영</sub> |
| <sub>`templates/Commom-sb-styleguide.md` 신규 — KRDS v1.0.0 Figma 공통 컴포넌트 12종 + 디자인 스타일 토큰을 **모노톤(블랙·무채색)** 화면설계 구성요소 가이드로 변환. 토큰(램프/타이포/간격/라운드)·컴포넌트별 Variant·치수·모노톤 색상 매트릭스·SB 표기 규칙·KRDS 원본 컬러 대조표 수록</sub> | <sub>2026.08.03</sub> | <sub>김단영</sub> |
| <sub>폴더 정리 — `references/`를 `rules/`로 옮겨 `reference/`와의 이름 중복 해소. reference=기존 산출물 레퍼런스 · samples=화면설계 HTML · templates=출력 에셋(로고 원본 이동)으로 역할 분리</sub> | <sub>2026.08.03</sub> | <sub>김단영</sub> |
| <sub>최초 등록 — AX-Pilot에서 이관. 범용 PC/MO B2C 화면설계를 기본으로 재구성(챗봇·어드민 규칙 분리) + 회귀 3건 수정</sub> | <sub>2026.08.03</sub> | <sub>김단영</sub> |

PC/모바일 **B2C 웹사이트의 PRD(명세서)와 SB(화면설계서·와이어프레임)** 를 자연어 요청으로 생성·수정하는 Claude Code 에이전트 하네스.

> **원작자 (Owner)** — 황다혜 프로
> **원본 (Resource)** — https://github.com/starryetribe-droid/AX-Pilot/tree/main
>
> 이 폴더는 위 원본의 `feature-spec` 스킬을 모노레포로 이관·재구성한 것이다.
> 작성 규칙·양식·컴포넌트 체계의 설계는 원작자에게 있다.


## 무엇을 만드나

| <div align="center"><sub>모드</sub></div> | <sub>요청 예시</sub> | <sub>산출물</sub> |
|:---|:---:|:---:|
| <sub>**프로젝트 착수**</sub> | <sub>`테스트커머스 서비스 기획해줘` (기능 ID 없이 신규 서비스)</sub> | <sub>서비스정의서 → IA → PRD N개 → SB M개</sub> |
| <sub>PRD</sub> | <sub>`A-02 PRD 만들어줘`</sub> | <sub>9섹션 PRD `.md` (플로우차트 포함)</sub> |
| <sub>SB</sub> | <sub>`A-01 PRD에서 SB 생성`</sub> | <sub>화면별 SB HTML — ETRIBE 2560px 시트(메타 헤더 + 와이어프레임 ∣ Description + 푸터)</sub> |
| <sub>통합</sub> | <sub>`A-04 기획해줘`</sub> | <sub>PRD 작성 → 확인 → SB</sub> |
| <sub>부분 수정</sub> | <sub>`A-01-003 화면 4번 항목 문구 수정`</sub> | <sub>기존 파일 직접 수정</sub> |

SB는 **HTML-to-Figma 임포트**를 전제로 만든다. Description을 한 항목 = 하나의 `<p>`로 쓰는 규칙, Static Pretendard 우선 지정 등이 모두 그 때문이다.

## 신규 서비스부터 시작할 때 (프로젝트 착수)

기능 ID 없이 **완전히 새로운 서비스를 처음부터** 정의하려면 이 파이프라인을 탄다. 서비스명·
디바이스를 맨 앞에서 확인해 두고, 그 답을 IA·SB 단계에서 재사용한다 — 같은 질문을 반복하지
않는다. 상세 절차는 `rules/project-kickoff.md`.

```
서비스명(프로젝트명) 확인 → 디바이스(PC/모바일 웹) 확인 → 작성자명 확인
  → 서비스 정의서 작성(경량 PRD — 개요·목표·대상 사용자·범위)
  → IA 생성 (ia-builder 스킬 호출 — 서비스명/개요/디바이스를 그대로 넘겨 중복 질문 없이 진행)
  → IA 화면을 플로우 단위로 묶어 플로우차트 생성·승인 (+ 필요 시 §3 9섹션 PRD)
  → 화면별 SB 추출 (§4 재사용 — 화면 분리는 IA 결과를 그대로 씀)
```

**전제 조건**: `ia-builder` 스킬이 이 폴더에서 자동 로드돼야 한다. 리포 클론 후 한 번만
실행한다.

```bash
cd dykim-claude-agents-skills
./sync-skills.ps1        # 또는 bash ./sync-skills.sh
```

IA는 별도 스킬(`skills/ia-builder`, 제작: 신지은)이 만들고, PRD·SB는 이 에이전트의 기존
엔진을 그대로 쓴다 — 프로젝트 착수 모드는 이 둘을 잇는 오케스트레이션 레이어다.

## 사용법

**준비물은 Python뿐이다. 토큰·계정 설정이 필요 없다.**

1. 이 폴더에서 Claude Code를 연다 → `CLAUDE.md`가 자동 로딩되어 활성화된다.
2. `A-02 PRD 만들어줘` 처럼 자연어로 요청한다.

엑셀 워크북 기반 분기(챗봇·어드민)를 쓸 때만 `pip install openpyxl`이 추가로 필요하다.

### 단계별로 이렇게 진행된다

**화면설계서(SB)를 만들 때**

| <div align="center"><sub>단계</sub></div> | <sub>무슨 일이 일어나나</sub> | <sub>내가 할 일</sub> |
|:---|:---:|:---:|
| <sub>1</sub> | <sub>작성자명을 묻는다</sub> | <sub>이름 입력 (예: 김기획)</sub> |
| <sub>2</sub> | <sub>모바일/PC 중 무엇인지 묻는다</sub> | <sub>하나 선택 — **한 번에 한 종류만** 만든다</sub> |
| <sub>3</sub> | <sub>작성 규칙을 가져온다</sub> | <sub>— (자동)</sub> |
| <sub>4</sub> | <sub>PRD를 읽고 화면을 나눈다</sub> | <sub>— (자동)</sub> |
| <sub>5</sub> | <sub>화면별 와이어프레임·Description을 쓴다</sub> | <sub>— (자동)</sub> |
| <sub>6</sub> | <sub>화면 하나당 HTML 하나씩 생성</sub> | <sub>결과 확인</sub> |

**명세서(PRD)부터 만들 때**는 앞에 이 단계가 붙는다.

| <div align="center"><sub>단계</sub></div> | <sub>무슨 일이 일어나나</sub> | <sub>내가 할 일</sub> |
|:---|:---:|:---:|
| <sub>1</sub> | <sub>작성자명을 묻는다</sub> | <sub>이름 입력</sub> |
| <sub>2</sub> | <sub>프로세스를 어떻게 알려줄지 묻는다</sub> | <sub>A~E 중 선택 (직접 설명 / 이미지 첨부 / 비슷한 PRD 참고 / 자동 / 다른 PRD 차용)</sub> |
| <sub>3</sub> | <sub>**Mermaid 플로우차트를 그려 보여준다**</sub> | <sub>보고 승인하거나 수정 요청 — 승인해야 다음으로 넘어간다</sub> |
| <sub>4</sub> | <sub>9섹션 PRD를 쓴다</sub> | <sub>— (자동)</sub> |
| <sub>5</sub> | <sub>**빠진 항목을 한 번에 모아 묻는다**</sub> | <sub>답변하거나 "패턴 따라가자" / "스킵"</sub> |
| <sub>6</sub> | <sub>저장</sub> | <sub>결과 확인</sub> |

3번과 5번이 품질을 좌우하는 지점이다. 플로우차트 단계에서 고치는 게 본문을 다 쓴 뒤 고치는 것보다 훨씬 싸고,
5번은 화면 종류별로 흔히 빠뜨리는 항목(빈 상태·권한·에러 등)을 미리 잡아준다.

### 작성 규칙은 어디서 오나

`SKILL.md`가 절차를, `guides/`가 **무슨 내용을 채울지**를 정한다. 규칙은 두 곳 중에서 자동으로 선택된다.

| <div align="center"><sub>상황</sub></div> | <sub>쓰는 것</sub> |
|:---|:---:|
| <sub>`~/.etribe/config.json`에 서버 URL·토큰이 있음</sub> | <sub>ETRIBE 사내 서버 최신본</sub> |
| <sub>설정이 없거나 서버에 못 닿음</sub> | <sub>리포의 `guides/` 로컬 정본</sub> |

**토큰이 없어도 같은 단계로 같은 산출물이 나온다.** 토큰이 있으면 서버 쪽 규칙 업데이트를 계속 받는다는 차이뿐이다.
서버를 건너뛰고 로컬만 쓰려면 `fetch_guide.py --offline`을 쓴다.

## 기본은 범용, 특수는 분리

`SKILL.md`의 기본 대상은 **PC/모바일 B2C 웹사이트**다. 챗봇·어드민 규칙은 `rules/`로 분리해 두고 §8에서 링크하며, 해당 키워드가 명시된 요청일 때만 읽는다. 두 참조 문서는 `SKILL.md` §4의 공통 규칙(골격·모달·Description·screens.json)을 상속하므로 거기 다시 적히지 않은 것은 §4를 따른다.

| <div align="center"><sub>분기</sub></div> | <sub>문서</sub> | <sub>내용</sub> |
|:---|:---:|:---:|
| <sub>어드민</sub> | <sub>`rules/admin-sb.md`</sub> | <sub>A-1 템플릿 기반 어드민 SB(common·chatbot: PC 고정 / krds: **PC/Mobile 범용**) / A-1.2 공통 어드민 프레임 규격 / A-2 세부기능정의 워크북 → PRD</sub> |
| <sub>프로젝트 착수</sub> | <sub>`rules/project-kickoff.md`</sub> | <sub>P-1 신규 서비스 정의 — 서비스명·디바이스 확인 → 서비스정의서 → IA(`ia-builder` 호출) → 플로우차트 → SB</sub> |

## PC / 모바일

한 번에 **한 variant만** 만든다. 캔버스 치수는 `generate_sb.py --variant`가 스타일 블록에 주입한다.

| <div align="center"></div> | <sub>모바일</sub> | <sub>PC</sub> |
|:---|:---:|:---:|
| <sub>캔버스 폭</sub> | <sub>390px 고정</sub> | <sub>1440px 고정 (`--canvas-width`)</sub> |
| <sub>캔버스 높이</sub> | <sub>최소 844px · **상한 없음**</sub> | <sub>최소 1440px · **상한 없음** (`--canvas-min-height`)</sub> |
| <sub>컴포넌트</sub> | <sub>app-bar · tab-bar · FAB</sub> | <sub>GNB · 테이블 · 숫자 페이지네이션 · LNB</sub> |

**높이는 하한만 있고 상한이 없다.** 목록·상세처럼 화면이 길어지면 콘텐츠 길이만큼 세로로 늘어나며 잘리지 않는다.

본문에 인라인 치수를 주면 안 된다. `style="width:100%"`는 시트(`.sb-page`)가 `width:max-content`라 기준 폭이 없어 캔버스가 콘텐츠 폭으로 쭈그러들고, `style="height:…"`나 `max-height`는 긴 화면을 그 높이에서 잘라먹는다(생성 시 경고). 폭은 `--canvas-width`, 높이 하한은 `--canvas-min-height`로 조정한다. 폭이 1724px를 넘기면 시트가 2560px보다 넓어진다는 경고가 나온다.

## 구조

```
feature-spec-sb/
├── SKILL.md                    동작 규칙 정본
├── CLAUDE.md                   진입 안내 (폴더 열면 자동 로딩)
├── ONBOARDING.md               설치·사용법 (토큰 설정은 선택)
├── HISTORY.md                  구축 맥락·결정사항·트러블슈팅 (인수인계용)
├── UPDATE-GUIDE.md             기존 설치 PC 업데이트 절차
├── guides/                     작성 규칙 로컬 정본 (토큰 없을 때 쓰임)
│   ├── features-list.md        기능 ID ↔ 기능명·카테고리 (14분류 69개)
│   ├── prd-structure.md        PRD 9섹션 + 화면 타입 17종 체크리스트
│   ├── flowchart-rules.md      Mermaid 6도형·색상·작성 원칙
│   └── sb-writing.md           화면 분리·Description·Figma 호환
├── rules/
│   ├── admin-sb.md             어드민 분기
│   └── project-kickoff.md      프로젝트 착수 분기 (신규 서비스 정의, ia-builder 연동)
├── scripts/
│   ├── fetch_guide.py          서버에서 가이드 fetch
│   ├── generate_sb.py          screens.json → SB HTML (variant별 캔버스 주입)
│   ├── build_chatbot_sb.py     인텐트 워크북 → SB 일체 생성
│   ├── chatbot_to_sb.py        워크북 → screens.json
│   ├── chatbot_components.py   KRDS 아키타입 12종 렌더러
│   ├── build_component_guide.py 컴포넌트 카탈로그 생성
│   ├── build_admin_sb.py       템플릿 + 본문 → 어드민 PC SB
│   ├── parse_admin_spec.py     세부기능정의 워크북 파서 + 커버리지 검증
│   └── serve.py                로컬 미리보기
├── templates/                  SB 출력에 들어가는 것 — 시트 골격 · 로고(png/base64) · admin-{common,pulmuone,krds}
│   └── Commom-sb-styleguide.md 공통 화면설계 구성요소 가이드 (KRDS → 모노톤 변환 기준)
├── reference/                  기존 산출물 레퍼런스 — 공통 어드민 디자인 시스템 (생성물에 포함 안 됨)
└── samples/                    HTML로 추출된 화면설계 파일 (자세한 안내는 samples/README.md)
    ├── admin/                  어드민 화면 본문 src — 템플릿과 결합해 완성 (KT AX 화면만)
    └── b2c/                    범용 B2C 완성 예시 — mobile 4 · pc 4 · long-page 1 + 입력 json
```

### 폴더 역할 구분

이름이 비슷해 헷갈리기 쉬운 폴더들의 경계는 이렇다.

| <div align="center"><sub>폴더</sub></div> | <sub>담는 것</sub> | <sub>판단 기준</sub> |
|:---|:---:|:---:|
| <sub>`samples/`</sub> | <sub>HTML로 추출된 **화면설계 파일**</sub> | <sub>`admin/`은 본문 src, `b2c/`는 완성 결과물. 새 화면을 그릴 때 패턴으로 본다</sub> |
| <sub>`reference/`</sub> | <sub>**기존 산출물 레퍼런스** (디자인 시스템 등)</sub> | <sub>사람이 열어보는 참고물. 생성물에 들어가지 않는다</sub> |
| <sub>`templates/`</sub> | <sub>SB 출력에 **실제로 삽입되는** 골격·에셋</sub> | <sub>생성물의 일부가 된다 (스타일 블록·로고)</sub> |
| <sub>`rules/`</sub> | <sub>특수 분기 **규칙 문서** (`*.md`)</sub> | <sub>챗봇·어드민 요청일 때만 읽는 지시문</sub> |
| <sub>`guides/`</sub> | <sub>**작성 규칙 정본** (`*.md`)</sub> | <sub>모든 요청에서 쓰는 기본 규칙. 토큰 없을 때 `fetch_guide.py`가 여기서 읽는다</sub> |

## 주의

- **토큰 없이 동작한다.** 작성 규칙 정본이 `guides/`에 있다. 토큰을 설정하면 ETRIBE 사내 서버(Vercel)의 최신본을 우선 쓰며, 서버본은 디스크에 저장하지 않는다. 토큰 발급·회전은 `HISTORY.md` §6.
- **규칙을 고칠 때는 양쪽을 맞춘다.** `guides/`만 고치면 토큰 쓰는 사용자에게 반영되지 않는다.
- `samples/admin/`에는 **KT AX 화면만** 수록했다. 원본 AX-Pilot에 있던 타 고객 샘플은 옮기지 않았다.
- 원본 리포(AX-Pilot)는 공개 저장소다. 고객 자료를 추가할 때 어느 쪽에 넣는지 확인한다.
