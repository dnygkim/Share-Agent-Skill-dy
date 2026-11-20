# rfp-analysis-research — RFP 분석 · 리서치 스킬 (제안서 1단계)

RFP/RFI 문서를 넣으면 요구사항 구조화 결과(발주기관 · 사업 개요 · 요구사항 · 평가 기준 · 제출 요건 · 리스크)와 출처를 단 산업 · 경쟁사 · 기술 트렌드 리서치가 나오는 제안서 작성 전 기초 분석 스킬

## 한눈에 보기

| <div align="center"><sub>항목</sub></div> | <sub>내용</sub> |
|:---|:---:|
| <sub>목적</sub> | <sub>RFP 요구사항의 빠짐없는 구조화 + 제안 근거가 될 업계 · 경쟁사 · 기술 자료 확보</sub> |
| <sub>이럴 때 사용</sub> | <sub>RFP/RFI를 받은 직후 · 제안 착수 전 요구사항 · 평가 구조 파악 · 경쟁사 · 유사 사례 벤치마킹 자료가 필요할 때</sub> |
| <sub>넣는 것</sub> | <sub>RFP/RFI 문서(업로드 또는 파일 경로) · 클라이언트 사이트 등 참고 URL(있으면)</sub> |
| <sub>나오는 것</sub> | <sub>요구사항 구조화 6항목 + 현황분석 · 리서치 4항목(항목마다 출처 병기)<br>기본 = 대화 응답(마크다운 표 · 목록) · 요청 시 HTML 문서(본문 항목에 출처 하이퍼링크)</sub> |
| <sub>부르는 법</sub> | <sub>`이 RFP 분석해줘` 같은 요청 · 슬래시 명령 `/rfp-analysis-research`</sub> |
| <sub>제작</sub> | <sub>김단영(dykim)</sub> |
| <sub>연계</sub> | <sub>제안 스킬 파이프라인 **①**(아래 표) · 하네스 [agent/proposal](../../agent/proposal/) S1 단계의 `rfp-analyst`가 이 스킬 우선 호출</sub> |

**제안 스킬 파이프라인 · agent/proposal 단계 대응**

| <div align="center"><sub>순서</sub></div> | <sub>스킬</sub> | <sub>하는 일</sub> | <sub>agent/proposal 단계 · 에이전트</sub> |
|:---|:---:|:---:|:---:|
| <sub>**①**</sub> | <sub>**`rfp-analysis-research`(이 스킬)**</sub> | <sub>RFP 구조화 + 업계 리서치</sub> | <sub>S1 RFP 분석 · 리서치 · `rfp-analyst`</sub> |
| <sub>②</sub> | <sub>[`ux-journey-insight`](../ux-journey-insight/README.md)</sub> | <sub>사용자 여정맵 + UX 개선 전략</sub> | <sub>S1 선택 모듈 · `ux-strategist`</sub> |
| <sub>③</sub> | <sub>[`proposal-structure-validation`](../proposal-structure-validation/README.md)</sub> | <sub>목차 구성 + 자기검증</sub> | <sub>S3 제안 목차(GATE ②) · `structure-validator`</sub> |
| <sub>④</sub> | <sub>[`proposal-slide-builder`](../proposal-slide-builder/README.md)</sub> | <sub>본문 슬라이드 제작</sub> | <sub>S4 1차 추출 · S6 n차 추출 · `slide-builder`</sub> |

> 하네스의 S2 컨셉 · S5 피드백 반영 · S7 최종본은 이 4개 스킬 밖의 에이전트 단계 — 전체 7단계 흐름 = [agent/proposal/README.md](../../agent/proposal/README.md)

## 이렇게 요청

