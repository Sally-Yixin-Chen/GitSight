param(
    [ValidateSet("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")]
    [string]$Day = "MON",

    [ValidatePattern("^([01]\d|2[0-3]):[0-5]\d$")]
    [string]$Time = "09:00"
)

$taskName = "GitSight Weekly Refresh"
$projectRoot = Split-Path -Parent $PSScriptRoot
$refreshScript = Join-Path $PSScriptRoot "refresh_projects.py"

$pythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
if (-not $pythonCommand) {
    throw "python.exe was not found. Install Python and add it to PATH."
}

$python = $pythonCommand.Source
if (-not (Test-Path -LiteralPath $refreshScript -PathType Leaf)) {
    throw "Refresh script was not found: $refreshScript"
}

$dayMap = @{
    MON = [System.DayOfWeek]::Monday
    TUE = [System.DayOfWeek]::Tuesday
    WED = [System.DayOfWeek]::Wednesday
    THU = [System.DayOfWeek]::Thursday
    FRI = [System.DayOfWeek]::Friday
    SAT = [System.DayOfWeek]::Saturday
    SUN = [System.DayOfWeek]::Sunday
}

$at = [datetime]::ParseExact(
    $Time,
    "HH:mm",
    [System.Globalization.CultureInfo]::InvariantCulture
)

$action = New-ScheduledTaskAction `
    -Execute $python `
    -Argument ('"{0}"' -f $refreshScript) `
    -WorkingDirectory $projectRoot
$trigger = New-ScheduledTaskTrigger `
    -Weekly `
    -DaysOfWeek $dayMap[$Day] `
    -At $at
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Force | Out-Null

Write-Host "Created weekly refresh task: $taskName"
