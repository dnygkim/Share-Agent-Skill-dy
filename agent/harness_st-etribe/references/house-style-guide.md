# 하우스 스타일 가이드

builder가 참조. 전체 CSS는 `template/house-style.css`(1,410줄)에 있고 그대로 `<style>`에 인라인한다. 여기서는 **디자인 토큰과 컴포넌트 클래스 카탈로그**만 정리한다(중복 금지).

## 톤 (2026-08-19 개정)

**warm paper × near-black 에디토리얼.** 기준 레퍼런스 = 신승 비즈니스AI플래너 권한정책 매트릭스.
- 크림 지면(`--paper`) 위 흰 면(`--surface`)과 near-black 잉크(`--ink`) 3층으로만 위계를 만든다.
- **그라디언트·박스섀도 금지. radius 0-2px.** 면은 1px 헤어라인으로 나눈다.
- **색은 정보를 나를 때만 쓴다** — 단계 구분(간트·WBS)과 경고(`--warn`)뿐. 장식용 색 금지.
- 데코 이모지(💡·⏱·★·🏢) 금지. 강조는 서체 굵기와 선으로 한다.

## 디자인 토큰 (:root)
| 변수 | 값 | 용도 |
|------|----|----|
| `--paper` / `--paper-2` | #F1EDE5 / #E8E3D9 | 지면 배경 / 표 헤더·강조 면 |
| `--surface` | #FFFFFF | 카드·표 본문 면 |
| `--ink` | #14130F | 본문·헤딩·다크 밴드 배경 |
| `--ink-2` / `--ink-3` | #56534C / #8C887F | 보조 텍스트 / 흐린 텍스트·번호 |
| `--line` / `--line-2` | #D9D3C7 / #E6E1D7 | 외곽 헤어라인 / 셀 구분선 |
| `--warn` | #7A4A2C | 경고·확인필요·산정노트 강조 |
| `--font-title` | Paperlogy → Pretendard | 제목·표 헤더·수치·배지 |
| `--font-body` | Pretendard Variable | 본문 |
| `--ph-*` (9종) | pm/analyze/design/designv/pub/dev/ai/test/stable | 간트 바·WBS 단계 색(저채도 어스톤) |

**구 토큰(`--brand`·`--brand-dark`·`--brand-soft`·`--ink-soft`·`--muted`·`--bg`·`--card`·`--tag-bg`·`--insight-bg`·`--insight-border`)은 별칭으로 남아 있다** — 지우지 마라. `diagrams.css`(eco/aws 도식)와 `build_report.py` 의 spec palette 주입이 이 이름을 쓴다. 기본값은 무채색이라 팔레트를 안 주면 레퍼런스 톤 그대로 나온다.

→ **고객 브랜드색이 필요하면 `--brand` 계열만** 덮어쓴다. 그 별칭은 도식에만 닿고 본문 레이아웃 색은 안 건드린다. 레이아웃/구조 클래스는 불변.

## 컴포넌트 클래스 카탈로그
| 영역 | 핵심 클래스 |
|------|-----------|
| 상단/히어로 | `.top-header`(다크 표지 밴드), `.hero-grid`/`.hero-card`(`.label`/`.value`/`.unit`/`.sub`/`.hl`) |
| 섹션 헤더 | `.section-header`(`.num-box` + `.text h2` + `.area`), `.effort-badge`(`.new`) |
| IA 트리 | `.menu-grid`/`.menu-item`/`.menu-num`/`.menu-name`, `.depth1`/`.depth2`, `.menu-chip` |
| 공수 표 | `.monthly-effort`/`.effort-table`, `.num`(`.zero`), `.subtotal`, `.total`, `.role`, `.month-header` |
| 매트릭스 | `.matrix`, `.group-header`, `.empty` |
| 간트 | `.gantt`, `.gantt-legend`, `.bar-pm`/`.bar-design`/`.bar-dev`/`.bar-pub`/`.bar-test`/`.bar-analyze`/`.bar-ai`/`.bar-stable` |
| 요약/카드 | `.effort-grid`/`.card`(`.ttl`/`.body`), `.lead`, `.subhead`, `.chip`, `.badge` |
| 타임라인 | `.timeline`/`.phase`(`.ph-num`/`.ph-name`/`.ph-desc`), `.test`(강조 단계) |
| 인사이트 | `.insight`(`.title` + `ul`) |
| 푸터 | `.footer` |

## 렌더 규칙
- 단일 파일. **예외는 웹폰트 2종뿐** — Pretendard(`@import`)와 Paperlogy(`@font-face`)는 `local()` 우선 + jsdelivr CDN 폴백으로 house-style.css 맨 위에 있다. 폰트가 안 잡히는 환경(오프라인·폐쇄망)에서는 시스템 폰트로 우아하게 떨어진다. **그 밖의 외부 링크(스크립트·이미지·CSS)는 여전히 금지.**
- `@import` 는 스타일시트 최상단에만 유효하다 — house-style.css 앞에 다른 CSS를 붙이지 마라(`inline_css.py`·`build_report.py` 의 주입 순서 = house → diagrams → palette override).
- 숫자 셀은 `.num`, 0/미투입은 `.num zero">-`.
- 소계행 `.subtotal`, 총계행 `.total`.
- 범위 표기 하이픈(-), 물결표(~) 금지.
- 인쇄는 A4 세로 기준(`@page`)이며 `print-color-adjust:exact` 대상이 지정돼 있다 — 다크 밴드·간트 바는 인쇄에서도 색이 남는다.
