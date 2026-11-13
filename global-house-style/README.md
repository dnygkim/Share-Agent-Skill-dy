# global-house-style — HTML 하우스 스타일 · 전역 규칙 정본

별도 요청이 없을 때 모든 HTML 산출물(분석서 · 리포트 · PRD · 제안 덱)에 쓰는 하우스 스타일과, 모든 세션에 걸리는 전역 규칙(문체 · 파일명 등)의 Git 정본 사본. 실제 적용 위치는 `~/.claude/`

## 한눈에 보기

| <div align="center"><sub>항목</sub></div> | <sub>내용</sub> |
|:---|:---:|
| <sub>**목적**</sub> | <sub>일반 대화 · 하네스 · 스킬의 HTML 산출물 모양을 하나로 통일(2026.08.27) + 전역 규칙을 여러 PC에서 같게 유지</sub> |
| <sub>**정체**</sub> | <sub>하네스 아님 — `~/.claude/house-style/` · `~/.claude/CLAUDE.md`의 사본을 버전관리하는 폴더. 이 폴더 자체의 실행 기능 부재</sub> |
| <sub>**적용 범위**</sub> | <sub>HTML 산출물 전부(문서형 · 슬라이드형). pptx · xlsx · docx는 각 스킬 규격 사용</sub> |
| <sub>**스타일**</sub> | <sub>warm paper(`#F1EDE5`) + near-black ink 2톤 · Pretendard / Paperlogy · 강조는 색 대신 반전(ink 바탕 + paper 글자) · 어절 단위 줄바꿈 · A4 인쇄 대응</sub> |
| <sub>**설치**</sub> | <sub>원본 리포 `bash install-global.sh` · 공유 리포 `bash share/update.sh` — 아래 「설치」</sub> |
| <sub>**기준본**</sub> | <sub>`신승-비즈니스AI플래너_권한정책매트릭스_초안(260810).html` (토프바 + LNB + 표지 + 목차 + 섹션 + footer)</sub> |

## 이렇게 요청

| <div align="center"><sub>상황</sub></div> | <sub>요청 예시</sub> | <sub>나오는 것</sub> |
|:---|:---:|:---:|
| <sub>일반 대화에서 문서형 HTML</sub> | <sub>`이 분석 내용 HTML 리포트로 정리해줘`</sub> | <sub>문서형 골격 하우스 스타일 단일 HTML — 확인 질문 없이 기본 적용</sub> |
| <sub>하네스 · 스킬의 HTML 추출</sub> | <sub>인테이크 질문 「기본 스타일로 추출할까요?」에 `기본으로` · `네` · `알아서`</sub> | <sub>하우스 스타일 — 무응답 · 일괄 진행이어도 같은 기본 양식</sub> |
| <sub>고객사 CI 컬러 적용</sub> | <sub>`CI 적용해줘` · `Primary #0050AA로 뽑아줘`</sub> | <sub>§2b 오버라이드 — 포인트 색 + 바탕 · 선 · 보조 글자색까지 CI 계열 저채도 중립색</sub> |
| <sub>수치 · 일정 시각화</sub> | <sub>`그래프로 표현해줘`</sub> | <sub>§23 막대 · 마일스톤(D-day) 그래프 + 같은 수치 표</sub> |
| <sub>출처가 있는 리서치 문서</sub> | <sub>`출처 링크 걸어줘`(리서치 산출물은 기본 적용)</sub> | <sub>§22 `a.ext` — 항목 타이틀 · 구절에 외부링크, hover 반전 · 끝 아이콘</sub> |

## 진행 단계 (HTML 산출물이 만들어지는 순서)

```
① 골격 선택 → ② 정본 CSS 인라인 → ③ 고정 영역 그대로 → ④ 콘텐츠 컴포넌트 선택 → ⑤ 스타일 확인 → ⑥ 수정 이력 기록
```

