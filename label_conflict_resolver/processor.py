import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from .heuristics import detect_conflict, infer_conflict_reason, suggest_label


def load_dataset(path: str) -> List[Dict[str, Any]]:
    """Load JSONL dataset from path."""
    items: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            items.append(json.loads(line))
    return items


def normalize_labels(raw_labels: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Ensure each label entry has annotator and label keys."""
    normalized = []
    for entry in raw_labels:
        annotator = entry.get("annotator") or entry.get("worker") or "unknown"
        label = entry.get("label") or entry.get("value") or entry.get("annotation") or "unknown"
        normalized.append({"annotator": annotator, "label": label})
    return normalized


def analyze_sample(sample: Dict[str, Any]) -> Dict[str, Any]:
    labels_raw = sample.get("labels", [])
    labels = normalize_labels(labels_raw)
    label_values = [l["label"] for l in labels]
    conflict = detect_conflict(label_values)
    conflict_reason = infer_conflict_reason(sample.get("text", ""), label_values) if conflict else None
    suggestion = suggest_label(sample.get("text", ""), label_values)

    return {
        "id": sample.get("id"),
        "text": sample.get("text", ""),
        "labels": labels,
        "is_conflict": conflict,
        "conflict_reason": conflict_reason,
        "suggested_label": suggestion,
    }


def analyze_dataset(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [analyze_sample(item) for item in items]


def write_output(results: List[Dict[str, Any]], output_path: str) -> None:
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for row in results:
            f.write(json.dumps(row, ensure_ascii=False))
            f.write("\n")


def extract_conflicts(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [r for r in results if r.get("is_conflict")]


def main(input_path: str, output_path: Optional[str] = None, conflicts_only: bool = False) -> str:
    """Run analysis pipeline.

    Returns the output path written.
    """
    items = load_dataset(input_path)
    results = analyze_dataset(items)
    if conflicts_only:
        results = extract_conflicts(results)
    if output_path is None:
        # Default output path next to input_path
        suffix = "_conflicts.jsonl" if conflicts_only else "_analysis.jsonl"
        output_path = str(Path(input_path).with_name(Path(input_path).stem + suffix))
    write_output(results, output_path)
    return output_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Detect and analyze label conflicts in multi-annotator datasets.")
    parser.add_argument("input", help="Path to input JSONL dataset")
    parser.add_argument("-o", "--output", help="Path to output JSONL file")
    parser.add_argument("--conflicts-only", action="store_true", help="Write only conflict samples")
    args = parser.parse_args()
    out = main(args.input, args.output, args.conflicts_only)
    print(f"Wrote analysis to {out}")
