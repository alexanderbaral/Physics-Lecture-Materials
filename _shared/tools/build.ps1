param(
    [ValidateSet('script','sheets','all')][string]$Target = 'all',
    [switch]$Status,
    [switch]$Cloze,
    [switch]$Wait
)
$ErrorActionPreference = 'Stop'
$commandArgs = @((Join-Path $PSScriptRoot 'build.py'))
if ($Status) { $commandArgs += 'status' } else { $commandArgs += 'update' }
$commandArgs += @('--product',$Target)
if ($Wait) { $commandArgs += '--wait' }
if ($Cloze) { $commandArgs += '--cloze' }
if (-not $Status -and $Target -eq 'all') { $commandArgs += '--open-preview' }
& python @commandArgs
exit $LASTEXITCODE

