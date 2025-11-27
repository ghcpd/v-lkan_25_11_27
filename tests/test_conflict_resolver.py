import json
from pathlib import Path

import pytest

from label_conflict_resolver import processor
from label_conflict_resolver.heuristics import detect_conflict, suggest_label, infer_conflict_reason


def test_detect_conflict_basic():
    assert detect_conflict(["Positive", "Negative"]) is True
    assert detect_conflict(["Positive", "Positive"]) is False


def test_suggest_label_majority_high_dominance():
    text = "Great product!"
    labels = ["Positive", "Positive", "Neutral"]
    suggestion = suggest_label(text, labels)
    assert suggestion["label"] == "Positive"
    assert suggestion["majority_label"] == "Positive"
    assert suggestion["confidence"] >= 0.6


def test_suggest_label_mixed_due_to_contrast():
    text = "The UI is clean but performance is terrible."
    labels = ["Positive", "Negative"]
    suggestion = suggest_label(text, labels)
    assert suggestion["label"] == "Mixed"
    assert "contrast" in suggestion["reason"].lower()


def test_infer_conflict_reason_short_text():
    reason = infer_conflict_reason("Okay", ["Positive", "Negative"])
    assert "short" in reason.lower()


def test_analyze_sample_structure_and_conflict_reason():
    sample = {
        "id": 47,
        "text": "The UI is clean but performance is terrible.",
        "labels": [
            {"annotator": "A1", "label": "Negative"},
            {"annotator": "A2", "label": "Positive"},
        ],
    }
    result = processor.analyze_sample(sample)
    assert result["is_conflict"] is True
    assert result["conflict_reason"]
    assert result["suggested_label"]["label"] == "Mixed"


def test_analyze_dataset_and_write_output(tmp_path: Path):
    dataset = [
        {"id": 1, "text": "Great", "labels": [{"annotator": "A1", "label": "Positive"}]},
        {
            "id": 2,
            "text": "Okay but slow",
            "labels": [
                {"annotator": "A1", "label": "Neutral"},
                {"annotator": "A2", "label": "Negative"},
            ],
        },
    ]
    out_path = tmp_path / "out.jsonl"
    results = processor.analyze_dataset(dataset)
    processor.write_output(results, out_path)

    # Reload and verify persistence
    reloaded = []
    with open(out_path, "r", encoding="utf-8") as f:
        for line in f:
            reloaded.append(json.loads(line))
    assert len(reloaded) == 2
    conflicts = [r for r in reloaded if r["is_conflict"]]
    assert len(conflicts) == 1
    assert conflicts[0]["id"] == 2


def test_main_conflicts_only(tmp_path: Path):
    dataset = [
        {"id": 1, "text": "Great", "labels": [{"annotator": "A1", "label": "Positive"}]},
        {
            "id": 2,
            "text": "Bad",
            "labels": [
                {"annotator": "A1", "label": "Negative"},
                {"annotator": "A2", "label": "Positive"},
            ],
        },
    ]
    in_path = tmp_path / "in.jsonl"
    with open(in_path, "w", encoding="utf-8") as f:
        for row in dataset:
            f.write(json.dumps(row))
            f.write("\n")
    out_path = tmp_path / "only_conflicts.jsonl"
    processor.main(str(in_path), str(out_path), conflicts_only=True)

    # Verify only conflict sample is written
    with open(out_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    assert len(lines) == 1
    obj = json.loads(lines[0])
    assert obj["id"] == 2
    assert obj["is_conflict"] is True


def test_deterministic_output_for_collaboration(tmp_path: Path):
    """Simulate repeated runs to ensure deterministic outputs for collaborative settings."""
    dataset = [
        {
            "id": 1,
            "text": "The service was okay but could improve.",
            "labels": [
                {"annotator": "A1", "label": "Neutral"},
                {"annotator": "A2", "label": "Positive"},
            ],
        },
    ]
    in_path = tmp_path / "in.jsonl"
    for _ in range(2):
        with open(in_path, "w", encoding="utf-8") as f:
            for row in dataset:
                f.write(json.dumps(row))
                f.write("\n")
        out_path = tmp_path / "out.jsonl"
        processor.main(str(in_path), str(out_path), conflicts_only=False)
        with open(out_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) == 1
        obj = json.loads(lines[0])
        assert obj["suggested_label"]["label"]  # always present
        # run again and compare
        first = obj
    # second run
    processor.main(str(in_path), str(out_path), conflicts_only=False)
    with open(out_path, "r", encoding="utf-8") as f:
        lines2 = f.readlines()
    assert lines2[0] == lines[0]
