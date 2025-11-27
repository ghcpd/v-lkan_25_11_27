import json
import sys

i = sys.argv[1] if len(sys.argv) > 1 else 'conflicts_output.jsonl'
count = 0
with open(i, 'r', encoding='utf-8') as f:
    for line in f:
        if not line.strip():
            continue
        obj = json.loads(line)
        if obj.get('is_conflict'):
            count += 1
            print('-'*80)
            print(json.dumps({
                'id': obj['id'],
                'text': obj['text'],
                'labels': obj['labels'],
                'conflict_reason': obj['conflict_reason'],
                'suggested_label': obj['suggested_label'],
                'suggestion_confidence': obj.get('suggestion_confidence'),
                'suggestion_explanation': obj.get('suggestion_explanation')
            }, ensure_ascii=False, indent=2))
print('\nTotal conflicts:', count)
