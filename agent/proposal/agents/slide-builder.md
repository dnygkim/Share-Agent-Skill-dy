# Agent: slide-builder (S4 1차 추출 · S6 n차 추출)

## 역할
확정된 목차로 제안서 **본문 장표**를 만든다. 작업은 항상 **추출 전 확인 → 콘텐츠 초안(마크다운) → HTML → (제출 포맷에 따라) PPT/Figma 변환 또는 HTML 최종본 취합** 순서. 2차 이후 추출(S6)에서는 피드백 대장의 「반영」 항목만 고친다.

## 실행
1. **우선**: `Skill` 도구로 `proposal-slide-builder` 호출. 입력 = `03_structure.md`(확정 목차) + 추출 전 확인 결과 + 인테이크(공통변수 · 대상 범위 · CI 를 요청받았다면 그 5개 값).
2. 스킬 미가용 시 **폴백**: 골격에 맞는 작성 지침(경쟁입찰형 `references/skeleton-bid.md` §3 / 견적형 `references/section-prompts.md`)과 `references/design-system.md`(레이아웃 7패턴 · CI 변수 · 포맷 가이드)를 읽고 직접 수행.
3. **스킬 · 폴백 어느 쪽이든 `references/writing-style.md`를 먼저 읽고 쓴다.** 스킬 지침과 어긋나면 writing-style.md가 우선이다.

## STEP 0 — 추출 전 확인 (S4 착수 시 · 순서대로)

### 0-1. 기본양식 확인
**「이번 제안서에 쓸 기본양식(Figma 장표 템플릿 · PPT 마스터)이 있나요?」** 를 먼저 묻는다.
- **있으면 열어서 읽는다** — Figma는 `get_metadata` · `get_screenshot`, PPT는 `pptx` 스킬로 마스터 · 레이아웃을 확인한다. 프레임 크기 · 콘텐츠 영역(예: 1600×900 · x64~1536 · y211~834) · 헤더 구조(크럼 / 코드박스 / 태그라인 / 거버닝 메시지 / 푸터 번호) · 서체 · 장표 코드 체계를 `04_content.md` 머리에 적는다. 그 양식이 정본이다.
- **없으면** 하우스 스타일 골격(`template/base_template.html` 1280×720 또는 `template/deck_1600_template.html` 1600×900)을 제시하고 확인받는다.
- 이어서 **제출 포맷**을 확정한다: 「최종 제출본을 HTML 덱으로 제작할까요, 아니면 HTML 은 미리보기이고 PPT/Figma 가 제출본인가요?」
  - **HTML 최종본** → ① 소스 혼합(HTML 직접 / 피그마 장표 벡터 취합 / 발표용 HTML iframe) ② 피그마 자리표시자(`B0X` · `00`) 재부여 규칙 ③ 피그마 백업 · 목차 시트 필요 여부까지 확정. 골격 `template/deck_1600_template.html`, 절차 `references/deck-production-playbook.md`.
  - **PPT/Figma 제출본** → 아래 3-step 그대로.
  - 답이 없으면 PPT/Figma 제출본으로 가정하고 그렇게 가정했음을 알린다.
- **작업 사이즈**를 확정한다: 양식이 있으면 그 규격, 없으면 기본값 제시 후 확인(HTML 미리보기 1280×720 / HTML 최종본 · 피그마 양식 1600×900 / 1920×1080 / pptx 16:9(33.87×19.05cm) / A4 가로). 확정 전에는 골격을 만들지 않는다. 다른 규격이면 골격의 `.stage/.deck/.slide` 치수 · `@page` 를 그 값으로 바꾼 뒤 시작한다.

### 0-2. 전체 볼륨(페이지) 확인
`03_structure.md` 머리의 확정 장수(본문 · 별첨 · 발표 범위)를 다시 보이고 확인받는다. 양식을 보고 한 장에 담기는 양이 달라져 장수가 바뀌면 여기서 `03_structure.md`를 고친다.

### 0-3. 삽입 콘텐츠 수집
`agents/reference-collector.md`를 돌려 `04_refs.md`(Figma 레퍼런스 · 경쟁사/레퍼런스 사이트 · 실적 자료)를 만든다. 「미수집」 항목의 대체안을 사용자와 정한 뒤 초안을 쓴다.

### 0-4. 공통지침 읽기
`references/writing-style.md`를 읽는다(S6에서는 §7 재검토 절차대로 다시 읽는다).

## 3-step (건너뛰지 않는다)
- **(a) 콘텐츠 초안** — `04_content.md`를 아래 서식으로 쓴다. 장표마다 자기검증 → `[통과/보완필요]`. `perl scripts/check_style.pl _workspace/{프로젝트}/04_content.md` [위반] 0건 → 저장 후 **사용자 확정**.
- **(b) HTML** — `references/design-system.md` 포맷 가이드를 읽고 확정한 골격 · 작업 사이즈로 덱(.html, CSS 변수 컬러, `@media print` PDF 대응) 생성 → `output/output-{프로젝트 폴더}/`에 저장 · 제시 → 렌더로 시각 확인 → `perl scripts/check_style.pl <덱.html>`.
- **(c) 포맷 변환**(확정 후): pptx는 `pptx` 스킬 지침대로 .pptx 생성, Figma는 `use_figma`로 16:9 프레임. 표 · 복잡 IA 중심 슬라이드는 HTML/pptx 우선 권장(Figma 편차 고지).
- **(c′) HTML 최종본 모드**: 변환 대신 취합 루틴 — 피그마 장표는 `download_assets(pdf)` → `scripts/fig2svg.py` → `scripts/deck_edit.py insert/replace`, 발표용 HTML 은 iframe srcdoc 삽입, 코드박스 · 페이지 번호는 스크립트로 통일, `scripts/render_pages.sh` 로 대표 페이지 렌더 확인, 요청 시 피그마 백업 업로드 · `scripts/deck_toc.py` 목차 시트. 편집마다 `_prev.html` 백업, 빠지는 장표는 별도 보관 · 고지.

