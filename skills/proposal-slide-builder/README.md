# proposal-slide-builder — 제안서 본문 슬라이드 생성 스킬 (제안서 4단계)

확정 목차(또는 사용자에게 받은 핵심 정보)를 넣으면 섹션별 콘텐츠 초안(마크다운) → HTML 슬라이드 미리보기 → pptx · Figma 순으로 IT 서비스 · 플랫폼 제안서 본문 슬라이드가 나오는 제안서 4단계 스킬

## 한눈에 보기

| <div align="center"><sub>항목</sub></div> | <sub>내용</sub> |
|:---|:---:|
| <sub>목적</sub> | <sub>IT 서비스 · 플랫폼 제안서 본문 슬라이드의 섹션 단위 제작 · 콘텐츠 확정 후에만 포맷 렌더링</sub> |
| <sub>이럴 때 사용</sub> | <sub>목차 확정(3단계) 후 본문 제작 · 표지 · 전략 방향 · 기대효과 · IA 구조도 등 특정 섹션만 필요할 때 · 제안서를 HTML · PPT · Figma로 만들 때</sub> |
| <sub>넣는 것</sub> | <sub>1~3단계 결과(있으면 근거로 활용, 없으면 핵심 정보 질문) · 공통 변수 9개 · (CI 요청 시) HEX 5개 · (있으면) 디자인파트 · 클라이언트 양식(피그마 장표 템플릿 · PPT 마스터)</sub> |
| <sub>나오는 것</sub> | <sub>콘텐츠 초안(`.md`) → HTML 슬라이드 덱(`.html`, 기본 1280×720) → `.pptx` · Figma 16:9 프레임(복수 선택)<br>HTML을 최종 제출본으로 정하면 제출 규격 HTML 덱</sub> |
| <sub>부르는 법</sub> | <sub>`제안서 슬라이드 만들어줘` · `제안서 PPT 작성` · `SECTION N 작성해줘` · `표지/전략방향/기대효과 슬라이드` · `IA 구조도 슬라이드` · `제안서를 PPT로/HTML로/피그마로` · 슬래시 명령 `/proposal-slide-builder`</sub> |
| <sub>제작</sub> | <sub>김단영(dykim)</sub> |
| <sub>연계</sub> | <sub>제안 스킬 파이프라인 **④**(아래 표) · 하네스 [agent/proposal](../../agent/proposal/) S4 1차 추출 · S6 n차 추출의 `slide-builder`가 이 스킬 우선 호출<br>PPT 장표 규격 · 스타일은 [`deckslide-design-guideline`](../deckslide-design-guideline/README.md)과 함께 사용 가능</sub> |

**제안 스킬 파이프라인 · agent/proposal 단계 대응**

| <div align="center"><sub>순서</sub></div> | <sub>스킬</sub> | <sub>하는 일</sub> | <sub>agent/proposal 단계 · 에이전트</sub> |
|:---|:---:|:---:|:---:|
| <sub>①</sub> | <sub>[`rfp-analysis-research`](../rfp-analysis-research/README.md)</sub> | <sub>RFP 구조화 + 업계 리서치</sub> | <sub>S1 RFP 분석 · 리서치 · `rfp-analyst`</sub> |
| <sub>②</sub> | <sub>[`ux-journey-insight`](../ux-journey-insight/README.md)</sub> | <sub>사용자 여정맵 + UX 개선 전략</sub> | <sub>S1 선택 모듈 · `ux-strategist`</sub> |
| <sub>③</sub> | <sub>[`proposal-structure-validation`](../proposal-structure-validation/README.md)</sub> | <sub>목차 구성 + 자기검증</sub> | <sub>S3 제안 목차(GATE ②) · `structure-validator`</sub> |
| <sub>**④**</sub> | <sub>**`proposal-slide-builder`(이 스킬)**</sub> | <sub>본문 슬라이드 제작</sub> | <sub>S4 1차 추출 · S6 n차 추출 · `slide-builder`</sub> |

