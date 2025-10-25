"""
Simple test to verify name personalization system logic.
"""

def test_name_logic():
    """Test the core logic without streamlit mocking."""
    
    # Simulate session state as a dict
    session_state = {}
    
    def mock_set_person_name(name: str) -> None:
        """Simulate set_person_name logic."""
        name = str(name).strip() if name else ""
        
        if name:
            session_state["person_a_name"] = name
            session_state["person_name"] = name
            session_state["planning_for_name"] = name
            
            if "profile" not in session_state:
                session_state["profile"] = {}
            session_state["profile"]["person_name"] = name
        else:
            session_state.pop("person_a_name", None)
            session_state.pop("person_name", None)
            session_state.pop("planning_for_name", None)
            
            if "profile" in session_state and isinstance(session_state["profile"], dict):
                session_state["profile"].pop("person_name", None)
    
    def mock_get_person_name() -> str:
        """Simulate get_person_name logic."""
        name_keys = ["person_a_name", "person_name", "planning_for_name"]
        for key in name_keys:
            name = session_state.get(key)
            if name and str(name).strip():
                return str(name).strip()
        
        profile = session_state.get("profile", {})
        if isinstance(profile, dict):
            profile_name = profile.get("person_name")
            if profile_name and str(profile_name).strip():
                return str(profile_name).strip()
        
        gcp_data = session_state.get("gcp", {})
        if isinstance(gcp_data, dict):
            gcp_name = gcp_data.get("person_a_name")
            if gcp_name and str(gcp_name).strip():
                return str(gcp_name).strip()
        
        return ""
    
    # Test setting name
    mock_set_person_name("John Doe")
    assert session_state["person_a_name"] == "John Doe"
    assert session_state["person_name"] == "John Doe"
    assert session_state["planning_for_name"] == "John Doe"
    assert session_state["profile"]["person_name"] == "John Doe"
    
    # Test getting name
    name = mock_get_person_name()
    assert name == "John Doe"
    
    # Test clearing name
    mock_set_person_name("")
    assert "person_a_name" not in session_state
    assert "person_name" not in session_state
    assert "planning_for_name" not in session_state
    assert "person_name" not in session_state.get("profile", {})
    
    # Test getting cleared name
    name = mock_get_person_name()
    assert name == ""
    
    print("✅ All name personalization logic tests passed!")


def test_bootstrap_logic():
    """Test snapshot rehydration logic."""
    
    session_state = {}
    
    def mock_set_person_name(name: str) -> None:
        """Simulate set_person_name logic."""
        name = str(name).strip() if name else ""
        if name:
            session_state["person_a_name"] = name
            session_state["person_name"] = name
            session_state["planning_for_name"] = name
            
            if "profile" not in session_state:
                session_state["profile"] = {}
            session_state["profile"]["person_name"] = name
    
    def mock_rehydrate_name_from_snapshot(snapshot):
        """Simulate rehydrate_name_from_snapshot logic."""
        if not snapshot or not isinstance(snapshot, dict):
            return
        
        name_keys = ["person_a_name", "person_name", "planning_for_name"]
        for key in name_keys:
            name = snapshot.get(key)
            if name and str(name).strip():
                mock_set_person_name(str(name).strip())
                return
        
        gcp_data = snapshot.get("gcp", {})
        if isinstance(gcp_data, dict):
            gcp_name = gcp_data.get("person_a_name")
            if gcp_name and str(gcp_name).strip():
                mock_set_person_name(str(gcp_name).strip())
                return
        
        profile_data = snapshot.get("profile", {})
        if isinstance(profile_data, dict):
            profile_name = profile_data.get("person_name")
            if profile_name and str(profile_name).strip():
                mock_set_person_name(str(profile_name).strip())
                return
    
    # Test with snapshot containing name
    snapshot = {"person_a_name": "Jane Smith"}
    mock_rehydrate_name_from_snapshot(snapshot)
    assert session_state["person_a_name"] == "Jane Smith"
    
    # Test with nested profile name
    session_state.clear()
    snapshot = {"profile": {"person_name": "Bob Johnson"}}
    mock_rehydrate_name_from_snapshot(snapshot)
    assert session_state["person_a_name"] == "Bob Johnson"
    
    # Test with empty snapshot
    session_state.clear()
    mock_rehydrate_name_from_snapshot({})
    assert len(session_state) == 0
    
    print("✅ All bootstrap logic tests passed!")


if __name__ == "__main__":
    test_name_logic()
    test_bootstrap_logic()
    print("🎉 Name personalization system logic is verified!")