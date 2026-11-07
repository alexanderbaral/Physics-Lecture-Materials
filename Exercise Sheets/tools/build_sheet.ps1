param($projectRoot, $cacheRoot, $workingCopy, $latexmk, $lang, $sheetEntry, $mode, $runId, $Warm, $Force, $outputRoot)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $projectRoot
        $sheetTimer = [Diagnostics.Stopwatch]::StartNew()
        $id = $sheetEntry.Id
        $variant = if ($mode -eq 'on') { "${lang}_solutions" } else { $lang }
        $outDir = Join-Path $outputRoot "build/$variant"
        # Isolated runs avoid locked recorder/auxiliary files in synced folders.
        $auxDir = (Join-Path $cacheRoot "latex_runs/$variant/$id/$runId").Replace('\','/')
        $cacheReused = $false
        if ($Warm) {
            $previous = Get-ChildItem -LiteralPath (Join-Path $cacheRoot "latex_runs/$variant/$id") -Directory -ErrorAction SilentlyContinue |
                Where-Object { $_.Name -match '^\d{8}_\d{9}$' -and
                    (Test-Path -LiteralPath (Join-Path $_.FullName "$id.fdb_latexmk")) -and
                    (Test-Path -LiteralPath (Join-Path $_.FullName "$id.pdf")) } |
                Sort-Object Name -Descending | Select-Object -First 1
            if ($previous) {
                $auxDir = $previous.FullName.Replace('\','/')
                $cacheReused = $true
            }
        }
        $latexPasses = 0
        $title = if ($lang -eq 'de') { $sheetEntry.TitleDe } else { $sheetEntry.TitleEn }
        $title = $title.Replace('~', ' ')
        $prefix = if ($lang -eq 'de') { ([char]0x00DC).ToString() + 'bungsblatt' } else { 'Exercise Sheet' }
        $fileStem = "$prefix $($sheetEntry.Number) - $title"
        if ($mode -eq 'on') {
            if ($lang -eq 'de') { $fileStem += (' (mit L' + [char]0x00F6 + 'sungen)') }
            else { $fileStem += ' (with Solutions)' }
        }
        $fileName = "$fileStem.pdf"
        $output = Join-Path $outDir $fileName
        New-Item -ItemType Directory -Force -Path $outDir,$auxDir | Out-Null
        # Only request-local staging is replaced; published PDFs remain intact.
        if (Test-Path -LiteralPath $output) { Remove-Item -LiteralPath $output }
        $entry = "content/chapters_$lang/$($sheetEntry.Entry)"
        $status = 'failed'
        $detail = ''
        if (-not (Test-Path -LiteralPath $entry)) {
            $detail = "Missing content: $entry"
        } else {
            $suffix = if ($mode -eq 'on') { '-solutions' } else { '' }
            $wrapper = "$auxDir/entry.tex"
            $tex = "\def\SheetId{$id}`n\input{tools/build-$lang$suffix.tex}`n"
            if (-not (Test-Path -LiteralPath $wrapper) -or [IO.File]::ReadAllText($wrapper) -ne $tex) {
                [IO.File]::WriteAllText($wrapper, $tex, [Text.UTF8Encoding]::new($false))
            }
            $buildLog = "$auxDir/build.log"
            Write-Host "Building $variant/$id ..."
            $savedErrorPreference = $ErrorActionPreference
            $ErrorActionPreference = 'Continue'
            $extraArguments = if ($Force) { @('-g') } else { @() }
            try {
                Set-Location -LiteralPath $workingCopy
                & $latexmk @extraArguments '-lualatex' '-halt-on-error' '-interaction=nonstopmode' "-outdir=$auxDir" "-auxdir=$auxDir" '-out2dir=' "-jobname=$id" $wrapper *> $buildLog
                $buildExit = $LASTEXITCODE
            } finally { Set-Location -LiteralPath $projectRoot }
            $ErrorActionPreference = $savedErrorPreference
            $latexPasses = @(Select-String -LiteralPath $buildLog -Pattern "Run number \d+ of rule 'lualatex'").Count
            if ($buildExit -eq 0 -and (Test-Path -LiteralPath "$auxDir/$id.pdf")) {
                Copy-Item -LiteralPath "$auxDir/$id.pdf" -Destination $output
                $status = 'ok'
                $detail = "build/$variant/$fileName"
            } else { $detail = "See $buildLog" }
        }
        Write-Host "[$status] $variant/$id : $detail"
        [pscustomobject]@{sheet=$id;language=$lang;solutions=$mode;status=$status;detail=$detail;seconds=[math]::Round($sheetTimer.Elapsed.TotalSeconds,3);cache_reused=$cacheReused;latex_passes=$latexPasses;cache_directory=$auxDir}
