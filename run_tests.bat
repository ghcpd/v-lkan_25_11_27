@echo off
REM Test execution script for Multi-Annotator Conflict Detection System (Windows)
REM Supports both local Python and Docker environments

setlocal enabledelayedexpansion
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo.
echo =============================================
echo Multi-Annotator Conflict Detection System
echo Test Suite Execution (Windows)
echo =============================================
echo.

REM Check for test environment
set DOCKER_AVAILABLE=false
set VENV_AVAILABLE=false

where docker >nul 2>nul
if %errorlevel% equ 0 (
    set DOCKER_AVAILABLE=true
)

if exist "venv" (
    set VENV_AVAILABLE=true
)

REM Create output directories
if not exist "test_reports" mkdir test_reports
if not exist "test_output" mkdir test_output

echo Available test options:
echo 1. Run unit tests (unittest)
echo 2. Run integration tests
echo 3. Run all tests locally
if "%DOCKER_AVAILABLE%"=="true" (
    echo 4. Run all tests with Docker
    echo 5. Run all tests (Docker + local)
    set /p TEST_OPTION="Choose option (1-5) [3]: "
) else (
    set /p TEST_OPTION="Choose option (1-3) [3]: "
)

if "%TEST_OPTION%"=="" set TEST_OPTION=3

REM Execute selected option
if "%TEST_OPTION%"=="1" (
    call :run_unittest
) else if "%TEST_OPTION%"=="2" (
    call :run_integration_tests
) else if "%TEST_OPTION%"=="3" (
    call :run_unittest
    if !errorlevel! equ 0 (
        call :run_integration_tests
    )
) else if "%TEST_OPTION%"=="4" (
    if "%DOCKER_AVAILABLE%"=="true" (
        call :run_docker_tests
    ) else (
        echo [ERROR] Docker is not available
        exit /b 1
    )
) else if "%TEST_OPTION%"=="5" (
    if "%DOCKER_AVAILABLE%"=="true" (
        call :run_unittest
        if !errorlevel! equ 0 (
            call :run_docker_tests
        )
    ) else (
        echo [ERROR] Docker is not available
        exit /b 1
    )
) else (
    echo [ERROR] Invalid option
    exit /b 1
)

set TEST_EXIT_CODE=!errorlevel!

echo.
echo =============================================
if %TEST_EXIT_CODE% equ 0 (
    echo [OK] Test execution completed successfully!
    echo Test reports are available in: test_reports\
) else (
    echo [ERROR] Test execution failed!
    echo Check test_reports\ for details
)
echo =============================================
echo.

exit /b %TEST_EXIT_CODE%

:run_unittest
setlocal
echo.
echo [INFO] Running tests with unittest...
echo.

if "%VENV_AVAILABLE%"=="true" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo [INFO] Running test suite...
python -m unittest discover -s . -p "test_*.py" -v
set RESULT=%errorlevel%

if %RESULT% equ 0 (
    echo [OK] All tests passed!
) else (
    echo [ERROR] Some tests failed ^(exit code: %RESULT%^)
)

endlocal & exit /b %RESULT%

:run_integration_tests
setlocal
echo.
echo [INFO] Running integration tests...
echo.

if "%VENV_AVAILABLE%"=="true" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Test 1: Analysis of provided dataset
echo [INFO] Test 1: Analyzing provided dataset...
python main.py text_label.jsonl ^
    --output test_output\integration_test_results.jsonl ^
    --report test_output\integration_test_report.json ^
    --conflicts-only ^
    -v

if %errorlevel% equ 0 (
    echo [OK] Integration test 1 passed
) else (
    echo [ERROR] Integration test 1 failed
    exit /b 1
)

REM Test 2: Verify output file format
echo [INFO] Test 2: Verifying output file format...
if exist "test_output\integration_test_results.jsonl" (
    echo [OK] Output file created
) else (
    echo [ERROR] Output file not created
    exit /b 1
)

REM Test 3: Verify report generation
echo [INFO] Test 3: Verifying report generation...
if exist "test_output\integration_test_report.json" (
    echo [OK] Report file created
) else (
    echo [ERROR] Report file not created
    exit /b 1
)

echo [OK] All integration tests passed!

endlocal & exit /b 0

:run_docker_tests
setlocal
echo.
echo [INFO] Running tests with Docker...
echo.

if "%DOCKER_AVAILABLE%"=="false" (
    echo [ERROR] Docker is not installed
    exit /b 1
)

echo [INFO] Building Docker image...
docker build -t conflict-detection-system:test .

echo [INFO] Running test suite in Docker...
docker run --rm ^
    -v "%cd%\test_output:/app/output" ^
    -v "%cd%\test_reports:/app/test_reports" ^
    conflict-detection-system:test ^
    python -m unittest discover -s . -p "test_*.py" -v

set RESULT=%errorlevel%

if %RESULT% equ 0 (
    echo [OK] All tests passed in Docker!
) else (
    echo [ERROR] Some tests failed in Docker ^(exit code: %RESULT%^)
)

endlocal & exit /b %RESULT%
