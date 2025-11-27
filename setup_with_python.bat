@echo off
if "%~1"=="" (
  echo Usage: setup_with_python.bat C:\path\to\python.exe
  exit /b 1
)
set PYTHON_EXEC=%~1

REM Create venv using provided interpreter
"%PYTHON_EXEC%" -m venv venv
if errorlevel 1 (
  echo Failed creating venv using %PYTHON_EXEC%
  exit /b 1
)

REM Activate venv and install requirements
call venv\Scripts\activate
echo Using %PYTHON_EXEC% to install requirements
venv\Scripts\python -m pip install --upgrade pip
venv\Scripts\python -m pip install -r requirements.txt

echo "Done. Activate the virtual environment with: call venv\Scripts\activate"
exit /b 0
