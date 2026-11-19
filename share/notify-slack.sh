#!/usr/bin/env bash
# notify-slack.sh — 관리자(김단영) PC 전용
# 공유 리포에 새로 올라간 커밋을 슬랙 채널에 「MM/DD 항목 업데이트 내역」 + 불릿 형태로 게시한다.
#   bash share/notify-slack.sh --daily            전일 기준 하루치를 한 건으로 묶어 게시 (작업 스케줄러 dykim-share-slack-daily 매일 09:10)
#   bash share/notify-slack.sh                    마지막 게시 이후 커밋을 바로 게시 (수동 · 2026-11-19부터 미러는 이 스크립트를 부르지 않는다)
#   bash share/notify-slack.sh --dry-run          게시하지 않고 메시지만 출력
#   bash share/notify-slack.sh --since <공유 sha>  기준점을 지정 (그 커밋 다음부터)
#   bash share/notify-slack.sh --daily --cutoff "YYYY-MM-DD HH:MM"   묶음 기준 시각 지정 (기본 = 오늘 01:00)
#
# 하루 1회 묶음(--daily): 마지막 게시 이후 ~ 오늘 01:00 이전 공유 리포 커밋을 「MM/DD 업데이트 내역」 한 건으로 게시.
#   01:00 기준이라 토 00:10 주간 미러(금요일 작업분)는 토요일 아침 게시에 들어가고, 01:00 뒤 커밋은 다음 날 게시.
#   같은 항목은 한 묶음으로 합치고 같은 불릿은 한 번만 싣는다. 새 커밋이 없으면 게시하지 않는다.
#   PC가 꺼져 하루를 건너뛰면 다음 실행 때 밀린 날짜까지 한 건으로(「MM/DD~MM/DD 업데이트 내역」).
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

dry=0; since=""; daily=0; cutoff=""
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) dry=1 ;;
    --daily) daily=1 ;;
    --cutoff) cutoff="$2"; shift ;;
    --since) since="$2"; shift ;;
    *) echo "알 수 없는 인자: $1" >&2; exit 2 ;;
  esac
  shift
done

head="$(git -C "$share" rev-parse HEAD)"
if [ "$daily" -eq 1 ]; then
  git -C "$share" fetch -q origin 2>/dev/null || true
  ref="$(git -C "$share" rev-parse -q --verify origin/main || git -C "$share" rev-parse HEAD)"
  [ -n "$cutoff" ] || cutoff="$(date '+%Y-%m-%d') 01:00"
  head="$(git -C "$share" log -1 --before="$cutoff" --format=%H "$ref")"
  [ -n "$head" ] || { echo "슬랙: 기준 시각($cutoff) 이전 커밋 없음"; exit 0; }
fi
if [ -z "$since" ]; then
  if [ -f "$state" ]; then
    since="$(tr -d ' \r\n' < "$state")"
  else
    mkdir -p "$(dirname "$state")"; echo "$head" > "$state"
    echo "슬랙: 기준점 기록 ${head:0:7} (이후 커밋부터 게시)"; exit 0
  fi
fi
since="$(git -C "$share" rev-parse "$since")"
if [ "$since" = "$head" ] || git -C "$share" merge-base --is-ancestor "$head" "$since" 2>/dev/null; then
  echo "슬랙: 새 커밋 없음"; exit 0
fi

