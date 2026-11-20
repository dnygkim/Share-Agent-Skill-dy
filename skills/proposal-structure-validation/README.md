# proposal-structure-validation — 제안서 목차 구성 · 자기검증 스킬 (제안서 3단계)

RFP 분석 · 리서치 · UX 인사이트 결과를 넣으면 목차별 핵심 내용과 분량 배분을 단 제안서 목차, 5개 기준 자기검증 판정(통과 · 보완필요 · 미충족)과 보완 방향이 나오는 제안서 3단계 스킬

## 한눈에 보기

| <div align="center"><sub>항목</sub></div> | <sub>내용</sub> |
|:---|:---:|
| <sub>목적</sub> | <sub>1 · 2단계 결과를 평가 배점에 맞춘 목차로 묶고, 요구사항 누락 · 근거 · 차별화 · 실행가능성 점검</sub> |
| <sub>이럴 때 사용</sub> | <sub>RFP 분석 · UX 인사이트 완료 후 목차를 짤 때 · 제안서 초안 완성 후 최종 자기검증</sub> |
| <sub>넣는 것</sub> | <sub>이전 대화의 RFP 분석 · 리서치 · UX 인사이트 결과(1 · 2단계)<br>하네스 안 = `01_rfp.md` + 승인된 `02_concept.md`(+ `01_ux.md`)</sub> |
| <sub>나오는 것</sub> | <sub>제안서 목차(RFP 지정 목차 우선 · 없으면 기본 10장) + 목차별 핵심 포함 내용 2~3줄 + 고배점 항목 분량 배분 + 자기검증 5기준 판정 · 개선 방향<br>기본 = 대화 응답(마크다운) · 하네스 안 = `03_structure.md`</sub> |
| <sub>부르는 법</sub> | <sub>`제안서 목차 짜줘` · `제안서 초안 자기검증해줘` 같은 요청 · 슬래시 명령 `/proposal-structure-validation`</sub> |
| <sub>제작</sub> | <sub>김단영(dykim)</sub> |
| <sub>연계</sub> | <sub>제안 스킬 파이프라인 **③**(아래 표) · 하네스 [agent/proposal](../../agent/proposal/) S3 제안 목차의 `structure-validator`가 이 스킬 우선 호출 → **GATE ② 목차 · 분량 승인**</sub> |

**제안 스킬 파이프라인 · agent/proposal 단계 대응**

| <div align="center"><sub>순서</sub></div> | <sub>스킬</sub> | <sub>하는 일</sub> | <sub>agent/proposal 단계 · 에이전트</sub> |
|:---|:---:|:---:|:---:|
| <sub>①</sub> | <sub>[`rfp-analysis-research`](../rfp-analysis-research/README.md)</sub> | <sub>RFP 구조화 + 업계 리서치</sub> | <sub>S1 RFP 분석 · 리서치 · `rfp-analyst`</sub> |
| <sub>②</sub> | <sub>[`ux-journey-insight`](../ux-journey-insight/README.md)</sub> | <sub>사용자 여정맵 + UX 개선 전략</sub> | <sub>S1 선택 모듈 · `ux-strategist`</sub> |
| <sub>**③**</sub> | <sub>**`proposal-structure-validation`(이 스킬)**</sub> | <sub>목차 구성 + 자기검증</sub> | <sub>S3 제안 목차(GATE ②) · `structure-validator`</sub> |
| <sub>④</sub> | <sub>[`proposal-slide-builder`](../proposal-slide-builder/README.md)</sub> | <sub>본문 슬라이드 제작</sub> | <sub>S4 1차 추출 · S6 n차 추출 · `slide-builder`</sub> |

> 하네스의 S2 컨셉 · S5 피드백 반영 · S7 최종본은 이 4개 스킬 밖의 에이전트 단계 — 전체 7단계 흐름 = [agent/proposal/README.md](../../agent/proposal/README.md)

## 이렇게 요청

