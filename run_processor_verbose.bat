@echo off
REM Run the label processor with verbose logging and capture logs to file
set PY=%~1
if "%PY%"=="" set PY=python
%PY% src\label_processor.py -i text_label.jsonl -o conflicts_output.jsonl --log-file processor.log --verbose
if exist processor.log type processor.log
