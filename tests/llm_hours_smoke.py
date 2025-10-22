"""
Smoke tests for hours/day suggestion (baseline + LLM refinement).

Tests 3 key scenarios:
- Case A: Light needs (<1h baseline)
- Case B: Heavy ADL needs (4-8h baseline)
- Case C: Risky behaviors or overnight (4-8h baseline, LLM may escalate to 24h)
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_baseline_hours_light():
    """Test Case A: Light needs → <1h baseline."""
    from ai.hours_schemas import HoursContext
    from ai.hours_engine import baseline_hours
    
    # Minimal needs: independent, no falls, no risky behaviors
    ctx = HoursContext(
        badls_count=0,
        iadls_count=1,  # Maybe help with housekeeping
        falls="none",
        mobility="independent",
        risky_behaviors=False,
        meds_complexity="simple",
        primary_support="family",
        overnight_needed=False,
        current_hours=None,
    )
    
    band = baseline_hours(ctx)
    
    print("\n" + "=" * 60)
    print("CASE A: Light needs")
    print("=" * 60)
    print(f"BADLs: {ctx.badls_count}/6")
    print(f"IADLs: {ctx.iadls_count}/8")
    print(f"Falls: {ctx.falls}")
    print(f"Mobility: {ctx.mobility}")
    print(f"Risky behaviors: {ctx.risky_behaviors}")
    print(f"Baseline band: {band}")
    
    assert band == "<1h", f"Expected <1h, got {band}"
    print("✅ Baseline suggests <1h (minimal support)")
    print("=" * 60)


def test_baseline_hours_heavy():
    """Test Case B: Heavy ADL needs → 4-8h baseline."""
    from ai.hours_schemas import HoursContext
    from ai.hours_engine import baseline_hours
    
    # High ADL needs: 3+ BADLs, multiple falls
    ctx = HoursContext(
        badls_count=3,  # Bathing, dressing, toileting
        iadls_count=2,  # Meals, meds
        falls="multiple",
        mobility="walker",
        risky_behaviors=False,
        meds_complexity="moderate",
        primary_support="family",
        overnight_needed=False,
        current_hours=None,
    )
    
    band = baseline_hours(ctx)
    
    print("\n" + "=" * 60)
    print("CASE B: Heavy ADL needs")
    print("=" * 60)
    print(f"BADLs: {ctx.badls_count}/6")
    print(f"IADLs: {ctx.iadls_count}/8")
    print(f"Falls: {ctx.falls}")
    print(f"Mobility: {ctx.mobility}")
    print(f"Risky behaviors: {ctx.risky_behaviors}")
    print(f"Baseline band: {band}")
    
    assert band == "4-8h", f"Expected 4-8h, got {band}"
    print("✅ Baseline suggests 4-8h (substantial support)")
    print("=" * 60)


def test_baseline_hours_risky():
    """Test Case C: Risky behaviors/overnight → 4-8h baseline (floor)."""
    from ai.hours_schemas import HoursContext
    from ai.hours_engine import baseline_hours
    
    # Risky behaviors: wandering, aggression (safety needs)
    ctx = HoursContext(
        badls_count=2,
        iadls_count=3,
        falls="once",
        mobility="independent",
        risky_behaviors=True,  # Wandering, aggression
        meds_complexity="moderate",
        primary_support="family",
        overnight_needed=False,
        current_hours=None,
    )
    
    band = baseline_hours(ctx)
    
    print("\n" + "=" * 60)
    print("CASE C: Risky behaviors (safety needs)")
    print("=" * 60)
    print(f"BADLs: {ctx.badls_count}/6")
    print(f"IADLs: {ctx.iadls_count}/8")
    print(f"Falls: {ctx.falls}")
    print(f"Mobility: {ctx.mobility}")
    print(f"Risky behaviors: {ctx.risky_behaviors}")
    print(f"Baseline band: {band}")
    
    assert band == "4-8h", f"Expected 4-8h (floor), got {band}"
    print("✅ Baseline suggests 4-8h (floor for safety needs)")
    print("⚠️  LLM may escalate to 24h if justified by specific behaviors")
    print("=" * 60)


def test_baseline_hours_overnight():
    """Test Case D: Overnight needed → 4-8h baseline (floor)."""
    from ai.hours_schemas import HoursContext
    from ai.hours_engine import baseline_hours
    
    # Overnight needs: full support required
    ctx = HoursContext(
        badls_count=4,
        iadls_count=5,
        falls="multiple",
        mobility="wheelchair",
        risky_behaviors=False,
        meds_complexity="complex",
        primary_support="paid",
        overnight_needed=True,  # Medical/safety needs overnight
        current_hours="24h",
    )
    
    band = baseline_hours(ctx)
    
    print("\n" + "=" * 60)
    print("CASE D: Overnight needed (full support)")
    print("=" * 60)
    print(f"BADLs: {ctx.badls_count}/6")
    print(f"IADLs: {ctx.iadls_count}/8")
    print(f"Falls: {ctx.falls}")
    print(f"Mobility: {ctx.mobility}")
    print(f"Overnight needed: {ctx.overnight_needed}")
    print(f"Current hours: {ctx.current_hours}")
    print(f"Baseline band: {band}")
    
    assert band == "4-8h", f"Expected 4-8h (floor), got {band}"
    print("✅ Baseline suggests 4-8h (floor for overnight needs)")
    print("⚠️  LLM may escalate to 24h based on medical complexity")
    print("=" * 60)


def test_llm_refinement_schema_validation():
    """Test LLM output schema validation (off-menu rejection)."""
    from ai.hours_schemas import HoursAdvice
    from pydantic import ValidationError
    
    print("\n" + "=" * 60)
    print("SCHEMA VALIDATION TEST")
    print("=" * 60)
    
    # Valid output
    try:
        advice = HoursAdvice(
            band="1-3h",
            reasons=["Needs help with 2 BADLs", "Mobility aid (walker)"],
            confidence=0.85,
        )
        print(f"✅ Valid band '1-3h' accepted")
        print(f"   Reasons: {advice.reasons}")
        print(f"   Confidence: {advice.confidence}")
    except ValidationError as e:
        print(f"❌ Unexpected validation error: {e}")
        raise
    
    # Invalid band (off-menu)
    try:
        HoursAdvice(
            band="2-4h",  # Not in allowed set
            reasons=["Test"],
            confidence=0.9,
        )
        print("❌ Invalid band '2-4h' was accepted (should have failed)")
        raise AssertionError("Off-menu band should be rejected")
    except ValidationError:
        print("✅ Invalid band '2-4h' rejected by schema")
    
    # Too many reasons (should clip to 3)
    advice = HoursAdvice(
        band="4-8h",
        reasons=["R1", "R2", "R3", "R4", "R5"],  # 5 reasons
        confidence=0.8,
    )
    assert len(advice.reasons) == 3, f"Expected 3 reasons, got {len(advice.reasons)}"
    print("✅ Reasons clipped to max 3")
    
    print("=" * 60)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("HOURS/DAY SUGGESTION SMOKE TESTS")
    print("=" * 60)
    
    test_baseline_hours_light()
    test_baseline_hours_heavy()
    test_baseline_hours_risky()
    test_baseline_hours_overnight()
    test_llm_refinement_schema_validation()
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED ✅")
    print("=" * 60)
