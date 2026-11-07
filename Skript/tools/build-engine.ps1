param(
    [switch]$Force,
    [switch]$CleanCache,
    [switch]$Serial,
    [string]$SourceRoot,
    [string]$CanonicalRoot
)

$ErrorActionPreference = 'Stop'
$buildTimer = [System.Diagnostics.Stopwatch]::StartNew()
$buildLock = $null
$buildJobs = @()
try {

$projectRoot = if ($SourceRoot) { $SourceRoot } else { Split-Path -Parent $PSScriptRoot }
if (-not $CanonicalRoot) { $CanonicalRoot = $projectRoot }
$fileHashes = @{}

# In-memory hashes and portable dependency checks; no figure is trusted without its source hashes.
. (Join-Path $PSScriptRoot 'build-cache.ps1')

$sharedRoot = Join-Path (Split-Path -Parent $projectRoot) '_shared'
$approvalPath = Join-Path $sharedRoot 'tools/build_variants.json'
$approvedLanguages = @('de')
if (Test-Path -LiteralPath $approvalPath) {
    $approvedLanguages = @((Get-Content -LiteralPath $approvalPath -Raw | ConvertFrom-Json).script_languages)
}
if ('de' -notin $approvedLanguages) { throw 'The German master must remain enabled.' }
$variants = @(foreach ($lang in $approvedLanguages) {
    if ($lang -notin @('de','en')) { throw "Unsupported approved language: $lang" }
    @{ File = "tools/build-$lang.tex"; Label = "$lang complete"; Language = $lang; Cloze = 'false' }
    @{ File = "tools/build-$lang-cloze.tex"; Label = "$lang cloze"; Language = $lang; Cloze = 'true' }
})

$buildDirectory = Join-Path $projectRoot 'build'
New-Item -ItemType Directory -Force -Path $buildDirectory | Out-Null

$localCacheDirectory = Get-LectureCacheRoot 'script'
$expectedLocalCacheDirectory = $localCacheDirectory

if ($CleanCache) {
    if (Test-Path -LiteralPath $localCacheDirectory) {
        $resolvedLocalCacheDirectory = (Resolve-Path -LiteralPath $localCacheDirectory).Path
        if ($resolvedLocalCacheDirectory -ne $expectedLocalCacheDirectory) {
            throw "Refusing to remove unexpected cache path: $resolvedLocalCacheDirectory"
        }
        Remove-Item -LiteralPath $resolvedLocalCacheDirectory -Recurse -Force
        Write-Host "Removed local LaTeX cache: $resolvedLocalCacheDirectory"
    }
    else {
        Write-Host "Local LaTeX cache is already empty: $localCacheDirectory"
    }
    exit 0
}

New-Item -ItemType Directory -Force -Path $localCacheDirectory | Out-Null
try {
    $buildLock = [System.IO.File]::Open(
        (Join-Path $localCacheDirectory 'build.lock'),
        [System.IO.FileMode]::OpenOrCreate,
        [System.IO.FileAccess]::ReadWrite,
        [System.IO.FileShare]::None
    )
}
catch {
    throw 'Another full build is using the persistent cache. Wait for it to finish; do not start a competing build.'
}
Write-Host "Persistent local cache: $localCacheDirectory"

# Publishing a PDF compiled while its inputs changed would create a mixed
# source state. Include new/deleted files as well as changed file contents.
function Get-ProjectSourceFingerprint {
    $paths = @(
        Get-ChildItem -LiteralPath (Join-Path $projectRoot 'common'), (Join-Path $projectRoot 'content') -File -Recurse |
            Select-Object -ExpandProperty FullName
        (Join-Path $projectRoot 'main.tex')
        (Join-Path $projectRoot 'latexmkrc')
        (Join-Path $projectRoot 'tools/build-tikz.tex')
        (Join-Path $sharedRoot 'lecture_metadata.tex')
        foreach ($folder in 'style','commands','resources') {
            Get-ChildItem -LiteralPath (Join-Path $sharedRoot $folder) -File -Recurse |
                Select-Object -ExpandProperty FullName
        }
        foreach ($variant in $variants) { Join-Path $projectRoot $variant.File }
    ) | Sort-Object -Unique
    $records = foreach ($path in $paths) {
        '{0}:{1}' -f $path, (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash
    }
    return $records -join "`n"
}
$sourceFingerprintBefore = Get-ProjectSourceFingerprint

# Reuse figures only when their actual recorded source inputs still match.
# Body-only layout changes must not discard standalone figure PDFs.
$tikzCacheDirectory = Join-Path $localCacheDirectory 'tikz'
New-Item -ItemType Directory -Force -Path $tikzCacheDirectory | Out-Null
foreach ($variant in $variants) {
    $jobName = [System.IO.Path]::GetFileNameWithoutExtension($variant.File)
    New-Item -ItemType Directory -Force -Path (Join-Path $tikzCacheDirectory $jobName) | Out-Null
}

$tikzCachePathForTex = $tikzCacheDirectory.Replace('\', '/')
$tikzCachePathFile = Join-Path $buildDirectory 'tikz-cache-path.tex'
$tikzCachePathDefinition = "\renewcommand{\TikzCacheRoot}{$tikzCachePathForTex/\TikzCacheVariant}"
if (Test-Path -LiteralPath (Join-Path $projectRoot 'build-context.tex')) {
    $tikzCachePathDefinition += "`n\def\BuildContextFile{build-context.tex}"
}
$storedTikzCachePathDefinition = if (Test-Path -LiteralPath $tikzCachePathFile) {
    (Get-Content -LiteralPath $tikzCachePathFile -Raw).Trim()
}
else {
    ''
}
if ($storedTikzCachePathDefinition -ne $tikzCachePathDefinition) {
    Set-Content -LiteralPath $tikzCachePathFile -Encoding utf8 -Value $tikzCachePathDefinition
}

$texmfCacheDirectory = Join-Path $localCacheDirectory 'texmf-cache'
New-Item -ItemType Directory -Force -Path $texmfCacheDirectory | Out-Null
$env:TEXMFVAR = $texmfCacheDirectory
$env:TEXMFCACHE = $texmfCacheDirectory
$auxDirectory = Join-Path $localCacheDirectory 'latex-aux'
New-Item -ItemType Directory -Force -Path $auxDirectory | Out-Null
# Keep intermediate passes out of the viewer; publish only converged PDFs.
$stagingDirectory = Join-Path $localCacheDirectory 'latex-output'
New-Item -ItemType Directory -Force -Path $stagingDirectory | Out-Null
$env:LATEXMK_OUT_DIR = $stagingDirectory.Replace('\', '/')
$env:LATEXMK_AUX_DIR = $auxDirectory.Replace('\', '/')
$latexmk = (Get-Command latexmk -ErrorAction Stop).Source
$lualatex = (Get-Command lualatex -ErrorAction Stop).Source
$latexmkArguments = @(
    '-lualatex',
    '-halt-on-error',
    '-interaction=nonstopmode'
)
if ($Force) {
    $latexmkArguments = @('-g') + $latexmkArguments
}

$tikzSources = @(
    Get-ChildItem -LiteralPath (Join-Path $projectRoot 'content/resources'), (Join-Path $sharedRoot 'resources') -Recurse -Filter '*.tex' -File |
        Where-Object {
            $_.Directory.Name -eq 'tikz' -and
            # These sources need caller-defined commands or document references.
            $_.BaseName -notin @(
                'number_set_inclusions',
                'parameterized_line_representation',
                'plane_representation_conversion'
            )
        } |
        Sort-Object -Property FullName
)
$duplicateTikzNames = $tikzSources | Group-Object -Property BaseName | Where-Object { $_.Count -gt 1 }
if ($duplicateTikzNames) {
    throw "TikZ cache filenames must be unique: $($duplicateTikzNames.Name -join ', ')"
}
# Keep inactive and temporarily unused cached figures for later sessions.
# Cache deletion is an explicit operation through -CleanCache only.

foreach ($variant in $variants) {
    $jobName = [System.IO.Path]::GetFileNameWithoutExtension($variant.File)
    $variantTikzCacheDirectory = Join-Path $tikzCacheDirectory $jobName
    $figuresToBuild = @()
    $reusedFigures = 0
    $existingFigurePdfs = 0

    foreach ($source in $tikzSources) {
        $figureName = $source.BaseName
        $figurePdf = Join-Path $variantTikzCacheDirectory "$figureName.pdf"
        $figureFingerprintFile = Join-Path $variantTikzCacheDirectory "$figureName.sha256"
        $figureRecorderFile = Join-Path $variantTikzCacheDirectory "$figureName.fls"
        $dependencyFingerprint = Get-TikzDependencyFingerprint $figureRecorderFile
        $sourceFingerprint = Get-BuildFileHash $source.FullName
        $figureFingerprint = "$sourceFingerprint`:$($variant.Language)`:$($variant.Cloze)`:$dependencyFingerprint"
        $storedFigureFingerprint = if (Test-Path -LiteralPath $figureFingerprintFile) {
            (Get-Content -LiteralPath $figureFingerprintFile -Raw).Trim()
        }
        else {
            ''
        }

        # Migrate the previous global-hash prefix without recompiling: the
        # independently verified dependency hash already covers real inputs.
        $storedParts = $storedFigureFingerprint.Split(':')
        if ($storedParts.Count -eq 5 -and $storedParts[0] -match '^[0-9a-fA-F]{64}$') {
            $storedFigureFingerprint = $storedParts[1..4] -join ':'
        }
        if (Test-Path -LiteralPath $figurePdf) { $existingFigurePdfs++ }
        if ($dependencyFingerprint -and $storedFigureFingerprint -eq $figureFingerprint -and (Test-Path -LiteralPath $figurePdf)) {
            $reusedFigures++
            continue
        }
        $figuresToBuild += $source
    }

    Write-Host "$($variant.Label): reusing $reusedFigures of $($tikzSources.Count) figures; rebuilding $($figuresToBuild.Count)."
    if ($existingFigurePdfs -eq 0) {
        Write-Warning "No existing figure cache for $($variant.Label): a complete figure rebuild is necessary and can take considerably longer."
    }
    elseif ($reusedFigures -eq 0 -and $figuresToBuild.Count -gt 0) {
        Write-Warning "All recorded figure inputs changed or cannot be verified for $($variant.Label); a complete figure rebuild is necessary despite existing PDFs."
    }
    foreach ($source in $figuresToBuild) {
        $figureName = $source.BaseName
        $figurePdf = Join-Path $variantTikzCacheDirectory "$figureName.pdf"
        $figureFingerprintFile = Join-Path $variantTikzCacheDirectory "$figureName.sha256"
        $figureRecorderFile = Join-Path $variantTikzCacheDirectory "$figureName.fls"
        $sourceFingerprint = Get-BuildFileHash $source.FullName
        Write-Host "  Rebuilding $figureName"
        $projectRootPrefix = $projectRoot.TrimEnd('\') + '\'
        $sharedPrefix = $sharedRoot.TrimEnd('\') + '\'
        if ($source.FullName.StartsWith($projectRootPrefix, [StringComparison]::OrdinalIgnoreCase)) {
            $relativeSource = $source.FullName.Substring($projectRootPrefix.Length).Replace('\', '/')
        }
        elseif ($source.FullName.StartsWith($sharedPrefix, [StringComparison]::OrdinalIgnoreCase)) {
            $relativeSource = '../_shared/' + $source.FullName.Substring($sharedPrefix.Length).Replace('\', '/')
        }
        else {
            throw "Unexpected TikZ source path: $($source.FullName)"
        }
        $texCommand = "\def\ScriptLanguage{$($variant.Language)}\def\ClozeMode{$($variant.Cloze)}\def\TikzCacheVariant{$jobName}\def\TikzSource{$relativeSource}\input{tools/build-tikz.tex}"
        $figureBuildLog = Join-Path $variantTikzCacheDirectory "$figureName.build.log"
        Set-Location -LiteralPath $projectRoot
        & $lualatex '-recorder' '-halt-on-error' '-interaction=nonstopmode' "-output-directory=$variantTikzCacheDirectory" "-jobname=$figureName" $texCommand *> $figureBuildLog
        if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $figurePdf)) {
            Write-Host "[FAILED] TikZ figure $figureName for $($variant.Label)" -ForegroundColor Red
            Get-Content -LiteralPath $figureBuildLog | Out-Host
            exit 1
        }
        $dependencyFingerprint = Get-TikzDependencyFingerprint $figureRecorderFile -Refresh
        if (-not $dependencyFingerprint) {
            throw "Missing or incomplete recorder inputs for TikZ figure $figureName"
        }
        $figureFingerprint = "$sourceFingerprint`:$($variant.Language)`:$($variant.Cloze)`:$dependencyFingerprint"
        Set-Content -LiteralPath $figureFingerprintFile -Value $figureFingerprint -Encoding ascii
        @('.aux', '.log') | ForEach-Object {
            $temporaryFigureFile = Join-Path $variantTikzCacheDirectory "$figureName$_"
            if (Test-Path -LiteralPath $temporaryFigureFile) {
                Remove-Item -LiteralPath $temporaryFigureFile -Force
            }
        }
    }
}

$runVariant = {
    param($root, $variant, $latexmkPath, $arguments, $aux, $output, $fontCache)
    $ErrorActionPreference = 'Stop'
    Set-Location -LiteralPath $root
    $env:TEXMFVAR = $fontCache
    $env:TEXMFCACHE = $fontCache
    $env:LATEXMK_OUT_DIR = $output.Replace('\', '/')
    $env:LATEXMK_AUX_DIR = $aux.Replace('\', '/')
    $jobName = [System.IO.Path]::GetFileNameWithoutExtension($variant.File)
    $log = Join-Path $aux "$jobName.build.log"
    $timer = [System.Diagnostics.Stopwatch]::StartNew()
    $ErrorActionPreference = 'Continue'
    & $latexmkPath @arguments $variant.File *> $log
    $code = $LASTEXITCODE
    $timer.Stop()
    [pscustomobject]@{ JobName=$jobName; Label=$variant.Label; ExitCode=$code; Log=$log; Seconds=$timer.Elapsed.TotalSeconds }
}

Write-Host ('Building all complete documents ({0})...' -f $(if ($Serial) { 'sequential' } else { 'parallel' }))
if ($Serial -or $variants.Count -eq 1) {
    $results = @(foreach ($variant in $variants) {
        & $runVariant $projectRoot $variant $latexmk $latexmkArguments $auxDirectory $stagingDirectory $texmfCacheDirectory
    })
}
else {
    $buildJobs = @(foreach ($variant in $variants) {
        Start-Job -ScriptBlock $runVariant -ArgumentList $projectRoot,$variant,$latexmk,$latexmkArguments,$auxDirectory,$stagingDirectory,$texmfCacheDirectory
    })
    $results = @($buildJobs | Wait-Job | Receive-Job -ErrorAction Stop)
}
$failed = $results.Count -ne $variants.Count
foreach ($result in $results) {
    if ($result.ExitCode -ne 0) {
        $failed = $true
        Write-Host "[FAILED] $($result.Label)" -ForegroundColor Red
        Get-Content -LiteralPath $result.Log | Out-Host
    }
    else {
        $finalLog = Join-Path $auxDirectory ($result.JobName + '.log')
        $finalLogText = [System.IO.File]::ReadAllText($finalLog)
        if ($finalLogText -match 'There were undefined references|Label\(s\) may have changed|Rerun to get cross-references right') {
            throw "References did not converge for $($result.Label); previous published PDFs were retained. See $finalLog"
        }
        foreach ($suffix in @('.pdf', '.synctex.gz')) {
            if (-not (Test-Path -LiteralPath (Join-Path $stagingDirectory ($result.JobName + $suffix)))) {
                throw "Expected output was not created: $($result.JobName)$suffix"
            }
        }
        Write-Host ('[OK] {0}: {1:F2} s' -f $result.Label, $result.Seconds) -ForegroundColor Green
    }
}
if ($failed) { exit 1 }
if ((Get-ProjectSourceFingerprint) -cne $sourceFingerprintBefore) {
    throw 'Sources changed during the build. Previous published PDFs were retained; rerun the full build for the new source state.'
}
foreach ($result in $results) {
    foreach ($suffix in @('.pdf', '.synctex.gz')) {
        Copy-Item -LiteralPath (Join-Path $stagingDirectory ($result.JobName + $suffix)) -Destination (Join-Path $buildDirectory ($result.JobName + $suffix)) -Force
    }
}
Write-Host 'Published all current full PDFs and SyncTeX maps.'

exit 0
}
finally {
    try {
    foreach ($job in $buildJobs) {
        if ($job.State -eq 'Running') { Stop-Job -Job $job }
        Remove-Job -Job $job -Force
    }
    if ($buildLock) {
    $buildDirectory = Join-Path $projectRoot 'build'
    $cachePathFile = Join-Path $buildDirectory 'tikz-cache-path.tex'
    $resolvedBuildDirectory = [System.IO.Path]::GetFullPath($buildDirectory)
    $expectedBuildDirectory = [System.IO.Path]::GetFullPath(
        (Join-Path $projectRoot 'build')
    )
    if ($resolvedBuildDirectory -ne $expectedBuildDirectory) {
        throw "Refusing to clean unexpected build directory: $resolvedBuildDirectory"
    }
    $buildPrefix = $resolvedBuildDirectory.TrimEnd('\') + '\'
    Get-ChildItem -LiteralPath $resolvedBuildDirectory -File -Recurse -Force |
        Where-Object {
            $_.Extension -ine '.pdf' -and
            -not $_.Name.EndsWith('.synctex.gz', [System.StringComparison]::OrdinalIgnoreCase)
        } |
        ForEach-Object {
            $resolvedFile = [System.IO.Path]::GetFullPath($_.FullName)
            if (-not $resolvedFile.StartsWith(
                $buildPrefix, [System.StringComparison]::OrdinalIgnoreCase
            )) {
                throw "Refusing to remove a file outside build directory: $resolvedFile"
            }
            Remove-Item -LiteralPath $resolvedFile -Force
        }
    Get-ChildItem -LiteralPath $resolvedBuildDirectory -File -Recurse -Filter '*.synctex.gz' -Force |
        ForEach-Object {
            $resolvedFile = [System.IO.Path]::GetFullPath($_.FullName)
            if (-not $resolvedFile.StartsWith(
                $buildPrefix, [System.StringComparison]::OrdinalIgnoreCase
            )) {
                throw "Refusing to validate a file outside build directory: $resolvedFile"
            }
            $pdfPath = $resolvedFile.Substring(0, $resolvedFile.Length - '.synctex.gz'.Length) + '.pdf'
            if (-not (Test-Path -LiteralPath $pdfPath -PathType Leaf)) {
                Remove-Item -LiteralPath $resolvedFile -Force
            }
        }
    Get-ChildItem -LiteralPath $resolvedBuildDirectory -Directory -Recurse -Force |
        Sort-Object { $_.FullName.Length } -Descending |
        ForEach-Object {
            $resolvedFolder = [System.IO.Path]::GetFullPath($_.FullName)
            if (-not $resolvedFolder.StartsWith(
                $buildPrefix, [System.StringComparison]::OrdinalIgnoreCase
            )) {
                throw "Refusing to remove a folder outside build directory: $resolvedFolder"
            }
            if (-not (Get-ChildItem -LiteralPath $resolvedFolder -Force | Select-Object -First 1)) {
                Remove-Item -LiteralPath $resolvedFolder -Force
            }
        }
    if (Test-Path -LiteralPath $cachePathFile -PathType Leaf) {
        throw "Generated TikZ cache configuration remained in build directory: $cachePathFile"
    }
    }
    }
    finally {
    $buildTimer.Stop()
    if ($buildLock) { $buildLock.Dispose() }
    Write-Host ('Baudauer: {0:F2} Sekunden' -f $buildTimer.Elapsed.TotalSeconds)
    }
}
