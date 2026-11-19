# ORCHESTRATOR — IA·공수 HTML 자동 생성 파이프라인

> 이 하네스는 `.claude/`가 아닌 `works/` 안에 있어 **자동 트리거되지 않는다**. 메인 에이전트(나)가 이 문서를 읽고 직접 실행한다: 각 단계에서 해당 역할 정의(`agents/*.md`)의 내용을 **프롬프트로 주입**해 `Agent(subagent_type: "general-purpose", model: "opus")`로 스폰한다.

## 실행 모드
**파이프라인 (순차 의존)** + 마지막에 builder↔qa 생성-검증 루프. 한 방에 끝까지 생성 후 사용자가 수정하는 방식.

```
analyst → architect → builder → qa ──(FAIL)──▶ builder 보정 → qa 재검수
   │          │          │         (PASS)
   ▼          ▼          ▼            ▼
01_analysis 02_spec   03_draft.html  04_qa → 최종 HTML 확정
```

## Phase 0: 컨텍스트 확인 (시작 시 반드시)
- **★ 프로젝트별 작업 폴더**: 중간 산출물은 `_workspace/{프로젝트slug}/`(예: `_workspace/woongjin-direct/`)에 둔다. **여러 프로젝트가 `_workspace/01·02`를 공유하면 서로 덮어쓴다**(실제 사고: GS칼텍스 런이 웅진 01/02 덮음). slug는 고객·주제로 생성.
- `_workspace/{slug}/` 상태로 실행 모드 결정:
  - 비어있음 → **초기 실행** (analyst부터)
  - 존재 + 부분 수정 요청 → **부분 재실행**(해당 단계만; 스크립트 렌더면 02_spec.json 수정 → build_report 재실행)
  - 존재 + 새 입력 → 기존을 `{slug}_prev/`로 이동 후 초기 실행.

## ★ 시각 표시 (시작·완료)
- **착수 시**(분석/작성 시작): 현재 시각을 조회(`date +"%H:%M"` 또는 PowerShell `Get-Date -Format "HH:mm"`)해 `현재 HH시 MM분입니다. 작업 시작합니다.` 한 줄.
- **최종 HTML 완성 시**: 같은 방식으로 `현재 HH시 MM분입니다. 작업 완료했습니다.` (착수~완료 경과 가늠용). 시:분은 환경에 없으니 반드시 조회해서 쓴다(추정 금지).
- 완료 보고에는 HTML 산출물의 **내부망 URL**을 짧은 주소(`http://<IP>:<포트>/`)로만 함께 적는다 — 절차 = CLAUDE.md 3c

