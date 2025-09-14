#!/bin/bash

# Code Guardian Installation Script

set -e

echo "🛡️ Installing Code Guardian..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install package in development mode
echo "📚 Installing Code Guardian..."
pip install -e .

# Install development dependencies
echo "🛠️ Installing development dependencies..."
pip install pytest pytest-cov black isort mypy

echo "✅ Installation complete!"
echo ""
echo "🚀 Quick start:"
echo "  source venv/bin/activate"
echo "  ai-guardian scan examples/"
echo "  python3 demo.py"
echo ""
echo "📚 Documentation: https://github.com/yes-its-shivam/codeGuardian"