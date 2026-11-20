#!/bin/sh
# _guard.sh — 훅 공용: 파이썬을 찾아 guard.py 를 부른다 (pre-commit · commit-msg · pre-push 가 읽어 들인다 · 2026-11-25)
# 파이썬을 못 찾으면 통과시키지 않는다 — 검사를 못 하면 내보내지 않는다.
guard_run() {
  _gd="$(dirname "$0")"
  _py=""
  for _c in python3 python; do
    _p="$(command -v "$_c" 2>/dev/null)" || continue
    case "$_p" in *WindowsApps*) continue ;; esac   # Windows 스토어 연결용 빈 실행 파일
    if "$_p" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' 2>/dev/null; then _py="$_p"; break; fi
  done
  if [ -z "$_py" ]; then
    for _p in "$HOME/AppData/Local/Programs/Python/Python314/python.exe" "$HOME/AppData/Local/Programs/Python/Python313/python.exe"; do
      if [ -x "$_p" ]; then _py="$_p"; break; fi
    done
  fi
  if [ -z "$_py" ]; then
    echo "✗ 가드 실행 불가 — 파이썬 3.8 이상을 찾지 못함. 검사 없이 내보내지 않는다(파이썬 설치 뒤 다시)." >&2
    return 2
  fi
  "$_py" -X utf8 -I "$_gd/guard.py" "$@"
}
