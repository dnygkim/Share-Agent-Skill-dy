# 어드민 SB / 어드민 워크북 PRD 분기 (참조 문서)

> `SKILL.md` §8에서 링크된 **특수 분기**입니다. 관리자(백오피스) 화면 또는
> 어드민 세부기능정의 워크북(xlsx) 요청일 때만 이 문서를 읽고 따릅니다.
> 일반 PC/모바일 B2C 화면설계는 `SKILL.md` §4를 따릅니다.
>
> 여기 규칙은 `SKILL.md` §4의 공통 규칙(Description 작성 · screens.json 형식)을
> **상속**합니다. 아래에 다시 적지 않은 것은 §4를 따릅니다.

---

## A-1. 어드민 SB — 템플릿 기반

관리자(백오피스) 화면. 컴포넌트 룩은 **템플릿 1벌**(`templates/admin-<템플릿>.html`)이 단일 출처이고, 화면 본문은 화면별로 작성한다. 템플릿별로 **variant 지원 범위가 다르다**:

| 템플릿 | Variant | 특징 |
|--------|---------|------|
| admin-common | PC 고정 | 공통 어드민(권장 기본), 2560px 프레임 + 무채색/그린 포인트 (A-1.2) |
| admin-chatbot | PC 고정 | 챗봇 어드민, 좌측 GNB + 상단 유틸바 + 그린 |
| admin-krds | **PC / Mobile** | KRDS 기본, Front 표준 컴포넌트 → PC(2560px)/Mobile(390px) **범용 가능** |

```
Step 0   작성자명 입력 요청 (★ 공통)
Step 0.1 템플릿 선택 질문 (★ 필수) — "어떤 템플릿으로 만들까요?"
           - 공통 어드민(권장 기본) → admin-common
           - 챗봇 어드민 → admin-chatbot
           - KRDS 기본 → admin-krds
           사용자가 "챗봇 버전으로" / "KRDS로" 미리 답하면 그 값 사용.
Step 0.1b (admin-krds만) Variant 선택 — "PC 또는 Mobile?"
           - PC → 2560px 캔버스, 데스크톱 관리 화면
           - Mobile → 390px 캔버스, 모바일 관리 화면
           다른 템플릿은 variant 자동 고정 (질문 생략)
Step 0.2 화면 지정 질문 — "어떤 화면을 만들까요?"
           - 등록된 화면(예: 배너목록) → 바로 생성
           - 새 화면 → 시안 이미지/설명을 받아 본문 작성 (아래 Step 1.5)
Step 1   fetch_guide.py --mode sb-pc|sb-mobile --author "{author}" --feature-id "{ID}" --action create
           # (admin-krds Mobile 선택 시 --mode sb-mobile, 나머지는 --mode sb-pc)
Step 1.5 (새 화면만) 본문 작성:
           - templates/admin-<템플릿>.html 의 클래스(.adm-*)로 .wf-canvas 본문 + .desc-panel 작성
           - samples/admin/KTAX-AD-MN01-0000.src.html 을 패턴으로 참고 (영역마다 .adm-num 배지 1:1)
           - samples/admin/<ID>.src.html 로 저장하고 build_admin_sb.py SCREENS에 등록
Step 2   python3 .claude/skills/feature-spec/scripts/build_admin_sb.py {화면키}
           # 또는: --src samples/admin/<ID>.src.html --id <ID> --title "..." --path "..." --template admin-krds --variant mobile
```

`build_admin_sb.py`가 한 번에 수행: ① 템플릿 스타일 + 화면 본문 결합 → ② `generate_sb.py --variant {pc|mobile}` 렌더.
출력: `~/Downloads/SB_어드민/{ID}.html` (환경변수 `ADMIN_OUT`로 변경).

규칙:
- **admin-common / admin-chatbot = PC 고정**. `SKILL.md` §4.0의 PC/Mobile 질문 생략.
- **admin-krds = PC/Mobile 범용**. Step 0.1b에서 variant를 명시적으로 선택. 모바일 페어 콘텐츠 동일성 규칙(가이드 PC §)은 어드민 단독이라 적용 안 함. ★ KRDS는 Front 기본 컴포넌트를 사용하므로 두 variant 모두 동일한 컴포넌트 룩.
- 넘버 배지는 프론트 표준(`.num-badge` 빨강 캡슐 스타일). `overflow:hidden` 컨테이너 안에 두지 말 것(가이드 §6.2).
- **★ n-n 서브 넘버링 (사용자 확정 2026-07-07)**: 영역 배지(n)만으로 끝내지 말 것.
  영역 내 세부 요소도 `n-m` 서브 배지(`.adm-num.sub`, 소형)로 와이어프레임에 1:1 부여
  (예: 필터 조건 4-1~4-8, 테이블 컬럼 8-1~8-15). Description의 번호와 정확히 일치시킬 것.
