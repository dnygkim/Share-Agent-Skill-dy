# -*- coding: utf-8 -*-
"""im-not-ai(humanize-korean) 1차 윤문용 — 장표 문구 추출 · 되돌려 넣기

  추출:  python -X utf8 scripts/antiai_units.py extract <04_content.md | 덱.html> --project _workspace/{프로젝트}
             [--codes B02,B05] [--skip-codes X02,X03]
         → _workspace/{프로젝트}/antiai/{YYYY-MM-DD-NNN-TAG}/  01_input.txt · units.json · meta.json
           (01_input.txt = humanize-korean 의 run 폴더 입력 그대로. 한 줄 = `[NNNN] 문구`, 장표 사이 빈 줄)
  적용:  python -X utf8 scripts/antiai_units.py apply <run 폴더> [--keep 0012,0040] [--who 담당자]
             [--out 다른파일] [--dry-run] [--force]
         → 원본 제자리 갱신(직전본 *_prev.* 백업) · diff.tsv · diff.md(장표 · 전 · 후 표) · apply.json
           덱 HTML 은 <head> 수정 이력 한 줄 + revision 메타 날짜 자동 갱신

단위(unit) = 장표 텍스트 요소 하나.
  - 덱 HTML: 안쪽이 텍스트 + 인라인 태그(span · b · strong · em · i · u · small · sup · sub · mark · a · br)뿐인
    요소 중 가장 바깥 + 블록 요소에 직접 붙은 텍스트. header · footer · nav(로고 락업 · 장 pill · 쪽 번호) 제외
  - 04_content.md: `### [코드]` 장표 아래의 거버닝 · 항목 · 표 칸 · 결론 바 줄. 작업 메모 줄
    (레이아웃 · 레퍼런스 · 근거 · 비고 · 자기검증 · 출처) · 머리말 · 태그라인 제외
  - 공통 제외: 한글 6자 미만 · 「출처」로 시작 · 표지 · 목차 · 간지(divd · divider · D1 …) · --skip-codes
인라인 표식: 강조(태그 쌍 · **…**) = ⟦n⟧…⟦/n⟧, 줄바꿈 · 코드 · 링크 · 단독 태그 = ⟦n/⟧.
되돌려 넣을 때 줄마다 검증하고, 하나라도 걸리면 그 줄은 원문을 유지한다:
  표식 순서 · 수치 · 영문 토큰(고유명사 · 약어) · 새 ㅁ 명사형 어미 · --keep 지정 · 추출 뒤 원본 변경.
"""
import argparse
import datetime as dt
import hashlib
import html as H
import json
import os
import re
import secrets
import sys
from collections import Counter
from pathlib import Path

INLINE = {'span', 'b', 'strong', 'em', 'i', 'u', 'small', 'sup', 'sub', 'mark', 'a', 'br'}
VOID = {'br', 'img', 'input', 'meta', 'hr', 'source', 'wbr', 'link', 'col', 'area', 'embed', 'track', 'param'}
SKIP_TREE = {'header', 'footer', 'nav', 'script', 'style', 'svg', 'head'}
SKIP_CODES = {'표지', '목차'}
SKIP_SLIDE_CLASS = re.compile(r'\b(?:cover|divd|divider|toc)\b')
MEMO_LABELS = {'레이아웃', '레퍼런스', '근거', '비고', '자기검증', '출처', '메모', '작업 메모', '도식'}
HANG = re.compile(r'[가-힣]')
MARK = re.compile(r'⟦(/?)(\d+)(/?)⟧')
NUM = re.compile(r'\d+(?:[.,]\d+)*')
LAT = re.compile(r'[A-Za-z][A-Za-z0-9+&\-]*')
# 새로 생기면 되돌리는 ㅁ 명사형 어미(하우스 문체 금지). 명사로 굳은 말은 예외
BAD_END = re.compile(r'(?:함|됨|임|둠|씀|듦|짐|움|않음|없음|있음|같음|많음|적음|좁음|넓음|높음|낮음|늦음|짧음|작음|따름)$')
NOUN_OK = re.compile(r'(?:도움|싸움|배움|다음|처음|마음|이음|모음|걸음|믿음|물음|울음|웃음|얼음|죽음|젊음|그림|느낌|기쁨|아픔|슬픔)$')
TRAIL = re.compile(r'[\s.。…!?)\]」』"\'’”]+$')


