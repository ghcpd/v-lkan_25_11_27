"""
conflict_resolver.py

Detect and resolve conflicts in multi-annotator datasets.

CLI usage:
python -m src.conflict_resolver --input text_label.jsonl --output resolved.jsonl --conflicts conflicts.jsonl
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
import math
import re
from typing import List, Dict, Any, Tuple

POSITIVE_WORDS = set([
    "excellent", "enjoyed", "loved", "amazing", "great", "fantastic", "impressive",
    "reliable", "helpful", "positive", "good", "perfect", "satisfied", "stable",
    "best", "easy", "comfortable", "love", "liked", "good", "clean"
])
NEGATIVE_WORDS = set([
    "terrible", "worst", "rude", "disappointed", "crashes", "slow", "noisy",
    "broke", "broken", "bad", "poor", "cheap", "overpriced", "broken", "distorted",
    "overheats", "shrink", "unusable", "unreliable", "worst" 
])

POSITIVE_NEGATIVE_PATTERN = re.compile(r"\b(but|however|though|although|yet)\b", re.I)
HEDGING_WORDS = re.compile(r"\b(guess|maybe|might|could|sometimes|might be|I guess)\b", re.I)

LABELS_ALLOWED = ["Positive", "Negative", "Neutral"]


def load_jsonl(path: str):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def write_jsonl(path: str, items: List[dict]):
    with open(path, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")


def label_counts(labels: List[dict]) -> Counter:
    c = Counter()
    for l in labels:
        c[l["label"]] += 1
    return c


def detect_conflict(labels: List[dict]) -> bool:
    # conflict if more than one distinct label exists among annotators
    unique_labels = set(l["label"] for l in labels)
    return len(unique_labels) > 1


def text_sentiment_score(text: str) -> int:
    # small lexicon-based score
    text_lower = text.lower()
    score = 0
    for w in POSITIVE_WORDS:
        if w in text_lower:
            score += 1
    for w in NEGATIVE_WORDS:
        if w in text_lower:
            score -= 1
    return score


def analyze_conflict_reason(text: str, labels: List[dict]) -> str | None:
    # heuristics to explain disagreement
    lc = label_counts(labels)
    unique_labels = list(lc.keys())

    text_lower = text.lower()
    if len(unique_labels) <= 1:
        return None

    # Mixed aspect: presence of "but" or multiple clauses with opposite sentiment
    if POSITIVE_NEGATIVE_PATTERN.search(text_lower) or (text_sentiment_score(text) == 0 and any(w in text_lower for w in ["but", "however"])):
        return "Mixed sentiment across aspects (positive and negative statements in one text)."

    # Hedging / ambiguous phrasing
    if HEDGING_WORDS.search(text_lower) or text_lower.strip().startswith("i guess"):
        return "Ambiguous or hedged expression; annotators interpreted sentiment differently."

    # Multi-aspect or multi-intent (e.g., aspects are positive/negative)
    pos = any(w in text_lower for w in POSITIVE_WORDS)
    neg = any(w in text_lower for w in NEGATIVE_WORDS)
    if pos and neg:
        return "Mixed sentiment (both positive and negative indicators present)."

    # Minor difference or label confusion: e.g., Neutral vs Positive or Negative vs Neutral
    if set(unique_labels) <= set(["Neutral", "Positive"]) or set(unique_labels) <= set(["Neutral","Negative"]):
        return "Annotators have different thresholds for Neutral vs Positive/Negative (boundary disagreement)."

    # One annotator is outlier - suggest possible annotator mistake
    counts = lc.most_common()
    if counts[0][1] >= 2 and counts[-1][1] == 1:
        return "One annotator disagrees while others agree; could be annotator error or different interpretation."

    # Default
    return "Different subjective interpretations or unclear annotation policy."


def resolve_label(labels: List[dict], text: str) -> Tuple[str, dict]:
    # returns (chosen_label, reasoning dict)
    total = len(labels)
    counts = label_counts(labels)
    most_common_label, most_common_count = counts.most_common(1)[0]

    # Basic majority
    if most_common_count > total / 2:
        chosen = most_common_label
        confidence = most_common_count / total
        explanation = f"Majority vote: {most_common_label} with {most_common_count}/{total} annotators."
        # Add sentiment support
        sentiment_score = text_sentiment_score(text)
        if (sentiment_score > 0 and chosen != 'Positive') or (sentiment_score < 0 and chosen != 'Negative'):
            explanation += f" Note: lexicon sentiment score={sentiment_score} suggests {('Positive' if sentiment_score>0 else 'Negative' if sentiment_score<0 else 'Neutral')}."
        return chosen, {"majority_label": most_common_label, "majority_count": most_common_count, "confidence": round(confidence, 3), "explanation": explanation}

    # No strict majority: use lexicon scoring to break tie
    sentiment_score = text_sentiment_score(text)
    if sentiment_score > 0:
        chosen = 'Positive'
        reason = f"No clear majority; sentiment lexicon score {sentiment_score} indicates Positive; majority counts: {dict(counts)}."
        confidence = (max(counts.values()) / total) * 0.75 + min(1.0, abs(sentiment_score)/3) * 0.25
    elif sentiment_score < 0:
        chosen = 'Negative'
        reason = f"No clear majority; sentiment lexicon score {sentiment_score} indicates Negative; majority counts: {dict(counts)}."
        confidence = (max(counts.values()) / total) * 0.75 + min(1.0, abs(sentiment_score)/3) * 0.25
    else:
        # sentiment neutral: pick label with highest count, break tie by preferring Neutral
        counts_most = counts.most_common()
        candidate = [c for c in counts_most if c[1] == counts_most[0][1]]
        # If tie includes Neutral, prefer Neutral
        labels_in_tie = [c[0] for c in candidate]
        if 'Neutral' in labels_in_tie:
            chosen = 'Neutral'
        else:
            chosen = counts_most[0][0]
        reason = f"No clear majority; choose {chosen} based on counts: {dict(counts)} and neutral sentiment."
        confidence = (max(counts.values()) / total)

    # Adjust confidence into [0.01, 0.99]
    confidence = max(0.01, min(0.99, round(float(confidence), 3)))

    return chosen, {"majority_label": most_common_label if most_common_count > 0 else None, "majority_count": most_common_count, "confidence": confidence, "explanation": reason}


def process_dataset(input_path: str) -> List[dict]:
    processed = []
    for sample in load_jsonl(input_path):
        labels = sample.get("labels", [])
        is_conflict = detect_conflict(labels)
        conflict_reason = analyze_conflict_reason(sample.get("text",""), labels) if is_conflict else None
        suggested_label, reasoning = resolve_label(labels, sample.get("text",""))
        out = {
            "id": sample.get("id"),
            "text": sample.get("text"),
            "labels": labels,
            "is_conflict": is_conflict,
            "conflict_reason": conflict_reason,
            "suggested_label": suggested_label,
            "suggested_label_reason": reasoning
        }
        processed.append(out)
    return processed


def compute_annotator_agreement(processed: List[dict]) -> Dict[str, Dict[str, Any]]:
    """
    Compute agreement (vs majority) per annotator.
    Returns a dict annotator -> {agreements, total, rate}
    """
    stats = {}
    for item in processed:
        maj_label = item.get('suggested_label')
        for lab in item.get('labels', []):
            annot = lab['annotator']
            if annot not in stats:
                stats[annot] = {'agreements': 0, 'total': 0}
            stats[annot]['total'] += 1
            if lab['label'] == maj_label:
                stats[annot]['agreements'] += 1
    # set rate
    for a in stats:
        t = stats[a]['total']
        stats[a]['rate'] = round(stats[a]['agreements'] / t if t else 0.0, 3)
    return stats


def main():
    parser = argparse.ArgumentParser(description="Resolve conflicts in multi-annotator label dataset")
    parser.add_argument("--input", required=True, help="Input JSONL file with id, text, labels fields")
    parser.add_argument("--output", required=True, help="Output JSONL file with resolved labels and analysis")
    parser.add_argument("--conflicts", required=False, help="Output JSONL file containing only conflict samples")
    args = parser.parse_args()

    processed = process_dataset(args.input)
    write_jsonl(args.output, processed)

    if args.conflicts:
        conflicts = [p for p in processed if p["is_conflict"]]
        write_jsonl(args.conflicts, conflicts)

    # compute annotator stats for analysis
    try:
        from pprint import pprint
        stats = compute_annotator_agreement(processed)
        print(f"Processed {len(processed)} samples, found {sum(1 for p in processed if p['is_conflict'])} conflict(s).")
        print("Annotator agreement (vs suggested label):")
        pprint(stats)
    except Exception:
        print(f"Processed {len(processed)} samples, found {sum(1 for p in processed if p['is_conflict'])} conflict(s).")


if __name__ == '__main__':
    main()
