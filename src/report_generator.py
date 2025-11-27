"""
Report generator for analysis results
"""

from typing import List, Dict, Any
from pathlib import Path
from .conflict_analyzer import SampleAnalysis
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates comprehensive reports from analysis results"""

    @staticmethod
    def generate_detailed_report(
        results: List[SampleAnalysis],
        conflict_results: List[SampleAnalysis],
        output_path: str,
    ) -> None:
        """Generate a detailed analysis report"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Detailed Label Conflict Analysis Report\n\n")

            # Executive Summary
            f.write("## Executive Summary\n\n")
            f.write(
                f"- **Total Samples**: {len(results)}\n"
                f"- **Conflicting Samples**: {len(conflict_results)}\n"
                f"- **Conflict Rate**: {len(conflict_results)/len(results)*100:.2f}%\n\n"
            )

            # All Samples with Analysis
            f.write("## Detailed Sample Analysis\n\n")
            for i, result in enumerate(results, 1):
                f.write(f"### Sample {i} (ID: {result.id})\n\n")
                f.write(f"**Text**: {result.text}\n\n")

                # Labels
                f.write("**Annotators' Labels**:\n")
                for label in result.labels:
                    f.write(f"- {label['annotator']}: {label['label']}\n")
                f.write("\n")

                # Conflict status
                status = "⚠️ CONFLICT" if result.is_conflict else "✓ Agreement"
                f.write(f"**Status**: {status}\n\n")

                # Analysis
                if result.is_conflict:
                    f.write(f"**Conflict Reason**: {result.conflict_reason}\n\n")
                    f.write(f"**Suggested Label**: {result.suggested_label}\n")
                    f.write(f"**Confidence**: {result.confidence:.1%}\n\n")

                    if result.analysis_details:
                        f.write("**Analysis Details**:\n")
                        f.write(f"- Explanation: {result.analysis_details.get('explanation', 'N/A')}\n")
                        if 'label_distribution' in result.analysis_details:
                            dist = result.analysis_details['label_distribution']
                            f.write(f"- Label Distribution: {dict(dist)}\n")
                        f.write("\n")
                else:
                    f.write(f"**Agreed Label**: {result.suggested_label}\n\n")

                f.write("-" * 80 + "\n\n")

        logger.info(f"Detailed report saved to {output_path}")

    @staticmethod
    def generate_conflict_report(
        conflict_results: List[SampleAnalysis],
        output_path: str,
    ) -> None:
        """Generate a conflict-focused report"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Conflict Analysis Report\n\n")
            f.write(f"**Total Conflicts Found**: {len(conflict_results)}\n\n")

            # Group conflicts by type
            conflict_types = {}
            for result in conflict_results:
                if result.analysis_details and 'unique_labels' in result.analysis_details:
                    labels = tuple(sorted(result.analysis_details['unique_labels']))
                    if labels not in conflict_types:
                        conflict_types[labels] = []
                    conflict_types[labels].append(result)

            # Conflict Type Analysis
            f.write("## Conflict Types and Frequency\n\n")
            for labels, samples in sorted(conflict_types.items(), key=lambda x: len(x[1]), reverse=True):
                f.write(f"### Conflict: {' vs '.join(labels)} ({len(samples)} cases)\n\n")

                for sample in samples[:3]:  # Show first 3 examples
                    f.write(f"- **ID {sample.id}**: {sample.text[:80]}...\n")
                    f.write(f"  - Reason: {sample.conflict_reason}\n")
                    f.write(f"  - Suggested: {sample.suggested_label} (confidence: {sample.confidence:.1%})\n")

                if len(samples) > 3:
                    f.write(f"- ... and {len(samples) - 3} more cases\n")

                f.write("\n")

            # Resolution Summary
            f.write("## Resolution Summary\n\n")
            high_confidence = [r for r in conflict_results if r.confidence >= 0.8]
            medium_confidence = [r for r in conflict_results if 0.5 <= r.confidence < 0.8]
            low_confidence = [r for r in conflict_results if r.confidence < 0.5]

            f.write(f"- **High Confidence Resolutions** (≥80%): {len(high_confidence)}\n")
            f.write(f"- **Medium Confidence Resolutions** (50-80%): {len(medium_confidence)}\n")
            f.write(f"- **Low Confidence Resolutions** (<50%): {len(low_confidence)}\n\n")

        logger.info(f"Conflict report saved to {output_path}")

    @staticmethod
    def generate_metrics_report(
        results: List[SampleAnalysis],
        output_path: str,
    ) -> None:
        """Generate evaluation metrics report"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Calculate metrics
        total = len(results)
        conflicts = len([r for r in results if r.is_conflict])
        no_conflicts = total - conflicts

        avg_confidence = sum(r.confidence for r in results if r.confidence) / len(
            [r for r in results if r.confidence]
        )

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Evaluation Metrics Report\n\n")

            f.write("## Dataset Overview\n\n")
            f.write(f"| Metric | Value |\n")
            f.write(f"|--------|-------|\n")
            f.write(f"| Total Samples | {total} |\n")
            f.write(f"| Agreement Samples | {no_conflicts} ({no_conflicts/total*100:.1f}%) |\n")
            f.write(f"| Conflict Samples | {conflicts} ({conflicts/total*100:.1f}%) |\n\n")

            f.write("## Conflict Resolution Metrics\n\n")
            f.write(f"| Metric | Value |\n")
            f.write(f"|--------|-------|\n")
            f.write(f"| Average Confidence | {avg_confidence:.1%} |\n")

            # Confidence distribution
            high_conf = [r for r in results if r.confidence and r.confidence >= 0.8]
            medium_conf = [r for r in results if r.confidence and 0.5 <= r.confidence < 0.8]
            low_conf = [r for r in results if r.confidence and r.confidence < 0.5]

            f.write(f"| High Confidence (≥80%) | {len(high_conf)} ({len(high_conf)/total*100:.1f}%) |\n")
            f.write(f"| Medium Confidence (50-80%) | {len(medium_conf)} ({len(medium_conf)/total*100:.1f}%) |\n")
            f.write(f"| Low Confidence (<50%) | {len(low_conf)} ({len(low_conf)/total*100:.1f}%) |\n\n")

            # Label distribution in suggested labels
            f.write("## Suggested Label Distribution\n\n")
            from collections import Counter
            label_dist = Counter(r.suggested_label for r in results)
            f.write(f"| Label | Count | Percentage |\n")
            f.write(f"|-------|-------|------------|\n")
            for label, count in label_dist.most_common():
                f.write(f"| {label} | {count} | {count/total*100:.1f}% |\n")

            f.write("\n## Key Findings\n\n")
            f.write(
                f"1. The dataset has a {conflicts/total*100:.1f}% conflict rate, indicating "
                f"{'high' if conflicts/total > 0.2 else 'moderate' if conflicts/total > 0.1 else 'low'} "
                f"disagreement among annotators.\n"
            )
            f.write(
                f"2. Average confidence in suggested labels is {avg_confidence:.1%}, "
                f"suggesting {'strong' if avg_confidence > 0.8 else 'moderate' if avg_confidence > 0.6 else 'weak'} "
                f"resolution confidence.\n"
            )
            f.write(
                f"3. The suggested labels are distributed as: "
                f"{', '.join(f'{label} ({count})' for label, count in label_dist.most_common())}.\n"
            )

        logger.info(f"Metrics report saved to {output_path}")
