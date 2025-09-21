# 🌉 Ultimate Bridge Launcher - PowerShell Version
# Launches the complete airi-zenOS bridge system on Windows

param(
    [string]$Command = "interactive",
    [string]$Query = "",
    [string]$Mode = "auto"
)

# Colors for output (removed unused $Colors variable)

# Logging functions
function Write-Log {
    param([string]$Message, [string]$Color = "White")
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] $Message" -ForegroundColor $Color
}

function Write-Success {
    param([string]$Message)
    Write-Log "✅ $Message" -Color Green
}

function Write-Error {
    param([string]$Message)
    Write-Log "❌ $Message" -Color Red
}

function Write-Warning {
    param([string]$Message)
    Write-Log "⚠️ $Message" -Color Yellow
}

# Check if we're in the right directory
function Test-ZenOSDirectory {
    if (-not (Test-Path "zen\cli.py")) {
        Write-Error "Not in zenOS directory. Please run from zenOS root."
        exit 1
    }
    Write-Success "zenOS directory found"
}

# Check Python installation
function Test-PythonInstallation {
    try {
        $pythonVersion = python --version 2>&1
        Write-Success "Python found: $pythonVersion"
        return $true
    }
    catch {
        Write-Error "Python not found. Please install Python 3.8+"
        return $false
    }
}

# Install dependencies
function Install-Dependencies {
    Write-Log "Installing Python dependencies..." -Color Blue
    
    try {
        pip install -e . | Out-Null
        Write-Success "Dependencies installed"
    }
    catch {
        Write-Error "Failed to install dependencies"
        exit 1
    }
}

# Create mobile context
function Get-MobileContext {
    $context = @{
        Device = "Windows Desktop"
        Mode = "Desktop Bridge"
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        HasInternet = Test-NetConnection -ComputerName "8.8.8.8" -Port 53 -InformationLevel Quiet
        BatteryLevel = 100  # Desktop doesn't have battery
        IsCharging = $true
    }
    
    return $context
}

# Process query through zenOS
function Invoke-ZenOSProcessing {
    param(
        [string]$Query,
        [hashtable]$Context
    )
    
    Write-Log "Processing through zenOS: $($Query.Substring(0, [Math]::Min(50, $Query.Length)))..." -Color Blue
    
    try {
        # Create context file
        $contextFile = [System.IO.Path]::GetTempFileName()
        $Context | ConvertTo-Json | Out-File -FilePath $contextFile -Encoding UTF8
        
        # Run zenOS
        $result = python -m zen.cli chat $Query --context-file $contextFile 2>&1
        
        # Clean up
        Remove-Item $contextFile -Force
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "zenOS processing complete"
            return $result
        }
        else {
            Write-Error "zenOS processing failed: $result"
            return "zenOS processing failed"
        }
    }
    catch {
        Write-Error "zenOS processing error: $($_.Exception.Message)"
        return "zenOS processing error"
    }
}

# Process through airi (simulated)
function Invoke-AiriProcessing {
    param(
        [string]$Input,
        [hashtable]$Context
    )
    
    Write-Log "Processing through airi..." -Color Magenta
    
    # Simulate airi processing
    $airiResponse = @"
📱 airi enhancement: $Input
🔋 Mobile-optimized response
📱 Context-aware processing complete
🌉 airi-zenOS bridge active
"@
    
    Write-Success "airi processing complete"
    return $airiResponse
}

# Main processing function
function Invoke-MainProcessing {
    param(
        [string]$Query,
        [string]$Mode = "auto"
    )
    
    Write-Log "🌉 Starting airi-zenOS Bridge Processing..." -Color Cyan
    
    # Get mobile context
    $context = Get-MobileContext
    
    # Process through zenOS
    $zenosResponse = Invoke-ZenOSProcessing -Query $Query -Context $context
    
    # Process through airi
    $airiResponse = Invoke-AiriProcessing -Input $zenosResponse -Context $context
    
    # Format output
    $output = @"
🧘 zenOS:
   $zenosResponse

📱 airi:
   $airiResponse

🌉 Bridge Status:
   Device: $($context.Device)
   Mode: $($context.Mode)
   Internet: $(if ($context.HasInternet) { "✅" } else { "❌" })
   Timestamp: $($context.Timestamp)
"@
    
    Write-Host $output -ForegroundColor White
    Write-Success "Processing complete"
}

