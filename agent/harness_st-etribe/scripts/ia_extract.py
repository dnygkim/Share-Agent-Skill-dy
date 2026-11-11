#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ia_extract.py — 사이트 IA 정밀 추출기 (v0.1)

analyst가 기존 사이트 IA를 뽑을 때 쓰는 도구. references/ia-extraction-upgrade.md 의
규칙을 코드화한다. "보이는 슬림 nav"가 아니라 메가메뉴/사이트맵을 정본으로,
1노드=1줄, 탭/그룹/페이지/외부를 type으로 구분하고, page/view 이중 카운트를 낸다.

사용:
    python scripts/ia_extract.py <URL> [--json out.json] [--lang kr]

출력: 사람이 읽는 트리(stdout) + JSON(--json 또는 stdout 말미).
한계(v0.1): 메뉴 마크업은 사이트마다 다르다. 이 도구는 (1)중첩 <ul><li><a> 트리와
(2)"제목 div + ul" 패널을 모두 시도하고, URL 경로 깊이로 교차검증한다. 자동 추출이
부실하면 analyst가 firecrawl/playwright로 보완하고, 로그인 영역은 사용자에게 요청한다.
"""
import sys, re, json, argparse, ssl, urllib.request
from html import unescape
from html.parser import HTMLParser
from urllib.parse import urlparse, urljoin

for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")   # cp949 콘솔 한글 깨짐 방지 (보조규칙)
    except Exception: pass

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"}
LOGIN_KW = ["로그인", "login", "logout", "회원가입", "signup", "마이페이지", "mypage", "회원", "탈퇴", "myaccount"]
# 로그인 단서 발견 시 유추할 표준 회원 도메인(분리 페이지) — source:추정
MEMBER_SET = ["로그인", "회원가입(약관동의·본인인증·정보입력·완료)", "아이디/비밀번호 찾기",
              "소셜 로그인", "회원정보 수정", "회원 탈퇴", "마이페이지"]


def fetch(url, insecure=False):
    # 기본: TLS 검증 ON(MITM 방지). 내부 자체서명 호스트만 --insecure로 명시적 우회.
    ctx = ssl.create_default_context()
    if insecure:
        ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25, context=ctx).read()
    m = re.search(rb'charset=["\']?([\w-]+)', raw[:2000], re.I)
    for enc in [(m.group(1).decode() if m else "utf-8"), "utf-8", "cp949", "euc-kr"]:
        try: return raw.decode(enc)
        except Exception: continue
    return raw.decode("utf-8", "replace")


def clean(t):
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", "", t))).strip()


def anchors(seg):
    """seg 안의 <a> (텍스트, href) — dedup, 순서보존."""
    out, seen = [], set()
    for m in re.finditer(r'<a\b[^>]*href="([^"]*)"[^>]*>(.*?)</a>', seg, re.S):
        txt = clean(m.group(2)); href = m.group(1)
        if txt and (txt, href) not in seen:
            seen.add((txt, href)); out.append((txt, href))
    return out


def grab_block(html, marker, tag="div"):
    """marker(클래스 문자열)를 포함하는 <tag>를 div 밸런싱으로 정확히 잘라낸다."""
    blocks, i = [], 0
    pat = re.compile(rf"<(/?){tag}\b", re.I)
    while True:
        i = html.find(marker, i)
        if i == -1: break
        st = html.rfind("<" + tag, 0, i)
        depth = 0; end = None
        for mm in pat.finditer(html, st):
            depth += -1 if mm.group(1) else 1
            if depth == 0:
                end = html.find(">", mm.end()) + 1; break
        if end: blocks.append(html[st:end])
        i += len(marker)
    return blocks


class UlTree(HTMLParser):
    """중첩 <ul><li><a>+<ul> 를 트리로. 각 li의 첫 <a>가 라벨."""
    def __init__(s):
        super().__init__(); s.root = []; s.lists = [s.root]; s.lis = []; s.cap = False; s.buf = ""
    def handle_starttag(s, t, attrs):
        d = dict(attrs)
        if t == "ul":
            s.lists.append(s.lis[-1]["children"] if s.lis else s.root)
        elif t == "li":
            node = {"name": None, "href": None, "type": None, "children": []}
            (s.lists[-1] if s.lists else s.root).append(node); s.lis.append(node)
        elif t == "a" and s.lis and s.lis[-1]["name"] is None:
            s.lis[-1]["href"] = d.get("href", ""); s.cap = True; s.buf = ""
            if "more" in d.get("class", ""): s.lis[-1]["_more"] = True
    def handle_endtag(s, t):
        if t == "ul" and len(s.lists) > 1: s.lists.pop()
        elif t == "li" and s.lis: s.lis.pop()
        elif t == "a" and s.cap:
            s.lis[-1]["name"] = clean(s.buf); s.cap = False
    def handle_data(s, data):
        if s.cap: s.buf += data


def detect_nav(html):
    """폴백: 메뉴 후보 중 <a>가 가장 많은 블록(중첩 ul/li/a 패턴 사이트용)."""
    cands = []
    for marker in ['global-navigation', 'gnb', 'lnb', 'sitemap']:
        cands += grab_block(html, marker, "div") + grab_block(html, marker, "nav")
    if not cands:
        m = re.search(r"<nav\b.*?</nav>", html, re.S | re.I)
        cands = [m.group(0)] if m else [html]
    return max(cands, key=lambda b: b.count("<a "))


def panel_title(b):
    m = re.search(r'class="[^"]*\btitle\b[^"]*"[^>]*>(.*?)</div>', b, re.S)
    return clean(m.group(1)) if m else None


def dedup_children(kids):
    seen, out = set(), []
    for c in kids:
        k = (c.get("name") or "").strip().lower()
        if k and k not in seen:
            seen.add(k); c["children"] = dedup_children(c.get("children", [])); out.append(c)
    return out


def dedup_nodes(nodes):
    """메가메뉴가 2-3중 렌더(슬림·메가·모바일)되므로 1뎁스명으로 병합."""
    by, order = {}, []
    for n in nodes:
        k = (n.get("name") or "").strip().lower()
        if not k: continue
        if k not in by:
            by[k] = n; order.append(k)
        else:
            e = by[k]
            if (not e.get("href") or e["href"] == "#") and n.get("href") and n["href"] != "#":
                e["href"] = n["href"]
            names = {(c.get("name") or "").lower() for c in e["children"]}
            for c in n["children"]:
                if (c.get("name") or "").lower() not in names:
                    e["children"].append(c)
    return [{**by[k], "children": dedup_children(by[k]["children"])} for k in order]


def _leaf_paths(node):
    out = []
    for c in node.get("children", []):
        if (c.get("href") or "").startswith("/"): out.append(c["href"])
        out += _leaf_paths(c)
    return out


def prune_cross_dups(tree):
    """블록 경계 bleed로 한 1뎁스가 옆 메뉴 항목을 흡수한 중복 제거.
    섹션(/lang/Section)별 소유자 = 그 섹션을 가장 '순수하게'(비율 최대) 담은 1뎁스.
    (count 동률이어도, 100% 그 섹션인 메뉴가 혼합 메뉴를 이긴다.)"""
    import collections
    sec = lambda p: "/".join(p.split("/")[:3]) if p.count("/") >= 3 else None
    info = []
    for t in tree:
        leaves = _leaf_paths(t)
        info.append((t, collections.Counter(s for s in map(sec, leaves) if s), max(len(leaves), 1)))
    owner = {}
    for S in set().union(*[set(c) for _, c, _ in info]) if info else set():
        owner[S] = max(info, key=lambda x: x[1].get(S, 0) / x[2])[0]

    def filt(node, top):
        node["children"] = [c for c in node.get("children", [])
                            if c.get("children") or not (c.get("href", "").startswith("/")
                            and sec(c["href"]) and owner.get(sec(c["href"])) is not top)]
        for c in node["children"]: filt(c, top)
    for t, _, _ in info: filt(t, t)
    return tree


def extract_tree(html, host, lang):
    """정본 = 메가패널(제목 div + ul + depth3-list). 슬림 nav 아님(E1 방지)."""
    panels = grab_block(html, "menu-box", "div") or grab_block(html, "gnb-2depth", "div")
    nodes = []
    for b in panels:
        title = panel_title(b)
        up = UlTree(); up.feed(b)
        kids = [n for n in up.root if n.get("name")]
        href = "#"
        if title is None:                      # 제목 없는 패널 = 첫 항목이 1뎁스 랜딩
            if not kids: continue
            title, href, kids = kids[0]["name"], (kids[0].get("href") or "#"), kids[1:]
        nodes.append({"name": title, "href": href, "type": None, "children": kids})
    nodes = dedup_nodes(nodes)
    if not nodes:                              # 폴백: 중첩 ul/li/a
        up = UlTree(); up.feed(detect_nav(html)); nodes = [n for n in up.root if n.get("name")]
    return nodes


def tag_types(node, base_host, lang):
    """page | tab | group | external 태깅 + 탭 판별(부모 href == 자식 href)."""
    href = node.get("href") or ""
    kids = node.get("children", [])
    # external
    if href.startswith("http") and urlparse(href).netloc and urlparse(href).netloc != base_host:
        node["type"] = "external"
    elif href in ("", "#", None) and kids:
        node["type"] = "group"            # 묶음(#) — 자식은 별도 페이지
    else:
        node["type"] = "page"
    # 탭 판별: 자식 중 부모와 같은 href가 있으면 이 노드는 탭형 페이지, 그 자식들은 tab
    if kids and node["type"] == "page" and any((k.get("href") == href) for k in kids):
        node["tabs"] = [{"name": k["name"], "href": k.get("href"), "type": "tab"} for k in kids]
        node["children"] = []             # 탭은 children에서 빼고 tabs로
    else:
        for k in kids: tag_types(k, base_host, lang)
    return node


def count(nodes, c):
    for n in nodes:
        t = n.get("type")
        if t == "page":
            c["page"] += 1; c["view"] += 1
            c["view"] += len(n.get("tabs", []))     # 탭 = 디자인 뷰로 추가
        elif t == "external":
            c["external"] += 1
        count(n.get("children", []), c)
    return c


def render(nodes, depth=0):
    out = []
    for n in nodes:
        ind = "  " * depth
        mark = {"page": "•", "group": "▸", "external": "↗", None: "•"}.get(n.get("type"), "•")
        out.append(f"{ind}{mark} {n['name']}  [{n.get('href','')}] ({n.get('type')})")
        for tb in n.get("tabs", []):
            out.append(f"{ind}    - {tb['name']}  [{tb.get('href','')}] (tab)")
        out += render(n.get("children", []), depth + 1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url"); ap.add_argument("--json"); ap.add_argument("--lang", default="kr")
    ap.add_argument("--insecure", action="store_true", help="자체서명 내부 호스트만 TLS 검증 우회")
    a = ap.parse_args()
    html = fetch(a.url, insecure=a.insecure)
    host = urlparse(a.url).netloc

    # 1) 본문 메뉴 트리 (메가패널 정본) + 경계 bleed 중복 제거
    tree = prune_cross_dups(extract_tree(html, host, a.lang))
    for n in tree: tag_types(n, host, a.lang)

    # 2) footer (법적/유틸 — 자주 누락) + 외부 분리
    fs = html.lower().find("<footer"); fe = html.lower().find("</footer>", fs)
    footer_in, footer_ext = [], []
    if fs != -1:
        for txt, href in anchors(html[fs:fe + 9]):
            (footer_ext if (href.startswith("http") and host not in href) else footer_in).append(
                {"name": txt, "href": href, "type": "external" if (href.startswith("http") and host not in href) else "page"})

    # 3) 로그인/회원 도메인 감지
    login = {k for k in LOGIN_KW if re.search(re.escape(k), html, re.I)}
    member = {"detected": bool(login), "signals": sorted(login),
              "inferred_pages": (MEMBER_SET if login else []),
              "note": "로그인 단서 발견 → 회원 도메인(가입·탈퇴 등) 유추(source:추정). 로그인 필요 영역은 접근 불가 시 사용자에게 캡처/계정 요청." if login
                      else "로그인 단서 0 → 비회원 정보형 사이트로 판단."}

    c = count(tree, {"page": 0, "view": 0, "external": 0})
    c["page"] += sum(1 for f in footer_in)        # footer 내부 페이지 포함
    c["view"] += sum(1 for f in footer_in)
    result = {"site": a.url, "tree": tree, "footer": footer_in, "external": footer_ext,
              "member_domain": member, "access_blocked": [],
              "counts": {"page_count": c["page"], "view_count": c["view"], "external_count": c["external"] + len(footer_ext)}}

    print("\n".join(render(tree)))
    if footer_in: print("\n[FOOTER]\n" + "\n".join(f"  • {f['name']}  [{f['href']}]" for f in footer_in))
    if footer_ext: print("\n[EXTERNAL] " + " · ".join(f["name"] for f in footer_ext))
    print(f"\n[MEMBER] {member['note']}")
    print(f"[COUNTS] page={result['counts']['page_count']} view={result['counts']['view_count']} external={result['counts']['external_count']}")
    print("\n※ 자동추출 한계 시 firecrawl/playwright 보완 + 로그인 영역은 사용자에 캡처/계정 요청(추측 금지).")

    if a.json:
        with open(a.json, "w", encoding="utf-8") as f: json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\nJSON saved: {a.json}")
    else:
        print("\n----- JSON -----"); print(json.dumps(result, ensure_ascii=False, indent=2)[:4000])


if __name__ == "__main__":
    main()
