@echo off
REM Test Runner Script - Windows Version
REM Executes all tests and generates a comprehensive test report

setlocal enabledelayedexpansion

echo ======================================
echo Running Test Suite
echo ======================================

REM Check if virtual environment is activated
if "%VIRTUAL_ENV%"=="" (
    echo Virtual environment not activated. Activating...
    call venv\Scripts\activate.bat
    if errorlevel 1 (
        echo Error: Failed to activate virtual environment
        exit /b 1
    )
)

REM Create test reports directory
if not exist "reports" mkdir reports

echo.
echo [1/3] Running unit tests...
python -m pytest tests\test_conflict_analyzer.py -v --tb=short --junit-xml=reports\test_results.xml

echo.
echo [2/3] Running coverage analysis...
python -m pytest tests\test_conflict_analyzer.py --cov=src --cov-report=html:reports\coverage --cov-report=term

echo.
echo [3/3] Generating test summary...
python tests\test_conflict_analyzer.py

echo.
echo ======================================
echo Tests Complete!
echo ======================================
echo.
echo Test Results: reports\test_results.xml
echo Coverage:     reports\coverage\index.html
echo.

endlocal
