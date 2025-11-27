# Multi-Annotator Conflict Detection System
# Dockerfile for reproducible environment

FROM python:3.11-slim

LABEL maintainer="conflict-detection-system"
LABEL description="Multi-Annotator Conflict Detection and Resolution System"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY analyzer.py .
COPY main.py .
COPY test_conflict_detection.py .
COPY text_label.jsonl .

# Create output directory
RUN mkdir -p /app/output

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Default command
ENTRYPOINT ["python"]
CMD ["main.py", "text_label.jsonl", "--output", "output/results.jsonl", "--report", "output/report.json"]
