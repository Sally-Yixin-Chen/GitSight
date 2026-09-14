param(
    [string]$Day = "MON",
    [string]$Time = "09:00"
)

$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $env:LOCALAPPDATA "Programs\Python\Python313\python.exe"
$refreshScript = Join-Path $projectRoot "refresh_projects.py"

if (-not (Test-Path -LiteralPath $python)) {
    throw "找不到 Python 3.13：$python"
}

$taskCommand = '"{0}" "{1}"' -f $python, $refreshScript
schtasks /Create /F /SC WEEKLY /D $Day /ST $Time /TN "GitPulse Weekly Refresh" /TR $taskCommand