## Phase 1: 입력 수집 + 인테이크 + 변형 결정
- **입력 데이터 계약**(`report-spec.md` §2): project·palette·ia·admin_ia·scope_premise·externals·boundary·schedule·team·measure_note.
- **★ 입력 자료 출처 인벤토리 (자료 > 유추)**: analyst가 분석 착수 전 받은 모든 자료(RFP·**기능목록 xls/시트**·인프라 구성도·이미지·사이트)를 영역×출처(자료제공/부분/없음)로 매핑한다. **자료가 제공된 영역은 자료를 정본(실측)으로 반영**하고 "자료 기반"으로 표기 — 유추로 깎지 마라. (사고: 관리자 79기능 자료를 유추로 오표기 → analyst.md "입력 자료 출처 인벤토리" 절 신설.)
- **★ 인테이크 — 한 번에 하나씩 순차 질문** (분석 착수 직전): 사용자가 작성을 시작하면, 필요한 확인 항목을 **한꺼번에 나열하지 말고 한 번에 하나씩** 묻고 답을 받은 뒤 다음 항목으로 넘어간다(짧은 단일 질문 또는 `AskUserQuestion` 1개). **콜드 메뉴 금지·추론 가능한 건 묻지 않음**(산출물 종류는 추론·선언). 한 항목에 "알아서/모름"이면 표준 가정으로 그 항목만 진행하고 다음으로.
  - **첫 응답**: 추론한 산출물/범위를 1줄 선언("이 요건이면 공수산정 리포트로 봅니다") + "확인 몇 가지를 하나씩 여쭐게요".
  - **질문 순서 = 고정 필수 5(항상) + 조건부 + 동적(RFP 근거)**:
    - **[A] 고정 필수 — RFP와 무관하게 모든 프로젝트에서 항상 묻는다**(이미 자료/대화로 확정된 항목만 건너뜀):
      ① **디자인 수준**(보통/높음/프리미엄)
      ② **개발 방법**(기존 소스 그대로 활용 / 부분 재개발 / 전면 신규 — 리뉴얼·이관·신규 구분. **공수의 핵심 분기**, project-cases 케이스 결정)
      ③ **인프라 구축(실제 작업) 포함 여부** — 우리가 **실제 구축·세팅(공수에 포함)**하는지, **구성도 제시만(작업 아님)**인지. (인프라=제시지 작업 아님 원칙의 출발점)
      ④ **상주 / 비상주**
      ⑤ **고객 요청 프로젝트 기간**(개월) + 일정·예산 압박 정도
    - **[B] 조건부**: (RFP에 **AS-IS 인프라**가 있으면) **TO-BE 인프라 제안 포함 여부**.
    - **[C] 동적 — 이 RFP에서 도출한 추가 확인 질문(적극 포함)**: ⑥ analyst가 RFP를 전수 항목화하며 찾은 **실제 미상·모호 항목** 중 **공수/범위에 영향 큰 것**(보통 2-4개, RFP 실질에 맞게)을 묻는다. 고정 1-2개 캡 아님. `playbook-domain-questions`는 빈칸을 빠뜨리지 않기 위한 *보조 체크리스트*다.
  - **★ ⑥ 동적 질문 = "이 RFP가 다루는 것의 빈칸 메우기"지 "RFP에 없는 신규 기능 타진"이 아니다**: RFP에 명시됐는데 값이 비었거나 모호한 것을 적극적으로 묻는다(예: PG사·결제수단 미정, 연동 N종 규격/테스트계정 시점, 관리자 권한 등급, 정산/환불 책임 경계, 다국어·이관 범위). **하지만 RFP에 없는 기능을 "혹시 챗봇/AI/추천도 필요하세요?"로 타진하지 마라**(출력 가드를 질문으로 우회). RFP에 없으면 묻지 말고 범위 밖으로 둔다.
  - **한꺼번에 답하면 그대로 수용**하고 남은 항목만 이어서 묻는다(순차가 원칙이지 강제 1턴-1문항은 아님).
  - 공수 반영: **비상주→퍼블·개발 최대 -30%**(기획/디자인 제외) / **상주→감면 없음 + 상주 인력 장기 0.5 금지**. 미응답 시 상주 가정(보수적).
  - 받은 정성 신호는 analyst가 `01`의 "정성 신호·리스크"에 기록 → architect가 **공수 가중**(디자인 high→디자인·퍼블↑, 기획 염려→버퍼+confidence↓, 비상주→-최대30%, 상주→PM 장기0.5 금지).
- **★ 사용자가 투입공수표(team)를 제시하면 그게 최우선 정본** → architect는 역산 모드.
- **산출물 변형 결정**(`report-spec.md` §1): ① 단독안 ② 통합안 ③ 옵션 비교안 ④ 동시진행안.

## Phase 1.5: corpus 검색 (유사 선례 끌어오기) + id 확정
- **★ 프로젝트 id를 1회 확정**: `id = {고객}-{주제}` 안정 slug(= `_workspace/{slug}`의 slug와 동일). 이후 모든 snapshot·save가 이 id를 쓴다 → 중간물과 최종본이 corpus `deliverables/{id}/` 한 폴더로 모인다. 재작업은 같은 id(덮어써 최신화).
- `python scripts/corpus.py pull` 후, 새 프로젝트의 도메인·기능 태그로 `search` → 유사 과거 산출물 상위 N건을 analyst·architect 참고자료로 전달. 가이드 `references/corpus-knowledge-base.md`.
- **★ 케이스 먼저(KB 사용법)**: 새 건의 유형(신규구축/리뉴얼/이관/기능추가/모듈이식)을 정해 **`cases/{유형}.md`**에서 "통상 범위 + 꼭 확인할 것 + 공수 밴드"를 참고한 뒤, 유사 대표 프로젝트의 **`scope/`→`questions/`→`estimates/` 사슬**과 도메인 **`patterns/`**로 내려간다. corpus는 원자 카드(섹션별)라 큰 HTML 재분석 불필요.
- **★ corpus 상태를 사용자에게 항상 가시화(흔적 남김)**: pull+search 직후 **반드시 한 줄 보고**한다 — 연결되면 `📚 corpus: 유사 선례 N건 [{id}({total_mm}M/M)·…]` (없으면 `📚 corpus: 유사 선례 0건(신규 패턴)`), **연결 실패면** `⚠️ corpus 미연결({사유: 토큰 없음/오프라인}) — 선례 참조 없이 진행`. 이 한 줄이 "git 데이터를 봤다"는 흔적이다. **`[WARN] 준비 실패`를 조용히 넘기지 마라** — 그 경우 사용자에게 미연결을 명시(테스트 폴더는 `.env` 토큰 필요).
- **★ 선례 반영 흔적을 산출물까지 전달**: search 결과가 있으면 analyst가 `01`에 **"참조 선례"**(id·유사도·끌어온 교훈·`⚠️under_estimated` 경고)를 적고, architect는 산정 근거 코멘트에 **어느 선례 밴드를 참고했는지** 남긴다. 단순 복붙·앵커링이 아니라 "선례 대비 본 건은 왜 이 수준"의 근거로 쓴다(아래 산정 독립성과 병립 — corpus는 허용된 참조다).

