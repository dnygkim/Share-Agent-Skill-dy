# proposal — 제안서 작성 7단계 에이전트 (proposal agent_dykim)

IT 서비스 · 플랫폼 사업의 RFP · 과업지시서 · 회의록을 넣으면 RFP 분석 보고서 → 컨셉 · 목차 → 제안서 덱 → 차수별 변경분 HTML → 제출본(PDF · HTML · PPT)까지 7단계로 만드는 제안서 작성 하네스

## 한눈에 보기

| <div align="center"><sub>항목</sub></div> | <sub>내용</sub> |
|:---|:---:|
| <sub>목적</sub> | <sub>RFP를 받은 날부터 제출일까지 제안서 작업 전 과정을 7단계로 나눠 Claude와 진행. 사용자 몫 = 자료 전달 · 요청 한 줄 · **승인 3회**(컨셉 · 목차 · 피드백 반영 계획), 분석 · 작성 · 점검 = Claude 몫</sub> |
| <sub>대상</sub> | <sub>IT 서비스 · 플랫폼 구축/운영 사업의 제안서(슬라이드 덱). 골격 2종 = 경쟁입찰형(기본 · 컨셉과 스토리 중심) · 견적형(공수 · 범위 중심 10섹션)</sub> |
| <sub>이럴 때 사용</sub> | <sub>RFP를 받아 처음부터 제안서 작성 · RFP 분석 보고서만 먼저 필요 · 임원 보고 피드백 반영 · 제출 직전 PDF · PPT · 발표용 파일 추출 · 표지나 특정 장 · 문장 하나만 수정</sub> |
| <sub>넣는 것</sub> | <sub>RFP · 과업지시서 · 기능목록 · 구성도 · 기존 제안서 · 회의록 → `input/YYMMDD. [제안] {사업명}/`. 사이트 주소는 대화로, 임원 보고 회의록(md · pdf · docx)은 그 폴더의 `feedback/r{n}/`</sub> |
| <sub>나오는 것</sub> | <sub>RFP 분석 보고서 HTML · 제안서 덱 HTML(필요 시 PPT · Figma) · 변경분 HTML 간략본(2차 추출부터) · 제출본 v1.0(PDF · HTML · PPT) → `output/output-{프로젝트 폴더}/`. 단계별 중간물 md → `_workspace/{프로젝트}/`. 파일명 = `업무명-문서명-버전-작성일자`</sub> |
| <sub>시작 방법</sub> | <sub>`agent/proposal/` 폴더에서 Claude Code 실행 → `CLAUDE.md` 자동 로딩 → `이 RFP로 제안서 만들어줘`</sub> |
| <sub>연계</sub> | <sub>단계별 스킬 4종 호출(`rfp-analysis-research` · `ux-journey-insight` · `proposal-structure-validation` · `proposal-slide-builder`). 견적(M/M)은 자매 하네스 [`harness_st-etribe`](../harness_st-etribe/) 담당, 공수 · 일정 수치는 그 산출물이 정본. HTML 스타일 정본 = 리포 `global-house-style/house-style.css`. PPT = `pptx` 스킬(최종본은 `deckslide-design-guideline` 규격)</sub> |

## 이렇게 요청

| <div align="center"><sub>상황</sub></div> | <sub>요청 예시</sub> | <sub>나오는 것</sub> |
|:---|:---:|:---:|
| <sub>RFP를 받아 처음부터</sub> | <sub>`이 RFP로 제안서 만들어줘`</sub> | <sub>①부터 순서대로 · 분석 보고서 → 컨셉 → 목차 → 덱 v0.1</sub> |
| <sub>분석 보고서만 먼저</sub> | <sub>`RFP 분석 보고서만 뽑아줘`</sub> | <sub>①만 · 분석 보고서 HTML · `01_rfp.md`</sub> |
| <sub>임원 보고 뒤 피드백 반영</sub> | <sub>`임원 보고 회의록이야, 반영해줘`</sub> | <sub>⑤ 피드백 대장 → 승인 → ⑥ 덱 v0.n + 변경분 HTML (차수 +1)</sub> |
| <sub>장표 · 문구 지정 수정</sub> | <sub>`A07 헤드라인을 이 문장으로 바꿔줘`</sub> | <sub>지정한 곳만 수정 · 대장 생략 · `diff_deck.pl`로 수정 범위 확인</sub> |
| <sub>장표 하나만 새로</sub> | <sub>`표지 슬라이드만 만들어줘`</sub> | <sub>slide-builder 단독 실행 · 해당 장표만</sub> |
| <sub>제출 직전</sub> | <sub>`제출용 PDF랑 발표용 뽑아줘`</sub> | <sub>⑦ 제출본 v1.0 · 발표용 파생본 · 제출 전 점검표</sub> |

- `컨셉 잡아줘` · `목차 짜줘`처럼 중간 단계부터 요청 가능. `_workspace/{프로젝트}/` 상태로 시작 단계 판정(「단계별 상세 · 시작 단계 판정」), 앞 단계 산출물이 없으면 빠진 단계부터 안내
- 착수부터 제출까지의 실제 대화 흐름은 「예시 대화」

## 진행 단계

```
① RFP 분석 · 리서치 → ② 컨셉 · 스토리 [GATE ①] → ③ 목차 [GATE ②] → ④ 1차 추출 → ⑤ 피드백 대장 [GATE ③] → ⑥ n차 추출 + 변경분 HTML → ⑦ 최종본
```

- ⑤–⑥은 차수마다 반복, ④ ⑥ ⑦ 추출마다 qa 검수
- ①–⑦ = 정본 `ORCHESTRATOR.md`의 S1–S7. 단계 · 파일명 · GATE가 이 README와 어긋나면 `ORCHESTRATOR.md` 우선

| <div align="center"><sub>단계</sub></div> | <sub>하는 일</sub> | <sub>사용자 할 일</sub> | <sub>결과물</sub> |
|:---|:---:|:---:|:---:|
| <sub>① RFP 분석 · 리서치 (S1)</sub> | <sub>요구사항 · 평가 항목 · 배점 · 제출 조건 정리, 산업 · 경쟁사 · 동종/유사 업계 조사, 제안 키워드 5–7개 · 방향성 후보 2–3안 도출</sub> | <sub>자료 제공 · 인테이크 답변</sub> | <sub>분석 보고서 HTML · `01_rfp.md` (+ 선택 `01_ux.md`)</sub> |
| <sub>② 컨셉 · 스토리 (S2) **GATE ①**</sub> | <sub>고객 과제 3–5개 → 컨셉 후보 2–3안 → 추천안 스토리 9단계 · 표지 · 2장 · 맺음 거버닝 후보</sub> | <sub>**컨셉 선택 · 수정 · 승인** (승인 전 목차 작업 보류)</sub> | <sub>`02_concept.md`</sub> |
| <sub>③ 목차 (S3) **GATE ②**</sub> | <sub>행 = 장표 1장인 목차, 장표마다 주요 삽입내용 · 근거 · 필요한 레퍼런스 · RFP 요구 항목 대응, 확정 장수</sub> | <sub>**목차 · 분량(본문 · 별첨 · 발표 범위) 승인** (승인 전 본문 작업 보류)</sub> | <sub>`03_structure.md`</sub> |
| <sub>④ 초안 · 1차 추출 (S4)</sub> | <sub>추출 전 확인(양식 · 제출 포맷 · 작업 사이즈 · 볼륨 · 레퍼런스) → 콘텐츠 초안 → HTML → PPT/Figma 변환 또는 HTML 최종본 취합 → qa</sub> | <sub>양식 파일 · 레퍼런스 전달, 콘텐츠 초안 확정</sub> | <sub>덱 v0.1 · `04_content.md` · `04_refs.md` · `r1/qa.md`</sub> |
| <sub>⑤ 피드백 대장 (S5) **GATE ③**</sub> | <sub>회의록을 발언 단위로 나눠 대상 장표 · 유형 · 처리 방안 기록, 상충 · 상위 변경 · 분량 증감 표시</sub> | <sub>회의록 파일 전달 · 「확인 필요」 「상충」 답변 · **반영 계획 승인** (승인 전 덱 수정 보류)</sub> | <sub>`r{n}/05_feedback.md`</sub> |
| <sub>⑥ n차 추출 + 변경분 HTML (S6)</sub> | <sub>대장의 「반영」 항목만 고친 새 버전(+0.1) → `diff_deck.pl` 비교 · 대장 대조 → 변경분 HTML 간략본 → qa</sub> | <sub>새 덱 · 변경분 검토 (추가 피드백이면 ⑤로)</sub> | <sub>덱 v0.n · 변경분 HTML · `r{n}/06_changes.md` · `r{n}/qa.md`</sub> |
| <sub>⑦ 최종본 (S7)</sub> | <sub>제출 조건 확인 → 대상 버전 동결 → 포맷별 추출(PDF · HTML · PPT) → 제출 전 점검표 → qa</sub> | <sub>제출 조건 답변 · 실제 제출 · 발송</sub> | <sub>제출본 v1.0(`submit/`) · `07_release.md`</sub> |

**공통 진행 규칙**

- 견적형 골격: ② 컨셉을 「제안 방향 3가지」 한 쪽으로 축소, GATE ①을 GATE ②와 함께 승인
- 단계마다 착수 직전 입력 경로 · 저장 경로 기본값 제시. 사용자가 다른 경로를 지정하면 그 경로가 정본
- 착수 · 완료 때 현재 시각 한 줄(`현재 HH시 MM분입니다. 작업 시작합니다.`), HTML 산출 완료 보고에 내부망 짧은 주소 동봉
- 질문 · GATE 직전 Dan Jr.(`persona.md`) 등급 조회: A 기본값으로 진행 · B 진행 후 완료 보고에 표기 · C 질문. GATE ①②③은 persona.md 밖의 결정이라 항상 사용자 승인

**인테이크 질문** (착수 직전 · 한 번에 하나씩)

