<#
save-secret.ps1 — 클립보드에 복사한 슬랙 비밀값을 화면에 출력하지 않고 파일로 저장

  powershell -ExecutionPolicy Bypass -File save-secret.ps1 -Kind webhook -Name my-bot-webhook.url
  powershell -ExecutionPolicy Bypass -File save-secret.ps1 -Kind bot     -Name my-bot-bot-token
  powershell -ExecutionPolicy Bypass -File save-secret.ps1 -Kind app     -Name my-bot-app-token

  -Kind   webhook = https://hooks.slack.com/services/…  ·  bot = xoxb-…  ·  app = xapp-…
  -Name   저장할 파일 이름 (폴더는 -Dir, 기본 ~/.claude/secrets — 리포 밖)
  -Dir    저장 폴더를 바꿀 때만
  -Value  클립보드 대신 값을 직접 넘길 때만 (시험용 — 명령이 기록에 남으므로 실제 값에는 쓰지 않는다)

- 형식이 맞을 때만 저장하고, 저장 뒤 클립보드를 비운다. 출력은 저장 위치와 값의 길이뿐이다.
- 형식이 다르면 아무것도 저장하지 않는다. 클립보드 내용은 일부도 출력하지 않는다.
#>
param(
  [Parameter(Mandatory = $true)][ValidateSet('webhook', 'bot', 'app')][string]$Kind,
  [Parameter(Mandatory = $true)][string]$Name,
  [string]$Dir = (Join-Path $HOME '.claude\secrets'),
  [string]$Value
)

$patterns = @{
  webhook = '^https://hooks\.slack\.com/services/\S+$'
  bot     = '^xoxb-\S+$'
  app     = '^xapp-\S+$'
}
$fromClipboard = -not $PSBoundParameters.ContainsKey('Value')
if ($fromClipboard) { $Value = Get-Clipboard -Raw }
$v = ("$Value").Trim()

if ($v -notmatch $patterns[$Kind]) {
  Write-Output "저장 안 함: $Kind 형식이 아님 (값 길이 $($v.Length)). 슬랙 화면의 Copy 버튼을 다시 누른 뒤 실행"
  exit 1
}

New-Item -ItemType Directory -Force $Dir | Out-Null
$path = Join-Path $Dir $Name
[IO.File]::WriteAllText($path, $v)
if ($fromClipboard) { Set-Clipboard -Value ' ' }
Write-Output "저장 완료: $path (길이 $($v.Length))"
