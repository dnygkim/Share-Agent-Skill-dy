# config.json 스키마 (generate_spec.py 입력)

```jsonc
{
  "template": "type2",                     // 출력 양식 (STEP 1 확정): "type1"=목록·작업관리형(samples/화면명세서-샘플타입1.xlsx)
                                           // "type2"=표준 채번형(samples/화면명세서-샘플타입2.xlsx, 기본·스크립트 네이티브)
                                           // "custom"=사용자 제공 양식 — 이때 "template_path"에 양식 파일 경로 기록
  "project": {
    "title": "롯데호텔 채널시스템 리뉴얼",   // 표지 프로젝트명
    "subtitle": "화면명세서",
    "phase": "설계",
    "doc_no": "LHCR-DG-02",
    "date": "2026-07-13",                  // 표지·개정이력·Last Updated
    "version": "Ver 0.1",
    "author": "김단영",
    "approver": "",
    "reason": "화면명세서 초안 생성 (IA 기반 자동 추출)"  // 개정이력 사유
  },
  "id_rule": {                             // 채번규칙 (STEP 3 확정, 전체 생략 시 RULES.md 기본값)
    "format": "{biz}-{gubun}-{ch}-{cat}-{seq}",  // 세그먼트: biz=업무구분, gubun=구분, ch=채널, cat=대분류, seq=일련번호(+접미사)
    "seq_digits": 5,                       // 일련번호 자릿수
    "suffixes": {"Popup": "P", "Layer": "L", "Tab": "T", "Bottom Sheet": "B"}
  },
  "sheets": [                              // IA 시트당 1개, 배열 순서 = 채번 순서
    {
      "ia_sheet": "01. FO통합",            // parsed.json의 시트명과 일치해야 함
      "out_sheet": "FO_Global",
      "title": "[FO] Global WEB 화면명세서",
      "biz": "FO",                         // 업무구분 코드
      "gubun_code": "SB",                  // ID 두 번째 세그먼트 (기본 SB)
      "channels": [                        // 채널별 (화면ID, 본수) 컬럼 쌍
        {"code": "PW", "id_header": "PC 화면ID", "cnt_header": "PCW\n본수"},
        {"code": "MW", "id_header": "MW 화면ID", "cnt_header": "MOW\n본수"}
      ],
      "code_columns": false,               // true면 채널/코드 컬럼 추가 (BO 스타일)
      "default_type": "Page",              // 화면타입 공란일 때
      "category_key_depth": 1,             // 대분류 키가 되는 Depth 번호
                                           // (FO: Depth0=HOME/GNB라 1, BO: 최상위가 대분류라 1)
      "common_menus": ["로그인", "회원가입"],  // 공통영역 대분류 메뉴명 목록 (STEP 4 확정)
                                           // --preview에서 common/menu 분리 기준, 규정 시트에 (공통) 표기
      "codes": {                           // 대분류 코드표 — 사용자 승인 후 확정 (공통영역 포함)
        "HOME": ["MAIN", "MA"],            // "IA 메뉴명": ["영문명", "2자리 코드"]
        "브랜드": ["BRAND", "BR"]
      }
    }
  ]
}
```

## 주의
- `template`은 generate_spec.py가 직접 읽지 않는다 — 에이전트가 STEP 6 분기(타입2=스크립트 직접 생성 / 타입1·custom=preview JSON을 양식 레이아웃으로 변환)에 사용하는 기록용 필드다.
- `codes`에 없는 대분류가 IA에 존재하면 generate_spec.py가 오류로 중단한다 (의도된 안전장치 — 코드표 승인 없이 임의 채번 금지). 단, `--preview` 모드에서는 `(코드미정)`으로 표시하고 계속 진행한다 (`summary.undefined_categories`로 목록 확인).
- 같은 `biz` 안에서 대분류 코드는 시트가 달라도 동일 채번 카운터를 공유한다 (예: FO_Global의 MA-00005 다음은 FO_Chain에서 MA-00006).
- `category_key_depth` − 시트의 최소 Depth = path 인덱스. 경로가 그보다 짧으면 최상위 이름을 대분류 키로 쓴다 (예: HOME).
