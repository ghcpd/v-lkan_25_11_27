@echo off
REM Setup development environment on Windows (cmd)
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "Setup complete. Run run_tests.sh to execute tests."
pause
