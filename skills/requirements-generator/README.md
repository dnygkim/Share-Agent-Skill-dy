# requirements-generator — 요구사항 정의서 엑셀 생성 스킬

회의록 · RFP · 기존 IA/기능정의 엑셀이나 말로 한 프로젝트 설명을 넣으면 요구사항마다 출처를 밝힌 표준 요구사항 정의서(.xlsx, 17개 항목) 초안이 나오는 스킬

## 한눈에 보기

| <div align="center"><sub>항목</sub></div> | <sub>내용</sub> |
|:---|:---:|
| <sub>목적</sub> | <sub>실제 SI 산출물 양식(`04_요구사항 정의서` 시트) 그대로의 요구사항 정의서 초안 — 지어내지 않고 근거를 밝히고 애매하면 되묻는 방식</sub> |
| <sub>이럴 때 사용</sub> | <sub>회의록 · RFP에서 요구사항 목록 도출 · IA/기능목록 엑셀을 요구사항 정의서로 전환 · RD(요구사항 정의서) 작성</sub> |
| <sub>넣는 것</sub> | <sub>회의록 · RFP · 기존 IA/기능정의 엑셀(첨부 · 붙여넣기) 또는 자연어 프로젝트 설명 · 둘 다 가능 · 작업 폴더에 `_inputs/`가 있으면 관련 자료 먼저 확인</sub> |
| <sub>나오는 것</sub> | <sub>요구사항 정의서 `.xlsx`(시트 `04_요구사항 정의서` · 17개 항목/21개 열) + 결과 요약(총 건수 · AI추정 건수 · 비율 · 경고)</sub> |
| <sub>부르는 법</sub> | <sub>`요구사항 정의서 만들어줘` · `이 회의록으로 요구사항 정의서 뽑아줘` · `IA 엑셀로 요구사항 정의서 만들어줘` · `RD 작성해줘` 등 · 슬래시 명령 `/requirements-generator`</sub> |
| <sub>범위 밖</sub> | <sub>「요구사항이 뭐냐」 같은 개념 질문 · 이미 있는 정의서의 오타 수정</sub> |
| <sub>핵심 원칙</sub> | <sub>근거 없는 요구사항 생성 금지 — 자료에서 나온 항목은 출처 표기 · AI가 관례상 추정한 항목은 `AI추정(확인필요)` 표시 → 결과물 = 완성본이 아닌 믿고 검토할 수 있는 초안</sub> |
| <sub>제작</sub> | <sub>신지은 (GitHub [jieun994](https://github.com/jieun994)) · 이 리포 이관 2026.07.21</sub> |
| <sub>출처</sub> | <sub>[jieun994/zinis_claude_skills](https://github.com/jieun994/zinis_claude_skills) · 원본 경로 `skills/requirements-generator/`</sub> |
| <sub>연계</sub> | <sub>호출 하네스 미지정 · 단독 사용 · 앞 단계 산출물 활용 = [`ia-builder`](../ia-builder/README.md) IA 엑셀 · [`meeting-minutes`](../meeting-minutes/README.md) 회의록</sub> |

## 이렇게 요청

| <div align="center"><sub>상황</sub></div> | <sub>요청 예시</sub> | <sub>나오는 것</sub> |
|:---|:---:|:---:|
| <sub>회의록이 있을 때</sub> | <sub>(회의록 붙여넣기 · 첨부) `이 회의록으로 요구사항 정의서 만들어줘`</sub> | <sub>회의록 근거 요구사항 표 → 엑셀</sub> |
| <sub>IA · 기능목록 엑셀이 있을 때</sub> | <sub>(엑셀 첨부) `이 IA 엑셀 기능목록으로 요구사항 정의서 뽑아줘`</sub> | <sub>시트 · 컬럼 구조 확인 후 요구사항 정의서</sub> |
| <sub>말로만 설명할 때</sub> | <sub>`쇼핑몰 요구사항 정리해서 엑셀로 줘`</sub> | <sub>짧은 되묻기 3~5개 → 초안(추정 항목 `AI추정(확인필요)`)</sub> |
| <sub>목록부터 볼 때</sub> | <sub>`요구사항 목록 뽑아줘`</sub> | <sub>마크다운 표 검토 → 엑셀</sub> |
| <sub>다른 양식을 쓸 때</sub> | <sub>(양식 엑셀 첨부) `이 양식에 맞춰서 요구사항 정의서 만들어줘`</sub> | <sub>첨부 양식 컬럼 기준 정의서</sub> |

## 진행 단계

```
① 입력 감지 · 수집 → ② 빈약 입력 되묻기 → ③ 요구사항 도출(원문 → 추정) → ④ 표 검토(GATE) → ⑤ 엑셀 생성 → ⑥ 결과 요약
```

| <div align="center"><sub>단계</sub></div> | <sub>하는 일</sub> | <sub>사용자 할 일</sub> | <sub>결과물</sub> |
|:---|:---:|:---:|:---:|
| <sub>① 입력 감지 · 수집</sub> | <sub>파일 · 자연어 · 둘 다 판별 · 엑셀은 시트 · 컬럼 구조 요약 후 「이 구조로 읽어도 될지」 확인(임의 파싱 금지)</sub> | <sub>자료 첨부 · **엑셀 구조 해석 확인**</sub> | <sub>1차 근거</sub> |
| <sub>② 빈약 입력 되묻기</sub> | <sub>근거가 부족하면 생성 대신 3~5개 짧은 질문(대상 사용자 · 핵심 기능 수 · 비기능 요건 유무 · 대분류 체계)</sub> | <sub>답변 · 또는 `그냥 알아서`(최소 골격 + 전 항목 `AI추정(확인필요)`)</sub> | <sub>보강 정보</sub> |
| <sub>③ 요구사항 도출</sub> | <sub>원문 매핑 먼저(출처 = `RFP` · `킥오프 회의록` 등) → 관례상 빠진 항목만 추정 보완(출처 `AI추정(확인필요)`) · 원문과 추정 혼합 금지</sub> | <sub>—</sub> | <sub>요구사항 목록</sub> |
| <sub>**④ 표 검토 (GATE)**</sub> | <sub>엑셀 전 마크다운 표로 먼저 제시 · 생략 불가(초안 오류를 사람이 잡는 유일한 지점)</sub> | <sub>**분류 · 우선순위 · 관련화면 · 누락 확인 · 수정**</sub> | <sub>확정 요구사항</sub> |
| <sub>⑤ 엑셀 생성</sub> | <sub>확정 요구사항 → JSON → `build_requirements_xlsx.py` · 요구사항 ID 대분류별 자동 채번</sub> | <sub>—</sub> | <sub>요구사항 정의서 .xlsx</sub> |
| <sub>⑥ 결과 요약</sub> | <sub>파일 경로 · 총 건수 · AI추정 건수 · 비율 · ID 중복 경고 안내 · 추정 30% 이상이면 입력 보강 권고</sub> | <sub>추정 항목 검토</sub> | <sub>결과 요약</sub> |

## 산출물

- 시트 `04_요구사항 정의서` · 1행 제목 `요구사항 정의서` · 3~4행 2단 헤더(검정 배경 + 흰 굵은 글씨) · 5행부터 데이터 · 틀고정 A5
- 파일명 고정 규칙 미지정 · 생성 시 출력 경로 지정

| <div align="center"><sub>항목</sub></div> | <sub>내용</sub> |
|:---|:---:|
| <sub>No</sub> | <sub>순번 자동</sub> |
| <sub>요구사항 ID</sub> | <sub>`REQ-<접두어>-###` · 대분류별 자동 채번</sub> |
| <sub>RFP 매핑 ID</sub> | <sub>RFP 요구사항 번호(예 `SFR-002`)</sub> |
| <sub>Q_N</sub> | <sub>질의사항 연결 번호</sub> |
| <sub>대분류 · 중분류</sub> | <sub>챗봇 · 공통 · 어드민 · 시스템 · 관리 / 대화·인텐트 · 보안 · CI/CD · 데이터 · 테스트 등</sub> |
| <sub>요구사항명(1Depth · 2Depth)</sub> | <sub>상위 명칭 · 하위 명칭</sub> |
| <sub>요구사항 상세설명</sub> | <sub>본문(줄바꿈 허용)</sub> |
| <sub>요청자(소속 · 파트 · 이름 · 요청일시)</sub> | <sub>요청자 정보</sub> |
| <sub>유형</sub> | <sub>기능 · 비기능 · 운영 · 인터페이스 · 보안</sub> |
| <sub>출처</sub> | <sub>**근거 컬럼** — 입력 자료 근거 또는 `AI추정(확인필요)`</sub> |
| <sub>우선순위</sub> | <sub>최상 · 상 · 중 · 하 · 미정</sub> |
| <sub>난이도</sub> | <sub>상 · 중 · 하</sub> |
| <sub>수용 여부 · 담당자 · 처리방안 · 관련 자료</sub> | <sub>검토 · 처리 기록 · 화면 · 문서 링크</sub> |

요구사항 ID 접두어 — 대분류마다 001부터 독립 채번

| <div align="center"><sub>대분류</sub></div> | <sub>접두어</sub> |
|:---|:---:|
| <sub>챗봇</sub> | <sub>`REQ-CHT`</sub> |
| <sub>공통</sub> | <sub>`REQ-COM`</sub> |
| <sub>어드민</sub> | <sub>`REQ-BOS`</sub> |
| <sub>시스템</sub> | <sub>`REQ-SYS`</sub> |
| <sub>관리</sub> | <sub>`REQ-MNG`</sub> |
| <sub>그 외</sub> | <sub>`REQ-ETC`</sub> |

- 출처가 `AI추정`인 행 = 출처 셀 연노랑 강조 · AI추정 비율 30% 이상이면 경고 · 출처가 빈 요구사항은 생성 금지
- 기존 ID를 이어서 쓸 때는 JSON에 기존 ID를 넣으면 다음 번호부터 채번

### 결과 예시

| <div align="center"><sub>No</sub></div> | <sub>요구사항 ID</sub> | <sub>대분류</sub> | <sub>중분류</sub> | <sub>요구사항명</sub> | <sub>상세설명</sub> | <sub>유형</sub> | <sub>출처</sub> | <sub>우선순위</sub> |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| <sub>1</sub> | <sub>REQ-COM-001</sub> | <sub>공통</sub> | <sub>회원</sub> | <sub>회원가입</sub> | <sub>이메일·비밀번호로 가입</sub> | <sub>기능</sub> | <sub>RFP</sub> | <sub>상</sub> |
| <sub>4</sub> | <sub>REQ-CHT-001</sub> | <sub>챗봇</sub> | <sub>대화/인텐트</sub> | <sub>주문조회</sub> | <sub>배송상태 문의 안내</sub> | <sub>기능</sub> | <sub>인텐트정의서</sub> | <sub>중</sub> |
| <sub>10</sub> | <sub>REQ-COM-004</sub> | <sub>공통</sub> | <sub>회원</sub> | <sub>회원 탈퇴</sub> | <sub>탈퇴 및 개인정보 파기</sub> | <sub>기능</sub> | <sub>**AI추정(확인필요)**</sub> | <sub>미정</sub> |

- 실제 결과 예시: `samples/요구사항정의서_예시.xlsx`

### 옵션

| <div align="center"><sub>설정</sub></div> | <sub>기본값</sub> | <sub>변경 방법</sub> |
|:---|:---:|:---:|
| <sub>컬럼 세트</sub> | <sub>표준 17개 항목(실제 양식)</sub> | <sub>다른 회사 · 프로젝트 양식 엑셀 첨부 → 그 양식 컬럼 기준 생성</sub> |
| <sub>우선순위 표기</sub> | <sub>최상/상/중/하/미정</sub> | <sub>요청 시 H/M/L · MoSCoW 등으로 변경</sub> |
| <sub>ID 접두어</sub> | <sub>대분류별 CHT/COM/BOS/SYS/MNG</sub> | <sub>엑셀 생성 전 매핑 조정</sub> |

## 설치 · 단독 사용

```bash
cp -r skills/requirements-generator ~/.claude/skills/requirements-generator
```

- 리포 루트 기준 명령 · 스킬 일괄 설치는 원본 리포 `bash install-global.sh` · 공유 리포 `share/update.sh`
- 의존성: Python 3 + `pip install openpyxl`(미설치 시 스크립트가 설치 안내 후 종료) · `python`이 없으면 `py -3`
- 실행은 Claude 담당 — `python "${CLAUDE_PLUGIN_ROOT}/scripts/build_requirements_xlsx.py" <input.json> <output.xlsx> "프로젝트명"`(Windows PowerShell은 `$env:CLAUDE_PLUGIN_ROOT`) · 입력 JSON 스키마 · 채번 규칙은 [references/template-spec.md](references/template-spec.md)
- 하네스 안에서: 이 스킬을 호출하는 하네스 미지정 · `sync-skills`가 전체 스킬을 `agent/proposal` · `agent/feature-spec-sb` · `agent/test-runner`의 `.claude/skills/`로 복사하므로 그 폴더 세션에서도 사용 가능

## 폴더 구성

```
skills/requirements-generator/
├── SKILL.md                             Claude 작동 정본 (Iron Law · 6단계 워크플로 · 엣지 케이스)
├── README.md                            사람용 안내 (이 문서)
├── references/template-spec.md          컬럼 정의 · 채번 규칙 · 출처(근거) 규칙 · 입력 JSON 스키마
├── scripts/build_requirements_xlsx.py   JSON → 정의서 엑셀 (자동 채번 · AI추정 강조 · ID 무결성 검사)
├── samples/요구사항정의서_예시.xlsx       결과 예시
└── .claude-plugin/plugin.json           플러그인 정보 (제작자 신지은)
```

## 주의

- 결과물 = 초안 · 우선순위 · 분류 · 관련화면은 사람 검증 필요
- 되묻기 신호: 입력이 프로젝트명 한 줄 · 「○○ 만들어줘」 수준 / 첨부 엑셀 컬럼 구조 불확실 / 생성할 요구사항의 30% 이상이 입력 근거 부재
- 근거 없는 우선순위 = `미정` + 검토 요청 · IA가 없으면 관련화면 빈칸 · 모르는 셀은 빈칸
- 「입력이 부족하니 일반적인 기능은 다 넣자」 = 이 프로젝트의 요구사항이 아닌 남의 프로젝트 이야기 → 되묻기
- 대량 입력(요구사항 수백 개) = 화면 · 섹션 단위로 나눠 도출 · ID는 대분류별 카운터로 전체 연속 채번(중복 · 결번 방지)
- 지저분한 첨부 엑셀(병합 셀 · 컬럼 순서 혼재) = 파싱 오류를 숨기지 않고 구조 확인 필요 안내 → 컬럼 매핑 확인
- 중간 실패 = 확정 요구사항 JSON 보존 · 진행 지점 안내 후 그 지점부터 재개

## 릴리즈노트

| <div align="center"><sub>요약내용</sub><img width="1" height="1"></div> | <sub>업데이트 일자</sub><img width="1" height="1"> | <sub>소유자</sub><img width="45" height="1"> |
|:---|:---:|:---:|
| <sub>README 전면 개편 — 목적 · 넣는 것 · 산출물 형태 · 요청 예시 · 진행 단계 순으로 재구성, 릴리즈노트 맨 아래로 이동</sub> | <sub>2026.11.13</sub> | <sub>김단영</sub> |
| <sub>최초 등록 — 신지은 스킬 이관 (jieun994/zinis_claude_skills)</sub> | <sub>2026.07.21</sub> | <sub>신지은</sub> |