| <div align="center"><sub>질문</sub></div> | <sub>답 예시</sub> | <sub>기본값</sub> |
|:---|:---:|:---:|
| <sub>① 클라이언트명 · 사업명 · 업무명(파일명 앞머리)</sub> | <sub>`ACME보험운영제안`</sub> | <sub>자료에서 추출해 확인만. 처음 쓰는 업무명은 반드시 확인</sub> |
| <sub>② 입력 자료 정본</sub> | <sub>「RFP.pdf가 정본, 기능목록은 참고」</sub> | <sub>폴더의 자료 목록 제시 후 확인</sub> |
| <sub>③ 골격</sub> | <sub>「경쟁입찰」 · 「견적형」</sub> | <sub>경쟁입찰형 (RFP에 평가 항목 · 배점 · 발표가 있으면 경쟁입찰형으로 보고 확인만)</sub> |
| <sub>④ HTML 스타일 (고객사 CI)</sub> | <sub>「네」 · 「이 색으로」 · 「기본으로」</sub> | <sub>고객사 로고 Primary 컬러 적용. 대표 사이트 · 로고 확인 → 미확인 · 후보 복수면 먼저 질문 → Primary 실측 → 「CI Primary `#HEX`(출처)로 추출할까요?」 한 줄 확인</sub> |
| <sub>⑤ 대상 범위 · 제출 기한</sub> | <sub>「전체 · 11/30 제출」</sub> | <sub>전체. 선택 장(회사소개 · 수행실적 · 유지보수) 포함 여부와 단일안 · 복수안(1안/2안)도 함께 확인</sub> |

- 요청 문장에 답이 있으면 재질문 생략 · 한꺼번에 답하면 남은 것만 질문 · 「알아서」면 표준 가정으로 진행
- 제출 포맷 · 기본양식 · 작업 사이즈 · 분량은 인테이크 제외 항목. 분량은 GATE ②, 나머지는 ④ 착수 때 「추출 전 확인」에서 확정

## 산출물

| <div align="center"><sub>파일</sub></div> | <sub>형식</sub> | <sub>위치</sub> | <sub>내용</sub> |
|:---|:---:|:---:|:---:|
| <sub>`{업무명}-RFP분석리서치보고서-v0.1-YYYYMMDD.html`</sub> | <sub>HTML 문서형 · 고객사 CI</sub> | <sub>`output/output-{프로젝트 폴더}/`</sub> | <sub>① 분석 보고서. PART Ⅰ RFP 분석 · Ⅱ 현황 · 시장 · Ⅲ 중점 과제 심층 · Ⅳ 제안 전략 · 실행 초안, 그래프와 같은 수치 표</sub> |
| <sub>`{업무명}-제안서-v0.x-YYYYMMDD.html`</sub> | <sub>HTML 덱 (+ pptx · Figma)</sub> | <sub>같은 폴더 · 직전 버전은 `old/`</sub> | <sub>④ ⑥ 제안서 덱. 작업 사이즈는 ④ 착수 때 확정(양식 규격 또는 1280×720 · 1600×900 등)</sub> |
| <sub>`{업무명}-제안서변경분({n}차)-v0.1-YYYYMMDD.html`</sub> | <sub>HTML 문서형 · 고객사 CI</sub> | <sub>같은 폴더</sub> | <sub>⑥ 변경분 간략본. 요약 스탯 · 목차별 변경 · 헤드라인 변경 · 신규/삭제/이동 · 미반영/보류 · 분량, 2차 추출부터 덱과 한 쌍</sub> |
| <sub>`{업무명}-제안서-v1.0-YYYYMMDD.pdf` · `.html` · `.pptx`</sub> | <sub>PDF · HTML · PPT</sub> | <sub>같은 폴더의 `submit/`</sub> | <sub>⑦ 제출본 · 발표용 파생본. 파일명은 RFP 지정 > 사용자 지정 > 이 규칙 순</sub> |
| <sub>`01_rfp.md` · `01_ux.md`(선택)</sub> | <sub>md</sub> | <sub>`_workspace/{프로젝트}/`</sub> | <sub>요건 구조화 · 리서치 · 제안 키워드 · 방향성 후보 / 여정 · IA 인사이트</sub> |
| <sub>`02_concept.md`</sub> | <sub>md</sub> | <sub>같은 폴더</sub> | <sub>과제 · 컨셉 · 스토리 흐름 · 거버닝 후보</sub> |
| <sub>`03_structure.md`</sub> | <sub>md</sub> | <sub>같은 폴더</sub> | <sub>목차 · 페이지별 삽입내용 · 확정 장수</sub> |
| <sub>`04_content.md` · `04_refs.md`</sub> | <sub>md</sub> | <sub>같은 폴더</sub> | <sub>장표별 콘텐츠 초안(항상 최신 덱과 같은 내용) · 레퍼런스 대장</sub> |
| <sub>`r{n}/05_feedback.md`</sub> | <sub>md</sub> | <sub>`_workspace/{프로젝트}/r{n}/`</sub> | <sub>n차 추출용 피드백 대장</sub> |
| <sub>`r{n}/06_changes.md` · `.json`</sub> | <sub>md · json</sub> | <sub>같은 폴더</sub> | <sub>직전 대비 변경분 데이터(`diff_deck.pl` 출력)</sub> |
| <sub>`r{n}/qa.md`</sub> | <sub>md</sub> | <sub>같은 폴더</sub> | <sub>검수 리포트(`r1` = 1차 추출)</sub> |
| <sub>`07_release.md`</sub> | <sub>md</sub> | <sub>`_workspace/{프로젝트}/`</sub> | <sub>제출 조건 · 점검표 결과 · 파일 목록</sub> |

예시 (가상 사업 「ACME보험 홈페이지 운영」)

```
output/output-261110. [제안] ACME보험 홈페이지 운영/
├── ACME보험운영제안-RFP분석리서치보고서-v0.1-20261110.html   ← ① 분석 보고서
├── ACME보험운영제안-제안서-v0.2-20261120.html               ← 최신 덱 (2차 추출)
├── ACME보험운영제안-제안서변경분(2차)-v0.1-20261120.html     ← 변경분 간략본
├── old/ACME보험운영제안-제안서-v0.1-20261117.html           ← 직전 버전 (비교 기준)
└── submit/                                                 ← 제출본 v1.0 (PDF · HTML · PPT)

_workspace/ACME보험-홈페이지운영/
├── 01_rfp.md · 02_concept.md · 03_structure.md · 04_content.md · 04_refs.md
├── r1/qa.md
├── r2/05_feedback.md · 06_changes.md · 06_changes.json · qa.md
└── 07_release.md
```

- `{프로젝트 폴더}` = `YYMMDD. [제안] {사업명}`(드라이브 폴더명과 같게) · `{프로젝트}` = `{클라이언트}-{주제}`(공백 없이)
- 파일명 = `업무명-문서명-버전-작성일자`. 「최종 · 수정본」 같은 접미사 금지. 분석 보고서 문서명은 그 프로젝트에서 이미 확정한 이름이 있으면 그 이름(예 `RFP요약`)
- HTML 산출물(분석 보고서 · 덱 · 변경분)은 자기완결 단일 파일 · 고객사 로고 Primary 컬러 기본 적용 · 저장할 때마다 `<head>` 수정 이력 메타 한 줄
- 같은 파일을 드라이브 `02. Work` 산출물 경로에도 보관
- 부산물 폴더: `old/`(직전 버전 · `_prev.html` · 분리 보관 장표) · `refs/`(수집 이미지) · `render/`(검수 PNG) · `toc/`(목차 시트 매핑) · `submit/`(제출본) · `research/`(리서치 노트)
- 중간물(`_workspace/`)은 지우지 않고 유지. 파일 머리의 「상태: … / 승인(YYYY-MM-DD)」 줄이 다음 세션의 진행 단계 판정 근거

| <div align="center"><sub>시점</sub></div> | <sub>버전</sub> | <sub>비고</sub> |
|:---|:---:|:---:|
| <sub>1차 추출</sub> | <sub>v0.1</sub> | <sub>`r1/`</sub> |
| <sub>n차 추출 (피드백 반영)</sub> | <sub>직전 +0.1 (v0.8 초과 금지)</sub> | <sub>`r{n}/` · 변경분 HTML 동반 · 직전본은 `old/`</sub> |
| <sub>PM 검토 · 지적 반영 완료</sub> | <sub>v0.9</sub> | <sub>—</sub> |
| <sub>고객 제출본</sub> | <sub>v1.0</sub> | <sub>이후 덮어쓰기 금지, 수정은 새 버전 파일</sub> |

- 같은 차수 안의 오탈자 · 링크 수정은 파일명 · 버전을 유지한 제자리 갱신. 장표 코드는 차수가 바뀌어도 유지

## 준비 (처음 한 번)

| <div align="center"><sub>순서</sub></div> | <sub>할 일</sub> | <sub>비고</sub> |
|:---|:---:|:---:|
| <sub>①</sub> | <sub>Claude Code 설치</sub> | <sub>터미널(CLI) · 데스크톱 앱 · IDE 확장 중 편한 것</sub> |
| <sub>②</sub> | <sub>리포 받기 `git clone https://github.com/dnygkim/dykim-claude-agents-skills.git`</sub> | <sub>비공개 리포. 접근 권한 필요</sub> |
| <sub>③</sub> | <sub>리포 루트에서 `./sync-skills.ps1`(Windows) 또는 `bash ./sync-skills.sh`(macOS) 실행</sub> | <sub>스킬 정본(`skills/`)을 `agent/proposal/.claude/skills/`로 복사. 스킬이 갱신되면 다시 실행</sub> |
| <sub>④</sub> | <sub>perl 확인 `perl -v`</sub> | <sub>문체 점검 · 변경분 비교 스크립트용. Windows는 Git Bash에 포함, macOS는 기본 설치</sub> |
| <sub>⑤ (선택)</sub> | <sub>Python 3 설치</sub> | <sub>덱 편집 · 피그마 PDF 취합 · 목차 시트 등 보조 스크립트용. 패키지는 「의존성 · 알려진 제한」. 없어도 7단계 진행 가능</sub> |
| <sub>⑥ (선택)</sub> | <sub>Figma · Chrome 연결</sub> | <sub>Figma 양식 · 레퍼런스 확인, 사이트 캡처, PDF 렌더에 사용</sub> |

