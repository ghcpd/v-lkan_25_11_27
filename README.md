# Multi-Annotator Conflict Detection and Resolution

This project contains tools to detect, analyze, and propose resolutions for inconsistent labeling in multi-annotator datasets saved in JSONL format.

Quickstart:
- Create a virtual environment and install dependencies:
	- `setup.sh` (Windows): creates `.venv` and installs packages
- Run the processor on the dataset:
	- `python src\label_processor.py -i text_label.jsonl -o conflicts_output.jsonl`
- Run tests:
	- `run_tests.sh`

Files:
- `src/label_processor.py`: Core processing logic -> conflict detection, reasons, suggested resolution
- `tests/test_processor.py`: Automated tests verifying detection and suggestions
- `requirements.txt`: Dependency list (vaderSentiment, pytest)
- `Dockerfile`: Reproducible container to run tests
- `run_tests.sh` and `setup.sh` for quick local execution

Design and heuristics:
- Uses VADER for sentiment heuristics to assist in conflict resolution.
- Suggests final labels based on majority label with sentiment tie-breakers and confidence scoring.
- Provides `conflict_reason` to explain possible reasons for disagreement (ambiguous phrasing, multi-aspect content, polarizing sentiment, policy confusion).

Notes:
- The heuristics are explainable and traceable; you can substitute a more advanced model or custom policies as needed.

How to integrate with a larger pipeline:
- The `src/label_processor.py` module exposes `LabelProcessor(input_path)` and `process(output_path)` to make integration straightforward.

Contact:
- If you need help extending the resolution strategies or adding adjudication workflows, open an issue or PR.

Verbose logging and runtime logs:
- Use `--verbose` to enable DEBUG logs printed to console and `--log-file <path>` to save logs to file.
- Quick run (Windows):
	- `run_processor_verbose.bat "D:\\package\\venv310\\Scripts\\python.exe"` -- runs the processor with verbose logging and writes `processor.log`.

Log contents:
- The log file contains detailed per-sample processing lines, including sample id, sentiment compound score, conflict reason if any, suggested label and confidence.
- You can use the `scripts/show_conflicts.py` to print conflict entries for a quick human review.