## Phase 2~5: 단계 실행 (앞단·중간단 병렬) — `{ws}` = `_workspace/{프로젝트slug}/`
| Phase | 에이전트 | 모델 | 입력 | 출력 | 비고 |
|-------|---------|------|------|------|------|
| 2a | **site-analyst** (사이트 URL 있을 때만) | **sonnet** | 사이트 URL | `{ws}/01a_site-ia.md` (+`01a_site-ia.json`) |
| 2b | analyst (requirement+병합) | opus | 자료 + 인테이크 + corpus + (있으면)01a | `{ws}/01_analysis.md` |
| 3a | architect | opus | 01 + corpus + 정성 신호 | `{ws}/02_spec.json` (build_report 스키마) + `02_spec.md`(사람용) |
| 3b | solution-architect | opus | 01의 연동/API/경계 (SSOT 불요) | `{ws}/02b_solution.json` (+`02b_solution.md`) | **★ 조건부: infra/concept가 스코프일 때만**. 인프라 구축/구성도·생태계 도식이 불필요한 단순건(정적 소개형 등)은 **skip**(opus 1회 절감) |
| **3c** | **persona-review (estimate)** | **opus** | 01 + 02_spec(공수·인사이트·인프라) | `{ws}/02c_persona_review.md` (페르소나별 코멘트·P0/P1·결론) | 공수 타당성 + **콘텐츠 발전도(RFP 나열↔고도화)** 정면 검토 |
| 4 | builder | **sonnet** | 02_spec.json + prose | `{ws}/03_draft.html` |
| 5 | qa | **sonnet** | 03 (검증은 스크립트) | `{ws}/04_qa.md` |
| **5b** | **persona-review (final)** | **opus** | 03_draft.html(qa PASS 후) | `{ws}/04b_persona_review.md` (콘텐츠 관점) | **★ 조건부: 3c가 콘텐츠 실질 변경 P0/P1 / 폴백 수기렌더 / 대형·고위험 때만**. 평시(결정적 렌더+3c 깨끗+표준규모)는 **skip**(opus 1회 절감) |

