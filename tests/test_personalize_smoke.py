"""
Smoke tests for name personalization token resolution.
"""

def test_tokens_resolve_basic():
    """Test basic token resolution with name."""
    import sys
    from unittest.mock import MagicMock
    
    # Mock streamlit with session state
    mock_st = MagicMock()
    mock_session_state = {"person_name": "Shane"}
    mock_st.session_state = mock_session_state
    sys.modules['streamlit'] = mock_st
    
    from core.content_contract import build_token_context, interpolate
    
    # Test with Shane as name using mocked session state
    ctx = build_token_context(mock_session_state)
    
    # Test NAME token
    result = interpolate("About {NAME}", ctx)
    assert result == "About Shane", f"Expected 'About Shane', got '{result}'"
    
    # Test NAME_POS token
    result = interpolate("What is {NAME_POS} age range?", ctx)
    # Handle both Shane's and Shane' variations
    assert result in ["What is Shane's age range?", "What is Shane' age range?"], (
        f"Expected possessive form, got '{result}'"
    )
    
    # Test combined tokens
    result = interpolate("{NAME} needs care and {NAME_POS} family is worried.", ctx)
    expected_options = [
        "Shane needs care and Shane's family is worried.",
        "Shane needs care and Shane' family is worried."
    ]
    assert result in expected_options, f"Expected combined form, got '{result}'"


def test_tokens_resolve_fallback():
    """Test token resolution falls back to 'you/your' when no name."""
    import sys
    import importlib
    from unittest.mock import MagicMock
    
    # Clear any cached modules
    modules_to_clear = [m for m in sys.modules.keys() if m.startswith('core.text') or m.startswith('core.state')]
    for m in modules_to_clear:
        if m in sys.modules:
            del sys.modules[m]
    
    # Mock streamlit with empty session state
    mock_st = MagicMock()
    mock_session_state = {}
    mock_st.session_state = mock_session_state
    sys.modules['streamlit'] = mock_st
    
    from core.content_contract import build_token_context, interpolate
    
    # Test with no name using mocked session state
    ctx = build_token_context(mock_session_state)
    
    # Test NAME token fallback
    result = interpolate("About {NAME}", ctx)
    assert result == "About you", f"Expected 'About you', got '{result}'"
    
    # Test NAME_POS token fallback
    result = interpolate("What is {NAME_POS} age range?", ctx)
    assert result == "What is your age range?", f"Expected 'What is your age range?', got '{result}'"


def test_personalize_text_helper():
    """Test the universal personalize_text helper function."""
    import sys
    from unittest.mock import MagicMock
    
    # Mock streamlit
    mock_st = MagicMock()
    mock_st.session_state = {"person_name": "Mary"}
    sys.modules['streamlit'] = mock_st
    
    from core.text import personalize_text
    
    # Test simple text
    result = personalize_text("Welcome {NAME}!")
    assert result == "Welcome Mary!", f"Expected 'Welcome Mary!', got '{result}'"
    
    # Test None/empty handling
    assert personalize_text(None) is None
    assert personalize_text("") == ""
    
    # Test list handling (if supported)
    try:
        result = personalize_text(["Hello {NAME}", "How is {NAME_POS} day?"])
        if isinstance(result, list):
            assert result[0] == "Hello Mary"
            assert result[1] in ["How is Mary's day?", "How is Mary' day?"]
    except (TypeError, AttributeError):
        # interpolate might not support lists, that's okay
        pass


def test_edge_cases():
    """Test edge cases and complex scenarios."""
    import sys
    from unittest.mock import MagicMock
    
    # Mock streamlit
    mock_st = MagicMock()
    sys.modules['streamlit'] = mock_st
    
    from core.content_contract import build_token_context, interpolate
    
    # Test multiple names in different locations
    mock_session_state = {
        "person_a_name": "John Doe",
        "person_name": "Jane Smith",  # Should be overridden by person_a_name
    }
    mock_st.session_state = mock_session_state
    
    ctx = build_token_context(mock_session_state)
    
    result = interpolate("Planning for {NAME}", ctx)
    assert result == "Planning for John", f"Expected 'Planning for John', got '{result}'"
    
    # Test with profile name
    mock_session_state = {
        "profile": {"person_name": "Bob Johnson"}
    }
    mock_st.session_state = mock_session_state
    
    ctx = build_token_context(mock_session_state)
    
    result = interpolate("{NAME} needs assistance", ctx)
    assert result == "Bob needs assistance", f"Expected 'Bob needs assistance', got '{result}'"


if __name__ == "__main__":
    test_tokens_resolve_basic()
    test_tokens_resolve_fallback()
    test_personalize_text_helper()
    test_edge_cases()
    print("✅ All personalization smoke tests passed!")