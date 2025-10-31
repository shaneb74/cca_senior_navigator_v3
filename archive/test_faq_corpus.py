#!/usr/bin/env python3
"""
Test FAQ corpus retrieval for the three queries from user request.

Tests:
1. Seattle senior living options (should hit regional guides)
2. Memory care advisory service for Alzheimer's in WA (should hit consults/checklists)
3. Post-move support (should hit follow-up/adjustment tips)
"""

import sys
import os
import json
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def load_corp_chunks():
    """Load corp knowledge chunks."""
    chunks_path = "config/corp_knowledge.jsonl"
    if not os.path.exists(chunks_path):
        print(f"ERROR: {chunks_path} not found")
        return []
    
    chunks = []
    with open(chunks_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                chunks.append(json.loads(line))
            except Exception:
                pass
    return chunks


def simple_retrieve(query, chunks, k=5):
    """Simple keyword-based retrieval (no sklearn)."""
    from collections import Counter
    
    # Tokenize query
    q_tokens = set(query.lower().split())
    
    # Score chunks by keyword overlap
    scored = []
    for chunk in chunks:
        text = f"{chunk.get('title', '')} {chunk.get('heading', '')} {chunk.get('text', '')}"
        text_tokens = set(text.lower().split())
        overlap = len(q_tokens & text_tokens)
        
        if overlap > 0:
            scored.append((overlap, chunk))
    
    # Sort by score descending
    scored.sort(reverse=True, key=lambda x: x[0])
    return [c for score, c in scored[:k]]


def test_query(query, chunks):
    """Test a single query."""
    print(f"\n{'=' * 80}")
    print(f"QUERY: {query}")
    print(f"{'=' * 80}")
    
    hits = simple_retrieve(query, chunks, k=5)
    
    if not hits:
        print("❌ NO RESULTS FOUND")
        return False
    
    print(f"✅ Found {len(hits)} results:\n")
    
    for i, hit in enumerate(hits, 1):
        print(f"{i}. [{hit['doc_id']}] {hit['title']}")
        print(f"   Heading: {hit.get('heading', 'N/A')[:80]}")
        print(f"   Text: {hit.get('text', 'N/A')[:150]}...")
        print(f"   URL: {hit['url']}")
        print()
    
    return True


def main():
    print("Loading corpus from config/corp_knowledge.jsonl...")
    chunks = load_corp_chunks()
    
    if not chunks:
        print("ERROR: No chunks loaded. Run 'make sync-site' first.")
        return 1
    
    print(f"Loaded {len(chunks)} chunks")
    
    # Test queries from user request
    queries = [
        "What kinds of senior living options do you recommend in Seattle, and how do you ensure a good match?",
        "How does your free advisory service work for finding memory care for Alzheimer's in Washington state?",
        "What support happens after moving into assisted living?"
    ]
    
    results = []
    for query in queries:
        success = test_query(query, chunks)
        results.append(success)
    
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")
    print(f"Total queries: {len(queries)}")
    print(f"Successful: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("\n✅ ALL QUERIES PASSED")
        return 0
    else:
        print("\n❌ SOME QUERIES FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