# 블록 = 항목 하나의 「MM/DD 항목 업데이트 내역」. 같은 항목이 이어지면 한 블록으로 합친다.
items=(); dates=(); bodies=(); srcs=(); shares=()
add_block() {   # item date bullets src share
  local n=${#items[@]} i line
  if [ "$daily" -eq 1 ]; then   # 하루 묶음: 같은 항목은 어디서 나와도 한 묶음, 같은 불릿은 한 번만
    for ((i = 0; i < n; i++)); do
      [ "${items[$i]}" = "$1" ] || continue
      while IFS= read -r line; do
        [ -n "$line" ] || continue
        grep -qxF -- "$line" <<< "${bodies[$i]}" || bodies[$i]+="$line"$'\n'
      done <<< "$3"
      dates[$i]="$2"; shares[$i]="$5"; [ -z "$4" ] || srcs[$i]="$4"
      return
    done
    items+=("$1"); dates+=("$2"); bodies+=("$3"); srcs+=("$4"); shares+=("$5"); return
  fi
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
# 부분 반영(mirror(<폴더>): …)으로 이미 실은 원본 커밋 — 뒤 전체 미러 범위에서 다시 싣지 않는다
partial_done="$(git -C "$share" log --format=%b "$head" | tr -d '\r' | sed -n 's/^원본 커밋: \([0-9a-f]\{40\}\)$/\1/p')"
while IFS=$'\t' read -r sh_full sh subj; do
  case "$subj" in
    "mirror("*"): 원본 "*" 반영")
      c="$(git -C "$share" log -1 --format=%b "$sh_full" | tr -d '\r' | sed -n 's/^원본 커밋: \([0-9a-f]\{40\}\)$/\1/p' | awk 'NR==1')"
      [ -n "$c" ] || c="$(echo "$subj" | sed -n 's/^mirror([^)]*): 원본 \([0-9a-f]*\) 반영$/\1/p')"
      if git -C "$src" cat-file -e "$c^{commit}" 2>/dev/null; then
        csubj="$(git -C "$src" log -1 --format=%s "$c")"
        cd="$(git -C "$src" log -1 --format=%cd --date=format:%m/%d "$c")"
        add_block "${csubj%%: *}" "$cd" "$(bullets_of "$c" "$csubj")"$'\n' "$(git -C "$src" rev-parse --short "$c")" "$sh"
      fi
      ;;
    "mirror: 원본 "*" 반영")
      to="$(echo "$subj" | sed -n 's/^mirror: 원본 \([0-9a-f]*\) 반영$/\1/p')"
      from="$(git -C "$share" log --format=%s "$sh_full~1" 2>/dev/null | sed -n 's/^mirror: 원본 \([0-9a-f]*\) 반영$/\1/p' | head -1)"
      range="${from:+$from..}$to"; [ -n "$from" ] || range="$to~1..$to"
      last_src="$to"
      while IFS=$'\t' read -r c ch cd csubj; do
        grep -qxF -- "$c" <<< "$partial_done" && continue
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
if [ "$daily" -eq 1 ]; then
  # 날짜 = 공유 리포 커밋 시각 - 1시간(00:10 주간 미러 = 전날 작업분) 의 첫날 ~ 끝날
  days="$(git -C "$share" log --format=%ct "$since..$head" | while read -r t; do date -d "@$((t - 3600))" +%m/%d; done | sort -u)"
  d_from="$(head -1 <<< "$days")"; d_to="$(tail -1 <<< "$days")"
  label="$d_from"; [ "$d_from" = "$d_to" ] || label="${d_from}~${d_to}"
  msg="*${label} 업데이트 내역* (전일 기준 · 하루 1회 묶음)"$'\n'
  for i in "${!items[@]}"; do msg+=$'\n'"*${items[$i]}*"$'\n'"${bodies[$i]}"; done
  ref_line="공유용 리포($(git -C "$share" rev-parse --short "$head"))"
  [ -z "${last_src:-}" ] || ref_line="원본 리포(${last_src}) · ${ref_line}"
  msg+=$'\n'"• ${ref_line}까지 반영, GitHub 업로드 완료"$'\n'
fi
[ "$daily" -eq 1 ] || for i in "${!items[@]}"; do
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
  echo "$head" > "$state"
  if [ "$daily" -eq 1 ]; then echo "슬랙: 하루치 묶음 게시 완료 (${label} · 항목 ${#items[@]}개)"; else echo "슬랙: 게시 완료 (블록 ${#items[@]}개)"; fi
else
  echo "슬랙: 게시 실패 — 응답: ${resp:-없음} (다음 실행 때 다시 시도)" >&2; exit 1
fi
