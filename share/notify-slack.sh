#!/usr/bin/env bash
# notify-slack.sh — 관리자(김단영) PC 전용
# 공유 리포에 새로 올라간 커밋을 슬랙 채널에 「MM/DD 항목 업데이트 내역」 + 불릿 형태로 게시한다.
#   bash share/notify-slack.sh                    마지막 게시 이후 커밋을 게시 (mirror-from-source.sh 가 푸시 뒤 자동 호출)
#   bash share/notify-slack.sh --dry-run          게시하지 않고 메시지만 출력
#   bash share/notify-slack.sh --since <공유 sha>  기준점을 지정 (그 커밋 다음부터)
#
# - 웹후크 URL: ~/.claude/secrets/slack-share-webhook.url (리포에 넣지 않는다). 없으면 게시하지 않고 끝낸다.
# - 상태: ~/.claude/state/share-slack-last = 마지막으로 게시한 공유 리포 커밋. 처음 실행은 기준점만 기록한다.
# - 불릿 = 원본 커밋 본문의 「- 」 줄(없으면 제목). 원본 커밋 본문 불릿은 명사형 종결로 쓴다(슬랙 문구가 된다).
# - 개인 전용 경로만 바꾼 원본 커밋(mirror-from-source.sh EXCLUDE 와 같다)은 싣지 않는다.
set -euo pipefail

share="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
src="${SOURCE_REPO:-$HOME/Documents/Claude/dykim-claude-agents-skills}"
hook_file="${SLACK_SHARE_WEBHOOK_FILE:-$HOME/.claude/secrets/slack-share-webhook.url}"
state="${SLACK_SHARE_STATE_FILE:-$HOME/.claude/state/share-slack-last}"
EXCL_RE='^(agent/danibot/|skills/danjr/|persona/|memory/|\.claude/|CLAUDE\.md$|install-global\.sh$|push-memory\.sh$)'

dry=0; since=""
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) dry=1 ;;
    --since) since="$2"; shift ;;
    *) echo "알 수 없는 인자: $1" >&2; exit 2 ;;
  esac
  shift
done

head="$(git -C "$share" rev-parse HEAD)"
if [ -z "$since" ]; then
  if [ -f "$state" ]; then
    since="$(tr -d ' \r\n' < "$state")"
  else
    mkdir -p "$(dirname "$state")"; echo "$head" > "$state"
    echo "슬랙: 기준점 기록 ${head:0:7} (이후 커밋부터 게시)"; exit 0
  fi
fi
since="$(git -C "$share" rev-parse "$since")"
[ "$since" = "$head" ] && { echo "슬랙: 새 커밋 없음"; exit 0; }

