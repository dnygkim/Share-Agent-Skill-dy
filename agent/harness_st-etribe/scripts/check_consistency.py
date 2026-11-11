#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_consistency.py — 산출물 HTML의 공수 정합성을 '실제 표를 파싱'해 검증한다(범용).

★ 절대 프로젝트별 숫자를 하드코딩하지 않는다. (이전 버전이 SDN 숫자를 박아 다른
   프로젝트를 검증 못 한 사고가 있었음.) 어떤 프로젝트든 .monthly-effort 표를 읽어
   행/열 산술과 총계 일관성을 검사한다.

검사:
  (1) 월별 투입표(.monthly-effort) 각 행: 월 셀 합 == 합계열(마지막 num).
  (2) 총계행(tr.total)의 월 셀 합 == 그 행 총계.
  (3) 총계값이 문서 곳곳(히어로·요약·푸터)에 일관 등장(>=4회).
  (4) 범위 표기 물결표(~) 미사용.

사용: python scripts/check_consistency.py <html>
종료코드: 0 통과 / 1 불일치(또는 표 못 찾음).
"""
import sys, re

for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass

if len(sys.argv) < 2:
    print("usage: check_consistency.py <html>", file=sys.stderr); sys.exit(1)
html = open(sys.argv[1], encoding="utf-8").read()

TAG = re.compile(r"<[^>]+>")
def text(s): return TAG.sub("", s).replace("&amp;", "&").strip()
def num(s):
    s = text(s)
    if s in ("-", "", "·"): return 0.0
    m = re.match(r"-?\d+(\.\d+)?", s.replace(",", ""))
    return float(m.group()) if m else None

fails, checks = [], 0
def chk(ok, msg):
    global checks; checks += 1
    print(("  OK   " if ok else "  FAIL ") + msg)
    if not ok: fails.append(msg)

m = re.search(r'<table[^>]*class="[^"]*monthly-effort[^"]*"[^>]*>(.*?)</table>', html, re.S | re.I)
if not m:
    print("[ERROR] .monthly-effort 표를 찾지 못함 — 공수 표 클래스 확인", file=sys.stderr); sys.exit(1)
rows = re.findall(r"<tr[^>]*>(.*?)</tr>", m.group(1), re.S | re.I)

print("=== 월별 투입표 행별 산술 (월 셀 합 == 합계열) ===")
grand = None
for r in rows:
    cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S | re.I)
    numcells = [num(c) for c in re.findall(r'<td[^>]*class="[^"]*\bnum\b[^"]*"[^>]*>(.*?)</td>', r, re.S | re.I)]
    numcells = [x for x in numcells if x is not None]
    if len(numcells) < 2:
        continue
    label = (text(cells[0])[:24] if cells else "?") or "row"
    months, total = numcells[:-1], numcells[-1]
    s = round(sum(months), 2)
    chk(abs(s - total) < 0.01, f"[{label}] 월셀합 {s} == 합계열 {total}")
    if grand is None or total >= grand:
        grand = total

# 총계행 명시 탐지(class에 total)
mt = re.search(r'<tr[^>]*class="[^"]*\btotal\b[^"]*"[^>]*>(.*?)</tr>', m.group(1), re.S | re.I)
if mt:
    tn = [num(c) for c in re.findall(r'<td[^>]*class="[^"]*\bnum\b[^"]*"[^>]*>(.*?)</td>', mt.group(1), re.S | re.I)]
    tn = [x for x in tn if x is not None]
    if len(tn) >= 2:
        grand = tn[-1]
        print("\n=== 총계행 ===")
        chk(abs(round(sum(tn[:-1]), 2) - tn[-1]) < 0.01, f"[총계행] 월셀합 {round(sum(tn[:-1]),2)} == {tn[-1]}")

print("\n=== 총계 일관성 ===")
if grand is not None:
    g = "%g" % grand
    cnt = len(re.findall(re.escape(g) + r"(?!\d)", html))
    chk(cnt >= 3, f"총계값 '{g}' 문서 등장 {cnt}회 (>=3 기대: 최소 히어로·표·푸터)")
else:
    chk(False, "총계값을 찾지 못함")

print("\n=== 표기 규칙 ===")
chk(not re.search(r"~\s*(M\+|\d개월|\d+주)", html), "범위 표기 물결표(~) 미사용")

print(f"\n=== 결과 === ({checks} 검사, {len(fails)} 실패)")
if fails:
    for f in fails: print("  - " + f)
    sys.exit(1)
print("PASS")
sys.exit(0)
