# skills — 개별 사용 가능한 스킬 정본

이 폴더의 각 스킬은 **단독으로도 쓸 수 있는 정본**이다. 원하는 스킬 폴더 하나만 자신의 스킬 경로로 복사하면 된다. (상위 [README.md](../README.md) "B. 스킬을 개별로 쓰기"와 동일.)

## 설치 (개별)

- **사용자 전역**(모든 프로젝트에서 사용): `<스킬명>/` → `~/.claude/skills/<스킬명>/`
- **특정 프로젝트에서만**: `<스킬명>/` → `<프로젝트>/.claude/skills/<스킬명>/`

PowerShell:
```powershell
Copy-Item -Recurse rfp-analysis-research "$HOME/.claude/skills/rfp-analysis-research"
```

bash:
```bash
cp -r rfp-analysis-research ~/.claude/skills/rfp-analysis-research
```

복사 후 Claude Code에서 해당 스킬이 인식된다(트리거는 각 `SKILL.md` 상단 `description` 참고).

## 스킬 목록

### 제안서 파이프라인·디자인 — 제작: dykim

| <div align="center"><sub>스킬</sub></div> | <sub>용도</sub> | <sub>파이프라인 단계</sub> |
|:---|:---:|:---:|
| <sub>[`rfp-analysis-research`](rfp-analysis-research/SKILL.md)</sub> | <sub>RFP/RFI 파싱 → 요구사항 구조화 + 산업·경쟁사·기술 리서치</sub> | <sub>1</sub> |
| <sub>[`ux-journey-insight`](ux-journey-insight/SKILL.md)</sub> | <sub>사용자 여정맵 + 개선 포인트·UI/UX 전략 도출</sub> | <sub>2</sub> |
| <sub>[`proposal-structure-validation`](proposal-structure-validation/SKILL.md)</sub> | <sub>RFP·UX 종합 → 제안서 목차 구성 + 최종 자기검증</sub> | <sub>3</sub> |
| <sub>[`proposal-slide-builder`](proposal-slide-builder/SKILL.md)</sub> | <sub>본문 슬라이드 생성 (콘텐츠 초안 → HTML → PPT/Figma)</sub> | <sub>4</sub> |
| <sub>[`deckslide-design-guideline`](deckslide-design-guideline/SKILL.md)</sub> | <sub>PPT 장표 규격·레이아웃·디자인 스타일 표준 적용 (블랙 헤더 + 라운드 카드 + 포인트 컬러, pptxgenjs)</sub> | <sub>독립</sub> |

### 세션 운영 — 제작: dykim

| <div align="center"><sub>스킬</sub></div> | <sub>용도</sub> |
|:---|:---:|
| <sub>[`handoff`](handoff/SKILL.md)</sub> | <sub>`/clear` 전에 현재 세션 맥락을 `.claude/HANDOFF.md` 로 저장 → 다음 세션이 이어받기 (SessionStart 훅과 함께 사용)</sub> |

### 협업 · 알림 — 제작: dykim

| <div align="center"><sub>스킬</sub></div> | <sub>용도</sub> |
|:---|:---:|
| <sub>[`Slack-Bot`](Slack-Bot/SKILL.md)</sub> | <sub>슬랙 봇 만들기 — 채널 자동 게시(Incoming Webhook) · @멘션 질문에 정해 둔 자료로 스레드 답변(Socket Mode + Claude), 6단계 진행 · 비밀값 저장 · 자동 시작 등록 (호출 이름 `slack-bot`)</sub> |

### 기획 실무 스킬 — 제작: 신지은

출처: [jieun994/zinis_claude_skills](https://github.com/jieun994/zinis_claude_skills) — **제작자 신지은**([@jieun994](https://github.com/jieun994)). 모두 독립 스킬이다.

| <div align="center"><sub>스킬</sub></div> | <sub>용도</sub> |
|:---|:---:|
| <sub>[`dev-reading`](dev-reading/SKILL.md)</sub> | <sub>개발자료(API 명세·DB 스키마/ERD·기술문서)를 비개발 기획자 눈높이로 해설 + 확인·질문 포인트 도출</sub> |
| <sub>[`flowchart-defense`](flowchart-defense/SKILL.md)</sub> | <sub>고객 전달 플로우차트 검토 → 누락된 예외·빈결과·취소·막다른 길 방어설계 보강</sub> |
| <sub>[`ia-builder`](ia-builder/SKILL.md)</sub> | <sub>서비스 메뉴·뎁스 구조(사이트맵/IA)·기능정의서 엑셀 생성</sub> |
| <sub>[`meeting-minutes`](meeting-minutes/SKILL.md)</sub> | <sub>녹취록·메모·회의자료 → 표준 엑셀 회의록(개요/내용/TO-DO/이슈)</sub> |
| <sub>[`qa-master`](qa-master/SKILL.md)</sub> | <sub>ISTQB(CTFL·CTAL·CTEL) 기반 테스트케이스·시나리오 엑셀 생성 + 기획서 QA 검토 + 테스트 계획 수립</sub> |
| <sub>[`requirements-generator`](requirements-generator/SKILL.md)</sub> | <sub>회의록·RFP·IA 엑셀 → 요구사항 정의서(.xlsx) 생성</sub> |
| <sub>[`wbs-generator`](wbs-generator/SKILL.md)</sub> | <sub>WBS 엑셀 생성 (L1~L3 작업 계층·일정·담당자·진척률·간트)</sub> |
| <sub>[`weekly-report`](weekly-report/SKILL.md)</sub> | <sub>주간업무 보고서(PPT) 자동 작성 (W1/W2 선택, 진척률 6칸 자동 계산)</sub> |

### 외부 스킬 백업

| <div align="center"><sub>스킬</sub></div> | <sub>용도</sub> | <sub>출처</sub> |
|:---|:---:|:---:|
| <sub>[`eli5`](eli5/SKILL.md)</sub> | <sub>어떤 주제든 그림 위주·적은 텍스트의 HTML 아티팩트로 쉽게 설명 (`/eli5 <주제>`)</sub> | <sub>[anthropics/claude-plugins-community](https://github.com/anthropics/claude-plugins-community/blob/main/eli5/skills/eli5/SKILL.md)</sub> |

## 에이전트와 함께 쓸 때

전체 제안서 파이프라인으로 쓰려면 개별 복사 대신 리포 루트에서 `sync-skills` 스크립트를 돌려 `agent/.claude/skills/`로 한 번에 복사한다. 상위 [README.md](../README.md) "A. 에이전트로 쓰기" 참고.

> **정본은 이 폴더다.** 스킬 내용을 고칠 때는 여기(`skills/`)만 수정하고, 에이전트용 사본은 `sync-skills`로 다시 생성한다.
