@echo off
REM Run the resolver using a specific python executable
if "%~1"=="" (
  echo Usage: run_resolve_with_python.bat C:\path\to\python.exe [input] [output] [conflicts]
  echo Default input: text_label.jsonl
  echo Default output: resolved.jsonl
  echo Default conflicts: conflicts.jsonl
  exit /b 1
)
set PYTHON_EXEC=%~1
set INPUT=%~2
if "%INPUT%"=="" set INPUT=text_label.jsonl
set OUTPUT=%~3
if "%OUTPUT%"=="" set OUTPUT=resolved.jsonl
set CONFLICTS=%~4
if "%CONFLICTS%"=="" set CONFLICTS=conflicts.jsonl

"%PYTHON_EXEC%" -m src.conflict_resolver --input "%INPUT%" --output "%OUTPUT%" --conflicts "%CONFLICTS%"

echo Done. Output files: %OUTPUT% and %CONFLICTS%
