# zenOS Private Development Workflow
# PowerShell version for Windows

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

# Configuration
$owner = $env:ZENOS_GITHUB_OWNER
if (-not $owner) { $owner = $env:GITHUB_OWNER }
if (-not $owner) { $owner = $env:GITHUB_USERNAME }
if (-not $owner) { $owner = "YOUR_GITHUB_USERNAME" }
$PRIVATE_REPO = if ($env:ZENOS_PRIVATE_REPO) { $env:ZENOS_PRIVATE_REPO } else { "https://github.com/$owner/zenOS-dev.git" }
$DEVELOPMENT_BRANCH = "development"
$MAIN_BRANCH = "main"

function Show-Help {
    Write-Host "🧘 zenOS Private Development Workflow" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\scripts\private-dev.ps1 [COMMAND]"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  setup     - Set up private remote and development branch"
    Write-Host "  sync      - Sync development branch to private repo"
    Write-Host "  pull      - Pull latest from private repo"
    Write-Host "  promote   - Promote development to main (public)"
    Write-Host "  status    - Show current status"
    Write-Host "  help      - Show this help"
    Write-Host ""
}

function Setup-Private {
    Write-Host "🔧 Setting up private development workflow..." -ForegroundColor Yellow
    
    # Check if private remote exists
    try {
        $null = git remote get-url private
        Write-Host "✅ Private remote already configured" -ForegroundColor Green
    }
    catch {
        Write-Host "📝 Adding private remote..." -ForegroundColor Yellow
        git remote add private $PRIVATE_REPO
        Write-Host "✅ Private remote added" -ForegroundColor Green
    }
    
    # Ensure we're on development branch
    $currentBranch = git branch --show-current
    if ($currentBranch -ne $DEVELOPMENT_BRANCH) {
        Write-Host "📝 Switching to development branch..." -ForegroundColor Yellow
        try {
            git checkout -b $DEVELOPMENT_BRANCH
        }
        catch {
            git checkout $DEVELOPMENT_BRANCH
        }
    }
    
    # Push development branch to private repo
    Write-Host "📤 Pushing development branch to private repo..." -ForegroundColor Yellow
    git push -u private $DEVELOPMENT_BRANCH
    
    Write-Host "✅ Private development setup complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Workflow:" -ForegroundColor Cyan
    Write-Host "  • Work on 'development' branch"
    Write-Host "  • Use '.\scripts\private-dev.ps1 sync' to push to private repo"
    Write-Host "  • Use '.\scripts\private-dev.ps1 promote' to merge to public main"
}

function Sync-To-Private {
    Write-Host "📤 Syncing development to private repo..." -ForegroundColor Yellow
    
    # Ensure we're on development branch
    $currentBranch = git branch --show-current
    if ($currentBranch -ne $DEVELOPMENT_BRANCH) {
        Write-Host "❌ Not on development branch. Switch to development first." -ForegroundColor Red
        exit 1
    }
    
    # Add all changes
    git add -A
    
    # Commit if there are changes
    $stagedChanges = git diff --cached --name-only
    if ($stagedChanges) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        git commit -m "Development: $timestamp"
    }
    
    # Push to private repo
    git push private $DEVELOPMENT_BRANCH
    
    Write-Host "✅ Synced to private repo" -ForegroundColor Green
}

function Pull-From-Private {
    Write-Host "📥 Pulling latest from private repo..." -ForegroundColor Yellow
    
    git pull private $DEVELOPMENT_BRANCH
    
    Write-Host "✅ Pulled from private repo" -ForegroundColor Green
}

function Promote-To-Public {
    Write-Host "🚀 Promoting development to public main..." -ForegroundColor Yellow
    
    # Switch to main
    git checkout $MAIN_BRANCH
    
    # Merge development
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    git merge $DEVELOPMENT_BRANCH --no-ff -m "Merge development: $timestamp"
    
    # Push to public
    git push origin $MAIN_BRANCH
    
    Write-Host "✅ Promoted to public main" -ForegroundColor Green
    Write-Host "💡 You can now continue development on the development branch" -ForegroundColor Cyan
}

function Show-Status {
    Write-Host "zenOS Development Status" -ForegroundColor Cyan
    Write-Host "================================================"
    
    # Current branch
    $currentBranch = git branch --show-current
    Write-Host "Current Branch: $currentBranch" -ForegroundColor Yellow
    
    # Remote status
    Write-Host "`nRemotes:" -ForegroundColor Blue
    git remote -v | ForEach-Object { Write-Host "  $_" }
    
    # Uncommitted changes
    $uncommitted = git status --porcelain
    if ($uncommitted) {
        Write-Host "`n⚠️  Uncommitted changes:" -ForegroundColor Yellow
        $uncommitted | ForEach-Object { Write-Host "  $_" }
    }
    else {
        Write-Host "`n✅ Working directory clean" -ForegroundColor Green
    }
    
    # Branch status
    Write-Host "`nBranch Status:" -ForegroundColor Blue
    if ($currentBranch -eq $DEVELOPMENT_BRANCH) {
        Write-Host "  ✅ On development branch" -ForegroundColor Green
    }
    else {
        Write-Host "  ⚠ Not on development branch" -ForegroundColor Yellow
    }
    
    # Check if private remote exists
    try {
        $null = git remote get-url private
        Write-Host "  ✅ Private remote configured" -ForegroundColor Green
    }
    catch {
        Write-Host "  ❌ Private remote not configured" -ForegroundColor Red
    }
}

# Main script logic
switch ($Command.ToLower()) {
    "setup" { Setup-Private }
    "sync" { Sync-To-Private }
    "pull" { Pull-From-Private }
    "promote" { Promote-To-Public }
    "status" { Show-Status }
    "help" { Show-Help }
    default {
        Write-Host "❌ Unknown command: $Command" -ForegroundColor Red
        Show-Help
        exit 1
    }
}
