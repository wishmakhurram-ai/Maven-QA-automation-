# PowerShell script to install Allure Framework on Windows
# This script downloads and sets up Allure CLI

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Allure Framework Installation Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Java is installed
Write-Host "Checking Java installation..." -ForegroundColor Yellow
try {
    $javaVersion = java -version 2>&1 | Select-Object -First 1
    Write-Host "[OK] Java is installed: $javaVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Java is not installed!" -ForegroundColor Red
    Write-Host "Please install Java from: https://www.oracle.com/java/technologies/downloads/" -ForegroundColor Yellow
    exit 1
}

# Allure download URL (latest version)
$allureVersion = "2.24.0"
$allureUrl = "https://github.com/allure-framework/allure2/releases/download/$allureVersion/allure-commandline-$allureVersion.zip"
$downloadPath = "$env:TEMP\allure-commandline-$allureVersion.zip"
$extractPath = "$env:ProgramFiles\allure"

Write-Host ""
Write-Host "Downloading Allure Framework..." -ForegroundColor Yellow
Write-Host "URL: $allureUrl" -ForegroundColor Gray
Write-Host "This may take a few minutes..." -ForegroundColor Gray

try {
    # Download Allure
    Invoke-WebRequest -Uri $allureUrl -OutFile $downloadPath -UseBasicParsing
    Write-Host "[OK] Download completed" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Download failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Manual installation steps:" -ForegroundColor Yellow
    Write-Host "1. Download from: https://github.com/allure-framework/allure2/releases" -ForegroundColor White
    Write-Host "2. Extract to: C:\Program Files\allure" -ForegroundColor White
    Write-Host "3. Add C:\Program Files\allure\bin to PATH" -ForegroundColor White
    exit 1
}

Write-Host ""
Write-Host "Extracting Allure..." -ForegroundColor Yellow

try {
    # Create extraction directory
    if (Test-Path $extractPath) {
        Remove-Item $extractPath -Recurse -Force
    }
    New-Item -ItemType Directory -Path $extractPath -Force | Out-Null
    
    # Extract ZIP file
    Expand-Archive -Path $downloadPath -DestinationPath $extractPath -Force
    
    # Find the actual allure folder (it might be nested)
    $allureBin = Get-ChildItem -Path $extractPath -Recurse -Filter "allure.bat" | Select-Object -First 1
    if ($allureBin) {
        $actualAllurePath = $allureBin.Directory.Parent.FullName
        Write-Host "[OK] Extraction completed to: $actualAllurePath" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Could not find allure.bat after extraction" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] Extraction failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Adding Allure to PATH..." -ForegroundColor Yellow

try {
    $allureBinPath = Join-Path $actualAllurePath "bin"
    
    # Get current PATH
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    
    # Check if already in PATH
    if ($currentPath -notlike "*$allureBinPath*") {
        # Add to user PATH
        $newPath = "$currentPath;$allureBinPath"
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        Write-Host "[OK] Added to user PATH" -ForegroundColor Green
        Write-Host "  Note: You may need to restart your terminal for PATH changes to take effect" -ForegroundColor Yellow
    } else {
        Write-Host "[OK] Already in PATH" -ForegroundColor Green
    }
} catch {
    Write-Host "[WARNING] Could not add to PATH automatically: $_" -ForegroundColor Yellow
    Write-Host "Please manually add to PATH: $allureBinPath" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Cleaning up..." -ForegroundColor Yellow
Remove-Item $downloadPath -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To verify installation, restart your terminal and run:" -ForegroundColor Yellow
Write-Host "  allure --version" -ForegroundColor White
Write-Host ""
Write-Host "If the command does not work, you may need to:" -ForegroundColor Yellow
Write-Host "1. Restart your terminal/PowerShell" -ForegroundColor White
if ($allureBinPath) {
    Write-Host "2. Or manually add to PATH: $allureBinPath" -ForegroundColor White
}
Write-Host ""
