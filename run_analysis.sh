#!/usr/bin/env bash
set -euo pipefail
INPUT=${1:-text_label.jsonl}
OUTPUT=${2:-analysis_output.jsonl}
python analyze_labels.py "$INPUT" -o "$OUTPUT"
