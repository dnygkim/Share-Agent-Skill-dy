# feature-spec-sb — PRD → SB 화면설계서 에이전트

기능 ID(예 `A-02`)나 신규 서비스명을 말로 요청하면 PC/모바일 B2C 웹사이트의 PRD(명세서 `.md`)와 SB(화면설계서 · 와이어프레임 HTML)를 만드는 에이전트 하네스. 신규 서비스는 서비스 정의서 → IA 엑셀 → 플로우차트 → SB까지 한 흐름으로 진행, 토큰 · 계정 설정 없이 동작

> **원작자 (Owner)** — 황다혜 프로  
> **원본 (Resource)** — https://github.com/starryetribe-droid/AX-Pilot/tree/main  
> 이 폴더 = 위 원본 `feature-spec` 스킬의 모노레포 이관 · 재구성본  
> 작성 규칙 · 양식 · 컴포넌트 체계 설계 = 원작자 설계

## 한눈에 보기

| <div align="center"><sub>항목</sub></div> | <sub>내용</sub> |
|:---|:---:|
| <sub>목적</sub> | <sub>기능 단위 PRD(명세서)와 SB(화면설계서 · 와이어프레임) 작성 자동화 · SB는 HTML-to-Figma 임포트 전제</sub> |
| <sub>이럴 때 사용</sub> | <sub>공통 기능(회원가입 · 로그인 등) PRD 작성 · 기존 PRD에서 화면설계서 추출 · 신규 서비스 착수(서비스 정의 → IA → SB) · 어드민(백오피스) 화면설계</sub> |
| <sub>넣는 것</sub> | <sub>기능 ID 또는 기능명(`guides/features-list.md` 14분류 91개) · 기존 PRD `.md` 경로 · 신규 서비스명 · (어드민) 시안 이미지 · 설명 또는 세부기능정의 워크북 xlsx</sub> |
| <sub>나오는 것</sub> | <sub>9섹션 PRD `.md`(Mermaid 플로우차트 포함) · 화면별 SB HTML(ETRIBE 2560px 시트, 화면 1개 = 파일 1개) · (착수) 서비스 정의서 `.md` + IA `.xlsx`</sub> |
| <sub>저장 위치</sub> | <sub>기본 모드 = 작업 폴더의 `01. 공통 기능/{카테고리}/PRD/` · `SB/` · 착수 = `output/{slug}/` · 어드민 SB = `~/Downloads/SB_어드민/`</sub> |
| <sub>시작 방법</sub> | <sub>`agent/feature-spec-sb/` 폴더에서 Claude Code 실행 → `CLAUDE.md` 자동 로딩 → 자연어 요청</sub> |
| <sub>연계</sub> | <sub>`skills/ia-builder`(제작 신지은) = 착수 모드의 IA 생성 담당 · 이름이 비슷한 `agent/screen-spec-id` = IA → 화면ID 채번 · 화면명세서 엑셀(이 하네스 = PRD → 와이어프레임 HTML)</sub> |

## 이렇게 요청

| <div align="center"><sub>상황</sub></div> | <sub>요청 예시</sub> | <sub>나오는 것</sub> |
|:---|:---:|:---:|
| <sub>**SB만 만들기** · 기존 PRD 보유</sub> | <sub>`A-01 PRD에서 SB 생성` · `A-01 SB 만들어줘`</sub> | <sub>화면별 SB HTML (모바일 또는 PC 한 종류)</sub> |
| <sub>**PRD부터 만들기** · 기능 ID만 보유</sub> | <sub>`A-02 PRD 만들어줘`</sub> | <sub>9섹션 PRD `.md` (Mermaid 플로우차트 포함)</sub> |
| <sub>**PRD + SB 한 번에** (통합)</sub> | <sub>`A-04 기획해줘` · `회원가입 기획해줘`</sub> | <sub>PRD 작성 → SB 진행 확인 → 화면별 SB HTML</sub> |
| <sub>**프로젝트 착수** · 기능 ID 없는 신규 서비스</sub> | <sub>`테스트커머스 서비스 기획해줘` · `새 프로젝트 시작`</sub> | <sub>서비스 정의서 → IA 엑셀 → PRD N개 → SB M개</sub> |
| <sub>**어드민 분기** · 관리자(백오피스) 화면</sub> | <sub>`관리자 화면 SB` · `어드민 정의서로 PRD` · `챗봇 SB 만들고 싶어`</sub> | <sub>어드민 SB HTML(템플릿 3종) · 워크북 기반 PRD `.md`</sub> |
| <sub>**부분 수정**</sub> | <sub>`A-01-003 화면 4번 항목 문구 수정` · `A-01-003 화면 추가`</sub> | <sub>기존 PRD · SB 파일 직접 수정</sub> |

- 기능 ID가 언급되면 항상 기본 모드(SB · PRD · 통합) · 프로젝트 착수는 기능 ID 없이 서비스 자체를 처음부터 정의하는 요청 전용
- 어드민 분기는 「어드민」 · 「관리자」 · 「챗봇 SB」 키워드가 명시된 요청에서만 적용

### 예시 대화

```
사용자: A-02 PRD 만들어줘
Claude: 작성자명을 입력해주세요 (예: 김기획, 박PM 등)
사용자: 김기획
Claude: [A-02 로그인 (이메일/ID)] PRD 작성 전에 프로세스를 알려주세요  A) 단계별 글  B) 이미지 첨부  C) 비슷한 PRD 참고  D) 일반 패턴(자동)  E) 다른 PRD 패턴 차용
사용자: D
Claude: [A-02 플로우 초안] (Mermaid 플로우차트) OK신가요? 수정사항 있으면 말씀해주세요
사용자: OK
Claude: [A-02 PRD 체크리스트 검증] 아래 화면의 정의가 필요한 항목입니다. 한 번에 답변해주세요 (항목별 답변 · 패턴 따라가자 · 스킵)
```

