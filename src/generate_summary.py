import json
from pathlib import Path
from collections import Counter


def generate_summary(input_path):
    p = Path(input_path)
    counts = Counter()
    conflicts = []
    total = 0
    with open(p, 'r', encoding='utf-8') as f:
        for line in f:
            j = json.loads(line)
            total += 1
            counts[j['suggested_label']] += 1
            if j.get('is_conflict'):
                conflicts.append(j)
    summary = {
        'total_samples': total,
        'per_label': dict(counts),
        'conflicts_count': len(conflicts)
    }
    return summary


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', type=str, required=True)
    parser.add_argument('--output', '-o', type=str, required=False)
    args = parser.parse_args()
    s = generate_summary(args.input)
    print(json.dumps(s, indent=2))
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(s, f, indent=2)
