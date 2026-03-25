$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $repoRoot

$env:PSXRECOMP_DEBUG_BLACKSCREEN = "1"
$env:PSX_TRACE_A110_EXIT = "1"
$env:PSX_TRACE_A110_ORDER = "1"
$env:PSX_TRACE_A110_DEEP = "1"
$env:PSX_CASTLE_TIMER_OVERRIDE = "1"
Remove-Item Env:PSX_CASTLE_15308_SOURCE_MODE -ErrorAction SilentlyContinue

$cue = "CastlevaniaRecomp-master\isos\Castlevania - Symphony of the Night (USA).cue"
$out = "CastlevaniaRecomp-master\blackscreen_gate_deep_check.log"

& ".\CastlevaniaRecomp-master\build\CastlevaniaRecomp.exe" --cue $cue *> $out
Write-Host "Log salvo em: $out"
