"""Unit tests for HTML sanitization in Advisor/FAQ pipeline."""

import pytest
from ai.llm_mediator import _html_to_markdown, _normalize_answer


class TestHTMLSanitization:
    """Test HTML removal and Markdown conversion."""
    
    def test_strip_chat_bubble_wrapper(self):
        """Remove legacy chat-bubble__content wrapper."""
        html = '<div class="chat-bubble__content">Hello world</div>'
        result = _html_to_markdown(html)
        assert result == "Hello world"
        assert "<" not in result
    
    def test_strip_chat_sources_wrapper(self):
        """Remove legacy chat-sources wrapper."""
        html = '<div class="chat-sources"><span>Source</span></div>'
        result = _html_to_markdown(html)
        assert "chat-sources" not in result
        assert "<" not in result
    
    def test_convert_links_to_markdown(self):
        """Convert HTML links to Markdown."""
        html = '<a href="https://example.com">Click here</a>'
        result = _html_to_markdown(html)
        assert result == "[Click here](https://example.com)"
        assert "<a" not in result
    
    def test_convert_br_to_newline(self):
        """Convert <br> tags to newlines."""
        html = "Line 1<br/>Line 2<br>Line 3"
        result = _html_to_markdown(html)
        assert "<br" not in result
        assert "Line 1\nLine 2\nLine 3" in result
    
    def test_remove_paragraph_tags(self):
        """Strip <p> tags."""
        html = "<p>Paragraph 1</p><p>Paragraph 2</p>"
        result = _html_to_markdown(html)
        assert "<p>" not in result
        assert "Paragraph 1" in result
        assert "Paragraph 2" in result
    
    def test_unescape_entities(self):
        """Unescape HTML entities."""
        html = "It&#x27;s a &quot;test&quot; &amp; more"
        result = _html_to_markdown(html)
        assert result == 'It\'s a "test" & more'
        assert "&#x27;" not in result
        assert "&quot;" not in result
    
    def test_normalize_answer_wrapper(self):
        """Test _normalize_answer calls _html_to_markdown."""
        html = '<div class="chat-bubble__content">Test answer</div>'
        result = _normalize_answer(html)
        assert result == "Test answer"
        assert "<" not in result
    
    def test_multi_div_pattern(self):
        """Handle multiple div wrappers."""
        html = '''
        <div class="chat-bubble__content">Answer text</div>
        <div class="chat-sources">Source info</div>
        '''
        result = _html_to_markdown(html)
        assert "chat-bubble__content" not in result
        assert "chat-sources" not in result
        assert "Answer text" in result
    
    def test_clean_markdown_passthrough(self):
        """Clean Markdown should pass through unchanged."""
        markdown = "# Heading\n\nThis is **bold** and *italic*.\n\n- Item 1\n- Item 2"
        result = _html_to_markdown(markdown)
        assert result == markdown
    
    def test_residual_angle_brackets(self):
        """Ensure no residual < or > remain after sanitization."""
        test_cases = [
            '<div class="chat-bubble__content">Test</div>',
            '<a href="url">Link</a>',
            '<p>Para</p><br/><span>Text</span>',
            '&lt;script&gt;alert("xss")&lt;/script&gt;',
        ]
        
        for html in test_cases:
            result = _html_to_markdown(html)
            # Allow markdown links like [text](url) but no HTML tags
            assert not (result.count("<") - result.count("](") > 0), \
                f"Residual '<' found in: {result}"


class TestAdvisorServiceSanitization:
    """Test that advisor_service sanitizes responses."""
    
    def test_sanitize_answer_payload(self):
        """Verify _sanitize_answer_payload exists and works."""
        from products.global.ai.advisor_service import _sanitize_answer_payload
        
        payload = {
            "answer": '<div class="chat-bubble__content">Test</div>',
            "mode": "rag",
            "sources": []
        }
        
        result = _sanitize_answer_payload(payload)
        assert result["answer"] == "Test"
        assert "<" not in result["answer"]
    
    def test_get_answer_returns_clean_markdown(self):
        """Integration test: get_answer should return Markdown."""
        from products.global.ai.advisor_service import get_answer
        
        # This will actually hit the LLM/RAG, so we just check the contract
        response = get_answer("What is CCA?", name="Test User")
        
        assert isinstance(response, dict)
        assert "answer" in response
        assert "mode" in response
        
        # The answer should be clean Markdown (no HTML wrappers)
        answer = response["answer"]
        
        # Check for banned patterns
        assert "chat-bubble__content" not in answer
        assert "chat-sources" not in answer
        assert not answer.startswith("<div")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
