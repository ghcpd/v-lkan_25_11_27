@echo off
REM Simple setup to create a virtual environment and install dependencies
python -m venv .venv
.\.venv\Scripts\pip install --upgrade pip
.\.venv\Scripts\pip install -r requirements.txt
echo Setup complete. Activate the venv with: .\.venv\Scripts\activate
