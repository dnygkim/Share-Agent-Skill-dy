#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
inline_css.py — 하우스 스타일/도식 CSS를 HTML <style>에 '그대로(verbatim)' 주입한다.

목적: builder(LLM)가 CSS를 직접 타이핑하면 요약·누락으로 디자인이 드리프트한다.
      그래서 builder는 본문 HTML만 작성하고 <style>에는 마커만 둔다. 이 스크립트가
      template/house-style.css 와 (필요 시) template/diagrams.css 의 내용을
      바이트 그대로 마커 위치에 끼워넣는다.

마커(HTML <style> 안에 둔다):
    /*__HOUSE_STYLE_DOC__*/   → ★ 기본(2026-11-27~). 전역 정본 house-style.css 전체로 치환
                               (문서형 골격 topbar · lnb · cover · toc — 2026-11 홈페이지 재구축 공수산정 양식)
                               탐색 순서: $HOUSE_STYLE_CSS → ~/.claude/house-style/house-style.css
                                        → 리포 global-house-style/house-style.css
    /*__HOUSE_STYLE_CSS__*/   → (레거시) template/house-style.css — build_report.py의 top-header 구조 전용
    /*__DIAGRAMS_CSS__*/      → diagrams.css 전체로 치환(도식 섹션이 있을 때만 마커를 둔다)

사용:
    python inline_css.py <html_path>            # in-place 주입
    python inline_css.py <html_path> -o out.html # 다른 경로로 출력

종료코드: 0 정상 / 1 오류(마커 없음·파일 없음 등) — qa가 빌드 정합성 게이트로 활용.
"""
import sys
import os
import re
import argparse

HOUSE_MARKER = "/*__HOUSE_STYLE_CSS__*/"
DOC_MARKER = "/*__HOUSE_STYLE_DOC__*/"


def global_house_css(here):
    """전역 정본 house-style.css 경로 — 로컬 설치본이 최신 기준."""
    cands = [os.environ.get("HOUSE_STYLE_CSS", ""),
             os.path.join(os.path.expanduser("~"), ".claude", "house-style", "house-style.css"),
             os.path.join(here, "..", "..", "..", "global-house-style", "house-style.css")]
    for c in cands:
        if c and os.path.isfile(c):
            return os.path.normpath(c)
    return None
DIAGRAMS_MARKER = "/*__DIAGRAMS_CSS__*/"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html", help="대상 HTML 경로")
    ap.add_argument("-o", "--out", help="출력 경로(미지정 시 in-place)")
    args = ap.parse_args()

    # template/ 은 이 스크립트 기준 ../template
    here = os.path.dirname(os.path.abspath(__file__))
    tpl = os.path.join(here, "..", "template")
    house_css = os.path.join(tpl, "house-style.css")
    diagrams_css = os.path.join(tpl, "diagrams.css")

    if not os.path.isfile(args.html):
        print(f"[ERROR] HTML 없음: {args.html}", file=sys.stderr)
        return 1

    with open(args.html, encoding="utf-8") as f:
        html = f.read()

    if DOC_MARKER in html:
        g = global_house_css(here)
        if not g:
            print("[ERROR] 전역 정본 house-style.css 없음 (~/.claude/house-style · global-house-style)", file=sys.stderr)
            return 1
        house_css = g
        HM = DOC_MARKER
    else:
        HM = HOUSE_MARKER
    if HM not in html:
        print(f"[ERROR] 하우스 스타일 마커 없음: {DOC_MARKER} (또는 레거시 {HOUSE_MARKER})", file=sys.stderr)
        print("        <style> 안에 마커를 두고 CSS는 직접 작성하지 말 것.", file=sys.stderr)
        return 1

    # ★ 주입 전 소스 CSS의 중괄호 균형 검증 — 미닫힌 { 하나가 그 뒤 CSS 전체 파싱을
    #   깨뜨려(브라우저가 규칙을 통째로 버림) 도식이 무스타일로 평면화된 사고가 있었음.
    def balanced(path):
        with open(path, encoding="utf-8") as f:
            css = f.read()
        return css.count("{") == css.count("}"), css.count("{"), css.count("}")

    for css_path in [house_css] + ([diagrams_css] if DIAGRAMS_MARKER in html else []):
        ok, o, c = balanced(css_path)
        if not ok:
            print(f"[ERROR] CSS 중괄호 불균형: {os.path.basename(css_path)} {{={o} }}={c} "
                  f"— 미닫힌 블록이 뒤 CSS를 삼켜 렌더가 깨진다. 소스를 고치고 다시 주입할 것.",
                  file=sys.stderr)
            return 1

    with open(house_css, encoding="utf-8") as f:
        html = html.replace(HM, f.read())
    if DIAGRAMS_MARKER in html:
        with open(diagrams_css, encoding="utf-8") as f:
            html = html.replace(DIAGRAMS_MARKER, f.read())
        used_diagrams = True
    else:
        used_diagrams = False

    # 주입 후 최종 <style> 균형도 재확인(이중 안전장치)
    style = "".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S | re.I))
    if style.count("{") != style.count("}"):
        print(f"[ERROR] 주입 후 <style> 중괄호 불균형 {{={style.count('{')} }}={style.count('}')}", file=sys.stderr)
        return 1

    out = args.out or args.html
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[OK] CSS 주입 완료 → {out}  ({'정본 ' + house_css if HM == DOC_MARKER else '레거시 template/house-style.css'}{' + diagrams' if used_diagrams else ''}, 중괄호 균형 검증 통과)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
