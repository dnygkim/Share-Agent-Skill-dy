# HTML 산출물 자동화 하네스

이트라이브의 **IA·공수산정 HTML 리포트**(웅진 04/05, FunETF 01, 아너파라다이스 02 류)를 한 번에 생성하기 위한 에이전트 하네스.

## 무엇을 자동화하나
기존 사이트/RFP/레퍼런스에서 출발해 → 분석·IA추출 → IA·공수 설계 → 하우스 스타일 단일 파일 HTML 생성 → 정합성 검수까지. **한 방에 생성하고 이후 수정**하는 방식. 렌더는 `build_report.py`가 JSON 스펙을 받아 **결정적으로** 수행해 구조·스타일·정합을 코드가 보장한다.

## 파이프라인 (6 에이전트, 앞단·중간단 병렬 + 생성-검증)
```
┬ site-analyst(사이트시)┐       ┬ architect ───────┐
└ analyst(요건+병합)    ┘→ 01 →└ solution-architect┘→ builder → qa ─(FAIL)→ 보정 → 최종 HTML
```
| 에이전트 | 모델 | 역할 |
|---------|------|------|
| **site-analyst** | sonnet | (사이트 URL 있을 때만) ia_extract.py로 IA 3뎁스+·page/view 카운트·관리자/API 유추 — analyst와 병렬 |
| **analyst** | opus | 요건·현황·제약·인사이트 + 인테이크 정성신호 + 요건↔IA 병합 (사이트 없으면 IA도 직접) |
| **architect** | opus | 월별 투입표(SSOT)·매트릭스·WBS·간트·공수산정 + 정성신호 **공수 가중** + 5축 검증 |
| **solution-architect** | opus | 기술 아키텍처·AWS 인프라·개념도 설계 (공수 무관 → architect와 **병렬**) |
| **persona-review** | opus | 멀티 페르소나(PM·아키텍트·개발·디자인/퍼블·고객) 다관점 검토 — ① GATE 전(공수·인사이트) ② 최종 전(콘텐츠). qa가 못 보는 설득력·현실성·고객 수용성 |
| **builder** | sonnet | `02_spec.json`을 `build_report.py`로 결정적 렌더(6표+인프라/개념도+CSS+팔레트). 자유서술 prose만 작성. LLM 수기 렌더는 폴백 |
| **qa** | sonnet | 정합(a-h)·발명클래스·공수5축 검증(실검사는 스크립트) |

> 모델 티어링: 추론=opus / 기계적=sonnet (비용·속도). 인프라 분기 병렬로 지연 단축.

## 핵심 산출 규칙 (운영 누적 — 위반 시 qa FAIL/build_report WARN)
- **자료 > 유추**: 고객 제공 자료(기능목록·구성도·xls 시트·이미지)가 있는 영역은 **자료 기반(실측)**으로 반영, 없을 때만 유추. analyst가 착수 시 "입력 자료 출처 인벤토리"로 영역×출처 매핑.
- **인테이크 = 한 번에 하나씩 순차 질문**: 작성 시작 시 디자인수준 → 일정 → 상주/비상주 → 인프라 포함 → (AS-IS 있으면)TO-BE → 누락 순. 추론 가능한 건 안 물음.
- **IA = 페이지(기능) 단위, 1노드=1행**: 콘텐츠 개수로 노드 부풀리지 않음("스타일 N"은 한 페이지 내 표시 변형일 때만). **admin 있으면 Front IA / Admin IA 2섹션 분리**, admin 없는 사이트(정적·소개형)는 Front만.
- **인프라 AS-IS = 고객 제공 구성도 원본 그대로(`figure`)** / **TO-BE = AS-IS delta**(유지/변경/신규/제거 + 근거, 현행 필수요소 임의 제거 금지). RFP에 인프라 요구 없을 때만 일반 권장 구성.
- **인력 정책**: 톱니(중간월 0.5)·장기반투입(0.5 2개월+) 금지(정당 파트타임은 `parttime:true`). QA=기획 겸임(전담 직군 X, 기획 1명 막달까지). 테스트 구간 디자인/퍼블 2명+ → 1명 감쇠. 비상주→퍼블·개발 -최대30%/상주→감면없음.
- **RFP 커버리지 + 확인 질문**: 요건 전수 항목화 → 커버리지 대조표 + 산출물 맨 끝 "확인 필요 질문"(추정·데이터갭).
- **출력 위치**: 산출물은 `_workspace/{slug}/`·`output/`만(temp·홈 금지). build_report의 모든 `[WARN]`을 0으로 만든 뒤 qa PASS.
- **렌더 = 결정적 스크립트**: `build_report.py`가 JSON→HTML(전 섹션 kind). 클래스 발명·CSS 직접작성·prose 자유HTML 최소화. (상세·변경 경위는 아래 변경 이력)

