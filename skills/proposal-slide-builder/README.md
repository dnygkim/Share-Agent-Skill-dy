# proposal-slide-builder — 제안서 본문 슬라이드 생성 스킬 (제안서 4단계)

## 릴리즈노트

| <div align="center"><sub>요약내용</sub><img width="1" height="1"></div> | <sub>업데이트 일자</sub><img width="1" height="1"> | <sub>소유자</sub><img width="45" height="1"> |
|:---|:---:|:---:|
| <sub>STEP 0 에 실제 제작 포맷 확인(HTML 최종본 vs PPT/Figma 제출본)·작업 사이즈(장표 규격) 확인 단계 추가 — HTML 최종본이면 제출 규격 덱 + 제안서 하네스 취합 루틴(deck-production-playbook) 연계. design-system §3 크기 착수 시 확인·§5 1600×900 덱 안내 (GS칼텍스 제안 실전 반영)</sub> | <sub>2026.09.11</sub> | <sub>김단영</sub> |
| <sub>최초 등록 — 모노레포 재구성, 개별 사용 지원</sub> | <sub>2026.07.07</sub> | <sub>김단영</sub> |

IT 서비스·플랫폼 제안서의 **본문 슬라이드를 섹션별로 생성**하는 스킬이다.
콘텐츠 초안(마크다운) 확정 → HTML 슬라이드 미리보기 → pptx·Figma 변환 순으로
진행한다. 목차 확정(3단계) 후 본문 제작 단계(4단계)에서 쓰며, 단독 호출로 특정
섹션만 만들 수도 있다.

- **파이프라인 위치**: `rfp-analysis-research`(1) → `ux-journey-insight`(2) → `proposal-structure-validation`(3) → 4단계
- **작동 정의**: [SKILL.md](SKILL.md) 참고
- **에이전트 연계**: [agent/proposal](../../agent/proposal/) 파이프라인의 slide-builder 단계
- **디자인 표준**: `deckslide-design-guideline` 스킬과 함께 쓰면 장표 스타일이 통일된다
