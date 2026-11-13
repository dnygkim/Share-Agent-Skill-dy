# prd — 공수산정 · 기초 PRD(RRD) 생성 하네스

RFP · 회의록 · AS-IS 실측 자료를 넣으면 산정 단위 정의부터 공수 3축 분해 · 리스크까지 담은 공수산정 및 기초 PRD(RRD) 문서를 만들고, 이후 회의록 · 고객 답변이 들어올 때마다 프로젝트별 STATE.md를 먼저 고쳐 바뀐 섹션만 다시 쓰는 살아있는 문서 하네스

## 한눈에 보기

| <div align="center"><sub>항목</sub></div> | <sub>내용</sub> |
|:---|:---:|
| <sub>목적</sub> | <sub>견적 근거 · 착수 내부 배포 · 고객 RRD 3용도를 함께 채우는 구조화 문서<br>「무엇을 1단위로 세는가(산정 단위)」에서 출발하는 공수 산정 · 거품과 누락 동시 제거</sub> |
| <sub>이럴 때 사용</sub> | <sub>수주 전 가견적 · 공수 근거 작성<br>착수 시 구성 인력에게 프로젝트 전체 그림 전달<br>고객과 범위 · R&R · 전제조건 합의<br>미팅 뒤 회의록 · 고객 답변 반영 갱신</sub> |
| <sub>넣는 것</sub> | <sub>`input/{프로젝트}/`에 RFP(`.md` · `.docx` · `.pdf`) · 회의록 · 추가자료 · 가견적 요청 메일 · AS-IS 실측 자료(URL · 캡처 · HTML · DB 스키마)<br>유입 차수별 하위폴더 권장(`00_rfp/` · `01_meeting_0707/`) · 경로 · URL을 대화로 전달해도 가능</sub> |
| <sub>나오는 것</sub> | <sub>PRD 본문 `output/{프로젝트}/{NN}_{사업명}_PRD_v{X.Y}.{html\|md\|docx}` · 헤더 + 10섹션 + 자기검증 8항목 판정표<br>지속 상태 `_workspace/{프로젝트}/STATE.md` + 단계 산출물 6종(`01_diagnosis.md` – `06_qa.md`)</sub> |
| <sub>시작 방법</sub> | <sub>`agent/prd/` 폴더에서 Claude Code 실행 → `CLAUDE.md` 자동 로딩 → 「이 RFP로 PRD 만들어줘」 요청</sub> |
| <sub>연계</sub> | <sub>뒤 단계: `../proposal` 제안서 본문 슬라이드 · 스킬 `rfp-analysis-research` · `ux-journey-insight` · `proposal-structure-validation`의 입력으로 활용<br>공수 정본: `../harness_st-etribe`(공수산정 HTML) 산출물이 있으면 그 수치가 최우선 정본 · 재산정 생략</sub> |

## 이렇게 요청

| <div align="center"><sub>상황</sub></div> | <sub>요청 예시</sub> | <sub>나오는 것</sub> |
|:---|:---:|:---:|
| <sub>신규 생성</sub> | <sub>`이 RFP로 PRD 만들어줘`<br>`이 자료로 공수산정 문서 뽑아줘`</sub> | <sub>인테이크 → GATE 2회 → `01_{사업명}_PRD_v0.1.html` + STATE.md</sub> |
| <sub>회의록 · 고객 답변 반영</sub> | <sub>`회의록 반영해서 PRD 업데이트해줘`</sub> | <sub>STATE.md 선갱신 → 영향 섹션만 재생성 → v0.2 + 버전 히스토리 1줄</sub> |
| <sub>특정 섹션만 수정</sub> | <sub>`공수 표만 다시`<br>`리스크 매트릭스만 보강해줘`</sub> | <sub>해당 Phase 산출물만 수정 → STATE.md 정합 확인 → output 재조립(경미 수정은 제자리 갱신)</sub> |
| <sub>완전히 새 판</sub> | <sub>`처음부터 새 판으로 다시 만들어줘`</sub> | <sub>기존 `_workspace/{프로젝트}/` → `{프로젝트}_prev/` 이동 후 신규 생성</sub> |

**예시 대화**

