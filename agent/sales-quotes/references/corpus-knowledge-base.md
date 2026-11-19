# corpus 집단기억 활용 (에이전트 워크플로우)

corpus = 누적되는 과거 산출물 저장소. **같은 repo의 별도 `corpus` 브랜치**(도구 코드는 `etribe` 브랜치). 새 프로젝트가 오면 유사 과거 산출물을 참고해 일관성·정확도를 높이고, 완성본은 다시 corpus 브랜치에 환원한다. 엔진: `scripts/corpus.py`가 gitignored `.corpus/`(corpus 브랜치만 클론)에서 읽고/쓰고/push 한다. 사용자는 `.corpus/`를 직접 만질 필요 없음 — corpus.py가 자동 클론·갱신.

## corpus 브랜치 디렉토리 구조 — ★ 우리 산출물 섹션 정렬 원자 + 케이스별 종합
**목적: 유형(신규구축/리뉴얼/이관/기능추가/모듈이식)별로 "범위→확인사항→공수" 인과를 빨리 참고**한다. "한 파일 = 한 검색 단위"(frontmatter title·type·tags). 큰 HTML을 다시 분석할 필요 없이 원자 카드로 출발.
```
corpus 브랜치 루트 (= .corpus/)
  INDEX.md                         # ★ 진입점 — 케이스 먼저, 그다음 프로젝트·패턴
  cases/{유형}.md                  # ★ 케이스 종합: 통상 범위 + 꼭 확인할 것 + 공수 밴드 + 대표 프로젝트
                                   #   (new-build·renewal-reskin·migration-rebuild·addon-channel·module-port)
  estimates/{id}.md                # 공수(밴드·직군) ┐
  scope/{id}.md                    # 범위 in/out·전제 │ ★ 범위→확인→공수 사슬(원자끼리 [[링크]])
  questions/{id}.md                # 꼭 확인할 것(사전질의·데이터갭) ┘
  ia/{id}.md · approach/{id}.md · direction/{id}.md · overview/{id}.md · infra/{id}.md  # 리포트 섹션별 원자
  dev-notes/decisions/{id}.md      # 설계 의도 + 결정·수정 이력(버전 변천)
  patterns/{slug}.md               # 프로젝트 횡단 재사용 노하우(기간계 역할분리·멱등성·모듈이식 등)
  deliverables/{id}/report.html    # 원본 풀 산출물(최후 딥레퍼런스)
  index.jsonl                      # 기계검색용(corpus.py search). workspace/ 중간물은 검색 제외(노이즈 0)
```
- **★ id = 안정 slug `{고객}-{주제}`** (예: `woongjin-direct`, `snu-sdn`). **`_workspace/{slug}`의 slug와 동일하게 쓴다**(매핑 불필요). 날짜·버전은 폴더명이 아니라 `meta`(date)에 둔다.
- **같은 프로젝트 재작업 = 같은 id**로 폴더를 덮어써 최신화(이력은 git 히스토리에 남음). 완전 별건만 새 id.
- ORCHESTRATOR가 **착수 시 id를 1회 확정** → 이후 snapshot·save가 같은 id를 사용(중간물과 최종본이 같은 폴더로 모임).
- **검색 격리**: `search`는 `index.jsonl`(최종본 메타)만 본다 → `workspace/` 중간물은 검색 결과에 안 섞인다(노이즈 0).

## 읽기 — analyst/architect 초입에 (검색-증강)
1. `python scripts/corpus.py pull` — 최신 corpus 받기(실패해도 로컬로 진행).
2. 새 프로젝트의 **도메인 + 기능 태그**를 뽑는다(analyst가 IA·요건에서 추출).
3. `python scripts/corpus.py search --domain {도메인} --tags {기능1,기능2,...} --top 5`
   → 밴드 카드(JSON: total_mm·months·headcount·role_breakdown·scope_in/out·data_gaps·**ref_scope·ref_questions·ref_estimate·ref_ia·ref_decision**).
