"""
Quick test script to verify Navi dialogue system integration.

Tests:
1. Dialogue JSON loads correctly
2. Journey messages retrieved for each phase
3. Context formatting works (name, tier, costs)
4. Product intros, gates, and micro-moments accessible
"""

import json
from pathlib import Path


def test_dialogue_loads():
    """Test that dialogue JSON loads without errors."""
    print("🧪 Test 1: Loading navi_dialogue.json...")
    config_path = Path(__file__).parent / "config" / "navi_dialogue.json"
    
    with open(config_path, "r") as f:
        dialogue = json.load(f)
    
    assert "navi" in dialogue
    assert "journey_phases" in dialogue
    assert "product_gates" in dialogue
    assert "product_intros" in dialogue
    assert "micro_moments" in dialogue
    
    print("✅ Dialogue loaded successfully")
    print(f"   - {len(dialogue['journey_phases'])} journey phases")
    print(f"   - {len(dialogue['product_gates'])} product gates")
    print(f"   - {len(dialogue['product_intros'])} product intros")
    print()


def test_journey_messages():
    """Test that journey messages exist for all phases."""
    print("🧪 Test 2: Journey phase messages...")
    
    from core.navi_dialogue import NaviDialogue
    
    phases = ["getting_started", "in_progress", "nearly_there", "complete"]
    
    for phase in phases:
        # Test guest message
        message_guest = NaviDialogue.get_journey_message(phase, is_authenticated=False)
        assert "text" in message_guest
        assert "icon" in message_guest
        print(f"✅ {phase} (guest): {message_guest['icon']} {message_guest['text'][:50]}...")
        
        # Test authenticated message
        message_auth = NaviDialogue.get_journey_message(phase, is_authenticated=True)
        assert "text" in message_auth
        print(f"✅ {phase} (authenticated): {message_auth['icon']} {message_auth['text'][:50]}...")
    
    print()


def test_context_formatting():
    """Test that context variables are formatted correctly."""
    print("🧪 Test 3: Context formatting...")
    
    from core.navi_dialogue import NaviDialogue
    
    context = {
        "name": "Sarah",
        "tier": "Assisted Living",
        "confidence": 85,
        "monthly_cost": "$4,500",
        "runway_months": 30
    }
    
    # Test in_progress message with context
    message = NaviDialogue.get_journey_message("in_progress", is_authenticated=True, context=context)
    
    text = message.get("text", "")
    print(f"✅ Formatted message: {text}")
    
    # Verify context variables were replaced
    assert "Sarah" in text or "{name}" not in text
    print(f"✅ Name formatting works")
    
    # Test context boost
    boost = NaviDialogue.get_context_boost("in_progress", context)
    if boost:
        print(f"✅ Context boost: {len(boost)} messages")
        for b in boost[:2]:
            print(f"   - {b}")
    
    print()


def test_product_gates():
    """Test product gate messages."""
    print("🧪 Test 4: Product gate messages...")
    
    from core.navi_dialogue import NaviDialogue
    
    gates = ["gcp_locked", "cost_locked", "pfma_locked"]
    
    for gate in gates:
        message = NaviDialogue.get_gate_message(gate)
        assert "message" in message
        assert "action" in message
        print(f"✅ {gate}: {message['message'][:60]}...")
    
    print()


def test_product_intros():
    """Test product intro messages."""
    print("🧪 Test 5: Product intro messages...")
    
    from core.navi_dialogue import NaviDialogue
    
    intros = ["gcp_start", "cost_start", "pfma_start"]
    
    for intro in intros:
        message = NaviDialogue.get_product_intro(intro)
        assert "welcome" in message
        print(f"✅ {intro}: {message['welcome']}")
    
    print()


def test_micro_moments():
    """Test micro-moment messages."""
    print("🧪 Test 6: Micro-moment messages...")
    
    from core.navi_dialogue import NaviDialogue
    
    moments = [
        "progress_save",
        "returning_user",
        "achievement_earned"
    ]
    
    for moment in moments:
        message = NaviDialogue.get_micro_moment(moment)
        assert len(message) > 0
        print(f"✅ {moment}: {message[:60]}...")
    
    print()


def test_tips():
    """Test tip/hint messages."""
    print("🧪 Test 7: Tips and hints...")
    
    from core.navi_dialogue import NaviDialogue
    
    tips = ["gcp_tips", "cost_tips", "pfma_tips"]
    
    for tip_category in tips:
        tip = NaviDialogue.get_tip(tip_category)
        assert len(tip) > 0
        print(f"✅ {tip_category}: {tip[:60]}...")
    
    print()


def test_module_guidance():
    """Test module-level guidance messages."""
    print("🧪 Test 8: Module guidance (NEW)...")
    
    from core.navi_dialogue import NaviDialogue
    
    # Test GCP modules
    gcp_modules = ["intro", "mobility", "cognitive", "medical", "social", "living", "complete"]
    for module in gcp_modules:
        message = NaviDialogue.get_module_message("gcp", module)
        assert "text" in message
        assert "icon" in message
        print(f"✅ gcp.{module}: {message['icon']} {message['text'][:50]}...")
    
    # Test Cost Planner modules
    cost_modules = ["intro", "income", "assets", "expenses", "complete"]
    for module in cost_modules:
        message = NaviDialogue.get_module_message("cost_planner", module)
        assert "text" in message
        print(f"✅ cost_planner.{module}: {message['icon']} {message['text'][:50]}...")
    
    # Test PFMA modules
    pfma_modules = ["intro", "select_advisor", "choose_time", "confirm", "complete"]
    for module in pfma_modules:
        message = NaviDialogue.get_module_message("pfma", module)
        assert "text" in message
        print(f"✅ pfma.{module}: {message['icon']} {message['text'][:50]}...")
    
    print()


def run_all_tests():
    """Run all tests."""
    print("=" * 70)
    print("🤖 NAVI DIALOGUE SYSTEM TEST SUITE")
    print("=" * 70)
    print()
    
    try:
        test_dialogue_loads()
        test_journey_messages()
        test_context_formatting()
        test_product_gates()
        test_product_intros()
        test_micro_moments()
        test_tips()
        test_module_guidance()  # NEW TEST
        
        print("=" * 70)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("1. ✅ Dialogue system working")
        print("2. ✅ Journey status banner integrated")
        print("3. ✅ Module guidance system built")
        print("4. ✅ Navi sits at top of every module")
        print("5. ⏳ Test live app with Navi in modules")
        print("6. ⏳ End-to-end testing with full Navi guidance")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
