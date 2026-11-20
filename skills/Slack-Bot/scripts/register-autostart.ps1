<#
register-autostart.ps1 — 멘션 응답 봇을 Windows 작업 스케줄러에 등록하고 바로 시작

  powershell -ExecutionPolicy Bypass -File register-autostart.ps1 -TaskName my-bot-slack -BotDir "$HOME\.claude\tools\my-bot"
  powershell -ExecutionPolicy Bypass -File register-autostart.ps1 -TaskName my-bot-slack -BotDir "$HOME\.claude\tools\my-bot" -DryRun

  -TaskName  작업 스케줄러에 보일 이름
  -BotDir    slack_mention_bot.py · config.json · system-prompt.md 가 있는 폴더
  -Pythonw   pythonw.exe 경로 (생략하면 PATH → %LOCALAPPDATA%\Programs\Python 순서로 찾음 · WindowsApps 바로가기 제외)
  -DryRun    등록하지 않고 등록할 내용만 출력

- 시작 조건: 로그온할 때 + 등록 1분 뒤부터 10분마다. 이미 돌고 있으면 봇이 lock_port 로 알아채고 바로 끝나므로 하나만 돈다.
- 창 없이 돌도록 pythonw 로 실행한다. 기록은 config.json 의 log_file (기본 ~/.claude/<bot_name>-slack.log).
- 멈추기: Stop-ScheduledTask -TaskName <이름>  ·  해제: Unregister-ScheduledTask -TaskName <이름> -Confirm:$false
  (해제 뒤에도 돌고 있는 봇은 작업 관리자에서 pythonw 종료)
#>
param(
  [Parameter(Mandatory = $true)][string]$TaskName,
  [Parameter(Mandatory = $true)][string]$BotDir,
  [string]$Pythonw,
  [switch]$DryRun
)

if (-not (Test-Path $BotDir)) { Write-Output "폴더 없음: $BotDir"; exit 1 }
$BotDir = (Resolve-Path $BotDir).Path
$script = Join-Path $BotDir 'slack_mention_bot.py'
$conf = Join-Path $BotDir 'config.json'
foreach ($f in @($script, $conf, (Join-Path $BotDir 'system-prompt.md'))) {
  if (-not (Test-Path $f)) { Write-Output "없음: $f"; exit 1 }
}

if (-not $Pythonw) {
  $c = Get-Command pythonw -All -ErrorAction SilentlyContinue | Where-Object { $_.Source -notmatch 'WindowsApps' } | Select-Object -First 1
  if ($c) { $Pythonw = $c.Source }
  else {
    $Pythonw = Get-ChildItem "$env:LOCALAPPDATA\Programs\Python\Python3*\pythonw.exe" -ErrorAction SilentlyContinue |
      Sort-Object FullName -Descending | Select-Object -First 1 -ExpandProperty FullName
  }
}
if (-not $Pythonw -or -not (Test-Path $Pythonw)) { Write-Output "pythonw.exe 를 찾지 못함 — -Pythonw 로 경로 지정"; exit 1 }

$cfg = Get-Content $conf -Raw -Encoding UTF8 | ConvertFrom-Json
$botName = if ($cfg.bot_name) { $cfg.bot_name } else { 'my-bot' }
$log = if ($cfg.log_file) { $cfg.log_file } else { Join-Path $HOME ".claude\$botName-slack.log" }

if ($DryRun) {
  Write-Output "등록 예정 (DryRun — 아직 등록하지 않음)"
  Write-Output "  작업 이름 : $TaskName"
  Write-Output "  실행      : $Pythonw -I `"$script`""
  Write-Output "  작업 폴더 : $BotDir"
  Write-Output "  시작 조건 : 로그온할 때 · 등록 1분 뒤부터 10분마다"
  Write-Output "  설정      : 놓친 시작은 바로 실행 · 중복 실행 무시 · 실행 시간 제한 없음 · 실패 시 1분 뒤 재시작 · 배터리 사용 중에도 실행"
  Write-Output "  기록 파일 : $log"
  exit 0
}

$action = New-ScheduledTaskAction -Execute $Pythonw -Argument "-I `"$script`"" -WorkingDirectory $BotDir
$t1 = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$t2 = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 10)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit ([TimeSpan]::Zero) `
  -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger @($t1, $t2) -Settings $settings `
  -Description "슬랙 멘션 응답 봇 $botName (Socket Mode 상주 · 10분마다 확인, 중복 실행은 봇이 막음)" -Force | Out-Null
Start-ScheduledTask -TaskName $TaskName
Start-Sleep -Seconds 8
Write-Output "등록 완료: $TaskName · 상태 $((Get-ScheduledTask -TaskName $TaskName).State)"
if (Test-Path $log) { Write-Output "기록 마지막 줄:"; Get-Content $log -Tail 3 -Encoding UTF8 }
