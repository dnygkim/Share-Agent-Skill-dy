# test-runner — 테스트케이스 브라우저 실행 하네스

qa-master 테스트케이스(TC) 엑셀을 넣으면 Claude가 브라우저를 직접 조작해 TC를 하나씩 수행하고, 정상(Pass) · 오류(Fail) · 보류(Block) 판정과 화면 캡처를 기입한 결과 엑셀 사본 · HTML 요약 리포트를 회차별로 만드는 실행 하네스

## 한눈에 보기

| <div align="center"><sub>항목</sub></div> | <sub>내용</sub> |
|:---|:---:|
| <sub>목적</sub> | <sub>사람이 QA하는 순서 그대로의 TC 수행 자동화<br>테스트 환경 확정 → 시나리오 순서대로 진행 → 「테스트 절차」대로 클릭 · 입력 → 「기대결과」와 실제 화면 대조 판정 → 화면 캡처 증적 → 결과 엑셀 · 요약 리포트</sub> |
| <sub>이럴 때 사용</sub> | <sub>기능 테스트 수행 · 수정 반영 재확인(Fail만 다시) · 같은 TC의 PC/모바일 웹 회차 분리 수행 · 반복 회귀 테스트</sub> |
| <sub>넣는 것</sub> | <sub>TC 엑셀(qa-master 양식 · 시트 3개 · 테스트케이스 19컬럼) → `input/{프로젝트}/`<br>TC 엑셀이 없으면 기획서 · 화면설계서(qa-master 모드 1로 TC 추출 후 진행)<br>접속정보(URL · 테스트 계정 · 비밀번호)는 파일 저장 금지 · 대화로만 전달</sub> |
| <sub>나오는 것</sub> | <sub>결과 엑셀 사본(.xlsx) · HTML 요약 리포트(.html) · TC별 증적 PNG → `output/{프로젝트}/`<br>파일명 예 `ACME쇼핑몰-테스트실행결과(PC01회차)-v0.1-20261104.xlsx`</sub> |
| <sub>시작 방법</sub> | <sub>`agent/test-runner/` 폴더에서 Claude Code 실행 → `CLAUDE.md` 자동 로딩 → 「PC에서 이 TC 돌려줘」 요청</sub> |
| <sub>연계</sub> | <sub>앞 단계: `../../skills/qa-master`(TC 설계 · 엑셀 생성 모드 1 · 기획서 QA 모드 2 · 테스트 계획 모드 3) · 이 하네스의 입력 생성<br>공유 절차: `../proposal` 완료 보고의 내부망 URL 절차(`CLAUDE.md` 3c)</sub> |

> **qa-master와의 관계**
> - TC 엑셀 **생성** = 스킬 `../../skills/qa-master`(ISTQB 기반 테스트케이스 생성)
> - TC 엑셀 **실행** = 이 하네스
> - 엑셀 양식은 qa-master 정본 그대로 사용, 양식 변경 금지

## 이렇게 요청

| <div align="center"><sub>상황</sub></div> | <sub>요청 예시</sub> | <sub>나오는 것</sub> |
|:---|:---:|:---:|
| <sub>PC 웹 전체 수행</sub> | <sub>`PC에서 이 TC 돌려줘`</sub> | <sub>PC 회차(`20261104-PC-01`) 결과 엑셀 · HTML 리포트 · 증적</sub> |
| <sub>모바일 웹 · 범위 지정</sub> | <sub>`모바일 웹으로 주문 시나리오만 테스트해줘`</sub> | <sub>MW 회차 · 지정 범위만 수행 · 범위 밖 TC `미실행` 유지</sub> |
| <sub>PC 회차 뒤 같은 TC를 모바일로</sub> | <sub>`같은 TC 모바일 웹으로`</sub> | <sub>새 회차 `…-MW-01` · tc.json 재사용 · 기본 프로필 iPhone 14(Playwright 권장)</sub> |
| <sub>앱 웹뷰 화면</sub> | <sub>`앱 웹뷰 화면도 같은 TC로 돌려줘`</sub> | <sub>APP-WV 회차 · 웹뷰 · 하이브리드 화면만 모바일 웹 대체 수행 · 네이티브 기능은 `Block(NATIVE)` + 실기기 수동 확인 목록</sub> |
| <sub>수정 반영 재확인</sub> | <sub>`어제 Fail 난 것만 다시 확인해줘`</sub> | <sub>새 회차 번호 · 직전 회차의 Fail · Block이 기본 범위 · 직전 기록 보존</sub> |
| <sub>TC 엑셀 없이 기획서만</sub> | <sub>`PC에서 테스트 수행해줘`<br>(`input/{프로젝트}/`에 기획서만)</sub> | <sub>qa-master 모드 1로 TC 추출 → 사용자 확인 → 같은 흐름으로 수행</sub> |

