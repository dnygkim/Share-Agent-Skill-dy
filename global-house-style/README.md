# Global House Style (모든 HTML 산출물의 기본 스타일)

## 릴리즈노트

| <div align="center"><sub>요약내용</sub><img width="1" height="1"></div> | <sub>업데이트 일자</sub><img width="1" height="1"> | <sub>소유자</sub><img width="45" height="1"> |
|:---|:---:|:---:|
| <sub>외부링크 아이콘을 블랙 라인(투명도 제거)으로 변경하고, 본문 고유명사(사이트 · 서비스 · 기관 · 도구)도 같은 `a.ext`로 연결하는 규칙을 `house-style.css` §22에 명시 — 2026.11.10 지시, `~/.claude/house-style/` 사본과 동일 유지</sub> | <sub>2026.11.10</sub> | <sub>김단영</sub> |
| <sub>전역 규칙 3종 동기화 — 산출물 파일명 원문 대조 보강(단계코드 · 문서번호 · 확정본 보존 · 개정이력 · 적용 제외)·자동화 창은 서브모니터로·HTML 산출물 수정 이력 메타정보(모두 2026.10.28 지시). Windows PC `~/.claude/CLAUDE.md` 기준 반영 — Dan Jr. 절의 리포 전용 문구(전역 규칙 없는 환경 · 클라우드 세션 안내) 유지</sub> | <sub>2026.11.06</sub> | <sub>김단영</sub> |
| <sub>출처 외부링크 규칙 추가 — 리서치·분석 문서는 출처 URL을 항목 타이틀(1건)·해당 구절(2건 이상)에 직접 연결. `house-style.css` §22 `a.ext`(옅은 밑줄 · 끝 외부링크 아이콘 · hover 반전 · 인쇄 시 아이콘 숨김) · `.src-tag`, `base_template_doc.html` 팔레트 · 출처 표 예시, 전역 규칙 「출처 외부링크」 절 — 메리츠화재 RFP 분석 보고서에서 확정</sub> | <sub>2026.10.19</sub> | <sub>김단영</sub> |
| <sub>전역 규칙 3종 동기화 — 거버닝 메시지 문체(2026.09.11)·어절 단위 줄바꿈(2026.09.17)·산출물 파일명 두 트랙(2026.10.01). `house-style.css` §3 `word-break:keep-all`·제목 `text-wrap:balance` 반영 — 8/27 이후 `~/.claude/` 에만 있던 변경분</sub> | <sub>2026.10.09</sub> | <sub>김단영</sub> |
| <sub>확인 생략 시 폴백 명문화 — 스타일 확인 질문 없이 진행되면(무응답·일괄 진행·비대화형) 하네스/스킬에 정의된 기본 양식으로 작성, 임의 스타일·보류 금지</sub> | <sub>2026.08.27</sub> | <sub>김단영</sub> |
| <sub>HTML 기본 스타일 전면 통일 — `agent/proposal`(슬라이드형)·`agent/prd`(문서형)·`proposal-slide-builder` 가 이 정본을 공유. 자체 팔레트(CI 5색·`--brand` 대시보드) 은퇴 · CI 옵트인 · 하네스는 추출 전 기본 스타일 확인</sub> | <sub>2026.08.27</sub> | <sub>김단영</sub> |
| <sub>LNB 상단 정렬(`margin-top:0`)·앵커 목적지 보정(`[id]{scroll-margin-top}`)·목차 `#s0` 목적지 신설 — KOMCA RFI 분석서에서 손으로 덧댄 보정을 정본으로 흡수</sub> | <sub>2026.08.27</sub> | <sub>김단영</sub> |
| <sub>최초 등록 — `~/.claude/house-style/` + `~/.claude/CLAUDE.md`의 Git 백업/정본</sub> | <sub>2026.08.20</sub> | <sub>김단영</sub> |

## 무엇인가

**별도 요청이 없으면 HTML 산출물은 전부 이 스타일로 뽑는다**(2026-08-27 통일). 일반 대화든,
에이전트 하네스(`agent/proposal`·`agent/prd`)든, 스킬이든 같은 정본을 쓴다.

- **실제로 적용되는 위치는 이 리포가 아니라 `~/.claude/`**다 — `~/.claude/house-style/house-style.css`,
  `~/.claude/house-style/base_template_doc.html`, `~/.claude/CLAUDE.md`(전역 규칙 파일).
- 이 폴더(`global-house-style/`)는 그 세 파일의 **사본**을 버전관리하기 위한 것이다. Claude Code가 이
  폴더 자체를 열어서 동작을 트리거하는 하네스가 아니다.
