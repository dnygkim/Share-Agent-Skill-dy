#!/usr/bin/env bash
# build-release-notes.sh — 공유 리포 README 의 릴리즈노트 영역을 다시 만든다
#   bash share/build-release-notes.sh [원본 README 경로]
# mirror-from-source.sh 가 미러할 때마다 자동으로 부른다. 직접 돌릴 일은 거의 없다.
#
# 모으는 곳 (공유 리포에 들어 있는 것만)
# - agent/<이름>/README.md · skills/<이름>/README.md · global-house-style/README.md 의 「## 릴리즈노트」 표
# - agent/harness_st-etribe/README.md 의 「## 변경 이력」 표
# - 원본 루트 README 의 ui-ux-pro-max-skill · agent/*(하네스 공통) 행 — 폴더 README 에 이력이 없는 항목
# 공통 반영 사항은 global-house-style/CLAUDE.md 의 「# 전역 규칙 — …」 제목에서 뽑는다.
# README.md 의 <!-- RELEASE-NOTES:START --> ~ <!-- RELEASE-NOTES:END --> 사이만 바꾼다.
set -euo pipefail
export LC_ALL=C

share="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
src_readme="${1:-}"
readme="$share/README.md"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
rows="$work/rows.tsv"     # 일자 \t 구분순서+구분 \t 항목 \t 항목링크 \t 내용 \t 소유자
: > "$rows"

# 표 한 줄을 칸으로 나눈다: \| 는 보존, <sub> 태그 제거, 앞뒤 공백 제거
# 폴더 README 안의 상대 링크는 리포 루트 기준으로 바꾼다
read_table() {  # $1=파일 $2=섹션 제목 정규식 $3=형식(rel|hist) $4=구분 $5=항목 $6=항목링크
  awk -v sec="$2" -v fmt="$3" -v kind="$4" -v item="$5" -v link="$6" -v dir="$(dirname "$7")" '
    function clean(s) {
      gsub(/<\/?sub>/, "", s); gsub(/<img[^>]*>/, "", s); gsub(/<\/?div[^>]*>/, "", s)
      gsub(/^[ \t]+|[ \t]+$/, "", s); return s
    }
    function relink(s,   out, pre, rest, tgt) {
      out = ""
      while (match(s, /\]\([^)]+\)/)) {
        pre = substr(s, 1, RSTART + 1); tgt = substr(s, RSTART + 2, RLENGTH - 3); rest = substr(s, RSTART + RLENGTH)
        if (tgt !~ /^(https?:|#|mailto:|\/)/) tgt = dir "/" tgt
        out = out pre tgt ")"; s = rest
      }
      return out s
    }
    $0 ~ sec { on = 1; next }
    on && /^## / { exit }
    on && /^\|/ {
      line = $0; gsub(/\\\|/, "\001", line)
      n = split(line, f, "|")
      for (i = 1; i <= n; i++) { gsub(/\001/, "\\|", f[i]); f[i] = clean(f[i]) }
      if (fmt == "rel") { body = f[2]; date = f[3]; owner = f[4] }
      else              { date = f[2]; body = f[3]; owner = "—" }
      gsub(/-/, ".", date)
      if (date !~ /^[0-9][0-9][0-9][0-9]\.[0-9][0-9]\.[0-9][0-9]$/) next
      if (owner == "") owner = "—"
      gsub(/\t/, " ", body)
      printf "%s\t%s\t%s\t%s\t%s\t%s\n", date, kind, item, link, relink(body), owner
    }
  ' "$1"
}

for f in "$share"/agent/*/README.md; do
  name="$(basename "$(dirname "$f")")"; rel="agent/$name/README.md"
  if grep -q '^## 릴리즈노트' "$f"; then read_table "$f" '^## 릴리즈노트' rel "2하네스" "$name" "$rel" "$rel" >> "$rows"; fi
  if grep -q '^## 변경 이력' "$f"; then read_table "$f" '^## 변경 이력' hist "2하네스" "$name" "$rel" "$rel" >> "$rows"; fi
done
for f in "$share"/skills/*/README.md; do
  name="$(basename "$(dirname "$f")")"; rel="skills/$name/README.md"
  read_table "$f" '^## 릴리즈노트' rel "3스킬" "$name" "$rel" "$rel" >> "$rows"
done
read_table "$share/global-house-style/README.md" '^## 릴리즈노트' rel "1공통" "global-house-style" \
  "global-house-style/README.md" "global-house-style/README.md" >> "$rows"

