#!/usr/bin/env bash
# update.sh — 받는 사람 PC용 (설치 + 주간 업데이트 공용)
# 공유 리포의 최신본을 받아 이 PC의 Claude Code 에 반영한다.
#   macOS / Linux:  bash share/update.sh
#   Windows:        Git Bash 에서  bash share/update.sh
#   bash share/update.sh --force     변경이 없어도 다시 반영
#
# 반영하는 것
# - skills/<이름>/          → ~/.claude/skills/<이름>/      (이 리포가 설치한 스킬만 교체 · 삭제)
# - global-house-style/     → ~/.claude/house-style/        (house-style.css · base_template_doc.html · global-rules.md)
# - ~/.claude/CLAUDE.md     → 맨 끝에 「@~/.claude/house-style/global-rules.md」 한 줄만 추가 (기존 내용은 그대로)
# - agent/<이름>/.claude/skills/ → sync-skills.sh 로 다시 생성 (하네스용)
#
# 이 PC에 원래 있던 같은 이름의 스킬은 처음 한 번 ~/.claude/skills-backup-날짜시각/ 으로 옮겨 둔다.
# 이 리포 폴더 안의 파일을 직접 고치지 않는다 — 업데이트 때 원격 내용으로 되돌아간다.
set -euo pipefail

force=0
[ "${1:-}" = "--force" ] && force=1

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
dest="${CLAUDE_HOME:-$HOME/.claude}"
stamp="$dest/.dykim-share-installed"
manifest="$dest/skills/.dykim-share-manifest"

# 1) 받기
git -C "$repo" fetch -q origin main
cur="$(git -C "$repo" rev-parse HEAD)"
new="$(git -C "$repo" rev-parse origin/main)"
if [ "$cur" = "$new" ] && [ -f "$stamp" ] && [ "$(cat "$stamp")" = "$new" ] && [ "$force" -eq 0 ]; then
  echo "$(date '+%F %T') 변경 없음 ($(git -C "$repo" rev-parse --short HEAD))"
  exit 0
fi
git -C "$repo" reset -q --hard origin/main

mkdir -p "$dest/skills" "$dest/house-style"

# 2) 스킬
old_list=""
[ -f "$manifest" ] && old_list="$(cat "$manifest")"
is_ours() { printf '%s\n' "$old_list" | grep -qxF -- "$1"; }
backup=""
new_list=""
for d in "$repo"/skills/*/; do
  [ -d "$d" ] || continue
  name="$(basename "$d")"
  if [ -e "$dest/skills/$name" ] && ! is_ours "$name"; then
    # 이 리포가 설치한 적 없는 같은 이름 스킬 → 지우지 않고 보관
    if [ -z "$backup" ]; then backup="$dest/skills-backup-$(date +%Y%m%d-%H%M%S)"; mkdir -p "$backup"; fi
    mv "$dest/skills/$name" "$backup/"
  fi
  rm -rf "${dest:?}/skills/$name"
  cp -R "$d" "$dest/skills/$name"
  new_list="$new_list$name
"
done
# 리포에서 빠진 스킬은 이 PC에서도 뺀다 (이 리포가 설치했던 것만)
printf '%s\n' "$old_list" | while IFS= read -r name; do
  [ -n "$name" ] || continue
  printf '%s' "$new_list" | grep -qxF -- "$name" || rm -rf "${dest:?}/skills/$name"
done
printf '%s' "$new_list" > "$manifest"
n="$(printf '%s' "$new_list" | grep -c . || true)"
echo "skills ($n) -> $dest/skills/"
[ -n "$backup" ] && echo "원래 있던 같은 이름 스킬 보관 -> $backup"

# 3) 하우스 스타일 + 전역 규칙
cp "$repo/global-house-style/house-style.css" "$repo/global-house-style/base_template_doc.html" "$dest/house-style/"
cp "$repo/global-house-style/CLAUDE.md" "$dest/house-style/global-rules.md"
line='@~/.claude/house-style/global-rules.md'
touch "$dest/CLAUDE.md"
if ! grep -qxF "$line" "$dest/CLAUDE.md"; then
  printf '\n# 공유 규칙 (dykim-claude-agents-skills-share · share/update.sh 가 추가)\n%s\n' "$line" >> "$dest/CLAUDE.md"
  echo "CLAUDE.md 에 공유 규칙 불러오기 한 줄 추가"
fi
echo "house-style -> $dest/house-style/"

# 4) 하네스용 스킬 사본
bash "$repo/sync-skills.sh" >/dev/null && echo "agent/*/.claude/skills 재생성"

printf '%s' "$new" > "$stamp"
echo "$(date '+%F %T') 반영 완료 ($(git -C "$repo" log -1 --format='%h %ad' --date=short))"
