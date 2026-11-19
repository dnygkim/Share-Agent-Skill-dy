# IA 추출 고도화 — 문제·해결 핸드오프

> **목적**: analyst의 IA 추출이 "사용자가 실제 보는 IA"와 어긋나는 문제들을 정리. 다른 세션이 이 문서로 ① `site-ia-extraction.md` 갱신 ② `scripts/ia_extract.py` 신규 구현을 진행한다.
> **검증 사례**: `https://www.gscaltex.com/kr/` (실측, 본문 §6).
> **핵심 한 줄**: IA의 가치는 "**분리된 화면을 하나도 빠짐없이, 합치지도 쪼개지도 않고**" 뽑는 데 있다. 그래야 기획/디자인/퍼블/개발 범위가 정확히 잡힌다.

---

## 1. GNB 추출 ≠ IA 추출 (서로 다른 작업)
- **GNB**: 상단 대메뉴 골격(개요용).
- **IA**: 분리된 **모든 페이지를 3뎁스까지 하나씩 노드로**. 공수 산정의 기준은 항상 **IA(전수 페이지)**.
- 추출기 기본값 = **full IA**. GNB-only는 "개요 요약"으로만 별도 제공.

## 2. 관찰된 오류 7종 (실제로 본 사례)
| # | 오류 | 사례 | 영향 |
|---|------|------|------|
| E1 | 슬림 nav만 긁고 **메가메뉴(3뎁스) 누락** | 첫 스크랩 39앵커=2뎁스만 | 3뎁스 통째 누락 |
| E2 | **분리 페이지를 한 줄로 합침** | Future 5페이지 → "A·B·C·D·E" 1줄 | 페이지 과소 → 공수 깎임 |
| E3 | **탭을 별도 페이지로 쪼갬** | 재무정보(1페이지·탭2) → 2페이지 | 페이지 과대 |
| E4 | **탭을 트리에서 인라인 처리** | "탭: 손익계산서·재무상태표" 1줄 | 디자인 뷰 누락 |
| E5 | **footer/유틸 메뉴 무시** | 법적고지·개인정보처리방침 누락 | 별도 페이지(특히 개인정보처리방침=퍼블 큼) 누락 |
| E6 | **회원 도메인 미유추** | 로그인 있으면 가입·탈퇴·ID/PW찾기·마이페이지가 따라옴 | 회원 플로우(기획·디자인·퍼블·개발 큼) 통째 누락 |
| E7 | **접근 차단 영역 추측** | 로그인 必 영역을 임의 추정 | 부정확한 IA |
| (보조) | **인코딩/콘솔 깨짐 오인** | 소스 UTF-8 정상인데 cp949 콘솔서 깨짐 | "추출 실패" 오판 |

## 3. 해결 방향 — 추출 규칙 (구현 대상)
1. **정본 = 가장 깊은 패널**: 슬림 nav가 아니라 메가메뉴/사이트맵(`menu-box`+`depth3-list` 류)을 정본으로. (E1)
2. **dedup**: 같은 메뉴가 슬림·메가·모바일 3중 렌더됨 → href+텍스트로 중복 제거. 블록 경계는 div 밸런싱으로 정확히 끊어 **인접 메뉴 흡수 방지**(고객지원이 Recruit로 빨려든 사례). (E1)
3. **1 노드 = 1 줄 = 제 깊이**: 형제 페이지를 점(·)/쉼표로 합치지 말 것. 탭도 트리에선 **각자 제 줄(3뎁스)** 로 펼침. (E2·E4)
4. **type 태깅**: 모든 노드에 `page | tab | group | external`.
   - `group`: `href="#"` + 자식 URL 각기 다름 → 자식은 **별도 페이지**.
   - `tab`: **부모 URL = 자식 URL** (또는 페이지에 `tabmenu` UI) → 부모=`page`(탭형), 자식=`tab`. (E3)
   - `external`: 타 도메인 → 페이지 카운트 제외, "외부 링크"로 분리. (E5 패밀리사이트·SNS)
5. **이중 카운트 산출**:
   - `page_count` = 개발·이관 단위 (탭은 부모 page로 롤업).
   - `view_count` = 기획·디자인·퍼블 단위 (탭 각각 포함).
   - 탭 = "페이지 1 + 디자인 뷰 N" — 공짜 아님, N페이지도 아님.
