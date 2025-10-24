#!/usr/bin/env python3
"""Fix Python 3.10+ type hints for Python 3.9 compatibility."""
from pathlib import Path

def fix_file(filepath):
    content = Path(filepath).read_text()
    has_optional = 'Optional' in content
    
    # Replace all | None patterns
    content = content.replace(': Optional[str]', ': Optional[str]')
    content = content.replace(': Optional[int]', ': Optional[int]')
    content = content.replace(': dict | None', ': Optional[dict]')
    content = content.replace(': CareRecommendation | None', ': Optional["CareRecommendation"]')
    
    # Add Optional import if needed
    if not has_optional and 'Optional[' in content:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('from') or line.startswith('import'):
                if i > 0 and (lines[i-1].startswith('from') or lines[i-1].startswith('import')):
                    continue
                lines.insert(i+1, 'from typing import Optional')
                break
        content = '\n'.join(lines)
    
    Path(filepath).write_text(content)
    print(f"Fixed {filepath}")

# Fix files
fix_file('core/ui.py')
fix_file('core/mcip.py')
print("Done!")
