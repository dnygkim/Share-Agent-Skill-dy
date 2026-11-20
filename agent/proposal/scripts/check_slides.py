#!/usr/bin/env python3
"""제안서 산출물(HTML) 1차 자동 점검 — 표준 라이브러리만 사용.
사용법: python scripts/check_slides.py output/<파일>.html
점검: 미해결 플래그([CI 확인 필요]/[미검증]/[정책 확인 필요]/[추가 제안]),
      미치환 자리표시자({...}), 슬라이드 수,
      (1600 덱) 페이지 번호 1..N 연속 여부, 장표 코드/페이지 자리표시자(B0X·A0X·00) 잔존, 피그마 벡터 슬라이드 id 접두 중복.
종료코드: 잔존 플래그/미치환이 있으면 1, 깨끗하면 0.
"""
import sys, re, pathlib

# Windows 콘솔(cp949)에서도 한글·기호 출력이 깨지지 않도록 UTF-8 강제
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

FLAGS = ["[CI 확인 필요]", "[미검증]", "[정책 확인 필요]", "[추가 제안]"]
# {CI_메인컬러} 같은 한글/영문 자리표시자 (CSS의 {} 블록은 공백/개행 포함이라 제외됨)
PLACEHOLDER = re.compile(r"\{[가-힣A-Za-z_][가-힣A-Za-z0-9_]*\}")

def main():
    if len(sys.argv) < 2:
        print("사용법: python scripts/check_slides.py <파일.html>")
        return 2
    p = pathlib.Path(sys.argv[1])
    if not p.exists():
        print(f"[ERROR] 파일 없음: {p}")
        return 2
    text = p.read_text(encoding="utf-8", errors="replace")

    issues = 0
    print(f"== 점검: {p.name} ==")

    # 1) 잔존 플래그
    for f in FLAGS:
        n = text.count(f)
        if n:
            print(f"  [잔존] {f} × {n}")
            issues += n

    # 2) 미치환 자리표시자
    ph = sorted(set(m.group() for m in PLACEHOLDER.finditer(text)))
    if ph:
        print(f"  [미치환 자리표시자] {len(ph)}종: {', '.join(ph[:12])}{' ...' if len(ph)>12 else ''}")
        issues += len(ph)

    # 3-0) 1600 덱(section.slide 나열 + data-chap) 전용 점검
    if 'data-chap="' in text and '<section class="slide' in text:
        parts = [q for q in re.split(r'(?=<section class="slide)', text[text.index('<section class="slide'):]) if q.strip()]
        seq = []
        for q in parts:
            m = re.search(r'(?:<span class="pg">|class="pg figpg" style="top:865px">)(\d+)<', q) or re.search(r'&lt;b&gt;(\d{2})&lt;/b&gt;', q)
            seq.append(int(m.group(1)) if m else None)
        if seq != list(range(1, len(seq) + 1)):
            bad = [(i + 1, v) for i, v in enumerate(seq) if v != i + 1]
            print(f"  [페이지 번호 불연속] {bad[:10]}{' ...' if len(bad) > 10 else ''}  → scripts/deck_edit.py 로 재번호")
            issues += 1
        ph = re.findall(r'class="code">([A-Z]0X)<', text) + re.findall(r'<span class="pg">(00)</span>', text)
        if ph:
            print(f"  [장표 코드/페이지 자리표시자 잔존] {sorted(set(ph))} × {len(ph)}")
            issues += len(ph)
        pref = re.findall(r'id="([a-z]\d{2}_)', text)
        dup = {k for k in set(pref) if [q for q in parts if 'id="%s' % k in q].__len__() > 1}
        if dup:
            print(f"  [SVG id 접두 중복 — 슬라이드 간 충돌] {sorted(dup)}")
            issues += len(dup)

    # 3) 슬라이드 수 (참고)
    # class 속성에서 'slide'가 (하이픈 없는) 독립 토큰인 경우만 = 슬라이드 컨테이너
    slides = len(re.findall(r'class="(?:[^"]*\s)?slide(?:\s[^"]*)?"', text))
    print(f"  [정보] 슬라이드 수: {slides}")

    print("== 결과:", "통과(PASS)" if issues == 0 else f"보완필요 - {issues}건", "==")
    return 0 if issues == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
