# --- Step 9: Compile Python Script ---
$ProjectFolder = Split-Path -Parent $MyInvocation.MyCommand.Definition
$PythonScript = Join-Path $ProjectFolder "src\ui_with_aya_lang_detect.py"
if (Test-Path $PythonScript) {
    Write-Host "Compiling Python script using PyInstaller..."
    
    # Capture the Scripts directory path from Python
    # $pathToPyInstaller = python -c "import sys, os; print(os.path.join(os.path.dirname(sys.executable), 'Scripts'))"
    
    # Construct the full path to pyinstaller.exe
    # $pyInstallerCmd = Join-Path $pathToPyInstaller "pyinstaller"
    $pyInstallerCmd = "C:\Users\vatsan\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\pyinstaller"

    # Execute PyInstaller with --onefile option
    & $pyInstallerCmd --onefile $PythonScript
} else {
    Write-Host "Error: Python script not found."
}



$pyInstallerCmd = "C:\Users\vatsan\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\pyinstaller"
& $pyInstallerCmd --onefile $PythonScript
