# harness_st-etribe — IA·공수산정 HTML 리포트 생성 하네스

RFP · 요건서 · 기능목록 · 기존 사이트 URL을 넣으면 IA 정보구조도와 공수 6표를 담은 이트라이브 IA·공수산정 HTML 리포트를 정합성 검수까지 거쳐 한 번에 생성하는 에이전트 하네스

## 한눈에 보기

| <div align="center"><sub>항목</sub></div> | <sub>내용</sub> |
|:---|:---:|
| <sub>목적</sub> | <sub>이트라이브 IA·공수산정 HTML 리포트(웅진 04/05 · FunETF 01 · 아너파라다이스 02 류)를 한 번에 생성하고 이후 대화로 고치는 방식 · 렌더는 `build_report.py`가 JSON 스펙으로 결정적 수행, 구조 · 스타일 · 수치 정합을 코드로 보장</sub> |
| <sub>이럴 때 사용</sub> | <sub>RFP · 요건을 받아 공수 산정 근거 문서가 필요할 때 · 기존 사이트 리뉴얼의 IA 추출 + 공수 산정 · 고객 제출용 공수산정안 작성 · 투입표 한 장 기준의 전체 표 재정렬</sub> |
| <sub>넣는 것</sub> | <sub>`input/`의 RFP · 요건정의서 · 개발계획서(.md · .docx · .pdf) · 기능목록(.xls) · 인프라 구성도 이미지 · 사이트 URL(.txt) 또는 대화로 준 경로 · URL · 고객 Q&A, 투입공수표(이미지 · 표)는 최우선 정본</sub> |
| <sub>나오는 것</sub> | <sub>`output/{NN}_{주제}_v{X.Y}.html` 자기완결 단일 HTML(하우스 스타일 · CSS 인라인) + 단계별 중간물 `_workspace/{slug}/` + corpus(KB) 버전 저장</sub> |
| <sub>산출물 유형</sub> | <sub>타입 A IA 정보구조도 · 타입 B 공수산정 리포트(기본) · 타입 C 제출용 공수산정안, 변형 4종(단독 · 통합 · 옵션 비교 · 동시진행)</sub> |
| <sub>시작 방법</sub> | <sub>`agent/harness_st-etribe/` 폴더에서 Claude Code 실행 → `CLAUDE.md` 자동 로딩, 별도 호출 · 설치 불필요 · 대화 흐름 예시는 `사용자가이드.html`</sub> |
| <sub>연계</sub> | <sub>corpus(KB, 사내 git `corpus` 브랜치)의 선례 검색 · 완성본 환원 · Dan Jr.(`persona.md`)의 인테이크 · GATE 등급 조회 · 다른 하네스 · 스킬 의존 부재</sub> |
| <sub>주의</sub> | <sub>고객 자료 전부 민감자료 — 추적 · 재활용 · 외부 반출 금지(아래 「민감자료 정책」)</sub> |

## 이렇게 요청

| <div align="center"><sub>상황</sub></div> | <sub>요청 예시</sub> | <sub>나오는 것</sub> |
|:---|:---:|:---:|
| <sub>RFP · 요건 자료로 공수 리포트(기본)</sub> | <sub>`input에 파일 넣었어. 작업 시작해줘` · `이 계획서로 산출물 만들어줘` · `공수 HTML 뽑아줘`</sub> | <sub>타입 B 공수산정 리포트 — IA + 공수 6표(+ 인프라 · 개념도)</sub> |
| <sub>기존 사이트 리뉴얼</sub> | <sub>`이 사이트(URL) 리뉴얼 공수 HTML 만들어줘`</sub> | <sub>사이트 IA 3뎁스+ 실측(page/view 카운트 · 관리자 · API 유추) 반영 리포트</sub> |
| <sub>IA만 필요</sub> | <sub>`이 사이트 IA 정보구조도 만들어줘`</sub> | <sub>타입 A IA 정보구조도 — 공수 값이 없으면 공수 컬럼 자동 생략</sub> |
| <sub>고객 제출본</sub> | <sub>`이 건 공수산정안 제출본으로 만들어줘`</sub> | <sub>타입 C 제출용 공수산정안 — 5장 고정 · 표 10개 · 단가 · 금액 제외 · v1.0</sub> |
| <sub>수치 부분 수정</sub> | <sub>`퍼블 마지막달 0.5→1로`</sub> | <sub>SSOT 1셀 변경 → 파생값 재계산 → 같은 수치 등장 위치 전부 갱신 · 정합 재검수(in-place)</sub> |
| <sub>내 투입표 기준 정렬</sub> | <sub>`내가 만든 투입표 줄 테니, 이걸 기준으로 산출물 전체가 서로 모순 없도록 맞춰줘`</sub> | <sub>투입표 = 최우선 정본, 영역별 · 매트릭스 · WBS · 간트 · 핵심 요약 · 히어로 카드 역산</sub> |

corpus 조회 · 실제 공수 회수 · 피드백 요청은 아래 「corpus(KB)」 표

예시 대화 (가상 고객 `테스트커머스`)

```
사용자    input에 파일 넣었어. 작업 시작해줘
에이전트  이 요건이면 공수산정 리포트로 봅니다. 현재 13시 30분입니다. 작업 시작합니다
에이전트  확인 몇 가지를 하나씩 여쭐게요. 디자인 수준은? (보통 · 높음 · 프리미엄)
사용자    높음          ← 이어서 개발 방법 · 인프라 · 상주 여부 · 기간을 하나씩, 모르면 「알아서」
에이전트  corpus: 유사 선례 2건 [acme-shop-renewal(…M/M) · …]
에이전트  GATE — 총 M/M · 인원 · 기간 · 범위 · 전제. 이대로 렌더할까요, 조정할 부분이 있나요?
사용자    진행
에이전트  output/01_테스트커머스_리뉴얼공수산정_v1.0.html · 현재 14시 30분입니다. 작업 완료했습니다
```

## 진행 단계

```
① 착수 → ② 인테이크 → ③ corpus 검색 → ④ 분석 → ⑤ 설계 · 산정 → ⑥ 다관점 검토 · GATE → ⑦ 렌더 → ⑧ 검수 → ⑨ 저장 · 환원
```

| <div align="center"><sub>단계</sub></div> | <sub>하는 일</sub> | <sub>사용자 할 일</sub> | <sub>결과물</sub> |
|:---|:---:|:---:|:---:|
| <sub>① 착수</sub> | <sub>`input/` 우선 확인(워크스페이스 전역 검색 금지) · 산출물 종류 1줄 선언 · 시작 시각 표시 · `_workspace/{slug}/` 상태로 실행 모드 결정(빈 폴더 = 초기 실행 · 부분 수정 = 해당 단계만 · 새 입력 = 기존을 `{slug}_prev/`로 옮긴 뒤 초기 실행)</sub> | <sub>자료를 `input/`에 두거나 경로 · URL 제공. `input/`이 비어 있으면 요청받은 자료 제공</sub> | <sub>시작 시각 한 줄</sub> |
| <sub>② 인테이크</sub> | <sub>고정 필수 5 + 조건부 + 동적 질문을 한 번에 하나씩 · 입력 자료 출처 인벤토리(영역 × 자료 제공 · 부분 제공 · 유추) · 산출물 변형 결정</sub> | <sub>질문마다 답변, 모르면 「알아서」(표준 가정)</sub> | <sub>정성 신호(공수 가중 근거)</sub> |
| <sub>③ corpus 검색</sub> | <sub>프로젝트 id(= slug `{고객}-{주제}`) 1회 확정 · `corpus.py pull` + `search` · 케이스 종합(`cases/{유형}.md`) → 유사 프로젝트 순 참조</sub> | <sub>한 줄 보고 확인(연결 시 선례 N건 · 실패 시 미연결 사유)</sub> | <sub>참조 선례 목록</sub> |
| <sub>④ 분석</sub> | <sub>site-analyst(사이트 URL 있을 때) ∥ analyst — 케이스 판별(A-H) · 요건 전수 항목화 · IA 3뎁스+ · 관리자 · API 유추 · 인사이트</sub> | <sub>로그인 · 봇 차단 영역은 요청 시 캡처 · 테스트 계정 · 메뉴 구술 제공</sub> | <sub>`01a_site-ia.md` · `01a_site-ia.json` · `01_analysis.md`</sub> |
| <sub>⑤ 설계 · 산정</sub> | <sub>architect — 월별 투입표(SSOT) · 공수 6표 · IA · 섹션 구성을 JSON 스펙으로 ∥ solution-architect — AS-IS/TO-BE 인프라 · 개념도(infra · concept 범위일 때만)</sub> | <sub>—</sub> | <sub>`02_spec.json`(+ `02_spec.md`) · `02b_solution.json`</sub> |
| <sub>**⑥ 다관점 검토 · GATE**</sub> | <sub>persona-review(estimate) — PM · 아키텍트 · 개발 · 디자인/퍼블 · 고객 관점의 공수 · 인사이트 · 콘텐츠 발전도 검토, P0면 architect 반려 · 재산정 후 GATE 제시</sub> | <sub>**총 M/M · 인원 · 기간 · 범위 · 전제 확인 → 렌더 승인 또는 조정 지시**</sub> | <sub>`02c_persona_review.md`</sub> |
| <sub>⑦ 렌더</sub> | <sub>builder — `build_report.py`로 JSON → HTML 결정적 렌더, prose 슬롯만 작성 · LLM 수기 렌더는 폴백</sub> | <sub>—</sub> | <sub>`03_draft.html`</sub> |
| <sub>⑧ 검수</sub> | <sub>qa — 정합 (a)-(h) · 발명 클래스 · 샘플 유출 · `[WARN]` 0 · RFP 커버리지 등, FAIL이면 builder 보정 → 재검수 · persona-review(final)는 조건부</sub> | <sub>2라운드 후 잔여 불일치 에스컬레이션 시 판단</sub> | <sub>`04_qa.md`(+ `04b_persona_review.md`)</sub> |
| <sub>⑨ 저장 · 환원</sub> | <sub>`output/` 저장 · `corpus.py put-html` 버전 커밋 · qa PASS 후 `corpus.py save` 환원 · 완료 시각 + 내부망 짧은 주소(`http://<IP>:<포트>/`) 보고</sub> | <sub>결과 확인, 이후 대화로 수정</sub> | <sub>`output/{NN}_{주제}_v{X.Y}.html` · `05_meta.json`</sub> |
| <sub>수시 · 피드백</sub> | <sub>feedback-curator — 이번 세션 수정 건 번호 열거 → 선택 → 오너용 수정 제안 리포트, 에이전트 자동 수정 없이 검토 큐 누적</sub> | <sub>대상 번호 선택 · 반영 여부는 오너 판단</sub> | <sub>`feedback/proposals.md`(corpus)</sub> |

