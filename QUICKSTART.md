# Quick Start Guide

## 1. Setup (One-time)

### Windows
```cmd
setup.bat
venv\Scripts\activate.bat
```

### Linux/macOS
```bash
bash setup.sh
source venv/bin/activate
```

## 2. Run Analysis

### Windows
```cmd
run.bat
```

### Linux/macOS
```bash
bash run.sh
```

## 3. View Results

Open generated files:
- `output/all_analysis_results.jsonl` - All samples with analysis
- `output/conflict_samples.jsonl` - Only conflicting samples
- `output/analysis_summary.json` - Summary statistics
- `reports/detailed_analysis_report.md` - Full detailed report
- `reports/conflict_analysis_report.md` - Conflict-focused report
- `reports/evaluation_metrics_report.md` - Metrics and statistics

## 4. Run Tests

### Windows
```cmd
run_tests.bat
```

### Linux/macOS
```bash
bash run_tests.sh
```

## 5. Using Docker

```bash
# Build
docker build -t label-analyzer .

# Run
docker run -v $(pwd)/output:/app/output label-analyzer
```

## Expected Output

```
======================================
Starting Label Conflict Analysis Pipeline
======================================

[Step 1] Loading data from text_label.jsonl
✓ Loaded 100 samples

[Step 2] Analyzing samples for label conflicts
✓ Analysis complete

[Step 3] Extracting conflict samples
✓ Found 16 conflicting samples

[Step 4] Saving results
✓ Results saved to output

[Step 5] Generating analysis reports
✓ Reports generated

[Step 6] Analysis Statistics
  Total Samples: 100
  Conflicting Samples: 16
  Conflict Rate: 16.00%

======================================
Analysis Pipeline Completed Successfully!
======================================
```

## Sample Output Structure

```json
{
  "id": 21,
  "text": "The service was okay but could improve.",
  "labels": [
    {"annotator": "A1", "label": "Neutral"},
    {"annotator": "A2", "label": "Positive"}
  ],
  "is_conflict": true,
  "conflict_reason": "Mixed signal - text has positive elements but lacks strong positivity",
  "suggested_label": "Neutral",
  "confidence": 0.5,
  "analysis_details": {
    "explanation": "Slight majority - Text analysis suggests Positive...",
    "unique_labels": ["Neutral", "Positive"],
    "label_distribution": {"Neutral": 1, "Positive": 1},
    "annotators_involved": ["A1", "A2"]
  }
}
```

## Key Metrics

After running analysis, check `reports/evaluation_metrics_report.md` for:
- **Total Samples**: Overall dataset size
- **Conflict Rate**: % of samples with disagreement
- **Average Confidence**: Confidence in suggested labels
- **Label Distribution**: Breakdown of suggested labels

## Common Issues

**Q: Virtual environment not found**
A: Run `setup.bat` (Windows) or `bash setup.sh` (Linux/macOS) first

**Q: Input file not found**
A: Ensure `text_label.jsonl` exists in the current directory

**Q: Python not found**
A: Install Python 3.8+ from python.org

For more detailed help, see `README_ANALYZER.md`
