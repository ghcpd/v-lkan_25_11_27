@echo off
REM Multi-Annotator Label Conflict Analyzer - Windows Setup Script
REM This script sets up the environment and prepares the system for analysis

setlocal enabledelayedexpansion

echo ======================================
echo Setting up Label Conflict Analyzer
echo ======================================

REM Check Python version
echo [1/4] Checking Python version...
python --version
if errorlevel 1 (
    echo Error: Python 3 is not installed or not in PATH
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [2/4] Creating virtual environment...
    python -m venv venv
) else (
    echo [2/4] Virtual environment already exists
)

REM Activate virtual environment
echo [3/4] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    exit /b 1
)

REM Install dependencies
echo [4/4] Installing dependencies...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt

echo.
echo ======================================
echo Setup Complete!
echo ======================================
echo.
echo To use the analyzer, run:
echo   venv\Scripts\activate.bat
echo   python src\pipeline.py --input text_label.jsonl --output output
echo.

endlocal