```
사용자: input/acme-shop/에 RFP 넣었어. 이 RFP로 PRD 만들어줘
에이전트: (인테이크 → STATE.md 생성 → 현황 진단 → 산정 단위) [GATE 1] 산정 단위 = 템플릿 · 환산 테이블 제시. 이 단위로 확정할까요?
사용자: 확정
에이전트: [GATE 2] 시나리오 A 기본 · B 절감 · C 전수용 · D 추천 매트릭스 제시. 추천안 D로 확정할까요?
사용자: D로 진행
에이전트: output/acme-shop/01_{사업명}_PRD_v0.1.html 완성 · 자기검증 8항목 판정 첨부
사용자: (다음 미팅 뒤) 어제 미팅 회의록 반영해줘
에이전트: STATE.md Q-03 ANSWERED · D-05(오픈일) 등록 → 04_effort · 05_narrative만 재생성 → v0.2
```

## 진행 단계

| <div align="center"><sub>STATE.md 상태 · 요청</sub></div> | <sub>모드</sub> |
|:---|:---:|
| <sub>STATE.md 부재</sub> | <sub>**신규 생성** · Phase 1부터 전체 파이프라인</sub> |
| <sub>STATE.md 존재 + 새 자료 · 답변 유입</sub> | <sub>**업데이트** · 아래 업데이트 절차(전체 재생성 금지)</sub> |
| <sub>STATE.md 존재 + 부분 수정 요청</sub> | <sub>**부분 재실행** · 해당 Phase만</sub> |
| <sub>STATE.md 존재 + 완전히 새 판 요청</sub> | <sub>기존 폴더 `{프로젝트}_prev/` 이동 후 신규 생성</sub> |

### 신규 생성

```
① 인테이크 → ② 현황 진단 → ③ 산정 단위 → GATE 1(단위 승인) → ④ 범위 · 전략 → ⑤ 공수 산정 → GATE 2(추천안 승인) → ⑥ 서사 · 리스크 → ⑦ 검증 · 조립
```

| <div align="center"><sub>단계</sub></div> | <sub>하는 일</sub> | <sub>사용자 할 일</sub> | <sub>결과물</sub> |
|:---|:---:|:---:|:---:|
| <sub>① 인테이크</sub> | <sub>입력 인벤토리(영역 × 출처 매핑, 자료 우선) · 최대 6문항 순차 질문 · STATE.md 생성</sub> | <sub>질문에 답변(한꺼번에 답변 가능 · 「알아서」면 표준 가정)</sub> | <sub>`_workspace/{프로젝트}/STATE.md`</sub> |
| <sub>② 현황 진단</sub> | <sub>AS-IS 직접 측정(코드 · HTML · DB · 화면) → 실측값 + 견적 시사점 · 실측 불가 영역은 `[착수 후 분석 예정]`</sub> | <sub>—</sub> | <sub>`01_diagnosis.md`(§2)</sub> |
| <sub>③ 산정 단위</sub> | <sub>1단위 선언(페이지 · 화면 · 템플릿 · 모듈 · 기능 · API) + 인스턴스 → 고유 단위 환산 테이블 · 재사용 구조</sub> | <sub>—</sub> | <sub>`02_units.md`(§3)</sub> |
| <sub>**GATE 1 · 산정 단위 승인**</sub> | <sub>단위 선언 + 환산 테이블 제시 · 승인 전 공수 수치 산출 보류</sub> | <sub>**채택 단위와 고유 단위 합계 확인 후 승인**</sub> | <sub>STATE.md 산정 단위 확정본 · D-xx 기록</sub> |
| <sub>④ 범위 · 전략</sub> | <sub>요구사항 · 범위(수용 · 확인 필요 · 제외) · 대응 전략 · 연동 흐름 · R&R · 영향도</sub> | <sub>—</sub> | <sub>`03_scope.md`(§4 · 5 · 6) · P-xx · Q-xx 등록</sub> |
| <sub>⑤ 공수 산정</sub> | <sub>영역 × 직군 × 등급 3축 분해 · 월별 투입 · 시나리오 A–D 매트릭스 · 절감 카드 · WBS · 간트</sub> | <sub>—</sub> | <sub>`04_effort.md`(§7)</sub> |
| <sub>**GATE 2 · 공수 추천안 승인**</sub> | <sub>시나리오 A 기본 · B 절감 · C 전수용 · D 추천 매트릭스 제시</sub> | <sub>**채택 시나리오 확인 후 승인** · 승인한 안의 수치가 공수 정본</sub> | <sub>STATE.md 공수 정본(총 M/M · 직군 분해 · 채택안)</sub> |
| <sub>⑥ 서사 · 리스크</sub> | <sub>퀵 스탯 헤더 · 개요(AS-IS → TO-BE) · 진행 흐름 · 종합 총평 · 사전 확인 · 리스크</sub> | <sub>—</sub> | <sub>`05_narrative.md`(§0 · 1 · 8 · 9 · 10)</sub> |
| <sub>⑦ 검증 · 조립</sub> | <sub>자기검증 8항목 · 총 M/M 정합(±10%) · `[확인 필요]` 전수 역검증 → 헤더 + 10섹션 조립</sub> | <sub>산출물 확인</sub> | <sub>`06_qa.md` + `output/{프로젝트}/01_{사업명}_PRD_v0.1.html`</sub> |

