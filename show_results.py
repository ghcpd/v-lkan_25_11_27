import json

print("\n" + "="*80)
print("DETAILED CONFLICT ANALYSIS RESULTS")
print("="*80 + "\n")

with open('conflicts_only.jsonl', 'r') as f:
    conflicts = [json.loads(line) for line in f]

print(f"Total Conflicts Found: {len(conflicts)}\n")

for i, sample in enumerate(conflicts, 1):
    print(f"\n{'─'*80}")
    print(f"[Conflict #{i}] Sample ID: {sample['id']}")
    print(f"{'─'*80}")
    print(f"Text: {sample['text']}")
    print(f"\nAnnotations:")
    for ann in sample['labels']:
        print(f"  • {ann['annotator']}: {ann['label']}")
    print(f"\nConflict Reasons:")
    for reason in sample['conflict_reason'].split(' | '):
        print(f"  ➤ {reason}")
    print(f"\nResolution:")
    print(f"  Suggested Label: {sample['suggested_label']}")
    print(f"  Confidence Score: {sample['confidence']:.3f}")
    print(f"  Reasoning: {sample['reasoning']}")

print(f"\n{'='*80}")
print("SUMMARY STATISTICS")
print(f"{'='*80}")
avg_confidence = sum(s['confidence'] for s in conflicts) / len(conflicts)
print(f"Average Confidence Score: {avg_confidence:.3f}")
print(f"Total Conflicted Samples: {len(conflicts)}/100 (10%)")