## 디렉토리
```
084.HTML산출물자동화-하네스/
├── CLAUDE.md                       ← ★ 폴더 열면 자동 로딩되는 현관문(동작 규칙)
├── README.md                       ← 이 파일(개요·설치)
├── ORCHESTRATOR.md                 ← 실행 워크플로우(메인이 읽고 구동)
├── agents/  analyst·site-analyst·architect·solution-architect·builder·qa .md
├── references/
│   ├── report-spec.md              ← ★ 생성 규칙 정본(입력계약·6표·정합 a-h·4변형)
│   ├── house-style-guide.md        ← 디자인 토큰·클래스 카탈로그
│   ├── section-catalog.md          ← 표준 섹션 순서
│   ├── consistency-checklist.md    ← 수치 정합성 (a)-(h) 교차검증(qa 핵심)
│   ├── effort-estimation-methodology.md ← 공수 산정 방법론·함정(architect 두뇌)
│   ├── site-ia-extraction.md       ← 기존 사이트 IA 3뎁스+ 추출·유추 (+정밀도 규칙)
│   ├── ia-extraction-upgrade.md    ← IA 추출 오류7·해결규칙·JSON스키마·GS칼텍스 검증사례
│   ├── architecture-infra-diagram.md ← AWS 공식 아이콘 도식·개념도
│   ├── corpus-knowledge-base.md     ← corpus(KB) 검색-증강·환원·피드백 루프
│   ├── playbook-domain-questions.md ← 요건 누락 탐지 체크리스트(analyst)
│   └── playbook-effort-validation.md ← 공수 5축 자기검증(architect/qa)
├── template/
│   ├── base_template.html          ← 섹션 스켈레톤(CSS는 마커 주입)
│   ├── house-style.css             ← 하우스 스타일 전체 CSS(1,410줄 · warm paper × near-black)
│   └── diagrams.css                ← 개념도(eco) + AWS 인프라(aws-*) CSS
├── scripts/
│   ├── build_report.py             ← ★ 렌더 엔진. JSON 스펙→HTML 결정적 렌더(IA·월별·영역·매트릭스·WBS·간트·요약·인프라·개념도+CSS주입+팔레트)
│   ├── inline_css.py               ← CSS 바이트 그대로 <style> 주입(폴백 렌더용·드리프트 차단)
│   ├── check_consistency.py        ← 표 파싱·합산 (a)-(h) 자동 검증
│   ├── corpus.py                   ← corpus 동기화·검색·저장·중간물 스냅샷(pull/search/snapshot/save/feedback)
│   ├── check_classes.py            ← 발명 클래스(정의0·사용N) 검출 — 렌더 깨짐 가드
│   ├── ia_extract.py               ← 사이트 IA 정밀 추출(메가패널·탭/그룹·이중카운트·footer·로그인)
│   └── extract_assets.py           ← RFP(.docx/.pptx) 임베드 이미지 추출(AS-IS 인프라 구성도 등 → Read 판독)
├── .env.example                    ← corpus 토큰·브랜치 설정 템플릿(.env는 gitignored)
│   (corpus 데이터는 별도 `corpus` 브랜치 — corpus.py가 .corpus/에 클론, etribe 코드와 분리)
├── examples/                       ← 과거 완성본 샘플(로컬 전용·git 미추적, INDEX.md만 추적) — 형식·구성 참고, 다른 문서 재사용 금지
├── 사용자가이드.html               ← VSCode 환경 모사 사용 가이드(팀 배포용)
├── input/                          ← 사용자 입력 자료 둘 곳(배포 시 비움)
├── output/                         ← 최종 HTML 산출물 `{NN}_{주제}_v{X.Y}.html`
└── _workspace/{slug}/              ← 런타임 중간물(프로젝트별 폴더, 배포 시 비움)
                                       01a_site-ia · 01_analysis · 02_spec · 02b_solution · 03_draft · 04_qa · 05_meta
```

## 설치 & 사용 (배포 모델)
이 폴더 전체를 git으로 배포한다. 사용자는:
1. **clone/다운로드** → 받은 폴더를 연다.
2. **그 폴더에서 Claude Code를 실행** → 루트 `CLAUDE.md`가 자동 로딩되어 에이전트가 활성화된다(별도 명시 호출·설치 불필요).
3. 입력 자료를 `input/`에 두고(또는 경로·내용 제공) "이 계획서로 산출물 만들어줘"라고 요청 → 결과는 `output/`에.

> 폴더 안에서 열기 때문에 모든 경로가 상대경로로 동작한다(이식성 확보, 절대경로 없음).

- 부분 수정: "퍼블 마지막달 0.5→1로" → architect SSOT 갱신 → builder 위치별 Edit → qa 교차검증

## 배포 전 체크리스트
- [ ] `_workspace/`·`input/`·`output/` 비우기(테스트 산출물 제거)
- [ ] 절대경로 0건 확인(`grep -rn "d:/" .`)
- [ ] `.gitignore`에 `_workspace/`·`output/` 추가 권장(런타임 산출물 미추적)
- [x] playwright 런타임 산출(`.playwright-mcp/`)·루트 캡처 이미지(`/*.png|jpg|jpeg`) `.gitignore` 등록 완료 + 캡처는 `_workspace/{slug}/` 저장 지침(site-analyst §9)

## 설계 결정 메모
- 위치: `.claude/` 대신 `works/`(사용자 선택). 폴더 하나로 자급식 묶음. 자동 트리거가 필요해지면 `.claude/skills/`로 승격 가능.
- 모델 티어링: 추론(analyst·architect·solution-architect)=opus / 기계적(site-analyst·builder·qa)=sonnet. 실행 모드: 서브에이전트(general-purpose에 역할 정의 주입).
- 인프라는 기본 **AWS 형식**, AWS 공식 아이콘(외부 PNG) 사용 — 사용자 선호.