- 작성 순서 근거: 실측(§2) → 단위(§3) → 공수(§7)를 먼저 확정한 뒤 개요 · 흐름 · 총평(§1 · 8 · 9) 정리 · 근거와 서사의 어긋남 방지
- 특정 섹션만 요청하면 파이프라인 전체가 아니라 해당 Phase만 단독 실행
- 착수 · 완료 시 현재 시각 한 줄 표시

### 인테이크 질문

| <div align="center"><sub>#</sub></div> | <sub>질문</sub> | <sub>답 예시</sub> | <sub>기본값</sub> |
|:---|:---:|:---:|:---:|
| <sub>①</sub> | <sub>클라이언트명 / 사업명</sub> | <sub>`ACME 쇼핑몰 리뉴얼`</sub> | <sub>자료에 있으면 추출 후 확인만</sub> |
| <sub>②</sub> | <sub>입력자료 확정(정본 파일)</sub> | <sub>`input/acme-shop/00_rfp/`의 RFP</sub> | <sub>—</sub> |
| <sub>③</sub> | <sub>프로젝트 유형</sub> | <sub>리뉴얼 · 신규 구축 · 고도화 · AI · 신기술</sub> | <sub>유형별 중점 · 경량 섹션 결정에 사용</sub> |
| <sub>④</sub> | <sub>AS-IS 실측 가능 여부</sub> | <sub>대상 URL · 소스 · CMS 접근 가능 여부</sub> | <sub>불가 시 섹션 2 = `[착수 후 분석 예정]`</sub> |
| <sub>⑤</sub> | <sub>출력 포맷</sub> | <sub>HTML · Markdown · DOCX</sub> | <sub>HTML</sub> |
| <sub>⑥</sub> | <sub>(HTML 선택 시) 스타일 확인 · 「기본 스타일로 추출할까요?」</sub> | <sub>「기본으로」 · 「CI 적용」</sub> | <sub>하우스 스타일 · CI는 요청 시 HEX 확정 후 정본 §2b 방식</sub> |

- 추론 가능한 항목은 질문 생략 · 한꺼번에 답하면 수용 후 남은 것만 질문 · 「알아서」면 표준 가정
- 질문 · GATE 직전 Dan Jr. 등급 조회(`~/.claude/persona/persona.md`) · A 등급은 기본값 진행, B는 진행 후 완료 보고에 한 줄, C · 미등록은 질문 · 건너뛴 게이트는 완료 보고에 ID 표기
- GATE 1 · 2(산정 단위 · 추천안)는 persona.md에 없는 결정이라 항상 사용자 승인

### 업데이트 (새 정보 유입 시)

```
새 자료 추가 → ① 분류 → ② STATE.md 선갱신 → ③ 영향 섹션 매핑 → ④ 델타 재생성 → ⑤ 정합 재검증 · 버전업
```