> 하네스의 S2 컨셉 · S5 피드백 반영 · S7 최종본은 이 4개 스킬 밖의 에이전트 단계 — 전체 7단계 흐름 = [agent/proposal/README.md](../../agent/proposal/README.md)

## 이렇게 요청

| <div align="center"><sub>상황</sub></div> | <sub>요청 예시</sub> | <sub>나오는 것</sub> |
|:---|:---:|:---:|
| <sub>제안서 본문 전체</sub> | <sub>`제안서 슬라이드 만들어줘` · `제안서 PPT 작성해줘`</sub> | <sub>범위 확인 → 전 섹션 콘텐츠 초안 → HTML 덱 → PPT/Figma</sub> |
| <sub>특정 섹션만</sub> | <sub>`SECTION 5 작성해줘` · `표지 슬라이드 만들어줘` · `기대효과 슬라이드 만들어줘`</sub> | <sub>해당 섹션 초안 → HTML → 변환</sub> |
| <sub>IA 구조도</sub> | <sub>`IA 구조도 슬라이드 만들어줘`</sub> | <sub>SECTION 3 서비스 구조 — 기능 범위 카드 · Front Office · Back Office IA 다이어그램</sub> |
| <sub>포맷 지정</sub> | <sub>`제안서를 PPT로 만들어줘` · `피그마로 만들어줘`</sub> | <sub>HTML 확인 후 `.pptx` 또는 Figma 16:9 프레임</sub> |
| <sub>HTML이 최종 제출본</sub> | <sub>`제출본은 HTML 덱으로 만들어줘`</sub> | <sub>제출 규격 HTML 덱(디자인파트 양식이면 1600×900) · 변환 대신 취합 루틴</sub> |

## 진행 단계

```
STEP 0 범위 확인 → STEP 1 콘텐츠 초안(md) → [확정] → STEP 2 HTML 미리보기 → [확인] → STEP 3 PPT · Figma 변환
                                                                              (HTML 최종본이면 STEP 3 대신 취합 루틴)
```

| <div align="center"><sub>단계</sub></div> | <sub>하는 일</sub> | <sub>사용자 할 일</sub> | <sub>결과물</sub> |
|:---|:---:|:---:|:---:|
| <sub>STEP 0 범위 확인</sub> | <sub>대상 섹션 · 공통 변수 9개 · 스타일 · 제출 포맷 · 작업 사이즈 확정(이전 대화에 있으면 추출 후 확인만)</sub> | <sub>아래 확인 질문 답변</sub> | <sub>확정 범위 · 변수 · 규격</sub> |
| <sub>STEP 1 콘텐츠 초안</sub> | <sub>`references/section-prompts.md` 대상 섹션 읽기 → 슬라이드 단위 마크다운(적용 레이아웃 패턴 명시 · 변수 자리표시자 유지) → 섹션별 자기검증 `[통과/보완필요]`</sub> | <sub>**초안 확정 또는 수정 요청 — 확정 전 포맷 렌더링 보류**</sub> | <sub>콘텐츠 초안(`.md`)</sub> |
| <sub>STEP 2 HTML 미리보기</sub> | <sub>`references/design-system.md` 포맷별 가이드 읽기 → 확정 작업 사이즈의 HTML 덱 생성(CSS 변수 컬러 · 인쇄 PDF 대응) · 곧바로 PPT/Figma로 가지 않는 필수 중간 단계</sub> | <sub>**레이아웃 · 컬러 · 텍스트 확인 — 수정 요청 시 갱신 후 재제시**</sub> | <sub>HTML 덱</sub> |
| <sub>STEP 3 PPT · Figma 변환</sub> | <sub>pptx = `pptx` 스킬 지침대로 생성 · HTML 덱과 구성 · 컬러 일치 / Figma = `use_figma` 16:9 프레임 → 변환 후 `[CI 확인 필요]` · `[미검증]` 잔존 점검 · 남으면 안내</sub> | <sub>변환 포맷 선택(복수 가능) · Figma는 생성 전 슬라이드 수 · 패턴 확인</sub> | <sub>`.pptx` · Figma 프레임</sub> |
| <sub>(HTML 최종본) 취합 루틴</sub> | <sub>STEP 3 대신 제출 규격 덱 취합 — agent/proposal의 `references/deck-production-playbook.md` · `template/deck_1600_template.html` · `scripts/deck_edit.py` · `fig2svg.py` · `render_pages.sh` · `deck_toc.py`<br>페이지 번호 · 장표 코드는 스크립트로만 재부여</sub> | <sub>규격 · 양식 · 소스 혼합 · 장표 코드 체계 확정</sub> | <sub>제출용 HTML 덱</sub> |

