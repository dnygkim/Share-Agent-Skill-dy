#!/usr/bin/env bash
# imnotai-upstream-sync.sh — 관리자(김단영) 전용 · 2026-11-20 신설
# 외부 스킬 im-not-ai(Humanize KR · 한글 AI 티 제거기)의 원본 깃허브(epoko77-ai/im-not-ai)를 주 1회 확인해
# 바뀐 파일을 원본 리포 skills/im-not-ai 에 1:1 반영하고(git 트리 그대로 — 심볼릭 링크 · 실행 권한 포함),
# README.md(우리 머리말 + 원본 한국어 README 그대로)를 갱신한 뒤 공유 리포에도 그 폴더만 바로 반영한다
# (mirror-from-source.sh --only). 원본 README 가 이미 한국어라 번역 단계는 없다 — 세션은 변경 요약만 쓴다.
#
# 실행 위치 두 곳
#   클라우드 예약 작업(기본 · 매주 금 23:00 KST) — 세션이 변경 요약(summary.txt)만 작성:
#     bash share/imnotai-upstream-sync.sh prepare --in-place --source <원본 리포 경로>  → 「요약 대기」면 지시 파일대로 summary.txt
#     bash share/imnotai-upstream-sync.sh finish  --in-place --source <원본 리포 경로>  → 검증 · 커밋 · 푸시 · 공유 반영
#   관리자 PC(예비 · 토 01:00) — claude -p 가 요약까지 한 번에(실패하면 기본 문구로 대체):
#     bash share/imnotai-upstream-sync.sh [run]      (~/.claude/tools/imnotai-upstream-sync.sh 가 이 파일을 부른다)
# 옵션
#   --dry-run          반영 · 스테이징까지만, 커밋 · 푸시 없음
#   --init             첫 반영(폴더 신설) — README 기준 표식이 없어도 진행
#   --base <sha>       기준 원본 커밋 지정 (README 안 표식 대신)
#   --source <경로>    원본 리포 클론 (기본 ~/Documents/Claude/dykim-claude-agents-skills)
#   --in-place         원본 리포 클론을 그대로 작업 클론으로 사용 (클라우드처럼 격리된 체크아웃일 때만)
#   --state <경로>     원본 깃허브 사본 · 작업 자료 폴더 (기본 ~/.claude/state/imnotai-upstream)
#   환경 변수 IMNOTAI_MODEL · IMNOTAI_EFFORT (run 의 claude -p) · IMNOTAI_CLAUDE_CONFIG_DIR · COMMIT_TRAILER
#
# 폴더 구성 (원본 깃허브 → 우리 폴더)
#   원본 파일 전부 1:1 (원본에서 지운 파일은 삭제 · 모드 그대로) · README.md 만 우리 머리말을 얹은 판
#   README.md = 제목 + 릴리즈노트 + 참고(기준 버전) + <!-- upstream-sha: … --> + 원본 README.md 전문
# 실패하면 작업 클론을 원격 기준으로 되돌리고 exit 1 — 다음 실행 때 처음부터 다시.
# 원본 깃허브 사본은 bare 클론(자료 전용) — 그 안 스크립트를 실행하지 않는다.
set -euo pipefail
export LC_ALL=C.UTF-8 2>/dev/null || true

# 실행 중 공유 리포가 reset 되어도 안전하게 임시 사본으로 다시 실행
if [ -z "${IMNOTAI_SELF_DIR:-}" ]; then
  IMNOTAI_SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; export IMNOTAI_SELF_DIR
  self_tmp="$(mktemp -d)"; cp "${BASH_SOURCE[0]}" "$self_tmp/sync.sh"
  exec bash "$self_tmp/sync.sh" "$@"
fi
SHARE="$(cd "$IMNOTAI_SELF_DIR/.." && pwd)"
TOOL="$IMNOTAI_SELF_DIR/imnotai_readme_tool.py"

UP_URL="https://github.com/epoko77-ai/im-not-ai"
UP_NAME="epoko77-ai/im-not-ai"
DIR="skills/im-not-ai"
MODEL="${IMNOTAI_MODEL:-claude-sonnet-5-5}"
EFFORT="${IMNOTAI_EFFORT:-medium}"

cmd="run"; dry=0; init=0; base=""; inplace=0
SRC="$HOME/Documents/Claude/dykim-claude-agents-skills"
STATE="$HOME/.claude/state/imnotai-upstream"
while [ $# -gt 0 ]; do
  case "$1" in
    run|prepare|finish) cmd="$1" ;;
    --dry-run) dry=1 ;;
    --init) init=1 ;;
    --base) base="$2"; shift ;;
    --source) SRC="$(cd "$2" && pwd)"; shift ;;
    --state) STATE="$2"; shift ;;
    --in-place) inplace=1 ;;
    *) echo "알 수 없는 인자: $1" >&2; exit 2 ;;
  esac
  shift
