# skills — 스킬 정본

한 가지 일을 끝내는 단독 도구 모음. 스킬 폴더 하나를 `~/.claude/skills/`에 복사하면 어느 프로젝트에서든 요청 문장 한 줄로 호출

## 한눈에 보기

| <div align="center"><sub>항목</sub></div> | <sub>내용</sub> |
|:---|:---:|
| <sub>**스킬이란**</sub> | <sub>`SKILL.md`(동작 정의 · 트리거 문장) + 참고 자료 · 스크립트 · 템플릿을 담은 폴더. 요청 문장이 `SKILL.md` 상단 `description`의 트리거와 맞으면 Claude가 자동 호출</sub> |
| <sub>**부르는 법**</sub> | <sub>요청 문장(예 `회의록 작성해줘`) 또는 슬래시 명령(예 `/handoff` · `/eli5 <주제>`) — 스킬 이름을 말하지 않아도 동작</sub> |
| <sub>**설치 위치**</sub> | <sub>전역 `~/.claude/skills/<스킬명>/` · 특정 프로젝트만 `<프로젝트>/.claude/skills/<스킬명>/`</sub> |
| <sub>**하네스와의 관계**</sub> | <sub>하네스(`agent/`)는 스킬 여러 개를 단계별로 묶은 파이프라인 — 하네스용 사본은 리포 루트 `sync-skills`로 생성</sub> |
| <sub>**사용 설명서**</sub> | <sub>스킬 폴더마다 `README.md` — 목적 · 요청 예시 · 진행 단계 · 산출물 · 설치 · 릴리즈노트</sub> |

## 스킬 목록

### 제안서 파이프라인 · 디자인 — 제작: dykim

제안 1~4단계는 [`agent/proposal`](../agent/proposal/) 하네스가 단계별로 자동 호출, 단독 호출도 가능

| <div align="center"><sub>스킬</sub></div> | <sub>용도</sub> | <sub>이렇게 요청</sub> |
|:---|:---:|:---:|
| <sub>[`rfp-analysis-research`](rfp-analysis-research/README.md)</sub> | <sub>제안 1단계 — RFP/RFI 파싱 → 요구사항 구조화 + 산업·경쟁사·기술 리서치</sub> | <sub>`이 RFP 분석하고 경쟁사 리서치해줘`</sub> |
| <sub>[`ux-journey-insight`](ux-journey-insight/README.md)</sub> | <sub>제안 2단계 — 사용자 여정맵 + 개선 포인트·UI/UX 전략 도출</sub> | <sub>`이 서비스 사용자 여정맵 그려줘`</sub> |
| <sub>[`proposal-structure-validation`](proposal-structure-validation/README.md)</sub> | <sub>제안 3단계 — RFP·UX 종합 → 제안서 목차 구성 + 최종 자기검증</sub> | <sub>`제안서 목차 구성하고 검증해줘`</sub> |
| <sub>[`proposal-slide-builder`](proposal-slide-builder/README.md)</sub> | <sub>제안 4단계 — 본문 슬라이드 생성 (콘텐츠 초안 → HTML → PPT/Figma)</sub> | <sub>`SECTION 3 작성해줘` · `제안서를 PPT로 만들어줘`</sub> |
| <sub>[`deckslide-design-guideline`](deckslide-design-guideline/README.md)</sub> | <sub>PPT 장표 규격·레이아웃·디자인 스타일 표준 적용 (블랙 헤더 + 라운드 카드 + 포인트 컬러, pptxgenjs)</sub> | <sub>`PPT 디자인 지침 적용해줘` · `장표 디자인 통일해줘`</sub> |

### 세션 운영 — 제작: dykim

| <div align="center"><sub>스킬</sub></div> | <sub>용도</sub> | <sub>이렇게 요청</sub> |
|:---|:---:|:---:|
| <sub>[`handoff`](handoff/README.md)</sub> | <sub>`/clear` 전에 현재 세션 맥락을 `.claude/HANDOFF.md` 로 저장 → 다음 세션이 이어받기 (SessionStart 훅과 함께 사용)</sub> | <sub>`/handoff` · `핸드오프 저장해줘`</sub> |

### 협업 · 알림 — 제작: dykim

| <div align="center"><sub>스킬</sub></div> | <sub>용도</sub> | <sub>이렇게 요청</sub> |
|:---|:---:|:---:|
| <sub>[`Slack-Bot`](Slack-Bot/README.md)</sub> | <sub>슬랙 봇 만들기 — 채널 자동 게시(Incoming Webhook) · @멘션 질문에 정해 둔 자료로 스레드 답변(Socket Mode + Claude), 6단계 진행 · 비밀값 저장 · 자동 시작 등록 (호출 이름 `slack-bot`)</sub> | <sub>`슬랙 봇 만들어줘` · `봇 멘션하면 답하게 해줘`</sub> |

### 기획 실무 스킬 — 제작: 신지은

