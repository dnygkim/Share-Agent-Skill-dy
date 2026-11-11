#!/usr/bin/env bash
# build-release-notes.sh — 공유 리포 README 의 자동 영역 3곳을 다시 만든다
#   bash share/build-release-notes.sh [원본 README 경로] [원본 커밋 sha] [원본 커밋 일자 YYYY.MM.DD]
# mirror-from-source.sh 가 미러할 때마다 자동으로 부른다. 직접 돌릴 일은 거의 없다.
#
# 자동 영역 (README.md 의 표식 사이만 바꾼다)
# - SYNC-STATUS  : 최상단 배치 시점 · 현재 반영본(원본 sha · 하네스/스킬 수 · 릴리즈노트 최신)
# - CONTENTS     : 「들어 있는 것」 하네스 표(원본 루트 README 표 기준, 단이bot 제외) · 스킬 표(skills/README.md 기준)
# - RELEASE-NOTES: 릴리즈노트
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
src_sha="${2:-}"
src_date="${3:-}"
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

# ── 들어 있는 것: 하네스 표 + 스킬 표 ──────────────────────────────────────
{
  echo '<!-- CONTENTS:START — share/build-release-notes.sh 가 미러할 때마다 다시 만든다. 이 사이는 직접 고치지 않는다 -->'
  echo '| <div align="center"><sub>에이전트(하네스)</sub></div> | <sub>역할</sub> |'
  echo '|:---|:---|'
  # 원본 루트 README 의 에이전트 표 행 (공유 리포에 있는 폴더만, 원본 순서)
  if [ -n "$src_readme" ] && [ -f "$src_readme" ]; then
    awk '/^\| *<div align="center"><sub>에이전트<\/sub>/ { on = 1; next } on && /^\|:/ { next } on && !/^\|/ { exit } on { print }' "$src_readme"
  fi > "$work/agent_rows.md"
  for d in "$share"/agent/*/; do
    name="$(basename "$d")"
    row="$(grep -F "[\`agent/$name/\`]" "$work/agent_rows.md" | head -1 || true)"
    if [ -z "$row" ]; then   # 원본 표에 없는 하네스: 폴더 README 첫 문단
      desc="$(awk 'NR > 1 && /^[^# \t|>`-]/ { gsub(/\*\*/, ""); sub(/[. ]+$/, ""); print; exit }' "$d/README.md" 2>/dev/null || true)"
      row="| <sub>[\`agent/$name/\`](agent/$name/)</sub> | <sub>${desc}</sub> |"
    fi
    printf '%s\t%s\n' "$(grep -nF "[\`agent/$name/\`]" "$work/agent_rows.md" | head -1 | cut -d: -f1 || true)" "$row"
  done | sort -t "$(printf '\t')" -k1,1n | awk -F '\t' '$1 != "" { print $2 } $1 == "" { tail[++t] = $2 } END { for (i = 1; i <= t; i++) print tail[i] }'
  echo
  echo '하네스는 해당 폴더에서 Claude Code를 열어 쓴다. 쓰는 방법은 각 폴더의 `README.md`.'
  echo
  echo '| <div align="center"><sub>스킬</sub></div> | <sub>용도</sub> | <sub>제작</sub> |'
  echo '|:---|:---|:---:|'
  awk '
    /^## 스킬 목록/ { on = 1; next }
    on && /^## / { exit }
    on && /^### / { by = "외부 백업"; if (match($0, /제작: */)) by = substr($0, RSTART + RLENGTH); next }
    on && /^\| *<sub>\[`/ {
      n = split($0, f, "|")
      gsub(/\]\(/, "](skills/", f[2])
      printf "|%s|%s| <sub>%s</sub> |\n", f[2], f[3], by
    }
  ' "$share/skills/README.md"
  echo
  echo '스킬 제작자와 설치 방법은 [`skills/README.md`](skills/README.md). 신지은 제작 스킬의 출처는 [jieun994/zinis_claude_skills](https://github.com/jieun994/zinis_claude_skills). `ui-ux-pro-max-skill/`은 외부 스킬(MIT) 백업으로 자동 설치 대상이 아니다.'
  echo '<!-- CONTENTS:END -->'
} > "$work/contents.md"
n_agent="$(grep -c '^| <sub>\[`agent/' "$work/contents.md" || true)"
n_skill="$(find "$share/skills" -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l | tr -d ' ')"

# ── 최상단: 배치 시점 · 현재 반영본 ─────────────────────────────────────────
{
  echo '<!-- SYNC-STATUS:START — share/build-release-notes.sh 가 미러할 때마다 다시 만든다. 이 사이는 직접 고치지 않는다 -->'
  echo '| <div align="center"><sub>배치</sub></div> | <sub>시점</sub> | <sub>하는 일</sub> |'
  echo '|:---|:---:|:---|'
  echo '| <sub>원본 일일 커밋</sub> | <sub>매일 00:00</sub> | <sub>관리자 PC의 그날 작업분을 원본 리포에 커밋 · 푸시</sub> |'
  echo '| <sub>공유 리포 반영</sub> | <sub>매주 금 24:00 (토 00:10)</sub> | <sub>원본 최신본을 이 리포에 1:1 반영 · 커밋 · 푸시 — 바뀐 게 없으면 건너뜀</sub> |'
  echo '| <sub>내 PC 업데이트</sub> | <sub>매주 월 09:00</sub> | <sub>이 리포를 받아 내 Claude Code에 반영 — 아래 「처음 설치」 3)을 등록한 PC만</sub> |'
  echo
  printf '**현재 반영본** — 원본 `%s`(%s 커밋) · 하네스 %s종 · 스킬 %s종 · 릴리즈노트 %s건(최신 %s)\n' \
    "${src_sha:-?}" "${src_date:-?}" "$n_agent" "$n_skill" "$total" "$latest"
  echo '<!-- SYNC-STATUS:END -->'
} > "$work/status.md"

# README 의 표식 사이를 교체 (표식이 없으면 그대로 둔다 — RELEASE-NOTES 만 끝에 붙인다)
replace_block() {  # $1=표식 이름 $2=새 내용 파일
  if grep -q "^<!-- $1:START" "$readme"; then
    awk -v notes="$2" -v s="^<!-- $1:START" -v e="^<!-- $1:END -->" '
      $0 ~ s { while ((getline l < notes) > 0) print l; skip = 1; next }
      $0 ~ e { skip = 0; next }
      !skip { print }
    ' "$readme" > "$work/README.new" && cp "$work/README.new" "$readme"
  elif [ "$1" = "RELEASE-NOTES" ]; then
    { echo; cat "$2"; } >> "$readme"
  fi
}
replace_block SYNC-STATUS "$work/status.md"
replace_block CONTENTS "$work/contents.md"
replace_block RELEASE-NOTES "$work/notes.md"
echo "readme: 하네스 ${n_agent} · 스킬 ${n_skill} · 릴리즈노트 ${total}건 (최신 ${latest}) · 원본 ${src_sha:-?}"
