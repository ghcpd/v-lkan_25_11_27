"""
Integration tests for real-time collaboration, persistence, conflict handling,
and multi-document behavior
"""

import unittest
import tempfile
import os
import json
import time
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.conflict_analyzer import ConflictAnalyzer
from src.data_handler import DataHandler
from src.pipeline import AnalysisPipeline


class TestRealTimeCollaboration(unittest.TestCase):
    """Test real-time collaboration scenarios"""

    def setUp(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.handler = DataHandler()

    def tearDown(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_concurrent_annotation_handling(self):
        """Test handling multiple annotators adding labels"""
        # Simulate incremental annotation
        sample = {
            "id": 1,
            "text": "Test product",
            "labels": []
        }

        # First annotator
        sample["labels"].append({"annotator": "A1", "label": "Positive"})
        analyzer = ConflictAnalyzer()
        result = analyzer.analyze_sample(sample)
        self.assertFalse(result.is_conflict)

        # Second annotator with same label
        sample["labels"].append({"annotator": "A2", "label": "Positive"})
        result = analyzer.analyze_sample(sample)
        self.assertFalse(result.is_conflict)

        # Third annotator with different label
        sample["labels"].append({"annotator": "A3", "label": "Neutral"})
        result = analyzer.analyze_sample(sample)
        self.assertTrue(result.is_conflict)

    def test_annotation_update_handling(self):
        """Test handling when annotators update their labels"""
        analyzer = ConflictAnalyzer()

        sample = {
            "id": 1,
            "text": "Test text",
            "labels": [
                {"annotator": "A1", "label": "Positive"},
                {"annotator": "A2", "label": "Positive"}
            ]
        }

        # Initial state: agreement
        result = analyzer.analyze_sample(sample)
        self.assertFalse(result.is_conflict)
        initial_suggestion = result.suggested_label

        # Update A2's label
        sample["labels"][1]["label"] = "Negative"
        result = analyzer.analyze_sample(sample)
        self.assertTrue(result.is_conflict)
        self.assertNotEqual(result.suggested_label, initial_suggestion)

    def test_new_annotator_addition(self):
        """Test adding new annotators to existing samples"""
        analyzer = ConflictAnalyzer()
        original_labels = 2

        sample = {
            "id": 1,
            "text": "Product review",
            "labels": [
                {"annotator": "A1", "label": "Positive"},
                {"annotator": "A2", "label": "Positive"}
            ]
        }

        result = analyzer.analyze_sample(sample)
        self.assertEqual(len(result.labels), original_labels)

        # Add new annotator
        sample["labels"].append({"annotator": "A3", "label": "Positive"})
        result = analyzer.analyze_sample(sample)
        self.assertEqual(len(result.labels), original_labels + 1)


class TestPersistenceAndRecovery(unittest.TestCase):
    """Test data persistence and recovery"""

    def setUp(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.handler = DataHandler()

    def tearDown(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_and_reload_results(self):
        """Test saving and reloading analysis results"""
        original_data = [
            {"id": 1, "text": "Test 1", "value": "data1"},
            {"id": 2, "text": "Test 2", "value": "data2"},
        ]

        file_path = os.path.join(self.temp_dir, "persist.jsonl")

        # Save
        self.handler.save_jsonl(original_data, file_path)
        self.assertTrue(os.path.exists(file_path))

        # Reload
        loaded_data = self.handler.load_jsonl(file_path)
        self.assertEqual(len(loaded_data), len(original_data))
        self.assertEqual(loaded_data[0]["value"], "data1")

    def test_incremental_save(self):
        """Test incremental saving of results"""
        base_path = os.path.join(self.temp_dir, "incremental.jsonl")

        # First batch
        batch1 = [{"id": 1, "data": "batch1"}]
        self.handler.save_jsonl(batch1, base_path)

        # Second batch (overwrite)
        batch2 = batch1 + [{"id": 2, "data": "batch2"}]
        self.handler.save_jsonl(batch2, base_path)

        # Verify
        loaded = self.handler.load_jsonl(base_path)
        self.assertEqual(len(loaded), 2)

    def test_json_persistence(self):
        """Test JSON file persistence"""
        data = {
            "timestamp": "2025-11-27",
            "results": [{"id": 1}, {"id": 2}],
            "metrics": {"conflict_rate": 15.0}
        }

        file_path = os.path.join(self.temp_dir, "data.json")
        self.handler.save_json(data, file_path)

        loaded_data = self.handler.load_json(file_path)
        self.assertEqual(loaded_data["metrics"]["conflict_rate"], 15.0)


class TestConflictHandling(unittest.TestCase):
    """Test comprehensive conflict handling"""

    def setUp(self):
        """Setup test fixtures"""
        self.analyzer = ConflictAnalyzer(verbose=False)

    def test_pairwise_conflict_detection(self):
        """Test detecting conflicts between every pair of annotators"""
        sample = {
            "id": 1,
            "text": "Test text",
            "labels": [
                {"annotator": "A1", "label": "Positive"},
                {"annotator": "A2", "label": "Negative"},
                {"annotator": "A3", "label": "Neutral"}
            ]
        }

        result = self.analyzer.analyze_sample(sample)
        self.assertTrue(result.is_conflict)
        self.assertEqual(len(result.labels), 3)

    def test_conflict_resolution_consistency(self):
        """Test that conflict resolution is consistent"""
        sample = {
            "id": 1,
            "text": "Test",
            "labels": [
                {"annotator": "A1", "label": "Positive"},
                {"annotator": "A2", "label": "Neutral"},
                {"annotator": "A3", "label": "Positive"}
            ]
        }

        # Analyze multiple times
        result1 = self.analyzer.analyze_sample(sample)
        result2 = self.analyzer.analyze_sample(sample)

        self.assertEqual(result1.suggested_label, result2.suggested_label)
        self.assertEqual(result1.confidence, result2.confidence)

    def test_majority_determination(self):
        """Test correct majority label determination"""
        # 2 positive, 1 negative
        sample = {
            "id": 1,
            "text": "Test",
            "labels": [
                {"annotator": "A1", "label": "Positive"},
                {"annotator": "A2", "label": "Positive"},
                {"annotator": "A3", "label": "Negative"}
            ]
        }

        result = self.analyzer.analyze_sample(sample)
        self.assertEqual(result.suggested_label, "Positive")

    def test_edge_case_single_label_conflict(self):
        """Test edge case with minimal conflict"""
        sample = {
            "id": 1,
            "text": "Test",
            "labels": [
                {"annotator": "A1", "label": "Positive"},
                {"annotator": "A2", "label": "Neutral"}
            ]
        }

        result = self.analyzer.analyze_sample(sample)
        self.assertTrue(result.is_conflict)
        self.assertIsNotNone(result.suggested_label)


class TestMultiDocumentBehavior(unittest.TestCase):
    """Test multi-document/dataset behavior"""

    def setUp(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.handler = DataHandler()
        self.analyzer = ConflictAnalyzer(verbose=False)

    def tearDown(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_independent_sample_analysis(self):
        """Test that samples are analyzed independently"""
        samples = [
            {
                "id": 1,
                "text": "Text 1",
                "labels": [
                    {"annotator": "A1", "label": "Positive"},
                    {"annotator": "A2", "label": "Positive"}
                ]
            },
            {
                "id": 2,
                "text": "Text 2",
                "labels": [
                    {"annotator": "A1", "label": "Negative"},
                    {"annotator": "A2", "label": "Positive"}
                ]
            }
        ]

        results = self.analyzer.analyze_dataset(samples)

        # First sample should be agreement
        self.assertFalse(results[0].is_conflict)
        # Second sample should be conflict
        self.assertTrue(results[1].is_conflict)

    def test_cross_sample_statistics(self):
        """Test that statistics are correctly computed across samples"""
        samples = [
            {"id": i, "text": f"Text {i}", "labels": [
                {"annotator": "A1", "label": "Positive"},
                {"annotator": "A2", "label": "Positive"}
            ]} for i in range(1, 6)
        ]

        # Add some conflicts
        samples[1]["labels"][1]["label"] = "Negative"
        samples[3]["labels"][1]["label"] = "Neutral"

        results = self.analyzer.analyze_dataset(samples)
        stats = self.analyzer.get_statistics()

        self.assertEqual(stats["total_samples"], 5)
        self.assertEqual(stats["conflict_samples"], 2)
        self.assertEqual(stats["conflict_rate"], 40.0)

    def test_multi_batch_processing(self):
        """Test processing multiple batches of data"""
        batch1 = [
            {"id": 1, "text": "A", "labels": [
                {"annotator": "A1", "label": "Positive"},
                {"annotator": "A2", "label": "Positive"}
            ]},
            {"id": 2, "text": "B", "labels": [
                {"annotator": "A1", "label": "Negative"},
                {"annotator": "A2", "label": "Negative"}
            ]}
        ]

        batch2 = [
            {"id": 3, "text": "C", "labels": [
                {"annotator": "A1", "label": "Positive"},
                {"annotator": "A2", "label": "Neutral"}
            ]},
            {"id": 4, "text": "D", "labels": [
                {"annotator": "A1", "label": "Neutral"},
                {"annotator": "A2", "label": "Neutral"}
            ]}
        ]

        # Process batch 1
        results1 = self.analyzer.analyze_dataset(batch1)
        stats1 = self.analyzer.get_statistics()
        self.assertEqual(stats1["conflict_samples"], 0)

        # Process batch 2
        results2 = self.analyzer.analyze_dataset(batch2)
        stats2 = self.analyzer.get_statistics()
        self.assertEqual(stats2["conflict_samples"], 1)
        self.assertEqual(stats2["total_samples"], 2)

    def test_dataset_integrity(self):
        """Test that datasets maintain integrity through processing"""
        original_samples = [
            {
                "id": 1,
                "text": "Original text",
                "labels": [
                    {"annotator": "A1", "label": "Positive"},
                    {"annotator": "A2", "label": "Positive"}
                ]
            },
            {
                "id": 2,
                "text": "Another text",
                "labels": [
                    {"annotator": "A1", "label": "Negative"},
                    {"annotator": "A2", "label": "Negative"}
                ]
            }
        ]

        results = self.analyzer.analyze_dataset(original_samples)

        # Verify original samples unchanged
        self.assertEqual(original_samples[0]["text"], "Original text")
        self.assertEqual(len(original_samples[1]["labels"]), 2)

        # Verify results have correct data
        self.assertEqual(results[0].text, "Original text")
        self.assertEqual(results[1].id, 2)


class TestEndToEndIntegration(unittest.TestCase):
    """Test complete end-to-end workflow"""

    def setUp(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.handler = DataHandler()

        # Create test data
        self.test_data = [
            {
                "id": 1,
                "text": "Great product!",
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
                "text": "Terrible",
                "labels": [
                    {"annotator": "A1", "label": "Negative"},
                    {"annotator": "A2", "label": "Negative"}
                ]
            }
        ]

        self.input_file = os.path.join(self.temp_dir, "test.jsonl")
        self.handler.save_jsonl(self.test_data, self.input_file)

    def tearDown(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_pipeline_workflow(self):
        """Test complete pipeline from input to output"""
        output_dir = os.path.join(self.temp_dir, "output")
        pipeline = AnalysisPipeline(self.input_file, output_dir, verbose=False)

        result = pipeline.run()

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["statistics"]["total_samples"], 3)
        self.assertEqual(result["statistics"]["conflict_samples"], 1)

    def test_output_file_creation(self):
        """Test that all output files are created"""
        output_dir = os.path.join(self.temp_dir, "output")
        pipeline = AnalysisPipeline(self.input_file, output_dir, verbose=False)

        result = pipeline.run()

        # Check output files exist
        for file_type, path in result["output_files"].items():
            self.assertTrue(
                os.path.exists(path),
                f"Output file missing: {file_type} at {path}"
            )

    def test_result_correctness(self):
        """Test that results are correct"""
        output_dir = os.path.join(self.temp_dir, "output")
        pipeline = AnalysisPipeline(self.input_file, output_dir, verbose=False)

        result = pipeline.run()

        # Load and verify results
        results_file = result["output_files"]["all_results"]
        results = self.handler.load_jsonl(results_file)

        self.assertEqual(len(results), 3)
        self.assertFalse(results[0]["is_conflict"])
        self.assertTrue(results[1]["is_conflict"])
        self.assertFalse(results[2]["is_conflict"])


def run_integration_tests():
    """Run all integration tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestRealTimeCollaboration))
    suite.addTests(loader.loadTestsFromTestCase(TestPersistenceAndRecovery))
    suite.addTests(loader.loadTestsFromTestCase(TestConflictHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestMultiDocumentBehavior))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEndIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    run_integration_tests()
