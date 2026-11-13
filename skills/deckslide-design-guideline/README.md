# deckslide-design-guideline — PPT 장표 규격 · 디자인 표준 스킬

고객사 · 제안사명과 강조 컬러를 넣으면 풀 폭 블랙 헤더(2단 위계 GNB) + 라운드 코너 카드 + 포인트 컬러 강조 디자인 시스템을 적용한 pptxgenjs 장표와 노출 금지 메타데이터 8종 검수 결과가 나오는 PPT 장표 규격 스킬

## 한눈에 보기

| <div align="center"><sub>항목</sub></div> | <sub>내용</sub> |
|:---|:---:|
| <sub>목적</sub> | <sub>제안서 · 보고서 PPT 장표의 규격 · 레이아웃 · 스타일 표준화와 검수(콘텐츠 기획 · 문안 작성은 `proposal-slide-builder` 담당)</sub> |
| <sub>이럴 때 사용</sub> | <sub>여러 장표의 디자인 통일 · 이 디자인 시스템으로 pptx 제작 · 거버닝 메시지 규칙 정리 · 완성 장표의 내부 메타데이터 노출 검수</sub> |
| <sub>넣는 것</sub> | <sub>프로젝트 변수(`{clientName}` · `{proposerName}` 필수 · `accent` · `brand` · 폰트 · 비율) + 장표 콘텐츠(초안 또는 기존 장표)</sub> |
| <sub>나오는 것</sub> | <sub>디자인 시스템이 적용된 pptxgenjs 코드 → `.pptx` 장표(기본 4:3) · 노출 금지 메타데이터 8종 검수 결과(매칭 0건 확인)</sub> |
| <sub>부르는 법</sub> | <sub>`PPT 디자인 지침 적용해줘` · `장표 디자인 통일해줘` · `이 디자인 시스템으로 PPT 만들어줘` · `거버닝 메시지 규칙 맞춰줘` · `PPT 장표화 검수해줘` · 슬래시 명령 `/deckslide-design-guideline`</sub> |
| <sub>제작</sub> | <sub>김단영(dykim) · 특정 운영사업 제안서의 디자인 시스템 가이드 v6.4(2026.05)를 범용화한 판</sub> |
| <sub>연계</sub> | <sub>[`proposal-slide-builder`](../proposal-slide-builder/README.md)(콘텐츠) 다음 PPT 규격 적용 · 하네스 [agent/proposal](../../agent/proposal/) S7 최종본의 `release-packager`가 PPT 추출 때 이 규격 사용</sub> |

## 이렇게 요청

| <div align="center"><sub>상황</sub></div> | <sub>요청 예시</sub> | <sub>나오는 것</sub> |
|:---|:---:|:---:|
| <sub>새 장표 제작</sub> | <sub>`이 디자인 시스템으로 PPT 만들어줘`</sub> | <sub>변수 인테이크 → 표준 헤더 · 라운드 카드 · 푸터를 적용한 pptxgenjs 코드 → 최종 검수</sub> |
| <sub>기존 장표 스타일 통일</sub> | <sub>`장표 디자인 통일해줘` · `PPT 디자인 지침 적용해줘`</sub> | <sub>모든 슬라이드에 GNB · 라운드 카드 · 거버닝 메시지 · 강조 · 푸터 규격 공통 적용</sub> |
| <sub>거버닝 메시지 정리</sub> | <sub>`거버닝 메시지 규칙 맞춰줘`</sub> | <sub>헤더 직하 14pt · 「~합니다」 체 · 1~2문장(약 80~140자) · 슬라이드당 1개 · 절 단위 줄바꿈</sub> |
| <sub>완성 장표 검수만</sub> | <sub>`PPT 장표화 검수해줘`</sub> | <sub>디자인 적용 생략 · 노출 금지 메타데이터 8종 체크리스트 결과만 보고</sub> |

## 진행 단계

```
① 프로젝트 변수 인테이크 → ② 디자인 시스템 적용 → ③ 최종 검수(노출 금지 8종 · 매칭 0건까지)
   검수만 요청하면 ③만
```

| <div align="center"><sub>단계</sub></div> | <sub>하는 일</sub> | <sub>사용자 할 일</sub> | <sub>결과물</sub> |
|:---|:---:|:---:|:---:|
| <sub>① 변수 인테이크</sub> | <sub>아래 변수를 한 번에 하나씩 확인 · 이미 아는 값은 질문 생략 · `accent`를 바꾸면 `accentLite` · `accentDark`도 같은 계열로 파생</sub> | <sub>고객사 · 제안사명 · 강조 컬러 등 답변</sub> | <sub>확정 변수</sub> |
| <sub>② 디자인 시스템 적용</sub> | <sub>`references/design-guide.md` 읽기 → 모든 슬라이드에 GNB · 라운드 카드 · 거버닝 메시지 · 강조 · 푸터 · 반복 컴포넌트를 가이드 좌표 · 토큰 그대로 적용 · 가이드 §8 표준 코드 베이스에 변수 치환</sub> | <sub>결과 확인</sub> | <sub>pptxgenjs 코드 · 장표</sub> |
| <sub>③ 최종 검수</sub> | <sub>노출 금지 내부 메타데이터 8종을 정규식으로 전수 검사 → 1건이라도 매칭되면 자연어로 재서술 후 재검사</sub> | <sub>검수 결과 확인</sub> | <sub>매칭 0건 장표 · 체크리스트 결과</sub> |

