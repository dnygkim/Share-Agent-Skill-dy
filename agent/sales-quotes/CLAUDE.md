# IA·공수 HTML 산출물 생성 에이전트

이 폴더는 **이트라이브 IA·공수산정 HTML 리포트**(웅진 04/05·아너파라다이스 02 류)를 자동 생성하는 에이전트 하네스다. **이 폴더에서 Claude Code를 열면 이 파일이 자동 로딩**되어 아래 규칙대로 동작한다. (모든 경로는 이 폴더 기준 상대경로.)

## 이 에이전트가 하는 일
요건정의서·개발계획서·RFP·기존 사이트 등을 입력받아 → 분석·IA추출 → IA·공수 설계 → 하우스 스타일 단일 HTML → 정합성 검수까지 **한 번에 생성**한다.

## 사용법 (사용자)
1. 입력 자료(요건/계획서 `.md`·`.docx`, 기존 사이트 URL 등)를 `input/`에 두거나, 경로·내용을 대화로 제공한다.
2. "이 계획서로 산출물 만들어줘 / 공수 HTML 뽑아줘" 라고 요청한다.
3. 결과 HTML은 `output/`에 저장된다.

## ★ 민감자료 정책 (추적 금지 · 재활용 금지 · 외부 반출 금지)

이 하네스가 다루는 **고객 자료는 전부 민감자료**다. 아래 세 가지를 어떤 단계·어떤 에이전트도 어기지 않는다.

| 대상 | 성격 | 규칙 |
|------|------|------|
| `input/` | RFP·요건·기능목록·구성도 등 고객 원자료 | git 미추적(`.gitignore`). 대화·산출물 밖으로 내보내지 않음 |
| `output/` · `_workspace/` | 이번 프로젝트 산출물·중간물 | git 미추적. 프로젝트 슬러그 폴더 밖으로 복사·병합 금지 |
| `examples/*.html` | **과거 고객 완성본(샘플)** — 실제 공수·견적·단가 포함 | git 미추적(INDEX.md만 추적). **샘플로만 활용** — 아래 "재활용 금지" |
| `.corpus/` · `.env` | 선례 KB 클론 · 접근 토큰 | git 미추적. 토큰을 MD·코드·로그에 쓰지 않음 |

1. **추적 금지** — 위 경로는 저장소에 커밋하지 않는다. 부모 저장소 `.githooks/pre-commit`이 스테이징을 차단하며, 우회(`--no-verify`·`git add -f`) 금지.
2. **재활용 금지** — `examples/`와 corpus 선례는 **형식·구성·도식 구현·산정 방식**을 보는 샘플이다. 샘플의 **고객명·수치(M/M·단가·기간·인원)·범위(in/out)·IA 트리·문장·표 행을 다른 프로젝트 산출물에 옮기거나 적용하지 않는다.** 산정 밴드는 감각 보정에만 쓰고, 근거는 매번 이번 프로젝트의 RFP·입력·인테이크 답변에서 새로 세운다. 이전 프로젝트의 스타일 변형(CI 색·톤)도 다음 프로젝트에 이월하지 않는다.
3. **외부 반출 금지** — 고객 자료·산출물을 외부 저장소(공개/타 조직 GitHub 등)·아티팩트 공개 링크·외부 SaaS(드라이브·노션·슬랙 등)·외부 API로 보내지 않는다. corpus push는 `.env`의 사내 원격(`CORPUS_GIT_REMOTE`)에만 한다. 사용자가 명시적으로 지정한 대상만 예외.
4. **게이트** — qa는 `python scripts/check_leak.py <html> --allow {이번 고객명}`으로 샘플 고객 토큰 잔존 0건을 확인한다(FAIL이면 builder 재수정). 수치·문장 재사용 여부는 qa (s)·persona-review가 본다.

## 동작 규칙 (에이전트)
요건/산출물 요청을 받으면:

0. **★ 착수 절차 — 자료는 `input/`을 가장 먼저 본다 (전역 검색 금지)**: **"분석/산출물/공수/IA/HTML/프로젝트 …해줘"** 류 요청(예: "GS관련 프로젝트 분석해줘")이 오면, **워크스페이스 전역을 `Grep`으로 헌팅하지 말고** 먼저 **`input/` 폴더(+대화로 준 경로/URL)**를 확인한다.
   - input/에 자료가 있으면 → 그걸 정본으로 **바로 ORCHESTRATOR 파이프라인 착수**(시각 표시 후). 자료를 찾으러 상위 폴더·works 전역을 뒤지지 않는다.
   - input/이 비어 있고 경로도 안 줬으면 → **"input/에 자료를 넣어주세요(또는 경로/URL을 알려주세요)"**라고 되묻는다(임의 전역 검색 금지).
   - 이 폴더에서 도는 동안 **모든 산출물성 요청은 이 하네스로 라우팅**한다(단순 질문·코드 수정 등 비산출물 작업은 예외). "분석해줘"도 자료가 input/에 있으면 산출물 작업으로 본다.
