"""
Multi-Annotator Conflict Detection and Resolution System

This module provides comprehensive analysis of disagreements between annotators
in labeled datasets, including conflict detection, reasoning, and resolution.
"""

import json
import logging
from typing import List, Dict, Any, Tuple, Optional
from collections import Counter
from dataclasses import dataclass, asdict
from enum import Enum


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SentimentStrength(Enum):
    """Sentiment intensity indicators"""
    STRONG_POSITIVE = 0.9
    POSITIVE = 0.7
    NEUTRAL = 0.5
    NEGATIVE = -0.7
    STRONG_NEGATIVE = -0.9


@dataclass
class AnnotationResult:
    """Result structure for analyzed annotation"""
    id: int
    text: str
    labels: List[Dict[str, str]]
    is_conflict: bool
    conflict_reason: Optional[str]
    suggested_label: str
    confidence: float
    reasoning: str
    annotation_distribution: Dict[str, int]


class ConflictAnalyzer:
    """Main class for detecting and analyzing annotation conflicts"""

    # Keyword mappings for sentiment analysis
    STRONG_POSITIVE_KEYWORDS = {
        'excellent', 'amazing', 'fantastic', 'love', 'loved', 'perfect',
        'highly recommend', 'outstanding', 'wonderful', 'great', 'excellent',
        'fantastic', 'exceptional', 'impressive', 'reliable', 'comfortable',
        'powerful', 'lightweight', 'smooth', 'fast', 'easy', 'helpful',
        'responsive', 'breathable', 'durable', 'elegant', 'ergo', 'quiet'
    }

    POSITIVE_KEYWORDS = {
        'good', 'nice', 'well', 'works', 'fine', 'okay', 'met', 'stitching',
        'quality', 'value', 'beautiful', 'comfortable', 'easy', 'clean'
    }

    STRONG_NEGATIVE_KEYWORDS = {
        'worst', 'terrible', 'awful', 'horrible', 'destroyed', 'broken',
        'damaged', 'hate', 'hated', 'never', 'avoid', 'regret', 'extremely',
        'poor', 'distorted', 'unstable', 'dangerous', 'painful'
    }

    NEGATIVE_KEYWORDS = {
        'bad', 'wrong', 'issue', 'problem', 'late', 'slow', 'rude', 'disappoint',
        'cheap', 'breaks', 'broke', 'shrunk', 'irritation', 'overpriced',
        'drains', 'overheats', 'bends', 'stopped', 'stopped working'
    }

    NEUTRAL_INDICATORS = {
        'okay', 'fine', 'average', 'normal', 'nothing special', 'nothing wrong',
        'i guess', 'decent', 'basic', 'meets', 'reasonable', 'neither'
    }

    AMBIGUOUS_INDICATORS = {
        'liked some', 'disliked others', 'but', 'however', 'although',
        'despite', 'both', 'depends', 'luck', 'could improve', 'not bad',
        'somewhat', 'part', 'polite but', 'clean but', 'good but'
    }

    def __init__(self):
        """Initialize the conflict analyzer"""
        self.analyzed_samples = []
        self.conflict_samples = []

    def detect_conflicts(self, dataset: List[Dict[str, Any]]) -> None:
        """
        Detect conflicts in the dataset and analyze them
        
        Args:
            dataset: List of sample dictionaries with id, text, and labels
        """
        logger.info(f"Starting analysis of {len(dataset)} samples")
        
        for sample in dataset:
            result = self._analyze_sample(sample)
            self.analyzed_samples.append(result)
            
            if result.is_conflict:
                self.conflict_samples.append(result)
                logger.debug(f"Conflict detected in sample {result.id}: {result.conflict_reason}")
        
        logger.info(f"Analysis complete. Found {len(self.conflict_samples)} conflicts out of {len(dataset)} samples")

    def _analyze_sample(self, sample: Dict[str, Any]) -> AnnotationResult:
        """
        Analyze a single sample for conflicts
        
        Args:
            sample: Sample dictionary with id, text, and labels
            
        Returns:
            AnnotationResult with analysis details
        """
        sample_id = sample['id']
        text = sample['text']
        labels = sample['labels']
        
        # Extract labels from annotators
        annotator_labels = {label['annotator']: label['label'] for label in labels}
        
        # Check for conflicts
        unique_labels = set(annotator_labels.values())
        is_conflict = len(unique_labels) > 1
        
        # Count label distribution
        label_distribution = Counter(annotator_labels.values())
        
        # Get conflict reason and suggested label
        conflict_reason = None
        suggested_label, confidence, reasoning = self._resolve_conflict(
            text=text,
            annotator_labels=annotator_labels,
            label_distribution=label_distribution,
            is_conflict=is_conflict
        )
        
        if is_conflict:
            conflict_reason = self._explain_conflict(text, annotator_labels, label_distribution)
        
        return AnnotationResult(
            id=sample_id,
            text=text,
            labels=labels,
            is_conflict=is_conflict,
            conflict_reason=conflict_reason,
            suggested_label=suggested_label,
            confidence=confidence,
            reasoning=reasoning,
            annotation_distribution=dict(label_distribution)
        )

    def _explain_conflict(
        self,
        text: str,
        annotator_labels: Dict[str, str],
        label_distribution: Counter
    ) -> str:
        """
        Explain the reason for annotation conflict
        
        Args:
            text: The text being annotated
            annotator_labels: Dictionary of annotator -> label mappings
            label_distribution: Counter of label frequencies
            
        Returns:
            Explanation string
        """
        reasons = []
        
        # Check for mixed sentiment
        if self._has_mixed_sentiment(text):
            reasons.append("Mixed sentiment detected - text contains both positive and negative aspects")
        
        # Check for ambiguous language
        if self._has_ambiguous_language(text):
            reasons.append("Ambiguous language - statements could be interpreted multiple ways")
        
        # Check for neutral with strong opinions
        if "Neutral" in annotator_labels.values():
            positive_count = sum(1 for l in annotator_labels.values() if l == "Positive")
            negative_count = sum(1 for l in annotator_labels.values() if l == "Negative")
            
            if positive_count > 0 and negative_count == 0:
                reasons.append("Disagreement on intensity - some view as positive, others as neutral/moderate")
            elif negative_count > 0 and positive_count == 0:
                reasons.append("Disagreement on intensity - some view as negative, others as neutral/moderate")
        
        # Check for context-dependent interpretation
        if self._is_context_dependent(text):
            reasons.append("Context-dependent interpretation - meaning relies on prior experience or expectations")
        
        # Check for subjective evaluation
        if self._is_subjective(text):
            reasons.append("Subjective evaluation - personal preferences influence rating")
        
        # Multi-aspect evaluation
        if self._has_multiple_aspects(text):
            reasons.append("Multi-aspect evaluation - text covers multiple features with varying quality")
        
        return " | ".join(reasons) if reasons else "Unclear reason for disagreement"

    def _resolve_conflict(
        self,
        text: str,
        annotator_labels: Dict[str, str],
        label_distribution: Counter,
        is_conflict: bool
    ) -> Tuple[str, float, str]:
        """
        Resolve conflict and suggest final label
        
        Args:
            text: The text being annotated
            annotator_labels: Dictionary of annotator -> label mappings
            label_distribution: Counter of label frequencies
            is_conflict: Whether a conflict exists
            
        Returns:
            Tuple of (suggested_label, confidence, reasoning)
        """
        if not is_conflict:
            # No conflict - use unanimous label
            majority_label = label_distribution.most_common(1)[0][0]
            confidence = 1.0
            reasoning = f"Unanimous agreement among {len(annotator_labels)} annotators"
            return majority_label, confidence, reasoning
        
        # Conflict resolution strategy:
        # 1. Check for ambiguous/mixed sentiment in text
        # 2. Use weighted voting based on text analysis
        # 3. Apply confidence-based reasoning
        
        # Analyze text for sentiment strength
        text_sentiment = self._analyze_text_sentiment(text)
        
        # Get majority label
        majority_label, majority_count = label_distribution.most_common(1)[0]
        total_annotators = len(annotator_labels)
        agreement_ratio = majority_count / total_annotators
        
        # If strong majority (>50% but less than unanimous), use it
        if agreement_ratio > 0.5:
            confidence = agreement_ratio
            reasoning = f"Majority vote ({majority_count}/{total_annotators} annotators agreed on '{majority_label}')"
            
            # Adjust reasoning based on text analysis
            if self._has_mixed_sentiment(text):
                reasoning += "; text contains mixed sentiment but majority view prevails"
                confidence *= 0.85
            elif self._has_ambiguous_language(text):
                reasoning += "; ambiguous language but majority interpretation preferred"
                confidence *= 0.9
        else:
            # Tie or balanced disagreement - use text analysis
            if text_sentiment:
                suggested_label = text_sentiment['label']
                confidence = text_sentiment['strength']
                reasoning = f"Equal disagreement; suggestion based on text sentiment analysis: {text_sentiment['explanation']}"
            else:
                # Fallback to majority
                suggested_label = majority_label
                confidence = agreement_ratio
                reasoning = "Balanced disagreement; resolved using majority vote as fallback"
                return suggested_label, confidence, reasoning
        
        return majority_label, confidence, reasoning

    def _analyze_text_sentiment(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Analyze sentiment from the text itself
        
        Args:
            text: The text to analyze
            
        Returns:
            Dictionary with label, strength, and explanation or None
        """
        text_lower = text.lower()
        
        # Count keyword matches
        strong_pos_count = sum(1 for kw in self.STRONG_POSITIVE_KEYWORDS if kw in text_lower)
        pos_count = sum(1 for kw in self.POSITIVE_KEYWORDS if kw in text_lower)
        strong_neg_count = sum(1 for kw in self.STRONG_NEGATIVE_KEYWORDS if kw in text_lower)
        neg_count = sum(1 for kw in self.NEGATIVE_KEYWORDS if kw in text_lower)
        neutral_count = sum(1 for kw in self.NEUTRAL_INDICATORS if kw in text_lower)
        ambiguous_count = sum(1 for kw in self.AMBIGUOUS_INDICATORS if kw in text_lower)
        
        # Calculate sentiment score
        sentiment_score = (
            strong_pos_count * 2 + pos_count * 1 - 
            strong_neg_count * 2 - neg_count * 1
        )
        
        # Adjust for neutral and ambiguous indicators
        if neutral_count > 0:
            sentiment_score = sentiment_score * 0.5
        if ambiguous_count > 0:
            sentiment_score = sentiment_score * 0.7
        
        # Determine final sentiment
        if sentiment_score > 1:
            return {
                'label': 'Positive',
                'strength': min(0.95, 0.7 + (strong_pos_count / 10)),
                'explanation': f"Text contains {strong_pos_count} strong positive and {pos_count} positive indicators"
            }
        elif sentiment_score < -1:
            return {
                'label': 'Negative',
                'strength': min(0.95, 0.7 + (strong_neg_count / 10)),
                'explanation': f"Text contains {strong_neg_count} strong negative and {neg_count} negative indicators"
            }
        elif neutral_count > 0 or (abs(sentiment_score) <= 1 and (pos_count > 0 or neg_count > 0)):
            return {
                'label': 'Neutral',
                'strength': 0.65,
                'explanation': "Text shows neutral or balanced sentiment"
            }
        
        return None

    def _has_mixed_sentiment(self, text: str) -> bool:
        """Check if text contains mixed positive and negative sentiment"""
        text_lower = text.lower()
        has_positive = any(kw in text_lower for kw in self.STRONG_POSITIVE_KEYWORDS | self.POSITIVE_KEYWORDS)
        has_negative = any(kw in text_lower for kw in self.STRONG_NEGATIVE_KEYWORDS | self.NEGATIVE_KEYWORDS)
        return has_positive and has_negative

    def _has_ambiguous_language(self, text: str) -> bool:
        """Check if text uses ambiguous language"""
        text_lower = text.lower()
        return any(kw in text_lower for kw in self.AMBIGUOUS_INDICATORS)

    def _is_context_dependent(self, text: str) -> bool:
        """Check if meaning is context-dependent"""
        indicators = {'depends', 'luck', 'expected', 'normal', 'advertised', 'luck', 'after', 'before'}
        return any(indicator in text.lower() for indicator in indicators)

    def _is_subjective(self, text: str) -> bool:
        """Check if evaluation is subjective"""
        subjective_phrases = {
            'love', 'like', 'dislike', 'prefer', 'think', 'feel', 'opinion',
            'satisfied', 'disappointed', 'expect', 'hope', 'personally', 'truly'
        }
        return any(phrase in text.lower() for phrase in subjective_phrases)

    def _is_context_dependent(self, text: str) -> bool:
        """Check if meaning is context-dependent"""
        indicators = {'depends', 'luck', 'expected', 'normal', 'advertised'}
        return any(indicator in text.lower() for indicator in indicators)

    def _has_multiple_aspects(self, text: str) -> bool:
        """Check if text evaluates multiple aspects"""
        aspect_words = {'design', 'performance', 'quality', 'price', 'packaging', 'battery', 
                       'camera', 'microphone', 'speaker', 'display', 'battery', 'size', 
                       'weight', 'comfort', 'durability', 'ui', 'usability', 'support', 
                       'delivery', 'shipping'}
        return sum(1 for aspect in aspect_words if aspect in text.lower()) >= 2

    def get_conflict_report(self) -> Dict[str, Any]:
        """
        Generate a summary report of conflict analysis
        
        Returns:
            Dictionary with summary statistics
        """
        if not self.analyzed_samples:
            return {}
        
        total_samples = len(self.analyzed_samples)
        conflict_count = len(self.conflict_samples)
        conflict_percentage = (conflict_count / total_samples * 100) if total_samples > 0 else 0
        
        # Analyze conflict reasons
        conflict_reasons = {}
        for sample in self.conflict_samples:
            if sample.conflict_reason:
                # Parse multiple reasons separated by |
                for reason in sample.conflict_reason.split('|'):
                    reason = reason.strip()
                    conflict_reasons[reason] = conflict_reasons.get(reason, 0) + 1
        
        # Calculate annotator agreement statistics
        annotator_agreement = self._calculate_annotator_agreement()
        
        return {
            'total_samples': total_samples,
            'conflicted_samples': conflict_count,
            'conflict_percentage': round(conflict_percentage, 2),
            'top_conflict_reasons': sorted(
                conflict_reasons.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            'annotator_agreement': annotator_agreement,
            'average_confidence': round(
                sum(s.confidence for s in self.analyzed_samples) / len(self.analyzed_samples),
                3
            )
        }

    def _calculate_annotator_agreement(self) -> Dict[str, float]:
        """Calculate pairwise agreement between annotators"""
        annotators = set()
        for sample in self.analyzed_samples:
            for label in sample.labels:
                annotators.add(label['annotator'])
        
        annotator_pairs = {}
        for sample in self.analyzed_samples:
            labels_dict = {label['annotator']: label['label'] for label in sample.labels}
            annotator_list = list(labels_dict.items())
            
            for i in range(len(annotator_list)):
                for j in range(i + 1, len(annotator_list)):
                    ann1, label1 = annotator_list[i]
                    ann2, label2 = annotator_list[j]
                    pair_key = tuple(sorted([ann1, ann2]))
                    
                    if pair_key not in annotator_pairs:
                        annotator_pairs[pair_key] = {'agree': 0, 'total': 0}
                    
                    annotator_pairs[pair_key]['total'] += 1
                    if label1 == label2:
                        annotator_pairs[pair_key]['agree'] += 1
        
        agreement_stats = {}
        for pair, counts in annotator_pairs.items():
            agreement = counts['agree'] / counts['total'] if counts['total'] > 0 else 0
            pair_key = f"{pair[0]}-{pair[1]}"
            agreement_stats[pair_key] = round(agreement, 3)
        
        return agreement_stats

    def export_results(self, output_file: str = 'conflict_analysis_results.jsonl') -> None:
        """
        Export analyzed results to JSONL file
        
        Args:
            output_file: Output file path
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            for result in self.analyzed_samples:
                output_dict = {
                    'id': result.id,
                    'text': result.text,
                    'labels': result.labels,
                    'is_conflict': result.is_conflict,
                    'conflict_reason': result.conflict_reason,
                    'suggested_label': result.suggested_label,
                    'confidence': result.confidence,
                    'reasoning': result.reasoning,
                    'annotation_distribution': result.annotation_distribution
                }
                f.write(json.dumps(output_dict, ensure_ascii=False) + '\n')
        
        logger.info(f"Results exported to {output_file}")

    def export_conflicts_only(self, output_file: str = 'conflicts_only.jsonl') -> None:
        """
        Export only conflicted samples to a separate file
        
        Args:
            output_file: Output file path
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            for result in self.conflict_samples:
                output_dict = {
                    'id': result.id,
                    'text': result.text,
                    'labels': result.labels,
                    'is_conflict': result.is_conflict,
                    'conflict_reason': result.conflict_reason,
                    'suggested_label': result.suggested_label,
                    'confidence': result.confidence,
                    'reasoning': result.reasoning,
                    'annotation_distribution': result.annotation_distribution
                }
                f.write(json.dumps(output_dict, ensure_ascii=False) + '\n')
        
        logger.info(f"Conflict samples exported to {output_file}")
