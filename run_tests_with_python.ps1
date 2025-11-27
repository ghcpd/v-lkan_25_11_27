param(
    [string]$PythonPath = "D:\package\venv310\Scripts\python.exe",
    [switch]$InstallDeps = $true
)

# Ensure the path is quoted for safety
Write-Host "Using Python: $PythonPath"

if ($InstallDeps) {
    & $PythonPath -m pip install --upgrade pip
    & $PythonPath -m pip install -r requirements.txt
}

# Run pytest
& $PythonPath -m pytest -q
