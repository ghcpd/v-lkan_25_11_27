"""
Comprehensive test suite for multi-annotator conflict detection system

Tests cover:
- Conflict detection accuracy
- Conflict reasoning quality
- Label resolution reliability
- Data persistence
- Edge cases and error handling
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
from typing import List, Dict, Any

from analyzer import ConflictAnalyzer, AnnotationResult


class TestConflictDetection(unittest.TestCase):
    """Test conflict detection functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = ConflictAnalyzer()
    
    def test_no_conflict_unanimous_agreement(self):
        """Test that unanimous agreement is correctly identified as no conflict"""
        dataset = [{
            'id': 1,
            'text': 'Excellent product!',
            'labels': [
                {'annotator': 'A1', 'label': 'Positive'},
                {'annotator': 'A2', 'label': 'Positive'}
            ]
        }]
        
        self.analyzer.detect_conflicts(dataset)
        result = self.analyzer.analyzed_samples[0]
        
        self.assertFalse(result.is_conflict)
        self.assertEqual(result.suggested_label, 'Positive')
        self.assertEqual(result.confidence, 1.0)
    
    def test_conflict_detection_binary(self):
        """Test detection of simple binary conflict"""
        dataset = [{
            'id': 1,
            'text': 'The product is okay but has issues.',
            'labels': [
                {'annotator': 'A1', 'label': 'Positive'},
                {'annotator': 'A2', 'label': 'Negative'}
            ]
        }]
        
        self.analyzer.detect_conflicts(dataset)
        result = self.analyzer.analyzed_samples[0]
        
        self.assertTrue(result.is_conflict)
        self.assertIsNotNone(result.conflict_reason)
    
    def test_conflict_detection_three_way(self):
        """Test detection of three-way conflict"""
        dataset = [{
            'id': 1,
            'text': 'Product is somewhat mixed.',
            'labels': [
                {'annotator': 'A1', 'label': 'Positive'},
                {'annotator': 'A2', 'label': 'Neutral'},
                {'annotator': 'A3', 'label': 'Negative'}
            ]
        }]
        
        self.analyzer.detect_conflicts(dataset)
        result = self.analyzer.analyzed_samples[0]
        
        self.assertTrue(result.is_conflict)
        self.assertEqual(len(result.annotation_distribution), 3)
    
    def test_conflict_with_two_of_three_agreement(self):
        """Test conflict with 2-out-of-3 agreement"""
        dataset = [{
            'id': 1,
            'text': 'Great product overall.',
            'labels': [
                {'annotator': 'A1', 'label': 'Positive'},
                {'annotator': 'A2', 'label': 'Positive'},
                {'annotator': 'A3', 'label': 'Neutral'}
            ]
        }]
        
        self.analyzer.detect_conflicts(dataset)
        result = self.analyzer.analyzed_samples[0]
        
        self.assertTrue(result.is_conflict)
        self.assertEqual(result.suggested_label, 'Positive')
        self.assertGreater(result.confidence, 0.5)