| <div align="center"><sub>상황</sub></div> | <sub>요청 예시</sub> | <sub>나오는 것</sub> |
|:---|:---:|:---:|
| <sub>1 · 2단계 직후 목차 구성</sub> | <sub>`분석 결과 종합해서 제안서 목차 짜줘`</sub> | <sub>기본 10장(또는 RFP 지정) 목차 + 목차별 핵심 내용 2~3줄 + 분량 배분 + 자기검증 판정</sub> |
| <sub>RFP가 목차를 지정한 경우</sub> | <sub>`RFP 지정 목차 기준으로 구성하고 보강할 항목 제안해줘`</sub> | <sub>지정 구조 우선 목차 + 보강 항목 제안</sub> |
| <sub>초안 완성 후 최종 점검</sub> | <sub>`SECTION 7~9까지 썼어, 전체 제안서 최종 검증해줘`</sub> | <sub>5기준 판정([통과 / 보완필요 / 미충족]) + 보완필요 · 미충족 항목별 개선 방향</sub> |
| <sub>제안서 하네스 안(컨셉 승인 후)</sub> | <sub>`목차 짜줘`(agent/proposal 폴더에서)</sub> | <sub>`03_structure.md` 제시 → 목차 · 분량 승인(GATE ②)</sub> |

## 진행 단계

```
① 제안서 목차 구성 → ② 자기검증(5기준) → ③ 보완 방향 제시 → (하네스 안) GATE ② 목차 · 분량 승인
```

| <div align="center"><sub>단계</sub></div> | <sub>하는 일</sub> | <sub>사용자 할 일</sub> | <sub>결과물</sub> |
|:---|:---:|:---:|:---:|
| <sub>① 목차 구성</sub> | <sub>RFP 지정 목차가 있으면 그 구조 우선 + 보강 항목 제안 · 없으면 기본 10장 적용 → 목차별 핵심 포함 내용 2~3줄 요약 → 평가 배점이 높은 항목에 더 많은 분량 배분 명시</sub> | <sub>1 · 2단계 결과 제공 · RFP 지정 목차 여부 확인</sub> | <sub>목차안</sub> |
| <sub>② 자기검증</sub> | <sub>전체 산출물을 아래 5기준으로 검증 → 항목마다 [통과 / 보완필요 / 미충족] 판정</sub> | <sub>판정 검토</sub> | <sub>검증표</sub> |
| <sub>③ 보완 방향</sub> | <sub>보완필요 · 미충족 항목마다 구체적 개선 방향 제시 · 최종 판단 기준 = 클라이언트가 읽었을 때 「이 업체가 우리 사업을 제대로 이해했다」는 인상</sub> | <sub>보완 범위 결정</sub> | <sub>개선 방향</sub> |
| <sub>(하네스 안) GATE ②</sub> | <sub>`03_structure.md` 제시 → 목차와 분량(확정 장수) 승인 요청 · 수정 요청 시 갱신 후 재제시</sub> | <sub>**목차 · 분량 승인 — 승인 전 본문 제작(`slide-builder`) 보류**</sub> | <sub>승인된 `03_structure.md`</sub> |

**자기검증 5기준**

| <div align="center"><sub>#</sub></div> | <sub>기준</sub> | <sub>확인 내용</sub> |
|:---|:---:|:---:|
| <sub>1</sub> | <sub>RFP 요구사항 커버리지</sub> | <sub>필수 요구사항 누락 여부 → 누락 시 구체 명시</sub> |
| <sub>2</sub> | <sub>평가 배점 정합성</sub> | <sub>고배점 항목에 충분한 깊이 할당 여부</sub> |
| <sub>3</sub> | <sub>근거 완결성</sub> | <sub>출처 없는 주장 · `[미검증]` 잔존 여부</sub> |
| <sub>4</sub> | <sub>차별화 포인트</sub> | <sub>경쟁 대비 우위 주장 가능 여부</sub> |
| <sub>5</sub> | <sub>실행가능성</sub> | <sub>일정 · 인력 · 기술 구성의 현실성</sub> |

## 산출물