- 요청 뒤 인테이크 8문항을 하나씩 진행 · 요청 문장에 이미 있는 답(예 「PC에서」)은 재질문 생략
- 전체 대화 흐름은 [예시 대화](#예시-대화)

## 진행 단계

```
① 인테이크 → ② device-checker(환경 실측 · 창 준비) → ③ tc-loader(엑셀 로드 · 실행 계획) → ④ GATE(실행 계획 승인) → ⑤ runner(TC 수행 · 판정 · 증적) → ⑥ reporter(결과 엑셀 · HTML) → ⑦ 완료 보고
```

| <div align="center"><sub>단계</sub></div> | <sub>하는 일</sub> | <sub>사용자 할 일</sub> | <sub>결과물</sub> |
|:---|:---:|:---:|:---:|
| <sub>① 인테이크</sub> | <sub>업무명 · TC 엑셀 · 디바이스 · 엔진 · 범위 · 접속정보 · 개입 모드 · 리포트 스타일 8문항 순차 질문</sub> | <sub>질문에 답변(한꺼번에 답변 가능) · 접속정보는 대화로만 전달</sub> | <sub>회차 설정(접속정보는 이 세션 안에서만 사용)</sub> |
| <sub>② device-checker</sub> | <sub>서브모니터에 새 브라우저 창 생성 · 브라우저 버전 · OS · 뷰포트 실측 · 회차 번호 자동 채번</sub> | <sub>—</sub> | <sub>`_workspace/{프로젝트}/runs/{회차ID}/run.json` 머리말</sub> |
| <sub>③ tc-loader</sub> | <sub>TC 엑셀 → `tc.json` 변환 · 사전 점검(출처 빈 TC · 시나리오 ID 불일치 · `[확인 필요]` · 중복 ID) · 범위 적용 실행 계획표 작성</sub> | <sub>—</sub> | <sub>`_workspace/{프로젝트}/tc.json` · 실행 계획표</sub> |
| <sub>**④ GATE · 실행 계획 승인**</sub> | <sub>계획표 + 회차 ID · 디바이스 · 엔진 · 접속 URL · 개입 모드 · 예상 소요 제시</sub> | <sub>**시나리오별 대상 TC 수 · 제외 TC · 접속 URL 확인 후 「진행」 승인** · 대분류별 중간 보고가 필요하면 이때 지정</sub> | <sub>확정 범위(run.json `scope`)</sub> |
| <sub>⑤ runner</sub> | <sub>시나리오 ID → TC ID 순 수행 · 기대결과 대조 판정 · 전수 화면 캡처 · TC마다 즉시 기록</sub> | <sub>자동화 불가 단계(OTP · 실결제 등)만 직접 처리 후 「계속」(유인 모드)</sub> | <sub>run.json 결과 · `evidence/{회차ID}/*.png`</sub> |
| <sub>⑥ reporter</sub> | <sub>원본 엑셀 복제 → 실행 컬럼 기입 · HTML 리포트 생성 · 자기검증(기입 건수 · 증적 수 · 비밀번호 잔존 0건)</sub> | <sub>—</sub> | <sub>결과 엑셀 · HTML 리포트</sub> |
| <sub>⑦ 완료 보고</sub> | <sub>집계 → Fail 목록(증적 경로) → 수동 확인 목록 → 예외 → 산출물 경로 + 내부망 URL</sub> | <sub>Fail은 결함 등록, Block은 조건 준비 후 재실행 판단</sub> | <sub>채팅 보고</sub> |

- GATE 승인 뒤 중간 정지 없이 끝까지 진행(수동 개입 단계 · 같은 원인 연속 Fail 5건 중단 제외)
- 착수 · 완료 시 현재 시각 한 줄 표시
- 단계별 세부 동작은 [단계별 상세](#단계별-상세)

### 인테이크 질문

| <div align="center"><sub>#</sub></div> | <sub>질문</sub> | <sub>답 예시</sub> | <sub>기본값(「알아서」 답변 시)</sub> |
|:---|:---:|:---:|:---:|
| <sub>①</sub> | <sub>업무명(파일명 앞머리)</sub> | <sub>`ACME쇼핑몰`</sub> | <sub>처음 쓰는 이름은 반드시 확인</sub> |
| <sub>②</sub> | <sub>TC 엑셀 정본</sub> | <sub>`input/acme-shop/…v0.1.xlsx`</sub> | <sub>폴더에 1개면 그 파일</sub> |
| <sub>③</sub> | <sub>디바이스(이번 회차 1개)</sub> | <sub>`PC` · `MW` · `APP`</sub> | <sub>필수 답변</sub> |
| <sub>④</sub> | <sub>엔진</sub> | <sub>`claude-in-chrome` · `Playwright`</sub> | <sub>claude-in-chrome</sub> |
| <sub>⑤</sub> | <sub>TC 범위</sub> | <sub>「전체」 · 「주문 대분류만」 · 「우선순위 상만」</sub> | <sub>전체</sub> |
| <sub>⑥</sub> | <sub>접속정보</sub> | <sub>URL · 계정 ID · 비밀번호</sub> | <sub>필수 답변 · 파일 저장 금지</sub> |
| <sub>⑦</sub> | <sub>수동 개입 모드</sub> | <sub>「유인」 · 「무인」</sub> | <sub>유인 · OTP 등은 그 자리에서 사용자에게 요청</sub> |
| <sub>⑧</sub> | <sub>HTML 리포트 스타일</sub> | <sub>「기본으로」 · 「CI 적용」</sub> | <sub>하우스 스타일</sub> |

- 질문 직전 Dan Jr. 등급 조회(`~/.claude/persona/persona.md`) · A 등급은 기본값으로 진행, B는 진행 후 완료 보고에 한 줄, C · 미등록은 질문
- 건너뛴 질문은 완료 보고에 ID 표기(예 「Dan Jr. 적용: D-01(A)」) · 처음 쓰는 업무명(F-02 · C)과 실행 계획 GATE는 항상 사용자 확인

## 산출물

| <div align="center"><sub>파일</sub></div> | <sub>형식</sub> | <sub>위치</sub> | <sub>내용</sub> |
|:---|:---:|:---:|:---:|
| <sub>결과 엑셀</sub> | <sub>xlsx</sub> | <sub>`output/{프로젝트}/`</sub> | <sub>원본 TC 엑셀 복제 + 「테스트케이스」 시트 실행 컬럼 기입 + 「개요」 시트 회차 정보 · 집계<br>예 `ACME쇼핑몰-테스트실행결과(PC01회차)-v0.1-20261104.xlsx`</sub> |
| <sub>HTML 리포트</sub> | <sub>html(하우스 스타일 · 단일 파일)</sub> | <sub>`output/{프로젝트}/`</sub> | <sub>표지 → 목차 → 실행 개요 → 시나리오별 결과 → Fail 목록 · 증적 → Block 목록 · 사유 → 수동 확인 → 전체 TC 결과 → 출처<br>파일명은 결과 엑셀과 같은 이름의 `.html`</sub> |
| <sub>증적</sub> | <sub>png</sub> | <sub>`output/{프로젝트}/evidence/{회차ID}/`</sub> | <sub>TC마다 1장 `{TC ID}.png` · Fail은 오류 화면 `{TC ID}_fail.png` 추가</sub> |
| <sub>회차 기록</sub> | <sub>json</sub> | <sub>`_workspace/{프로젝트}/runs/{회차ID}/run.json`</sub> | <sub>회차 정본 · 환경 실측값 · 확정 범위 · TC별 결과</sub> |
| <sub>TC 파싱본</sub> | <sub>json</sub> | <sub>`_workspace/{프로젝트}/tc.json`</sub> | <sub>엑셀 파생물 · 엑셀이 바뀌면 다시 로드</sub> |
| <sub>Playwright 플랜 · 결과</sub> | <sub>json</sub> | <sub>`_workspace/{프로젝트}/runs/{회차ID}/`</sub> | <sub>`plan_{시나리오ID}.json` · `pw_{시나리오ID}.json` · Playwright 엔진 회차만</sub> |

```
output/{프로젝트}/
├── ACME쇼핑몰-테스트실행결과(PC01회차)-v0.1-20261104.xlsx   ← 결과 엑셀(원본 복제 + 실행 컬럼 기입)
├── ACME쇼핑몰-테스트실행결과(PC01회차)-v0.1-20261104.html   ← HTML 요약 리포트
└── evidence/20261104-PC-01/
    ├── TC-ORD-001.png                                      ← TC마다 1장(전수)
    ├── TC-ORD-002.png
    └── TC-ORD-002_fail.png                                 ← Fail은 오류 화면 1장 추가
```

- 파일명은 전역 규칙의 업무 산출물 트랙(`업무명-문서명-vX.Y-날짜`) · 공식 납품이면 `{프로젝트코드}-TE-…`
- 회차마다 **새 파일** 생성(PC 1회차 · MW 1회차 · PC 2회차 …) · 덮어쓰기 금지 · 같은 회차를 다시 저장하면 버전 +0.1(v0.2)
- 수행 기록의 정본은 `_workspace/{프로젝트}/runs/{회차ID}/run.json` · 엑셀 · HTML은 run.json 파생물이라 수정이 필요하면 run.json 수정 후 재생성
- HTML 증적은 기본 상대경로 링크 · 공유용은 `--embed`로 이미지 인라인 · `<head>`에 수정 이력 메타정보 기록

## 준비 (처음 한 번)

| <div align="center"><sub>순서</sub></div> | <sub>할 일</sub> | <sub>비고</sub> |
|:---|:---:|:---:|
| <sub>①</sub> | <sub>리포 루트에서 `./sync-skills.ps1`(또는 `bash ./sync-skills.sh`) 실행</sub> | <sub>qa-master 등 스킬을 `agent/test-runner/.claude/skills/`로 복사</sub> |
| <sub>②</sub> | <sub>Node.js(npm 포함) 확인</sub> | <sub>스크립트는 Node(ESM) · 창 캡처만 PowerShell · dykim-win11 설치 경로 `C:\Program Files\nodejs`</sub> |
| <sub>③</sub> | <sub>`scripts/` 폴더에서 `npm install`</sub> | <sub>엑셀 읽기 · 쓰기(exceljs) · Playwright 패키지 · 모든 회차에 필요</sub> |
| <sub>④</sub> | <sub>`npx playwright install chromium webkit`</sub> | <sub>Playwright 브라우저(약 300MB) · Playwright 엔진 회차만 · 명령 상세 `scripts/README.md` · dykim-win11은 2026.11.04 설치 완료</sub> |
| <sub>⑤</sub> | <sub>Claude in Chrome 확장 연결 확인</sub> | <sub>claude-in-chrome 엔진 사용 시에만 필요</sub> |
| <sub>(선택)</sub> | <sub>Python + openpyxl</sub> | <sub>TC 엑셀 없이 qa-master 모드 1로 TC를 추출할 때만 필요</sub> |

> **이 PC(dykim-win11) 참고**
> - Claude 세션 셸에 node가 PATH로 잡히지 않는 환경 → `C:\Program Files\nodejs`를 PATH 앞에 붙인 뒤 실행(`scripts/README.md`)
> - Python 미설치(2026.11.04 기준) → qa-master의 TC 추출(모드 1) 실행 불가 · 엑셀은 다른 PC에서 생성하거나 Python 설치 후 생성

## 폴더 구성

```
agent/test-runner/
├── CLAUDE.md                  # 하네스 규칙 (폴더에서 Claude Code 실행 시 자동 로딩)
├── ORCHESTRATOR.md            # 파이프라인 · GATE · 파일 네이밍 (실행 정본)
├── agents/                    # device-checker · tc-loader · runner · reporter 역할 정의
├── references/
│   ├── device-profiles.md     # 디바이스 코드 · 뷰포트/UA 프로필 표 · 엔진 선택 기준 · 창 배치
│   ├── result-rules.md        # Pass/Fail/Block 판정 원칙 · 보류 사유 코드 · 엑셀 기입 형식
│   └── run-schema.md          # tc.json · run.json · Playwright 플랜 스키마
├── scripts/                   # Node — load_tc · init_run · add_result · write_results · build_report · pw_run · capture_window.ps1 (README.md)
├── .claude/skills/            # sync-skills 생성 사본(qa-master 등) · Git 미추적
├── input/{프로젝트}/           # TC 엑셀 (접속정보 파일 금지)
├── _workspace/{프로젝트}/      # tc.json · runs/{회차ID}/run.json (회차 정본)
└── output/{프로젝트}/          # 결과 엑셀 · HTML 리포트 · evidence/{회차ID}/*.png
```

- `input/` · `_workspace/` · `output/` · `scripts/node_modules/` · Playwright 프로필은 Git 미추적(폴더 구조만 유지)

## 용어

| <div align="center"><sub>용어</sub></div> | <sub>뜻</sub> |
|:---|:---:|
| <sub>**회차(run)**</sub> | <sub>디바이스 1개로 TC를 한 바퀴 도는 단위 · 번호는 「날짜-디바이스-순번」(예 `20261104-PC-01`) · PC와 모바일을 모두 보면 회차 2개</sub> |
| <sub>**판정값**</sub> | <sub>사용자 용어 정상 · 오류 · 보류 = 엑셀 값 `Pass` · `Fail` · `Block` · 범위 밖 TC는 `미실행` 유지</sub> |
| <sub>**증적**</sub> | <sub>TC마다 마지막 절차 직후 화면을 저장한 PNG · 전수 저장</sub> |
| <sub>**엔진**</sub> | <sub>브라우저 조작 수단 · claude-in-chrome(지금 연결된 Chrome, 로그인 세션 그대로) 또는 Playwright(반복 회귀 · WebKit · 모바일 정밀 에뮬레이션)</sub> |
| <sub>**유인 · 무인**</sub> | <sub>자동화 불가 단계(OTP · 실결제 · 메일 수신 확인 · 실물 기기) 처리 방식 · 유인 = 그 자리에서 사용자 처리 요청 후 대기(기본) · 무인 = `Block(MANUAL)` 기록 후 다음 TC</sub> |

## 단계별 상세

- ① 인테이크는 [인테이크 질문](#인테이크-질문) 표 참고

### ② device-checker (환경 실측 · 브라우저 창 준비)

- 서브모니터 유무 확인 후 **새 브라우저 창을 서브모니터에** 생성 · 사용자의 기존 창 조작 금지 · 서브모니터가 없으면 주 모니터 새 창 + 완료 보고에 한 줄
- 브라우저 버전 · OS · 뷰포트를 실제 조회해 기록 · 추정값 사용 금지
- 모바일(MW)은 뷰포트를 `iPhone 14`(390×844) 등 프로필 값으로 조정 · Playwright는 UA · 터치까지 에뮬레이션, claude-in-chrome은 뷰포트만
- Playwright 엔진은 설치 확인(`pw_run.mjs --check`) · 미설치면 `scripts/README.md` 설치 절차 안내 후 대기
- 결과물: `_workspace/{프로젝트}/runs/{회차ID}/run.json` 머리말(회차 번호 자동 채번)

### ③ tc-loader (엑셀 로드 · 실행 계획표 작성)

- 엑셀의 「테스트 시나리오」 「테스트케이스」 시트를 `tc.json`으로 변환 · 컬럼을 헤더 이름으로 찾는 방식이라 제출용 엑셀(적용 기법 컬럼 제외본)도 처리 가능
- 사전 점검 항목: 출처가 빈 TC · 시나리오 ID 불일치 TC · 기대결과가 `[확인 필요]`인 TC · 중복 TC ID → 경고를 GATE 표에 그대로 표시
- 범위(인테이크 ⑤) 적용 후 **실행 계획표** 작성: 시나리오별 TC 수 · 우선순위 분포 · 수동 개입 예상 · 제외 예정(앱 네이티브 기능 등) · 예상 소요 시간(PC 1.5분/TC · MW 2분/TC)
- 예정 Block 표기: APP-WV 회차의 네이티브 기능 TC → `NATIVE`(수행 생략) · 기대결과 `[확인 필요]` → `EXPECT`(수행 후 Block)
- 시트 · 헤더 이름이 달라 파싱이 실패하면 발견한 시트 · 헤더를 보여 주고 매핑 확인

### ④ GATE (실행 전 사용자 승인 1회)

- 계획표와 「회차 ID · 디바이스 · 엔진 · 접속 URL · 개입 모드」 제시 → **승인 후에만 수행 시작**
- 승인 이후 중간 정지 없이 끝까지 진행(수동 개입 단계 제외)
- 대분류별 중간 보고가 필요하면 이 단계에서 지정

### ⑤ runner (TC 수행 · 판정)

- 수행 주체 = 메인 에이전트 · 브라우저 세션 · 판정 맥락 유지를 위해 서브에이전트 위임 금지
- 수행 순서: 시나리오 ID 순 → 그 안의 TC ID 순(사전조건 흐름 유지)
- TC 1건 처리 순서
  1. **사전조건 확인** — 로그인 상태 · 데이터 불일치 시 준비, 준비 불가 시 보류(`PRECOND`)
  2. **테스트 절차 수행** — 번호 순서 그대로, 절차 밖 조작 금지(우회로 Pass 만들기 금지)
  3. **화면 캡처** — `output/{프로젝트}/evidence/{회차ID}/{TC ID}.png`
  4. **기대결과 대조 · 판정**
     - 일치 → `Pass`
     - 수행은 됐으나 결과 불일치 → `Fail` + 오류 화면 `{TC ID}_fail.png` 추가 + 「실제 결과」에 차이 내용(문구 · URL · 콘솔 오류) 기록
     - 수행 자체가 막힌 경우 → `Block` + 사유 코드(아래 표)
     - 판정이 애매하면 재수행 1회 · 그래도 애매하면 `Block(UNSURE)` · 임의 Pass 금지
  5. **run.json 즉시 기록** — 중간 중단 시에도 그 지점부터 이어서 수행
- **자동화 불가 단계**(OTP · 실결제 · 메일 수신 확인 · 실물 기기) 처리
  - 유인 모드(기본): 「TC-xxx 절차 3: 카드사 OTP를 입력해 주세요. 끝나면 「계속」」 요청 → 대기 → 이어서 수행
  - 무인 모드: 해당 TC `Block(MANUAL)` 기록 후 다음 TC로 이동
- **앱(APP) 테스트**: 앱 내 웹뷰 · 하이브리드 화면만 모바일 웹으로 대체 수행 · 푸시 · 카메라 · 생체인증 · 인앱결제 등 네이티브 기능은 `Block(NATIVE)`로 남겨 실기기 수동 확인 목록에 등록
- **Playwright 엔진**: 시나리오 단위 플랜(`plan_{시나리오ID}.json`) 실행 → 스텝별 성공 · 실패와 캡처 확인 → 최종 판정은 기대결과 대조(스크립트의 expect 실패 = Fail 후보) · `--user-data-dir`로 로그인 · OTP 세션 유지
- **오류 처리**: 페이지 로드 타임아웃 → 1회 재시도 후 Fail(「응답 없음 N초」) · 브라우저 도구 실패 2~3회 → `Block(TOOL)` + 상황 보고 · 화면 접근 차단 → 해당 시나리오 전체 `Block(ACCESS)` + 보고, 임의 우회 금지
- **중단 조건**: 같은 원인의 연속 Fail 5건(서버 다운 등) → 수행 중단 후 계속 여부 확인
- **비밀값**: 비밀번호 입력 화면 캡처는 마스킹(●●●) 확인 · 평문이 보이면 그 장 저장 제외 + 비고에 「증적 생략(비밀값 노출)」
- 회차 종료 시 그 회차용 브라우저 창 닫기

| <div align="center"><sub>보류 사유 코드</sub></div> | <sub>뜻</sub> |
|:---|:---:|
| <sub>`MANUAL`</sub> | <sub>무인 모드에서 자동화 불가 단계 발생</sub> |
| <sub>`PRECOND`</sub> | <sub>앞 TC Fail로 사전조건 준비 불가</sub> |
| <sub>`NATIVE`</sub> | <sub>앱 네이티브 기능(브라우저 수행 불가)</sub> |
| <sub>`EXPECT`</sub> | <sub>기대결과 `[확인 필요]` — 판정 기준 부재</sub> |
| <sub>`UNSURE`</sub> | <sub>재수행 후에도 판정 불명확</sub> |
| <sub>`ACCESS`</sub> | <sub>권한 · IP 차단으로 화면 진입 불가</sub> |
| <sub>`TOOL`</sub> | <sub>브라우저 도구 반복 실패</sub> |
| <sub>`DATA`</sub> | <sub>테스트 데이터(품절 상품 등) 부재</sub> |

- 엑셀 「비고」 앞머리에 `[코드]` 표기(예 `[PRECOND] TC-ORD-003 Fail로 주문 데이터 부재`) · 판정 원칙 정본 `references/result-rules.md`

### ⑥ reporter (결과 엑셀 · HTML 리포트 생성)

- **결과 엑셀**: 원본 엑셀 복제 후 「테스트케이스」 시트의 실행 컬럼(실행결과 · 실제 결과 · 재현 절차 · 발견 환경 · 상태 · 비고) 기입
  - 원본 서식 · 드롭다운 유지
  - 「개요」 시트 끝에 회차 정보 · 집계(Pass / Fail / Block / 미실행) 추가
  - 범위 밖 TC는 `미실행` 유지
- **HTML 리포트**(하우스 스타일): 실행 개요(집계 스탯) → 시나리오별 결과 → Fail 목록(절차 · 기대 · 실제 · 콘솔 오류 · 증적 이미지) → Block 목록 · 사유 → 수동 확인(개입 이력 · 남은 확인) → 전체 TC 표
- **자기검증**: 기록 건수와 엑셀 기입 건수 일치 · 증적 파일 수 · 비밀번호 잔존 0건 · HTML `<head>` 수정 이력 메타정보

### ⑦ 완료 보고

- 한 것 → 집계(시나리오별 포함) → Fail 목록(증적 경로) → 수동 확인 목록 → 「다만」 예외(건너뛴 TC · 접근 불가 화면 · 서브모니터 부재 등) → 산출물 경로 + 내부망 URL
- 채팅 · HTML 표기는 「정상(Pass) · 오류(Fail) · 보류(Block)」 병기 · Fail 목록은 우선순위 상 → 중 → 하 순

## 디바이스 · 엔진 선택 기준

| <div align="center"><sub>디바이스 코드</sub></div> | <sub>뜻</sub> | <sub>수행 방식</sub> |
|:---|:---:|:---:|
| <sub>`PC`</sub> | <sub>데스크톱 웹</sub> | <sub>브라우저 창 그대로 · 기본 프로필 `PC-FHD` 1920×1080</sub> |
| <sub>`MW`</sub> | <sub>모바일 웹</sub> | <sub>모바일 프로필 에뮬레이션 · 기본 `iPhone 14` 390×844 · 그 외 `iPhone SE` · `Pixel 7` · `Galaxy S9+` · `iPad (gen 7)`</sub> |
| <sub>`APP-WV`</sub> | <sub>앱의 웹뷰 · 하이브리드 화면(인테이크 답 `APP`)</sub> | <sub>MW 프로필로 대체 수행 · 네이티브 기능 TC는 `Block(NATIVE)`</sub> |

| <div align="center"><sub>상황</sub></div> | <sub>엔진</sub> |
|:---|:---:|
| <sub>지금 Chrome에 로그인된 세션으로 바로 확인 · 1회성 수행 · 사내망/SSO 사이트</sub> | <sub>**claude-in-chrome**</sub> |
| <sub>같은 TC 반복(회귀) · Safari(WebKit)/Firefox 확인 · 모바일 UA · 터치 정밀 에뮬레이션 · 무인 장시간 실행</sub> | <sub>**Playwright**</sub> |
| <sub>수동 개입이 많은 흐름(OTP · 결제)</sub> | <sub>claude-in-chrome(같은 창에서 사용자가 바로 처리) · Playwright면 `--headed --user-data-dir`로 세션 유지</sub> |

- claude-in-chrome은 UA · 터치 이벤트 변경 불가 → 반응형 레이아웃 확인까지 가능 · UA 분기(모바일 전용 리다이렉트 등)가 있는 사이트는 Playwright
- 한 회차에 두 엔진 혼용 금지 · 섞어야 하면 회차 분리
- 사용자가 특정 기기 · 해상도를 지정하면 그 값이 정본 · 프로필 정본 `references/device-profiles.md`

## 예시 대화

- 실제 대화 흐름 예시 · Claude 발화는 채팅 문장 그대로 표기

```
사용자: input/acme-shop/에 넣은 TC PC에서 돌려줘

Claude: 현재 14시 05분입니다. 작업 시작합니다.
        ACME 쇼핑몰 주문 TC의 PC 실행 결과 엑셀·리포트를 만들겠습니다.
        ① 업무명(파일명 앞머리)을 「ACME쇼핑몰」로 할까요?
사용자: 응
Claude: ② input/acme-shop/에 「테스트케이스_주문_v0.1_20261104.xlsx」 하나가 있습니다. 이 파일로 진행할까요?
사용자: 응
        ※ ③ 디바이스는 요청에 「PC」가 있어 재질문 생략
Claude: ④ 엔진은 지금 연결된 Chrome(claude-in-chrome)으로 할까요, Playwright로 할까요?
사용자: 크롬
Claude: ⑤ 범위는 전체로 할까요?
사용자: 전체
Claude: ⑥ 테스트 대상 URL과 테스트 계정(ID/비밀번호)을 알려 주세요. 파일에는 저장하지 않습니다.
사용자: https://stg.acme.example / qa_user01 / ****
Claude: ⑦ OTP·결제처럼 자동화가 안 되는 단계는 그 자리에서 요청드리고 기다릴까요(유인)?
사용자: 응
Claude: ⑧ HTML 리포트는 기본 스타일로 추출할까요?
사용자: 기본으로

Claude: [실행 계획] 회차 20261104-PC-01 · PC-FHD 1920×1080 · Chrome 130 · 서브모니터
        | 시나리오 | TC | 상/중/하 | 수동 개입 예상 | 제외 |
        | TS-ORD-001 비회원 주문 | 12 | 6/4/2 | — | — |
        | TS-PAY-001 결제 | 8 | 8/0/0 | 2건(OTP) | — |
        … 총 48건 · 예상 소요 72분. 진행할까요?
사용자: 진행

Claude: (TC 수행 중 …)
        TC-PAY-003 절차 4: 카드사 OTP를 입력해 주세요. 끝나면 「계속」이라고 답해 주세요.
사용자: 계속
Claude: (계속 수행 …)

Claude: 현재 15시 20분입니다. 작업 완료했습니다.
        정상(Pass) 41 · 오류(Fail) 4 · 보류(Block) 3 · 미실행 0
        Fail — TC-ORD-007(상) 수량 0 입력 시 안내 없음 … (증적 evidence/20261104-PC-01/TC-ORD-007_fail.png)
        수동 확인 — TC-PAY-003·005 OTP 사용자 처리
        산출물 — output/acme-shop/ACME쇼핑몰-테스트실행결과(PC01회차)-v0.1-20261104.xlsx / .html
        http://10.x.x.x:8003/
```

## 자주 묻는 질문

| <div align="center"><sub>상황</sub></div> | <sub>처리</sub> |
|:---|:---:|
| <sub>TC 엑셀 없이 기획서만 있는 경우</sub> | <sub>qa-master 모드 1로 TC 추출 → 사용자 확인 → 실행 · 단 추출은 Python(openpyxl)이 있는 PC에서만 가능</sub> |
| <sub>모바일도 확인하려는 경우</sub> | <sub>PC 회차 종료 후 「같은 TC 모바일 웹으로」 요청 → 새 회차 `…-MW-01` · UA 분기가 있는 사이트는 Playwright 권장</sub> |
| <sub>수정 반영 여부만 다시 보려는 경우</sub> | <sub>「어제 Fail만 다시」 요청 → 직전 회차의 Fail · Block이 기본 범위, 새 회차 번호로 저장</sub> |
| <sub>기대결과가 `[확인 필요]`인 TC</sub> | <sub>수행 후 `Block(EXPECT)` 기록 · 관찰 내용만 기입, 판정 기준 임의 작성 금지</sub> |
| <sub>기대결과 밖의 문제(디자인 어긋남 등)</sub> | <sub>Fail 근거에서 제외 · 비고에 「참고」로만 기록</sub> |
| <sub>비밀번호 기록 여부</sub> | <sub>run.json · 엑셀 · HTML 어디에도 기록 금지 · 기록 스크립트가 비밀값 패턴 차단 · 평문이 보이는 캡처는 저장 제외</sub> |
| <sub>브라우저 창이 작업 화면을 가리는 경우</sub> | <sub>새 창을 서브모니터에 생성 · 서브모니터가 없으면 주 모니터 새 창 + 완료 보고에 명시</sub> |
| <sub>작업 도중 세션이 끊긴 경우</sub> | <sub>run.json에 TC마다 즉시 기록 → 마지막 기록 다음 TC부터 이어서 수행 · 이미 기록된 TC는 재수행 생략</sub> |
| <sub>엑셀 시트 · 헤더 이름이 qa-master 양식과 다른 경우</sub> | <sub>tc-loader가 발견한 시트 · 헤더 제시 → 매핑 확인 후 진행</sub> |
| <sub>같은 원인으로 Fail이 이어지는 경우(서버 다운 등)</sub> | <sub>연속 5건이면 남은 TC 수행 보류 → 계속 · 중단 여부 확인</sub> |

## 릴리즈노트

| <div align="center"><sub>요약내용</sub><img width="1" height="1"></div> | <sub>업데이트 일자</sub><img width="1" height="1"> | <sub>소유자</sub><img width="45" height="1"> |
|:---|:---:|:---:|
| <sub>README 전면 개편 — 목적 · 넣는 것 · 산출물 형태 · 요청 예시 · 진행 단계 순으로 재구성, 릴리즈노트 맨 아래로 이동</sub> | <sub>2026.11.13</sub> | <sub>김단영</sub> |
| <sub>README 전면 보강 — 처음 쓰는 사람 기준 단계별 동작 설명(사전 준비 → 인테이크 8문항 → device-checker · tc-loader · GATE · runner · reporter → 산출물), 보류 사유 코드 · 예시 대화 · 자주 묻는 질문 추가, 명사형 종결 · 리포 README 표 표기 규칙 적용, scripts/README 설치 명령 보정(PATH 선행)</sub> | <sub>2026.11.04</sub> | <sub>김단영</sub> |
| <sub>최초 등록 — qa-master TC 엑셀을 브라우저(claude-in-chrome · Playwright)에서 직접 수행하고 Pass/Fail/Block·전수 증적을 기입하는 실행 하네스. 회차(디바이스 1개)별 결과 엑셀 사본 + 하우스 스타일 HTML 리포트. Node 스크립트 7종</sub> | <sub>2026.11.04</sub> | <sub>김단영</sub> |
