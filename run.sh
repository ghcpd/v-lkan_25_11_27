#!/bin/bash

# Main Run Script
# Executes the analysis pipeline on the input dataset

set -e

echo "======================================"
echo "Label Conflict Analyzer"
echo "======================================"

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Virtual environment not activated. Please run: source venv/bin/activate"
    exit 1
fi

# Parse command line arguments
INPUT_FILE="${1:-text_label.jsonl}"
OUTPUT_DIR="${2:-output}"

echo ""
echo "Configuration:"
echo "  Input File:  $INPUT_FILE"
echo "  Output Dir:  $OUTPUT_DIR"
echo ""

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: Input file '$INPUT_FILE' not found!"
    exit 1
fi

echo "Starting analysis..."
python src/pipeline.py --input "$INPUT_FILE" --output "$OUTPUT_DIR"

echo ""
echo "======================================"
echo "Analysis Complete!"
echo "======================================"
echo ""
echo "Output files:"
echo "  Results:      $OUTPUT_DIR/all_analysis_results.jsonl"
echo "  Conflicts:    $OUTPUT_DIR/conflict_samples.jsonl"
echo "  Summary:      $OUTPUT_DIR/analysis_summary.json"
echo ""
echo "Reports:"
echo "  Detailed:     reports/detailed_analysis_report.md"
echo "  Conflicts:    reports/conflict_analysis_report.md"
echo "  Metrics:      reports/evaluation_metrics_report.md"
echo ""
