# 데이터 스키마 — tc.json · run.json · Playwright 플랜

## 1. tc.json (`scripts/load_tc.mjs` 출력 — 엑셀 파생물)
```json
{
  "source": "input/acme-shop/테스트케이스_주문_v0.1_20261104.xlsx",
  "loaded_at": "2026-11-04T14:00:00+09:00",
  "overview": [["프로젝트명", "ACME 쇼핑몰"], ["테스트 범위", "…"]],
  "scenarios": [
    {"id": "TS-ORD-001", "category": "주문", "name": "비회원 주문", "desc": "…", "tc_count": 6, "source": "기획서 p.12"}
  ],
  "testcases": [
    {"row": 2, "tc_id": "TC-ORD-001", "cat1": "주문", "cat2": "장바구니", "cat3": "수량 변경",
     "scenario_id": "TS-ORD-001", "priority": "상", "technique": "경계값분석",
     "precond": "장바구니에 상품 1개", "steps": "1. …\n2. …", "data": "수량 0", "expected": "…", "source": "기획서 p.12",
     "note": "", "flags": ["EXPECT_TBD"]}
  ],
  "warnings": ["TC-ORD-009: 출처 비어 있음", "TC-ORD-012: 시나리오 TS-ORD-004 없음"]
}
```
- `flags`: `EXPECT_TBD`(기대결과에 `[확인 필요]`) · `NATIVE`(네이티브 키워드) · `NO_SOURCE` · `DUP_ID`.
- 헤더는 이름으로 찾는다(qa-master `TC_HEADER` 19개 · 제출용은 「적용 기법」 없음).

## 2. run.json (`scripts/init_run.mjs` 생성 → `scripts/add_result.mjs`로 results append — 회차 정본)
```json
{
  "run_id": "20261104-PC-01",
  "slug": "acme-shop",
  "task_name": "ACME쇼핑몰",
  "device": "PC",
  "engine": "claude-in-chrome",
  "profile": {"name": "PC-FHD", "viewport": "1920x1080", "dpr": 1, "browser": "Chrome 130.0.6723.92", "os": "Windows 11", "monitor": "sub(-1920,0 1920x1080)", "note": ""},
  "base_url": "https://stg.acme.example",
  "account_id": "qa_user01",
  "tester": "김단영",
  "manual_mode": "attended",
  "started": "2026-11-04T14:05:00+09:00",
  "finished": null,
  "source_xlsx": "input/acme-shop/테스트케이스_주문_v0.1_20261104.xlsx",
  "tc_json": "_workspace/acme-shop/tc.json",
  "scope": {"description": "전체", "tc_ids": ["TC-ORD-001", "…"], "excluded": [{"tc_id": "TC-APP-003", "reason": "NATIVE"}]},
  "results": [
    {"tc_id": "TC-ORD-001", "scenario_id": "TS-ORD-001", "result": "Pass",
     "actual": "", "repro": "", "env": "PC · Chrome 130 · Windows 11 · 1920×1080 · qa_user01",
     "hold_code": null, "note": "", "manual": null,
     "evidence": ["evidence/20261104-PC-01/TC-ORD-001.png"],
     "console_errors": [], "started": "…", "finished": "…"},
    {"tc_id": "TC-ORD-002", "scenario_id": "TS-ORD-001", "result": "Fail",
     "actual": "수량 0 입력 후 「변경」 클릭 시 안내 없이 수량 1로 되돌아감. 기대: \"1개 이상 입력\" 안내", "repro": "",
     "env": "…", "hold_code": null, "note": "", "manual": null,
     "evidence": ["evidence/20261104-PC-01/TC-ORD-002.png", "evidence/20261104-PC-01/TC-ORD-002_fail.png"],
     "console_errors": ["TypeError: qty is null (cart.js:120)"], "started": "…", "finished": "…"},
    {"tc_id": "TC-ORD-003", "scenario_id": "TS-ORD-001", "result": "Block",
     "actual": "", "repro": "", "env": "…", "hold_code": "PRECOND", "note": "TC-ORD-002 Fail로 수량 0 상태 재현 불가",
     "manual": null, "evidence": [], "console_errors": [], "started": "…", "finished": "…"},
    {"tc_id": "TC-PAY-001", "scenario_id": "TS-PAY-001", "result": "Pass",
     "actual": "", "repro": "", "env": "…", "hold_code": null, "note": "",
     "manual": {"step": 4, "what": "카드사 OTP 입력", "by": "사용자"},
     "evidence": ["evidence/20261104-PC-01/TC-PAY-001.png"], "console_errors": [], "started": "…", "finished": "…"}
  ]
}
```
- `manual_mode`: `attended`(유인) / `unattended`(무인).
- `hold_code`: `references/result-rules.md` §3. Block일 때만.
- `evidence` 경로는 `output/{slug}/` 기준 상대경로.
- **비밀번호·OTP 값은 어떤 필드에도 쓰지 않는다.**
- results는 TC마다 즉시 append(중단 대비). 같은 tc_id가 두 번 들어오면 마지막 것이 유효(재수행).

## 3. Playwright 플랜 (`scripts/pw_run.mjs --plan`)
```json
{
  "browser": "chromium",
  "device": "iPhone 14",
  "viewport": {"width": 1920, "height": 1080},
  "base_url": "https://stg.acme.example",
  "tcs": [
    {"tc_id": "TC-ORD-001",
     "steps": [
       {"action": "goto", "url": "/cart"},
       {"action": "fill", "selector": "input[name=qty]", "value": "0"},
       {"action": "click", "text": "변경"},
       {"action": "expect_text", "value": "1개 이상 입력"},
       {"action": "screenshot", "name": "TC-ORD-001"}
     ]}
  ]
}
```
- `browser`: chromium | webkit | firefox. `device`가 있으면 Playwright 디바이스 프로필 적용(viewport 무시).
- 스텝 액션: `goto`(url 상대/절대) · `click`(selector | text | role+name) · `fill` · `press`(key) · `select`(selector,value) · `check`/`uncheck` · `hover` · `wait`(ms | selector) · `expect_text`(value, 선택 selector) · `expect_url`(contains) · `expect_visible`/`expect_hidden`(selector | text) · `expect_value`(selector,value) · `screenshot`(name) · `console_snapshot`.
- 결과 JSON: `{tc_id, ok, steps:[{i, action, ok, error, ms}], screenshots:[], console_errors:[]}` 배열. 마지막 스텝에 screenshot이 없으면 `{tc_id}.png`를 자동 저장. expect 실패 스텝 뒤는 수행하지 않고 `{tc_id}_fail.png` 저장.