**STEP 0 확인 질문**

| <div align="center"><sub>#</sub></div> | <sub>질문</sub> | <sub>답 예시</sub> | <sub>기본값</sub> |
|:---|:---:|:---:|:---:|
| <sub>①</sub> | <sub>대상 섹션</sub> | <sub>「전체」 · 「SECTION 1~3」 · 「표지만」</sub> | <sub>[선택] 섹션(0-1 회사 소개 · 0-2 수행 실적 · 9 유지보수) 포함 여부 함께 확인</sub> |
| <sub>②</sub> | <sub>공통 변수 9개</sub> | <sub>`{클라이언트명}` 테스트커머스 · `{프로젝트유형}` 신규구축</sub> | <sub>미확정 항목은 질문 또는 `[확인 필요]` 표기</sub> |
| <sub>③</sub> | <sub>스타일(HTML 추출 전 기본 스타일 여부 확인)</sub> | <sub>「기본으로」 · 「CI 적용」</sub> | <sub>하우스 스타일(warm paper + near-black ink) · CI는 요청 시만 HEX 5개 확정 · 끝내 미확정이면 하우스 기본 + `[CI 확인 필요]` · 무응답 진행 때도 기본 양식(보류 금지)</sub> |
| <sub>④</sub> | <sub>실제 제출 포맷(HTML 최종본 / HTML은 미리보기 · PPT · Figma가 제출본)</sub> | <sub>「PPT가 제출본」 · 「HTML 최종본」</sub> | <sub>무응답이면 PPT/Figma 제출본 가정 + 한 줄 안내 · HTML 최종본이면 규격 · 양식 · 소스 혼합(HTML 직접 / 피그마 장표 벡터 취합 / 발표용 HTML iframe) · 장표 코드 체계까지 추가 확정</sub> |
| <sub>⑤</sub> | <sub>작업 사이즈(장표 규격) — 포맷 답 직후</sub> | <sub>「1600×900」</sub> | <sub>HTML 미리보기 1280×720 · HTML 최종본 · 피그마 양식 1600×900 · 1920×1080 · pptx 16:9(33.87×19.05cm) · A4 가로 중 제시 후 확인<br>양식이 있으면 그 규격이 정본(프레임 크기 · 여백 함께 기록) · 확정 전 골격 생성 보류 · 초안 머리말에 「작업 사이즈: WxH · 양식: …」</sub> |

**공통 변수 9개**(`references/design-system.md` §1 · 예시는 가상 값)

| <div align="center"><sub>변수</sub></div> | <sub>설명</sub> | <sub>예시</sub> |
|:---|:---:|:---:|
| <sub>`{클라이언트명}`</sub> | <sub>발주사 명칭</sub> | <sub>테스트커머스</sub> |
| <sub>`{사업명}`</sub> | <sub>프로젝트 공식 명칭</sub> | <sub>커머스 플랫폼 구축</sub> |
| <sub>`{프로젝트유형}`</sub> | <sub>신규구축 / 개편고도화 / 운영유지보수</sub> | <sub>신규구축</sub> |
| <sub>`{산업군}`</sub> | <sub>서비스 산업 분류</sub> | <sub>유통 · 커머스</sub> |
| <sub>`{주요기능}`</sub> | <sub>핵심 기능 키워드 3~5개</sub> | <sub>상품 검색, 결제, 관리자</sub> |
| <sub>`{기술스택}`</sub> | <sub>FE/BE/인프라 구성</sub> | <sub>React, Spring Boot, AWS</sub> |
| <sub>`{구축안}`</sub> | <sub>제안 옵션명</sub> | <sub>1안(단일국가) / 2안(다국가 확장)</sub> |
| <sub>`{예산범위}`</sub> | <sub>개략 예산</sub> | <sub>2억 내외</sub> |
| <sub>`{차별화포인트}`</sub> | <sub>수주사 강점 키워드</sub> | <sub>UX 최적화, 안정적 인프라</sub> |

