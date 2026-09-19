param(
    [Parameter(Mandatory=$true)][string]$Job,
    [int]$TimeoutSeconds = 120
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$jobPath = (Resolve-Path -LiteralPath $Job).Path
$allowedRoot = [IO.Path]::GetFullPath((Join-Path $projectRoot 'build\worker-jobs')) + '\'
if (-not $jobPath.StartsWith($allowedRoot, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Worker jobs must be inside this project build/worker-jobs directory.'
}
$request = Get-Content -LiteralPath (Join-Path $jobPath 'request.json') -Raw | ConvertFrom-Json
function Assert-Hash([string]$Path, [string]$Expected) {
    if ((Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $Expected) {
        throw "Worker input changed: $Path"
    }
}
Assert-Hash $request.emulator $request.emulator_sha256
Assert-Hash (Join-Path $jobPath 'worker.uae') $request.config_sha256
Assert-Hash (Join-Path $jobPath 'kick.rom') $request.rom_sha256
Assert-Hash (Join-Path $jobPath 'sys\s\startup-sequence') $request.guest_script_sha256
foreach ($entry in $request.pinned_inputs) {
    Assert-Hash (Join-Path $projectRoot $entry.path) $entry.sha256
}
foreach ($entry in $request.source_files) {
    Assert-Hash (Join-Path (Join-Path $jobPath 'sys\work') $entry.path) $entry.sha256
}
$donePath = Join-Path $jobPath 'sys\work\done.txt'
if (Test-Path -LiteralPath $donePath) { throw 'Completed job may not be rerun in place.' }
$workerProcess = $null
try {
    $workerProcess = Start-Process -FilePath $request.emulator -ArgumentList @('-f', "`"$(Join-Path $jobPath 'worker.uae')`"") -WorkingDirectory $jobPath -WindowStyle Hidden -PassThru
    $workerProcess.Id | Set-Content -LiteralPath (Join-Path $jobPath 'worker.pid')
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    while (-not (Test-Path -LiteralPath $donePath)) {
        $workerProcess.Refresh()
        if ($workerProcess.HasExited) { throw "Worker exited before completion: $($workerProcess.ExitCode)" }
        if ([DateTime]::UtcNow -gt $deadline) { throw 'Historical worker timed out; job files and logs retained.' }
        Start-Sleep -Milliseconds 500
    }
    Write-Output "Guest job completed: $jobPath"
} finally {
    if ($workerProcess) {
        $workerProcess.Refresh()
        if (-not $workerProcess.HasExited) { Stop-Process -Id $workerProcess.Id }
    }
}
