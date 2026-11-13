# screen-spec-id — IA → 화면명세서 자동생성 에이전트

메뉴구조도(IA) 엑셀을 넣으면 출력 양식 선택 · 대분류 코드표 승인 · 화면ID 채번을 거쳐 화면명세서 초기 버전(v0.x) xlsx를 만드는 에이전트 하네스. 단계마다 사용자 승인 후 다음 단계 진행

## 한눈에 보기

| <div align="center"><sub>항목</sub></div> | <sub>내용</sub> |
|:---|:---:|
| <sub>목적</sub> | <sub>IA 기반 화면ID 채번 · 화면명세서 초안 작성 자동화</sub> |
| <sub>이럴 때 사용</sub> | <sub>IA 확정 직후 화면 목록 · 화면ID 체계 수립 · 채널(PC 웹 · 모바일 웹 · 앱)별 화면 본수 집계</sub> |
| <sub>넣는 것</sub> | <sub>IA 엑셀(채널별 시트 + `No.` 헤더 행 + `Depth 0~N` 계단식 트리) · `input/`에 두거나 대화로 경로 전달 · (선택) 사용자 양식 파일</sub> |
| <sub>나오는 것</sub> | <sub>`output/{프로젝트}_화면명세서_v0.1_{YYYYMMDD}.xlsx` · 기본 양식(샘플타입2) = 표지 · 개정이력 · 규정(코드표) · 채널별 시트</sub> |
| <sub>시작 방법</sub> | <sub>`agent/screen-spec-id/` 폴더에서 Claude Code 실행 → `CLAUDE.md` 자동 로딩 → `이 IA로 화면명세서 만들어줘`</sub> |
| <sub>연계</sub> | <sub>앞 = IA 확정(`skills/ia-builder` 등) · 이름이 비슷한 `agent/feature-spec-sb` = PRD → 화면설계서(와이어프레임 HTML) · 이 하네스 = IA → 화면ID · 화면명세서 엑셀</sub> |
| <sub>범위</sub> | <sub>초기 버전(v0.x) 생성까지 · 설계 중 추가되는 Popup · Tab · Bottom Sheet는 이후 수기 관리</sub> |

## 이렇게 요청

| <div align="center"><sub>상황</sub></div> | <sub>요청 예시</sub> | <sub>나오는 것</sub> |
|:---|:---:|:---:|
| <sub>IA로 새 화면명세서</sub> | <sub>`이 IA로 화면명세서 만들어줘`</sub> | <sub>양식 선택부터 6단계 진행 → v0.1 xlsx</sub> |
| <sub>양식을 정해 둔 경우</sub> | <sub>`샘플타입1 양식으로 화면명세서 만들어줘`</sub> | <sub>목록 · 작업관리형 레이아웃 xlsx</sub> |
| <sub>회사 · 고객 양식 사용</sub> | <sub>`이 양식 파일 구조로 화면명세서 만들어줘` (양식 경로 함께 전달)</sub> | <sub>사용자 양식 레이아웃 xlsx (기타 · `custom`)</sub> |
| <sub>단계 보고를 이어서 받기</sub> | <sub>`한 번에 진행해줘`</sub> | <sub>채번규칙 · 공통영역 보고 연속 수행 · 승인은 단계별</sub> |
| <sub>생성 후 양식만 변경</sub> | <sub>`타입2 양식으로 다시 만들어줘`</sub> | <sub>채번 결과 유지 · 명세서 생성(STEP 6)만 재실행</sub> |
| <sub>채번규칙 · 코드표 변경</sub> | <sub>`일련번호 4자리로 바꿔줘` · `브랜드 코드를 BD로 바꿔줘`</sub> | <sub>config 수정 → 해당 STEP부터 재진행</sub> |

### 예시 대화

```
사용자: 이 IA로 화면명세서 만들어줘
Claude: input/에서 IA 파일을 확인했습니다. 기본양식 2종 비교표입니다. 샘플타입1 · 샘플타입2(기본 권장) · 기타 중 어떤 양식으로 만들까요?
사용자: 타입2
Claude: IA 파싱 결과입니다(시트별 행수 · 화면타입 분포 · 대분류 후보). 프로젝트명과 문서번호를 알려주세요
사용자: 테스트커머스 리뉴얼, TCR-DG-02
Claude: 채번규칙 제안입니다. FO-SB-PW-BR-00012 형식 · 채널 PW/MW · 일련번호 5자리 · 접미사 P/L/T/B. 승인하시면 공통영역 후보로 넘어갑니다
사용자: 승인
```

