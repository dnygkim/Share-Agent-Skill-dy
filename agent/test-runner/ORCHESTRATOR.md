# ORCHESTRATOR — 테스트 실행 파이프라인

> 이 하네스는 `.claude/`가 아닌 일반 폴더라 **자동 트리거되지 않는다.** 메인 에이전트(나)가 이 문서를 읽고 직접 실행한다. runner 단계는 서브에이전트에 넘기지 않고 내가 브라우저 도구를 직접 조작한다.

## 실행 모드
**파이프라인(순차)** + 실행 계획 GATE 1회 + 수동 개입 지점에서만 대기. 회차(run) = 디바이스 1개 × TC 범위 1세트.

```
device-checker → tc-loader ─[GATE: 실행 계획 승인]─▶ runner ─▶ reporter ─▶ 완료 보고
   (환경 확인)    (엑셀→tc.json)                    (TC 수행·판정·증적)  (엑셀 사본·HTML)
                                                      │ 자동화 불가 단계
                                                      └─ 사용자에게 묻고 대기 → 「계속」
```

## Phase 0: 컨텍스트 확인 (시작 시 반드시)
- **프로젝트별 폴더 격리**: `input/{slug}/` · `_workspace/{slug}/` · `output/{slug}/`. `slug = {클라이언트}-{주제}`.
- `_workspace/{slug}/runs/` 상태로 모드 결정:
  - 비어 있음 → **신규 회차**(Phase 1부터)
  - 이전 회차 있음 + 같은 디바이스 재실행 요청(「Fail만 다시」「수정 반영 확인」) → **재실행 회차**: 새 run_id, 범위 기본값 = 직전 회차의 Fail·Block TC. 직전 run.json은 손대지 않음
  - 이전 회차 있음 + 다른 디바이스 → **신규 회차**(tc.json 재사용, 엑셀이 바뀌었으면 다시 로드)
- 시각 표시: `현재 HH시 MM분입니다. 작업 시작합니다.`

## Phase 1: 인테이크 (CLAUDE.md §2 순서 — 하나씩)
① 업무명 → ② TC 엑셀 확정(없으면 qa-master 모드 1 추출 → 사용자 확인) → ③ 디바이스 1개 → ④ 엔진 → ⑤ TC 범위 → ⑥ 접속정보(세션 내 보관) → ⑦ 수동 개입 모드(기본 유인) → ⑧ 스타일 확인(HTML 리포트).
- Dan Jr. 등급을 먼저 본다 — ① 처음 쓰는 업무명 F-02(C) · ⑧ D-01(A·하네스는 한 번 묻기) · 그 외는 persona.md에 없으므로 묻는다.

## Phase 2~5: 단계 실행 — `{ws}` = `_workspace/{slug}/`, `{run}` = `{ws}/runs/{run_id}/`

| Phase | 에이전트 | 수단 | 입력 | 출력 |
|---|---|---|---|---|
| 2 | **device-checker** | PowerShell · 브라우저 도구 | 인테이크 ③④ | `{run}/run.json` 머리말(profile·engine·browser 실측값) — `scripts/init_run.mjs` |
| 3 | **tc-loader** | `scripts/load_tc.mjs` | `input/{slug}/*.xlsx` | `{ws}/tc.json` + 실행 계획 표(GATE 제시용) |
| — | **GATE (실행 계획 승인)** | — | 계획 표 | 사용자 승인 ← 수행 전 유일한 분기점 |
| 4 | **runner** | claude-in-chrome 도구 또는 `scripts/pw_run.mjs` | tc.json · run.json · 접속정보 | `{run}/run.json` results[] + `output/{slug}/evidence/{run_id}/*.png` |
| 5 | **reporter** | `scripts/write_results.mjs` · `scripts/build_report.mjs` | run.json · 원본 엑셀 | `output/{slug}/` 결과 엑셀 사본 + HTML 리포트 |

### Phase 2 — device-checker
1. 서브모니터 Bounds 조회(`[System.Windows.Forms.Screen]::AllScreens`, `Primary=False`). 없으면 기록해 두고 완료 보고에 한 줄.
2. 엔진별 준비:
   - **claude-in-chrome**: `tabs_context_mcp` → 새 창 생성 → 서브모니터로 이동(`SetWindowPos`) → 그 창의 탭 ID만 사용. MW/APP-WV는 DevTools 디바이스 모드가 아니라 `resize_window`로 뷰포트를 프로필 값으로 맞추고, UA는 바꾸지 않는다(한계를 run.json `profile.note`에 기록).
   - **Playwright**: `scripts/pw_run.mjs --check`로 설치 확인(미설치면 `scripts/README.md` 설치 절차 안내 후 대기). 프로필은 `references/device-profiles.md` §2 표의 Playwright 디바이스명.
