# handoff — /clear 전 세션 맥락 저장 스킬

컨텍스트를 비우기(/clear) 전에 부르면 작업 목표 · 진행 상태 · 사용자 결정 · 다음 할 일 · 관련 파일 · 명령이 `<프로젝트 루트>/.claude/HANDOFF.md`에 저장되고, 다음 세션이 그 파일의 「다음 할 일」 1번부터 이어 가는 세션 인수인계 스킬

## 한눈에 보기

| <div align="center"><sub>항목</sub></div> | <sub>내용</sub> |
|:---|:---:|
| <sub>목적</sub> | <sub>`/clear` 뒤에도 다음 세션이 곧바로 일할 수 있는 작업 상태 기록</sub> |
| <sub>이럴 때 사용</sub> | <sub>대화가 길어져 `/clear` 하기 전 · 세션을 넘기기 전 · 다른 PC로 작업을 넘길 때</sub> |
| <sub>넣는 것</sub> | <sub>현재 세션 맥락(Claude가 정리) · (선택) `/handoff <메모>`의 메모</sub> |
| <sub>나오는 것</sub> | <sub>`<프로젝트 루트>/.claude/HANDOFF.md` 1개 — 마크다운 · 40줄 안팎 · 저장 때마다 덮어쓰기</sub> |
| <sub>부르는 법</sub> | <sub>`/handoff` · `핸드오프 저장해줘` · `맥락 저장하고 clear 할게` · `세션 넘길 준비해줘`</sub> |
| <sub>제작</sub> | <sub>김단영(dykim)</sub> |
| <sub>연계</sub> | <sub>자동 불러오기 = SessionStart 훅(PC별 `~/.claude/settings.json`, 리포 미포함) · 이 리포에서는 루트 [CLAUDE.md](../../CLAUDE.md)의 세션 시작 확인 규칙 · 특정 하네스 비종속</sub> |

## 이렇게 요청

| <div align="center"><sub>상황</sub></div> | <sub>요청 예시</sub> | <sub>나오는 것</sub> |
|:---|:---:|:---:|
| <sub>`/clear` 직전 저장</sub> | <sub>`/handoff` · `핸드오프 저장해줘`</sub> | <sub>`.claude/HANDOFF.md` 저장 + 「핸드오프 저장 완료. 이제 `/clear` 하셔도 됩니다.」 한 줄</sub> |
| <sub>메모를 함께 저장</sub> | <sub>`/handoff 시안 B안 확정, 다음엔 피드백 반영부터`</sub> | <sub>「사용자 메모」 항목에 메모 원문 기록</sub> |
| <sub>세션 이관 준비</sub> | <sub>`맥락 저장하고 clear 할게` · `세션 넘길 준비해줘`</sub> | <sub>같은 저장 동작</sub> |
| <sub>다음 세션 시작</sub> | <sub>(SessionStart 훅이 파일 자동 로드)</sub> | <sub>첫 응답에서 이전 핸드오프 확인 한 줄 + 「다음 할 일」 1번부터 진행</sub> |
| <sub>작업이 모두 끝난 뒤</sub> | <sub>—</sub> | <sub>`.claude/HANDOFF.md` 삭제 여부 질문</sub> |

**예시 대화**

```
사용자: /handoff 시안 B안 확정, 다음엔 피드백 반영부터
Claude: 핸드오프 저장 완료. 이제 /clear 하셔도 됩니다.
사용자: /clear
        (SessionStart 훅이 .claude/HANDOFF.md를 컨텍스트에 로드)
Claude: (이전 핸드오프 확인 한 줄 → 「다음 할 일」 1번부터 진행)
```

## 진행 단계

```
① .claude/ 확인 → ② HANDOFF.md 덮어쓰기 → ③ 저장 완료 안내 → (사용자 /clear) → ④ 다음 세션 이어받기 → ⑤ 작업 종료 후 정리
```

| <div align="center"><sub>단계</sub></div> | <sub>하는 일</sub> | <sub>사용자 할 일</sub> | <sub>결과물</sub> |
|:---|:---:|:---:|:---:|
| <sub>① 폴더 확인</sub> | <sub>프로젝트 루트(현재 작업 디렉터리)에 `.claude/` 폴더가 없으면 생성</sub> | <sub>`/handoff` 호출</sub> | <sub>—</sub> |
| <sub>② 기록</sub> | <sub>아래 양식으로 `.claude/HANDOFF.md` 덮어쓰기(이전 핸드오프 삭제)</sub> | <sub>(선택) 메모 전달</sub> | <sub>`HANDOFF.md`</sub> |
| <sub>③ 안내</sub> | <sub>「핸드오프 저장 완료. 이제 `/clear` 하셔도 됩니다.」 한 줄</sub> | <sub>`/clear` 실행</sub> | <sub>—</sub> |
| <sub>④ 다음 세션</sub> | <sub>SessionStart 훅이 파일을 컨텍스트에 로드 → 첫 응답에서 「이전 핸드오프를 읽었다」 한 줄 → 「다음 할 일」 1번부터 진행<br>핸드오프 내용이 현재 코드 · 파일 상태와 다르면 실제 파일 우선 · 다른 점을 짚고 진행</sub> | <sub>이어서 작업 지시</sub> | <sub>—</sub> |
| <sub>⑤ 정리</sub> | <sub>작업이 끝나 더 필요 없으면 `.claude/HANDOFF.md` 삭제 여부 질문</sub> | <sub>삭제 여부 답변</sub> | <sub>—</sub> |

