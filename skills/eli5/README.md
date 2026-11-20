# eli5 — 그림 위주 쉬운 설명 스킬 (외부 스킬 백업)

주제 하나를 넣으면 그 주제를 처음 접하는 사람 눈높이의 HTML 아티팩트(큰 그림 · 적은 글자)가 나오는 설명 스킬, anthropics/claude-plugins-community 원본의 백업본

> **출처** — [anthropics/claude-plugins-community](https://github.com/anthropics/claude-plugins-community) 리포의 `eli5` 스킬(`eli5/skills/eli5/SKILL.md`) 백업본 · 원본 구성 = `SKILL.md` 단일 파일

## 한눈에 보기

| <div align="center"><sub>항목</sub></div> | <sub>내용</sub> |
|:---|:---:|
| <sub>목적</sub> | <sub>낯선 개념 · 동작 원리를 다섯 살 아이에게 하듯 그림 위주로 쉽게 설명(ELI5 = Explain Like I'm 5)</sub> |
| <sub>이럴 때 사용</sub> | <sub>처음 접하는 개념의 큰 그림이 필요할 때 · 비전문가에게 동작 원리를 보여 줄 때</sub> |
| <sub>넣는 것</sub> | <sub>설명할 주제 한 줄(`/eli5` 뒤 인자 → SKILL.md `$ARGUMENTS`)</sub> |
| <sub>나오는 것</sub> | <sub>HTML 아티팩트 1개 — 큰 그림 위주 · 글자 최소</sub> |
| <sub>부르는 법</sub> | <sub>`/eli5 <주제>` · `…가 어떻게 동작하는지 아주 쉽게 그림으로 설명해줘` 같은 요청</sub> |
| <sub>출처</sub> | <sub>원작 [anthropics/claude-plugins-community · eli5/skills/eli5/SKILL.md](https://github.com/anthropics/claude-plugins-community/blob/main/eli5/skills/eli5/SKILL.md)</sub> |
| <sub>리포 등록</sub> | <sub>김단영 — 외부 스킬 백업(2026.09.02)</sub> |
| <sub>연계</sub> | <sub>특정 하네스 비종속 · 단독 스킬</sub> |

## 이렇게 요청

| <div align="center"><sub>상황</sub></div> | <sub>요청 예시</sub> | <sub>나오는 것</sub> |
|:---|:---:|:---:|
| <sub>개념 하나 설명</sub> | <sub>`/eli5 DNS`</sub> | <sub>DNS가 하는 일을 큰 그림 위주로 푼 HTML 아티팩트</sub> |
| <sub>동작 원리 설명</sub> | <sub>`/eli5 OAuth 로그인`</sub> | <sub>로그인 과정을 그림 위주로 푼 HTML 아티팩트</sub> |
| <sub>슬래시 명령 없이</sub> | <sub>`블록체인이 어떻게 동작하는지 아주 쉽게 그림으로 설명해줘`</sub> | <sub>같은 형식의 HTML 아티팩트</sub> |

## 진행 단계

```
① 주제 받기(/eli5 인자) → ② HTML 아티팩트 작성(큰 그림 · 적은 글자)
```

| <div align="center"><sub>단계</sub></div> | <sub>하는 일</sub> | <sub>사용자 할 일</sub> | <sub>결과물</sub> |
|:---|:---:|:---:|:---:|
| <sub>① 주제 받기</sub> | <sub>`/eli5` 뒤 인자를 SKILL.md의 `Topic: $ARGUMENTS`로 전달</sub> | <sub>주제 입력</sub> | <sub>—</sub> |
| <sub>② 설명 작성</sub> | <sub>주제를 전혀 모르는 사람 기준으로 큰 그림 위주 · 적은 글자의 HTML 아티팩트 작성</sub> | <sub>결과 확인 · 추가 질문</sub> | <sub>HTML 아티팩트</sub> |

## 산출물

| <div align="center"><sub>산출물</sub></div> | <sub>형식</sub> | <sub>구성</sub> |
|:---|:---:|:---:|
| <sub>설명 아티팩트</sub> | <sub>HTML 아티팩트</sub> | <sub>큰 그림 위주 · 글자 최소 · 대상 = 주제를 처음 접하는 사람</sub> |

## 설치 · 단독 사용

```bash
# 리포 루트에서 — 이 스킬만 전역 설치
cp -r skills/eli5 ~/.claude/skills/eli5
```

- **리포 스킬 일괄 설치**: 리포 루트 `bash install-global.sh`에도 포함(`skills/` 아래 전체 복사)
- **의존성**: 추가 패키지 불필요
- **하네스 안에서 쓸 때**: 특정 하네스 비종속 · 단독 스킬

## 주의

- 외부 스킬 백업본 — 원작자 = anthropics/claude-plugins-community · 원본 위치 = [`eli5/skills/eli5/SKILL.md`](https://github.com/anthropics/claude-plugins-community/blob/main/eli5/skills/eli5/SKILL.md)
- SKILL.md 본문은 영어(설명 지시 1줄 + `Topic: $ARGUMENTS`)

## 릴리즈노트

| <div align="center"><sub>요약내용</sub><img width="1" height="1"></div> | <sub>업데이트 일자</sub><img width="1" height="1"> | <sub>소유자</sub><img width="45" height="1"> |
|:---|:---:|:---:|
| <sub>README 전면 개편 — 목적 · 넣는 것 · 산출물 형태 · 요청 예시 · 진행 단계 순으로 재구성, 릴리즈노트 맨 아래로 이동</sub> | <sub>2026.11.13</sub> | <sub>김단영</sub> |
| <sub>최초 등록 — [anthropics/claude-plugins-community](https://github.com/anthropics/claude-plugins-community/blob/main/eli5/skills/eli5/SKILL.md) 백업</sub> | <sub>2026.09.02</sub> | <sub>김단영</sub> |
