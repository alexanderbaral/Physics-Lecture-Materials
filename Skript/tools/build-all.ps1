param([switch]$Force, [switch]$CleanCache, [switch]$Serial)
$ErrorActionPreference = 'Stop'
$arguments = @((Join-Path $PSScriptRoot 'build_coordinator.py'), 'full', '--wait')
if ($Force) { $arguments += '--force' }
if ($Serial) { $arguments += '--serial' }
if ($CleanCache) { $arguments = @((Join-Path $PSScriptRoot 'build_coordinator.py'), 'clean') }
& python @arguments
exit $LASTEXITCODE
