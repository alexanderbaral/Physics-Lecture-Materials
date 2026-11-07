param([switch]$Status, [switch]$Wait)
$ErrorActionPreference = 'Stop'
$arguments = @((Join-Path $PSScriptRoot 'build_coordinator.py'))
if ($Status) { $arguments += 'status' } else { $arguments += 'update' }
if ($Wait) { $arguments += '--wait' }
& python @arguments
exit $LASTEXITCODE
