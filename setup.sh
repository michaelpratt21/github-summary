#!/bin/bash
# Setup script for GitHub Summary
# This creates a virtual environment and installs all dependencies

set -e  # Exit on error

echo "🚀 Setting up GitHub Summary..."
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Found Python $PYTHON_VERSION"

# Check for GitHub CLI
if ! command -v gh &> /dev/null; then
    echo "⚠️  Warning: GitHub CLI (gh) is not installed"
    echo "   Install with: brew install gh"
    echo "   Then authenticate with: gh auth login"
    echo ""
fi

# Create virtual environment
if [ -d "venv" ]; then
    echo "✓ Virtual environment already exists"
else
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate and install dependencies
echo "📚 Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Set environment variables:"
echo "   export OPENAI_API_KEY='your-api-key'"
echo "   export SMTP_USER='your.email@company.com'"
echo "   export SMTP_PASSWORD='your-app-password'"
echo "   export SMTP_FROM='your.email@company.com'"
echo ""
echo "2. Run your first summary:"
echo "   ./run.sh --repos 'owner/repo' --time-range 24h --file test.md"
echo ""
echo "See QUICKSTART.md for more details!"
