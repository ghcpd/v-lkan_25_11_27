@echo off
REM Setup script for Multi-Annotator Conflict Detection System (Windows)
REM Supports both local environment and Docker setup

setlocal enabledelayedexpansion
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo.
echo =============================================
echo Multi-Annotator Conflict Detection System
echo Setup Script (Windows)
echo =============================================
echo.

REM Check if Docker is available
where docker >nul 2>nul
if %errorlevel% equ 0 (
    echo [OK] Docker is installed
    set DOCKER_AVAILABLE=true
) else (
    echo [WARNING] Docker not found. Will use local Python environment.
    set DOCKER_AVAILABLE=false
)

REM Check if Python is available
where python >nul 2>nul
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
    echo [OK] Python found: !PYTHON_VERSION!
    set PYTHON_AVAILABLE=true
) else (
    echo [ERROR] Python 3 is required but not found
    set PYTHON_AVAILABLE=false
)

echo.
echo =============================================
echo Installation Options
echo =============================================
echo.

if "%DOCKER_AVAILABLE%"=="true" (
    echo 1. Docker-based setup (recommended)
    echo 2. Local Python environment setup
    echo 3. Both Docker and local setup
    echo.
    set /p INSTALL_OPTION="Choose installation option (1-3): "
) else (
    echo 1. Local Python environment setup
    set /p INSTALL_OPTION="Enter 1 to continue with local Python setup: "
)

REM Execute selected option
if "%INSTALL_OPTION%"=="1" (
    call :setup_local_environment
) else if "%INSTALL_OPTION%"=="2" (
    call :setup_docker_environment
) else if "%INSTALL_OPTION%"=="3" (
    call :setup_local_environment
    call :setup_docker_environment
) else (
    echo [ERROR] Invalid option
    exit /b 1
)

echo.
echo =============================================
echo Setup Complete!
echo =============================================
echo.
echo Next steps:
echo 1. Review the README.md file for usage examples
echo 2. Run tests with: run_tests.bat
echo 3. Analyze your dataset with: python main.py ^<input_file^>
echo.

exit /b 0

:setup_local_environment
setlocal
echo.
echo =============================================
echo Setting up Local Python Environment
echo =============================================
echo.

if "%PYTHON_AVAILABLE%"=="false" (
    echo [ERROR] Python 3 is required
    exit /b 1
)

echo Creating Python virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment
    exit /b 1
)
echo [OK] Virtual environment created

echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    exit /b 1
)
echo [OK] Virtual environment activated

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    exit /b 1
)
echo [OK] Dependencies installed

if not exist "output" mkdir output
echo [OK] Output directory created

echo.
echo [OK] Local environment setup complete!
echo.
echo To activate the environment in the future, run:
echo   venv\Scripts\activate.bat
echo.

endlocal
exit /b 0

:setup_docker_environment
setlocal
echo.
echo =============================================
echo Setting up Docker Environment
echo =============================================
echo.

if "%DOCKER_AVAILABLE%"=="false" (
    echo [ERROR] Docker is not installed
    exit /b 1
)

echo Building Docker image...
docker build -t conflict-detection-system:latest .
if %errorlevel% neq 0 (
    echo [ERROR] Failed to build Docker image
    exit /b 1
)
echo [OK] Docker image built

if not exist "output" mkdir output
echo [OK] Output directory created

echo.
echo [OK] Docker setup complete!
echo.
echo To run with Docker, use:
echo   docker run -v %%cd%%\output:/app/output conflict-detection-system:latest main.py text_label.jsonl
echo.

endlocal
exit /b 0