## 진행 단계

```
STEP 0 입력 확인 → ① 양식 선택(GATE) → ② IA 파싱 → ③ 채번규칙(GATE) → ④ 공통영역 화면ID(GATE) → ⑤ 메뉴별 화면ID(GATE) → ⑥ 명세서 생성 · 검증
```

- 모든 STEP 종료 시 결과 보고 → 「승인」 · 「다음」 · 「진행」 답변 후에만 다음 STEP
- 질문은 한 번에 하나 · 추론 가능한 항목은 질문 생략
- Dan Jr. 등급 조회: 각 STEP 승인 · 「~할까요?」 질문 직전 `persona.md` 확인 → A 기본값 진행 · B 진행 후 완료 보고에 한 줄 · C 또는 해당 항목 부재 시 질문 · 건너뛴 게이트는 완료 보고에 ID 표기(예 「Dan Jr. 적용: F-01(A)」) · 채번규칙 · 코드표 승인처럼 persona.md에 없는 결정은 그대로 사용자 승인

| <div align="center"><sub>단계</sub></div> | <sub>하는 일</sub> | <sub>사용자 할 일</sub> | <sub>결과물</sub> |
|:---|:---:|:---:|:---:|
| <sub>STEP 0</sub> | <sub>입력 확인 · `input/` 최우선 확인(전역 검색 금지) · 비어 있고 경로도 없으면 파일 배치 요청</sub> | <sub>IA 파일을 `input/`에 두거나 경로 전달</sub> | <sub>—</sub> |
| <sub>STEP 1 **GATE**</sub> | <sub>출력 양식 선택 · `samples/` 2종 비교표 제시 · 무응답 시 타입2 권장 이유와 함께 재질문(임의 진행 금지)</sub> | <sub>**양식 선택** · 샘플타입1 · 샘플타입2(기본 권장) · 기타(양식 파일 경로)</sub> | <sub>config `template`(`type1` · `type2` · `custom`)</sub> |
| <sub>STEP 2</sub> | <sub>IA 파싱(`parse_ia.py`) · slug(`{고객}-{주제}`) 1회 확정 · 시트별 행수 · 화면타입 분포 · 대분류 후보 보고</sub> | <sub>구조 보고 확인</sub> | <sub>`_workspace/{slug}/parsed.json`</sub> |
| <sub>STEP 3 **GATE**</sub> | <sub>프로젝트명 · 문서번호 질문 → 채번규칙 표 제안(ID 포맷 · 구분코드 `SB` · 채널코드 `PW` · `MW` · `MA` · 일련번호 5자리 · 접미사 `P` · `L` · `T` · `B`) + IA 시트 → 출력 시트 · 업무구분 · 채널 매핑</sub> | <sub>**프로젝트명 · 문서번호 답변 · 채번규칙과 시트 매핑 확인 · 조정 · 승인**</sub> | <sub>`_workspace/{slug}/config.json`(`id_rule` · `sheets`)</sub> |
| <sub>STEP 4 **GATE**</sub> | <sub>공통영역 후보 제안 → 공통영역 대분류 코드표(영문명 + 2자리) 제안 → `--preview` 결과를 대분류별 표(화면명 · 화면타입 · 채널별 화면ID)로 보고 · 메뉴 대분류 코드 미정분은 `(코드미정)` 표시</sub> | <sub>**공통영역 범위 · 코드표 · 채번 결과 승인**</sub> | <sub>config `common_menus` · `codes`</sub> |
| <sub>STEP 5 **GATE**</sub> | <sub>나머지 대분류 코드표 제안(중복 코드 금지) → `--preview` 재실행 · 미정의 대분류 0건 확인 → 메뉴(대분류)별 표 보고</sub> | <sub>**메뉴별 코드표 · 채번 결과 승인**</sub> | <sub>config `codes` 완성</sub> |
| <sub>STEP 6</sub> | <sub>명세서 생성 · 타입2 = `generate_spec.py` 직접 생성(ID 중복 · 미정의 대분류 자체 검증, 실패 시 중단) · 타입1 · 기타 = preview 결과를 선택 양식 레이아웃으로 변환 → 검증 보고</sub> | <sub>검증 보고 확인</sub> | <sub>`output/{프로젝트}_화면명세서_v0.1_{YYYYMMDD}.xlsx`</sub> |

