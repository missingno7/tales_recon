param(
    [Parameter(Mandatory=$true)][string]$PipeName,
    [Parameter(Mandatory=$true)][string]$Output,
    [ValidateRange(1,256)][int]$Instructions = 64
)
# Bounded read-only PC history through WinUAE's existing DBG IPC interface.
# The pipe name must come from this instance's WinUAE log. No guessed instance,
# debugger writes, memory patching, input simulation, or emulator replacement.
$ErrorActionPreference = 'Stop'
$repoRoot = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$outputPath = [IO.Path]::GetFullPath($Output)
$scratchRoot = [IO.Path]::GetFullPath((Join-Path $repoRoot 'build')) + '\'
if (-not $outputPath.StartsWith($scratchRoot, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Runtime captures must be inside build/.'
}
if ($PipeName -notmatch '^[A-Za-z0-9_.-]+$') { throw 'Use the local instance pipe name from its log.' }
$pipe = [IO.Pipes.NamedPipeClientStream]::new('.', $PipeName, [IO.Pipes.PipeDirection]::InOut)
try {
    $pipe.Connect(5000)
    $pipe.ReadMode = [IO.Pipes.PipeTransmissionMode]::Message
    $command = [Text.Encoding]::UTF8.GetBytes("DBG H $Instructions" + [char]0)
    # WinUAE distinguishes UTF-8 requests with a BOM.
    $message = [byte[]](0xef,0xbb,0xbf) + $command
    $pipe.Write($message,0,$message.Length)
    $pipe.Flush()
    $buffer = New-Object byte[] 16384
    $result = [IO.MemoryStream]::new()
    do {
        $read = $pipe.ReadAsync($buffer,0,$buffer.Length)
        if (-not $read.Wait(5000)) { throw 'WinUAE history read timed out.' }
        $count = $read.Result
        if ($count -eq 0) { throw 'WinUAE pipe closed without a history response.' }
        $result.Write($buffer,0,$count)
        if ($result.Length -gt 65536) { throw 'Runtime response exceeds bounded capture.' }
    } while (-not $pipe.IsMessageComplete)
    $text = [Text.Encoding]::UTF8.GetString($result.ToArray()).TrimEnd([char]0)
    if ($text -eq '404' -or $text -eq '501') { throw "WinUAE did not support history capture: $text" }
    [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($outputPath)) | Out-Null
    if ([IO.File]::Exists($outputPath)) { throw 'Preserve prior captures; choose a new output file.' }
    [IO.File]::WriteAllText($outputPath,$text,[Text.UTF8Encoding]::new($false))
    Write-Output "Captured bounded WinUAE PC history: $outputPath"
} finally { $pipe.Dispose() }
