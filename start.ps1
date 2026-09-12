# zenOS Quick Start Script for Windows

Write-Host "🧘 Welcome to zenOS - AI CLI Tool" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check for Docker
try {
    docker --version | Out-Null
} catch {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    Write-Host "   Visit: https://docs.docker.com/desktop/windows/install/" -ForegroundColor Yellow
    exit 1
}

# Check for Docker Compose
try {
    docker-compose --version | Out-Null
} catch {
    Write-Host "❌ Docker Compose is not installed. It should come with Docker Desktop." -ForegroundColor Red
    Write-Host "   Visit: https://docs.docker.com/compose/install/" -ForegroundColor Yellow
    exit 1
}

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "📝 No .env file found. Creating from template..." -ForegroundColor Yellow
    Copy-Item "env.example" ".env"
    Write-Host ""
    Write-Host "⚠️  Please edit .env and add your OpenRouter API key" -ForegroundColor Yellow
    Write-Host "   Get your key at: https://openrouter.ai/keys" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   Then run this script again."
    exit 1
}

# Check if API key is set (empty + placeholders count as unset)
function Get-DotEnvValue([string]$Key) {
    if (-not (Test-Path ".env")) { return $null }
    foreach ($line in Get-Content ".env") {
        if ($line -match "^\s*#" -or $line -notmatch "=") { continue }
        $name, $val = $line.Split("=", 2)
        if ($name.Trim() -eq $Key) { return $val.Trim().Trim("'`"") }
    }
    return $null
}

$placeholders = @(
    "",
    "your-api-key-here",
    "sk-or-v1-your-api-key-here",
    "YOUR_API_KEY",
    "<your-api-key>",
    "changeme"
)
$key = $env:OPENROUTER_API_KEY
if (-not $key) { $key = Get-DotEnvValue "OPENROUTER_API_KEY" }
if (-not $key -or $placeholders -contains $key) {
    Write-Host "⚠️  Please set OPENROUTER_API_KEY in .env (copy env.example)" -ForegroundColor Yellow
    Write-Host "   Get your key at: https://openrouter.ai/keys" -ForegroundColor Cyan
    exit 1
}

Write-Host "✅ Configuration looks good!" -ForegroundColor Green
Write-Host ""

# Build and start services
Write-Host "🔨 Building Docker images..." -ForegroundColor Cyan
docker-compose build

Write-Host ""
Write-Host "🚀 Starting zenOS services..." -ForegroundColor Cyan
docker-compose up -d

Write-Host ""
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check service health
Write-Host "🏥 Checking service health..." -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "✨ zenOS is ready!" -ForegroundColor Green
Write-Host ""
Write-Host "Try these commands:" -ForegroundColor Cyan
Write-Host '  docker-compose exec zen-cli zen "What is zenOS?"' -ForegroundColor White
Write-Host "  docker-compose exec zen-cli zen chat" -ForegroundColor White
Write-Host "  docker-compose logs -f zen-cli" -ForegroundColor White
Write-Host ""
Write-Host "To stop zenOS:" -ForegroundColor Cyan
Write-Host "  docker-compose down" -ForegroundColor White
Write-Host ""
Write-Host "Enjoy the zen of AI! 🧘" -ForegroundColor Green
