# 디바이스 프로필 · 엔진 선택 기준

## 1. 디바이스 코드 (인테이크 ③ · run.json `device`)

| 코드 | 뜻 | 수행 방식 | 발견 환경 표기 예 |
|---|---|---|---|
| `PC` | 데스크톱 웹 | 브라우저 창 그대로 | `PC · Chrome 130 · Windows 11 · 1920×1080` |
| `MW` | 모바일 웹 | 모바일 프로필(뷰포트·UA·터치) 에뮬레이션 | `MW · iPhone 14(에뮬) · Safari 17(WebKit) · 390×844` |
| `APP-WV` | 앱의 웹뷰·하이브리드 화면 | MW 프로필로 **대체 수행**. 네이티브 기능 TC는 Block(`NATIVE`) | `APP-WV(모바일 웹 대체) · Pixel 7(에뮬) · Chrome 130` |

- 회차 = 디바이스 1개. 여러 디바이스는 회차를 나눈다(`…-PC-01`, `…-MW-01`).
- 네이티브 판정 키워드(소분류 · 절차 · 입력 데이터에 등장하면 `NATIVE`): 푸시 알림 · 카메라 · 갤러리 · 생체인증(FaceID·지문) · 앱 결제(인앱) · 딥링크 · 앱 권한 · 백그라운드 · 위젯 · 앱 업데이트. 애매하면 GATE 표에 올려 사용자 판단.

## 2. 프로필 표

| 프로필명 | 디바이스 | 뷰포트 | DPR | Playwright 디바이스명 | claude-in-chrome |
|---|---|---|---|---|---|
| `PC-FHD` (기본) | PC | 1920×1080 | 1 | (없음 · viewport 지정) | 창 크기 1920×1080 |
| `PC-HD` | PC | 1366×768 | 1 | (viewport 지정) | 창 크기 1366×768 |
| `iPhone 14` (MW 기본) | MW | 390×844 | 3 | `iPhone 14` (WebKit 권장) | `resize_window` 390×844 · UA 미변경 |
| `iPhone SE` | MW | 375×667 | 2 | `iPhone SE` | 375×667 |
| `Pixel 7` | MW | 412×915 | 2.625 | `Pixel 7` (Chromium) | 412×915 |
| `Galaxy S9+` | MW | 320×658 | 4.5 | `Galaxy S9+` | 320×658 |
| `iPad (gen 7)` | MW(태블릿) | 810×1080 | 2 | `iPad (gen 7)` | 810×1080 |

- 사용자가 특정 기기·해상도를 지정하면 그 값이 정본. 표에 없으면 viewport·DPR을 직접 적는다.
- claude-in-chrome은 **UA·터치 이벤트를 바꾸지 못한다** — 반응형 레이아웃 확인까지는 되지만 UA 분기(모바일 전용 리다이렉트 등)가 있는 사이트는 Playwright를 쓴다. 한계는 run.json `profile.note`에 남긴다.

## 3. 엔진 선택 기준 (인테이크 ④)

| 상황 | 엔진 |
|---|---|
| 지금 Chrome에 로그인된 세션으로 바로 확인 · 1회성 수행 · 사내망/SSO 사이트 | **claude-in-chrome** |
| 같은 TC를 반복(회귀) · Safari(WebKit)/Firefox 확인 · 모바일 UA·터치 정밀 에뮬레이션 · 무인 장시간 실행 | **Playwright** |
| 수동 개입이 많은 흐름(OTP · 결제) | claude-in-chrome(사용자가 같은 창에서 바로 처리). Playwright면 `--headed --user-data-dir`로 세션 유지 |

- 두 엔진을 한 회차에 섞지 않는다. 섞어야 하면 회차를 나눈다.
- Playwright 브라우저 기본값: PC = chromium, MW iPhone = webkit, MW Android = chromium. 사용자가 지정하면 그 값.

## 4. 창 배치 (전역 규칙 2026-10-28)
- 새 창을 **서브모니터**(`Primary=False`)에 띄운다. Playwright는 `--monitor sub` 옵션으로 pw_run이 `--window-position`을 자동 적용(chromium만 · webkit/firefox는 미지원이라 주 모니터에 뜸 → 보고에 한 줄), claude-in-chrome은 창 생성 후 `SetWindowPos`.
- 서브모니터 없음 → 주 모니터 새 창 + 완료 보고 한 줄.
