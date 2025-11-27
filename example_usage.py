"""
Example script showing how to use the Label Conflict Analyzer as a library
"""

from src.conflict_analyzer import ConflictAnalyzer
from src.data_handler import DataHandler
from src.pipeline import AnalysisPipeline
import json

# Example 1: Basic Analysis of Single Sample
print("=" * 80)
print("Example 1: Analyzing a Single Sample")
print("=" * 80)

analyzer = ConflictAnalyzer(verbose=True)

sample = {
    "id": 1,
    "text": "The service was okay but could improve.",
    "labels": [
        {"annotator": "A1", "label": "Neutral"},
        {"annotator": "A2", "label": "Positive"}
    ]
}

result = analyzer.analyze_sample(sample)
print(f"\nSample ID: {result.id}")
print(f"Text: {result.text}")
print(f"Is Conflict: {result.is_conflict}")
if result.is_conflict:
    print(f"Conflict Reason: {result.conflict_reason}")
    print(f"Suggested Label: {result.suggested_label}")
    print(f"Confidence: {result.confidence:.1%}")
    print(f"Analysis: {result.analysis_details['explanation']}")

# Example 2: Analyzing Multiple Samples
print("\n" + "=" * 80)
print("Example 2: Analyzing Multiple Samples")
print("=" * 80)

samples = [
    {
        "id": 1,
        "text": "Excellent product!",
        "labels": [
            {"annotator": "A1", "label": "Positive"},
            {"annotator": "A2", "label": "Positive"}
        ]
    },
    {
        "id": 2,
        "text": "It was okay.",
        "labels": [
            {"annotator": "A1", "label": "Neutral"},
            {"annotator": "A2", "label": "Positive"}
        ]
    },
    {
        "id": 3,
        "text": "Terrible experience",
        "labels": [
            {"annotator": "A1", "label": "Negative"},
            {"annotator": "A2", "label": "Negative"}
        ]
    }
]

results = analyzer.analyze_dataset(samples)
stats = analyzer.get_statistics()

print(f"\nAnalyzed {stats['total_samples']} samples")
print(f"Found {stats['conflict_samples']} conflicts")
print(f"Conflict rate: {stats['conflict_rate']:.1f}%")

print("\nDetailed Results:")
for result in results:
    status = "✓ AGREE" if not result.is_conflict else "⚠️ CONFLICT"
    print(f"  ID {result.id}: {status} → {result.suggested_label}")

# Example 3: Working with Data Files
print("\n" + "=" * 80)
print("Example 3: Loading and Saving Data")
print("=" * 80)

handler = DataHandler()

# Load JSONL file
print("Loading JSONL file...")
samples = handler.load_jsonl("text_label.jsonl")
print(f"Loaded {len(samples)} samples")

# Analyze
print("Analyzing samples...")
analyzer = ConflictAnalyzer()
results = analyzer.analyze_dataset(samples)

# Convert to dictionaries for saving
results_dicts = [r.to_dict() for r in results]

# Save results
print("Saving results...")
handler.save_jsonl(results_dicts, "example_output.jsonl")
print("Saved to example_output.jsonl")

# Example 4: Using the Full Pipeline
print("\n" + "=" * 80)
print("Example 4: Using the Complete Pipeline")
print("=" * 80)

pipeline = AnalysisPipeline(
    input_file="text_label.jsonl",
    output_dir="example_output",
    verbose=True
)

print("Running pipeline (check output/ directory)...")
# Uncomment to run: result = pipeline.run()

# Example 5: Filtering Results
print("\n" + "=" * 80)
print("Example 5: Working with Results")
print("=" * 80)

print(f"\nTotal results: {len(results)}")

# Get only conflicts
conflicts = [r for r in results if r.is_conflict]
print(f"Conflict samples: {len(conflicts)}")

# Group by confidence
high_conf = [r for r in results if r.confidence and r.confidence >= 0.8]
med_conf = [r for r in results if r.confidence and 0.5 <= r.confidence < 0.8]
low_conf = [r for r in results if r.confidence and r.confidence < 0.5]

print(f"High confidence (≥80%): {len(high_conf)}")
print(f"Medium confidence (50-80%): {len(med_conf)}")
print(f"Low confidence (<50%): {len(low_conf)}")

# Example 6: Custom Analysis Logic
print("\n" + "=" * 80)
print("Example 6: Custom Processing")
print("=" * 80)

# Get conflict samples with specific reasons
for result in conflicts[:3]:  # First 3 conflicts
    print(f"\nID {result.id}: {result.text[:50]}...")
    print(f"  Labels: {[l['label'] for l in result.labels]}")
    print(f"  Reason: {result.conflict_reason}")
    print(f"  Suggested: {result.suggested_label} ({result.confidence:.0%})")

print("\n" + "=" * 80)
print("Examples Complete!")
print("=" * 80)