- 시각 표시 형식: 착수 「현재 HH시 MM분입니다. 작업 시작합니다.」 · 완료 「현재 HH시 MM분입니다. 작업 완료했습니다.」, 시:분은 매번 조회
- 내부망 주소는 output 원본을 가리키는 심볼릭 링크 + 로컬 HTTP 서버(8001번부터 빈 포트) 방식, 절차 `CLAUDE.md` 3c
- 단계 실패 시 1회 재시도, 재실패면 해당 산출물 없이 진행 + 최종 보고에 누락 명시
- 산정 충돌(필요 > 가용)은 숨김 없이 표면화 + 완화안(범위 분리 · 기간 연장) 병기
- 사이트 로그인 · 봇 차단 영역은 추측 금지, 자료를 못 받으면 `접근불가` + `추정` 플래그와 보고서의 미접근 · 추정 명시
- Dan Jr. 등급 조회(2026.10.22): 인테이크 질문 · GATE · 「할까요?」 확인 직전 `~/.claude/persona/persona.md`(전역 규칙이 없는 환경은 `../../persona/persona.md`) 확인 → A 기본값 진행 · B 진행 후 완료 보고에 한 줄 · C 또는 미등재 항목은 질문, 건너뛴 게이트는 완료 보고에 「Dan Jr. 적용: D-09(A)」 형식 표기
  - 고정 필수 5 인테이크 · 공수 GATE처럼 persona.md에 없는 결정은 사용자 확인 유지

### 인테이크 질문

| <div align="center"><sub>질문</sub></div> | <sub>답 예시</sub> | <sub>기본값</sub> |
|:---|:---:|:---:|
| <sub>① 디자인 수준</sub> | <sub>보통 · 높음 · 프리미엄</sub> | <sub>표준 가정</sub> |
| <sub>② 개발 방법(공수 핵심 분기)</sub> | <sub>기존 소스 그대로 활용 · 부분 재개발 · 전면 신규</sub> | <sub>표준 가정</sub> |
| <sub>③ 인프라 구축 실제 작업 포함 여부</sub> | <sub>실제 구축 · 세팅(공수 포함) · 구성도 제시만(작업 제외)</sub> | <sub>표준 가정</sub> |
| <sub>④ 상주 / 비상주</sub> | <sub>상주 · 비상주</sub> | <sub>상주(보수적 가정)</sub> |
| <sub>⑤ 고객 요청 프로젝트 기간</sub> | <sub>6개월 · 일정 · 예산 압박 정도</sub> | <sub>표준 가정</sub> |
| <sub>조건부 · TO-BE 인프라 제안 포함</sub> | <sub>포함 · 제외(RFP에 AS-IS 인프라가 있을 때만 질문)</sub> | <sub>표준 가정</sub> |
| <sub>동적 · ⑥ RFP 미상 · 모호 항목 2-4개</sub> | <sub>PG사 · 결제수단 미정, 연동 규격 · 테스트계정 시점, 관리자 권한 등급, 정산 · 환불 책임 경계, 다국어 · 이관 범위</sub> | <sub>표준 가정</sub> |

- 고정 필수 5는 RFP와 무관하게 항상 질문, 자료 · 대화로 이미 확정된 항목만 생략. 추론 가능한 항목(산출물 종류 등)은 질문 대신 선언
- 한꺼번에 답하면 그대로 수용, 남은 항목만 이어서 질문
- ⑥은 RFP가 다루는 내용의 빈칸만 대상. RFP에 없는 신규 기능(챗봇 · AI · 추천)의 「필요하세요?」 타진 금지
- 공수 반영: 디자인 높음 → 디자인 · 퍼블 상향 · 비상주 → 퍼블 · 개발 최대 -30%(기획 · 디자인 제외) · 상주 → 감면 제외 + 상주 인력 장기 0.5 금지 · 기획 염려 → 버퍼 + confidence 하향

## 산출물

### 파일

| <div align="center"><sub>파일</sub></div> | <sub>형식</sub> | <sub>위치</sub> | <sub>내용</sub> |
|:---|:---:|:---:|:---:|
| <sub>`{NN}_{주제}_v{X.Y}.html` 예) `01_테스트커머스_리뉴얼공수산정_v1.0.html`</sub> | <sub>HTML 단일 파일(CSS 인라인 + 말미 JS)</sub> | <sub>`output/`</sub> | <sub>최종 리포트(1파일 = 1주제) · 초안 v0.1 · 정식 v1.0 · 수정은 in-place 기본, 매우 큰 수정만 버전업</sub> |
| <sub>`01a_site-ia.md` · `01a_site-ia.json`</sub> | <sub>md · json</sub> | <sub>`_workspace/{slug}/`</sub> | <sub>사이트 IA 트리(type · 출처) · footer · 회원 도메인 · 관리자 · API 유추 · page/view 카운트(사이트 URL 있을 때)</sub> |
| <sub>`01_analysis.md`</sub> | <sub>md</sub> | <sub>`_workspace/{slug}/`</sub> | <sub>프로젝트 케이스 · 입력 자료 출처 인벤토리 · 요건 리스트 · 현황 · 인사이트 · 정성 신호 · 참조 선례</sub> |
| <sub>`02_spec.json`(+ `02_spec.md`)</sub> | <sub>json(+ md 짧은 요약)</sub> | <sub>`_workspace/{slug}/`</sub> | <sub>`build_report.py` 입력 스펙(SSOT) — meta · hero · sections · footer</sub> |
| <sub>`02b_solution.json`</sub> | <sub>json</sub> | <sub>`_workspace/{slug}/`</sub> | <sub>infra · concept 섹션 객체, `02_spec.json`에 합류</sub> |
| <sub>`02c_persona_review.md` · `04b_persona_review.md`</sub> | <sub>md</sub> | <sub>`_workspace/{slug}/`</sub> | <sub>페르소나별 코멘트 · P0/P1/P2 · 합의 결론(GATE 전 · 최종 전 조건부)</sub> |
| <sub>`03_draft.html`</sub> | <sub>html</sub> | <sub>`_workspace/{slug}/`</sub> | <sub>렌더 결과(검수 대상)</sub> |
| <sub>`04_qa.md`</sub> | <sub>md</sub> | <sub>`_workspace/{slug}/`</sub> | <sub>PASS/FAIL 요약 · 불일치 목록(위치 · 현재값 · 기대값 · 근거) · builder 재수정 요청</sub> |
| <sub>`05_meta.json`</sub> | <sub>json</sub> | <sub>`_workspace/{slug}/`</sub> | <sub>corpus 환원용 리치 메타(식별 · 공수 · 섹션 콘텐츠)</sub> |
| <sub>`deliverables/{id}/report.html` + 섹션 원자</sub> | <sub>git 커밋</sub> | <sub>corpus 브랜치(`.corpus/`)</sub> | <sub>버전 이력 · 태그 `kb/{id}` · 다음 유사 산정의 선례</sub> |

### 리포트 유형

| <div align="center"><sub>유형</sub></div> | <sub>언제</sub> | <sub>구성</sub> |
|:---|:---:|:---:|
| <sub>타입 A IA 정보구조도</sub> | <sub>IA만 필요할 때</sub> | <sub>사이트 · 시스템 메뉴 구조(1-3뎁스) + 관리자 IA, 공수 값이 없으면 IA 표 공수 컬럼 자동 생략</sub> |
| <sub>타입 B 공수산정 리포트</sub> | <sub>기본</sub> | <sub>아래 「리포트 구성」 + 공수 6표</sub> |
| <sub>타입 C 제출용 공수산정안</sub> | <sub>「공수산정안 제출」 요청</sub> | <sub>5장 고정(프로젝트 개요 · 주요 요구사항별 구현방향 · 사업 수행계획 · 투입공수 · 기타 고려사항) · 표 10개 · 본문 약 1.2만 자(타입 B 대비 약 50%) · 단가 · 금액 · 개정 이력 · 출처 섹션 제외 · 제출본 v1.0, 제출 뒤 변경은 v2.0 새 파일(v1.0 보존) · 정본 `references/report-spec.md` §1-1</sub> |
| <sub>변형 4종</sub> | <sub>시스템 · 옵션 구성에 따라</sub> | <sub>① 단독안(시스템 1개) ② 통합안(여러 건을 한 사이트로) ③ 옵션 비교안(옵션1/옵션2) ④ 동시진행안</sub> |

### 리포트 구성 (타입 B)

| <div align="center"><sub>순서</sub></div> | <sub>섹션</sub> | <sub>포함</sub> |
|:---|:---:|:---:|
| <sub>H</sub> | <sub>헤더 + hero 카드(기간 · 총공수 분해 · 투입인력 · 핵심 · 대상 규모 · 실측) · 좌측 목차 자동</sub> | <sub>고정</sub> |
| <sub>1</sub> | <sub>대상 개요(메뉴칩 + insight)</sub> | <sub>항상</sub> |
| <sub>2</sub> | <sub>배경 · 현황 진단(실측 결과)</sub> | <sub>항상</sub> |
| <sub>3</sub> | <sub>IA 정보구조도(1노드 = 1행) — 관리자가 있으면 Front IA / Admin IA 2섹션</sub> | <sub>항상</sub> |
| <sub>4</sub> | <sub>영역 · 모듈 분석 — IA 변경 분석 · 외부 연동 · 관리자 · 인프라 AS-IS/TO-BE · RFP 요건 커버리지 대조표</sub> | <sub>조건부</sub> |
| <sub>5</sub> | <sub>value-chain</sub> | <sub>거의 항상</sub> |
| <sub>6</sub> | <sub>종합 분석 총평</sub> | <sub>거의 항상</sub> |
| <sub>7</sub> | <sub>프로젝트 개요(AS-IS / TO-BE / 제약 / 방향)</sub> | <sub>항상</sub> |
| <sub>8</sub> | <sub>공수 산정 6표 — 영역별 공수 → 월별 투입 인력표(SSOT) → 역할 · 단계 매트릭스 → WBS → 간트 차트 → 핵심 요약(번호 8-1부터 8-6)</sub> | <sub>항상</sub> |
| <sub>9</sub> | <sub>확인 필요 질문(고객 확인용, 미확정 시 공수 · 범위 · 일정 영향 병기)</sub> | <sub>항상 · 맨 마지막</sub> |
| <sub>F</sub> | <sub>푸터(총공수 · 개월 · 인원)</sub> | <sub>고정</sub> |