## 산출물

| <div align="center"><sub>산출물</sub></div> | <sub>형식</sub> | <sub>구성</sub> |
|:---|:---:|:---:|
| <sub>콘텐츠 초안</sub> | <sub>`.md`</sub> | <sub>슬라이드 단위 구분 · 적용 레이아웃 패턴 · 변수 자리표시자 · 섹션별 자기검증 `[통과/보완필요]`<br>표형 · 카드형 · 비교형은 마크다운 표, 그 외(2분할형 · 스텝형 · 타임라인형 · IA형)는 슬라이드별 블록(제목 + 불릿)</sub> |
| <sub>HTML 덱</sub> | <sub>`.html` 단일 파일</sub> | <sub>1슬라이드 = `<section class="slide">` 고정 비율 컨테이너(기본 1280×720) · 컬러 토큰을 `:root`에 인라인(외부 `.css` link 금지) · 키보드 좌우 이동 또는 스크롤 스냅 · `@media print` 페이지 분할(Ctrl+P → PDF)</sub> |
| <sub>PPT</sub> | <sub>`.pptx`</sub> | <sub>16:9 슬라이드 마스터에 헤더바 · 푸터 공통 적용 · 레이아웃 패턴을 도형 · 표 · SmartArt로 구현 · HTML 덱과 구성 · 컬러 일치</sub> |
| <sub>Figma</sub> | <sub>`use_figma` 디자인 프레임</sub> | <sub>16:9 프레임(1280×720)을 슬라이드 수만큼 · 카드형 · 2분할형 · 표지처럼 단순 레이아웃에 강점 · 표 · 복잡 IA는 결과 편차로 수동 보정 필요</sub> |
| <sub>HTML 최종본</sub> | <sub>제출 규격 `.html`</sub> | <sub>디자인파트 양식(1600×900)이면 스테이지 핏 골격(하네스 `template/deck_1600_template.html`) · 피그마 장표 벡터 취합 · 박스 r=0 · 강조는 배지만 · 레드는 경고에만</sub> |
| <sub>agent/proposal S4 · S6</sub> | <sub>`04_content.md` · `04_refs.md` → 덱 `.html`(+ `.pptx` · Figma)</sub> | <sub>덱 파일명 `{업무명}-제안서-v0.x-YYYYMMDD.html` · 저장 `output/output-{프로젝트 폴더}/`(`agents/slide-builder.md`)</sub> |

**섹션 구성**(`references/section-prompts.md`)

