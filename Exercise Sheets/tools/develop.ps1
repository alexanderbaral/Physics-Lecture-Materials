param(
    [ValidateSet('de','en','all')][string]$Language = 'de',
    [ValidateSet('both','on','off')][string]$Solutions = 'both',
    [ValidateRange(1,16)][int]$Jobs = 4,
    [switch]$Once,
    [string]$Python = ''
)
$ErrorActionPreference = 'Stop'
$candidates = if ($Python) { @($Python) } else {
    @('python', (Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'))
}
foreach ($candidate in $candidates) {
    if (Get-Command $candidate -ErrorAction SilentlyContinue) {
        & $candidate -c 'import importlib.util, sys; sys.exit(0 if importlib.util.find_spec(sys.argv[1]) else 1)' pypdf
        if ($LASTEXITCODE -eq 0) { $Python = $candidate; break }
    }
}
if (-not $Python) { throw 'Python with pypdf is required.' }
$extra = @()
if ($Once) { $extra += '--once' }
& $Python -B (Join-Path $PSScriptRoot 'watch_build.py') --language $Language --solutions $Solutions --jobs $Jobs @extra
exit $LASTEXITCODE

