#!/bin/bash

# Script to replace exit.py with the redesigned version
# Run this from the repository root

echo "🔄 Replacing exit.py with redesigned version..."

# Remove extended attributes if any
xattr -c products/cost_planner_v2/exit.py 2>/dev/null || true

# Make the file writable
chmod +w products/cost_planner_v2/exit.py

# Replace the file
cat products/cost_planner_v2/exit_redesigned.py > products/cost_planner_v2/exit.py

echo "✅ Exit page redesign applied successfully!"
echo "📝 Original backed up as exit_redesigned.py"
echo "🧪 Test by navigating to the completion page"
