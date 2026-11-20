#!/bin/zsh
# render_pages.sh — HTML 덱을 headless Chrome 으로 페이지별 PNG 렌더(검증·피그마 백업용).
#   scripts/render_pages.sh <deck.html> <out_dir> [from=1] [to=끝] [scale=2]
# - 페이지는 URL 해시 #pN 으로 지정(덱 골격의 네비 스크립트가 해석)
# - 순차 실행 + 파일 생성 감시(워치독). 병렬 + --user-data-dir 조합은 크롬이 종료되지 않아 사용하지 않는다
# - scale=2 → 3200×1800 PNG(피그마 업로드용), 1 → 1600×900(빠른 검수)
set -u
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
F="$1"; OUT="$2"; FROM="${3:-1}"; SCALE="${5:-2}"
[ -f "$F" ] || { echo "no file: $F"; exit 1; }
mkdir -p "$OUT"
TOTAL=$(grep -o '<section class="slide' "$F" | wc -l | tr -d ' ')
TO="${4:-$TOTAL}"
case "$F" in /*) ABS="$F";; *) ABS="$PWD/$F";; esac
: > "$OUT/render.log"
for p in $(seq $FROM $TO); do
  out="$OUT/p$(printf %02d $p).png"
  "$CH" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=$SCALE --window-size=1600,900 \
        --virtual-time-budget=8000 --screenshot="$out" "file://$ABS#p$p" >/dev/null 2>&1 &
  pid=$!
  for i in $(seq 1 90); do [ -s "$out" ] && break; sleep 1; done
  sleep 1; kill $pid 2>/dev/null; wait $pid 2>/dev/null
  echo "$p $( [ -s "$out" ] && echo ok || echo FAIL )" >> "$OUT/render.log"
done
echo "rendered $(grep -c ok "$OUT/render.log")/$((TO-FROM+1)) → $OUT (fail: $(grep -c FAIL "$OUT/render.log"))"
