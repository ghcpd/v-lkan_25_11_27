# Simple Dockerfile for label conflict analyzer
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default command: analyze provided dataset if present
CMD ["python", "analyze_labels.py", "text_label.jsonl", "-o", "analysis_output.jsonl"]
