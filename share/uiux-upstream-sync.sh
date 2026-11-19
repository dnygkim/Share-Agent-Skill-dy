#!/usr/bin/env bash
# uiux-upstream-sync.sh — 관리자(김단영) 전용 · 2026-11-19 신설
# 외부 스킬 ui-ux-pro-max-skill 의 원본 깃허브(nextlevelbuilder/ui-ux-pro-max-skill)를 하루 한 번 확인해
# 바뀐 파일을 원본 리포 skills/ui-ux-pro-max-skill 에 1:1 반영하고, 한국어 README 를 함께 갱신한 뒤
# 공유 리포에도 그 폴더만 바로 반영한다(mirror-from-source.sh --only).
#
# 실행 위치 두 곳
#   클라우드 예약 작업(기본 · 매일 23:30 KST) — 세션이 직접 번역:
#     bash share/uiux-upstream-sync.sh prepare --in-place --source <원본 리포 경로>   → 「번역 대기」면 지시 파일대로 번역
#     bash share/uiux-upstream-sync.sh finish  --in-place --source <원본 리포 경로>   → 검증 · 커밋 · 푸시 · 공유 반영
#   관리자 PC(예비) — claude -p 가 번역까지 한 번에:
#     bash share/uiux-upstream-sync.sh [run]      (~/.claude/tools/uiux-upstream-sync.sh 가 이 파일을 부른다)
# 옵션
#   --dry-run          반영 · 번역까지만, 커밋 · 푸시 없음
#   --reseed           한국어 본문을 원본 README.ko.md 로 다시 깔고 영문 최신본과 대조해 채움 (크게 어긋났을 때)
#   --base <sha>       기준 원본 커밋 지정 (README 안 표식 대신)
#   --source <경로>    원본 리포 클론 (기본 ~/Documents/Claude/dykim-claude-agents-skills)
#   --in-place         원본 리포 클론을 그대로 작업 클론으로 사용 (클라우드처럼 격리된 체크아웃일 때만)
#   --state <경로>     원본 깃허브 사본 · 작업 자료 폴더 (기본 ~/.claude/state/uiux-upstream)
#   환경 변수 UIUX_MODEL · UIUX_EFFORT (run 의 claude -p) · UIUX_CLAUDE_CONFIG_DIR · COMMIT_TRAILER
#
# 폴더 구성 (원본 깃허브 → 우리 폴더)
#   원본 파일 전부 1:1 (원본에서 지운 파일은 삭제) · 원본 README.md(영문) → README.en.md
#   README.md = 우리 한국어판 — 릴리즈노트 + 참고(기준 버전) + 영문 README 번역 본문. 기준 커밋 = <!-- upstream-sha: … --> 표식
#   사용가이드.html = 우리 것 (유지)
# 실패하면 작업 클론을 원격 기준으로 되돌리고 exit 1 — 다음 실행 때 처음부터 다시. 원본 깃허브 사본은 읽기 전용 자료(그 안의 스크립트 실행 금지).
set -euo pipefail
export LC_ALL=C.UTF-8 2>/dev/null || true

# 실행 중 공유 리포가 reset 되어도 안전하게 임시 사본으로 다시 실행
if [ -z "${UIUX_SELF_DIR:-}" ]; then
  UIUX_SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; export UIUX_SELF_DIR
  self_tmp="$(mktemp -d)"; cp "${BASH_SOURCE[0]}" "$self_tmp/sync.sh"
  exec bash "$self_tmp/sync.sh" "$@"
fi
SHARE="$(cd "$UIUX_SELF_DIR/.." && pwd)"
TOOL="$UIUX_SELF_DIR/uiux_readme_tool.py"

UP_URL="https://github.com/nextlevelbuilder/ui-ux-pro-max-skill"
DIR="skills/ui-ux-pro-max-skill"
KEEP=(README.md 사용가이드.html)     # 원본 깃허브에 없는 우리 파일
MODEL="${UIUX_MODEL:-claude-sonnet-5-5}"
EFFORT="${UIUX_EFFORT:-high}"