**인테이크 변수**

| <div align="center"><sub>변수</sub></div> | <sub>설명</sub> | <sub>기본값</sub> |
|:---|:---:|:---:|
| <sub>`{clientName}`</sub> | <sub>고객사명(푸터 좌측)</sub> | <sub>필수</sub> |
| <sub>`{proposerName}`</sub> | <sub>제안사명(푸터 우측)</sub> | <sub>필수</sub> |
| <sub>`accent`</sub> | <sub>메인 강조 컬러</sub> | <sub>`#2DBFB8`(청록)</sub> |
| <sub>`brand`</sub> | <sub>제안사 브랜드 컬러 · 푸터 로고 점 전용(본문 강조 사용 금지)</sub> | <sub>제안사 CI에서 추출</sub> |
| <sub>폰트</sub> | <sub>전체 폰트 패밀리</sub> | <sub>`Pretendard`</sub> |
| <sub>비율</sub> | <sub>캔버스 비율</sub> | <sub>4:3(10" × 7.5")</sub> |

**디자인 시스템 요약**(정본 = `references/design-guide.md`)

| <div align="center"><sub>구성</sub></div> | <sub>규격</sub> |
|:---|:---:|
| <sub>캔버스(§0)</sub> | <sub>4:3 · 10" × 7.5"(pptxgenjs `LAYOUT_4x3`) · 16:9로 바꾸면 x · w 좌표를 13.33" 폭 기준으로 재산정</sub> |
| <sub>상단 블랙 바 GNB(§1 · §3-1)</sub> | <sub>풀 폭 `0, 0, 10, 0.55` · `headerBg #1A1A1B` · 좌측 「중단원 12pt Regular > 소단원 16pt Bold」 한 줄 · 우측 Part명 11pt Medium · 헤더 안 글씨 전부 화이트</sub> |
| <sub>라운드 카드 · 여백(§1)</sub> | <sub>`0, 0.55, 10, 7.5` 흰 배경 · `rectRadius 0.25"` · 하단을 슬라이드 밖으로 빼 상단 양쪽만 라운드 · 카드 내부 패딩 좌우 0.4" · 상하 0.3" · 본문 영역 폭 약 9.2"</sub> |
| <sub>본문 타이틀(§3-2)</sub> | <sub>미사용 — 헤더 16pt Bold 소단원이 타이틀 역할</sub> |
| <sub>거버닝 메시지(§3-3)</sub> | <sub>헤더 직하 y 0.85" · 14pt 고정 · `descText #666666` · 「~합니다」 체 · 1~2문장 약 80~140자 · 슬라이드당 1개 · 핵심 키워드 1~2개만 `accent` Bold</sub> |
| <sub>강조(§2 · §6-4)</sub> | <sub>`accent` Bold · 본문 키워드 슬라이드당 1~3개 · `accent` 사용처 슬라이드당 3~5곳</sub> |
| <sub>푸터(§5)</sub> | <sub>좌 `{clientName}` · 중앙 「- N -」 · 우 브랜드 점(`brand`) + `{proposerName}` · y 7.15"</sub> |
| <sub>반복 컴포넌트(§6 · §7)</sub> | <sub>사이드 라벨 + 카드 그리드(As-Is · To-Be · 챕터 매핑) · As-Is → To-Be 화살표 · 인용/결론 박스 · Win Theme 배지(슬라이드당 최대 1개 · 평가 점수 표기 금지)</sub> |
| <sub>표준 코드(§8)</sub> | <sub>슬라이드 시작 · 표준 헤더 + 라운드 카드 · 표준 푸터 pptxgenjs 코드 블록</sub> |

**노출 금지 내부 메타데이터 8종**(§3-4 · 장표화 검수 필수)

