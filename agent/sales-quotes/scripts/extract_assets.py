#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_assets.py — input 문서(.docx/.pptx/.xlsx)에 임베드된 이미지를 추출.

왜: RFP/요건서에 **AS-IS 인프라 구성도·아키텍처 도식·화면 시안**이 이미지로 박혀 있는 경우가 많다.
    이를 꺼내 `Read`(멀티모달)로 판독하면 현행 인프라(노드·이중화·영역·OS/미들웨어·연동)를 구조화할 수 있다.
    Office 문서는 zip이라 word/media · ppt/media · xl/media 에 원본 이미지가 들어있다.

사용: python scripts/extract_assets.py "input/문서.docx" --out _workspace/{slug}/assets
      → assets/{문서명}_img01.png ... 로 추출. 이후 solution-architect/analyst가 Read로 판독.
"""
import sys, os, zipfile, argparse

for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass

MEDIA_DIRS = ("word/media/", "ppt/media/", "xl/media/")
RASTER = ("png", "jpg", "jpeg", "gif", "bmp")          # Read로 바로 판독 가능
VECTOR = ("emf", "wmf", "svg")                          # 벡터(판독 제한 — 경고만)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("doc", help="input 문서 경로(.docx/.pptx/.xlsx)")
    ap.add_argument("--out", required=True, help="추출 폴더(예: _workspace/{slug}/assets)")
    a = ap.parse_args()

    if not os.path.isfile(a.doc):
        print(f"[ERROR] 파일 없음: {a.doc}", file=sys.stderr); return 1
    if not zipfile.is_zipfile(a.doc):
        print(f"[ERROR] zip 기반 Office 문서가 아님(.docx/.pptx/.xlsx만 지원): {a.doc}", file=sys.stderr); return 1

    os.makedirs(a.out, exist_ok=True)
    base = os.path.splitext(os.path.basename(a.doc))[0]
    z = zipfile.ZipFile(a.doc)
    n = 0; vector = 0
    for name in sorted(z.namelist()):
        if not any(name.startswith(d) for d in MEDIA_DIRS) or "." not in name:
            continue
        ext = name.rsplit(".", 1)[1].lower()
        if ext in RASTER:
            n += 1
            out = os.path.join(a.out, f"{base}_img{n:02d}.{ext}")
            with open(out, "wb") as f:
                f.write(z.read(name))
            print(f"  추출: {out} ({z.getinfo(name).file_size // 1024}KB)")
        elif ext in VECTOR:
            vector += 1
    if vector:
        print(f"[WARN] 벡터 이미지 {vector}개(emf/wmf/svg)는 Read 판독이 제한적 — 필요 시 사용자에게 캡처 요청", file=sys.stderr)
    print(f"[OK] 래스터 이미지 {n}개 추출 → {a.out}" if n else "[OK] 추출할 래스터 이미지 없음")
    return 0


if __name__ == "__main__":
    sys.exit(main())