## 진행 단계

### 모든 모드 공통

- 첫 작성 규칙 로드 전 **작성자명** 질문 필수(착수 모드는 서비스명 · 디바이스 다음) · 작업 내내 재사용(재입력 생략) · 작성 규칙 로드 기록(`--author`)에 사용
- SB는 **한 번에 한 종류**(모바일 또는 PC) · 둘 다 필요하면 한쪽 완료 후 별도 요청으로 다른 쪽
- 승인 게이트(**GATE**)에서는 답을 받기 전 다음 단계 진행 보류
- Dan Jr. 등급 조회: 작성자명 · 양식 · 「~할까요?」 질문 직전 `persona.md` 확인 → A 기본값 진행 · B 진행 후 완료 보고에 한 줄 · C 또는 해당 항목 부재 시 질문 · 건너뛴 게이트는 완료 보고에 ID 표기(예 「Dan Jr. 적용: D-01(A)」) · persona.md에 없는 결정(프로세스 입력 · 플로우차트 승인 등)은 그대로 사용자 승인

### ① SB만 만들기 (기존 PRD)

```
① 작성자명 → ② 모바일 / PC 선택 → ③ 작성 규칙 로드 → ④ 화면 분리 → ⑤ 화면별 본문 작성 → ⑥ SB HTML 생성 → ⑦ 결과 보고
```

| <div align="center"><sub>단계</sub></div> | <sub>하는 일</sub> | <sub>사용자 할 일</sub> | <sub>결과물</sub> |
|:---|:---:|:---:|:---:|
| <sub>①</sub> | <sub>작성자명 질문</sub> | <sub>이름 입력(예 `김기획`)</sub> | <sub>—</sub> |
| <sub>②</sub> | <sub>양식 확인(모바일 / PC)</sub> | <sub>하나 선택 · 기본값 모바일</sub> | <sub>—</sub> |
| <sub>③</sub> | <sub>`fetch_guide.py --mode sb-mobile` 또는 `sb-pc`로 작성 규칙 로드</sub> | <sub>—</sub> | <sub>—</sub> |
| <sub>④</sub> | <sub>PRD 분석 → 화면 분리(1화면 = 1상태 · 화면 ID `A-01-001`부터)</sub> | <sub>—</sub> | <sub>화면 목록</sub> |
| <sub>⑤</sub> | <sub>화면별 와이어프레임 · Description 작성(필수 골격 · 모달 서브 캔버스 · desc-block 규칙)</sub> | <sub>—</sub> | <sub>화면별 본문 HTML</sub> |
| <sub>⑥</sub> | <sub>`screens.json` 작성 → `generate_sb.py --variant mobile` 또는 `pc` 실행</sub> | <sub>—</sub> | <sub>화면 1개 = HTML 1개</sub> |
| <sub>⑦</sub> | <sub>화면 수 · 경로 · 경고 유무 보고</sub> | <sub>결과 확인 · Figma 임포트</sub> | <sub>`01. 공통 기능/{카테고리}/SB/{기능ID}/` (PC는 `{기능ID}_PC/`)</sub> |

### ② PRD부터 만들기 (기능 ID)

```
① 작성자명 → ② 프로세스 입력 방식 → ③ 규칙 · 기능 정보 조회 → ④ 플로우차트 승인(GATE) → ⑤ 9섹션 PRD 작성 → ⑥ 누락 항목 일괄 질문(GATE) → ⑦ 저장
```

| <div align="center"><sub>단계</sub></div> | <sub>하는 일</sub> | <sub>사용자 할 일</sub> | <sub>결과물</sub> |
|:---|:---:|:---:|:---:|
| <sub>①</sub> | <sub>작성자명 질문</sub> | <sub>이름 입력</sub> | <sub>—</sub> |
| <sub>②</sub> | <sub>프로세스 입력 방식 질문</sub> | <sub>A 단계별 글 · B 손그림/플로우차트 이미지 첨부 · C 비슷한 PRD 참고 · D 일반 패턴(자동) · E 다른 PRD 패턴 차용 중 선택 · ETRIBE 고유 정책 · 분기 함께 전달</sub> | <sub>—</sub> |
| <sub>③</sub> | <sub>`fetch_guide.py --mode prd` 규칙 로드 · `features-list`에서 기능명 · 카테고리 조회</sub> | <sub>—</sub> | <sub>—</sub> |
| <sub>④ **GATE**</sub> | <sub>Mermaid 플로우차트 초안 제시 (Step 2.5)</sub> | <sub>**플로우 확인 → 승인 또는 수정 요청(반복)** · 승인 전 본문 작성 보류 · D 선택 시에도 적용</sub> | <sub>승인된 플로우차트</sub> |
| <sub>⑤</sub> | <sub>9섹션 PRD 본문 작성 · 승인된 Mermaid 그대로 사용</sub> | <sub>—</sub> | <sub>PRD 초안</sub> |
| <sub>⑥ **GATE**</sub> | <sub>화면 타입 17종 체크리스트로 누락 항목 추출 → 화면별로 묶어 한 번에 질문 (Step 3.5)</sub> | <sub>**항목별 답변 · 「패턴 따라가자」 · 「스킵」 중 선택** · 답 전 저장 보류</sub> | <sub>§5 예외 처리 · §6 화면별 UI 보완</sub> |
| <sub>⑦</sub> | <sub>저장</sub> | <sub>결과 확인</sub> | <sub>`01. 공통 기능/{카테고리}/PRD/{기능ID}_{영문명}.md`</sub> |