| <div align="center"><sub>단계</sub></div> | <sub>하는 일</sub> | <sub>사용자 할 일</sub> | <sub>결과물</sub> |
|:---|:---:|:---:|:---:|
| <sub>① 분류</sub> | <sub>새 자료를 `input/{프로젝트}/{NN}_{유형}_{날짜}/`에 배치 · 정보 유형 분해(Q 답변 · 새 확정 · 새 확인 필요 · 전제 성립/붕괴 · 범위 변경)</sub> | <sub>새 회의록 · 답변을 `input/{프로젝트}/`에 추가 후 「회의록 반영해서 PRD 업데이트해줘」</sub> | <sub>분류 결과</sub> |
| <sub>② STATE.md 선갱신</sub> | <sub>Q-xx `OPEN → ANSWERED` · 확정 사항 D-xx 신규 등록 · 전제 P-xx 상태 변경 + 재산정 트리거 판단</sub> | <sub>기존 확정(D-xx)과 모순되는 정보면 양쪽 출처를 보고 판단</sub> | <sub>STATE.md</sub> |
| <sub>③ 영향 섹션 매핑</sub> | <sub>D · Q · P 「영향 섹션」 열 기준 재생성 대상 결정<br>단위 변경 → 02 + 04 · 범위 변경 → 03 + 04 + 05 · 답변만 → 해당 섹션 + §10</sub> | <sub>—</sub> | <sub>재생성 대상 목록</sub> |
| <sub>④ 델타 재생성</sub> | <sub>영향받는 작업 파일만 수정 · 처리된 Q-xx `ANSWERED → 반영완료` · output 재조립</sub> | <sub>—</sub> | <sub>수정된 `0N_*.md`</sub> |
| <sub>⑤ 정합 재검증 · 버전업</sub> | <sub>총 M/M 정합(§0 ↔ 7-1 ↔ 7-2 ↔ 7-5 ↔ STATE.md) · v0.1 → v0.2 · 버전 히스토리 1줄</sub> | <sub>공수 정본이 바뀌는 재산정이면 고지 내용 · 변경 전후 수치 확인</sub> | <sub>`…_PRD_v0.2.html` · STATE.md 버전 히스토리</sub> |

| <div align="center"><sub>변경 종류</sub></div> | <sub>버전 처리</sub> |
|:---|:---:|
| <sub>정보 유입에 의한 내용 변경</sub> | <sub>마이너 버전업(v0.x)</sub> |
| <sub>산정 단위 · 공수 정본이 바뀌는 재산정</sub> | <sub>사용자 고지 후 버전업 + 변경 전후 수치 병기</sub> |
| <sub>오탈자 · 표현 수정</sub> | <sub>제자리 수정(in-place)</sub> |

## 산출물

| <div align="center"><sub>파일</sub></div> | <sub>형식</sub> | <sub>위치</sub> | <sub>내용</sub> |
|:---|:---:|:---:|:---:|
| <sub>PRD 본문</sub> | <sub>html · md · docx</sub> | <sub>`output/{프로젝트}/`</sub> | <sub>헤더 + 10섹션 + 자기검증 8항목 판정표<br>예 `01_{사업명}_PRD_v0.1.html`</sub> |
| <sub>`STATE.md`</sub> | <sub>md</sub> | <sub>`_workspace/{프로젝트}/`</sub> | <sub>프로젝트 지속 상태 정본(SSOT) · 공수 정본 · 산정 단위 확정본 · D · Q · P 레지스터 · 리스크 요약 · 버전 히스토리</sub> |
| <sub>`01_diagnosis.md`</sub> | <sub>md</sub> | <sub>`_workspace/{프로젝트}/`</sub> | <sub>§2 현황 진단(실측)</sub> |
| <sub>`02_units.md`</sub> | <sub>md</sub> | <sub>`_workspace/{프로젝트}/`</sub> | <sub>§3 산정 단위 정의</sub> |
| <sub>`03_scope.md`</sub> | <sub>md</sub> | <sub>`_workspace/{프로젝트}/`</sub> | <sub>§4 요구사항 · 범위 + §5 전략 · R&R + §6 영향도</sub> |
| <sub>`04_effort.md`</sub> | <sub>md</sub> | <sub>`_workspace/{프로젝트}/`</sub> | <sub>§7 공수 산정(7-1 – 7-7)</sub> |
| <sub>`05_narrative.md`</sub> | <sub>md</sub> | <sub>`_workspace/{프로젝트}/`</sub> | <sub>§0 헤더 + §1 개요 + §8 흐름 + §9 총평 + §10 사전 확인 · 리스크</sub> |
| <sub>`06_qa.md`</sub> | <sub>md</sub> | <sub>`_workspace/{프로젝트}/`</sub> | <sub>자기검증 8항목 판정</sub> |

- 출력 포맷: HTML = 문서형(롱스크롤 리포트 · A4 인쇄) · 고객 전달 가능 / Markdown = 옵시디언 호환 · 편집 · 버전 관리 용이 / DOCX = 공식 문서형 · 인쇄 · 고객 공식 전달용
- HTML = 하우스 스타일 정본(`../../global-house-style/house-style.css`) 전문 인라인 + 문서형 골격(`base_template_doc.html`) · 자기완결 단일 파일 · 간트는 정본 §21 마크업 직접 작성(JS 자동 생성 금지)
- 파일명 `{NN}_{사업명}_PRD_v{X.Y}` · 경미 수정은 제자리 갱신 · 정보 유입에 의한 갱신은 버전업 + STATE.md 버전 히스토리 기록
- 작업 파일 경로는 항상 `_workspace/{프로젝트}/{파일}` · `_workspace/` 바로 아래 생성 금지