3. 실측값(브라우저 버전·OS·뷰포트·DPR)을 `init_run.mjs` 인자로 넘겨 `run.json` 생성.

### Phase 3 — tc-loader
1. `node scripts/load_tc.mjs <엑셀> --out {ws}/tc.json` — 시트 「테스트 시나리오」「테스트케이스」를 헤더명 기준으로 파싱(제출용 변형·컬럼 순서 변경 허용). 「출처」 빈 TC·시나리오 ID 불일치는 경고로 출력.
2. 인테이크 ⑤ 범위로 필터해 **실행 계획 표**를 만든다: 시나리오 ID · 시나리오명 · 대상 TC 수 · 우선순위 분포 · 제외 사유(범위 밖 · APP 네이티브 · 기대결과 `[확인 필요]`).
3. 예상 소요 = TC 수 × 디바이스별 평균(PC 1.5분 · MW 2분, 수동 개입 TC는 별도 표기).
4. **GATE**: 표 + 「회차 ID · 디바이스/프로필 · 엔진 · 접속 URL · 수동 개입 모드」를 제시하고 승인을 받는다. 승인 시 run.json `scope`에 확정 범위 기록.

### Phase 4 — runner (판정 정본 = `references/result-rules.md`)
- **순서**: 시나리오 ID 오름차순 → 그 안의 TC ID 오름차순. 사전조건 연결이 끊기지 않게 시나리오를 중간에 건너뛰지 않는다.
- **TC 1건 수행 루프**:
  1. 사전조건 확인(로그인 상태 · 데이터). 안 맞으면 만들 수 있으면 만들고, 못 만들면 Block(`PRECOND`).
  2. 테스트 절차를 번호 순서로 수행. **절차에 없는 조작을 보태지 않는다**(우회해서 Pass 만들기 금지).
  3. 마지막 절차 직후 화면 캡처 → `evidence/{run_id}/{TC ID}.png`.
  4. 기대결과와 대조 → Pass / Fail / Block. Fail이면 오류 화면 `{TC ID}_fail.png` 추가, 콘솔 오류(`read_console_messages`)가 있으면 「실제 결과」에 요약.
  5. run.json `results[]`에 1건 append(**TC마다 즉시 저장** — 중단돼도 기록이 남게).
- **자동화 불가 단계**(OTP · 실결제 · 메일/SMS 수신 · 실물 기기 · 캡차): 유인 모드면 「TC-xxx 절차 N: {무엇을} 처리해 주세요. 끝나면 「계속」」이라고 묻고 대기 → 이어서 수행. 무인 모드면 Block(`MANUAL`) 후 다음 TC.
- **APP-WV 회차**: 네이티브 기능 TC는 수행 시도 없이 Block(`NATIVE`). 웹뷰 화면 TC는 MW 프로필로 수행하고 「발견 환경」에 `APP-WV(모바일 웹 대체)` 표기.
- **Playwright 경로**: 시나리오 단위로 `plan_{시나리오ID}.json`을 만들어 `node scripts/pw_run.mjs --plan ... --out {run}/pw_{시나리오ID}.json --evidence output/{slug}/evidence/{run_id}` 실행 → 결과 JSON의 단계별 성공/실패·스크린샷을 보고 **판정은 내가** 한다(스크립트의 expect 실패 = Fail 후보, 최종 판정은 기대결과 대조). 로그인 세션은 `--user-data-dir {run}/profile`로 유지해 수동 개입(OTP) 뒤에도 이어서 돌린다.
- **중단 규칙**: 같은 원인으로 연속 5건 Fail(서버 다운 · 로그인 불가)이면 남은 TC를 돌리지 않고 사용자에게 보고 → 계속/중단 확인. 그 외에는 끝까지.

