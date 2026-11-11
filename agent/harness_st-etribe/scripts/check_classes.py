#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_classes.py — 본문에서 쓴 class 중 <style>에 '정의되지 않은' 것(발명 클래스)을 잡는다.

왜: builder가 .d1-no/.d2-chip 같은 새 클래스를 만들면 인라인 CSS에 정의가 없어
    스타일이 안 먹고 평문으로 깨진다(아너파라다이스 v1.0 사고). 정의 0·사용 N인
    클래스가 있으면 렌더가 깨진 것 → FAIL.

사용: python scripts/check_classes.py <html_path>
종료코드: 0 정상 / 1 orphan 발견(또는 파일 없음).
"""
import sys, re

# 유틸리티성으로 정의 없이도 쓰는 관용 클래스(허용 화이트리스트)
WHITELIST = {"num", "zero", "hl", "new", "total", "subtotal", "empty", "center"}

for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass

if len(sys.argv) < 2:
    print("usage: check_classes.py <html>", file=sys.stderr); sys.exit(1)

try:
    html = open(sys.argv[1], encoding="utf-8").read()
except OSError as e:
    print(f"[ERROR] {e}", file=sys.stderr); sys.exit(1)

# <style> 블록들에서 '정의된' 클래스 수집(.foo)
defined = set()
for style in re.findall(r"<style[^>]*>(.*?)</style>", html, re.S | re.I):
    defined |= set(re.findall(r"\.([A-Za-z_][\w-]*)", style))

# 본문에서 '사용된' 클래스 수집 — <style>·<script> 제외(JS의 'bar-'+phase 류 거짓양성 방지)
body = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.S | re.I)
body = re.sub(r"<script[^>]*>.*?</script>", "", body, flags=re.S | re.I)
used = {}
for attr in re.findall(r'class\s*=\s*"([^"]*)"', body):
    for c in attr.split():
        used[c] = used.get(c, 0) + 1

orphans = {c: n for c, n in used.items() if c not in defined and c not in WHITELIST}

if orphans:
    print(f"[FAIL] 정의되지 않은(발명) 클래스 {len(orphans)}종 — 스타일 미적용으로 렌더 깨짐:")
    for c, n in sorted(orphans.items(), key=lambda x: -x[1]):
        print(f"    .{c}  (사용 {n}회, 정의 0)")
    print("→ house-style.css/diagrams.css의 정규 클래스로 교체하거나 examples/ 구조를 따를 것.")
    sys.exit(1)

print(f"[OK] 발명 클래스 없음 (사용 클래스 {len(used)}종 모두 정의됨)")
sys.exit(0)
