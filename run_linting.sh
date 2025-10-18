#!/bin/bash

# Linting script for CCA Senior Navigator v3
# Run this script to auto-fix linting issues

echo "🔍 Running ruff linter..."
echo ""

# Run ruff check with auto-fix
echo "Step 1: Auto-fixing linting issues..."
./venv/bin/python -m ruff check . --fix --no-cache

echo ""
echo "Step 2: Formatting code..."
./venv/bin/python -m ruff format . --no-cache

echo ""
echo "Step 3: Final check (remaining issues)..."
./venv/bin/python -m ruff check . --no-cache --statistics

echo ""
echo "✅ Linting complete!"
echo ""
echo "To view details of remaining issues:"
echo "  ./venv/bin/python -m ruff check . --no-cache"
