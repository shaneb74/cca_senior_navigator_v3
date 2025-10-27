#!/usr/bin/env python3
"""
Build and save RAG corpus index for fast loading.

Creates a pre-built TF-IDF index from config/corp_knowledge.jsonl
and saves it to config/corp_index.pkl for instant loading at runtime.
"""
from __future__ import annotations
import json
import pickle
from pathlib import Path
from datetime import datetime

def main():
    from sklearn.feature_extraction.text import TfidfVectorizer
    
    corpus_path = Path("config/corp_knowledge.jsonl")
    index_path = Path("config/corp_index.pkl")
    
    print(f"[RAG_BUILD] Loading corpus from {corpus_path}")
    
    # Load all chunks
    chunks = []
    with corpus_path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                chunk = json.loads(line)
                chunks.append(chunk)
            except Exception as e:
                print(f"[RAG_BUILD] WARNING: Failed to parse line: {e}")
                continue
    
    print(f"[RAG_BUILD] Loaded {len(chunks)} chunks")
    
    # Build TF-IDF index
    print("[RAG_BUILD] Building TF-IDF index...")
    texts = []
    for c in chunks:
        # Combine title, heading/section, and text for better matching
        title = c.get("title", "")
        heading = c.get("heading") or c.get("section", "")
        text = c.get("text", "")
        combined = f"{title} {heading} {text}"
        texts.append(combined)
    
    vectorizer = TfidfVectorizer(stop_words="english", max_features=500)
    X = vectorizer.fit_transform(texts)
    
    # Save index
    index_data = {
        "vectorizer": vectorizer,
        "matrix": X,
        "chunks": chunks,
        "built_at": datetime.utcnow().isoformat() + "Z",
        "chunk_count": len(chunks)
    }
    
    print(f"[RAG_BUILD] Saving index to {index_path}")
    with index_path.open("wb") as f:
        pickle.dump(index_data, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    file_size = index_path.stat().st_size / (1024 * 1024)  # MB
    print(f"[RAG_BUILD] ✅ Index built successfully")
    print(f"[RAG_BUILD] Chunks: {len(chunks)}")
    print(f"[RAG_BUILD] Size: {file_size:.2f} MB")
    print(f"[RAG_BUILD] Output: {index_path}")
    
    # Show source breakdown
    sources = {}
    for c in chunks:
        src = c.get("source", c.get("type", "unknown"))
        sources[src] = sources.get(src, 0) + 1
    
    print("\n[RAG_BUILD] Source breakdown:")
    for src, count in sorted(sources.items(), key=lambda x: -x[1]):
        print(f"  {src}: {count} chunks")

if __name__ == "__main__":
    main()
