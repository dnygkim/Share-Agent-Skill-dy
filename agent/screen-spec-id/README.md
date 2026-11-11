# screen-spec-id — IA → 화면명세서 자동생성 에이전트

## 릴리즈노트

| <div align="center"><sub>요약내용</sub><img width="1" height="1"></div> | <sub>업데이트 일자</sub><img width="1" height="1"> | <sub>소유자</sub><img width="45" height="1"> |
|:---|:---:|:---:|
| <sub>Dan Jr. 등급 조회 추가 — 각 STEP 승인 직전 `persona.md` 확인(A 진행·B 보고·C 질문), 건너뛴 게이트는 완료 보고에 ID 표기</sub> | <sub>2026.10.22</sub> | <sub>김단영</sub> |
| <sub>v0.3 출력 양식 선택 게이트 도입 + samples 양식 2종 추가</sub> | <sub>2026.07.20</sub> | <sub>김단영</sub> |
| <sub>최초 등록 — IA→화면ID 채번→화면명세서 자동생성</sub> | <sub>2026.07.13</sub> | <sub>김단영</sub> |


메뉴구조도(IA) 엑셀을 입력받아 화면ID 채번 규칙에 따라 **화면명세서 초기 버전(v0.x) xlsx**를 자동 생성하는 Claude Code 에이전트 하네스.

**단계별 진행**: ① 출력 양식 선택(승인) → ② IA 파싱 → ③ 채번규칙 정의(승인) → ④ 공통영역 화면ID 추출(승인) → ⑤ 메뉴별 상세 화면ID 추출(승인) → ⑥ 명세서 생성·검증. 각 단계마다 사용자 승인 후 진행한다.

## 기본양식 (samples/)

실행 시 STEP 1에서 아래 기본양식 중 하나를 선택한다 (또는 사용자 양식 파일 제공).

| <div align="center"><sub>양식</sub></div> | <sub>파일</sub> | <sub>구조</sub> | <sub>용도</sub> |
|:---|:---:|:---:|:---:|
| <sub>**샘플타입1** — 목록·작업관리형</sub> | <sub>`samples/화면명세서-샘플타입1.xlsx`</sub> | <sub>단일 시트: 화면목록(순번·화면코드 PC/MO·depth·본수) + 기획/디자인/퍼블리싱/프로그래밍 공정률 블록, `기준` 시트</sub> | <sub>화면목록과 일정·진척 관리를 한 문서로 겸할 때</sub> |
| <sub>**샘플타입2** — 표준 채번형 (기본)</sub> | <sub>`samples/화면명세서-샘플타입2.xlsx`</sub> | <sub>개정이력·규정 + 채널별 시트(No./상태/수정일/채널별 화면ID·본수/화면타입/화면명/Depth 0~N/비고)</sub> | <sub>표준 채번 기반 화면명세서. `generate_spec.py` 네이티브 출력</sub> |

## 구조
```
screen-spec-id/
├── CLAUDE.md                # 에이전트 지침 (실행 플로우)
├── RULES.md                 # 채번·변환 규칙 정본
├── samples/                 # 기본양식 2종 (샘플타입1·2 — STEP 1 선택지 정본)
├── input/                   # 사용자 IA 파일
├── output/                  # 생성된 화면명세서
├── _workspace/{slug}/       # parsed.json · config.json (중간물)
├── scripts/
│   ├── parse_ia.py          # IA xlsx → JSON 트리
│   └── generate_spec.py     # 채번 + 명세서 xlsx 생성 (타입2 네이티브)
└── references/
    └── config-schema.md     # config.json 스키마
```

## 사용법
1. IA 엑셀을 `input/`에 넣는다.
2. 이 폴더에서 Claude Code를 열고 "이 IA로 화면명세서 만들어줘"라고 요청한다.
3. **출력 양식을 선택한다** — 샘플타입1 / 샘플타입2(기본 권장) / 기타(양식 파일 제공).
4. 단계별 제안을 승인한다 — 채번규칙(ID 포맷·자릿수·접미사) → 공통영역 화면ID → 메뉴별 상세 화면ID.
5. 최종 승인하면 `output/`에 xlsx가 생성된다.

`scripts/generate_spec.py --preview`로 xlsx 생성 전에 채번 결과(공통영역/메뉴별 분리)를 JSON으로 미리 확인할 수 있다. 타입1·기타 양식은 preview 채번 결과를 해당 양식 레이아웃으로 변환해 생성한다(작업관리 블록은 빈칸, 사후 수기 관리).

## 요구사항
- Python 3.12 + `openpyxl`

## 변경이력
- 2026-07-20 v0.3 기본양식 2종(`samples/`) 추가, STEP 1 출력 양식 선택 게이트 도입 (6단계로 재편), config `template` 필드 추가
- 2026-07-15 v0.2 단계별 진행 흐름 도입 (채번규칙 정의 → 공통영역 추출 → 메뉴별 상세 추출, 각 단계 승인 게이트). `--preview` 모드, config `id_rule`·`common_menus` 추가
- 2026-07-13 v0.1 최초 구축 (샘플: 롯데호텔 채널시스템 리뉴얼 IA·화면명세서 기반)
