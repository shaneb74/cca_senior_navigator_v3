"""Global AI Advisor Service - Single brain facade for all AI-powered Q&A."""

from typing import Optional, List, Dict, Any
import time


def get_answer(
    question: str,
    name: Optional[str] = None,
    tags: Optional[List[str]] = None,
    source: str = "auto"
) -> Dict[str, Any]:
    """
    Global AI advisor service that routes questions through FAQ and corporate content.
    
    Args:
        question: User's question text
        name: Optional user name for personalization
        tags: Optional tags for filtering (future use)
        source: "auto" (try FAQ then corp), "faq" (FAQ only), or "corp" (corp only)
    
    Returns:
        {
            "answer": str,
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
        used_faq_ids = []
        used_urls = []
        fallback = False
        
        # Try FAQ first if auto or explicit
        if source in ("auto", "faq"):
            top_faqs = retrieve_faq(question, faqs, k=3)
            if top_faqs:
                used_faq_ids = [x.get("id") for x in top_faqs if isinstance(x, dict)]
                result = answer_faq(question, name, top_faqs, policy)
        
        # Try corporate content if no FAQ result and allowed
        if not result and source in ("auto", "corp"):
            top_chunks = retrieve_corp(question, corp, k=5)
            if top_chunks:
                used_urls = list({c.get("url", "") for c in top_chunks if isinstance(c, dict)})
                result = answer_corp(question, name, top_chunks, policy)
        
        # Final fallback if nothing worked
        if not result:
            fallback = True
            fallback_md = (
                "We don't have that in our FAQ yet. "
                "You can start the **Guided Care Plan** to get a tailored next step."
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
        return {
            "answer": result.get("answer", ""),
            "sources": result.get("sources", [])[:2],  # Limit to 2 sources
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