| <div align="center"><sub>단계</sub></div> | <sub>하는 일</sub> | <sub>사용자 할 일</sub> | <sub>결과물</sub> |
|:---|:---:|:---:|:---:|
| <sub>① 골격 선택</sub> | <sub>산출물 성격에 맞춰 문서형(롱스크롤 + A4) · 슬라이드형(덱) 중 하나</sub> | <sub>—</sub> | <sub>골격 파일</sub> |
| <sub>② 정본 CSS 인라인</sub> | <sub>`house-style.css` 전문을 `<style>`에 그대로 삽입 — 외부 `.css` 링크 금지(자기완결 단일 파일)</sub> | <sub>—</sub> | <sub>단일 HTML</sub> |
| <sub>③ 고정 영역</sub> | <sub>GNB(토프바) · LNB · 표지 · 목차 · footer 구조와 스타일 그대로 사용</sub> | <sub>—</sub> | <sub>공통 틀</sub> |
| <sub>④ 콘텐츠 선택</sub> | <sub>「콘텐츠 컴포넌트 팔레트」에서 내용 성격에 맞는 것만 골라 조합 — 팔레트 통째 나열 금지, 섹션마다 조합 상이 가능</sub> | <sub>—</sub> | <sub>섹션 본문</sub> |
| <sub>⑤ 스타일 확인</sub> | <sub>하네스 · 스킬 세션은 추출 직전 「기본 스타일로 추출할까요?」 1회 확인 — CI를 답하면 그때 HEX 확정</sub> | <sub>**기본 / CI 선택**</sub> | <sub>확정 스타일</sub> |
| <sub>⑥ 수정 이력</sub> | <sub>갱신 · 배포 때마다 `<head>`의 `<meta name="revision">` 날짜 갱신 + 수정 이력 주석 맨 위에 한 줄 추가</sub> | <sub>—</sub> | <sub>메타정보</sub> |

## 산출물 골격 2종

| <div align="center"><sub>골격</sub></div> | <sub>파일</sub> | <sub>쓰는 곳</sub> |
|:---|:---:|:---:|
| <sub>문서형 (롱스크롤 + A4 인쇄)</sub> | <sub>`base_template_doc.html`</sub> | <sub>일반 대화 리포트 · `agent/prd` PRD · `agent/proposal` S1 분석 보고서(문서형 기반 `../agent/proposal/template/rfp_report_template.html`)</sub> |
| <sub>슬라이드형 (덱)</sub> | <sub>`../agent/proposal/template/base_template.html`</sub> | <sub>`agent/proposal` · `skills/proposal-slide-builder`</sub> |

- 슬라이드형은 정본의 §1 서체 · §2 토큰만 복제(`../agent/proposal/template/slide-tokens.css`)하고 슬라이드 전용 규칙은 자기 `<style>`에 보관
- **값을 바꿀 곳은 언제나 정본 `house-style.css` 하나** — 앵커 `scroll-margin-top` · LNB sticky 위치도 정본이 처리, 산출물에서 덧대기 금지

## house-style.css 구성

| <div align="center"><sub>§</sub></div> | <sub>내용</sub> | <sub>비고</sub> |
|:---|:---:|:---:|
| <sub>1 · 2 · 2b</sub> | <sub>서체 · 토큰 · CI 오버라이드</sub> | <sub>CI는 요청 시에만 §2b로</sub> |
| <sub>3 ~ 9</sub> | <sub>리셋 · 본문 · 토프바 · LNB 레이아웃 · 표지 · 목차 · 섹션 · 콘셉트 문장</sub> | <sub>고정 영역</sub> |
| <sub>10 ~ 17</sub> | <sub>표 · 진단 박스 · 루프 / 플로우 도식 · 계층 트리(IA) · 모듈 · 노트 · 등급 목록 · 마무리 · mermaid</sub> | <sub>콘텐츠 팔레트</sub> |
| <sub>18 · 19</sub> | <sub>반응형 · A4 인쇄</sub> | <sub>공통</sub> |
| <sub>20 · 21</sub> | <sub>요약 스탯 그리드 · 간트 / 타임라인</sub> | <sub>수치 리포트 확장</sub> |
| <sub>22</sub> | <sub>출처 · 고유명사 외부링크 `a.ext`</sub> | <sub>리서치 · 분석 문서</sub> |
| <sub>23</sub> | <sub>막대 · 마일스톤 그래프(`.hbars` · `.cols` · `.ms` · 간트 마감 표시)</sub> | <sub>리서치 · 분석 문서</sub> |

## 전역 규칙 (CLAUDE.md)

`CLAUDE.md` = `~/.claude/CLAUDE.md` 사본. 별도 요청이 없으면 모든 세션에 적용