### STEP 6 검증 보고 (양식 공통 · 필수)

- IA 행수 vs 명세서 행수 일치 여부
- 시트별 본수 합계
- 공통영역 · 메뉴별 채번 범위
- Menu · Link 등 ID 미부여 행 수
- 불일치 시 원인 설명 → 수정 후 재생성

### 인테이크 질문

| <div align="center"><sub>질문</sub></div> | <sub>답 예시</sub> | <sub>기본값</sub> |
|:---|:---:|:---:|
| <sub>출력 양식 (STEP 1)</sub> | <sub>`샘플타입2` · `샘플타입1` · 양식 파일 경로</sub> | <sub>타입2 권장 · 무응답 시 재질문</sub> |
| <sub>프로젝트명 · 문서번호 (STEP 3)</sub> | <sub>`테스트커머스 리뉴얼` · `TCR-DG-02`</sub> | <sub>필수 답변</sub> |
| <sub>채번규칙 조정 (STEP 3)</sub> | <sub>「일련번호 4자리로」 · 「기본값 그대로」</sub> | <sub>`RULES.md` 기본값</sub> |
| <sub>공통영역 범위 (STEP 4)</sub> | <sub>「로그인 · 회원가입 · 검색은 공통」</sub> | <sub>에이전트 제안안</sub> |
| <sub>대분류 코드표 (STEP 4 · 5)</sub> | <sub>「브랜드 = BRAND / BR」</sub> | <sub>에이전트 제안안(영문명 + 2자리)</sub> |

### 수정 요청 처리

| <div align="center"><sub>변경</sub></div> | <sub>처리</sub> | <sub>다시 진행하는 범위</sub> |
|:---|:---:|:---:|
| <sub>양식 변경 (타입1 ↔ 타입2 ↔ 기타)</sub> | <sub>config `template` 수정 · 채번 결과 유지</sub> | <sub>STEP 6만</sub> |
| <sub>채번규칙 변경 (포맷 · 자릿수 · 접미사)</sub> | <sub>config `id_rule` 수정 · 기존 승인 내용 유지, 프리뷰로 변경분만 확인</sub> | <sub>STEP 4부터</sub> |
| <sub>코드표 · 공통영역 변경</sub> | <sub>config만 수정</sub> | <sub>해당 STEP부터</sub> |
| <sub>기본값 자체 변경</sub> | <sub>`RULES.md` · 스크립트 수정</sub> | <sub>—</sub> |

- 생성된 xlsx 직접 수기 편집 금지 · 재생성 시 유실

## 산출물

| <div align="center"><sub>파일</sub></div> | <sub>형식</sub> | <sub>위치</sub> | <sub>내용</sub> |
|:---|:---:|:---:|:---:|
| <sub>`{프로젝트}_화면명세서_v0.1_{YYYYMMDD}.xlsx` (예 `테스트커머스_화면명세서_v0.1_20261113.xlsx`)</sub> | <sub>xlsx</sub> | <sub>`output/`</sub> | <sub>선택 양식 기준 화면명세서 · in-place 갱신 기본, 구조 변경 시에만 버전업</sub> |
| <sub>`parsed.json`</sub> | <sub>json</sub> | <sub>`_workspace/{slug}/`</sub> | <sub>IA 파싱 결과(시트별 행 · Depth 경로 · 화면타입 · 비고 소스)</sub> |
| <sub>`config.json`</sub> | <sub>json</sub> | <sub>`_workspace/{slug}/`</sub> | <sub>승인된 양식 · 프로젝트 정보 · 채번규칙 · 시트 매핑 · 공통영역 · 코드표 (스키마 `references/config-schema.md`)</sub> |
| <sub>일회성 변환 스크립트</sub> | <sub>py</sub> | <sub>`_workspace/{slug}/`</sub> | <sub>타입1 · 기타 양식 선택 시 preview 결과 → 양식 레이아웃 변환</sub> |

### 기본양식 2종 (samples/)

STEP 1 선택지 정본 · 사용자 양식 파일을 대신 제공 가능