def plain(t):
    return MARK.sub('', t)


def hangul(t):
    return len(HANG.findall(t))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ───────────────────────── 덱 HTML ─────────────────────────

def _mask(t):
    for pat in (r'<!--.*?-->', r'<style\b.*?</style>', r'<script\b.*?</script>', r'<svg\b.*?</svg>', r'<head\b.*?</head>'):
        t = re.sub(pat, lambda m: ' ' * len(m.group(0)), t, flags=re.S | re.I)
    return t


def _attr(tag, name):
    m = re.search(r'\b' + name + r'="([^"]*)"', tag)
    return m.group(1) if m else ''


def extract_html(s, codes, skip_codes):
    m = _mask(s)
    secs = [(x.start(), x.group(0)) for x in re.finditer(r'<section\b[^>]*class="[^"]*\bslide\b[^"]*"[^>]*>', s)]
    toks = [(x.start(), x.end(), x.group(0)) for x in re.finditer(r'<[^>]+>', m)]
    root = {'name': '#root', 'kids': [], 'parent': None}
    cur, nodes, pos = root, [], 0

    def addtext(a, b):
        if b > a and m[a:b].strip():
            cur['kids'].append({'text': True, 'a': a, 'b': b})

    for a, b, t in toks:
        addtext(pos, a)
        pos = b
        nm = re.match(r'</?\s*([a-zA-Z0-9]+)', t)
        if not nm:
            continue
        name = nm.group(1).lower()
        if t.startswith('</'):
            p = cur
            while p is not root and p['name'] != name:
                p = p['parent']
            if p is not root:
                p['ce'] = (a, b)
                cur = p['parent']
            continue
        el = {'name': name, 'oa': a, 'ob': b, 'tag': t, 'kids': [], 'parent': cur}
        cur['kids'].append(el)
        nodes.append(el)
        if name not in VOID and not t.endswith('/>'):
            cur = el
    addtext(pos, len(m))

    memo = {}

    def inline_only(el):
        k = id(el)
        if k in memo:
            return memo[k]
        ok = 'ce' in el or el['name'] in VOID
        if ok:
            for c in el['kids']:
                if c.get('text'):
                    continue
                if c['name'] not in INLINE or not inline_only(c):
                    ok = False
                    break
        memo[k] = ok
        return ok

    def skipped_tree(el):
        p = el
        while p is not None and p is not root:
            if p['name'] in SKIP_TREE:
                return True
            p = p['parent']
        return False

    def slide_of(p):
        lo = None
        for i, (at, _) in enumerate(secs):
            if at <= p:
                lo = i
            else:
                break
        return lo

    def slide_ok(i):
        if i is None:
            return None
        stag = secs[i][1]
        code = _attr(stag, 'data-code')
        if code in skip_codes or SKIP_SLIDE_CLASS.search(_attr(stag, 'class')) or re.fullmatch(r'D\d+', code):
            return None
        if codes and code not in codes:
            return None
        return code

    units = []

    def sentence_like(txt):
        if re.search(r'⟦/\d+⟧\s*⟦\d+⟧', txt):
            return False                      # 블록처럼 쓰인 span 나열
        outside = re.sub(r'⟦(\d+)⟧.*?⟦/\1⟧', '', txt)
        return hangul(outside) >= 4

    def add_unit(a, b, el_name, cls, tags, txt):
        p = plain(txt)
        if hangul(p) < 6 or (not tags and len(p) < 20) or (tags and len(p) < 12) or p.startswith('출처'):
            return
        i = slide_of(a)
        code = slide_ok(i)
        if code is None:
            return
        units.append({'id': 0, 'slide': i + 1, 'code': code, 'a': a, 'b': b, 'el': el_name, 'cls': cls,
                      'tags': tags, 'text': txt, 'orig': s[a:b]})

    def make(el):
        a, b = el['ob'], el['ce'][0]
        tags, out, cnt = [], [], [0]

        def walk(e):
            for c in e['kids']:
                if c.get('text'):
                    out.append(re.sub(r'\s+', ' ', H.unescape(s[c['a']:c['b']])))
                elif c['name'] in VOID:
                    cnt[0] += 1
                    tags.append(c['tag'])
                    out.append(f'⟦{cnt[0]}/⟧')
                else:
                    cnt[0] += 1
                    n = cnt[0]
                    tags.append(c['tag'])
                    out.append(f'⟦{n}⟧')
                    walk(c)
                    out.append(f'⟦/{n}⟧')
                    tags.append(s[c['ce'][0]:c['ce'][1]])
        walk(el)
        txt = ''.join(out).strip()
        if tags and re.search(r'⟦\d+⟧', txt) and not sentence_like(txt):
            return False                      # 블록 묶음 → 자식으로 내려감
        add_unit(a, b, el['name'], _attr(el['tag'], 'class'), tags, txt)
        return True

    def consider(el):
        raw = s[el['ob']:el['ce'][0]]
        if re.search(r'<(svg|img|video|iframe|canvas)\b', raw, re.I) or not make(el):
            for c in el['kids']:
                if not c.get('text') and c['name'] not in VOID and 'ce' in c:
                    consider(c)

    for el in nodes:
        if el['name'] in VOID or 'ce' not in el or skipped_tree(el):
            continue
        if inline_only(el):
            par = el['parent']
            if par is not root and inline_only(par):
                continue
            consider(el)
        else:
            # 블록 요소에 직접 붙은 텍스트(인라인 요소 밖) — 섞인 내용의 맨글
            for c in el['kids']:
                if c.get('text'):
                    raw = s[c['a']:c['b']]
                    lead = len(raw) - len(raw.lstrip())
                    trail = len(raw) - len(raw.rstrip())
                    a, b = c['a'] + lead, c['b'] - trail
                    add_unit(a, b, '#text', '', [], re.sub(r'\s+', ' ', H.unescape(s[a:b])))
    units.sort(key=lambda u: u['a'])
    return units


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