- ④ · ⑥ = 품질을 좌우하는 지점 · 플로우 단계 수정이 본문 완성 후 수정보다 저비용, ⑥은 화면 종류별로 흔히 빠뜨리는 항목(빈 상태 · 권한 · 에러 등) 사전 점검
- PRD 9섹션 = 개요 · 선행 조건 · 플로우차트 · 단계별 상세 · 예외 처리 · 화면별 UI 요소 · 데이터 처리 · 연관 기능 · 변경 이력 (`guides/prd-structure.md`)

### ③ PRD + SB 한 번에 (통합)

- `A-04 기획해줘`처럼 기능 ID · 기능명만 말한 요청
- ② PRD부터 만들기 전체 → SB 진행 의사 확인 → ① SB만 만들기의 ②(모바일 / PC)부터 진행
- PRD 단계의 프로세스 입력 · 플로우차트 승인은 그대로 적용 · 작성자명 재질문 생략

### ④ 프로젝트 착수 (신규 서비스)

- 기능 ID 없이 완전히 새로운 서비스를 처음부터 정의하는 요청 전용
- 서비스명 · 디바이스를 맨 앞에서 확인 → IA · SB 단계에서 재사용(같은 질문 반복 생략)
- IA = 별도 스킬 `skills/ia-builder`(제작 신지은) · PRD · SB = 이 에이전트의 기존 엔진 · 착수 모드 = 둘을 잇는 오케스트레이션 레이어
- 상세 절차 정본 `rules/project-kickoff.md`

```
① 서비스명 → ② 디바이스 → ③ 작성자명 → ④ 서비스 정의서 → ⑤ IA 생성(ia-builder · GATE) → ⑥ 플로우차트 + PRD(GATE) → ⑦ 화면별 SB → ⑧ 요약 보고
```

| <div align="center"><sub>단계</sub></div> | <sub>하는 일</sub> | <sub>사용자 할 일</sub> | <sub>결과물</sub> |
|:---|:---:|:---:|:---:|
| <sub>①</sub> | <sub>서비스명(프로젝트명) 질문 → 영문 슬러그 변환(예 `테스트커머스` → `test-commerce`)</sub> | <sub>서비스명 입력 · 슬러그를 못 정하면 영문 표기 답변</sub> | <sub>산출물 폴더 `output/{slug}/`</sub> |
| <sub>②</sub> | <sub>디바이스 질문 · IA와 SB 양쪽에 재사용</sub> | <sub>PC · 모바일 웹 · 둘 다 중 선택(기본값 둘 다) · 관리자(Admin) 화면 필요 여부(여기 또는 ④ 대상 사용자에서 확인)</sub> | <sub>—</sub> |
| <sub>③</sub> | <sub>작성자명 질문</sub> | <sub>이름 입력</sub> | <sub>—</sub> |
| <sub>④</sub> | <sub>서비스 정의서(경량 PRD) 작성 · 개요 · 목표 · 대상 사용자 · 범위</sub> | <sub>내용 확인 · 확정</sub> | <sub>`00. 서비스 정의서.md`</sub> |
| <sub>⑤ **GATE**</sub> | <sub>`ia-builder` 스킬 호출 · ①~④ 정보 전달로 시작 인터뷰 중복 생략 · 헤더 양식 확인부터 골격(v0.1) → 컬럼별 순차 디벨롭</sub> | <sub>**IA 검토 · 확정** · 확정 전 다음 단계 보류</sub> | <sub>`01. IA/{서비스명}_IA_v0.1_{YYYYMMDD}.xlsx`</sub> |
| <sub>⑥ **GATE**</sub> | <sub>IA 화면을 사용자 플로우 단위로 묶어 Mermaid 플로우차트 작성 · 플로우별 9섹션 PRD 작성 여부 확인</sub> | <sub>**플로우차트 일괄 승인** · PRD 작성 여부 선택(단순 화면은 생략 제안)</sub> | <sub>`02. 공통 기능/{기능슬러그}/PRD/…`</sub> |
| <sub>⑦</sub> | <sub>화면별 SB 추출 · 화면 분리는 IA 결과 그대로 · 작성자 · 디바이스 재질문 생략</sub> | <sub>둘 다 선택 시 한쪽 완료 후 다른 쪽</sub> | <sub>`02. 공통 기능/{기능슬러그}/SB/…`</sub> |
| <sub>⑧</sub> | <sub>요약 보고 · 서비스명 · 산출물 목록(서비스 정의서 1 · IA 1 · PRD N · SB M)과 경로</sub> | <sub>결과 확인</sub> | <sub>—</sub> |

- 모든 단계 = 앞 단계 사용자 확정 후 진행 · 순서 건너뛰기 불가
- ⑥에서 PRD를 쓰기로 하면 PRD 본문 작성부터 진행 · 작성자 · 프로세스 입력 · 플로우차트 승인 재진행 생략
- 새 서비스 기능이 기존 69개 공통기능(`guides/features-list.md`)과 성격이 겹치면 그 카테고리 재사용 가능
- 전제 = `ia-builder`가 이 폴더에서 자동 로드되는 상태 · 아래 「준비」의 `sync-skills` 1회 실행

### ⑤ 어드민 분기 (해당 키워드가 있을 때만)

- 기본 대상 = PC/모바일 B2C 웹사이트 · 어드민 · 관리자 요청에서만 `rules/admin-sb.md` 적용
- `SKILL.md` §4 공통 규칙(와이어프레임 골격 · 모달 · Description · screens.json) 상속 · 분기 문서에 다시 적히지 않은 항목은 §4 기준

