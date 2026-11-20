# 공통 화면설계 구성요소 가이드 (Common SB Style Guide)

> **모노톤(Black & Gray) 변환판** — KRDS 공통 컴포넌트를 화면설계서(SB/스토리보드) 산출물용으로 무채색화한 기준 문서

| 항목 | 내용 |
|---|---|
| 문서 버전 | v0.1 |
| 작성일 | 2026-08-03 |
| 출처 | Figma `KRDS_v1.0.0 (Community)` — fileKey `pLS2ICqNvRUs9Vyv6yVNf9` |
| 원본 페이지 | 🎨 Design style, Header, Main menu, Badge, Carousel, Tab, Text list, Link, Button, Checkbox, Toggle switch, Alert, Infobox (13개) |
| 적용 대상 | `agent/feature-spec-sb` 가 생성하는 SB(와이어프레임) HTML |
| 연계 파일 | `sb-style-block.html`(토큰·레이아웃), `admin-common.html`·`admin-krds.html`(어드민 템플릿) |

---

## 1. 이 문서의 사용법

1. **토큰만 먼저 본다** — §3의 CSS 블록을 SB HTML `<style>` 최상단에 붙이면 전체가 모노톤으로 렌더된다.
2. **컴포넌트를 그릴 때** — §5의 해당 항목에서 *Variant → Size → State* 순서로 값을 확정한다.
3. **SB 표기 규칙** — §6은 "정적 산출물에서 인터랙션 상태를 어떻게 다룰지"의 규칙이다. 상태를 화면에 그릴지 Description에 쓸지가 여기서 갈린다.
4. **원본 색이 필요할 때** — §7 부록에 KRDS 원본 컬러 전량을 남겨두었다. 컬러 시안(디자인 단계)으로 넘어갈 때 역매핑용으로 쓴다.

> ⚠️ 이 문서는 **KRDS의 구조·치수·Variant 체계를 그대로 따르고, 색상 축만 무채색으로 치환**한다.
> 치수(높이·패딩·라운드·타이포)를 임의로 바꾸지 않는다. 바꿔야 할 사유가 생기면 이 문서를 먼저 개정한다.

---

## 2. 모노톤 변환 원칙

SB는 **레이아웃·정보구조·플로우를 합의하는 산출물**이다. 색으로 의미를 전달하면 검토자가 색을 "디자인 확정안"으로 오해한다. 그래서 색상 축을 제거하고, 의미는 **명도 · 형태 · 아이콘 · 텍스트 라벨** 4가지로만 전달한다.

