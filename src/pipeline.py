"""
Main pipeline for analyzing label conflicts
"""

import logging
import sys
from pathlib import Path
from typing import List, Dict, Any

from .conflict_analyzer import ConflictAnalyzer, SampleAnalysis
from .data_handler import DataHandler
from .report_generator import ReportGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('analysis.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class AnalysisPipeline:
    """Main pipeline orchestrating the analysis process"""

    def __init__(self, input_file: str, output_dir: str = "output", verbose: bool = True):
        """Initialize the pipeline"""
        self.input_file = input_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.verbose = verbose
        self.analyzer = ConflictAnalyzer(verbose=verbose)
        self.data_handler = DataHandler()
        self.report_generator = ReportGenerator()

    def run(self) -> Dict[str, Any]:
        """Execute the complete analysis pipeline"""
        logger.info("=" * 80)
        logger.info("Starting Label Conflict Analysis Pipeline")
        logger.info("=" * 80)

        try:
            # Step 1: Load data
            logger.info(f"\n[Step 1] Loading data from {self.input_file}")
            samples = self.data_handler.load_jsonl(self.input_file)
            logger.info(f"✓ Loaded {len(samples)} samples")

            # Step 2: Analyze dataset
            logger.info("\n[Step 2] Analyzing samples for label conflicts")
            results = self.analyzer.analyze_dataset(samples)
            logger.info(f"✓ Analysis complete")

            # Step 3: Extract conflict samples
            logger.info("\n[Step 3] Extracting conflict samples")
            conflict_results = self.analyzer.get_conflict_samples(results)
            logger.info(f"✓ Found {len(conflict_results)} conflicting samples")

            # Step 4: Save results
            logger.info("\n[Step 4] Saving results")
            output_files = self._save_results(results, conflict_results)
            logger.info(f"✓ Results saved to {self.output_dir}")

            # Step 5: Generate reports
            logger.info("\n[Step 5] Generating analysis reports")
            report_files = self._generate_reports(results, conflict_results, samples)
            logger.info(f"✓ Reports generated")

            # Step 6: Print statistics
            stats = self.analyzer.get_statistics()
            logger.info("\n[Step 6] Analysis Statistics")
            logger.info(f"  Total Samples: {stats['total_samples']}")
            logger.info(f"  Conflicting Samples: {stats['conflict_samples']}")
            logger.info(f"  Conflict Rate: {stats['conflict_rate']:.2f}%")

            result = {
                "status": "success",
                "statistics": stats,
                "output_files": output_files,
                "report_files": report_files,
                "analysis_results": results,
            }

            logger.info("\n" + "=" * 80)
            logger.info("Analysis Pipeline Completed Successfully!")
            logger.info("=" * 80)

            return result

        except Exception as e:
            logger.error(f"\n✗ Pipeline failed: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
            }

    def _save_results(
        self, results: List[SampleAnalysis], conflict_results: List[SampleAnalysis]
    ) -> Dict[str, str]:
        """Save analysis results to files"""
        output_files = {}

        # Save all results
        all_results_path = self.output_dir / "all_analysis_results.jsonl"
        all_results_dicts = [r.to_dict() for r in results]
        self.data_handler.save_jsonl(all_results_dicts, str(all_results_path))
        output_files["all_results"] = str(all_results_path)

        # Save conflict-only results
        conflict_results_path = self.output_dir / "conflict_samples.jsonl"
        conflict_dicts = [r.to_dict() for r in conflict_results]
        self.data_handler.save_jsonl(conflict_dicts, str(conflict_results_path))
        output_files["conflicts_only"] = str(conflict_results_path)

        # Save summary JSON
        summary_path = self.output_dir / "analysis_summary.json"
        summary = {
            "total_samples": len(results),
            "conflict_count": len(conflict_results),
            "conflict_rate": len(conflict_results) / len(results) * 100 if results else 0,
            "suggested_labels_summary": self._generate_label_summary(results),
        }
        self.data_handler.save_json(summary, str(summary_path))
        output_files["summary"] = str(summary_path)

        return output_files

    def _generate_label_summary(self, results: List[SampleAnalysis]) -> Dict[str, int]:
        """Generate summary of suggested labels"""
        from collections import Counter
        suggested_labels = [r.suggested_label for r in results if r.suggested_label]
        return dict(Counter(suggested_labels))

    def _generate_reports(
        self,
        results: List[SampleAnalysis],
        conflict_results: List[SampleAnalysis],
        original_samples: List[Dict[str, Any]],
    ) -> Dict[str, str]:
        """Generate comprehensive reports"""
        report_files = {}

        # Generate detailed report
        detailed_report_path = "reports/detailed_analysis_report.md"
        self.report_generator.generate_detailed_report(
            results, conflict_results, detailed_report_path
        )
        report_files["detailed"] = detailed_report_path

        # Generate conflict analysis report
        conflict_report_path = "reports/conflict_analysis_report.md"
        self.report_generator.generate_conflict_report(
            conflict_results, conflict_report_path
        )
        report_files["conflicts"] = conflict_report_path

        # Generate evaluation metrics report
        metrics_report_path = "reports/evaluation_metrics_report.md"
        self.report_generator.generate_metrics_report(
            results, metrics_report_path
        )
        report_files["metrics"] = metrics_report_path

        return report_files


def main(input_file: str = "text_label.jsonl", output_dir: str = "output"):
    """Main entry point"""
    pipeline = AnalysisPipeline(input_file, output_dir, verbose=True)
    result = pipeline.run()
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze label conflicts in multi-annotator datasets"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="text_label.jsonl",
        help="Input JSONL file path",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output",
        help="Output directory for results",
    )
    args = parser.parse_args()

    main(args.input, args.output)
