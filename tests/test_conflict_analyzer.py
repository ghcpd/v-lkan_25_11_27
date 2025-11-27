"""
Comprehensive test suite for label conflict detection and resolution
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
from typing import List, Dict, Any
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.conflict_analyzer import ConflictAnalyzer, SampleAnalysis
from src.data_handler import DataHandler
from src.pipeline import AnalysisPipeline


class TestConflictDetection(unittest.TestCase):
    """Test conflict detection functionality"""

    def setUp(self):
        """Setup test fixtures"""
        self.analyzer = ConflictAnalyzer(verbose=False)

    def test_detect_agreement(self):
        """Test detection of unanimous agreement"""
        labels = [
            {"annotator": "A1", "label": "Positive"},
            {"annotator": "A2", "label": "Positive"},
        ]
        is_conflict = self.analyzer.detect_conflict(labels)
        self.assertFalse(is_conflict)

    def test_detect_conflict_two_labels(self):
        """Test detection of conflict between two labels"""
        labels = [
            {"annotator": "A1", "label": "Positive"},
            {"annotator": "A2", "label": "Negative"},
        ]
        is_conflict = self.analyzer.detect_conflict(labels)
        self.assertTrue(is_conflict)

    def test_detect_conflict_three_labels(self):
        """Test detection of conflict with three different labels"""
        labels = [
            {"annotator": "A1", "label": "Positive"},
            {"annotator": "A2", "label": "Negative"},
            {"annotator": "A3", "label": "Neutral"},
        ]
        is_conflict = self.analyzer.detect_conflict(labels)
        self.assertTrue(is_conflict)

    def test_single_annotator(self):
        """Test handling of single annotator"""
        labels = [{"annotator": "A1", "label": "Positive"}]
        is_conflict = self.analyzer.detect_conflict(labels)
        self.assertFalse(is_conflict)


class TestConflictAnalysis(unittest.TestCase):
    """Test conflict analysis and reasoning"""

    def setUp(self):
        """Setup test fixtures"""
        self.analyzer = ConflictAnalyzer(verbose=False)

    def test_positive_negative_conflict_reason(self):
        """Test conflict reason for Positive vs Negative"""
        labels = [
            {"annotator": "A1", "label": "Positive"},
            {"annotator": "A2", "label": "Negative"},
        ]
        text = "The product is good but expensive"
        reason = self.analyzer.analyze_conflict_reason(text, labels, {"Positive", "Negative"})
        self.assertIsNotNone(reason)
        self.assertIn("sentiment", reason.lower())

    def test_positive_neutral_conflict_reason(self):
        """Test conflict reason for Positive vs Neutral"""
        labels = [
            {"annotator": "A1", "label": "Positive"},
            {"annotator": "A2", "label": "Neutral"},
        ]
        text = "The service was okay"
        reason = self.analyzer.analyze_conflict_reason(text, labels, {"Positive", "Neutral"})
        self.assertIsNotNone(reason)

    def test_no_conflict_reason(self):
        """Test no reason for agreement"""
        labels = [
            {"annotator": "A1", "label": "Positive"},
            {"annotator": "A2", "label": "Positive"},
        ]
        reason = self.analyzer.analyze_conflict_reason("text", labels, {"Positive"})
        self.assertIsNone(reason)


class TestLabelSuggestion(unittest.TestCase):
    """Test final label suggestion logic"""

    def setUp(self):
        """Setup test fixtures"""
        self.analyzer = ConflictAnalyzer(verbose=False)

    def test_unanimous_agreement(self):
        """Test unanimous agreement returns 100% confidence"""
        labels = [
            {"annotator": "A1", "label": "Positive"},
            {"annotator": "A2", "label": "Positive"},
            {"annotator": "A3", "label": "Positive"},
        ]
        text = "Great product!"
        suggestion, confidence, explanation = self.analyzer.suggest_final_label(labels, text)
        self.assertEqual(suggestion, "Positive")
        self.assertEqual(confidence, 1.0)
        self.assertIn("Unanimous", explanation)

    def test_majority_vote_two_vs_one(self):
        """Test majority vote with 2 vs 1 split"""
        labels = [
            {"annotator": "A1", "label": "Positive"},
            {"annotator": "A2", "label": "Positive"},
            {"annotator": "A3", "label": "Negative"},
        ]
        text = "The product is good."
        suggestion, confidence, explanation = self.analyzer.suggest_final_label(labels, text)
        self.assertEqual(suggestion, "Positive")
        self.assertEqual(confidence, 2/3)

    def test_majority_vote_all_equal(self):
        """Test when all annotators disagree equally"""
        labels = [
            {"annotator": "A1", "label": "Positive"},
            {"annotator": "A2", "label": "Negative"},
            {"annotator": "A3", "label": "Neutral"},
        ]
        text = "Mixed quality product"
        suggestion, confidence, explanation = self.analyzer.suggest_final_label(labels, text)
        # Should pick one arbitrarily but with lower confidence
        self.assertIn(suggestion, ["Positive", "Negative", "Neutral"])
        self.assertLess(confidence, 1.0)

    def test_text_based_reasoning(self):
        """Test text-based reasoning for suggestions"""
        labels = [
            {"annotator": "A1", "label": "Positive"},
            {"annotator": "A2", "label": "Positive"},
        ]
        # Very negative text
        text = "Terrible, broken, defective product"
        suggestion, confidence, explanation = self.analyzer.suggest_final_label(labels, text)
        # Should consider text indicators
        self.assertIsNotNone(suggestion)


class TestSampleAnalysis(unittest.TestCase):
    """Test complete sample analysis"""

    def setUp(self):
        """Setup test fixtures"""
        self.analyzer = ConflictAnalyzer(verbose=False)

    def test_analyze_agreement_sample(self):
        """Test analyzing a sample with agreement"""
        sample = {
            "id": 1,
            "text": "Excellent product!",
            "labels": [
                {"annotator": "A1", "label": "Positive"},
                {"annotator": "A2", "label": "Positive"},
            ],
        }
        result = self.analyzer.analyze_sample(sample)

        self.assertEqual(result.id, 1)
        self.assertEqual(result.text, "Excellent product!")
        self.assertFalse(result.is_conflict)
        self.assertEqual(result.suggested_label, "Positive")
        self.assertEqual(result.confidence, 1.0)

    def test_analyze_conflict_sample(self):
        """Test analyzing a sample with conflict"""
        sample = {
            "id": 2,
            "text": "The service was okay but expensive.",
            "labels": [
                {"annotator": "A1", "label": "Positive"},
                {"annotator": "A2", "label": "Neutral"},
            ],
        }
        result = self.analyzer.analyze_sample(sample)

        self.assertEqual(result.id, 2)
        self.assertTrue(result.is_conflict)
        self.assertIsNotNone(result.conflict_reason)
        self.assertIsNotNone(result.suggested_label)
        self.assertIsNotNone(result.confidence)

    def test_sample_to_dict(self):
        """Test converting sample analysis to dictionary"""
        sample = {
            "id": 3,
            "text": "Great!",
            "labels": [{"annotator": "A1", "label": "Positive"}],
        }
        result = self.analyzer.analyze_sample(sample)
        result_dict = result.to_dict()

        self.assertIsInstance(result_dict, dict)
        self.assertEqual(result_dict["id"], 3)
        self.assertEqual(result_dict["text"], "Great!")
        self.assertFalse(result_dict["is_conflict"])


class TestDatasetAnalysis(unittest.TestCase):
    """Test dataset-level analysis"""

    def setUp(self):
        """Setup test fixtures"""
        self.analyzer = ConflictAnalyzer(verbose=False)

    def test_analyze_dataset(self):
        """Test analyzing complete dataset"""
        samples = [
            {
                "id": 1,
                "text": "Great!",
                "labels": [
                    {"annotator": "A1", "label": "Positive"},
                    {"annotator": "A2", "label": "Positive"},
                ],
            },
            {
                "id": 2,
                "text": "Bad experience",
                "labels": [
                    {"annotator": "A1", "label": "Negative"},
                    {"annotator": "A2", "label": "Positive"},
                ],
            },
        ]

        results = self.analyzer.analyze_dataset(samples)

        self.assertEqual(len(results), 2)
        self.assertFalse(results[0].is_conflict)
        self.assertTrue(results[1].is_conflict)

        stats = self.analyzer.get_statistics()
        self.assertEqual(stats["total_samples"], 2)
        self.assertEqual(stats["conflict_samples"], 1)
        self.assertAlmostEqual(stats["conflict_rate"], 50.0, places=1)

    def test_get_conflict_samples(self):
        """Test extracting conflict samples"""
        samples = [
            {
                "id": 1,
                "text": "Text 1",
                "labels": [
                    {"annotator": "A1", "label": "Positive"},
                    {"annotator": "A2", "label": "Positive"},
                ],
            },
            {
                "id": 2,
                "text": "Text 2",
                "labels": [
                    {"annotator": "A1", "label": "Positive"},
                    {"annotator": "A2", "label": "Negative"},
                ],
            },
            {
                "id": 3,
                "text": "Text 3",
                "labels": [
                    {"annotator": "A1", "label": "Neutral"},
                    {"annotator": "A2", "label": "Negative"},
                ],
            },
        ]

        results = self.analyzer.analyze_dataset(samples)
        conflict_results = self.analyzer.get_conflict_samples(results)

        self.assertEqual(len(conflict_results), 2)
        self.assertEqual(conflict_results[0].id, 2)
        self.assertEqual(conflict_results[1].id, 3)


class TestDataHandler(unittest.TestCase):
    """Test data loading and saving"""

    def setUp(self):
        """Setup test fixtures"""
        self.handler = DataHandler()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_and_load_jsonl(self):
        """Test saving and loading JSONL files"""
        test_data = [
            {"id": 1, "text": "Sample 1"},
            {"id": 2, "text": "Sample 2"},
        ]

        file_path = os.path.join(self.temp_dir, "test.jsonl")
        self.handler.save_jsonl(test_data, file_path)
        loaded_data = self.handler.load_jsonl(file_path)

        self.assertEqual(len(loaded_data), 2)
        self.assertEqual(loaded_data[0]["id"], 1)
        self.assertEqual(loaded_data[1]["text"], "Sample 2")

    def test_save_and_load_json(self):
        """Test saving and loading JSON files"""
        test_data = {"key": "value", "number": 42}

        file_path = os.path.join(self.temp_dir, "test.json")
        self.handler.save_json(test_data, file_path)
        loaded_data = self.handler.load_json(file_path)

        self.assertEqual(loaded_data["key"], "value")
        self.assertEqual(loaded_data["number"], 42)


class TestPipeline(unittest.TestCase):
    """Test end-to-end pipeline"""

    def setUp(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.handler = DataHandler()

        # Create a small test dataset
        self.test_data = [
            {
                "id": 1,
                "text": "Great product!",
                "labels": [
                    {"annotator": "A1", "label": "Positive"},
                    {"annotator": "A2", "label": "Positive"},
                ],
            },
            {
                "id": 2,
                "text": "It was okay.",
                "labels": [
                    {"annotator": "A1", "label": "Neutral"},
                    {"annotator": "A2", "label": "Positive"},
                ],
            },
            {
                "id": 3,
                "text": "Terrible experience",
                "labels": [
                    {"annotator": "A1", "label": "Negative"},
                    {"annotator": "A2", "label": "Negative"},
                ],
            },
        ]

        self.input_file = os.path.join(self.temp_dir, "test_input.jsonl")
        self.handler.save_jsonl(self.test_data, self.input_file)

    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_pipeline_execution(self):
        """Test complete pipeline execution"""
        output_dir = os.path.join(self.temp_dir, "output")
        pipeline = AnalysisPipeline(self.input_file, output_dir, verbose=False)
        result = pipeline.run()

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["statistics"]["total_samples"], 3)
        self.assertEqual(result["statistics"]["conflict_samples"], 1)

    def test_pipeline_output_files(self):
        """Test that pipeline creates expected output files"""
        output_dir = os.path.join(self.temp_dir, "output")
        pipeline = AnalysisPipeline(self.input_file, output_dir, verbose=False)
        result = pipeline.run()

        output_files = result["output_files"]
        self.assertIn("all_results", output_files)
        self.assertIn("conflicts_only", output_files)
        self.assertIn("summary", output_files)

        # Check files exist
        self.assertTrue(os.path.exists(output_files["all_results"]))
        self.assertTrue(os.path.exists(output_files["conflicts_only"]))
        self.assertTrue(os.path.exists(output_files["summary"]))


class TestRealWorldScenarios(unittest.TestCase):
    """Test real-world scenarios and edge cases"""

    def setUp(self):
        """Setup test fixtures"""
        self.analyzer = ConflictAnalyzer(verbose=False)

    def test_ambiguous_text_with_mixed_sentiment(self):
        """Test handling ambiguous text with mixed sentiment"""
        sample = {
            "id": 1,
            "text": "The UI is clean but performance is terrible.",
            "labels": [
                {"annotator": "A1", "label": "Negative"},
                {"annotator": "A2", "label": "Positive"},
            ],
        }
        result = self.analyzer.analyze_sample(sample)

        self.assertTrue(result.is_conflict)
        self.assertIn("mixed", result.conflict_reason.lower() or "ambiguous" in result.conflict_reason.lower())

    def test_unclear_annotation_policy(self):
        """Test handling samples where annotation policy is unclear"""
        sample = {
            "id": 2,
            "text": "It's just fine, nothing wrong with it.",
            "labels": [
                {"annotator": "A1", "label": "Positive"},
                {"annotator": "A2", "label": "Neutral"},
            ],
        }
        result = self.analyzer.analyze_sample(sample)

        self.assertTrue(result.is_conflict)
        self.assertIsNotNone(result.suggested_label)
        self.assertGreater(result.confidence, 0)

    def test_multi_aspect_evaluation(self):
        """Test handling multi-aspect evaluation"""
        sample = {
            "id": 3,
            "text": "Good quality but terrible packaging.",
            "labels": [
                {"annotator": "A1", "label": "Positive"},
                {"annotator": "A2", "label": "Negative"},
                {"annotator": "A3", "label": "Neutral"},
            ],
        }
        result = self.analyzer.analyze_sample(sample)

        self.assertTrue(result.is_conflict)
        self.assertIsNotNone(result.suggested_label)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestConflictDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestConflictAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(TestLabelSuggestion))
    suite.addTests(loader.loadTestsFromTestCase(TestSampleAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(TestDatasetAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(TestDataHandler))
    suite.addTests(loader.loadTestsFromTestCase(TestPipeline))
    suite.addTests(loader.loadTestsFromTestCase(TestRealWorldScenarios))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    run_tests()
