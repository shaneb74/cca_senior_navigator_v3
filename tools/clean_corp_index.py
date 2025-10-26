#!/usr/bin/env python
"""
Clean legacy HTML from corp_knowledge.jsonl corpus.

Usage:
    python tools/clean_corp_index.py

Creates: config/corp_knowledge_clean.jsonl
"""

import json
import sys
import re
import html
import pathlib


def strip_html(s: str) -> str:
    """Strip HTML tags and unescape entities from text."""
    if not s or not isinstance(s, str):
        return s
    
    # Convert <br> to newlines
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    
    # Add newlines after closing paragraph tags
    s = re.sub(r"</p\s*>", "\n\n", s, flags=re.I)
    
    # Convert list items to bullets
    s = re.sub(r"<li\s*>", "\n- ", s, flags=re.I)
    s = re.sub(r"</li\s*>", "", s, flags=re.I)
    
    # Strip all HTML tags
    s = re.sub(r"</?(ul|ol|p|div|span|strong|em|b|i|u|h[1-6]|a|table|tr|td|th|thead|tbody)[^>]*>", "", s, flags=re.I)
    
    # Unescape HTML entities
    s = html.unescape(s)
    
    # Clean up whitespace
    s = re.sub(r"\n{3,}", "\n\n", s)
    s = re.sub(r"[ \t]+", " ", s)
    s = s.strip()
    
    return s


def main():
    src = pathlib.Path("config/corp_knowledge.jsonl")
    dst = pathlib.Path("config/corp_knowledge_clean.jsonl")
    
    if not src.exists():
        print(f"Error: {src} not found")
        sys.exit(1)
    
    print(f"Reading from: {src}")
    print(f"Writing to:   {dst}")
    print()
    
    chunks_read = 0
    chunks_cleaned = 0
    
    with src.open("r", encoding="utf-8") as fin, dst.open("w", encoding="utf-8") as fout:
        for line in fin:
            chunks_read += 1
            obj = json.loads(line)
            
            # Clean text field
            if "text" in obj and isinstance(obj["text"], str):
                original = obj["text"]
                cleaned = strip_html(original)
                if cleaned != original:
                    chunks_cleaned += 1
                obj["text"] = cleaned
            
            # Clean heading field (less common but possible)
            if "heading" in obj and isinstance(obj["heading"], str):
                obj["heading"] = strip_html(obj["heading"])
            
            fout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    
    print(f"✅ Processed {chunks_read} chunks")
    print(f"✅ Cleaned {chunks_cleaned} chunks with HTML")
    print(f"✅ Wrote cleaned corpus: {dst}")
    print()
    print("To use the cleaned corpus:")
    print(f"  mv {dst} {src}")
    print("  # Or update CORP_INDEX_PATH in your config")


if __name__ == "__main__":
    main()
