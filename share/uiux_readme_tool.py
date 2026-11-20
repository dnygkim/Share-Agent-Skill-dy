# uiux_readme_tool.py — share/uiux-upstream-sync.sh 보조 (한국어 README 조립 · 검증 · 릴리즈노트 행 추가)
#   python -X utf8 -I share/uiux_readme_tool.py <명령> ...
# 명령
#   extract-body <README.md> <out>                 「<!-- ko-body:start」 표식 아래 본문만 꺼냄 (표식 없으면 exit 3)
#   reseed-body  <ko-upstream.md> <out>            원본 한국어판에서 제목 · 언어 선택 블록을 뺀 본문
#   validate     <en-new.md> <body.md>             코드 블록 수 · 제목 수 · 한글 분량 검사 (문제 있으면 exit 1)
#   fix-anchors  <en-new.md> <body.md>             영문 제목 앵커로 남은 문서 안 링크를 같은 순번 한국어 제목 앵커로 보정
#   assemble     <README.md> <body.md> <folder> <out> <row|-> <full_sha> <date> <ver_label>
#   root-row     <root README.md> <row text> <YYYY.MM.DD>   「릴리즈노트 현황」 표 맨 위에 ui-ux 행 추가
#   versions     <ver> <file>...                   「UI UX Pro Max(vX · MIT)」 · 「…ui-ux-pro-max-skill)(vX · MIT)」 버전 표기 갱신
import os
import re
import sys

UP = "https://github.com/nextlevelbuilder/ui-ux-pro-max-skill"
BODY_MARK = "<!-- ko-body:start"
SHA_RE = re.compile(r"^<!-- upstream-sha: ([0-9a-f]{40}) -->$", re.M)
LANG = {"zh": "🇨🇳 简体中文", "ja": "🇯🇵 日本語", "ko": "🇰🇷 한국어(원본판)", "fr": "🇫🇷 Français",
        "fa": "🇮🇷 فارسی", "az": "🇦🇿 Azərbaycanca", "id": "🇮🇩 Bahasa Indonesia", "vi": "🇻🇳 Tiếng Việt",
        "es": "🇪🇸 Español", "de": "🇩🇪 Deutsch", "pt": "🇵🇹 Português", "ru": "🇷🇺 Русский", "tr": "🇹🇷 Türkçe"}


def rd(p):
    with open(p, encoding="utf-8", newline="") as f:
        return f.read().replace("\r\n", "\n")


def wr(p, s):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)


def strip_title_and_langs(md):
    """첫 줄 제목 + 바로 다음 언어 선택 <p align="center"> 블록(README.xx.md 링크 묶음)을 뺀 나머지."""
    lines = md.split("\n")
    i = 0
    while i < len(lines) and not lines[i].startswith("# "):
        i += 1
    i += 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and lines[i].strip().startswith("<p"):
        j = i
        while j < len(lines) and "</p>" not in lines[j]:
            j += 1
        block = "\n".join(lines[i:j + 1])
        if re.search(r"README\.[a-z]{2}\.md", block):
            i = j + 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    return "\n".join(lines[i:]).rstrip("\n") + "\n"


def structure(md):
    fences, heads, in_code = 0, 0, False
    prose = []
    for ln in md.split("\n"):
        if ln.lstrip().startswith("```"):
            fences += 1
            in_code = not in_code
            continue
        if in_code:
            continue
        if re.match(r"^#{2,4} ", ln):
            heads += 1
        prose.append(ln)
    return fences, heads, "\n".join(prose)


def gh_slug(h):
    h = re.sub(r"<[^>]+>", "", h).strip().lower()
    h = re.sub(r"[^\w\- ]", "", h)          # GitHub 앵커: 글자(한글 포함) · 숫자 · _ · - · 공백만 남기고 공백 → -
    return h.replace(" ", "-")


def heading_anchors(md):
    out, seen, in_code = [], {}, False
    for ln in md.split("\n"):
        if ln.lstrip().startswith("```"):
            in_code = not in_code
            continue
        m = re.match(r"^(#{2,4}) (.+)$", ln)
        if m and not in_code:
            s = gh_slug(m.group(2))
            n = seen.get(s, 0)
            seen[s] = n + 1
            out.append(s if n == 0 else f"{s}-{n}")
    return out


def cmd_fix_anchors(en_new, body):
    """영문 제목 앵커(#installation 등)로 남은 문서 안 링크를 같은 순번의 한국어 제목 앵커로 바꾼다."""
    en = heading_anchors(strip_title_and_langs(rd(en_new)))
    b = rd(body)
    ko = heading_anchors(b)
    if len(en) != len(ko):
        print(f"앵커 보정 생략: 제목 수 다름 (영문 {len(en)} · 한국어 {len(ko)})")
        return
    m = dict(zip(en, ko))
    fixed = []

    def rep(mo):
        a = mo.group(2)
        if a in ko or a not in m:
            return mo.group(0)
        fixed.append(f"#{a} → #{m[a]}")
        return mo.group(1) + m[a] + mo.group(3)
    nb = re.sub(r'(\]\(#)([^)\s]+)(\))', rep, b)
    nb = re.sub(r'(href="#)([^"]+)(")', rep, nb)
    bad = sorted({a for a in re.findall(r'\]\(#([^)\s]+)\)|href="#([^"]+)"', nb) for a in a if a} - set(ko))
    if fixed:
        wr(body, nb)
        print("앵커 보정: " + " · ".join(fixed))
    if bad:
        print("경고: 대상 제목이 없는 앵커 " + " · ".join("#" + x for x in bad))