출처 [jieun994/zinis_claude_skills](https://github.com/jieun994/zinis_claude_skills) · **제작자 신지은**([@jieun994](https://github.com/jieun994)) · 모두 독립 스킬

| <div align="center"><sub>스킬</sub></div> | <sub>용도</sub> | <sub>이렇게 요청</sub> |
|:---|:---:|:---:|
| <sub>[`dev-reading`](dev-reading/README.md)</sub> | <sub>개발자료(API 명세·DB 스키마/ERD·기술문서)를 비개발 기획자 눈높이로 해설 + 확인·질문 포인트 도출</sub> | <sub>`이 API 명세 풀어줘` · `ERD 해석해줘`</sub> |
| <sub>[`flowchart-defense`](flowchart-defense/README.md)</sub> | <sub>고객 전달 플로우차트 검토 → 누락된 예외·빈결과·취소·막다른 길 방어설계 보강</sub> | <sub>`이 챗봇 흐름도 검토해줘`</sub> |
| <sub>[`ia-builder`](ia-builder/README.md)</sub> | <sub>서비스 메뉴·뎁스 구조(사이트맵/IA)·기능정의서 엑셀 생성</sub> | <sub>`IA 만들어줘` · `사이트맵 만들어줘`</sub> |
| <sub>[`meeting-minutes`](meeting-minutes/README.md)</sub> | <sub>녹취록·메모·회의자료 → 표준 엑셀 회의록(개요/내용/TO-DO/이슈)</sub> | <sub>`이 녹취록 회의록으로 정리해줘`</sub> |
| <sub>[`qa-master`](qa-master/README.md)</sub> | <sub>ISTQB(CTFL·CTAL·CTEL) 기반 테스트케이스·시나리오 엑셀 생성 + 기획서 QA 검토 + 테스트 계획 수립</sub> | <sub>`테스트케이스 만들어줘` · `이 기획서 QA해줘`</sub> |
| <sub>[`requirements-generator`](requirements-generator/README.md)</sub> | <sub>회의록·RFP·IA 엑셀 → 요구사항 정의서(.xlsx) 생성</sub> | <sub>`이 회의록으로 요구사항 정의서 뽑아줘`</sub> |
| <sub>[`wbs-generator`](wbs-generator/README.md)</sub> | <sub>WBS 엑셀 생성 (L1~L3 작업 계층·일정·담당자·진척률·간트)</sub> | <sub>`이 프로젝트 WBS 짜줘`</sub> |
| <sub>[`weekly-report`](weekly-report/README.md)</sub> | <sub>주간업무 보고서(PPT) 자동 작성 (W1/W2 선택, 진척률 6칸 자동 계산)</sub> | <sub>`이번주 주간보고 작성해줘`</sub> |

### 외부 스킬 백업

출처 [anthropics/claude-plugins-community](https://github.com/anthropics/claude-plugins-community/blob/main/eli5/skills/eli5/SKILL.md) · 원본 그대로 보관

| <div align="center"><sub>스킬</sub></div> | <sub>용도</sub> | <sub>이렇게 요청</sub> |
|:---|:---:|:---:|
| <sub>[`eli5`](eli5/README.md)</sub> | <sub>어떤 주제든 그림 위주·적은 텍스트의 HTML 아티팩트로 쉽게 설명 (`/eli5 <주제>`)</sub> | <sub>`/eli5 DNS가 뭐야`</sub> |

## 설치 (개별)

- **사용자 전역**(모든 프로젝트): `<스킬명>/` → `~/.claude/skills/<스킬명>/`
- **특정 프로젝트만**: `<스킬명>/` → `<프로젝트>/.claude/skills/<스킬명>/`

```bash
# bash · Git Bash
cp -r rfp-analysis-research ~/.claude/skills/rfp-analysis-research
```

```powershell
# PowerShell
Copy-Item -Recurse rfp-analysis-research "$HOME/.claude/skills/rfp-analysis-research"
```

- 복사 후 새로 여는 Claude Code 세션부터 인식 — 트리거 문장은 각 `SKILL.md` 상단 `description`
- 전체를 한 번에: 원본 리포는 루트 `bash install-global.sh`, 공유 리포는 `bash share/update.sh`
- Python · Node 등 의존성이 있는 스킬은 각 README 「설치 · 단독 사용」 절에 표기

## 하네스와 함께 쓸 때

- 하네스 파이프라인 안에서 쓰려면 개별 복사 대신 리포 루트에서 `bash ./sync-skills.sh`(PowerShell `./sync-skills.ps1`) 실행 → `agent/<이름>/.claude/skills/`로 일괄 복사
- 현재 사본 대상 하네스: `proposal` · `feature-spec-sb` · `test-runner`

## 수정 규칙

- **정본은 이 폴더** — 스킬 내용은 여기(`skills/`)만 수정, 하네스용 사본은 `sync-skills`로 재생성
- 새 스킬 추가: `<스킬명>/SKILL.md` + `README.md` → 위 「스킬 목록」 해당 절에 행 추가(첫 열 링크 · 용도 · 이렇게 요청) → 리포 루트 `README.md` 표에도 추가
- 위 표는 공유 리포 README 「들어 있는 것」 스킬 표의 원천 — `### … 제작: 이름` 소제목 · 표 열 순서 유지
