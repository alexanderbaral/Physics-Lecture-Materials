param(
    [ValidateSet('de','en','all')][string]$Language = 'de',
    [string[]]$Sheet = @('all'),
    [ValidateSet('on','off','both')][string]$Solutions = 'off',
    [switch]$Force, [switch]$Warm, [switch]$Incremental,
    [ValidateRange(1,16)][int]$Jobs = 4,
    [string]$Python = 'python',
    [switch]$Wait,
    [switch]$Status
)
$ErrorActionPreference = 'Stop'
$commandArgs = @((Join-Path $PSScriptRoot 'build_coordinator.py'))
if ($Status) { $commandArgs += 'status' } else {
    $commandArgs += @('update','--language',$Language,'--solutions',$Solutions,'--jobs',"$Jobs")
    foreach ($id in $Sheet) { $commandArgs += @('--sheet',$id) }
    if ($Force) { $commandArgs += '--force' }
    if ($Wait) { $commandArgs += '--wait' }
}
& $Python @commandArgs
exit $LASTEXITCODE
