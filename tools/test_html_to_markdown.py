#!/usr/bin/env python
"""Test script for HTML→Markdown conversion in AI Advisor answers.

Tests that _html_to_markdown() properly:
- Strips chat-bubble wrappers
- Converts <a> tags to [text](url)
- Handles HTML entities
- Preserves text structure
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.llm_mediator import _html_to_markdown


def test_cases():
    """Run all HTML→Markdown test cases."""
    
    tests = [
        # Test 1: Chat bubble wrapper + entities + link
        {
            "name": "Full RAG answer with wrapper and link",
            "input": "<div class='chat-bubble__content'>Hello &#x27;Seattle&#x27;.\n<br><a href='https://example.com'>Read more</a></div>",
            "expected": "Hello 'Seattle'.\n\n[Read more](https://example.com)"
        },
        
        # Test 2: Multiple links
        {
            "name": "Multiple links in paragraph",
            "input": "<p>Visit <a href='https://site1.com'>Site One</a> or <a href='https://site2.com'>Site Two</a> for help.</p>",
            "expected": "Visit [Site One](https://site1.com) or [Site Two](https://site2.com) for help."
        },
        
        # Test 3: HTML entities
        {
            "name": "HTML entities without tags",
            "input": "Hello &amp; goodbye. Cost: &#36;5,000.",
            "expected": "Hello & goodbye. Cost: $5,000."
        },
        
        # Test 4: List with bullets
        {
            "name": "Unordered list to Markdown bullets",
            "input": "<ul><li>Item one</li><li>Item two</li></ul>",
            "expected": "- Item one\n- Item two"
        },
        
        # Test 5: Nested formatting
        {
            "name": "Nested bold/italic tags",
            "input": "<p><strong>Bold text</strong> and <em>italic text</em>.</p>",
            "expected": "Bold text and italic text."
        },
        
        # Test 6: Link with nested HTML
        {
            "name": "Link with nested tags in text",
            "input": "<a href='https://x.com'><strong>Bold</strong> link</a>",
            "expected": "[Bold link](https://x.com)"
        },
        
        # Test 7: Already clean Markdown
        {
            "name": "Already clean Markdown (no HTML)",
            "input": "This is **Markdown** with [a link](https://example.com).",
            "expected": "This is **Markdown** with [a link](https://example.com)."
        },
        
        # Test 8: Paragraph spacing
        {
            "name": "Multiple paragraphs",
            "input": "<p>First paragraph.</p><p>Second paragraph.</p>",
            "expected": "First paragraph.\n\nSecond paragraph."
        },
        
        # Test 9: Link without text (URL only)
        {
            "name": "Link without visible text",
            "input": "<a href='https://example.com'></a>",
            "expected": "<https://example.com>"
        },
        
        # Test 10: Complex real-world example
        {
            "name": "Complex RAG answer",
            "input": """<div class="chat-bubble__content">
            <p>Based on your location, I recommend these <strong>assisted living</strong> communities:</p>
            <ul>
                <li><a href="https://cca.com/facility1">Sunrise Senior Living</a> - Memory care specialist</li>
                <li><a href="https://cca.com/facility2">Brookdale Seattle</a> - Full continuum of care</li>
            </ul>
            <p>Read more in our <a href="https://cca.com/guide">Senior Living Guide</a>.</p>
            </div>""",
            # Note: Extra newlines from multi-line HTML are acceptable in practice
            "expected_contains": [
                "assisted living communities",
                "[Sunrise Senior Living](https://cca.com/facility1)",
                "[Brookdale Seattle](https://cca.com/facility2)",
                "[Senior Living Guide](https://cca.com/guide)"
            ]
        }
    ]
    
    passed = 0
    failed = 0
    
    print("=" * 70)
    print("HTML→Markdown Conversion Tests")
    print("=" * 70)
    
    for i, test in enumerate(tests, 1):
        print(f"\n[Test {i}] {test['name']}")
        print(f"Input:    {test['input'][:80]}{'...' if len(test['input']) > 80 else ''}")
        
        result = _html_to_markdown(test["input"])
        
        # Check if using contains-based assertion (for complex multi-line HTML)
        if "expected_contains" in test:
            all_found = all(substring in result for substring in test["expected_contains"])
            if all_found:
                print(f"✅ PASS (contains all required substrings)")
                passed += 1
            else:
                print(f"❌ FAIL (missing substrings)")
                print(f"Expected contains: {test['expected_contains']}")
                print(f"Got: {repr(result)}")
                failed += 1
        else:
            # Exact match
            if result == test["expected"]:
                print(f"✅ PASS")
                passed += 1
            else:
                print(f"❌ FAIL")
                print(f"Expected: {repr(test['expected'])}")
                print(f"Got:      {repr(result)}")
                failed += 1
    
    print("\n" + "=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = test_cases()
    sys.exit(0 if success else 1)
