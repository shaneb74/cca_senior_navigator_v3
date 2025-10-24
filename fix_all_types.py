#!/usr/bin/env python3
import re
import os

def fix_type_hints(content):
    # Replace all | None patterns with proper spacing handling
    patterns = [
        (r'\bstr\s*\|\s*None\b', 'Optional[str]'),
        (r'\bint\s*\|\s*None\b', 'Optional[int]'),
        (r'\bbool\s*\|\s*None\b', 'Optional[bool]'),
        (r'\bfloat\s*\|\s*None\b', 'Optional[float]'),
        (r'dict\[str,\s*str\]\s*\|\s*None', 'Optional[dict[str, str]]'),
        (r'dict\[str,\s*Any\]\s*\|\s*None', 'Optional[dict[str, Any]]'),
        (r'tuple\[str,\s*Any\]\s*\|\s*None', 'Optional[tuple[str, Any]]'),
        (r'list\[[\w\s,\[\]]+\]\s*\|\s*None', lambda m: f'Optional[{m.group(0).split("|")[0].strip()}]'),
    ]
    
    for pattern, replacement in patterns:
        if callable(replacement):
            content = re.sub(pattern, replacement, content)
        else:
            content = re.sub(pattern, replacement, content)
    
    # Add Optional to typing imports if needed
    if 'Optional[' in content and 'from typing import' in content:
        # Check if Optional is already imported
        typing_import_match = re.search(r'from typing import Optional, ([^\n]+)', content)
        if typing_import_match and 'Optional' not in typing_import_match.group(1):
            old_import = typing_import_match.group(0)
            new_import = old_import.replace('import ', 'import Optional, ')
            content = content.replace(old_import, new_import, 1)
    
    return content

count = 0
for root, dirs, files in os.walk('.'):
    # Skip certain directories
    if any(skip in root for skip in ['.git', '__pycache__', 'venv', '.cache', 'node_modules']):
        continue
    
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = fix_type_hints(content)
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Fixed: {filepath}")
                    count += 1
            except Exception as e:
                print(f"Error in {filepath}: {e}")

print(f"\nTotal files fixed: {count}")