class TestConflictReasoning(unittest.TestCase):
    """Test conflict reasoning and explanation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = ConflictAnalyzer()
    
    def test_mixed_sentiment_detection(self):
        """Test detection of mixed sentiment in conflict reasoning"""
        dataset = [{
            'id': 1,
            'text': 'Good design but terrible performance.',
            'labels': [
                {'annotator': 'A1', 'label': 'Positive'},
                {'annotator': 'A2', 'label': 'Negative'}
            ]
        }]
        
        self.analyzer.detect_conflicts(dataset)
        result = self.analyzer.analyzed_samples[0]
        
        self.assertTrue(result.is_conflict)
        self.assertIn('mixed sentiment', result.conflict_reason.lower())
    
    def test_ambiguous_language_detection(self):
        """Test detection of ambiguous language"""
        dataset = [{
            'id': 1,
            'text': 'I liked some parts but disliked others.',
            'labels': [
                {'annotator': 'A1', 'label': 'Positive'},
                {'annotator': 'A2', 'label': 'Neutral'}
            ]
        }]
        
        self.analyzer.detect_conflicts(dataset)
        result = self.analyzer.analyzed_samples[0]
        
        self.assertTrue(result.is_conflict)
        self.assertIn('ambiguous', result.conflict_reason.lower())
    
    def test_intensity_disagreement_detection(self):
        """Test detection of intensity disagreement"""
        dataset = [{
            'id': 1,
            'text': 'Good product, somewhat satisfactory.',
            'labels': [
                {'annotator': 'A1', 'label': 'Positive'},
                {'annotator': 'A2', 'label': 'Neutral'}
            ]
        }]
        
        self.analyzer.detect_conflicts(dataset)
        result = self.analyzer.analyzed_samples[0]
        
        self.assertTrue(result.is_conflict)
        self.assertIn('intensity', result.conflict_reason.lower())
    
    def test_subjective_evaluation_detection(self):
        """Test detection of subjective evaluation"""
        dataset = [{
            'id': 1,
            'text': 'I love the design but my friend thinks it is ugly.',
            'labels': [
                {'annotator': 'A1', 'label': 'Positive'},
                {'annotator': 'A2', 'label': 'Negative'}
            ]
        }]
        
        self.analyzer.detect_conflicts(dataset)
        result = self.analyzer.analyzed_samples[0]
        
        self.assertTrue(result.is_conflict)
        self.assertIsNotNone(result.conflict_reason)


class TestLabelResolution(unittest.TestCase):
    """Test label resolution and suggestion"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = ConflictAnalyzer()
    
    def test_majority_vote_resolution(self):
        """Test majority vote resolution"""
        dataset = [{
            'id': 1,
            'text': 'Excellent product!',
            'labels': [
                {'annotator': 'A1', 'label': 'Positive'},
                {'annotator': 'A2', 'label': 'Positive'},
                {'annotator': 'A3', 'label': 'Neutral'}
            ]
        }]
        
        self.analyzer.detect_conflicts(dataset)
        result = self.analyzer.analyzed_samples[0]
        
        self.assertEqual(result.suggested_label, 'Positive')
        self.assertGreater(result.confidence, 0.5)
    
    def test_text_sentiment_analysis_resolution(self):
        """Test text sentiment-based resolution for balanced disagreement"""
        dataset = [{
            'id': 1,
            'text': 'Terrible service and awful experience!',
            'labels': [
                {'annotator': 'A1', 'label': 'Positive'},
                {'annotator': 'A2', 'label': 'Negative'}
            ]
        }]
        
        self.analyzer.detect_conflicts(dataset)
        result = self.analyzer.analyzed_samples[0]
        
        # Should resolve to Negative based on strong negative keywords
        self.assertEqual(result.suggested_label, 'Negative')
    
    def test_confidence_scoring(self):
        """Test confidence score calculation"""
        # Unanimous agreement
        dataset1 = [{
            'id': 1,
            'text': 'Great product!',
            'labels': [
                {'annotator': 'A1', 'label': 'Positive'},
                {'annotator': 'A2', 'label': 'Positive'}
            ]
        }]
        
        self.analyzer.detect_conflicts(dataset1)
        result1 = self.analyzer.analyzed_samples[0]
        high_confidence = result1.confidence
        
        # Conflicted disagreement
        analyzer2 = ConflictAnalyzer()
        dataset2 = [{
            'id': 1,
            'text': 'Mixed sentiments here.',
            'labels': [
                {'annotator': 'A1', 'label': 'Positive'},
                {'annotator': 'A2', 'label': 'Negative'}
            ]
        }]
        
        analyzer2.detect_conflicts(dataset2)
        result2 = analyzer2.analyzed_samples[0]
        low_confidence = result2.confidence
        
        # Unanimous should have higher confidence than conflicted
        self.assertGreater(high_confidence, low_confidence)