## 산출물

`<프로젝트 루트>/.claude/HANDOFF.md` — 마크다운 1개, 40줄 안팎

| <div align="center"><sub>항목</sub></div> | <sub>적는 내용</sub> |
|:---|:---:|
| <sub>머리말</sub> | <sub>`# HANDOFF — YYYY-MM-DD HH:MM`</sub> |
| <sub>작업 목표</sub> | <sub>이 세션에서 하려던 일 1~2문장</sub> |
| <sub>진행 상태</sub> | <sub>완료 · 진행 중(어디까지) · 막힌 것(원인 · 시도한 것)</sub> |
| <sub>사용자 결정 사항</sub> | <sub>하기로 · 하지 않기로 한 결정</sub> |
| <sub>다음 할 일</sub> | <sub>우선순위순 번호 목록</sub> |
| <sub>관련 파일 · 명령</sub> | <sub>`path/to/file` — 무엇인지 · `command` — 언제 쓰는지</sub> |
| <sub>사용자 메모</sub> | <sub>`/handoff <메모>` 인자(있으면)</sub> |

- **작성 원칙**: 대화 요약 대신 다음 세션이 곧바로 일할 정보만 · 파일 경로 · 명령 · 브랜치명 · URL은 정확히 그대로(추측 금지) · 사용자 결정 누락 금지 · 길어지면 「다음 할 일」 우선
- 양식 원문 = [SKILL.md](SKILL.md) 「양식」

## 설치 · 단독 사용

```bash
# 리포 루트에서 — 이 스킬만 전역 설치
cp -r skills/handoff ~/.claude/skills/handoff
```

- **리포 스킬 일괄 설치**: 리포 루트 `bash install-global.sh` → 다른 스킬과 함께 `~/.claude/skills/handoff/`에 설치
- **의존성**: 추가 패키지 불필요 · `/clear` 뒤 자동 불러오기는 SessionStart 훅 별도 설정(PC별 `~/.claude/settings.json`, 리포 미포함)
- **하네스 안에서 쓸 때**: 특정 하네스 비종속 — 어느 프로젝트 폴더에서나 사용

## 주의 · 자주 묻는 질문

| <div align="center"><sub>질문</sub></div> | <sub>답</sub> |
|:---|:---:|
| <sub>`/clear` 뒤 자동으로 읽히지 않는 경우</sub> | <sub>SessionStart 훅이 없는 PC · 클라우드 세션 — 이 리포에서는 루트 [CLAUDE.md](../../CLAUDE.md) 안내에 따라 세션 시작 때 `.claude/HANDOFF.md` 확인</sub> |
| <sub>이전 핸드오프 보관</sub> | <sub>보관 대상 외 — 저장 때마다 덮어쓰기</sub> |
| <sub>핸드오프와 현재 파일이 다를 때</sub> | <sub>현재 코드 · 파일 상태 우선 · 차이를 짚은 뒤 진행</sub> |
| <sub>PC 간 인수인계</sub> | <sub>이 리포의 `.claude/HANDOFF.md` = Mac → Windows 작업 동기화 현황판<br>세션 시작 때 또는 `git pull`로 이 파일이 새로 들어오거나 바뀌면 첫 응답에서 「이어서 할 일이 있다」 한 줄 후 「다음 할 일」 1번부터 진행 · 파일 머리말이 다른 PC를 가리키면 실행 대신 그 사실만 안내(루트 CLAUDE.md)</sub> |

## 릴리즈노트

| <div align="center"><sub>요약내용</sub><img width="1" height="1"></div> | <sub>업데이트 일자</sub><img width="1" height="1"> | <sub>소유자</sub><img width="45" height="1"> |
|:---|:---:|:---:|
| <sub>README 전면 개편 — 목적 · 넣는 것 · 산출물 형태 · 요청 예시 · 진행 단계 순으로 재구성, 릴리즈노트 맨 아래로 이동</sub> | <sub>2026.11.13</sub> | <sub>김단영</sub> |
| <sub>최초 등록 — `/clear` 전 세션 맥락을 `.claude/HANDOFF.md` 로 저장하는 개인 스킬을 리포 정본으로 등록. 같은 파일을 PC 간 인수인계(Mac → Windows)에도 사용</sub> | <sub>2026.10.09</sub> | <sub>김단영</sub> |