# ───────────────────────── 04_content.md ─────────────────────────

MD_TOKEN = re.compile(r'`[^`]+`|\[[^\]]*\]\([^)]*\)|<br\s*/?>|<[^>]+>|\*\*')


def md_mark(body):
    """본문 → (표식 문자열, 원래 토큰 목록). ** 쌍 = 강조, 나머지 토큰 = 단독 표식."""
    toks = list(MD_TOKEN.finditer(body))
    pairs = [t for t in toks if t.group(0) == '**']
    paired_ok = len(pairs) % 2 == 0
    out, tags, pos, n, stack = [], [], 0, 0, []
    for t in toks:
        out.append(body[pos:t.start()])
        pos = t.end()
        g = t.group(0)
        if g == '**' and paired_ok:
            if stack:
                out.append(f'⟦/{stack.pop()}⟧')
            else:
                n += 1
                stack.append(n)
                out.append(f'⟦{n}⟧')
            tags.append(g)
        else:
            n += 1
            out.append(f'⟦{n}/⟧')
            tags.append(g)
    out.append(body[pos:])
    return ''.join(out), tags


def md_cells(line):
    """표 줄 → 칸 (시작, 끝) 목록(앞뒤 공백 제외)."""
    bars = [i for i, ch in enumerate(line) if ch == '|' and (i == 0 or line[i - 1] != '\\')]
    spans = []
    for k in range(len(bars) - 1):
        a, b = bars[k] + 1, bars[k + 1]
        seg = line[a:b]
        lead = len(seg) - len(seg.lstrip())
        trail = len(seg) - len(seg.rstrip())
        if b - trail > a + lead:
            spans.append((a + lead, b - trail))
    return spans


LABEL = re.compile(r'^(\*{0,2}([^:：*\[\]`]{1,12}?)\*{0,2}\s*[:：]\s*)')