| <div align="center"><sub>상황</sub></div> | <sub>요청 예시</sub> | <sub>나오는 것</sub> |
|:---|:---:|:---:|
| <sub>RFP를 받은 직후 기초 분석</sub> | <sub>`이 RFP 분석해줘`</sub> | <sub>요구사항 구조화 6항목 + 현황분석 · 리서치 4항목</sub> |
| <sub>경쟁사 · 유사 사례 조사 강화</sub> | <sub>`RFP 분석하고 같은 업계 경쟁사 사례까지 리서치해줘`</sub> | <sub>동일 산업군 경쟁사 · 유사 사례 벤치마킹 3건 이상(출처 병기) 포함 결과</sub> |
| <sub>공유용 HTML 문서</sub> | <sub>`RFP 분석 결과 HTML 문서로 뽑아줘`</sub> | <sub>HTML 문서 · 출처 URL을 본문 항목에 하이퍼링크 · 본문 미연결 출처 완료 보고</sub> |
| <sub>제안서 하네스 안</sub> | <sub>`RFP 분석 보고서만 뽑아줘`(agent/proposal 폴더에서)</sub> | <sub>S1 산출물 `01_rfp.md` + 분석 보고서 HTML</sub> |

## 진행 단계

```
① RFP 파싱 · 요구사항 구조화 → ② 현황분석 · 리서치 → ③ (HTML 요청 시) 출처 하이퍼링크 · 미연결 출처 보고
```

| <div align="center"><sub>단계</sub></div> | <sub>하는 일</sub> | <sub>사용자 할 일</sub> | <sub>결과물</sub> |
|:---|:---:|:---:|:---:|
| <sub>① RFP 파싱 · 요구사항 구조화</sub> | <sub>발주기관 정보(기관명 · 산업군 · 규모) · 사업 개요(사업명 · 기간 · 예산 범위) · 핵심 요구사항(기능/비기능 구분) · 평가 기준 및 배점 구조 · 제출 요건(목차 지정 여부 · 페이지 제한 · 필수 항목) · 리스크 요인 추출<br>RFP에 없지만 일반적으로 필요한 항목은 `[보완 필요]` 표기</sub> | <sub>RFP/RFI 문서 전달</sub> | <sub>요구사항 구조화 결과</sub> |
| <sub>② 현황분석 · 리서치</sub> | <sub>① 기반 조사 — 산업 디지털 트랜스포메이션 트렌드 · 주요 이슈, 클라이언트 현재 서비스/플랫폼 상태 · 공개 사업 히스토리, 동일 산업군 경쟁사/유사 사례 벤치마킹 3건 이상, 적용 가능한 최신 기술 · 방법론<br>항목마다 출처(URL 또는 보고서명) 병기 · 검증 불가 정보는 `[미검증]`</sub> | <sub>결과 검토 · 추가 조사 요청</sub> | <sub>리서치 결과</sub> |
| <sub>③ HTML 산출(요청 시)</sub> | <sub>출처 URL을 `[S번호]` 태그 · 출처 표에만 두지 않고 본문 항목에 `a.ext` 링크 — 출처 1건 = 항목 타이틀, 2건 이상 = 각 출처가 뒷받침하는 구절<br>본문 고유명사(사이트 · 서비스 · 기관 · 제품 · 도구)도 공식 URL 연결 · 섹션당 같은 URL 첫 등장 1회 · 걸기 전 URL 열림 확인</sub> | <sub>HTML 형식 요청 · 스타일 확인 답변(기본 = 하우스 스타일)</sub> | <sub>HTML 문서 + 본문 미연결 출처 목록(완료 보고)</sub> |

## 산출물

| <div align="center"><sub>구분</sub></div> | <sub>형식</sub> | <sub>구성</sub> |
|:---|:---:|:---:|
| <sub>기본(단독 사용)</sub> | <sub>대화 응답 · 마크다운 표 · 목록</sub> | <sub>① 발주기관 · 사업 개요 · 핵심 요구사항 · 평가 기준 · 제출 요건 · 리스크<br>② 산업 트렌드 · 클라이언트 현황 · 벤치마킹 3건 이상 · 기술 · 방법론<br>항목별 출처 · `[보완 필요]` · `[미검증]` 표기</sub> |
| <sub>HTML 요청 시</sub> | <sub>`.html` 단일 파일</sub> | <sub>같은 구성 + 본문 출처 하이퍼링크 · 출처 표(`[S번호]`)<br>링크 모양(옅은 밑줄 · 우측 끝 블랙 라인 외부링크 아이콘 · hover 반전) = 하우스 스타일 정본 §22</sub> |
| <sub>agent/proposal S1</sub> | <sub>`_workspace/{프로젝트}/01_rfp.md` · 분석 보고서 HTML</sub> | <sub>`01_rfp.md` 머리에 제안 주요 키워드 5–7개 · 제안 방향성 후보 2–3안 · 평가 구조 · 동종/유사 업계 사례 추가(`agents/rfp-analyst.md`)<br>보고서 파일명 `{업무명}-RFP분석리서치보고서-v0.1-YYYYMMDD.html` · 양식 · 색 = 하네스 `references/rfp-report-format.md`(고객사 CI Primary 기본)</sub> |

