function Get-LectureCacheRoot([ValidateSet('script','sheets')][string]$Product) {
    if ($Product -eq 'sheets' -and $env:EXERCISE_SHEETS_CACHE) {
        return [IO.Path]::GetFullPath($env:EXERCISE_SHEETS_CACHE)
    }
    # Use the persistent profile, not redirected LocalApplicationData.
    $profilePath = [Environment]::GetFolderPath('UserProfile')
    if (-not $profilePath) { throw 'Cannot determine the user profile for the build cache.' }
    $paths = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'cache_paths.json') -Raw -Encoding utf8 |
        ConvertFrom-Json
    $target = [IO.Path]::GetFullPath((Join-Path $profilePath $paths.$Product))
    $profilePrefix = [IO.Path]::GetFullPath($profilePath).TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
    if (-not $target.StartsWith($profilePrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Invalid cache path: $target"
    }
    return $target
}

# Shared dependency checks for the standalone TikZ cache. No build is started here.
function Get-BuildFileHash([string]$Path) {
    if (-not $fileHashes.ContainsKey($Path)) {
        $fileHashes[$Path] = if ([System.IO.File]::Exists($Path)) {
            (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
        }
        else { $null }
    }
    return $fileHashes[$Path]
}

function Get-TikzRelativeDependency([string]$Path) {
    $normalized = $Path.Replace('\', '/')
    $sharedName = $null
    if ($normalized.StartsWith('__shared__/')) { $sharedName = $normalized.Substring(11) }
    elseif ($normalized -match '(?i)/_shared/(.+)$') { $sharedName = $Matches[1] }
    if ($sharedName -and $sharedName.Split('/') -notcontains '..') {
        $sharedFile = Join-Path (Join-Path (Split-Path -Parent $projectRoot) '_shared') $sharedName
        if ([IO.File]::Exists($sharedFile)) { return '__shared__/' + $sharedName }
    }
    if ($normalized.Split('/') -contains '..') { return $null }
    $candidates = [System.Collections.Generic.List[string]]::new()
    if ($normalized -notmatch '^(?:[A-Za-z]:|/)') {
        while ($normalized.StartsWith('./')) { $normalized = $normalized.Substring(2) }
        $candidates.Add($normalized)
    }
    else {
        foreach ($base in @($CanonicalRoot, $projectRoot)) {
            $prefix = $base.Replace('\', '/').TrimEnd('/') + '/'
            if ($normalized.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
                $candidates.Add($normalized.Substring($prefix.Length))
            }
        }
        # Older caches recorded an absolute checkout path. Only existing project
        # inputs are mapped; their original hashes are still checked below.
        foreach ($match in [regex]::Matches($normalized, '(?i)(?:^|(?<=/))(common|content|tools)/')) {
            $candidates.Add($normalized.Substring($match.Groups[1].Index))
        }
        $name = ($normalized -split '/')[-1]
        if ($name -in @('main.tex', 'latexmkrc')) { $candidates.Add($name) }
    }
    $rootPrefix = [System.IO.Path]::GetFullPath($projectRoot).TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
    foreach ($relative in $candidates) {
        if (-not $relative -or $relative.Split('/') -contains '..') { continue }
        try { $actual = [System.IO.Path]::GetFullPath((Join-Path $projectRoot $relative)) }
        catch [System.ArgumentException] { continue }
        if ($actual.StartsWith($rootPrefix, [System.StringComparison]::OrdinalIgnoreCase) -and
            [System.IO.File]::Exists($actual)) {
            return $relative
        }
    }
    return $null
}

function Get-TikzDependencyFingerprint([string]$RecorderFile, [switch]$Refresh) {
    $dependencyFile = [System.IO.Path]::ChangeExtension($RecorderFile, '.deps')
    if (-not $Refresh -and [System.IO.File]::Exists($dependencyFile)) {
        $inputs = [System.IO.File]::ReadAllLines($dependencyFile)
    }
    else {
        if (-not [System.IO.File]::Exists($RecorderFile)) { return $null }
        $inputs = @([System.IO.File]::ReadAllLines($RecorderFile) | ForEach-Object {
            if ($_.StartsWith('INPUT ')) {
                $relative = Get-TikzRelativeDependency $_.Substring(6)
                if ($relative -and -not $relative.StartsWith('build/', [System.StringComparison]::OrdinalIgnoreCase)) {
                    $relative
                }
            }
        } | Sort-Object -Unique)
        # New metadata is relative to the checkout and survives directory moves.
        [System.IO.File]::WriteAllLines($dependencyFile, [string[]]$inputs)
    }
    if ($inputs.Count -eq 0) { return $null }
    $lines = [System.Collections.Generic.List[string]]::new()
    foreach ($inputPath in $inputs) {
        $relative = Get-TikzRelativeDependency $inputPath
        if (-not $relative) { return $null }
        $actualInput = if ($relative.StartsWith('__shared__/')) {
            Join-Path (Join-Path (Split-Path -Parent $projectRoot) '_shared') $relative.Substring(11)
        } else { Join-Path $projectRoot $relative }
        $inputHash = Get-BuildFileHash $actualInput
        if (-not $inputHash) { return $null }
        # Retain the recorded spelling for old cache signatures; current file
        # contents, not an old location or modification time, determine reuse.
        $lines.Add(('{0}:{1}' -f $inputPath, $inputHash))
    }
    $hash = [System.Security.Cryptography.SHA256]::Create()
    try {
        [System.BitConverter]::ToString(
            $hash.ComputeHash([System.Text.Encoding]::UTF8.GetBytes(($lines -join "`n")))
        ).Replace('-', '').ToLowerInvariant()
    }
    finally { $hash.Dispose() }
}
