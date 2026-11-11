#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""codebox_overlay.py — 피그마 벡터 슬라이드(s-fig) 위에 덱 공통 코드박스(장번호 / 라벨 / 코드)를 HTML로 덮어 씌운다.
피그마 원본의 코드(A03 등)를 고치지 않고도 덱 전체 코드 체계(B06~)로 맞출 때 사용. 서체·색이 HTML 장표와 동일해진다.

  python scripts/codebox_overlay.py <deck.html> --pages 24-35 --ch 2 --name "핵심 이슈" --start B06
  python scripts/codebox_overlay.py <deck.html> --chap "2.2 핵심 이슈 분석 (AS-IS)" --ch 2 --name "핵심 이슈" --start B06

- 이미 코드박스 오버레이가 있으면 교체한다. 위치 규격(.figcode: left 64 / top 75 / 104×117.3)은 덱 골격 CSS 에 있다.
- 번호는 지정 페이지 순서대로 start 부터 +1.
"""
import argparse, io, re, sys

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('deck'); ap.add_argument('--pages', help='예 24-35 또는 24,25,30')
    ap.add_argument('--chap', help='data-chap 값이 일치하는 슬라이드 전부')
    ap.add_argument('--ch', required=True, help='장 번호(코드박스 상단 숫자)')
    ap.add_argument('--name', required=True, help='라벨(예: 핵심 이슈)')
    ap.add_argument('--start', required=True, help='시작 코드(예: B06)')
    a = ap.parse_args()
    h = io.open(a.deck, encoding='utf-8').read()
    head_end = h.index('<section class="slide'); tail_start = h.rindex('</section>') + len('</section>')
    parts = [q for q in re.split(r'(?=<section class="slide)', h[head_end:tail_start]) if q.strip()]
    targets = set()
    if a.pages:
        for r in a.pages.split(','):
            x, _, y = r.partition('-'); targets.update(range(int(x), int(y or x) + 1))
    if a.chap:
        targets.update(i for i, s in enumerate(parts, 1) if 'data-chap="%s"' % a.chap in s[:200])
    letter, num = re.match(r'([A-Z]+)(\d+)', a.start).groups(); n = int(num); w = len(num)
    done = []
    for i in sorted(targets):
        s = parts[i - 1]
        if 's-fig' not in s[:80]:
            print('  skip p%d (s-fig 아님)' % i); continue
        code = '%s%0*d' % (letter, w, n); n += 1
        box = '<div class="codebox figcode"><div class="ch">%s</div><div class="cline"></div><div class="cname">%s</div><div class="code">%s</div></div>' % (a.ch, a.name, code)
        s = re.sub(r'<div class="codebox figcode">.*?</div></div>', '', s, flags=re.S)
        s = s.replace('<span class="figpatch">', box + '<span class="figpatch">', 1)
        parts[i - 1] = s; done.append((i, code))
    io.open(a.deck, 'w', encoding='utf-8').write(h[:head_end] + ''.join(parts) + h[tail_start:])
    print('codebox applied:', done)

if __name__ == '__main__':
    sys.exit(main())