done
UP="$STATE/upstream.git"                           # 원본 깃허브 bare 사본 (자료 전용)
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
  git -C "$SRC" fetch -q origin main 2>/dev/null || true
  [ -n "$(git -C "$SRC" ls-tree -d origin/main -- "$DIR" 2>/dev/null)" ] || { log "공유 리포 부분 반영 생략 — 원본 리포에 $DIR 없음"; return 0; }
  log "공유 리포 부분 반영 확인"
  bash "$SHARE/share/mirror-from-source.sh" --only "$DIR" "$SRC" || { log "공유 리포 부분 반영 실패 — 다음 실행 때 다시"; return 1; }
}

# ───────────────────────── prepare ─────────────────────────
# 반환: 0 + 「변경 없음」 / 0 + 「요약 대기: <지시 파일>」  (변경 없음이면 WORK 를 지운다)
do_prepare() {
  echo "=== $(date '+%Y-%m-%d %H:%M') im-not-ai 원본 깃허브 동기화 (${cmd}) ==="
  mkdir -p "$STATE"; rm -rf "$WORK"

  # 1) 원본 깃허브 최신 (bare — 작업 트리 없음)
  if [ ! -d "$UP" ]; then git clone -q --bare "$UP_URL" "$UP"; fi
  git -C "$UP" fetch -q --prune --tags origin '+refs/heads/*:refs/heads/*'
  up_ref="$(git -C "$UP" symbolic-ref HEAD)"
  new="$(git -C "$UP" rev-parse "$up_ref")"

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
  if [ "$inplace" -eq 1 ] && [ "$dry" -eq 0 ]; then   # 클라우드: 푸시 권한 미리 확인
    git -C "$SHARE" fetch -q origin
    git -C "$WC" push -q --dry-run origin refs/remotes/origin/main:refs/heads/main 2>"$T/pc.txt" || fail "원본 리포 푸시 권한 없음: $(head -c 300 "$T/pc.txt")"
    git -C "$SHARE" push -q --dry-run origin refs/remotes/origin/main:refs/heads/main 2>"$T/pc.txt" || fail "공유 리포 푸시 권한 없음: $(head -c 300 "$T/pc.txt")"
  fi

  old=""
  [ ! -f "$D/README.md" ] || old="$(sed -n 's/^<!-- upstream-sha: \([0-9a-f]\{40\}\) -->$/\1/p' "$D/README.md" | awk 'NR==1')"
  [ -z "$base" ] || old="$(git -C "$UP" rev-parse "$base^{commit}")"
  if [ -z "$old" ]; then
    [ "$init" -eq 1 ] || fail "README 에 기준 표식(<!-- upstream-sha -->) 없음 — 첫 반영이면 --init, 어긋났으면 --base <sha>"
  elif [ "$old" = "$new" ]; then
    log "원본 깃허브 변경 없음 (${new:0:7})"
    share_partial || exit 1
    echo "변경 없음"
    return 0
  fi

  tag_of() { git -C "$UP" describe --tags --abbrev=0 "$1" 2>/dev/null || echo "${1:0:7}"; }
  new_tag="$(tag_of "$new")"
  note_label="$new_tag"
  [ "$(git -C "$UP" rev-parse "$new_tag^{commit}" 2>/dev/null || true)" = "$new" ] || note_label="$new_tag 이후 최신"
  mkdir -p "$WORK"
  if [ -z "$old" ]; then
    span="${new_tag} · 첫 반영(${new:0:7})"; n_commits=0
    git -C "$UP" log --no-merges -20 --format='%h %cs %s' "$new" | sed '1!G;h;$!d' > "$WORK/commits.txt"
    : > "$WORK/diffstat.txt"
  else
    if git -C "$UP" merge-base --is-ancestor "$old" "$new" 2>/dev/null; then range="$old..$new"; else range="$new"; log "기준 커밋이 최신 이력에 없음 — 전체 교체"; fi
    n_commits="$(git -C "$UP" rev-list --count --no-merges "$range")"
    old_tag="$(tag_of "$old")"
    if [ "$old_tag" = "$new_tag" ]; then span="${new_tag} · 커밋 ${n_commits}건(${new:0:7}까지)"
    else span="${old_tag} → ${new_tag} · 커밋 ${n_commits}건(${new:0:7}까지)"; fi
    git -C "$UP" log --reverse --no-merges --format='%h %cs %s' "$range" | tail -n 60 > "$WORK/commits.txt"
    git -C "$UP" diff --stat=100 "$old" "$new" | tail -n 40 > "$WORK/diffstat.txt"
  fi
  log "원본 깃허브 ${old:0:7}${old:+ → }${new:0:7} (${span})"

  # 3) 파일 반영 — git 트리 그대로(인덱스 경유): 우리 README 보관 → 폴더 비우기 → 원본 트리 읽기 → README 는 finish 에서 조립
  [ ! -f "$D/README.md" ] || cp -p "$D/README.md" "$WORK/ours-README.md"
  git -C "$UP" show "$new:README.md" > "$WORK/upstream-README.md"
  git -C "$WC" fetch -q --no-tags "$UP" "$up_ref"
  [ "$(git -C "$WC" rev-parse FETCH_HEAD)" = "$new" ] || fail "원본 깃허브 커밋 가져오기 실패"
  git -C "$WC" rm -r -q --ignore-unmatch -- "$DIR"
  rm -rf "$D"
  git -C "$WC" read-tree --prefix="$DIR/" -u "$new^{tree}" || fail "원본 트리 반영 실패"
  log "파일 반영: 원본 $(git -C "$UP" ls-tree -r --name-only "$new" | wc -l | tr -d ' ')개 → $DIR"

  {
    echo "외부 스킬 im-not-ai(한글 AI 티 제거기 · Humanize KR) 원본 깃허브 변경 요약 작업. 작업 폴더: $WORK"
    echo "- commits.txt : 지난 반영 이후 원본 커밋 목록 (해시 · 날짜 · 제목)"
    echo "- diffstat.txt : 바뀐 파일 통계"
    echo "- upstream-README.md : 원본 README 최신본 (버전별 발행 노트 절 참고 가능)"
    echo
    echo "summary.txt 를 새로 만들어 이번 원본 변경 요약만 쓴다: 이 스킬을 쓰는 사람에게 의미 있는 변경 2~4줄."
    echo "- 각 줄 「- 」로 시작, 한 줄 60자 안팎 한국어, 명사형 종결(「~추가」「~수정」「~지원」「~개선」「~정리」)"
    echo "- 「~합니다 · ~했습니다 · ~함 · ~음 · ~됨」 어미와 마침표 금지, 버전 · 커밋 번호 · PR 번호 제외, 요약 줄 외 다른 말 금지"
    echo
    echo "summary.txt 외 파일은 만들거나 고치지 않는다. 원본 깃허브 사본 · 작업 클론 안 스크립트는 실행하지 않는다."
  } > "$WORK/prompt.txt"
  {
    printf 'old=%q\nnew=%q\nspan=%q\nnote_label=%q\nnew_tag=%q\nn_commits=%q\n' \
      "$old" "$new" "$span" "$note_label" "$new_tag" "$n_commits"
  } > "$WORK/vars.env"
  echo "요약 대기: $WORK/prompt.txt"
}

