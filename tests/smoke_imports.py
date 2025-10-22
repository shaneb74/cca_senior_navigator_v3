"""Smoke tests to verify basic imports work."""
import sys
from pathlib import Path

# Add repo root to path
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))


def test_core_imports():
    """Test core module imports."""
    from core import flags
    from core import nav
    from core import state
    from core import ui
    from core import paths
    
    assert hasattr(flags, 'get_flag')
    assert hasattr(nav, 'load_navigation')
    assert hasattr(state, 'ensure_session')
    assert hasattr(ui, 'render_header')
    assert hasattr(paths, 'get_static')
    print("✓ Core imports successful")


def test_gcp_imports():
    """Test GCP v4 product imports."""
    from products.gcp_v4 import product
    from products.gcp_v4.modules.care_recommendation import logic
    from products.gcp_v4.modules.care_recommendation import config
    
    assert hasattr(product, 'render')
    assert hasattr(logic, 'compute_recommendation_category')
    assert hasattr(config, 'load_module_config')
    print("✓ GCP v4 imports successful")


def test_cost_planner_imports():
    """Test Cost Planner v2 product imports."""
    from products.cost_planner_v2 import product
    from products.cost_planner_v2 import intro
    from products.cost_planner_v2 import prepare_quick_estimate
    from products.cost_planner_v2.utils import cost_calculator
    
    assert hasattr(product, 'render')
    assert hasattr(intro, 'render_intro')
    assert hasattr(prepare_quick_estimate, 'render_quick_estimate_v2')
    assert hasattr(cost_calculator, 'CostCalculator')
    print("✓ Cost Planner v2 imports successful")


def test_other_product_imports():
    """Test other product imports."""
    from products import advisor_prep
    from products import pfma_v3
    from products import senior_trivia
    from products.resources_common import coming_soon
    
    assert hasattr(advisor_prep.product, 'render')
    assert hasattr(pfma_v3.product, 'render')
    assert hasattr(senior_trivia.product, 'render')
    assert hasattr(coming_soon, 'render_coming_soon')
    print("✓ Other product imports successful")


def test_hub_imports():
    """Test hub imports."""
    from hubs import concierge
    from hubs import learning
    from hubs import partners
    
    assert hasattr(concierge, 'render')
    assert hasattr(learning, 'render')
    assert hasattr(partners, 'render')
    print("✓ Hub imports successful")


def test_page_imports():
    """Test page imports."""
    from pages import welcome
    from pages import login
    from pages import _stubs
    
    assert hasattr(welcome, 'render')
    assert hasattr(login, 'render')
    assert hasattr(_stubs, 'render_welcome')
    print("✓ Page imports successful")


def test_paths_helper():
    """Test path helper functions."""
    from core.paths import get_static, get_gcp_module_path, get_config_path
    
    # Test static path
    static_path = get_static("images/test.png")
    assert "static/images/test.png" in static_path
    
    # Test GCP module path
    gcp_path = get_gcp_module_path()
    assert gcp_path == "products/gcp_v4/modules/care_recommendation/module.json"
    
    # Test config path
    config_path = get_config_path("nav.json")
    assert "config/nav.json" in config_path
    
    print("✓ Path helpers working correctly")


def run_all_tests():
    """Run all smoke tests."""
    print("\n=== Running Smoke Tests ===\n")
    
    try:
        test_core_imports()
        test_gcp_imports()
        test_cost_planner_imports()
        test_other_product_imports()
        test_hub_imports()
        test_page_imports()
        test_paths_helper()
        
        print("\n✅ All smoke tests passed!\n")
        return 0
    except Exception as e:
        print(f"\n❌ Smoke test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