- 기본 적용: 이트라이브 화이트 로고(`template/etribe_logo_white.png`) · 스크롤 고정 Mini GNB · 상위 그룹 타이틀과 2단 목차(`report-spec.md` §3b)
- 기본 톤 warm paper × near-black, 고객 브랜드색은 `palette` 지정 시 `--brand` 별칭(도식)에만 반영

## 준비 (처음 한 번)

| <div align="center"><sub>준비</sub></div> | <sub>방법</sub> | <sub>필요 시점</sub> |
|:---|:---:|:---:|
| <sub>Python 3</sub> | <sub>`scripts/` 전부 표준 라이브러리만 사용, 추가 패키지 설치 불필요</sub> | <sub>항상</sub> |
| <sub>하네스 받기</sub> | <sub>이 리포 또는 사내 GitLab `harness_st`의 `etribe` 브랜치 clone → 받은 하네스 폴더를 Claude Code로 열기</sub> | <sub>처음 1회</sub> |
| <sub>corpus 연결</sub> | <sub>`.env.example`을 `.env`로 복사 후 `CORPUS_GIT_TOKEN` 입력 · `CORPUS_GIT_REMOTE`(비우면 현재 repo origin) · `CORPUS_GIT_BRANCH`(기본 `corpus`)</sub> | <sub>선택 — 미설정 시 선례 참조 없이 진행</sub> |
| <sub>git</sub> | <sub>corpus 동기화 · 버전 커밋</sub> | <sub>corpus 사용 시</sub> |
| <sub>민감자료 커밋 차단 훅</sub> | <sub>리포 루트에서 `git config core.hooksPath .githooks`</sub> | <sub>리포 clone 직후 1회</sub> |
| <sub>스킬 동기화</sub> | <sub>불필요 — 스킬 의존 부재</sub> | <sub>—</sub> |

- 폴더 안에서 열어 쓰는 구조라 모든 경로가 상대경로로 동작(이식성 확보, 절대경로 부재)
- 토큰은 `.env`에만 기록, MD · 코드 · 로그 기재 금지

## 폴더 구성

```
harness_st-etribe/
├── CLAUDE.md                 폴더를 열면 자동 로딩되는 현관문 — 동작 규칙 · 민감자료 정책
├── ORCHESTRATOR.md           실행 워크플로우(메인이 읽고 구동) · 파일 네이밍 표준 정본
├── README.md                 이 파일(개요 · 사용법 · 변경 이력)
├── 사용자가이드.html          Claude Code 대화 흐름 형식 사용 가이드(팀 배포용)
├── .env.example              corpus 토큰 · 원격 · 브랜치 설정 템플릿(.env는 git 미추적)
├── agents/                   에이전트 정의 8종
│   ├── site-analyst.md · analyst.md
│   ├── architect.md · solution-architect.md
│   ├── persona-review.md · builder.md · qa.md
│   └── feedback-curator.md
├── references/
│   ├── report-spec.md                    생성 규칙 정본 — 입력 계약 · 섹션 순서 · 6표 · 정합 a-h · 변형 · 타입 C
│   ├── project-cases.md                  프로젝트 케이스 A-H · delta 2축
│   ├── effort-estimation-methodology.md  공수 산정 방법론 · 함정(architect 두뇌)
│   ├── house-style-guide.md              디자인 토큰 · 클래스 카탈로그
│   ├── section-catalog.md                표준 섹션 순서
│   ├── consistency-checklist.md          수치 정합성 (a)-(h) 교차검증(qa 핵심)
│   ├── site-ia-extraction.md             기존 사이트 IA 3뎁스+ 추출 · 유추(+정밀도 규칙)
│   ├── ia-extraction-upgrade.md          IA 추출 오류 7종 · 해결 규칙 · JSON 스키마 · 검증 사례
│   ├── architecture-infra-diagram.md     AWS 공식 아이콘 도식 · 개념도 · AS-IS/TO-BE 원칙
│   ├── corpus-knowledge-base.md          corpus(KB) 검색-증강 · 환원 · 피드백 루프
│   ├── playbook-domain-questions.md      요건 누락 탐지 체크리스트(analyst)
│   └── playbook-effort-validation.md     공수 5축 자기검증(architect · qa)
├── template/
│   ├── base_template.html    섹션 스켈레톤(CSS는 마커 주입)
│   ├── house-style.css       하우스 스타일 전체 CSS(warm paper × near-black)
│   ├── diagrams.css          개념도(eco) + AWS 인프라(aws-*) CSS
│   └── etribe_logo_white.png 헤더 로고 · Mini GNB 기본 로고
├── scripts/
│   ├── build_report.py       렌더 엔진 — JSON 스펙 → HTML 결정적 렌더 · CSS 주입 · 팔레트 · [WARN] 가드
│   ├── inline_css.py         CSS 바이트 그대로 <style> 주입(폴백 렌더용 · 중괄호 균형 가드)
│   ├── check_consistency.py  표 파싱 · 합산 정합 자동 검증
│   ├── check_classes.py      발명 클래스(정의 0 · 사용 N) 검출 — 렌더 깨짐 가드
│   ├── check_leak.py         샘플 고객 토큰 잔존 검사(qa 게이트)
│   ├── corpus.py             corpus 동기화 · 검색 · 스냅샷 · 환원 · 버전 · 피드백 · 제안
│   ├── ia_extract.py         사이트 IA 정밀 추출(메가패널 · 탭/그룹 · 이중 카운트 · footer · 로그인)
│   └── extract_assets.py     RFP(.docx · .pptx · .xlsx) 임베드 이미지 추출 → Read 판독
├── examples/                 과거 완성본 샘플(로컬 전용 · git 미추적, INDEX.md만 추적) — 형식 · 구성 참고 전용
├── input/                    사용자 입력 자료(git 미추적)
├── output/                   최종 HTML(실행 시 생성 · git 미추적)
└── _workspace/{slug}/        프로젝트별 중간물(실행 시 생성 · git 미추적)
                              01a_site-ia · 01_analysis · 02_spec · 02b_solution · 02c_persona_review
                              03_draft · 04_qa · 04b_persona_review · 05_meta
```

corpus 데이터는 별도 `corpus` 브랜치 — `corpus.py`가 git 미추적 `.corpus/`에 클론, 도구 코드(`etribe` 브랜치)와 분리

## 에이전트 구성

```
┬ site-analyst (사이트 URL 있을 때) ┐        ┬ architect ─────────────────┐
└ analyst (요건 + 병합)              ┘→ 01 → └ solution-architect(조건부) ┘→ persona-review → GATE → builder → qa ─(FAIL)→ 보정 → 최종 HTML
```

| <div align="center"><sub>에이전트</sub></div> | <sub>모델</sub> | <sub>실행</sub> | <sub>역할</sub> |
|:---|:---:|:---:|:---:|
| <sub>**site-analyst**</sub> | <sub>sonnet</sub> | <sub>사이트 URL 있을 때 · analyst와 병렬</sub> | <sub>`ia_extract.py`로 IA 3뎁스+ 전수 추출 · page/view 이중 카운트 · footer · 회원 도메인 · 관리자 · API 유추</sub> |
| <sub>**analyst**</sub> | <sub>opus</sub> | <sub>항상</sub> | <sub>케이스 판별 · 입력 자료 출처 인벤토리 · 요건 전수 항목화 · 현황 · 제약 · 인사이트 · 정성 신호 · 요건 ↔ IA 병합(사이트가 없으면 IA도 직접)</sub> |
| <sub>**architect**</sub> | <sub>opus</sub> | <sub>항상</sub> | <sub>월별 투입표(SSOT) · 매트릭스 · WBS · 간트 · 공수 산정 + 정성 신호 공수 가중 + 5축 자기검증 → `02_spec.json`</sub> |
| <sub>**solution-architect**</sub> | <sub>opus</sub> | <sub>infra · concept 범위일 때 · architect와 병렬</sub> | <sub>기술 아키텍처 · AS-IS/TO-BE 인프라(AWS 형식) · 통합 생태계 개념도, 공수와 무관</sub> |
| <sub>**persona-review**</sub> | <sub>opus</sub> | <sub>GATE 전 항상 · 최종 전 조건부</sub> | <sub>PM · 아키텍트 · 개발 · 디자인/퍼블 · 고객 다관점 검토 — qa가 못 보는 설득력 · 현실성 · 고객 수용성 · 콘텐츠 발전도</sub> |
| <sub>**builder**</sub> | <sub>sonnet</sub> | <sub>항상</sub> | <sub>`02_spec.json`을 `build_report.py`로 결정적 렌더(6표 · 인프라 · 개념도 · CSS · 팔레트), 자유 서술 prose만 작성 · LLM 수기 렌더는 폴백</sub> |
| <sub>**qa**</sub> | <sub>sonnet</sub> | <sub>항상</sub> | <sub>정합 · 발명 클래스 · 샘플 유출 · 공수 5축 등 검증(실검사는 스크립트)</sub> |
| <sub>**feedback-curator**</sub> | <sub>opus</sub> | <sub>사용자 수정 확정 시 on-demand</sub> | <sub>수정 건의 오너용 수정 제안 리포트 정리 · 에이전트 직접 수정 금지</sub> |

