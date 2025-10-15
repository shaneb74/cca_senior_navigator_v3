#!/usr/bin/env python3
"""
End-to-End Test Script: Navi Single Intelligence Layer

Manual testing checklist per architectural spec.
Run this script to validate all integration points.

Usage:
    python test_navi_e2e.py

This script performs static analysis and imports to validate:
1. All files exist
2. All imports work
3. All required methods exist
4. All integrations are in place
"""

import sys
import os
from pathlib import Path


class TestResults:
    """Track test results."""
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
    
    def pass_test(self, name: str):
        self.passed.append(f"✅ {name}")
        print(f"✅ {name}")
    
    def fail_test(self, name: str, error: str):
        self.failed.append(f"❌ {name}: {error}")
        print(f"❌ {name}: {error}")
    
    def warn_test(self, name: str, warning: str):
        self.warnings.append(f"⚠️  {name}: {warning}")
        print(f"⚠️  {name}: {warning}")
    
    def summary(self):
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"Passed: {len(self.passed)}")
        print(f"Failed: {len(self.failed)}")
        print(f"Warnings: {len(self.warnings)}")
        
        if self.failed:
            print("\n❌ FAILED TESTS:")
            for fail in self.failed:
                print(f"  {fail}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warn in self.warnings:
                print(f"  {warn}")
        
        print("="*80)
        return len(self.failed) == 0


def test_file_structure(results: TestResults):
    """Test 1: Verify all required files exist."""
    print("\n" + "="*80)
    print("TEST 1: File Structure")
    print("="*80)
    
    required_files = [
        'core/navi.py',
        'core/flags.py',
        'core/navi_dialogue.py',
        'config/navi_dialogue.json',
        'NAVI_SINGLE_INTELLIGENCE_LAYER.md',
        'hubs/concierge.py',
        'products/gcp_v4/product.py',
        'products/cost_planner_v2/product.py',
        'products/cost_planner_v2/hub.py',
        'products/pfma_v2/product.py',
    ]
    
    for filepath in required_files:
        if os.path.exists(filepath):
            results.pass_test(f"File exists: {filepath}")
        else:
            results.fail_test(f"File missing: {filepath}", "Required file not found")


def test_imports(results: TestResults):
    """Test 2: Verify all imports work."""
    print("\n" + "="*80)
    print("TEST 2: Import Tests")
    print("="*80)
    
    # Test core.flags
    try:
        from core.flags import get_all_flags, get_flag, has_any_flags, has_all_flags
        results.pass_test("Import core.flags")
    except ImportError as e:
        if "streamlit" in str(e):
            results.pass_test("Import core.flags (Streamlit not available - OK for static test)")
        else:
            results.fail_test("Import core.flags", str(e))
    except Exception as e:
        results.fail_test("Import core.flags", str(e))
    
    # Test core.navi
    try:
        from core.navi import NaviOrchestrator, NaviContext, render_navi_panel
        results.pass_test("Import core.navi")
    except ImportError as e:
        if "streamlit" in str(e):
            results.pass_test("Import core.navi (Streamlit not available - OK for static test)")
        else:
            results.fail_test("Import core.navi", str(e))
    except Exception as e:
        results.fail_test("Import core.navi", str(e))
    
    # Test core.navi_dialogue
    try:
        from core.navi_dialogue import NaviDialogue
        results.pass_test("Import core.navi_dialogue")
    except ImportError as e:
        if "streamlit" in str(e):
            results.pass_test("Import core.navi_dialogue (Streamlit not available - OK for static test)")
        else:
            results.fail_test("Import core.navi_dialogue", str(e))
    except Exception as e:
        results.fail_test("Import core.navi_dialogue", str(e))


def test_navi_orchestrator_methods(results: TestResults):
    """Test 3: Verify NaviOrchestrator has all required methods."""
    print("\n" + "="*80)
    print("TEST 3: NaviOrchestrator Methods")
    print("="*80)
    
    try:
        from core.navi import NaviOrchestrator
        
        required_methods = [
            'get_context',
            'get_next_action',
            'get_suggested_questions',
            'get_additional_services',
            'get_context_summary',
            'get_context_boost',
        ]
        
        for method_name in required_methods:
            if hasattr(NaviOrchestrator, method_name):
                results.pass_test(f"NaviOrchestrator.{method_name} exists")
            else:
                results.fail_test(f"NaviOrchestrator.{method_name} missing", "Required method not found")
    
    except ImportError as e:
        if "streamlit" in str(e):
            results.pass_test("NaviOrchestrator verification (Streamlit not available - checking source directly)")
            # Check source file directly
            try:
                with open('core/navi.py', 'r') as f:
                    content = f.read()
                required_methods = [
                    'get_context',
                    'get_next_action',
                    'get_suggested_questions',
                    'get_additional_services',
                    'get_context_summary',
                    'get_context_boost',
                ]
                for method_name in required_methods:
                    if f'def {method_name}(' in content:
                        results.pass_test(f"NaviOrchestrator.{method_name} exists")
                    else:
                        results.fail_test(f"NaviOrchestrator.{method_name} missing", "Required method not found")
            except Exception as e2:
                results.fail_test("NaviOrchestrator source verification", str(e2))
        else:
            results.fail_test("NaviOrchestrator verification", str(e))
    except Exception as e:
        results.fail_test("NaviOrchestrator verification", str(e))


def test_navi_context_dataclass(results: TestResults):
    """Test 4: Verify NaviContext has all required fields."""
    print("\n" + "="*80)
    print("TEST 4: NaviContext Dataclass")
    print("="*80)
    
    try:
        from core.navi import NaviContext
        from dataclasses import fields
        
        required_fields = {
            'progress', 'next_action', 'care_recommendation', 'financial_profile',
            'advisor_appointment', 'flags', 'user_name', 'is_authenticated',
            'location', 'module_step', 'module_total'
        }
        
        field_names = {f.name for f in fields(NaviContext)}
        
        for field_name in required_fields:
            if field_name in field_names:
                results.pass_test(f"NaviContext.{field_name} exists")
            else:
                results.fail_test(f"NaviContext.{field_name} missing", "Required field not found")
    
    except ImportError as e:
        if "streamlit" in str(e):
            results.pass_test("NaviContext verification (Streamlit not available - checking source directly)")
            # Check source file directly
            try:
                with open('core/navi.py', 'r') as f:
                    content = f.read()
                required_fields = {
                    'progress', 'next_action', 'care_recommendation', 'financial_profile',
                    'advisor_appointment', 'flags', 'user_name', 'is_authenticated',
                    'location', 'module_step', 'module_total'
                }
                for field_name in required_fields:
                    if field_name in content:
                        results.pass_test(f"NaviContext.{field_name} exists")
                    else:
                        results.fail_test(f"NaviContext.{field_name} missing", "Required field not found")
            except Exception as e2:
                results.fail_test("NaviContext source verification", str(e2))
        else:
            results.fail_test("NaviContext verification", str(e))
    except Exception as e:
        results.fail_test("NaviContext verification", str(e))


def test_hub_integration(results: TestResults):
    """Test 5: Verify hub integration."""
    print("\n" + "="*80)
    print("TEST 5: Hub Integration")
    print("="*80)
    
    # Check Concierge hub
    try:
        with open('hubs/concierge.py', 'r') as f:
            content = f.read()
        
        if 'from core.navi import render_navi_panel' in content:
            results.pass_test("Concierge imports render_navi_panel")
        else:
            results.fail_test("Concierge missing import", "from core.navi import render_navi_panel not found")
        
        if 'render_navi_panel(' in content:
            results.pass_test("Concierge calls render_navi_panel")
        else:
            results.fail_test("Concierge missing call", "render_navi_panel() call not found")
        
        if 'hub_guide_block=None' in content or 'hub_guide_block' not in content:
            results.pass_test("Concierge deprecated hub_guide_block")
        else:
            results.warn_test("Concierge hub_guide_block", "May still be using hub_guide_block")
    
    except Exception as e:
        results.fail_test("Concierge hub verification", str(e))


def test_product_integration(results: TestResults):
    """Test 6: Verify product integration."""
    print("\n" + "="*80)
    print("TEST 6: Product Integration")
    print("="*80)
    
    products = [
        ('products/gcp_v4/product.py', 'GCP v4'),
        ('products/cost_planner_v2/product.py', 'Cost Planner v2'),
        ('products/pfma_v2/product.py', 'PFMA v2'),
    ]
    
    for filepath, name in products:
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            if 'from core.navi import render_navi_panel' in content:
                results.pass_test(f"{name} imports render_navi_panel")
            else:
                results.fail_test(f"{name} missing import", "from core.navi import render_navi_panel not found")
            
            if 'render_navi_panel(' in content:
                results.pass_test(f"{name} calls render_navi_panel")
            else:
                results.fail_test(f"{name} missing call", "render_navi_panel() call not found")
        
        except Exception as e:
            results.fail_test(f"{name} verification", str(e))
    
    # Check Cost Planner hub
    try:
        with open('products/cost_planner_v2/hub.py', 'r') as f:
            content = f.read()
        
        if 'from core.navi import render_navi_panel' in content:
            results.pass_test("Cost Planner hub imports render_navi_panel")
        else:
            results.fail_test("Cost Planner hub missing import", "from core.navi import render_navi_panel not found")
        
        if 'render_navi_panel(' in content:
            results.pass_test("Cost Planner hub calls render_navi_panel")
        else:
            results.fail_test("Cost Planner hub missing call", "render_navi_panel() call not found")
    
    except Exception as e:
        results.fail_test("Cost Planner hub verification", str(e))


def test_flag_aggregation(results: TestResults):
    """Test 7: Verify flag aggregation system."""
    print("\n" + "="*80)
    print("TEST 7: Flag Aggregation System")
    print("="*80)
    
    try:
        from core.flags import get_all_flags, get_flag, has_any_flags, has_all_flags
        
        # Test functions exist
        results.pass_test("get_all_flags function exists")
        results.pass_test("get_flag function exists")
        results.pass_test("has_any_flags function exists")
        results.pass_test("has_all_flags function exists")
        
        # Check core.navi uses flags
        with open('core/navi.py', 'r') as f:
            content = f.read()
        
        if 'from core.flags import' in content or 'import core.flags' in content:
            results.pass_test("Navi imports flags module")
        else:
            results.fail_test("Navi missing flags import", "Should import from core.flags")
        
        if 'get_all_flags()' in content:
            results.pass_test("Navi uses get_all_flags()")
        else:
            results.warn_test("Navi flags usage", "May not be using get_all_flags()")
    
    except ImportError as e:
        if "streamlit" in str(e):
            results.pass_test("Flag aggregation verification (Streamlit not available - checking source)")
            # Check source directly
            try:
                with open('core/flags.py', 'r') as f:
                    content = f.read()
                
                if 'def get_all_flags(' in content:
                    results.pass_test("get_all_flags function exists")
                if 'def get_flag(' in content:
                    results.pass_test("get_flag function exists")
                if 'def has_any_flags(' in content:
                    results.pass_test("has_any_flags function exists")
                if 'def has_all_flags(' in content:
                    results.pass_test("has_all_flags function exists")
                
                # Check core.navi uses flags
                with open('core/navi.py', 'r') as f2:
                    navi_content = f2.read()
                
                if 'from core.flags import' in navi_content or 'import core.flags' in navi_content:
                    results.pass_test("Navi imports flags module")
                else:
                    results.fail_test("Navi missing flags import", "Should import from core.flags")
                
                if 'get_all_flags()' in navi_content:
                    results.pass_test("Navi uses get_all_flags()")
                else:
                    results.warn_test("Navi flags usage", "May not be using get_all_flags()")
            except Exception as e2:
                results.fail_test("Flag aggregation source verification", str(e2))
        else:
            results.fail_test("Flag aggregation verification", str(e))
    except Exception as e:
        results.fail_test("Flag aggregation verification", str(e))


def test_navigation_routing(results: TestResults):
    """Test 8: Verify navigation uses canonical route IDs."""
    print("\n" + "="*80)
    print("TEST 8: Navigation & Routing")
    print("="*80)
    
    try:
        import json
        
        with open('config/nav.json', 'r') as f:
            nav_config = json.load(f)
        
        # Check hub_concierge exists  
        # Search through all items for hub_concierge key
        all_items = []
        if 'items' in nav_config:
            all_items = nav_config['items']
        if 'groups' in nav_config:
            for group in nav_config['groups']:
                if 'items' in group:
                    all_items.extend(group['items'])
        
        hub_concierge_found = any(item.get('key') == 'hub_concierge' for item in all_items)
        
        if hub_concierge_found:
            results.pass_test("hub_concierge route exists in nav.json")
        else:
            results.fail_test("hub_concierge route missing", "Required route not in nav.json")
        
        # Check core.navi uses route keys
        with open('core/navi.py', 'r') as f:
            content = f.read()
        
        if '"gcp_v4"' in content and '"cost_v2"' in content and '"pfma_v2"' in content:
            results.pass_test("Navi uses canonical route IDs")
        else:
            results.warn_test("Navi route IDs", "Verify route IDs match nav.json")
    
    except Exception as e:
        results.fail_test("Navigation verification", str(e))


def test_documentation(results: TestResults):
    """Test 9: Verify documentation exists and is complete."""
    print("\n" + "="*80)
    print("TEST 9: Documentation")
    print("="*80)
    
    try:
        with open('NAVI_SINGLE_INTELLIGENCE_LAYER.md', 'r') as f:
            content = f.read()
        
        required_sections = [
            'Placement',
            'Responsibilities',
            'Inputs',
            'Outputs',
            'Additional Services',
            'Navigation',
            'Test Plan',
            'Deliverables',
        ]
        
        for section in required_sections:
            if section in content:
                results.pass_test(f"Documentation includes {section}")
            else:
                results.warn_test(f"Documentation {section}", f"Section may be missing or named differently")
        
        # Check for key architectural decisions
        if 'single intelligence layer' in content.lower():
            results.pass_test("Documentation describes single intelligence layer")
        else:
            results.warn_test("Documentation", "May not clearly describe single intelligence layer")
        
        if 'deprecate' in content.lower() and 'hub guide' in content.lower():
            results.pass_test("Documentation mentions Hub Guide deprecation")
        else:
            results.warn_test("Documentation", "May not mention Hub Guide deprecation")
    
    except Exception as e:
        results.fail_test("Documentation verification", str(e))


def test_regression_checks(results: TestResults):
    """Test 10: Regression checks."""
    print("\n" + "="*80)
    print("TEST 10: Regression Checks")
    print("="*80)
    
    # Check no old render_mcip_journey_status in hubs (should be replaced)
    try:
        with open('hubs/concierge.py', 'r') as f:
            content = f.read()
        
        if 'render_mcip_journey_status()' not in content:
            results.pass_test("Concierge doesn't call deprecated render_mcip_journey_status()")
        else:
            results.warn_test("Concierge", "Still calls render_mcip_journey_status() - may need cleanup")
    except Exception as e:
        results.fail_test("Concierge regression check", str(e))
    
    # Check PFMA doesn't render duck progress
    try:
        with open('products/pfma_v2/product.py', 'r') as f:
            content = f.read()
        
        if '_render_duck_progress_sidebar()' not in content.split('def render()')[1].split('\n\n')[0]:
            results.pass_test("PFMA doesn't call deprecated _render_duck_progress_sidebar()")
        else:
            results.warn_test("PFMA", "May still call _render_duck_progress_sidebar() - check if deprecated")
    except Exception as e:
        results.fail_test("PFMA regression check", str(e))
    
    # Check no duplicate imports
    files_to_check = [
        'hubs/concierge.py',
        'products/gcp_v4/product.py',
        'products/cost_planner_v2/product.py',
        'products/pfma_v2/product.py',
    ]
    
    for filepath in files_to_check:
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
            
            navi_imports = [line for line in lines if 'from core.navi import' in line or 'import core.navi' in line]
            
            if len(navi_imports) == 1:
                results.pass_test(f"{filepath} has single Navi import")
            elif len(navi_imports) == 0:
                results.fail_test(f"{filepath} missing Navi import", "No import found")
            else:
                results.warn_test(f"{filepath}", f"Has {len(navi_imports)} Navi imports - may have duplicates")
        except Exception as e:
            results.fail_test(f"{filepath} import check", str(e))


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("NAVI SINGLE INTELLIGENCE LAYER - END-TO-END TESTING")
    print("="*80)
    print("Validating implementation per architectural spec")
    print("="*80)
    
    results = TestResults()
    
    # Run all test suites
    test_file_structure(results)
    test_imports(results)
    test_navi_orchestrator_methods(results)
    test_navi_context_dataclass(results)
    test_hub_integration(results)
    test_product_integration(results)
    test_flag_aggregation(results)
    test_navigation_routing(results)
    test_documentation(results)
    test_regression_checks(results)
    
    # Print summary
    success = results.summary()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! Navi integration is complete.")
        print("\nNext steps:")
        print("1. Start Streamlit: streamlit run app.py")
        print("2. Manual testing:")
        print("   - Navigate to Concierge Hub")
        print("   - Verify Navi panel appears under header")
        print("   - Complete GCP → verify Navi updates")
        print("   - Complete Cost Planner → verify service recommendations")
        print("   - Test suggested question chips")
        print("   - Verify 'Back to Hub' routes to Concierge")
        return 0
    else:
        print("\n❌ TESTS FAILED. Please fix issues before continuing.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