| <div align="center"><sub>양식</sub></div> | <sub>파일</sub> | <sub>구조</sub> | <sub>용도</sub> |
|:---|:---:|:---:|:---:|
| <sub>**샘플타입1** 목록 · 작업관리형</sub> | <sub>`samples/화면명세서-샘플타입1.xlsx`</sub> | <sub>단일 시트 화면목록(순번 · 화면코드 PC/MO · depth · 본수) + 기획 · 디자인 · 퍼블리싱 · 프로그래밍 공정률 블록 · `기준` 시트</sub> | <sub>화면목록과 일정 · 진척 관리를 한 문서로 겸할 때</sub> |
| <sub>**샘플타입2** 표준 채번형 (기본)</sub> | <sub>`samples/화면명세서-샘플타입2.xlsx`</sub> | <sub>개정이력 · 규정 + 채널별 시트(No. / 상태 / 수정일 / 채널별 화면ID · 본수 / 화면타입 / 화면명 / Depth 0~N / 비고)</sub> | <sub>표준 채번 기반 화면명세서 · `generate_spec.py` 네이티브 출력</sub> |

- 타입1 · 기타 = preview 채번 결과를 해당 양식 레이아웃으로 변환 생성 · 화면코드 컬럼은 STEP 3 승인 채번규칙 ID(양식 원본의 구식 코드체계를 따르려면 `id_rule`로 조정) · 작업관리 · 공정률 블록은 빈칸(수식 미포함, 사후 수기 관리)

### 샘플타입2 출력 시트 구성

| <div align="center"><sub>시트</sub></div> | <sub>내용</sub> |
|:---|:---:|
| <sub>`표지`</sub> | <sub>프로젝트명 · 문서번호 · 단계 · 작성일 · 버전</sub> |
| <sub>`개정이력`</sub> | <sub>Ver 0.1 신규 1행 (사유: IA 기반 자동 추출)</sub> |
| <sub>`규정`</sub> | <sub>ID 생성규칙 · 접미사 규칙 · 확정된 대분류 코드매핑표(공통영역 메뉴명에 `(공통)` 표기)</sub> |
| <sub>채널별 시트 (예 `FO_Global` · `FO_Chain` · `BO_Admin`)</sub> | <sub>타이틀(2행) · Last Updated · 본수 Total(3~4행) · 헤더(5행) · 데이터(6행~) · 컬럼 = No. / 상태 / 수정일 / [채널/코드] / 채널별 화면ID · 본수 / 화면타입 / 화면명 / Depth 0~N / 비고</sub> |

### 화면ID 형식 (RULES.md 기본값)

```
{업무구분}-{구분}-{채널}-{대분류}-{일련번호5자리}      예) FO-SB-PW-BR-00012 · 같은 페이지의 팝업 FO-SB-PW-BR-00012P1
```

| <div align="center"><sub>세그먼트</sub></div> | <sub>기본값</sub> |
|:---|:---:|
| <sub>업무구분</sub> | <sub>시트별 지정 (예 `FO` · `BO`)</sub> |
| <sub>구분</sub> | <sub>`SB` (스토리보드)</sub> |
| <sub>채널</sub> | <sub>PC WEB `PW` · MO WEB `MW` · APP `MA`</sub> |
| <sub>대분류</sub> | <sub>Depth 1 메뉴 기준 2자리 코드(시트별 `category_key_depth`로 조정) · 에이전트 제안 → 사용자 승인 → `규정` 시트 기록</sub> |
| <sub>일련번호</sub> | <sub>(업무구분, 대분류) 단위로 1부터 순차 · 시트를 넘어 연속 채번 · PC/MW 쌍은 같은 번호</sub> |
| <sub>접미사</sub> | <sub>Popup `P1…` · Layer `L1…` · Tab `T1…` · Bottom Sheet `B1…` · 소속 페이지(같은 대분류의 직전 Page) 번호 뒤에 순차</sub> |

- 프로젝트별 조정 항목(config `id_rule`) = `format`(세그먼트 구성 · 구분자) · `seq_digits`(일련번호 자릿수) · `suffixes`(접미사 문자)
- 공통영역도 각자의 대분류 코드로 채번 · 일련번호가 대분류 단위로 독립이라 메뉴 영역과 번호 충돌 미발생

### IA 행 처리

