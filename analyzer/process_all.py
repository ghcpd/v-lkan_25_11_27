"""
Process all *.jsonl files in a directory and generate outputs.
"""
from pathlib import Path
from analyzer.analyze_conflicts import analyze_file


def process_directory(input_dir='.', pattern='*.jsonl'):
    p = Path(input_dir)
    for f in sorted(p.glob(pattern)):
        if f.name.startswith('conflict') or f.name.startswith('resolved'):
            continue
        out_conflict = p / f'conflicts_{f.stem}.jsonl'
        out_resolved = p / f'resolved_{f.stem}.jsonl'
        analyze_file(str(f), str(out_conflict), str(out_resolved))


if __name__ == '__main__':
    process_directory()