def extract_md(s, codes, skip_codes):
    lines = s.split('\n')
    units = []
    slide_no, code, active = 0, None, False
    fence = comment = False
    for li, raw in enumerate(lines):
        line = raw[:-1] if raw.endswith('\r') else raw
        st = line.strip()
        if st.startswith('```'):
            fence = not fence
            continue
        if fence:
            continue
        if comment:
            if '-->' in st:
                comment = False
            continue
        if st.startswith('<!--'):
            comment = '-->' not in st
            continue
        h = re.match(r'^(#{1,6})\s+(.*)$', line)
        if h:
            hm = re.match(r'^\[([^\]]+)\]\s*(.*)$', h.group(2).strip())
            if len(h.group(1)) >= 3 and hm:
                slide_no += 1
                code = hm.group(1).strip()
                title = hm.group(2)
                active = not (code in skip_codes or re.fullmatch(r'D\d+', code)
                              or re.search(r'표지|목차|간지', code + ' ' + title)
                              or (codes and code not in codes))
            elif len(h.group(1)) <= 2:
                active = False
            continue
        if not active or not st:
            continue
        spans = []
        if st.startswith('|'):
            if re.fullmatch(r'\|?[\s:|-]+\|?', st):
                continue
            spans = md_cells(line)
        else:
            mm = re.match(r'^(\s*(?:[-*+]|\d+[.)])\s+|\s*>\s*|\s*)(.*)$', line)
            a = len(mm.group(1))
            body = mm.group(2)
            lab = LABEL.match(body)
            if lab:
                if lab.group(2).strip() in MEMO_LABELS:
                    continue
                a += len(lab.group(1))
            b = len(line.rstrip())
            if b > a:
                spans = [(a, b)]
        for a, b in spans:
            body = line[a:b]
            txt, tags = md_mark(body)
            p = plain(txt)
            if hangul(p) < 6 or p.strip().startswith('출처'):
                continue
            units.append({'id': 0, 'slide': slide_no, 'code': code, 'line': li, 'a': a, 'b': b,
                          'tags': tags, 'text': txt, 'orig': body})
    return units


# ───────────────────────── 공통 ─────────────────────────

def rebuild(u, txt, kind):
    if MARK.findall(txt) != MARK.findall(u['text']):
        return None
    parts = re.split(r'(⟦/?\d+/?⟧)', txt)
    out, k = [], 0
    for p in parts:
        if MARK.fullmatch(p):
            out.append(u['tags'][k])
            k += 1
        else:
            out.append(esc(p) if kind == 'html' else p)
    return ''.join(out)


def show(u, txt, kind):
    """보고용 글자 — 태그를 걷고 줄바꿈은 ' / '."""
    r = rebuild(u, txt, kind)
    if r is None:
        r = plain(txt)
    if kind == 'html':
        r = re.sub(r'<br\s*/?>', ' / ', r, flags=re.I)
        r = H.unescape(re.sub(r'<[^>]+>', '', r))
    else:
        r = re.sub(r'<br\s*/?>', ' / ', r, flags=re.I)
    return re.sub(r'\s+', ' ', r).strip().replace('|', '\\|')


def endings(t):
    t = re.sub(r'⟦/?\d+⟧', '', t)
    segs = [TRAIL.sub('', x) for x in re.split(r'⟦\d+/⟧', t)]
    return sum(1 for x in segs if BAD_END.search(x) and not NOUN_OK.search(x))


def check(before, after, keep):
    if keep:
        return '확정 · 지정 유지'
    if MARK.findall(after) != MARK.findall(before):
        return '표식 순서'
    if Counter(NUM.findall(plain(before))) != Counter(NUM.findall(plain(after))):
        return '수치'
    if Counter(LAT.findall(plain(before))) != Counter(LAT.findall(plain(after))):
        return '영문 토큰'
    if endings(after) > endings(before):
        return 'ㅁ 명사형 어미'
    if not plain(after).strip():
        return '빈 줄'
    return ''


def new_run_dir(project):
    base = Path(project) / 'antiai'
    base.mkdir(parents=True, exist_ok=True)
    day = dt.date.today().isoformat()
    nums = [int(m.group(1)) for p in base.iterdir()
            if (m := re.match(re.escape(day) + r'-(\d{3})', p.name))]
    run = base / f'{day}-{(max(nums) + 1 if nums else 1):03d}-{secrets.token_hex(2)}'
    run.mkdir()
    return run


def split_codes(v):
    return {c.strip() for c in (v or '').split(',') if c.strip()}