| <div align="center"><sub>IA 행</sub></div> | <sub>처리</sub> |
|:---|:---:|
| <sub>`Page`</sub> | <sub>ID 채번 · 채널별 본수 1</sub> |
| <sub>`Layer` · `Popup` · `Tab` · `Bottom Sheet`</sub> | <sub>직전 Page ID + 접미사 채번 · 본수 1</sub> |
| <sub>화면타입 공란</sub> | <sub>Page로 간주</sub> |
| <sub>상위 그룹 메뉴 (화면 미보유)</sub> | <sub>`Menu` 행 · ID `-` · 본수 0 · 회색 배경</sub> |
| <sub>`Internal/External Link`</sub> | <sub>행 유지 · ID `-` · 본수 0</sub> |
| <sub>`구분` · `기능` · 기타 컬럼</sub> | <sub>`비고`란에 `[통합/Dynamic] …` 형식으로 이관</sub> |

- 본수 = 해당 채널 ID가 채번되면 1, 아니면 0 · 시트 합계는 SUM 수식
- ID 중복은 생성 시점에 검증 · 중복 발견 시 생성 중단

## 준비 (처음 한 번)

| <div align="center"><sub>준비</sub></div> | <sub>필요한 경우</sub> | <sub>방법</sub> |
|:---|:---:|:---:|
| <sub>Python 3.12 + `openpyxl`</sub> | <sub>모든 실행</sub> | <sub>`pip install openpyxl`</sub> |
| <sub>`input/` 폴더</sub> | <sub>IA 파일을 폴더로 넘길 때</sub> | <sub>리포 미포함(`.gitignore` 대상) · 이 폴더 아래 `input/` 생성 후 IA 배치 · 대화로 경로만 전달해도 진행</sub> |

- `skills/` 스킬 미사용 · `sync-skills` 실행 불필요

## 폴더 구성

```
screen-spec-id/
├── README.md                # 이 문서
├── CLAUDE.md                # 에이전트 지침 (실행 플로우 · 승인 게이트, 폴더를 열면 자동 로딩)
├── RULES.md                 # 채번 · 변환 규칙 기본값 정본
├── samples/                 # 기본양식 2종 (STEP 1 선택지 정본 · 수정 금지)
│   ├── 화면명세서-샘플타입1.xlsx   # 목록 · 작업관리형
│   └── 화면명세서-샘플타입2.xlsx   # 표준 채번형 (기본)
├── scripts/
│   ├── parse_ia.py          # IA xlsx → JSON 트리 (parsed.json)
│   └── generate_spec.py     # 채번 + 명세서 xlsx 생성 (타입2 네이티브) · --preview = 채번 결과 JSON만 출력
├── references/
│   └── config-schema.md     # config.json 스키마 정본
├── input/                   # 사용자 IA 파일 (git 제외 · 배포 시 비우기)
├── _workspace/{slug}/       # parsed.json · config.json 중간물 (git 제외 · 배포 시 비우기)
└── output/                  # 생성된 화면명세서 (git 제외)
```

## 용어

| <div align="center"><sub>용어</sub></div> | <sub>뜻</sub> |
|:---|:---:|
| <sub>**IA (메뉴구조도)**</sub> | <sub>채널별 시트 + `Depth 0~N` 계단식 트리로 된 메뉴 구조 엑셀 · 각 행의 노드 = 가장 깊은 Depth 셀, 상위 경로는 이월</sub> |
| <sub>**화면명세서**</sub> | <sub>화면별 화면ID · 화면타입 · 화면명 · Depth · 채널별 본수를 정리한 목록 문서</sub> |
| <sub>**채번**</sub> | <sub>정해진 규칙으로 화면마다 고유 ID 부여</sub> |
| <sub>**대분류 코드**</sub> | <sub>대분류 메뉴별 영문명 + 2자리 코드 (예 브랜드 = BRAND / BR)</sub> |
| <sub>**공통영역**</sub> | <sub>특정 메뉴에 속하지 않고 서비스 전반에서 쓰는 영역 · 로그인 · 회원가입 · 마이페이지 · 알림 · 검색 · 어권/통화선택 · 약관/정책 · 사이트맵 · GNB/푸터 유틸 등</sub> |
| <sub>**본수**</sub> | <sub>채널별 화면 수 · ID가 채번된 행 = 1</sub> |
| <sub>**slug**</sub> | <sub>프로젝트 중간물 폴더 이름 `{고객}-{주제}` (예 `acme-shop`)</sub> |
| <sub>**preview**</sub> | <sub>`generate_spec.py --preview` · xlsx 없이 채번 결과를 공통영역 / 메뉴별 JSON으로 출력하는 검토 모드</sub> |

## 자주 묻는 질문