| <div align="center"><sub>규칙</sub></div> | <sub>요지</sub> |
|:---|:---:|
| <sub>HTML 산출물 하우스 스타일</sub> | <sub>위 골격 · 토큰 기본 적용, 콘텐츠 컴포넌트는 내용에 맞춰 선택, 클라이언트 CI는 옵트인(CI를 얹으면 콘텐츠 영역도 CI 톤)</sub> |
| <sub>거버닝 메시지 문체</sub> | <sub>장표 · 섹션 헤드라인 = 20~30자 짧은 상태 묘사, 수치는 본문으로, 본문은 명사형 종결 · 어절 단위 줄바꿈 · 출처 외부링크</sub> |
| <sub>산출물 파일명</sub> | <sub>공식 `프로젝트코드-단계코드-문서명-버전-작성일자` · 업무 `업무명-문서명-버전-작성일자`, 버전 v0.1~v0.8 작성 · v0.9 PM 검토 · v1.0 고객 확정</sub> |
| <sub>자동화 창은 서브모니터로</sub> | <sub>브라우저 · 앱 자동화 창은 주 모니터를 가리지 않게 서브모니터 새 창에서 진행</sub> |
| <sub>HTML 수정 이력 메타정보</sub> | <sub>HTML 갱신 · 배포 때마다 `<head>`에 수정 페이지 · 내역 한 줄 기록</sub> |
| <sub>Dan Jr. 페르소나</sub> | <sub>승인 게이트 직전 `persona.md` 등급 조회 — 원본 리포 전용, 공유 리포 판본에서는 제외</sub> |

## 설치

| <div align="center"><sub>리포</sub></div> | <sub>명령</sub> | <sub>하는 일</sub> |
|:---|:---:|:---:|
| <sub>원본 `dykim-claude-agents-skills`</sub> | <sub>`bash install-global.sh`</sub> | <sub>`house-style.css` · `base_template_doc.html` → `~/.claude/house-style/`, `CLAUDE.md` → `~/.claude/CLAUDE.md`(내용이 다르면 `.bak-날짜시각` 백업 후 교체), 스킬 · 메모리도 함께</sub> |
| <sub>공유 `Share-Agent-Skill-dy`</sub> | <sub>`bash share/update.sh`</sub> | <sub>같은 두 파일 + `CLAUDE.md` → `~/.claude/house-style/global-rules.md`, 기존 `~/.claude/CLAUDE.md` 끝에 불러오기 한 줄만 추가</sub> |

- Windows는 Git Bash에서 실행
- 손 설치: `house-style.css` · `base_template_doc.html`을 `~/.claude/house-style/`에 복사 → `CLAUDE.md` 내용을 `~/.claude/CLAUDE.md`에 반영(파일이 없으면 복사, 있으면 병합 — 전역 파일에 다른 개인 규칙 공존 가능)
- 설치 후에는 어느 프로젝트 폴더에서 Claude Code를 열어도 적용, 새로 여는 세션부터 반영

## 동기화 규칙

- `~/.claude/house-style/*` · `~/.claude/CLAUDE.md`를 고치면 **이 폴더에도 같은 내용 반영 후 커밋** — 로컬만 고치면 백업이 낡은 상태로 남음
- 산출물이 어긋나면 산출물이 아니라 정본(`house-style.css`)을 수정

## 하네스 · 스킬과의 관계

2026.08.27부터 하네스 · 스킬이 모두 이 정본을 공유. 하네스별 자체 팔레트(제안서 CI 5색 · PRD `--brand` 그라데이션 대시보드)는 은퇴

| <div align="center"><sub>대상</sub></div> | <sub>골격</sub> | <sub>스타일 규약 위치</sub> |
|:---|:---:|:---:|
| <sub>일반 대화</sub> | <sub>문서형</sub> | <sub>`~/.claude/CLAUDE.md`</sub> |
| <sub>`agent/prd`</sub> | <sub>문서형</sub> | <sub>`agent/prd/references/master-prompt-v2.0.md` [HTML 산출물 사양] · `CLAUDE.md` 인테이크 ⑥</sub> |
| <sub>`agent/proposal`</sub> | <sub>슬라이드형 + 문서형(S1 보고서)</sub> | <sub>`agent/proposal/references/design-system.md` §2 · `CLAUDE.md` ③ — 고객사 로고 Primary 컬러 기본 적용(이 하네스의 상시 지시)</sub> |
| <sub>`skills/proposal-slide-builder`</sub> | <sub>슬라이드형</sub> | <sub>`SKILL.md` 3 · `references/design-system.md` §2</sub> |

- **HTML이 아닌 산출물은 대상 외** — pptx(`deckslide-design-guideline` · `weekly-report`) · xlsx(`wbs-generator` · `requirements-generator` · `meeting-minutes` · `ia-builder`) · docx는 각자 규격
- 코드 스니펫 · 웹앱 UI 프로토타입 · 랜딩페이지 · 포스터처럼 문서가 아닌 산출물은 강제하지 않고 방향 확인

## 구성

```
global-house-style/
├── CLAUDE.md               전역 규칙 — ~/.claude/CLAUDE.md 와 같은 내용
├── house-style.css         스타일 정본 (§1~19 공통 · §20~23 확장: 요약 스탯 · 간트 · 외부링크 · 그래프)
├── base_template_doc.html  문서형 골격 + 「콘텐츠 컴포넌트 팔레트」 견본
└── README.md               이 문서
```