4. **★ 케이스 먼저**: 새 건의 유형을 정해 `cases/{유형}.md`(INDEX 참조)에서 **통상 범위·꼭 확인할 것·공수 밴드**를 본다("저번 신규구축/리뉴얼 땐 범위 이만큼, 확인 이거, 공수 이거").
5. 유사 대표 프로젝트로 내려가 **범위→확인→공수 사슬**을 읽어 근거 확인:
   - **architect**: `estimates/`(밴드·직군) + `decisions/`(왜 그 공수) → **산정 보정 기준**(복제 아님, 차이 반영).
   - **analyst**: `ia/`·`scope/`·`questions/`(꼭 확인할 것) + `approach/`(개발 제안) 참고.
   - 도메인 **`patterns/`** 적용(기간계 역할분리·멱등성·모듈이식·측정단위 등).
6. 매칭이 없으면(신규 패턴) 그대로 진행하고, 산정 노트에 "유사 선례 없음" 명시.

> `examples/`(엄선 정본 4종)와 `corpus/`(전체 누적 이력)는 공존: 스타일 기준은 examples, 유사 선례 데이터는 corpus.

검색 결과의 **`⚠️under_estimated`** 플래그(과거 실제공수 > 산정 +20%)는 blind-spot 신호다 — architect가 유사 산정 시 버퍼를 검토한다(기계가 알리고 판단은 사람이).

## 작업 중간물 스냅샷 — 단계/게이트 완료마다 (★ 이력 보존)
KB는 완성본뿐 아니라 **작업 과정도 누적**한다. 각 단계(analyst / architect+sol-arch / builder) 또는 게이트 승인 직후:
- `python scripts/corpus.py snapshot --id {id} --ws _workspace/{slug} --stage {단계명}`
- → `_workspace/{slug}` 전체를 `deliverables/{id}/workspace/`에 미러 + corpus 브랜치 commit/push. **index.jsonl은 건드리지 않음**(검색 노이즈 0).
- push 실패해도 로컬 `.corpus/`에 저장 → 다음 호출에서 함께 올라감(중간물은 `_workspace/`에도 안전).
- 같은 id로 반복 호출하면 최신 상태로 갱신(작업이 진행될수록 workspace/가 채워짐).

## 쓰기 — qa PASS 후 자동 (환원)
1. 메타 추출 → `meta.json`. **id = 안정 slug `{고객}-{주제}`**(= `_workspace/{slug}`의 slug, 날짜는 `date` 필드로). **스키마(KB frontmatter 차용)**:
   `id·date·client·topic·type·domain·features[]·total_mm·months·headcount·stack[]` + `sensitivity(기본 internal)·confidence(high|medium|low)·actual_mm(미정, 피드백 시)·lesson`.
2. `python scripts/corpus.py save --html output/{최종}.html --meta meta.json --ws _workspace/{slug}` → `deliverables/{id}/`에 report.html + workspace/ 저장 + index append + commit/push.
3. push 실패 시 로컬 저장됨 → 보고에 명시(산출물은 output/에 안전).

## 피드백 — 실제공수 회수 (누적 자기보정 ★)
프로젝트 종료/중간점검 때 실제 공수를 알게 되면:
- `python scripts/corpus.py feedback --id {id} --actual {실제M/M} --lesson "{교훈}"`
- → 그 견적에 `actual_mm`·`lesson` 기록. 이후 유사 검색에서 과소/과대산정 경고로 되먹임 → **산정이 쓸수록 정확해진다**(운영 하네스 history-manager 패턴). 사용자가 "이 건 실제 N M/M 들었어" 류로 알려주면 이 명령을 실행.

## 가드
- **qa PASS가 push 게이트.** 검수 통과본만 공유 corpus로 올라간다(미완성·오류본 차단).
- corpus는 사내 전용(고객 단가·공수 포함). 외부 노출 금지.
- 토큰은 `.env`(gitignored)에만. 산출물·메타·로그에 토큰이 새어들지 않게.