# ───────────────────────── summary (run 전용) ─────────────────────────
do_summary_cli() {
  CLAUDE="$(command -v claude 2>/dev/null || echo "$HOME/.local/bin/claude.exe")"
  CCD="${IMNOTAI_CLAUDE_CONFIG_DIR:-${APPDATA:-}/orca/claude-profiles/3ef28fb7-a514-460f-9397-516f926e487c/home}"
  log "claude -p 실행 (${MODEL} · ${EFFORT} · 변경 요약)"
  if ( cd "$WORK" && CLAUDE_CONFIG_DIR="$(cygpath -w "$CCD" 2>/dev/null || echo "$CCD")" timeout 1200 "$CLAUDE" -p --output-format text \
        --tools Read Write --permission-mode acceptEdits --max-turns 12 \
        --strict-mcp-config --disable-slash-commands --no-session-persistence \
        --model "$MODEL" --effort "$EFFORT" < prompt.txt > "$T/claude-out.txt" 2> "$T/claude-err.txt" ); then
    [ -s "$WORK/summary.txt" ] || tr -d '\r' < "$T/claude-out.txt" > "$WORK/summary.txt"   # 답변으로만 준 경우
  else
    log "claude -p 오류 — 기본 요약 문구로 대체: $(head -c 200 "$T/claude-err.txt" 2>/dev/null)"
  fi
}