### PRD 섹션 구성 (헤더 + 10섹션)

| <div align="center"><sub>섹션</sub></div> | <sub>담는 내용</sub> | <sub>작업 파일</sub> |
|:---|:---:|:---:|
| <sub>§0 퀵 스탯 헤더</sub> | <sub>사업 기간 · 오픈 목표일 · 총 M/M · 투입 인력 · 작업 방식 · 직군 비중</sub> | <sub>`05_narrative.md`</sub> |
| <sub>§1 프로젝트 개요</sub> | <sub>CORE THESIS 1문장 · AS-IS vs TO-BE · 제약과 방향 · 범위 요약 · 핵심 메시지</sub> | <sub>`05_narrative.md`</sub> |
| <sub>§2 현황 진단</sub> | <sub>실측값(증거) + 의미(견적 시사점) 2열 · 실측 출처 · 진단 요약 인사이트</sub> | <sub>`01_diagnosis.md`</sub> |
| <sub>§3 산정 단위 정의</sub> | <sub>단위 선언 · 인스턴스 → 고유 단위 환산 테이블 · 재사용 구조 · 산정 단위 인사이트</sub> | <sub>`02_units.md`</sub> |
| <sub>§4 요구사항 · 범위</sub> | <sub>요구사항 목록(수용 · 확인 필요 · 제외) · 기능/비기능 · 의존관계 · Out of Scope 사유</sub> | <sub>`03_scope.md`</sub> |
| <sub>§5 대응 전략 · 연동 · R&R</sub> | <sub>핵심 가정 · 조건부 견적 전제 · 연동 흐름 · R&R 매트릭스</sub> | <sub>`03_scope.md`</sub> |
| <sub>§6 영향도 분석</sub> | <sub>「영향 없음 · 최소 영향 · 주요 영향」 3단계 분류 · 회귀 테스트 범위</sub> | <sub>`03_scope.md`</sub> |
| <sub>§7 공수 산정</sub> | <sub>7-1 영역별(직군 분해) · 7-2 월별 투입(등급) · 7-3 시나리오 매트릭스 + 절감 카드 · 7-4 역할 · 단계별 업무 · 7-5 WBS · 7-6 간트 · 7-7 핵심 요약</sub> | <sub>`04_effort.md`</sub> |
| <sub>§8 진행 흐름</sub> | <sub>단계 플로우 · 단계별 산출물 태그 · 게이트 밴드</sub> | <sub>`05_narrative.md`</sub> |
| <sub>§9 종합 총평</sub> | <sub>본질 · 무게중심 · 핵심 · 게이트 4관점 + 월별 일정 타임라인</sub> | <sub>`05_narrative.md`</sub> |
| <sub>§10 사전 확인 · 리스크</sub> | <sub>사전 확인(A 범위 · B 기술 · C 환경 · 일정 · D 견적) · 리스크 매트릭스(High · Mid · Low) · 협상 전략(내부용)</sub> | <sub>`05_narrative.md`</sub> |
| <sub>말미</sub> | <sub>자기검증 8항목 판정표(`[통과]` · `[보완필요]` · `[미충족]`)</sub> | <sub>`06_qa.md`</sub> |

### STATE.md 구성