- 컴포넌트 룩 변경/추가는 `templates/admin-<템플릿>.html` 한 곳에서. 새 화면은 본문 src만 추가.
- 챗봇과 달리 워크북이 없으므로 **새 화면은 시안(이미지/설명) 또는 PRD**가 입력 소스.
  프로젝트에 기존 PRD가 있어도 **소스로 쓸지 사용자에게 반드시 확인** 후 진행.
- 환경변수: `ADMIN_OUT`(출력 루트, 기본 ~/Downloads/SB_어드민) · `ADMIN_AUTHOR`(작성자 기본 'AX Pilot').

### A-1.1 ★ 챗봇 SB 표준 프로세스 (사용자 확정 2026-07-07)

"챗봇 SB 만들고 싶어"류 요청(소스 미첨부)은 아래 순서를 **고정**으로 따른다:

```
1. 작성자명 질문 (★ 공통)
2. 기능정의 엑셀(어드민 세부기능정의 워크북 xlsx) 첨부 요청
     예: {프로젝트명}_어드민_세부기능정의_YYYYMMDD.xlsx → ADMIN_SPEC_XLSX
3. A-2 분기로 PRD 생성 (커버리지 기계 검증 포함) → 사용자 컨펌 대기
4. PRD 컨펌 후 A-1 어드민 SB 생성 (템플릿: 챗봇 admin-chatbot)
```

- 3→4 사이 컨펌 없이 SB로 넘어가지 말 것.
- 워크북 없이 시안/기존 PRD로 바로 SB를 원하면 A-1 기본 플로우로 진행(이때도 소스 확인 질문 필수).

### A-1.2 ★ 공통 어드민 템플릿 (admin-common) — 프레임·퍼블리싱 규격 (사용자 확정 2026-07-21)

브랜드 무관 공통 어드민의 **권장 기본 템플릿**. 디자인 시스템 단일 출처 =
워크스페이스 `90. 어드민/DesignSystem/admin-common-design-system.html` (컴포넌트 룩·토큰·상태 정의,
저장소 사본: `reference/admin-common-design-system.html` — 워크스페이스본 수정 시 사본도 갱신).
템플릿(`templates/admin-common.html`)은 이 시스템에서 추출한 것 — **룩 수정은 디자인 시스템 → 템플릿 순으로 반영**.

**프레임 규격 (절대 어기지 말 것)**:

| 항목 | 값 |
|------|-----|
| `.admin-canvas` | **W 2560px 고정** · min-height 1504px (헤더 64 + 바디 1440) |
| 헤더 `.adm-topbar` | H 64px 풀폭 |
| LNB `.adm-gnb` | W 260px |
| 콘텐츠 `.adm-content` | **W 1440px 고정**, `.adm-main`(flex 중앙)이 자동 센터링 |
| 수직 여백 | 콘텐츠 상단 48px / 하단 96px (`.adm-content` padding에 내장) |
| 수직 리듬 | 카드 간 24px(`.adm-content` gap) · 섹션 간 40px(`.adm-sec-gap` 16px 추가) · 카드 패딩 24px |
| 컨트롤 높이 | 기본 40 · 소형 32 · 대형 48 · 모달 풀버튼 52 |

**본문 골격** (src 작성 시 이 구조 고정):
```html
<div class="wf-canvas admin-canvas">
  <div class="adm-topbar">…</div>
  <div class="adm-body">
    <div class="adm-gnb">…</div>
    <div class="adm-main"><div class="adm-content">
      <div class="adm-pagebar">…</div>
      <!-- 필터 카드 / 툴바 / 테이블 / 페이지네이션 … -->
    </div></div>
  </div>
</div>
```

