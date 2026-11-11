# -*- coding: utf-8 -*-
"""generate_spec.py — parse_ia.py 결과 + config로 화면명세서 xlsx를 생성한다.

사용법:
    python scripts/generate_spec.py <parsed.json> <config.json> -o <출력.xlsx>
    python scripts/generate_spec.py <parsed.json> <config.json> --preview   # 채번 결과만 JSON 출력 (xlsx 미생성)

--preview 모드: 코드 미정의 대분류를 오류 대신 "(코드미정)"으로 표시하고,
공통영역(common_menus)과 메뉴별로 나눠 채번 결과를 출력한다. 단계별 검토용.

config 스키마는 references/config-schema.md 참조.
채번 규칙 기본값 정본: RULES.md (프로젝트별 조정은 config의 id_rule)
"""
import argparse
import json
import sys
from datetime import date

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

FONT = "맑은 고딕"
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
HDR_FILL = PatternFill("solid", fgColor="D9D9D9")
MENU_FILL = PatternFill("solid", fgColor="F2F2F2")

NO_ID_TYPES = {"Menu", "Internal Link", "External Link", "Link"}
UNDEF = "(코드미정)"

# 채번 규칙 기본값 (RULES.md 정본). config의 id_rule로 프로젝트별 재정의 가능.
DEFAULT_RULE = {
    "format": "{biz}-{gubun}-{ch}-{cat}-{seq}",
    "seq_digits": 5,
    "suffixes": {"Popup": "P", "Layer": "L", "Tab": "T", "Bottom Sheet": "B", "BottomSheet": "B"},
}


def resolve_rule(cfg):
    rule = dict(DEFAULT_RULE)
    user = cfg.get("id_rule", {})
    rule.update({k: v for k, v in user.items() if k != "suffixes"})
    if "suffixes" in user:
        rule["suffixes"] = dict(user["suffixes"])
    return rule


def make_id(rule, biz, gubun, ch_code, cat_code, num, suffix=""):
    seq = f"{num:0{rule['seq_digits']}d}{suffix}"
    return rule["format"].format(biz=biz, gubun=gubun, ch=ch_code, cat=cat_code, seq=seq)


def cell(ws, r, c, v=None, bold=False, size=10, fill=None, align="left", wrap=False, border=True):
    x = ws.cell(row=r, column=c)
    if v is not None:
        x.value = v
    x.font = Font(name=FONT, size=size, bold=bold)
    x.alignment = Alignment(horizontal=align, vertical="center", wrap_text=wrap)
    if fill:
        x.fill = fill
    if border:
        x.border = BORDER
    return x


def category_of(row, key_depth, dmin):
    """대분류 키 = key_depth 위치의 경로명 (없으면 최상위)."""
    p = row["path"]
    idx = key_depth - dmin
    if len(p) > idx:
        return p[idx]
    return p[0] if p else ""


def build_remark(row):
    parts = []
    tag = "/".join(x for x in (row.get("gubun"), row.get("func")) if x)
    if tag:
        parts.append(f"[{tag}]")
    for v in row.get("extras", {}).values():
        parts.append(v)
    return " ".join(parts)


def make_cover(wb, prj):
    ws = wb.create_sheet("표지")
    ws.sheet_view.showGridLines = False
    cell(ws, 4, 2, prj.get("title", ""), bold=True, size=22, border=False)
    cell(ws, 6, 2, prj.get("subtitle", "화면명세서"), bold=True, size=16, border=False)
    cell(ws, 9, 2, f"단계명 : {prj.get('phase', '설계')}", size=11, border=False)
    cell(ws, 10, 2, f"문서번호 : {prj.get('doc_no', '')}", size=11, border=False)
    cell(ws, 11, 2, f"작성일 : {prj.get('date', str(date.today()))}", size=11, border=False)
    cell(ws, 12, 2, f"버전 : {prj.get('version', 'Ver 0.1')}", size=11, border=False)


