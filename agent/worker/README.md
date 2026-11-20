# worker — 단순작업 위임 서브에이전트 (백업)

판단이 필요 없는 단순 조회 · 이름 변경 · 오타 수정 · 포맷팅 · 값 찾기 같은 기계적 작업을 메인 대화 대신 처리하는 Claude Code 로컬 서브에이전트 worker의 정의 파일 백업

## 한눈에 보기

| <div align="center"><sub>항목</sub></div> | <sub>내용</sub> |
|:---|:---:|
| <sub>목적</sub> | <sub>판단이 필요 없는 기계적 작업의 위임 · 가벼운 설정(sonnet · effort low)으로 처리 후 짧게 보고</sub> |
| <sub>이럴 때 사용</sub> | <sub>단순 조회 · 검색 · 확인 · 파일/폴더 이름 변경 · 오타 · 맞춤법 수정 · 코드 · 문서 · 마크다운 포맷팅 · 엑셀 · CSV · 문서에서 특정 값이나 항목 찾기 · 반복 텍스트 · 코드 치환 · 목록 정리 · 정해진 규칙대로 처리하는 작업</sub> |
| <sub>넣는 것</sub> | <sub>범위가 확정된 작업 지시(대상 파일 · 바꿀 내용 · 찾을 값)</sub> |
| <sub>나오는 것</sub> | <sub>짧은 결과 보고(한 일 · 변경 파일 목록 · 발견 값) · 판단이 필요한 지점은 추측 없이 그 지점 보고</sub> |
| <sub>부르는 법</sub> | <sub>자동 위임: Claude Code가 단순 작업을 만나면 Agent 도구의 `worker` 타입으로 위임<br>직접 지정: 요청 문장에 「worker로」 명시</sub> |
| <sub>제작 · 출처</sub> | <sub>김단영 · 정본 `~/.claude/agents/worker.md`(로컬 서브에이전트) · 이 폴더는 정본의 리포 백업</sub> |
| <sub>연계 하네스</sub> | <sub>하네스 무관 · 설치한 PC의 모든 Claude Code 세션 공통</sub> |

## 이렇게 요청

| <div align="center"><sub>상황</sub></div> | <sub>요청 예시</sub> | <sub>나오는 것</sub> |
|:---|:---:|:---:|
| <sub>파일 · 폴더 이름 변경</sub> | <sub>`이 폴더 파일명 날짜 형식으로 바꿔줘`</sub> | <sub>변경 파일 목록</sub> |
| <sub>오타 · 맞춤법 수정</sub> | <sub>`이 문서 오타만 고쳐줘`</sub> | <sub>수정 위치 · 변경 파일</sub> |
| <sub>값 · 항목 찾기</sub> | <sub>`이 엑셀에서 담당자가 비어 있는 행 찾아줘`</sub> | <sub>발견 값 · 위치</sub> |
| <sub>반복 치환 · 포맷팅</sub> | <sub>`이 폴더 md 파일 날짜 표기를 YYYY.MM.DD로 통일해줘`</sub> | <sub>변경 파일 목록</sub> |
| <sub>직접 지정</sub> | <sub>`worker로 이 목록 가나다순 정리해줘`</sub> | <sub>정리 결과 · 변경 파일</sub> |

- 위임 여부는 메인 에이전트가 description 기준으로 판단 · 판단이 필요한 작업(설계 · 문장 작성 · 검토)은 위임 대상 제외

## 진행 단계

```
① 사용자 요청 → ② 메인 에이전트가 단순 작업 판단 → ③ worker 위임 → ④ 지시 범위만 수행 → ⑤ 짧은 결과 보고 → ⑥ 메인 에이전트가 사용자에게 전달
```

| <div align="center"><sub>단계</sub></div> | <sub>하는 일</sub> | <sub>사용자 할 일</sub> | <sub>결과물</sub> |
|:---|:---:|:---:|:---:|
| <sub>① 요청</sub> | <sub>—</sub> | <sub>대상 · 바꿀 내용을 구체적으로 요청</sub> | <sub>—</sub> |
| <sub>② · ③ 위임</sub> | <sub>메인 에이전트가 description에 맞는 작업을 Agent 도구 `worker` 타입으로 위임</sub> | <sub>—</sub> | <sub>작업 지시</sub> |
| <sub>④ 수행</sub> | <sub>지시받은 범위만 정확히 수행 · 요청 부분 외 수정 금지 · 애매한 상황은 추측 대신 그 지점 보고</sub> | <sub>—</sub> | <sub>파일 변경 · 조회 결과</sub> |
| <sub>⑤ · ⑥ 보고</sub> | <sub>한 일 · 변경 파일 목록 · 발견 값만 요약 · 과정 설명 생략</sub> | <sub>결과 확인 · 애매한 지점 판단</sub> | <sub>결과 보고</sub> |

## 산출물

- 짧은 결과 보고: 한 일 · 변경 파일 목록 · 발견 값
- 파일 수정은 요청 부분만 · 포맷 전체 재정렬 금지
- 한국어 문서는 한국어로 · 코드 · 기술 파일은 원문 언어 그대로

## 설치 · 단독 사용

- 전역 설치(리포 루트에서): `worker.md` → `~/.claude/agents/worker.md`

```bash
mkdir -p ~/.claude/agents && cp agent/worker/worker.md ~/.claude/agents/worker.md
```

- 적용 확인: 새 Claude Code 세션에서 `/agents` 목록에 `worker` 표시
- 의존성: 추가 설치 불필요 · `install-global.sh` 동기화 대상이 아니라 수동 복사
- 정본을 고친 뒤 백업 갱신: `cp ~/.claude/agents/worker.md agent/worker/worker.md`

| <div align="center"><sub>설정(frontmatter)</sub></div> | <sub>값</sub> |
|:---|:---:|
| <sub>`name`</sub> | <sub>`worker`</sub> |
| <sub>`model`</sub> | <sub>`sonnet`</sub> |
| <sub>`effort`</sub> | <sub>`low`</sub> |
| <sub>`tools`</sub> | <sub>미지정 · 메인 세션 도구 상속</sub> |

## 폴더 구성

```
agent/worker/
├── worker.md     # 서브에이전트 정의(frontmatter + 작업 규칙) · ~/.claude/agents/worker.md 백업
└── README.md
```

## 릴리즈노트

| <div align="center"><sub>요약내용</sub><img width="1" height="1"></div> | <sub>업데이트 일자</sub><img width="1" height="1"> | <sub>소유자</sub><img width="45" height="1"> |
|:---|:---:|:---:|
| <sub>README 전면 개편 — 목적 · 넣는 것 · 산출물 형태 · 요청 예시 · 진행 단계 순으로 재구성, 릴리즈노트 맨 아래로 이동</sub> | <sub>2026.11.13</sub> | <sub>김단영</sub> |
| <sub>최초 등록 — 로컬 서브에이전트 worker 백업</sub> | <sub>2026.07.15</sub> | <sub>김단영</sub> |