## 폴더 구성

```
agent/proposal/
├── CLAUDE.md            # 동작 규칙 · 인테이크 (이 폴더에서 Claude Code 실행 시 자동 로딩)
├── ORCHESTRATOR.md      # 7단계 파이프라인 정본 (단계 · GATE · 파일 네이밍 · 차수와 버전)
├── README.md            # 이 문서
├── agents/              # 역할 정의 9개
│   ├── rfp-analyst.md          # S1 RFP 분석 · 리서치 · 분석 보고서 HTML
│   ├── ux-strategist.md        # S1 선택 모듈 · 여정 · IA 분석
│   ├── concept-planner.md      # S2 컨셉 · 스토리 (GATE ①)
│   ├── structure-validator.md  # S3 목차 (GATE ②)
│   ├── reference-collector.md  # S4 삽입 콘텐츠 · 레퍼런스 수집
│   ├── slide-builder.md        # S4 · S6 덱 제작
│   ├── feedback-integrator.md  # S5 피드백 대장 (GATE ③) · S6 변경분 HTML
│   ├── release-packager.md     # S7 최종본 · 제출 포맷
│   └── qa.md                   # 추출마다 검수
├── references/
│   ├── writing-style.md            # 문체 공통지침
│   ├── slide-quality-bar.md        # 장표 품질 기준 (최종 제출본 학습)
│   ├── skeleton-bid.md             # 경쟁입찰형 골격 (기본)
│   ├── section-prompts.md          # 견적형 골격 (10섹션)
│   ├── design-system.md            # 레이아웃 패턴 · CI 변수 · 포맷별 렌더링
│   ├── rfp-report-format.md        # S1 분석 보고서 양식 · 고객사 CI · 구성 · 검수
│   └── deck-production-playbook.md # HTML 최종본 취합 · 편집 · 피그마 백업 · PDF 절차
├── template/
│   ├── base_template.html          # 1280×720 슬라이드 골격 (미리보기)
│   ├── deck_1600_template.html     # 1600×900 슬라이드 골격 (HTML 최종본)
│   ├── slide-tokens.css            # 덱 색 토큰 · [CI 오버라이드] 블록
│   └── rfp_report_template.html    # S1 분석 보고서 골격 (문서형 · PART 2단 LNB)
├── scripts/
│   ├── check_style.pl · diff_deck.pl · deck_lib.pl      # 문체 점검 · 변경분 비교 · 공용 함수 (perl)
│   ├── check_slides.py                                  # 잔존 표기 · 자리표시자 · 쪽 번호 점검
│   ├── deck_edit.py · codebox_overlay.py · fig2svg.py   # 덱 편집 · 코드박스 통일 · 피그마 벡터 취합
│   ├── deck_toc.py · build_compressed_pdf.py            # 목차 시트 · 피그마 PDF 병합 압축
│   └── render_pages.sh                                  # headless Chrome 페이지 렌더
├── examples/            # 과거 예시 + INDEX.md (톤 · 구성 · 분량 참고용)
├── .claude/skills/      # sync-skills 생성물 (깃 제외)
├── input/{프로젝트 폴더}/            # 입력 자료 · feedback/r{n}/ 회의록 (깃 제외)
├── _workspace/{프로젝트}/            # 중간물 (깃 제외)
└── output/output-{프로젝트 폴더}/    # 산출물 · old/ · submit/ (깃 제외)
```

이 하네스가 쓰는 스킬 4종(`rfp-analysis-research` · `ux-journey-insight` · `proposal-structure-validation` · `proposal-slide-builder`)의 정본은 리포 루트 `../../skills/`. `sync-skills` 실행 시 `skills/` 전체가 이 폴더 `.claude/skills/`로 복사돼 자동 로드. 리포 전체 개요는 루트 [README.md](../../README.md)

## 용어

| <div align="center"><sub>용어</sub></div> | <sub>뜻</sub> |
|:---|:---:|
| <sub>**하네스**</sub> | <sub>Claude가 정해진 순서와 규칙대로 일하도록 역할 정의 · 지침 · 도구를 묶어 둔 폴더. 이 폴더에서 Claude Code를 열면 규칙 자동 적용</sub> |
| <sub>**RFP**</sub> | <sub>제안요청서. 고객사가 사업 범위 · 요구사항 · 평가 기준 · 제출 조건을 적어 보낸 문서</sub> |
| <sub>**덱**</sub> | <sub>슬라이드로 된 제안서 한 벌. 이 하네스의 기본 작업 형식은 HTML 슬라이드</sub> |
| <sub>**장표**</sub> | <sub>슬라이드 한 장</sub> |
| <sub>**골격**</sub> | <sub>제안서의 기본 뼈대. **경쟁입찰형**(기본 · 컨셉과 스토리 중심 · `references/skeleton-bid.md`)과 **견적형**(공수 · 범위 중심 10섹션 · `references/section-prompts.md`) 2종</sub> |
| <sub>**컨셉**</sub> | <sub>제안 전체를 한 줄로 말한 문장. 표지에 놓이고 지향점 · 맺음 장에서 다시 등장</sub> |
| <sub>**거버닝 메시지**</sub> | <sub>장표 한 장의 결론을 한 줄로 세운 헤드라인. 제목만 읽어도 그 장의 주장이 전달되는 문장(20–40자)</sub> |
| <sub>**태그라인**</sub> | <sub>거버닝 메시지 위의 한 줄. 절 번호 + 무엇 · 범위 · 기준, 주장은 거버닝 메시지 몫</sub> |
| <sub>**장표 코드**</sub> | <sub>장표마다 붙는 고유 번호(`B02` · `A07`). 앞 글자 = 장(C 제안사 소개 · B 제안 개요 · A 상세 방안 · P 별첨, 선택 장 S · D 파트너 · 개발 · M 사업 관리). 차수가 바뀌어도 유지, 새 장표는 그 장에서 쓰지 않은 다음 번호</sub> |
| <sub>**GATE**</sub> | <sub>사용자 승인 지점. 승인 전에는 다음 단계로 넘어가지 않는 관문(① 컨셉 ② 목차 · 분량 ③ 피드백 반영 계획)</sub> |
| <sub>**차수**</sub> | <sub>추출 회차. 1차 추출 = `r1`, 피드백을 반영한 2차 추출 = `r2`. 차수마다 버전 +0.1</sub> |
| <sub>**피드백 대장**</sub> | <sub>회의록의 발언을 한 줄씩 나눠 대상 장표 · 처리 방안 · 결과를 적은 표</sub> |
| <sub>**변경분 간략본**</sub> | <sub>직전 버전과 달라진 곳을 목차 순서로 정리한 별도 HTML. 2차 추출부터 덱과 함께 제공</sub> |
| <sub>**HTML 최종본**</sub> | <sub>HTML 덱이 그대로 제출본인 제작 방식(주로 1600×900 골격 · PDF는 HTML에서 인쇄). 반대 = HTML 미리보기 + PPT/Figma 제출본</sub> |
| <sub>**qa**</sub> | <sub>단계가 아니라 추출마다(④ ⑥ ⑦) 붙는 검수</sub> |
| <sub>**기준 덱**</sub> | <sub>문체의 본보기로 삼는 실제 제출 제안서. 현재 = 메리츠화재 2027 운영 제안 발표본(2026.11.09)</sub> |

## 단계별 상세

### 전체 흐름

```
S1 분석 · 리서치 ─▶ S2 컨셉 · 스토리 ─[GATE ①]─▶ S3 목차 ─[GATE ②]─▶ S4 1차 추출 ─▶ 검수
                                                                           │
        ┌──────────────────────────────────────────────────────────────────┘
        ▼
S5 피드백 대장 ─[GATE ③]─▶ S6 n차 추출 + 변경분 HTML ─▶ 검수      (S5–S6 = 차수마다 반복)
                                        │
                                        ▼
                             S7 최종본 (PDF · HTML · PPT)
```

### 단계별 담당 · 스킬

| <div align="center"><sub>단계</sub></div> | <sub>에이전트</sub> | <sub>우선 스킬</sub> | <sub>모델 권장</sub> |
|:---|:---:|:---:|:---:|
| <sub>S1 RFP 분석 · 리서치</sub> | <sub>`rfp-analyst` (+ 선택 `ux-strategist`)</sub> | <sub>`rfp-analysis-research` (+ `ux-journey-insight`)</sub> | <sub>opus</sub> |
| <sub>S2 컨셉 · 스토리</sub> | <sub>`concept-planner`</sub> | <sub>— (에이전트 절차대로 직접 수행)</sub> | <sub>opus</sub> |
| <sub>S3 목차</sub> | <sub>`structure-validator`</sub> | <sub>`proposal-structure-validation`</sub> | <sub>opus</sub> |
| <sub>S4 1차 추출</sub> | <sub>`slide-builder` (+ `reference-collector`) → `qa`</sub> | <sub>`proposal-slide-builder`</sub> | <sub>sonnet</sub> |
| <sub>S5 피드백 대장</sub> | <sub>`feedback-integrator`</sub> | <sub>— (에이전트 절차대로 직접 수행)</sub> | <sub>opus</sub> |
| <sub>S6 n차 추출</sub> | <sub>`slide-builder` → `feedback-integrator` → `qa`</sub> | <sub>`proposal-slide-builder`</sub> | <sub>sonnet</sub> |
| <sub>S7 최종본</sub> | <sub>`release-packager` → `qa`</sub> | <sub>(`pptx` · `pdf`)</sub> | <sub>sonnet</sub> |

- 스킬이 없는 환경은 에이전트 문서의 폴백 절차로 진행 + 「스킬 미연결, 폴백 진행」 한 줄 보고
- 스킬 산출물에 이 하네스 서식(제안 키워드 · 페이지별 삽입내용 등)이 빠지면 에이전트 문서 기준으로 보충
- 각 에이전트는 자기 문서의 「참조 파일」만 읽는 구조

### 시작 단계 판정

