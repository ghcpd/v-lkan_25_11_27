import json
from pathlib import Path
from analyzer.process_all import process_directory


def test_process_all_outputs(tmp_path):
    # Create two jsonl files
    f1 = tmp_path / 'a.jsonl'
    f1.write_text(json.dumps({'id': 1, 'text': 'Good', 'labels':[{'annotator':'A1','label':'Positive'}]}) + '\n')

    f2 = tmp_path / 'b.jsonl'
    f2.write_text(json.dumps({'id': 2, 'text': 'Bad', 'labels':[{'annotator':'A1','label':'Negative'},{'annotator':'A2','label':'Neutral'}]}) + '\n')

    # Process directory
    process_directory(str(tmp_path), pattern='*.jsonl')

    # Check outputs
    assert (tmp_path / 'conflicts_a.jsonl').exists()
    assert (tmp_path / 'resolved_a.jsonl').exists()
    assert (tmp_path / 'conflicts_b.jsonl').exists()
    assert (tmp_path / 'resolved_b.jsonl').exists()

    # Check count in resolved files
    r1 = (tmp_path / 'resolved_a.jsonl').read_text()
    assert 'suggested_label' in r1

    r2 = (tmp_path / 'resolved_b.jsonl').read_text()
    assert 'suggested_label' in r2
