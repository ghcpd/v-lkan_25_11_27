"""
Multi-Annotator Label Conflict Analyzer
Detects, analyzes, and resolves labeling inconsistencies in datasets.
"""

import json
from typing import List, Dict, Any, Tuple
from collections import Counter
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class LabelRecord:
    """Represents a single label from an annotator"""
    annotator: str
    label: str


@dataclass
class SampleAnalysis:
    """Analysis result for a sample"""
    id: int
    text: str
    labels: List[Dict[str, str]]
    is_conflict: bool
    conflict_reason: str = None
    suggested_label: str = None
    confidence: float = None
    analysis_details: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


class ConflictAnalyzer:
    """Analyzes and resolves label conflicts in multi-annotator datasets"""

    # Label sentiment scores for intelligent reasoning
    LABEL_PROPERTIES = {
        "Positive": {"sentiment": 1.0, "strength": "high"},
        "Negative": {"sentiment": -1.0, "strength": "high"},
        "Neutral": {"sentiment": 0.0, "strength": "low"},
    }

    # Conflict patterns and their likely causes
    CONFLICT_PATTERNS = {
        ("Positive", "Negative"): "Strong sentiment disagreement - text may contain mixed opinions",
        ("Positive", "Neutral"): "Mixed signal - text has positive elements but lacks strong positivity",
        ("Negative", "Neutral"): "Severity interpretation - text has negative aspects but not overwhelmingly",
        ("Positive", "Neutral", "Negative"): "High ambiguity - text has multiple conflicting signals",
    }

    def __init__(self, verbose: bool = False):
        """Initialize the analyzer"""
        self.verbose = verbose
        self.statistics = {
            "total_samples": 0,
            "conflict_samples": 0,
            "conflict_rate": 0.0,
            "annotator_pairs": {},
        }

    def detect_conflict(self, labels: List[Dict[str, str]]) -> bool:
        """
        Detect if there's a conflict in labels
        A conflict exists when annotators assign different labels to the same text
        """
        unique_labels = set(label["label"] for label in labels)
        return len(unique_labels) > 1

    def analyze_conflict_reason(
        self,
        text: str,
        labels: List[Dict[str, str]],
        unique_labels: set,
    ) -> str:
        """Analyze and explain the reason for conflict"""
        if len(unique_labels) == 1:
            return None

        # Get sorted labels for consistent pattern matching
        label_tuple = tuple(sorted(unique_labels))

        # Check predefined conflict patterns
        for pattern, reason in self.CONFLICT_PATTERNS.items():
            if set(label_tuple) == set(pattern):
                return reason

        # Generic fallback
        return f"Disagreement between {', '.join(sorted(unique_labels))} labels"

    def suggest_final_label(
        self,
        labels: List[Dict[str, str]],
        text: str,
    ) -> Tuple[str, float, str]:
        """
        Suggest a final label based on intelligent reasoning
        Returns: (suggested_label, confidence, explanation)
        """
        label_counts = Counter(label["label"] for label in labels)
        unique_labels = list(label_counts.keys())

        # Case 1: No conflict - use unanimous label
        if len(unique_labels) == 1:
            label = unique_labels[0]
            return label, 1.0, "Unanimous agreement among all annotators"

        # Case 2: Majority vote with reasoning
        majority_label, majority_count = label_counts.most_common(1)[0]
        total_annotators = len(labels)
        confidence = majority_count / total_annotators

        # Analyze text characteristics for stronger reasoning
        text_lower = text.lower()

        # Strong positive indicators
        positive_words = [
            "excellent", "amazing", "perfect", "love", "great", "fantastic",
            "outstanding", "wonderful", "awesome", "highly", "best", "impressed",
            "smooth", "responsive", "reliable", "durable", "comfortable",
            "lightweight", "powerful", "efficient"
        ]

        # Strong negative indicators
        negative_words = [
            "terrible", "horrible", "worst", "broken", "damaged", "rude", "slow",
            "disappointing", "poor", "cheap", "defective", "stopped", "failed",
            "unstable", "irritation", "distorted", "painful", "shrunk", "overpriced"
        ]

        # Neutral/mixed indicators
        neutral_words = ["okay", "fine", "average", "decent", "normal", "reasonable"]

        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        neutral_count = sum(1 for word in neutral_words if text_lower.count(word))

        explanation = f"Majority vote ({majority_count}/{total_annotators})"

        # Text-based reasoning to strengthen the suggestion
        if confidence == 1.0:
            explanation += " - Unanimous agreement"
        elif confidence >= 2/3:
            explanation += " - Strong majority consensus"
        else:
            explanation += " - Slight majority"

        # Additional reasoning based on text analysis
        if positive_count > negative_count + neutral_count and majority_label != "Positive":
            suggestion = "Positive"
            confidence = 0.7
            explanation = (
                f"Text analysis suggests Positive (detected {positive_count} positive indicators), "
                f"but {majority_label} had {majority_count}/{total_annotators} votes"
            )
        elif negative_count > positive_count + neutral_count and majority_label != "Negative":
            suggestion = "Negative"
            confidence = 0.7
            explanation = (
                f"Text analysis suggests Negative (detected {negative_count} negative indicators), "
                f"but {majority_label} had {majority_count}/{total_annotators} votes"
            )
        else:
            suggestion = majority_label
            if positive_count == 0 and negative_count == 0:
                explanation += " - Neutral tone detected in text"

        return suggestion, confidence, explanation

    def analyze_sample(self, sample: Dict[str, Any]) -> SampleAnalysis:
        """Analyze a single sample for conflicts and suggest resolution"""
        labels = sample.get("labels", [])
        unique_labels = set(label["label"] for label in labels)
        is_conflict = self.detect_conflict(labels)

        conflict_reason = None
        suggested_label = None
        confidence = None
        analysis_details = {}

        if is_conflict:
            conflict_reason = self.analyze_conflict_reason(
                sample["text"], labels, unique_labels
            )
            suggested_label, confidence, explanation = self.suggest_final_label(
                labels, sample["text"]
            )
            analysis_details = {
                "explanation": explanation,
                "unique_labels": list(unique_labels),
                "label_distribution": dict(
                    Counter(label["label"] for label in labels)
                ),
                "annotators_involved": [label["annotator"] for label in labels],
            }
        else:
            suggested_label = unique_labels.pop()
            confidence = 1.0
            analysis_details = {
                "explanation": "No conflict - unanimous label",
                "unique_labels": list(unique_labels),
            }

        return SampleAnalysis(
            id=sample["id"],
            text=sample["text"],
            labels=labels,
            is_conflict=is_conflict,
            conflict_reason=conflict_reason,
            suggested_label=suggested_label,
            confidence=confidence,
            analysis_details=analysis_details,
        )

    def analyze_dataset(self, samples: List[Dict[str, Any]]) -> List[SampleAnalysis]:
        """Analyze entire dataset and return results"""
        results = []
        conflict_count = 0

        for sample in samples:
            analysis = self.analyze_sample(sample)
            results.append(analysis)
            if analysis.is_conflict:
                conflict_count += 1

        # Update statistics
        self.statistics["total_samples"] = len(samples)
        self.statistics["conflict_samples"] = conflict_count
        self.statistics["conflict_rate"] = (
            conflict_count / len(samples) * 100 if samples else 0
        )

        if self.verbose:
            logger.info(f"Analysis complete: {conflict_count}/{len(samples)} conflicts")

        return results

    def get_conflict_samples(
        self, results: List[SampleAnalysis]
    ) -> List[SampleAnalysis]:
        """Extract only samples with conflicts"""
        return [r for r in results if r.is_conflict]

    def get_statistics(self) -> Dict[str, Any]:
        """Get analysis statistics"""
        return self.statistics.copy()
