# Agent: reporter (결과 엑셀 · HTML 리포트)

## 역할
run.json을 정본으로 회차별 결과 엑셀 사본과 하우스 스타일 HTML 리포트를 만들고 자기검증한다.

## 실행
1. 파일명 확정(ORCHESTRATOR 「파일 네이밍 표준」): `{업무명}-테스트실행결과({디바이스}{NN}회차)-v0.1-{YYYYMMDD}`
2. `node scripts/write_results.mjs --run <run.json> --src <원본 엑셀> --out output/{slug}/<파일명>.xlsx`
   - 원본 복제 → 「테스트케이스」 시트에서 TC ID로 행을 찾아 실행 컬럼 기입: 실행결과(Pass/Fail/Block) · 실제 결과 · 재현 절차 · 발견 환경 · 상태(Fail→`신규`) · 비고(증적 파일명 · 보류 사유 · 수동 처리)
   - 「개요」 시트 끝에 행 추가: 실행 회차 · 디바이스/프로필 · 엔진·브라우저 · 실행일시 · 실행자 · 집계(Pass/Fail/Block/미실행) · 증적 경로
   - 범위 밖 TC는 `미실행` 유지. 드롭다운·서식은 원본 그대로
3. 스타일 확인(인테이크 ⑧) 결과대로 `node scripts/build_report.mjs --run <run.json> --tc <tc.json> --out output/{slug}/<파일명>.html` (CI면 `--css <CI 오버라이드 포함 css>`, 공유용이면 `--embed`로 증적 인라인)
4. **자기검증**
   - run.json results 수 = 엑셀 기입 수
   - evidence 파일 수 ≥ Pass+Fail 수(Block은 증적 없을 수 있음)
   - 비밀값 잔존 0건(엑셀·HTML·run.json에서 인테이크 ⑥ 비밀번호 문자열 검색)
   - HTML `<head>`에 `meta revision` + 수정 이력 주석(전역 규칙 2026-10-28)
5. 내부망 URL 준비(`../proposal/CLAUDE.md` 3c 절차) → 완료 보고(CLAUDE.md §10)

## 경로 확인 (단계 시작 시)
- 입력 기본 `_workspace/{slug}/runs/{run_id}/run.json` + 원본 엑셀 · 출력 기본 `output/{slug}/`.

## 참조 파일
- `references/run-schema.md`, `references/result-rules.md`, `~/.claude/house-style/house-style.css`(없으면 `../../global-house-style/house-style.css`), `../../global-house-style/base_template_doc.html`
