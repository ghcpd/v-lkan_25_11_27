@echo off
REM Main Run Script - Windows Version
REM Executes the analysis pipeline on the input dataset

setlocal enabledelayedexpansion

echo ======================================
echo Label Conflict Analyzer
echo ======================================

REM Check if virtual environment is activated
if "%VIRTUAL_ENV%"=="" (
    echo Virtual environment not activated. Please run: venv\Scripts\activate.bat
    exit /b 1
)

REM Parse command line arguments
set INPUT_FILE=%1
set OUTPUT_DIR=%2

if "!INPUT_FILE!"=="" set INPUT_FILE=text_label.jsonl
if "!OUTPUT_DIR!"=="" set OUTPUT_DIR=output

echo.
echo Configuration:
echo   Input File:  !INPUT_FILE!
echo   Output Dir:  !OUTPUT_DIR!
echo.

REM Check if input file exists
if not exist "!INPUT_FILE!" (
    echo Error: Input file '!INPUT_FILE!' not found!
    exit /b 1
)

echo Starting analysis...
python src\pipeline.py --input "!INPUT_FILE!" --output "!OUTPUT_DIR!"

echo.
echo ======================================
echo Analysis Complete!
echo ======================================
echo.
echo Output files:
echo   Results:      !OUTPUT_DIR!\all_analysis_results.jsonl
echo   Conflicts:    !OUTPUT_DIR!\conflict_samples.jsonl
echo   Summary:      !OUTPUT_DIR!\analysis_summary.json
echo.
echo Reports:
echo   Detailed:     reports\detailed_analysis_report.md
echo   Conflicts:    reports\conflict_analysis_report.md
echo   Metrics:      reports\evaluation_metrics_report.md
echo.

endlocal
