# Label Conflict Analyzer

This project detects conflicts in multi-annotator datasets, analyzes causes, and suggests a resolved label with confidence reasoning.

## Quick start

1. Ensure Python 3.8+ is installed.
3. On Windows (cmd.exe):
    - Run: `setup.sh` to install dependencies.
    - Run: `run_tests.sh` to run tests.
    - Or run the analyzer from the workspace root:
       - `python conflict_analyzer.py --input text_label.jsonl --out_conflicts conflicts.jsonl --out_resolved resolved.jsonl`
       - Alternatively use the single-file convenience script:
          `python conflict_analyzer_single.py --input text_label.jsonl --out_conflicts conflicts.jsonl --out_resolved resolved.jsonl`

Or with Docker:

   docker build -t label-analyzer .
   docker run --rm -v "$PWD":/workspace label-analyzer

## File layout
- `analyzer/analyze_conflicts.py` - main script to analyze input JSONL and write resolved/conflict outputs.
- `text_label.jsonl` - input file with the multi-annotator dataset.
- `conflict_samples.jsonl` - generated output with conflict highlighting.
- `resolved_labels.jsonl` - generated resolved dataset with suggestions and reasoning.
- `tests/` - contains pytest suite.

## Outputs
Each record in the outputs includes:
```
{
 "id": ..., 
 "text": "...",
 "labels": [{"annotator":"A1","label":"Positive"}, ...],
 "is_conflict": true/false,
 "conflict_reason": "...",
 "suggested_label": {"label":"Positive","confidence":0.9,"explanation":"majority_vote"}
}
```

## Notes
- The system uses heuristics (contrast words, sentiment word lists) to analyze reasons for disagreements.
- Suggested labels leverage majority vote with lexical cues, and lower confidence on ties or contrast words.
