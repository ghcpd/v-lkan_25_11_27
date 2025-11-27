import os
import json
from src.label_processor import LabelProcessor


def test_conflict_detection_matches_manual_logic():
    # Use the file in workspace
    base = os.path.dirname(os.path.dirname(__file__))
    input_path = os.path.join(base, 'text_label.jsonl')
    assert os.path.exists(input_path), 'Input JSONL must be present for tests'
    proc = LabelProcessor(input_path)
    results = proc.process()

    # For each result recompute conflict logic and confirm
    for r in results:
        labels = r['labels']
        unique_labels = set([l['label'] for l in labels])
        expected_conflict = len(unique_labels) > 1
        assert r['is_conflict'] == expected_conflict


def test_some_expected_conflict_ids_present():
    base = os.path.dirname(os.path.dirname(__file__))
    input_path = os.path.join(base, 'text_label.jsonl')
    proc = LabelProcessor(input_path)
    results = proc.process()
    id_to_result = {r['id']: r for r in results}

    # Known conflict ids from quick manual scan
    expected_conflicts = [21, 29, 33, 47, 84, 72, 97, 41, 63, 56]
    for eid in expected_conflicts:
        assert eid in id_to_result, f"Expected ID {eid} to be present"
        assert id_to_result[eid]['is_conflict'], f"Expected ID {eid} to be conflict"


def test_suggested_label_confidence_and_reasoning():
    base = os.path.dirname(os.path.dirname(__file__))
    input_path = os.path.join(base, 'text_label.jsonl')
    proc = LabelProcessor(input_path)
    results = proc.process()
    for r in results:
        # suggested label must be provided
        assert 'suggested_label' in r
        assert r['suggestion_confidence'] is not None
        assert 0.0 <= r['suggestion_confidence'] <= 1.0
        if r['is_conflict']:
            assert r['conflict_reason'] is not None
            assert isinstance(r['suggestion_explanation'], str)


def test_output_file_written(tmp_path):
    base = os.path.dirname(os.path.dirname(__file__))
    input_path = os.path.join(base, 'text_label.jsonl')
    out_file = tmp_path / 'out.jsonl'
    proc = LabelProcessor(input_path)
    results = proc.process(str(out_file))
    assert out_file.exists()
    # check counts match
    with open(str(out_file), 'r', encoding='utf-8') as f:
        lines = [l for l in f if l.strip()]
    assert len(lines) == len(results)


def test_suggested_label_consistency():
    base = os.path.dirname(os.path.dirname(__file__))
    input_path = os.path.join(base, 'text_label.jsonl')
    proc = LabelProcessor(input_path)
    results = proc.process()
    for r in results:
        labels = [l['label'] for l in r['labels']]
        unique_labels = set(labels)
        suggested = r['suggested_label']
        # suggested label should be one of the known labels or a neutral fallback
        assert suggested in ['Positive', 'Neutral', 'Negative']
        if not r['is_conflict']:
            # When unanimous, the suggested label should equal the unanimous label
            assert suggested in unique_labels


def test_log_file_written(tmp_path):
    base = os.path.dirname(os.path.dirname(__file__))
    input_path = os.path.join(base, 'text_label.jsonl')
    out_file = tmp_path / 'out.jsonl'
    log_file = tmp_path / 'processor.log'
    proc = LabelProcessor(input_path)
    # configure logger
    import logging
    logger = logging.getLogger('test_proc_logger')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(str(log_file), encoding='utf-8')
    fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.handlers = []
    logger.addHandler(fh)
    proc.logger = logger
    results = proc.process(str(out_file))
    assert log_file.exists()
    assert log_file.stat().st_size > 0
    content = log_file.read_text(encoding='utf-8')
    assert 'Starting processing' in content
    assert 'Finished processing' in content
