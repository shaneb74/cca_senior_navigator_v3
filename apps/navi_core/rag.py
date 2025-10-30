"""
NAVI Core RAG (Retrieval-Augmented Generation)

Tier-1: Mini-FAQ exact/fuzzy matching
Tier-2: Semantic embedding retrieval (placeholder)
Tier-3: Full LLM generation with context (placeholder)
"""

import json
from pathlib import Path
from typing import Optional


class MiniFAQRetriever:
    """Tier-1 FAQ retriever using exact and fuzzy matching.
    
    Provides instant answers for common questions without LLM overhead.
    High confidence (1.0) when matched.
    """
    
    def __init__(self, config_path: str = "apps/navi_core/config/mini_faq.json"):
        """Initialize FAQ retriever.
        
        Args:
            config_path: Path to mini_faq.json configuration
        """
        self.config_path = Path(config_path)
        self.faq = self._load_faq()
        
    def _load_faq(self) -> dict:
        """Load FAQ from JSON file."""
        try:
            with open(self.config_path) as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"[NAVI_RAG] FAQ file not found: {self.config_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"[NAVI_RAG] Invalid FAQ JSON: {e}")
            return {}
    
    def match(self, question: str) -> Optional[str]:
        """Match question to FAQ answer.
        
        Uses case-insensitive substring matching for flexibility.
        
        Args:
            question: User's question
            
        Returns:
            FAQ answer if matched, None otherwise
        """
        if not question or not self.faq:
            return None
            
        q_lower = question.strip().lower()
        
        # Return None for empty or whitespace-only questions
        if not q_lower or len(q_lower) < 3:
            return None
        
        # Try exact question match first
        for faq_q, faq_a in self.faq.items():
            if q_lower == faq_q.lower():
                print(f"[NAVI_RAG] Tier-1 exact match: '{question}'")
                return faq_a
        
        # Try fuzzy match using keyword-based approach
        import re
        for faq_q, faq_a in self.faq.items():
            faq_q_lower = faq_q.lower()
            
            # Extract meaningful keywords (remove common stop words and punctuation)
            stop_words = {'what', 'is', 'are', 'the', 'a', 'an', 'how', 'do', 'does', 'can', 'i', 'you', 
                        'about', 'tell', 'me', 'know', 'my', 'to', 'of'}
            # Remove punctuation and split
            faq_keywords = [w for w in re.findall(r'\b\w+\b', faq_q_lower) 
                          if w not in stop_words and len(w) >= 4]
            
            if not faq_keywords:
                continue
            
            # Count matching keywords
            matched_keywords = [kw for kw in faq_keywords if kw in q_lower]
            
            # Classify keywords as generic or specific
            generic_words = {'senior', 'care', 'living', 'home', 'cost', 'need'}
            specific_matches = [kw for kw in matched_keywords if kw not in generic_words]
            generic_matches = [kw for kw in matched_keywords if kw in generic_words]
            
            # Match criteria:
            # - At least 2 specific keywords, OR
            # - 1 specific + 1 generic keyword, OR  
            # - 1 compound keyword (8+ chars)
            if len(specific_matches) >= 2 or \
               (len(specific_matches) >= 1 and len(generic_matches) >= 1) or \
               any(len(kw) >= 8 for kw in specific_matches):
                print(f"[NAVI_RAG] Tier-1 fuzzy match: '{question}' -> '{faq_q}'")
                return faq_a
        
        print(f"[NAVI_RAG] No Tier-1 match for: '{question}'")
        return None
    
    def reload(self) -> None:
        """Reload FAQ from disk (useful for hot-reloading config)."""
        self.faq = self._load_faq()
        print(f"[NAVI_RAG] Reloaded {len(self.faq)} FAQ entries")


# Placeholder for Tier-2 semantic retrieval
class SemanticRetriever:
    """Tier-2 semantic retriever using embeddings (placeholder).
    
    Will use vector similarity search to find relevant context chunks
    from knowledge base, user history, and care documentation.
    """
    
    def __init__(self, embedding_model: str = "text-embedding-3-small"):
        """Initialize semantic retriever.
        
        Args:
            embedding_model: OpenAI embedding model to use
        """
        self.embedding_model = embedding_model
        print(f"[NAVI_RAG] Semantic retriever initialized (placeholder)")
    
    def retrieve(self, question: str, top_k: int = 5) -> list:
        """Retrieve semantically similar chunks (placeholder).
        
        Args:
            question: User's question
            top_k: Number of chunks to retrieve
            
        Returns:
            List of chunk metadata dicts
        """
        # TODO: Implement embedding-based retrieval
        print(f"[NAVI_RAG] Tier-2 semantic retrieval not yet implemented")
        return []
