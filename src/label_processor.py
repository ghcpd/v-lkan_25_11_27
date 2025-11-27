import json
import logging
import time
import traceback
from pathlib import Path
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from collections import Counter


class LabelProcessor:
    def __init__(self, input_path):
        self.input_path = Path(input_path)
        self.analyzer = SentimentIntensityAnalyzer()
        self.logger = None

    def load(self):
        data = []
        with open(self.input_path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                data.append(json.loads(line))
        return data

    def majority_label(self, labels):
        # labels is list of dicts {annotator:..., label:...}
        counts = Counter([l['label'] for l in labels])
        most_common = counts.most_common()
        if len(most_common) == 0:
            return None, {}
        top_count = most_common[0][1]
        top_labels = [label for label, count in most_common if count == top_count]
        # if tie, return list
        if len(top_labels) == 1:
            return top_labels[0], counts
        else:
            return top_labels, counts

    def sentiment_guess(self, text):
        s = self.analyzer.polarity_scores(text)
        compound = s['compound']
        if compound >= 0.5:
            guess = 'Positive'
        elif compound <= -0.5:
            guess = 'Negative'
        else:
            guess = 'Neutral'
        return guess, s

    def conflict_reasoner(self, text, labels, sentiment_scores, majority):
        # Several heuristics to detect reason for conflict
        reasons = []
        label_set = set([l['label'] for l in labels])
        text_lower = text.lower()
        # mixed sentiment words
        if any(x in text_lower for x in ["but", "however", "although", "though", "but still"]):
            reasons.append('Multi-aspect / contradictory clauses')
        # ambiguous or mild sentiment
        compound = sentiment_scores['compound']
        if abs(compound) < 0.25:
            reasons.append('Ambiguous or weak sentiment')
        # polarized labeling (Positive vs Negative)
        if 'Positive' in label_set and 'Negative' in label_set:
            reasons.append('Polarized annotator opinions (strong positive vs negative words)')
        # positive vs neutral
        if 'Positive' in label_set and 'Neutral' in label_set and 'Negative' not in label_set:
            reasons.append('Mild positive language interpreted differently (neutral vs positive)')
        # negative vs neutral
        if 'Negative' in label_set and 'Neutral' in label_set and 'Positive' not in label_set:
            reasons.append('Mild negative language or phrasing ambiguity')
        # if annotators disagree significantly (e.g., 2 categories present)
        if len(label_set) > 1 and len(reasons) == 0:
            reasons.append('Annotator inconsistency - possible policy misinterpretation or missing context')

        if len(reasons) == 0:
            return None
        return '; '.join(reasons)

    def resolve_suggested_label(self, text, labels):
        maj_label, counts = self.majority_label(labels)
        sentiment_label, scores = self.sentiment_guess(text)
        # Flatten majority label when tie
        maj_label_resolved = maj_label if isinstance(maj_label, str) else None
        # Decide final suggestion
        # If no maj_label (unlikely), use sentiment
        confidence = 0.0
        if isinstance(maj_label, str):
            total = sum(counts.values())
            majority_ratio = counts[maj_label] / total
            # base confidence on majority ratio and sentiment agreement
            agree = 1 if maj_label == sentiment_label else 0
            confidence = 0.6 * majority_ratio + 0.4 * agree
            suggested = maj_label
        else:
            # tie: use sentiment, otherwise default to 'Neutral'
            suggested = sentiment_label if sentiment_label is not None else 'Neutral'
            # small heuristics
            confidence = 0.5

        # Build explanation string
        explanation_parts = []
        explanation_parts.append(f"Majority: {maj_label}")
        explanation_parts.append(f"Sentiment_guess: {sentiment_label} (compound={scores['compound']:.3f})")
        explanation_parts.append(f"Confidence_score: {confidence:.2f}")

        explanation = '; '.join(explanation_parts)
        return suggested, round(confidence, 3), explanation

    def process(self, output_path=None):
        start_time = time.time()
        if self.logger:
            self.logger.info('Starting processing')
        data = self.load()
        results = []
        for entry in data:
            if self.logger:
                self.logger.debug(f"Processing id={entry.get('id')}: text='{entry.get('text')}'")
            entry_meta = {
                'id': entry.get('id'),
                'text': entry.get('text'),
                'labels': entry.get('labels', [])
            }
            labels = entry_meta['labels']
            unique_labels = set([l['label'] for l in labels])
            is_conflict = len(unique_labels) > 1
            sentiment_label, sentiment_scores = self.sentiment_guess(entry_meta['text'])
            maj_label, counts = self.majority_label(labels)
            conflict_reason = None
            suggested_label = None
            suggestion_explanation = None
            if is_conflict:
                conflict_reason = self.conflict_reasoner(entry_meta['text'], labels, sentiment_scores, maj_label)
                suggested_label, conf_score, suggestion_explanation = self.resolve_suggested_label(entry_meta['text'], labels)
                if self.logger:
                    self.logger.debug(f"id={entry_meta['id']} conflict_reason={conflict_reason}")
                    self.logger.debug(f"id={entry_meta['id']} suggested={suggested_label} confidence={conf_score}")
            else:
                # No conflict - just confirm the label and provide explanation
                suggested_label = list(unique_labels)[0] if len(unique_labels) == 1 else None
                conf_score = 1.0
                suggestion_explanation = f"No conflict; unanimous label {suggested_label}. Sentiment_guess: {sentiment_label}"

            results.append({
                'id': entry_meta['id'],
                'text': entry_meta['text'],
                'labels': entry_meta['labels'],
                'is_conflict': is_conflict,
                'conflict_reason': conflict_reason,
                'suggested_label': suggested_label,
                'suggestion_confidence': conf_score,
                'suggestion_explanation': suggestion_explanation
            })

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as of:
                for r in results:
                    of.write(json.dumps(r, ensure_ascii=False) + '\n')
        if self.logger:
            elapsed = time.time() - start_time
            self.logger.info(f'Finished processing {len(results)} samples in {elapsed:.2f}s')
        return results


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Process multi-annotator JSONL and detect conflicts.')
    parser.add_argument('--input', '-i', type=str, default='text_label.jsonl')
    parser.add_argument('--output', '-o', type=str, default='conflicts_output.jsonl')
    parser.add_argument('--log-file', type=str, default=None, help='Optional log file path')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging (DEBUG)')
    args = parser.parse_args()
    proc = LabelProcessor(args.input)
    # setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = logging.getLogger('label_processor')
    logger.setLevel(log_level)
    # format and handlers
    fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    sh = logging.StreamHandler()
    sh.setLevel(log_level)
    sh.setFormatter(fmt)
    logger.handlers = []
    logger.addHandler(sh)
    if args.log_file:
        fh = logging.FileHandler(args.log_file, encoding='utf-8')
        fh.setLevel(log_level)
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    proc.logger = logger
    res = proc.process(args.output)
    print(f"Processed {len(res)} samples; output written to {args.output}")
