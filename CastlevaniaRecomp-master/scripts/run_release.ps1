$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $repoRoot

Remove-Item Env:PSX_CASTLE_15308_SOURCE_MODE -ErrorAction SilentlyContinue
Remove-Item Env:PSX_A110_FORCE_C9278_LT -ErrorAction SilentlyContinue
Remove-Item Env:PSX_CASTLE_TIMER_PTR_MODE -ErrorAction SilentlyContinue
Remove-Item Env:PSX_TRACE_A110_DEEP -ErrorAction SilentlyContinue
Remove-Item Env:PSX_TRACE_A110_ORDER -ErrorAction SilentlyContinue
Remove-Item Env:PSX_TRACE_A110_EXIT -ErrorAction SilentlyContinue

$cue = "CastlevaniaRecomp-master\isos\Castlevania - Symphony of the Night (USA).cue"
& ".\CastlevaniaRecomp-master\build\CastlevaniaRecomp.exe" --cue $cue