**디자인 규칙**: 무채색 기본(Primary 버튼 = g900 검정). 컬러는 상태 전용 —
Green(태그·토글 ON), Red(공지·삭제·에러), Blue(텍스트 링크). 폰트 Pretendard
(generate_sb.py 보일러플레이트가 CDN 로드, 템플릿 `--adm-font`로 강제).
선택 컨트롤: **다중 선택 = 사각 체크박스(.adm-check) · 배타 선택 = 점 라디오(.adm-radio)** 각 1종만.

**퍼블리싱 품질 (HTML-to-Figma + 개발 직행)**: 이 템플릿의 SB는 와이어프레임이자
퍼블리싱 산출물이다 — ① 시맨틱 마크업(table은 `<table>`, 버튼은 button성 요소)
② 레이아웃은 flex/grid로 실제 동작(absolute 좌표 배치 금지, .adm-num 배지 제외)
③ 색·치수는 템플릿 CSS 변수만 사용(임의 hex/px 최소화) ④ Description desc-block 규칙(`SKILL.md` §4.4) 동일 적용.

**★ 넘버 배지 오버레이 (사용자 확정 2026-07-22)**: 배지는 와이어프레임 레이아웃에
영향을 주면 안 된다 — 인라인(static) 배치 금지, `<br>`로 줄 분리 금지. 영역 배지·세부
배지(.adm-num.sub) 모두 absolute 오버레이(th/td/.adm-field/.adm-kv>div는 템플릿이 relative 처리,
기본 오프셋 -8~-10px). 버튼·셀렉트 등 단일 요소에는 `.adm-anchor` 래퍼로 감싸 부여.

