#!/usr/bin/env python3
"""check_leak.py — 산출물 HTML에 examples/ 샘플(과거 고객 완성본)의 고객명·식별 토큰이 섞였는지 검사.

  usage: check_leak.py <html> [--allow 토큰,토큰]   # --allow = 이번 프로젝트의 실제 고객명(정상 등장)

규칙(CLAUDE.md "민감자료 정책"): examples/ 는 형식·구성 참고 샘플일 뿐이다. 다른 프로젝트 산출물에
샘플의 고객명·수치·범위·IA·문장을 재사용·적용하면 안 된다. 이 스크립트는 그 중 기계적으로 잡히는
"고객 식별 토큰" 잔존을 0건으로 강제한다(qa 게이트). 수치·문장 재사용은 qa/persona-review가 본다.
토큰 = examples/*.html 파일명의 고객 접두어 + 아래 EXTRA. 새 샘플을 넣으면 자동 반영된다.
"""
import os, re, sys, html as _h

HERE = os.path.dirname(os.path.abspath(__file__))
EXDIR = os.path.join(HERE, "..", "examples")
EXTRA = ["웅진", "아너파라다이스", "코스모진", "FunETF", "동양ABL", "자이홈", "SDN"]

def tokens():
    t = set(EXTRA)
    if os.path.isdir(EXDIR):
        for f in os.listdir(EXDIR):
            if f.lower().endswith(".html"):
                head = re.split(r"[_\s]", re.sub(r"^\d+_", "", f), 1)[0]
                if len(head) >= 2: t.add(head)
    return sorted(t, key=len, reverse=True)

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    path = sys.argv[1]; allow = set()
    if "--allow" in sys.argv:
        allow = {a.strip() for a in sys.argv[sys.argv.index("--allow")+1].split(",") if a.strip()}
    raw = open(path, encoding="utf-8", errors="replace").read()
    text = _h.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)[\s\S]*?</\1>", " ", raw, flags=re.I)))
    hits = []
    for tok in tokens():
        if tok in allow: continue
        for m in re.finditer(re.escape(tok), text):
            ctx = text[max(0, m.start()-30):m.end()+30].replace("\n", " ")
            hits.append((tok, re.sub(r"\s+", " ", ctx)))
    if hits:
        print(f"  FAIL 샘플 고객 토큰 잔존 {len(hits)}건 — examples/ 는 샘플 전용, 다른 문서에 재사용·적용 금지")
        for tok, ctx in hits[:40]: print(f"       [{tok}] …{ctx}…")
        sys.exit(1)
    print("  OK   샘플 고객 토큰 잔존 0건 (examples/ 유출 없음)"); sys.exit(0)

if __name__ == "__main__": main()