# Interactive mode
function Start-InteractiveMode {
    Write-Log "🌉 Starting airi-zenOS Bridge in interactive mode..." -Color Cyan
    Write-Host "Welcome to the airi-zenOS Bridge!" -ForegroundColor Magenta
    Write-Host "Type 'exit' to quit, 'help' for commands" -ForegroundColor Yellow
    Write-Host ""
    
    while ($true) {
        $userInput = Read-Host "airi-zenOS"
        
        switch ($userInput.ToLower()) {
            "exit" { 
                Write-Log "Exiting interactive mode"
                Write-Host "Goodbye! 👋" -ForegroundColor Yellow
                break 
            }
            "help" {
                Write-Host "Available commands:" -ForegroundColor Green
                Write-Host "  help     - Show this help"
                Write-Host "  exit     - Exit the bridge"
                Write-Host "  <query>  - Process text query"
            }
            "" { continue }
            default {
                Invoke-MainProcessing -Query $userInput
            }
        }
        Write-Host ""
    }
}

# Quick mode
function Start-QuickMode {
    param([string]$Query)
    
    Write-Log "⚡ Quick mode processing..." -Color Yellow
    
    try {
        $result = python -m zen.cli chat $Query --model claude-3-haiku --max-tokens 200 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "⚡ Quick: $result" -ForegroundColor Green
        }
        else {
            Write-Error "Quick processing failed: $result"
        }
    }
    catch {
        Write-Error "Quick processing error: $($_.Exception.Message)"
    }
}

# Setup function
function Initialize-Bridge {
    Write-Log "🌉 Initializing airi-zenOS Bridge..." -Color Cyan
    
    # Check directory
    Test-ZenOSDirectory
    
    # Check Python
    if (-not (Test-PythonInstallation)) {
        exit 1
    }
    
    # Install dependencies
    Install-Dependencies
    
    Write-Success "Bridge initialized successfully"
}

# Main function
function Main {
    param(
        [string]$Command,
        [string]$Query,
        [string]$Mode
    )
    
    # Initialize
    Initialize-Bridge
    
    # Process command
    switch ($Command.ToLower()) {
        "interactive" {
            Start-InteractiveMode
        }
        "quick" {
            if ($Query) {
                Start-QuickMode -Query $Query
            }
            else {
                Write-Error "No query provided for quick mode"
            }
        }
        "help" {
            Write-Host "airi-zenOS Bridge - Ultimate Mobile AI Stack" -ForegroundColor Magenta
            Write-Host ""
            Write-Host "Usage:" -ForegroundColor Green
            Write-Host "  .\bridge-launcher.ps1 [command] [query]" -ForegroundColor White
            Write-Host ""
            Write-Host "Commands:" -ForegroundColor Green
            Write-Host "  interactive  - Start interactive mode (default)"
            Write-Host "  quick        - Quick processing mode"
            Write-Host "  help         - Show this help"
            Write-Host ""
            Write-Host "Examples:" -ForegroundColor Green
            Write-Host "  .\bridge-launcher.ps1"
            Write-Host "  .\bridge-launcher.ps1 quick 'Hello world'"
            Write-Host "  .\bridge-launcher.ps1 interactive"
        }
        default {
            if ($Query) {
                Invoke-MainProcessing -Query $Query -Mode $Mode
            }
            else {
                Start-InteractiveMode
            }
        }
    }
}

# Run main function
Main -Command $Command -Query $Query -Mode $Mode
