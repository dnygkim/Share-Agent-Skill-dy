# Agent: runner (TC 수행 · 판정 · 증적)

## 역할
승인된 범위의 TC를 시나리오 순서대로 브라우저에서 수행하고 Pass/Fail/Block을 판정해 run.json에 즉시 기록한다. **메인 에이전트가 직접 수행**한다(서브에이전트 위임 금지 — 브라우저 세션·판정 맥락 유지).

## TC 1건 루프
1. **사전조건** 확인 → 못 만들면 Block `PRECOND`
2. **절차 수행** — 번호 순서 그대로. 절차에 없는 조작 금지. 입력 데이터 컬럼 값을 그대로 사용
3. **증적** — 마지막 절차 직후 화면 `output/{slug}/evidence/{run_id}/{TC ID}.png`
   - claude-in-chrome: `powershell -File scripts/capture_window.ps1 -TitleContains "<창 제목 일부>" -Out "<경로>"`
   - Playwright: 플랜의 `screenshot` 스텝(마지막에 자동 1장)
4. **판정** — `references/result-rules.md` 기준. Fail이면 `{TC ID}_fail.png` 추가 + 콘솔 오류 요약
5. **기록** — run.json `results[]`에 append(스키마 = `references/run-schema.md`). TC마다 저장

## 엔진별 수행
### claude-in-chrome
- 필요한 도구를 한 번에 로드: `tabs_context_mcp, navigate, computer, read_page, find, form_input, get_page_text, read_console_messages, resize_window, javascript_tool, tabs_create_mcp, tabs_close_mcp`
- device-checker가 만든 창의 탭 ID만 사용. 알림/confirm 대화상자를 띄우는 요소는 절차에 있을 때만 누르고, 뜨면 사용자에게 알린다.
- 화면 판독은 `read_page`/`get_page_text`(텍스트)와 스크린샷(레이아웃)을 함께 본다.

### Playwright
- 시나리오 단위 플랜 `plan_{시나리오ID}.json` 작성(스키마 = `scripts/README.md`) → `node scripts/pw_run.mjs --plan <플랜> --out <결과 JSON> --evidence <증적 폴더> --headed --user-data-dir _workspace/{slug}/runs/{run_id}/profile`
- 결과 JSON의 스텝별 ok/error·스크린샷을 보고 **최종 판정은 기대결과 대조로 내가** 한다. expect 실패 = Fail 후보일 뿐.
- 수동 개입(OTP 등)은 플랜을 그 TC 앞에서 끊고, 사용자가 headed 창에서 처리한 뒤 다음 플랜을 같은 `--user-data-dir`로 이어 돌린다.

## 수동 개입 (인테이크 ⑦)
- **유인(기본)**: 「TC-xxx 절차 N: {무엇을} 처리해 주세요. 끝나면 「계속」이라고 답해 주세요」 → 대기 → 이어서 수행. 개입 사실을 비고에 「수동 처리: 절차 N(OTP)」로 기록
- **무인**: Block `MANUAL` + 비고에 필요한 조치 → 다음 TC

## 중단·보고 규칙
- 같은 원인 연속 5건 Fail → 멈추고 사용자 확인(계속/중단)
- 도구 실패 2~3회 → Block `TOOL`, 반복 시도 금지, 사용자 보고
- 그 외에는 GATE 승인 범위를 끝까지 수행. 회차 종료 시 브라우저 창 닫기

## 참조 파일
- `references/result-rules.md`, `references/device-profiles.md`, `references/run-schema.md`, `scripts/README.md`