- **★ 렌더 경로(기본 = 스크립트 결정적)**: architect가 **JSON 스펙**을 내고 → builder가 **`python scripts/build_report.py _workspace/{slug}/02_spec.json -o _workspace/{slug}/03_draft.html`** 실행 + 자유서술(prose) 슬롯만 채움. 구조·스타일·정합(월별 합계·IA 1노드=1행·콜그룹·팔레트)은 **코드가 보장**. **폴백(LLM 전체 HTML)**: build_report가 못 다루는 커스텀 섹션이 많을 때만 builder.md의 수기 렌더 규칙으로.
- **★ 출력 위치 고정(흩어짐 금지)**: 모든 입출력 경로는 **harness 폴더 기준**으로 항상 적는다 — 중간물 `_workspace/{slug}/`, 최종 `output/{NN}_{주제}_vX.Y.html`. **temp·홈 디렉토리·cwd 임의 경로 금지**(산출물이 흩어지면 KB 누적·추적·스냅샷이 깨진다). build_report는 `-o`가 `_workspace/`·`output/` 밖이면 `[WARN]`을 낸다 → 그 경고가 보이면 경로를 바로잡고 재실행. 명령 실행 디렉토리는 harness 루트로 고정.
- **2a∥2b 병렬**(사이트 있을 때): site-analyst 크롤 ∥ analyst 요건분석 → 병합해 `01` 확정. 사이트 없으면 2a 스킵.
- **3a∥3b 병렬**: 둘 다 01만 소비. solution-architect는 `02b_solution.json`(infra/concept 섹션)을 내고 → **architect가 `02_spec.json`의 §4 위치로 합류** → builder는 합쳐진 `02_spec.json` 하나만 소비. **★ 3b는 infra/concept가 스코프일 때만 스폰**(인프라 구축/구성도·생태계 도식 불요 단순건은 3a만, opus 1회 절감). 3b 스킵 시 architect가 §4를 생략하거나 텍스트로 처리.
- **★ 중간물 스냅샷(KB 이력) — 기본 GATE 1회 + 최종 save**: 최종 `save`가 `_workspace/{slug}` 전체를 `deliverables/{id}/workspace/`로 미러하므로 **KB 최종 상태는 단계별 스냅샷 없이도 동일**하다. 따라서 기본은 **GATE 승인 시점에 1회** `python scripts/corpus.py snapshot --id {id} --ws {ws} --stage gate` + 최종 save만(git commit/push I/O·시간 절감). **단계별 스냅샷(`01_analyst`·`02_spec`·`03_draft`)은 옵션** — 장시간·고위험 실행에서 중간 크래시 대비가 필요할 때만 켠다. index는 불변(검색 노이즈 0). push 실패해도 로컬 누적 → 최종 save 때 함께 올라감.
- **★ 페르소나 검토 2지점(생성-검증의 '판단' 측)**: qa(규칙·정합)가 못 보는 **설득력·현실성·고객 수용성**을 멀티 페르소나(PM·아키텍트·개발·디자인/퍼블·고객)로 비판.
  - **3c (GATE 전, 항상)**: architect 산정 직후 `persona-review --mode estimate`로 공수·인사이트·AS-IS/TO-BE 근거·자료반영 **+ 콘텐츠 발전도(RFP 나열↔고도화)**를 검토 → 결과(`02c`)를 **GATE에서 사용자에게 함께 제시**. **비싼 builder 렌더 전 방향 교정**(여기가 깊이/발전도 검토의 정위치 — 렌더 전이라 가장 쌈). P0면 architect/analyst 반려 후 재산정·재작성.
  - **5b (최종 전, ★ 조건부)**: 평시엔 **skip**(콘텐츠는 3c에서 검토됐고 build_report가 spec을 결정적 렌더). 다음일 때만 `persona-review --mode final` 실행: ① 3c P0/P1 보완이 콘텐츠를 실질 변경 ② builder 폴백(수기 렌더) ③ 대형·고위험·고객 직제출로 사용자가 최종 확인 요청. 실행 시 P0면 builder 반려. 통과(또는 skip) 후 Phase 6.
- **모델 티어링 + 비용 규율**: 추론(analyst·architect·solution-architect·persona-review)=opus / 기계적(site-analyst·builder·qa)=sonnet. 각 스폰 시 해당 .md의 "참조 파일"만 첨부. **★ opus는 필요할 때만 스폰**: 3b는 infra/concept 스코프일 때만, 5b는 위 조건부. **평시 opus 호출 = 3회**(analyst·architect·persona-review estimate), 인프라 있으면 +1(3b), 최종 재검토 트리거 시 +1(5b). 콘텐츠 깊이 1차 탐지는 qa(r)(sonnet)가 값싸게 거르고 판단만 3c(opus)가 한다.

## Phase 7: 수정 피드백 → 오너용 제안 (feedback-curator, on-demand)
- **에이전트 수정 권한은 오너 단독.** 이 단계는 자동 반영이 아니라 **오너가 판단하도록 "수정 제안 리포트"를 만들어 공유**하는 것.
- 산출물이 방향과 안 맞아 **사용자가 대화로 고치고 "이대로 확정"** 하거나 "수정 피드백/피드백 문서 작성해줘"라고 하면 `feedback-curator` 호출.
- **★ 다건이면 먼저 열거→선택**: 한 세션엔 보통 수정이 여러 건 → **이번 대화의 수정들을 번호 리스트(1·2·3)로 제시하고 "어느 것에 대한 피드백?"**을 물어 고르게 한다(복수·전체 가능). 1건뿐이거나 사용자가 "N번"으로 특정하면 생략. 그다음 선택분에 대해 **수정 제안 리포트**(무엇이 어긋났나 · 원하는 방향 · 일반화 규칙 · 성격[객관개선/취향] · 어디를 어떻게 고치면 · 영향범위)를 **담당자 전달용**으로 보여주고, `corpus.py propose`로 `feedback/proposals.md`(검토 큐)에 누적.
- **오너가 "이건 반영하자"고 하면 그때 `/harness`(또는 오너 직접 편집)로 에이전트 수정.** feedback-curator는 절대 에이전트를 직접 고치지 않는다. 일회성("이번만")은 기록 안 함.

