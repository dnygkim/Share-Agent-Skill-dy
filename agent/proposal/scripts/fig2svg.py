#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fig2svg.py — 피그마 PDF export → 덱에 바로 삽입 가능한 벡터 슬라이드(<section class="slide s-fig">) 묶음.

  python scripts/fig2svg.py --prefix i --part 2 --chap "2.2 핵심 이슈 분석" --out ins.html 01.pdf 02.pdf ...

절차(GS칼텍스 2026-09 검증): Figma MCP download_assets(defaultFormat="pdf") → curl 즉시 저장(URL 단명)
→ 이 스크립트 → deck_edit.py insert/replace. 텍스트는 패스로 변환(text_as_path)되어 서체 의존이 없고 선명도는 벡터.
- 드롭섀도 프레임은 export 페이지가 1700×1000 등으로 커지고 3400×2000 그림자 래스터가 들어감 → 3000px 이상 이미지 제거 + 흰 1600×900 사각형 위치로 cropbox 자동 검출
- PyMuPDF SVG의 <mask> 내부 path 는 fill 이 없어 크롬에서 검게 마스킹됨 → fill="#ffffff" 주입
- 인라인 SVG 여러 장은 id 충돌 → --prefix 로 id/url(#)/href 네임스페이스(장별 iNN_)
- 피그마 쪽 페이지 번호(예: 00)는 .figpatch(흰 패치)로 가리고 .figpg 에 덱 번호를 얹는다(번호는 deck_edit.py 가 재부여)
의존: PyMuPDF (`python3 -m pip install --user pymupdf`)
"""
import argparse, io, os, re, sys

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--prefix', default='f', help='SVG id 접두(장별 <prefix>NN_)')
    ap.add_argument('--part', default='3', help='data-part 값(장 번호)')
    ap.add_argument('--chap', default='', help='data-chap 값')
    ap.add_argument('--out', required=True)
    ap.add_argument('--width', type=int, default=1600); ap.add_argument('--height', type=int, default=900)
    ap.add_argument('pdfs', nargs='+')
    a = ap.parse_args()
    import fitz
    W, Hh = a.width, a.height
    HEAD = '<svg class="figsvg" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, Hh, W, Hh)
    secs = []
    for k, f in enumerate(a.pdfs, 1):
        d = fitz.open(f); p = d[0]
        for x in p.get_images(full=True):
            if x[2] >= 3000: p.delete_image(x[0])
        fr = None
        for dr in p.get_drawings():
            r = dr['rect']
            if dr.get('fill') and abs(r.width - W) < 1 and abs(r.height - Hh) < 1: fr = r; break
        if fr and (fr.x0 or fr.y0): p.set_cropbox(fitz.Rect(fr.x0, fr.y0, fr.x0 + W, fr.y0 + Hh))
        svg = p.get_svg_image(text_as_path=True)
        m = re.search(r'<svg[^>]*>', svg); tag = m.group(0)
        vb = re.search(r'viewBox="([^"]+)"', tag).group(1)
        if vb.split()[2:] != [str(W), str(Hh)]:
            print('[경고] %s viewBox=%s (기대 %dx%d)' % (f, vb, W, Hh))
        body = svg[m.end():svg.rindex('</svg>')]
        pid = '%s%02d_' % (a.prefix, k)
        body = re.sub(r'id="([^"]+)"', lambda mm: 'id="%s%s"' % (pid, mm.group(1)), body)
        body = re.sub(r'url\(#([^)]+)\)', lambda mm: 'url(#%s%s)' % (pid, mm.group(1)), body)
        body = re.sub(r'(xlink:href|href)="#([^"]+)"', lambda mm: '%s="#%s%s"' % (mm.group(1), pid, mm.group(2)), body)
        body = re.sub(r'<mask\b.*?</mask>', lambda mm: re.sub(r'<path(?![^>]*\bfill=)', '<path fill="#ffffff"', mm.group(0)), body, flags=re.S)
        body = re.sub(r'(\d+\.\d{4,})', lambda mm: ('%.3f' % float(mm.group(1))).rstrip('0').rstrip('.'), body)
        secs.append('<section class="slide s-fig" data-part="%s" data-chap="%s">\n%s%s</svg> \n  <span class="figpatch"></span><span class="pg figpg" style="top:865px">0</span>\n</section>\n\n' % (a.part, a.chap, HEAD, body))
        print(os.path.basename(f), 'crop', fr, 'svg %.1fMB' % (len(secs[-1]) / 1e6))
    io.open(a.out, 'w', encoding='utf-8').write(''.join(secs))
    print('wrote', a.out, '%.1fMB' % (os.path.getsize(a.out) / 1e6), '·', len(secs), 'slides')

if __name__ == '__main__':
    sys.exit(main())