def make_history(wb, prj):
    ws = wb.create_sheet("개정이력")
    cell(ws, 1, 1, "개정이력", bold=True, size=14, border=False)
    heads = ["버전", "제.개정일자", "구분", "개정사유", "작성자", "승인자"]
    for i, h in enumerate(heads, 1):
        cell(ws, 3, i, h, bold=True, fill=HDR_FILL, align="center")
    vals = [prj.get("version", "Ver 0.1"), prj.get("date", str(date.today())), "신규",
            prj.get("reason", "화면명세서 초안 생성 (IA 기반 자동 추출)"),
            prj.get("author", ""), prj.get("approver", "")]
    for i, v in enumerate(vals, 1):
        cell(ws, 4, i, v, wrap=True)
    widths = [10, 14, 8, 60, 12, 12]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


def make_rules(wb, cfg, rule):
    ws = wb.create_sheet("규정")
    cell(ws, 1, 2, "화면코드 부여 규정", bold=True, size=14, border=False)
    r = 3
    d = rule["seq_digits"]
    readable = rule["format"].format(
        biz="{업무구분}", gubun="{구분}", ch="{채널}", cat="{대분류}", seq=f"{{일련번호 {d}자리}}")
    example = make_id(rule, "FO", "SB", "PW", "BR", 12)
    cell(ws, r, 2, "화면아이디 생성규칙", bold=True, fill=HDR_FILL); r += 1
    cell(ws, r, 2, f"{readable}  예: {example}"); r += 2
    cell(ws, r, 2, "화면타입 접미사", bold=True, fill=HDR_FILL); r += 1
    shown = set()
    for t, s in rule["suffixes"].items():
        if s in shown:
            continue
        shown.add(s)
        cell(ws, r, 2, f"{t} = 소속 페이지 화면코드 뒤 {s}n (예: …-{12:0{d}d}{s}1)"); r += 1
    r += 1
    cell(ws, r, 2, "일련번호는 대분류별 순차 채번, 숫자 외 사용 불가. Menu/Link 행은 ID 미부여('-').")
    r += 2
    for sh in cfg["sheets"]:
        common = set(sh.get("common_menus", []))
        cell(ws, r, 2, f"[{sh['out_sheet']}] 대분류 코드", bold=True, fill=HDR_FILL)
        cell(ws, r, 3, "", fill=HDR_FILL); cell(ws, r, 4, "", fill=HDR_FILL)
        r += 1
        cell(ws, r, 2, "메뉴명", bold=True, align="center", fill=MENU_FILL)
        cell(ws, r, 3, "영문명", bold=True, align="center", fill=MENU_FILL)
        cell(ws, r, 4, "코드", bold=True, align="center", fill=MENU_FILL)
        r += 1
        for name, (en, code) in sh["codes"].items():
            label = f"{name} (공통)" if name in common else name
            cell(ws, r, 2, label); cell(ws, r, 3, en); cell(ws, r, 4, code, align="center")
            r += 1
        r += 1
    for col, w in [(2, 34), (3, 34), (4, 10)]:
        ws.column_dimensions[get_column_letter(col)].width = w


