#!/usr/bin/env bash
# schedule-weekly-mac.sh — 받는 사람 Mac용
# share/update.sh 를 매주 월요일 09:00 에 자동 실행하도록 launchd 에 등록한다.
# Mac이 잠자기였으면 깨어난 뒤 실행한다. 실행 기록은 ~/.claude/dykim-share-update.log 에 남는다.
#   bash share/schedule-weekly-mac.sh
#   해제:  launchctl unload ~/Library/LaunchAgents/com.dykim.share-update.plist && rm ~/Library/LaunchAgents/com.dykim.share-update.plist
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
plist="$HOME/Library/LaunchAgents/com.dykim.share-update.plist"
mkdir -p "$(dirname "$plist")"

cat > "$plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.dykim.share-update</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>-lc</string>
    <string>bash '$repo/share/update.sh'</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>9</integer><key>Minute</key><integer>0</integer></dict>
  <key>StandardOutPath</key><string>$HOME/.claude/dykim-share-update.log</string>
  <key>StandardErrorPath</key><string>$HOME/.claude/dykim-share-update.log</string>
</dict>
</plist>
EOF

launchctl unload "$plist" 2>/dev/null || true
launchctl load "$plist"
echo "등록 완료: 매주 월 09:00 · $plist"
echo "기록: $HOME/.claude/dykim-share-update.log"