| <div align="center"><sub>분기</sub></div> | <sub>요청 예시</sub> | <sub>진행</sub> | <sub>결과물</sub> |
|:---|:---:|:---:|:---:|
| <sub>**어드민 SB** (A-1)</sub> | <sub>`어드민 만들어줘` · `관리자 화면 SB`</sub> | <sub>작성자명 → 템플릿 선택 → (KRDS만) PC / Mobile 선택 → 화면 지정(등록 화면은 바로 생성 · 새 화면은 시안 이미지 · 설명 또는 PRD) → 본문 작성 → `build_admin_sb.py`로 SB 생성</sub> | <sub>`~/Downloads/SB_어드민/{화면ID}.html`</sub> |
| <sub>**챗봇 어드민 SB** (A-1.1)</sub> | <sub>`챗봇 SB 만들고 싶어`</sub> | <sub>작성자명 → 기능정의 엑셀(어드민 세부기능정의 워크북) 첨부 → PRD 자동 생성(커버리지 기계 검증) → **GATE PRD 컨펌** → SB 생성(챗봇 어드민 템플릿 · PC)</sub> | <sub>PRD `.md` + SB HTML</sub> |
| <sub>**어드민 워크북 → PRD** (A-2)</sub> | <sub>`어드민 정의서로 PRD`</sub> | <sub>작성자명 → 워크북 경로 · 대상 메뉴 · 기능ID(`ADM-{영문 슬러그}`) 확인 → 워크북 파싱 · 체크리스트 → 9섹션 PRD 일괄 작성 → 커버리지 검증(누락 0까지 반복) → 저장 · ✓/✗ 결과 보고</sub> | <sub>`90. 어드민/PRD/{기능ID}_{영문슬러그}.md`</sub> |

| <div align="center"><sub>템플릿</sub></div> | <sub>Variant</sub> | <sub>특징</sub> |
|:---|:---:|:---:|
| <sub>공통 어드민 `admin-common` (권장 기본)</sub> | <sub>PC 고정</sub> | <sub>2560px 프레임 · 콘텐츠 1440px 중앙 · 무채색 + 상태 컬러 · 팝업 = 별도 SB 페이지</sub> |
| <sub>챗봇 어드민 `admin-chatbot`</sub> | <sub>PC 고정</sub> | <sub>좌측 GNB + 상단 유틸바 + 그린 포인트</sub> |
| <sub>KRDS 기본 `admin-krds`</sub> | <sub>**PC / Mobile**</sub> | <sub>Front 표준 컴포넌트 · PC 2560px / Mobile 390px 범용</sub> |

- 영역 배지(n)에 더해 세부 요소 서브 배지(n-m, 예 필터 4-1~4-8 · 테이블 컬럼 8-1~8-15)까지 1:1 부여 · Description 번호와 일치
- 새 화면 소스로 기존 PRD 사용 여부는 반드시 사용자 확인
- 챗봇 어드민 SB는 PRD 컨펌 전 SB 진행 금지 · 워크북 없이 시안 · 기존 PRD로 바로 SB를 원하면 어드민 SB(A-1) 흐름
- 어드민 워크북 → PRD는 검토 절차(프로세스 입력 · 플로우차트 승인 · 체크리스트 질문) 생략 · 워크북 미정의 항목은 ETRIBE 공통 패턴 자동 적용 후 «(제안)» 표기 · SB는 별도 요청 시 어드민 SB(A-1)로 진행
- 인텐트 워크북 기반 챗봇 SB 자동 생성 · 컴포넌트 카탈로그(구 C-1 · C-2)는 규칙 문서 삭제(2026.08.03, 메모리 아카이브) · 빌더 스크립트만 내부용으로 유지

### ⑥ 부분 수정

- 기존 PRD · SB 파일을 Edit로 직접 수정 · 생성 스크립트 미사용
- SB 수정 시 Description `desc-block` 구조 유지

### 인테이크 질문

| <div align="center"><sub>질문</sub></div> | <sub>답 예시</sub> | <sub>기본값</sub> |
|:---|:---:|:---:|
| <sub>작성자명 (모든 모드 · 착수는 세 번째 질문)</sub> | <sub>`김기획` · `박PM`</sub> | <sub>필수 답변 · 사용 기록용이라 같은 이름으로 일관 입력</sub> |
| <sub>모바일 / PC (SB)</sub> | <sub>`A` 모바일 · `B` PC</sub> | <sub>모바일</sub> |
| <sub>프로세스 입력 방식 (PRD)</sub> | <sub>`A`~`E` 중 하나 + ETRIBE 고유 정책 · 분기</sub> | <sub>필수 답변 · D여도 플로우차트 승인 유지</sub> |
| <sub>누락 항목 (PRD 저장 전)</sub> | <sub>항목별 정의 · `패턴 따라가자` · `스킵`</sub> | <sub>비즈니스 결정 항목(필터 종류 · 권한 정책 · 임시저장 등)은 반드시 질문</sub> |
| <sub>서비스명 (착수)</sub> | <sub>`테스트커머스`</sub> | <sub>필수 답변 · 영문 슬러그 미확정 시 영문 표기 추가 질문</sub> |
| <sub>디바이스 (착수)</sub> | <sub>PC · 모바일 웹 · 둘 다</sub> | <sub>둘 다</sub> |
| <sub>템플릿 (어드민 SB)</sub> | <sub>공통 어드민 · 챗봇 어드민 · KRDS 기본</sub> | <sub>필수 질문 · 권장 기본 공통 어드민 · 요청에 미리 답이 있으면 그 값</sub> |

## 산출물