1. **`ORCHESTRATOR.md`를 읽고 파이프라인으로 처리한다: (site-analyst ∥ analyst) → (architect ∥ solution-architect) → builder → qa.**
   - 에이전트: `agents/{analyst,site-analyst,architect,solution-architect,persona-review,builder,qa,feedback-curator}.md`. **모델 티어링**: analyst·architect·solution-architect·**persona-review·feedback-curator**=**opus**, **site-analyst·builder·qa=sonnet**. site-analyst는 사이트 URL 있을 때만, **feedback-curator는 사용자 수정 확정 시 on-demand**. 각 에이전트는 자기 .md "참조 파일"만 읽음.
   - **페르소나 검토 (비용 규율)**: ① **3c estimate(항상)** — architect 후 GATE 전, 공수·인사이트 다관점 **+ 콘텐츠 발전도(RFP 나열↔고도화)** 검토, 결과를 GATE에 제시. ② **5b final(조건부)** — qa 후, *3c P0/P1 콘텐츠 변경 / 폴백 수기렌더 / 대형·고위험* 때만(평시 skip). qa=규칙검증·얕음 1차탐지(r), persona-review=설득력·발전도·고객 수용성 *판단*. P0면 반려. **opus 절약**: 3b(solution-architect)는 infra/concept 스코프일 때만, 5b는 조건부 → **평시 opus 3회**.
   - **★ 렌더 기본 = 스크립트 결정적**: architect가 `02_spec.json` 출력 → builder가 `python scripts/build_report.py 02_spec.json -o 03_draft.html` 실행 + prose 슬롯만 작성. 구조·스타일·정합을 코드가 보장(반복 사고 차단). LLM 전체 렌더는 폴백.
   - **★ 중간 산출물은 프로젝트별 폴더** `_workspace/{slug}/` (공유 시 교차 덮어쓰기 사고).
   - 생성 규칙 정본: `references/report-spec.md` (입력계약·6표·정합 a-h·4변형).
2b. **★ 수정 피드백 → 오너용 제안 (feedback-curator, 자동수정 X)**: **에이전트 수정 권한은 오너 단독.** 산출물이 방향과 안 맞아 사용자가 대화로 고치고 "이대로 확정"하면(또는 "피드백 문서 작성해줘") `feedback-curator`를 on-demand 호출. **다건이면 이번 세션 수정들을 번호(1·2·3)로 열거→"어느 것?" 선택**받은 뒤(1건이면 생략) → **수정 제안 리포트**(무엇이 어긋났나·원하는 방향·일반화 규칙·성격[객관개선/취향]·어디를 어떻게·영향범위)를 오너에게 공유 + `corpus.py propose`로 `feedback/proposals.md`(검토 큐) 누적. **오너가 보고 "반영하자"고 하면 그때 `/harness`나 직접 편집으로 수정** — feedback-curator는 에이전트를 직접 안 고친다. 일회성은 기록 안 함.
2. **인테이크(분석 착수 전) — 한 번에 하나씩 순차 질문**: 작성 시작 요청이 오면 산출물 1줄 선언 후, 필요한 확인 항목을 **한꺼번에 나열하지 말고 하나씩** 묻고 답을 받아 진행한다(콜드 메뉴 X·추론 가능한 건 안 물음). 순서 = **고정 필수 5(RFP 무관·항상) + 조건부 + 동적**: [고정] ① 디자인 수준 ② 개발 방법(기존소스/부분재개발/전면신규 — 공수 핵심 분기) ③ 인프라 구축 실제작업 포함 여부(공수 포함 vs 구성도 제시만) ④ 상주/비상주 ⑤ 고객 요청 프로젝트 기간(+일정·예산 압박) → [조건부] (AS-IS 인프라 있으면) TO-BE 제안 포함 → [동적] ⑥ analyst가 이 RFP에서 도출한 미상·모호 항목 중 공수/범위 영향 큰 것 2-4개(적극 포함, 고정캡 아님). **⑥은 RFP가 다루는 것의 빈칸만 — RFP에 없는 신규 기능(챗봇·AI·추천)을 "필요하세요?"로 타진 금지.** 한꺼번에 답하면 수용하고 남은 것만 이어 묻는다. 항목별 "알아서"면 표준 가정. 받은 신호 → architect **공수 가중**(디자인 high→디자인↑, 비상주→퍼블·개발 -최대30%, 상주→PM 등 장기 0.5 금지).
   - **Dan Jr. 등급 조회(승인 게이트 공통, 2026-10-22)**: 인테이크 질문·GATE·「~할까요?」를 묻기 직전에 `~/.claude/persona/persona.md`(전역 규칙이 없는 환경은 `../../persona/persona.md`)에서 같은 상황을 찾는다. 등급 **A**면 묻지 않고 기본값으로 진행, **B**면 진행 후 완료 보고에 한 줄, **C** 또는 해당 항목 없음이면 지금처럼 묻는다. 건너뛴 게이트는 완료 보고에 「Dan Jr. 적용: D-09(A)」처럼 ID로 적는다. 고정 필수 5 인테이크와 공수 GATE처럼 persona.md에 없는 결정은 그대로 사용자 확인.
