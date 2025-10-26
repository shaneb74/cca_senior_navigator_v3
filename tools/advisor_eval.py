"""
Advisor Evaluation Script - Test RAG-first routing and corpus coverage.

Usage:
    python tools/advisor_eval.py
"""

import importlib

# Import from products.global (reserved keyword workaround)
advisor_service = importlib.import_module("products.global.ai.advisor_service")
get_answer = advisor_service.get_answer


# Test questions covering key topics
TEST_QUESTIONS = [
    # Assisted Living
    "What do I need to know about assisted living?",
    "How much does assisted living cost?",
    "What services are included in assisted living?",
    
    # Memory Care
    "Do I need a diagnosis for Memory Care?",
    "What is the difference between assisted living and memory care?",
    "How do I know if my parent needs memory care?",
    
    # Cost Planning
    "What does the Cost Planner do?",
    "How can I pay for senior care?",
    "What financial assistance is available?",
    
    # GCP/Assessment
    "How long does the Guided Care Plan take?",
    "What questions does the assessment ask?",
    "Is the care assessment free?",
    
    # General
    "What is CCA Senior Navigator?",
    "How does CCA help families?",
    "Can I get help choosing a facility?",
]


def eval_advisor():
    """Run evaluation on test questions."""
    print("=" * 80)
    print("ADVISOR EVALUATION - RAG-First Architecture")
    print("=" * 80)
    print()
    
    results = {
        "rag": 0,
        "faq": 0,
        "suggest": 0,
        "error": 0,
    }
    
    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"\n[{i}/{len(TEST_QUESTIONS)}] Q: {question}")
        print("-" * 80)
        
        try:
            response = get_answer(question, source="auto")
            
            mode = response.get("mode", "unknown")
            answer = response.get("answer", "")
            sources = response.get("sources", [])
            meta = response.get("meta", {})
            
            results[mode] = results.get(mode, 0) + 1
            
            # Show mode and source count
            print(f"Mode: {mode.upper()}")
            print(f"Sources: {len(sources)}")
            if sources:
                for src in sources[:2]:  # Show first 2 sources
                    print(f"  - {src.get('title', 'Unknown')} ({src.get('url', 'no-url')[:50]}...)")
            
            # Show answer preview (first 150 chars)
            answer_preview = answer[:150].replace("\n", " ")
            print(f"Answer: {answer_preview}...")
            
            # Show timing
            elapsed = meta.get("elapsed_ms", 0)
            print(f"Time: {elapsed}ms")
            
        except Exception as e:
            print(f"ERROR: {e}")
            results["error"] += 1
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    total = sum(results.values())
    for mode, count in sorted(results.items(), key=lambda x: -x[1]):
        pct = (count / total * 100) if total > 0 else 0
        print(f"{mode.upper():12s}: {count:3d} ({pct:5.1f}%)")
    
    print("\n✅ Evaluation complete!")
    print(f"   RAG coverage: {results['rag']}/{len(TEST_QUESTIONS)} questions")
    print(f"   Expected: High RAG %, low FAQ/suggest %")


if __name__ == "__main__":
    eval_advisor()