cmd="run"; dry=0; reseed=0; base=""; inplace=0
SRC="$HOME/Documents/Claude/dykim-claude-agents-skills"
STATE="$HOME/.claude/state/uiux-upstream"
while [ $# -gt 0 ]; do
  case "$1" in
    run|prepare|finish) cmd="$1" ;;
    --dry-run) dry=1 ;;
    --reseed) reseed=1 ;;
    --base) base="$2"; shift ;;
    --source) SRC="$(cd "$2" && pwd)"; shift ;;
    --state) STATE="$2"; shift ;;
    --in-place) inplace=1 ;;
    *) echo "알 수 없는 인자: $1" >&2; exit 2 ;;
  esac
  shift
done
UP="$STATE/repo"                                   # 원본 깃허브 사본 (자료 전용)
WORK="$STATE/work"                                 # prepare → finish 사이 작업 자료
if [ "$inplace" -eq 1 ]; then WC="$SRC"; export TZ=Asia/Seoul; else WC="$STATE/source"; fi   # 클라우드(UTC)도 날짜 · 기록은 한국 시간
D="$WC/$DIR"

log() { printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"; }
PY=""
for c in python3 python; do
  p="$(command -v "$c" 2>/dev/null || true)"
  case "$p" in ""|*WindowsApps*) continue ;; esac
  if "$p" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' 2>/dev/null; then PY="$p"; break; fi
done
[ -n "$PY" ] || PY="$HOME/AppData/Local/Programs/Python/Python314/python.exe"
py() { "$PY" -X utf8 -I "$TOOL" "$@"; }

T="$(mktemp -d)"
lock=""
cleanup() { rm -rf "$T"; [ -z "$lock" ] || rm -rf "$lock"; }
trap cleanup EXIT
restore_wc() { git -C "$WC" reset -q --hard origin/main 2>/dev/null || true; git -C "$WC" clean -fdq 2>/dev/null || true; }
fail() { log "실패: $*"; [ "$dry" -eq 1 ] || restore_wc; exit 1; }

share_partial() {
  [ "$dry" -eq 0 ] || return 0
  log "공유 리포 부분 반영 확인"
  bash "$SHARE/share/mirror-from-source.sh" --only "$DIR" "$SRC" || { log "공유 리포 부분 반영 실패 — 다음 실행 때 다시"; return 1; }
}