3. 기본 산출물 = **공수산정 리포트(타입 B)**. **「공수산정안 제출」 요청이면 타입 C(제출본) — 분량 · 작성 스타일은 GRS 원보드 v1.0(2026-10-16) 기준, 정본 `references/report-spec.md` §1-1.** 변형(단독/통합/옵션비교/동시진행)은 `references/report-spec.md` §1.
3b. **★ 시각 표시(시작·완료)**: 분석/작성에 **착수할 때**와 **최종 HTML 완성 때** 현재 시각을 한 줄 표시한다. 시:분은 환경에 없으니 **조회**해서 쓴다(`date +"%H:%M"` 또는 PowerShell `Get-Date -Format "HH:mm"`). 형식: 착수=`현재 HH시 MM분입니다. 작업 시작합니다.` / 완료=`현재 HH시 MM분입니다. 작업 완료했습니다.`

3c. **★ 내부망 URL 함께 제공 (HTML 산출 완료 시)**: HTML 산출물을 저장·검수한 뒤 완료 보고에 사내망 링크를 같이 준다(2026-10-22 사용자 지시).
   ① `~/Documents/Local-Projects/internal-share/<프로젝트 약칭>/`에 output 원본을 가리키는 심볼릭 링크 2개(원래 파일명 + `index.html`)를 만든다 — 파일 복사 금지.
   ② 비어 있는 포트를 고른다(8001부터 차례로 `lsof -nP -iTCP:<포트> -sTCP:LISTEN` 확인). 서버는 단독 명령으로 띄운다: `nohup python3 -m http.server <포트> --bind 0.0.0.0 --directory <폴더> > <폴더>.log 2>&1 &`
   ③ `127.0.0.1`과 사내 IP(`ipconfig getifaddr en0`)로 200 응답을 확인한다.
   ④ 보고에는 **짧은 주소 `http://<IP>:<포트>/`만** 적는다 — 파일명 인코딩 전체 주소는 쓰지 않는다(2026-10-22 지시). 맥 IP가 DHCP로 바뀔 수 있다는 점을 한 줄 덧붙인다.
   - 같은 프로젝트로 이미 띄운 서버가 있으면 새 서버를 띄우지 않고 심볼릭 링크만 새 파일로 바꾼다.
   - 실행이 막히면 재시도하지 말고 같은 명령을 `!` 한 줄로 드린다. 상세 절차·사용 중 포트 = 메모리 `internal-url-share`.
