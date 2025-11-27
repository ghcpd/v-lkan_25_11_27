#!/usr/bin/env python3
"""CLI entrypoint for label conflict analysis."""
from label_conflict_resolver.processor import main
import argparse


def cli():
    parser = argparse.ArgumentParser(description="Detect, analyze, and resolve inconsistent labeling in multi-annotator datasets.")
    parser.add_argument("input", help="Path to input JSONL dataset (text_label.jsonl)")
    parser.add_argument("-o", "--output", help="Path to output JSONL file")
    parser.add_argument("--conflicts-only", action="store_true", help="Write only conflict samples")
    args = parser.parse_args()
    out = main(args.input, args.output, args.conflicts_only)
    print(f"Wrote analysis to {out}")


if __name__ == "__main__":
    cli()
