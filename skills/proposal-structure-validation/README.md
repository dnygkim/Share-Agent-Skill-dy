# proposal-structure-validation — 제안서 목차 구성·검증 스킬 (제안서 3단계, GATE)

## 릴리즈노트

| <div align="center"><sub>요약내용</sub><img width="1" height="1"></div> | <sub>업데이트 일자</sub><img width="1" height="1"> | <sub>소유자</sub><img width="45" height="1"> |
|:---|:---:|:---:|
| <sub>최초 등록 — 모노레포 재구성, 개별 사용 지원</sub> | <sub>2026.07.07</sub> | <sub>김단영</sub> |

RFP 분석과 UX 인사이트를 종합해 **제안서 목차를 구성하고 최종 자기검증**을
수행하는 스킬이다. 제안서 초안 완성 단계(3단계, 품질 GATE)에서 쓴다.

- **파이프라인 위치**: `rfp-analysis-research`(1) → `ux-journey-insight`(2) → 3단계(GATE) → `proposal-slide-builder`(4)
- **작동 정의**: [SKILL.md](SKILL.md) 참고
- **에이전트 연계**: [agent/proposal](../../agent/proposal/) 파이프라인의 structure-validator 단계
