# dykim-claude-agents-skills-share

김단영(dykim)의 Claude Code **스킬**과 **에이전트 하네스**를 받아 쓰는 공유용 리포.
원본 리포 `dykim-claude-agents-skills`에서 개인 전용 항목만 뺀 나머지가 1:1로 들어 있고, 원본이 바뀌면 이 리포도 같이 바뀐다.

- **이 리포는 받기 전용** — 여기서 고친 내용은 다음 업데이트 때 원본 내용으로 되돌아간다. 고칠 점은 관리자에게 전달
- **빠진 것**: 단이bot(`agent/danibot`) · Dan Jr. 스킬(`skills/danjr`) · 페르소나(`persona`) · 개인 메모리 · PC 동기화 스크립트

## 처음 설치 (1회)

준비물: Git, Claude Code. Windows는 [Git for Windows](https://git-scm.com/download/win)에 포함된 **Git Bash**에서 실행한다(PowerShell의 `bash`는 WSL일 수 있어 쓰지 않는다).

```bash
# 1) 받기 — 처음 한 번 GitHub 로그인 창이 뜬다
cd ~/Documents
git clone https://github.com/dnygkim/dykim-claude-agents-skills-share.git
cd dykim-claude-agents-skills-share

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

## 관리자용

원본 → 공유 리포 반영: `bash share/mirror-from-source.sh` (관리자 PC에서 자동 실행). 원본 `origin/main`에 푸시된 내용만 옮기고, 전역 규칙에서 Dan Jr. 조항을 뺀다. 제외 목록은 스크립트 머리의 `EXCLUDE`.