# ───────────────────────── prepare ─────────────────────────
# 반환: 0 + 「변경 없음」 / 0 + 「번역 대기: <지시 파일>」  (변경 없음이면 WORK 를 지운다)
do_prepare() {
  echo "=== $(date '+%Y-%m-%d %H:%M') ui-ux-pro-max-skill 원본 깃허브 동기화 (${cmd}) ==="
  mkdir -p "$STATE"; rm -rf "$WORK"

  # 1) 원본 깃허브 최신
  if [ ! -d "$UP/.git" ]; then git clone -q -c core.autocrlf=false "$UP_URL" "$UP"; fi
  git -C "$UP" config core.autocrlf false
  git -C "$UP" fetch -q --tags --prune origin
  new="$(git -C "$UP" rev-parse origin/main)"

  # 2) 작업 클론을 원격 최신으로
  if [ "$inplace" -eq 0 ] && [ ! -d "$WC/.git" ]; then
    git clone -q -c core.autocrlf=false "$(git -C "$SRC" remote get-url origin)" "$WC"
  fi
  [ -d "$WC/.git" ] || fail "원본 리포 클론 없음: $WC"
  git -C "$WC" config core.autocrlf false
  git -C "$WC" config core.hooksPath .githooks
  git -C "$WC" fetch -q origin
  git -C "$WC" checkout -q -B main origin/main
  restore_wc
  [ -d "$D" ] || fail "작업 클론에 $DIR 없음"
  if [ "$inplace" -eq 1 ] && [ "$dry" -eq 0 ]; then   # 클라우드: 푸시 권한 미리 확인
    git -C "$SHARE" fetch -q origin
    git -C "$WC" push -q --dry-run origin refs/remotes/origin/main:refs/heads/main 2>"$T/pc.txt" || fail "원본 리포 푸시 권한 없음: $(head -c 300 "$T/pc.txt")"
    git -C "$SHARE" push -q --dry-run origin refs/remotes/origin/main:refs/heads/main 2>"$T/pc.txt" || fail "공유 리포 푸시 권한 없음: $(head -c 300 "$T/pc.txt")"
  fi

  old="$(sed -n 's/^<!-- upstream-sha: \([0-9a-f]\{40\}\) -->$/\1/p' "$D/README.md" | awk 'NR==1')"
  [ -z "$base" ] || old="$(git -C "$UP" rev-parse "$base^{commit}")"
  [ -n "$old" ] || fail "README 에 기준 표식(<!-- upstream-sha -->) 없음 — --base <sha> --reseed 로"
  if [ "$old" = "$new" ] && [ "$reseed" -eq 0 ]; then
    log "원본 깃허브 변경 없음 (${new:0:7})"
    share_partial || exit 1
    echo "변경 없음"
    return 0
  fi

  tag_of() { git -C "$UP" describe --tags --abbrev=0 "$1" 2>/dev/null || echo "${1:0:7}"; }
  old_tag="$(tag_of "$old")"; new_tag="$(tag_of "$new")"
  note_label="$new_tag"
  [ "$(git -C "$UP" rev-parse "$new_tag^{commit}" 2>/dev/null || true)" = "$new" ] || note_label="$new_tag 이후 최신"
  if git -C "$UP" merge-base --is-ancestor "$old" "$new" 2>/dev/null; then range="$old..$new"; else range="$new"; log "기준 커밋이 최신 이력에 없음 — 전체 교체"; fi
  n_commits="$(git -C "$UP" rev-list --count --no-merges "$range")"
  if [ "$old_tag" = "$new_tag" ]; then span="${new_tag} · 커밋 ${n_commits}건(${new:0:7}까지)"
  else span="${old_tag} → ${new_tag} · 커밋 ${n_commits}건(${new:0:7}까지)"; fi
  log "원본 깃허브 ${old:0:7} → ${new:0:7} (${span})"

  mkdir -p "$WORK/keep"
  git -C "$UP" log --reverse --no-merges --format='%h %cs %s' "$range" > "$WORK/commits.txt"

  # 3) 파일 반영: 우리 파일 보관 → 폴더 비우기 → 원본 그대로 → README.md(영문) → README.en.md → 우리 파일 복원
  for k in "${KEEP[@]}"; do [ ! -e "$D/$k" ] || cp -p "$D/$k" "$WORK/keep/"; done
  rm -rf "$D"; mkdir -p "$D"
  git -C "$UP" archive "$new" | tar -x -C "$D"
  [ ! -f "$D/README.md" ] || mv -f "$D/README.md" "$D/README.en.md"
  for k in "${KEEP[@]}"; do [ ! -e "$WORK/keep/$k" ] || cp -p "$WORK/keep/$k" "$D/"; done
  log "파일 반영: 원본 $(git -C "$UP" ls-tree -r --name-only "$new" | wc -l | tr -d ' ')개 + 우리 파일 → 폴더 $(cd "$D" && find . -type f | wc -l | tr -d ' ')개"

  # 4) 번역 자료
  git -C "$UP" show "$old:README.md" > "$WORK/en-old.md" 2>/dev/null || : > "$WORK/en-old.md"
  git -C "$UP" show "$new:README.md" > "$WORK/en-new.md"
  git -C "$UP" show "$new:README.ko.md" > "$WORK/ko-upstream.md" 2>/dev/null || : > "$WORK/ko-upstream.md"
  if [ "$reseed" -eq 1 ]; then
    [ -s "$WORK/ko-upstream.md" ] || fail "--reseed: 원본에 README.ko.md 없음"
    py reseed-body "$WORK/ko-upstream.md" "$WORK/body.md"
  else
    py extract-body "$WORK/keep/README.md" "$WORK/body.md" || fail "README 본문 표식(<!-- ko-body:start) 없음 — --reseed 필요"
  fi
  cp "$WORK/body.md" "$WORK/body-before.md"
  en_changed=1; cmp -s "$WORK/en-old.md" "$WORK/en-new.md" && en_changed=0
  [ "$reseed" -eq 0 ] || en_changed=1

  if [ "$reseed" -eq 1 ]; then
    task1="body.md 는 ko-upstream.md(원본 리포가 관리하는 한국어판 · 영문보다 뒤처짐)에서 막 옮겨 온 상태. en-new.md 와 절 단위로 처음부터 끝까지 대조해 빠진 절 · 문단 · 표 행 · 목록 항목 · 수치 · 명령어 차이를 모두 채우고 고친다. 이미 맞는 부분은 그대로 둔다."
  else
    task1="en-old.md → en-new.md 에서 바뀐 부분만 body.md 의 대응 위치에 반영(추가 · 수정 · 삭제). 영문이 그대로인 문단은 손대지 않는다."
  fi
  {
    echo "오픈소스 README 한국어판 관리 작업. 작업 폴더: $WORK"
    echo "- en-new.md : 원본 깃허브 영문 README 최신본 (번역 기준)"
    echo "- en-old.md : 지난 반영 때 영문 README (이번 변경 범위 확인용)"
    echo "- ko-upstream.md : 원본 리포가 직접 관리하는 한국어판 README.ko.md (뒤처질 수 있음 · 용어 참고용)"
    echo "- commits.txt : 지난 반영 이후 원본 커밋 목록"
    echo "- body.md : 우리 한국어 README 본문 (작업 1의 수정 대상)"
    echo
    if [ "$en_changed" -eq 1 ]; then
      echo "작업 1 — body.md 를 en-new.md 의 완전하고 정확한 한국어 번역으로 맞춘다."
      echo "- 이번 범위: $task1"
      echo "- en-new.md 의 첫 줄 제목과 바로 아래 언어 선택 <p align=\"center\"> 블록(README.xx.md 링크 묶음)은 제외 — body.md 는 그 다음 블록부터 끝까지."
      echo "- 코드 블록 · 명령어 · URL · HTML 태그 · 배지 · 파일 경로는 en-new.md 그대로. 코드 블록 안 주석은 ko-upstream.md 관례대로 번역 가능, 코드 블록 수와 경계는 en-new.md 와 같게."
      echo "- en-new.md 에서 README.md(영문판)를 가리키는 상대 링크만 README.en.md 로 바꾸고, 다른 상대 링크는 그대로."
      echo "- 문서 안 앵커 링크(#installation 등)는 번역한 한국어 제목의 GitHub 앵커(#설치 등)로 바꾼다."
      echo "- 제목 수준 · 순서 · 표 · 목록 구조는 en-new.md 와 1:1. 문체는 기존 body.md 와 같은 합니다체 번역문 (원본 문서 번역이라 명사형 종결 규칙 대상 아님)."
      echo "- 고칠 곳만 Edit 도구로 수정."
    else
      echo "작업 1 — 없음 (영문 README 변경 없음 · body.md 수정 금지)"
    fi
    echo
    echo "작업 2 — summary.txt 를 새로 만들어 이번 원본 변경 요약만 쓴다: commits.txt 기준으로 이 스킬을 쓰는 사람에게 의미 있는 변경 2~4줄."
    echo "- 각 줄 「- 」로 시작, 한 줄 60자 안팎 한국어, 명사형 종결(「~추가」「~수정」「~지원」「~개선」「~정리」)"
    echo "- 「~합니다 · ~했습니다 · ~함 · ~음 · ~됨」 어미와 마침표 금지, 버전 · 커밋 번호 · PR 번호 제외, 요약 줄 외 다른 말 금지"
    echo
    echo "body.md · summary.txt 외 파일은 만들거나 고치지 않는다. 원본 깃허브 사본 안 스크립트는 실행하지 않는다."
  } > "$WORK/prompt.txt"
  {
    printf 'old=%q\nnew=%q\nspan=%q\nnote_label=%q\nnew_tag=%q\nn_commits=%q\nen_changed=%q\nreseed=%q\n' \
      "$old" "$new" "$span" "$note_label" "$new_tag" "$n_commits" "$en_changed" "$reseed"
  } > "$WORK/vars.env"
  echo "번역 대기: $WORK/prompt.txt"
}

