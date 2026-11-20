#!/usr/bin/env bash
# mirror-from-source.sh — 관리자(김단영) PC 전용
# 원본 리포 dykim-claude-agents-skills 의 origin/main 을 이 공유용 리포에 1:1로 반영한다.
#   bash share/mirror-from-source.sh [원본 클론 경로]      기본값 ~/Documents/Claude/dykim-claude-agents-skills
#   bash share/mirror-from-source.sh --no-push             반영·커밋만 하고 푸시하지 않는다 (확인용)
#   bash share/mirror-from-source.sh --only <폴더>         그 폴더만 원본 최신본으로 반영 (부분 반영)
#
# - 원본에 푸시된 내용(origin/main)만 옮긴다. 원본 작업 폴더의 미커밋 변경은 나가지 않는다.
# - 제외: 개인 전용(Dan Jr. · 페르소나 · 단이bot · 메모리 · PC 동기화 스크립트 · 인수인계 파일)
# - 공유 리포 고유 파일(README.md · share/)은 원본에 없어도 지우지 않는다.
# - 원본에서 지운 파일은 공유 리포에서도 지운다.
# - 슬랙 채널 게시는 하지 않는다 — 매일 09:10 share/notify-slack.sh --daily 가 전일분을 한 건으로 묶어 게시(2026-11-19 변경)
# - 부분 반영(--only, 2026-11-19 신설): 외부 스킬 원본 깃허브 일일 동기화(~/.claude/tools/uiux-upstream-sync.sh)가
#   skills/ui-ux-pro-max-skill 만 그날 바로 반영할 때 쓴다(2026-11-20부터 im-not-ai 주간 동기화도 skills/im-not-ai 로). 나머지 폴더는 주간 전체 미러 몫.
# - 심볼릭 링크(2026-11-20): Windows 에서도 원본 트리의 링크를 링크로 유지(아래 2b)
#   커밋 = 「mirror(<폴더 이름>): 원본 <sha> 반영」 + 본문 「원본 커밋: <전체 sha>」(notify-slack.sh 가 중복 게시를 막는 데 사용).
#   README 자동 영역의 「현재 반영본」은 마지막 전체 미러 기준을 유지하고 릴리즈노트만 새로 모은다.
set -euo pipefail

no_push=0
only=""
args=()
while [ $# -gt 0 ]; do
  case "$1" in
    --no-push) no_push=1 ;;
    --only) only="${2%/}"; shift ;;
    *) args+=("$1") ;;
  esac
  shift
done

share="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
src="${args[0]:-$HOME/Documents/Claude/dykim-claude-agents-skills}"
[ -d "$src/.git" ] || { echo "원본 클론이 없습니다: $src" >&2; exit 1; }

# 원본에서 빼는 경로 (공유 대상 아님)
EXCLUDE=(
  agent/danibot          # 단이bot
  skills/danjr           # Dan Jr. 판정 스킬
  persona                # Dan Jr. 페르소나
  memory                 # 개인 메모리
  .claude                # PC 간 인수인계(HANDOFF.md)
  CLAUDE.md              # 원본 리포 작업 규칙(인수인계·메모리 안내)
  README.md              # 원본 README — 공유 리포는 자체 README 사용
  install-global.sh      # 원본 PC 동기화용 — 공유 리포는 share/update.sh 사용
  push-memory.sh         # 메모리 올리기
)
# 공유 리포에만 있는 파일 (미러가 지우지 않음)
OWN_RE='^(README\.md|share/)'

# 1) 공유 리포를 원격 최신으로 맞춘다 (다른 PC에서 먼저 미러했어도 충돌 없이)
if git -C "$share" remote get-url origin >/dev/null 2>&1; then
  git -C "$share" fetch -q origin
  if git -C "$share" rev-parse -q --verify origin/main >/dev/null; then
    git -C "$share" reset -q --hard origin/main
  fi
fi

# 2) 원본 origin/main 을 임시 폴더로 꺼낸다
git -C "$src" fetch -q origin main
src_sha="$(git -C "$src" rev-parse --short origin/main)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
git -C "$src" archive origin/main | tar -x -C "$tmp"
src_readme="$(mktemp)"
trap 'rm -rf "$tmp" "$src_readme"' EXIT
cp "$tmp/README.md" "$src_readme" 2>/dev/null || : > "$src_readme"   # 릴리즈노트 생성용 (README 자체는 제외 대상)
for p in "${EXCLUDE[@]}"; do rm -rf "${tmp:?}/$p"; done