**★ 팝업 = 별도 SB 페이지 (사용자 확정 2026-07-22)**: admin-common에서는 `SKILL.md` §4.3의
서브 캔버스 규칙 대신 **모달/팝업을 별도 SB 페이지로 분리**한다 (화면ID -00N 증분,
예: ADM-MAIN-002 배너 등록/수정 팝업). 팝업 페이지 캔버스 = 회색 스테이지(#DFE2E6)
중앙에 .adm-modal 배치, 부모 화면 desc에 «연결 SB» 상호 참조 표기.
**알럿·토스트류 경량 오버레이만** 같은 장 우측 서브 캔버스 허용.

**★ SB 시트 양식 (사용자 확정 2026-07-28 — 레퍼런스 화면설계서 기준)**

시트 골격은 `generate_sb.py` + `sb-style-block.html`이 자동 처리한다 — src에서 재정의 금지:
- 메타 테이블 2행: 1행 «화면/컴포넌트·값 | Local·KO | 화면ID·작성자·작성일(라벨)» /
  2행 «화면경로·값 | Channel·값 | 화면ID값·작성자값·작성일값». th 배경 #E9E9E9 + 글자 #111.
- 작성일 = YYYY-MM-DD 전체 날짜, 어드민은 Channel=Admin (`build_admin_sb.py`가 channel 전달).
- 시트 가장자리 여백 40px(상단 28px) — 메타/본문이 가장자리에 붙지 않음. 시트 좌상단 타이틀 없음.
- 좌측 와이어프레임 영역 = .wf-panel 1px 외곽선 박스.
- 푸터: 시트 끝~끝 전폭 구분선 + 우측 하단 ETRIBE 로고만 (버전 표기 없음). 본문이 짧아도 시트 하단 고정.

**Description 패널(src 작성 시) 규칙 — 섹션은 정확히 2개**:
1. «화면 설명» — 화면 유형·경로·연결 SB·프론트 연동 등 개요 bullet만.
   **화면ID·화면명 라인 넣지 않음** (메타 테이블과 중복).
2. «Description» — 번호 항목(1~N, 배지와 1:1) 전체. 동작·예외 항목은 별도 섹션으로 만들지 말고
   Description 하단에 `[동작 / 예외]` 라벨 li 이후 이어서 작성.
섹션 헤더/본문 스타일(연회색 헤더, 본문 16px 통일)은 스타일 블록이 처리 — desc-block 규칙(`SKILL.md` §4.4)만 준수.

**★ 필터 카드 배치 (사용자 확정 2026-07-29)**: 키워드 검색 조합(검색 기준 셀렉트 + 검색어 인풋)은
필터 카드에서 **항상 맨 아래**(그리드 = 마지막 행, 인라인 = 액션 앞 맨 뒤)에 배치한다.
배지 번호는 정의서 번호를 따르므로 시각 순서와 달라도 무방.

**★ 배지 겹침 금지 (사용자 확정 2026-07-29)**: 영역 배지(n)와 세부 배지(n-m)가 같은 자리에
겹치면 안 된다. 템플릿이 자동 분리 —
- 세부 배지는 **대상 요소의 시작점 위(left:0)**: 테이블 th는 컬럼 좌측 시작점, 앵커(.adm-anchor)는 요소 좌측.
- **테이블 영역 배지는 좌측 바깥(left:-30px)** — 첫 컬럼 세부 배지와 충돌 회피.
인라인 스타일로 배지 위치를 재정의할 때도 서로의 점유 영역(배지 크기 ≈ 22×22px)을 침범하지 말 것.
검증법: 전 배지 쌍의 rect 교차 검사 = 0건.


## A-2. 어드민 세부기능정의 워크북 → PRD

소스가 **어드민 세부기능정의 워크북(xlsx)** 인 경우의 PRD 분기. **산출물 = PRD만.**
시트 구조: `항목(메뉴) / 세부항목 / 기능(번호 아웃라인) / 세부기능(규칙 산문) / 비고 / 진행여부 / 예시 화면 / 기능매핑`.
목표 = **누락 0**: 워크북의 모든 기능 라벨·규칙·예외가 PRD에 반영되고, 이를 **기계 검증**으로 보증한다.

★ 일반 PRD 모드(§3)와 다른 점 — **검토 절차 전부 생략**:
- Step 0.1 프로세스 입력 질문 X (워크북이 프로세스 정의를 대체)
- Step 2.5 Mermaid 프리뷰/승인 루프 X (플로우차트는 PRD §3 본문에 바로 포함)
- Step 3.5 화면별 체크리스트 질문 X — 워크북 미정의 항목은 ETRIBE 공통 패턴을
  자동 적용하되 PRD에 **«(제안)»** 표기로 구분. 비즈니스 결정이 꼭 필요한 것만 질문.

```
Step 0   작성자명 입력 요청 (★ 공통)
Step 0.1 워크북 경로(ADMIN_SPEC_XLSX) + 대상 항목(메뉴) + 기능ID 확인
           - 기능ID 제안: ADM-{항목 영문 슬러그} (예: 챗봇 대화 내역 → ADM-CHAT)
Step 1   python3 .claude/skills/feature-spec/scripts/parse_admin_spec.py --id {ID}
           → _build/{ID}_spec.json + _build/{ID}_checklist.md
           체크리스트 = 기능 라벨(하드) · 예외(PRD §5 필수) · 조건 분기 · 규칙(Default/포맷/옵션)
Step 2   9섹션 PRD 작성 (가이드 §3 구조 그대로, 프리뷰 없이 일괄 작성)
           - §3 플로우차트: Mermaid 6도형/색상 규칙으로 본문에 포함 (승인 루프 없음)
           - §5 예외 처리: 체크리스트 «예외» 전수 + 공통(조회 0건·API 실패·권한)은 «(제안)» 표기
           - §6 화면별 UI: 체크리스트 «기능 라벨» 전수 + 규칙(Default·포맷·옵션) 반영
Step 3   저장 전 커버리지 검증 (★ 필수, 통과까지 반복):
           python3 .../parse_admin_spec.py --id {ID} --verify {PRD.md}
           → 누락 라벨 0 될 때까지 보완. «매칭 약한 규칙»은 직접 확인 후 진행.
Step 4   Write로 저장: 90. 어드민/PRD/{기능ID}_{영문슬러그}.md (워크스페이스 기준)
           verify 출력(✓/✗)을 사용자에게 그대로 보여주고 완료 보고.
```

규칙:
- 검증(Step 3)을 건너뛴 채 저장/완료 보고 금지.
- 워크북에 없는 동작을 임의 추가하지 않는다. 보완이 필요하면 «(제안)» 표기로 구분(비고 열 참고).
- `진행여부`·`기능매핑` 열 값이 있으면 PRD §1(개요)·§6에 반영.
- **SB는 여기서 만들지 않는다.** 필요 시 사용자가 별도로 요청하면 A-1 어드민 SB 분기로 진행
  (이때 PRD·체크리스트를 입력 소스로 사용, Description 기능번호 1:1 규칙 동일).
- 환경변수: `ADMIN_SPEC_XLSX`(워크북 경로, 필수).
