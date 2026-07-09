# ducky/run.ps1 — USB / Windows tap-to-bootstrap entry

param(
    [string]$Profile = $(if ($env:DUCKY_PROFILE) { $env:DUCKY_PROFILE } else { "developer" })
)

$ErrorActionPreference = "Stop"
$DuckyRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ZenOSRoot = Split-Path -Parent $DuckyRoot
$env:DUCKY_PROFILE = $Profile

function Log($msg) { Write-Host "🦆 $msg" }

Log "ducky quickstart — zenOS env pipeline"
Log "zenOS root: $ZenOSRoot"
Log "profile: $Profile"

Log "running env-doctor"
python "$DuckyRoot\env_doctor.py" --zenos-root $ZenOSRoot
if ($LASTEXITCODE -ne 0) {
    Write-Warning "env-doctor reported issues — continuing hydration"
}

Log "hydrating scaffold"
& bash "$DuckyRoot\hydrate.sh"
if ($LASTEXITCODE -ne 0) {
    throw "hydrate.sh failed"
}

if (Test-Path "$ZenOSRoot\setup.py") {
    switch ($Profile) {
        "minimal" {
            Log "running programmatic setup: validate-only"
            Push-Location $ZenOSRoot
            python setup.py --validate-only
            Pop-Location
        }
        "offline" {
            Log "running offline setup hooks"
            if (Test-Path "$ZenOSRoot\scripts\setup-offline.sh") {
                bash "$ZenOSRoot\scripts\setup-offline.sh"
            }
        }
        default {
            Log "running programmatic setup: unattended"
            Push-Location $ZenOSRoot
            python setup.py --unattended
            Pop-Location
        }
    }
} else {
    Write-Warning "setup.py not found — clone zenOS first"
}

Log "done — check .zen-hydration\ for local deets + manifest"
