# scripts — test-runner 스크립트

- 전부 Node(ESM) 스크립트
- 이 PC(dykim-win11)는 Python 미설치 · Claude 세션 셸에 node가 PATH로 잡히지 않는 환경 → `C:\Program Files\nodejs`를 PATH 앞에 붙인 뒤 실행

```powershell
$env:Path = "C:\Program Files\nodejs;" + $env:Path
node scripts\load_tc.mjs "input\acme-shop\TC.xlsx" --out _workspace\acme-shop\tc.json
```

- Git Bash: `export PATH="/c/Program Files/nodejs:$PATH"` 후 `node scripts/load_tc.mjs …`

## 설치 (최초 1회 · `scripts/` 안에서)

```powershell
cd scripts
$env:Path = "C:\Program Files\nodejs;" + $env:Path   # npm·npx가 node를 찾도록 PATH 선행
npm install                                          # exceljs · playwright
npx playwright install chromium webkit               # 브라우저(약 300MB) · firefox 필요 시 추가
node pw_run.mjs --check                              # 설치 확인
```

- PATH 선행 없이 `npx.cmd`를 전체 경로로 부르면 「'node'은(는) 내부 또는 외부 명령 … 아닙니다」 오류로 실패(2026-11-04 확인)
- PATH 선행 후 PowerShell · Git Bash 양쪽에서 `npx playwright` 정상 동작 확인(2026-11-04)

## 스크립트

| <div align="center"><sub>파일</sub></div> | <sub>역할</sub> | <sub>호출</sub> |
|:---|:---:|:---:|
| <sub>`load_tc.mjs`</sub> | <sub>qa-master 엑셀 → `tc.json` + GATE용 시나리오별 집계 출력</sub> | <sub>`load_tc.mjs <xlsx> --out <tc.json>`</sub> |
| <sub>`init_run.mjs`</sub> | <sub>회차 채번(`YYYYMMDD-{디바이스}-NN`) + `run.json` 머리말 생성</sub> | <sub>`init_run.mjs --slug … --device PC --engine claude-in-chrome --profile PC-FHD --viewport 1920x1080 --browser "…" --os "…" --base-url … --account … --task … --tester … --manual attended --source-xlsx … --tc-json …`</sub> |
| <sub>`add_result.mjs`</sub> | <sub>`run.json`에 결과 추가(재수행은 교체) · 비밀값 패턴 차단 · `--scope-file` 범위 갱신 · `--finish` 종료 시각 기록</sub> | <sub>`add_result.mjs --run <run.json> --tc TC-… --result Fail --actual "…" --env "…" --evidence a.png,b.png` 또는 `--file result.json`</sub> |
| <sub>`write_results.mjs`</sub> | <sub>원본 엑셀 복제 → 실행 컬럼 기입 + 개요 시트 회차 행 추가</sub> | <sub>`write_results.mjs --run <run.json> --src <원본.xlsx> --out <결과.xlsx>`</sub> |
| <sub>`build_report.mjs`</sub> | <sub>하우스 스타일 HTML 리포트(자기완결 단일 파일) 생성</sub> | <sub>`build_report.mjs --run <run.json> --tc <tc.json> --out <리포트.html> [--embed] [--css …] [--client …] [--author …]`</sub> |
| <sub>`pw_run.mjs`</sub> | <sub>Playwright 플랜 실행(스텝 수행 · 스크린샷 · 콘솔 오류 수집)</sub> | <sub>`pw_run.mjs --plan <plan.json> --out <pw.json> --evidence <폴더> [--headed] [--user-data-dir <폴더>] [--monitor sub]`</sub> |
| <sub>`capture_window.ps1`</sub> | <sub>창 제목으로 Chrome 창 캡처 → PNG(claude-in-chrome 증적)</sub> | <sub>`powershell -NoProfile -File capture_window.ps1 -TitleContains "…" -Out <png>`</sub> |
| <sub>`_common.mjs`</sub> | <sub>인자 파싱 · 셀 텍스트 · 날짜 유틸</sub> | <sub>내부 모듈</sub> |

- 플랜 · run.json · tc.json 스키마 = `../references/run-schema.md`
- `pw_run.mjs`는 판정 미수행 · expect 실패는 Fail 후보 · 최종 판정은 에이전트가 기대결과와 대조
- `--user-data-dir` 지정 시 headed 영속 컨텍스트로 실행 → 로그인 · OTP 세션을 다음 플랜까지 유지 · 수동 개입 후 같은 폴더로 다음 플랜 실행
- `--monitor sub`(기본): Windows에서 `Primary=False` 모니터 좌표 조회 → chromium 창을 서브모니터에 배치 · webkit · firefox는 창 위치 인자 미지원이라 주 모니터에 표시(결과 JSON `monitor`에 기록)
- `capture_window.ps1`: 다른 창에 가려진 상태면 가린 내용까지 캡처 → 캡처 전 대상 창을 맨 앞으로 이동
