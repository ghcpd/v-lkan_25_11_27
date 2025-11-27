# Quick Start Guide - Multi-Annotator Conflict Detection System

## 🚀 30-Second Setup

### Windows
```cmd
setup.bat
# Enter 1 for local Python, or 3 for Docker + Python
venv\Scripts\activate.bat
python main.py text_label.jsonl
```

### Unix/Linux/Mac
```bash
chmod +x setup.sh run_tests.sh
./setup.sh
# Enter 2 for local Python, or 3 for Docker + Python
source venv/bin/activate
python main.py text_label.jsonl
```

### Docker (All Platforms)
```bash
./setup.sh  # or setup.bat on Windows
docker run -v $(pwd)/output:/app/output conflict-detection-system:latest main.py text_label.jsonl
```

---

## 📖 Usage Examples

### 1. Basic Analysis
```bash
python main.py text_label.jsonl
```
**Outputs**: `conflict_analysis_results.jsonl`, `conflict_report.json`

### 2. Export Conflicts Only
```bash
python main.py text_label.jsonl --conflicts-only
```
**Outputs**: `conflicts_only.jsonl`, `conflict_report.json`

### 3. Custom Output Files
```bash
python main.py text_label.jsonl \
    --output my_results.jsonl \
    --report my_report.json \
    --conflicts-only
```

### 4. Verbose Output
```bash
python main.py text_label.jsonl --verbose
```

---

## 🧪 Run Tests

### Unix/Linux/Mac
```bash
./run_tests.sh
# Choose option 4 for all tests
```

### Windows
```cmd
run_tests.bat
# Choose option 3 for all tests
```

### Expected Output
```
.............................................
Ran 42 tests in 0.456s

OK

Test reports available in: test_reports/
```

---

## 📊 Understanding the Output

### Results File (JSONL)
Each line is a JSON object with:
```json
{
  "id": 1,
  "text": "Great service!",
  "labels": [...],           // Original annotator labels
  "is_conflict": false,      // true if annotators disagreed
  "conflict_reason": null,   // Why they disagreed (if conflict)
  "suggested_label": "Positive",  // Recommended final label
  "confidence": 1.0,         // Confidence (0.0-1.0)
  "reasoning": "Unanimous agreement among 2 annotators",
  "annotation_distribution": {"Positive": 2}  // Label counts
}
```

### Report File (JSON)
```json
{
  "total_samples": 100,
  "conflicted_samples": 13,
  "conflict_percentage": 13.0,
  "annotator_agreement": {
    "A1-A2": 0.95,
    "A1-A3": 0.88,
    "A2-A3": 0.92
  },
  "average_confidence": 0.92,
  "top_conflict_reasons": [...]
}
```

---

## 🔧 Customization

### Change Sentiment Keywords
Edit `analyzer.py`:
```python
STRONG_POSITIVE_KEYWORDS = {
    'excellent', 'amazing', 'fantastic',
    # Add your custom keywords
}
```

### Add Custom Conflict Detection
Edit `analyzer.py`, method `_explain_conflict()`:
```python
if self._is_your_pattern(text):
    reasons.append("Your custom conflict reason")
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'analyzer'` | Run `pip install -r requirements.txt` |
| `FileNotFoundError` | Use absolute path: `python main.py /path/to/file.jsonl` |
| `Permission denied setup.sh` | Run: `chmod +x setup.sh run_tests.sh` |
| Docker build fails | Run: `docker system prune` then rebuild |
| Out of memory | Use smaller dataset or process in batches |

---

## 📈 Performance Tips

- **Small datasets** (< 1000): Use local Python
- **Medium datasets** (1000-10000): Use Docker or Python with batch processing
- **Large datasets** (> 10000): Consider implementing batch processing in `main.py`

---

## 📚 Learn More

- Full documentation: See `README.md`
- Implementation details: See `IMPLEMENTATION_SUMMARY.md`
- API reference: Check docstrings in `analyzer.py`
- Test examples: Review `test_conflict_detection.py`

---

## ✅ Validation Checklist

- [ ] Setup script ran successfully
- [ ] Tests pass (42/42)
- [ ] Can run: `python main.py text_label.jsonl`
- [ ] Output files created (`results.jsonl`, `report.json`)
- [ ] Results are valid JSON/JSONL

---

## 💡 Next Steps

1. **Try with your data**: Replace `text_label.jsonl` with your dataset
2. **Customize analysis**: Edit sentiment keywords and conflict rules
3. **Automate**: Add to your pipeline with Docker
4. **Integrate**: Use the analyzer as a library in your code:
   ```python
   from analyzer import ConflictAnalyzer
   
   analyzer = ConflictAnalyzer()
   analyzer.detect_conflicts(your_dataset)
   report = analyzer.get_conflict_report()
   ```

---

## 📞 Support

- **Issues**: Check `README.md` Troubleshooting section
- **Enhancement requests**: Extend the analyzer methods
- **Questions**: Review code docstrings and comments

---

**Version**: 1.0.0  
**Ready to use!** ✨
