@echo off
REM Run tests using a specified python executable
if "%~1"=="" (
  echo Usage: run_tests_with_python.bat C:\path\to\python.exe
  exit /b 1
)
set PYTHON_EXEC=%~1
"%PYTHON_EXEC%" -m pip install --upgrade pip
"%PYTHON_EXEC%" -m pip install -r requirements.txt
"%PYTHON_EXEC%" -m pytest -q
