# scripts — test-runner 스크립트

test-runner 하네스가 TC 엑셀 로드 · 회차 기록 · 결과 엑셀 기입 · HTML 리포트 · Playwright 수행 · 창 캡처에 쓰는 스크립트 7종(Node 6종 + PowerShell 1종)과 공통 모듈

## 용도

- 엑셀 · JSON을 손으로 고치지 않고 스크립트로만 읽고 쓰기 위한 입구(하네스 규칙 `../CLAUDE.md` §8)
- 판정은 스크립트 범위 밖 · 최종 판정은 에이전트가 기대결과와 대조
- Node(ESM) 스크립트 + 창 캡처용 PowerShell 1종 · Python 불필요

## 들어 있는 것

| <div align="center"><sub>파일</sub></div> | <sub>역할</sub> | <sub>호출</sub> |
|:---|:---:|:---:|
| <sub>`load_tc.mjs`</sub> | <sub>qa-master 엑셀 → `tc.json` + GATE용 시나리오별 집계 출력</sub> | <sub>`load_tc.mjs <xlsx> --out <tc.json>`</sub> |
| <sub>`init_run.mjs`</sub> | <sub>회차 채번(`YYYYMMDD-{디바이스}-NN`) + `run.json` 머리말 생성</sub> | <sub>`init_run.mjs --slug … --device PC --engine claude-in-chrome --profile PC-FHD --viewport 1920x1080 --browser "…" --os "…" --base-url … --account … --task … --tester … --manual attended --source-xlsx … --tc-json …`</sub> |
| <sub>`add_result.mjs`</sub> | <sub>`run.json`에 결과 추가(재수행은 교체) · 비밀값 패턴 차단 · `--scope-file` 범위 갱신 · `--finish` 종료 시각 기록</sub> | <sub>`add_result.mjs --run <run.json> --tc TC-… --result Fail --actual "…" --env "…" --evidence a.png,b.png` 또는 `--file result.json`</sub> |
| <sub>`write_results.mjs`</sub> | <sub>원본 엑셀 복제 → 실행 컬럼 기입 + 개요 시트 회차 행 추가</sub> | <sub>`write_results.mjs --run <run.json> --src <원본.xlsx> --out <결과.xlsx>`</sub> |
| <sub>`build_report.mjs`</sub> | <sub>하우스 스타일 HTML 리포트(자기완결 단일 파일) 생성</sub> | <sub>`build_report.mjs --run <run.json> --tc <tc.json> --out <리포트.html> [--embed] [--css …] [--client …] [--author …] [--doc-name …]`</sub> |
| <sub>`pw_run.mjs`</sub> | <sub>Playwright 플랜 실행(스텝 수행 · 스크린샷 · 콘솔 오류 수집) · `--check` 설치 확인</sub> | <sub>`pw_run.mjs --plan <plan.json> --out <pw.json> --evidence <폴더> [--headed] [--user-data-dir <폴더>] [--monitor sub\|primary\|X,Y] [--timeout 15000] [--slowmo 0] [--keep-open]`</sub> |
| <sub>`capture_window.ps1`</sub> | <sub>창 제목으로 Chrome 창 캡처 → PNG(claude-in-chrome 증적)</sub> | <sub>`powershell -NoProfile -File capture_window.ps1 -TitleContains "…" -Out <png> [-ProcessName chrome]`</sub> |
| <sub>`_common.mjs`</sub> | <sub>인자 파싱 · 셀 텍스트 · 날짜 유틸</sub> | <sub>내부 모듈</sub> |
| <sub>`package.json`</sub> | <sub>의존성(exceljs · playwright) · npm 스크립트 `check` · `install-browsers`</sub> | <sub>`npm run check` · `npm run install-browsers`</sub> |

- 플랜 · run.json · tc.json 스키마 = `../references/run-schema.md`

## 설치 (처음 한 번 · `scripts/` 안에서)

```powershell
cd scripts
$env:Path = "C:\Program Files\nodejs;" + $env:Path   # npm·npx가 node를 찾도록 PATH 선행
npm install                                          # exceljs · playwright
npx playwright install chromium webkit               # 브라우저(약 300MB) · firefox 필요 시 추가
node pw_run.mjs --check                              # 설치 확인
```

- `npm install`은 모든 회차에 필요(엑셀 읽기 · 쓰기) · 브라우저 설치는 Playwright 엔진 회차만
- PATH 선행 없이 `npx.cmd`를 전체 경로로 부르면 「'node'은(는) 내부 또는 외부 명령 … 아닙니다」 오류로 실패(2026.11.04 확인)
- PATH 선행 후 PowerShell · Git Bash 양쪽에서 `npx playwright` 정상 동작 확인(2026.11.04)

## 실행 방법

- 실행 위치 = `agent/test-runner/` 폴더 · `input/` · `_workspace/` · `output/` 경로 기준
- 이 PC(dykim-win11)는 Python 미설치(2026.11.04 기준) · Claude 세션 셸에 node가 PATH로 잡히지 않는 환경 → `C:\Program Files\nodejs`를 PATH 앞에 붙인 뒤 실행
  - PowerShell: `$env:Path = "C:\Program Files\nodejs;" + $env:Path`
  - Git Bash: `export PATH="/c/Program Files/nodejs:$PATH"` 후 `node scripts/load_tc.mjs …`

