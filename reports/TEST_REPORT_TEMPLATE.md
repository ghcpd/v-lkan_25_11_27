# Test Report Template

## Test Execution Summary

**Date**: [Date]
**Time**: [Time]
**Environment**: [OS/Platform]
**Python Version**: [Version]

## Test Statistics

| Metric | Value |
|--------|-------|
| Total Tests | [#] |
| Passed | [#] |
| Failed | [#] |
| Skipped | [#] |
| Success Rate | [%] |
| Duration | [time]s |

## Test Results by Category

### Unit Tests: Conflict Detection
- [ ] test_detect_agreement
- [ ] test_detect_conflict_two_labels
- [ ] test_detect_conflict_three_labels
- [ ] test_single_annotator

**Status**: ✅ / ❌ / ⚠️
**Details**: [Pass/Fail details]

### Unit Tests: Conflict Analysis
- [ ] test_positive_negative_conflict_reason
- [ ] test_positive_neutral_conflict_reason
- [ ] test_no_conflict_reason

**Status**: ✅ / ❌ / ⚠️

### Unit Tests: Label Suggestion
- [ ] test_unanimous_agreement
- [ ] test_majority_vote_two_vs_one
- [ ] test_majority_vote_all_equal
- [ ] test_text_based_reasoning

**Status**: ✅ / ❌ / ⚠️

### Unit Tests: Sample Analysis
- [ ] test_analyze_agreement_sample
- [ ] test_analyze_conflict_sample
- [ ] test_sample_to_dict

**Status**: ✅ / ❌ / ⚠️

### Integration Tests: Dataset Analysis
- [ ] test_analyze_dataset
- [ ] test_get_conflict_samples

**Status**: ✅ / ❌ / ⚠️

### Integration Tests: Data Handler
- [ ] test_save_and_load_jsonl
- [ ] test_save_and_load_json

**Status**: ✅ / ❌ / ⚠️

### Integration Tests: Pipeline
- [ ] test_pipeline_execution
- [ ] test_pipeline_output_files

**Status**: ✅ / ❌ / ⚠️

### Real-world Scenarios
- [ ] test_ambiguous_text_with_mixed_sentiment
- [ ] test_unclear_annotation_policy
- [ ] test_multi_aspect_evaluation

**Status**: ✅ / ❌ / ⚠️

## Code Coverage

| Component | Coverage |
|-----------|----------|
| conflict_analyzer.py | [%] |
| data_handler.py | [%] |
| pipeline.py | [%] |
| report_generator.py | [%] |
| **Total** | **[%]** |

Target: 85%+

## Performance Tests

| Operation | Time | Status |
|-----------|------|--------|
| Load 100 samples | [ms] | ✅ |
| Analyze 100 samples | [ms] | ✅ |
| Generate reports | [ms] | ✅ |
| Save results | [ms] | ✅ |

Target: <5s for 100 samples

## Known Issues

- [ ] Issue 1: [Description]
  - Severity: [Low/Medium/High]
  - Status: [Open/Resolved/In Progress]
  - Notes: [Details]

- [ ] Issue 2: [Description]
  - Severity: [Low/Medium/High]
  - Status: [Open/Resolved/In Progress]
  - Notes: [Details]

## Resolved Issues

- ✅ [Resolved issue 1]
- ✅ [Resolved issue 2]

## Recommendations

1. [Recommendation 1]
2. [Recommendation 2]
3. [Recommendation 3]

## Sign-off

| Role | Name | Date | Status |
|------|------|------|--------|
| Test Lead | [Name] | [Date] | [✅/❌] |
| QA Manager | [Name] | [Date] | [✅/❌] |
| Release Manager | [Name] | [Date] | [✅/❌] |

---

**Status**: [PASS/FAIL/CONDITIONAL]
**Approved for Release**: [YES/NO/CONDITIONAL]
