# # Install-ChocolateyOffline.ps1
# # This script installs Chocolatey offline from the "chocolatey.2.4.3" folder inside the project directory.
# # It automatically requests administrative privileges if not already running as Administrator.

# # --- Step 1: Request Admin Privileges ---
# $CurrentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent()
# $Principal = New-Object System.Security.Principal.WindowsPrincipal($CurrentUser)
# $AdminRole = [System.Security.Principal.WindowsBuiltInRole]::Administrator

# if (-not $Principal.IsInRole($AdminRole)) {
#     Write-Host "Requesting Administrator privileges..."
#     Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
#     exit
# }

# # --- Step 2: Determine Paths ---
# # Get the directory where this script is located (the project folder)
# $ProjectFolder = Split-Path -Parent $MyInvocation.MyCommand.Definition

# # Define the offline Chocolatey package folder
# $ChocoOfflineFolder = Join-Path $ProjectFolder "chocolatey.2.4.3"

# # Define the expected location of the Chocolatey installation script
# $ChocoInstallScript = Join-Path $ChocoOfflineFolder "tools\chocolateyInstall\chocolateyInstall.ps1"

# # --- Step 3: Pre-checks ---
# # Check if Chocolatey is already installed
# if (Test-Path "$env:ProgramData\Chocolatey\choco.exe") {
#     Write-Host "Chocolatey is already installed on this machine."
#     exit
# }

# # Ensure the Chocolatey installation script exists
# if (!(Test-Path $ChocoInstallScript)) {
#     Write-Host "Error: Chocolatey installation script not found at:"
#     Write-Host "       $ChocoInstallScript"
#     Write-Host "Please ensure the offline Chocolatey package is correctly extracted in the 'chocolatey.2.4.3' folder."
#     exit 1
# }

# # --- Step 4: Install Chocolatey ---
# # Temporarily bypass execution policy for this session
# Set-ExecutionPolicy Bypass -Scope Process -Force

# Write-Host "Installing Chocolatey from the offline package..."
# # Execute the installation script
# & $ChocoInstallScript

# # --- Step 5: Update System PATH ---
# $ChocoBinPath = "$env:ProgramData\Chocolatey\bin"
# if (-not ($env:Path -match [regex]::Escape($ChocoBinPath))) {
#     [System.Environment]::SetEnvironmentVariable("Path", $env:Path + ";" + $ChocoBinPath, [System.EnvironmentVariableTarget]::Machine)
#     $env:Path += ";" + $ChocoBinPath
#     Write-Host "Updated system PATH to include Chocolatey binaries."
# }

# # --- Step 6: Verify Installation ---
# if (Test-Path "$env:ProgramData\Chocolatey\choco.exe") {
#     Write-Host "Chocolatey installed successfully!"
#     Write-Host "Chocolatey version:"
#     choco -v
# } else {
#     Write-Host "Chocolatey installation failed. Please check the offline package and try again."
# }

# # --- Step 7: Reset Execution Policy ---
# # Reset the execution policy to the default Restricted mode for security
# Set-ExecutionPolicy Restricted -Scope Process -Force

# # --- Step 8:  ---
# $ChocoOfflineSoftwareFolder = Join-Path $ProjectFolder "chocolatey_softwares"
# choco install ffmpeg --source $ChocoOfflineSoftwareFolder\ffmpeg.nupkg -y

# # --- Step 9: install python requirements ---
# pip install -r requirements.txt

# # --- Step 10: run the python scripts ---
# pyinstaller --onefile ui_with_aya_lang_detect.py



# Install-ChocolateyOffline.ps1
# This script installs Chocolatey offline and sets up required dependencies.

# --- Step 1: Request Admin Privileges ---
$CurrentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent()
$Principal = New-Object System.Security.Principal.WindowsPrincipal($CurrentUser)
$AdminRole = [System.Security.Principal.WindowsBuiltInRole]::Administrator

