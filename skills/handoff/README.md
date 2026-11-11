# handoff (세션 맥락 인수인계)

## 릴리즈노트

| <div align="center"><sub>요약내용</sub><img width="1" height="1"></div> | <sub>업데이트 일자</sub><img width="1" height="1"> | <sub>소유자</sub><img width="45" height="1"> |
|:---|:---:|:---:|
| <sub>최초 등록 — `/clear` 전 세션 맥락을 `.claude/HANDOFF.md` 로 저장하는 개인 스킬을 리포 정본으로 등록. 같은 파일을 PC 간 인수인계(Mac → Windows)에도 사용</sub> | <sub>2026.10.09</sub> | <sub>김단영</sub> |

## 무엇을 하나요

`/handoff` 또는 「핸드오프 저장해 줘」로 호출하면, 컨텍스트를 비우기(`/clear`) 전에 현재 작업 상태를 `<프로젝트 루트>/.claude/HANDOFF.md` 에 기록한다. 다음 세션은 그 파일을 읽고 「다음 할 일」 1번부터 이어간다.

- **기록 항목**: 작업 목표 · 진행 상태 · 사용자 결정 사항 · 다음 할 일 · 관련 파일·명령 · 사용자 메모 (40줄 안팎)
- **자동 불러오기**: `/clear` 뒤에 자동으로 읽히려면 SessionStart 훅이 필요하다. 훅은 이 리포에 들어 있지 않고 PC별 `~/.claude/settings.json` 에 둔다. 훅이 없는 PC와 클라우드 세션은 리포 루트 [CLAUDE.md](../../CLAUDE.md) 의 안내에 따라 세션 시작 때 이 파일을 읽는다.
- **PC 간 인수인계**: 이 리포의 `.claude/HANDOFF.md` 는 Mac → Windows 작업 동기화 현황판으로 쓴다.

## 설치

리포 루트에서 `bash install-global.sh` 를 실행하면 다른 스킬과 함께 `~/.claude/skills/handoff/` 에 들어간다. 이 스킬만 쓰려면 폴더를 복사한다.

```bash
cp -r skills/handoff ~/.claude/skills/handoff
```
