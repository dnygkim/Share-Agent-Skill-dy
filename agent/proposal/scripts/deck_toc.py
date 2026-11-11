#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""deck_toc.py — HTML 덱에서 목차(페이지·장·절·코드·태그라인·거버닝 메시지·유형)를 추출해 xlsx 시트 / 마크다운으로 만든다.

  python scripts/deck_toc.py <deck.html> --xlsx <목차.xlsx> [--sheet 목차_YYMMDD] [--titles titles.json] [--md out.md]

- HTML 장표: crumb(장·절)·codebox(code)·tagline·bigtitle 자동 추출. 표지(cover)는 '간지'.
- 피그마 벡터 장표(s-fig)는 텍스트가 패스라 자동 추출 불가 → --titles JSON {"24": ["B06", "태그라인", "제목"], ...} 로 보완
  (피그마 프레임 텍스트를 use_figma 로 읽거나 렌더 PNG 를 보고 옮겨 적는다)
- --xlsx 가 기존 파일이면 시트를 첫 탭으로 추가(같은 이름 시트는 교체), 없으면 새로 만든다.
  구글 드라이브의 xlsx 는 로컬 동기화 경로를 직접 수정해야 같은 파일 ID 로 반영된다(Drive MCP 는 내용 갱신 불가).
의존: openpyxl (--xlsx 사용 시)
"""
import argparse, html as H, io, json, re, sys

def extract(path, titles):
    h = io.open(path, encoding='utf-8').read()
    head_end = h.index('<section class="slide'); tail_start = h.rindex('</section>') + len('</section>')
    parts = [q for q in re.split(r'(?=<section class="slide)', h[head_end:tail_start]) if q.strip()]
    rows = []
    for i, s in enumerate(parts, 1):
        cls = s[:80].split('"')[1]
        g = lambda pat: (re.search(pat, s, re.S) or [None, ''])[1]
        strip = lambda t: re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]+>', ' ', t))).strip()
        crumb = strip(g(r'class="crumb">(.*?)</div>')); ch, _, sec = [x.strip() for x in crumb.partition('—')]
        chap = g(r'data-chap="([^"]*)"')
        kind = '간지(챕터 표지)' if 'cover' in cls else ('발표용 HTML(iframe)' if 's-emb' in cls else ('피그마 벡터(SVG)' if 's-fig' in cls else 'HTML 장표'))
        code = g(r'class="code">([A-Z]\d+)<'); tag = strip(g(r'class="tagline">(.*?)</div>')); title = strip(g(r'class="bigtitle">(.*?)</div>')) or strip(g(r'class="ct3"[^>]*>(.*?)</div>'))
        if 'cover' in cls: code = '간지'; ch = ch or crumb
        t = titles.get(str(i))
        if t:
            code, tag, title = (t + ['', '', ''])[:3]
            if not ch: ch = chap.split(' ')[0] if chap else ''
            if not sec: sec = chap
        rows.append([i, ch, sec, code, tag, title, kind, ''])
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('deck'); ap.add_argument('--xlsx'); ap.add_argument('--sheet', default='목차(HTML기준)')
    ap.add_argument('--titles'); ap.add_argument('--md')
    a = ap.parse_args()
    titles = json.load(open(a.titles)) if a.titles else {}
    rows = extract(a.deck, titles)
    hdr = ['페이지', '장(챕터)', '절(섹션)', '코드', '소제목(태그라인)', '장표 제목(거버닝 메시지)', '유형', '비고']
    if a.md:
        with io.open(a.md, 'w', encoding='utf-8') as f:
            f.write('| ' + ' | '.join(hdr) + ' |\n|' + '---|' * len(hdr) + '\n')
            for r in rows: f.write('| ' + ' | '.join(str(x) for x in r) + ' |\n')
        print('md ->', a.md)
    if a.xlsx:
        import os, openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
        wb = openpyxl.load_workbook(a.xlsx) if os.path.exists(a.xlsx) else openpyxl.Workbook()
        if not os.path.exists(a.xlsx): wb.remove(wb.active)
        if a.sheet in wb.sheetnames: del wb[a.sheet]
        ws = wb.create_sheet(a.sheet, 0); ws.append(hdr)
        for r in rows: ws.append(r)
        thin = Side(style='thin', color='BFBFBF'); bd = Border(left=thin, right=thin, top=thin, bottom=thin)
        hf = Font(name='Malgun Gothic', size=11, bold=True); bf = Font(name='Malgun Gothic', size=10); cf = Font(name='Malgun Gothic', size=10, bold=True, color='FFFFFF')
        for c in ws[1]: c.font = hf; c.fill = PatternFill('solid', fgColor='D8D8D8'); c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True); c.border = bd
        for i, r in enumerate(rows, start=2):
            for j, c in enumerate(ws[i], start=1):
                c.font = bf; c.border = bd; c.alignment = Alignment(horizontal='center' if j in (1, 4, 7) else 'left', vertical='center', wrap_text=True)
            if r[3] == '간지':
                for c in ws[i]: c.font = cf; c.fill = PatternFill('solid', fgColor='1E2836')
            elif r[6] != 'HTML 장표':
                for c in ws[i]: c.fill = PatternFill('solid', fgColor='EAF2FB')
        for k, w in enumerate([7, 20, 30, 7, 48, 62, 16, 48], start=1): ws.column_dimensions[get_column_letter(k)].width = w
        ws.freeze_panes = 'A2'; ws.auto_filter.ref = 'A1:H%d' % (len(rows) + 1); wb.active = 0
        wb.save(a.xlsx); print('xlsx ->', a.xlsx, 'sheet', a.sheet, len(rows), 'rows')
    if not a.md and not a.xlsx:
        for r in rows: print(r)

if __name__ == '__main__':
    sys.exit(main())