중간 단계부터 시작해도 무방. Claude가 `_workspace/{프로젝트}/` 상태와 요청으로 시작 단계 판정

| <div align="center"><sub>작업 폴더 상태 · 요청</sub></div> | <sub>시작 단계</sub> |
|:---|:---:|
| <sub>빈 폴더</sub> | <sub>S1</sub> |
| <sub>`01_rfp.md`만 존재</sub> | <sub>S2 (컨셉)</sub> |
| <sub>`02_concept.md` 승인 완료</sub> | <sub>S3</sub> |
| <sub>`03_structure.md` 승인 완료</sub> | <sub>S4</sub> |
| <sub>기존 덱 + 회의록 · 피드백 제공</sub> | <sub>S5 → S6 (차수 +1)</sub> |
| <sub>기존 덱 + 「제출본 뽑아줘 · PDF로」</sub> | <sub>S7</sub> |
| <sub>기존 덱 + 장 · 문구 직접 지정</sub> | <sub>지정한 것만 수정(대장 생략) → 변경분 데이터로 범위 확인</sub> |
| <sub>특정 섹션 단독 요청(「표지만」)</sub> | <sub>slide-builder만</sub> |
| <sub>같은 프로젝트에 새 RFP · 범위 변경</sub> | <sub>기존 `_workspace/{프로젝트}/`를 `{프로젝트}_prev/`로 옮기고 S1</sub> |

- 앞 단계 산출물 없이 뒤 단계를 요청하면(컨셉 없이 「목차 짜줘」) 빠진 단계를 한 줄로 안내 → 그 단계를 짧게 먼저 할지, 사용자가 준 내용으로 대신할지 질문

### S1 RFP 분석 · 동종/유사 업계 리서치

- **필요한 이유**: 요구사항을 빠짐없이 파악하고 제안의 재료를 모으는 단계. 뒤 단계 전체의 근거
- **Claude가 하는 일**
  - RFP에서 요구사항 · 평가 항목 · 배점 · 제출 조건을 표로 정리
  - 산업 · 경쟁사 · 동종/유사 업계 사례 조사. RFP 원문과 입찰 조건은 검색어에 넣지 않는 원칙
  - 결과 머리에 **제안 주요 키워드 5–7개**와 **제안 방향성 후보 2–3안** 정리 (S2의 재료)
  - 착수 때 이트라이브 실적표와 고객사 수행 이력 대조(현 운영사 여부 포함) → 보고서 §0 핵심 판단 · PART Ⅳ 수행 이력에 반영
  - 구축 · 리뉴얼처럼 화면이 본론인 사업은 `ux-strategist`로 사용자 여정 · 메뉴 구조 분석 추가(`01_ux.md`). 운영 · 유지보수 사업은 생략
- **사용자 할 일**: 자료 제공 · 인테이크 답변. 대표 사이트 · 로고 질문이 오면 URL이나 로고 파일 전달
- **결과물**: 분석 보고서 HTML(`{업무명}-RFP분석리서치보고서-v0.1-YYYYMMDD.html`) · `01_rfp.md`
  - 보고서 양식 = 삼성자산운용 FunETF v0.3(2026.11.11) 기준. PART Ⅰ RFP 분석 · Ⅱ 현황 · 시장 · Ⅲ 중점 과제 심층 · Ⅳ 제안 전략 · 실행 초안, 발주 일정 D-day · 작업 간트 · 배점 · 시장 추이 · 로드맵 · 지면 배분 등 그래프와 같은 수치 표
  - 색은 고객사 로고의 Primary 컬러(토프바 · 강조선 · 반전 블록 · 강조 막대)와 흰색 로고. 정본 `references/rfp-report-format.md` · 골격 `template/rfp_report_template.html`
  - 출처와 본문 고유명사(사이트 · 서비스 · 기관 · 도구)에 외부링크(`a.ext`) 연결, 걸기 전 URL 열림 확인(`CLAUDE.md` 5a)

### S2 컨셉 · 스토리텔링 (GATE ①)

- **필요한 이유**: 경쟁입찰의 평가위원은 여러 제안서를 연달아 읽는 독자. 한 줄로 기억되는 컨셉과 표지에서 맺음까지 이어지는 이야기가 차이를 만드는 지점. 목차부터 짜면 요구 항목 나열로 끝나기 쉬운 구조
- **Claude가 하는 일**
  - 고객의 과제 3–5개 도출 (고객이 실제로 하는 말로 서술 · 근거 없는 과제 제외)
  - 컨셉 후보 2–3안 제시: 안마다 한 줄 문장 · 키워드 · 답하는 과제 · 증거 · 약점
  - 추천안으로 스토리 흐름 9단계 구성 + 표지 · 2장 · 맺음 거버닝 메시지 후보
- **사용자 할 일**: 컨셉 선택 · 수정 지시 · 승인. **승인 전 목차 작업 보류**. 사용자가 고친 컨셉 문장은 그대로 확정
- **결과물**: `02_concept.md` (과제 · 컨셉 · 스토리 흐름 · 거버닝 후보 · 평가자가 물을 질문과 답)

| <div align="center"><sub>순서</sub></div> | <sub>스토리 단계</sub> | <sub>답하는 질문</sub> | <sub>대응 장표</sub> |
|:---|:---:|:---:|:---:|
| <sub>①</sub> | <sub>컨셉</sub> | <sub>이 제안을 한 줄로 말하면</sub> | <sub>표지</sub> |
| <sub>②</sub> | <sub>자격</sub> | <sub>왜 이 회사가 말할 자격이 있는가</sub> | <sub>1장 제안사 소개</sub> |
| <sub>③</sub> | <sub>이해</sub> | <sub>고객의 사업 목표는 무엇인가</sub> | <sub>2장 사업 이해</sub> |
| <sub>④</sub> | <sub>과제</sub> | <sub>그 목표를 막는 것은 무엇인가</sub> | <sub>2장 AS-IS 과제</sub> |
| <sub>⑤</sub> | <sub>지향점</sub> | <sub>그래서 어떤 상태로 바꾸는가</sub> | <sub>2장 지향점</sub> |
| <sub>⑥</sub> | <sub>전략</sub> | <sub>과제마다 무엇을 하는가</sub> | <sub>2장 전략 체계</sub> |
| <sub>⑦</sub> | <sub>지표</sub> | <sub>달라진 것을 무엇으로 재는가</sub> | <sub>2장 목표 지표</sub> |
| <sub>⑧</sub> | <sub>증명</sub> | <sub>실제로 어떻게 수행하는가</sub> | <sub>3장 상세 방안</sub> |
| <sub>⑨</sub> | <sub>맺음</sub> | <sub>컨셉을 한 번 더</sub> | <sub>맺음</sub> |

> 견적형 골격은 이 단계를 「제안 방향 3가지」 한 쪽으로 줄이고 GATE ①을 GATE ②와 함께 진행

### S3 목차 (GATE ②)

- **필요한 이유**: 본문을 만들기 전에 「몇 쪽에 무엇이 들어가는지」를 합의하는 단계. 장표를 만든 뒤 구조를 바꾸면 재작업 비용이 큰 구간
- **Claude가 하는 일**
  - 컨셉 · 스토리를 장으로 분해. **표의 한 행 = 장표 1장**. RFP가 목차를 지정했으면 그 순서와 제목 우선
  - 행마다 코드 · 장/절 · 태그라인 · 거버닝 메시지(안) · **주요 삽입내용** · 근거/출처 · 필요한 레퍼런스 · 대응하는 RFP 요구 항목 기재. 모르는 칸은 비우지 않고 「확인 필요」
  - RFP 요구 항목이 빠짐없이 장표에 대응하는지 검증 + **확정 장수**(본문 · 별첨 · 발표 범위) 제시
  - 분량 기준: RFP 쪽수 제한이 상한(표지 · 목차 · 간지 · 별첨 포함 여부는 RFP 문구로 확인), 제한이 없으면 본문 30–40장 기본 제시, 발표 시간이 정해지면 장당 40–60초로 역산
- **사용자 할 일**: 목차와 분량 승인. **승인 전 본문 작업 보류**
- **결과물**: `03_structure.md`

목차 표 한 행 예시

| <div align="center"><sub>코드</sub></div> | <sub>장 · 절</sub> | <sub>거버닝 메시지(안)</sub> | <sub>주요 삽입내용</sub> | <sub>필요한 레퍼런스</sub> |
|:---|:---:|:---:|:---:|:---:|
| <sub>B02</sub> | <sub>2. 제안 개요 · 2.2 AS-IS 운영 과제</sub> | <sub>요청마다 처리 방식이 달라지는 운영</sub> | <sub>과제 4개 카드(고객의 말 1줄 + 근거 2줄 + 필요한 것) · 요청 처리 건수 표</sub> | <sub>현행 요청 접수 화면 캡처</sub> |

### S4 초안 · 1차 추출

- **필요한 이유**: 승인된 목차를 실제 장표로 만드는 단계. 만들기 전에 양식과 분량을 다시 확인해 재작업 방지
- **진행 순서** (순서 고정)

