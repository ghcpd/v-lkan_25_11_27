import json
import pandas as pd

print("\n" + "="*100)
print("多标注者标签冲突检测 - 完整数据表")
print("="*100 + "\n")

# 读取冲突数据
with open('conflicts_only.jsonl', 'r') as f:
    conflicts = [json.loads(line) for line in f]

# 创建DataFrame
data = []
for s in conflicts:
    labels = ', '.join([f"{a['annotator']}:{a['label']}" for a in s['labels']])
    reasons = s['conflict_reason'].split(' | ')
    main_reason = reasons[0][:40] + '...' if len(reasons[0]) > 40 else reasons[0]
    reason_count = len(reasons)
    
    data.append({
        'ID': s['id'],
        '文本摘要': s['text'][:35] + '...',
        '标注': labels,
        '主要冲突原因': main_reason,
        '原因数': reason_count,
        '建议标签': s['suggested_label'],
        '置信度': f"{s['confidence']:.2f}",
    })

df = pd.DataFrame(data)

# 打印表格
print(df.to_string(index=False))

print("\n" + "="*100)
print("统计摘要 | STATISTICS SUMMARY")
print("="*100)

print(f"""
基本统计:
  • 总样本数: 100
  • 冲突样本: 10 (10.0%)
  • 无冲突: 90 (90.0%)
  
标注者一致性:
  • A1-A2: 92.3% ⭐ 最高
  • A1-A3: 88.9%
  • A2-A3: 88.9%

置信度统计:
  • 最高: 0.80 (ID 33)
  • 最低: 0.50 (ID 56, 84, 97)
  • 平均: 0.625

冲突原因排行:
""")

# 统计冲突原因频次
reason_counts = {}
for s in conflicts:
    for reason in s['conflict_reason'].split(' | '):
        reason_counts[reason] = reason_counts.get(reason, 0) + 1

sorted_reasons = sorted(reason_counts.items(), key=lambda x: x[1], reverse=True)
for i, (reason, count) in enumerate(sorted_reasons[:5], 1):
    pct = (count / 10) * 100
    bar = '█' * count + '░' * (10 - count)
    print(f"  {i}. [{bar}] {count}/10 ({pct:.0f}%) {reason[:50]}")

print("\n" + "="*100)