4. **CSS는 직접 작성 금지** → `<style>`에 마커만 두고 `python scripts/inline_css.py <draft.html>`로 주입. 도식(개념도·AWS 인프라)은 기본 포함. 가이드 `references/architecture-infra-diagram.md`.
5. **정합 규칙 (a)-(h)** 준수 → `python scripts/check_consistency.py <html>`로 자동검증. 기준 `references/consistency-checklist.md`. **샘플 유출 검사** → `python scripts/check_leak.py <html> --allow {이번 고객명}` 0건(민감자료 정책 4).
6. 산정 판단은 `references/effort-estimation-methodology.md`(측정단위·재스킨·재사용 비대칭·경계·함정). **★ 사용자가 투입공수표(이미지/표)를 주면 그게 최우선 정본** → 나머지는 역산.
7. **`examples/`의 과거 완성본은 샘플로만 참고**한다(`examples/INDEX.md` 인덱스, 로컬 전용·미추적). 스타일·도식·구성·산정 방식을 보되, **고객명·수치·범위·IA·문장을 다른 문서에 재사용·적용하지 않는다**(민감자료 정책 2). 도식(AWS 인프라/개념도)은 `아너파라다이스` 예시가 정본 레퍼런스.
8. **playbook 적용**: 분석 시 `references/playbook-domain-questions.md`로 요건 누락 탐지, 산정 후 `references/playbook-effort-validation.md` 5축 자기검증(QA·이관·배포 누락 주의). 산정 노트에 `confidence`+데이터갭 명시.
9. **corpus(집단기억, KB) 활용** — `references/corpus-knowledge-base.md`. corpus 데이터는 별도 `corpus` 브랜치(corpus.py가 `.corpus/`에 자동 클론):
   - **시작**: 프로젝트 **id=slug 1회 확정**(`{고객}-{주제}`, = `_workspace/{slug}`) → `scripts/corpus.py search`로 유사 선례 검색 → 산정·IA·스타일 보정. `⚠️under_estimated` 경고 시 버퍼 검토.
   - **스냅샷(비용 절감)**: 기본 **GATE 1회 + 최종 save만**(`scripts/corpus.py snapshot --stage gate`). 최종 save가 `_workspace` 전체를 미러하므로 KB 최종상태 동일 → 단계별 스냅샷은 장시간·고위험 실행 시 옵션. 검색 인덱스는 불변.
   - **끝(qa PASS 후)**: `scripts/corpus.py save --html .. --meta {ws}/05_meta.json --ws ..`로 환원. **05_meta.json은 리치 메타**(식별·공수 + 섹션 콘텐츠 overview·direction·ia_summary·approach·scope·questions·infra·decisions) → save가 **섹션 원자별로 1커밋씩** + `kb(report)` + 태그 `kb/{id}`. qa PASS가 push 게이트. (커밋 포인트 정본 = ORCHESTRATOR "커밋/푸시 포인트".)
   - **피드백**: 실제 공수를 알게 되면 `scripts/corpus.py feedback --id .. --actual N --lesson ..` → 산정이 누적 자기보정.
   - **HTML 버전 관리(다중 사용자)**: 최종 HTML 생성·수정 시 `corpus.py put-html --id .. --html .. --note ..`로 자동 버전 커밋·push(태그 `kb/{id}` 이동). 사용자가 "최신 HTML 보자"면 로컬 말고 `corpus.py get --id ..`로 git 최신본을 받아 보여준다(과거 버전=`--rev 태그/해시`). 버전 이력 = `git log -- deliverables/{id}/report.html`.
   - **★ 산정 독립성(오케스트레이터 규율)**: 에이전트에 **현재 세션·메모리의 다른 프로젝트 수치나 수작업·미커밋 산출물 수치를 주입·비교시키지 마라.** 산정은 RFP+방법론+Q&A로 독립 추론한다. **단 corpus(커밋 KB)는 금지 대상이 아니라 "허용된 유일한 참조"다 — 적극 검색·인용하고 흔적을 남겨라.** 독립성 금지의 대상은 세션·메모리·미커밋 수치이지 corpus가 아니다. corpus 선례는 밴드 보정·교훈·과소산정 경고로 쓰되 맹목 복붙·앵커링은 금지(선례 대비 본 건의 차이를 근거로). 에이전트는 추론값+근거 코멘트(+참조 선례 id)를 주고 사용자 확인을 받는다.

## 입출력 규약 (★ 파일 네이밍 표준 정본 = `ORCHESTRATOR.md` "파일 네이밍 표준")
- `input/` — 사용자 입력 자료 (배포 시 비움)
- `_workspace/{slug}/` — 파이프라인 중간물. **항상 `{slug}/` 하위**(bare 금지 — 프로젝트 간 덮어쓰기 방지). 단계 파일: `01a_site-ia.md/.json` · `01_analysis.md` · `02_spec.json(+.md)` · `02b_solution.json(+.md)` · `03_draft.html` · `04_qa.md` · `05_meta.json`. (배포 시 비움)
- `output/` — 최종 HTML `{NN}_{주제}_v{X.Y}.html`. in-place 수정 기본, 매우 큰 수정만 버전업.
- corpus(KB) — **섹션 원자 구조**: `cases/{유형}.md`(케이스 종합: 범위·확인·공수) + `estimates/`·`scope/`·`questions/`·`ia/`·`approach/`·`direction/`·`overview/`·`infra/`·`dev-notes/decisions/`(프로젝트별 원자) + `patterns/`(횡단) + `deliverables/{id}/report.html`+`workspace/`(원본·미러) + `index.jsonl`. **커밋은 원자 단위**(검색 정밀), 메시지 `kb({type}): {id} | …`, 태그 `kb/{id}`.

## 표기 규칙
한국어. 범위 표기 물결표(~) 금지 → 하이픈(-) (단 HTML 본문 `~5스타일` 류는 허용). 상세 `references/report-spec.md` §8.

> 전체 개요·디렉토리·변경이력은 `README.md`, 실행 상세는 `ORCHESTRATOR.md` 참조.