# 2b) 심볼릭 링크 복원 준비 (2026-11-20 · 외부 스킬 im-not-ai 의 codex/skills/humanize-korean/references 등)
#     Windows(core.symlinks=false)에선 tar · cp 가 링크를 대상 폴더 사본으로 풀어 공유 리포에 엉뚱한 폴더가 생긴다.
#     원본 트리의 링크(모드 120000)를 「링크 대상 경로를 담은 작은 파일 + 인덱스 모드 120000」으로 되돌린다(git 의 Windows 체크아웃과 같은 모양).
#     리눅스(클라우드)는 tar · cp 가 링크를 그대로 두므로 건너뛴다.
links="$(mktemp)"
trap 'rm -rf "$tmp" "$src_readme" "$links"' EXIT
if [ "$(git -C "$share" config --bool core.symlinks 2>/dev/null || echo true)" = false ]; then
  git -C "$src" -c core.quotepath=off ls-tree -r origin/main ${only:+-- "$only"} \
    | awk -F'\t' '{ split($1, a, " "); if (a[1] == "120000") print a[3] "\t" $2 }' \
    | while IFS="$(printf '\t')" read -r sha path; do
        skip=0; for p in "${EXCLUDE[@]}"; do case "$path" in "$p"|"$p"/*) skip=1 ;; esac; done
        [ "$skip" -eq 1 ] || printf '%s\t%s\n' "$sha" "$path"
      done > "$links"
fi
fix_links_tree() {   # 복사 직후: 사본 폴더를 지우고 링크 대상 경로 파일로
  while IFS="$(printf '\t')" read -r sha path; do
    [ -n "$path" ] || continue
    rm -rf "${share:?}/$path"; mkdir -p "$(dirname "$share/$path")"
    git -C "$src" cat-file blob "$sha" > "$share/$path"
  done < "$links"
}
fix_links_index() {  # git add 직후: 인덱스 모드를 링크(120000)로
  while IFS="$(printf '\t')" read -r sha path; do
    [ -n "$path" ] || continue
    [ "$(git -C "$share" hash-object -w -- "$path")" = "$sha" ] || { echo "링크 복원 실패: $path" >&2; exit 1; }
    git -C "$share" update-index --add --cacheinfo "120000,$sha,$path"
  done < "$links"
}

# 3) 전역 규칙에서 Dan Jr. 조항을 뺀다 (하우스 스타일 · 문체 · 파일명 · 창 위치 · 수정 이력 규칙은 유지)
rules="$tmp/global-house-style/CLAUDE.md"
if [ -f "$rules" ]; then
  awk '
    /^# 전역 규칙 — Dan Jr\./ { skip=1; next }
    /^# / { skip=0 }
    skip { next }
    /^- Dan Jr\. 등급:/ { next }
    { print }
  ' "$rules" | sed 's#dykim-claude-agents-skills/agent/#Share-Agent-Skill-dy/agent/#g' > "$rules.tmp"
  mv "$rules.tmp" "$rules"
fi

# 4) 원본에 없는 파일은 공유 리포에서도 지운다 (공유 리포 고유 파일 제외)
cd "$share"
if [ -n "$only" ]; then
  # 부분 반영: 그 폴더 안에서만 지우고 덮어쓴다
  case "$only" in /*|*..*) echo "--only 는 리포 안 상대 경로만: $only" >&2; exit 2 ;; esac
  for p in "${EXCLUDE[@]}"; do
    case "$only" in "$p"|"$p"/*) echo "--only 대상이 공유 제외 경로입니다: $only" >&2; exit 2 ;; esac
  done
  git -c core.quotepath=off ls-files -- "$only" | while IFS= read -r f; do
    if [ ! -e "$tmp/$f" ]; then git rm -q -f -- "$f"; fi
  done
  if [ -d "$tmp/$only" ]; then mkdir -p "$share/$only"; cp -R "$tmp/$only/." "$share/$only/"; fi
  fix_links_tree
  # 「현재 반영본」은 마지막 전체 미러 기준 유지, 릴리즈노트 · 목록만 다시 모은다
  only_full="$(git -C "$src" log -1 --format=%H origin/main -- "$only")"
  only_sha="$(git -C "$src" rev-parse --short "$only_full")"
  last_full="$(git log --format=%s | sed -n 's/^mirror: 원본 \([0-9a-f]*\) 반영$/\1/p' | awk 'NR==1')"   # head 는 SIGPIPE → pipefail 로 중단될 수 있어 awk
  if [ -n "$last_full" ] && git -C "$src" cat-file -e "$last_full^{commit}" 2>/dev/null; then
    git -C "$src" show "$last_full:README.md" > "$src_readme" 2>/dev/null || : > "$src_readme"
    last_date="$(git -C "$src" log -1 --format=%cd --date=format:%Y.%m.%d "$last_full")"
    bash "$share/share/build-release-notes.sh" "$src_readme" "$last_full" "$last_date"
  fi
  git add -A -- "$only" README.md
  fix_links_index
  if git diff --cached --quiet; then
    echo "변경 없음 ($only · 원본 $only_sha)"
    exit 0
  fi
  git commit -q -F - <<EOF
mirror($(basename "$only")): 원본 $only_sha 반영

원본 커밋: $only_full
범위: $only (부분 반영 — 나머지 폴더는 주간 전체 미러)
EOF
  echo "반영 -> $(git log -1 --format='%h %s')"
  git diff --stat HEAD~1 HEAD 2>/dev/null | tail -1 || true
  if [ "$no_push" -eq 0 ]; then
    git push -q origin HEAD:main
    echo "푸시 완료"
    echo "슬랙: 다음 09:10 하루치 묶음 게시 예정"
  fi
  exit 0
fi
git -c core.quotepath=off ls-files | { grep -vE "$OWN_RE" || true; } | while IFS= read -r f; do
  if [ ! -e "$tmp/$f" ]; then
    git rm -q -f -- "$f"
  fi
done

# 5) 덮어쓰기 + 커밋
cp -R "$tmp/." "$share/"
fix_links_tree
src_date="$(git -C "$src" log -1 --format=%cd --date=format:%Y.%m.%d origin/main)"
bash "$share/share/build-release-notes.sh" "$src_readme" "$src_sha" "$src_date"
git add -A
fix_links_index
if git diff --cached --quiet; then
  echo "변경 없음 (원본 $src_sha)"
  echo "슬랙: 새 반영 없음 — 게시 대상 아님"
  exit 0
fi
git commit -q -m "mirror: 원본 $src_sha 반영"
echo "반영 -> $(git log -1 --format='%h %s')"
git diff --stat HEAD~1 HEAD 2>/dev/null | tail -1 || true

if [ "$no_push" -eq 0 ]; then
  git push -q origin HEAD:main
  echo "푸시 완료"
  # 슬랙 채널 게시는 바로 하지 않고 매일 09:10 하루치 묶음으로 (작업 스케줄러 dykim-share-slack-daily)
  echo "슬랙: 다음 09:10 하루치 묶음 게시 예정"
fi