- 모델 티어링: 추론 = opus · 기계적 = sonnet(비용 · 속도), 앞단(site-analyst ∥ analyst) · 중간단(architect ∥ solution-architect) 병렬로 지연 단축
- opus 호출: 평시 3회(analyst · architect · persona-review estimate), 인프라 범위면 +1(solution-architect), 최종 재검토 조건 충족 시 +1(persona-review final)
- persona-review final 조건: estimate의 P0/P1 보완이 콘텐츠를 실질 변경 · builder 폴백(수기 렌더) · 대형 · 고위험 · 고객 직제출로 사용자가 최종 확인 요청
- 실행 방식: 메인이 `ORCHESTRATOR.md`를 읽고 단계마다 `agents/*.md` 역할 정의를 프롬프트로 주입해 서브에이전트(general-purpose) 스폰, 각 에이전트는 자기 .md의 「참조 파일」만 읽기

## 핵심 산출 규칙

운영 누적 규칙 · 위반 시 qa FAIL 또는 build_report `[WARN]`

- **자료 > 유추**: 고객 제공 자료(기능목록 · 구성도 · xls 시트 · 이미지)가 있는 영역은 자료 기반(실측) 반영, 자료가 없을 때만 유추. analyst가 착수 시 「입력 자료 출처 인벤토리」로 영역 × 출처 매핑
- **인테이크 = 한 번에 하나씩 순차 질문**: 고정 필수 5(디자인 수준 → 개발 방법 → 인프라 실작업 포함 → 상주/비상주 → 기간) → 조건부(AS-IS 인프라가 있으면 TO-BE 제안 포함) → 동적(RFP 미상 · 모호 2-4개). 추론 가능한 항목은 질문 생략
- **IA = 페이지(기능) 단위, 1노드 = 1행**: 콘텐츠 개수로 노드 부풀리기 금지(「스타일 N」은 한 페이지 안 표시 변형일 때만). admin이 있으면 Front IA / Admin IA 2섹션 분리, admin 없는 정적 · 소개형 사이트는 Front만, 프론트 없는 백오피스 · ERP(케이스 D)는 Admin(단일) IA만
- **케이스 판별 + delta 2축**: 표현(화면) · 구현(기능) 축 분리 — 디자인만 변경(F)은 개발 ≈ 0, 화면 유지 + 백엔드 신규(G)는 개발 = 신규
- **인프라 AS-IS = 고객 제공 구성도 원본 그대로(`figure`) / TO-BE = AS-IS delta**(유지 · 변경 · 신규 · 제거 + 근거, 현행 필수 요소 임의 제거 금지). RFP에 인프라 요구가 없을 때만 일반 권장 구성. 인프라는 제시 항목, 영역별 공수 제외
- **인력 정책**: 톱니(중간 월 0.5) · 장기 반투입(0.5 2개월+) 금지(정당한 파트타임은 `parttime:true`). QA = 기획 겸임(전담 직군 금지, 기획 1명 막달까지). 테스트 구간 디자인/퍼블 2명+ → 1명 감쇠. 기획 실무가 디자인의 절반 미만이면 기획 과소 경고. 비상주 → 퍼블 · 개발 최대 -30% / 상주 → 감면 제외
- **RFP 충실성**: RFP에 없는 기능(챗봇 등) 추가 금지, 요건의 기술 솔루션 비약 금지(GEO/SEO 최적화 ≠ 색인엔진 인프라), 외부사 시스템(VAN · PG · 기간계)은 연계 I/F만
- **RFP 커버리지 + 확인 질문**: 요건 전수 항목화 → 커버리지 대조표 + 산출물 맨 끝 「확인 필요 질문」(추정 · 데이터갭)
- **투입공수표 = 최우선 정본**: 사용자가 투입공수표(이미지 · 표)를 주면 나머지 표 역산
- **산정 독립성**: 세션 · 메모리의 다른 프로젝트 수치 · 미커밋 수치의 비교 · 앵커 금지. 허용된 참조는 corpus(커밋 KB)뿐 — 선례는 밴드 보정 · 교훈 · 과소산정 경고 용도, 인용 흔적 필수
- **출력 위치**: 산출물은 `_workspace/{slug}/` · `output/`만(temp · 홈 금지). build_report의 모든 `[WARN]`을 0으로 만든 뒤 qa PASS
- **렌더 = 결정적 스크립트**: `build_report.py`가 JSON → HTML(전 섹션 kind). 클래스 발명 · CSS 직접 작성 · prose 자유 HTML 최소화(상세 · 변경 경위는 「변경 이력」)
- **표현 절제**: 섹션 제목 · 도식 라벨의 과장 네이밍 · 마케팅 수식어 금지, 섹션 도입 prose는 짧은 리드(1-2문장) + 표 · 불릿

## 민감자료 정책

추적 금지 · 재활용 금지 · 외부 반출 금지 — 이 하네스가 다루는 고객 자료 전부 민감자료, 어떤 단계 · 어떤 에이전트도 예외 부재(정본 `CLAUDE.md`)

| <div align="center"><sub>대상</sub></div> | <sub>성격</sub> | <sub>규칙</sub> |
|:---|:---:|:---:|
| <sub>`input/`</sub> | <sub>RFP · 요건 · 기능목록 · 구성도 등 고객 원자료</sub> | <sub>git 미추적(`.gitignore`), 대화 · 산출물 밖 반출 금지</sub> |
| <sub>`output/` · `_workspace/`</sub> | <sub>이번 프로젝트 산출물 · 중간물</sub> | <sub>git 미추적, 프로젝트 슬러그 폴더 밖 복사 · 병합 금지</sub> |
| <sub>`examples/*.html`</sub> | <sub>과거 고객 완성본(샘플) — 실제 공수 · 견적 · 단가 포함</sub> | <sub>git 미추적(INDEX.md만 추적), 샘플 전용</sub> |
| <sub>`.corpus/` · `.env`</sub> | <sub>선례 KB 클론 · 접근 토큰</sub> | <sub>git 미추적, 토큰의 MD · 코드 · 로그 기재 금지</sub> |

1. **추적 금지**: 위 경로의 저장소 커밋 금지. 부모 저장소 `.githooks/pre-commit`이 스테이징 차단, 우회(`--no-verify` · `git add -f`) 금지
2. **재활용 금지**: `examples/` · corpus 선례는 형식 · 구성 · 도식 구현 · 산정 방식을 보는 샘플. 고객명 · 수치(M/M · 단가 · 기간 · 인원) · 범위(in/out) · IA 트리 · 문장 · 표 행의 다른 프로젝트 이전 · 적용 금지. 산정 밴드는 감각 보정에만, 근거는 매번 이번 프로젝트의 RFP · 입력 · 인테이크 답변에서 새로 수립. 이전 프로젝트의 스타일 변형(CI 색 · 톤) 이월 금지
3. **외부 반출 금지**: 고객 자료 · 산출물의 외부 저장소(공개 · 타 조직 GitHub 등) · 아티팩트 공개 링크 · 외부 SaaS(드라이브 · 노션 · 슬랙 등) · 외부 API 전송 금지. corpus push는 `.env`의 사내 원격(`CORPUS_GIT_REMOTE`)에만, 사용자가 명시 지정한 대상만 예외
4. **게이트**: qa가 `python scripts/check_leak.py <html> --allow {이번 고객명}`으로 샘플 고객 토큰 잔존 0건 확인(FAIL이면 builder 재수정). 수치 · 문장 재사용 여부는 qa (s) · persona-review 점검

## 검수 기준

| <div align="center"><sub>구분</sub></div> | <sub>점검</sub> | <sub>도구</sub> |
|:---|:---:|:---:|
| <sub>수치 정합 (a)-(h)</sub> | <sub>영역표 합 = 제작 소계 · 제작 소계 + PM/기획 = 총 공수 · 디/퍼/개 분해 일치(영역표 · 월별표 · hero · 핵심 요약) · 월별표 행 · 열 · 총계 합 · 개월수 일치(월별 · 매트릭스 · WBS · 간트 · hero · footer) · 간트 totalWeeks = 개월수 × 4 · 이전 브랜드 hex 잔존 0 · 수정 전 총량 · 개월수 문자열 잔존 0</sub> | <sub>`check_consistency.py` · 문자열 검색</sub> |
| <sub>렌더 무결성 (i)(k)</sub> | <sub>발명 클래스 0 · CSS 중괄호 균형 · 도식 포함 시 런타임 렌더 1회 확인</sub> | <sub>`check_classes.py` · `inline_css.py` · 로컬 서버 + 브라우저</sub> |
| <sub>빌드 경고 (l)</sub> | <sub>`[WARN]` 0 — IA 압축 · 인력 정책 · 출력 위치 · 확인 질문 누락 · TO-BE 단독</sub> | <sub>`build_report.py`</sub> |
| <sub>내용 (j)(m)-(s)</sub> | <sub>공수 5축 · RFP 요건 커버리지 · 제공 자료 반영 · TO-BE = AS-IS delta · RFP 충실성 · 공수 추론 사슬 · 얕음 · 복붙 1차 탐지 · 표현 절제</sub> | <sub>qa 판독 · persona-review 에스컬레이션</sub> |
| <sub>샘플 유출 (t)</sub> | <sub>`examples/` · corpus 선례의 고객 토큰 잔존 0</sub> | <sub>`check_leak.py`</sub> |

- 판정 정본 `references/consistency-checklist.md`(= `report-spec.md` §5), 발견은 위치 · 현재값 · 기대값 · 근거로 보고, 상충 데이터는 임의 삭제 금지(출처 병기)

## corpus(KB)

팀이 쓸수록 쌓이는 과거 산출물 저장소 — 유사 선례 검색으로 산정 일관성 보정, 완성본 환원, 실제 공수 회수로 누적 자기보정

