@echo off
setlocal
set INPUT=%1
if "%INPUT%"=="" set INPUT=text_label.jsonl
set OUTPUT=%2
if "%OUTPUT%"=="" set OUTPUT=analysis_output.jsonl
python analyze_labels.py "%INPUT%" -o "%OUTPUT%"
