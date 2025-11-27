# Test Report Template

Summary:
- Date: <DATE>
- Test run by: <NAME>
- Repo/branch: <REPO>/<BRANCH>

Metrics:
- Total records analyzed: <TOTAL>
- Conflict samples found: <CONFLICTS>
- Resolved labels distribution:
  - Positive: <N>
  - Negative: <N>
  - Neutral: <N>

Conflicts by cause:
| Cause | Count |
| --- | --- |
| Mixed sentiment | |
| Ambiguous text | |
| Unclear annotation policy | |
| Annotator error | |

Key Findings:
- Summarize trends: e.g., many Neutral vs Positive conflicts due to short messages; >X% false positives, etc.

Recommendations:
- Clarify policy
- Add extra examples to annotation guide
- Retrain annotators

Test artifacts:
- Path to outputs: `conflict_samples.jsonl`, `resolved_labels.jsonl`
- Command run: `pytest -q` or `python analyzer/analyze_conflicts.py` with args

Detailed sample list (optional):
- Attach CSV or JSONL of conflicts for reviewer