| <div align="center"><sub>시점 · 요청</sub></div> | <sub>명령</sub> | <sub>결과</sub> |
|:---|:---:|:---:|
| <sub>착수</sub> | <sub>`corpus.py pull` → `search --domain .. --tags ..`</sub> | <sub>유사 선례 밴드 카드 · 한 줄 보고(연결 시 선례 N건, 실패 시 미연결 사유)</sub> |
| <sub>GATE 승인 직후(장시간 · 고위험만)</sub> | <sub>`snapshot --id .. --ws .. --stage gate`</sub> | <sub>workspace 미러 1커밋 · 검색 인덱스 불변</sub> |
| <sub>최종 HTML 작성 · 수정마다</sub> | <sub>`put-html --id .. --html .. --note ..`</sub> | <sub>버전 커밋 + 태그 `kb/{id}` 이동</sub> |
| <sub>qa PASS 후</sub> | <sub>`save --html .. --meta 05_meta.json --ws ..`</sub> | <sub>섹션 원자별 커밋 + report 커밋 + 태그, qa PASS = push 게이트</sub> |
| <sub>`최신 HTML 보자`</sub> | <sub>`get --id .. [--out ..] [--rev ..]`</sub> | <sub>로컬 대신 git 최신본(또는 특정 버전) + 버전 이력</sub> |
| <sub>`이 건 실제 N M/M 들었어`</sub> | <sub>`feedback --id .. --actual N --lesson ..`</sub> | <sub>실제 공수 기록 → 이후 유사 검색의 과소 · 과대 산정 경고</sub> |
| <sub>수정 확정 후 `피드백 문서 작성해줘`</sub> | <sub>feedback-curator → `propose --note ..`</sub> | <sub>`feedback/proposals.md` 오너 검토 큐 누적 · 반영은 오너 판단(직접 편집 또는 `/harness`)</sub> |

- 위치: 같은 repo의 별도 `corpus` 브랜치(도구 코드 = `etribe` 브랜치), `corpus.py`가 git 미추적 `.corpus/`에 클론 · 갱신
- 구조: `cases/{유형}.md`(케이스 종합 — 통상 범위 · 꼭 확인할 것 · 공수 밴드) · 섹션 원자(`estimates/` · `scope/` · `questions/` · `ia/` · `approach/` · `direction/` · `overview/` · `infra/` · `dev-notes/decisions/`) · `patterns/` · `deliverables/{id}/report.html` + `workspace/` · `index.jsonl`
- id = slug `{고객}-{주제}`(예: `acme-shop-renewal`), 같은 프로젝트 재작업은 같은 id로 최신화(이력은 git 히스토리)
- 커밋 메시지 `kb({type}): {id} | {고객} | {케이스} | {요약}`, 원자 단위 커밋(통 커밋 금지) · 중간 단계 push 남발 금지 · 정본 `ORCHESTRATOR.md` 「커밋/푸시 포인트」
- 사내 전용(고객 단가 · 공수 포함), 외부 노출 금지

## 용어

| <div align="center"><sub>용어</sub></div> | <sub>뜻</sub> |
|:---|:---:|
| <sub>SSOT</sub> | <sub>월별 투입 인력표 — 모든 공수 수치의 단일 출처, 영역별 공수 · 역할 매트릭스 · WBS · 간트 · 히어로 · 푸터는 전부 여기서 파생</sub> |
| <sub>GATE</sub> | <sub>최종 렌더 직전 사용자 확인 지점 — 총 M/M · 인원 · 기간 · 범위 · 전제 + persona-review 결과</sub> |
| <sub>slug · id</sub> | <sub>프로젝트 식별자 `{고객}-{주제}`(예: `acme-shop-renewal`) — `_workspace/{slug}/`와 corpus id 공통</sub> |
| <sub>corpus(KB)</sub> | <sub>팀 공용 과거 산출물 저장소(사내 git `corpus` 브랜치) — 유사 선례 검색 · 완성본 환원 · 실제 공수 피드백</sub> |
| <sub>케이스 A-H</sub> | <sub>IA 확인 불가 · 프론트만 · 어드민까지 · 어드민만 · 리뉴얼/이관 · 디자인만 변경 · 화면 유지 + 백엔드 신규 · 신규 구축(`references/project-cases.md`)</sub> |
| <sub>delta 2축</sub> | <sub>표현(화면 · 디자인) 축과 구현(기능 · 백엔드) 축을 나눈 유지 · 변경 · 신규 분류 — 디자인 · 퍼블 공수와 개발 공수를 각각 도출</sub> |
| <sub>page_count · view_count</sub> | <sub>IA 이중 카운트 — 개발 · 이관 단위(탭 롤업) · 디자인 · 퍼블 단위(탭 포함)</sub> |
| <sub>디/퍼/개</sub> | <sub>디자인 · 퍼블리싱 · 개발 제작 공수 3분해</sub> |
| <sub>정성 신호</sub> | <sub>인테이크 답변(디자인 수준 · 상주 여부 · 기획 염려 등) — architect 공수 가중 근거</sub> |
| <sub>P0 · P1 · P2</sub> | <sub>persona-review 심각도 — 반드시 수정(진행 차단) · 권고 · 참고</sub> |

## 배포 · 설계 메모

### 배포 전 체크리스트

- [ ] `_workspace/` · `input/` · `output/` 비우기(테스트 산출물 제거)
- [ ] 절대경로 0건 확인(`grep -rn "d:/" .`)
- [x] `.gitignore`에 `_workspace/` · `output/` · `input/` 등록 완료(런타임 산출물 미추적) + `examples/*`(INDEX.md 제외) · `.env` · `.corpus/` 등록
- [x] playwright 런타임 산출(`.playwright-mcp/`) · 루트 캡처 이미지(`/*.png|jpg|jpeg`) `.gitignore` 등록 완료 + 캡처는 `_workspace/{slug}/` 저장 지침(site-analyst §9)

### 설계 결정 메모

- 위치: `.claude/` 대신 자급식 독립 폴더(당초 `works/` 하위 · 사용자 선택, 현재 리포 `agent/harness_st-etribe/`), 자동 트리거가 필요해지면 `.claude/skills/`로 승격 가능
- 모델 티어링: 추론(analyst · architect · solution-architect · persona-review · feedback-curator) = opus / 기계적(site-analyst · builder · qa) = sonnet, 실행 모드 = 서브에이전트(general-purpose에 역할 정의 주입)
- 인프라 기본 = AWS 형식 · AWS 공식 아이콘(외부 PNG) — 사용자 선호
- 렌더 기본 = 스크립트 결정적 렌더(`build_report.py`), LLM 수기 렌더는 폴백
- 배포 원격: 사내 GitLab `code.etribe.co.kr/smart-technology/harness_st` — `etribe` 브랜치(도구 코드 · clone 대상) · `corpus` 브랜치(데이터, orphan) · main은 protected(미사용)

### 표기 규칙

- 한국어 · 범위 표기 물결표 금지 → 하이픈(-), 단 HTML 본문 `~5스타일` 류는 허용 · 상세 `references/report-spec.md` §8

## 변경 이력