## 릴리즈노트

| <div align="center"><sub>요약내용</sub><img width="1" height="1"></div> | <sub>업데이트 일자</sub><img width="1" height="1"> | <sub>소유자</sub><img width="45" height="1"> |
|:---|:---:|:---:|
| <sub>README 전면 개편 — 목적 · 넣는 것 · 산출물 형태 · 요청 예시 · 진행 단계 순으로 재구성, 릴리즈노트 맨 아래로 이동</sub> | <sub>2026.11.13</sub> | <sub>김단영</sub> |
| <sub>막대 · 마일스톤 그래프 컴포넌트 추가(`house-style.css` §23) — 수치 비교 `.hbars` · 시점 추이 `.cols` · 발주 일정 D-day `.ms` · 간트 마감 표시 `.gbar.mk`. 계열 하나 · 강조 막대만 `.key`(CI 문서는 포인트 색) · 같은 수치는 표로도 남김 · 인쇄 시 막대 색 유지. `base_template_doc.html` 팔레트에 견본 추가 — 2026.11.11 「그래프로 표현」 지시, 삼성자산운용 FunETF RFP 분석 v0.3에 첫 적용</sub> | <sub>2026.11.11</sub> | <sub>김단영</sub> |
| <sub>외부링크 아이콘을 블랙 라인(투명도 제거)으로 변경하고, 본문 고유명사(사이트 · 서비스 · 기관 · 도구)도 같은 `a.ext`로 연결하는 규칙을 `house-style.css` §22에 명시 — 2026.11.10 지시, `~/.claude/house-style/` 사본과 동일 유지</sub> | <sub>2026.11.10</sub> | <sub>김단영</sub> |
| <sub>전역 규칙 3종 동기화 — 산출물 파일명 원문 대조 보강(단계코드 · 문서번호 · 확정본 보존 · 개정이력 · 적용 제외)·자동화 창은 서브모니터로·HTML 산출물 수정 이력 메타정보(모두 2026.10.28 지시). Windows PC `~/.claude/CLAUDE.md` 기준 반영 — Dan Jr. 절의 리포 전용 문구(전역 규칙 없는 환경 · 클라우드 세션 안내) 유지</sub> | <sub>2026.11.06</sub> | <sub>김단영</sub> |
| <sub>출처 외부링크 규칙 추가 — 리서치·분석 문서는 출처 URL을 항목 타이틀(1건)·해당 구절(2건 이상)에 직접 연결. `house-style.css` §22 `a.ext`(옅은 밑줄 · 끝 외부링크 아이콘 · hover 반전 · 인쇄 시 아이콘 숨김) · `.src-tag`, `base_template_doc.html` 팔레트 · 출처 표 예시, 전역 규칙 「출처 외부링크」 절 — 메리츠화재 RFP 분석 보고서에서 확정</sub> | <sub>2026.10.19</sub> | <sub>김단영</sub> |
| <sub>전역 규칙 3종 동기화 — 거버닝 메시지 문체(2026.09.11)·어절 단위 줄바꿈(2026.09.17)·산출물 파일명 두 트랙(2026.10.01). `house-style.css` §3 `word-break:keep-all`·제목 `text-wrap:balance` 반영 — 8/27 이후 `~/.claude/` 에만 있던 변경분</sub> | <sub>2026.10.09</sub> | <sub>김단영</sub> |
| <sub>확인 생략 시 폴백 명문화 — 스타일 확인 질문 없이 진행되면(무응답·일괄 진행·비대화형) 하네스/스킬에 정의된 기본 양식으로 작성, 임의 스타일·보류 금지</sub> | <sub>2026.08.27</sub> | <sub>김단영</sub> |
| <sub>HTML 기본 스타일 전면 통일 — `agent/proposal`(슬라이드형)·`agent/prd`(문서형)·`proposal-slide-builder` 가 이 정본을 공유. 자체 팔레트(CI 5색·`--brand` 대시보드) 은퇴 · CI 옵트인 · 하네스는 추출 전 기본 스타일 확인</sub> | <sub>2026.08.27</sub> | <sub>김단영</sub> |
| <sub>LNB 상단 정렬(`margin-top:0`)·앵커 목적지 보정(`[id]{scroll-margin-top}`)·목차 `#s0` 목적지 신설 — KOMCA RFI 분석서에서 손으로 덧댄 보정을 정본으로 흡수</sub> | <sub>2026.08.27</sub> | <sub>김단영</sub> |
| <sub>최초 등록 — `~/.claude/house-style/` + `~/.claude/CLAUDE.md`의 Git 백업/정본</sub> | <sub>2026.08.20</sub> | <sub>김단영</sub> |