| <div align="center"><sub>파일</sub></div> | <sub>형식</sub> | <sub>위치</sub> | <sub>내용</sub> |
|:---|:---:|:---:|:---:|
| <sub>`{기능ID}_{영문명}.md` (예 `A-01_signup.md`)</sub> | <sub>md</sub> | <sub>`01. 공통 기능/{카테고리}/PRD/`</sub> | <sub>9섹션 PRD · Mermaid 플로우차트 포함</sub> |
| <sub>`{화면ID}.html` (예 `A-01-001.html`)</sub> | <sub>html</sub> | <sub>`01. 공통 기능/{카테고리}/SB/{기능ID}/` · PC는 `{기능ID}_PC/`</sub> | <sub>화면 1개 = 파일 1개 · ETRIBE 2560px 시트</sub> |
| <sub>`00. 서비스 정의서.md`</sub> | <sub>md</sub> | <sub>`output/{slug}/`</sub> | <sub>(착수) 개요 · 목표 · 대상 사용자 · 범위</sub> |
| <sub>`{서비스명}_IA_v0.1_{YYYYMMDD}.xlsx`</sub> | <sub>xlsx</sub> | <sub>`output/{slug}/01. IA/`</sub> | <sub>(착수) ia-builder 기본 관례 · 다른 경로 요청 시 그 경로</sub> |
| <sub>PRD `.md` · SB `.html`</sub> | <sub>md · html</sub> | <sub>`output/{slug}/02. 공통 기능/{기능슬러그}/PRD/` · `SB/`</sub> | <sub>(착수) 플로우별 PRD · 화면별 SB</sub> |
| <sub>`{화면ID}.html`</sub> | <sub>html</sub> | <sub>`~/Downloads/SB_어드민/` (환경변수 `ADMIN_OUT`으로 변경)</sub> | <sub>(어드민) 템플릿 + 화면 본문 결합 SB · Channel = Admin</sub> |
| <sub>`{기능ID}_{영문슬러그}.md`</sub> | <sub>md</sub> | <sub>`90. 어드민/PRD/`</sub> | <sub>(어드민 워크북) 9섹션 PRD · 중간물 `scripts/_build/{ID}_spec.json` · `{ID}_checklist.md`</sub> |

- 경로 기준 = Claude Code를 연 작업 폴더(이 폴더에서 열면 `agent/feature-spec-sb/` 하위)

### SB 한 장의 구성

| <div align="center"><sub>영역</sub></div> | <sub>내용</sub> |
|:---|:---:|
| <sub>시트</sub> | <sub>2560px 고정 폭 + 외곽 프레임 · 캔버스가 넓으면 함께 확장</sub> |
| <sub>메타 헤더 (2행)</sub> | <sub>화면/컴포넌트 · 화면경로 · Local(KO) · Channel(기본 Front · 어드민 Admin) · 화면ID · 작성자 · 작성일</sub> |
| <sub>와이어프레임 (좌측)</sub> | <sub>넘버 배지 + 캔버스 · 모달 · 다이얼로그 · 바텀시트는 메인 캔버스 우측 서브 캔버스</sub> |
| <sub>Description (우측 640px)</sub> | <sub>「화면 설명」 · 「Description」 2개 섹션 · 번호 항목은 캔버스 배지와 1:1</sub> |
| <sub>푸터</sub> | <sub>우측 하단 ETRIBE 로고 · 버전 표기 미포함</sub> |

### PC / 모바일 캔버스

| <div align="center"><sub>항목</sub></div> | <sub>모바일</sub> | <sub>PC</sub> |
|:---|:---:|:---:|
| <sub>캔버스 폭</sub> | <sub>390px 고정</sub> | <sub>1440px 고정 (`--canvas-width`로 변경)</sub> |
| <sub>캔버스 높이</sub> | <sub>최소 844px · **상한 미설정**</sub> | <sub>최소 1440px · **상한 미설정** (`--canvas-min-height`)</sub> |
| <sub>컴포넌트</sub> | <sub>app-bar · tab-bar · FAB</sub> | <sub>GNB · 테이블 · 숫자 페이지네이션 · LNB</sub> |
| <sub>페이지 타이틀</sub> | <sub>22px</sub> | <sub>28–32px</sub> |
| <sub>입력 · 버튼 높이</sub> | <sub>48px</sub> | <sub>40–48px</sub> |

- 화면 정의 콘텐츠(컴포넌트 목록 · 동작 설명 · 예외 처리)는 두 양식 동일 · 차이는 레이아웃뿐 · PC라는 이유로 화면 병합 · 추가 분리 금지
- 캔버스 치수는 `generate_sb.py --variant`가 스타일 블록에 주입 · 목록 · 상세처럼 긴 화면도 콘텐츠 길이만큼 세로 확장
- 본문 인라인 치수 금지
  - `style="width:100%"` → 시트(`.sb-page`)가 `width:max-content`라 기준 폭 부재 → 캔버스가 콘텐츠 폭으로 축소
  - `style="height:…"` · `max-height` → 긴 화면이 그 높이에서 잘리는 문제(생성 시 경고)
  - 폭은 `--canvas-width`, 높이 하한은 `--canvas-min-height`로 조정 · 폭 1724px 초과 시 시트가 2560px보다 넓어진다는 경고

### HTML-to-Figma 전제

- SB = HTML-to-Figma 임포트 전제 · 아래 두 규칙의 이유
- Description 한 항목 = 하나의 `<p class="desc-block">` · `<div>` 분리 · CSS `::before` · padding/margin 들여쓰기 금지
- 폰트 = Static Pretendard 우선 지정 · Variable 폰트는 Figma 플러그인의 weight 축 매핑 실패로 볼드가 풀리는 문제

## 준비 (처음 한 번)

- 토큰 · 계정 설정 불필요 · 기본 모드(SB · PRD · 통합)는 Python만으로 바로 사용

