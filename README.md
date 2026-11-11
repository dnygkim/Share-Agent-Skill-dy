# Share-Agent-Skill(dy)

김단영(dykim)의 Claude Code **스킬**과 **에이전트 하네스**를 받아 쓰는 공유용 리포.
원본 리포 `dykim-claude-agents-skills`에서 개인 전용 항목만 뺀 나머지가 1:1로 들어 있고, 원본이 바뀌면 이 리포도 같이 바뀐다.

- **이 리포는 받기 전용** — 여기서 고친 내용은 다음 업데이트 때 원본 내용으로 되돌아간다. 고칠 점은 관리자에게 전달
- **빠진 것**: 단이bot(`agent/danibot`) · Dan Jr. 스킬(`skills/danjr`) · 페르소나(`persona`) · 개인 메모리 · PC 동기화 스크립트

## 처음 설치 (1회)

준비물: Git, Claude Code. Windows는 [Git for Windows](https://git-scm.com/download/win)에 포함된 **Git Bash**에서 실행한다(PowerShell의 `bash`는 WSL일 수 있어 쓰지 않는다).

```bash
# 1) 받기 — 처음 한 번 GitHub 로그인 창이 뜬다
cd ~/Documents
git clone https://github.com/dnygkim/Share-Agent-Skill-dy.git
cd Share-Agent-Skill-dy

# 2) 내 Claude Code 에 반영
bash share/update.sh
```

```powershell
# 3) 주 1회 자동 업데이트 등록 — Windows (PowerShell)
powershell -ExecutionPolicy Bypass -File share\schedule-weekly-windows.ps1
```

```bash
# 3) 주 1회 자동 업데이트 등록 — Mac (터미널)
bash share/schedule-weekly-mac.sh
```

등록 후에는 **매주 월요일 09:00**에 새 내용이 있을 때만 받아서 반영한다. PC가 꺼져 있었으면 켜진 뒤 실행한다. 반영된 내용은 새로 여는 Claude Code 세션부터 적용된다. 실행 기록은 `~/.claude/dykim-share-update.log`.

## 업데이트가 내 PC에서 하는 일

| <sub>대상</sub> | <sub>동작</sub> |
|:---|:---|
| <sub>`~/.claude/skills/<스킬>`</sub> | <sub>이 리포의 스킬을 설치·교체. 리포에서 빠진 스킬은 이 리포가 설치했던 것만 지운다. 원래 있던 같은 이름 스킬은 처음 한 번 `~/.claude/skills-backup-날짜시각/`으로 옮겨 둔다</sub> |
| <sub>`~/.claude/house-style/`</sub> | <sub>HTML 산출물 기본 스타일(`house-style.css` · `base_template_doc.html`)과 공유 규칙(`global-rules.md`) 교체</sub> |
| <sub>`~/.claude/CLAUDE.md`</sub> | <sub>기존 내용은 그대로 두고, 맨 끝에 공유 규칙 불러오기 한 줄(`@~/.claude/house-style/global-rules.md`)만 1회 추가. 공유 규칙을 끄려면 이 줄을 지운다</sub> |
| <sub>`agent/*/.claude/skills/`</sub> | <sub>하네스가 쓰는 스킬 사본을 다시 생성(`sync-skills.sh`)</sub> |

지금 바로 받고 싶으면 `bash share/update.sh`, 변경이 없어도 다시 반영하려면 `bash share/update.sh --force`.
자동 업데이트 해제: Windows `Unregister-ScheduledTask -TaskName 'dykim-share-update' -Confirm:$false` · Mac은 `share/schedule-weekly-mac.sh` 머리말 참고.

## 들어 있는 것

| <sub>에이전트(하네스)</sub> | <sub>역할</sub> |
|:---|:---|
| <sub>[`agent/proposal/`](agent/proposal/)</sub> | <sub>제안서 작성 파이프라인 (RFP 분석 · 리서치 → 컨셉 → 목차 → 차수별 추출 → 최종본)</sub> |
| <sub>[`agent/prd/`](agent/prd/)</sub> | <sub>공수산정 · 기초 PRD(RRD) 생성</sub> |
| <sub>[`agent/harness_st-etribe/`](agent/harness_st-etribe/)</sub> | <sub>공수산정 분석서 하네스</sub> |
| <sub>[`agent/screen-spec-id/`](agent/screen-spec-id/)</sub> | <sub>메뉴구조도(IA) 엑셀 → 화면ID 채번 → 화면명세서</sub> |
| <sub>[`agent/feature-spec-sb/`](agent/feature-spec-sb/)</sub> | <sub>PRD(명세서) → SB(화면설계서 · 와이어프레임)</sub> |
| <sub>[`agent/test-runner/`](agent/test-runner/)</sub> | <sub>qa-master TC 엑셀을 브라우저에서 수행 → 결과 엑셀 · HTML 리포트</sub> |
| <sub>[`agent/worker/`](agent/worker/)</sub> | <sub>단순작업 위임 서브에이전트</sub> |

하네스는 해당 폴더에서 Claude Code를 열어 쓴다. 쓰는 방법은 각 폴더의 `README.md`.

스킬 목록과 제작자는 [`skills/README.md`](skills/README.md). 기획 실무 스킬 8종(`dev-reading` · `flowchart-defense` · `ia-builder` · `meeting-minutes` · `qa-master` · `requirements-generator` · `wbs-generator` · `weekly-report`)의 제작자는 신지은([jieun994/zinis_claude_skills](https://github.com/jieun994/zinis_claude_skills)). `ui-ux-pro-max-skill/`은 외부 스킬(MIT) 백업으로 자동 설치 대상이 아니다.

## 알아 둘 점

- 하네스 문서에 나오는 「Dan Jr. 등급 조회」는 관리자 PC 전용 파일(`~/.claude/persona/persona.md`)을 가리킨다. 받는 PC에는 이 파일이 없으므로 하네스는 승인 단계마다 그대로 묻는다
- `agent/*/input/` · `output/`에 넣은 고객 자료는 Git에 올라가지 않는다(`.gitignore`). `agent/*/examples/`의 완성본은 형식 참고용 — 고객명 · 수치 · 문장을 다른 문서에 재사용하지 않는다

<!-- RELEASE-NOTES:START — share/build-release-notes.sh 가 미러할 때마다 다시 만든다. 이 사이는 직접 고치지 않는다 -->
## 릴리즈노트

원본 각 폴더 README 의 릴리즈노트를 모아 일자별로 정리한 것 (총 126건 · 최신 2026.11.10). 상세는 항목 이름을 눌러 해당 README 에서 본다.

### 공통 반영 사항

모든 하네스 · 스킬에 공통으로 적용되는 전역 규칙. 정본은 [`global-house-style/CLAUDE.md`](global-house-style/CLAUDE.md)이고, `share/update.sh` 가 `~/.claude/house-style/global-rules.md` 로 설치해 `~/.claude/CLAUDE.md` 에서 불러온다. 규칙이 바뀐 이력은 아래 표의 「공통」 구분.

| <div align="center"><sub>#</sub></div> | <sub>전역 규칙</sub> |
|:---:|:---|
| <sub>1</sub> | <sub>HTML 산출물 하우스 스타일</sub> |
| <sub>2</sub> | <sub>거버닝 메시지 문체 (장표·섹션 헤드라인)</sub> |
| <sub>3</sub> | <sub>산출물 파일명</sub> |
| <sub>4</sub> | <sub>자동화 창은 서브모니터로</sub> |
| <sub>5</sub> | <sub>HTML 산출물 수정 이력 메타정보</sub> |

### 일자별 업데이트 항목

| <sub>일자</sub> | <sub>공통</sub> | <sub>하네스</sub> | <sub>스킬</sub> |
|:---:|:---|:---|:---|
| <sub>2026.11.10</sub> | <sub>[global-house-style](global-house-style/README.md)</sub> | <sub>[proposal](agent/proposal/README.md)</sub> | <sub>[rfp-analysis-research](skills/rfp-analysis-research/README.md)</sub> |
| <sub>2026.11.06</sub> | <sub>[global-house-style](global-house-style/README.md)</sub> |  |  |
| <sub>2026.11.04</sub> |  | <sub>[test-runner](agent/test-runner/README.md)</sub> | <sub>[qa-master](skills/qa-master/README.md)</sub> |
| <sub>2026.10.22</sub> | <sub>[하네스 공통](agent/)</sub> | <sub>[feature-spec-sb](agent/feature-spec-sb/README.md) · [harness_st-etribe](agent/harness_st-etribe/README.md) · [prd](agent/prd/README.md) · [proposal](agent/proposal/README.md) · [screen-spec-id](agent/screen-spec-id/README.md)</sub> |  |
| <sub>2026.10.19</sub> | <sub>[global-house-style](global-house-style/README.md)</sub> |  | <sub>[rfp-analysis-research](skills/rfp-analysis-research/README.md)</sub> |
| <sub>2026.10.09</sub> | <sub>[global-house-style](global-house-style/README.md)</sub> |  | <sub>[handoff](skills/handoff/README.md)</sub> |
| <sub>2026.09.11</sub> |  | <sub>[proposal](agent/proposal/README.md)</sub> | <sub>[proposal-slide-builder](skills/proposal-slide-builder/README.md)</sub> |
| <sub>2026.09.03</sub> |  | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> |  |
| <sub>2026.09.02</sub> |  |  | <sub>[eli5](skills/eli5/README.md)</sub> |
| <sub>2026.08.27</sub> | <sub>[global-house-style](global-house-style/README.md)</sub> |  |  |
| <sub>2026.08.20</sub> | <sub>[global-house-style](global-house-style/README.md)</sub> | <sub>[prd](agent/prd/README.md)</sub> |  |
| <sub>2026.08.19</sub> |  | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> |  |
| <sub>2026.08.04</sub> |  |  | <sub>[ia-builder](skills/ia-builder/README.md)</sub> |
| <sub>2026.08.03</sub> |  | <sub>[feature-spec-sb](agent/feature-spec-sb/README.md)</sub> |  |
| <sub>2026.07.21</sub> |  |  | <sub>[dev-reading](skills/dev-reading/README.md) · [flowchart-defense](skills/flowchart-defense/README.md) · [ia-builder](skills/ia-builder/README.md) · [meeting-minutes](skills/meeting-minutes/README.md) · [requirements-generator](skills/requirements-generator/README.md) · [wbs-generator](skills/wbs-generator/README.md) · [weekly-report](skills/weekly-report/README.md)</sub> |
| <sub>2026.07.20</sub> |  | <sub>[screen-spec-id](agent/screen-spec-id/README.md)</sub> |  |
| <sub>2026.07.16</sub> |  |  | <sub>[ui-ux-pro-max-skill](ui-ux-pro-max-skill/README.md)</sub> |
| <sub>2026.07.15</sub> |  | <sub>[proposal](agent/proposal/README.md) · [worker](agent/worker/README.md)</sub> |  |
| <sub>2026.07.13</sub> |  | <sub>[screen-spec-id](agent/screen-spec-id/README.md)</sub> | <sub>[deckslide-design-guideline](skills/deckslide-design-guideline/README.md)</sub> |
| <sub>2026.07.07</sub> |  | <sub>[prd](agent/prd/README.md) · [proposal](agent/proposal/README.md)</sub> | <sub>[proposal-slide-builder](skills/proposal-slide-builder/README.md) · [proposal-structure-validation](skills/proposal-structure-validation/README.md) · [rfp-analysis-research](skills/rfp-analysis-research/README.md) · [ux-journey-insight](skills/ux-journey-insight/README.md)</sub> |
| <sub>2026.06.14</sub> |  | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> |  |
| <sub>2026.06.13</sub> |  | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> |  |
| <sub>2026.06.12</sub> |  | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> |  |
| <sub>2026.06.11</sub> |  | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> |  |

### 상세 내역 (월별)

<details open>
<summary><b>2026.11</b> · 8건</summary>

| <sub>일자</sub> | <sub>구분</sub> | <sub>항목</sub> | <div align="center"><sub>내용</sub></div> | <sub>소유자</sub> |
|:---:|:---:|:---:|:---|:---:|
| <sub>2026.11.10</sub> | <sub>공통</sub> | <sub>[global-house-style](global-house-style/README.md)</sub> | <sub>외부링크 아이콘을 블랙 라인(투명도 제거)으로 변경하고, 본문 고유명사(사이트 · 서비스 · 기관 · 도구)도 같은 `a.ext`로 연결하는 규칙을 `house-style.css` §22에 명시 — 2026.11.10 지시, `~/.claude/house-style/` 사본과 동일 유지</sub> | <sub>김단영</sub> |
|  | <sub>하네스</sub> | <sub>[proposal](agent/proposal/README.md)</sub> | <sub>작업단계 7단계 재편 + README 전면 보강 — ① RFP 분석 · 리서치(제안 키워드 · 방향성) ② 컨셉 · 스토리텔링 ③ 목차(페이지별 삽입내용) ④ 초안 · 1차 추출 ⑤ 피드백 반영 ⑥ 2차 추출 + 변경분 HTML ⑦ 최종본. 컨셉 승인 후 목차로 넘어가는 경쟁입찰형 골격을 기본으로(`references/skeleton-bid.md`), 견적형은 유지. 에이전트 4종 신설(`concept-planner` · `reference-collector` · `feedback-integrator` · `release-packager`), 문체 공통지침(`references/writing-style.md` · 기준 덱 = 메리츠화재 2027 발표본), 문체 점검 · 변경분 비교 스크립트(`check_style.pl` · `diff_deck.pl`), 차수 폴더(`r{n}/`)와 버전 연결, 산출물 파일명을 전역 규칙으로 통일. README는 처음 쓰는 사람 기준으로 배경 · 활용 목적 · 용어 · 단계별 설명 · 예시 대화 · 자주 묻는 질문 추가. 문체: 거버닝 메시지는 명사구가 기본이고 약속형(~하겠습니다)은 일부 허용하는 예외로 확정, 기준 덱(메리츠) 예문은 지침에 그대로 유지</sub> | <sub>김단영</sub> |
|  | <sub>하네스</sub> | <sub>[proposal](agent/proposal/README.md)</sub> | <sub>HTML 문서 외부링크 규칙 추가(`CLAUDE.md` 5a) — 출처뿐 아니라 본문 고유명사(사이트 · 서비스 · 기관 · 도구)도 `a.ext`로 연결, 아이콘은 텍스트 우측 끝 블랙 라인(정본 §22), URL 열림 검증 · 링크 전후 화면 텍스트 동일 검수. `rfp-analyst` · `qa` 에이전트 반영 (삼성자산운용 FunETF RFP 분석 보고서에 적용)</sub> | <sub>김단영</sub> |
|  | <sub>스킬</sub> | <sub>[rfp-analysis-research](skills/rfp-analysis-research/README.md)</sub> | <sub>본문 고유명사(사이트 · 서비스 · 기관 · 도구) 링크 규칙 추가 — 섹션당 첫 등장 `a.ext` 연결, 아이콘은 우측 끝 블랙 라인(정본 §22). `SKILL.md` [HTML 산출 시 출처 링크] 절 보강</sub> | <sub>김단영</sub> |
| <sub>2026.11.06</sub> | <sub>공통</sub> | <sub>[global-house-style](global-house-style/README.md)</sub> | <sub>전역 규칙 3종 동기화 — 산출물 파일명 원문 대조 보강(단계코드 · 문서번호 · 확정본 보존 · 개정이력 · 적용 제외)·자동화 창은 서브모니터로·HTML 산출물 수정 이력 메타정보(모두 2026.10.28 지시). Windows PC `~/.claude/CLAUDE.md` 기준 반영 — Dan Jr. 절의 리포 전용 문구(전역 규칙 없는 환경 · 클라우드 세션 안내) 유지</sub> | <sub>김단영</sub> |
| <sub>2026.11.04</sub> | <sub>하네스</sub> | <sub>[test-runner](agent/test-runner/README.md)</sub> | <sub>README 전면 보강 — 처음 쓰는 사람 기준 단계별 동작 설명(사전 준비 → 인테이크 8문항 → device-checker · tc-loader · GATE · runner · reporter → 산출물), 보류 사유 코드 · 예시 대화 · 자주 묻는 질문 추가, 명사형 종결 · 리포 README 표 표기 규칙 적용, scripts/README 설치 명령 보정(PATH 선행)</sub> | <sub>김단영</sub> |
|  | <sub>하네스</sub> | <sub>[test-runner](agent/test-runner/README.md)</sub> | <sub>최초 등록 — qa-master TC 엑셀을 브라우저(claude-in-chrome · Playwright)에서 직접 수행하고 Pass/Fail/Block·전수 증적을 기입하는 실행 하네스. 회차(디바이스 1개)별 결과 엑셀 사본 + 하우스 스타일 HTML 리포트. Node 스크립트 7종</sub> | <sub>김단영</sub> |
|  | <sub>스킬</sub> | <sub>[qa-master](skills/qa-master/README.md)</sub> | <sub>최초 등록 — 신지은 스킬 이관 (jieun994/zinis_claude_skills, v0.1.0)</sub> | <sub>신지은</sub> |

</details>

<details>
<summary><b>2026.10</b> · 10건</summary>

| <sub>일자</sub> | <sub>구분</sub> | <sub>항목</sub> | <div align="center"><sub>내용</sub></div> | <sub>소유자</sub> |
|:---:|:---:|:---:|:---|:---:|
| <sub>2026.10.22</sub> | <sub>공통</sub> | <sub>[하네스 공통](agent/)</sub> | <sub>prd·proposal·harness_st-etribe·screen-spec-id·feature-spec-sb 5종 CLAUDE.md에 Dan Jr. 등급 조회 공통 절차 추가 — 인테이크·GATE·「~할까요?」 직전 persona.md 확인, 건너뛴 게이트는 완료 보고에 ID 표기</sub> | <sub>김단영</sub> |
|  | <sub>하네스</sub> | <sub>[feature-spec-sb](agent/feature-spec-sb/README.md)</sub> | <sub>Dan Jr. 등급 조회 추가 — 작성자명·양식 질문 직전 `persona.md` 확인(A 진행·B 보고·C 질문), Step 0.1·2.5 승인은 유지</sub> | <sub>김단영</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**Dan Jr. 등급 조회**(CLAUDE.md 동작 규칙 2): 인테이크·GATE 직전 `persona.md` 확인 — A 진행·B 보고·C 질문, 건너뛴 게이트는 완료 보고에 ID 표기</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[prd](agent/prd/README.md)</sub> | <sub>Dan Jr. 등급 조회 추가 — 인테이크·GATE 직전 `persona.md` 확인(A 진행·B 보고·C 질문), 건너뛴 게이트는 완료 보고에 ID 표기</sub> | <sub>김단영</sub> |
|  | <sub>하네스</sub> | <sub>[proposal](agent/proposal/README.md)</sub> | <sub>Dan Jr. 등급 조회 추가 — 인테이크·GATE 직전 `persona.md` 확인(A 진행·B 보고·C 질문), 건너뛴 게이트는 완료 보고에 ID 표기</sub> | <sub>김단영</sub> |
|  | <sub>하네스</sub> | <sub>[screen-spec-id](agent/screen-spec-id/README.md)</sub> | <sub>Dan Jr. 등급 조회 추가 — 각 STEP 승인 직전 `persona.md` 확인(A 진행·B 보고·C 질문), 건너뛴 게이트는 완료 보고에 ID 표기</sub> | <sub>김단영</sub> |
| <sub>2026.10.19</sub> | <sub>공통</sub> | <sub>[global-house-style](global-house-style/README.md)</sub> | <sub>출처 외부링크 규칙 추가 — 리서치·분석 문서는 출처 URL을 항목 타이틀(1건)·해당 구절(2건 이상)에 직접 연결. `house-style.css` §22 `a.ext`(옅은 밑줄 · 끝 외부링크 아이콘 · hover 반전 · 인쇄 시 아이콘 숨김) · `.src-tag`, `base_template_doc.html` 팔레트 · 출처 표 예시, 전역 규칙 「출처 외부링크」 절 — 메리츠화재 RFP 분석 보고서에서 확정</sub> | <sub>김단영</sub> |
|  | <sub>스킬</sub> | <sub>[rfp-analysis-research](skills/rfp-analysis-research/README.md)</sub> | <sub>HTML 산출 시 출처 링크 규칙 추가 — 출처 URL을 [S번호]·출처 표에만 두지 않고 본문 항목 타이틀·구절에 `a.ext`로 연결, 스타일은 하우스 스타일 정본 §22</sub> | <sub>김단영</sub> |
| <sub>2026.10.09</sub> | <sub>공통</sub> | <sub>[global-house-style](global-house-style/README.md)</sub> | <sub>전역 규칙 3종 동기화 — 거버닝 메시지 문체(2026.09.11)·어절 단위 줄바꿈(2026.09.17)·산출물 파일명 두 트랙(2026.10.01). `house-style.css` §3 `word-break:keep-all`·제목 `text-wrap:balance` 반영 — 8/27 이후 `~/.claude/` 에만 있던 변경분</sub> | <sub>김단영</sub> |
|  | <sub>스킬</sub> | <sub>[handoff](skills/handoff/README.md)</sub> | <sub>최초 등록 — `/clear` 전 세션 맥락을 `.claude/HANDOFF.md` 로 저장하는 개인 스킬을 리포 정본으로 등록. 같은 파일을 PC 간 인수인계(Mac → Windows)에도 사용</sub> | <sub>김단영</sub> |

</details>

<details>
<summary><b>2026.09</b> · 4건</summary>

| <sub>일자</sub> | <sub>구분</sub> | <sub>항목</sub> | <div align="center"><sub>내용</sub></div> | <sub>소유자</sub> |
|:---:|:---:|:---:|:---|:---:|
| <sub>2026.09.11</sub> | <sub>하네스</sub> | <sub>[proposal](agent/proposal/README.md)</sub> | <sub>HTML 최종본 모드 추가 — 착수 시 실제 제작 포맷(HTML 제출본 vs PPT/Figma)·작업 사이즈(장표 규격) 확인, 1600×900 골격(`template/deck_1600_template.html`), 덱 제작 플레이북(`references/deck-production-playbook.md`), 덱 편집·피그마 벡터 취합·렌더·목차 스크립트 5종, check_slides 덱 점검 확장 (GS칼텍스 제안 실전 반영)</sub> | <sub>김단영</sub> |
|  | <sub>스킬</sub> | <sub>[proposal-slide-builder](skills/proposal-slide-builder/README.md)</sub> | <sub>STEP 0 에 실제 제작 포맷 확인(HTML 최종본 vs PPT/Figma 제출본)·작업 사이즈(장표 규격) 확인 단계 추가 — HTML 최종본이면 제출 규격 덱 + 제안서 하네스 취합 루틴(deck-production-playbook) 연계. design-system §3 크기 착수 시 확인·§5 1600×900 덱 안내 (GS칼텍스 제안 실전 반영)</sub> | <sub>김단영</sub> |
| <sub>2026.09.03</sub> | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**★ 민감자료 정책 명문화**(CLAUDE.md): 추적 금지·재활용 금지·외부 반출 금지 3원칙 + `examples/*.html` git 미추적(.gitignore) + `scripts/check_leak.py`(샘플 고객 토큰 잔존 0건, qa 게이트) + 부모 저장소 `.githooks/pre-commit`(input/output/_workspace/examples 스테이징 차단)</sub> | <sub>—</sub> |
| <sub>2026.09.02</sub> | <sub>스킬</sub> | <sub>[eli5](skills/eli5/README.md)</sub> | <sub>최초 등록 — [anthropics/claude-plugins-community](https://github.com/anthropics/claude-plugins-community/blob/main/eli5/skills/eli5/SKILL.md) 백업</sub> | <sub>김단영</sub> |

</details>

<details>
<summary><b>2026.08</b> · 13건</summary>

| <sub>일자</sub> | <sub>구분</sub> | <sub>항목</sub> | <div align="center"><sub>내용</sub></div> | <sub>소유자</sub> |
|:---:|:---:|:---:|:---|:---:|
| <sub>2026.08.27</sub> | <sub>공통</sub> | <sub>[global-house-style](global-house-style/README.md)</sub> | <sub>확인 생략 시 폴백 명문화 — 스타일 확인 질문 없이 진행되면(무응답·일괄 진행·비대화형) 하네스/스킬에 정의된 기본 양식으로 작성, 임의 스타일·보류 금지</sub> | <sub>김단영</sub> |
|  | <sub>공통</sub> | <sub>[global-house-style](global-house-style/README.md)</sub> | <sub>HTML 기본 스타일 전면 통일 — `agent/proposal`(슬라이드형)·`agent/prd`(문서형)·`proposal-slide-builder` 가 이 정본을 공유. 자체 팔레트(CI 5색·`--brand` 대시보드) 은퇴 · CI 옵트인 · 하네스는 추출 전 기본 스타일 확인</sub> | <sub>김단영</sub> |
|  | <sub>공통</sub> | <sub>[global-house-style](global-house-style/README.md)</sub> | <sub>LNB 상단 정렬(`margin-top:0`)·앵커 목적지 보정(`[id]{scroll-margin-top}`)·목차 `#s0` 목적지 신설 — KOMCA RFI 분석서에서 손으로 덧댄 보정을 정본으로 흡수</sub> | <sub>김단영</sub> |
| <sub>2026.08.20</sub> | <sub>공통</sub> | <sub>[global-house-style](global-house-style/README.md)</sub> | <sub>최초 등록 — `~/.claude/house-style/` + `~/.claude/CLAUDE.md`의 Git 백업/정본</sub> | <sub>김단영</sub> |
|  | <sub>하네스</sub> | <sub>[prd](agent/prd/README.md)</sub> | <sub>인테이크에 스타일 확인 단계 신설 — HTML 산출 시 컬러를 임의 고정하지 않고 매 프로젝트 확인 후 적용</sub> | <sub>김단영</sub> |
| <sub>2026.08.19</sub> | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**★ 하우스 스타일 전면 개정 — warm paper × near-black 에디토리얼**: `house-style.css` 재작성(팔레트 cream/ink · radius 0-2px · 그라디언트·박스섀도 제거 · Paperlogy+Pretendard 웹폰트 · 간트/WBS `--ph-*` 저채도 9색 램프 · `@page A4` 인쇄 규칙 신설). **클래스명 100% 유지**(check_classes·build_report 호환), 구 `--brand` 계열은 별칭으로 잔존(diagrams.css·spec palette 주입용). 부수: `diagrams.css` `.pub/.designv` 를 토큰 참조로(구 파스텔이 house-style을 덮고 있었음) · `build_report.py` 구 파스텔 role 배경 매핑 + insight 제목 데코 이모지 제거 · `base_template.html` 주석/이모지 정리 · house-style-guide·report-spec §4 개정</sub> | <sub>—</sub> |
| <sub>2026.08.04</sub> | <sub>스킬</sub> | <sub>[ia-builder](skills/ia-builder/README.md)</sub> | <sub>기본형 결과 예시(samples/결과_예시.xlsx) 업데이트</sub> | <sub>김단영</sub> |
| <sub>2026.08.03</sub> | <sub>하네스</sub> | <sub>[feature-spec-sb](agent/feature-spec-sb/README.md)</sub> | <sub>**(0) 프로젝트 착수 모드 신설** — 서비스명(프로젝트명)·디바이스(PC/모바일 웹) 확인 → 서비스 정의서(경량 PRD) → IA 생성(`ia-builder` 스킬 호출) → 화면별 플로우차트 → SB 추출까지 잇는 신규 파이프라인. `rules/project-kickoff.md` 신설, `sync-skills`에 이 폴더 추가(ia-builder 자동 로드). IA↔SB 연결 지점 실행 검증 완료</sub> | <sub>김단영</sub> |
|  | <sub>하네스</sub> | <sub>[feature-spec-sb](agent/feature-spec-sb/README.md)</sub> | <sub>**토큰 프리 전환** — 작성 규칙 정본을 `guides/` 4종(features-list·prd-structure·flowchart-rules·sb-writing)으로 수록. `fetch_guide.py`가 «토큰 있으면 서버 최신본, 없으면 로컬 정본»으로 자동 폴백(`--offline` 옵션). 이미 리포에 구현된 시트 CSS·KRDS 컴포넌트·챗봇 카탈로그는 중복 수록하지 않음. CLAUDE.md·README에 단계별 사용법 명시. 원작자(황다혜 프로) 표기 전 문서 삽입. 검증: 설정 파일 제거 상태에서 SB 8장 192개 검사 + 어드민 9장 전부 통과</sub> | <sub>김단영</sub> |
|  | <sub>하네스</sub> | <sub>[feature-spec-sb](agent/feature-spec-sb/README.md)</sub> | <sub>하네스 실동작 테스트 후 수정 — ① PC 캔버스 세로 Flexible 명시(`height:auto` + `--canvas-min-height`, 인라인 높이 고정 시 경고) ② 챗봇·어드민 워크북 경로 하드코딩 제거(원제작자 macOS 경로·고객 파일명 삭제, 미지정 시 설정 방법 안내) ③ `build_chatbot_sb.py`의 스킬 경로를 스크립트 위치 기준으로 변경</sub> | <sub>김단영</sub> |
|  | <sub>하네스</sub> | <sub>[feature-spec-sb](agent/feature-spec-sb/README.md)</sub> | <sub>`templates/Commom-sb-styleguide.md` 신규 — KRDS v1.0.0 Figma 공통 컴포넌트 12종 + 디자인 스타일 토큰을 **모노톤(블랙·무채색)** 화면설계 구성요소 가이드로 변환. 토큰(램프/타이포/간격/라운드)·컴포넌트별 Variant·치수·모노톤 색상 매트릭스·SB 표기 규칙·KRDS 원본 컬러 대조표 수록</sub> | <sub>김단영</sub> |
|  | <sub>하네스</sub> | <sub>[feature-spec-sb](agent/feature-spec-sb/README.md)</sub> | <sub>폴더 정리 — `references/`를 `rules/`로 옮겨 `reference/`와의 이름 중복 해소. reference=기존 산출물 레퍼런스 · samples=화면설계 HTML · templates=출력 에셋(로고 원본 이동)으로 역할 분리</sub> | <sub>김단영</sub> |
|  | <sub>하네스</sub> | <sub>[feature-spec-sb](agent/feature-spec-sb/README.md)</sub> | <sub>최초 등록 — AX-Pilot에서 이관. 범용 PC/MO B2C 화면설계를 기본으로 재구성(챗봇·어드민 규칙 분리) + 회귀 3건 수정</sub> | <sub>김단영</sub> |

</details>

<details>
<summary><b>2026.07</b> · 21건</summary>

| <sub>일자</sub> | <sub>구분</sub> | <sub>항목</sub> | <div align="center"><sub>내용</sub></div> | <sub>소유자</sub> |
|:---:|:---:|:---:|:---|:---:|
| <sub>2026.07.21</sub> | <sub>스킬</sub> | <sub>[dev-reading](skills/dev-reading/README.md)</sub> | <sub>최초 등록 — 신지은 스킬 이관 (jieun994/zinis_claude_skills)</sub> | <sub>신지은</sub> |
|  | <sub>스킬</sub> | <sub>[flowchart-defense](skills/flowchart-defense/README.md)</sub> | <sub>최초 등록 — 신지은 스킬 이관 (jieun994/zinis_claude_skills)</sub> | <sub>신지은</sub> |
|  | <sub>스킬</sub> | <sub>[ia-builder](skills/ia-builder/README.md)</sub> | <sub>플랫폼형 실전 예시(신승 IA v0.01) 레퍼런스 등록·README 전면 개편</sub> | <sub>김단영</sub> |
|  | <sub>스킬</sub> | <sub>[ia-builder](skills/ia-builder/README.md)</sub> | <sub>헤더 양식 가변 지원(layout·labels·depth_min·roles_style) + 골격→컬럼 순차 디벨롭 워크플로</sub> | <sub>김단영</sub> |
|  | <sub>스킬</sub> | <sub>[ia-builder](skills/ia-builder/README.md)</sub> | <sub>최초 등록 — 신지은 스킬 이관 (jieun994/zinis_claude_skills)</sub> | <sub>신지은</sub> |
|  | <sub>스킬</sub> | <sub>[meeting-minutes](skills/meeting-minutes/README.md)</sub> | <sub>최초 등록 — 신지은 스킬 이관 (jieun994/zinis_claude_skills)</sub> | <sub>신지은</sub> |
|  | <sub>스킬</sub> | <sub>[requirements-generator](skills/requirements-generator/README.md)</sub> | <sub>최초 등록 — 신지은 스킬 이관 (jieun994/zinis_claude_skills)</sub> | <sub>신지은</sub> |
|  | <sub>스킬</sub> | <sub>[wbs-generator](skills/wbs-generator/README.md)</sub> | <sub>최초 등록 — 신지은 스킬 이관 (jieun994/zinis_claude_skills)</sub> | <sub>신지은</sub> |
|  | <sub>스킬</sub> | <sub>[weekly-report](skills/weekly-report/README.md)</sub> | <sub>최초 등록 — 신지은 스킬 이관 (jieun994/zinis_claude_skills)</sub> | <sub>신지은</sub> |
| <sub>2026.07.20</sub> | <sub>하네스</sub> | <sub>[screen-spec-id](agent/screen-spec-id/README.md)</sub> | <sub>v0.3 출력 양식 선택 게이트 도입 + samples 양식 2종 추가</sub> | <sub>김단영</sub> |
| <sub>2026.07.16</sub> | <sub>스킬</sub> | <sub>[ui-ux-pro-max-skill](ui-ux-pro-max-skill/README.md)</sub> | <sub>백업 등록 — v2.11.0, README 한국어 번역</sub> | <sub>김단영</sub> |
| <sub>2026.07.15</sub> | <sub>하네스</sub> | <sub>[proposal](agent/proposal/README.md)</sub> | <sub>input 폴더 깃 추적 제외 (기업 민감정보 보호)</sub> | <sub>김단영</sub> |
|  | <sub>하네스</sub> | <sub>[worker](agent/worker/README.md)</sub> | <sub>최초 등록 — 로컬 서브에이전트 worker 백업</sub> | <sub>김단영</sub> |
| <sub>2026.07.13</sub> | <sub>하네스</sub> | <sub>[screen-spec-id](agent/screen-spec-id/README.md)</sub> | <sub>최초 등록 — IA→화면ID 채번→화면명세서 자동생성</sub> | <sub>김단영</sub> |
|  | <sub>스킬</sub> | <sub>[deckslide-design-guideline](skills/deckslide-design-guideline/README.md)</sub> | <sub>최초 등록 — PPT 장표 디자인 지침 스킬</sub> | <sub>김단영</sub> |
| <sub>2026.07.07</sub> | <sub>하네스</sub> | <sub>[prd](agent/prd/README.md)</sub> | <sub>최초 등록 — 공수산정 + 기초 PRD(RRD) 빌더 하네스</sub> | <sub>김단영</sub> |
|  | <sub>하네스</sub> | <sub>[proposal](agent/proposal/README.md)</sub> | <sub>최초 등록 — 제안서 작성 파이프라인 (모노레포 재배치)</sub> | <sub>김단영</sub> |
|  | <sub>스킬</sub> | <sub>[proposal-slide-builder](skills/proposal-slide-builder/README.md)</sub> | <sub>최초 등록 — 모노레포 재구성, 개별 사용 지원</sub> | <sub>김단영</sub> |
|  | <sub>스킬</sub> | <sub>[proposal-structure-validation](skills/proposal-structure-validation/README.md)</sub> | <sub>최초 등록 — 모노레포 재구성, 개별 사용 지원</sub> | <sub>김단영</sub> |
|  | <sub>스킬</sub> | <sub>[rfp-analysis-research](skills/rfp-analysis-research/README.md)</sub> | <sub>최초 등록 — 모노레포 재구성, 개별 사용 지원</sub> | <sub>김단영</sub> |
|  | <sub>스킬</sub> | <sub>[ux-journey-insight](skills/ux-journey-insight/README.md)</sub> | <sub>최초 등록 — 모노레포 재구성, 개별 사용 지원</sub> | <sub>김단영</sub> |

</details>

<details>
<summary><b>2026.06</b> · 70건</summary>

| <sub>일자</sub> | <sub>구분</sub> | <sub>항목</sub> | <div align="center"><sub>내용</sub></div> | <sub>소유자</sub> |
|:---:|:---:|:---:|:---|:---:|
| <sub>2026.06.14</sub> | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>갭 #2(우산 시스템 비기능 전이): RFP가 우리 대상+외부/현행 시스템을 한 우산(무장애/레거시/기간계) 아래 묶으면 → 정체·경계·HA등급 상속·전환경계·I/F무단절 4종을 확인질문 표준 포함. playbook 공통·analyst</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>GS칼텍스 전체테스트 발견 갭 반영: ① 외부사 시스템(VAN·PG·기간계)=연계 I/F만, 시스템 전환개발 금지(architect·analyst·qa(p)⑥) ② corpus.py search 자유어 쿼리+태그 부분매칭(exact→substring, positional/--q)</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>피드백 정정: 자동반영·멀티유저 prefs 제거 → feedback-curator는 "오너용 수정 제안 리포트"만 생성(corpus.py propose→feedback/proposals.md 검토큐). 에이전트 수정은 오너 단독·승인 후 /harness</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>수정 피드백 루프: feedback-curator(opus·on-demand) — 확정된 대화 수정을 취향(user)/공통개선(global) 분류해 corpus.py pref로 기록(prefs/{user}·feedback/agent-improvements). 취향=다음부터 자동, 공통=/harness 반영. 사용자가이드에 흐름 추가</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>최종 HTML 자동 버전관리: corpus.py put-html(생성/수정시 버전 커밋·태그 이동)·get(최신/특정버전 받아보기). save의 index를 update-or-append로(재작업 중복 방지). 다중 사용자 대응</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>기획 과소 가드: 기획 베이스=페이지수+난이도, 디자인 고도화 시 기획 동반 상승. build_report [WARN](agent/harness_st-etribe/기획 실무<디자인×0.5 / 기획1명vs디자인+퍼블4명+). 방법론§9·architect</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>커밋/푸시 포인트 정리: corpus.py save가 섹션 원자별 1커밋(kb(type):id</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>corpus KB 재설계(사내 kb 규약 채택, 우리 산출물 정렬): 섹션 원자 9종(overview·direction·ia·approach·infra·estimates·scope·questions·decisions)+케이스별 종합 cases/(범위→확인→공수 밴드)+patterns 14. corpus.py search 강화(밴드 카드+사슬 ref). 7폴더 9건 적재</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>버전 변천 학습 반영(웅진081·코스모진078 23판 분석): ⑤표현절제(과장네이밍 금지) ⑥불확실시나리오 본산정 분리 ①수치변동 1:1사유+확정도(탐색/제안/확정) ④범위경계 in/out표+기존소스인계 확인. architect·builder·analyst·qa(s)·report-spec§8</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>corpus 참조 가시화·흔적 강제: Phase1.5 corpus 상태 한줄 보고(연결/0건/미연결사유) + analyst "참조 선례" 절·architect measure_note 선례 인용 필수 + 독립성 규칙에서 "corpus=허용된 참조(인용 대상)" 분리 + corpus.py 미연결 사유 명확화</sub> | <sub>—</sub> |
| <sub>2026.06.13</sub> | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>2차 비용 최적화(같은 결과·최소 비용): persona-review=methodology §13·§1.5만 / architect·analyst corpus-kb=검색부분만 / 02_spec.md=짧은요약·02b.md=기본생략 / 중간 스냅샷→GATE+최종 save만</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>콘텐츠 발전도 검토 추가 + 파이프라인 비용 최적화: 발전도(RFP 나열↔고도화)를 3c persona-review estimate에 흡수(신규 opus 0) + qa(r) 얕음 1차탐지 / 3b·5b 조건부화 → 평시 opus 5→3회</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>인테이크 재정의: 고정 필수 5(디자인·개발방법·인프라구축실작업·상주비상주·기간, RFP 무관 항상) + 동적 RFP 질문 ⑥(2-4개 적극 도출). ORCHESTRATOR·CLAUDE·사용자가이드</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>인테이크 질문 ⑥ 가드: 확인 질문은 RFP 내부 미상·모호 항목만, RFP 없는 기능(챗봇·AI) "필요하세요?" 타진 금지. ORCHESTRATOR⑥·CLAUDE§2·playbook</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>섹션 도입 prose 가독성 규칙: 짧은 리드(1-2문장)+구조화(불릿/표), 런온 한 문단 금지. 유지/변경/신규·스펙 나열은 delta 표/불릿으로. builder§9·architect·report-spec§8</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**★ 프로젝트 케이스 매트릭스 + 2축 delta(케이스 커버리지 점검)**: `references/project-cases.md` 신설(A.IA확인불가 / B.프론트만 / C.어드민자료 / D.어드민만[프론트X] / E.리뉴얼 / F.디자인만변경[개발0] / G.화면유지+백엔드신규[개발=신규] / H.신규구축). analyst 착수 시 케이스 판별→01 명시. **delta를 표현(화면)/구현(기능) 2축으로** 분리(F·G 오판 차단). architect/qa(q)/방법론§1.5/report-spec(D) 반영</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**★★ IA delta → 작업 도출 → 공수 추론 사슬(핵심 구조)**: 방법론 §1.5 신설 — 현행 IA를 RFP 대비 유지/변경/신규 분류 → 프론트 변경의 관리자 파생 작업 → 그 분류에서 공수 도출(영역 desc에 "현행X→분류→작업→공수" 근거). analyst(IA delta 태깅·관리자 파생)·architect(공수 delta 도출·"IA 변경 분석" 섹션)·qa(q)·persona-review·report-spec</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**★ RFP 충실성·범위 정확성 강화(실테스트 5결함 교정)**: ① RFP 없는 기능(챗봇) 추가 금지·현행은 "유지"로만 ② 요건 비약 금지(GEO/SEO=콘텐츠·구조 최적화 SW지 색인엔진 인프라 아님) ③ 인프라 구축은 공수 작업 아님(제시만, 영역별 제외) ④ 관리자 IA 기본 골격(로그인·운영자관리·권한·보안/감사) 필수 ⑤ 역할 매트릭스 투입인력 세분(빈 cells 금지). analyst/architect/solution-architect/qa(p)/방법론§11/report-spec</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**★ persona-review 에이전트 신규(멀티 페르소나 검토) + 2지점 삽입**: PM·아키텍트·개발·디자인/퍼블·고객 다관점으로 ① GATE 전(공수·인사이트, `02c`) ② qa 후 최종 전(콘텐츠, `04b`) 검토 → P0면 반려. qa(규칙·정합)와 분리된 '판단·설득력·고객 수용성' 검증</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**IA Front/Admin 분리 표시 + admin 조건부**: admin이 존재하는 사이트면 `Front IA 정보구조도`/`Admin IA 정보구조도` 2섹션 분리(통합+구분행은 폴백). **admin 없는 사이트(정적·소개형)는 Front만** — 억지 유추 금지. 관리자 누락 가드 제거(admin 강제 안 함). analyst·architect·site-ia·report-spec 반영</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**★ TO-BE 인프라 = AS-IS delta(베스트안)**: 일반 모범 구성도 금지 → AS-IS 각 요소를 유지/변경/신규/제거로 분류·근거(RFP·현행) 표기, 현행 필수요소(이중화·환경분리·연계·IDC) 근거없이 제거 금지. 마이그레이션을 delta 표로. solution-architect·infra-diagram 가이드·qa (o)</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**★ 고객 제공 구성도는 원본 그대로(figure kind)**: AS-IS 인프라가 고객 제공 도식이면 `infra`(aws 그리드)로 다시 그리지 말고 **원본 이미지를 `figure`로 임베드**(로컬→base64 인라인, self-contained). solution-architect 지침 + AS-IS/TO-BE 가드 figure 인식</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**★ 자료 > 유추 원칙 + 입력 자료 출처 인벤토리(하네스 진화)**: analyst에 "입력 자료 출처 인벤토리" 절 신설(영역×출처 매핑: 자료제공/부분/없음), report-spec 입력계약 "자료 우선" 행, ORCHESTRATOR Phase1 인벤토리, qa (n) 제공자료 반영 점검(자료를 유추로 표기 시 FAIL), 관리자=유추 편향→케이스 분기</sub> | <sub>—</sub> |
| <sub>2026.06.12</sub> | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**★ diagrams.css 미닫힌 `}` 수정(도식 깨짐 진짜 원인)** + `inline_css.py` 중괄호 균형 가드</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>레이아웃 구조 고정(base_template `.layout/.sidebar`) + builder 인라인 override 금지 + `.pub/.designv` house-style로 이전</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**산정 독립성**: 세션/메모리의 다른 프로젝트·수작업 수치 비교·앵커 금지, 참고원은 corpus KB뿐</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**IA 표 룰(운영 피드백)**: 1노드=1row(·/쉼표 통합 금지·전 대메뉴 동일) + `.effort-table fixed`+colgroup+word-break:keep-all</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**★ 스크립트 결정적 렌더 `build_report.py`(Phase 1-4)**: 구조화 JSON→HTML(레이아웃·IA표 1노드=1행·월별표 합계계산·영역별·간트·핵심요약·CSS·팔레트). 정합·구조·스타일을 코드가 보장</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>렌더 기본경로를 스크립트로 채택(architect→`02_spec.json`→build_report, LLM builder=폴백) + 중간물 **프로젝트별 `_workspace/{slug}/`**</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**build_report 4 렌더러 추가(역할매트릭스·WBS·개념도·인프라)** → 공수 6표 전부 + 도식 2종 결정적 렌더. css_block에 diagrams.css 인라인</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**★ 투입 연속성 가드 `build_report.compute_monthly`**: 톱니(중간월 0.5)·장기 반투입(0.5 2개월+ 연속) 자동 `[WARN]` + member `parttime:true` 예외</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>목차(사이드바) 제목 끝 괄호 부연 자동 제거(`nav_label`) + architect title 규칙(부연은 area로)</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**KB 중간물 스냅샷**: `corpus.py snapshot`(단계/게이트마다 `_workspace/{slug}`→`deliverables/{id}/workspace/` 커밋, index 불변→검색 노이즈0) + `save --ws` + 안정 id 규칙(id=slug={고객}-{주제})·corpus 디렉토리 구조 문서화</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**파일 네이밍 표준 전면 통일**: `_workspace/{slug}/NN[x]_{artifact}`(bare 금지) — 01a_site-ia·01_analysis·02_spec·02b_solution·03_draft·04_qa·05_meta. 레거시명 전부 정리, ORCHESTRATOR에 정본 표 신설, 6에이전트+CLAUDE.md 정렬</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**사용자가이드.html**(Claude Code 대화 흐름 형식: 실제 사용 시나리오 + 안내 캡션) 추가</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**투입 연속성 자동 가드**: `build_report.check_sawtooth`(톱니·0.5 2개월+ 연속 → [WARN]) + 방법론§9·architect·qa(l). 정당 파트타임은 member `parttime:true` 예외</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**인테이크 항목 추가: 수행형태(상주/비상주)·예상 인프라 포함**. 비상주→퍼블·개발 -최대30%(AI활용, 기획/디자인 제외), 상주→감면없음+상주 인력 장기0.5 금지(parttime 예외 불가). 미응답 시 상주 가정</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**QA 인력 = 기획자 겸임(표준)**: QA 전담 직군 금지, 기획 1명 막달(통합테스트·UAT·오픈)까지 유지. build_report 가드(QA 전담 직군·기획 막달0 → [WARN])</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**테스트 구간 인력 감쇠(§9)**: 막달은 신규 제작 없음 → 디자인·퍼블 2명+ 투입 시 1명만 잔류(PM·기획·개발은 풀 가능, 디자인 위주면 개발도 감원). build_report 가드(막달 디자인/퍼블 2명+ → [WARN])</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**IA 압축 자동 가드**: build_report가 children 없는 대메뉴 desc에 ·가 2개+면 [WARN](agent/harness_st-etribe/하위를 한 셀에 압축). architect IA는 하위를 반드시 `children[]`로 분해 명시</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**root 오염 정리**: `.playwright-mcp/`·루트 캡처 이미지(`/*.png\|jpg\|jpeg`) `.gitignore` 차단 + site-analyst §9 캡처를 `_workspace/{slug}/` 저장 지침. 기존 루트 캡처는 `input/`로 이동</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**사용자가이드.html 보강**: 인테이크 질문(디자인·일정·상주/비상주·인프라 포함) 대화 추가, 비상주 -감면·인프라 포함 흐름 반영</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**관리자 IA 유추 강제**: IA group `admin:true` 플래그 + build_report 구분행("관리자 영역·유추·추정") + 누락 가드([WARN]). analyst 관리자 유추 필수 격상(표준 어드민 세트), architect IA=사용자+관리자 둘 다</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>목차 '공수 산정 —' 묶음 접두 자동 제거(nav_label) + 하위표 title 표이름만·번호 8-1~8-6</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**인테이크 순차 질문화**: 작성 시작 시 필요 항목을 한꺼번에 안 묻고 **하나씩** 질문→답→진행(디자인→일정→상주/비상주→인프라→TO-BE→누락). 한꺼번에 답하면 수용</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**AS-IS 인프라 이미지 판독 + TO-BE 제안**: `extract_assets.py`(docx/pptx 임베드 이미지 추출) + analyst 판독 지침 + solution-architect AS-IS(Read 판독)→TO-BE 2섹션+마이그레이션. GS칼텍스 RFP 구성도 2종 판독 실증</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>IA 표 공수 컬럼 조건부: effort가 하나도 없으면(메뉴구조도) "공수(M/M)" 컬럼 자동 생략(3컬럼)</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**서술형 섹션 6종 전용 템플릿 + 번호 자동화**: build_report에 overview(메뉴칩)·modules(menu-list)·narrative(다크 final-report)·questions(확인질문)·coverage(요건표)·insight 렌더러 추가(cards=기존 summary 재사용). `no` 미지정 시 순번 자동. 기존 산출물 8종 클래스 패턴 실증→전용화. 신규 6종 렌더·발명클래스0·Playwright 런타임(menu-grid/list·final-report 다크·effort-grid·insight·번호 1-5) GREEN</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>측정 철학 정정: IA=페이지(기능) 단위, "스타일 N"은 한 페이지 내 표시 변형일 때만(상품 56개=상품상세 1페이지·스타일은 디자인 산정에)</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**RFP 커버리지 + 확인 질문 + 인프라 AS-IS 동반**: analyst RFP 요건 전수 항목화 → architect 요건 커버리지 대조표(반영/부분/제외+사유/미확인) + "확인 필요 질문" 항상 마지막 섹션(추정·데이터갭 중립 질문) / 인프라 제안(TO-BE)은 AS-IS와 쌍. build_report 가드(확인질문 누락·TO-BE 단독 → [WARN]), qa (l)+(m) 점검</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**출력 위치 가드 + 전체경로 강제**: build_report `-o`가 `_workspace/`·`output/` 밖(temp·홈)이면 [WARN]. ORCHESTRATOR 명령 예시를 전체경로(`_workspace/{slug}/...`)로, temp/cwd 금지 규칙. qa (l)을 'build_report 모든 WARN 0'으로 일반화(IA압축·관리자누락·인력정책·출력위치 무시 금지)</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>IA 표 공수 컬럼 조건부 생략(effort 전무 시) + 관리자 출처 라벨 `admin_label`(자료 기반/유추)</sub> | <sub>—</sub> |
| <sub>2026.06.11</sub> | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>초기 구성(에이전트4·레퍼런스5·템플릿3)</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>도식화 범위 추가(개념도+AWS 인프라)</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>`effort-estimation-methodology.md` 추가(레퍼런스6) + architect 연결</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>시운전(서울대 SDN) 4단계 완주 + qa가 phantom +4.0(29.0/33.0 불일치) 적발</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>CSS 스크립트 주입(`scripts/inline_css.py`) + base_template 마커화 + builder.md "CSS 직접작성 금지·도식 기본포함"</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>`report-spec.md` 추가(생성 규칙 정본: 입력계약·6표·정합 a-h·4변형) + consistency-checklist를 a-h로 교체 + architect 자기검증</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>워크스페이스 루트 `CLAUDE.md`에 하네스 트리거 규칙 등록(요건문서→파이프라인, 콜드메뉴 금지)</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**배포 패키징**: 루트 `CLAUDE.md`(현관문) + `input/`·`output/`·`.gitignore` + 상대경로 이식성 확인</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>`examples/` few-shot 라이브러리 추가(과거 완성본 4종 + INDEX)</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**corpus 집단기억** 추가(`corpus/`·`scripts/corpus.py`·`.env`) — 산출물 누적, 유사 선례 검색-증강, qa PASS 시 자동 push</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>GitLab 배포: code.etribe.co.kr/smart-technology/harness_st. **브랜치 2개 — `etribe`(도구 코드, clone 대상) / `corpus`(데이터, orphan)**. main은 protected(미사용)</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>builder "클래스 발명 금지" 규칙 + `scripts/check_classes.py` orphan-class 가드(qa (i))</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**corpus를 별도 `corpus` 브랜치로 분리**(etribe=코드/corpus=데이터). corpus.py가 gitignored `.corpus/`에 클론·commit·push</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**IA 추출 고도화**: `scripts/ia_extract.py`(메가패널 정본·탭/그룹/외부 type·page/view 이중카운트·footer·로그인·경계bleed 섹션비율 dedup) + `ia-extraction-upgrade.md`(오류7·규칙·스키마) + site-ia-extraction/analyst/methodology/report-spec 연결</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>KB 방법론 이식(독립): playbook 2종(요건누락·공수5축검증) + corpus 피드백 루프(`corpus.py feedback`, 실제공수→과소산정 경고) + frontmatter 스키마·confidence/데이터갭</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>인테이크(정성 신호: 기획염려·디자인레벨→공수 가중) + 모델 티어링(builder·qa→sonnet) + solution-architect 분리해 architect와 병렬</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>analyst 분리(site-analyst sonnet, 사이트 IA 병렬) + 에이전트별 ref 화이트리스트</sub> | <sub>—</sub> |
|  | <sub>하네스</sub> | <sub>[harness_st-etribe](agent/harness_st-etribe/README.md)</sub> | <sub>**v1.1 시운전(아너파라다이스) GREEN** + 잠복결함 수정: `check_consistency.py`를 SDN하드코딩→**실제 표 파싱 범용**으로 재작성 · `check_classes.py` `<script>`제외(JS 거짓양성) · base_template `.hero-grid` · diagrams.css `.pub/.designv` 보강</sub> | <sub>—</sub> |

</details>

<!-- RELEASE-NOTES:END -->

## 관리자용

원본 → 공유 리포 반영: `bash share/mirror-from-source.sh` — 관리자 PC 작업 스케줄러 `dykim-share-mirror`가 **매주 금요일 24시(토 00:00)** 자동 실행하고 커밋 · 푸시까지 끝낸다(PC가 꺼져 있었으면 켜진 직후 실행). 받는 쪽 주간 업데이트(월 09:00)는 그 뒤에 돈다. 원본 `origin/main`에 푸시된 내용만 옮기고, 전역 규칙에서 Dan Jr. 조항을 뺀다. 제외 목록은 스크립트 머리의 `EXCLUDE`.
위 릴리즈노트는 미러할 때마다 `share/build-release-notes.sh`가 원본 각 폴더 README의 릴리즈노트에서 다시 만든다 — 내용을 고치려면 원본 쪽 README의 릴리즈노트를 고친다.

| <sub>공유 리포 운영 이력</sub> | <sub>일자</sub> |
|:---|:---:|
| <sub>원본 반영 주기 변경 — 매일 08:30 → 매주 금요일 24시(토 00:00)</sub> | <sub>2026.11.11</sub> |
| <sub>리포 이름 변경 — `dykim-claude-agents-skills-share` → `Share-Agent-Skill-dy` (예전 주소는 GitHub 이 자동 연결)</sub> | <sub>2026.11.11</sub> |
| <sub>릴리즈노트 자동 생성 추가 — 일자별 업데이트 항목 · 월별 상세 · 공통 반영 사항</sub> | <sub>2026.11.11</sub> |
| <sub>공유 리포 개설 — 원본 1:1 미러(단이bot · Dan Jr. · 페르소나 · 메모리 제외), 받는 쪽 주간 업데이트</sub> | <sub>2026.11.11</sub> |
