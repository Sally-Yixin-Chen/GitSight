param(
    [string]$Day = "MON",
    [string]$Time = "09:00"
)

$projectRoot = Split-Path -Parent $PSScriptRoot
$refreshScript = Join-Path $PSScriptRoot "refresh_projects.py"

$python = $null

# Prefer Python 3.13 from the Python Launcher; otherwise use Python from PATH.
$pyLauncher = Get-Command py.exe -ErrorAction SilentlyContinue
if ($pyLauncher) {
    $python313 = & $pyLauncher.Source -3.13 -c "import sys; print(sys.executable)" 2>$null | Select-Object -First 1
    if ($python313 -and (Test-Path -LiteralPath $python313)) {
        $python = $python313
    }
}

if (-not $python) {
    $pythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($pythonCommand -and (Test-Path -LiteralPath $pythonCommand.Source)) {
        $python = $pythonCommand.Source
    }
}

if (-not $python) {
    throw "No usable Python installation was found. Install Python 3.13 or add Python to PATH."
}

$taskCommand = '"{0}" "{1}"' -f $python, $refreshScript
schtasks /Create /F /SC WEEKLY /D $Day /ST $Time /TN "GitSight Weekly Refresh" /TR $taskCommand