| <div align="center"><sub>순서</sub></div> | <sub>확인 · 작업</sub> | <sub>내용</sub> |
|:---|:---:|:---:|
| <sub>ⓐ</sub> | <sub>기본양식 확인</sub> | <sub>Figma · PPT 양식 파일 유무 확인 → 있으면 열어서 프레임 크기 · 콘텐츠 영역 · 헤더 구조 · 장표 코드 체계 파악. 이어서 제출 포맷(HTML 최종본 / HTML 미리보기 + PPT · Figma 제출본)과 작업 사이즈(양식 규격, 없으면 1280×720 · 1600×900 · 1920×1080 · pptx 16:9 · A4 가로 중 확인) 확정. 포맷 답이 없으면 PPT/Figma 제출본으로 가정하고 안내, 사이즈 확정 전 골격 제작 보류</sub> |
| <sub>ⓑ</sub> | <sub>전체 볼륨 확인</sub> | <sub>목차의 확정 장수 재확인. 양식을 보고 장수가 달라지면 이 시점에 조정</sub> |
| <sub>ⓒ</sub> | <sub>삽입 콘텐츠 수집</sub> | <sub>`reference-collector`가 Figma 레퍼런스 · 경쟁사/레퍼런스 사이트 캡처 · 실적 자료를 모아 레퍼런스 대장(`04_refs.md`) 작성. 못 구한 항목은 대체안 합의</sub> |
| <sub>ⓓ</sub> | <sub>추출</sub> | <sub>콘텐츠 초안(마크다운) → 사용자 확정 → HTML 슬라이드 → 제출 포맷에 따라 PPT/Figma 변환 또는 HTML 최종본 취합</sub> |
| <sub>ⓔ</sub> | <sub>공통지침 적용</sub> | <sub>문체 지침(`references/writing-style.md`)대로 작성, `check_style.pl`로 초안 · 덱 각각 [위반] 0건 확인</sub> |
| <sub>ⓕ</sub> | <sub>장표 품질 기준</sub> | <sub>`references/slide-quality-bar.md`로 덱 유형(§1) 확정, 장표마다 유형별 「반드시」(§3) 자기검증 → [통과/보완필요]</sub> |

- **HTML 최종본 모드**: 1600×900 골격(`template/deck_1600_template.html`) + `references/deck-production-playbook.md`. HTML 직접 작성 · 피그마 장표 벡터 취합 · 발표용 HTML iframe을 한 덱에 혼합 가능, 편집은 스크립트로만(「HTML 최종본 편집 스크립트」), 대표 페이지 렌더 확인, 요청 시 피그마 백업 · 목차 시트
- **사용자 할 일**: 양식 파일 · 레퍼런스 전달, 콘텐츠 초안 확정
- **결과물**: 덱 **v0.1** · `04_content.md` · `04_refs.md` · 검수 리포트(`r1/qa.md`)

### S5 피드백 반영 (GATE ③)

- **필요한 이유**: 회의에서 나온 말은 흩어져 있고 서로 부딪히는 경우도 있는 재료. 고치기 전에 「무엇을 어떻게 고칠지」를 표로 합의해야 누락과 임의 수정을 막는 구조
- **입력**: 회의록으로 정리된 파일(md · pdf · docx)을 `input/{프로젝트 폴더}/feedback/r{n}/`에 배치. 음성 녹취는 전사 · 회의록 정리를 마친 뒤 전달(음성 전사는 하네스 범위 밖). 대화로 준 구두 지시도 같은 대장에 기록(출처 = 「대화 YYYY-MM-DD」)
- **Claude가 하는 일**
  - 회의록을 발언 단위로 나눠 **피드백 대장** 작성: 번호(F-01…) · 발언 원문 · 발언자 역할(이름 대신 대표 · 본부장 · PM) · 대상 장표 · 유형 · 처리 방안(반영 · 보류 · 확인 필요)
  - 서로 상충하는 발언, 컨셉 · 목차까지 바뀌는 발언(상위 변경), 분량이 늘거나 주는 항목 표시
  - 문체 지적은 `writing-style.md` 추가 후보로 따로 정리(사용자 확인 후 반영)
  - 「확인 필요」와 「상충」 항목만 모아 한 번에 질문
- **사용자 할 일**: 질문 답변 · 대장 승인. **승인 전 덱 수정 보류**
- **결과물**: `r{n}/05_feedback.md`

### S6 n차 추출 + 변경분 HTML

- **필요한 이유**: 다시 보고받는 사람은 전체를 처음부터 읽지 않는 독자. 바뀐 곳만 골라 볼 수 있는 자료가 있어야 재검토가 빨라지는 구조
- **Claude가 하는 일**
  1. 문체 공통지침 재검토 (직전 피드백에 문체 지적이 있으면 지침에 먼저 반영)
  2. 직전본을 `old/`에 보관하고, 대장의 「반영」 항목만 고친 새 버전 작성(버전 +0.1 · 그날 날짜). 상위 변경은 `02_concept.md` → `03_structure.md` → `04_content.md` 순서로 반영. **대장에 없는 장표는 수정 금지**, 고치다 보인 문제는 보고만
  3. `diff_deck.pl`로 직전본과 신규본 비교 → 대장과 대조해 의도하지 않은 변경 · 미반영 항목 확인. 「시각」 변경 장표는 렌더로 실제 차이 확인
  4. **변경분 HTML 간략본** 작성: 요약 수치 / 목차별 변경 표 / 헤드라인 변경 / 신규 · 삭제 · 이동 / 미반영 · 보류 / 분량. 장표 본문은 옮겨 적지 않는 간략본, 회의록 인명 대신 역할과 F-번호만
  5. 검수
- **사용자 할 일**: 새 덱과 변경분 검토. 추가 피드백이 오면 S5로 돌아가 차수 +1
- **결과물**: 덱 **v0.n** + 변경분 간략본(별도 파일 · 덱과 항상 한 쌍) · `r{n}/06_changes.md` · `r{n}/qa.md`

### S7 최종본

- **필요한 이유**: 내용이 좋아도 제출 조건(포맷 · 쪽수 · 파일명 · 기한)을 놓치면 감점이나 접수 거부로 이어지는 단계
- **Claude가 하는 일**
  - 제출 조건 확인: 포맷(PDF · HTML · PPT) · 제출 방식 · 기한 · 파일명 · 분리 제출물 · 쪽수 제한 · 발표용 파생본 · 공개 범위. RFP · `01_rfp.md`에서 먼저 채우고 빈 것만 한 번에 질문
  - 대상 버전 동결 → 포맷별 추출 → 제출 전 점검표 작성
    - HTML = 자기완결 단일 파일(이미지 data URI) · PDF = 장당 1쪽 인쇄 또는 피그마 PDF 병합 · PPT = `pptx` 스킬(기존 발표본 pptx가 있으면 그 틀에 이미지 교체)
    - 발표용 iframe · 애니메이션 장표는 PDF · PPT에서 정지 화면 → 목차 비고 · 완료 보고에 표기
    - 점검표: 잔존 표기 · 자리표시자 0건 · 문체 [위반] 0건 · 쪽 번호 연속 · RFP 요구 항목 대응 · 장표 사이 수치 일치 · 쪽수 · 용량 · 파일명 · 제출본에서 뺄 정보(HTML 주석 · 수정 이력 메타 · 문서 속성) · 분리 제출물 · 드라이브 반영
  - 동결 이후 수정은 사용자가 지정한 장 · 문구만 반영(`diff_deck.pl`로 지정 장표만 바뀌었는지 확인). 제출본이 바뀌면 발표용 파생본도 다시 추출
  - 동결 뒤 점검에서 찾은 문제는 고치지 않고 보고, 수정 여부는 사용자 결정
- **사용자 할 일**: 제출 조건 답변. 실제 제출 · 발송은 사용자 몫
- **결과물**: 제출본 **v1.0**(`submit/`) · 발표용 파생본 · `07_release.md`

### 검수 (추출할 때마다)

- S4 · S6 · S7 뒤에 `qa` 에이전트가 자동 수행. 불합격 항목은 slide-builder 보정 후 재검수, 2라운드 뒤 남은 항목은 리포트에 적고 사용자 판단
- 점검 항목
  - 문체: `check_style.pl` [위반] 0건 · 거버닝 메시지 40자 이내 · 짝 장표 대구 · 컨셉 키워드는 헤드라인 2–3곳만
  - 정합 · 누락: 잔존 표기(`[CI 확인 필요]` 등) · 공수 ↔ 일정 M/M 합계 · 장표 사이 수치 · 목차 대비 누락 · RFP 요구 항목 대응 · `04_content.md`와 덱 문구 일치 · 작업 사이즈 일치
  - 장표 품질: `slide-quality-bar.md` §5 완성도 점검표(수치 · 근거 / 화면 · 구조 / 형식 / 스토리) · 유형별 「반드시」 누락 장표
  - HTML: 외부링크 · 쪽 번호 연속 · 자리표시자(`B0X` · `00`) · 간지 목차와 실제 장 구성 일치 · `<head>` 수정 이력 메타 · 파일명 · 버전
  - (2차 이후) 변경분 장표의 대장 근거 · 대장 「반영」 항목의 변경분 반영 · 변경분 HTML 동반 · 직전본 `old/` 보관
- 사용자가 확정한 문장 · S7 동결 뒤의 덱은 고치지 않고 보고만

## 문체 · 장표 품질 · 점검 도구

### 문체 공통지침 (`references/writing-style.md`)

실제 제출한 제안서(기준 덱)에서 뽑은 규칙. 1차 추출 전과 2차 이후 추출 전에 매번 다시 확인

| <div align="center"><sub>규칙</sub></div> | <sub>예</sub> |
|:---|:---:|
| <sub>항목 · 설명 · 표 셀은 명사구로 끝맺기</sub> | <sub>「정기 · 수시 배포 일정 확정」</sub> |
| <sub>「~함 · ~임 · ~음 · ~됨」 어미 금지</sub> | <sub>「전달되지 않음」 → 「미전달」 · 「필요함」 → 「필요」</sub> |
| <sub>「~합니다」는 고객에게 말을 거는 문장에만 (전체의 약 4%)</sub> | <sub>「담당자가 바뀌면 처음부터 다시 배웁니다」</sub> |
| <sub>거버닝 메시지는 한 문장 · 20–40자, 기본은 명사구</sub> | <sub>「작업자의 실수가 고객에게 전달되지 않는 검수 밀도」</sub> |
| <sub>약속형 거버닝(~하겠습니다)은 예외로 일부만 허용 · 덱당 5장 안팎 · 쓴 장은 완료 보고에 코드로 표기</sub> | <sub>「투입인력 전체 정규직으로 구성, 안정적으로 운영하겠습니다」</sub> |
| <sub>「당사 · 저희 · 귀사」 대신 회사명</sub> | <sub>「이트라이브는 …」</sub> |
| <sub>번역투 · 상투어 금지</sub> | <sub>「~를 통해」 「극대화」 「시너지」 「다양한」 「최적의」</sub> |
| <sub>「A를 통한 B 확보」 연쇄 · 최상급(업계 최고 · 최초 · Zero) · 1 · 2인칭(우리는 · 여러분) 금지, 「A가 아닌 B」는 덱 전체 3회 이하</sub> | <sub>「안정화 백업 인력 운용을 통한 품질 연속성 확보」 → 「결원이 생기면 본사 인력이 먼저 메우는 운영」</sub> |
| <sub>수치에는 단위와 기준 시점</sub> | <sub>「158명 · 2026.07 기준」</sub> |
| <sub>흐름은 화살표, 나열은 가운뎃점</sub> | <sub>「요청 접수 → 배분 → 검수 → 배포」</sub> |

