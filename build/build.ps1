$ErrorActionPreference = 'Stop'

# Helper to download and install .NET SDK if not already present
function Install-DotNetSdk {
    $installDir = "$env:USERPROFILE\dotnet-sdk"
    $dotnetExe = Join-Path $installDir 'dotnet.exe'
    if (Test-Path $dotnetExe) {
        Write-Host ".NET SDK already installed at $dotnetExe"
        return $dotnetExe
    }
    Write-Host "Downloading dotnet-install script..."
    $scriptPath = "$env:USERPROFILE\dotnet-install.ps1"
    Invoke-WebRequest -Uri 'https://dot.net/v1/dotnet-install.ps1' -OutFile $scriptPath -UseBasicParsing
    Write-Host "Installing .NET SDK 8.0 to $installDir..."
    & powershell -NoProfile -ExecutionPolicy Bypass -Command "& {\n        \$ErrorActionPreference = 'Stop'\n        . '$scriptPath' -Channel 8.0 -InstallDir '$installDir'\n    }"
    if (Test-Path $dotnetExe) {
        Write-Host "Installation succeeded."
        return $dotnetExe
    } else {
        Write-Error "Failed to install .NET SDK. Check the logs."
        exit 1
    }
}

# Determine PyInstaller path (same as before)
$pyInstallerPath = "$env:USERPROFILE\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts\pyinstaller.exe"
if (-not (Test-Path $pyInstallerPath)) {
    Write-Host "PyInstaller not found, installing via pip..."
    python -m pip install --upgrade pip
    python -m pip install pyinstaller
    $pyInstallerPath = "$env:USERPROFILE\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts\pyinstaller.exe"
}

# Ensure .NET SDK is available
$dotnetPath = Install-DotNetSdk

# Step 1: Build Python backend
Write-Host "Building Python backend..."
& $pyInstallerPath --onefile --distpath "${PSScriptRoot}\backend" "${PSScriptRoot}\..\backend_server.py"

# Step 2: Build .NET WinForms host
Write-Host "Building .NET WinForms host..."
Push-Location "${PSScriptRoot}\..\OmniCoreWin"
& $dotnetPath restore
& $dotnetPath build -c Release -o "${PSScriptRoot}\release"
Pop-Location

# Step 3: Copy backend executable
Write-Host "Copying backend executable..."
Copy-Item "${PSScriptRoot}\backend\backend_server.exe" -Destination "${PSScriptRoot}\release" -Force

Write-Host "Packaging complete. Executable located at ${PSScriptRoot}\release\OmniCoreWin.exe"
