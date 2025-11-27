# v-lkan_25_11_27

## Label Conflict Analyzer

This project detects, analyzes, and resolves inconsistent labeling in multi-annotator datasets (JSONL format).

### Project Layout
- `text_label.jsonl` – sample dataset
- `label_conflict_resolver/` – core logic (loading, conflict detection, heuristics, suggestions)
- `analyze_labels.py` – CLI entrypoint
- `tests/` – pytest suite and report template
- `analysis_output.jsonl` / `conflicts_output.jsonl` – generated reports (after running analysis)

### Setup
```cmd
"D:\package\venv310\Scripts\python.exe" -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Run Analysis
```cmd
python analyze_labels.py text_label.jsonl -o analysis_output.jsonl
python analyze_labels.py text_label.jsonl --conflicts-only -o conflicts_output.jsonl
```
Or use the helper scripts:
```cmd
run_analysis.bat
```

### Run Tests
```cmd
run_tests.bat
```
Generates a concise pytest run; fill `tests/test_report_template.md` for reporting.

### Docker
```cmd
docker build -t label-conflict-analyzer .
docker run --rm -v %CD%:/app label-conflict-analyzer
```

### Output Schema (per sample)
```
{
	"id": <id>,
	"text": "<text>",
	"labels": [{"annotator":"A1","label":"..."}, ...],
	"is_conflict": true|false,
	"conflict_reason": "<reason or null>",
	"suggested_label": {
			"label": "<final_label>",
			"majority_label": "<majority_or_null>",
			"confidence": <0-1>,
			"reason": "<explanation>"
	}
}
```

### Notes
- Conflict reason/suggestion is heuristic (contrast markers, ambiguity, dominance ratios, etc.).
- Deterministic outputs support collaborative workflows.