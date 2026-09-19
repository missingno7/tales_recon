# Windows-hosted verification only. This does not build a reconstructed game.
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $projectRoot
try {
    python tools/census.py --check
    if ($LASTEXITCODE -ne 0) { throw 'Evidence verification failed.' }
    python -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw 'Evidence regression tests failed.' }
} finally {
    Pop-Location
}
