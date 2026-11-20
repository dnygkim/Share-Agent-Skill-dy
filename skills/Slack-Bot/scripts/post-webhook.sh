#!/usr/bin/env bash
# post-webhook.sh — 슬랙 Incoming Webhook 으로 메시지 한 건 게시
#
#   bash post-webhook.sh <웹후크 파일> <메시지 파일>             게시
#   bash post-webhook.sh <웹후크 파일> -                         표준입력의 메시지를 게시
#   bash post-webhook.sh <웹후크 파일> <메시지 파일> --dry-run   게시하지 않고 보낼 JSON 만 출력
#
# - 웹후크 파일: URL 한 줄이 든 파일 (예 ~/.claude/secrets/my-bot-webhook.url). URL 은 출력하지 않는다.
# - 메시지: 슬랙 mrkdwn 텍스트, UTF-8 (*굵게* · 「• 」 불릿 · <https://주소|링크 문구>)
# - 결과: 슬랙 응답이 ok 면 exit 0 · 아니면 응답을 stderr 로 내고 exit 1
set -euo pipefail

if [ $# -lt 2 ]; then
  sed -n '2,11p' "$0" >&2; exit 2
fi
hook_file="$1"; msg_src="$2"; dry=0
[ "${3:-}" = "--dry-run" ] && dry=1

if [ "$msg_src" = "-" ]; then msg="$(cat)"; else msg="$(cat "$msg_src")"; fi
msg="$(printf '%s' "$msg" | tr -d '\r')"
[ -n "$msg" ] || { echo "메시지가 비어 있음" >&2; exit 2; }

# JSON 문자열로 바꾸기: 역슬래시 · 큰따옴표 이스케이프, 탭은 공백, 줄바꿈은 \n
json_escape() {
  printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' -e 's/\t/ /g' \
    | awk 'BEGIN{ORS=""} NR>1{print "\\n"} {print}'
}
payload="$(mktemp)"; trap 'rm -f "$payload"' EXIT
printf '{"text":"%s"}' "$(json_escape "$msg")" > "$payload"

if [ "$dry" -eq 1 ]; then cat "$payload"; echo; exit 0; fi

[ -s "$hook_file" ] || { echo "웹후크 파일 없음: $hook_file" >&2; exit 1; }
url="$(tr -d ' \r\n' < "$hook_file")"
resp="$(curl -sS -m 20 -X POST -H 'Content-Type: application/json; charset=utf-8' \
        --data-binary @"$payload" "$url" || true)"
if [ "$resp" = "ok" ]; then
  echo "게시 완료"
else
  echo "게시 실패 — 슬랙 응답: ${resp:-없음}" >&2; exit 1
fi
