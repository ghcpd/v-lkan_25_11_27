import json
import os
import tempfile
import sys

# ensure package import works in test runner
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.conflict_resolver import process_dataset, load_jsonl, write_jsonl


DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))


def test_conflict_detection_simple():
    # Use the fixture dataset in workspace root
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    input_path = os.path.join(root, "text_label.jsonl")
    processed = process_dataset(input_path)
    # sanity: 100 samples
    assert len(processed) >= 100

    # Check a known non-conflict sample: id 1 should be Positive and not conflict
    s1 = next((x for x in processed if x['id'] == 1), None)
    assert s1 is not None
    assert s1['is_conflict'] is False
    assert s1['suggested_label'] == 'Positive'

    # id 21 has a disagreement (Neutral vs Positive) - conflict
    s21 = next(x for x in processed if x['id'] == 21)
    assert s21['is_conflict'] is True
    # expected suggested label should be Positive or Neutral - our rule often picks Positive based on sentiment and counts
    assert s21['suggested_label'] in ('Neutral', 'Positive')
    # suggested reason should be present
    assert 'suggested_label_reason' in s21
    r = s21['suggested_label_reason']
    assert 'majority_label' in r and 'confidence' in r and 'explanation' in r

    # id 29 is Negative vs Neutral - conflict
    s29 = next(x for x in processed if x['id'] == 29)
    assert s29['is_conflict'] is True
    assert s29['suggested_label'] in ('Neutral', 'Negative')
    assert 'suggested_label_reason' in s29
    r29 = s29['suggested_label_reason']
    assert 'majority_label' in r29 and 'confidence' in r29 and 'explanation' in r29


def test_conflict_output_files(tmp_path):
    # verify output file writing
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    input_path = os.path.join(root, "text_label.jsonl")
    processed = process_dataset(input_path)

    out_file = tmp_path / "out.jsonl"
    write_jsonl(str(out_file), processed)
    assert out_file.exists()
    # read back
    read_back = list(load_jsonl(str(out_file)))
    assert len(read_back) == len(processed)

    # conflicts only
    conflicts = [p for p in processed if p['is_conflict']]
    conflict_file = tmp_path / "conflicts.jsonl"
    write_jsonl(str(conflict_file), conflicts)
    cback = list(load_jsonl(str(conflict_file)))
    assert len(cback) == len(conflicts)


def test_annotator_stats():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    input_path = os.path.join(root, "text_label.jsonl")
    processed = process_dataset(input_path)
    from src.conflict_resolver import compute_annotator_agreement
    stats = compute_annotator_agreement(processed)
    assert isinstance(stats, dict)
    # basic check: expected annotators A1, A2, A3 exist
    for a in ("A1", "A2", "A3"):
        assert a in stats
        assert 'agreements' in stats[a] and 'total' in stats[a] and 'rate' in stats[a]
