# worker — 단순작업 위임 서브에이전트 (백업)

## 릴리즈노트

| <div align="center"><sub>요약내용</sub><img width="1" height="1"></div> | <sub>업데이트 일자</sub><img width="1" height="1"> | <sub>소유자</sub><img width="45" height="1"> |
|:---|:---:|:---:|
| <sub>최초 등록 — 로컬 서브에이전트 worker 백업</sub> | <sub>2026.07.15</sub> | <sub>김단영</sub> |

단순 조회·검색·확인, 파일/폴더 이름 변경, 오타·맞춤법 수정, 포맷팅, 엑셀·문서에서
값 찾기 같은 **판단이 필요 없는 기계적 작업을 위임**하는 로컬 서브에이전트의 백업이다.

- **정본 위치**: `~/.claude/agents/worker.md` (sonnet + reasoning low, advisorModel: fable)
- **이 폴더**: 정본의 리포 백업. 수정 시 정본과 함께 갱신한다.
- **사용**: Claude Code가 단순 작업을 만나면 Agent 도구의 `worker` 타입으로 위임된다.