6. **footer/유틸 필수 포함**: 법적고지·개인정보처리방침·사이트맵·이메일무단수집거부·검색 등 = 별도 페이지. 패밀리사이트·SNS = external 분리. (E5)
7. **회원/인증 도메인 유추**: 로그인 단서(로그인·login·마이페이지·회원·가입·탈퇴 키워드) 발견 시, 표준 회원 페이지 세트를 IA에 포함(`type:page, source:추정`):
   - 로그인 · 회원가입(약관동의·본인인증·정보입력·완료) · 아이디/비밀번호 찾기 · 소셜로그인 · **회원정보수정 · 회원탈퇴** · 마이페이지(주문/예약/포인트 등 서비스별). (E6)
8. **접근 차단 시 멈춤 체크포인트**: 로그인 필요·봇차단으로 못 들어가는 영역은 **추측 금지**. 진행을 멈추고 사용자에게 요청:
   - "① 로그인 후 메뉴/화면을 **캡처해 이미지로 첨부**해 주세요, ② 또는 테스트 계정, ③ 또는 메뉴 구조를 알려주세요."
   - 받은 자료로 회원/마이 영역 IA 완성. 못 받으면 해당 영역 `source:추정`+`접근불가` 플래그. (E7)
9. **인코딩 강제**: fetch 시 charset 메타 우선, 출력은 `sys.stdout.reconfigure(encoding="utf-8")`. (보조)
10. **출처 태깅**(기존 규칙 유지): 노드별 `실측 | 추정`(+근거 1줄).

## 4. 산출 스키마 (`ia_extract.py` 출력 = JSON)
```json
{
  "site": "https://www.gscaltex.com/kr/",
  "extracted_at": "<주입>",
  "tree": [
    {"name":"IR","url":"/kr/ir","depth":1,"type":"page","source":"실측","children":[
      {"name":"재무정보","url":"/kr/Ir/FinancialInfo/Income","depth":2,"type":"page","tabs":[
        {"name":"손익계산서","url":"/kr/Ir/FinancialInfo/Income","type":"tab"},
        {"name":"재무상태표","url":"/kr/Ir/FinancialInfo/Financial","type":"tab"}
      ]},
      {"name":"신용등급","url":"/kr/Ir/Creditrating","depth":2,"type":"page"},
      {"name":"보고서","url":"#","depth":2,"type":"group","children":[
        {"name":"감사보고서","url":"/kr/Ir/Irinfo/AuditReport","depth":3,"type":"page"},
        {"name":"사업보고서","url":"/kr/Ir/Irinfo/BusinessReport","depth":3,"type":"page"}
      ]}
    ]}
  ],
  "footer": [{"name":"법적고지","url":"/kr/LegalNotice","type":"page"},
             {"name":"개인정보처리방침","url":"/kr/PrivacyPolicy","type":"page"}],
  "external": [{"name":"(주)GS","url":"http://www.gs.co.kr/"}],
  "member_domain": {"detected": false, "inferred_pages": []},
  "access_blocked": [],
  "counts": {"page_count": 0, "view_count": 0, "external_count": 0}
}
```
- builder/architect는 이 JSON으로 IA 표(2뎁스/3뎁스)와 페이지·뷰 카운트를 만든다.
- `report-spec.md`/`effort-estimation-methodology.md`의 측정단위 환산은 **page_count→개발, view_count→디자인/퍼블** 로 연결.

## 5. 구현 힌트 (검증된 로직)
- fetch: `urllib`(UA 헤더) → charset 메타 감지 → decode. 동적 메뉴면 firecrawl/playwright 폴백.
- 메가메뉴 파싱: `menu-box`(1뎁스 패널) 블록을 div 밸런싱으로 추출 → `ul.menu-list>li>a.item`(2뎁스), `a.item.more`(자식 있음 마커) + `ul.depth3-list>li>a.item`(3뎁스).
- 탭 판정: 부모 url == 자식 url, 또는 페이지 fetch 후 `tabmenu`/`tabmenu-list` 클래스 확인.
- footer: `<footer>` 영역 앵커 추출 → 내부/외부 분리.
- 로그인 감지: 본문에서 `로그인|login|마이페이지|회원|가입|탈퇴` grep.
- ※ 클래스명(`menu-box`,`depth3-list`,`tabmenu`)은 GS칼텍스(사이트별 상이). 추출기는 **클래스 의존을 최소화**하고 ul/li 중첩 + URL 경로 깊이로 교차검증.