# ───────────────────────── translate (run 전용) ─────────────────────────
do_translate_cli() {
  CLAUDE="$(command -v claude 2>/dev/null || echo "$HOME/.local/bin/claude.exe")"
  CCD="${UIUX_CLAUDE_CONFIG_DIR:-${APPDATA:-}/orca/claude-profiles/3ef28fb7-a514-460f-9397-516f926e487c/home}"
  # shellcheck disable=SC1091
  . "$WORK/vars.env"
  local turns=20; [ "$en_changed" -eq 0 ] || turns=60; [ "$reseed" -eq 0 ] || turns=120
  log "claude -p 실행 (${MODEL} · ${EFFORT} · 본문 갱신 $([ "$en_changed" -eq 1 ] && echo 있음 || echo 없음))"
  ( cd "$WORK" && CLAUDE_CONFIG_DIR="$(cygpath -w "$CCD" 2>/dev/null || echo "$CCD")" timeout 3600 "$CLAUDE" -p --output-format text \
      --tools Read Edit Write --permission-mode acceptEdits --max-turns "$turns" \
      --strict-mcp-config --disable-slash-commands --no-session-persistence \
      --model "$MODEL" --effort "$EFFORT" < prompt.txt > "$T/claude-out.txt" 2> "$T/claude-err.txt" ) \
    || fail "claude -p 오류: $(head -c 300 "$T/claude-err.txt" 2>/dev/null) $(tail -c 300 "$T/claude-out.txt" 2>/dev/null)"
  if [ ! -s "$WORK/summary.txt" ]; then tr -d '\r' < "$T/claude-out.txt" > "$WORK/summary.txt"; fi   # 답변으로만 준 경우
}