## 변경 이력
| 날짜 | 변경 | 사유 |
|------|------|------|
| 2026-10-22 | **Dan Jr. 등급 조회**(CLAUDE.md 동작 규칙 2): 인테이크·GATE 직전 `persona.md` 확인 — A 진행·B 보고·C 질문, 건너뛴 게이트는 완료 보고에 ID 표기 | 반복 결정을 Dan Jr.(사용자 골든셋)에 위임해 승인 게이트 축소(오너 지시) |
| 2026-09-03 | **★ 민감자료 정책 명문화**(CLAUDE.md): 추적 금지·재활용 금지·외부 반출 금지 3원칙 + `examples/*.html` git 미추적(.gitignore) + `scripts/check_leak.py`(샘플 고객 토큰 잔존 0건, qa 게이트) + 부모 저장소 `.githooks/pre-commit`(input/output/_workspace/examples 스테이징 차단) | 하네스를 `dykim-claude-agents-skills/agent/`로 이동하며 과거 고객 완성본이 저장소에 올라간 사고 정정. 기존 자료는 샘플로만 쓰고 다른 문서에 재사용·적용 금지(오너 지시) |
| 2026-06-11 | 초기 구성(에이전트4·레퍼런스5·템플릿3) | 신규 구축 |
| 2026-06-11 | 도식화 범위 추가(개념도+AWS 인프라) | 078 아너파라다이스 산출물 참고 요청 |
| 2026-06-11 | `effort-estimation-methodology.md` 추가(레퍼런스6) + architect 연결 | 공수 산정 판단(측정단위·재스킨·재사용 비대칭·경계·함정13) 미문서화 빈칸 보강 |
| 2026-06-11 | 시운전(서울대 SDN) 4단계 완주 + qa가 phantom +4.0(29.0/33.0 불일치) 적발 | 하네스 검증 |
| 2026-06-11 | CSS 스크립트 주입(`scripts/inline_css.py`) + base_template 마커화 + builder.md "CSS 직접작성 금지·도식 기본포함" | 빌더가 CSS를 일부만 재작성해 디자인 드리프트(135→104 셀렉터)·도식 생략한 결함 교정 |
| 2026-06-11 | `report-spec.md` 추가(생성 규칙 정본: 입력계약·6표·정합 a-h·4변형) + consistency-checklist를 a-h로 교체 + architect 자기검증 | 타 세션 실전 명세 흡수 |
| 2026-06-11 | 워크스페이스 루트 `CLAUDE.md`에 하네스 트리거 규칙 등록(요건문서→파이프라인, 콜드메뉴 금지) | works 하위 어느 폴더에서 띄워도 자동 인식되게(078에서 미작동 문제 해결) |
| 2026-06-11 | **배포 패키징**: 루트 `CLAUDE.md`(현관문) + `input/`·`output/`·`.gitignore` + 상대경로 이식성 확인 | git 배포 모델 확정(폴더 clone→그 폴더에서 Claude Code 실행) |
| 2026-06-11 | `examples/` few-shot 라이브러리 추가(과거 완성본 4종 + INDEX) | 스타일·도식·산정 보정 참고. 사내 전용(고객 데이터 포함) |
| 2026-06-11 | **corpus 집단기억** 추가(`corpus/`·`scripts/corpus.py`·`.env`) — 산출물 누적, 유사 선례 검색-증강, qa PASS 시 자동 push | 팀이 쓸수록 데이터 축적→유사 건 일관성↑. 구조 B(1 repo), 인증 공용토큰(.env gitignored) |
| 2026-06-11 | GitLab 배포: code.etribe.co.kr/smart-technology/harness_st. **브랜치 2개 — `etribe`(도구 코드, clone 대상) / `corpus`(데이터, orphan)**. main은 protected(미사용) | 도구·데이터 분리 |
| 2026-06-11 | builder "클래스 발명 금지" 규칙 + `scripts/check_classes.py` orphan-class 가드(qa (i)) | 아너파라다이스 v1.0이 발명 클래스(.d1-no/.d2-chip 정의0·사용26)로 평문 깨짐 → 재발 차단 |
| 2026-06-11 | **corpus를 별도 `corpus` 브랜치로 분리**(etribe=코드/corpus=데이터). corpus.py가 gitignored `.corpus/`에 클론·commit·push | 도구 브랜치가 산출물 커밋으로 더러워지지 않게. 저장→push→검색 end-to-end 검증 완료 |
| 2026-06-11 | **IA 추출 고도화**: `scripts/ia_extract.py`(메가패널 정본·탭/그룹/외부 type·page/view 이중카운트·footer·로그인·경계bleed 섹션비율 dedup) + `ia-extraction-upgrade.md`(오류7·규칙·스키마) + site-ia-extraction/analyst/methodology/report-spec 연결 | 슬림 nav만 긁어 3뎁스·footer·회원도메인 누락, 분리페이지 합침/탭 쪼갬으로 공수 오차. GS칼텍스 검증(page74/view76) |
| 2026-06-11 | KB 방법론 이식(독립): playbook 2종(요건누락·공수5축검증) + corpus 피드백 루프(`corpus.py feedback`, 실제공수→과소산정 경고) + frontmatter 스키마·confidence/데이터갭 | 사내 KB·운영하네스 분석 차용. 쓸수록 산정 정확도 누적 |
| 2026-06-11 | 인테이크(정성 신호: 기획염려·디자인레벨→공수 가중) + 모델 티어링(builder·qa→sonnet) + solution-architect 분리해 architect와 병렬 | UX·비용·속도 동시 개선 |
| 2026-06-11 | analyst 분리(site-analyst sonnet, 사이트 IA 병렬) + 에이전트별 ref 화이트리스트 | 앞단 병렬·토큰 절감 |
| 2026-06-11 | **v1.1 시운전(아너파라다이스) GREEN** + 잠복결함 수정: `check_consistency.py`를 SDN하드코딩→**실제 표 파싱 범용**으로 재작성 · `check_classes.py` `<script>`제외(JS 거짓양성) · base_template `.hero-grid` · diagrams.css `.pub/.designv` 보강 | qa 스크립트가 SDN전용 일회용이라 타 프로젝트 검증 불가했던 것 적발·수정. 43.0 정합 PASS·발명클래스 0 |
| 2026-06-12 | **★ diagrams.css 미닫힌 `}` 수정(도식 깨짐 진짜 원인)** + `inline_css.py` 중괄호 균형 가드 | 078 추출 시 `@media` 닫는 `}` 1개 누락 → 뒤 AWS CSS 전체 파싱 붕괴 → 인프라 평면화(처음부터). Playwright 런타임 검증으로 `.aws-row` block→flex 확인. 클래스명/숫자 체크로는 못 잡던 CSS 파싱 오류라 빌드시 균형 가드 추가 |
| 2026-06-12 | 레이아웃 구조 고정(base_template `.layout/.sidebar`) + builder 인라인 override 금지 + `.pub/.designv` house-style로 이전 | 폭·타이틀이 즉흥 인라인으로 어긋남. 웅진 다이렉트 RFP end-to-end 검증 통과 |
| 2026-06-12 | **산정 독립성**: 세션/메모리의 다른 프로젝트·수작업 수치 비교·앵커 금지, 참고원은 corpus KB뿐 | 추론값+근거코멘트→사용자 확인. 과거 수치 수렴 비교는 순환·편향 |
| 2026-06-12 | **IA 표 룰(운영 피드백)**: 1노드=1row(·/쉼표 통합 금지·전 대메뉴 동일) + `.effort-table fixed`+colgroup+word-break:keep-all | 별도 사이트에서 일부 대메뉴만 펼치고 일부 통합·한글 컬럼 글자깨짐 |
| 2026-06-12 | **★ 스크립트 결정적 렌더 `build_report.py`(Phase 1-4)**: 구조화 JSON→HTML(레이아웃·IA표 1노드=1행·월별표 합계계산·영역별·간트·핵심요약·CSS·팔레트). 정합·구조·스타일을 코드가 보장 | builder(LLM) 반복 사고(클래스발명·도식깨짐·레이아웃·phantom) 원천 차단. 웅진 다이렉트 9섹션 렌더·정합16검사0·런타임 GREEN |
| 2026-06-12 | 렌더 기본경로를 스크립트로 채택(architect→`02_spec.json`→build_report, LLM builder=폴백) + 중간물 **프로젝트별 `_workspace/{slug}/`** | 공유 _workspace 교차 덮어쓰기(GS칼텍스가 웅진 덮음) 사고 방지 + 결정적 렌더 정규화 |
| 2026-06-12 | **build_report 4 렌더러 추가(역할매트릭스·WBS·개념도·인프라)** → 공수 6표 전부 + 도식 2종 결정적 렌더. css_block에 diagrams.css 인라인 | 도식까지 스크립트 kind화(손으로 안 그림). Playwright 런타임 GREEN(aws-row flex·eco-sat absolute·wbs phase색). etribe 9b8682a |
| 2026-06-12 | **★ 투입 연속성 가드 `build_report.compute_monthly`**: 톱니(중간월 0.5)·장기 반투입(0.5 2개월+ 연속) 자동 `[WARN]` + member `parttime:true` 예외 | 방법론 §9·qa (l)이 이미 전제하던 WARN을 정작 코드가 안 내보내던 빈칸. GS칼텍스 런에서 PM·기획·안정화 3행 톱니/장기0.5 적발(qa 1차 미검출) → 가드 구현·재배치(총 47.0 보존, 패턴 현실화) |
| 2026-06-12 | 목차(사이드바) 제목 끝 괄호 부연 자동 제거(`nav_label`) + architect title 규칙(부연은 area로) | 목차에 `(SSOT)`·`(주 단위/20주)` 등 군더더기 노출. etribe 8e7e0fc |
| 2026-06-12 | **KB 중간물 스냅샷**: `corpus.py snapshot`(단계/게이트마다 `_workspace/{slug}`→`deliverables/{id}/workspace/` 커밋, index 불변→검색 노이즈0) + `save --ws` + 안정 id 규칙(id=slug={고객}-{주제})·corpus 디렉토리 구조 문서화 | 완성본뿐 아니라 작업 과정도 KB에 누적(이력·감사). etribe 346f645 |
| 2026-06-12 | **파일 네이밍 표준 전면 통일**: `_workspace/{slug}/NN[x]_{artifact}`(bare 금지) — 01a_site-ia·01_analysis·02_spec·02b_solution·03_draft·04_qa·05_meta. 레거시명 전부 정리, ORCHESTRATOR에 정본 표 신설, 6에이전트+CLAUDE.md 정렬 | 산출물명 제각각·slug 누락(교차 덮어쓰기 원인) 해소 |
| 2026-06-12 | **사용자가이드.html**(Claude Code 대화 흐름 형식: 실제 사용 시나리오 + 안내 캡션) 추가 | 팀 배포용 사용법 가이드 |
| 2026-06-12 | **투입 연속성 자동 가드**: `build_report.check_sawtooth`(톱니·0.5 2개월+ 연속 → [WARN]) + 방법론§9·architect·qa(l). 정당 파트타임은 member `parttime:true` 예외 | 연속 투입 인력 중간월 0.5 불가 정책 부재 보완 |
| 2026-06-12 | **인테이크 항목 추가: 수행형태(상주/비상주)·예상 인프라 포함**. 비상주→퍼블·개발 -최대30%(AI활용, 기획/디자인 제외), 상주→감면없음+상주 인력 장기0.5 금지(parttime 예외 불가). 미응답 시 상주 가정 | 최초 사용자 확인 사항·수행형태별 공수 차이 미반영 |
| 2026-06-12 | **QA 인력 = 기획자 겸임(표준)**: QA 전담 직군 금지, 기획 1명 막달(통합테스트·UAT·오픈)까지 유지. build_report 가드(QA 전담 직군·기획 막달0 → [WARN]) | "기획자 없이 QA만" 구성 불가 정책 명문화 |
| 2026-06-12 | **테스트 구간 인력 감쇠(§9)**: 막달은 신규 제작 없음 → 디자인·퍼블 2명+ 투입 시 1명만 잔류(PM·기획·개발은 풀 가능, 디자인 위주면 개발도 감원). build_report 가드(막달 디자인/퍼블 2명+ → [WARN]) | 다인 디자인/퍼블이 끝까지 풀 잔류하는 과다 산정 방지 |
| 2026-06-12 | **IA 압축 자동 가드**: build_report가 children 없는 대메뉴 desc에 ·가 2개+면 [WARN](하위를 한 셀에 압축). architect IA는 하위를 반드시 `children[]`로 분해 명시 | 2뎁스 메뉴가 개별 행으로 안 펴지고 압축됨. 렌더러·샘플 무관(children 주면 펴짐), IA 데이터 생성 문제 |
| 2026-06-12 | **root 오염 정리**: `.playwright-mcp/`·루트 캡처 이미지(`/*.png\|jpg\|jpeg`) `.gitignore` 차단 + site-analyst §9 캡처를 `_workspace/{slug}/` 저장 지침. 기존 루트 캡처는 `input/`로 이동 | playwright 산출·사이트 캡처가 root에 쌓여 git 오염 |
| 2026-06-12 | **사용자가이드.html 보강**: 인테이크 질문(디자인·일정·상주/비상주·인프라 포함) 대화 추가, 비상주 -감면·인프라 포함 흐름 반영 | 물어봐야 할 항목을 대화 형식으로 보강 |
| 2026-06-12 | **관리자 IA 유추 강제**: IA group `admin:true` 플래그 + build_report 구분행("관리자 영역·유추·추정") + 누락 가드([WARN]). analyst 관리자 유추 필수 격상(표준 어드민 세트), architect IA=사용자+관리자 둘 다 | 프론트만 조사하고 관리자 IA가 누락/미구분되던 문제(렌더·가드에 admin 개념 부재) |
| 2026-06-12 | 목차 '공수 산정 —' 묶음 접두 자동 제거(nav_label) + 하위표 title 표이름만·번호 8-1~8-6 | 목차가 "공수 산정 — 영역별 공수"로 장황·08 6번 반복 |
| 2026-06-12 | **인테이크 순차 질문화**: 작성 시작 시 필요 항목을 한꺼번에 안 묻고 **하나씩** 질문→답→진행(디자인→일정→상주/비상주→인프라→TO-BE→누락). 한꺼번에 답하면 수용 | 한 번에 폭탄 질문 대신 대화형 단계 진행 |
| 2026-06-12 | **AS-IS 인프라 이미지 판독 + TO-BE 제안**: `extract_assets.py`(docx/pptx 임베드 이미지 추출) + analyst 판독 지침 + solution-architect AS-IS(Read 판독)→TO-BE 2섹션+마이그레이션. GS칼텍스 RFP 구성도 2종 판독 실증 | RFP 인프라 구성도 이미지를 읽어 현행 파악·제안까지 대응 |
| 2026-06-12 | IA 표 공수 컬럼 조건부: effort가 하나도 없으면(메뉴구조도) "공수(M/M)" 컬럼 자동 생략(3컬럼) | IA 정보구조도에 빈 공수 컬럼이 남아 어색했던 시각 문제(GS칼텍스 테스트 발견) |
| 2026-06-12 | **서술형 섹션 6종 전용 템플릿 + 번호 자동화**: build_report에 overview(메뉴칩)·modules(menu-list)·narrative(다크 final-report)·questions(확인질문)·coverage(요건표)·insight 렌더러 추가(cards=기존 summary 재사용). `no` 미지정 시 순번 자동. 기존 산출물 8종 클래스 패턴 실증→전용화. 신규 6종 렌더·발명클래스0·Playwright 런타임(menu-grid/list·final-report 다크·effort-grid·insight·번호 1-5) GREEN | prose 자유HTML이던 서술형 섹션 스타일 드리프트 차단(JSON 주입 100% 재현) |
| 2026-06-12 | 측정 철학 정정: IA=페이지(기능) 단위, "스타일 N"은 한 페이지 내 표시 변형일 때만(상품 56개=상품상세 1페이지·스타일은 디자인 산정에) | IA를 스타일 수로 축약하는 혼동 제거 |
| 2026-06-12 | **RFP 커버리지 + 확인 질문 + 인프라 AS-IS 동반**: analyst RFP 요건 전수 항목화 → architect 요건 커버리지 대조표(반영/부분/제외+사유/미확인) + "확인 필요 질문" 항상 마지막 섹션(추정·데이터갭 중립 질문) / 인프라 제안(TO-BE)은 AS-IS와 쌍. build_report 가드(확인질문 누락·TO-BE 단독 → [WARN]), qa (l)+(m) 점검 | RFP 반영 누락 확인·추측분 확인 리스트화·제안 인프라 현행 대비 |
| 2026-06-12 | **출력 위치 가드 + 전체경로 강제**: build_report `-o`가 `_workspace/`·`output/` 밖(temp·홈)이면 [WARN]. ORCHESTRATOR 명령 예시를 전체경로(`_workspace/{slug}/...`)로, temp/cwd 금지 규칙. qa (l)을 'build_report 모든 WARN 0'으로 일반화(IA압축·관리자누락·인력정책·출력위치 무시 금지) | 산출물이 temp 등 다른 장소에 흩어져 렌더되던 문제(상대경로+cwd 어긋남) |
| 2026-06-12 | IA 표 공수 컬럼 조건부 생략(effort 전무 시) + 관리자 출처 라벨 `admin_label`(자료 기반/유추) | IA 빈 공수 컬럼·관리자 자료를 유추로 오표기한 시각/표기 문제 |
| 2026-06-14 | 갭 #2(우산 시스템 비기능 전이): RFP가 우리 대상+외부/현행 시스템을 한 우산(무장애/레거시/기간계) 아래 묶으면 → 정체·경계·HA등급 상속·전환경계·I/F무단절 4종을 확인질문 표준 포함. playbook 공통·analyst | 실런에서 I/F 규격은 물었으나 "무장애 HA 전이가 홈페이지에 적용되나" 토대질문 누락(Q7 1개뿐) |
| 2026-06-14 | GS칼텍스 전체테스트 발견 갭 반영: ① 외부사 시스템(VAN·PG·기간계)=연계 I/F만, 시스템 전환개발 금지(architect·analyst·qa(p)⑥) ② corpus.py search 자유어 쿼리+태그 부분매칭(exact→substring, positional/--q) | 실런에서 VAN 174를 우리 구축으로 오인(112→GATE정정 77) + search 0건으로 index 수동조회 |
| 2026-06-14 | 피드백 정정: 자동반영·멀티유저 prefs 제거 → feedback-curator는 "오너용 수정 제안 리포트"만 생성(corpus.py propose→feedback/proposals.md 검토큐). 에이전트 수정은 오너 단독·승인 후 /harness | 에이전트 수정은 오너만, 피드백은 이해하기 쉬운 제안용 |
| 2026-06-14 | 수정 피드백 루프: feedback-curator(opus·on-demand) — 확정된 대화 수정을 취향(user)/공통개선(global) 분류해 corpus.py pref로 기록(prefs/{user}·feedback/agent-improvements). 취향=다음부터 자동, 공통=/harness 반영. 사용자가이드에 흐름 추가 | 한 사람 기준 하네스 → 사용자별 취향 반영 + 공통 개선 환류 |
| 2026-06-14 | 최종 HTML 자동 버전관리: corpus.py put-html(생성/수정시 버전 커밋·태그 이동)·get(최신/특정버전 받아보기). save의 index를 update-or-append로(재작업 중복 방지). 다중 사용자 대응 | 최종 HTML 자동 git 관리 + 최신본 조회 + 버전관리 요청 |
| 2026-06-14 | 기획 과소 가드: 기획 베이스=페이지수+난이도, 디자인 고도화 시 기획 동반 상승. build_report [WARN](기획 실무<디자인×0.5 / 기획1명vs디자인+퍼블4명+). 방법론§9·architect | 테스트결과 기획1 vs 디자인4 불균형 반복(GS: 기획5.5/1명 vs 디자인12.5/3명+퍼블14/4명) |
| 2026-06-14 | 커밋/푸시 포인트 정리: corpus.py save가 섹션 원자별 1커밋(kb(type):id|…)+kb(report)+태그 kb/{id}, snapshot/feedback 메시지 검색형 통일. ORCHESTRATOR "커밋/푸시 포인트" 정책+리치 05_meta 스키마. 옛 meta.md 구조 잔재 제거(CLAUDE·ORCHESTRATOR) | 한 덩어리 커밋→git log 검색 뭉툭. 원자 단위 커밋+검색형 메시지+태그로 빠른 취득 |
| 2026-06-14 | corpus KB 재설계(사내 kb 규약 채택, 우리 산출물 정렬): 섹션 원자 9종(overview·direction·ia·approach·infra·estimates·scope·questions·decisions)+케이스별 종합 cases/(범위→확인→공수 밴드)+patterns 14. corpus.py search 강화(밴드 카드+사슬 ref). 7폴더 9건 적재 | 단순 카드+HTML 재분석 구조 → 유형별 범위·확인·공수 인과를 바로 참고 |
| 2026-06-14 | 버전 변천 학습 반영(웅진081·코스모진078 23판 분석): ⑤표현절제(과장네이밍 금지) ⑥불확실시나리오 본산정 분리 ①수치변동 1:1사유+확정도(탐색/제안/확정) ④범위경계 in/out표+기존소스인계 확인. architect·builder·analyst·qa(s)·report-spec§8 | 사용자가 매 버전 적용한 관점을 에이전트에 내재화 |
| 2026-06-14 | corpus 참조 가시화·흔적 강제: Phase1.5 corpus 상태 한줄 보고(연결/0건/미연결사유) + analyst "참조 선례" 절·architect measure_note 선례 인용 필수 + 독립성 규칙에서 "corpus=허용된 참조(인용 대상)" 분리 + corpus.py 미연결 사유 명확화 | 산출물에 git KB 참조 흔적이 안 보임(테스트폴더 토큰부재로 조용히 skip + 소프트 단계라 흔적 미기록) |
| 2026-06-13 | 2차 비용 최적화(같은 결과·최소 비용): persona-review=methodology §13·§1.5만 / architect·analyst corpus-kb=검색부분만 / 02_spec.md=짧은요약·02b.md=기본생략 / 중간 스냅샷→GATE+최종 save만 | per-call 컨텍스트 적재·출력토큰·런타임 git I/O 낭비 제거(최종 산출물 동일) |
| 2026-06-13 | 콘텐츠 발전도 검토 추가 + 파이프라인 비용 최적화: 발전도(RFP 나열↔고도화)를 3c persona-review estimate에 흡수(신규 opus 0) + qa(r) 얕음 1차탐지 / 3b·5b 조건부화 → 평시 opus 5→3회 | RFP 충분히 발전 검토 담당 부재 + 최소 비용 요청 |
| 2026-06-13 | 인테이크 재정의: 고정 필수 5(디자인·개발방법·인프라구축실작업·상주비상주·기간, RFP 무관 항상) + 동적 RFP 질문 ⑥(2-4개 적극 도출). ORCHESTRATOR·CLAUDE·사용자가이드 | 개발방법·인프라 실작업 분기가 고정질문에 없거나 모호 / RFP 근거 확인질문은 동적·적극 도출이어야 |
| 2026-06-13 | 인테이크 질문 ⑥ 가드: 확인 질문은 RFP 내부 미상·모호 항목만, RFP 없는 기능(챗봇·AI) "필요하세요?" 타진 금지. ORCHESTRATOR⑥·CLAUDE§2·playbook | 출력 가드(RFP없는 챗봇 금지)를 인테이크 질문으로 우회 — GS 테스트에서 챗봇 필요 여부를 사용자에게 물음 |
| 2026-06-13 | 섹션 도입 prose 가독성 규칙: 짧은 리드(1-2문장)+구조화(불릿/표), 런온 한 문단 금지. 유지/변경/신규·스펙 나열은 delta 표/불릿으로. builder§9·architect·report-spec§8 | 섹션 도입부가 현행·변경·신규·스펙을 한 문단에 욱여넣어 가독성 저하 |
| 2026-06-13 | **★ 프로젝트 케이스 매트릭스 + 2축 delta(케이스 커버리지 점검)**: `references/project-cases.md` 신설(A.IA확인불가 / B.프론트만 / C.어드민자료 / D.어드민만[프론트X] / E.리뉴얼 / F.디자인만변경[개발0] / G.화면유지+백엔드신규[개발=신규] / H.신규구축). analyst 착수 시 케이스 판별→01 명시. **delta를 표현(화면)/구현(기능) 2축으로** 분리(F·G 오판 차단). architect/qa(q)/방법론§1.5/report-spec(D) 반영 | 드라이런으로 D·F·G 갭 발견(화면 유지를 개발 0으로 오판 등) → 보강 |
| 2026-06-13 | **★★ IA delta → 작업 도출 → 공수 추론 사슬(핵심 구조)**: 방법론 §1.5 신설 — 현행 IA를 RFP 대비 유지/변경/신규 분류 → 프론트 변경의 관리자 파생 작업 → 그 분류에서 공수 도출(영역 desc에 "현행X→분류→작업→공수" 근거). analyst(IA delta 태깅·관리자 파생)·architect(공수 delta 도출·"IA 변경 분석" 섹션)·qa(q)·persona-review·report-spec | 산출물이 "RFP 포인트→공수 점프"로 빈약 — IA·기능엔 delta 사슬이 없었음(인프라만 delta) |
| 2026-06-13 | **★ RFP 충실성·범위 정확성 강화(실테스트 5결함 교정)**: ① RFP 없는 기능(챗봇) 추가 금지·현행은 "유지"로만 ② 요건 비약 금지(GEO/SEO=콘텐츠·구조 최적화 SW지 색인엔진 인프라 아님) ③ 인프라 구축은 공수 작업 아님(제시만, 영역별 제외) ④ 관리자 IA 기본 골격(로그인·운영자관리·권한·보안/감사) 필수 ⑤ 역할 매트릭스 투입인력 세분(빈 cells 금지). analyst/architect/solution-architect/qa(p)/방법론§11/report-spec | GS칼텍스 실테스트 산출물에서 5결함 발견 |
| 2026-06-13 | **★ persona-review 에이전트 신규(멀티 페르소나 검토) + 2지점 삽입**: PM·아키텍트·개발·디자인/퍼블·고객 다관점으로 ① GATE 전(공수·인사이트, `02c`) ② qa 후 최종 전(콘텐츠, `04b`) 검토 → P0면 반려. qa(규칙·정합)와 분리된 '판단·설득력·고객 수용성' 검증 | 인사이트·공수·콘텐츠에 다관점 페르소나 검토가 파이프라인에 없었음(전역 review-board는 수동·미연결) |
| 2026-06-13 | **IA Front/Admin 분리 표시 + admin 조건부**: admin이 존재하는 사이트면 `Front IA 정보구조도`/`Admin IA 정보구조도` 2섹션 분리(통합+구분행은 폴백). **admin 없는 사이트(정적·소개형)는 Front만** — 억지 유추 금지. 관리자 누락 가드 제거(admin 강제 안 함). analyst·architect·site-ia·report-spec 반영 | IA에 admin 들어가면 분리 표시 요청 + admin은 항상 있는 게 아님 |
| 2026-06-13 | **★ TO-BE 인프라 = AS-IS delta(베스트안)**: 일반 모범 구성도 금지 → AS-IS 각 요소를 유지/변경/신규/제거로 분류·근거(RFP·현행) 표기, 현행 필수요소(이중화·환경분리·연계·IDC) 근거없이 제거 금지. 마이그레이션을 delta 표로. solution-architect·infra-diagram 가이드·qa (o) | TO-BE가 AS-IS 무시하고 일반 단순 구성도로 가서 현행 연계 4종 등 필수요소 누락 |
| 2026-06-13 | **★ 고객 제공 구성도는 원본 그대로(figure kind)**: AS-IS 인프라가 고객 제공 도식이면 `infra`(aws 그리드)로 다시 그리지 말고 **원본 이미지를 `figure`로 임베드**(로컬→base64 인라인, self-contained). solution-architect 지침 + AS-IS/TO-BE 가드 figure 인식 | aws 그리드 템플릿이 온프레미스 토폴로지(L4·서버명·연결선·VM·연계)를 표현 못 해 고객 구성도를 요약·변형한 사고 — 제공 도식 변형 금지 |
| 2026-06-13 | **★ 자료 > 유추 원칙 + 입력 자료 출처 인벤토리(하네스 진화)**: analyst에 "입력 자료 출처 인벤토리" 절 신설(영역×출처 매핑: 자료제공/부분/없음), report-spec 입력계약 "자료 우선" 행, ORCHESTRATOR Phase1 인벤토리, qa (n) 제공자료 반영 점검(자료를 유추로 표기 시 FAIL), 관리자=유추 편향→케이스 분기 | **근본 원인: "관리자=유추" 디폴트 편향 + 입력 자료 출처 분류 단계 부재 → 자료(xls ADMIN 79기능) 무시·유추 사고. IA·기능·인프라·연동 전 영역 일반화** |
| 2026-08-19 | **★ 하우스 스타일 전면 개정 — warm paper × near-black 에디토리얼**: `house-style.css` 재작성(팔레트 cream/ink · radius 0-2px · 그라디언트·박스섀도 제거 · Paperlogy+Pretendard 웹폰트 · 간트/WBS `--ph-*` 저채도 9색 램프 · `@page A4` 인쇄 규칙 신설). **클래스명 100% 유지**(check_classes·build_report 호환), 구 `--brand` 계열은 별칭으로 잔존(diagrams.css·spec palette 주입용). 부수: `diagrams.css` `.pub/.designv` 를 토큰 참조로(구 파스텔이 house-style을 덮고 있었음) · `build_report.py` 구 파스텔 role 배경 매핑 + insight 제목 데코 이모지 제거 · `base_template.html` 주석/이모지 정리 · house-style-guide·report-spec §4 개정 | 기준 레퍼런스 = 신승 비즈니스AI플래너 권한정책 매트릭스. 파랑 브랜드+그라디언트 카드 톤이 문서형 산출물에 과했음. NH농협손해보험 spec 재렌더로 검증(정합 13검사 0실패 · 발명클래스 0) |
