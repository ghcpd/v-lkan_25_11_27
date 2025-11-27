# Architecture & Design Documentation

## System Architecture

### Overview Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Input Data (JSONL)                       │
│              Multiple Annotators' Labels                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │   Data Handler (DataHandler)          │
        │  - Load JSONL/JSON files              │
        │  - Parse and validate data            │
        │  - Convert to Python objects          │
        └──────────────────┬───────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │  Conflict Analyzer (ConflictAnalyzer) │
        │  - Detect label conflicts             │
        │  - Analyze disagreement reasons       │
        │  - Suggest final labels               │
        │  - Calculate confidence scores        │
        └──────────────────┬───────────────────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            ▼              ▼              ▼
      ┌─────────┐  ┌─────────┐  ┌──────────────┐
      │ Results │  │  Stats  │  │ Conflict     │
      │ (JSONL) │  │ (JSON)  │  │ Analysis     │
      └─────────┘  └─────────┘  └──────────────┘
            │              │              │
            └──────────────┼──────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │ Report Generator (ReportGenerator)    │
        │  - Generate detailed reports          │
        │  - Create conflict analysis           │
        │  - Compute evaluation metrics         │
        └──────────────────┬───────────────────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            ▼              ▼              ▼
      ┌────────┐  ┌────────┐  ┌────────┐
      │Detailed│  │Conflict│  │Metrics │
      │Report  │  │Report  │  │Report  │
      └────────┘  └────────┘  └────────┘
```

### Component Responsibilities

#### 1. **Data Handler** (`data_handler.py`)
- **Purpose**: Input/Output operations
- **Methods**:
  - `load_jsonl()`: Load JSONL dataset
  - `load_json()`: Load JSON configuration
  - `save_jsonl()`: Save results as JSONL
  - `save_json()`: Save metadata as JSON
- **Dependencies**: None (stdlib only)

#### 2. **Conflict Analyzer** (`conflict_analyzer.py`)
- **Purpose**: Core analysis logic
- **Classes**:
  - `SampleAnalysis`: Dataclass for results
  - `ConflictAnalyzer`: Main analyzer
- **Methods**:
  - `detect_conflict()`: Identify disagreements
  - `analyze_conflict_reason()`: Explain disagreements
  - `suggest_final_label()`: Recommend label
  - `analyze_sample()`: Analyze single sample
  - `analyze_dataset()`: Analyze full dataset
  - `get_statistics()`: Return metrics
- **Key Algorithms**:
  - Majority voting with confidence
  - Text-based sentiment analysis
  - Keyword matching for interpretation

#### 3. **Pipeline** (`pipeline.py`)
- **Purpose**: Orchestrate analysis workflow
- **Class**: `AnalysisPipeline`
- **Workflow**:
  1. Load data from JSONL
  2. Analyze all samples
  3. Extract conflicts
  4. Save results
  5. Generate reports
  6. Compute statistics
- **Features**:
  - Step-by-step execution
  - Comprehensive logging
  - Error handling
  - Command-line interface

#### 4. **Report Generator** (`report_generator.py`)
- **Purpose**: Generate analysis reports
- **Methods**:
  - `generate_detailed_report()`: All samples
  - `generate_conflict_report()`: Conflicts only
  - `generate_metrics_report()`: Statistics
- **Output Format**: Markdown

## Data Flow

```
Sample Input:
{
  "id": 1,
  "text": "Product review text",
  "labels": [
    {"annotator": "A1", "label": "Positive"},
    {"annotator": "A2", "label": "Neutral"}
  ]
}
        │
        ▼
Conflict Detection:
  - Extract unique labels: {Positive, Neutral}
  - Count: 2 unique → IS CONFLICT
        │
        ▼
Reason Analysis:
  - Pattern match: (Positive, Neutral) ∈ PATTERNS
  - Reason: "Mixed signal..."
        │
        ▼
Label Suggestion:
  - Majority vote: Positive=1, Neutral=1 (tie)
  - Text analysis: Find "product" → Neutral
  - Confidence: 50% (tie)
        │
        ▼
Output:
{
  "id": 1,
  "text": "Product review text",
  "labels": [...],
  "is_conflict": true,
  "conflict_reason": "Mixed signal...",
  "suggested_label": "Neutral",
  "confidence": 0.5,
  "analysis_details": {...}
}
```

## Key Algorithms

### 1. Conflict Detection Algorithm

```python
def detect_conflict(labels):
    unique_labels = set(label["label"] for label in labels)
    return len(unique_labels) > 1