### 회차 1개 흐름 예

```powershell
$env:Path = "C:\Program Files\nodejs;" + $env:Path

# ② device-checker — 회차 생성(run_id 자동 채번)
node scripts\init_run.mjs --slug acme-shop --device PC --engine claude-in-chrome --profile PC-FHD --viewport 1920x1080 --browser "Chrome 130" --os "Windows 11" --base-url https://stg.acme.example --account qa_user01 --task ACME쇼핑몰 --tester "{작성자}" --manual attended --source-xlsx input\acme-shop\TC.xlsx --tc-json _workspace\acme-shop\tc.json

# ③ tc-loader — 엑셀 → tc.json + 시나리오별 집계
node scripts\load_tc.mjs "input\acme-shop\TC.xlsx" --out _workspace\acme-shop\tc.json

# ④ GATE 승인 뒤 — 확정 범위 기록
node scripts\add_result.mjs --run _workspace\acme-shop\runs\20261104-PC-01\run.json --scope-file scope.json

# ⑤ runner — 증적 캡처(claude-in-chrome) · TC마다 결과 기록
powershell -NoProfile -File scripts\capture_window.ps1 -TitleContains "ACME" -Out "output\acme-shop\evidence\20261104-PC-01\TC-ORD-001.png"
node scripts\add_result.mjs --run _workspace\acme-shop\runs\20261104-PC-01\run.json --tc TC-ORD-001 --result Pass --evidence evidence/20261104-PC-01/TC-ORD-001.png
node scripts\add_result.mjs --run _workspace\acme-shop\runs\20261104-PC-01\run.json --finish

# ⑥ reporter — 결과 엑셀 · HTML 리포트
node scripts\write_results.mjs --run _workspace\acme-shop\runs\20261104-PC-01\run.json --src input\acme-shop\TC.xlsx --out "output\acme-shop\ACME쇼핑몰-테스트실행결과(PC01회차)-v0.1-20261104.xlsx"
node scripts\build_report.mjs --run _workspace\acme-shop\runs\20261104-PC-01\run.json --tc _workspace\acme-shop\tc.json --out "output\acme-shop\ACME쇼핑몰-테스트실행결과(PC01회차)-v0.1-20261104.html"
```

- Playwright 엔진 회차는 ⑤에서 시나리오 단위 플랜 실행: `node scripts\pw_run.mjs --plan <run 폴더>\plan_TS-ORD-001.json --out <run 폴더>\pw_TS-ORD-001.json --evidence output\acme-shop\evidence\20261104-PC-01 --headed --user-data-dir <run 폴더>\profile`

## 스크립트별 참고

- `init_run.mjs`: `--device`는 `PC` · `MW` · `APP-WV`, `--engine`은 `claude-in-chrome` · `playwright` · 회차 번호 = 같은 날 같은 디바이스 회차 수 + 1 · 비밀번호 · OTP는 인자 대상 제외
- `add_result.mjs`: `Block`은 `--hold` 사유 코드 필수(`MANUAL` · `PRECOND` · `NATIVE` · `EXPECT` · `UNSURE` · `ACCESS` · `TOOL` · `DATA`) · 같은 TC ID 재기록 시 교체 · 실제 결과 · 재현 절차 · 비고 · 발견 환경에 비밀값 패턴(`password=` · `비밀번호:` · `otp=` 등)이 있으면 기록 거부
- `write_results.mjs`: 「테스트케이스」 시트의 「TC ID」 · 「실행결과」 헤더 필수 · 원본 서식 · 드롭다운 유지 · run.json에 있으나 엑셀에서 못 찾은 TC는 경고 출력
- `build_report.mjs`: 스타일 정본 탐색 순서 `--css` → `~/.claude/house-style/house-style.css` → 리포 `global-house-style/house-style.css` · 증적은 기본 상대경로 링크, `--embed`면 base64 인라인(공유용)
- `pw_run.mjs`는 판정 미수행 · expect 실패는 Fail 후보 · 최종 판정은 에이전트가 기대결과와 대조
- `--user-data-dir` 지정 시 headed 영속 컨텍스트로 실행 → 로그인 · OTP 세션을 다음 플랜까지 유지 · 수동 개입 후 같은 폴더로 다음 플랜 실행
- `--monitor sub`(기본): Windows에서 `Primary=False` 모니터 좌표 조회 → chromium 창을 서브모니터에 배치 · headed 실행(`--headed` · `--user-data-dir`)일 때만 적용 · webkit · firefox는 창 위치 인자 미지원이라 주 모니터에 표시(결과 JSON `monitor`에 기록)
- `capture_window.ps1`: 다른 창에 가려진 상태면 가린 내용까지 캡처 → 캡처 전 대상 창을 맨 앞으로 이동 · 최소화 상태는 캡처 불가(오류 종료)