## Phase 6: corpus 환원 (qa PASS 후 자동)
- 최종본을 `output/`에 저장 후 → `python scripts/corpus.py save --html output/{...}.html --meta {ws}/05_meta.json --ws {ws}`. qa PASS가 push 게이트. push 실패해도 output/은 안전 — 보고에 명시.
- **★ 05_meta.json은 "리치 메타"여야 한다(save가 이걸로 섹션 원자를 생성)**: 기본 식별·공수 필드 + **섹션 콘텐츠 필드**를 담는다. 환원 직전 오케스트레이터가 `01_analysis`·`02_spec`·`02b_solution`·`02c/04b`에서 모아 조립:
  - 식별: `id·topic·client·doc_type·domain·project_case·tags`
  - 공수: `total_mm·months·headcount·role_breakdown·design_level·staffing·confidence`
  - 섹션: `overview·direction·ia_summary·approach[]·scope_in·scope_out·data_gaps·questions[]·infra·decisions{intent,decisions[[단계,변경,의도]],reuse[]}`
  - `save`는 있는 섹션 필드마다 원자(estimates·scope·questions·ia·approach·direction·overview·infra·decision)를 만들고 **원자별로 1커밋**한다.

## ★ 커밋/푸시 포인트 (corpus — 한 번에 통 커밋 금지, 원자 단위)
검색(`git log --grep`)·되돌리기·blame이 정밀하도록 **포인트를 고정**한다. 커밋 메시지 = `kb({type}): {id} | {고객} | {케이스} | {요약}`(git 검색키). 푸시는 각 포인트에서 1회.
| 포인트 | 시점 | 동작 | 커밋 |
|--------|------|------|------|
| **스냅샷** | GATE 승인 직후(장시간·고위험만, 평시 생략) | `corpus.py snapshot --stage gate` (workspace 미러) | `kb(snapshot): {id} [gate]` 1커밋+push |
| **★ HTML 버전** | **최종 HTML 최초 작성·수정(in-place)할 때마다** | `corpus.py put-html --id {id} --html output/{..}.html --note "{사유}"` | `kb(report): {id} | {사유}` 1커밋 + 태그 `kb/{id}` 이동 + push |
| **환원(필수)** | qa PASS 후 | `corpus.py save` → **섹션 원자별 N커밋** + `kb(report)` 1커밋 + 태그 `kb/{id}` | 원자 N + report 1, 묶어서 1 push |
| **피드백(공수)** | 실제 공수 확인 시 | `corpus.py feedback --actual N --lesson ..` | `kb(feedback): {id} | actual=N` 1커밋+push |
| **★ 수정 제안** | 사용자가 대화로 고치고 "이대로 확정" | `feedback-curator` → `corpus.py propose --note ..`(오너 검토 큐, 자동수정 X) | `kb(propose): ..` 1커밋+push |
| **조회** | 사용자 "최신 HTML 보자"(다중 사용자) | `corpus.py get --id {id} [--out 경로] [--rev 태그/해시]` → git에서 **최신본 받아** 열람·버전 이력 출력 | (읽기, 커밋 없음) |
- **★ 버전 관리**: 한 산출물의 버전 = **git 히스토리**(`git log -- deliverables/{id}/report.html` = 전 버전). **최신 = `kb/{id}` 태그(매 커밋 이동)**, 과거 버전 = `get --rev {해시/태그}`. 여러 사람이 작업하므로 **읽기·수정 전 `pull`**(get/put-html이 자동 pull), index.jsonl은 같은 id면 교체(중복 방지).
- **★ "최신 보자" 요청 = 로컬 캐시 말고 git에서**: `corpus.py get`으로 받아 보여준다(딴 사람이 갱신했을 수 있음).
- 도구 코드(에이전트·스크립트) 변경은 **`etribe` 브랜치**에 별도 커밋(데이터=corpus 브랜치와 분리). 한 변경=한 커밋, 메시지에 사유.
- **중간 단계마다 push 남발 금지** — 위 포인트가 전부. 단계 산출물은 `_workspace/`에 로컬 보존되다가 환원 때 함께 올라감.