| <div align="center"><sub>준비</sub></div> | <sub>필요한 경우</sub> | <sub>방법</sub> |
|:---|:---:|:---:|
| <sub>Python 3</sub> | <sub>모든 모드</sub> | <sub>기본 스크립트(`fetch_guide.py` · `generate_sb.py` · `build_admin_sb.py`)는 표준 라이브러리만 사용</sub> |
| <sub>`ia-builder` 자동 로드</sub> | <sub>프로젝트 착수</sub> | <sub>리포 루트에서 `./sync-skills.ps1`(또는 `bash ./sync-skills.sh`) 1회 실행</sub> |
| <sub>`openpyxl`</sub> | <sub>프로젝트 착수(IA 엑셀 생성) · 어드민 워크북 → PRD · 챗봇 빌더 스크립트</sub> | <sub>`pip install openpyxl`</sub> |
| <sub>토큰 (선택)</sub> | <sub>사내 서버 최신 규칙 수신</sub> | <sub>`~/.etribe/config.json`에 서버 URL · 토큰 저장 (`ONBOARDING.md` Step 3)</sub> |
| <sub>Static Pretendard (선택)</sub> | <sub>Figma 임포트 시 볼드 유지</sub> | <sub>Static OTF/TTF 설치 후 Figma 재시작 (`HISTORY.md` §10.3)</sub> |

```bash
cd dykim-claude-agents-skills
./sync-skills.ps1        # 또는 bash ./sync-skills.sh
```

- `skills/` 정본을 `agent/feature-spec-sb/.claude/skills/`로 복사 · 복사본은 `.gitignore` 대상이라 클론 후 1회 필요

### 작성 규칙 출처 (토큰 선택)

- `SKILL.md` = 절차 · `guides/` = 무슨 내용을 채울지 · 규칙은 두 곳 중 자동 선택

| <div align="center"><sub>상황</sub></div> | <sub>쓰는 것</sub> |
|:---|:---:|
| <sub>`~/.etribe/config.json`에 서버 URL · 토큰 보유</sub> | <sub>ETRIBE 사내 서버 최신본</sub> |
| <sub>설정 부재 또는 서버 접속 실패</sub> | <sub>리포의 `guides/` 로컬 정본</sub> |

- 토큰 유무와 무관하게 같은 단계 · 같은 산출물 · 차이는 서버 쪽 규칙 업데이트 수신 여부뿐
- 서버를 건너뛰고 로컬만 쓰려면 `fetch_guide.py --offline`
- 어느 쪽을 썼는지는 stderr에 표시(`[INFO] 로컬 가이드 사용` 또는 서버 응답)

## 폴더 구성

```
feature-spec-sb/
├── README.md                    이 문서
├── CLAUDE.md                    진입 안내 (폴더를 열면 자동 로딩)
├── SKILL.md                     동작 규칙 정본 (기본 = PC/모바일 B2C 화면설계)
├── ONBOARDING.md                설치 · 사용법 (토큰 설정은 선택)
├── HISTORY.md                   구축 맥락 · 결정사항 · 트러블슈팅 (인수인계용)
├── UPDATE-GUIDE.md              기존 설치 PC 업데이트 절차 (챗봇 어드민 SB 추가분)
├── .gitignore                   빌더 중간물 scripts/_build/ 제외
├── guides/                      작성 규칙 로컬 정본 (토큰 없을 때 사용 · guides/README.md)
│   ├── features-list.md         기능 ID ↔ 기능명 · 카테고리 (14분류 91개)
│   ├── prd-structure.md         PRD 9섹션 + 화면 타입 17종 체크리스트
│   ├── flowchart-rules.md       Mermaid 6도형 · 색상 · 작성 원칙
│   └── sb-writing.md            화면 분리 · Description · Figma 호환
├── rules/                       특수 분기 규칙 (해당 요청일 때만 읽기)
│   ├── admin-sb.md              어드민 분기 (A-1 템플릿 SB · A-1.1 챗봇 어드민 · A-1.2 공통 어드민 규격 · A-2 워크북 → PRD)
│   └── project-kickoff.md       프로젝트 착수 분기 (P-1 신규 서비스 정의 · ia-builder 연동)
├── scripts/
│   ├── fetch_guide.py           작성 규칙 로드 (서버 → 실패 시 guides/ 자동 전환 · --offline)
│   ├── generate_sb.py           screens.json → 화면별 SB HTML (variant별 캔버스 주입 · 로고 검증)
│   ├── build_admin_sb.py        어드민 템플릿 + 화면 본문 → 어드민 SB
│   ├── parse_admin_spec.py      어드민 세부기능정의 워크북 파서 + 커버리지 검증
│   ├── build_chatbot_sb.py      (내부용) 인텐트 워크북 → 챗봇 SB 일체 생성
│   ├── chatbot_to_sb.py         (내부용) 인텐트 워크북 → screens.json
│   ├── chatbot_components.py    (내부용) KRDS 아키타입 12종 렌더러
│   ├── build_component_guide.py (내부용) 챗봇 컴포넌트 카탈로그 HTML
│   └── serve.py                 (내부용) 챗봇 SB 출력 폴더 로컬 미리보기 서버
├── templates/                   SB 출력에 실제로 삽입되는 것
│   ├── sb-style-block.html      SB 인라인 <style> 전체 (시트 골격 · 메타 헤더 · 캔버스 · 푸터)
│   ├── sb-logo-data-url.txt     ETRIBE 로고 base64 (생성 시 MD5 검증 · 수정 금지)
│   ├── etribe-logo.png          로고 원본
│   ├── admin-common.html        공통 어드민 템플릿 (권장 기본)
│   ├── admin-chatbot.html       챗봇 어드민 템플릿
│   ├── admin-krds.html          KRDS 기본 어드민 템플릿
│   └── Commom-sb-styleguide.md  공통 화면설계 구성요소 가이드 (KRDS → 모노톤 변환 기준)
├── reference/                   기존 산출물 레퍼런스 (생성물 미포함)
│   └── admin-common-design-system.html  공통 어드민 디자인 시스템 사본
└── samples/                     HTML로 추출된 화면설계 파일 (samples/README.md)
    ├── admin/                   어드민 화면 본문 src 12장 (KT AX 화면만)
    └── b2c/                     범용 B2C 완성 예시 · mobile 4 · pc 4 · long-page 1 + 입력 json
```