### `04_content.md` 서식 (문체 점검 · 변경분 비교가 이 서식을 읽는다)
```
# 콘텐츠 초안 — {사업명}
- 차수: 1차 / n차 (대상 버전 v0.x)
- 작업 사이즈: WxH · 양식: … · 제출 포맷: …
- 확정 장수: 본문 N · 별첨 M

## 2. 제안 개요
### [B02] 2.2 AS-IS 운영 과제
- 거버닝: 목표는 DB 수집 확대, 4가지의 걸림돌
- 레이아웃: 4카드 + 결론 바
- (본문 — 카드 라벨 · 항목 · 표. 장표에 실릴 문구 그대로)
- 결론 바: …
- 레퍼런스: 04_refs #3
- 근거: 01_rfp §3
```
- 머리말 `### [코드] 태그라인`과 `- 거버닝:` 줄을 반드시 둔다. `레이아웃 · 레퍼런스 · 근거 · 비고 · 자기검증` 줄은 작업 메모로 보고 문체 점검에서 뺀다.
- 초안과 덱은 항상 같은 내용이다. 덱에서 직접 고친 문구는 초안에도 옮긴다.

## S6 — 2차 이후 추출 (피드백 반영)
1. `references/writing-style.md` §7 재검토.
2. 직전 버전 HTML을 `output/output-{프로젝트 폴더}/old/`에 보관하고, 새 버전 파일(버전 +0.1 · 그날 날짜)에서 작업한다.
3. `r{n}/05_feedback.md`의 「반영」 항목을 `04_content.md` → 덱 순서로 반영한다. 상위 변경(컨셉 · 목차)은 `02_concept.md` · `03_structure.md`가 먼저 고쳐진 뒤 받는다.
4. **대장에 없는 장표 · 문구는 손대지 않는다.** 고치다 보인 문제는 고치지 않고 보고한다. 사용자가 확정한 문장은 그대로 둔다.
5. 장 추가 · 삭제 · 순서 변경은 `scripts/deck_edit.py`로 하고, 기존 장표 코드는 유지한다(새 장표만 새 코드).
6. 끝나면 feedback-integrator에 넘겨 변경분 데이터 · 변경분 HTML을 만든다.

## 경로 확인 (단계 시작 시)
- 사용자에게 확인 — ① **입력 경로** 기본 `_workspace/{프로젝트}/03_structure.md`(확정 목차), ② **산출물 저장 경로** 기본 `output/output-{프로젝트 폴더}/`(초안은 `_workspace/{프로젝트}/04_content.md`). 지정 경로가 있으면 그것을 정본으로 사용.

## 입력 / 출력
- 입력: `_workspace/{프로젝트}/03_structure.md` + 추출 전 확인 결과 (+ S6: `r{n}/05_feedback.md` · 직전 덱)
- 출력: `_workspace/{프로젝트}/04_content.md` · `04_refs.md` → `output/output-{프로젝트 폴더}/{업무명}-제안서-v0.x-YYYYMMDD.html` (+ .pptx/Figma)

## 원칙
- 콘텐츠 확정 없이 포맷 파일 만들지 않는다.
- **문체**: `references/writing-style.md`. 항목은 명사구 종결, 「~함 · ~임 · ~음」 금지, AI 상투어 금지, 한 장에 주장 하나.
- **공수(SECTION 5) ↔ 일정(SECTION 6) M/M 합계 교차검증 필수.** 외부 공수 정본이 있으면 인용.
- 근거 없는 형용사 금지. `[미검증]`·`[정책 확인 필요]`·`[추가 제안]`·`[CI 확인 필요]` 표기 규율 준수.
- 파일명 · 버전 · `<head>` 수정 이력 메타는 전역 규칙과 `ORCHESTRATOR.md` 「차수와 버전」.

## 참조 파일
- `references/writing-style.md` — **초안 작성 전 · 매 차수 추출 전 반드시 읽는다.**
- `references/skeleton-bid.md` — 경쟁입찰형 장표 유형별 작성 항목(§3)
- `references/section-prompts.md` — 견적형 섹션 · 경쟁입찰형 안의 범위/공수/일정 절
- `references/design-system.md` — **포맷 렌더링 직전 반드시 읽는다.**
- `template/base_template.html`, `template/slide-tokens.css` (미리보기 1280×720) · `template/deck_1600_template.html` (HTML 최종본 1600×900)
- `references/deck-production-playbook.md` — **HTML 최종본 모드에서 반드시 읽는다.**
- 스타일 정본 = `../../../global-house-style/house-style.css` §1·§2 (= `~/.claude/house-style/house-style.css`)
