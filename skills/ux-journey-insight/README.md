# ux-journey-insight — UX 여정맵 · 인사이트 스킬 (제안서 2단계)

RFP 분석 · 현황 리서치 결과를 넣으면 페르소나별 As-Is 사용자 여정맵(단계별 Pain Point · Opportunity), Impact × Feasibility 개선 우선순위, UI/UX 개선 전략 프레임워크가 나오는 제안서 2단계 스킬

## 한눈에 보기

| <div align="center"><sub>항목</sub></div> | <sub>내용</sub> |
|:---|:---:|
| <sub>목적</sub> | <sub>클라이언트 서비스의 사용자 여정에서 개선 포인트를 찾고, 사례 · 데이터 근거의 UI/UX 전략 도출</sub> |
| <sub>이럴 때 사용</sub> | <sub>RFP 분석(1단계) 완료 후 · 구축 · 리뉴얼 · UI/UX 개선처럼 화면과 여정이 본론인 사업 · 제안서 사용자 분석 · UX 전략 장 준비</sub> |
| <sub>넣는 것</sub> | <sub>이전 대화의 RFP 분석 · 현황 리서치 결과(`rfp-analysis-research` 결과)<br>하네스 안 = `_workspace/{프로젝트}/01_rfp.md` + `input/{프로젝트 폴더}/` 자료</sub> |
| <sub>나오는 것</sub> | <sub>페르소나 2~3개 · 페르소나별 As-Is 여정맵 표 · 개선 우선순위 매트릭스 · To-Be 방향성 · 전략 키워드 3개 이내 · 실행 방안 · 기대 효과<br>기본 = 대화 응답(마크다운 표) · 하네스 안 = `01_ux.md`</sub> |
| <sub>부르는 법</sub> | <sub>`RFP 분석 결과로 사용자 여정맵 만들어줘` 같은 요청 · 슬래시 명령 `/ux-journey-insight`</sub> |
| <sub>제작</sub> | <sub>김단영(dykim)</sub> |
| <sub>연계</sub> | <sub>제안 스킬 파이프라인 **②**(아래 표) · 하네스 [agent/proposal](../../agent/proposal/) S1 선택 모듈 `ux-strategist`가 이 스킬 우선 호출</sub> |

**제안 스킬 파이프라인 · agent/proposal 단계 대응**

| <div align="center"><sub>순서</sub></div> | <sub>스킬</sub> | <sub>하는 일</sub> | <sub>agent/proposal 단계 · 에이전트</sub> |
|:---|:---:|:---:|:---:|
| <sub>①</sub> | <sub>[`rfp-analysis-research`](../rfp-analysis-research/README.md)</sub> | <sub>RFP 구조화 + 업계 리서치</sub> | <sub>S1 RFP 분석 · 리서치 · `rfp-analyst`</sub> |
| <sub>**②**</sub> | <sub>**`ux-journey-insight`(이 스킬)**</sub> | <sub>사용자 여정맵 + UX 개선 전략</sub> | <sub>S1 선택 모듈 · `ux-strategist`</sub> |
| <sub>③</sub> | <sub>[`proposal-structure-validation`](../proposal-structure-validation/README.md)</sub> | <sub>목차 구성 + 자기검증</sub> | <sub>S3 제안 목차(GATE ②) · `structure-validator`</sub> |
| <sub>④</sub> | <sub>[`proposal-slide-builder`](../proposal-slide-builder/README.md)</sub> | <sub>본문 슬라이드 제작</sub> | <sub>S4 1차 추출 · S6 n차 추출 · `slide-builder`</sub> |

> 하네스의 S2 컨셉 · S5 피드백 반영 · S7 최종본은 이 4개 스킬 밖의 에이전트 단계 — 전체 7단계 흐름 = [agent/proposal/README.md](../../agent/proposal/README.md)

## 이렇게 요청

| <div align="center"><sub>상황</sub></div> | <sub>요청 예시</sub> | <sub>나오는 것</sub> |
|:---|:---:|:---:|
| <sub>RFP 분석 직후 여정맵 작성</sub> | <sub>`RFP 분석 결과로 사용자 여정맵 만들어줘`</sub> | <sub>페르소나 2~3개 + 페르소나별 As-Is 여정맵 표(단계별 Pain Point · Opportunity)</sub> |
| <sub>개선 포인트 도출</sub> | <sub>`여정맵 기준으로 개선 포인트 우선순위 정리해줘`</sub> | <sub>Impact × Feasibility 우선순위 + To-Be 방향성 요약</sub> |
| <sub>UI/UX 전략 도출</sub> | <sub>`UI/UX 개선 전략 방향 잡아줘`</sub> | <sub>전략 키워드 3개 이내 · 전략별 세부 실행 방안 · 기대 효과(정량 지표 가능 시)</sub> |
| <sub>제안서 하네스 안(구축 · 리뉴얼 사업)</sub> | <sub>`이 RFP로 제안서 만들어줘`(agent/proposal 폴더에서)</sub> | <sub>S1에서 `rfp-analyst`에 이어 실행 → `_workspace/{프로젝트}/01_ux.md`</sub> |

