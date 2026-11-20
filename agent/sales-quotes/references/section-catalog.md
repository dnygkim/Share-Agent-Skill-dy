# 섹션 카탈로그

IA·공수산정 HTML 리포트의 표준 섹션 순서와 내용. builder는 이 순서를 유지하되, 프로젝트에 없는 섹션은 생략 가능(억지로 채우지 않음).

| # | 섹션 | 필수 | 핵심 컴포넌트 | 출처 에이전트 |
|---|------|:---:|--------------|--------------|
| H | 상단 헤더 + 히어로 지표 카드 | ● | `.top-header` + `.hero-card`(총 공수·기간·인원 등) | architect 수치 |
| 1 | 배경 / 고객 Q&A 반영 | ● | `.section-header` + 카드/문단 | analyst |
| 2 | IA 정보구조도 (사용자 + 관리자, 3뎁스+) | ● | `.menu-grid`/`.depth1`/`.depth2` | analyst |
| | ↳ **IA 표 규칙**: `.effort-table fixed` + `<colgroup>` 폭지정. **대메뉴마다 하위를 1개씩 별도 tr(depth2)로 펼침 — ·/쉼표 통합 금지, 전 대메뉴 동일.** (builder.md 도식 IA 절) | | | |
| 3 | 핵심 플로우 / 단계 | ○ | `.section-header` + `.effort-badge` | architect |
| 4 | 외부 연동 / 기술 구조 (API 유추 포함) | ○ | 카드/표 + `.effort-badge` | analyst+architect |
| 5 | 관리자 페이지 | ○ | 카드/표 | analyst |
| A1 | 통합 생태계 개념도 (허브-위성) | ○ | `.eco-hub`/`.eco-sat` (→ architecture-infra-diagram.md) | architect |
| A2 | 기술 아키텍처 · 인프라 설계 (AWS 공식 아이콘) | ○ | `.infra-diagram`/`.aws-*` + AWS 아이콘 img (→ architecture-infra-diagram.md) | architect+builder |
| 6 | 공수 산정 | ● | 아래 6.1~6.6 | architect |
| 6.1 | IA 영역별 공수 (요약표) | ● | `.effort-table` + `.total` | architect(SSOT 파생) |
| 6.2 | 월별 투입 인력표 | ● | `.monthly-effort`(`.subtotal`/`.total`) | **architect SSOT** |
| 6.3 | 역할·단계별 업무 매트릭스 | ● | `.matrix`/`.group-header` | architect |
| 6.4 | WBS (월별 작업 분해) | ○ | 표 | architect |
| 6.5 | 간트 (주 단위) | ○ | `.gantt`/`.bar-*` | architect |
| 6.6 | 핵심 요약 (투입/제외/전제/리스크) | ● | `.effort-grid`/`.card` | architect+analyst |
| 7 | 일정 타임라인 | ● | `.timeline`/`.phase` | architect |
| 8 | 공수 산정 노트 | ● | `.insight` | architect |
| F | 푸터 (총계·기간·인원 재기재) | ● | `.footer` | architect 수치 |

## 수치가 중복 등장하는 섹션 (qa 교차검증 대상)
총 M/M · 인원 · 기간 · 영역별 공수는 다음에서 **반복**된다 → 반드시 SSOT와 일치:
- 히어로 카드(H) · 영역별 요약표 총계(6.1) · 월별표 총계(6.2) · 핵심요약 카드(6.6) · 푸터(F) · 각 섹션 lead/서술문
- 상세 위치 맵: `consistency-checklist.md`