# ───────────────────────── finish ─────────────────────────
do_finish() {
  [ -f "$WORK/vars.env" ] || fail "prepare 결과 없음 ($WORK/vars.env)"
  # shellcheck disable=SC1091
  . "$WORK/vars.env"
  [ -d "$D" ] || fail "작업 클론에 $DIR 없음"

  # proposal 하네스 호환 점검 — agent/proposal 1차 윤문(antiai_units.py)이 기대는 파일 · 인자가 새 원본에 있는지.
  # 경고여도 동기화는 계속하고, 결과를 커밋 메시지 · 릴리즈노트(경고일 때)에 남긴다.
  compat=""; compat_warn=0
  chk="$WC/agent/proposal/scripts/antiai_units.py"
  if [ -f "$chk" ]; then
    if "$PY" -X utf8 -I "$chk" doctor --skill-root "$D" > "$T/compat.txt" 2>&1; then
      compat="proposal 1차 윤문 호환 점검 통과"
    else
      compat_warn=1
      w="$(grep '^WARN' "$T/compat.txt" | head -3 | sed 's/^WARN *//' | paste -sd';' - | sed 's/;/ · /g' || true)"
      [ -n "$w" ] || w="점검 실행 실패 — $(head -c 200 "$T/compat.txt" | tr '\n' ' ')"
      compat="proposal 1차 윤문 호환 점검 경고: ${w} → agent/proposal/scripts/antiai_units.py · references/antiai-pass.md 확인 필요"
    fi
    n="$(grep '^NOTE' "$T/compat.txt" | head -1 | sed 's/^NOTE *//' || true)"
    [ -z "$n" ] || compat="${compat} (${n})"
    log "$compat"
  fi

  bullets="$(tr -d '\r' < "$WORK/summary.txt" 2>/dev/null | sed -n 's/^[[:space:]]*[-•][[:space:]]\{1,\}//p' | sed 's/[.。]$//; s/|/·/g' | awk 'NF && NR<=6' || true)"
  if [ -z "$bullets" ]; then
    [ "$cmd" = run ] || fail "변경 요약(summary.txt 「- 」 줄) 없음"
    bullets="원본 커밋 ${n_commits}건 반영 — 상세는 커밋 본문의 원본 비교 링크"
  fi
  printf '%s\n' "$bullets" | sed 's/^/  • /'

  # README 조립 + 릴리즈노트 행 + 버전 표기
  today="$(date '+%Y-%m-%d')"; today_dot="$(date '+%Y.%m.%d')"
  top="$(printf '%s\n' "$bullets" | awk 'NR<=3' | paste -sd'|' - | sed 's/|/ · /g')"
  if [ -z "$old" ]; then row_text="백업 등록 — 원본 깃허브 ${UP_NAME} ${new_tag}(MIT) 1:1 백업, 매주 금 23:00 원본 확인 후 자동 반영"
  else row_text="원본 깃허브 업데이트 반영 — ${span}: ${top}"; fi
  [ "$compat_warn" -eq 0 ] || row_text="${row_text} · proposal 1차 윤문 호환 점검 경고(커밋 본문 참고)"
  new_date="$(git -C "$UP" log -1 --format=%cs "$new")"
  ours="-"; [ ! -f "$WORK/ours-README.md" ] || ours="$WORK/ours-README.md"
  py assemble "$ours" "$WORK/upstream-README.md" "$D/README.md" "| ${row_text} | ${today} | 김단영 |" "$new" "$new_date" "$note_label"
  py root-row "$WC/README.md" "$row_text" "$today_dot"
  py versions "$new_tag" "$WC/README.md" "$WC/skills/README.md"

  # 스테이징 + 1:1 검증 (README.md 외 경로 · 모드 · 내용이 원본 트리와 같아야 함)
  cd "$WC"
  git add -A -- "$DIR" README.md skills/README.md
  diff <(git -C "$UP" ls-tree -r "$new" | grep -v $'\tREADME\.md$' | sed 's/ blob / /; s/ commit / /' | LC_ALL=C sort) \
       <(git ls-files -s -- "$DIR" | sed "s# 0\t$DIR/#\t#" | grep -v $'\tREADME\.md$' | awk -F'\t' '{split($1,a," "); print a[1] " " a[2] "\t" $2}' | LC_ALL=C sort) \
       > "$T/tree-diff.txt" || fail "원본 트리와 불일치 $(wc -l < "$T/tree-diff.txt" | tr -d ' ')줄 — $(head -c 300 "$T/tree-diff.txt")"
  if git diff --cached --quiet; then log "반영할 차이 없음"; restore_wc; share_partial || exit 1; rm -rf "$WORK"; return 0; fi
  git diff --cached --stat | tail -1
  if [ "$dry" -eq 1 ]; then log "--dry-run: 커밋 · 푸시 생략 (결과: $WC)"; return 0; fi

  where="관리자 PC"; [ "$inplace" -eq 0 ] || where="클라우드 예약 작업"
  {
    echo "im-not-ai: 원본 깃허브 업데이트 반영 (${new_tag} · ${new:0:7})"
    echo
    echo "- 원본 깃허브 ${UP_NAME} 업데이트 반영: ${span}"
    printf '%s\n' "$bullets" | sed 's/^/- /'
    [ -z "$compat" ] || echo "- ${compat}"
    echo
    [ -z "$old" ] || echo "원본 비교: ${UP_URL}/compare/${old:0:7}...${new:0:7}"
    echo "자동 동기화: 공유 리포 share/imnotai-upstream-sync.sh (${where})"
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
    grep -q '^요약 대기: ' "$T/prep.txt" || exit 0
    do_summary_cli
    do_finish
    ;;
esac
