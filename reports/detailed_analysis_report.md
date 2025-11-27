# Detailed Label Conflict Analysis Report

## Executive Summary

- **Total Samples**: 3
- **Conflicting Samples**: 1
- **Conflict Rate**: 33.33%

## Detailed Sample Analysis

### Sample 1 (ID: 1)

**Text**: Great product!

**Annotators' Labels**:
- A1: Positive
- A2: Positive

**Status**: ✓ Agreement

**Agreed Label**: Positive

--------------------------------------------------------------------------------

### Sample 2 (ID: 2)

**Text**: It was okay.

**Annotators' Labels**:
- A1: Neutral
- A2: Positive

**Status**: ⚠️ CONFLICT

**Conflict Reason**: Mixed signal - text has positive elements but lacks strong positivity

**Suggested Label**: Neutral
**Confidence**: 50.0%

**Analysis Details**:
- Explanation: Majority vote (1/2) - Slight majority - Neutral tone detected in text
- Label Distribution: {'Neutral': 1, 'Positive': 1}

--------------------------------------------------------------------------------

### Sample 3 (ID: 3)

**Text**: Terrible

**Annotators' Labels**:
- A1: Negative
- A2: Negative

**Status**: ✓ Agreement

**Agreed Label**: Negative

--------------------------------------------------------------------------------