def release_rows(readme):
    m = re.search(r"^## 릴리즈노트\s*\n", readme, re.M)
    if not m:
        return []
    rows = []
    for ln in readme[m.end():].split("\n"):
        s = ln.strip()
        if not s:
            if rows:
                break
            continue
        if not s.startswith("|"):
            break
        rows.append(s)
    # 헤더 · 구분선 제외
    return [r for r in rows if not re.match(r"^\|\s*요약내용", r) and not re.match(r"^\|[\s:|-]+\|$", r)]


def cmd_extract_body(readme, out):
    t = rd(readme)
    k = t.find(BODY_MARK)
    if k < 0:
        sys.exit(3)
    nl = t.find("\n", k)
    wr(out, t[nl + 1:].lstrip("\n"))


def cmd_reseed_body(ko, out):
    wr(out, strip_title_and_langs(rd(ko)))


def cmd_validate(en_new, body):
    en_f, en_h, _ = structure(strip_title_and_langs(rd(en_new)))
    b = rd(body)
    b_f, b_h, prose = structure(b)
    hangul = len(re.findall(r"[가-힣]", prose))
    latin = len(re.findall(r"[A-Za-z]", re.sub(r"<[^>]+>|\]\([^)]*\)|`[^`]*`|https?://\S+", "", prose)))
    errs = []
    if b_f != en_f:
        errs.append(f"코드 블록 경계 수 불일치 (영문 {en_f} · 한국어 {b_f})")
    if abs(b_h - en_h) > 1:
        errs.append(f"제목 수 불일치 (영문 {en_h} · 한국어 {b_h})")
    if hangul < 3000 or hangul < latin * 0.5:
        errs.append(f"한글 분량 부족 (한글 {hangul}자 · 영문자 {latin}자)")
    if len(b) < len(rd(en_new)) * 0.5:
        errs.append("본문 길이가 영문의 절반 미만")
    print(f"검증: 코드 블록 {b_f}/{en_f} · 제목 {b_h}/{en_h} · 한글 {hangul}자")
    if errs:
        print("검증 실패: " + " / ".join(errs))
        sys.exit(1)


def cmd_assemble(readme, body, folder, out, row, full_sha, date, ver_label):
    old = rd(readme) if os.path.exists(readme) else ""
    rows = release_rows(old)
    if row != "-":
        rows.insert(0, row)
    langs = []
    for f in sorted(os.listdir(folder)):
        m = re.match(r"^README\.([a-z]{2})\.md$", f)
        if m and m.group(1) != "en":
            langs.append(f'<a href="{f}">{LANG.get(m.group(1), m.group(1))}</a>')
    short = full_sha[:7]
    head = [
        "# [UI UX Pro Max](https://uupm.cc)",
        "",
        "## 릴리즈노트",
        "",
        "| 요약내용 | 업데이트 일자 | 소유자 |",
        "|---|---|---|",
        *rows,
        "",
        "",
        '<p align="center">',
        "  🇰🇷 한국어 |",
        '  <a href="README.en.md">🇺🇸 English</a>' + (" |" if langs else ""),
        *[("  " + l + (" |" if i < len(langs) - 1 else "")) for i, l in enumerate(langs)],
        "</p>",
        "",
        f"> **참고:** [nextlevelbuilder/ui-ux-pro-max-skill]({UP}) 원본 리포(MIT 라이선스) 백업 · 기준 **{ver_label}** · "
        f"커밋 [`{short}`]({UP}/commit/{full_sha})({date}) · 매일 23:30 원본 깃허브 확인 후 바뀐 파일 1:1 반영 · "
        "이 README = 원본 영문 README([README.en.md](README.en.md))의 한국어 번역, 원본 반영 때 함께 갱신 · "
        "원본이 제공하는 다른 언어판(README.ko.md 등)은 그대로 보관",
        "",
        f"<!-- upstream-sha: {full_sha} -->",
        "<!-- ko-body:start — 이 줄 아래 = 영문 README 번역 본문 (공유 리포 share/uiux-upstream-sync.sh 가 갱신) -->",
        "",
    ]
    wr(out, "\n".join(head) + rd(body).lstrip("\n"))


def cmd_root_row(root, text, date):
    t = rd(root)
    m = re.search(r"^## 릴리즈노트 현황.*$", t, re.M)
    if not m:
        print("루트 README 「릴리즈노트 현황」 표 없음 — 행 추가 생략")
        return
    sep = re.compile(r"^\|:---\|.*$", re.M).search(t, m.end())
    if not sep:
        print("루트 README 표 구분선 없음 — 행 추가 생략")
        return
    row = (f"| <sub>스킬</sub> | <sub>[ui-ux-pro-max-skill](skills/ui-ux-pro-max-skill/README.md)</sub> | "
           f"<sub>{text}</sub> | <sub>{date}</sub> | <sub>김단영</sub> |")
    wr(root, t[:sep.end()] + "\n" + row + t[sep.end():])


def cmd_versions(ver, *files):
    for p in files:
        if not os.path.exists(p):
            continue
        t = rd(p)
        n = re.sub(r"(UI UX Pro Max\()v[0-9][0-9.]*( · MIT\))", r"\g<1>" + ver + r"\g<2>", t)
        n = re.sub(r"(nextlevelbuilder/ui-ux-pro-max-skill\)\()v[0-9][0-9.]*( · MIT\))", r"\g<1>" + ver + r"\g<2>", n)
        if n != t:
            wr(p, n)
            print(f"버전 표기 갱신: {os.path.basename(p)} → {ver}")


if __name__ == "__main__":
    c, a = sys.argv[1], sys.argv[2:]
    {"extract-body": cmd_extract_body, "reseed-body": cmd_reseed_body, "validate": cmd_validate,
     "fix-anchors": cmd_fix_anchors,
     "assemble": cmd_assemble, "root-row": cmd_root_row, "versions": cmd_versions}[c](*a)