## 진행 단계

```
① 사용자 여정맵 → ② 개선 인사이트 → ③ UI/UX 개선 전략 프레임워크
```

| <div align="center"><sub>단계</sub></div> | <sub>하는 일</sub> | <sub>사용자 할 일</sub> | <sub>결과물</sub> |
|:---|:---:|:---:|:---:|
| <sub>① 사용자 여정맵</sub> | <sub>주요 사용자 페르소나 2~3개 정의 → 페르소나별 As-Is 여정맵(인지 → 진입 → 탐색 → 핵심행동 → 이탈/재방문) → 단계별 Pain Point · Opportunity 명시 · 표 형식 정리</sub> | <sub>1단계 분석 결과 제공(같은 대화 또는 파일)</sub> | <sub>페르소나 · 여정맵 표</sub> |
| <sub>② 개선 인사이트</sub> | <sub>여정맵 기반 개선 포인트를 Impact × Feasibility 매트릭스로 우선순위화 · To-Be 방향성 요약</sub> | <sub>우선순위 검토</sub> | <sub>우선순위 매트릭스 · To-Be 요약</sub> |
| <sub>③ UI/UX 개선 전략</sub> | <sub>전략 방향 3개 이내 핵심 키워드 · 전략별 세부 실행 방안 · 기대 효과(정량 지표 가능 시 명시)</sub> | <sub>전략 방향 확인</sub> | <sub>전략 프레임워크</sub> |

## 산출물

| <div align="center"><sub>구분</sub></div> | <sub>형식</sub> | <sub>구성</sub> |
|:---|:---:|:---:|
| <sub>기본(단독 사용)</sub> | <sub>대화 응답 · 마크다운 표</sub> | <sub>페르소나 정의 · 페르소나별 As-Is 여정맵 표 · Impact × Feasibility 우선순위 · To-Be 방향성 · 전략 키워드 · 실행 방안 · 기대 효과</sub> |
| <sub>agent/proposal S1 선택 모듈</sub> | <sub>`_workspace/{프로젝트}/01_ux.md`</sub> | <sub>같은 구성 · S2 컨셉의 과제 근거와 3장 상세 방안 · 개선 제안 장표의 재료(`agents/ux-strategist.md`)<br>견적형 골격에서는 SECTION 3 서비스 구조(IA) · SECTION 1-1 전략 방향의 재료</sub> |

## 설치 · 단독 사용

```bash
# 리포 루트에서 — 이 스킬만 전역 설치
cp -r skills/ux-journey-insight ~/.claude/skills/ux-journey-insight
```

- **리포 스킬 일괄 설치**: 리포 루트 `bash install-global.sh`(전역 규칙 · 하우스 스타일 등과 함께 적용)
- **의존성**: 추가 패키지 불필요
- **선행 조건**: 이전 대화의 RFP 분석 · 현황 리서치 결과 전제 → 1단계 [`rfp-analysis-research`](../rfp-analysis-research/README.md) 먼저 실행
- **하네스 안에서 쓸 때**: [agent/proposal](../../agent/proposal/) — 리포 루트 `./sync-skills.ps1`(또는 `bash ./sync-skills.sh`)로 `agent/proposal/.claude/skills/`에 복사 → `agent/proposal/` 폴더에서 Claude Code 실행 → S1에서 구축 · 리뉴얼 · UI/UX 개선 과제일 때만 `ux-strategist`가 `Skill` 도구로 호출(운영 · 유지보수 사업은 생략)

## 주의

- 근거 없는 UX 주장 금지 → 사례 · 데이터 기반 서술
- 개선안마다 「왜 이것이 효과적인가」 설명 필수
- 클라이언트 산업군의 특수성 반영
- 하네스 안 원칙(`agents/ux-strategist.md`) — 사용자 플로우 최소 3단계 이상 구체화 · 정책 판단 필요 항목 `[정책 확인 필요]` · 페이지 수는 공수와 직결되므로 과소 산정 주의 · 현행 화면 캡처는 공개 화면만 · 개인정보 가림 · 출처 표기

## 릴리즈노트

| <div align="center"><sub>요약내용</sub><img width="1" height="1"></div> | <sub>업데이트 일자</sub><img width="1" height="1"> | <sub>소유자</sub><img width="45" height="1"> |
|:---|:---:|:---:|
| <sub>README 전면 개편 — 목적 · 넣는 것 · 산출물 형태 · 요청 예시 · 진행 단계 순으로 재구성, 릴리즈노트 맨 아래로 이동</sub> | <sub>2026.11.13</sub> | <sub>김단영</sub> |
| <sub>최초 등록 — 모노레포 재구성, 개별 사용 지원</sub> | <sub>2026.07.07</sub> | <sub>김단영</sub> |
