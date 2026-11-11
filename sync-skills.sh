#!/usr/bin/env bash
# sync-skills.sh
# 정본 skills/ 를 각 에이전트의 .claude/skills/ 로 복사해 자동 로드하도록 한다.
# agent/<이름>/.claude/skills/ 는 .gitignore 처리되어 있으므로(생성물), 클론 후 한 번 실행한다.
#   bash:  ./sync-skills.sh
#
# 새 에이전트가 이 스킬들을 쓰려면 아래 agents 목록에 폴더명을 추가한다.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
src="$root/skills"
agents=(proposal feature-spec-sb test-runner)   # 스킬을 받을 agent/<이름> 목록

[ -d "$src" ] || { echo "정본 폴더가 없습니다: $src" >&2; exit 1; }

for a in "${agents[@]}"; do
  dst="$root/agent/$a/.claude/skills"
  rm -rf "$dst"
  mkdir -p "$dst"
  cp -r "$src/"* "$dst/"
  echo "Synced skills -> agent/$a/.claude/skills/"
  ls -1 "$dst"
done
