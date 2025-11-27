import json
from analyzer.analyze_conflicts import analyze_file
from pathlib import Path


def test_analyze_and_detect_conflicts(tmp_path):
    wkdir = Path(__file__).resolve().parents[1]
    input_file = wkdir / 'text_label.jsonl'

    out_conflicts = tmp_path / 'conflicts.jsonl'
    out_resolved = tmp_path / 'resolved.jsonl'
    analyze_file(str(input_file), str(out_conflicts), str(out_resolved))

    # Ensure files created
    assert out_conflicts.exists()
    assert out_resolved.exists()

    # Load conflicts
    conflicts = [json.loads(l) for l in out_conflicts.read_text(encoding='utf-8').strip().splitlines()]
    resolved = [json.loads(l) for l in out_resolved.read_text(encoding='utf-8').strip().splitlines()]

    # There should be conflicts for records with mixed labels: check a few by ID
    ids_with_conflicts = set([c['id'] for c in conflicts])
    assert 21 in ids_with_conflicts  # Neutral vs Positive
    assert 47 in ids_with_conflicts  # Positive vs Negative
    # id 2 was Negative vs Negative -> no conflict
    assert 2 not in ids_with_conflicts

    # Check suggested_label structure
    s = next(r for r in resolved if r['id'] == 21)
    assert 'suggested_label' in s
    assert 'label' in s['suggested_label']
    assert 'confidence' in s['suggested_label']
    assert 0 <= s['suggested_label']['confidence'] <= 1

    # Minimal sanity: suggested label is among allowed labels
    allowed = {'Positive', 'Negative', 'Neutral'}
    for r in resolved:
        assert r['suggested_label']['label'] in allowed


# Additional test: specific heuristics

def test_contrast_word_low_confidence(tmp_path):
    # Build a small dataset that includes contrast
    tmp_input = tmp_path / 'tmp_input.jsonl'
    tmp_input.write_text(json.dumps({
        'id': 900,
        'text': 'Great battery but the screen is terrible',
        'labels': [{'annotator': 'A1', 'label': 'Positive'}, {'annotator': 'A2', 'label': 'Negative'}]
    }) + '\n')

    out_conflicts = tmp_path / 'conflicts2.jsonl'
    out_resolved = tmp_path / 'resolved2.jsonl'

    analyze_file(str(tmp_input), str(out_conflicts), str(out_resolved))
    resolved = [json.loads(l) for l in out_resolved.read_text(encoding='utf-8').strip().splitlines()]
    r = resolved[0]
    assert r['is_conflict'] is True
    assert r['conflict_reason'] is not None
    assert r['suggested_label']['confidence'] <= 0.6, 'Confidence should be lowered due to contrast words'