class TestDataPersistence(unittest.TestCase):
    """Test data persistence and export functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = ConflictAnalyzer()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_export_all_results(self):
        """Test exporting all analyzed results"""
        dataset = [
            {
                'id': 1,
                'text': 'Good product.',
                'labels': [
                    {'annotator': 'A1', 'label': 'Positive'},
                    {'annotator': 'A2', 'label': 'Positive'}
                ]
            },
            {
                'id': 2,
                'text': 'Good but bad.',
                'labels': [
                    {'annotator': 'A1', 'label': 'Positive'},
                    {'annotator': 'A2', 'label': 'Negative'}
                ]
            }
        ]
        
        self.analyzer.detect_conflicts(dataset)
        output_file = os.path.join(self.temp_dir, 'results.jsonl')
        self.analyzer.export_results(output_file)
        
        # Verify file exists and contains correct number of lines
        self.assertTrue(os.path.exists(output_file))
        with open(output_file, 'r') as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 2)
        
        # Verify JSON validity
        for line in lines:
            data = json.loads(line)
            self.assertIn('id', data)
            self.assertIn('is_conflict', data)
            self.assertIn('suggested_label', data)
    
    def test_export_conflicts_only(self):
        """Test exporting only conflicted samples"""
        dataset = [
            {
                'id': 1,
                'text': 'Good product.',
                'labels': [
                    {'annotator': 'A1', 'label': 'Positive'},
                    {'annotator': 'A2', 'label': 'Positive'}
                ]
            },
            {
                'id': 2,
                'text': 'Good but bad.',
                'labels': [
                    {'annotator': 'A1', 'label': 'Positive'},
                    {'annotator': 'A2', 'label': 'Negative'}
                ]
            }
        ]
        
        self.analyzer.detect_conflicts(dataset)
        output_file = os.path.join(self.temp_dir, 'conflicts.jsonl')
        self.analyzer.export_conflicts_only(output_file)
        
        # Verify file exists and contains only conflicts
        self.assertTrue(os.path.exists(output_file))
        with open(output_file, 'r') as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 1)  # Only one conflict
        
        # Verify conflict sample
        data = json.loads(lines[0])
        self.assertTrue(data['is_conflict'])


class TestReportGeneration(unittest.TestCase):
    """Test report generation functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = ConflictAnalyzer()
    
    def test_conflict_report_structure(self):
        """Test structure of generated conflict report"""
        dataset = [
            {
                'id': 1,
                'text': 'Good product.',
                'labels': [
                    {'annotator': 'A1', 'label': 'Positive'},
                    {'annotator': 'A2', 'label': 'Positive'}
                ]
            },
            {
                'id': 2,
                'text': 'Good but bad.',
                'labels': [
                    {'annotator': 'A1', 'label': 'Positive'},
                    {'annotator': 'A2', 'label': 'Negative'}
                ]
            }
        ]
        
        self.analyzer.detect_conflicts(dataset)
        report = self.analyzer.get_conflict_report()
        
        self.assertIn('total_samples', report)
        self.assertIn('conflicted_samples', report)
        self.assertIn('conflict_percentage', report)
        self.assertIn('annotator_agreement', report)
        self.assertIn('average_confidence', report)
        
        self.assertEqual(report['total_samples'], 2)
        self.assertEqual(report['conflicted_samples'], 1)
    
    def test_annotator_agreement_calculation(self):
        """Test annotator agreement statistics"""
        dataset = [
            {
                'id': 1,
                'text': 'Good product.',
                'labels': [
                    {'annotator': 'A1', 'label': 'Positive'},
                    {'annotator': 'A2', 'label': 'Positive'}
                ]
            },
            {
                'id': 2,
                'text': 'Bad product.',
                'labels': [
                    {'annotator': 'A1', 'label': 'Negative'},
                    {'annotator': 'A2', 'label': 'Negative'}
                ]
            }
        ]
        
        self.analyzer.detect_conflicts(dataset)
        report = self.analyzer.get_conflict_report()
        
        # A1 and A2 should have 100% agreement
        self.assertIn('A1-A2', report['annotator_agreement'])
        self.assertEqual(report['annotator_agreement']['A1-A2'], 1.0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = ConflictAnalyzer()
    
    def test_single_annotator(self):
        """Test handling of samples with only one annotator"""
        dataset = [{
            'id': 1,
            'text': 'Product review.',
            'labels': [
                {'annotator': 'A1', 'label': 'Positive'}
            ]
        }]
        
        self.analyzer.detect_conflicts(dataset)
        result = self.analyzer.analyzed_samples[0]
        
        self.assertFalse(result.is_conflict)
        self.assertEqual(result.suggested_label, 'Positive')
    
    def test_four_way_conflict(self):
        """Test handling of four-way conflict"""
        dataset = [{
            'id': 1,
            'text': 'Extremely mixed product.',
            'labels': [
                {'annotator': 'A1', 'label': 'Positive'},
                {'annotator': 'A2', 'label': 'Positive'},
                {'annotator': 'A3', 'label': 'Negative'},
                {'annotator': 'A4', 'label': 'Neutral'}
            ]
        }]
        
        self.analyzer.detect_conflicts(dataset)
        result = self.analyzer.analyzed_samples[0]
        
        self.assertTrue(result.is_conflict)
        self.assertEqual(result.suggested_label, 'Positive')  # Majority
    
    def test_empty_text_handling(self):
        """Test handling of empty text"""
        dataset = [{
            'id': 1,
            'text': '',
            'labels': [
                {'annotator': 'A1', 'label': 'Positive'},
                {'annotator': 'A2', 'label': 'Negative'}
            ]
        }]
        
        self.analyzer.detect_conflicts(dataset)
        result = self.analyzer.analyzed_samples[0]
        
        # Should handle gracefully
        self.assertTrue(result.is_conflict)
        self.assertIsNotNone(result.suggested_label)
    
    def test_large_dataset(self):
        """Test handling of large dataset"""
        # Generate 1000 samples
        dataset = []
        for i in range(1000):
            dataset.append({
                'id': i,
                'text': f'Sample text {i}',
                'labels': [
                    {'annotator': 'A1', 'label': 'Positive'},
                    {'annotator': 'A2', 'label': 'Positive' if i % 2 == 0 else 'Negative'}
                ]
            })
        
        self.analyzer.detect_conflicts(dataset)
        
        self.assertEqual(len(self.analyzer.analyzed_samples), 1000)
        self.assertEqual(len(self.analyzer.conflict_samples), 500)  # Approximately half


class TestSentimentAnalysis(unittest.TestCase):
    """Test text sentiment analysis"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = ConflictAnalyzer()
    
    def test_strong_positive_sentiment(self):
        """Test detection of strong positive sentiment"""
        text = "Excellent and amazing product! Highly recommend!"
        result = self.analyzer._analyze_text_sentiment(text)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['label'], 'Positive')
        self.assertGreater(result['strength'], 0.7)
    
    def test_strong_negative_sentiment(self):
        """Test detection of strong negative sentiment"""
        text = "Terrible and awful! Worst product ever! Avoid!"
        result = self.analyzer._analyze_text_sentiment(text)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['label'], 'Negative')
        self.assertGreater(result['strength'], 0.7)
    
    def test_neutral_sentiment(self):
        """Test detection of neutral sentiment"""
        text = "The product is okay and nothing special."
        result = self.analyzer._analyze_text_sentiment(text)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['label'], 'Neutral')
    
    def test_mixed_sentiment_analysis(self):
        """Test sentiment analysis with mixed content"""
        text = "Great design but terrible performance."
        has_mixed = self.analyzer._has_mixed_sentiment(text)
        
        self.assertTrue(has_mixed)


def run_tests(verbosity=2):
    """Run all tests and return results"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestConflictDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestConflictReasoning))
    suite.addTests(loader.loadTestsFromTestCase(TestLabelResolution))
    suite.addTests(loader.loadTestsFromTestCase(TestDataPersistence))
    suite.addTests(loader.loadTestsFromTestCase(TestReportGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestSentimentAnalysis))
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    return runner.run(suite)


if __name__ == '__main__':
    unittest.main()