```

**Time Complexity**: O(n) where n = number of annotators
**Space Complexity**: O(n)

### 2. Final Label Suggestion Algorithm

```
1. Count label frequencies
2. IF unanimous:
   - Return label with 100% confidence
3. ELSE IF majority exists:
   - Calculate confidence = majority_count / total_count
   - Perform text analysis for adjustments
   - Apply keyword matching
   - Return suggested label with confidence
4. ELSE:
   - Return first label with lower confidence
```

**Time Complexity**: O(n + m) where n = annotators, m = text length
**Space Complexity**: O(1)

### 3. Text Analysis Algorithm

```
1. Extract keywords from text
2. Count positive indicators
3. Count negative indicators
4. Count neutral indicators
5. Determine dominant sentiment
6. Adjust suggestion if strong signal detected
7. Return adjusted label with explanation
```

## Design Patterns Used

### 1. **Pipeline Pattern**
- Sequential processing steps
- Clear separation of concerns
- Easy to extend with new steps

### 2. **Strategy Pattern**
- Different conflict resolution strategies
- Pluggable analysis methods
- Extensible reasoning logic

### 3. **Factory Pattern**
- `SampleAnalysis` creation
- Report generation from templates
- Data handler instantiation

### 4. **Observer Pattern** (Logging)
- Log events at each step
- Multiple log handlers
- Non-intrusive monitoring

## Extensibility Points

### 1. Add Custom Conflict Patterns
```python
CONFLICT_PATTERNS = {
    ("Label1", "Label2"): "Custom reason"
}
```

### 2. Add Custom Keywords
```python
positive_words = [...]  # Add more keywords
negative_words = [...]
neutral_words = [...]
```

### 3. Add Custom Report Types
```python
def generate_custom_report(self, results, path):
    # Implement custom report
```

### 4. Add Custom Reasoning
```python
def suggest_final_label_custom(self, labels, text):
    # Implement custom logic
```

## Performance Characteristics

| Operation | Time | Space | Notes |
|-----------|------|-------|-------|
| Load 1000 samples | ~100ms | O(n) | Streaming read |
| Analyze 1000 samples | ~500ms | O(1) | Per-sample analysis |
| Generate reports | ~200ms | O(n) | Full content creation |
| Total pipeline | ~1s | O(n) | Complete workflow |

## Error Handling Strategy

```
Input Validation
    ├─ File existence
    ├─ JSONL format
    └─ Required fields
            │
            ▼
Processing
    ├─ Missing values → Use defaults
    ├─ Invalid labels → Log and skip
    └─ Malformed text → Continue
            │
            ▼
Output Validation
    ├─ Results format
    ├─ Report generation
    └─ File writing
            │
            ▼
Logging
    └─ All errors to analysis.log
```

## Thread Safety & Concurrency

**Current Status**: NOT thread-safe
- Shared analyzer state
- No locking mechanisms
- Sequential processing

**Future Enhancement**: Could add:
- Thread-local storage for analyzer state
- Lock-based synchronization
- Async/await for I/O operations

## Configuration Management

```
config.json
├── analyzer_config
│   ├── version
│   ├── name
│   └── description
├── conflict_patterns
├── text_analysis
│   ├── positive_indicators
│   ├── negative_indicators
│   └── neutral_indicators
├── confidence_thresholds
├── output_settings
└── report_settings
```

## Module Dependencies

```
Standard Library:
├── json
├── logging
├── pathlib
├── dataclasses
├── collections
└── typing

External:
└── jsonlines (for efficient JSONL handling)

Testing:
├── unittest (built-in)
├── pytest (optional)
└── pytest-cov (optional)
```

## Future Enhancements

1. **Machine Learning Integration**
   - Train on confidence patterns
   - Learn annotator reliability
   - Predict label probabilities

2. **Advanced NLP**
   - Semantic analysis
   - Word embeddings
   - Entity recognition

3. **Performance Optimization**
   - Batch processing
   - Parallel analysis
   - Caching strategies

4. **Interactive UI**
   - Web dashboard
   - Real-time updates
   - Manual resolution interface

5. **Advanced Reporting**
   - Charts and visualizations
   - Interactive reports
   - Export to multiple formats