# 블록 = 항목 하나의 「MM/DD 항목 업데이트 내역」. 같은 항목이 이어지면 한 블록으로 합친다.
items=(); dates=(); bodies=(); srcs=(); shares=()
add_block() {   # item date bullets src share
  local n=${#items[@]}
  if [ "$n" -gt 0 ] && [ "${items[$((n-1))]}" = "$1" ] && [ "${shares[$((n-1))]}" = "$5" ]; then
    dates[$((n-1))]="$2"; bodies[$((n-1))]+="$3"; srcs[$((n-1))]="$4"
  else
    items+=("$1"); dates+=("$2"); bodies+=("$3"); srcs+=("$4"); shares+=("$5")
  fi
}
item_of_path() {   # agent/proposal/x → proposal · skills/foo/x → foo · global-house-style/x → global-house-style
  case "$1" in
    agent/*/*|skills/*/*) echo "$1" | cut -d/ -f2 ;;
    */*) echo "$1" | cut -d/ -f1 ;;
    *) echo "README" ;;
  esac
}
bullets_of() {   # 커밋 본문 「- 」 줄 → 「• 」, 없으면 제목(접두 뺀 것)
  local c="$1" subj="$2" b
  b="$(git -C "$src" log -1 --format=%b "$c" | tr -d '\r' | sed -n 's/^- \{1,\}/• /p')"
  if [ -n "$b" ]; then printf '%s\n' "$b"; else printf '• %s\n' "${subj#*: }"; fi
}

git -C "$src" fetch -q origin main 2>/dev/null || true
while IFS=$'\t' read -r sh_full sh subj; do
  case "$subj" in
    "mirror: 원본 "*" 반영")
      to="$(echo "$subj" | sed -n 's/^mirror: 원본 \([0-9a-f]*\) 반영$/\1/p')"
      from="$(git -C "$share" log --format=%s "$sh_full~1" 2>/dev/null | sed -n 's/^mirror: 원본 \([0-9a-f]*\) 반영$/\1/p' | head -1)"
      range="${from:+$from..}$to"; [ -n "$from" ] || range="$to~1..$to"
      while IFS=$'\t' read -r c ch cd csubj; do
        files="$(git -C "$src" diff-tree --no-commit-id --name-only -r "$c" | grep -vE "$EXCL_RE" || true)"
        [ -n "$files" ] || continue
        if [[ "$csubj" == daily:* ]]; then
          names="$(while read -r f; do item_of_path "$f"; done <<< "$files" | sort -u | paste -sd'|' - | sed 's/|/ · /g')"
          nf="$(printf '%s\n' "$files" | wc -l | tr -d ' ')"
          add_block "$names" "$cd" "• 일일 자동 커밋 반영: 파일 ${nf}개"$'\n' "$ch" "$sh"
        else
          add_block "${csubj%%: *}" "$cd" "$(bullets_of "$c" "$csubj")"$'\n' "$ch" "$sh"
        fi
      done < <(git -C "$src" log --reverse --format=$'%H\t%h\t%cd\t%s' --date=format:%m/%d "$range")
      ;;
    *)
      cd="$(git -C "$share" log -1 --format=%cd --date=format:%m/%d "$sh_full")"
      b="$(git -C "$share" log -1 --format=%b "$sh_full" | tr -d '\r' | sed -n 's/^- \{1,\}/• /p')"
      [ -n "$b" ] || b="• ${subj#*: }"
      add_block "Share-Agent-Skill-dy" "$cd" "$b"$'\n' "" "$sh"
      ;;
  esac
done < <(git -C "$share" log --reverse --format=$'%H\t%h\t%s' "$since..$head")

if [ ${#items[@]} -eq 0 ]; then
  echo "슬랙: 게시할 항목 없음 (개인 전용 변경만)"
  [ "$dry" -eq 1 ] || echo "$head" > "$state"
  exit 0
fi

msg=""
for i in "${!items[@]}"; do
  [ -n "$msg" ] && msg+=$'\n'
  msg+="*${dates[$i]} ${items[$i]} 업데이트 내역*"$'\n'"${bodies[$i]}"
  if [ -n "${srcs[$i]}" ]; then
    msg+="• 원본 리포(${srcs[$i]}) · 공유용 리포(${shares[$i]}) 커밋, GitHub 업로드 완료"$'\n'
  else
    msg+="• 공유용 리포(${shares[$i]}) 커밋, GitHub 업로드 완료"$'\n'
  fi
done

if [ "$dry" -eq 1 ]; then printf '%s' "$msg"; exit 0; fi

if [ ! -s "$hook_file" ]; then
  echo "슬랙: 웹후크 파일 없음 ($hook_file) — 게시 건너뜀"; exit 0
fi
url="$(tr -d ' \r\n' < "$hook_file")"
json_escape() { printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' -e 's/\t/ /g' | awk 'BEGIN{ORS=""} NR>1{print "\\n"} {print}'; }
payload="$(mktemp)"; trap 'rm -f "$payload"' EXIT
printf '{"text":"%s"}' "$(json_escape "$msg")" > "$payload"
resp="$(curl -sS -m 20 -X POST -H 'Content-Type: application/json; charset=utf-8' --data-binary @"$payload" "$url" || true)"
if [ "$resp" = "ok" ]; then
  echo "$head" > "$state"; echo "슬랙: 게시 완료 (블록 ${#items[@]}개)"
else
  echo "슬랙: 게시 실패 — 응답: ${resp:-없음} (다음 실행 때 다시 시도)" >&2; exit 1
fi
