import re
from collections import Counter
from typing import List, Dict, Tuple, Optional

AMBIGUOUS_MARKERS = [
    r"\bmaybe\b",
    r"\bperhaps\b",
    r"\bnot sure\b",
    r"\bkind of\b",
    r"\bsort of\b",
    r"\bI guess\b",
]

CONTRAST_MARKERS = [
    r"\bbut\b",
    r"\bhowever\b",
    r"\balthough\b",
    r"\bthough\b",
    r"\bnevertheless\b",
    r"\byet\b",
]

MULTI_ASPECT_MARKERS = [
    ",",
    ";",
    r"\band\b",
]


def majority_label(labels: List[str]) -> Tuple[Optional[str], Counter]:
    """Return the majority label and counts."""
    counter = Counter(labels)
    if not counter:
        return None, counter
    # Choose label with max count; if tie, return None for majority (tie)
    most_common = counter.most_common()
    top_label, top_count = most_common[0]
    if len(most_common) > 1 and most_common[1][1] == top_count:
        return None, counter
    return top_label, counter


def detect_conflict(labels: List[str]) -> bool:
    return len(set(labels)) > 1


def infer_conflict_reason(text: str, labels: List[str]) -> str:
    """Heuristic explanation for disagreement."""
    if not labels or len(set(labels)) == 1:
        return ""

    text_lower = text.lower()
    # Mixed sentiment / contrastive
    if any(re.search(pattern, text_lower) for pattern in CONTRAST_MARKERS):
        return "Mixed/contrastive cues in text (e.g., 'but', 'however')."
    # Ambiguous phrasing
    if any(re.search(pattern, text_lower) for pattern in AMBIGUOUS_MARKERS):
        return "Ambiguous or uncertain language."
    # Short text
    if len(text.split()) < 5:
        return "Very short text; context may be insufficient."
    # Multi-aspect
    if any(re.search(pattern, text_lower) for pattern in MULTI_ASPECT_MARKERS):
        return "Multi-aspect statement; annotators may focus on different facets."
    # Presence of both positive and negative labels
    unique_labels = set(label.lower() for label in labels)
    if "positive" in unique_labels and "negative" in unique_labels:
        return "Conflicting sentiments (positive vs negative)."
    # Default
    return "Subjective interpretation or unclear annotation policy."


def suggest_label(text: str, labels: List[str]) -> Dict:
    """Suggest a final label with reasoning beyond simple majority.

    Strategy:
    - Compute majority and dominance ratio.
    - If dominance >= 0.6, pick majority with high confidence.
    - If tie or dominance < threshold:
        - If 'mixed' present, pick 'Mixed'.
        - If contrast markers present, suggest 'Mixed'.
        - If ambiguous markers present, suggest 'Ambiguous'.
        - Else combine top-2 labels as 'label1|label2' with low confidence.
    """
    maj_label, counts = majority_label(labels)
    total = sum(counts.values()) or 1
    dominant = counts[maj_label] / total if maj_label else 0
    text_lower = text.lower()

    reason_parts = []
    chosen_label = None
    confidence = 0.0

    if maj_label and dominant >= 0.6:
        chosen_label = maj_label
        confidence = dominant
        reason_parts.append(f"Majority label '{maj_label}' with dominance {dominant:.2f} (>=0.60).")
    else:
        # tie or weak majority
        if any(label.lower() == "mixed" for label in labels):
            chosen_label = "Mixed"
            confidence = max(counts.values()) / total
            reason_parts.append("'Mixed' label present among annotators; adopting it for disagreement.")
        elif any(re.search(pattern, text_lower) for pattern in CONTRAST_MARKERS):
            chosen_label = "Mixed"
            confidence = dominant if maj_label else max(counts.values()) / total
            reason_parts.append("Contrastive cues in text suggest mixed sentiment.")
        elif any(re.search(pattern, text_lower) for pattern in AMBIGUOUS_MARKERS):
            chosen_label = "Ambiguous"
            confidence = dominant if maj_label else max(counts.values()) / total
            reason_parts.append("Ambiguous language detected; marking as 'Ambiguous'.")
        else:
            # Combine top-2 labels
            top_two = counts.most_common(2)
            if top_two:
                labels_combo = "|".join(lbl for lbl, _ in top_two)
                chosen_label = labels_combo
                confidence = (top_two[0][1] / total)
                reason_parts.append("No strong majority; combining top labels as composite.")
            else:
                chosen_label = maj_label or "Unknown"
                confidence = dominant
                reason_parts.append("Fallback to majority/unknown.")

    # Add context about counts
    reason_parts.append(f"Label counts: {dict(counts)}")

    return {
        "label": chosen_label,
        "majority_label": maj_label,
        "confidence": round(confidence, 3),
        "reason": " ".join(reason_parts).strip(),
    }