# 원본 루트 README: 폴더 README 에 이력이 없는 항목만 (ui-ux-pro-max-skill, agent/* 하네스 공통)
if [ -n "$src_readme" ] && [ -f "$src_readme" ]; then
  awk '
    function clean(s) { gsub(/<\/?sub>/, "", s); gsub(/<img[^>]*>/, "", s); gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
    /^## 릴리즈노트/ { on = 1; next }
    on && /^## / { exit }
    on && /^\| *<sub>/ {
      line = $0; gsub(/\\\|/, "\001", line); n = split(line, f, "|")
      for (i = 1; i <= n; i++) { gsub(/\001/, "\\|", f[i]); f[i] = clean(f[i]) }
      item = f[3]; date = f[5]; owner = f[6]
      if (item ~ /^\[ui-ux-pro-max-skill\]/) { kind = "3스킬"; name = "ui-ux-pro-max-skill"; link = "ui-ux-pro-max-skill/README.md" }
      else if (item ~ /^\[agent\/\*\]/)     { kind = "1공통"; name = "하네스 공통"; link = "agent/" }
      else next
      if (date !~ /^[0-9][0-9][0-9][0-9]\.[0-9][0-9]\.[0-9][0-9]$/) next
      printf "%s\t%s\t%s\t%s\t%s\t%s\n", date, kind, name, link, f[4], owner
    }
  ' "$src_readme" >> "$rows"
fi

sort -t "$(printf '\t')" -k1,1r -k2,2 -k3,3 -s "$rows" > "$work/sorted.tsv"

# 공통 반영 사항: 전역 규칙 제목
common="$work/common.md"
grep '^# 전역 규칙 — ' "$share/global-house-style/CLAUDE.md" \
  | sed -e 's/^# 전역 규칙 — //' -e 's/ *([^)]*[0-9][0-9][0-9][0-9][^)]*)$//' \
  | awk '{ printf "| <sub>%d</sub> | <sub>%s</sub> |\n", NR, $0 }' > "$common"

total="$(wc -l < "$work/sorted.tsv" | tr -d ' ')"
latest="$(head -1 "$work/sorted.tsv" | cut -f1)"

{
  echo '<!-- RELEASE-NOTES:START — share/build-release-notes.sh 가 미러할 때마다 다시 만든다. 이 사이는 직접 고치지 않는다 -->'
  echo '## 릴리즈노트'
  echo
  echo "원본 각 폴더 README 의 릴리즈노트를 모아 일자별로 정리한 것 (총 ${total}건 · 최신 ${latest}). 상세는 항목 이름을 눌러 해당 README 에서 본다."
  echo
  echo '### 공통 반영 사항'
  echo
  echo '모든 하네스 · 스킬에 공통으로 적용되는 전역 규칙. 정본은 [`global-house-style/CLAUDE.md`](global-house-style/CLAUDE.md)이고, `share/update.sh` 가 `~/.claude/house-style/global-rules.md` 로 설치해 `~/.claude/CLAUDE.md` 에서 불러온다. 규칙이 바뀐 이력은 아래 표의 「공통」 구분.'
  echo
  echo '| <div align="center"><sub>#</sub></div> | <sub>전역 규칙</sub> |'
  echo '|:---:|:---|'
  cat "$common"
  echo
  echo '### 일자별 업데이트 항목'
  echo
  echo '| <sub>일자</sub> | <sub>공통</sub> | <sub>하네스</sub> | <sub>스킬</sub> |'
  echo '|:---:|:---|:---|:---|'
  awk -F '\t' '
    function add(list, x) { return (index(" · " list " · ", " · " x " · ") ? list : (list == "" ? x : list " · " x)) }
    function cell(x) { return (x == "" ? "" : "<sub>" x "</sub>") }
    function flush() { if (d != "") printf "| <sub>%s</sub> | %s | %s | %s |\n", d, cell(c), cell(h), cell(s) }
    $1 != d { flush(); d = $1; c = h = s = "" }
    { nm = "[" $3 "](" $4 ")"
      if ($2 ~ /^1/) c = add(c, nm); else if ($2 ~ /^2/) h = add(h, nm); else s = add(s, nm) }
    END { flush() }
  ' "$work/sorted.tsv"
  echo
  echo '### 상세 내역 (월별)'
  echo
  awk -F '\t' '
    function close_m() { if (m != "") { print ""; print "</details>"; print "" } }
    { mon = substr($1, 1, 7); cnt[mon]++ }
    { line[NR] = $0 }
    END {
      first = 1
      for (i = 1; i <= NR; i++) {
        split(line[i], f, "\t"); mon = substr(f[1], 1, 7)
        if (mon != m) {
          close_m(); m = mon
          printf "<details%s>\n<summary><b>%s</b> · %d건</summary>\n\n", (first ? " open" : ""), mon, cnt[mon]
          print "| <sub>일자</sub> | <sub>구분</sub> | <sub>항목</sub> | <div align=\"center\"><sub>내용</sub></div> | <sub>소유자</sub> |"
          print "|:---:|:---:|:---:|:---|:---:|"
          first = 0; pd = ""
        }
        kind = substr(f[2], 2)
        printf "| %s | <sub>%s</sub> | <sub>[%s](%s)</sub> | <sub>%s</sub> | <sub>%s</sub> |\n", (f[1] == pd ? "" : "<sub>" f[1] "</sub>"), kind, f[3], f[4], f[5], f[6]
        pd = f[1]
      }
      close_m()
    }
  ' "$work/sorted.tsv"
  echo '<!-- RELEASE-NOTES:END -->'
} > "$work/notes.md"

# README 의 표식 사이를 교체 (표식이 없으면 끝에 붙인다)
if grep -q '^<!-- RELEASE-NOTES:START' "$readme"; then
  awk -v notes="$work/notes.md" '
    /^<!-- RELEASE-NOTES:START/ { while ((getline l < notes) > 0) print l; skip = 1; next }
    /^<!-- RELEASE-NOTES:END -->/ { skip = 0; next }
    !skip { print }
  ' "$readme" > "$work/README.md"
else
  { cat "$readme"; echo; cat "$work/notes.md"; } > "$work/README.md"
fi
cp "$work/README.md" "$readme"
echo "release notes: ${total}건 (최신 ${latest}) -> README.md"
