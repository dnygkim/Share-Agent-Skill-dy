# flowchart-defense — 흐름도 검토 · 방어설계 스킬

고객이 보낸 챗봇 · 서비스 흐름도(PPT · 이미지 · PDF · mermaid)를 넣으면 빠진 예외 · 실패 · 빈 결과 · 취소 · 막다른 길을 패턴 1~8로 전수 점검한 보강 흐름도와 고객 회신용 검토 리포트(MD, 선택 시 워드 요약본)가 나오는 스킬

## 한눈에 보기

| <div align="center"><sub>항목</sub></div> | <sub>내용</sub> |
|:---|:---:|
| <sub>목적</sub> | <sub>정상 흐름(happy path) 위주 고객 흐름도의 누락 분기 보강 + 원본 · 보강 · 추정을 구분한 검토 리포트</sub> |
| <sub>이럴 때 사용</sub> | <sub>고객사 흐름도 회신 전 검토 · 오류 · 결과 0건 · 취소 · 수정 · 끊긴 화살표 점검 · 흐름도 수십 개 일괄 검토</sub> |
| <sub>넣는 것</sub> | <sub>흐름도 파일 1개 또는 여러 개 · 폴더 — PPTX · PNG/JPG · PDF · mermaid/MD</sub> |
| <sub>나오는 것</sub> | <sub>검토 리포트 `{흐름명}_검토리포트_YYYYMMDD.md`(8섹션 마스터) · 선택 시 고객 요약본 `{흐름명}_고객요약본_YYYYMMDD.md` → 워드(.docx)</sub> |
| <sub>부르는 법</sub> | <sub>흐름도 첨부 + `이 챗봇 흐름도 검토해줘` · `플로우차트 방어설계 해줘` 등 · 슬래시 명령 `/flowchart-defense`</sub> |
| <sub>범위 밖</sub> | <sub>흐름도 신규 작성 · 단순 요약</sub> |
| <sub>핵심 원칙</sub> | <sub>원본에 없는 흐름 생성 금지 — 보강 전 「원본을 이렇게 읽었어요」 확인 절차 필수 · 원본 · 보강 · 추정을 색과 표로 구분</sub> |
| <sub>제작</sub> | <sub>신지은 (GitHub [jieun994](https://github.com/jieun994)) · 이 리포 이관 2026.07.21</sub> |
| <sub>출처</sub> | <sub>[jieun994/zinis_claude_skills](https://github.com/jieun994/zinis_claude_skills) · 원본 경로 `skills/flowchart-defense/`</sub> |
| <sub>연계</sub> | <sub>호출 하네스 미지정 · 단독 사용</sub> |

## 이렇게 요청

| <div align="center"><sub>상황</sub></div> | <sub>요청 예시</sub> | <sub>나오는 것</sub> |
|:---|:---:|:---:|
| <sub>흐름도 1개 검토</sub> | <sub>(흐름도 첨부) `이 챗봇 흐름도 검토해줘` · `이 PPT 흐름 검토`</sub> | <sub>원본 인벤토리 확인 → 검토 리포트 MD</sub> |
| <sub>방어설계 보강</sub> | <sub>`플로우차트 방어설계 해줘` · `흐름도 보강해줘`</sub> | <sub>패턴 근거가 달린 보강 흐름도(mermaid) + 리포트</sub> |
| <sub>특정 누락 점검</sub> | <sub>`이 흐름에서 빠진 예외 찾아줘` · `막다른 길이랑 빈 결과 분기 체크해줘`</sub> | <sub>패턴 체크리스트 · 리스크 우선순위 중심 리포트</sub> |
| <sub>고객 전달본</sub> | <sub>`고객 전달본 워드로 만들어줘`</sub> | <sub>고객 요약본 4섹션 .docx</sub> |
| <sub>흐름도 여러 개</sub> | <sub>(파일 여러 개 · 폴더 첨부) `이 챗봇 흐름도 검토해줘`</sub> | <sub>묶음별 리포트(1개당 1개) · 묶음 요약 · 확인요망 취합본(선택)</sub> |

## 진행 단계

| <div align="center"><sub>모드</sub></div> | <sub>입력</sub> | <sub>방식</sub> |
|:---|:---:|:---:|
| <sub>단건</sub> | <sub>흐름도 파일 1개</sub> | <sub>원본 확정 게이트 전체 적용</sub> |
| <sub>배치</sub> | <sub>파일 여러 개 · 폴더</sub> | <sub>5~8개 묶음 자동 분할 · 1개당 리포트 1개 · 저신뢰 추출만 사람 확인</sub> |

### 단건 모드

```
① 입력 판독 → ② 원본 인벤토리 확정(GATE) → ③ 방어설계(패턴 1~8) → ④ 검토 리포트 → ⑤ (선택) 고객 요약본 · 워드
```

| <div align="center"><sub>단계</sub></div> | <sub>하는 일</sub> | <sub>사용자 할 일</sub> | <sub>결과물</sub> |
|:---|:---:|:---:|:---:|
| <sub>① 입력 판독</sub> | <sub>이미지 · PDF = 비전 판독 / PPTX = 도형 텍스트 추출(`extract_pptx.py`) + 슬라이드 PNG 렌더(`render_slides.py`) 후 비전으로 화살표 복원 / mermaid = 그대로 파싱</sub> | <sub>흐름도 파일 첨부</sub> | <sub>노드 · 엣지 목록(원본만)</sub> |
| <sub>**② 원본 인벤토리 확정 (GATE)**</sub> | <sub>읽은 노드 · 연결 · 흐릿한 부분 제시 · 승인 전 보강 착수 금지</sub> | <sub>**원본과 같은지 확인 → 「맞아요, 보강 진행」 · 「고칠 게 있어요」 · 「원본을 다시 줄게요」 중 선택**</sub> | <sub>확정 원본</sub> |
| <sub>③ 방어설계</sub> | <sub>노드 · 엣지마다 패턴 1~8 순회 · 보강마다 패턴 번호 근거 · 불확실 항목은 보강 대신 확인요망 · 과잉 보강 금지</sub> | <sub>—</sub> | <sub>보강안 · 체크리스트</sub> |
| <sub>④ 검토 리포트</sub> | <sub>8섹션 리포트 + 최상단 고지문 · mermaid 렌더 검증(`mmdc` 설치 시)</sub> | <sub>리포트 검토</sub> | <sub>`{흐름명}_검토리포트_YYYYMMDD.md`</sub> |
| <sub>⑤ 고객 전달본(선택)</sub> | <sub>마스터에서 4섹션 요약본 추출 → 워드 변환(맑은 고딕 지정 · 흐름도 PNG 삽입)</sub> | <sub>`고객 전달본 워드로 만들어줘` 요청</sub> | <sub>`{흐름명}_고객요약본_YYYYMMDD.md` · .docx</sub> |

### 배치 모드

```
① 목록 확인 · 묶음 분할 → ② 묶음별 처리 → ③ 묶음 요약 → ④ 확인요망 취합(선택)
```

| <div align="center"><sub>단계</sub></div> | <sub>하는 일</sub> | <sub>사용자 할 일</sub> | <sub>결과물</sub> |
|:---|:---:|:---:|:---:|
| <sub>① 목록 확인 · 묶음 분할</sub> | <sub>흐름도 · 슬라이드 N개 제시 · 5~8개 묶음 분할(8개 초과 시 8개씩) · 머지 · 통합 · 폐기 표식 슬라이드는 「→ 통합 대상」 1줄 표기 후 제외</sub> | <sub>목록 · 묶음 확인</sub> | <sub>처리 목록</sub> |
| <sub>② 묶음별 처리</sub> | <sub>파일마다 판독 → 방어설계 → 리포트(1개당 1개) · 원본 확정은 저신뢰 추출만 플래그</sub> | <sub>**플래그된 흐름도 확인**</sub> | <sub>리포트 묶음</sub> |
| <sub>③ 묶음 요약</sub> | <sub>「8개 중 6개 완료, 2개 확인 필요」 형식 요약 후 다음 묶음</sub> | <sub>요약 확인</sub> | <sub>묶음 요약</sub> |
| <sub>④ 확인요망 취합(선택)</sub> | <sub>리포트별 고객 확인요망 취합</sub> | <sub>—</sub> | <sub>`고객확인요망_취합.md`</sub> |

- 흐름도가 많을 때(예: 30개 · 108개) 폴더째 또는 여러 개 첨부 · 30~40개를 한 대화에 한꺼번에 넣으면 컨텍스트 한계로 뒤쪽 품질 저하 · 원본 확정 무력화 → 8개 이하 묶음 순차 처리
- 1슬라이드 = 1흐름 덱은 파일명 앞에 슬라이드 번호 2자리 `NN_{흐름명}_검토리포트_YYYYMMDD.md` (정렬 · 원본 대조용, 결번 = 폐기 슬라이드)
- 여러 흐름도를 하나로 합치기 금지 · 배치에서도 원본/보강/추정 분리 · 근거 부착 원칙 동일

## 산출물

### 검토 리포트 8섹션 (기획자 내부용 마스터)

| <div align="center"><sub>섹션</sub></div> | <sub>내용</sub> |
|:---|:---:|
| <sub>① 보강 흐름도</sub> | <sub>원본(실선) · 보강(점선 + `[추가]`) · 추정(회색 + `[추정]`) 구분 mermaid</sub> |
| <sub>② 분류 색상표</sub> | <sub>사용자 행동 · 화면(UI) · API 통신 · 판단/분기 · 시스템 처리 5색</sub> |
| <sub>③ 원본/보강/추정 구분표</sub> | <sub>노드별 구분 · 근거 패턴 · 원본 위치 — 원본과 AI 보강을 한눈에 구분</sub> |
| <sub>④ 패턴 적용 체크리스트</sub> | <sub>패턴 1~8 전수 점검 증거 · 비적용 패턴도 사유 기록</sub> |
| <sub>⑤ 리스크 우선순위</sub> | <sub>치명 · 중요 · 권장 순 정렬 + 사용자 영향 · 권고</sub> |
| <sub>⑥ Before/After 비교</sub> | <sub>변경 전후 노드 대조</sub> |
| <sub>⑦ 변경 이력</sub> | <sub>무엇을 왜 바꿨는지(근거 = 패턴 번호)</sub> |
| <sub>⑧ 고객 확인요망</sub> | <sub>고객에게 되물을 미확정 항목 · 내부 분석과 별도 분리</sub> |

- 최상단 고지문 자동 삽입: 원본 흐름도 + 보강 포함 · `[추가]` · `[추정]` 항목 검토 필요 안내

### 고객 요약본 (워드 전달본 기본 4섹션)

| <div align="center"><sub>섹션</sub></div> | <sub>내용</sub> | <sub>마스터 출처</sub> |
|:---|:---:|:---:|
| <sub>1 보강 흐름도</sub> | <sub>mermaid + 작은 색 범례(원본 · 보강 · 추정)</sub> | <sub>① 범례 압축</sub> |
| <sub>2 주요 변경 요약 Top 5</sub> | <sub>변경 내용 + 이유 한 줄씩</sub> | <sub>⑦ 압축</sub> |
| <sub>3 꼭 고쳐야 할 리스크</sub> | <sub>치명 · 중요만(권장은 상세본 참조)</sub> | <sub>⑤ 필터</sub> |
| <sub>4 고객 확인요망</sub> | <sub>고객이 답할 미확정 항목 전부</sub> | <sub>⑧ 그대로</sub> |

- 신뢰 중시 고객 = 원본/보강/추정 구분표를 더한 5섹션 · 고객이 원하면 전체 상세본(마스터 MD) 그대로 변환
- 워드 변환은 선택 · MD 리포트는 항상 생성 · 전체 8섹션은 MD에 그대로 유지(워드는 읽기 좋게 슬림)
- 고객 발송본 톤: 이모지 · ★ 제거 · 리스크 등급 텍스트(치명 · 중요 · 권장) · 개조식 · 명사형 · 「AI 방어설계」 대신 「검토 · 보강」
- 고객본 확인요망 형식: 명사형 토픽 + 현황 · 확인 2줄 · 「회신 요망」 · 「확정 요망」 종결

### 결과 예시

- 입력: 고객이 준 `배송일정변경_흐름도.pptx`(정상 흐름만) + `이 챗봇 흐름도 검토하고 방어설계 해줘`
- 결과: `배송일정변경_검토리포트_YYYYMMDD.md` — 예시 파일 [samples/배송일정변경_검토리포트_예시.md](samples/배송일정변경_검토리포트_예시.md)

### 옵션

| <div align="center"><sub>설정</sub></div> | <sub>기본값</sub> | <sub>변경 방법</sub> |
|:---|:---:|:---:|
| <sub>출력 형식</sub> | <sub>MD 마스터(8섹션)</sub> | <sub>`워드로 만들어줘` → 고객 요약본(4섹션) docx</sub> |
| <sub>고객본 섹션</sub> | <sub>4섹션</sub> | <sub>`5섹션으로`(구분표 추가) · `전체로`</sub> |
| <sub>배치 묶음 크기</sub> | <sub>8개</sub> | <sub>시작 시 `N개씩 나눠줘`</sub> |
| <sub>보강 섹션</sub> | <sub>8개 전부</sub> | <sub>`리스크 표는 빼줘` 식 가감</sub> |
| <sub>출력 언어</sub> | <sub>한국어</sub> | <sub>시작 시 다른 언어 요청</sub> |

## 점검 패턴 1~8

| <div align="center"><sub>패턴</sub></div> | <sub>이름</sub> | <sub>보강 내용</sub> |
|:---|:---:|:---:|
| <sub>1</sub> | <sub>분류 · 라벨 명확화</sub> | <sub>게이트를 존재 · 상태 · 조건으로 구분 · 모든 분기 라벨 명시 · 노드 5분류 색 태깅</sub> |
| <sub>2</sub> | <sub>진입 · 전제 검증</sub> | <sub>데이터 존재 · 로그인 · 권한 전제 게이트 + 전제 실패 시 대체 시나리오</sub> |
| <sub>3</sub> | <sub>빈 결과(0건) 분기</sub> | <sub>결과 노출 지점 앞 「결과 존재?」 게이트 + 안내 · 대안 버튼 · 상위 게이트가 이미 거른 0건은 추가 금지</sub> |
| <sub>4</sub> | <sub>발화 추출 · 결손 입력</sub> | <sub>발화로 말한 값은 저장 후 반영 · 빠진 값만 화면 입력</sub> |
| <sub>5</sub> | <sub>재시도 · 반복 제한</sub> | <sub>실패 안내 후 재시도 · 종료 분기 · 반복 횟수 가드</sub> |
| <sub>6</sub> | <sub>취소 · 수정 회귀</sub> | <sub>최종 확인 단계 확인 · 수정 · 취소 3분기 · 수정은 해당 입력 지점으로 회귀</sub> |
| <sub>7</sub> | <sub>노드 분리 · 선행 데이터</sub> | <sub>API 노드와 판단 노드 분리 · 화면 노출 전 선행 조회 API 점검</sub> |
| <sub>8</sub> | <sub>막다른 길 제거 · 실패 후속</sub> | <sub>모든 말단 종착 노드 마감 · 쓰기 API 실패 후속(콜백 · 접수)</sub> |

- 거의 모든 흐름 점검 = 1 · 3 · 6 · 8 / 흐름 성격에 따라 = 2 · 4 · 5 · 7
- 보강은 추가만 · 원본 노드 의미 · 라벨 변경 금지 · 챗봇 맥락에 안 맞는 분기(예: 결제 없는 안내봇의 결제 실패 흐름) 추가 금지
- 정의 · 탐지 조건 · 보강 방법 · 적용 예시 상세: [references/patterns.md](references/patterns.md)

## 설치 · 단독 사용

```bash
cp -r skills/flowchart-defense ~/.claude/skills/flowchart-defense
```

- 리포 루트 기준 명령 · 스킬 일괄 설치는 원본 리포 `bash install-global.sh` · 공유 리포 `share/update.sh`
- 하네스 안에서: 이 스킬을 호출하는 하네스 미지정 · `sync-skills`가 전체 스킬을 `agent/proposal` · `agent/feature-spec-sb` · `agent/test-runner`의 `.claude/skills/`로 복사하므로 그 폴더 세션에서도 사용 가능
- 의존성: 이미지 · PDF · mermaid 입력의 MD 리포트는 추가 설치 불필요 · PPTX 입력과 워드 변환에만 아래 도구 필요

| <div align="center"><sub>도구</sub></div> | <sub>용도</sub> | <sub>필요한 때</sub> |
|:---|:---:|:---:|
| <sub>Python 3</sub> | <sub>스크립트 실행 · `python`이 없으면 `py -3` · 한글 출력용 `PYTHONUTF8=1`</sub> | <sub>PPTX 입력 · 워드 변환</sub> |
| <sub>python-pptx (선택)</sub> | <sub>도형 좌표까지 추출 · 미설치 시 XML 텍스트만 추출(동작 유지)</sub> | <sub>PPTX 입력</sub> |
| <sub>PowerPoint 또는 LibreOffice</sub> | <sub>슬라이드 PNG 렌더(화살표 판독) · PowerPoint COM(`pywin32` 또는 `comtypes`) 우선 · LibreOffice는 PDF 변환 폴백</sub> | <sub>PPTX 입력</sub> |
| <sub>python-docx</sub> | <sub>`pip install python-docx` · 표 → 워드 표 · 한글 폰트(맑은 고딕) 지정</sub> | <sub>워드 전달본</sub> |
| <sub>mermaid-cli `mmdc` (선택)</sub> | <sub>`npm i -g @mermaid-js/mermaid-cli` · mermaid 문법 검증 · 워드 흐름도 PNG 삽입 · 미설치 시 MD 유지 + 워드는 코드블록 · 「흐름도는 MD에서 확인」 안내로 대체</sub> | <sub>렌더 검증 · 워드 전달본</sub> |

## 폴더 구성

```
skills/flowchart-defense/
├── SKILL.md                     Claude 작동 정본 (Iron Law · 단건/배치 워크플로 · 엣지 케이스)
├── README.md                    사람용 안내 (이 문서)
├── references/
│   ├── patterns.md              방어설계 패턴 1~8 (정의 · 탐지 조건 · 보강 방법 · 적용 예시)
│   └── output-templates.md      리포트 8섹션 · 고객 요약본 · 고객 발송본 톤
├── scripts/
│   ├── extract_pptx.py          PPTX 도형 텍스트 · 좌표 추출(보조)
│   ├── render_slides.py         PPTX 슬라이드 → PNG (화살표 판독용, 슬라이드 번호 · 해상도 지정)
│   └── render_docx.py           리포트 MD → 워드 + mermaid PNG 삽입
├── samples/배송일정변경_검토리포트_예시.md
└── .claude-plugin/plugin.json   플러그인 정보 (v0.2.0 · 제작자 신지은)
```

## 주의

- 흐름도를 새로 그리는 용도가 아니라 받은 흐름도를 검토 · 보강하는 용도
- 원본 · 보강 · 추정은 산출물 전체에서 분리(색 · 태그 · 구분 컬럼)
- 불확실한 라벨 · 연결 · 값 = `[추정]` 표시 + 고객 확인요망 · 「아마 ~일 것」 · 「원본에 없지만 넣어두자」 = 추정 신호
- 좌표가 캔버스 밖인 도형도 비전으로 실제 연결 확인 · 좌표만으로 「슬라이드 바깥 · 누락」 단정 금지
- 넓거나 세로로 긴 슬라이드 = PNG 가장자리가 잘릴 위험 → 슬라이드 크기 확인 후 고해상도 재렌더 또는 영역 크롭
- 이미지로 박힌 PPT 텍스트 · 도형에 안 붙은 화살표 → 위치로 임의 연결 금지 · 흐릿한 부분 명시 · 신뢰도 미달이면 원본 재요청
- 한 파일에 흐름 여럿 → 자동 분리 대신 분리 여부 질문
- 흐름도가 아닌 입력(와이어프레임 · 캡처 · 표) = 강제 변환 대신 재질의 · 한글이 깨진 비율이 높은 OCR 결과 = 원본 PPT · 텍스트 재요청
- 노드 2~3개 단순 흐름 = 보강 여지 부족 명시 · 억지 보강 금지 / 노드 다수 = 서브플로우 구간 분할
- 종료 없는 루프 = 패턴 8로 종착 처리 + 원본에 종료가 없던 사실을 변경 이력에 기록
- 실패 대비: 판독 → 인벤토리 → 보강 → 리포트 단계별 중간 결과 보존 · 신뢰도 미달이면 정지 후 사유 · 필요 자료 안내

## 릴리즈노트

| <div align="center"><sub>요약내용</sub><img width="1" height="1"></div> | <sub>업데이트 일자</sub><img width="1" height="1"> | <sub>소유자</sub><img width="45" height="1"> |
|:---|:---:|:---:|
| <sub>README 전면 개편 — 목적 · 넣는 것 · 산출물 형태 · 요청 예시 · 진행 단계 순으로 재구성, 릴리즈노트 맨 아래로 이동</sub> | <sub>2026.11.13</sub> | <sub>김단영</sub> |
| <sub>최초 등록 — 신지은 스킬 이관 (jieun994/zinis_claude_skills)</sub> | <sub>2026.07.21</sub> | <sub>신지은</sub> |
