"""
Conflict detection and resolution for multi-annotator datasets.
Usage: python analyzer/analyze_conflicts.py --input text_label.jsonl --out_conflicts conflicts.jsonl --out_resolved resolved_labels.jsonl

Outputs:
- conflicts.jsonl: samples where annotators disagree, includes analysis and suggested_label
- resolved_labels.jsonl: all samples with final suggested_label and analysis
"""

import json
import argparse
from collections import Counter, defaultdict
from pathlib import Path
import re

POSITIVE_WORDS = set([
    'excellent', 'great', 'amazing', 'loved', 'love', 'loves', 'good', 'good', 'fantastic', 'best', 'perfect', 'satisfied',
    'comfortable', 'reliable', 'impressive', 'high', 'highly', 'recommend', 'responsive', 'smooth', 'works'
])
NEGATIVE_WORDS = set([
    'terrible', 'worst', 'disappointed', 'bad', 'not', "didn't", 'rude', 'overheats', 'crashes', 'broke', 'broken', 'cheap', 'poor', 'hate', 'hated', 'slow', 'long', 'too', 'smell', 'shrank', 'shrunk'
])

NEUTRAL_WORDS = set(['okay', 'fine', 'average', 'normal', "just fine", 'neutral', 'decent', 'basic', 'nothing special'])

CONTRAST_WORDS = set(['but', 'however', 'although', 'though'])

LABELS = ['Positive', 'Negative', 'Neutral']


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', default='text_label.jsonl')
    parser.add_argument('--out_conflicts', '-oc', default='conflict_samples.jsonl')
    parser.add_argument('--out_resolved', '-or', default='resolved_labels.jsonl')
    return parser.parse_args()


def tokenize(text):
    # Simple tokenization lower-case words
    text = re.sub(r"[^A-Za-z0-9' ]+", ' ', text)
    return [t.lower() for t in text.split() if t]


def detect_conflict(labels):
    unique_labels = set([l['label'] for l in labels])
    return len(unique_labels) > 1


def detect_conflict_reason(text, labels):
    # Heuristics:
    # - Mixed sentiment clues in text (contrast words -> mixed aspects)
    # - Short or ambiguous text -> unclear
    # - Presence of multiple label types -> disagreement
    tokens = tokenize(text)
    token_set = set(tokens)

    label_set = set([l['label'] for l in labels])
    if not labels:
        return 'no_labels'

    if len(label_set) == 1:
        return None

    reasons = []
    # Mixed aspect: presence of 'but', 'however' or sentiment words on both sides
    if token_set & CONTRAST_WORDS:
        reasons.append('mixed_sentiment_or_aspects (contrast words present)')

    pos_count = len([w for w in tokens if w in POSITIVE_WORDS])
    neg_count = len([w for w in tokens if w in NEGATIVE_WORDS])
    neutral_count = len([w for w in tokens if w in NEUTRAL_WORDS])

    if pos_count and neg_count:
        reasons.append('mixed_sentiment_words')

    if neutral_count and (pos_count or neg_count):
        reasons.append('neutral_annotator_misalignment')

    # Ambiguous text (short or hedging words)
    if len(tokens) <= 3 or any(w in tokens for w in ('maybe', 'guess', 'think', 'I guess', 'I think', 'could')):
        reasons.append('ambiguous_or_short_text')

    # Multi-aspect evaluation due to presence of multiple clauses / punctuation
    if ',' in text or ';' in text or len(text.split('.')) > 1:
        if pos_count and neg_count:
            reasons.append('multi_aspect')

    # unclear policy if one annotator uses Neutral while another uses Positive/Negative often occurs
    # We'll set 'unclear_policy' when neutral is present with others
    if 'Neutral' in label_set and (('Positive' in label_set) or ('Negative' in label_set)):
        reasons.append('unclear_annotation_policy regarding Neutrality')

    if not reasons:
        # fallback generic
        reasons.append('annotator_disagreement; no linguistic cues')

    return '; '.join(reasons)


def suggest_label(text, labels):
    # Rule-based suggestion with confidence reasoning
    counts = Counter([l['label'] for l in labels])
    total = sum(counts.values())
    majority_label, majority_count = counts.most_common(1)[0]

    tokens = tokenize(text)
    pos_count = len([w for w in tokens if w in POSITIVE_WORDS])
    neg_count = len([w for w in tokens if w in NEGATIVE_WORDS])
    neutral_count = len([w for w in tokens if w in NEUTRAL_WORDS])

    # Confidence calculation base on majority ratio
    maj_ratio = majority_count / total
    base_confidence = maj_ratio

    # Adjust with lexical cues
    lexical_score = 0
    if pos_count > neg_count:
        lexical_score = 0.2 * min(1, pos_count / max(1, neg_count + 1))
    elif neg_count > pos_count:
        lexical_score = -0.2 * min(1, neg_count / max(1, pos_count + 1))

    # If lexical_score contradicts majority, reduce confidence
    if (lexical_score > 0 and majority_label == 'Negative') or (lexical_score < 0 and majority_label == 'Positive'):
        confidence = max(0.4, base_confidence - 0.2)
    else:
        confidence = min(0.98, base_confidence + abs(lexical_score))

    # Tiebreakers
    if len([l for l in counts if counts[l] == majority_count]) > 1:
        # tie; apply lexical evidence
        if pos_count > neg_count:
            final = 'Positive'
        elif neg_count > pos_count:
            final = 'Negative'
        else:
            final = 'Neutral'
        reason = f'tie_breaker_lexical: pos_count={pos_count}, neg_count={neg_count}, neutral_count={neutral_count}'
    else:
        final = majority_label
        reason = 'majority_vote'

    # If text contains contrast words, lower confidence
    if set(tokenize(text)) & CONTRAST_WORDS:
        confidence = min(confidence, 0.6)
        reason += '; contrast_words_lower_confidence'

    return final, round(confidence, 2), reason


def analyze_file(input_path, out_conflicts, out_resolved):
    in_path = Path(input_path)
    if not in_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    conflicts = []
    resolved = []

    with in_path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            rec_labels = rec.get('labels', [])
            is_conflict = detect_conflict(rec_labels)

            reason = detect_conflict_reason(rec['text'], rec_labels) if is_conflict else None
            suggested, confidence, suggest_reason = suggest_label(rec['text'], rec_labels)

            out_rec = {
                'id': rec.get('id'),
                'text': rec.get('text'),
                'labels': rec_labels,
                'is_conflict': is_conflict,
                'conflict_reason': reason,
                'suggested_label': {
                    'label': suggested,
                    'confidence': confidence,
                    'explanation': suggest_reason
                }
            }
            if is_conflict:
                conflicts.append(out_rec)
            resolved.append(out_rec)

    # write files
    with open(out_conflicts, 'w', encoding='utf-8') as f:
        for c in conflicts:
            f.write(json.dumps(c, ensure_ascii=False) + '\n')

    with open(out_resolved, 'w', encoding='utf-8') as f:
        for r in resolved:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

    print(f"Wrote {len(conflicts)} conflicts to {out_conflicts}")
    print(f"Wrote {len(resolved)} resolved records to {out_resolved}")


if __name__ == '__main__':
    args = parse_args()
    analyze_file(args.input, args.out_conflicts, args.out_resolved)