| <div align="center"><sub>절</sub></div> | <sub>담는 내용</sub> | <sub>기입 시점</sub> |
|:---|:---:|:---:|
| <sub>0 메타</sub> | <sub>slug · 클라이언트 / 사업명 · 유형 · 사업 기간 · 출력 포맷 · 현재 문서 버전</sub> | <sub>인테이크 직후</sub> |
| <sub>1 공수 정본</sub> | <sub>채택 시나리오 · 총 M/M · 직군 분해 · 투입 인력 · 안정화 · 외부 공수 정본 경로</sub> | <sub>GATE 2 승인 후</sub> |
| <sub>2 산정 단위 정의</sub> | <sub>채택 단위 · 고유 단위 합계 · 재사용 구조</sub> | <sub>GATE 1 승인 후</sub> |
| <sub>3 확정 사항 로그(D-xx)</sub> | <sub>합의 · 승인 · 확정 내용 · 날짜 · 출처 · 영향 섹션</sub> | <sub>확정마다</sub> |
| <sub>4 [확인 필요] 레지스터(Q-xx)</sub> | <sub>질문 · 답변 · 답변 출처 · 영향 섹션 · 상태 `OPEN → ANSWERED → 반영완료`</sub> | <sub>`[확인 필요]` 발생 즉시</sub> |
| <sub>5 조건부 전제(P-xx)</sub> | <sub>견적 성립 전제 · 불성립 시 재산정 트리거 · 상태 `성립 가정 → 확인됨 / 붕괴`</sub> | <sub>범위 · 전략 단계부터</sub> |
| <sub>6 리스크 요약</sub> | <sub>§10-2 리스크 매트릭스와 동기 · High만 상세</sub> | <sub>서사 · 리스크 단계</sub> |
| <sub>7 버전 히스토리</sub> | <sub>버전 · 날짜 · 트리거(유입 정보) · 변경 요지 · 공수 변동(전후 수치)</sub> | <sub>버전업마다</sub> |

- 섹션 파일과 STATE.md가 충돌하면 STATE.md 우선 → 섹션 파일 수정
- 모든 섹션 · 산출물은 STATE.md 값만 인용
- D-xx 삭제 금지 · 번복 시 새 D-xx 추가 + 구 항목 취소선 · 참조
- 템플릿 정본 `references/state-template.md`

## 준비 (처음 한 번)

- 별도 설치 불필요 · sync-skills · npm 설치 대상 제외 · 리포 안 HTML 스타일 정본(`../../global-house-style/`)과 마스터프롬프트(`references/master-prompt-v2.0.md`)를 그대로 사용

## 폴더 구성

```
agent/prd/
├── CLAUDE.md                      # 하네스 규칙 (폴더에서 Claude Code 열면 자동 로딩)
├── ORCHESTRATOR.md                # 파이프라인 + 업데이트 프로토콜 (실행 정본)
├── references/
│   ├── master-prompt-v2.0.md      # 섹션 작성 기준 정본 (옵시디언 원본의 사본)
│   └── state-template.md          # STATE.md 템플릿
├── input/{프로젝트}/               # 프로젝트별 입력(RFP · 회의록 · 실측) · 유입 차수별 하위폴더
├── _workspace/{프로젝트}/          # STATE.md + 01–06 단계 산출물
└── output/{프로젝트}/              # {NN}_{사업명}_PRD_v{X.Y}.{html|md|docx}
```

- `{프로젝트}` = slug `{클라이언트}-{주제}`(예 `acme-shop`) · input · 중간물 · output 모두 프로젝트별 하위폴더로 분리
- `input/` · `_workspace/` · `output/`은 Git 미추적(RFP 등 기업 민감정보 · 산출물) · 폴더 구조만 유지

## 용어

| <div align="center"><sub>용어</sub></div> | <sub>뜻</sub> |
|:---|:---:|
| <sub>**RRD**</sub> | <sub>Requirements Reference Document · 범위 · R&R · 전제조건 합의용 고객 공식 참조 문서</sub> |
| <sub>**마스터프롬프트(MP)**</sub> | <sub>`references/master-prompt-v2.0.md` · 헤더 + 10섹션 작성 기준의 유일한 정본</sub> |
| <sub>**산정 단위**</sub> | <sub>공수를 세는 1단위(페이지 · 화면 · 템플릿 · 모듈 · 기능 · API) · 인스턴스 반복은 1회 제작 + N회 재사용, 중복 계상 금지</sub> |
| <sub>**3축 분해**</sub> | <sub>모든 공수를 영역(기능군) × 직군(기획 · 디자인 · 퍼블 · 개발 · QA) × 등급(초급 · 중급 · 고급)으로 추적</sub> |
| <sub>**STATE.md**</sub> | <sub>프로젝트별 지속 상태 파일 · 단일 진실 공급원(SSOT)</sub> |
| <sub>**D-xx · Q-xx · P-xx**</sub> | <sub>확정 사항 · `[확인 필요]` 질문 · 조건부 전제의 ID</sub> |
| <sub>**델타 재생성**</sub> | <sub>새 정보가 영향을 주는 섹션 파일만 다시 쓰는 갱신 방식</sub> |
| <sub>**시나리오 A–D**</sub> | <sub>공수 견적안 · A 기본 · B 절감(재사용 · 이관 · 기존 유지) · C 고객 요청 전수용 · D 추천</sub> |