- 기준본: `신승-비즈니스AI플래너_권한정책매트릭스_초안(260810).html` (warm paper + near-black ink,
  Pretendard/Paperlogy, 토프바+LNB+표지+목차+섹션+footer 구조, A4 인쇄 대응).

**골격은 둘, 정본은 하나**

| 골격 | 파일 | 쓰는 곳 |
|---|---|---|
| 문서형 (롱스크롤 + A4) | `base_template_doc.html` | 일반 대화 리포트 · `agent/prd` PRD |
| 슬라이드형 (1280×720) | `../agent/proposal/template/base_template.html` | `agent/proposal` · `skills/proposal-slide-builder` |

슬라이드형은 정본의 §1 서체·§2 토큰만 복제하고(`../agent/proposal/template/slide-tokens.css`)
슬라이드 전용 규칙은 자기 `<style>`에 둔다. **값을 바꿀 곳은 언제나 정본 `house-style.css` 하나다.**

## 구성

```
global-house-style/
├── CLAUDE.md               전역 규칙 — ~/.claude/CLAUDE.md 와 동일 내용
├── house-style.css         스타일 정본 (§1~19 공통 컴포넌트 + §20~22 확장: 요약 스탯·간트·출처 외부링크)
├── base_template_doc.html  문서형 골격 + "콘텐츠 컴포넌트 팔레트" 주석
└── README.md               이 파일
```

**설계 원칙**: GNB(토프바)·LNB·표지·목차·footer는 골격·스타일 그대로 **고정**한다. 콘텐츠 영역(섹션 본문)은
고정하지 않는다 — `base_template_doc.html` 안 "콘텐츠 컴포넌트 팔레트" 주석 아래의 표·요약 스탯·플로우·
루프·트리·mermaid·진단박스·노트·등급목록 중 **추출한 내용의 성격에 맞는 것만** 골라 조합한다. 팔레트를
통째로 나열하지 않는다 — 섹션마다 쓰는 조합이 달라도 된다.

## 설치 (신규 머신 / 재설정 시)

리포 루트에서 `bash install-global.sh` 를 실행하면 아래 두 단계와 스킬 복사가 한 번에 된다(Windows 는 Git Bash).
손으로 할 때는 다음 순서다.

1. `house-style.css`, `base_template_doc.html`을 `~/.claude/house-style/`에 복사한다.
2. `CLAUDE.md`의 내용을 `~/.claude/CLAUDE.md`에 반영한다 — 그 파일이 없으면 그대로 복사, 있으면 이
   섹션을 병합한다(전역 파일에는 이 하우스 스타일 규칙 외에 다른 개인 규칙이 나중에 추가될 수 있다).

## 동기화 규칙

`~/.claude/house-style/*`나 `~/.claude/CLAUDE.md`의 하우스 스타일 규칙을 고치면, **이 폴더에도 같은
내용을 반영하고 Git에 커밋**한다 — 로컬만 고치고 여기를 그대로 두면 백업이 stale 해진다.

## 하네스·스킬과의 관계 — 같은 정본을 쓴다

2026-08-27 부터 `agent/proposal`·`agent/prd`·`skills/proposal-slide-builder` 가 모두 이 정본을 쓴다.
각 하네스가 갖고 있던 자체 팔레트(제안서 CI 5색 · PRD `--brand` 그라데이션 대시보드)는 은퇴했고,
**클라이언트 CI 는 옵트인**으로 바뀌었다 — 사용자가 명시적으로 요청했을 때만 §2b 오버라이드로 얹는다.
하네스·스킬 세션은 HTML 추출 직전 인테이크에서 **「기본 스타일로 추출할까요?」를 한 번 확인받은 뒤
추출한다**(일반 대화는 확인 없이 기본 적용). **확인 질문 없이 진행되는 경우에도 임의 스타일로 뽑거나
보류하지 않는다** — 그 하네스/스킬에 정의된 기본 양식(= 이 정본의 골격·토큰)으로 작성한다.

| 대상 | 골격 | 스타일 규약 위치 |
|---|---|---|
| 일반 대화 | 문서형 | `~/.claude/CLAUDE.md` |
| `agent/prd` | 문서형 | `agent/prd/references/master-prompt-v2.0.md` [HTML 산출물 사양] · `CLAUDE.md` §4⑥ |
| `agent/proposal` | 슬라이드형 | `agent/proposal/references/design-system.md` §2 · `CLAUDE.md` §2③ |
| `skills/proposal-slide-builder` | 슬라이드형 | `SKILL.md` 3 · `references/design-system.md` §2 |

**HTML 이 아닌 산출물은 대상이 아니다** — pptx(`deckslide-design-guideline`·`weekly-report`)·
xlsx(`wbs-generator`·`requirements-generator`·`meeting-minutes`·`ia-builder`)·docx 는 각자 규격을 따른다.