| # | 원칙 | 적용 |
|---|---|---|
| P1 | **유채색 0** | 모든 hue 제거. 무채색 램프(§3.1) 안에서만 표현 |
| P2 | **강조 = 검정** | KRDS `primary`(#256ef4) 자리에는 `ink-90`(#1e2124) |
| P3 | **위계는 명도로** | 강조 / 보통 / 약함 = `ink-90` / `ink-60` / `ink-30` 3단 고정 |
| P4 | **의미색은 형태로 대체** | danger·warning·success·info는 아이콘 기호 + 좌측 바 두께 + 라벨 텍스트로 구분 (§5.9) |
| P5 | **치수 불변** | 높이·패딩·라운드·폰트 크기는 KRDS 원값 유지 |
| P6 | **disabled는 원본 유지** | KRDS의 disabled(#cdd1d5/#8a949e/#6d7882)는 이미 무채색이므로 그대로 |
| P7 | **명도차 3단계 이상** | 인접 요소의 배경을 구분할 땐 램프 상 최소 2스텝(예: `ink-5` ↔ `ink-20`) 벌린다 |

### 2.1 변환 규칙표 (KRDS 역할 → 모노톤)

| KRDS 역할 토큰 | 원본 | 모노톤 대체 | 비고 |
|---|---|---|---|
| `color/element/primary` | `#256ef4` | `#1e2124` (ink-90) | 주 강조 = 검정 |
| `color/element/primary` (hover) | `#0b50d0` | `#131416` (ink-100) | 한 단계 진하게 |
| `color/element/primary` (pressed) | `#083891` | `#000000` (ink-max) | 최종 단계 |
| `color/element/primary-lighter` | `#ecf2fe` | `#f4f5f6` (ink-5) | 옅은 강조 배경 |
| `color/element/secondary` | `#063a74` | `#464c53` (ink-70) | 보조 강조 |
| `color/element/point` | `#d63d4a` | `#1e2124` (ink-90) | 포인트 = 강조와 동급 처리 |
| `color/text/primary` | `#0b50d0` | `#1e2124` (ink-90) | |
| `color/text/basic` | `#1e2124` | `#1e2124` | 변경 없음 |
| `color/text/subtle` | `#464c53` | `#464c53` | 변경 없음 |
| `color/text/disabled` | `#8a949e` | `#8a949e` | 변경 없음 |
| `color/text/inverse` | `#ffffff` | `#ffffff` | 변경 없음 |
| `color/border/primary` | `#256ef4` | `#1e2124` (ink-90) | |
| `color/border/gray` | `#b1b8be` | `#b1b8be` (ink-30) | 변경 없음 |
| `color/element/*-lighter` (의미색) | 각 hue | `#f4f5f6` / `#e6e8ea` | §5.9 표 참조 |
| `color/element/gray*` 전체 | — | 변경 없음 | 이미 무채색 |

---

## 3. 디자인 토큰

### 3.1 색상 — 모노톤 램프

원본 KRDS gray 램프를 **그대로 승계**한다. 임의 회색을 새로 만들지 않는다(KRDS 램프는 명도 간격과 대비비가 이미 검증되어 있음).

| 토큰 | HEX | 대응 KRDS | 주 용도 |
|---|---|---|---|
| `--sb-ink-0` | `#ffffff` | gray-0 | 캔버스·카드 배경, 반전 텍스트 |
| `--sb-ink-5` | `#f4f5f6` | gray-5 | 페이지 배경, 테이블 헤더, 옅은 강조 배경 |
| `--sb-ink-10` | `#e6e8ea` | gray-10 | 카드 보더, 행 구분선, pressed 배경 |
| `--sb-ink-20` | `#cdd1d5` | gray-20 | 입력 보더, disabled 채움, 구분선(진함) |
| `--sb-ink-30` | `#b1b8be` | gray-30 | 기본 보더, placeholder 아이콘 |
| `--sb-ink-40` | `#8a949e` | gray-40 | placeholder 텍스트, disabled 텍스트 |
| `--sb-ink-50` | `#6d7882` | gray-50 | 보조 텍스트, disabled-on 텍스트 |
| `--sb-ink-60` | `#58616a` | gray-60 | 서브 텍스트, tertiary 보더 |
| `--sb-ink-70` | `#464c53` | gray-70 | 본문 보조, 아이콘 |
| `--sb-ink-80` | `#33363d` | gray-80 | 본문 |
| `--sb-ink-90` | `#1e2124` | gray-90 | **강조(=구 primary)**, 제목, 기본 텍스트 |
| `--sb-ink-100` | `#131416` | text/bolder | 강조 hover |
| `--sb-ink-max` | `#000000` | gray-100 | 강조 pressed, 최고 대비 |

**위계 3단 고정 (P3)**

| 위계 | 채움 | 텍스트 | 보더 |
|---|---|---|---|
| Strong | `ink-90` | `ink-0` | 없음 |
| Medium | `ink-5` | `ink-90` | `ink-90` 1px |
| Weak | `transparent` | `ink-80` | `ink-60` 1px |

### 3.2 타이포그래피

- Family: `Pretendard GOV` → SB에서는 `Pretendard` 우선 (`sb-style-block.html`의 `--krds-font` 스택 사용)
- Line-height: **전 스타일 1.5 고정**
- Letter-spacing: `0` (단, display 전체 / heading xlarge·large는 `1`)

| 스케일 | 토큰 | size(px) | weight | letter-spacing | 용도 |
|---|---|---|---|---|---|
| Display | `display/large` | 60 | 700 | 1 | 메인 비주얼 헤드라인 |
| | `display/medium` | 44 | 700 | 1 | |
| | `display/small` | 36 | 700 | 1 | |
| Heading | `heading/xlarge` | 40 | 700 | 1 | 페이지 대표 타이틀 |
| | `heading/large` | 32 | 700 | 1 | |
| | `heading/medium` | 24 | 700 | 0 | 섹션 타이틀 |
| | `heading/small` | 19 | 700 | 0 | Tab primary, 카드 타이틀 |
| | `heading/xsmall` | 17 | 700 | 0 | Tab secondary, Alert 타이틀 |
| | `heading/xxsmall` | 15 | 700 | 0 | 소제목 |
| Body | `body/large` | 19 | 400 / 700 | 0 | 본문(큼) |
| | `body/medium` | 17 | 400 / 700 | 0 | **기본 본문** |
| | `body/small` | 15 | 400 / 700 | 0 | 보조 설명 |
| | `body/xsmall` | 13 | 400 / 700 | 0 | 캡션, 메타 |
| Label | `label/large` | 19 | 400 | 0 | Button xlarge |
| | `label/medium` | 17 | 400 | 0 | Button large·medium |
| | `label/small` | 15 | 400 | 0 | Button small·xsmall, Badge |

### 3.3 간격 · 높이 · 라운드

**Padding**

| 토큰 | px | | 토큰 | px |
|---|---|---|---|---|
| `padding/1` | 2 | | `padding/6` | 16 |
| `padding/2` | 4 | | `padding/7` | 20 |
| `padding/3` | 8 | | `padding/8` | 24 |
| `padding/4` | 10 | | `padding/9` | 32 |
| `padding/5` | 12 | | `padding-card/large` | 40 |

**Gap**

| 토큰 | px | | 레이아웃 갭 | px |
|---|---|---|---|---|
| `gap/1` | 2 | | `gap-layout/text-text-medium` | 16 |
| `gap/2` | 4 | | `gap-layout/title-body-medium` | 20 |
| `gap/3` | 8 | | `gap-layout/image-text-medium` | 24 |
| `gap/5` | 16 | | `gap-layout/contents-right` | 40 |
| `gap/7` | 24 | | | |
| `gap/9` | 40 | | | |
| `gap/11` | 64 | | | |

**Size-height** (컨트롤 표준 높이)

| 토큰 | px | 적용 |
|---|---|---|
| `size-height/4` | 24 | Badge medium, Button_text small |
| `size-height/5` | 32 | Button xsmall, Badge large |
| `size-height/6` | 40 | Button small, Tab secondary, Carousel arrow small |
| `size-height/7` | 48 | Button medium, Carousel arrow medium |
| `size-height/8` | 56 | Button large, Tab primary, Main menu bar |
| `size-height/9` | 64 | Button xlarge, Carousel arrow large |

**Radius**

| 토큰 | px | 적용 |
|---|---|---|
| `radius/xsmall1~3` | 2 | 미세 요소 |
| `radius/small1~3` | 4 | Badge, Button xsmall, 체크박스 |
| `radius/medium1~2` | 6 | Button small·medium, Tab fill secondary |
| `radius/medium3~4` | 8 | Button large·xlarge, Alert, Infobox, Tab fill primary |
| `radius/large1~2` | 10 | 카드 |
| `radius/xlarge1~2` | 12 | 큰 카드, 모달 |
| `radius/max` | 1000 | Toggle switch, dot, 원형 버튼 |

**Border-width**: `border-width/static-regular` = 1px (기본), 강조 시 2px, Alert 좌측 바 4px

### 3.4 복사용 CSS 토큰 블록

```css
/* ===== SB 모노톤 토큰 (KRDS v1.0.0 기반) ===== */
:root {
  /* --- 무채색 램프 --- */
  --sb-ink-0:   #ffffff;
  --sb-ink-5:   #f4f5f6;
  --sb-ink-10:  #e6e8ea;
  --sb-ink-20:  #cdd1d5;
  --sb-ink-30:  #b1b8be;
  --sb-ink-40:  #8a949e;
  --sb-ink-50:  #6d7882;
  --sb-ink-60:  #58616a;
  --sb-ink-70:  #464c53;
  --sb-ink-80:  #33363d;
  --sb-ink-90:  #1e2124;
  --sb-ink-100: #131416;
  --sb-ink-max: #000000;

  /* --- 역할 토큰 --- */
  --sb-strong:        var(--sb-ink-90);   /* 구 primary */
  --sb-strong-hover:  var(--sb-ink-100);
  --sb-strong-press:  var(--sb-ink-max);
  --sb-on-strong:     var(--sb-ink-0);
  --sb-surface:       var(--sb-ink-0);
  --sb-surface-sub:   var(--sb-ink-5);
  --sb-surface-sub2:  var(--sb-ink-10);
  --sb-border:        var(--sb-ink-30);
  --sb-border-strong: var(--sb-ink-90);
  --sb-divider:       var(--sb-ink-20);
  --sb-text:          var(--sb-ink-90);
  --sb-text-sub:      var(--sb-ink-70);
  --sb-text-weak:     var(--sb-ink-50);
  --sb-text-ph:       var(--sb-ink-40);
  --sb-disabled-fill: var(--sb-ink-20);
  --sb-disabled-text: var(--sb-ink-50);

  /* --- 라운드 --- */
  --sb-r-xs: 2px;  --sb-r-sm: 4px;  --sb-r-md: 6px;
  --sb-r-lg: 8px;  --sb-r-xl: 10px; --sb-r-2xl: 12px; --sb-r-max: 1000px;

  /* --- 높이 --- */
  --sb-h-24: 24px; --sb-h-32: 32px; --sb-h-40: 40px;
  --sb-h-48: 48px; --sb-h-56: 56px; --sb-h-64: 64px;

  /* --- 폰트 --- */
  --sb-font: Pretendard, 'Pretendard GOV', 'Pretendard Variable',
             -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
}

/* ===== 기존 --krds-* 템플릿을 그대로 모노톤화하는 오버라이드 =====
   sb-style-block.html / admin-krds.html 을 수정하지 않고 이 블록만 뒤에 붙이면 됨 */
:root {
  --krds-primary-5:  #f4f5f6;
  --krds-primary-10: #e6e8ea;
  --krds-primary-40: #33363d;
  --krds-primary-50: #1e2124;
  --krds-primary-60: #131416;
  --krds-primary-80: #000000;
  --krds-danger-5:   #f4f5f6;
  --krds-danger-50:  #1e2124;
  --krds-danger-60:  #131416;
  --krds-success-5:  #f4f5f6;
  --krds-success-50: #464c53;
  --krds-info-5:     #f4f5f6;
  --krds-info-50:    #58616a;
}
```

---

## 4. 컴포넌트 인벤토리

| # | 컴포넌트 | Figma 페이지 | 주 Variant 축 | SB 사용 빈도 |
|---|---|---|---|---|
| 5.1 | Header | Header (헤더) | Type(가로/세로/결합) | 높음 |
| 5.2 | Main menu | Main menu (메인 메뉴) | Type(2/3depth, simple), Banner | 높음 |
| 5.3 | Button / Button_text | Button (버튼) | Type × Size × State × Icon | 매우 높음 |
| 5.4 | Link (Button_link) | Link (링크) | Type × Size × State | 높음 |
| 5.5 | Checkbox | Checkbox (체크박스) | Size × Check × State | 높음 |
| 5.6 | Toggle switch | Toggle switch (토글 스위치) | Size × Select × State | 보통 |
| 5.7 | Tab | Tab (탭) | Style × Type × State | 높음 |
| 5.8 | Badge | Badge (배지) | Type × Color × Size × State | 높음 |
| 5.9 | Alert | Alert (얼럿) | State × Size | 높음 |
| 5.10 | Infobox | Infobox (인포박스) | Type × Size | 보통 |
| 5.11 | Text list | Text list (텍스트 목록) | Type × Level | 높음 |
| 5.12 | Carousel | Carousel (캐러셀) | 컨트롤 3종 × Size × State | 낮음 |

---

## 5. 공통 구성요소 상세

---

### 5.1 Header (헤더)

**구성**: `header__pc` / `header__mo` / `header_template__pc` / `utility_dropdown` + atomic 4종

#### Variant

| 축 | 값 | 치수 | 설명 |
|---|---|---|---|
| Type (PC) | `horizontal` | 1200 × **112** | 로고와 유틸리티가 한 줄 |
| | `vertical` | 1200 × **120** | 로고 아래에 메뉴 행 |
| | `union` (결합형) | 1200 × **120** | 헤더 + 메인메뉴 결합 |
| Type (MO) | `horizontal` / `vertical` | 360 × **104** | |

#### 하위 요소

| 요소 | Variant | 치수 |
|---|---|---|
| `header_menu__atomic` | Type `horizontal`(97×40) / `vertical`(69×56) × State `default`/`hover`/`pressed` | |
| `utility_dropdown` | — | 176 × 219 |
| `utility_dropdown__atomic` | state `default`/`hover`/`pressed`/`selected` | 140 × 48 |
| `header_utility_small__atomic` | Type `link` / `select` | h24 |
| `header_template__pc` | — | 1440 × 200 |
| 로고 | 대한민국정부 200×48 / KRDS 154×48 / 슬로건 114×48 | |

#### 모노톤 규칙

- 헤더 배경 `ink-0`, 하단 구분선 `1px ink-10`
- 로고 영역은 **회색 박스 placeholder**로 대체 (실제 로고 이미지 금지 — 프로젝트마다 다름)
- 유틸리티 링크 텍스트 `ink-70` / `body/small 15`
- 유틸리티 드롭다운 열림 상태: 배경 `ink-0`, 보더 `1px ink-20`, 그림자 `0 2px 8px rgba(0,0,0,.08)`
- selected 항목: 배경 `ink-5` + 텍스트 `ink-90` **Bold**

```html
<header class="sb-header">
  <div class="sb-header-logo"><span class="sb-ph-box" style="width:160px;height:32px"></span></div>
  <nav class="sb-header-util">
    <a>로그인</a><a>회원가입</a><a>사이트맵</a>
  </nav>
</header>
```
```css
.sb-header{height:112px;display:flex;align-items:center;justify-content:space-between;
  padding:0 40px;background:var(--sb-ink-0);border-bottom:1px solid var(--sb-ink-10);}
.sb-header-util{display:flex;gap:24px;font-size:15px;color:var(--sb-ink-70);}
.sb-ph-box{display:inline-block;background:var(--sb-ink-10);border-radius:var(--sb-r-sm);}
```

---

### 5.2 Main menu (메인 메뉴)

**구성**: `main_menu`(PC) / `main_menu_open` / `main_menu_open_simple` / `main_menu__mo` + atomic 9종

#### Variant

| 컴포넌트 | 축 | 값 |
|---|---|---|
| `main_menu` (PC) | State | `메뉴 오픈 전`(h56) / `메뉴 오픈 후`(h368~444) |
| `main_menu_open` | Type | `2depth` / `3depth` / `3depth_detail` |
| | Banner | `none` / `horizontal` / `vertical` |
| `main_menu_open_simple` | Type | `2depth` / `3depth` |
| | banner | `none` / `horizontal` / `vertical` |
| `main_menu__mo` | Type | `full` / `bar` / `4depth` (w360) |

> KRDS는 메뉴를 **Type 1(뎁스가 깊은 유형)** 과 **Type 2(정보구조가 단순한 경우 = simple)** 로 나눈다. IA 깊이가 3depth 이상이면 Type 1, 2depth 이하이면 Type 2를 쓴다.

#### Atomic 상태 및 치수

| Atomic | State | 치수 |
|---|---|---|
| `main_menu_bar__atomic__pc` | default / hover / pressed / **selected** | 160 × 56 |
| `main_menu_open_title__atomic__pc` | default / hover / pressed | 129 × 56 |
| `main_menu_open_sub_title__atomic__pc` | default / hover / pressed | 139 × 37 |
| `main_menu_open_2depth__atomic__pc` | (default/hover/pressed/selected) × More depth `Yes`/`No` | 266 × 58 |
| `main_menu_open_2depth_bar__atomic__pc` | 위와 동일 | 266 × 58 |
| `main_menu_open_last_depth__atomic__pc` | default / hover / pressed / selected | 224 × 46 |
| `main_menu_open_title__atomic__mo` | default / hover / pressed | 157 × 45~53 |
| `main_menu_open_2depth_bar__atomic__mo` | default / selected / pressed | 140 × 58 |
| `main_menu_open_2depth__atomic__mo` | default / pressed / selected | 185 × 50 |
| `main_menu_open_last_depth__atomic__mo` | default / pressed / selected | 185 × 46 |
| `main_menu_2depth_open__atomic__mo` | `closed`(202×50) / `open`(202×426) | 아코디언 |
| `main_menu_header__mo` | — | 360 × 265 |

#### 모노톤 규칙

- 1depth 바: 기본 텍스트 `ink-80` / `heading/xsmall 17 Bold`
- **selected**: 텍스트 `ink-90` Bold + 하단 `3px ink-90` 언더바 (색이 아닌 **선**으로 선택 표현)
- 2depth 패널 배경 `ink-5`, 항목 구분선 `1px ink-10`
- `More depth=Yes` 항목은 우측에 `›` 셰브론 (`ink-50`)
- 배너 영역은 `ink-10` 채움 placeholder + `[배너]` 라벨

---

### 5.3 Button (버튼)

KRDS Button 페이지는 **`button`** 과 **`button_text`(텍스트 버튼)** 두 컴포넌트를 담는다.

#### 5.3.1 `button`

| 축 | 값 |
|---|---|
| **Type** | `primary` / `secondary` / `tertiary` — 사용자 과업·플로우 중요도에 따른 위계 |
| **Size** | `xlarge` / `large` / `medium` / `small` / `xsmall` |
| **State** | `default` / `hover` / `pressed` / `disabled` |
| **Icon** | `left icon` / `right icon` / `both icon` |

**Size 스펙 (KRDS 원값 — 변경 금지)**

| Size | 높이 | 좌우 패딩 | 라운드 | 폰트 |
|---|---|---|---|---|
| `xlarge` | 64 | 24 | 8 | label/large 19 |
| `large` | 56 | 20 | 8 | label/medium 17 |
| `medium` | 48 | 16 | 6 | label/medium 17 |
| `small` | 40 | 12 | 6 | label/small 15 |
| `xsmall` | 32 | 10 | 4 | label/small 15 |

**모노톤 색상 매트릭스**

| Type | State | 배경 | 텍스트 | 보더 |
|---|---|---|---|---|
| primary | default | `#1e2124` | `#ffffff` | — |
| | hover | `#131416` | `#ffffff` | — |
| | pressed | `#000000` | `#ffffff` | — |
| secondary | default | `#f4f5f6` | `#1e2124` | `1px #1e2124` |
| | hover | `#e6e8ea` | `#1e2124` | `1px #1e2124` |
| | pressed | `#cdd1d5` | `#1e2124` | `1px #1e2124` |
| tertiary | default | `transparent` | `#1e2124` | `1px #58616a` |
| | hover | `#f4f5f6` | `#1e2124` | `1px #58616a` |
| | pressed | `#e6e8ea` | `#1e2124` | `1px #58616a` |
| 전체 | **disabled** | `#cdd1d5` | `#6d7882` | — |

> 원본 대비: primary `#256ef4`→`#1e2124`, secondary fill `#ecf2fe`→`#f4f5f6` & border `#256ef4`→`#1e2124`. tertiary는 원래부터 무채색(보더 `#58616a`)이라 **변경 없음**.

#### 5.3.2 `button_text` (텍스트 버튼)

| 축 | 값 |
|---|---|
| Size | `large`(h40) / `medium`(h32) / `small`(h24) / `xsmall`(h20) |
| State | `default` / `hover` / `pressed` / `disabled` |
| Icon | `left` / `right` / `both` |

- 배경 없음. 텍스트 `ink-90`, hover 시 밑줄 + `ink-100`, pressed `ink-max`, disabled `ink-40`

```css
.sb-btn{display:inline-flex;align-items:center;justify-content:center;gap:4px;
  font-family:var(--sb-font);font-weight:400;border:none;cursor:pointer;white-space:nowrap;}
.sb-btn--xl{height:64px;padding:0 24px;border-radius:8px;font-size:19px;}
.sb-btn--lg{height:56px;padding:0 20px;border-radius:8px;font-size:17px;}
.sb-btn--md{height:48px;padding:0 16px;border-radius:6px;font-size:17px;}
.sb-btn--sm{height:40px;padding:0 12px;border-radius:6px;font-size:15px;}
.sb-btn--xs{height:32px;padding:0 10px;border-radius:4px;font-size:15px;}

.sb-btn--primary  {background:var(--sb-ink-90);color:var(--sb-ink-0);}
.sb-btn--secondary{background:var(--sb-ink-5);color:var(--sb-ink-90);border:1px solid var(--sb-ink-90);}
.sb-btn--tertiary {background:transparent;color:var(--sb-ink-90);border:1px solid var(--sb-ink-60);}
.sb-btn:disabled, .sb-btn--disabled{background:var(--sb-ink-20);color:var(--sb-ink-50);border:none;}

.sb-btn-text{background:none;border:none;padding:0;color:var(--sb-ink-90);font-family:var(--sb-font);}
.sb-btn-text--lg{height:40px;font-size:19px;} .sb-btn-text--md{height:32px;font-size:17px;}
.sb-btn-text--sm{height:24px;font-size:15px;} .sb-btn-text--xs{height:20px;font-size:13px;}
```

---

### 5.4 Link (`button_link`)

| 축 | 값 | 설명 |
|---|---|---|
| **Type** | `default` / `subtle` / `subtle_none` | 명확한 요소 vs 보조 요소 |
| **Size** | `large`(19px, h29) / `medium`(17px, h26) / `small`(15px, h23) | **주변 텍스트와 동일 크기**로 맞춘다 |
| **State** | `default` / `hover` / `pressed` / `visited` / `disabled` | |
| **Icon** | 외부 사이트·타 페이지 이동 시 사용 | |

#### 모노톤 규칙

| Type | 텍스트 | 밑줄 |
|---|---|---|
| `default` | `ink-90` | 항상 있음 |
| `subtle` | `ink-70` | 항상 있음 |
| `subtle_none` | `ink-70` | 없음 (hover 시 표시) |

| State | 처리 |
|---|---|
| hover | `ink-100` + 밑줄 |
| pressed | `ink-max` |
| **visited** | `ink-50` — 색상 구분 불가하므로 **명도만 낮춤** |
| disabled | `ink-40`, 밑줄 제거 |

> visited는 모노톤에서 default와 구분이 약하다. SB에서는 **렌더하지 않고** Description에 "방문 후 회색 처리"로 서술한다(§6).

---

### 5.5 Checkbox (체크박스)

**구성**: `checkbox`(라벨 포함 행) / `checkbox__item`(박스 단독) / `checkbox__list`

| 축 | 값 |
|---|---|
| **Size** | `large` / `medium` |
| **Check** | `off` / `on` / `indeterminate` |
| **State** | `default` / `disabled` |
| **Text** | `help text` 있음 / 없음 |

**치수**

| Size | 박스 | 행 높이(help text 有) | 행 높이(無) | 폰트 |
|---|---|---|---|---|
| `large` | 24 × 24 | 59 | 30 | body/medium 17 |
| `medium` | 20 × 20 | 53 | 26 | body/small 15 |

#### 모노톤 규칙

| Check | State | 박스 배경 | 박스 보더 | 체크 마크 |
|---|---|---|---|---|
| off | default | `#ffffff` | `1px #b1b8be` | — |
| on | default | `#1e2124` | 없음 | `#ffffff` ✓ |
| indeterminate | default | `#1e2124` | 없음 | `#ffffff` — (가로 바) |
| off | disabled | `#f4f5f6` | `1px #cdd1d5` | — |
| on / indeterminate | disabled | `#cdd1d5` | 없음 | `#ffffff` |

- 라운드 `radius/small` 4px
- 라벨 텍스트 `ink-90`, help text `ink-50` / `body/small 15`
- disabled 라벨 `ink-40`

```css
.sb-chk{display:inline-flex;align-items:flex-start;gap:8px;}
.sb-chk__box{width:24px;height:24px;border-radius:4px;background:#fff;
  border:1px solid var(--sb-ink-30);flex-shrink:0;display:flex;align-items:center;
  justify-content:center;color:transparent;font-size:14px;line-height:1;}
.sb-chk__box--on{background:var(--sb-ink-90);border-color:var(--sb-ink-90);color:#fff;}
.sb-chk--md .sb-chk__box{width:20px;height:20px;font-size:12px;}
.sb-chk__label{font-size:17px;color:var(--sb-ink-90);}
.sb-chk__help{font-size:15px;color:var(--sb-ink-50);margin-top:4px;}
```

---

### 5.6 Toggle switch (토글 스위치)

| 축 | 값 |
|---|---|
| **Size** | `large`(행 h29) / `medium`(행 h26) |
| **Select** | `off` / `on` |
| **State** | `default` / `disabled` |

- 라운드 `radius/max` (완전 원형), 노브(knob) 흰색 원, 트랙 내부 패딩 2px
- 라벨 폰트: large `label/large 19`, medium `label/medium 17`, 트랙-라벨 간격 `gap/3` 8px

#### 모노톤 규칙

| Select | State | 트랙 | 노브 |
|---|---|---|---|
| off | default | `#6d7882` | `#ffffff` |
| on | default | `#1e2124` | `#ffffff` |
| off | disabled | `#cdd1d5` | `#ffffff` |
| on | disabled | `#8a949e` | `#ffffff` |

> on/off가 색이 아닌 **노브 위치**로 구분되므로 모노톤에서도 판별에 문제없다. 다만 SB에서는 on/off 상태 옆에 텍스트 라벨(`사용함`/`사용 안 함`)을 함께 표기한다.

---

### 5.7 Tab (탭)

| 축 | 값 | 설명 |
|---|---|---|
| **Style** | `line` / `fill` | 정보의 시각적 구분 정도 |
| **Type** | `primary`(h56) / `secondary`(h40) | 페이지 전체 콘텐츠 vs 세부 콘텐츠 |
| **State** (atomic) | `default` / `hover` / `pressed` / `active` / `disabled` | |
| **Position** (fill atomic) | `first` / `middle` / `last` | |
| **Swipe** | secondary 전용 — 탭 탐색 버튼 | |

**치수**

| 구분 | PC | MO |
|---|---|---|
| primary 탭 높이 | 56 | — |
| secondary 탭 높이 | 40 | 48 |
| primary 탭 폭(atomic) | 80 | — |
| secondary 탭 폭(atomic) | line 64 / fill 65 | 72 |
| 좌우 패딩 | primary 16 / secondary 12 | |
| 폰트 | primary `heading/small 19 Bold` / secondary `heading/xsmall 17 Bold` | |
| 라운드 | line 0 / fill primary 8, secondary 6 | |

#### 모노톤 규칙

**Style = line**

| State | 텍스트 | 하단 보더 |
|---|---|---|
| default | `ink-60` | `1px ink-20` |
| hover | `ink-80` | `1px ink-30` |
| pressed | `ink-90` | `2px ink-60` |
| **active** | `ink-90` **Bold** | **`3px ink-90`** |
| disabled | `ink-40` | `1px ink-10` |

**Style = fill**

| State | 배경 | 텍스트 | 보더 |
|---|---|---|---|
| default | `ink-0` | `ink-60` | `1px ink-20` |
| hover | `ink-5` | `ink-80` | `1px ink-30` |
| pressed | `ink-10` | `ink-90` | `1px ink-40` |
| **active** | `ink-90` | `ink-0` **Bold** | 없음 |
| disabled | `ink-5` | `ink-40` | `1px ink-10` |

```css
.sb-tabs{display:flex;border-bottom:1px solid var(--sb-ink-20);}
.sb-tab{height:56px;padding:0 16px;display:flex;align-items:center;font-size:19px;
  font-weight:400;color:var(--sb-ink-60);border-bottom:3px solid transparent;margin-bottom:-1px;}
.sb-tab--active{color:var(--sb-ink-90);font-weight:700;border-bottom-color:var(--sb-ink-90);}
.sb-tab--sm{height:40px;padding:0 12px;font-size:17px;}
```

---

### 5.8 Badge (배지)

**구성**: `badge__dot` / `badge__number` / `badge`

| 컴포넌트 | 축 | 값 | 치수 |
|---|---|---|---|
| `badge__dot` | Type | `primary` / `new` | 6 × 6 |
| `badge__number` | Type × Number | (`primary`/`new`) × (`0-9` / `10-999`) | 26×20 / 52×20 |
| `badge` | **Type** | `outline` / `solid` / `solid-pastel` | |
| | **Color** | `primary` `secondary` `tertiary` `point` `danger` `warning` `success` `info` | |
| | **Size** | `large`(h32) / `medium`(h24) | |
| | **State** | `default` / `disabled` | |

- 라운드 4px, 좌우 패딩 8px, 폰트 large `label/medium 17` / medium `label/small 15`

#### 모노톤 규칙 — Color 8종 → 위계 3단

색상 8종을 무채색으로 1:1 매핑하면 구분이 불가능하다. **위계 3단으로 축약하고, 의미는 배지 안의 텍스트로 전달**한다.

| 원본 Color | 모노톤 위계 | outline | solid | solid-pastel |
|---|---|---|---|---|
| `primary` `point` `danger` | **Strong** | 텍스트 `ink-90` / 보더 `1px ink-90` | 배경 `ink-90` / 텍스트 `ink-0` | 배경 `ink-10` / 텍스트 `ink-90` |
| `secondary` `warning` `info` | **Medium** | 텍스트 `ink-70` / 보더 `1px ink-60` | 배경 `ink-60` / 텍스트 `ink-0` | 배경 `ink-5` / 텍스트 `ink-70` |
| `tertiary` `success` | **Weak** | 텍스트 `ink-50` / 보더 `1px ink-30` | 배경 `ink-30` / 텍스트 `ink-0` | 배경 `ink-5` / 텍스트 `ink-50` |
| — | **disabled** | 텍스트 `ink-40` / 보더 `1px ink-20` | 배경 `ink-20` / 텍스트 `ink-50` | 배경 `ink-5` / 텍스트 `ink-40` |

- `badge__dot` / `badge__number`: 채움 `ink-90`, 숫자 텍스트 `ink-0`, 라운드 `max`

> **규칙**: 배지 라벨은 반드시 의미를 담은 단어(`진행중`, `마감`, `필수`)를 쓴다. 색만으로 구분하던 배지는 모노톤에서 라벨이 유일한 단서가 된다.

---

### 5.9 Alert (얼럿)

| 축 | 값 |
|---|---|
| **State** | `danger` / `warning` / `success` / `information` |
| **Size** | `+title`(제목+본문, h118 @720w) / `slim`(단문, h58) |

- 라운드 8px, 보더 1px, 패딩 `+title` 24, `slim` 16, 아이콘-텍스트 간격 8

#### 모노톤 규칙 (P4 — 형태로 의미 전달)

색을 뺀 자리를 **① 아이콘 기호 ② 좌측 바 두께 ③ 배경 명도 ④ 라벨 텍스트** 4중으로 채운다.

| State | 아이콘 | 좌측 바 | 배경 | 보더 | 제목 텍스트 | 라벨 |
|---|---|---|---|---|---|---|
| `danger` | ✕ (원형 채움 `ink-90`) | **4px `ink-90`** | `ink-10` | `1px ink-90` | `ink-90` Bold | `[오류]` |
| `warning` | ! (삼각 `ink-70`) | **4px `ink-60`** | `ink-5` | `1px ink-60` | `ink-90` Bold | `[주의]` |
| `success` | ✓ (원형 `ink-70`) | **4px `ink-40`** | `ink-0` | `1px ink-30` | `ink-90` Bold | `[완료]` |
| `information` | i (원형 `ink-50`) | **2px `ink-20`** | `ink-5` | `1px ink-20` | `ink-80` Bold | `[안내]` |

> 원본 대비: danger `#de3412`/`#fdefec` → `ink-90`/`ink-10`, warning `#ffb114`/`#fff3db` → `ink-60`/`ink-5`, success `#228738`/`#eaf6ec` → `ink-40`/`ink-0`, information `#0b78cb`/`#e7f4fe` → `ink-20`/`ink-5`.

```css
.sb-alert{display:flex;gap:8px;padding:24px;border-radius:8px;
  border:1px solid var(--sb-ink-30);background:var(--sb-ink-0);border-left-width:4px;}
.sb-alert--danger {background:var(--sb-ink-10);border-color:var(--sb-ink-90);}
.sb-alert--warning{background:var(--sb-ink-5); border-color:var(--sb-ink-60);}
.sb-alert--success{background:var(--sb-ink-0); border-color:var(--sb-ink-30);border-left-color:var(--sb-ink-40);}
.sb-alert--info   {background:var(--sb-ink-5); border-color:var(--sb-ink-20);border-left-width:2px;}
.sb-alert--slim{padding:16px;}
.sb-alert__title{font-size:17px;font-weight:700;color:var(--sb-ink-90);margin-bottom:4px;}
.sb-alert__body {font-size:17px;color:var(--sb-ink-70);line-height:1.5;}
```

---

### 5.10 Infobox (인포박스)

| 축 | 값 | 치수(@720w) |
|---|---|---|
| **Type** | `primary` (강조) / `secondary` (보통) | |
| **Size** | `Default` (제목+목록형 본문) / `slim` (단문) | primary 214 / secondary 198 / slim 58 |

#### 모노톤 규칙

| Type | 배경 | 보더 | 제목 | 본문 |
|---|---|---|---|---|
| `primary` | `ink-5` | `1px ink-90` | `ink-90` / heading/xsmall 17 Bold | `ink-70` / body/medium 17 |
| `secondary` | `ink-0` | `1px ink-20` | `ink-80` / heading/xsmall 17 Bold | `ink-70` / body/medium 17 |

- 라운드 8px, 패딩 24(Default) / 16(slim)
- Alert과 구분: **Infobox는 좌측 바가 없다.** 이것이 모노톤에서 두 컴포넌트를 가르는 유일한 형태 단서이므로 반드시 지킨다.

---

### 5.11 Text list (텍스트 목록)

**구성**: `list`(단일 항목) / `list_group`(묶음) / `list__atomic_bullet`

| 축 | 값 |
|---|---|
| **Type** | `unordered` (기호) / `ordered` (번호) |
| **Level** | `1` / `2` / `3` |

**Level별 스펙**

| Level | 불릿 폭(unordered) | 불릿 폭(ordered) | 항목 높이 | 폰트 |
|---|---|---|---|---|
| 1 | 24 | 24 | 26 | body/medium 17 |
| 2 | 20 | 20 | 26 | body/medium 17 |
| 3 | 16 | 24 | 23 | body/small 15 |

- `list_group`은 unordered / ordered / **혼합형**을 지원한다. 실무 SB에서는 혼합형(1depth 번호 + 2depth 기호)이 가장 흔하다.

#### 모노톤 규칙

| Level | 불릿 기호(unordered) | 번호 형식(ordered) | 텍스트 |
|---|---|---|---|
| 1 | `●` (`ink-90`) | `1.` | `ink-90` |
| 2 | `–` (`ink-60`) | `가.` | `ink-80` |
| 3 | `·` (`ink-50`) | `1)` | `ink-70` |

- 들여쓰기: Level당 +16px
- 불릿 자체에 색을 쓰지 않으므로 **기호 모양이 위계 단서**다. Level 3까지만 사용하고 그 이하는 만들지 않는다.

---

### 5.12 Carousel (캐러셀)

**구성**: `carousel__number` / `carousel__dot` / `carousel__arrow` / `carousel__atomic` / `swiper__atomic`

| 컴포넌트 | 축 | 값 | 치수 |
|---|---|---|---|
| `carousel__number` | — | 현재/전체 표시 | 65 × 40 |
| `carousel__dot` | Type | `1` ~ `5` (도트 개수) | 100 × 40 |
| `carousel__arrow` | Type × Size | (`left`/`right`) × (`large` 64 / `medium` 48 / `small` 40 / `xsmall` 32) | |
| `carousel__atomic` | type × state | (`arrow-left`/`arrow-right`/`play`/`pause`/`more`) × (`default`/`hover`/`pressed`/`disabled`) | 40 × 40 |
| `swiper__atomic` | Type × Arrow | (`circle` 64 / `square` 56 / `dropdown` 64) × (`left`/`right`) | h40 |

#### 모노톤 규칙

| 요소 | default | active/current | disabled |
|---|---|---|---|
| dot | `ink-30` 원 | `ink-90` 원 (폭 2배 pill) | — |
| number | 현재 `ink-90` Bold / 전체 `ink-50` | — | — |
| arrow | 아이콘 `ink-70`, 보더 `1px ink-30`, 배경 `ink-0` | — | 아이콘 `ink-30`, 보더 `1px ink-10` |
| play/pause | 아이콘 `ink-70` | — | `ink-30` |

- arrow 라운드 `max` (원형), swiper square는 `radius/small` 4px
- **현재 도트는 색이 아니라 `폭 2배 pill 형태`로 구분**한다 (모노톤 필수 규칙)

---

## 6. SB(화면설계서) 표기 규칙

### 6.1 상태(State) 렌더링 원칙

SB는 정적 산출물이다. 모든 State를 그리면 화면이 읽히지 않는다.

| State | SB에 렌더? | 처리 |
|---|---|---|
| `default` | ✅ 렌더 | 기본값 |
| `active` / `selected` | ✅ 렌더 | 현재 위치를 보여줘야 하므로 반드시 렌더 |
| `disabled` | ✅ 렌더 | 사용 불가가 화면 정보이므로 렌더 |
| `hover` | ❌ 미렌더 | Description에 서술 |
| `pressed` | ❌ 미렌더 | Description에 서술 |
| `visited` | ❌ 미렌더 | Description에 서술 |
| `indeterminate` | △ 조건부 | 전체선택 체크박스가 있는 목록에서만 렌더 |

Description 서술 예시:
> ⑤ 조회 버튼 — Primary / Medium. hover 시 배경 1단계 진하게, pressed 시 최고 대비. 검색어 미입력 시 disabled.

### 6.2 번호 뱃지 (`.num-badge`)

기존 `sb-style-block.html`의 번호 뱃지는 danger 계열(빨강)이다. 모노톤 SB에서는:

```css
.num-badge{background:var(--sb-ink-0);color:var(--sb-ink-90);border:1px solid var(--sb-ink-90);}
```

> 번호 뱃지는 **와이어프레임 위에 얹히는 주석**이지 UI 요소가 아니다. 배경 흰색 + 검정 보더로 본문과 분리되게 유지한다.

### 6.3 Placeholder 처리

| 대상 | 표기 |
|---|---|
| 이미지 | `ink-10` 채움 + 대각선 없음 + 중앙에 `[이미지]` 라벨 (`ink-50`, 13px) |
| 아이콘 | `ink-30` 정사각 (라운드 3px), 실제 아이콘 금지 |
| 로고 | `ink-10` 박스 + `[로고]` |
| 차트·그래프 | `ink-5` 박스 + `1px ink-20` 보더 + `[차트: 유형]` |

### 6.4 텍스트 대비 최소 기준

| 조합 | 대비비 | 판정 |
|---|---|---|
| `ink-90` on `ink-0` | 15.9:1 | ✅ |
| `ink-70` on `ink-0` | 8.6:1 | ✅ |
| `ink-50` on `ink-0` | 5.1:1 | ✅ 본문 가능 |
| `ink-40` on `ink-0` | 3.2:1 | ⚠️ disabled 전용 |
| `ink-0` on `ink-90` | 15.9:1 | ✅ |
| `ink-0` on `ink-60` | 6.4:1 | ✅ |
| `ink-0` on `ink-30` | 2.4:1 | ❌ 사용 금지 (Weak solid 배지는 `ink-90` 텍스트로) |

> Weak 위계 solid 배지(`ink-30` 배경 + `ink-0` 텍스트)는 대비 미달이다. 실제 적용 시 **텍스트를 `ink-90`으로** 바꾼다. §5.8 표의 해당 셀은 이 예외를 우선한다.

### 6.5 금지 사항

- ❌ 임의 회색 신규 생성 (램프 13단 밖의 값)
- ❌ 유채색 사용 (에러 강조라도 빨강 금지 — §5.9 형태 규칙으로 대체)
- ❌ 그라디언트, 컬러 그림자
- ❌ KRDS 치수(높이·패딩·라운드) 임의 변경
- ❌ Level 4 이상 목록 깊이

---

## 7. 부록 — KRDS 원본 컬러 대조표

컬러 시안 단계로 넘어갈 때 역매핑용. Figma `🎨 Design style` 페이지에서 추출한 실제 값이다.

### 7.1 Text

| 토큰 | HEX | | 토큰 | HEX |
|---|---|---|---|---|
| `text/basic` | `#1e2124` | | `text/primary` | `#0b50d0` |
| `text/bolder` | `#131416` | | `text/secondary` | `#052b57` |
| `text/subtle` | `#464c53` | | `text/point` | `#ab2b36` |
| `text/static` | `#1e2124` | | `text/danger` | `#bd2c0f` |
| `text/disabled` | `#8a949e` | | `text/warning` | `#8a5c00` |
| `text/disabled-on` | `#6d7882` | | `text/success` | `#267337` |
| `text/inverse-static` | `#ffffff` | | `text/information` | `#096ab3` |

### 7.2 Element

| 토큰 | HEX | | 토큰 | HEX |
|---|---|---|---|---|
| `element/primary` | `#256ef4` | | `element/primary-lighter` | `#ecf2fe` |
| `element/secondary` | `#063a74` | | `element/secondary-lighter` | `#eef2f7` |
| `element/point` | `#d63d4a` | | `element/point-lighter` | `#fbeff0` |
| `element/danger` | `#de3412` | | `element/danger-lighter` | `#fdefec` |
| `element/warning` | `#ffb114` | | `element/warning-lighter` | `#fff3db` |
| `element/success` | `#228738` | | `element/success-lighter` | `#eaf6ec` |
| `element/information` | `#0b78cb` | | `element/information-lighter` | `#e7f4fe` |
| `element/gray-dark` | `#58616a` | | `element/gray` | `#6d7882` |
| `element/gray-light` | `#e6e8ea` | | `element/gray-lighter` | `#f4f5f6` |
| `element/disabled-dark` | `#8a949e` | | `element/disabled-light` | `#cdd1d5` |
| `element/inverse` | `#ffffff` | | | |

### 7.3 Border / Surface / Divider / Icon

| 토큰 | HEX | | 토큰 | HEX |
|---|---|---|---|---|
| `border/gray` | `#b1b8be` | | `surface/gray-subtler` | `#f4f5f6` |
| `border/primary` | `#256ef4` | | `surface/gray-subtle` | `#e6e8ea` |
| `border/secondary` | `#063a74` | | `surface/danger-subtler` | `#fdefec` |
| `border/danger-light` | `#fcdfd9` | | `surface/warning-subtler` | `#fff3db` |
| `border/warning-light` | `#ffe0a3` | | `surface/success-subtler` | `#eaf6ec` |
| `border/success-light` | `#d8eedd` | | `surface/information-subtler` | `#e7f4fe` |
| `border/information-light` | `#d3ebfd` | | `surface/white-subtler` | `#ffffff` |
| `divider/gray` | `#8a949e` | | `icon/gray` | `#33363d` |
| `divider/gray-light` | `#cdd1d5` | | `icon/gray-light` | `#464c53` |
| `divider/secondary` | `#063a74` | | `icon/gray-fill` | `#cdd1d5` |
| `divider/secondary-light` | `#d6e0eb` | | `icon/inverse` | `#ffffff` |

### 7.4 Button 전용 (원본)

| 토큰 | HEX |
|---|---|
| `button/primary-fill` / `-hover` / `-pressed` | `#256ef4` / `#0b50d0` / `#083891` |
| `button/secondary-fill` / `-hover` / `-pressed` | `#ecf2fe` / `#d8e5fd` / `#b1cefb` |
| `button/secondary-border` | `#256ef4` |
| `button/tertiary-fill` / `-hover` / `-pressed` | `#ffffff00` / `#f4f5f6` / `#e6e8ea` |
| `button/tertiary-border` | `#58616a` |
| `button/disabled-fill` | `#cdd1d5` |

---

## 8. 변경 이력

| 버전 | 일자 | 내용 | 작성 |
|---|---|---|---|
| v0.1 | 2026-08-03 | 최초 작성. KRDS v1.0.0 Figma 13개 페이지(Design style + 컴포넌트 12종)에서 토큰·Variant·치수 추출 후 모노톤 변환 규칙 정의 | 김단영 |
