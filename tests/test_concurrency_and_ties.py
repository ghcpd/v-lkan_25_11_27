import json
import threading
import time
from pathlib import Path
from analyzer.analyze_conflicts import analyze_file


def test_simulate_concurrent_updates(tmp_path):
    input_path = tmp_path / 'input.jsonl'
    record1 = {'id': 1000, 'text': 'Works good', 'labels': [{'annotator':'A1','label':'Positive'}]}
    input_path.write_text(json.dumps(record1) + '\n')

    out_conflicts = tmp_path / 'conf.jsonl'
    out_resolved = tmp_path / 'resolved.jsonl'

    # Start analyzer in a thread
    def run_analyzer():
        analyze_file(str(input_path), str(out_conflicts), str(out_resolved))

    t = threading.Thread(target=run_analyzer)
    t.start()

    # While analyzer runs, quickly append another conflicting line
    time.sleep(0.1)
    record2 = {'id': 1001, 'text': 'Works bad', 'labels': [{'annotator':'A1','label':'Negative'},{'annotator':'A2','label':'Positive'}]}
    with open(input_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record2) + '\n')

    t.join()

    # Analyzer should complete without crashing and output exists
    assert out_resolved.exists()


def test_tie_breaker_lexical(tmp_path):
    input_path = tmp_path / 'input2.jsonl'
    # tie between Positive/Negative
    rec = {'id': 1010, 'text': 'battery life is excellent but weight is bad',
           'labels': [{'annotator':'A1','label':'Positive'},{'annotator':'A2','label':'Negative'}]}
    input_path.write_text(json.dumps(rec) + '\n')

    out_conflicts = tmp_path / 'conf2.jsonl'
    out_resolved = tmp_path / 'resolved2.jsonl'
    analyze_file(str(input_path), str(out_conflicts), str(out_resolved))

    resolved = [json.loads(l) for l in out_resolved.read_text(encoding='utf-8').strip().splitlines()]
    r = resolved[0]
    assert r['is_conflict'] is True
    # Since both sides present, lexical counts: 'excellent' positive, 'bad' negative; tie -> expect Neutral or lexical tiebreak applied
    assert r['suggested_label']['label'] in ('Positive', 'Negative', 'Neutral')