def cmd_extract(a):
    src = Path(a.source).resolve()
    s = src.read_text(encoding='utf-8')
    kind = 'html' if src.suffix.lower() in ('.html', '.htm') else 'md'
    codes = split_codes(a.codes)
    skip = SKIP_CODES | split_codes(a.skip_codes)
    units = (extract_html if kind == 'html' else extract_md)(s, codes, skip)
    for k, u in enumerate(units):
        u['id'] = k + 1
    run = new_run_dir(a.project)
    lines, cur = [], None
    for u in units:
        if u['slide'] != cur:
            if cur is not None:
                lines.append('')
            cur = u['slide']
        lines.append(f"[{u['id']:04d}] {u['text']}")
    (run / '01_input.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    (run / 'units.json').write_text(json.dumps(units, ensure_ascii=False), encoding='utf-8')
    meta = {'source': str(src), 'kind': kind, 'sha256': sha(src), 'run_id': run.name,
            'created': dt.datetime.now().isoformat(timespec='seconds'),
            'codes': sorted(codes), 'skip_codes': sorted(skip), 'units': len(units)}
    (run / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding='utf-8')
    n = sum(len(plain(u['text'])) for u in units)
    print(f"{len(units)} units · {n} chars · {len({u['slide'] for u in units})} slides · "
          f"{sum(1 for u in units if u['tags'])} with markers")
    print(f'RUN_DIR={run}')


def add_revision(s, who, codes, note):
    today = dt.date.today().strftime('%Y%m%d')
    s = re.sub(r'(<meta name="revision" content=")[^"]*(")', r'\g<1>' + today + r'\g<2>', s, count=1)
    m = re.search(r'<!--\s*═+\s*수정 이력.*?-->', s, re.S)
    if not m:
        return s
    block = m.group(0)
    line = f'[{today}] {who} · 수정 페이지: {" · ".join(codes)} · 내역: {note}\n'
    first = re.search(r'^\[\d{8}\]', block, re.M)
    pos = m.start() + (first.start() if first else block.rfind('-->'))
    return s[:pos] + line + s[pos:]


def cmd_apply(a):
    run = Path(a.run_dir)
    meta = json.loads((run / 'meta.json').read_text(encoding='utf-8'))
    units = {u['id']: u for u in json.loads((run / 'units.json').read_text(encoding='utf-8'))}
    kind, src = meta['kind'], Path(meta['source'])
    if sha(src) != meta['sha256'] and not a.force:
        sys.exit(f'원본이 추출 뒤 바뀜: {src}\n→ 다시 extract 하거나, 바뀐 줄을 건너뛰려면 --force')
    fin = run / 'final.md'
    t = re.sub(r'<!--\s*HUMANIZE-SUMMARY.*?-->', '', fin.read_text(encoding='utf-8'), flags=re.S)
    new = {}
    for ln in t.splitlines():
        mm = re.match(r'^\[(\d{4})\]\s?(.*)$', ln.strip())
        if mm:
            new[int(mm.group(1))] = mm.group(2).strip()
    extra = sorted(i for i in new if i not in units)
    missing = sorted(i for i in units if i not in new)
    keep = {int(x) for x in split_codes(a.keep)}
    s = src.read_text(encoding='utf-8', newline='') if kind == 'md' else src.read_text(encoding='utf-8')
    lines = s.split('\n') if kind == 'md' else None

    def cur_text(u):
        if kind == 'html':
            return s[u['a']:u['b']]
        ln = lines[u['line']]
        ln = ln[:-1] if ln.endswith('\r') else ln
        return ln[u['a']:u['b']]

    changed, held = [], []
    for i, u in sorted(units.items()):
        nt = new.get(i)
        if nt is None or nt == u['text']:
            continue
        why = check(u['text'], nt, i in keep)
        if not why and cur_text(u) != u['orig']:
            why = '원본 변경'
        if why:
            held.append((u, nt, why))
            continue
        changed.append((u, nt, rebuild(u, nt, kind)))

    if not a.dry_run and changed:
        if kind == 'html':
            for u, _, hn in sorted(changed, key=lambda c: -c[0]['a']):
                s = s[:u['a']] + hn + s[u['b']:]
            codes = list(dict.fromkeys(u['code'] for u, _, _ in sorted(changed, key=lambda c: c[0]['a'])))
            note = (f"im-not-ai 1차 윤문(humanize-korean · run {meta['run_id']}) {len(changed)}줄 문체 교정"
                    + (f", 자동 원문 유지 {len(held)}줄" if held else ''))
            s = add_revision(s, a.who, codes, note)
        else:
            for u, _, mn in sorted(changed, key=lambda c: (c[0]['line'], -c[0]['a'])):
                ln = lines[u['line']]
                cr = ln.endswith('\r')
                body = ln[:-1] if cr else ln
                lines[u['line']] = body[:u['a']] + mn + body[u['b']:] + ('\r' if cr else '')
            s = '\n'.join(lines)
        out = Path(a.out) if a.out else src
        if out == src:
            prev = src.with_name(src.stem + '_prev' + src.suffix)
            prev.write_bytes(src.read_bytes())
        out.write_text(s, encoding='utf-8', newline='')

    with open(run / 'diff.tsv', 'w', encoding='utf-8', newline='\n') as f:
        f.write('id\tslide\tcode\tbefore\tafter\tresult\n')
        for u, nt, why in sorted([(c[0], c[1], '') for c in changed] + held, key=lambda c: c[0]['id']):
            f.write(f"{u['id']}\t{u['slide']}\t{u['code']}\t{u['text']}\t{nt}\t{why or '반영'}\n")
    md = [f"# im-not-ai 1차 윤문 결과 — {src.name}", '',
          f"- run: `{meta['run_id']}` · 대상 {len(units)}줄 · 교정 {len(changed)}줄 · 자동 원문 유지 {len(held)}줄"
          + (' · **dry-run(원본 미반영)**' if a.dry_run else ''), '']
    if changed:
        md += ['## 교정', '', '| 장표 | 전 | 후 |', '|---|---|---|']
        md += [f"| {u['code']} | {show(u, u['text'], kind)} | {show(u, nt, kind)} |"
               for u, nt, _ in sorted(changed, key=lambda c: c[0]['id'])]
        md.append('')
    if held:
        md += ['## 자동 원문 유지 (윤문안을 반영하지 않은 줄)', '', '| 장표 | ID | 사유 | 원문 | 윤문안 |', '|---|---|---|---|---|']
        md += [f"| {u['code']} | {u['id']:04d} | {why} | {show(u, u['text'], kind)} | {show(u, nt, kind) if why != '표식 순서' else plain(nt).replace('|', '/')} |"
               for u, nt, why in held]
        md.append('')
    (run / 'diff.md').write_text('\n'.join(md), encoding='utf-8', newline='\n')
    summary = {'source': str(src), 'out': str(Path(a.out) if a.out else src), 'dry_run': a.dry_run,
               'units': len(units), 'changed': len(changed),
               'held': Counter(w for _, _, w in held), 'missing_in_final': len(missing), 'extra_ids': extra}
    (run / 'apply.json').write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f"changed {len(changed)} of {len(units)} · 원문 유지 {len(held)} {dict(summary['held'])}"
          + (f" · final 에 없는 ID {len(missing)}" if missing else '')
          + (f" · 모르는 ID {extra[:5]}" if extra else '')
          + (' · dry-run' if a.dry_run else ''))
    print(f"report: {run / 'diff.md'}")


