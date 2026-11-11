#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""deck_edit.py — 1600×900 / 1280×720 HTML 덱(section.slide 나열형)의 페이지 편집 도구.

  python scripts/deck_edit.py <deck.html> list                      # 페이지 목록(번호·클래스·data-chap·코드·제목)
  python scripts/deck_edit.py <deck.html> delete 24 37-46           # 페이지 삭제 후 1..N 재번호
  python scripts/deck_edit.py <deck.html> insert 24 <sections.html> # 해당 위치에 섹션 묶음 삽입 후 재번호
  python scripts/deck_edit.py <deck.html> replace 37-46 <sections.html>  # 범위 삭제 + 같은 자리에 삽입

재번호 대상(모두 자동): <span class="pg">N</span> · class="pg figpg" …>N< · iframe srcdoc 안의 &lt;b&gt;NN&lt;/b&gt;
원본은 덮어쓰기 전 <deck>_prev.html 로 1개 롤링 백업한다(--no-backup 으로 끔).
"""
import io, os, re, sys, shutil

def split_deck(h):
    head_end = h.index('<section class="slide')
    tail_start = h.rindex('</section>') + len('</section>')
    parts = [q for q in re.split(r'(?=<section class="slide)', h[head_end:tail_start]) if q.strip()]
    return h[:head_end], parts, h[tail_start:]

def page_no(s):
    m = re.search(r'(?:<span class="pg">|class="pg figpg" style="top:865px">)(\d+)<', s) or re.search(r'&lt;b&gt;(\d{2})&lt;/b&gt;', s)
    return int(m.group(1)) if m else None

def renum(p, n):
    p, c1 = re.subn(r'(<span class="pg">)\d+(</span>)', lambda m: m.group(1) + str(n) + m.group(2), p)
    p, c2 = re.subn(r'(class="pg figpg" style="top:865px">)\d+(<)', lambda m: m.group(1) + str(n) + m.group(2), p)
    p, c3 = re.subn(r'(&lt;b&gt;)\d{2}(&lt;/b&gt;)', lambda m: m.group(1) + '%02d' % n + m.group(2), p)
    if c1 + c2 + c3 == 0:
        print('  [경고] %d번째 슬라이드에서 페이지 번호 요소를 찾지 못함' % n)
    return p

def parse_ranges(args):
    out = set()
    for r in args:
        a, _, b = r.partition('-')
        out.update(range(int(a), int(b or a) + 1))
    return out

def describe(i, s):
    cls = s[:80].split('"')[1]
    chap = (re.search(r'data-chap="([^"]*)"', s) or [None, ''])[1]
    code = (re.search(r'class="code">([A-Z]\d+)<', s) or [None, ''])[1]
    title = re.sub(r'<[^>]+>', '', (re.search(r'class="bigtitle">(.*?)</div>', s, re.S) or [None, ''])[1]).strip()
    return '%3d | %-22s | %-32s | %-4s | %s' % (i, cls[:22], chap[:32], code, title[:50])

def main():
    if len(sys.argv) < 3:
        print(__doc__); return 2
    path, cmd = sys.argv[1], sys.argv[2]
    h = io.open(path, encoding='utf-8').read()
    head, parts, tail = split_deck(h)
    if cmd == 'list':
        for i, s in enumerate(parts, 1): print(describe(i, s))
        print('total', len(parts)); return 0
    backup = '--no-backup' not in sys.argv
    args = [a for a in sys.argv[3:] if not a.startswith('--')]
    if cmd == 'delete':
        kill = parse_ranges(args)
        parts = [p for i, p in enumerate(parts, 1) if i not in kill]
        print('delete', sorted(kill))
    elif cmd == 'insert':
        at = int(args[0]); new = [q for q in re.split(r'(?=<section class="slide)', io.open(args[1], encoding='utf-8').read()) if q.strip()]
        parts = parts[:at - 1] + new + parts[at - 1:]
        print('insert', len(new), 'slides at', at)
    elif cmd == 'replace':
        kill = sorted(parse_ranges([args[0]])); at = kill[0]
        new = [q for q in re.split(r'(?=<section class="slide)', io.open(args[1], encoding='utf-8').read()) if q.strip()]
        parts = [p for i, p in enumerate(parts, 1) if i not in kill]
        parts = parts[:at - 1] + new + parts[at - 1:]
        print('replace', kill, 'with', len(new), 'slides')
    else:
        print('unknown command', cmd); return 2
    parts = [renum(p, n) for n, p in enumerate(parts, 1)]
    if backup:
        b = re.sub(r'\.html$', '_prev.html', path); shutil.copy2(path, b); print('backup ->', os.path.basename(b))
    io.open(path, 'w', encoding='utf-8').write(head + ''.join(parts) + tail)
    seq = [page_no(p) for p in parts]
    print('now', len(parts), 'slides · numbering', 'OK' if seq == list(range(1, len(parts) + 1)) else 'BROKEN %s' % seq)
    return 0

if __name__ == '__main__':
    sys.exit(main())
