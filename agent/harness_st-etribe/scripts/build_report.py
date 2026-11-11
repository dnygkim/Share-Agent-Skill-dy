#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_report.py — 구조화 데이터(JSON) → 하우스 스타일 HTML 리포트를 '결정적으로' 렌더.

왜: LLM이 HTML 구조를 손으로 짜면 클래스 발명·IA 통합·레이아웃 드리프트·컬럼 폭 깨짐이
    반복된다(시운전 4회). 구조(레이아웃·표·IA·colgroup·CSS)는 코드가 박고, LLM은 '데이터'만
    채운다 → 스타일·구조 일관성이 검증이 아니라 '보장'된다. IA 표는 노드 1개=1 row로 루프
    렌더되어 통합/폭 깨짐이 물리적으로 불가능.

입력 JSON 스키마(요약):
{
  "meta": {"title","client","subtitle","version","date",
           "logo": "template/etribe_logo_white.png",   # §22 선택: 지정 시 배지 대신 헤더 로고 + 스크롤 Mini GNB(타이틀+로고) 자동 생성
           "palette": {"brand":"#c8102e","dark":"#8a0a1f","soft":"#fde7eb"}},
  "hero": [{"label","value","unit","sub"}],
  "sections": [
    {"no","id","title","area",
     "kind": "ia",                      # IA 표 섹션
     "table": {"effort_head":"공수 (M/M)",
               "groups": [{"num","name","desc","effort","admin":false,   # admin:true=관리자 영역(유추·추정)
                           "children":[{"name","desc","effort"}]}],       # 하위는 반드시 children로(1노드=1행)
               "subtotal": "..", "total": ".."}},   # ★ 사용자 그룹 + 관리자 그룹(admin:true) 모두 포함
    {"no","id","title","area","kind":"monthly","table":{"groups":[{"name","bg","members":[{"role","grade","months":[..],"parttime":false}]}]}},
    #   monthly: members[].months 만(소계·총계는 compute_monthly가 계산). parttime:true = 투입연속성 가드(톱니·장기0.5) 예외(PM 감리·QA 입회 등).
    {"no","id","title","area","kind":"area",  "table":{"rows":[{"num","name","desc","di","pu","de"}]}},
    {"no","id","title","area","kind":"gantt", "table":{"months":N,"groupHeaders":{..},"tasks":[{"label","phase","start","end"}]}},
    {"no","id","title","area","kind":"summary","table":{"cards":[{"ttl","body"}]}},
    # --- 매트릭스: 역할 × 단계 (cell = 문자열 | 리스트 | "-"(empty)) ---
    {"no","id","title","area","kind":"matrix","table":{"stages":["분석·설계",..],
        "rows":[{"role","meta","cells":["문자열", ["li1","li2"], "-"]}]}},
    # --- WBS: 블록(월)별 단계 phase 배지 ---
    {"no","id","title","area","kind":"wbs","table":{"blocks":[{"title",
        "rows":[{"phase":"mgmt|analyze|design|designv|pub|dev|test|stable","label","id","task","owner","result"}]}]}},
    # --- 개념도(생태계 허브): center + 위성 최대 10 ---
    {"no","id","title","area","kind":"concept","table":{
        "center":{"label","title","sub"},
        "satellites":[{"cls":"paradise|cosmojin|external|infra","icon","name","desc"}],  # ≤10
        "legend":[{"swatch_style":"background:var(--brand);","html":"<strong>코어</strong>"}]}},
    # --- AWS 인프라: row > col > aws-box(aws-account|aws-external) > 서비스 그리드 ---
    #     AS-IS/TO-BE 둘 다 그릴 땐 infra 섹션 2개(title "현행 인프라 (AS-IS)" / "제안 인프라 (TO-BE)") + 사이에 마이그레이션 prose
    {"no","id","title","area","kind":"infra","table":{
        "rows":[{"cols":[{"box":"aws-account","ico","label","flex":"1.2","services":[
            {"img":"<aws icon png url>","name","meta"} | {"emoji":"🗄️","name","meta"}]}]}],
        "flow":{"title":"데이터 흐름","steps":["1. …","2. …"]}}},
    {"no","id","title","area","kind":"prose","html":"<p>자유 서술…</p>"}
  ],
  "footer": "© … 총 X M/M · N개월 · N명"
}

지원 kind: part(상위 그룹 타이틀 — no·id·title만, 하위 섹션 no는 "N-M"로 두면 목차가 2단 위계로 렌더)
  · ia · monthly · area · gantt · summary · matrix · wbs · concept · infra
  · overview(메뉴칩 그리드+insight) · modules(menu-list 항목상세) · narrative(다크 final-report: value-chain·총평)
  · questions(확인 필요 질문) · coverage(RFP 요건 커버리지표) · insight(코멘트 박스)
  · figure(이미지 임베드: 고객 제공 구성도 등 '자료'를 원본 그대로 — 로컬 파일은 base64 인라인) · prose(자유 HTML).
narrative는 다크 풀블록이라 .section 래퍼 없이 자체 섹션. 그 외 kind는 s["html"](선택)을 표 앞 prose로 함께 둘 수 있다.
섹션 `no` 미지정 시 렌더가 순번 자동 부여(narrative 제외).

