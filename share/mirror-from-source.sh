#!/usr/bin/env bash
# mirror-from-source.sh — 관리자(김단영) PC 전용
# 원본 리포 dykim-claude-agents-skills 의 origin/main 을 이 공유용 리포에 1:1로 반영한다.
#   bash share/mirror-from-source.sh [원본 클론 경로]      기본값 ~/Documents/Claude/dykim-claude-agents-skills
#   bash share/mirror-from-source.sh --no-push             반영·커밋만 하고 푸시하지 않는다 (확인용)
#
# - 원본에 푸시된 내용(origin/main)만 옮긴다. 원본 작업 폴더의 미커밋 변경은 나가지 않는다.
# - 제외: 개인 전용(Dan Jr. · 페르소나 · 단이bot · 메모리 · PC 동기화 스크립트 · 인수인계 파일)
# - 공유 리포 고유 파일(README.md · share/)은 원본에 없어도 지우지 않는다.
# - 원본에서 지운 파일은 공유 리포에서도 지운다.
set -euo pipefail

no_push=0
args=()
for a in "$@"; do
  if [ "$a" = "--no-push" ]; then no_push=1; else args+=("$a"); fi
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
git -c core.quotepath=off ls-files | { grep -vE "$OWN_RE" || true; } | while IFS= read -r f; do
  if [ ! -e "$tmp/$f" ]; then
    git rm -q -f -- "$f"
  fi
done

# 5) 덮어쓰기 + 커밋
cp -R "$tmp/." "$share/"
src_date="$(git -C "$src" log -1 --format=%cd --date=format:%Y.%m.%d origin/main)"
bash "$share/share/build-release-notes.sh" "$src_readme" "$src_sha" "$src_date"
git add -A
if git diff --cached --quiet; then
  echo "변경 없음 (원본 $src_sha)"
  # 직전 게시가 실패했으면 여기서 다시 시도 (웹후크가 없으면 건너뜀)
  [ "$no_push" -eq 1 ] || bash "$share/share/notify-slack.sh" || echo "슬랙 게시 실패 — 미러는 정상" >&2
  exit 0
fi
git commit -q -m "mirror: 원본 $src_sha 반영"
echo "반영 -> $(git log -1 --format='%h %s')"
git diff --stat HEAD~1 HEAD 2>/dev/null | tail -1 || true

if [ "$no_push" -eq 0 ]; then
  git push -q origin HEAD:main
  echo "푸시 완료"
  # 슬랙 채널에 「MM/DD 항목 업데이트 내역」 게시 (share/notify-slack.sh · 웹후크가 없으면 건너뜀)
  bash "$share/share/notify-slack.sh" || echo "슬랙 게시 실패 — 미러는 정상" >&2
fi
