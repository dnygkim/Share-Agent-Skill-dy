# weekly-report — 주간업무 보고서(PPT) 자동 작성 스킬

지난주 보고서 PPT와 구분별 누적 진척률 4개 · 이번주 실적 · 차주 계획을 넣으면 기존 양식 그대로 채운 주간업무 보고서 PPT(W1 평소 8장 · W2 월말 12장)가 나오는 스킬

## 한눈에 보기

| <div align="center"><sub>항목</sub></div> | <sub>내용</sub> |
|:---|:---:|
| <sub>목적</sub> | <sub>매주 쓰는 주간업무 보고서를 기존 PPT 양식 그대로 채우고, 손으로 하던 진척률 계산 자동화</sub> |
| <sub>이럴 때 사용</sub> | <sub>주간보고 · 주간 실적 보고 작성 · 월말 마지막 주 월간 결산 포함 보고 · 첫 주 보고서 시작</sub> |
| <sub>넣는 것</sub> | <sub>W1/W2 선택 · 지난주 보고서 PPT(없으면 빈 양식) · 구분별 누적 % 4개(지난주 실적 · 이번주 목표 · 이번주 실적 · 차주 목표) · 업무구분별 이번주 실적 · 차주 계획 · 관련 산출물 · 주요 이슈 · (있으면) 지연 사유 · 캐치업 방안 · (W2) 월간 결산 내용</sub> |
| <sub>나오는 것</sub> | <sub>`<프로젝트명>_주간보고서_<W1 또는 W2>_<YYYYMMDD>.pptx` + 「이번주 누적 진척률 N%」 요약</sub> |
| <sub>부르는 법</sub> | <sub>`주간보고서 만들어줘` · `이번주 주간보고 작성해줘` · `W1 보고서 써줘` · `W2로 월말 보고서 만들어줘` 등 · 주간보고 관련 요청이면 스킬 이름 없이도 동작 · 슬래시 명령 `/weekly-report`</sub> |
| <sub>핵심 원칙</sub> | <sub>양식 보존 · 계산은 스크립트 · 모르는 칸은 빈칸 — 지난주 파일 복사 후 바뀐 셀만 교체</sub> |
| <sub>제작</sub> | <sub>신지은 (GitHub [jieun994](https://github.com/jieun994)) · 이 리포 이관 2026.07.21</sub> |
| <sub>출처</sub> | <sub>[jieun994/zinis_claude_skills](https://github.com/jieun994/zinis_claude_skills) · 원본 경로 `skills/weekly-report/`</sub> |
| <sub>연계</sub> | <sub>호출 하네스 미지정 · 단독 사용</sub> |

W1 / W2 양식

| <div align="center"><sub>양식</sub></div> | <sub>용도</sub> | <sub>분량</sub> |
|:---|:---:|:---:|
| <sub>W1</sub> | <sub>평소 주간보고</sub> | <sub>8장</sub> |
| <sub>W2</sub> | <sub>월말 마지막 주 보고 — W1과 같게 시작 + 뒤에 「월간 결산」 4장(전체 진척률 · 주요 성과 · 이슈 및 리스크 · 익월 목표)</sub> | <sub>12장</sub> |

## 이렇게 요청

| <div align="center"><sub>상황</sub></div> | <sub>요청 예시</sub> | <sub>나오는 것</sub> |
|:---|:---:|:---:|
| <sub>평소 주간보고</sub> | <sub>`이번주 주간보고서 만들어줘`</sub> | <sub>W1 보고서(월말 주면 W2 추천)</sub> |
| <sub>월말 마지막 주</sub> | <sub>`지난주 보고서 첨부했어. 이번주 W2로 작성해줘`</sub> | <sub>W2 보고서(월간 결산 4장 포함)</sub> |
| <sub>실적 보고</sub> | <sub>`주간 실적 보고서 만들어줘`</sub> | <sub>W1/W2 선택 후 보고서</sub> |
| <sub>양식을 정해 둔 경우</sub> | <sub>`W1 보고서 써줘` · `W2로 월말 보고서 만들어줘`</sub> | <sub>지정 양식 보고서</sub> |
| <sub>첫 주(지난주 파일 부재)</sub> | <sub>`주간보고서 만들어줘`</sub> | <sub>빈 양식 기반 보고서 · 지난주 실적 `0`</sub> |

입력 예시 (대화창에 한 번에 붙여넣기)

```
W2로 만들어줘. 지난주 보고서는 weekly_W1.pptx 야

[진척률 누적 %]
전체:  지난주 2.1 / 이번주목표 7.3 / 이번주실적 6.9 / 차주목표 11.8
기획:  지난주 3.7 / 이번주목표 6.5 / 이번주실적 7.0 / 차주목표 19.0
개발:  지난주 2.9 / 이번주목표 22.3 / 이번주실적 20.5 / 차주목표 29.0

[이번주 실적 / 차주 계획]
프로젝트 관리 - 이번주: WBS 현행화, 주간보고 / 차주: 요구사항 확정 대기
개발 - 이번주: 인터페이스 분석 / 차주: 코어 API 설계

[이슈] 요청: 요구사항 확정 / 이슈: 없음
```

## 진행 단계

```
① W1/W2 결정 → ② 베이스 파일 확보 → ③ 지난주 값 읽기 → ④ 내용 입력 → ⑤ 진척률 자동 계산 → ⑥ 보고서 생성
```

| <div align="center"><sub>단계</sub></div> | <sub>하는 일</sub> | <sub>사용자 할 일</sub> | <sub>결과물</sub> |
|:---|:---:|:---:|:---:|
| <sub>① W1/W2 결정</sub> | <sub>오늘이 그 달 마지막 주면 W2(월간 결산 포함) 추천 · 아니면 W1 기본 · 사용자가 「W2로」 · 「이번이 마지막 주야」라고 하면 그대로</sub> | <sub>**W1 · W2 선택 확정**</sub> | <sub>양식</sub> |
| <sub>② 베이스 파일 확보</sub> | <sub>지난주 보고서 PPT를 베이스로 복사 · 첫 주 · 파일이 없으면 `assets/W1_blank.pptx` · `assets/W2_blank.pptx`</sub> | <sub>지난주 PPT 첨부 · 경로 제공</sub> | <sub>베이스 PPT</sub> |
| <sub>③ 지난주 값 읽기</sub> | <sub>`weekly_report.py read` → 구분별 누적 실적 · 업무구분 목록 · 주차 라벨(예 「6월 4주차」) 추출</sub> | <sub>—</sub> | <sub>이번주 「지난주 실적」 기본값 · 입력 행 목록</sub> |
| <sub>④ 내용 입력</sub> | <sub>진척률 4개 · 실적/계획 텍스트 · 이슈 · 지연 사유 · (W2) 월간 결산 수집 · 주차 라벨 · 기간 · 보고 날짜는 날짜 기준 자동 입력 후 확인</sub> | <sub>**값 입력 · 자동 날짜 확인** (빈 칸은 빈 칸 유지)</sub> | <sub>`data.json`</sub> |
| <sub>⑤ 진척률 계산</sub> | <sub>누적 % 4개 → 표 6칸 계산(아래 공식) · 직접 암산 입력 금지</sub> | <sub>—</sub> | <sub>진척률 표</sub> |
| <sub>⑥ 보고서 생성</sub> | <sub>`weekly_report.py build` → 바뀐 셀만 교체 · W2인데 베이스에 월간 결산이 없으면(지난주 W1 파일 등) `assets/w2_monthly.pptx`의 4장을 #Appendix 앞에 자동 추가</sub> | <sub>결과 PPT 검토 · 결재</sub> | <sub>보고서 PPT + 누적 진척률 안내</sub> |

입력 항목

- **진척률(누적 %)** — 구분(전체 · 기획 · 디자인 · 퍼블리싱 · 개발 · 검증·릴리즈)마다 `지난주 실적` · `이번주 목표` · `이번주 실적` · `차주 목표` · 첫 주 지난주 실적 = `0` · 해당 없는 구분(예: 아직 미투입 디자인) = `-`
- **주간 실적 · 차주 계획** — 업무구분별 이번주 실적 · 차주 계획 + 관련 산출물 · 여러 줄은 줄바꿈 구분
- **주요 이슈** — 요청 사항 · 이슈 사항
- **지연 사유 · 캐치업 방안** — 있을 때만
- **W2 전용 월간 결산** — 월 전체 · 업무별 진척률 · 주요 성과 · 이슈 및 리스크 · 익월 목표

### 진척률 계산 방식

| <div align="center"><sub>표의 칸</sub></div> | <sub>계산식</sub> | <sub>예시(지난주 2.1 / 이번주목표 7.3 / 이번주실적 6.9 / 차주목표 11.8)</sub> |
|:---|:---:|:---:|
| <sub>주간 계획</sub> | <sub>이번주 목표 − 지난주 실적</sub> | <sub>5.2%</sub> |
| <sub>주간 실적</sub> | <sub>이번주 실적 − 지난주 실적</sub> | <sub>4.8%</sub> |
| <sub>누적 계획</sub> | <sub>이번주 목표</sub> | <sub>7.3%</sub> |
| <sub>누적 실적</sub> | <sub>이번주 실적</sub> | <sub>6.9%</sub> |
| <sub>차주 주간</sub> | <sub>차주 목표 − 이번주 실적</sub> | <sub>4.9%</sub> |
| <sub>차주 누적</sub> | <sub>차주 목표</sub> | <sub>11.8%</sub> |

- 사용자가 손으로 하던 계산과 같은 공식 · 표기는 소수 첫째 자리(예 5.2%) 고정
- 숫자가 아니거나 빈 입력 = 해당 칸 `-` + 「진척률은 직접 확인 필요」 안내 · 보고서 생성은 계속
- W2 월간 진척률 6열 순서: 당월계획 · 당월실적 · 누적계획 · 누적실적 · 익월계획 · 익월누적

## 산출물

| <div align="center"><sub>파일</sub></div> | <sub>형식</sub> | <sub>구성</sub> |
|:---|:---:|:---:|
| <sub>`<프로젝트명>_주간보고서_W1_<YYYYMMDD>.pptx`</sub> | <sub>pptx 8장</sub> | <sub>표지 · 전체 일정(간트) · 진척 현황 · 주간 실적 및 차주 계획 · 주요 이슈 · #Appendix(이슈 관리 대장) · End of Document</sub> |
| <sub>`<프로젝트명>_주간보고서_W2_<YYYYMMDD>.pptx`</sub> | <sub>pptx 12장</sub> | <sub>W1 구성 + 「○월 진척 상황 보고」 월간 결산 4장(진척률 · 주요 성과 · 이슈 및 리스크 · 익월 목표)</sub> |

- 결과 = PowerPoint(.pptx) · 열어서 바로 검토 · 결재 가능
- 파일명에 주차 · 날짜가 들어가 충돌이 적은 구조 · 같은 주차 파일이 이미 있으면 덮어쓰기 전 확인
- 실제 결과물: `samples/주간보고서_결과예시_W1.pptx`(평소 주간보고 8장) · `samples/주간보고서_결과예시_W2.pptx`(월말 보고 12장, 월간 결산 포함)

### 옵션

| <div align="center"><sub>설정</sub></div> | <sub>기본값</sub> | <sub>변경 방법</sub> |
|:---|:---:|:---:|
| <sub>양식 버전</sub> | <sub>날짜로 W1/W2 추천</sub> | <sub>① 단계에서 사용자 선택</sub> |
| <sub>베이스 파일</sub> | <sub>지난주 보고서 복사</sub> | <sub>없으면 `assets/W1_blank.pptx` · `assets/W2_blank.pptx`</sub> |
| <sub>출력 파일명</sub> | <sub>`<프로젝트명>_주간보고서_<W1 또는 W2>_<YYYYMMDD>.pptx`</sub> | <sub>`data.json`의 `output_file`</sub> |
| <sub>진척률 표기</sub> | <sub>소수 첫째 자리(예 5.2%)</sub> | <sub>스크립트 고정</sub> |

## 설치 · 단독 사용

```bash
cp -r skills/weekly-report ~/.claude/skills/weekly-report
```

- 리포 루트 기준 명령 · 스킬 일괄 설치는 원본 리포 `bash install-global.sh` · 공유 리포 `share/update.sh`
- 의존성: Python 3 + `python-pptx`(`weekly_report.py`의 PPT 읽기 · 쓰기 · `pip install python-pptx`)
- 실행은 Claude 담당 — `python scripts/weekly_report.py read <지난주 보고서.pptx>` · `python scripts/weekly_report.py build <data.json>`
- 하네스 안에서: 이 스킬을 호출하는 하네스 미지정 · `sync-skills`가 전체 스킬을 `agent/proposal` · `agent/feature-spec-sb` · `agent/test-runner`의 `.claude/skills/`로 복사하므로 그 폴더 세션에서도 사용 가능

## 폴더 구성

```
skills/weekly-report/
├── SKILL.md                         Claude 작동 정본 (6단계 워크플로 · 예외 처리 · 설정)
├── README.md                        사람용 안내 (이 문서)
├── scripts/weekly_report.py         read(지난주 값 추출) · build(보고서 생성 · 진척률 계산 · W2 월간 결산 추가)
├── assets/
│   ├── W1_blank.pptx                W1 빈 시작 템플릿(8장, 회사 데이터 미포함)
│   ├── W2_blank.pptx                W2 빈 시작 템플릿(12장, 회사 데이터 미포함)
│   └── w2_monthly.pptx              W1 베이스로 W2를 만들 때 덧붙이는 월간 결산 4장
├── samples/
│   ├── 주간보고서_결과예시_W1.pptx
│   └── 주간보고서_결과예시_W2.pptx
└── .claude-plugin/plugin.json       플러그인 정보 (제작자 신지은)
```

## 주의

- 양식 보존 — 베이스 PPT의 서식 · 레이아웃 · 간트는 그대로 두고 값이 바뀌는 셀만 교체
- 베이스 파일 방식 이유 — 전체 일정(간트) · 서식 · 누적치 유지 + 회사 데이터 외부 반출 방지
- 계산은 스크립트 담당 — 진척률 6칸 직접 암산 입력 금지(불일치 방지) · 진척률은 입력값 기반이므로 입력값 재확인
- 모르면 빈칸 — 입력이 없는 칸은 지어내지 않고 빈 칸 위치 안내 후 재생성 여부 확인
- 구분 키는 베이스 표의 구분명과 느슨하게 매칭(괄호 · 공백 차이 허용) · `read`가 뽑은 업무구분 목록 사용이 안전
- 양식 · 템플릿을 못 찾을 때 = 경로 재확인 · 수집한 입력은 `data.json`으로 보존
- HTML 하우스 스타일 비대상 — pptx 자체 양식 유지(global-house-style 규칙)

## 릴리즈노트

| <div align="center"><sub>요약내용</sub><img width="1" height="1"></div> | <sub>업데이트 일자</sub><img width="1" height="1"> | <sub>소유자</sub><img width="45" height="1"> |
|:---|:---:|:---:|
| <sub>README 전면 개편 — 목적 · 넣는 것 · 산출물 형태 · 요청 예시 · 진행 단계 순으로 재구성, 릴리즈노트 맨 아래로 이동</sub> | <sub>2026.11.13</sub> | <sub>김단영</sub> |
| <sub>최초 등록 — 신지은 스킬 이관 (jieun994/zinis_claude_skills)</sub> | <sub>2026.07.21</sub> | <sub>신지은</sub> |