사용: python scripts/build_report.py data.json -o out.html
"""
import sys, os, json, argparse, re, base64, html as _h

for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, "..", "template")


def esc(s):
    return _h.escape(str(s)) if s is not None else ""


# 구 팔레트(파랑·노랑 파스텔) role 배경 → 하우스 톤 저채도 틴트.
# 하우스 스타일이 warm paper x near-black 으로 바뀐 뒤에도 옛 spec 이 #dbeafe 류를 들고 오면
# 크림 지면 위에서 혼자 튄다. 값 정본 = references/report-spec.md §4.
_ROLE_BG = {
    "#dbeafe": "#DFE3E4",   # 기획
    "#fef9c3": "#E7E2D4",   # 디자인
    "#d1fae5": "#DFE6DD",   # 퍼블
    "#fce7f3": "#E8DFE0",   # 개발
    "#eef2ff": "var(--paper-2)",
    "#fef3c7": "#E7E2D4",
}


def _role_bg(bg):
    if not bg:
        return "var(--paper-2)"
    return _ROLE_BG.get(str(bg).strip().lower(), bg)


def rich(s):
    # 데이터에 <strong> 등 제한적 인라인 강조 허용(신뢰 입력). None→""
    return str(s) if s is not None else ""


def css_block(palette):
    with open(os.path.join(TPL, "house-style.css"), encoding="utf-8") as f:
        css = f.read()
    with open(os.path.join(TPL, "diagrams.css"), encoding="utf-8") as f:
        css += "\n" + f.read()   # 개념도(eco)·인프라(aws) 스타일도 항상 인라인
    # eco 개념도용 기본 변수(없으면 eco 색 깨짐) + 팔레트 brand 오버라이드
    v = ["--paradise-black:#0a0a0a;", "--paradise-dark:#1a1a1a;", "--paradise-deep:#2a2114;",
         "--gold-light:#d4b87c;", "--gold-pale:#ebd8a7;"]
    if palette:
        if palette.get("brand"): v.append(f"--brand:{palette['brand']};")
        if palette.get("dark"): v.append(f"--brand-dark:{palette['dark']};")
        if palette.get("soft"): v.append(f"--brand-soft:{palette['soft']};")
    return f"<style>\n{css}\n:root{{ {' '.join(v)} }}\n</style>"


def render_hero(hero):
    cards = []
    for c in hero or []:
        unit = f'<span class="unit">{esc(c.get("unit"))}</span>' if c.get("unit") else ""
        sub = f'<div class="sub">{rich(c.get("sub"))}</div>' if c.get("sub") else ""
        cards.append(
            f'<div class="hero-card"><div class="label">{esc(c.get("label"))}</div>'
            f'<div class="value">{esc(c.get("value"))}{unit}</div>{sub}</div>')
    return '<div class="hero-grid">\n' + "\n".join(cards) + "\n</div>"


def nav_label(title):
    # 목차는 간결하게: ① 묶음 접두("공수 산정 — ") 제거 — 표 이름만 ② 제목 끝 부연 괄호 제거
    s = re.sub(r"^\s*공수\s*산정\s*[—\-–:·]\s*", "", str(title))   # "공수 산정 — 영역별 공수" → "영역별 공수"
    s = re.sub(r"\s*[\(（〔][^)）〕]*[\)）〕]\s*$", "", s)            # 끝 부연 괄호(범위·단위·SSOT 등은 area에 있음)
    return s.strip()


def render_nav(sections):
    # §22 LNB 2단 위계: part(상위 그룹) 섹션이 하나라도 있으면 no가 "N-M"/"N.M" 꼴인 항목을 sub로 표시
    has_parts = any(s.get("kind") == "part" for s in sections)
    lis = []
    for s in sections:
        sub = ' class="sub"' if has_parts and re.match(r"^\d+[-.]", str(s.get("no", ""))) else ""
        lis.append(f'<li{sub}><a href="#{esc(s["id"])}"><span class="num">{esc(s.get("no",""))}</span> {esc(nav_label(s["title"]))}</a></li>')
    return ('<nav class="sidebar">\n  <div class="nav-title">CONTENTS</div>\n  <ol>\n    '
            + "\n    ".join(lis) + "\n  </ol>\n</nav>")


def render_ia_table(t):
    groups = t.get("groups", [])
    users = [g for g in groups if not g.get("admin")]
    admins = [g for g in groups if g.get("admin")]
    # 공수 컬럼은 effort가 하나라도 있을 때만(IA 정보구조도는 보통 공수 없음 → 빈 컬럼 제거)
    has_eff = (t.get("subtotal") is not None or t.get("total") is not None
               or any(g.get("effort") not in (None, "") for g in groups)
               or any(c.get("effort") not in (None, "") for g in groups for c in g.get("children", [])))
    eff = esc(t.get("effort_head", "공수 (M/M)"))
    if has_eff:
        colg = '<colgroup><col style="width:42px;"><col style="width:22%;"><col><col style="width:90px;"></colgroup>'
        thead = f'<thead><tr><th colspan="2">IA 메뉴 / 모듈</th><th>설명</th><th class="num">{eff}</th></tr></thead>'
        acs = "3"
    else:
        colg = '<colgroup><col style="width:42px;"><col style="width:24%;"><col></colgroup>'
        thead = '<thead><tr><th colspan="2">IA 메뉴 / 모듈</th><th>설명</th></tr></thead>'
        acs = "2"
    out = ['<table class="effort-table fixed">', '  ' + colg, '  ' + thead, '  <tbody>']
    # (관리자 IA 누락 가드는 main에서 전역 검사 — 분리 섹션 Front/Admin 케이스 대응)
    admin_hdr = False
    for g in users + admins:
        # 사용자→관리자 전환 시 구분 헤더행(관리자는 유추·추정)
        if g.get("admin") and not admin_hdr:
            admin_hdr = True
            # 출처 라벨: 자료 제공 시 "자료 기반", 미제공 유추 시 "유추·추정"(기본). spec의 admin_label로 지정.
            albl = esc(t.get("admin_label", "프론트 기반 유추 · 추정"))
            out.append(f'    <tr class="depth1"><td class="menu-num"></td>'
                       f'<td colspan="{acs}"><strong>관리자 영역</strong> '
                       f'<span style="color:var(--muted);font-weight:400;">({albl})</span></td></tr>')
        # depth1 = 모듈 (1 row)
        e1 = f'<td class="num">{esc(g.get("effort",""))}</td>' if has_eff else ""
        out.append(
            f'    <tr class="depth1"><td class="menu-num"><span>{esc(g.get("num",""))}</span></td>'
            f'<td>{esc(g.get("name"))}</td><td>{rich(g.get("desc"))}</td>{e1}</tr>')
        # IA 압축 가드: children로 분해 안 하고 desc 한 셀에 ·로 합치면 1노드=1행 위반
        if not g.get("children") and str(g.get("desc", "") or "").count("·") >= 2:
            n_items = str(g.get("desc", "")).count("·") + 1
            print(f"[WARN] IA '{g.get('name','')}': 하위 {n_items}개가 desc 한 셀에 ·로 압축된 듯 — "
                  f"children[]로 분해해야 1노드=1행으로 펴짐(report-spec 핵심 규칙).", file=sys.stderr)
        # depth2 = 하위 (★ 노드 1개 = 1 row, 절대 통합 안 함)
        for c in g.get("children", []):
            e2 = f'<td class="num">{esc(c.get("effort",""))}</td>' if has_eff else ""
            out.append(
                f'    <tr class="depth2"><td></td><td class="menu2">{esc(c.get("name"))}</td>'
                f'<td>{rich(c.get("desc"))}</td>{e2}</tr>')
    if t.get("subtotal") is not None:
        out.append(f'    <tr class="subtotal"><td colspan="3" style="text-align:right;">소계</td><td class="num">{esc(t["subtotal"])}</td></tr>')
    if t.get("total") is not None:
        out.append(f'    <tr class="total"><td colspan="3" style="text-align:right;">합계</td><td class="num">{esc(t["total"])}</td></tr>')
    out += ['  </tbody>', '</table>']
    return "\n".join(out)


def _fmt(v):
    v = round(float(v), 2)
    if v == int(v):
        return f"{int(v)}.0"          # 30 → "30.0", 5 → "5.0" (M/M 관례)
    return ("%.2f" % v).rstrip("0").rstrip(".")   # 0.5 → "0.5", 0.15 → "0.15"


def _cell(v):
    return f'<td class="num zero">-</td>' if round(float(v), 2) == 0 else f'<td class="num">{_fmt(v)}</td>'


def check_sawtooth(role, arr):
    """투입 연속성 규칙(methodology §9) 자동 탐지. 반환: 위반 사유 리스트(빈=정상).
    - 톱니: 연속 투입 인력의 중간 월 0.5 (1.0→0.5→1.0). 사람은 월 중간에 반만 붙였다 뗄 수 없다.
    - 장기 반투입: 2개월 이상 연속 0.5 (반만 일하는 유령 인력).
    정당한 파트타임(PM 감리·QA 입회·명시적 파트타임 역할)은 member에 "parttime": true 로 예외 처리."""
    a = [float(x) for x in arr]; n = len(a); flags = []
    for i in range(1, n - 1):
        if a[i] == 0.5 and a[i - 1] >= 1.0 and a[i + 1] >= 1.0:
            flags.append(f"톱니(중간월 {i+1}이 0.5, 양옆 1.0+)")
    run = 0
    for v in a:
        run = run + 1 if v == 0.5 else 0
        if run == 2:
            flags.append("장기 반투입(0.5 2개월+ 연속)")
    return flags


def compute_monthly(t):
    """월별 투입표 데이터에서 모든 소계·총계를 '계산'한다 → 정합(a-h) 보장(검증 아님)."""
    months = t["months"]; n = len(months)
    grand_m = [0.0] * n; grand = 0.0; headcount = 0
    warns = []
    for g in t["groups"]:
        gm = [0.0] * n
        for mem in g["members"]:
            if len(mem["months"]) != n:
                raise ValueError(f'{mem.get("role")}: 월 셀 수 {len(mem["months"])} != 개월수 {n}')
            if not mem.get("parttime"):
                for f in check_sawtooth(mem.get("role", ""), mem["months"]):
                    warns.append(f'{g.get("name","")}/{mem.get("role","")}: {f} → {mem["months"]}')
            for i, v in enumerate(mem["months"]):
                gm[i] += float(v)
        g["_gm"] = [round(x, 2) for x in gm]; g["_gt"] = round(sum(gm), 2)
        headcount += len(g["members"])
        for i in range(n): grand_m[i] += gm[i]
        grand += g["_gt"]
    t["_grand_m"] = [round(x, 2) for x in grand_m]; t["_grand"] = round(grand, 2)
    # QA 인력 정책(methodology §9): QA 전담 직군 금지 + 기획자 막달 유지(QA 겸임)
    plan_groups = [g for g in t["groups"] if ("기획" in g.get("name", "") or "PM" in g.get("name", "").upper())]
    for g in t["groups"]:
        gn = g.get("name", "")
        if ("QA" in gn.upper() or "품질" in gn) and not ("기획" in gn or "PM" in gn.upper()):
            warns.append(f'{gn}: QA 전담 직군 — QA는 기획자 겸임(§9), 기획에 포함할 것')
    if plan_groups and round(sum(g["_gm"][-1] for g in plan_groups), 2) == 0:
        warns.append('기획 직군 막달(통합테스트·UAT·오픈) 투입 0 — QA는 기획 겸임이므로 기획 1명은 끝까지 유지(§9)')
    # 테스트 구간 감쇠(§9): 디자인·퍼블이 막달에 2명+ 잔류면 과다(신규 제작 없음 → 1명 감쇠)
    for g in t["groups"]:
        gn = g.get("name", "")
        if "디자인" in gn or "퍼블" in gn:
            active_last = sum(1 for mem in g["members"] if float(mem["months"][-1]) > 0)
            if active_last >= 2:
                warns.append(f'{gn}: 막달(테스트·오픈)에 {active_last}명 잔류 — 신규 제작 없으므로 1명으로 감쇠 검토(§9)')
    # ★ 기획 과소 가드(§9): 디자인 고도화인데 기획이 정체(기획 1명 vs 디자인 3-4명) — 운영 반복 결함
    def _msum(mem): return sum(float(x) for x in mem.get("months", []) if isinstance(x, (int, float)))
    def _grp(kw, exclude_pm=False):
        mm = hc = 0.0
        for g in t["groups"]:
            if kw in g.get("name", ""):
                for mem in g["members"]:
                    if exclude_pm and "PM" in mem.get("role", "").upper(): continue
                    mm += _msum(mem); hc += 1
        return round(mm, 2), int(hc)
    plan_mm, plan_hc = _grp("기획", exclude_pm=True)   # PM 제외 기획 실무
    des_mm, des_hc = _grp("디자인")
    pub_mm, pub_hc = _grp("퍼블")
    if des_mm > 0 and plan_mm < des_mm * 0.5:
        warns.append(f'기획 실무 {plan_mm}M/M가 디자인 {des_mm}M/M의 절반 미만 — 기획 과소 의심(디자인 고도화 시 콘텐츠·화면설계·다국어 기획 동반 상승, §9). 페이지수·난이도로 재산정')
    elif plan_hc <= 1 and (des_hc + pub_hc) >= 4:
        warns.append(f'기획 실무 {plan_hc}명이 디자인+퍼블 {des_hc+pub_hc}명을 받침 — 기획 과소 의심(§9). 기획 베이스=페이지수+난이도 재점검')
    if warns:
        print("[WARN] 인력 정책(methodology §9) 의심 패턴 — 재배치 검토(정당한 파트타임은 spec에 \"parttime\": true):",
              file=sys.stderr)
        for w in warns:
            print(f"   - {w}", file=sys.stderr)
    return {"total_mm": _fmt(grand), "headcount": str(headcount), "months": str(n)}


def render_monthly_table(t):
    months = t["months"]; n = len(months)
    out = ['<table class="monthly-effort">',
           '  <thead><tr><th rowspan="2">구분</th><th rowspan="2">역할</th><th rowspan="2">등급</th>'
           f'<th colspan="{n}">M/M (월별)</th><th rowspan="2">합계</th></tr>',
           '  <tr>' + "".join(f"<th>{esc(m)}</th>" for m in months) + "</tr></thead>", '  <tbody>']
    for g in t["groups"]:
        mems = g["members"]
        for idx, mem in enumerate(mems):
            mtot = round(sum(float(x) for x in mem["months"]), 2)
            cells = "".join(_cell(v) for v in mem["months"])
            role_td = (f'<td rowspan="{len(mems)+1}" class="role" style="background:{_role_bg(g.get("bg"))};">'
                       f'<strong>{esc(g["name"])}</strong><br><small>소계 {_fmt(g["_gt"])} M/M<br>{len(mems)}명</small></td>'
                       ) if idx == 0 else ""
            out.append(f'    <tr>{role_td}<td style="text-align:left;">{esc(mem["role"])}</td>'
                       f'<td>{esc(mem.get("grade",""))}</td>{cells}<td class="num"><strong>{_fmt(mtot)}</strong></td></tr>')
        out.append(f'    <tr class="subtotal"><td colspan="2" style="text-align:right;">{esc(g["name"])} 소계</td>'
                   + "".join(_cell(v) for v in g["_gm"]) + f'<td class="num">{_fmt(g["_gt"])}</td></tr>')
    out.append(f'    <tr class="total"><td colspan="3" style="text-align:right;">월 합계 (M/M)</td>'
               + "".join(_cell(v) for v in t["_grand_m"]) + f'<td class="num">{_fmt(t["_grand"])}</td></tr>')
    out += ['  </tbody>', '</table>']
    return "\n".join(out)


def render_area_table(t):
    """영역별 공수표: 영역마다 (디/퍼/개) → 제작소계·총공수를 계산."""
    areas = t["areas"]; di = pu = de = 0.0
    rows = []
    for a in areas:
        x, y, z = float(a.get("di", 0)), float(a.get("pu", 0)), float(a.get("de", 0))
        di += x; pu += y; de += z
        rows.append(f'    <tr class="depth1"><td class="menu-num"><span>{esc(a.get("num",""))}</span></td>'
                    f'<td>{esc(a.get("name"))}</td><td>{rich(a.get("desc",""))}</td>'
                    f'<td class="num">{_fmt(x)}</td><td class="num">{_fmt(y)}</td><td class="num">{_fmt(z)}</td>'
                    f'<td class="num"><strong>{_fmt(x+y+z)}</strong></td></tr>')
    make = round(di + pu + de, 2); pm = float(t.get("pm_planning", 0)); total = round(make + pm, 2)
    head = ('  <thead><tr><th colspan="2">영역</th><th>구성</th>'
            '<th class="num">디</th><th class="num">퍼</th><th class="num">개</th><th class="num">합</th></tr></thead>')
    foot = (f'    <tr class="subtotal"><td colspan="3" style="text-align:right;">제작 소계</td>'
            f'<td class="num">{_fmt(di)}</td><td class="num">{_fmt(pu)}</td><td class="num">{_fmt(de)}</td><td class="num">{_fmt(make)}</td></tr>'
            f'\n    <tr class="subtotal"><td colspan="6" style="text-align:right;">PM/기획</td><td class="num">{_fmt(pm)}</td></tr>'
            f'\n    <tr class="total"><td colspan="6" style="text-align:right;">총 공수</td><td class="num">{_fmt(total)} M/M</td></tr>')
    return ('<table class="effort-table fixed">'
            '\n  <colgroup><col style="width:42px;"><col style="width:20%;"><col><col style="width:48px;"><col style="width:48px;"><col style="width:48px;"><col style="width:64px;"></colgroup>\n'
            + head + "\n  <tbody>\n" + "\n".join(rows) + "\n" + foot + "\n  </tbody>\n</table>")


def render_summary(t):
    cards = []
    for c in t["cards"]:
        cards.append(f'  <div class="card"><div class="ttl">{esc(c.get("ttl"))}</div><div class="body">{rich(c.get("body",""))}</div></div>')
    return '<div class="effort-grid">\n' + "\n".join(cards) + "\n</div>"


_GANTT_JS = """
<script>
const tasks = %s;
const groupHeaders = %s;
const totalWeeks = %d; const totalCols = 3 + totalWeeks;
const tbody = document.getElementById('gantt-tbody');
if (tbody) {
  tasks.forEach(t => {
    if (groupHeaders[t.id]) tbody.innerHTML += `<tr class="group-header"><td colspan="${totalCols}">${groupHeaders[t.id]}</td></tr>`;
    let row = `<tr><td class="task-id">${t.id}</td><td class="task-name">${t.name}</td><td class="task-owner">${t.owner}</td>`;
    for (let w = 1; w <= totalWeeks; w++) row += (w >= t.start && w <= t.end) ? `<td class="week bar-${t.phase}"></td>` : `<td class="week"></td>`;
    row += '</tr>'; tbody.innerHTML += row;
  });
}
</script>"""


def render_gantt(t):
    months = t["months"]; nm = len(months); weeks = nm * 4
    test_i = t.get("test_month_index", nm - 1)
    mheads = "".join(
        f'<th colspan="4" class="month-header{" test" if i == test_i else ""}">{esc(m)}</th>'
        for i, m in enumerate(months))
    wheads = "".join(f"<th>W{w}</th>" for w in range(1, weeks + 1))
    table = ('<table class="gantt">\n  <thead><tr><th rowspan="2">ID</th><th rowspan="2">작업</th><th rowspan="2">담당</th>'
             + mheads + '</tr>\n  <tr>' + wheads + '</tr></thead>\n  <tbody id="gantt-tbody"></tbody>\n</table>')
    script = _GANTT_JS % (json.dumps(t["tasks"], ensure_ascii=False),
                          json.dumps(t.get("groupHeaders", {}), ensure_ascii=False), weeks)
    return table + script


def render_matrix(t):
    """역할 × 단계 업무 매트릭스. cell: 문자열(li 1개)·리스트(li 다수)·"-"(empty)."""
    head = '<thead><tr><th style="width:110px;">역할</th>' + "".join(f"<th>{esc(s)}</th>" for s in t["stages"]) + "</tr></thead>"
    rows = []
    for r in t["rows"]:
        cs = []
        for c in r.get("cells", []):
            if c in (None, "", "-"):
                cs.append('<td class="empty">-</td>')
            elif isinstance(c, list):
                cs.append("<td><ul>" + "".join(f"<li>{rich(x)}</li>" for x in c) + "</ul></td>")
            else:
                cs.append(f"<td><ul><li>{rich(c)}</li></ul></td>")
        meta = f'<small>{esc(r.get("meta",""))}</small>' if r.get("meta") else ""
        rows.append(f'    <tr><td class="role">{esc(r["role"])}{meta}</td>' + "".join(cs) + "</tr>")
    return f'<table class="matrix">\n  {head}\n  <tbody>\n' + "\n".join(rows) + "\n  </tbody>\n</table>"


def render_wbs(t):
    out = []
    for b in t["blocks"]:
        out.append(f'<div class="wbs-section-title">{esc(b["title"])}</div>')
        out.append('<table class="wbs"><thead><tr><th>단계</th><th>ID</th><th>작업</th><th>담당</th><th>결과물</th></tr></thead><tbody>')
        for r in b.get("rows", []):
            out.append(f'  <tr><td class="phase {esc(r.get("phase",""))}">{esc(r.get("label",""))}</td>'
                       f'<td class="center">{esc(r.get("id",""))}</td><td>{rich(r.get("task",""))}</td>'
                       f'<td class="center">{esc(r.get("owner",""))}</td><td>{esc(r.get("result",""))}</td></tr>')
        out.append('</tbody></table>')
    return "\n".join(out)


_ECO_LINES = [(50, 12), (72.3, 19.2), (86.1, 38.3), (86.1, 61.7), (72.3, 80.8),
              (50, 88), (27.7, 80.8), (13.9, 61.7), (13.9, 38.3), (27.7, 19.2)]


def render_concept(t):
    sats = t["satellites"][:10]
    lines = "".join(f'<line x1="50" y1="50" x2="{x}" y2="{y}"/>' for x, y in _ECO_LINES[:len(sats)])
    c = t["center"]
    center = (f'<div class="eco-center"><div class="eco-c-label">{esc(c.get("label",""))}</div>'
              f'<div class="eco-c-title">{rich(c.get("title",""))}</div>'
              f'<div class="eco-c-sub">{esc(c.get("sub",""))}</div></div>')
    sd = [f'<div class="eco-sat {esc(s.get("cls",""))}" data-i="{i}"><div class="eco-s-icon">{esc(s.get("icon",""))}</div>'
          f'<div class="eco-s-name">{esc(s.get("name",""))}</div><div class="eco-s-desc">{esc(s.get("desc",""))}</div></div>'
          for i, s in enumerate(sats)]
    legend = ""
    if t.get("legend"):
        legend = '\n<div class="eco-legend">' + "".join(
            f'<span><span class="swatch" style="{esc(l.get("swatch_style",""))}"></span>{rich(l.get("html",""))}</span>'
            for l in t["legend"]) + "</div>"
    return f'<div class="eco-hub">\n<svg class="eco-svg" viewBox="0 0 100 100" preserveAspectRatio="none">{lines}</svg>\n{center}\n' + "\n".join(sd) + "\n</div>" + legend


def render_infra(t):
    out = ['<div class="infra-diagram">']
    for row in t["rows"]:
        out.append('  <div class="aws-row">')
        for col in row["cols"]:
            flex = f' style="flex:{col["flex"]};"' if col.get("flex") else ""
            out.append(f'    <div class="aws-col"{flex}>')
            out.append(f'      <div class="aws-box {esc(col.get("box","aws-external"))}">'
                       f'<span class="aws-box-label"><span class="ico">{esc(col.get("ico",""))}</span>{rich(col.get("label",""))}</span>')
            out.append('        <div class="aws-svc-grid">')
            for s in col.get("services", []):
                icon = (f'<img src="{esc(s["img"])}" alt="{esc(s.get("name",""))}" onerror="this.style.display=\'none\'">'
                        if s.get("img") else f'<span style="font-size:30px;line-height:40px;">{esc(s.get("emoji",""))}</span>')
                out.append(f'          <div class="aws-svc">{icon}<span class="name">{esc(s.get("name",""))}</span><span class="meta">{esc(s.get("meta",""))}</span></div>')
            out.append('        </div></div>')
            out.append('    </div>')
        out.append('  </div>')
    out.append('</div>')
    if t.get("flow"):
        out.append(f'<div class="aws-flow-list"><h6>{esc(t["flow"].get("title","데이터 흐름"))}</h6><ol>'
                   + "".join(f"<li>{rich(x)}</li>" for x in t["flow"].get("steps", [])) + "</ol></div>")
    return "\n".join(out)


# 하우스 스타일은 데코 이모지를 쓰지 않는다(강조는 서체 굵기와 선으로). ★·☆ 는 강조 마커라 유지.
_DECO_RE = re.compile(
    r"^(?:[\U0001F000-\U0001FAFF\u2190-\u2604\u2606-\u27BF\u2B00-\u2BFF\uFE0F\u200D]|\s)+"
)


def _strip_deco(s):
    return _DECO_RE.sub("", str(s or "")).strip()


def render_insight(t):
    title = esc(_strip_deco(t.get("title", "분석 코멘트")))
    items = "".join(f"<li>{rich(x)}</li>" for x in t.get("items", []))
    return f'<div class="insight">\n  <div class="title">{title}</div>\n  <ul>{items}</ul>\n</div>'


def render_overview(t):
    """대상 개요: 메뉴 칩 그리드 + (선택) insight."""
    chips = []
    for c in t.get("chips", []):
        href = f'#{esc(c["href"])}' if c.get("href") else "#"
        num = f'<span class="num">{esc(c.get("num",""))}</span>' if c.get("num") not in (None, "") else ""
        chips.append(f'<a class="menu-chip" href="{href}">{num}<span class="text-wrap">'
                     f'<span class="name">{esc(c.get("name"))}</span>'
                     f'<span class="desc">{esc(c.get("desc",""))}</span></span></a>')
    out = '<div class="menu-grid">\n' + "\n".join(chips) + "\n</div>"
    if t.get("insight"):
        out += "\n" + render_insight(t["insight"])
    return out


def render_modules(t):
    """모듈/항목 상세: menu-list > menu-item(menu-name + simple-desc 또는 detail의 label/value 쌍)."""
    items = []
    for it in t.get("items", []):
        inner = f'<div class="menu-name">{esc(it.get("name"))}</div>'
        if it.get("simple"):
            inner += f'<div class="simple-desc">{rich(it["simple"])}</div>'
        if it.get("rows"):
            det = []
            for r in it["rows"]:
                lab = "label opt" if r.get("opt") else "label"
                det.append(f'<span class="{lab}">{esc(r.get("label",""))}</span>'
                           f'<span class="value">{rich(r.get("value",""))}</span>')
            inner += '<div class="detail">' + "".join(det) + "</div>"
        cls = "menu-item new-module" if it.get("new") else "menu-item"
        items.append(f'  <div class="{cls}">{inner}</div>')
    return '<div class="menu-list">\n' + "\n".join(items) + "\n</div>"


def render_narrative(s):
    """다크 강조 블록(value-chain·종합 총평). 자체 <section class="final-report">라 .section 래퍼 없음."""
    t = s.get("table", {})
    title = esc(s.get("title") or t.get("title", "종합 분석"))
    lead = f'\n<p class="lead">{rich(t["lead"])}</p>' if t.get("lead") else ""
    items = []
    for i, it in enumerate(t.get("items", []), 1):
        items.append(f'  <div class="item"><div class="no">{i}</div>'
                     f'<h3>{rich(it.get("h3",""))}</h3><p>{rich(it.get("body",""))}</p></div>')
    return (f'<section class="final-report" id="{esc(s["id"])}">\n<h2>{title}</h2>{lead}\n'
            + "\n".join(items) + "\n</section>")


def render_questions(t):
    """확인 필요 질문(고객 확인용): insight 박스 + 번호 목록 + 미확정 시 영향."""
    title = esc(t.get("title", "확인 필요 질문 (고객 확인용)"))
    qs = []
    for q in t.get("questions", []):
        if isinstance(q, dict):
            imp = (f' <span style="color:var(--muted);">— 미확정 시 영향: {esc(q.get("impact",""))}</span>'
                   if q.get("impact") else "")
            qs.append(f'    <li>{rich(q.get("q",""))}{imp}</li>')
        else:
            qs.append(f'    <li>{rich(q)}</li>')
    return (f'<div class="insight">\n  <div class="title">{title}</div>\n  <ol>\n'
            + "\n".join(qs) + "\n  </ol>\n</div>")


def render_coverage(t):
    """RFP 요건 커버리지 대조표(effort-table). 상태=반영/부분/제외/미확인."""
    sty = [("미확인", 'style="color:#c0392b;font-weight:700;"'), ("제외", 'style="color:#888;"'),
           ("부분", 'style="color:#b9770a;"'), ("반영", "")]
    rows = []
    for r in t.get("rows", []):
        st = str(r.get("status", ""))
        scls = next((v for k, v in sty if k in st), "")
        rows.append(f'    <tr><td style="text-align:center;">{esc(r.get("id",""))}</td>'
                    f'<td>{rich(r.get("req",""))}</td><td>{rich(r.get("where",""))}</td>'
                    f'<td {scls}>{esc(st)}</td></tr>')
    return ('<table class="effort-table fixed">\n'
            '  <colgroup><col style="width:54px;"><col><col style="width:28%;"><col style="width:84px;"></colgroup>\n'
            '  <thead><tr><th>ID</th><th>요건</th><th>반영 위치</th><th>상태</th></tr></thead>\n  <tbody>\n'
            + "\n".join(rows) + "\n  </tbody>\n</table>")


def render_figure(t):
    """이미지 임베드(고객 제공 구성도 등 '자료'를 원본 그대로). 로컬 파일은 base64로 인라인(self-contained)."""
    src = t.get("src", "")
    if src and not src.startswith(("http://", "https://", "data:")):
        p = src if os.path.isabs(src) else os.path.normpath(os.path.join(HERE, "..", src))
        if os.path.isfile(p):
            ext = (os.path.splitext(p)[1].lstrip(".").lower() or "png")
            mime = {"jpg": "jpeg", "svg": "svg+xml"}.get(ext, ext)
            with open(p, "rb") as f:
                src = f"data:image/{mime};base64," + base64.b64encode(f.read()).decode()
        else:
            print(f"[WARN] figure 이미지 파일 없음: {t.get('src')} → 캡션만 렌더", file=sys.stderr)
            src = ""
    cap = rich(t.get("caption", ""))
    capdiv = (f'<figcaption style="font-size:12px;color:var(--muted);margin-top:8px;text-align:center;">{cap}</figcaption>'
              if cap else "")
    img = (f'<img src="{esc(src)}" alt="{esc(t.get("caption","도식"))}" '
           f'style="max-width:100%;height:auto;border:1px solid var(--line);">' if src else
           f'<div style="color:var(--muted);padding:20px;border:1px dashed var(--line);">[이미지 없음]</div>')
    return f'<figure style="margin:0;text-align:center;">{img}{capdiv}</figure>'


def render_section(s):
    k = s.get("kind")
    if k == "narrative":                      # 다크 풀블록 — 일반 .section 래퍼/헤더 없이 자체 섹션
        return render_narrative(s)
    if k == "part":                           # §22 상위 그룹 타이틀(1·2·3…) — 헤더만, 본문 없음. no는 명시 권장
        return (f'<div class="section-header part-title" id="{esc(s["id"])}">'
                f'<div class="num-box">{esc(s.get("no",""))}</div>'
                f'<div class="text"><h2>{esc(s.get("title"))}</h2></div></div>')
    area = f'<span class="area">{esc(s.get("area"))}</span>' if s.get("area") else ""
    head = (f'<div class="section-header"><div class="num-box">{esc(s.get("no",""))}</div>'
            f'<div class="text"><h2>{esc(s.get("title"))}</h2>{area}</div></div>')
    if k == "ia":
        body = render_ia_table(s["table"])
    elif k == "monthly":
        body = render_monthly_table(s["table"])
    elif k == "area":
        body = render_area_table(s["table"])
    elif k == "gantt":
        body = render_gantt(s["table"])
    elif k == "summary":
        body = render_summary(s["table"])
    elif k == "matrix":
        body = render_matrix(s["table"])
    elif k == "wbs":
        body = render_wbs(s["table"])
    elif k == "concept":
        body = render_concept(s["table"])
    elif k == "infra":
        body = render_infra(s["table"])
    elif k == "overview":
        body = render_overview(s["table"])
    elif k == "modules":
        body = render_modules(s["table"])
    elif k == "questions":
        body = render_questions(s["table"])
    elif k == "coverage":
        body = render_coverage(s["table"])
    elif k == "insight":
        body = render_insight(s["table"])
    elif k == "figure":
        body = render_figure(s["table"])
    else:
        body = rich(s.get("html", ""))
    # 한 섹션에 prose + 표를 같이 둘 수 있게: html(있으면) 먼저
    if s.get("html") and k in ("ia", "monthly", "area", "gantt", "summary", "matrix", "wbs", "concept",
                               "infra", "overview", "modules", "questions", "coverage", "insight", "figure"):
        body = rich(s["html"]) + "\n" + body
    return f'<section class="section" id="{esc(s["id"])}">\n{head}\n{body}\n</section>'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data"); ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    # 출력 위치 가드: 산출물은 _workspace/{slug}/ 또는 output/ 안에만(temp·cwd 등 흩어짐 방지)
    norm = a.out.replace("\\", "/")
    if not any(seg in norm for seg in ("_workspace/", "output/")):
        print(f'[WARN] 출력 경로가 약속된 위치 밖입니다: {a.out}\n'
              f'       산출물·중간물은 "_workspace/{{slug}}/03_draft.html"(중간) 또는 "output/{{주제}}_vX.Y.html"(최종)에 두세요. '
              f'temp/홈 디렉토리에 흩어지면 KB 누적·추적이 깨집니다.', file=sys.stderr)
    d = json.load(open(a.data, encoding="utf-8"))
    # 구성 가드: 확인 질문 섹션(항상) + 인프라 TO-BE는 AS-IS 동반
    _titles = [str(s.get("title", "")) for s in d.get("sections", [])]
    if _titles and not any(("확인" in t and "질문" in t) for t in _titles):
        print('[WARN] "확인 필요 질문" 섹션이 없음 — 추정·데이터갭·미정분기를 맨 마지막 prose 섹션에 '
              '질문 리스트(+미확정 시 영향)로 넣을 것(report-spec §9).', file=sys.stderr)
    _infra_t = [str(s.get("title", "")) for s in d.get("sections", []) if s.get("kind") == "infra"]
    _all_t = [str(s.get("title", "")) for s in d.get("sections", [])]
    _tobe = any(("TO-BE" in t or "제안" in t or "TOBE" in t) for t in _infra_t)
    # AS-IS는 figure로 실릴 수 있으므로 전체 섹션 title에서 탐지
    _asis = any(("AS-IS" in t or "현행" in t or "ASIS" in t) for t in _all_t)
    if _tobe and not _asis:
        print('[WARN] 인프라 제안(TO-BE)만 있고 현행(AS-IS)이 없음 — 인프라 제안은 AS-IS와 쌍으로 제시'
              '(현행 미파악이면 "현행 미파악·확인 필요"로라도 표기). solution-architect.', file=sys.stderr)
    # 섹션 번호 자동 부여(no 미지정 시 순번; narrative=총평은 번호 없음) — "끼워넣고 나중에 번호정리"를 코드가 보장
    _auto = 0
    for s in d.get("sections", []):
        if s.get("kind") == "narrative":
            continue
        cur = s.get("no")
        if cur in (None, "", "auto"):
            _auto += 1; s["no"] = str(_auto)
        else:
            try: _auto = int(str(cur).split("-")[0].split(".")[0])
            except Exception: pass
    # SSOT: 월별표가 있으면 합계를 '계산'해 hero(@token)·footer({token})에 자동 주입 → 수치 일관 보장
    ssot = {}
    for s in d["sections"]:
        if s.get("kind") == "monthly":
            ssot = compute_monthly(s["table"]); break
    for c in d.get("hero", []):
        v = c.get("value")
        if isinstance(v, str) and v.startswith("@"):
            c["value"] = ssot.get(v[1:], v)
    if ssot and isinstance(d.get("footer"), str):
        for k, val in ssot.items():
            d["footer"] = d["footer"].replace("{" + k + "}", val)
    m = d.get("meta", {})
    badge = esc(m.get("client", ""))
    # §22 로고·Mini GNB: meta.logo(파일 경로 또는 data URI) 지정 시 배지 대신 헤더 로고 + 스크롤 고정 바.
    #   화이트 로고 자산: template/etribe_logo_white.png (다크 헤더용). 미지정 시 기존 배지 동작 유지.
    logo_uri = None
    logo = m.get("logo")
    if logo:
        if str(logo).startswith("data:"):
            logo_uri = str(logo)
        else:
            lp = logo if os.path.isabs(logo) else os.path.normpath(os.path.join(HERE, "..", logo))
            if os.path.isfile(lp):
                ext = (os.path.splitext(lp)[1].lstrip(".").lower() or "png")
                mime = {"jpg": "jpeg", "svg": "svg+xml"}.get(ext, ext)
                logo_uri = f"data:image/{mime};base64," + base64.b64encode(open(lp, "rb").read()).decode()
            else:
                print(f"[WARN] meta.logo 파일 없음: {logo} → 배지로 폴백", file=sys.stderr)
    mini_gnb = (f'<div class="mini-gnb" id="mini-gnb"><span>{esc(m.get("title"))}</span>'
                f'<img src="{esc(logo_uri)}" alt="logo"></div>') if logo_uri else ""
    header_brand = (f'  <img class="header-logo" src="{esc(logo_uri)}" alt="logo">' if logo_uri
                    else (f'  <span class="badge">{badge}</span>' if badge else ""))
    parts = [
        '<!DOCTYPE html>', '<html lang="ko">', '<head>', '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f'<title>{esc(m.get("title"))} — {esc(m.get("version",""))}</title>',
        css_block(m.get("palette")), '</head>',
        '<body class="has-mini-gnb">' if logo_uri else '<body>',
        mini_gnb,
        '<header class="top-header">',
        header_brand,
        f'  <h1>{esc(m.get("title"))}</h1>',
        f'  <p class="subtitle">{esc(m.get("subtitle"))}</p>',
        render_hero(d.get("hero")), '</header>',
        '<div class="layout">', render_nav(d["sections"]), '<main class="main">',
    ]
    for s in d["sections"]:
        parts.append(render_section(s))
    mini_js = ('<script>\n(function(){var b=document.getElementById("mini-gnb"),hd=document.querySelector(".top-header");'
               'if(!b||!hd)return;var f=function(){b.classList.toggle("on",window.scrollY>hd.offsetHeight-10);};'
               'window.addEventListener("scroll",f,{passive:true});f();})();\n</script>') if logo_uri else ""
    parts += ['</main>', '</div><!-- /.layout -->',
              f'<footer class="footer">{rich(d.get("footer",""))}</footer>',
              mini_js,
              '</body>', '</html>']
    htmlout = "\n".join(p for p in parts if p != "")
    # 안전: <style> 중괄호 균형
    import re
    style = "".join(re.findall(r"<style[^>]*>(.*?)</style>", htmlout, re.S))
    if style.count("{") != style.count("}"):
        print(f"[ERROR] <style> 중괄호 불균형 {{={style.count('{')} }}={style.count('}')}", file=sys.stderr); return 1
    open(a.out, "w", encoding="utf-8").write(htmlout)
    print(f"[OK] 렌더 완료 → {a.out} ({htmlout.count(chr(10))+1}줄, 섹션 {len(d['sections'])}, "
          f"IA행 {sum(1+len(g.get('children',[])) for s in d['sections'] if s.get('kind')=='ia' for g in s['table'].get('groups',[]))})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
