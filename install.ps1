# zenOS Universal Installer for Windows - One Command to Rule Them All! 🧘
# Usage (from a checkout): .\install.ps1
# Bootstrap: $env:ZENOS_GITHUB_OWNER = "YOUR_GITHUB_USERNAME"; iwr -useb https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/zenOS/main/install.ps1 | iex

Write-Host "🧘 zenOS Universal Installer for Windows" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Function to install dependencies
function Install-Dependencies {
    Write-Host "🐍 Installing Python packages..." -ForegroundColor Yellow
    pip install rich click aiohttp aiofiles psutil pyyaml textblob nltk
    
    Write-Host "📥 Downloading NLTK data..." -ForegroundColor Yellow
    python -m textblob.download_corpora
}

# Function to setup environment
function Setup-Environment {
    Write-Host "🔧 Setting up environment..." -ForegroundColor Yellow
    
    # Add to PowerShell profile
    $profileContent = @"
# zenOS environment
`$env:PYTHONPATH = "`$PWD"
Set-Alias -Name zenos -Value "python zen/cli.py"
"@
    
    if (Test-Path $PROFILE) {
        Add-Content -Path $PROFILE -Value $profileContent
    } else {
        New-Item -Path $PROFILE -ItemType File -Force
        Add-Content -Path $PROFILE -Value $profileContent
    }
    
    Write-Host "✅ Environment setup complete!" -ForegroundColor Green
}

# Function to test installation
function Test-Installation {
    Write-Host "🧪 Testing installation..." -ForegroundColor Yellow
    
    $env:PYTHONPATH = "$PWD"
    python zen/cli.py --help | Out-Null
    
    Write-Host "✅ Installation test passed!" -ForegroundColor Green
}

# Function to install sample plugin
function Install-SamplePlugin {
    Write-Host "🔌 Installing sample plugin..." -ForegroundColor Yellow
    
    $env:PYTHONPATH = "$PWD"
    python zen/cli.py plugins install ./examples/sample-plugin --local
    
    Write-Host "✅ Sample plugin installed!" -ForegroundColor Green
}

function Get-DotEnvValue([string]$Key) {
    $paths = @(".env", (Join-Path $PSScriptRoot "env.example"))
    foreach ($path in $paths) {
        if (-not (Test-Path $path)) { continue }
        foreach ($line in Get-Content $path) {
            if ($line -match "^\s*#" -or $line -notmatch "=") { continue }
            $name, $val = $line.Split("=", 2)
            if ($name.Trim() -eq $Key -and $val.Trim()) { return $val.Trim().Trim("'`"") }
        }
    }
    return $null
}

function Get-ZenosCloneUrl {
    $owner = $env:ZENOS_GITHUB_OWNER
    if (-not $owner) { $owner = $env:GITHUB_OWNER }
    if (-not $owner) { $owner = $env:GITHUB_USERNAME }
    if (-not $owner) { $owner = Get-DotEnvValue "ZENOS_GITHUB_OWNER" }
    $repoUrl = $env:ZENOS_REPO_URL
    if (-not $repoUrl) { $repoUrl = Get-DotEnvValue "ZENOS_REPO_URL" }
    if ($repoUrl) { return $repoUrl }
    if (-not $owner -or $owner -eq "YOUR_GITHUB_USERNAME") {
        try { $owner = $null; $remote = git remote get-url origin 2>$null
            if ($remote -match "github.com[:/]([^/]+)/([^/.]+)") { $owner = $Matches[1] }
        } catch {}
    }
    if (-not $owner -or $owner -eq "YOUR_GITHUB_USERNAME") {
        throw "GitHub origin is not configured. Set ZENOS_GITHUB_OWNER in .env or clone this repo."
    }
    $repo = $env:ZENOS_REPO_NAME
    if (-not $repo) { $repo = Get-DotEnvValue "ZENOS_REPO_NAME" }
    if (-not $repo) { $repo = "zenOS" }
    return "https://github.com/$owner/$repo.git"
}

# Main installation
function Main {
    if ((Test-Path "pyproject.toml") -and (Test-Path "zen")) {
        Write-Host "Using existing zenOS checkout at $PWD" -ForegroundColor Yellow
    } elseif (-not (Test-Path "zenOS")) {
        Write-Host "Cloning zenOS repository..." -ForegroundColor Yellow
        git clone (Get-ZenosCloneUrl)
        Set-Location zenOS
    } else {
        Set-Location zenOS
    }

    if ((Test-Path "env.example") -and -not (Test-Path ".env")) {
        Copy-Item "env.example" ".env"
        Write-Host "Wrote .env from env.example — set OPENROUTER_API_KEY (and origin) once there." -ForegroundColor Yellow
    }
    
    # Install dependencies
    Install-Dependencies
    
    # Setup environment
    Setup-Environment
    
    # Test installation
    Test-Installation
    
    # Install sample plugin
    Install-SamplePlugin
    
    Write-Host ""
    Write-Host "🎉 zenOS installation complete!" -ForegroundColor Green
    Write-Host "==============================" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Quick start:" -ForegroundColor Cyan
    Write-Host "  `$env:PYTHONPATH = \"`$PWD\""
    Write-Host "  python zen/cli.py --help"
    Write-Host "  python zen/cli.py plugins list"
    Write-Host "  python zen/cli.py plugins execute com.example.text-processor text.summarize \"Hello world!\""
    Write-Host ""
    Write-Host "Full guides (in this checkout):" -ForegroundColor Cyan
    Write-Host "  Mobile:  docs/guides/QUICKSTART_MOBILE.md"
    Write-Host "  Windows: docs/guides/QUICKSTART_WINDOWS.md"
    Write-Host "  Linux:   docs/guides/QUICKSTART_LINUX.md"
    Write-Host ""
    Write-Host "Welcome to zenOS! Enjoy the zen!" -ForegroundColor Magenta
}

# Run main function
Main
