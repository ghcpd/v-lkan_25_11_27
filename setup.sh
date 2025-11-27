@echo off
python -m venv venv
call venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Environment ready. Use 'call venv\Scripts\activate' to activate the virtual env on Windows."