### 폴더 역할 구분

이름이 비슷해 헷갈리기 쉬운 폴더의 경계

| <div align="center"><sub>폴더</sub></div> | <sub>담는 것</sub> | <sub>판단 기준</sub> |
|:---|:---:|:---:|
| <sub>`samples/`</sub> | <sub>HTML로 추출된 **화면설계 파일**</sub> | <sub>`admin/` = 본문 src · `b2c/` = 완성 결과물 · 새 화면을 그릴 때 패턴 참고</sub> |
| <sub>`reference/`</sub> | <sub>**기존 산출물 레퍼런스** (디자인 시스템 등)</sub> | <sub>사람이 열어 보는 참고물 · 생성물 미포함</sub> |
| <sub>`templates/`</sub> | <sub>SB 출력에 **실제로 삽입되는** 골격 · 에셋</sub> | <sub>생성물의 일부 (스타일 블록 · 로고 · 어드민 템플릿)</sub> |
| <sub>`rules/`</sub> | <sub>특수 분기 **규칙 문서** (`*.md`)</sub> | <sub>어드민 · 프로젝트 착수 요청일 때만 읽는 지시문</sub> |
| <sub>`guides/`</sub> | <sub>**작성 규칙 정본** (`*.md`)</sub> | <sub>모든 요청의 기본 규칙 · 토큰이 없을 때 `fetch_guide.py`의 읽기 대상</sub> |

- 새 어드민 화면 패턴 = `samples/admin/KTAX-AD-MN01-0000.src.html` · 범용 B2C 화면 패턴 = `samples/b2c/` 완성 예시

## 용어

| <div align="center"><sub>용어</sub></div> | <sub>뜻</sub> |
|:---|:---:|
| <sub>**PRD**</sub> | <sub>기능 하나를 상세 정의하는 명세서 `.md` · 9섹션</sub> |
| <sub>**SB**</sub> | <sub>화면설계서(스토리보드) · 와이어프레임 + Description HTML</sub> |
| <sub>**서비스 정의서**</sub> | <sub>착수 모드의 경량 PRD · 서비스 전체의 개요 · 목표 · 대상 사용자 · 범위만 정리 · 9섹션 PRD와 별개 문서</sub> |
| <sub>**기능 ID · 카테고리**</sub> | <sub>`A-XX` → `01_auth_account` · `B-XX` → `02_mypage_personalization` · `C-XX` → `03_content_board` 등 · `ADM-XX` 별도 · 정확한 매핑은 `guides/features-list.md`</sub> |
| <sub>**화면 ID**</sub> | <sub>기능 ID + 일련번호 3자리 (예 `A-01-001`)</sub> |
| <sub>**variant**</sub> | <sub>SB 양식 종류 · 모바일(`mobile`) 또는 PC(`pc`)</sub> |
| <sub>**Description**</sub> | <sub>SB 우측 패널의 번호별 설명 · 캔버스 넘버 배지와 1:1</sub> |
| <sub>**screens.json**</sub> | <sub>화면별 본문(와이어프레임 + Description)을 담아 `generate_sb.py`에 넘기는 입력 파일</sub> |
| <sub>**slug**</sub> | <sub>착수 모드 산출물 폴더명 · 영문 · 숫자 · 하이픈 (예 `test-commerce`)</sub> |

## 자주 묻는 질문

| <div align="center"><sub>질문</sub></div> | <sub>답</sub> |
|:---|:---:|
| <sub>토큰 필요 여부</sub> | <sub>불필요 · `guides/` 로컬 정본으로 같은 단계 · 같은 산출물 · 토큰은 사내 서버 최신 규칙 수신용</sub> |
| <sub>`[INFO] 로컬 가이드 사용` 표시</sub> | <sub>정상 · 토큰 없이 리포 규칙으로 동작 중</sub> |
| <sub>`[WARN] 서버에 닿지 못했습니다` 표시</sub> | <sub>로컬 규칙으로 자동 전환 · 작업 계속 · 서버 규칙이 필요하면 네트워크 · URL 확인</sub> |
| <sub>`HTTP 401` 표시</sub> | <sub>토큰 오타 또는 만료 · 작업은 로컬 규칙으로 계속 · `config.json` 수정 또는 관리자에게 새 토큰 요청</sub> |
| <sub>PC · 모바일 둘 다 필요</sub> | <sub>한쪽 완료 후 별도 요청으로 다른 쪽 · 화면 분리 결과와 콘텐츠는 두 양식 동일</sub> |
| <sub>긴 화면 잘림 여부</sub> | <sub>잘림 미발생 · 캔버스 높이는 하한만 지정 · 예시 `samples/b2c/long-page/`</sub> |
| <sub>모달 · 다이얼로그 파일 분리 여부</sub> | <sub>별도 파일 금지 · 메인 캔버스 우측 서브 캔버스(예시 `samples/b2c/*/A-01-003.html`) · 공통 어드민 템플릿만 팝업 = 별도 SB 페이지(알럿 · 토스트는 서브 캔버스)</sub> |
| <sub>「패턴 따라가자」의 의미</sub> | <sub>ETRIBE 공통 패턴 자동 적용 · 목록 정렬 고정 우선 → 작성일 DESC · 페이지네이션 10건/페이지 · 모달 닫기 X 버튼 + 배경 클릭 + ESC · 상태/에러 G-01 매핑</sub> |
| <sub>Figma 임포트 후 볼드가 풀리는 현상</sub> | <sub>Static Pretendard 미설치가 원인 · Static OTF/TTF 설치 후 Figma 재시작 (`HISTORY.md` §10.3)</sub> |
| <sub>Figma에서 Description 줄별 분리</sub> | <sub>`<div>` 분리 · CSS `::before` 사용이 원인 · 한 항목 = 하나의 `<p class="desc-block">` 규칙 확인</sub> |
| <sub>SB 로고 손상</sub> | <sub>base64 문자열 손상 · `generate_sb.py`의 PNG MD5 자동 검증 · 손상 시 `templates/sb-logo-data-url.txt` 재생성 (`HISTORY.md` §10.1)</sub> |
| <sub>기능 ID 목록 위치</sub> | <sub>`guides/features-list.md` · 인증/계정 · 마이페이지 · 콘텐츠/게시판 등 13분류 69개 + 어드민 확장 22개</sub> |