| <div align="center"><sub>질문</sub></div> | <sub>답</sub> |
|:---|:---:|
| <sub>IA 시트 미인식</sub> | <sub>헤더 행(상단 10행 이내)에 `No.` 셀 + `Depth 0`~`Depth N` 컬럼 필요 · 둘 중 하나라도 빠지면 그 시트는 파싱 제외</sub> |
| <sub>컬럼 이름 인식 기준</sub> | <sub>「화면타입」이 들어간 헤더 = 화면타입 컬럼 · `구분` · `기능`은 같은 이름일 때만 인식 · 나머지 컬럼은 비고 소스</sub> |
| <sub>코드표에 없는 대분류 존재</sub> | <sub>본 생성은 오류로 중단(코드표 승인 없는 임의 채번 방지 장치) · `--preview`는 `(코드미정)` 표시 후 진행, `summary.undefined_categories`로 목록 확인</sub> |
| <sub>다음 시트 번호가 1부터 시작하지 않는 이유</sub> | <sub>같은 업무구분 안 대분류 카운터를 시트 간 공유 (예 FO_Global `MA-00005` 다음 FO_Chain `MA-00006`)</sub> |
| <sub>나중에 추가되는 Popup · Tab</sub> | <sub>범위 밖 · v0.x 이후 설계 단계에서 수기 관리(샘플 기준 전체 행의 약 60%가 사후 추가분) · IA에 이미 있는 Layer · Popup은 자동 채번</sub> |
| <sub>결과 xlsx 직접 수정</sub> | <sub>수기 편집 금지(재생성 시 유실) · config 수정 후 재생성</sub> |
| <sub>별도 양식 파일 사용</sub> | <sub>STEP 1에서 「기타」 선택 + 양식 경로 전달 → 구조 분석 후 그 레이아웃으로 생성 (config `template` = `custom` · `template_path` 기록)</sub> |

## 주의

- `samples/` = STEP 1 선택지 정본 · 수정 금지
- 자료는 `input/`을 가장 먼저 확인 · 전역 검색 금지
- `input/` · `_workspace/` = 배포 시 비울 폴더 · git 추적 제외
- 결과 xlsx 수기 편집 금지 · 수정은 config 경유 재생성
- 표기 = 한국어 · 파일명 날짜 `YYYYMMDD` · 범위 표기 하이픈(-)

## 버전 이력

| <div align="center"><sub>버전</sub></div> | <sub>일자</sub> | <sub>내용</sub> |
|:---|:---:|:---:|
| <sub>v0.3</sub> | <sub>2026.07.20</sub> | <sub>기본양식 2종(`samples/`) 추가, STEP 1 출력 양식 선택 게이트 도입 (6단계로 재편), config `template` 필드 추가</sub> |
| <sub>v0.2</sub> | <sub>2026.07.15</sub> | <sub>단계별 진행 흐름 도입 (채번규칙 정의 → 공통영역 추출 → 메뉴별 상세 추출, 각 단계 승인 게이트) · `--preview` 모드, config `id_rule` · `common_menus` 추가</sub> |
| <sub>v0.1</sub> | <sub>2026.07.13</sub> | <sub>최초 구축 (샘플: 롯데호텔 채널시스템 리뉴얼 IA · 화면명세서 기반)</sub> |

## 릴리즈노트

| <div align="center"><sub>요약내용</sub><img width="1" height="1"></div> | <sub>업데이트 일자</sub><img width="1" height="1"> | <sub>소유자</sub><img width="45" height="1"> |
|:---|:---:|:---:|
| <sub>README 전면 개편 — 목적 · 넣는 것 · 산출물 형태 · 요청 예시 · 진행 단계 순으로 재구성, 릴리즈노트 맨 아래로 이동</sub> | <sub>2026.11.13</sub> | <sub>김단영</sub> |
| <sub>Dan Jr. 등급 조회 추가 — 각 STEP 승인 직전 `persona.md` 확인(A 진행·B 보고·C 질문), 건너뛴 게이트는 완료 보고에 ID 표기</sub> | <sub>2026.10.22</sub> | <sub>김단영</sub> |
| <sub>v0.3 출력 양식 선택 게이트 도입 + samples 양식 2종 추가</sub> | <sub>2026.07.20</sub> | <sub>김단영</sub> |
| <sub>최초 등록 — IA→화면ID 채번→화면명세서 자동생성</sub> | <sub>2026.07.13</sub> | <sub>김단영</sub> |