| <div align="center"><sub>#</sub></div> | <sub>표기 유형</sub> | <sub>예시</sub> | <sub>처리</sub> |
|:---|:---:|:---:|:---:|
| <sub>1</sub> | <sub>목차 cross-reference 괄호 표기</sub> | <sub>`(Ⅶ-3.3)` · `(부록-4.3)` · `(별첨2 §1.3)`</sub> | <sub>전량 삭제 · 본문 어휘로 재서술</sub> |
| <sub>2</sub> | <sub>RFP · 평가기준 직접 인용 마커</sub> | <sub>`◀── [RFP §5.2]`</sub> | <sub>전량 삭제 · 핵심 어휘는 거버닝 메시지 · 카드 헤더에 흡수</sub> |
| <sub>3</sub> | <sub>평가 점수 매핑 표기</sub> | <sub>`AX 15점 中 5점` · `★18점 핵심`</sub> | <sub>전량 삭제</sub> |
| <sub>4</sub> | <sub>차별화 등급 표기</sub> | <sub>타이틀 접미사 `(★★★)`</sub> | <sub>타이틀에서 삭제 · 시각 위계로 대체</sub> |
| <sub>5</sub> | <sub>Phase 매핑 · 담당 메타</sub> | <sub>`> **Phase 매핑**: …`</sub> | <sub>헤더 블록 전체 삭제 · Phase는 타임라인 다이어그램으로 표현</sub> |
| <sub>6</sub> | <sub>리스크 · 작성 노트 표기</sub> | <sub>`[작성 노트 …]`</sub> | <sub>전량 삭제</sub> |
| <sub>7</sub> | <sub>MD 버전 · 작성일 · 선행 참조</sub> | <sub>`> **버전**: v0.1`</sub> | <sub>전량 삭제 · 푸터 페이지 번호 외 메타정보 노출 금지</sub> |
| <sub>8</sub> | <sub>MD 자기지칭 어휘</sub> | <sub>`본 꼭지` · `본 슬라이드` · `본 문서`</sub> | <sub>전량 삭제 또는 시각 위치 표현으로 재서술 · `본 제안` · `본 컨소시엄` · `본 사업`은 허용</sub> |

- 판정 기준 — 「이 표기가 청중에게 가치를 주는가?」, 애매하면 제거가 기본값
- 정규식 체크리스트 원문 = `references/design-guide.md` §3-4

## 산출물

| <div align="center"><sub>산출물</sub></div> | <sub>형식</sub> | <sub>구성</sub> |
|:---|:---:|:---:|
| <sub>장표 코드</sub> | <sub>pptxgenjs(JavaScript)</sub> | <sub>가이드 §8 표준 코드 블록 베이스 · 색 · 이름은 인테이크 변수로 치환</sub> |
| <sub>PPT 장표</sub> | <sub>`.pptx`(기본 4:3)</sub> | <sub>모든 슬라이드 공통 GNB · 라운드 카드 · 거버닝 메시지 · 푸터 · 반복 컴포넌트</sub> |
| <sub>검수 결과</sub> | <sub>체크리스트 보고</sub> | <sub>노출 금지 8종 정규식 전수 검사 · 매칭 0건 확인(검수만 요청 시 이 결과만)</sub> |

## 설치 · 단독 사용

```bash
# 리포 루트에서 — 이 스킬만 전역 설치
cp -r skills/deckslide-design-guideline ~/.claude/skills/deckslide-design-guideline
```

- **리포 스킬 일괄 설치**: 리포 루트 `bash install-global.sh`(전역 규칙 · 하우스 스타일 등과 함께 적용)
- **의존성**: pptxgenjs(Node.js 라이브러리 · 표준 코드 실행용) · Pretendard 폰트를 빌드 PC와 발표 PC 양쪽에 설치([Pretendard](https://github.com/orioncactus/pretendard) · 미설치 환경은 시스템 폰트 폴백으로 자간 · 줄간격 불일치)
- **하네스 안에서 쓸 때**: [agent/proposal](../../agent/proposal/) `agents/release-packager.md` — S7 최종본 PPT 추출 때 `pptx` 스킬 · 이 스킬 규격 사용(기존 발표본 pptx가 있으면 그것을 틀로 이미지만 교체) · 하네스 폴더 사본 생성 = 리포 루트 `./sync-skills.ps1`(또는 `bash ./sync-skills.sh`)

## 주의

- 가이드와 사용자 요청이 충돌하면 사용자 요청 우선 + 어떤 표준에서 벗어났는지 한 줄 안내
- `brand`는 푸터 로고 점 전용 · 본문 강조는 `accent` 단일
- `fontFace`는 인테이크에서 확정한 폰트명으로 고정 · 임의 대체 금지
- 한글 가독성 — 본문 이상 크기에 `charSpacing -0.3 ~ -0.5` 권장 · 긴 챕터명은 Part 번호 + 핵심 키워드 2~3단어로 축약
- PPT 산출물은 HTML 하우스 스타일 적용 대상 밖 — 이 스킬 규격 우선(전역 규칙 「이 스타일을 강제하지 않는 경우」)
- 유래 — 특정 운영사업 제안서 디자인 시스템 가이드 v6.4(풀 폭 블랙 헤더 + 라운드 카드 + 청록 강조, 2026.05) 범용판 · 고객사 · 제안사명 · 브랜드 컬러 · Part 구성 · Win Theme 메시지 · 적용 상태 추적은 변수 · 원칙으로 치환

## 릴리즈노트

| <div align="center"><sub>요약내용</sub><img width="1" height="1"></div> | <sub>업데이트 일자</sub><img width="1" height="1"> | <sub>소유자</sub><img width="45" height="1"> |
|:---|:---:|:---:|
| <sub>README 전면 개편 — 목적 · 넣는 것 · 산출물 형태 · 요청 예시 · 진행 단계 순으로 재구성, 릴리즈노트 맨 아래로 이동</sub> | <sub>2026.11.13</sub> | <sub>김단영</sub> |
| <sub>최초 등록 — PPT 장표 디자인 지침 스킬</sub> | <sub>2026.07.13</sub> | <sub>김단영</sub> |