- 기준 덱을 다른 제안서로 바꾸려면 「이 덱을 문체 기준으로 바꿔줘」라고 요청 → 지침 문서 재작성
- 분석 보고서 같은 문서형 HTML은 전역 본문 톤(명사형 종결 · 개조식) 적용

### 장표 품질 기준 (`references/slide-quality-bar.md`)

드라이브 최종 제출본 12건에서 장표 유형별로 뽑은 합격선. 초안 자기검증과 qa 검수의 [통과/보완필요] 판정 기준

| <div align="center"><sub>구성</sub></div> | <sub>내용</sub> |
|:---|:---:|
| <sub>§1 덱 유형별 골격</sub> | <sub>경쟁입찰(운영 30–40p · 구축 70–160p) · 평가 목차 지정형 · 제언서(RFI 응답형 · 피치형 15–20p) · 견적형 A4 · 발표 요약본, 회사 소개 20% 이하</sub> |
| <sub>§2 장표 해부</sub> | <sub>헤더 · 태그라인(전제) · 거버닝(결론) · 리드 · 근거 캡션 · 결론 바 · ※ 단서 · 푸터, 그룹마다 강조 1개</sub> |
| <sub>§3 유형별 합격선</sub> | <sub>표지 · 실적 · AS-IS 진단 · 여정맵 · 전략 체계 · UI 개선안 · IA · 아키텍처 · 인수인계 · SLA · 정형 관리 장 · 기대효과 · 맺음 등 레이아웃 · 반드시 · 불합격 예</sub> |
| <sub>§4 문장</sub> | <sub>잘 쓴 형태(동작 하나 · 고객 목소리 ↔ 필요한 것) · 버릴 형태(「~을 통한 ~ 확보」 · 최상급 · 「A가 아닌 B」 남발)</sub> |
| <sub>§5 완성도 점검표</sub> | <sub>수치 일치 · 수치 기준 · 콜아웃 번호 · 자리표시 · 명칭 통일 · 스토리 회수 · 발표본 문구 대조</sub> |

- 새 최종본이 올라오면 「최종본 보고 품질 기준 업데이트해줘」라고 요청 → §0 표에 추가하고 바뀐 합격선만 반영
- 역할 분담: 문장 규칙 정본 = `writing-style.md`, 색 · 서체 · 레이아웃 패턴 = `design-system.md`, 장 구성 = `skeleton-bid.md`. 이 기준과 어긋나면 `writing-style.md` · `design-system.md` 우선

### 문체 점검 `check_style.pl`

```bash
perl scripts/check_style.pl "_workspace/{프로젝트}/04_content.md"     # 콘텐츠 초안
perl scripts/check_style.pl "output/…/…-제안서-v0.1-20261117.html"   # HTML 덱
```

출력 예

```
== 문체 점검: 04_content.md ==
장표 2 · 문장(줄) 5 · 합니다체 0 (0%)

[위반] 2건
  [어미 ~음] B02 (p1): 담당자가 바뀌면 이력이 전달되지 않음
  [호칭 당사] B02 (p1): 당사는 다양한 채널을 통해 시너지를 극대화

[주의] 4건
  [상투어 「극대화」 × 1] B02
  …
결과: 위반 2건 → 고친 뒤 다시 점검
```

- 읽는 대상 = HTML 덱(`<section class="slide">`) · 콘텐츠 초안(`### [코드] 태그라인` 블록)
- **[위반]** = 반드시 고칠 것(ㅁ 명사화 어미 · 호칭 「당사 · 저희 · 귀사 · 폐사」 · 본문 대시 · 이모지). 0건이 추출 조건, 위반이 있으면 종료코드 1
- **[주의]** = 한 건씩 읽고 판단할 것(상투어 · 근거 없는 형용사 · 번역투 · 거버닝 40자 초과 · 2문장 · 누락 · 거버닝 「통한」 · 「~으로」 미완결 · 장끼리 같은 거버닝 · 한 장 합니다체 과다 · 인칭 · 띄어쓰기 · 「A가 아닌 B」 덱 4회 이상)
- `--quiet` = [주의] 생략, [위반]만 출력

### 변경분 비교 `diff_deck.pl`

```bash
perl scripts/diff_deck.pl "old/…-v0.1-20261117.html" "…-v0.2-20261120.html" \
     --md "_workspace/{프로젝트}/r2/06_changes.md" --json "_workspace/{프로젝트}/r2/06_changes.json"
```

- 두 덱의 장표를 코드(`data-code` · 코드박스)로 짝짓고, 코드가 바뀐 장표는 제목 · 본문 유사도로 다시 짝짓기
- 장표마다 변경 유형 판정(한 장에 여러 개 가능): 신규 · 삭제 · 헤드라인 · 태그라인 · 본문 · 본문 순서 · 시각(문구는 같고 이미지 · 벡터 · 스타일만 변경) · 이동 · 코드 변경 · 절 변경 · 동일
- 쪽 번호 · 저작권 푸터 변화는 변경으로 세지 않는 방식
- 결과(목차별 변경 표 · 장표별 상세 · 삭제된 장표)가 변경분 HTML 간략본의 근거 자료. 발표 요약본 문구 대조(`diff_deck.pl <제출본> <발표본>`)에도 사용

두 스크립트 모두 perl 기본 모듈만 사용. 추가 설치 불필요

### HTML 최종본 편집 스크립트

페이지 번호 · 장표 코드는 손으로 고치지 않고 스크립트로만 처리(`CLAUDE.md` 3a). 빠지는 장표(발표용 iframe 등)는 별도 파일로 보관 후 고지

| <div align="center"><sub>스크립트</sub></div> | <sub>하는 일</sub> | <sub>예</sub> |
|:---|:---:|:---:|
| <sub>`deck_edit.py`</sub> | <sub>페이지 목록 · 삭제 · 삽입 · 교체 후 1..N 자동 재번호, 실행마다 `_prev.html` 백업</sub> | <sub>`python scripts/deck_edit.py deck.html delete 24 37-46`</sub> |
| <sub>`fig2svg.py`</sub> | <sub>피그마 PDF export → 덱에 넣을 벡터 슬라이드(텍스트 패스 변환 · 서체 의존 제거)</sub> | <sub>`python scripts/fig2svg.py --prefix i --part 2 --chap "2.2 …" --out ins.html 01.pdf 02.pdf`</sub> |
| <sub>`codebox_overlay.py`</sub> | <sub>피그마 벡터 장표 위에 덱 공통 코드박스를 HTML로 덮어 코드 체계 통일</sub> | <sub>`python scripts/codebox_overlay.py deck.html --pages 24-35 --ch 2 --name "핵심 이슈" --start B06`</sub> |
| <sub>`render_pages.sh`</sub> | <sub>headless Chrome 페이지별 PNG 렌더(검수 · 피그마 백업)</sub> | <sub>`scripts/render_pages.sh deck.html out/ 24 29 1`</sub> |
| <sub>`deck_toc.py`</sub> | <sub>덱 목차(페이지 · 장 · 절 · 코드 · 태그라인 · 거버닝) → xlsx 시트 · md</sub> | <sub>`python scripts/deck_toc.py deck.html --xlsx 목차.xlsx --sheet 목차_YYMMDD`</sub> |
| <sub>`check_slides.py`</sub> | <sub>잔존 표기 · 미치환 자리표시자 · (1600 덱) 쪽 번호 연속 · 코드 자리표시자 · SVG id 접두 중복 점검</sub> | <sub>`python scripts/check_slides.py "output/…/<파일>.html"`</sub> |
| <sub>`build_compressed_pdf.py`</sub> | <sub>피그마 PDF 병합 · 그림자 래스터 치환 · 압축</sub> | <sub>—</sub> |

## 예시 대화

실제 진행 흐름 예시(가상 사업). Claude 발화는 채팅 문장 그대로 표기