## 6. 검증 사례 — GS칼텍스 (실측 IA, 올바른 표기)
GNB 7 대메뉴 + footer. (page=실페이지, tab=탭뷰, group=#묶음)
```
Company /kr/Company
  비전 · CEO · 연혁                         (page ×3)
  브랜드 (group)  → 슬로건·CI·BI            (page ×3)
  네트워크 (group) → 국내·해외              (page ×2)
  자회사·관계사 (group) → 국내자회사·해외자회사·관계사 (page ×3)
  PR룸 (group) → 보도자료·매거진·홍보영상·스포츠후원 (page ×4)
Future /kr/future
  DAX(DX+AX) · 그린트랜스포메이션 · 에너지플러스 · 미래형주유소 · 에너지플러스에코 (page ×5, 각 분리)
Business /kr/Business
  정유(group)→휘발유·고급휘발유·경유·등유·LPG·항공유·해상용연료유·아스팔트·중유·기타 (page ×10)
  방향족(group)→벤젠·톨루엔·파라자일렌·혼합자일렌·케미칼제품 (×5)
  올레핀(group)→에틸렌·프로필렌·C4유분 (×3)
  폴리머(group)→PP·복합수지·LFT·HDPE·저탄소MR복합수지 (×5)
  베이스오일(group)→Gr.II·Gr.III·WhiteOil (×3)
  윤활유 · 생산공정 · 연구개발 (page ×3)
Sustainability /kr/Sustainability
  윤리경영·SHE경영·인권경영·상생경영·고객경영 (page ×5)
  사회공헌(group)→활동체계·마음톡톡·일반사회공헌활동·GS칼텍스재단/예울마루 (×4)
  지속가능성보고서 (page ×1)
IR /kr/ir
  재무정보 (page·탭형) → [탭] 손익계산서 / 재무상태표
  신용등급 (page)
  보고서(group) → 감사보고서 · 사업보고서 (page ×2)
Recruit /kr/Recruit
  인재상 (page) · 인사제도(group→인사제도·복리후생·인재육성 ×3) · 채용사이트(external)
고객지원 /kr/CustomerSupport
  공지사항 · 문의하기 · 주유소·충전소·EV찾기 · MSDS · 파트너 (page ×5)
[FOOTER] 법적고지 · 개인정보처리방침 (page ×2)
[EXTERNAL] 패밀리사이트 10여(GS폴리머·Kixx·오토오아시스·(주)GS·GS에너지·GS엠비즈·GS바이오·GS에코메탈·이노폴리텍·상지해운·GS EV충전) + SNS 6
[MEMBER] 없음(비회원 정보형 — 로그인 단서 0)
```
- **page_count ≈ 74** (Company15·Future5·Business29·Sustainability10·IR4·Recruit4·고객지원5·footer2) + 1뎁스 랜딩 7.
- **view_count** = page_count + 탭뷰(재무정보 +1 등).
- 만약 첫 실수대로 "GNB 한 줄 요약"만 했다면 → footer 2 + 분리페이지 수십 개 누락 → 견적 붕괴.

## 7. 다른 세션 작업 지시 (To-Do)
1. `references/site-ia-extraction.md`에 본 문서 §1·§3 규칙을 **"IA 추출 정밀도 규칙"** 섹션으로 병합.
2. `scripts/ia_extract.py` 신규: §4 JSON 스키마 출력 + §5 로직. CLI `python scripts/ia_extract.py <url>`.
3. `references/report-spec.md` / `effort-estimation-methodology.md`에 **이중 카운트(page/view) → 공수 환산** 연결 명시.
4. `agents/analyst.md`에 ⏸ **접근 차단 체크포인트**(로그인 영역 → 사용자에 캡처/계정 요청) 추가.
5. analyst 산출(`01_analysis.md`)에 IA 트리(JSON) + page/view 카운트 + 미접근/추정 플래그 포함 의무화.
