#!/usr/bin/env python3
"""
Debug synthetic data processing in NavigatorDataReader
"""

import json
from shared.data_access.navigator_reader import NavigatorDataReader

def main():
    """Debug data processing"""
    print("🔍 Debugging synthetic data processing...")
    
    # Read a synthetic file directly
    with open("data/users/anon_synthetic_aug2025_001.json", 'r') as f:
        raw_data = json.load(f)
    
    print(f"\n📋 RAW DATA SAMPLE:")
    print(f"   User ID: {raw_data.get('uid')}")
    print(f"   Person Name: {raw_data.get('person_name')}")
    print(f"   Estimated Monthly Cost: {raw_data.get('estimated_monthly_cost')}")
    print(f"   GCP Care Recommendation: {raw_data.get('gcp_care_recommendation')}")
    
    if "mcip_contracts" in raw_data:
        contracts = raw_data["mcip_contracts"]
        print(f"\n🔧 MCIP CONTRACTS:")
        
        if "care_recommendation" in contracts:
            care_contract = contracts["care_recommendation"]
            print(f"   Care Status: {care_contract.get('status')}")
            print(f"   Care Tier: {care_contract.get('tier')}")
            print(f"   Confidence: {care_contract.get('confidence')}")
        
        if "financial_profile" in contracts:
            financial_contract = contracts["financial_profile"]
            print(f"   Financial Status: {financial_contract.get('status')}")
            print(f"   Monthly Cost: {financial_contract.get('monthly_cost')}")
    
    # Test NavigatorDataReader processing
    reader = NavigatorDataReader()
    customers = reader.get_all_customers()
    
    synthetic_customer = None
    for customer in customers:
        if customer.get('user_id') == 'anon_synthetic_aug2025_001':
            synthetic_customer = customer
            break
    
    if synthetic_customer:
        print(f"\n📊 PROCESSED BY NAVIGATOR READER:")
        print(f"   User ID: {synthetic_customer.get('user_id')}")
        print(f"   Person Name: {synthetic_customer.get('person_name')}")
        print(f"   Journey Stage: {synthetic_customer.get('journey_stage')}")
        print(f"   Care Recommendation: {synthetic_customer.get('care_recommendation')}")
        print(f"   GCP Assessment: {synthetic_customer.get('has_gcp_assessment')}")
        print(f"   Cost Plan: {synthetic_customer.get('has_cost_plan')}")
        print(f"   Monthly Cost: {synthetic_customer.get('monthly_cost_estimate')}")
        print(f"   Assessment Summary: {synthetic_customer.get('assessment_summary')}")
        print(f"   Cost Summary: {synthetic_customer.get('cost_summary')}")
    else:
        print(f"\n❌ Customer not found in processed data!")

if __name__ == "__main__":
    main()