| <div align="center"><sub>섹션</sub></div> | <sub>분량</sub> | <sub>주 레이아웃</sub> | <sub>연계</sub> |
|:---|:---:|:---:|:---:|
| <sub>0 표지</sub> | <sub>1장</sub> | <sub>2분할형</sub> | <sub>—</sub> |
| <sub>0-1 회사 소개 [선택]</sub> | <sub>1~2장</sub> | <sub>다크 배경 + 인포 블록 · 조직도</sub> | <sub>—</sub> |
| <sub>0-2 수행 실적 [선택]</sub> | <sub>1장</sub> | <sub>표형</sub> | <sub>—</sub> |
| <sub>1 프로젝트 개요</sub> | <sub>2~3장</sub> | <sub>2분할형 · 표형 + 비교형 · 벤치마킹 표형 [선택]</sub> | <sub>`rfp-analysis-research` 결과 활용</sub> |
| <sub>1-1 전략 방향</sub> | <sub>1~2장</sub> | <sub>카드형 3열</sub> | <sub>—</sub> |
| <sub>2 시스템 아키텍처</sub> | <sub>1~2장</sub> | <sub>구성도(다이어그램) · 인프라 · 개발 환경 표형 [선택]</sub> | <sub>`rfp-analysis-research` 기술 검토 참고</sub> |
| <sub>3 서비스 구조(IA)</sub> | <sub>2~3장</sub> | <sub>카드형 3×2 · IA 다이어그램형(Front · Back Office)</sub> | <sub>`ux-journey-insight` 결과 활용</sub> |
| <sub>4 수행 범위 및 산출물</sub> | <sub>1~2장</sub> | <sub>스텝형 · 상세 업무 범위 표형 [선택]</sub> | <sub>`proposal-structure-validation` 실행 전</sub> |
| <sub>5 투입 인력 및 공수</sub> | <sub>1~2장</sub> | <sub>표형 · 구축안 견적 비교형 [복수 안]</sub> | <sub>SECTION 6과 M/M 교차검증</sub> |
| <sub>6 추진 일정</sub> | <sub>2장</sub> | <sub>타임라인형 · 월별 투입 · 마일스톤 표형</sub> | <sub>SECTION 5와 M/M 교차검증</sub> |
| <sub>7 기대효과</sub> | <sub>1장</sub> | <sub>카드형 3×2</sub> | <sub>`proposal-structure-validation` 최종 검증</sub> |
| <sub>8 전제 조건 및 참고사항</sub> | <sub>1장</sub> | <sub>2분할 + 캡션</sub> | <sub>`proposal-structure-validation` 최종 검증</sub> |
| <sub>9 유지보수 및 운영지원 [선택]</sub> | <sub>1~2장</sub> | <sub>표형 + 구분 다이어그램 · 표형</sub> | <sub>—</sub> |

- **레이아웃 7패턴**(`references/design-system.md` §4): 카드형 · 스텝형 · 타임라인형 · 표형 · IA 다이어그램형 · 2분할형 · 비교형
- **권장 덱 순서**: 표지 → 회사 소개 [선택] → 수행 실적 [선택] → 프로젝트 개요 → 전략 방향 → 서비스 구조 → 추진 로드맵(SECTION 6 타임라인) → 단계별 상세 일정 · 산출물(SECTION 4) → 시스템 아키텍처 → 투입 인력 · 공수 → Phase 2 고도화 계획 [해당 시] → 기대효과 → 유지보수 · 운영지원 [선택] → 전제 조건 · 참고사항 → Thank You
- **참조 파일**: `references/section-prompts.md`(섹션 0~9 작성항목 · 작성원칙 · 자기검증 · 권장 순서 — 초안 작성 시) · `references/design-system.md`(공통 변수 · 컬러 · 16:9 구조 · 레이아웃 7패턴 · 포맷별 렌더링 — 포맷 렌더링 직전 필독)

## 설치 · 단독 사용

```bash
# 리포 루트에서 — 이 스킬만 전역 설치
cp -r skills/proposal-slide-builder ~/.claude/skills/proposal-slide-builder
```

- **리포 스킬 일괄 설치**: 리포 루트 `bash install-global.sh`(전역 규칙 · 하우스 스타일 등과 함께 적용)
- **의존성**: 패키지 설치 항목 부재 · pptx 변환 = `pptx` 스킬 · Figma 변환 = `use_figma` 도구(Figma 연결) · HTML 최종본 취합 = agent/proposal `scripts/`(Python · bash, 하네스 README 사전 준비 참고)
- **하네스 안에서 쓸 때**: [agent/proposal](../../agent/proposal/) — 리포 루트 `./sync-skills.ps1`(또는 `bash ./sync-skills.sh`)로 `agent/proposal/.claude/skills/`에 복사 → `agent/proposal/` 폴더에서 Claude Code 실행 → S4 · S6에서 `slide-builder`가 추출 전 확인(기본양식 · 제출 포맷 · 작업 사이즈 · 볼륨 · 레퍼런스 수집) 뒤 `Skill` 도구로 호출(미가용 시 `agents/slide-builder.md` 폴백 절차)