def make_sheet(wb, sh_cfg, parsed_sheet, counters, prj, rule, collect, preview=False):
    """채널별 명세서 시트 생성. counters: {(biz, cat_code): last_num} 워크북 공유.
    collect: 채번 결과 누적 리스트 (프리뷰·검증 보고용).
    preview=True면 코드 미정의 대분류를 오류 대신 UNDEF로 표시한다."""
    ws = wb.create_sheet(sh_cfg["out_sheet"])
    rows = parsed_sheet["rows"]
    dmin, dmax = parsed_sheet["depth_min"], parsed_sheet["depth_max"]
    channels = sh_cfg["channels"]
    biz, gubun = sh_cfg["biz"], sh_cfg.get("gubun_code", "SB")
    key_depth = sh_cfg.get("category_key_depth", dmin + 1)
    default_type = sh_cfg.get("default_type", "Page")
    code_cols = sh_cfg.get("code_columns", False)
    common_set = set(sh_cfg.get("common_menus", []))
    suffixes = rule["suffixes"]

    # ---- 컬럼 배치
    col = 2
    layout = [("No.", 6), ("상태", 6), ("수정일", 10)]
    if code_cols:
        layout += [("채널", 6), ("코드", 6)]
    for ch in channels:
        layout += [(ch["id_header"], 22), (ch["cnt_header"], 7)]
    layout += [("화면타입", 9), ("화면명", 26)]
    for d in range(dmin, dmax + 1):
        layout += [(f"Depth {d}", 18)]
    layout += [("비고", 40)]
    HDR = 5
    positions = {}
    for name, width in layout:
        positions[name] = col
        ws.column_dimensions[get_column_letter(col)].width = width
        cell(ws, HDR, col, name, bold=True, fill=HDR_FILL, align="center", wrap=True)
        col += 1

    # ---- 타이틀/메타
    cell(ws, 2, 2, sh_cfg.get("title", sh_cfg["out_sheet"]), bold=True, size=13, border=False)
    warn_col = positions["화면타입"]
    cell(ws, 2, warn_col, "수정자 외 [읽기모드]로 확인 부탁 드립니다. (휴먼에러 방지)", size=9, border=False)
    cell(ws, 3, 2, "Last Updated", bold=True, border=False)
    cell(ws, 3, 4, prj.get("date", str(date.today())), border=False)
    cell(ws, 3, 5, "본수(Total)", bold=True, border=False)

    # ---- 데이터
    r = HDR + 1
    first_data = r
    last_page_num = {}   # cat_code -> 마지막 페이지 번호
    suffix_seq = {}      # (cat_code, page_num, suffix) -> n
    id_seen = set()
    stats = {"rows": 0, "ids": 0, "counts": {ch["code"]: 0 for ch in channels}}

    for row in rows:
        typ = row["type"] or default_type
        cat_name = category_of(row, key_depth, dmin)
        mapped = sh_cfg["codes"].get(cat_name)
        if mapped is None and typ not in NO_ID_TYPES and not preview:
            raise SystemExit(f"[ERROR] 대분류 코드 미정의: '{cat_name}' (시트 {sh_cfg['out_sheet']}, IA행 {row['row']}) — config codes에 추가 필요")
        cat_code = mapped[1] if mapped else None

        ids = {}
        if typ in NO_ID_TYPES:
            for ch in channels:
                ids[ch["code"]] = "-"
        elif cat_code is None:  # 프리뷰에서 코드 미정의 — 채번 없이 표시만
            for ch in channels:
                ids[ch["code"]] = UNDEF
        elif typ in suffixes:
            key = (biz, cat_code)
            base = last_page_num.get(key)
            if base is None:
                counters[key] = counters.get(key, 0) + 1
                base = counters[key]
                last_page_num[key] = base
            letter = suffixes[typ]
            skey = (key, base, letter)
            suffix_seq[skey] = suffix_seq.get(skey, 0) + 1
            n = suffix_seq[skey]
            for ch in channels:
                ids[ch["code"]] = make_id(rule, biz, gubun, ch["code"], cat_code, base, f"{letter}{n}")
        else:  # Page 등 본 화면
            key = (biz, cat_code)
            counters[key] = counters.get(key, 0) + 1
            num = counters[key]
            last_page_num[key] = num
            for ch in channels:
                ids[ch["code"]] = make_id(rule, biz, gubun, ch["code"], cat_code, num)

        collect.append({
            "sheet": sh_cfg["out_sheet"], "ia_row": row["row"], "no": row["no"],
            "category": cat_name, "cat_code": cat_code, "common": cat_name in common_set,
            "type": typ, "name": row["name"], "ids": dict(ids),
        })

        is_menu = typ in NO_ID_TYPES
        fill = MENU_FILL if is_menu else None
        cell(ws, r, positions["No."], row["no"], align="center", fill=fill)
        cell(ws, r, positions["상태"], None, fill=fill)
        cell(ws, r, positions["수정일"], None, fill=fill)
        if code_cols:
            cell(ws, r, positions["채널"], channels[0]["code"] if not is_menu else "-", align="center", fill=fill)
            cell(ws, r, positions["코드"], cat_code or "-", align="center", fill=fill)
        for ch in channels:
            sid = ids[ch["code"]]
            real = sid not in ("-", UNDEF)
            cnt = 1 if real else 0
            cell(ws, r, positions[ch["id_header"]], sid, fill=fill)
            cell(ws, r, positions[ch["cnt_header"]], cnt, align="center", fill=fill)
            stats["counts"][ch["code"]] += cnt
            if real:
                if sid in id_seen:
                    raise SystemExit(f"[ERROR] 화면ID 중복: {sid} (행 {r})")
                id_seen.add(sid)
                stats["ids"] += 1
        cell(ws, r, positions["화면타입"], typ, align="center", fill=fill)
        cell(ws, r, positions["화면명"], row["name"], fill=fill, wrap=True)
        for d in range(dmin, dmax + 1):
            idx = d - dmin
            v = row["path"][idx] if (d == row["depth"] and len(row["path"]) > idx) else None
            cell(ws, r, positions[f"Depth {d}"], v, fill=fill, wrap=True)
        cell(ws, r, positions["비고"], build_remark(row), fill=fill, wrap=True)
        stats["rows"] += 1
        r += 1

    last_data = r - 1
    # ---- 본수 합계 (수식)
    total_cells = []
    for ch in channels:
        c = positions[ch["cnt_header"]]
        L = get_column_letter(c)
        cell(ws, 4, c, f"=SUM({L}{first_data}:{L}{last_data})", bold=True, align="center", border=False)
        total_cells.append(f"{L}4")
    cell(ws, 3, 6, f"={'+'.join(total_cells)}", bold=True, border=False)

    ws.freeze_panes = ws.cell(row=HDR + 1, column=4)
    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("parsed")
    ap.add_argument("config")
    ap.add_argument("-o", "--out", help="출력 xlsx 경로 (--preview가 아니면 필수)")
    ap.add_argument("--preview", action="store_true",
                    help="xlsx 생성 없이 채번 결과를 공통영역/메뉴별로 나눠 JSON 출력")
    args = ap.parse_args()
    if not args.preview and not args.out:
        ap.error("-o/--out이 필요합니다 (--preview 모드가 아닌 경우)")
    sys.stdout.reconfigure(encoding="utf-8")

    with open(args.parsed, encoding="utf-8") as f:
        parsed = json.load(f)
    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)

    rule = resolve_rule(cfg)
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    prj = cfg.get("project", {})
    make_cover(wb, prj)
    make_history(wb, prj)
    make_rules(wb, cfg, rule)

    counters = {}
    report = {}
    collect = []
    for sh_cfg in cfg["sheets"]:
        ia_name = sh_cfg["ia_sheet"]
        if ia_name not in parsed["sheets"]:
            raise SystemExit(f"[ERROR] IA 시트 없음: '{ia_name}' (파싱된 시트: {list(parsed['sheets'])})")
        report[sh_cfg["out_sheet"]] = make_sheet(
            wb, sh_cfg, parsed["sheets"][ia_name], counters, prj, rule, collect, preview=args.preview)

    if args.preview:
        entries = [e for e in collect if e["type"] not in NO_ID_TYPES]
        undefined = sorted({e["category"] for e in entries if e["cat_code"] is None})
        out = {
            "preview": True,
            "id_rule": rule,
            "summary": {
                "total_rows": len(collect),
                "id_rows": len(entries),
                "common_rows": sum(1 for e in entries if e["common"]),
                "menu_rows": sum(1 for e in entries if not e["common"]),
                "undefined_categories": undefined,
            },
            "common": [e for e in entries if e["common"]],
            "menu": [e for e in entries if not e["common"]],
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    wb.save(args.out)
    print(json.dumps({"output": args.out, "sheets": report}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
