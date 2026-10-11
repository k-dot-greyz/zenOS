# Compatibility shim. Canonical file lives under dex/<bank>/scripts/powershell/.
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $here
$target = Join-Path $root "dex\\ops\\scripts\\powershell\\bridge-launcher.ps1"
if (-not (Test-Path $target)) {
  Write-Error "canonical script missing: $target"
  exit 1
}
& $target @args