## 주의 · 자주 묻는 질문

| <div align="center"><sub>항목</sub></div> | <sub>내용</sub> |
|:---|:---:|
| <sub>표기 규칙</sub> | <sub>`[미검증]` 출처 미확인 데이터 · `[정책 확인 필요]` 정책 판단 필요 항목 · `[추가 제안]` RFP 외 추가 항목 · `[확인 필요]` 미확정 공통 변수 · `[CI 확인 필요]` CI 요청 후 HEX 미확정</sub> |
| <sub>작성 원칙</sub> | <sub>근거 없는 형용사(「다양한」 「최적의」 「획기적」) 금지 → 구체 수치 · 사례 · 출처 · 평어체(「~한다 · ~이다」) 통일 · 공수(SECTION 5) ↔ 일정(SECTION 6) M/M 교차검증 필수</sub> |
| <sub>하네스 안 문체</sub> | <sub>agent/proposal `references/writing-style.md`가 스킬 지침보다 우선(`agents/slide-builder.md`) — 명사구 종결 · 「~함 · ~임 · ~음」 금지</sub> |
| <sub>분량</sub> | <sub>페이지 수는 공수 산정과 연계 → 과소 산정 금지</sub> |
| <sub>Figma 품질</sub> | <sub>정교한 표 · IA는 결과 편차 → 생성 전 슬라이드 수 · 패턴 확인 및 수동 보정 고지 · 표 · 복잡 다이어그램 중심 슬라이드는 HTML/pptx 우선</sub> |
| <sub>CI 컬러</sub> | <sub>명시 요청 때만 적용(옵트인) · 과거 산출물 · 다른 프로젝트 CI 재사용 금지 · 확인 순서 = 브랜드 가이드 PDF → 공식 웹사이트 CSS → 담당자 HEX 확인(`references/design-system.md` §2)</sub> |
| <sub>저장 경로 표기</sub> | <sub>SKILL.md의 `/mnt/user-data/outputs` · `present_files` · `/mnt/skills/public/pptx/SKILL.md` = claude.ai 파일 환경 경로 · 하네스 안에서는 `output/output-{프로젝트 폴더}/` 저장 · `pptx` 스킬 사용</sub> |
| <sub>착수 체크리스트</sub> | <sub>공통 변수 9개 확정 → 스타일(기본 하우스 · CI는 요청 시) 확인 → 16:9 크기 확인 → RFP · 사전 미팅 내용을 `rfp-analysis-research`에 입력 → SECTION 1~3 초안 → SECTION 5 공수 · SECTION 6 일정 교차검증 → SECTION 7 수치 근거 재확인 → `proposal-structure-validation` 최종 검증 → 제출 전 `[CI 확인 필요]` 전체 검색 · 제거</sub> |

## 릴리즈노트

| <div align="center"><sub>요약내용</sub><img width="1" height="1"></div> | <sub>업데이트 일자</sub><img width="1" height="1"> | <sub>소유자</sub><img width="45" height="1"> |
|:---|:---:|:---:|
| <sub>README 전면 개편 — 목적 · 넣는 것 · 산출물 형태 · 요청 예시 · 진행 단계 순으로 재구성, 릴리즈노트 맨 아래로 이동</sub> | <sub>2026.11.13</sub> | <sub>김단영</sub> |
| <sub>STEP 0 에 실제 제작 포맷 확인(HTML 최종본 vs PPT/Figma 제출본)·작업 사이즈(장표 규격) 확인 단계 추가 — HTML 최종본이면 제출 규격 덱 + 제안서 하네스 취합 루틴(deck-production-playbook) 연계. design-system §3 크기 착수 시 확인·§5 1600×900 덱 안내 (GS칼텍스 제안 실전 반영)</sub> | <sub>2026.09.11</sub> | <sub>김단영</sub> |
| <sub>최초 등록 — 모노레포 재구성, 개별 사용 지원</sub> | <sub>2026.07.07</sub> | <sub>김단영</sub> |
