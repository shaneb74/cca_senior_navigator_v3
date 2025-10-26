"""Global AI Advisor Service - Single brain facade for all AI-powered Q&A."""

from typing import Optional, List, Dict, Any
import time
import os


# RAG configuration
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "8"))
MIN_SCORE = float(os.getenv("RAG_MIN_SCORE", "0.12"))


def get_answer(
    question: str,
    name: Optional[str] = None,
    tags: Optional[List[str]] = None,
    source: str = "auto"
) -> Dict[str, Any]:
    """
    Global AI advisor service - RAG-FIRST architecture.
    
    Routing priority:
    1. Corporate content/RAG (primary - 400+ page corpus)
    2. FAQ (fallback for specific questions)
    3. Suggestive guidance (if no matches)
    
    Args:
        question: User's question text
        name: Optional user name for personalization
        tags: Optional tags for filtering (future use)
        source: "auto" (try corp then FAQ), "corp" (corp only), or "faq" (FAQ only)
    
    Returns:
        {
            "answer": str,
            "mode": "rag|faq|suggest",
            "sources": List[{"title": str, "url": str}],
            "cta": Optional[{"label": str, "route": str}],
            "meta": {"elapsed_ms": int, "fallback": bool}
        }
    """
    start = time.time()
    
    # Import locally to avoid circular imports at import-time
    try:
        from pages.faq import (
            load_faq_items,
            load_faq_policy,
            retrieve_faq,
            load_corp_chunks,
            retrieve_corp
        )
        from ai.llm_mediator import answer_faq, answer_corp
    except ImportError as e:
        # Fallback if modules not available
        elapsed = int((time.time() - start) * 1000)
        return {
            "answer": "Our AI advisor is temporarily unavailable. Please try the Guided Care Plan for personalized recommendations.",
            "mode": "error",
            "sources": [],
            "cta": {"label": "Start Guided Care Plan", "route": "/gcp"},
            "meta": {"elapsed_ms": elapsed, "fallback": True, "error": str(e)},
        }
    
    try:
        # Load data sources
        policy = load_faq_policy()
        faqs = load_faq_items()
        corp_mtime = time.time()  # Cache key for corp chunks
        corp = load_corp_chunks(_mtime=corp_mtime)
        
        result = None
        mode = "suggest"
        used_faq_ids = []
        used_urls = []
        fallback = False
        
        # PRIORITY 1: Corporate content/RAG (primary source - unless explicitly FAQ-only)
        if source in ("auto", "corp"):
            top_chunks = retrieve_corp(question, corp, k=RAG_TOP_K)
            if top_chunks:
                # Filter by minimum relevance score (if chunks have scores)
                good_chunks = [c for c in top_chunks if isinstance(c, dict)]
                if good_chunks:
                    used_urls = list({c.get("url", "") for c in good_chunks})
                    result = answer_corp(question, name, good_chunks, policy)
                    if result:
                        mode = "rag"
                        print(f"[ADVISOR_RAG] question='{question[:50]}...' chunks={len(good_chunks)} urls={len(used_urls)}")
        
        # PRIORITY 2: FAQ (fallback if corp had no good matches, or explicit FAQ request)
        if not result and source in ("auto", "faq"):
            top_faqs = retrieve_faq(question, faqs, k=3)
            if top_faqs:
                used_faq_ids = [x.get("id") for x in top_faqs if isinstance(x, dict)]
                result = answer_faq(question, name, top_faqs, policy)
                if result:
                    mode = "faq"
        
        # PRIORITY 3: Suggestive guidance (no exact matches found)
        if not result:
            fallback = True
            mode = "suggest"
            fallback_md = (
                "I didn't find an exact match in our guides. Try asking about assisted living, "
                "memory care eligibility, or cost planning—or open the **Guided Care Plan** "
                "to get a tailored next step."
            )
            result = {
                "answer": fallback_md,
                "sources": [],
                "cta": policy.get("default_cta", {
                    "label": "Start Guided Care Plan",
                    "route": "/gcp"
                })
            }
        
        elapsed = int((time.time() - start) * 1000)
        
        # Build sources list from URLs (for RAG) or FAQ IDs
        sources = []
        if mode == "rag" and used_urls:
            # Extract sources from corp chunks
            for url in used_urls[:4]:  # Limit to 4 sources
                # Find matching chunk for title
                matching = next((c for c in corp if c.get("url") == url), None)
                if matching:
                    sources.append({
                        "title": matching.get("title", "CCA Source"),
                        "url": url
                    })
        elif mode == "faq":
            sources = result.get("sources", [])[:2]
        
        return {
            "answer": result.get("answer", ""),
            "mode": mode,
            "sources": sources,
            "cta": result.get("cta"),
            "meta": {
                "elapsed_ms": elapsed,
                "fallback": fallback,
                "faq_ids": used_faq_ids if used_faq_ids else None,
                "urls": used_urls if used_urls else None,
            },
        }
        
    except Exception as e:
        # Error fallback
        elapsed = int((time.time() - start) * 1000)
        return {
            "answer": "We're having trouble fetching that right now. Please try again or start the Guided Care Plan.",
            "mode": "error",
            "sources": [],
            "cta": {
                "label": "Start Guided Care Plan",
                "route": "/gcp"
            },
            "meta": {
                "elapsed_ms": elapsed,
                "fallback": True,
                "error": str(e)
            },
        }