def main():
    ap = argparse.ArgumentParser(description='im-not-ai 1차 윤문용 추출 · 되돌려 넣기')
    sub = ap.add_subparsers(dest='cmd', required=True)
    e = sub.add_parser('extract')
    e.add_argument('source')
    e.add_argument('--project', required=True, help='_workspace/{프로젝트} — run 폴더가 그 아래 antiai/ 에 생김')
    e.add_argument('--codes', help='이 장표 코드만(쉼표) — S6 변경 장표')
    e.add_argument('--skip-codes', help='더 뺄 장표 코드(쉼표) — 조견표 등')
    p = sub.add_parser('apply')
    p.add_argument('run_dir')
    p.add_argument('--keep', help='원문 유지할 ID(쉼표) — 사용자 확정 · 컨셉 문장')
    p.add_argument('--who', default='담당자', help='수정 이력 담당자(덱 HTML)')
    p.add_argument('--out', help='원본 대신 쓸 파일')
    p.add_argument('--dry-run', action='store_true', help='원본은 그대로, 보고서만')
    p.add_argument('--force', action='store_true', help='추출 뒤 원본이 바뀌어도 진행(바뀐 줄은 원문 유지)')
    a = ap.parse_args()
    (cmd_extract if a.cmd == 'extract' else cmd_apply)(a)


if __name__ == '__main__':
    main()
