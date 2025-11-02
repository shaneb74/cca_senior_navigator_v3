"""
Debug script to check if Navi Intelligence is working

Run this to see what MCIP data exists and what Navi would say.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up minimal Streamlit environment
import streamlit as st

# Initialize session state
if not hasattr(st, 'session_state'):
    st.session_state = {}

print("\n" + "="*70)
print("  NAVI INTELLIGENCE DEBUG")
print("="*70)

# Check feature flag
from core.flags import get_flag_value
flag_value = get_flag_value("FEATURE_NAVI_INTELLIGENCE", "off")
print(f"\n✓ Feature Flag: FEATURE_NAVI_INTELLIGENCE = {flag_value}")

# Check MCIP data
from core.mcip import MCIP

print("\n" + "-"*70)
print("  MCIP DATA CHECK")
print("-"*70)

try:
    care_rec = MCIP.get_care_recommendation()
    if care_rec:
        print(f"\n✓ Care Recommendation Found:")
        print(f"   Tier: {care_rec.tier}")
        print(f"   Confidence: {care_rec.confidence:.0%}")
        print(f"   Flags ({len(care_rec.flags)} total):")
        for flag in care_rec.flags:
            if flag.get('active'):
                severity = flag.get('severity', 'N/A')
                print(f"      - {flag['type']} (active, severity: {severity})")
    else:
        print("\n✗ No Care Recommendation (GCP not completed?)")
except Exception as e:
    print(f"\n✗ Error getting care recommendation: {e}")

try:
    financial = MCIP.get_financial_profile()
    if financial:
        print(f"\n✓ Financial Profile Found:")
        print(f"   Monthly Cost: ${financial.estimated_monthly_cost:,.0f}")
        print(f"   Runway: {financial.runway_months} months")
        print(f"   Gap: ${financial.gap_amount:,.0f}")
    else:
        print("\n✗ No Financial Profile (Cost Planner not completed?)")
except Exception as e:
    print(f"\n✗ Error getting financial profile: {e}")

# Get Navi context
print("\n" + "-"*70)
print("  NAVI CONTEXT")
print("-"*70)

from core.navi import NaviOrchestrator

try:
    ctx = NaviOrchestrator.get_context(location="hub")
    print(f"\n✓ NaviContext Created:")
    print(f"   Location: {ctx.location}")
    print(f"   Progress: {ctx.progress.get('completed_count', 0)}/3 products")
    print(f"   Has Care Rec: {ctx.care_recommendation is not None}")
    print(f"   Has Financial: {ctx.financial_profile is not None}")
except Exception as e:
    print(f"\n✗ Error getting NaviContext: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test NaviCommunicator
print("\n" + "-"*70)
print("  NAVI INTELLIGENCE OUTPUT")
print("-"*70)

if flag_value == "on":
    from core.navi_intelligence import NaviCommunicator
    
    try:
        encouragement = NaviCommunicator.get_hub_encouragement(ctx)
        print(f"\n✓ Enhanced Encouragement:")
        print(f"   Icon: {encouragement['icon']}")
        print(f"   Text: {encouragement['text']}")
        print(f"   Status: {encouragement['status']}")
        
        reason = NaviCommunicator.get_dynamic_reason_text(ctx)
        print(f"\n✓ Dynamic Reason:")
        print(f"   {reason}")
        
    except Exception as e:
        print(f"\n✗ Error running NaviCommunicator: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"\n⚠️  Feature is {flag_value}, not 'on'")
    print("   Enhanced messages won't show")

print("\n" + "="*70)
print("  DIAGNOSIS")
print("="*70)

# Diagnosis
if flag_value != "on":
    print("\n❌ Feature flag is not 'on'")
    print("   Fix: Set FEATURE_NAVI_INTELLIGENCE=on in core/flags.py")
elif not ctx.care_recommendation:
    print("\n❌ No care recommendation data")
    print("   Fix: Complete Guided Care Plan (GCP)")
    print("   Make sure to answer questions that trigger flags:")
    print("   - Safety section: Select 'multiple falls'")
    print("   - Cognitive section: Select memory decline options")
else:
    active_flags = [f['type'] for f in ctx.care_recommendation.flags if f.get('active')]
    if not active_flags:
        print("\n⚠️  Care recommendation exists but no flags are active")
        print(f"   Tier: {ctx.care_recommendation.tier}")
        print(f"   Confidence: {ctx.care_recommendation.confidence:.0%}")
        print("   You might see high-confidence message instead of flag-specific")
    else:
        print("\n✅ Everything looks good!")
        print(f"   Active flags: {', '.join(active_flags)}")
        print("   Enhanced messages should be showing in Hub Lobby")

print("\n" + "="*70 + "\n")
