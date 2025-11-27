# Test Report Template

- **Date:** {{DATE}}
- **Environment:** {{OS}} / Python {{PYTHON_VERSION}} / venv {{VENV_PATH}}
- **Git Commit:** {{GIT_COMMIT}}
- **Command:** {{TEST_COMMAND}}

## Summary
- **Total tests:** {{TOTAL}}
- **Passed:** {{PASSED}}
- **Failed:** {{FAILED}}
- **Skipped:** {{SKIPPED}}
- **Duration:** {{DURATION}}

## Detailed Results
| Test | Status | Duration | Notes |
|------|--------|----------|-------|
| {{TEST_NAME}} | {{STATUS}} | {{TIME}} | {{NOTES}} |

## Failures (if any)
```
{{FAILURE_TRACEBACKS}}
```

## Artifacts
- Logs: {{LOG_PATHS}}
- Reports: {{REPORT_PATHS}}

## Observations / Follow-ups
- {{NOTES}}
