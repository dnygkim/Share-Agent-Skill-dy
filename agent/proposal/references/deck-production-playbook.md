# 덱 제작 플레이북 — HTML 이 최종 포맷일 때 (1600×900 취합 덱)

> GS칼텍스 기업 홈페이지 재구축 제안(2026-09-10~11, 88p)에서 실제로 돌린 절차를 일반화한 것.
> slide-builder 가 **STEP 0 의 「실제 제작 포맷」 답이 "HTML 최종본"** 일 때 이 문서를 따른다.
> 미리보기용 1280×720 덱(`template/base_template.html`)과는 다른 골격(`template/deck_1600_template.html`)을 쓴다.

## 0. 착수 시 확정할 것 (slide-builder STEP 0 에서 묻는다)
1. **최종 제출 포맷** — ① HTML 덱이 그대로 제출본(PDF 는 HTML 에서 인쇄) ② HTML 은 미리보기, PPT/Figma 가 제출본. **①이면 이 플레이북**, ②면 기존 3-step.
2. **작업 사이즈(장표 규격)와 양식 — 별도 확인 단계** — 「작업 사이즈는 무엇으로 할까요?」를 포맷 답 직후에 묻는다(1280×720 / 1600×900 / 1920×1080 / pptx 16:9 / A4 등). 디자인파트/클라이언트 양식(예: 피그마 1600×900 장표 템플릿, 콘텐츠 영역 x64~1536 · y211~834)이 있으면 그 규격·헤더 구조(크럼 / 코드박스 / 태그라인 / 거버닝 메시지 / 푸터 번호)를 그대로 따른다. 없으면 하우스 스타일 1280×720. 확정값을 `04_content.md` 머리말에 적고, 덱·피그마 백업 프레임·PDF 페이지가 모두 이 한 규격을 따른다. 확정 전에는 골격을 만들지 않는다.
3. **소스 혼합 여부** — 장표가 어디서 오는가: (a) HTML 직접 작성 (b) 피그마에서 만든 장표(벡터 취합) (c) 인터랙티브 발표용 HTML(iframe 삽입). 세 가지를 한 덱에 섞을 수 있다.
4. **장표 코드 체계** — 장별 접두(C=회사소개, B=프로젝트 이해, A=수행 과제, S/D=파트너·개발, M=관리) + 2자리. 피그마 장표는 자리표시자(`B0X`·`00`)로 오는 경우가 많으니 취합 시 재부여 규칙을 미리 정한다.
5. **백업·공유 채널** — 피그마 백업 섹션(전 장 PNG 프레임)·목차 시트(xlsx/구글시트) 필요 여부.

## 1. 골격
- `template/deck_1600_template.html` 복사 → `output/output-{프로젝트 폴더}/{업무명}-제안서-v{X.Y}-{YYYYMMDD}.html`(전역 파일명 규칙). 자기완결 단일 파일(로고·이미지는 data URI).
- 슬라이드 4종: `cover`(간지) · 일반 장표 · `s-fig`(피그마 벡터) · `s-fig s-emb`(발표용 iframe). 모든 슬라이드에 `data-part`(장 번호)·`data-chap`(절 라벨)을 단다 — 목차 추출·목록의 키가 된다.
- 페이지 번호 요소는 종류별로 다르다(`.dfoot .pg` / `.figpg` / srcdoc 안 `&lt;b&gt;NN&lt;/b&gt;`). **손으로 고치지 말고 `scripts/deck_edit.py` 로만 재번호**한다.
- 헤더 문구 규칙: 거버닝 메시지는 전역 규칙(~/.claude/CLAUDE.md 「거버닝 메시지 문체」)을 따른다. 태그라인은 「무엇 · 범위 · 기준」만.

## 2. 피그마 장표를 벡터로 가져오기 (`scripts/fig2svg.py`)
1. 피그마에서 추출용 프레임을 한 섹션/프레임에 x 순서로 모은다(`get_metadata` 로 자식 x 정렬 → 순서 확정).
2. 프레임별 `download_assets(defaultFormat:"pdf")` → URL 이 단명이므로 **한 번에 여러 개 호출하고 바로 curl** 로 `01.pdf…` 저장.
3. `python scripts/fig2svg.py --prefix i --part 2 --chap "2.2 …" --out ins.html 01.pdf 02.pdf …`
   - 텍스트를 패스로 변환(text_as_path) → 서체 의존 없음, 선명도 벡터. MCP `svg` export 는 텍스트가 누락되므로 쓰지 않는다.
   - 드롭섀도 프레임은 export 가 1700×1000 으로 커지고 3400×2000 그림자 래스터가 들어감 → 스크립트가 제거·크롭.
   - 장별 id 접두(`i01_`…)로 인라인 SVG 충돌 방지. 이미 덱에 있는 접두와 겹치지 않게 prefix 를 바꾼다(`check_slides.py` 가 중복을 잡는다).
4. `python scripts/deck_edit.py deck.html insert 24 ins.html` (또는 `replace 37-46 ins.html`).
5. 피그마 쪽 자리표시자 처리: 페이지 번호 `00` 은 `.figpatch` 가 가리고 `.figpg` 가 덱 번호를 얹는다. 코드박스가 `A03` 등 덱 체계와 다르면 `scripts/codebox_overlay.py --pages 24-35 --ch 2 --name "핵심 이슈" --start B06` 으로 HTML 코드박스를 덮는다(원본 수정 불필요, 서체 동일).
6. **피그마 원본 텍스트 수정이 막힐 때**(Pretendard 로 된 텍스트는 use_figma 에서 폰트 로드 불가): Noto 로 바꾸지 말고, 덱 쪽에서 같은 규격의 HTML 요소(`.figbar` 예시)를 덮는다. 원본에 남은 오타는 사용자에게 보고한다.