| <div align="center"><sub>날짜</sub></div> | <sub>변경</sub> | <sub>사유</sub> |
|:---|:---:|:---:|
| <sub>2026.11.13</sub> | <sub>README 전면 개편 — 목적 · 넣는 것 · 산출물 형태 · 요청 예시 · 진행 단계 순으로 재구성, 변경 이력 맨 아래로 이동</sub> | <sub>README만 읽고 사용법을 이해하도록(오너 지시)</sub> |
| <sub>2026.10.22</sub> | <sub>**Dan Jr. 등급 조회**(CLAUDE.md 동작 규칙 2): 인테이크·GATE 직전 `persona.md` 확인 — A 진행·B 보고·C 질문, 건너뛴 게이트는 완료 보고에 ID 표기</sub> | <sub>반복 결정을 Dan Jr.(사용자 골든셋)에 위임해 승인 게이트 축소(오너 지시)</sub> |
| <sub>2026.09.03</sub> | <sub>**★ 민감자료 정책 명문화**(CLAUDE.md): 추적 금지·재활용 금지·외부 반출 금지 3원칙 + `examples/*.html` git 미추적(.gitignore) + `scripts/check_leak.py`(샘플 고객 토큰 잔존 0건, qa 게이트) + 부모 저장소 `.githooks/pre-commit`(input/output/_workspace/examples 스테이징 차단)</sub> | <sub>하네스를 `dykim-claude-agents-skills/agent/`로 이동하며 과거 고객 완성본이 저장소에 올라간 사고 정정. 기존 자료는 샘플로만 쓰고 다른 문서에 재사용·적용 금지(오너 지시)</sub> |
| <sub>2026.06.11</sub> | <sub>초기 구성(에이전트4·레퍼런스5·템플릿3)</sub> | <sub>신규 구축</sub> |
| <sub>2026.06.11</sub> | <sub>도식화 범위 추가(개념도+AWS 인프라)</sub> | <sub>078 아너파라다이스 산출물 참고 요청</sub> |
| <sub>2026.06.11</sub> | <sub>`effort-estimation-methodology.md` 추가(레퍼런스6) + architect 연결</sub> | <sub>공수 산정 판단(측정단위·재스킨·재사용 비대칭·경계·함정13) 미문서화 빈칸 보강</sub> |
| <sub>2026.06.11</sub> | <sub>시운전(서울대 SDN) 4단계 완주 + qa가 phantom +4.0(29.0/33.0 불일치) 적발</sub> | <sub>하네스 검증</sub> |
| <sub>2026.06.11</sub> | <sub>CSS 스크립트 주입(`scripts/inline_css.py`) + base_template 마커화 + builder.md "CSS 직접작성 금지·도식 기본포함"</sub> | <sub>빌더가 CSS를 일부만 재작성해 디자인 드리프트(135→104 셀렉터)·도식 생략한 결함 교정</sub> |
| <sub>2026.06.11</sub> | <sub>`report-spec.md` 추가(생성 규칙 정본: 입력계약·6표·정합 a-h·4변형) + consistency-checklist를 a-h로 교체 + architect 자기검증</sub> | <sub>타 세션 실전 명세 흡수</sub> |
| <sub>2026.06.11</sub> | <sub>워크스페이스 루트 `CLAUDE.md`에 하네스 트리거 규칙 등록(요건문서→파이프라인, 콜드메뉴 금지)</sub> | <sub>works 하위 어느 폴더에서 띄워도 자동 인식되게(078에서 미작동 문제 해결)</sub> |
| <sub>2026.06.11</sub> | <sub>**배포 패키징**: 루트 `CLAUDE.md`(현관문) + `input/`·`output/`·`.gitignore` + 상대경로 이식성 확인</sub> | <sub>git 배포 모델 확정(폴더 clone→그 폴더에서 Claude Code 실행)</sub> |
| <sub>2026.06.11</sub> | <sub>`examples/` few-shot 라이브러리 추가(과거 완성본 4종 + INDEX)</sub> | <sub>스타일·도식·산정 보정 참고. 사내 전용(고객 데이터 포함)</sub> |
| <sub>2026.06.11</sub> | <sub>**corpus 집단기억** 추가(`corpus/`·`scripts/corpus.py`·`.env`) — 산출물 누적, 유사 선례 검색-증강, qa PASS 시 자동 push</sub> | <sub>팀이 쓸수록 데이터 축적→유사 건 일관성↑. 구조 B(1 repo), 인증 공용토큰(.env gitignored)</sub> |
| <sub>2026.06.11</sub> | <sub>GitLab 배포: code.etribe.co.kr/smart-technology/harness_st. **브랜치 2개 — `etribe`(도구 코드, clone 대상) / `corpus`(데이터, orphan)**. main은 protected(미사용)</sub> | <sub>도구·데이터 분리</sub> |
| <sub>2026.06.11</sub> | <sub>builder "클래스 발명 금지" 규칙 + `scripts/check_classes.py` orphan-class 가드(qa (i))</sub> | <sub>아너파라다이스 v1.0이 발명 클래스(.d1-no/.d2-chip 정의0·사용26)로 평문 깨짐 → 재발 차단</sub> |
| <sub>2026.06.11</sub> | <sub>**corpus를 별도 `corpus` 브랜치로 분리**(etribe=코드/corpus=데이터). corpus.py가 gitignored `.corpus/`에 클론·commit·push</sub> | <sub>도구 브랜치가 산출물 커밋으로 더러워지지 않게. 저장→push→검색 end-to-end 검증 완료</sub> |
| <sub>2026.06.11</sub> | <sub>**IA 추출 고도화**: `scripts/ia_extract.py`(메가패널 정본·탭/그룹/외부 type·page/view 이중카운트·footer·로그인·경계bleed 섹션비율 dedup) + `ia-extraction-upgrade.md`(오류7·규칙·스키마) + site-ia-extraction/analyst/methodology/report-spec 연결</sub> | <sub>슬림 nav만 긁어 3뎁스·footer·회원도메인 누락, 분리페이지 합침/탭 쪼갬으로 공수 오차. GS칼텍스 검증(page74/view76)</sub> |
| <sub>2026.06.11</sub> | <sub>KB 방법론 이식(독립): playbook 2종(요건누락·공수5축검증) + corpus 피드백 루프(`corpus.py feedback`, 실제공수→과소산정 경고) + frontmatter 스키마·confidence/데이터갭</sub> | <sub>사내 KB·운영하네스 분석 차용. 쓸수록 산정 정확도 누적</sub> |
| <sub>2026.06.11</sub> | <sub>인테이크(정성 신호: 기획염려·디자인레벨→공수 가중) + 모델 티어링(builder·qa→sonnet) + solution-architect 분리해 architect와 병렬</sub> | <sub>UX·비용·속도 동시 개선</sub> |
| <sub>2026.06.11</sub> | <sub>analyst 분리(site-analyst sonnet, 사이트 IA 병렬) + 에이전트별 ref 화이트리스트</sub> | <sub>앞단 병렬·토큰 절감</sub> |
| <sub>2026.06.11</sub> | <sub>**v1.1 시운전(아너파라다이스) GREEN** + 잠복결함 수정: `check_consistency.py`를 SDN하드코딩→**실제 표 파싱 범용**으로 재작성 · `check_classes.py` `<script>`제외(JS 거짓양성) · base_template `.hero-grid` · diagrams.css `.pub/.designv` 보강</sub> | <sub>qa 스크립트가 SDN전용 일회용이라 타 프로젝트 검증 불가했던 것 적발·수정. 43.0 정합 PASS·발명클래스 0</sub> |
| <sub>2026.06.12</sub> | <sub>**★ diagrams.css 미닫힌 `}` 수정(도식 깨짐 진짜 원인)** + `inline_css.py` 중괄호 균형 가드</sub> | <sub>078 추출 시 `@media` 닫는 `}` 1개 누락 → 뒤 AWS CSS 전체 파싱 붕괴 → 인프라 평면화(처음부터). Playwright 런타임 검증으로 `.aws-row` block→flex 확인. 클래스명/숫자 체크로는 못 잡던 CSS 파싱 오류라 빌드시 균형 가드 추가</sub> |
| <sub>2026.06.12</sub> | <sub>레이아웃 구조 고정(base_template `.layout/.sidebar`) + builder 인라인 override 금지 + `.pub/.designv` house-style로 이전</sub> | <sub>폭·타이틀이 즉흥 인라인으로 어긋남. 웅진 다이렉트 RFP end-to-end 검증 통과</sub> |
| <sub>2026.06.12</sub> | <sub>**산정 독립성**: 세션/메모리의 다른 프로젝트·수작업 수치 비교·앵커 금지, 참고원은 corpus KB뿐</sub> | <sub>추론값+근거코멘트→사용자 확인. 과거 수치 수렴 비교는 순환·편향</sub> |
| <sub>2026.06.12</sub> | <sub>**IA 표 룰(운영 피드백)**: 1노드=1row(·/쉼표 통합 금지·전 대메뉴 동일) + `.effort-table fixed`+colgroup+word-break:keep-all</sub> | <sub>별도 사이트에서 일부 대메뉴만 펼치고 일부 통합·한글 컬럼 글자깨짐</sub> |
| <sub>2026.06.12</sub> | <sub>**★ 스크립트 결정적 렌더 `build_report.py`(Phase 1-4)**: 구조화 JSON→HTML(레이아웃·IA표 1노드=1행·월별표 합계계산·영역별·간트·핵심요약·CSS·팔레트). 정합·구조·스타일을 코드가 보장</sub> | <sub>builder(LLM) 반복 사고(클래스발명·도식깨짐·레이아웃·phantom) 원천 차단. 웅진 다이렉트 9섹션 렌더·정합16검사0·런타임 GREEN</sub> |
| <sub>2026.06.12</sub> | <sub>렌더 기본경로를 스크립트로 채택(architect→`02_spec.json`→build_report, LLM builder=폴백) + 중간물 **프로젝트별 `_workspace/{slug}/`**</sub> | <sub>공유 _workspace 교차 덮어쓰기(GS칼텍스가 웅진 덮음) 사고 방지 + 결정적 렌더 정규화</sub> |
| <sub>2026.06.12</sub> | <sub>**build_report 4 렌더러 추가(역할매트릭스·WBS·개념도·인프라)** → 공수 6표 전부 + 도식 2종 결정적 렌더. css_block에 diagrams.css 인라인</sub> | <sub>도식까지 스크립트 kind화(손으로 안 그림). Playwright 런타임 GREEN(aws-row flex·eco-sat absolute·wbs phase색). etribe 9b8682a</sub> |
| <sub>2026.06.12</sub> | <sub>**★ 투입 연속성 가드 `build_report.compute_monthly`**: 톱니(중간월 0.5)·장기 반투입(0.5 2개월+ 연속) 자동 `[WARN]` + member `parttime:true` 예외</sub> | <sub>방법론 §9·qa (l)이 이미 전제하던 WARN을 정작 코드가 안 내보내던 빈칸. GS칼텍스 런에서 PM·기획·안정화 3행 톱니/장기0.5 적발(qa 1차 미검출) → 가드 구현·재배치(총 47.0 보존, 패턴 현실화)</sub> |
| <sub>2026.06.12</sub> | <sub>목차(사이드바) 제목 끝 괄호 부연 자동 제거(`nav_label`) + architect title 규칙(부연은 area로)</sub> | <sub>목차에 `(SSOT)`·`(주 단위/20주)` 등 군더더기 노출. etribe 8e7e0fc</sub> |
| <sub>2026.06.12</sub> | <sub>**KB 중간물 스냅샷**: `corpus.py snapshot`(단계/게이트마다 `_workspace/{slug}`→`deliverables/{id}/workspace/` 커밋, index 불변→검색 노이즈0) + `save --ws` + 안정 id 규칙(id=slug={고객}-{주제})·corpus 디렉토리 구조 문서화</sub> | <sub>완성본뿐 아니라 작업 과정도 KB에 누적(이력·감사). etribe 346f645</sub> |
| <sub>2026.06.12</sub> | <sub>**파일 네이밍 표준 전면 통일**: `_workspace/{slug}/NN[x]_{artifact}`(bare 금지) — 01a_site-ia·01_analysis·02_spec·02b_solution·03_draft·04_qa·05_meta. 레거시명 전부 정리, ORCHESTRATOR에 정본 표 신설, 6에이전트+CLAUDE.md 정렬</sub> | <sub>산출물명 제각각·slug 누락(교차 덮어쓰기 원인) 해소</sub> |
| <sub>2026.06.12</sub> | <sub>**사용자가이드.html**(Claude Code 대화 흐름 형식: 실제 사용 시나리오 + 안내 캡션) 추가</sub> | <sub>팀 배포용 사용법 가이드</sub> |
| <sub>2026.06.12</sub> | <sub>**투입 연속성 자동 가드**: `build_report.check_sawtooth`(톱니·0.5 2개월+ 연속 → [WARN]) + 방법론§9·architect·qa(l). 정당 파트타임은 member `parttime:true` 예외</sub> | <sub>연속 투입 인력 중간월 0.5 불가 정책 부재 보완</sub> |
| <sub>2026.06.12</sub> | <sub>**인테이크 항목 추가: 수행형태(상주/비상주)·예상 인프라 포함**. 비상주→퍼블·개발 -최대30%(AI활용, 기획/디자인 제외), 상주→감면없음+상주 인력 장기0.5 금지(parttime 예외 불가). 미응답 시 상주 가정</sub> | <sub>최초 사용자 확인 사항·수행형태별 공수 차이 미반영</sub> |
| <sub>2026.06.12</sub> | <sub>**QA 인력 = 기획자 겸임(표준)**: QA 전담 직군 금지, 기획 1명 막달(통합테스트·UAT·오픈)까지 유지. build_report 가드(QA 전담 직군·기획 막달0 → [WARN])</sub> | <sub>"기획자 없이 QA만" 구성 불가 정책 명문화</sub> |
| <sub>2026.06.12</sub> | <sub>**테스트 구간 인력 감쇠(§9)**: 막달은 신규 제작 없음 → 디자인·퍼블 2명+ 투입 시 1명만 잔류(PM·기획·개발은 풀 가능, 디자인 위주면 개발도 감원). build_report 가드(막달 디자인/퍼블 2명+ → [WARN])</sub> | <sub>다인 디자인/퍼블이 끝까지 풀 잔류하는 과다 산정 방지</sub> |
| <sub>2026.06.12</sub> | <sub>**IA 압축 자동 가드**: build_report가 children 없는 대메뉴 desc에 ·가 2개+면 [WARN](하위를 한 셀에 압축). architect IA는 하위를 반드시 `children[]`로 분해 명시</sub> | <sub>2뎁스 메뉴가 개별 행으로 안 펴지고 압축됨. 렌더러·샘플 무관(children 주면 펴짐), IA 데이터 생성 문제</sub> |
| <sub>2026.06.12</sub> | <sub>**root 오염 정리**: `.playwright-mcp/`·루트 캡처 이미지(`/*.png\|jpg\|jpeg`) `.gitignore` 차단 + site-analyst §9 캡처를 `_workspace/{slug}/` 저장 지침. 기존 루트 캡처는 `input/`로 이동</sub> | <sub>playwright 산출·사이트 캡처가 root에 쌓여 git 오염</sub> |
| <sub>2026.06.12</sub> | <sub>**사용자가이드.html 보강**: 인테이크 질문(디자인·일정·상주/비상주·인프라 포함) 대화 추가, 비상주 -감면·인프라 포함 흐름 반영</sub> | <sub>물어봐야 할 항목을 대화 형식으로 보강</sub> |
| <sub>2026.06.12</sub> | <sub>**관리자 IA 유추 강제**: IA group `admin:true` 플래그 + build_report 구분행("관리자 영역·유추·추정") + 누락 가드([WARN]). analyst 관리자 유추 필수 격상(표준 어드민 세트), architect IA=사용자+관리자 둘 다</sub> | <sub>프론트만 조사하고 관리자 IA가 누락/미구분되던 문제(렌더·가드에 admin 개념 부재)</sub> |
| <sub>2026.06.12</sub> | <sub>목차 '공수 산정 —' 묶음 접두 자동 제거(nav_label) + 하위표 title 표이름만·번호 8-1~8-6</sub> | <sub>목차가 "공수 산정 — 영역별 공수"로 장황·08 6번 반복</sub> |
| <sub>2026.06.12</sub> | <sub>**인테이크 순차 질문화**: 작성 시작 시 필요 항목을 한꺼번에 안 묻고 **하나씩** 질문→답→진행(디자인→일정→상주/비상주→인프라→TO-BE→누락). 한꺼번에 답하면 수용</sub> | <sub>한 번에 폭탄 질문 대신 대화형 단계 진행</sub> |
| <sub>2026.06.12</sub> | <sub>**AS-IS 인프라 이미지 판독 + TO-BE 제안**: `extract_assets.py`(docx/pptx 임베드 이미지 추출) + analyst 판독 지침 + solution-architect AS-IS(Read 판독)→TO-BE 2섹션+마이그레이션. GS칼텍스 RFP 구성도 2종 판독 실증</sub> | <sub>RFP 인프라 구성도 이미지를 읽어 현행 파악·제안까지 대응</sub> |
| <sub>2026.06.12</sub> | <sub>IA 표 공수 컬럼 조건부: effort가 하나도 없으면(메뉴구조도) "공수(M/M)" 컬럼 자동 생략(3컬럼)</sub> | <sub>IA 정보구조도에 빈 공수 컬럼이 남아 어색했던 시각 문제(GS칼텍스 테스트 발견)</sub> |
| <sub>2026.06.12</sub> | <sub>**서술형 섹션 6종 전용 템플릿 + 번호 자동화**: build_report에 overview(메뉴칩)·modules(menu-list)·narrative(다크 final-report)·questions(확인질문)·coverage(요건표)·insight 렌더러 추가(cards=기존 summary 재사용). `no` 미지정 시 순번 자동. 기존 산출물 8종 클래스 패턴 실증→전용화. 신규 6종 렌더·발명클래스0·Playwright 런타임(menu-grid/list·final-report 다크·effort-grid·insight·번호 1-5) GREEN</sub> | <sub>prose 자유HTML이던 서술형 섹션 스타일 드리프트 차단(JSON 주입 100% 재현)</sub> |
| <sub>2026.06.12</sub> | <sub>측정 철학 정정: IA=페이지(기능) 단위, "스타일 N"은 한 페이지 내 표시 변형일 때만(상품 56개=상품상세 1페이지·스타일은 디자인 산정에)</sub> | <sub>IA를 스타일 수로 축약하는 혼동 제거</sub> |
| <sub>2026.06.12</sub> | <sub>**RFP 커버리지 + 확인 질문 + 인프라 AS-IS 동반**: analyst RFP 요건 전수 항목화 → architect 요건 커버리지 대조표(반영/부분/제외+사유/미확인) + "확인 필요 질문" 항상 마지막 섹션(추정·데이터갭 중립 질문) / 인프라 제안(TO-BE)은 AS-IS와 쌍. build_report 가드(확인질문 누락·TO-BE 단독 → [WARN]), qa (l)+(m) 점검</sub> | <sub>RFP 반영 누락 확인·추측분 확인 리스트화·제안 인프라 현행 대비</sub> |
| <sub>2026.06.12</sub> | <sub>**출력 위치 가드 + 전체경로 강제**: build_report `-o`가 `_workspace/`·`output/` 밖(temp·홈)이면 [WARN]. ORCHESTRATOR 명령 예시를 전체경로(`_workspace/{slug}/...`)로, temp/cwd 금지 규칙. qa (l)을 'build_report 모든 WARN 0'으로 일반화(IA압축·관리자누락·인력정책·출력위치 무시 금지)</sub> | <sub>산출물이 temp 등 다른 장소에 흩어져 렌더되던 문제(상대경로+cwd 어긋남)</sub> |
| <sub>2026.06.12</sub> | <sub>IA 표 공수 컬럼 조건부 생략(effort 전무 시) + 관리자 출처 라벨 `admin_label`(자료 기반/유추)</sub> | <sub>IA 빈 공수 컬럼·관리자 자료를 유추로 오표기한 시각/표기 문제</sub> |
| <sub>2026.06.14</sub> | <sub>갭 #2(우산 시스템 비기능 전이): RFP가 우리 대상+외부/현행 시스템을 한 우산(무장애/레거시/기간계) 아래 묶으면 → 정체·경계·HA등급 상속·전환경계·I/F무단절 4종을 확인질문 표준 포함. playbook 공통·analyst</sub> | <sub>실런에서 I/F 규격은 물었으나 "무장애 HA 전이가 홈페이지에 적용되나" 토대질문 누락(Q7 1개뿐)</sub> |
| <sub>2026.06.14</sub> | <sub>GS칼텍스 전체테스트 발견 갭 반영: ① 외부사 시스템(VAN·PG·기간계)=연계 I/F만, 시스템 전환개발 금지(architect·analyst·qa(p)⑥) ② corpus.py search 자유어 쿼리+태그 부분매칭(exact→substring, positional/--q)</sub> | <sub>실런에서 VAN 174를 우리 구축으로 오인(112→GATE정정 77) + search 0건으로 index 수동조회</sub> |
| <sub>2026.06.14</sub> | <sub>피드백 정정: 자동반영·멀티유저 prefs 제거 → feedback-curator는 "오너용 수정 제안 리포트"만 생성(corpus.py propose→feedback/proposals.md 검토큐). 에이전트 수정은 오너 단독·승인 후 /harness</sub> | <sub>에이전트 수정은 오너만, 피드백은 이해하기 쉬운 제안용</sub> |
| <sub>2026.06.14</sub> | <sub>수정 피드백 루프: feedback-curator(opus·on-demand) — 확정된 대화 수정을 취향(user)/공통개선(global) 분류해 corpus.py pref로 기록(prefs/{user}·feedback/agent-improvements). 취향=다음부터 자동, 공통=/harness 반영. 사용자가이드에 흐름 추가</sub> | <sub>한 사람 기준 하네스 → 사용자별 취향 반영 + 공통 개선 환류</sub> |
| <sub>2026.06.14</sub> | <sub>최종 HTML 자동 버전관리: corpus.py put-html(생성/수정시 버전 커밋·태그 이동)·get(최신/특정버전 받아보기). save의 index를 update-or-append로(재작업 중복 방지). 다중 사용자 대응</sub> | <sub>최종 HTML 자동 git 관리 + 최신본 조회 + 버전관리 요청</sub> |
| <sub>2026.06.14</sub> | <sub>기획 과소 가드: 기획 베이스=페이지수+난이도, 디자인 고도화 시 기획 동반 상승. build_report [WARN](기획 실무<디자인×0.5 / 기획1명vs디자인+퍼블4명+). 방법론§9·architect</sub> | <sub>테스트결과 기획1 vs 디자인4 불균형 반복(GS: 기획5.5/1명 vs 디자인12.5/3명+퍼블14/4명)</sub> |
| <sub>2026.06.14</sub> | <sub>커밋/푸시 포인트 정리: corpus.py save가 섹션 원자별 1커밋(kb(type):id\|…)+kb(report)+태그 kb/{id}, snapshot/feedback 메시지 검색형 통일. ORCHESTRATOR "커밋/푸시 포인트" 정책+리치 05_meta 스키마. 옛 meta.md 구조 잔재 제거(CLAUDE·ORCHESTRATOR)</sub> | <sub>한 덩어리 커밋→git log 검색 뭉툭. 원자 단위 커밋+검색형 메시지+태그로 빠른 취득</sub> |
| <sub>2026.06.14</sub> | <sub>corpus KB 재설계(사내 kb 규약 채택, 우리 산출물 정렬): 섹션 원자 9종(overview·direction·ia·approach·infra·estimates·scope·questions·decisions)+케이스별 종합 cases/(범위→확인→공수 밴드)+patterns 14. corpus.py search 강화(밴드 카드+사슬 ref). 7폴더 9건 적재</sub> | <sub>단순 카드+HTML 재분석 구조 → 유형별 범위·확인·공수 인과를 바로 참고</sub> |
| <sub>2026.06.14</sub> | <sub>버전 변천 학습 반영(웅진081·코스모진078 23판 분석): ⑤표현절제(과장네이밍 금지) ⑥불확실시나리오 본산정 분리 ①수치변동 1:1사유+확정도(탐색/제안/확정) ④범위경계 in/out표+기존소스인계 확인. architect·builder·analyst·qa(s)·report-spec§8</sub> | <sub>사용자가 매 버전 적용한 관점을 에이전트에 내재화</sub> |
| <sub>2026.06.14</sub> | <sub>corpus 참조 가시화·흔적 강제: Phase1.5 corpus 상태 한줄 보고(연결/0건/미연결사유) + analyst "참조 선례" 절·architect measure_note 선례 인용 필수 + 독립성 규칙에서 "corpus=허용된 참조(인용 대상)" 분리 + corpus.py 미연결 사유 명확화</sub> | <sub>산출물에 git KB 참조 흔적이 안 보임(테스트폴더 토큰부재로 조용히 skip + 소프트 단계라 흔적 미기록)</sub> |
| <sub>2026.06.13</sub> | <sub>2차 비용 최적화(같은 결과·최소 비용): persona-review=methodology §13·§1.5만 / architect·analyst corpus-kb=검색부분만 / 02_spec.md=짧은요약·02b.md=기본생략 / 중간 스냅샷→GATE+최종 save만</sub> | <sub>per-call 컨텍스트 적재·출력토큰·런타임 git I/O 낭비 제거(최종 산출물 동일)</sub> |
| <sub>2026.06.13</sub> | <sub>콘텐츠 발전도 검토 추가 + 파이프라인 비용 최적화: 발전도(RFP 나열↔고도화)를 3c persona-review estimate에 흡수(신규 opus 0) + qa(r) 얕음 1차탐지 / 3b·5b 조건부화 → 평시 opus 5→3회</sub> | <sub>RFP 충분히 발전 검토 담당 부재 + 최소 비용 요청</sub> |
| <sub>2026.06.13</sub> | <sub>인테이크 재정의: 고정 필수 5(디자인·개발방법·인프라구축실작업·상주비상주·기간, RFP 무관 항상) + 동적 RFP 질문 ⑥(2-4개 적극 도출). ORCHESTRATOR·CLAUDE·사용자가이드</sub> | <sub>개발방법·인프라 실작업 분기가 고정질문에 없거나 모호 / RFP 근거 확인질문은 동적·적극 도출이어야</sub> |
| <sub>2026.06.13</sub> | <sub>인테이크 질문 ⑥ 가드: 확인 질문은 RFP 내부 미상·모호 항목만, RFP 없는 기능(챗봇·AI) "필요하세요?" 타진 금지. ORCHESTRATOR⑥·CLAUDE§2·playbook</sub> | <sub>출력 가드(RFP없는 챗봇 금지)를 인테이크 질문으로 우회 — GS 테스트에서 챗봇 필요 여부를 사용자에게 물음</sub> |
| <sub>2026.06.13</sub> | <sub>섹션 도입 prose 가독성 규칙: 짧은 리드(1-2문장)+구조화(불릿/표), 런온 한 문단 금지. 유지/변경/신규·스펙 나열은 delta 표/불릿으로. builder§9·architect·report-spec§8</sub> | <sub>섹션 도입부가 현행·변경·신규·스펙을 한 문단에 욱여넣어 가독성 저하</sub> |
| <sub>2026.06.13</sub> | <sub>**★ 프로젝트 케이스 매트릭스 + 2축 delta(케이스 커버리지 점검)**: `references/project-cases.md` 신설(A.IA확인불가 / B.프론트만 / C.어드민자료 / D.어드민만[프론트X] / E.리뉴얼 / F.디자인만변경[개발0] / G.화면유지+백엔드신규[개발=신규] / H.신규구축). analyst 착수 시 케이스 판별→01 명시. **delta를 표현(화면)/구현(기능) 2축으로** 분리(F·G 오판 차단). architect/qa(q)/방법론§1.5/report-spec(D) 반영</sub> | <sub>드라이런으로 D·F·G 갭 발견(화면 유지를 개발 0으로 오판 등) → 보강</sub> |
| <sub>2026.06.13</sub> | <sub>**★★ IA delta → 작업 도출 → 공수 추론 사슬(핵심 구조)**: 방법론 §1.5 신설 — 현행 IA를 RFP 대비 유지/변경/신규 분류 → 프론트 변경의 관리자 파생 작업 → 그 분류에서 공수 도출(영역 desc에 "현행X→분류→작업→공수" 근거). analyst(IA delta 태깅·관리자 파생)·architect(공수 delta 도출·"IA 변경 분석" 섹션)·qa(q)·persona-review·report-spec</sub> | <sub>산출물이 "RFP 포인트→공수 점프"로 빈약 — IA·기능엔 delta 사슬이 없었음(인프라만 delta)</sub> |
| <sub>2026.06.13</sub> | <sub>**★ RFP 충실성·범위 정확성 강화(실테스트 5결함 교정)**: ① RFP 없는 기능(챗봇) 추가 금지·현행은 "유지"로만 ② 요건 비약 금지(GEO/SEO=콘텐츠·구조 최적화 SW지 색인엔진 인프라 아님) ③ 인프라 구축은 공수 작업 아님(제시만, 영역별 제외) ④ 관리자 IA 기본 골격(로그인·운영자관리·권한·보안/감사) 필수 ⑤ 역할 매트릭스 투입인력 세분(빈 cells 금지). analyst/architect/solution-architect/qa(p)/방법론§11/report-spec</sub> | <sub>GS칼텍스 실테스트 산출물에서 5결함 발견</sub> |
| <sub>2026.06.13</sub> | <sub>**★ persona-review 에이전트 신규(멀티 페르소나 검토) + 2지점 삽입**: PM·아키텍트·개발·디자인/퍼블·고객 다관점으로 ① GATE 전(공수·인사이트, `02c`) ② qa 후 최종 전(콘텐츠, `04b`) 검토 → P0면 반려. qa(규칙·정합)와 분리된 '판단·설득력·고객 수용성' 검증</sub> | <sub>인사이트·공수·콘텐츠에 다관점 페르소나 검토가 파이프라인에 없었음(전역 review-board는 수동·미연결)</sub> |
| <sub>2026.06.13</sub> | <sub>**IA Front/Admin 분리 표시 + admin 조건부**: admin이 존재하는 사이트면 `Front IA 정보구조도`/`Admin IA 정보구조도` 2섹션 분리(통합+구분행은 폴백). **admin 없는 사이트(정적·소개형)는 Front만** — 억지 유추 금지. 관리자 누락 가드 제거(admin 강제 안 함). analyst·architect·site-ia·report-spec 반영</sub> | <sub>IA에 admin 들어가면 분리 표시 요청 + admin은 항상 있는 게 아님</sub> |
| <sub>2026.06.13</sub> | <sub>**★ TO-BE 인프라 = AS-IS delta(베스트안)**: 일반 모범 구성도 금지 → AS-IS 각 요소를 유지/변경/신규/제거로 분류·근거(RFP·현행) 표기, 현행 필수요소(이중화·환경분리·연계·IDC) 근거없이 제거 금지. 마이그레이션을 delta 표로. solution-architect·infra-diagram 가이드·qa (o)</sub> | <sub>TO-BE가 AS-IS 무시하고 일반 단순 구성도로 가서 현행 연계 4종 등 필수요소 누락</sub> |
| <sub>2026.06.13</sub> | <sub>**★ 고객 제공 구성도는 원본 그대로(figure kind)**: AS-IS 인프라가 고객 제공 도식이면 `infra`(aws 그리드)로 다시 그리지 말고 **원본 이미지를 `figure`로 임베드**(로컬→base64 인라인, self-contained). solution-architect 지침 + AS-IS/TO-BE 가드 figure 인식</sub> | <sub>aws 그리드 템플릿이 온프레미스 토폴로지(L4·서버명·연결선·VM·연계)를 표현 못 해 고객 구성도를 요약·변형한 사고 — 제공 도식 변형 금지</sub> |
| <sub>2026.06.13</sub> | <sub>**★ 자료 > 유추 원칙 + 입력 자료 출처 인벤토리(하네스 진화)**: analyst에 "입력 자료 출처 인벤토리" 절 신설(영역×출처 매핑: 자료제공/부분/없음), report-spec 입력계약 "자료 우선" 행, ORCHESTRATOR Phase1 인벤토리, qa (n) 제공자료 반영 점검(자료를 유추로 표기 시 FAIL), 관리자=유추 편향→케이스 분기</sub> | <sub>**근본 원인: "관리자=유추" 디폴트 편향 + 입력 자료 출처 분류 단계 부재 → 자료(xls ADMIN 79기능) 무시·유추 사고. IA·기능·인프라·연동 전 영역 일반화**</sub> |
| <sub>2026.08.19</sub> | <sub>**★ 하우스 스타일 전면 개정 — warm paper × near-black 에디토리얼**: `house-style.css` 재작성(팔레트 cream/ink · radius 0-2px · 그라디언트·박스섀도 제거 · Paperlogy+Pretendard 웹폰트 · 간트/WBS `--ph-*` 저채도 9색 램프 · `@page A4` 인쇄 규칙 신설). **클래스명 100% 유지**(check_classes·build_report 호환), 구 `--brand` 계열은 별칭으로 잔존(diagrams.css·spec palette 주입용). 부수: `diagrams.css` `.pub/.designv` 를 토큰 참조로(구 파스텔이 house-style을 덮고 있었음) · `build_report.py` 구 파스텔 role 배경 매핑 + insight 제목 데코 이모지 제거 · `base_template.html` 주석/이모지 정리 · house-style-guide·report-spec §4 개정</sub> | <sub>기준 레퍼런스 = 신승 비즈니스AI플래너 권한정책 매트릭스. 파랑 브랜드+그라디언트 카드 톤이 문서형 산출물에 과했음. NH농협손해보험 spec 재렌더로 검증(정합 13검사 0실패 · 발명클래스 0)</sub> |
