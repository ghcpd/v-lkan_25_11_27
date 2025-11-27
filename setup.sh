#!/bin/bash

# Multi-Annotator Label Conflict Analyzer - Setup Script
# This script sets up the environment and prepares the system for analysis

set -e  # Exit on error

echo "======================================"
echo "Setting up Label Conflict Analyzer"
echo "======================================"

# Check Python version
echo "[1/4] Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "[2/4] Creating virtual environment..."
    python3 -m venv venv
else
    echo "[2/4] Virtual environment already exists"
fi

# Activate virtual environment
echo "[3/4] Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "[4/4] Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "To use the analyzer, run:"
echo "  source venv/bin/activate"
echo "  python src/pipeline.py --input text_label.jsonl --output output"
echo ""
