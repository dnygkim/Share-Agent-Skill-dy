# sync-skills.ps1
# 정본 skills/ 를 각 에이전트의 .claude/skills/ 로 복사해 자동 로드하도록 한다.
# agent/<이름>/.claude/skills/ 는 .gitignore 처리되어 있으므로(생성물), 클론 후 한 번 실행한다.
#   PowerShell:  ./sync-skills.ps1
#
# 새 에이전트가 이 스킬들을 쓰려면 아래 $agents 목록에 폴더명을 추가한다.

$root   = $PSScriptRoot
$src    = Join-Path $root 'skills'
$agents = @('proposal', 'feature-spec-sb', 'test-runner')   # 스킬을 받을 agent/<이름> 목록

if (-not (Test-Path $src)) { Write-Error "정본 폴더가 없습니다: $src"; exit 1 }

foreach ($a in $agents) {
  $dst = Join-Path $root "agent/$a/.claude/skills"
  if (Test-Path $dst) { Remove-Item -Recurse -Force $dst }
  New-Item -ItemType Directory -Force -Path $dst | Out-Null
  Copy-Item -Recurse -Force (Join-Path $src '*') $dst
  Write-Host "Synced skills -> agent/$a/.claude/skills/"
  Get-ChildItem $dst -Directory | ForEach-Object { Write-Host "  - $($_.Name)" }
}
