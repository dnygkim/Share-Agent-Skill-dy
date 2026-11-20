# capture_window.ps1 — 창 제목으로 브라우저 창을 찾아 PNG 로 저장 (claude-in-chrome 회차의 증적용)
#   powershell -NoProfile -File scripts\capture_window.ps1 -TitleContains "ACME" -Out "output\acme-shop\evidence\20261104-PC-01\TC-ORD-001.png"
#   -ProcessName 기본 chrome. -TitleContains 를 비우면 그 프로세스의 첫 번째 주 창.
param(
  [string]$TitleContains = "",
  [string]$ProcessName = "chrome",
  [Parameter(Mandatory = $true)][string]$Out
)
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class Win32Cap {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr hWnd);
  [DllImport("dwmapi.dll")] public static extern int DwmGetWindowAttribute(IntPtr hwnd, int attr, out RECT rect, int size);
}
"@
[void][Win32Cap]::SetProcessDPIAware()

$procs = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 }
if ($TitleContains) { $procs = $procs | Where-Object { $_.MainWindowTitle -like "*$TitleContains*" } }
$p = $procs | Select-Object -First 1
if (-not $p) { Write-Error "창을 찾지 못했습니다: process=$ProcessName title~'$TitleContains'"; exit 2 }
if ([Win32Cap]::IsIconic($p.MainWindowHandle)) { Write-Error "창이 최소화 상태입니다: $($p.MainWindowTitle)"; exit 3 }

$r = New-Object Win32Cap+RECT
$ok = [Win32Cap]::DwmGetWindowAttribute($p.MainWindowHandle, 9, [ref]$r, [Runtime.InteropServices.Marshal]::SizeOf($r))   # 9 = EXTENDED_FRAME_BOUNDS (그림자 제외)
if ($ok -ne 0) { [void][Win32Cap]::GetWindowRect($p.MainWindowHandle, [ref]$r) }
$w = $r.Right - $r.Left; $h = $r.Bottom - $r.Top
if ($w -le 0 -or $h -le 0) { Write-Error "창 크기가 0입니다"; exit 4 }

$dir = Split-Path -Parent $Out
if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
$bmp = New-Object System.Drawing.Bitmap $w, $h
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($r.Left, $r.Top, 0, 0, (New-Object System.Drawing.Size $w, $h))
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
Write-Output "saved=$Out size=${w}x${h} title=$($p.MainWindowTitle)"