# ───────────────────────── finish ─────────────────────────
do_finish() {
  [ -f "$WORK/vars.env" ] || fail "prepare 결과 없음 ($WORK/vars.env)"
  # shellcheck disable=SC1091
  . "$WORK/vars.env"
  [ -d "$D" ] || fail "작업 클론에 $DIR 없음"
  bullets="$(tr -d '\r' < "$WORK/summary.txt" 2>/dev/null | sed -n 's/^[[:space:]]*[-•][[:space:]]\{1,\}//p' | sed 's/[.。]$//; s/|/·/g' | awk 'NF && NR<=6' || true)"
  [ -n "$bullets" ] || fail "변경 요약(summary.txt 「- 」 줄) 없음"
  if [ "$en_changed" -eq 1 ]; then
    py validate "$WORK/en-new.md" "$WORK/body.md" || fail "한국어 본문 검증 실패 (작업 결과 버림)"
    py fix-anchors "$WORK/en-new.md" "$WORK/body.md"
  elif ! cmp -s "$WORK/body.md" "$WORK/body-before.md"; then
    fail "영문 변경이 없는데 본문이 바뀜"
  fi
  printf '%s\n' "$bullets" | sed 's/^/  • /'

  # README 조립 + 릴리즈노트 행 + 버전 표기
  today="$(date '+%Y-%m-%d')"; today_dot="$(date '+%Y.%m.%d')"
  top="$(printf '%s\n' "$bullets" | awk 'NR<=3' | paste -sd'|' - | sed 's/|/ · /g')"
  row_text="원본 깃허브 업데이트 반영 — ${span}: ${top}"
  [ "$en_changed" -eq 0 ] || row_text="${row_text} · 한국어 README 번역 갱신"
  new_date="$(git -C "$UP" log -1 --format=%cs "$new")"
  py assemble "$WORK/keep/README.md" "$WORK/body.md" "$D" "$D/README.md" "| ${row_text} | ${today} | 김단영 |" "$new" "$new_date" "$note_label"
  py root-row "$WC/README.md" "$row_text" "$today_dot"
  py versions "$new_tag" "$WC/README.md" "$WC/skills/README.md"

  # 커밋 · 푸시
  cd "$WC"
  git add -A -- "$DIR" README.md skills/README.md
  missing="$(comm -23 <(git -C "$UP" -c core.quotepath=off ls-tree -r --name-only "$new" | sed 's#^README\.md$#README.en.md#' | sort) \
                      <(git -c core.quotepath=off ls-files -- "$DIR" | sed "s#^$DIR/##" | sort) || true)"
  [ -z "$missing" ] || log "경고: .gitignore 에 걸려 빠진 원본 파일 $(printf '%s\n' "$missing" | wc -l | tr -d ' ')개 — $(printf '%s\n' "$missing" | awk 'NR<=5' | paste -sd' ' -)"
  if git diff --cached --quiet; then log "반영할 차이 없음"; restore_wc; share_partial || exit 1; rm -rf "$WORK"; return 0; fi
  git diff --cached --stat | tail -1
  if [ "$dry" -eq 1 ]; then log "--dry-run: 커밋 · 푸시 생략 (결과: $WC)"; return 0; fi

  where="관리자 PC"; [ "$inplace" -eq 0 ] || where="클라우드 예약 작업"
  {
    echo "ui-ux-pro-max-skill: 원본 깃허브 업데이트 반영 (${new_tag} · ${new:0:7})"
    echo
    echo "- 원본 깃허브 nextlevelbuilder/ui-ux-pro-max-skill 업데이트 반영: ${span}"
    printf '%s\n' "$bullets" | sed 's/^/- /'
    [ "$en_changed" -eq 0 ] || echo "- 한국어 README 본문을 영문 최신본 기준으로 번역 갱신"
    echo
    echo "원본 비교: ${UP_URL}/compare/${old:0:7}...${new:0:7}"
    echo "자동 동기화: 공유 리포 share/uiux-upstream-sync.sh (${where})"
    [ -z "${COMMIT_TRAILER:-}" ] || { echo; printf '%s\n' "$COMMIT_TRAILER"; }
  } > "$T/msg.txt"
  git commit -q -F "$T/msg.txt" || fail "커밋 실패 (커밋 가드 차단 등)"
  pushed=0
  for i in 1 2 3; do
    if git push -q origin HEAD:main 2>"$T/push-err.txt"; then pushed=1; break; fi
    log "푸시 거절 — 원격 최신으로 rebase 후 재시도 ($i)"
    git fetch -q origin
    if ! git rebase -q origin/main; then git rebase --abort 2>/dev/null || true; fail "rebase 충돌 — 다음 실행 때 다시"; fi
  done
  [ "$pushed" -eq 1 ] || fail "푸시 실패: $(cat "$T/push-err.txt")"
  log "원본 리포 커밋 · 푸시 $(git log -1 --format='%h %s')"

  # 관리자 PC: 사용자 작업 클론 fast-forward (main · 진행 중 작업 없음 · 겹치는 미커밋 변경 없을 때만)
  if [ "$inplace" -eq 0 ] && [ -d "$SRC/.git" ] && [ "$(git -C "$SRC" branch --show-current)" = main ]; then
    gd="$(git -C "$SRC" rev-parse --absolute-git-dir)"
    if [ ! -e "$gd/MERGE_HEAD" ] && [ ! -d "$gd/rebase-merge" ] && [ ! -d "$gd/rebase-apply" ]; then
      git -C "$SRC" fetch -q origin
      if git -C "$SRC" merge -q --ff-only origin/main 2>/dev/null; then log "작업 폴더 원본 클론 최신으로 맞춤"
      else log "작업 폴더 원본 클론은 그대로 (로컬 커밋 · 겹치는 변경) — 00:00 일일 커밋이 rebase 로 받음"; fi
    fi
  fi

  share_partial || exit 1
  rm -rf "$WORK"
  log "완료"
}

case "$cmd" in
  prepare) do_prepare ;;
  finish) do_finish ;;
  run)
    lock="$STATE/lock"; mkdir -p "$STATE"
    if ! mkdir "$lock" 2>/dev/null; then
      if [ -n "$(find "$lock" -maxdepth 0 -mmin +180 2>/dev/null)" ]; then rm -rf "$lock"; mkdir "$lock"
      else lock=""; log "중단: 다른 동기화가 실행 중"; exit 1; fi
    fi
    do_prepare | tee "$T/prep.txt"
    [ "${PIPESTATUS[0]}" -eq 0 ] || exit 1
    grep -q '^번역 대기: ' "$T/prep.txt" || exit 0
    do_translate_cli
    do_finish
    ;;
esac