## ★ 파일 네이밍 표준 (정본 — 모든 에이전트가 이 표를 따른다)
**경로 = 항상 `_workspace/{slug}/NN[x]_{artifact}.{ext}`.** bare `_workspace/파일` 금지(슬러그 없이 만들면 다른 프로젝트와 충돌). `NN`=2자리 단계번호, 병렬 분기는 접미 알파벳(01a·02b). 역할명은 파일명에 넣지 않음(단계번호가 역할을 함의). 종류는 확장자로 구분. 사람용 보조본은 같은 stem + `.md`.

| 순번 | 에이전트 | 파일 | 비고 |
|------|---------|------|------|
| 01a | site-analyst | `01a_site-ia.md` + `01a_site-ia.json` | 사이트 URL 있을 때만 |
| 01 | analyst | `01_analysis.md` | 요건+사이트 병합 분석 |
| 02 | architect | `02_spec.json` (+ `02_spec.md`) | build_report 스키마(SSOT). 02b를 §4로 합류 |
| 02b | solution-architect | `02b_solution.json` (+ `02b_solution.md`) | infra/concept 섹션 객체 |
| 02c | persona-review (estimate) | `02c_persona_review.md` | GATE 전 다관점 검토(공수·인사이트) |
| 03 | builder | `03_draft.html` | build_report 렌더 결과 |
| 04 | qa | `04_qa.md` | 검수 리포트 |
| 04b | persona-review (final) | `04b_persona_review.md` | 최종 전 다관점 검토(콘텐츠) |
| 05 | (환원) | `05_meta.json` | corpus save용 메타 |

- **KB 보존(섹션 원자 구조)**: corpus 루트에 **섹션 원자**(`estimates/{id}.md`·`scope/`·`questions/`·`ia/`·`approach/`·`direction/`·`overview/`·`infra/`·`dev-notes/decisions/`) + **케이스 종합**(`cases/{유형}.md`) + **패턴**(`patterns/`) + 원본(`deliverables/{id}/report.html` + `workspace/` 미러) + `index.jsonl`. **`id == slug`**. (옛 `meta.md` 단일 덩어리는 폐기 — 원자로 대체.)
- 최종 산출물(works 폴더 출력)만 별도 규칙: `{NN}_{주제}_v{X.Y}.html`(사용자 산출물 표기).

## 데이터 전달 프로토콜
- **파일 기반**(주): 위 "파일 네이밍 표준" 표를 따른다. 프로젝트별 `_workspace/{slug}/` 폴더로 격리(교차 덮어쓰기 방지). 중간본 보존.
- 최종 HTML만 사용자 지정 경로(보통 해당 프로젝트 works 폴더)에 출력.
- 서브에이전트 모드이므로 결과는 메인에게 반환 → 메인이 다음 단계로 전달.

## 에러 핸들링
- 단계 실패 1회 재시도. 재실패 시 해당 산출물 없이 진행하되 최종 보고에 **누락 명시**.
- 사이트 접근 차단 → analyst가 접근 가능 범위만 추출 + 미접근 영역 명시(임의 추정 금지).
- 산정 충돌(필요>가용) → 숨기지 말고 표면화 + 완화안 병기.
- qa 2라운드 후 잔여 불일치 → 보고서 명시 + 사용자 에스컬레이션. 상충 데이터 삭제 금지(출처 병기).

## 테스트 시나리오
**정상 흐름**: "이 사이트(URL) 리뉴얼 공수 HTML 만들어줘"
→ analyst가 IA 3뎁스+ 추출·API/관리자 유추 → architect SSOT 산정 → builder 하우스 스타일 렌더 → qa 정합성 PASS → 최종 HTML 출력.

**에러 흐름**: 기존 사이트가 로그인 차단
→ analyst 접근 범위만 추출 + 미접근 영역 플래그 → architect 추정 공수로 처리(노트에 불확실성) → builder 생성 → qa는 표 산술만 검증 가능(추정 영역은 통과 처리) → 보고서에 "미접근/추정" 명시.

**부분 수정 흐름**: "퍼블 마지막달 0.5→1로"
→ Phase 0이 부분 재실행 판별 → architect SSOT 1셀 변경·파생 재계산 → builder 해당 수치 등장 위치 전부 Edit → qa가 consistency-checklist로 9+곳 일치 확인.