if (-not $Principal.IsInRole($AdminRole)) {
    Write-Host "Requesting Administrator privileges..."
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

# --- Step 2: Determine Paths ---
$ProjectFolder = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ChocoOfflineFolder = Join-Path $ProjectFolder "chocolatey.2.4.3"
$ChocoInstallScript = Join-Path $ChocoOfflineFolder "tools\chocolateyInstall\chocolateyInstall.ps1"

# --- Step 3: Pre-checks ---
if (Test-Path "$env:ProgramData\Chocolatey\choco.exe") {
    Write-Host "Chocolatey is already installed."
} elseif (!(Test-Path $ChocoInstallScript)) {
    Write-Host "Error: Chocolatey installation script not found at $ChocoInstallScript"
    exit 1
} else {
    # --- Step 4: Install Chocolatey ---
    Set-ExecutionPolicy Bypass -Scope Process -Force
    Write-Host "Installing Chocolatey from offline package..."
    & $ChocoInstallScript
}

# --- Step 5: Update System PATH ---
$ChocoBinPath = "$env:ProgramData\Chocolatey\bin"
if (-not ($env:Path -match [regex]::Escape($ChocoBinPath))) {
    [System.Environment]::SetEnvironmentVariable("Path", $env:Path + ";" + $ChocoBinPath, [System.EnvironmentVariableTarget]::Machine)
    $env:Path += ";" + $ChocoBinPath
    Write-Host "Updated system PATH."
}

# --- Step 6: Verify Installation ---
if (Test-Path "$env:ProgramData\Chocolatey\choco.exe") {
    Write-Host "Chocolatey installed successfully!"
    choco -v
} else {
    Write-Host "Chocolatey installation failed."
    exit 1
}

# --- Step 7: Install FFmpeg Offline ---
$ChocoOfflineSoftwareFolder = Join-Path $ProjectFolder "chocolatey_softwares"

if (Test-Path $ChocoOfflineSoftwareFolder) {
    Write-Host "Installing FFmpeg from offline package..."
    choco install ffmpeg --source $ChocoOfflineSoftwareFolder -y
} else {
    Write-Host "Error: Offline software folder not found: $ChocoOfflineSoftwareFolder"
}

# --- Step 8: Install Python Requirements ---
$RequirementsFile = Join-Path $ProjectFolder "requirements.txt"
if (Test-Path $RequirementsFile) {
    Write-Host "Installing Python requirements..."
    pip install -r $RequirementsFile
} else {
    Write-Host "Error: requirements.txt not found."
}

# # --- Step 9: Compile Python Script ---
# $PythonScript = Join-Path $ProjectFolder "src\ui_with_aya_lang_detect.py"
# if (Test-Path $PythonScript) {
#     Write-Host "Compiling Python script using PyInstaller..."
#     $pathToPyInstaller = python -c "import sys, os; print(os.path.join(os.path.dirname(sys.executable), 'Scripts'))"
#     $pathToPyInstaller\pyinstaller --onefile $PythonScript
# } else {
#     Write-Host "Error: Python script not found."
# }

# --- Step 9: Compile Python Script ---
$PythonScript = Join-Path $ProjectFolder "src\ui_with_aya_lang_detect.py"
if (Test-Path $PythonScript) {
    Write-Host "Compiling Python script using PyInstaller..."
    
    # Capture the Scripts directory path from Python
    $pathToPyInstaller = python -c "import sys, os; print(os.path.join(os.path.dirname(sys.executable), 'Scripts'))"
    
    # Construct the full path to pyinstaller.exe
    $pyInstallerCmd = Join-Path $pathToPyInstaller "pyinstaller.exe"
    
    # Execute PyInstaller with --onefile option
    & $pyInstallerCmd --onefile $PythonScript
} else {
    Write-Host "Error: Python script not found."
}

# --- Step 10: Reset Execution Policy ---
Set-ExecutionPolicy Restricted -Scope Process -Force
