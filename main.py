"""
Main script for multi-annotator conflict detection and resolution

Usage:
    python main.py <input_file> [--output OUTPUT_FILE] [--conflicts-only] [--report REPORT_FILE]

Example:
    python main.py text_label.jsonl --output results.jsonl --report report.json
"""

import json
import argparse
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any

from analyzer import ConflictAnalyzer


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_jsonl_dataset(file_path: str) -> List[Dict[str, Any]]:
    """
    Load dataset from JSONL file
    
    Args:
        file_path: Path to JSONL file
        
    Returns:
        List of sample dictionaries
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is invalid
    """
    if not Path(file_path).exists():
        raise FileNotFoundError(f"Dataset file not found: {file_path}")
    
    dataset = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    sample = json.loads(line.strip())
                    dataset.append(sample)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON at line {line_num}: {e}")
    except Exception as e:
        logger.error(f"Error loading dataset: {e}")
        raise
    
    logger.info(f"Loaded {len(dataset)} samples from {file_path}")
    return dataset


def validate_dataset(dataset: List[Dict[str, Any]]) -> None:
    """
    Validate dataset structure
    
    Args:
        dataset: Dataset to validate
        
    Raises:
        ValueError: If dataset structure is invalid
    """
    if not dataset:
        raise ValueError("Dataset is empty")
    
    required_fields = {'id', 'text', 'labels'}
    
    for idx, sample in enumerate(dataset):
        if not isinstance(sample, dict):
            raise ValueError(f"Sample {idx} is not a dictionary")
        
        missing_fields = required_fields - set(sample.keys())
        if missing_fields:
            raise ValueError(f"Sample {idx} missing fields: {missing_fields}")
        
        if not isinstance(sample['labels'], list):
            raise ValueError(f"Sample {idx}: labels must be a list")
        
        if not sample['labels']:
            raise ValueError(f"Sample {idx}: labels list is empty")
        
        for label_idx, label in enumerate(sample['labels']):
            if not isinstance(label, dict):
                raise ValueError(f"Sample {idx}, label {label_idx} is not a dictionary")
            
            if 'annotator' not in label or 'label' not in label:
                raise ValueError(f"Sample {idx}, label {label_idx} missing annotator or label field")
    
    logger.info("Dataset validation passed")


def generate_report(analyzer: ConflictAnalyzer, report_file: str = 'conflict_report.json') -> None:
    """
    Generate analysis report
    
    Args:
        analyzer: ConflictAnalyzer instance with analyzed data
        report_file: Output report file path
    """
    report = analyzer.get_conflict_report()
    
    report['summary'] = {
        'total_samples_analyzed': report.get('total_samples', 0),
        'samples_with_conflicts': report.get('conflicted_samples', 0),
        'conflict_percentage': f"{report.get('conflict_percentage', 0)}%",
        'average_confidence_score': report.get('average_confidence', 0)
    }
    
    report['annotator_agreement_statistics'] = report.pop('annotator_agreement', {})
    report['top_conflict_reasons'] = [
        {
            'reason': reason,
            'frequency': count,
            'percentage': f"{(count / report['total_samples'] * 100):.2f}%"
        }
        for reason, count in report.pop('top_conflict_reasons', [])
    ]
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Report generated: {report_file}")
    
    # Print summary to console
    print("\n" + "="*70)
    print("CONFLICT ANALYSIS REPORT")
    print("="*70)
    print(f"\nTotal Samples Analyzed: {report['summary']['total_samples_analyzed']}")
    print(f"Samples with Conflicts: {report['summary']['samples_with_conflicts']}")
    print(f"Conflict Percentage: {report['summary']['conflict_percentage']}")
    print(f"Average Confidence Score: {report['summary']['average_confidence_score']}")
    
    print("\n" + "-"*70)
    print("TOP CONFLICT REASONS:")
    print("-"*70)
    for item in report['top_conflict_reasons']:
        print(f"  • {item['reason']}")
        print(f"    Frequency: {item['frequency']} ({item['percentage']})\n")
    
    print("\n" + "-"*70)
    print("ANNOTATOR AGREEMENT STATISTICS:")
    print("-"*70)
    for pair, agreement in report['annotator_agreement_statistics'].items():
        print(f"  {pair}: {agreement*100:.1f}% agreement")
    print()


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description='Detect and analyze annotation conflicts in multi-annotator datasets',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python main.py text_label.jsonl
  python main.py text_label.jsonl --output results.jsonl
  python main.py text_label.jsonl --conflicts-only --report report.json
        '''
    )
    
    parser.add_argument(
        'input_file',
        help='Path to input JSONL dataset file'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='conflict_analysis_results.jsonl',
        help='Output file for all analyzed results (default: conflict_analysis_results.jsonl)'
    )
    
    parser.add_argument(
        '--conflicts-only', '-c',
        action='store_true',
        help='Export only conflicted samples to a separate file (conflicts_only.jsonl)'
    )
    
    parser.add_argument(
        '--report', '-r',
        default='conflict_report.json',
        help='Output file for analysis report (default: conflict_report.json)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Load and validate dataset
        logger.info("Starting conflict analysis pipeline...")
        dataset = load_jsonl_dataset(args.input_file)
        validate_dataset(dataset)
        
        # Perform analysis
        analyzer = ConflictAnalyzer()
        analyzer.detect_conflicts(dataset)
        
        # Export results
        analyzer.export_results(args.output)
        if args.conflicts_only:
            analyzer.export_conflicts_only('conflicts_only.jsonl')
        
        # Generate report
        generate_report(analyzer, args.report)
        
        logger.info("Pipeline completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