## 설치 · 단독 사용

```bash
# 리포 루트에서 — 이 스킬만 전역 설치
cp -r skills/rfp-analysis-research ~/.claude/skills/rfp-analysis-research
```

- **리포 스킬 일괄 설치**: 리포 루트 `bash install-global.sh`(전역 규칙 · 하우스 스타일 등과 함께 적용)
- **의존성**: 추가 패키지 불필요 · 리서치 단계에서 웹 검색 사용
- **하네스 안에서 쓸 때**: [agent/proposal](../../agent/proposal/) — 리포 루트 `./sync-skills.ps1`(또는 `bash ./sync-skills.sh`)로 `agent/proposal/.claude/skills/`에 복사 → `agent/proposal/` 폴더에서 Claude Code 실행 → S1 `rfp-analyst`가 `Skill` 도구로 호출(미가용 시 `agents/rfp-analyst.md` 폴백 절차)

## 주의

- 모든 주장에 근거(데이터 · 사례 · 출처) 명시 · 장식적 표현과 모호한 추론 배제 · 웹 검색으로 최신 자료 확보
- 표기 — `[보완 필요]` RFP에 없지만 일반적으로 필요한 항목 · `[미검증]` 검증 불가 정보 · `[S번호]` 출처 표 번호 태그
- HTML 링크 범위 — 요약 스탯 라벨 · 표 캡션 · 출처 표 「자료」 열 제목까지 포함 · 고유명사 링크는 제목 · 표지 · 목차 · 거버닝 문장 · 출처 표 · 존재하지 않는 도메인 제외 · 링크 스타일은 정본 CSS 담당(산출물 `<style>` 재작성 금지)
- 링크 규칙 출처 — 전역 규칙 「출처 외부링크」(2026.10.19) · 본문 고유명사 링크(2026.11.10, agent/proposal `CLAUDE.md` 5a)
- 하네스 S1 원칙 — RFP · 입찰 조건의 검색어 · 외부 서비스 입력 금지(`agents/rfp-analyst.md` · Dan Jr. W-12)

## 릴리즈노트

| <div align="center"><sub>요약내용</sub><img width="1" height="1"></div> | <sub>업데이트 일자</sub><img width="1" height="1"> | <sub>소유자</sub><img width="45" height="1"> |
|:---|:---:|:---:|
| <sub>README 전면 개편 — 목적 · 넣는 것 · 산출물 형태 · 요청 예시 · 진행 단계 순으로 재구성, 릴리즈노트 맨 아래로 이동</sub> | <sub>2026.11.13</sub> | <sub>김단영</sub> |
| <sub>본문 고유명사(사이트 · 서비스 · 기관 · 도구) 링크 규칙 추가 — 섹션당 첫 등장 `a.ext` 연결, 아이콘은 우측 끝 블랙 라인(정본 §22). `SKILL.md` [HTML 산출 시 출처 링크] 절 보강</sub> | <sub>2026.11.10</sub> | <sub>김단영</sub> |
| <sub>HTML 산출 시 출처 링크 규칙 추가 — 출처 URL을 [S번호]·출처 표에만 두지 않고 본문 항목 타이틀·구절에 `a.ext`로 연결, 스타일은 하우스 스타일 정본 §22</sub> | <sub>2026.10.19</sub> | <sub>김단영</sub> |
| <sub>최초 등록 — 모노레포 재구성, 개별 사용 지원</sub> | <sub>2026.07.07</sub> | <sub>김단영</sub> |