```
사용자: input 폴더에 넣은 RFP로 제안서 만들어줘

Claude: 현재 10시 05분입니다. 작업 시작합니다.
        ① 업무명(파일명 앞머리)을 「ACME보험운영제안」으로 할까요?
사용자: 응
Claude: ② RFP.pdf를 정본으로, 기능목록.xlsx는 참고 자료로 보겠습니다. 맞을까요?
사용자: 맞아
Claude: ③ RFP에 평가 항목과 발표가 있어 경쟁입찰형 골격으로 진행합니다.
        ④ ACME보험 대표 사이트 로고 기준 CI Primary #0A5CFF(사이트 공통 CSS)로 추출할까요?
사용자: 응
        ※ 대표 사이트 · 로고 미확인이면 여기서 URL · 로고 파일 먼저 질문
        ※ ⑤ 범위 · 기한은 RFP에서 확인돼 재질문 생략

Claude: [S1 완료] 분석 보고서를 만들었습니다.
        제안 키워드 6개 · 방향성 후보 3안을 보고서 첫 장에 정리했습니다.
        이어서 컨셉을 제안합니다.

Claude: [S2 컨셉 — GATE ①]
        과제 4개: ① 요청마다 다른 처리 방식 ② 담당자 교체 시 이력 단절 …
        A안 「운영 이력이 쌓일수록 빨라지는 운영」  ← 추천
        B안 「요청부터 성과까지 한 화면에서 보는 운영」
        C안 …
        어느 안으로 진행할까요?
사용자: A안으로. 키워드에 '연속성'을 넣어줘
Claude: 반영했습니다. 이 컨셉으로 목차를 구성합니다.

Claude: [S3 목차 — GATE ②] 본문 36장 · 별첨 6장입니다.
        | B02 | 2.2 AS-IS 운영 과제 | 요청마다 처리 방식이 달라지는 운영 | 과제 4개 카드 … |
        … RFP 요구 항목 23건 모두 장표에 대응했습니다. 이 목차와 분량으로 진행할까요?
사용자: 진행

Claude: [S4 추출 전 확인] Figma나 PPT 기본양식 파일이 있을까요?
사용자: 없어. HTML로 제출할 거야
Claude: HTML 최종본으로 진행합니다. 작업 사이즈는 1600×900으로 할까요?
사용자: 응
Claude: (확정 장수 재확인 · 레퍼런스 수집 → 콘텐츠 초안 → 확정 → HTML 추출 …)
        현재 16시 40분입니다. 작업 완료했습니다.
        덱 v0.1(42장) · 문체 점검 위반 0건 · 검수 통과

── 며칠 뒤 ──

사용자: 임원 보고 회의록 넣었어. 반영해줘
Claude: [S5 피드백 대장 — GATE ③] 발언 14건을 정리했습니다. 반영 11 · 보류 1 · 확인 필요 2
        확인 필요 — F-06 「실적 장표를 줄이자」와 F-09 「금융 실적을 더 넣자」가 상충합니다.
        어느 쪽을 따를까요?
사용자: F-09를 따르고, 대신 비금융 실적을 한 장으로 합쳐
Claude: (대장 갱신 → 2차 추출 …)
        덱 v0.2 + 변경분 간략본을 만들었습니다. 변경 12장(헤드라인 4 · 본문 9 · 신규 1 · 삭제 2)

── 제출 전날 ──

사용자: 제출용 PDF랑 발표용 뽑아줘
Claude: [S7] 제출 조건을 확인하겠습니다. RFP 기준 PDF 1부 · 40쪽 이내 · 파일명 지정 양식 …
```

## 자주 묻는 질문

| <div align="center"><sub>상황</sub></div> | <sub>처리</sub> |
|:---|:---:|
| <sub>RFP 없이 구두 요청 · 메모만 있는 경우</sub> | <sub>받은 내용으로 S1을 축소 진행. 근거가 없는 부분은 `[미검증]` 표기 후 사용자 확인</sub> |
| <sub>자료도 경로도 주지 않은 경우</sub> | <sub>`input/{프로젝트 폴더}/`에 RFP · 요건자료를 넣거나 경로 · URL을 알려 달라는 안내부터. 워크스페이스 전역 검색 금지</sub> |
| <sub>공수 · 범위 중심의 비경쟁 제안</sub> | <sub>인테이크 ③에서 「견적형」 선택. 컨셉 단계는 「제안 방향 3가지」로 축소</sub> |
| <sub>컨셉 없이 「목차부터 짜줘」라고 요청</sub> | <sub>빠진 단계를 한 줄로 안내 → 컨셉을 짧게 먼저 할지, 사용자가 준 내용으로 대신할지 선택</sub> |
| <sub>이미 만든 덱이 있고 피드백만 반영하려는 경우</sub> | <sub>덱을 `output/output-{프로젝트 폴더}/`에, 회의록을 `input/{프로젝트 폴더}/feedback/r2/`에 두고 요청 → S5부터 시작</sub> |
| <sub>같은 프로젝트에 새 RFP가 오거나 범위가 바뀐 경우</sub> | <sub>기존 `_workspace/{프로젝트}/`를 `{프로젝트}_prev/`로 옮기고 S1부터</sub> |
| <sub>회의 녹음 파일만 있는 경우</sub> | <sub>전사 · 회의록 정리를 먼저 진행한 뒤 파일(md · pdf · docx)로 전달</sub> |
| <sub>피드백끼리 상충하는 경우</sub> | <sub>Claude가 임의로 고르지 않고 GATE ③에서 질문</sub> |
| <sub>문장 하나 · 장표 하나만 고치려는 경우</sub> | <sub>「A07 헤드라인을 이 문장으로」처럼 지정 → 지정한 곳만 그대로 반영(관련 장 검토 · 표기 보정 · 추가 제안 금지), 대장 생략, 비교 스크립트로 수정 범위 확인</sub> |
| <sub>2차 추출 뒤 또 피드백이 온 경우</sub> | <sub>같은 방식으로 3차(`r3`) 진행. 버전 +0.1, 변경분 간략본은 2차 대비로 작성</sub> |
| <sub>클라이언트 CI 색</sub> | <sub>고객사 로고의 Primary 컬러 기본 적용. 대표 사이트 · 로고를 확인하지 못하면 먼저 질문하고, 확인 없이 진행하면 기본 스타일 + `[CI 확인 필요]`. CI 없이 뽑으려면 「기본으로」</sub> |
| <sub>공수와 일정 수치가 어긋나는 경우</sub> | <sub>숨기지 않고 표면화 → 어느 쪽이 정본인지 사용자 확인. 공수 하네스 산출물이나 사용자 제공 표가 있으면 그 값 인용</sub> |
| <sub>스킬이 연결되지 않은 환경</sub> | <sub>각 에이전트 문서의 폴백 절차로 진행, 「스킬 미연결, 폴백 진행」 한 줄 보고</sub> |
| <sub>Python이 없는 PC</sub> | <sub>7단계와 perl 스크립트 2종은 그대로 동작. `check_slides.py` 점검은 전수 검색으로 대체, 덱 편집 · 피그마 PDF 취합 등 보조 스크립트만 실행 불가</sub> |
| <sub>고객 자료가 깃에 올라갈 염려</sub> | <sub>`input/` · `output/` · `_workspace/`는 `.gitignore`로 제외. 리포에는 규칙과 도구만 보관</sub> |
| <sub>사용자가 확정한 문장에 [주의]가 뜨는 경우</sub> | <sub>고치지 않고 보고만 진행. 확정 문장 유지가 우선</sub> |

## 핵심 원칙

- **컨셉 먼저**: 컨셉 · 스토리 승인 → 목차 승인 → 본문. 컨셉 없는 목차 작성 금지
- **순서 고정**: 추출 전 확인(양식 · 볼륨 · 레퍼런스) → 콘텐츠 초안(마크다운) → HTML → PPT/Figma. 콘텐츠 확정 전 포맷 파일 제작 금지
- **문체**: `references/writing-style.md` 기준. `check_style.pl` [위반] 0건에서 추출
- **장표 품질**: `references/slide-quality-bar.md` 유형별 「반드시」가 빠진 장표는 보완필요. 최종본에 남은 반례 답습 금지
- **차수**: 피드백은 대장으로 승인. 대장에 없는 장표는 수정 금지. 2차 추출부터 변경분 HTML 동반
- **마감 수정**: 지정한 장 · 문구만 그대로 반영. 관련 장 검토 · 표기 보정 · 추가 제안 금지
- **덱 편집은 스크립트로만**: 삭제 · 삽입 · 교체 · 재번호 = `deck_edit.py` 등. 번호 · 코드 수작업 수정 금지, 실행 전 `_prev.html` 백업 확인
- **공수 ↔ 일정 교차검증**: 공수(M/M) 합계와 일정 합계 일치. 외부 공수 정본이 있으면 인용
- **근거 규율**: 근거 없는 형용사 금지. `[CI 확인 필요]` · `[미검증]` · `[정책 확인 필요]` · `[추가 제안]` 표기 후 제출 전 전수 제거
- **외부링크**: HTML 문서는 출처와 본문 고유명사(사이트 · 서비스 · 기관 · 도구)를 `a.ext`로 연결, 걸기 전 URL 열림 확인(`CLAUDE.md` 5a)
- **자료 보호**: RFP · 입찰 조건을 검색어나 외부 서비스에 싣지 않는 원칙. 고객 자료는 리포 커밋 금지
- **제출은 사용자 몫**: 메일 발송 · 업로드 대행 제외

## 의존성 · 알려진 제한

| <div align="center"><sub>도구</sub></div> | <sub>필요한 것</sub> | <sub>비고</sub> |
|:---|:---:|:---:|
| <sub>`check_style.pl` · `diff_deck.pl` (`deck_lib.pl`)</sub> | <sub>perl 5 (기본 모듈만)</sub> | <sub>Git Bash(Windows) · macOS 기본 perl에서 그대로 실행</sub> |
| <sub>`check_slides.py` · `deck_edit.py` · `codebox_overlay.py` · `deck_toc.py`(md 출력)</sub> | <sub>Python 3 (표준 라이브러리)</sub> | <sub>Python이 없는 PC에서는 실행 불가. 착수 때 `python --version`으로 확인</sub> |
| <sub>`fig2svg.py`</sub> | <sub>Python + PyMuPDF</sub> | <sub>피그마 장표 벡터 취합</sub> |
| <sub>`build_compressed_pdf.py`</sub> | <sub>Python + pypdf · Pillow</sub> | <sub>피그마 PDF 병합 · 압축</sub> |
| <sub>`deck_toc.py --xlsx`</sub> | <sub>Python + openpyxl</sub> | <sub>목차 시트</sub> |
| <sub>`render_pages.sh`</sub> | <sub>zsh · headless Chrome</sub> | <sub>macOS Chrome 경로 기준. Windows는 Chrome 경로 수정 후 실행</sub> |
| <sub>PPT · Figma 변환</sub> | <sub>내장 `pptx` 스킬 · Figma 연결(`use_figma`)</sub> | <sub>—</sub> |

```bash
python3 -m pip install --user pymupdf pypdf pillow openpyxl
```

**알려진 제한 (2026.11.10 기준)**

- 7단계 전체를 실제 제안 건 하나로 끝까지 돌려 본 검증 전 상태. 스크립트 2종은 실제 제출 덱으로 확인 완료(문체 점검 40장 · 변경분 비교 45장 대 43장)
- 스킬 4종은 개편 전 흐름 기준. 스킬 산출물에 새 서식 항목(제안 키워드 · 페이지별 삽입내용 등)이 빠지면 에이전트 문서 기준으로 보충하는 방식
- `examples/INDEX.md`에 적힌 완성 제안서 파일은 리포에 없는 상태(`pptx` · `pdf` · `xlsx` 예시는 깃 제외 대상)
- `CLAUDE.md` 3c(내부망 URL 안내) 절차는 macOS 명령 기준

