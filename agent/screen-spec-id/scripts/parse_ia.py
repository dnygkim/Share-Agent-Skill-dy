# -*- coding: utf-8 -*-
"""parse_ia.py — 메뉴구조도(IA) xlsx를 파싱해 JSON 트리로 변환한다.

사용법:
    python scripts/parse_ia.py <IA.xlsx> -o <parsed.json>

동작:
- 각 시트에서 'No.' 셀이 있는 행을 헤더로 자동 탐지
- 'Depth N' 컬럼들을 찾아 계단식 트리를 경로(path)로 복원
- 화면타입/기능/구분/기타 컬럼을 행 단위로 수집
"""
import argparse
import json
import re
import sys

import openpyxl


def find_header(ws, search_rows=10):
    """'No.' 텍스트가 있는 행/열을 찾아 (row, {header: col}) 반환."""
    for r in range(1, min(search_rows, ws.max_row) + 1):
        for c in range(1, min(ws.max_column, 40) + 1):
            v = ws.cell(row=r, column=c).value
            if isinstance(v, str) and v.strip() in ("No.", "NO.", "no."):
                cols = {}
                for cc in range(1, ws.max_column + 1):
                    hv = ws.cell(row=r, column=cc).value
                    if hv is not None and str(hv).strip():
                        cols[str(hv).strip()] = cc
                return r, cols
    return None, None


def depth_columns(cols):
    """{depth_level: col} 매핑. 'Depth 0'~'Depth 10' 헤더를 인식."""
    out = {}
    for name, c in cols.items():
        m = re.match(r"^Depth\s*(\d+)$", name, re.IGNORECASE)
        if m:
            out[int(m.group(1))] = c
    return dict(sorted(out.items()))


def parse_sheet(ws):
    hdr_row, cols = find_header(ws)
    if hdr_row is None:
        return None
    dcols = depth_columns(cols)
    if not dcols:
        return None

    col_no = cols.get("No.")
    col_gubun = cols.get("구분")
    col_type = next((c for h, c in cols.items() if "화면타입" in h), None)
    col_func = next((c for h, c in cols.items() if h == "기능"), None)
    known = {col_no, col_gubun, col_type, col_func} | set(dcols.values())
    extra_cols = {h: c for h, c in cols.items() if c not in known}

    min_d, max_d = min(dcols), max(dcols)
    path = {}  # depth -> name (carry-over)
    rows = []
    for r in range(hdr_row + 1, ws.max_row + 1):
        filled = {d: ws.cell(row=r, column=c).value for d, c in dcols.items()
                  if ws.cell(row=r, column=c).value is not None}
        no = ws.cell(row=r, column=col_no).value if col_no else None
        if no is None and not filled:
            continue
        if filled:
            deepest = max(filled)
            for d in list(path):
                if d >= min(filled):
                    del path[d]
            for d, v in filled.items():
                path[d] = str(v).strip()
            node_depth = deepest
        else:
            # depth 셀이 모두 빈 행: 직전 경로 유지 (이름 없는 행)
            node_depth = max(path) if path else min_d
        full_path = [path[d] for d in sorted(path) if d <= node_depth]
        extras = {}
        for h, c in extra_cols.items():
            v = ws.cell(row=r, column=c).value
            if v is not None and str(v).strip():
                extras[h] = str(v).strip()
        rows.append({
            "row": r,
            "no": no if not isinstance(no, float) or no % 1 else int(no),
            "gubun": (str(ws.cell(row=r, column=col_gubun).value).strip()
                      if col_gubun and ws.cell(row=r, column=col_gubun).value else None),
            "depth": node_depth,
            "name": path.get(node_depth, ""),
            "path": full_path,
            "type": (str(ws.cell(row=r, column=col_type).value).strip()
                     if col_type and ws.cell(row=r, column=col_type).value else None),
            "func": (str(ws.cell(row=r, column=col_func).value).strip()
                     if col_func and ws.cell(row=r, column=col_func).value else None),
            "extras": extras,
        })
    return {
        "header_row": hdr_row,
        "depth_min": min_d,
        "depth_max": max_d,
        "columns": {h: c for h, c in cols.items()},
        "rows": rows,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("xlsx")
    ap.add_argument("-o", "--out", required=True)
    args = ap.parse_args()

    wb = openpyxl.load_workbook(args.xlsx, data_only=True)
    result = {"source": args.xlsx, "sheets": {}}
    for name in wb.sheetnames:
        parsed = parse_sheet(wb[name])
        if parsed and parsed["rows"]:
            result["sheets"][name] = parsed

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # 요약 출력 (에이전트가 코드표 제안에 사용)
    sys.stdout.reconfigure(encoding="utf-8")
    for name, sh in result["sheets"].items():
        rows = sh["rows"]
        top_names = []
        seen = set()
        for row in rows:
            key = row["path"][1] if len(row["path"]) > 1 else (row["path"][0] if row["path"] else "")
            if key and key not in seen:
                seen.add(key)
                top_names.append(key)
        types = {}
        for row in rows:
            types[row["type"]] = types.get(row["type"], 0) + 1
        print(f"[{name}] rows={len(rows)} depth={sh['depth_min']}..{sh['depth_max']} types={types}")
        print(f"  대분류 후보({len(top_names)}): {', '.join(top_names)}")


if __name__ == "__main__":
    main()