| <div align="center"><sub>구분</sub></div> | <sub>형식</sub> | <sub>구성</sub> |
|:---|:---:|:---:|
| <sub>기본(단독 사용)</sub> | <sub>대화 응답 · 마크다운</sub> | <sub>목차(기본 10장 또는 RFP 지정) · 목차별 핵심 내용 2~3줄 · 분량 배분 · 5기준 검증표 · 개선 방향</sub> |
| <sub>agent/proposal S3</sub> | <sub>`_workspace/{프로젝트}/03_structure.md`</sub> | <sub>머리말(상태 · 골격 · 확정 장수) + 목차 표(행 = 장표 1장: 코드 · 장 · 절 · 태그라인 · 거버닝 메시지(안) · 주요 삽입내용 · 근거 · 출처 · 필요한 레퍼런스 · RFP 요구 항목) + RFP 요구 항목 대응 + 검증 결과<br>스킬 결과가 이 서식에 못 미치면 `agents/structure-validator.md` 기준으로 보강</sub> |

**기본 목차 10장**(RFP 지정 목차가 없을 때)

| <div align="center"><sub>장</sub></div> | <sub>제목</sub> |
|:---|:---:|
| <sub>Ⅰ</sub> | <sub>사업 이해 및 환경 분석</sub> |
| <sub>Ⅱ</sub> | <sub>추진 전략 및 방향</sub> |
| <sub>Ⅲ</sub> | <sub>현황 분석 및 벤치마킹</sub> |
| <sub>Ⅳ</sub> | <sub>사용자 분석 및 개선 인사이트</sub> |
| <sub>Ⅴ</sub> | <sub>UI/UX 설계 전략</sub> |
| <sub>Ⅵ</sub> | <sub>주요 기능 및 서비스 설계</sub> |
| <sub>Ⅶ</sub> | <sub>기술 아키텍처 및 구현 방안</sub> |
| <sub>Ⅷ</sub> | <sub>추진 체계 및 일정 계획</sub> |
| <sub>Ⅸ</sub> | <sub>프로젝트 관리 방안</sub> |
| <sub>Ⅹ</sub> | <sub>기대 효과 및 향후 로드맵</sub> |

## 설치 · 단독 사용

```bash
# 리포 루트에서 — 이 스킬만 전역 설치
cp -r skills/proposal-structure-validation ~/.claude/skills/proposal-structure-validation
```

- **리포 스킬 일괄 설치**: 리포 루트 `bash install-global.sh`(전역 규칙 · 하우스 스타일 등과 함께 적용)
- **의존성**: 추가 패키지 불필요
- **선행 조건**: 이전 대화의 1 · 2단계 결과 전제 → [`rfp-analysis-research`](../rfp-analysis-research/README.md) · [`ux-journey-insight`](../ux-journey-insight/README.md) 먼저 실행
- **하네스 안에서 쓸 때**: [agent/proposal](../../agent/proposal/) — 리포 루트 `./sync-skills.ps1`(또는 `bash ./sync-skills.sh`)로 `agent/proposal/.claude/skills/`에 복사 → `agent/proposal/` 폴더에서 Claude Code 실행 → S3에서 `structure-validator`가 `Skill` 도구로 호출(미가용 시 `agents/structure-validator.md` 폴백 절차) · 선행 조건 = `02_concept.md` 승인(견적형 골격은 「제안 방향 3가지」로 대체)

## 주의

- 보완필요 · 미충족 판정에는 구체적 개선 방향 동반
- 최종 판단 기준 = 클라이언트가 읽었을 때 「이 업체가 우리 사업을 제대로 이해했다」는 인상
- 견적형 흐름(`proposal-slide-builder`의 `references/section-prompts.md` 연계 순서)에서는 SECTION 7~9 작성 후 이 스킬로 전체 정합성 · 근거 누락 · RFP 정렬 최종 검증
- 하네스 안 GATE ② — 승인 뒤 목차가 바뀌면(피드백 등) `03_structure.md`를 먼저 고친 뒤 장표에 반영

## 릴리즈노트

| <div align="center"><sub>요약내용</sub><img width="1" height="1"></div> | <sub>업데이트 일자</sub><img width="1" height="1"> | <sub>소유자</sub><img width="45" height="1"> |
|:---|:---:|:---:|
| <sub>README 전면 개편 — 목적 · 넣는 것 · 산출물 형태 · 요청 예시 · 진행 단계 순으로 재구성, 릴리즈노트 맨 아래로 이동</sub> | <sub>2026.11.13</sub> | <sub>김단영</sub> |
| <sub>최초 등록 — 모노레포 재구성, 개별 사용 지원</sub> | <sub>2026.07.07</sub> | <sub>김단영</sub> |
