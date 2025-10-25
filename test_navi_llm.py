"""
Test and Demo Script for Navi LLM Enhancement

This script demonstrates the enhanced Navi capabilities with LLM-powered
contextual advice generation. It can be run directly to test the system
or used to enable LLM features in the app.

Usage:
    python test_navi_llm.py [mode]
    
Modes:
    - off: Static dialogue only (default)
    - shadow: LLM runs in background, logs results, shows static
    - assist: LLM provides additional context alongside static
    - adjust: LLM fully replaces static with dynamic advice
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def set_llm_mode(mode: str = "adjust"):
    """Set the LLM feature flag mode."""
    valid_modes = ["off", "shadow", "assist", "adjust"]
    if mode not in valid_modes:
        print(f"Invalid mode '{mode}'. Valid modes: {valid_modes}")
        return False
        
    os.environ["FEATURE_LLM_NAVI"] = mode
    print(f"✅ Set FEATURE_LLM_NAVI to '{mode}'")
    return True

def test_navi_context_building():
    """Test building Navi context from mock data."""
    print("\n🧪 Testing Navi Context Building...")
    
    try:
        from ai.navi_llm_engine import NaviContext, build_navi_context_from_session
        
        # Test context creation
        context = NaviContext(
            journey_phase="in_progress",
            current_location="gcp",
            progress_percent=65,
            user_name="Test User",
            is_authenticated=True,
            care_tier="assisted_living",
            care_confidence=0.85,
            key_flags=["moderate_mobility", "falls_multiple"],
            estimated_cost=4500,
            cost_concern_level="medium",
            has_financial_profile=True
        )
        
        print(f"✅ Created NaviContext: {context.journey_phase}, {context.progress_percent}% complete")
        print(f"   Care tier: {context.care_tier} (confidence: {context.care_confidence})")
        print(f"   Key flags: {context.key_flags}")
        print(f"   Cost estimate: ${context.estimated_cost:,}/month")
        
        return True
        
    except Exception as e:
        print(f"❌ Context building failed: {e}")
        return False

def test_llm_advice_generation():
    """Test LLM advice generation with mock context."""
    print("\n🤖 Testing LLM Advice Generation...")
    
    try:
        from ai.navi_llm_engine import NaviLLMEngine, NaviContext
        
        # Create test context
        context = NaviContext(
            journey_phase="in_progress",
            current_location="cost_planner",
            progress_percent=45,
            user_name="Sarah",
            is_authenticated=True,
            care_tier="assisted_living",
            care_confidence=0.78,
            key_flags=["moderate_mobility", "chronic_present"],
            estimated_cost=3800,
            has_financial_profile=True,
            stress_indicators=["overwhelmed"]
        )
        
        # Test advice generation
        advice = NaviLLMEngine.generate_advice(context)
        if advice:
            print(f"✅ Generated Advice:")
            print(f"   Title: {advice.title}")
            print(f"   Message: {advice.message}")
            print(f"   Guidance: {advice.guidance}")
            print(f"   Encouragement: {advice.encouragement}")
            print(f"   Tone: {advice.tone} | Priority: {advice.priority}")
        else:
            print("❌ No advice generated (LLM might be disabled)")
            
        # Test contextual tips
        tips = NaviLLMEngine.generate_contextual_tips(context)
        if tips:
            print(f"✅ Generated Tips:")
            for i, tip in enumerate(tips.tips, 1):
                print(f"   {i}. {tip}")
            print(f"   Why this matters: {tips.why_this_matters}")
            if tips.time_estimate:
                print(f"   Time estimate: {tips.time_estimate}")
        else:
            print("❌ No tips generated")
            
        return advice is not None or tips is not None
        
    except Exception as e:
        print(f"❌ LLM advice generation failed: {e}")
        return False

def test_dialogue_enhancement():
    """Test enhanced dialogue system integration."""
    print("\n💬 Testing Enhanced Dialogue System...")
    
    try:
        from core.navi_dialogue import NaviDialogue
        
        # Test journey message with LLM enhancement
        message = NaviDialogue.get_journey_message(
            phase="in_progress",
            is_authenticated=True,
            context={
                "name": "Sarah",
                "tier": "assisted_living",
                "monthly_cost": 3800
            }
        )
        
        if message:
            print(f"✅ Enhanced Journey Message:")
            print(f"   Text: {message.get('text', 'N/A')}")
            print(f"   Subtext: {message.get('subtext', 'N/A')}")
            print(f"   CTA: {message.get('cta', 'N/A')}")
            print(f"   Icon: {message.get('icon', 'N/A')}")
            
            # Check for LLM enhancement indicators
            if message.get('priority') or message.get('encouragement'):
                print("   🤖 LLM Enhancement detected!")
        else:
            print("❌ No message generated")
            
        # Test contextual boost
        boost = NaviDialogue.get_context_boost(
            phase="in_progress",
            context={"tier": "assisted_living", "progress": 65}
        )
        
        if boost:
            print(f"✅ Enhanced Context Boost ({len(boost)} items):")
            for item in boost[:3]:  # Show first 3
                print(f"   • {item}")
        else:
            print("❌ No context boost generated")
            
        return True
        
    except Exception as e:
        print(f"❌ Dialogue enhancement test failed: {e}")
        return False

def demo_feature_modes():
    """Demonstrate different LLM feature modes."""
    print("\n🎭 LLM Feature Modes Demo:")
    print("   off: Static dialogue only (JSON-based messages)")
    print("   shadow: LLM runs in background, logs results, shows static messages")
    print("   assist: LLM provides additional context tips alongside static messages")
    print("   adjust: LLM fully replaces static messages with dynamic contextual advice")
    print()
    
    modes = ["off", "shadow", "assist", "adjust"]
    for mode in modes:
        print(f"🔧 Mode '{mode}':")
        set_llm_mode(mode)
        
        # Quick test of mode behavior
        from core.flags import get_flag_value
        current_mode = get_flag_value("FEATURE_LLM_NAVI", "off")
        print(f"   Current flag value: {current_mode}")
        
        if mode == "off":
            print("   → Static dialogue only")
        elif mode == "shadow":
            print("   → LLM generates advice but doesn't display it")
        elif mode == "assist":
            print("   → Static dialogue + LLM contextual tips")
        elif mode == "adjust":
            print("   → Full LLM-powered dynamic dialogue")
        print()

def main():
    """Main demo function."""
    print("🚀 Navi LLM Enhancement Demo")
    print("=" * 50)
    
    # Parse command line argument for mode
    mode = "adjust"  # Default to full enhancement
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    
    # Set the LLM mode
    if not set_llm_mode(mode):
        return
    
    # Run tests
    tests = [
        test_navi_context_building,
        test_llm_advice_generation,
        test_dialogue_enhancement,
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Navi LLM enhancement is working.")
        print(f"💡 LLM mode is set to '{mode}' - you can now run the app to see enhanced Navi dialogue.")
        print("💡 To change modes, set the environment variable: export FEATURE_LLM_NAVI=adjust")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
        
    # Show feature modes demo
    if len(sys.argv) <= 1:  # Only show if no specific mode requested
        demo_feature_modes()

if __name__ == "__main__":
    main()