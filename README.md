# Conflict Detection and Resolution for Multi-Annotator Datasets

This project implements a lightweight tool to detect inconsistent labeling among multiple annotators and provide a reasoned suggested label for each sample.

Usage
	- Build and run locally:
		- Windows (cmd):
			```cmd
			call setup.sh
			call venv\Scripts\activate
			python -m src.conflict_resolver --input text_label.jsonl --output resolved.jsonl --conflicts conflicts.jsonl
			```
		- Or use a specific Python executable to build venv (e.g., `D:\package\venv310\Scripts\python.exe`):
			```cmd
			setup_with_python.bat "D:\package\venv310\Scripts\python.exe"
			call venv\Scripts\activate
			python -m src.conflict_resolver --input text_label.jsonl --output resolved.jsonl --conflicts conflicts.jsonl
			```
		- PowerShell (use the `&` operator to call executables with arguments):
			```powershell
			# Install requirements and run tests using a specific Python executable
			Set-Location -Path 'D:\Downloads\1\oswe-mini-prime\v-lkan_25_11_27'
			& "D:\package\venv310\Scripts\python.exe" -m pip install --upgrade pip
			& "D:\package\venv310\Scripts\python.exe" -m pip install -r requirements.txt
			& "D:\package\venv310\Scripts\python.exe" -m pytest -q

			# Run the resolver directly in PowerShell
			& "D:\package\venv310\Scripts\python.exe" -m src.conflict_resolver --input text_label.jsonl --output resolved.jsonl --conflicts conflicts.jsonl
			```

		- Or use the PowerShell wrappers we added:
			```powershell
			# Run tests using a specific Python
			.\run_tests_with_python.ps1 -PythonPath 'D:\package\venv310\Scripts\python.exe'

			# Run the resolver with a specific Python
			.\run_resolve_with_python.ps1 -PythonPath 'D:\package\venv310\Scripts\python.exe' -Input 'text_label.jsonl' -Output 'resolved.jsonl' -Conflicts 'conflicts.jsonl'
			```
		- Docker:
			```bash
			docker build -t conflict-resolver .
			docker run --rm -v %CD%:/app -w /app conflict-resolver
			```

Testing
	- Run unit tests with pytest:
		```cmd
		call run_tests.sh
		```

Outputs
	- `resolved.jsonl` contains per-sample suggested labels and reasons.
	- `conflicts.jsonl` contains only samples identified as conflicts.

Design
	- Heuristics-based detection: lexicon sentiment scoring and pattern matching are used to explain disagreements.
	- Resolver uses majority vote with lexicon tie-breakers and confidence values.

Limitations and future improvements
	- You can swap the lexicon with a lightweight transformer or a more complex rule-based NLP model for higher quality.
	- More nuanced multi-aspect reasoning is possible by adding aspect-level classifiers.

License
	- MIT
