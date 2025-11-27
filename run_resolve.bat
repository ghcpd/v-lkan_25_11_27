@echo off
python -m src.conflict_resolver --input text_label.jsonl --output resolved.jsonl --conflicts conflicts.jsonl

echo Done. Outputs: resolved.jsonl and conflicts.jsonl