### Phase 5 — reporter
1. `node scripts/write_results.mjs --run {run}/run.json --src <원본 엑셀> --out output/{slug}/<파일명>.xlsx` — 원본을 복제해 「테스트케이스」 시트 실행 컬럼(실행결과 · 실제 결과 · 재현 절차 · 발견 환경 · 상태 · 비고)을 TC ID 기준으로 채우고, 「개요」 시트 끝에 회차 정보·집계 행을 추가. 범위 밖 TC는 `미실행` 유지.
2. `node scripts/build_report.mjs --run {run}/run.json --tc {ws}/tc.json --out output/{slug}/<파일명>.html [--css <경로>] [--embed]` — 하우스 스타일 문서형 HTML. 구성: 표지 → 목차 → 1 실행 개요(스탯) → 2 시나리오별 결과 → 3 오류(Fail) 목록·증적 → 4 보류(Block) 목록·사유 → 5 수동 확인 목록 → 6 전체 TC 결과 표 → 출처. 섹션 헤드라인은 거버닝 메시지 문체(명사형 상태 묘사).
3. 자기검증: run.json results 수 = 엑셀에 기입된 수, evidence 파일 수 ≥ Pass+Fail 수, 비밀값 패턴(비밀번호 입력값) 잔존 0건.
4. 완료 보고(CLAUDE.md §10) + 시각 표시.

## ★ 파일 네이밍 표준 (정본 — 모든 단계가 따른다)
- `run_id = {YYYYMMDD}-{디바이스}-{NN}` (예 `20261104-PC-01`). NN은 같은 날 같은 디바이스 회차 순번.
- `_workspace/{slug}/tc.json` · `_workspace/{slug}/runs/{run_id}/run.json` · `plan_{시나리오ID}.json` · `pw_{시나리오ID}.json`
- 결과 엑셀: `output/{slug}/{업무명}-테스트실행결과({디바이스}{NN}회차)-v0.1-{YYYYMMDD}.xlsx` — 전역 파일명 규칙 「업무 산출물」 트랙. 공식 산출물이면 `{프로젝트코드}-TE-테스트실행결과({디바이스}{NN}회차)-v0.1-{YYYYMMDD}.xlsx`.
- HTML 리포트: 같은 이름 `.html`.
- 증적: `output/{slug}/evidence/{run_id}/{TC ID}.png` · `{TC ID}_fail.png`.
- 같은 회차를 다시 저장하면 버전 +0.1(v0.2). 새 회차는 NN +1.

## 데이터 전달 프로토콜
- **run.json이 회차의 정본**(스키마 = `references/run-schema.md`). 엑셀·HTML은 run.json에서 생성한 파생물 — 손으로 고치지 않고 run.json을 고친 뒤 재생성.
- tc.json은 엑셀 파생물 — 엑셀이 바뀌면 다시 로드.
- 접속정보는 세션 메모리에만. run.json에는 `base_url`과 계정 ID만.

## 에러 핸들링
- 브라우저 도구 호출 실패 2~3회 → 같은 조작을 반복하지 않고 해당 TC Block(`TOOL`) + 사용자에게 상황 보고 후 계속 여부 확인.
- 페이지 로드 타임아웃 → 1회 재시도 후 Fail(실제 결과에 「응답 없음 N초」).
- 대상 화면 접근 차단(권한·IP) → 해당 시나리오 전체 Block(`ACCESS`) + 보고. 임의 우회 금지.
- 엑셀 파싱 실패(시트명·헤더 불일치) → tc-loader가 발견한 시트·헤더를 보여 주고 매핑을 사용자에게 확인.
- 세션 중단(컨텍스트 요약 등) → run.json results[]가 마지막 기록이므로 거기서 이어서 수행(이미 기록된 TC는 건너뜀).

## 테스트 시나리오
**정상 흐름**: "input/acme-shop/의 TC 엑셀 PC에서 돌려줘"
→ 인테이크(업무명·엔진·범위·접속정보·개입 모드·스타일) → device-checker(새 Chrome 창 서브모니터) → tc-loader(tc.json·계획 표) → GATE 승인 → runner(시나리오 순 수행·전수 증적·run.json) → reporter(엑셀 사본·HTML) → 완료 보고 + 내부망 URL.

**재실행 흐름**: "어제 Fail 난 것만 다시 확인해줘"
→ Phase 0 재실행 회차 판별 → 범위 기본값 = 직전 run.json의 Fail·Block → GATE → 수행 → 새 run_id로 산출.

**모바일 회차**: "같은 TC 모바일 웹으로"
→ 디바이스 MW · 프로필(기본 iPhone 14 · Playwright 권장) → tc.json 재사용 → 새 run_id `…-MW-01`.