## 만든 배경 · 얻는 것

### 만든 배경 (2026.11.10 개편 이유)

실제 제안 작업의 흐름과 개편 전 하네스 사이의 차이 4가지에서 출발

| <div align="center"><sub>실제 제안 작업</sub></div> | <sub>개편 전 하네스</sub> | <sub>생기던 문제</sub> |
|:---|:---:|:---:|
| <sub>컨셉 · 스토리를 먼저 정한 뒤 목차 구성</sub> | <sub>RFP 분석 직후 바로 목차 작성</sub> | <sub>요구 항목을 나열한 목차 · 장마다 따로 노는 메시지</sub> |
| <sub>임원 보고 → 피드백 → 재추출을 여러 차례 반복</sub> | <sub>한 번 추출하면 종료(단일 패스)</sub> | <sub>피드백 누락 · 바뀐 곳을 사람이 두 파일을 열어 눈으로 비교</sub> |
| <sub>제출 직전 포맷 변환 · 쪽수 · 파일명 점검</sub> | <sub>마감 단계 부재</sub> | <sub>제출 조건 누락 위험 · 발표용 파일 수작업</sub> |
| <sub>사람이 쓴 문장</sub> | <sub>문체 지침 한 줄(「평어체 통일」)</sub> | <sub>「~함 · ~임」 어미 · 번역투 · 상투어처럼 AI가 쓴 티가 나는 문장</sub> |

그래서 이번 개편에서 보강한 4가지

1. **컨셉 단계 신설**: 제안서는 대부분 경쟁입찰. 컨셉과 스토리를 먼저 승인받고 목차로 진행
2. **차수 반복 구조**: 피드백을 표(대장)로 정리해 승인받고, 2차 추출부터는 직전 대비 변경분을 별도 HTML로 제공
3. **최종본 단계 신설**: 제출 조건 확인 → 버전 동결 → 포맷별 추출 → 제출 전 점검표
4. **문체 공통지침 + 자동 점검**: 실제 제출한 제안서(기준 덱)에서 문체 규칙을 뽑아 문서화하고, 스크립트로 위반 여부 확인

### 얻는 것

| <div align="center"><sub>얻는 것</sub></div> | <sub>방법</sub> |
|:---|:---:|
| <sub>**컨셉이 서 있는 제안서**</sub> | <sub>컨셉 한 줄이 표지 → 지향점 → 맺음에서 다시 등장하도록 스토리 9단계로 설계</sub> |
| <sub>**만들기 전에 합의하는 목차**</sub> | <sub>목차 표의 한 행 = 장표 1장. 장마다 들어갈 내용 · 근거 · 필요한 레퍼런스까지 미리 확정</sub> |
| <sub>**사람이 쓴 것 같은 문장**</sub> | <sub>기준 덱의 문체를 규칙으로 정리 + `check_style.pl` 자동 점검</sub> |
| <sub>**빠짐없는 피드백 반영**</sub> | <sub>회의록을 발언 단위로 쪼갠 피드백 대장. 반영 · 보류 · 미반영을 항목마다 기록</sub> |
| <sub>**바뀐 곳만 보는 재검토**</sub> | <sub>`diff_deck.pl`이 직전본과 비교한 결과로 목차 기준 변경분 HTML 간략본 작성</sub> |
| <sub>**실수 없는 제출**</sub> | <sub>제출 포맷 · 쪽수 · 파일명 · 분리 제출물을 점검표로 확인</sub> |

## 릴리즈노트

| <div align="center"><sub>요약내용</sub><img width="1" height="1"></div> | <sub>업데이트 일자</sub><img width="1" height="1"> | <sub>소유자</sub><img width="45" height="1"> |
|:---|:---:|:---:|
| <sub>README 전면 개편 — 목적 · 넣는 것 · 산출물 형태 · 요청 예시 · 진행 단계 순으로 재구성, 릴리즈노트 맨 아래로 이동</sub> | <sub>2026.11.13</sub> | <sub>김단영</sub> |
| <sub>장표 품질 기준 신설 — 드라이브 `! 사업제안&견적` 최종 제출본 12건(메리츠화재 2027 · GS칼텍스를 기준으로 KB손해보험 · 롯데지주 LIPUS · 수협 · 블루망고 · 계룡건설 · MG새마을금고 · 아시아나 · 삼성닷컴 · 현대오토에버)을 장표 단위로 읽고 `references/slide-quality-bar.md`로 정리: ① 덱 유형별 골격 · 분량(경쟁입찰 운영 · 구축 / 평가 목차 지정형 / 제언서 RFI 응답형 · 피치형 / 견적형 / 발표 요약본) ② 장표 한 장의 해부(헤더 · 태그라인 · 거버닝 · 리드 · 근거 캡션 · 결론 바 · ※ 단서 · 그룹마다 강조 1개) ③ 장표 유형 30여 종의 레이아웃 · 반드시 들어갈 내용 · 불합격 예 ④ 잘 쓴 문장 · 버릴 문장 ⑤ 완성도 점검표(수치 일치 · 콜아웃 번호 · 명칭 통일 · 스토리 회수). `writing-style.md` §5에 반례 5종(「~을 통한 ~ 확보」 · 최상급 · 인칭 · 반복 · 띄어쓰기), `check_style.pl` [주의] 확장, slide-builder 자기검증 · qa 체크리스트 · `CLAUDE.md` 3-1 · `ORCHESTRATOR.md` S4 · `skeleton-bid.md` §3 연결. 드라이브 폴더 번호 변경에 맞춰 기준 덱 경로를 이름 기준으로</sub> | <sub>2026.11.13</sub> | <sub>김단영</sub> |
| <sub>S1 분석 보고서 양식 표준화 + 고객사 CI 기본 적용 — 삼성자산운용 FunETF v0.3 보고서를 기준본으로 골격(`template/rfp_report_template.html`)과 작성 규칙(`references/rfp-report-format.md`) 신설: PART Ⅰ RFP 분석 · Ⅱ 현황 · 시장 · Ⅲ 중점 과제 심층 · Ⅳ 제안 전략 · 실행 초안, LNB 2단 · 기본 그래프(D-day · 작업 간트 · 배점 · 시장 추이 · 로드맵 · 지면 배분)와 같은 수치 표. HTML 산출물(보고서 · 덱 · 변경분)은 고객사 로고 Primary 컬러를 기본 적용 — 대표 사이트 · 로고 확인 → 미확인 · 후보 복수면 먼저 질문 → Primary 실측 → 추출 전 한 줄 확인. `CLAUDE.md` ③ · `ORCHESTRATOR.md` · `rfp-analyst` · `design-system.md` · `slide-tokens.css` · `qa` 반영</sub> | <sub>2026.11.11</sub> | <sub>김단영</sub> |
| <sub>작업단계 7단계 재편 + README 전면 보강 — ① RFP 분석 · 리서치(제안 키워드 · 방향성) ② 컨셉 · 스토리텔링 ③ 목차(페이지별 삽입내용) ④ 초안 · 1차 추출 ⑤ 피드백 반영 ⑥ 2차 추출 + 변경분 HTML ⑦ 최종본. 컨셉 승인 후 목차로 넘어가는 경쟁입찰형 골격을 기본으로(`references/skeleton-bid.md`), 견적형은 유지. 에이전트 4종 신설(`concept-planner` · `reference-collector` · `feedback-integrator` · `release-packager`), 문체 공통지침(`references/writing-style.md` · 기준 덱 = 메리츠화재 2027 발표본), 문체 점검 · 변경분 비교 스크립트(`check_style.pl` · `diff_deck.pl`), 차수 폴더(`r{n}/`)와 버전 연결, 산출물 파일명을 전역 규칙으로 통일. README는 처음 쓰는 사람 기준으로 배경 · 활용 목적 · 용어 · 단계별 설명 · 예시 대화 · 자주 묻는 질문 추가. 문체: 거버닝 메시지는 명사구가 기본이고 약속형(~하겠습니다)은 일부 허용하는 예외로 확정, 기준 덱(메리츠) 예문은 지침에 그대로 유지</sub> | <sub>2026.11.10</sub> | <sub>김단영</sub> |
| <sub>HTML 문서 외부링크 규칙 추가(`CLAUDE.md` 5a) — 출처뿐 아니라 본문 고유명사(사이트 · 서비스 · 기관 · 도구)도 `a.ext`로 연결, 아이콘은 텍스트 우측 끝 블랙 라인(정본 §22), URL 열림 검증 · 링크 전후 화면 텍스트 동일 검수. `rfp-analyst` · `qa` 에이전트 반영 (삼성자산운용 FunETF RFP 분석 보고서에 적용)</sub> | <sub>2026.11.10</sub> | <sub>김단영</sub> |
| <sub>Dan Jr. 등급 조회 추가 — 인테이크·GATE 직전 `persona.md` 확인(A 진행·B 보고·C 질문), 건너뛴 게이트는 완료 보고에 ID 표기</sub> | <sub>2026.10.22</sub> | <sub>김단영</sub> |
| <sub>HTML 최종본 모드 추가 — 착수 시 실제 제작 포맷(HTML 제출본 vs PPT/Figma)·작업 사이즈(장표 규격) 확인, 1600×900 골격(`template/deck_1600_template.html`), 덱 제작 플레이북(`references/deck-production-playbook.md`), 덱 편집·피그마 벡터 취합·렌더·목차 스크립트 5종, check_slides 덱 점검 확장 (GS칼텍스 제안 실전 반영)</sub> | <sub>2026.09.11</sub> | <sub>김단영</sub> |
| <sub>input 폴더 깃 추적 제외 (기업 민감정보 보호)</sub> | <sub>2026.07.15</sub> | <sub>김단영</sub> |
| <sub>최초 등록 — 제안서 작성 파이프라인 (모노레포 재배치)</sub> | <sub>2026.07.07</sub> | <sub>김단영</sub> |
