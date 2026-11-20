# Agent: device-checker (실행 환경 확인)

## 역할
이번 회차의 디바이스·엔진·브라우저 환경을 **실측**해 run.json 머리말을 만든다. 추정값을 쓰지 않는다.

## 실행
1. **모니터**: PowerShell `Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Screen]::AllScreens | % { $_.DeviceName, $_.Primary, $_.Bounds }` → `Primary=False` Bounds를 서브모니터 좌표로. 없으면 `profile.monitor = "primary(서브 없음)"`.
2. **엔진별 준비**
   - claude-in-chrome: `tabs_context_mcp` → `tabs_create_mcp`(새 창) → 창 핸들을 잡아 `SetWindowPos`로 서브모니터 Bounds로 이동 → 이동 결과를 좌표로 확인. 브라우저 버전은 `javascript_tool`로 `navigator.userAgent` 조회. MW/APP-WV는 `resize_window`로 프로필 뷰포트 적용(UA 변경 불가 — `profile.note`에 「UA 데스크톱, 뷰포트만 모바일」기록).
   - Playwright: `node scripts/pw_run.mjs --check` → 설치된 브라우저·버전 출력. 미설치면 `scripts/README.md` 절차를 안내하고 대기.
3. `node scripts/init_run.mjs --slug {slug} --device {PC|MW|APP-WV} --engine {claude-in-chrome|playwright} --profile "{프로필명}" --viewport {W}x{H} --browser "{브라우저 버전}" --os "{OS}" --base-url {URL} --task "{업무명}" --tester "{작성자}"` → `_workspace/{slug}/runs/{run_id}/run.json` 생성(run_id 자동 채번).

## 경로 확인 (단계 시작 시)
- 산출 경로 기본 `_workspace/{slug}/runs/{run_id}/run.json`. 지정 경로가 있으면 그것을 정본.

## 입력 / 출력
- 입력: 인테이크 ③ 디바이스 · ④ 엔진 · ⑥ 접속 URL
- 출력: run.json 머리말(profile·engine·browser·monitor 실측)

## 참조 파일
- `references/device-profiles.md`, `references/run-schema.md`
