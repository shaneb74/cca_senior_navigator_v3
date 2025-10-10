#!/bin/bash
# Pre-deployment verification script
# Run this before pushing to ensure error styling fix is in place

echo "🔍 Verifying Streamlit Error Styling Fix..."
echo ""

ERRORS=0

# Check 1: config.toml
echo -n "Checking .streamlit/config.toml... "
if grep -q "showErrorDetails = false" .streamlit/config.toml 2>/dev/null; then
    echo "✅ PASS"
else
    echo "❌ FAIL - Missing 'showErrorDetails = false'"
    ERRORS=$((ERRORS + 1))
fi

# Check 2: theme.css error suppression rules
echo -n "Checking assets/css/theme.css... "
if grep -q "aria-invalid" assets/css/theme.css 2>/dev/null; then
    echo "✅ PASS"
else
    echo "❌ FAIL - Missing error suppression CSS rules"
    ERRORS=$((ERRORS + 1))
fi

# Check 3: app.py CSS injection try-except
echo -n "Checking app.py CSS injection... "
if grep -q "except FileNotFoundError:" app.py 2>/dev/null; then
    echo "✅ PASS"
else
    echo "❌ FAIL - Missing try-except block for CSS injection"
    ERRORS=$((ERRORS + 1))
fi

# Check 4: Documentation exists
echo -n "Checking documentation... "
if [ -f "STREAMLIT_ERROR_STYLING_FIX.md" ]; then
    echo "✅ PASS"
else
    echo "⚠️  WARNING - Documentation file not found"
fi

echo ""
if [ $ERRORS -eq 0 ]; then
    echo "✅ All checks passed! Safe to deploy."
    exit 0
else
    echo "❌ $ERRORS check(s) failed. Please fix before deploying."
    echo "See STREAMLIT_ERROR_STYLING_FIX.md for details."
    exit 1
fi
