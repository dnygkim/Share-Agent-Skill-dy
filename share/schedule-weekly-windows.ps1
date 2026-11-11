# schedule-weekly-windows.ps1 — 받는 사람 Windows PC용
# share/update.sh 를 매주 월요일 09:00 에 자동 실행하도록 작업 스케줄러에 등록한다.
# PC가 꺼져 있었으면 켜진 뒤 바로 실행한다. 실행 기록은 ~/.claude/dykim-share-update.log 에 남는다.
#   PowerShell:  powershell -ExecutionPolicy Bypass -File share\schedule-weekly-windows.ps1
#   해제:        Unregister-ScheduledTask -TaskName 'dykim-share-update' -Confirm:$false

$repo = Split-Path -Parent $PSScriptRoot
$git  = (Get-Command git -ErrorAction Stop).Source            # ...\Git\cmd\git.exe
$bash = Join-Path (Split-Path -Parent (Split-Path -Parent $git)) 'bin\bash.exe'
if (-not (Test-Path $bash)) { Write-Error "Git Bash 를 찾지 못했습니다: $bash"; exit 1 }

$repoUnix = (& $bash -lc "cygpath -u '$repo'").Trim()
$cmd      = "bash '$repoUnix/share/update.sh' >> ~/.claude/dykim-share-update.log 2>&1"

$action   = New-ScheduledTaskAction -Execute $bash -Argument "-lc `"$cmd`""
$trigger  = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 9am
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName 'dykim-share-update' -Action $action -Trigger $trigger -Settings $settings `
  -Description 'dykim-claude-agents-skills-share 주간 업데이트' -Force | Out-Null

Write-Host "등록 완료: 매주 월 09:00 · 작업 이름 dykim-share-update"
Write-Host "기록: $env:USERPROFILE\.claude\dykim-share-update.log"