## 3. 발표용 인터랙티브 HTML 삽입 (`s-emb`)
- 별도 HTML(자동 재생 와이어프레임 플로우 등)을 `<iframe class="embdeck" srcdoc="…">` 로 넣는다(HTML 이스케이프). 상단 헤더 문구 등 덱과 중복되는 요소는 srcdoc 안에서 제거.
- 안쪽 푸터 번호는 `&lt;b&gt;NN&lt;/b&gt;` 형태로 두면 deck_edit 가 재번호한다.
- 키보드 브리지: srcdoc 끝에 방향키를 `parent.postMessage({deckKey})` 로 올리는 스크립트, 덱 쪽은 Space 로 안쪽 `toggle()` 호출(템플릿에 포함).
- 이 슬라이드는 PDF·피그마 백업에서 **정지 화면**이 된다 — 목차 비고에 적는다.

## 4. 편집 루틴
- 목록: `deck_edit.py deck.html list` · 삭제: `delete 24 37-46` · 삽입: `insert 41 emb_typeA.html` · 교체: `replace 37-46 rep.html`. 실행마다 `_prev.html` 롤링 백업이 남는다. 빠지는 섹션(예: iframe 장표)은 별도 파일로 보관해 두었다가 다시 `insert` 한다.
- 검수 렌더: `scripts/render_pages.sh deck.html out/ 24 29 1` → PNG 를 열어 헤더·번호·오버레이 확인. **병렬 크롬은 종료가 안 되므로 순차**.
- 자동 점검: `python scripts/check_slides.py deck.html` — 번호 연속·자리표시자(B0X/00)·id 접두 중복·미검증 플래그.

## 5. 피그마 백업 업로드 (전 장 PNG 프레임)
1. `scripts/render_pages.sh deck.html render/ 1 88 2` → 3200×1800 PNG.
2. `use_figma` 로 대상 섹션 안에 1600×900 **일반 프레임**(오토레이아웃 없음)을 페이지 수만큼 생성. 배치 = 간지 기준 좌→우, 장이 바뀌면 다음 행(20열 랩, 간격 200 / 장 사이 600). 이름 `P{NN}_{코드}_{절}`.
3. `upload_assets(count≤60, nodeIds=[…])` 를 44장씩 2회 → 각 submitUrl 에 `curl -X POST -H 'Content-Type: image/png' --data-binary @pNN.png`(8병렬 OK).
4. **응답이 200·imageHash 여도 필이 안 붙을 수 있다** → 응답의 imageHash 로 `node.fills=[{type:'IMAGE',scaleMode:'FILL',imageHash}]` 를 use_figma 로 직접 적용하고, 섹션 스크린샷으로 확인.

## 6. 목차 시트
- `python scripts/deck_toc.py deck.html --xlsx <목차.xlsx> --sheet 목차_YYMMDD --titles titles.json` — HTML 장표는 자동, 피그마 벡터 장표는 `titles.json`(페이지→[코드, 태그라인, 제목])으로 보완(렌더 PNG 를 보고 옮겨 적는다).
- 구글시트로 공유된 xlsx 는 **로컬 드라이브 동기화 경로의 파일을 직접 수정**해야 같은 파일 ID·링크가 유지된다(Drive MCP `update_file` 은 메타만 변경). 수정 전 사본을 `old/` 에 남긴다.

## 7. PDF 제출본
- 브라우저 인쇄(`@media print`, 장당 1페이지) 또는 피그마 PDF export 병합. 피그마 PDF 를 합칠 때는 `scripts/build_compressed_pdf.py`(3000px↑ 그림자 래스터 치환·JPEG 압축)로 용량을 줄인다. 반투명 카드 그림자(3000px 미만 RGBA)는 건드리면 검게 깨진다.

## 8. 스타일·표기 규칙 (이 프로젝트에서 확정, 이후 기본값)
- 박스 모서리 r=0. 강조는 배지(NEW=옐로 배경+네이비 글자, 이동/변경=네이비 배경+흰 글자)만 — 텍스트·면 채색 금지, 블루 강조 금지. 레드는 경고·결손 표기에만.
- IA/메뉴구조 장표는 **메뉴트리 형태**가 기본(루트 → Depth1 카드 → Depth2 박스 목록, Depth 2 까지). 표·텍스트 나열 금지.
- 거버닝 메시지·서브타이틀은 전역 규칙. 본문은 명사형 종결·개조식.
- 피그마 런타임에서 만든 텍스트는 Noto Sans KR 로 생기며(Pretendard 로드 불가) 디자인파트가 서체를 교체한다 — 덱에 벡터로 가져오면 그 시점의 서체가 고정된다.

## 9. 하지 않는 것
- 클라이언트 산출물(덱·스크린샷·로고)을 이 리포에 복사하지 않는다(민감자료 3원칙). 이 문서와 스크립트만 남긴다.
- 발표용 iframe 장표를 "교체 범위"에 포함해 삭제할 때는 반드시 별도 파일로 보관하고 사용자에게 고지한다.
- 번호·코드를 수작업으로 고치지 않는다(스크립트 경유).