## 프로젝트 유형별 중점 섹션

| <div align="center"><sub>유형</sub></div> | <sub>핵심 섹션</sub> | <sub>경량 처리 가능</sub> |
|:---|:---:|:---:|
| <sub>홈페이지 · 플랫폼 리뉴얼</sub> | <sub>2(현황 진단) · 3(산정 단위) · 7-1(영역별 공수)</sub> | <sub>6(영향도)</sub> |
| <sub>신규 시스템 구축</sub> | <sub>4(요구사항) · 5(대응 전략) · 6(영향도)</sub> | <sub>2(현황 진단)</sub> |
| <sub>기존 시스템 고도화</sub> | <sub>4(요구사항) · 6(영향도) · 7(공수 산정)</sub> | <sub>3(산정 단위)</sub> |
| <sub>AI · 챗봇 · 신기술 도입</sub> | <sub>4(요구사항) · 5(대응 전략 · 연동) · 7-3(시나리오)</sub> | <sub>2(현황 진단)</sub> |

## 주의

- 근거 규율: 자료 · 실측에 없는 내용 추측 금지 → `[확인 필요]` 또는 `[자료 미제공]` · `[확인 필요]`는 즉시 STATE.md Q-레지스터 등록(섹션 10과 동기)
- 범위 안 · 밖 명확 구분 · 범위 밖 항목은 사유 필수 · 절감 로직은 수치로 · 조건부 전제는 재산정 트리거와 함께
- 공수 정합 불일치(±10% 초과)는 숨기지 않고 표면화 → 정본 값 사용자 확인 → STATE.md 갱신
- 공수 하네스(`../harness_st-etribe`) 산출물이 있으면 그 공수 수치를 정본으로 인용 · 재산정 생략
- §10-3 협상 전략은 내부 참고용 · 고객 전달본 제외
- 단계 실패 시 1회 재시도 · 재실패면 해당 섹션 `[생성 실패]` 표기 후 진행 + 최종 보고에 누락 명시
- 실측 대상 접근 차단 시 접근 가능 범위만 실측 + §2에 미접근 영역 명시 · 임의 추정 금지
- 모델 티어링: 추론(진단 · 단위 · 공수 · 서사) = opus · 기계적 작업(검증 · 조립) = sonnet 권장
- 표기: 한국어 · 명사형 종결 · 범위 표기는 물결표(~) 대신 하이픈(-)
- HTML 구 사양(`--brand` 그라데이션 대시보드 · 단계 색상칩 · 인사이트 박스)은 은퇴 · 재사용 금지 · CI는 인테이크 ⑥에서 명시적으로 요청받을 때만
- 원본 마스터프롬프트: 옵시디언 `100. Workspace/110. Templates/★프로젝트 공수산정 및 기초PRD_마스터프롬프트_v2.0.md` · 옵시디언 쪽을 수정하면 `references/master-prompt-v2.0.md`에도 반영 · 현재 개정 v2.0.2(2026.08.27)

## 릴리즈노트

| <div align="center"><sub>요약내용</sub><img width="1" height="1"></div> | <sub>업데이트 일자</sub><img width="1" height="1"> | <sub>소유자</sub><img width="45" height="1"> |
|:---|:---:|:---:|
| <sub>README 전면 개편 — 목적 · 넣는 것 · 산출물 형태 · 요청 예시 · 진행 단계 순으로 재구성, 릴리즈노트 맨 아래로 이동</sub> | <sub>2026.11.13</sub> | <sub>김단영</sub> |
| <sub>Dan Jr. 등급 조회 추가 — 인테이크·GATE 직전 `persona.md` 확인(A 진행·B 보고·C 질문), 건너뛴 게이트는 완료 보고에 ID 표기</sub> | <sub>2026.10.22</sub> | <sub>김단영</sub> |
| <sub>인테이크에 스타일 확인 단계 신설 — HTML 산출 시 컬러를 임의 고정하지 않고 매 프로젝트 확인 후 적용</sub> | <sub>2026.08.20</sub> | <sub>김단영</sub> |
| <sub>최초 등록 — 공수산정 + 기초 PRD(RRD) 빌더 하네스</sub> | <sub>2026.07.07</sub> | <sub>김단영</sub> |
