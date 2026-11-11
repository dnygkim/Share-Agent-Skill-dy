# PRD Builder Harness (agent/prd)

## 릴리즈노트

| <div align="center"><sub>요약내용</sub><img width="1" height="1"></div> | <sub>업데이트 일자</sub><img width="1" height="1"> | <sub>소유자</sub><img width="45" height="1"> |
|:---|:---:|:---:|
| <sub>Dan Jr. 등급 조회 추가 — 인테이크·GATE 직전 `persona.md` 확인(A 진행·B 보고·C 질문), 건너뛴 게이트는 완료 보고에 ID 표기</sub> | <sub>2026.10.22</sub> | <sub>김단영</sub> |
| <sub>인테이크에 스타일 확인 단계 신설 — HTML 산출 시 컬러를 임의 고정하지 않고 매 프로젝트 확인 후 적용</sub> | <sub>2026.08.20</sub> | <sub>김단영</sub> |
| <sub>최초 등록 — 공수산정 + 기초 PRD(RRD) 빌더 하네스</sub> | <sub>2026.07.07</sub> | <sub>김단영</sub> |


RFP·회의록·AS-IS 실측 자료로부터 **프로젝트 공수산정 및 기초 PRD(RRD)** 를 단계별로 생성하고, 이후 정보가 유입될 때마다 **살아있는 문서로 갱신**하는 Claude Code 에이전트 하네스.

## 핵심 개념 2가지

1. **마스터프롬프트 v2.0이 섹션 정본** — `references/master-prompt-v2.0.md`의 헤더+10섹션(현황진단·산정단위·요구사항·R&R·공수 3축 분해·진행흐름·총평·리스크)을 파이프라인으로 생성. 산정 단위 승인(GATE 1)과 공수 추천안 승인(GATE 2) 전에는 다음 단계로 넘어가지 않음.
2. **STATE.md가 지속 상태 정본(SSOT)** — 공수 수치·산정 단위·확정 사항(D-xx)·[확인 필요](Q-xx)·조건부 전제(P-xx)·버전 히스토리를 프로젝트별 `_workspace/{slug}/STATE.md` 한 파일에 누적. 회의록·고객 답변이 오면 STATE.md부터 갱신하고 영향받는 섹션만 델타 재생성 → 버전업. 전체 재생성 없음.

## 디렉토리

```
agent/prd/
├── CLAUDE.md                      # 하네스 규칙 (폴더에서 Claude Code 열면 자동 로딩)
├── ORCHESTRATOR.md                # 파이프라인 + 업데이트 프로토콜 (실행 정본)
├── references/
│   ├── master-prompt-v2.0.md      # 섹션 작성 기준 정본 (옵시디언 원본의 사본)
│   └── state-template.md          # STATE.md 템플릿
├── input/{slug}/                  # 프로젝트별 입력 (RFP·회의록·실측). 유입 차수별 하위폴더
├── _workspace/{slug}/             # STATE.md + 01~06 단계 산출물
└── output/{slug}/                 # {NN}_{사업명}_PRD_v{X.Y}.{html|md|docx}
```

## 사용 흐름

```
[신규]   input/{slug}/에 자료 → "이 RFP로 PRD 만들어줘"
         → 인테이크(5문항) → 진단 → 단위 GATE → 범위 → 공수 GATE → 서사 → 검증 → v0.1

[업데이트] input/{slug}/에 회의록 추가 → "회의록 반영해서 업데이트해줘"
         → STATE.md 갱신(Q답변·D확정·P전제) → 영향 섹션만 재생성 → v0.2
```

## 자매 하네스
- `../proposal` — 제안서 본문 슬라이드. 이 하네스의 산출물을 입력으로 사용 가능.
- `harness_st-etribe` — 공수산정 HTML. 공수 수치가 이미 있으면 그쪽이 정본(재산정 안 함).

> 원본 마스터프롬프트: 옵시디언 `100. Workspace/110. Templates/★프로젝트 공수산정 및 기초PRD_마스터프롬프트_v2.0.md`. 옵시디언 쪽을 수정하면 `references/master-prompt-v2.0.md`에도 반영할 것.
