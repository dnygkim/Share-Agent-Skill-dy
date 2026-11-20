# Agent: tc-loader (TC 로드 · 실행 계획)

## 역할
qa-master 엑셀을 tc.json으로 파싱하고, 범위를 적용한 **실행 계획 표**를 만들어 GATE에 올린다.

## 실행
1. `node scripts/load_tc.mjs "<엑셀 경로>" --out _workspace/{slug}/tc.json`
   - 시트 「테스트 시나리오」「테스트케이스」를 헤더명으로 찾는다(순서·제출용 변형 허용). 「개요」는 있으면 함께 담는다.
   - 경고 출력: 출처 빈 TC · 시나리오 ID가 시나리오 시트에 없는 TC · 기대결과에 `[확인 필요]` 포함 TC · 중복 TC ID. 경고는 GATE 표에 그대로 보여 준다.
2. 범위 적용(인테이크 ⑤): 시나리오 ID · 대분류 · 우선순위 · TC ID 범위. 기본 = 전체.
3. 자동 제외 규칙:
   - APP-WV 회차의 네이티브 기능 TC(소분류·절차에 푸시 · 카메라 · 생체인증 · 앱 결제 · 딥링크 등) → 수행 없이 Block(`NATIVE`) 예정으로 표기
   - 기대결과 `[확인 필요]` → 수행은 하되 Block(`EXPECT`) 예정으로 표기
4. **실행 계획 표** 작성 → GATE 제시:

| 시나리오 ID | 시나리오명 | 대상 TC | 상/중/하 | 수동 개입 예상 | 제외·예정 Block |
|---|---|---|---|---|---|

   머리말: 회차 ID · 디바이스/프로필 · 엔진 · 접속 URL · 개입 모드 · 예상 소요(PC 1.5분/TC · MW 2분/TC).
5. 승인 후 run.json `scope`에 확정 범위(tc_ids 목록)를 기록한다.

## qa-master 추출 연계 (TC 엑셀이 없을 때)
- `Skill` 도구로 `qa-master` 호출(모드 1). 입력 문서·범위를 넘기고 생성된 엑셀을 사용자가 확인한 뒤 `input/{slug}/`에 두고 1번부터 진행.
- 이 PC(Python 미설치)에서는 모드 1이 돌지 않는다 — 사용자에게 알리고 엑셀 제공을 요청한다.

## 경로 확인 (단계 시작 시)
- 입력 기본 `input/{slug}/*.xlsx` · 출력 기본 `_workspace/{slug}/tc.json`.

## 참조 파일
- `references/run-schema.md`(tc.json 스키마), `../../skills/qa-master/SKILL.md`(엑셀 컬럼 정의 1-5절)