## 주의

- 토큰 없이 동작 · 토큰 설정 시 ETRIBE 사내 서버(Vercel) 최신본 우선, 서버본은 디스크 저장 금지(메모리에서만 사용) · 토큰 발급 · 회전은 `HISTORY.md` §6
- 규칙 수정 시 양쪽 동기화 · `guides/`만 고치면 토큰 사용자에게 미반영
- `samples/admin/`에는 KT AX 화면만 수록 · 원본 AX-Pilot에 있던 타 고객 샘플 미이관
- 원본 리포(AX-Pilot)는 공개 저장소 · 고객 자료 추가 시 어느 쪽에 넣을지 확인
- 기본 모드 산출물 폴더(`01. 공통 기능/` · `90. 어드민/`)는 `.gitignore` 미등록 · 고객 자료가 담기면 커밋 전 확인

## 릴리즈노트

| <div align="center"><sub>요약내용</sub><img width="1" height="1"></div> | <sub>업데이트 일자</sub><img width="1" height="1"> | <sub>소유자</sub><img width="45" height="1"> |
|:---|:---:|:---:|
| <sub>README 전면 개편 — 목적 · 넣는 것 · 산출물 형태 · 요청 예시 · 진행 단계 순으로 재구성, 릴리즈노트 맨 아래로 이동</sub> | <sub>2026.11.13</sub> | <sub>김단영</sub> |
| <sub>Dan Jr. 등급 조회 추가 — 작성자명·양식 질문 직전 `persona.md` 확인(A 진행·B 보고·C 질문), Step 0.1·2.5 승인은 유지</sub> | <sub>2026.10.22</sub> | <sub>김단영</sub> |
| <sub>**(0) 프로젝트 착수 모드 신설** — 서비스명(프로젝트명)·디바이스(PC/모바일 웹) 확인 → 서비스 정의서(경량 PRD) → IA 생성(`ia-builder` 스킬 호출) → 화면별 플로우차트 → SB 추출까지 잇는 신규 파이프라인. `rules/project-kickoff.md` 신설, `sync-skills`에 이 폴더 추가(ia-builder 자동 로드). IA↔SB 연결 지점 실행 검증 완료</sub> | <sub>2026.08.03</sub> | <sub>김단영</sub> |
| <sub>**토큰 프리 전환** — 작성 규칙 정본을 `guides/` 4종(features-list·prd-structure·flowchart-rules·sb-writing)으로 수록. `fetch_guide.py`가 «토큰 있으면 서버 최신본, 없으면 로컬 정본»으로 자동 폴백(`--offline` 옵션). 이미 리포에 구현된 시트 CSS·KRDS 컴포넌트·챗봇 카탈로그는 중복 수록하지 않음. CLAUDE.md·README에 단계별 사용법 명시. 원작자(황다혜 프로) 표기 전 문서 삽입. 검증: 설정 파일 제거 상태에서 SB 8장 192개 검사 + 어드민 9장 전부 통과</sub> | <sub>2026.08.03</sub> | <sub>김단영</sub> |
| <sub>하네스 실동작 테스트 후 수정 — ① PC 캔버스 세로 Flexible 명시(`height:auto` + `--canvas-min-height`, 인라인 높이 고정 시 경고) ② 챗봇·어드민 워크북 경로 하드코딩 제거(원제작자 macOS 경로·고객 파일명 삭제, 미지정 시 설정 방법 안내) ③ `build_chatbot_sb.py`의 스킬 경로를 스크립트 위치 기준으로 변경</sub> | <sub>2026.08.03</sub> | <sub>김단영</sub> |
| <sub>`templates/Commom-sb-styleguide.md` 신규 — KRDS v1.0.0 Figma 공통 컴포넌트 12종 + 디자인 스타일 토큰을 **모노톤(블랙·무채색)** 화면설계 구성요소 가이드로 변환. 토큰(램프/타이포/간격/라운드)·컴포넌트별 Variant·치수·모노톤 색상 매트릭스·SB 표기 규칙·KRDS 원본 컬러 대조표 수록</sub> | <sub>2026.08.03</sub> | <sub>김단영</sub> |
| <sub>폴더 정리 — `references/`를 `rules/`로 옮겨 `reference/`와의 이름 중복 해소. reference=기존 산출물 레퍼런스 · samples=화면설계 HTML · templates=출력 에셋(로고 원본 이동)으로 역할 분리</sub> | <sub>2026.08.03</sub> | <sub>김단영</sub> |
| <sub>최초 등록 — AX-Pilot에서 이관. 범용 PC/MO B2C 화면설계를 기본으로 재구성(챗봇·어드민 규칙 분리) + 회귀 3건 수정</sub> | <sub>2026.08.03</sub> | <sub>김단영</sub> |
