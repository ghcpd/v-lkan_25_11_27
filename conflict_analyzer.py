"""
Convenience entry script in workspace root so the user can run analysis directly from the folder where `text_label.jsonl` resides.
Usage (cmd.exe):
    python conflict_analyzer.py --input text_label.jsonl
"""
import argparse
from analyzer.analyze_conflicts import analyze_file


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', default='text_label.jsonl')
    parser.add_argument('--out_conflicts', '-oc', default='conflict_samples.jsonl')
    parser.add_argument('--out_resolved', '-or', default='resolved_labels.jsonl')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    analyze_file(args.input, args.out_conflicts, args.out_resolved)
