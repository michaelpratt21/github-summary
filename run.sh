#!/bin/bash
# Convenience script to run GitHub Summary
# Automatically activates virtual environment and runs the script

set -e  # Exit on error

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Run ./setup.sh first to create it"
    exit 1
fi

# Activate venv and run script with all arguments
source venv/bin/activate
python github_summary.py "$@"
