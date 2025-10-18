#!/usr/bin/env python3
"""
Script to add 'level' property to assessment fields for Basic/Advanced toggle.
Reorganizes Income and Assets assessments per requirements.
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
ASSESSMENTS_DIR = PROJECT_ROOT / "products/cost_planner_v2/modules/assessments"


def update_income_json():
    """Update Income assessment with level property and restructured sections."""
    
    income_config = {
        "key": "income",
        "title": "Income Sources",
        "icon": "💰",
        "description": "Monthly income from all sources",
        "estimated_time": "5-7 min",
        "required": True,
        "sort_order": 1,
        "sections": [
            {
                "id": "intro",
                "type": "intro",
                "title": "Income Assessment",
                "icon": "💰",
                "help_text": "Let's capture your income. Use Basic for a quick total or Advanced if you want to break it down.",
                "fields": [],
                "info_boxes": [
                    {
                        "type": "info",
                        "message": "💡 You can save and come back anytime. Your progress is automatically tracked."
                    }
                ]
            },
            {
                "id": "household_context",
                "title": "Household Context",
                "icon": "👥",
                "help_text": "Tell me about anyone who shares income or expenses with you.",
                "layout": "single_column",
                "fields": [
                    {
                        "key": "has_partner",
                        "label": "Do you have a spouse or partner involved in your finances?",
                        "type": "select",
                        "required": False,
                        "level": "basic",
                        "options": [
                            {"value": "no_partner", "label": "No partner"},
                            {"value": "partner_separate", "label": "Yes, but we keep finances separate"},
                            {"value": "partner_shared", "label": "Yes, we share income and expenses"}
                        ],
                        "default": "no_partner",
                        "help": "This helps me understand whether to account for shared household income."
                    },
                    {
                        "key": "partner_income_monthly",
                        "label": "Partner's Monthly Contribution Toward Care",
                        "type": "currency",
                        "required": False,
                        "level": "basic",
                        "min": 0,
                        "max": 50000,
                        "step": 100,
                        "default": 0,
                        "help": "If your spouse/partner will help cover care, enter the amount they can reliably contribute each month.",
                        "visible_if": {
                            "field": "has_partner",
                            "equals": "partner_shared"
                        }
                    },
                    {
                        "key": "shared_finance_notes",
                        "label": "Anything important about how you share finances?",
                        "type": "textarea",
                        "required": False,
                        "level": "advanced",
                        "help": "Mention separate accounts, legal restrictions, or other details that affect how shared income can be used.",
                        "visible_if": {
                            "field": "has_partner",
                            "not_equals": "no_partner"
                        }
                    }
                ],
                "info_boxes": [
                    {
                        "type": "info",
                        "message": "👥 If you keep finances separate, note what is realistically available for care so we can build the right plan."
                    }
                ]
            },
            {
                "id": "social_security_pensions",
                "title": "Social Security & Pensions",
                "icon": "🏛️",
                "help_text": "Monthly Social Security and pension income",
                "layout": "single_column",
                "fields": [
                    {
                        "key": "ss_monthly",
                        "label": "Social Security (Monthly)",
                        "type": "currency",
                        "required": False,
                        "level": "basic",
                        "min": 0,
                        "max": 5000,
                        "step": 10,
                        "default": 0,
                        "help": "Total monthly benefits after deductions"
                    },
                    {
                        "key": "pension_monthly",
                        "label": "Pension (Monthly)",
                        "type": "currency",
                        "required": False,
                        "level": "basic",
                        "min": 0,
                        "max": 20000,
                        "step": 100,
                        "default": 0,
                        "help": "Monthly pension income"
                    }
                ],
                "info_boxes": [
                    {
                        "type": "info",
                        "message": "📊 Social Security: Age 62 (reduced) vs. 66-67 (full) vs. 70 (max, up to 30% more). Average 2024: $1,907/month. Pension: Lifetime guaranteed income is valuable for care planning."
                    }
                ]
            },
            {
                "id": "employment_other",
                "title": "Employment & Other Income",
                "icon": "💼",
                "help_text": "Current employment and other regular monthly income",
                "layout": "single_column",
                "fields": [
                    {
                        "key": "employment_income",
                        "label": "Employment Income (Monthly)",
                        "type": "currency",
                        "required": False,
                        "level": "basic",
                        "min": 0,
                        "max": 50000,
                        "step": 100,
                        "default": 0,
                        "help": "Net monthly income from employment or self-employment"
                    },
                    {
                        "key": "other_income",
                        "label": "Other Monthly Income",
                        "type": "currency",
                        "required": False,
                        "level": "basic",
                        "min": 0,
                        "max": 50000,
                        "step": 100,
                        "default": 0,
                        "help": "Any other regular monthly income not listed above"
                    },
                    {
                        "key": "employment_status",
                        "label": "Employment Status",
                        "type": "select",
                        "required": False,
                        "level": "advanced",
                        "options": [
                            {"value": "not_employed", "label": "Not employed"},
                            {"value": "part_time", "label": "Part-time employment"},
                            {"value": "full_time", "label": "Full-time employment"},
                            {"value": "self_employed", "label": "Self-employed"}
                        ],
                        "default": "not_employed",
                        "help": "Current employment situation"
                    }
                ],
                "info_boxes": [
                    {
                        "type": "info",
                        "message": "⚠️ Social Security impact: Earnings above $22,320 (2024) may reduce SS benefits if claiming before full retirement age."
                    }
                ]
            },
            {
                "id": "additional_income",
                "title": "Additional Income (Advanced)",
                "icon": "💵",
                "help_text": "Detailed breakdown of additional income sources",
                "layout": "two_column",
                "fields": [
                    {
                        "key": "annuity_monthly",
                        "label": "Annuity (Monthly)",
                        "type": "currency",
                        "required": False,
                        "level": "advanced",
                        "min": 0,
                        "max": 20000,
                        "step": 100,
                        "default": 0,
                        "help": "Monthly annuity payments",
                        "column": 1
                    },
                    {
                        "key": "retirement_distributions_monthly",
                        "label": "IRA/401(k) Distributions (Monthly)",
                        "type": "currency",
                        "required": False,
                        "level": "advanced",
                        "min": 0,
                        "max": 50000,
                        "step": 100,
                        "default": 0,
                        "help": "Monthly withdrawals from retirement accounts",
                        "column": 1
                    },
                    {
                        "key": "dividends_interest_monthly",
                        "label": "Dividends & Interest (Monthly)",
                        "type": "currency",
                        "required": False,
                        "level": "advanced",
                        "min": 0,
                        "max": 50000,
                        "step": 100,
                        "default": 0,
                        "help": "Monthly income from investments",
                        "column": 2
                    },
                    {
                        "key": "rental_income_monthly",
                        "label": "Rental Income (Monthly)",
                        "type": "currency",
                        "required": False,
                        "level": "advanced",
                        "min": 0,
                        "max": 50000,
                        "step": 100,
                        "default": 0,
                        "help": "Net monthly income from rental properties",
                        "column": 2
                    },
                    {
                        "key": "alimony_support_monthly",
                        "label": "Alimony/Support (Monthly)",
                        "type": "currency",
                        "required": False,
                        "level": "advanced",
                        "min": 0,
                        "max": 50000,
                        "step": 100,
                        "default": 0,
                        "help": "Monthly alimony or support payments received",
                        "column": 1
                    },
                    {
                        "key": "ltc_insurance_monthly",
                        "label": "Long-Term Care Insurance Benefits",
                        "type": "currency",
                        "required": False,
                        "level": "advanced",
                        "min": 0,
                        "max": 50000,
                        "step": 100,
                        "default": 0,
                        "help": "Monthly payout from long-term care insurance",
                        "column": 2
                    },
                    {
                        "key": "family_support_monthly",
                        "label": "Family Support (Monthly)",
                        "type": "currency",
                        "required": False,
                        "level": "advanced",
                        "min": 0,
                        "max": 50000,
                        "step": 100,
                        "default": 0,
                        "help": "Contributions from family for care costs",
                        "column": 1
                    }
                ],
                "info_boxes": [
                    {
                        "type": "info",
                        "message": "💡 Breaking down income sources helps identify guaranteed vs. variable income for better care planning."
                    }
                ]
            },
            {
                "id": "results",
                "type": "results",
                "title": "Income Assessment Complete",
                "icon": "✅",
                "fields": []
            }
        ],
        "summary": {
            "type": "calculated",
            "label": "Total Monthly Income",
            "formula": "sum(ss_monthly, pension_monthly, employment_income, other_income, annuity_monthly, retirement_distributions_monthly, dividends_interest_monthly, rental_income_monthly, alimony_support_monthly, ltc_insurance_monthly, family_support_monthly, partner_income_monthly)",
            "display_format": "${:,.0f}/month"
        },
        "output_contract": {
            "has_partner": "string",
            "partner_income_monthly": "number",
            "shared_finance_notes": "string",
            "ss_monthly": "number",
            "pension_monthly": "number",
            "employment_status": "string",
            "employment_income": "number",
            "other_income": "number",
            "annuity_monthly": "number",
            "retirement_distributions_monthly": "number",
            "dividends_interest_monthly": "number",
            "rental_income_monthly": "number",
            "alimony_support_monthly": "number",
            "ltc_insurance_monthly": "number",
            "family_support_monthly": "number",
            "total_monthly_income": "calculated"
        }
    }
    
    output_path = ASSESSMENTS_DIR / "income.json"
    with open(output_path, 'w') as f:
        json.dump(income_config, f, indent=2)
    
    print(f"✅ Updated {output_path}")


def update_assets_json():
    """Update Assets assessment with level property and restructured sections."""
    
    assets_config = {
        "key": "assets",
        "title": "Assets & Resources",
        "icon": "🏦",
        "description": "Available financial assets and resources",
        "estimated_time": "6-8 min",
        "required": True,
        "sort_order": 2,
        "sections": [
            {
                "id": "intro",
                "type": "intro",
                "title": "Assets Assessment",
                "icon": "🏦",
                "help_text": "Estimate your assets. Basic gives a quick snapshot; Advanced lets you add detail.",
                "fields": [],
                "info_boxes": [
                    {
                        "type": "info",
                        "message": "💡 Inputs stay visible. You can save and come back anytime."
                    }
                ]
            },
            {
                "id": "household_context",
                "title": "Household Context",
                "icon": "👥",
                "help_text": "Let me know if anyone else shares ownership or limits how assets can be used.",
                "layout": "single_column",
                "fields": [
                    {
                        "key": "asset_has_partner",
                        "label": "Do you share assets with a spouse or partner?",
                        "type": "select",
                        "required": False,
                        "level": "basic",
                        "options": [
                            {"value": "no_partner", "label": "No, assets are only in my name"},
                            {"value": "partner_separate", "label": "Yes, but we keep finances separate"},
                            {"value": "partner_shared", "label": "Yes, we pool assets for care decisions"}
                        ],
                        "default": "no_partner",
                        "help": "Helps me understand which resources are truly available for care."
                    },
                    {
                        "key": "asset_legal_restrictions",
                        "label": "Any legal or family restrictions on using these assets?",
                        "type": "textarea",
                        "required": False,
                        "level": "advanced",
                        "help": "Example: community property rules, assets earmarked for a spouse, or power-of-attorney considerations.",
                        "visible_if": {
                            "field": "asset_has_partner",
                            "not_equals": "no_partner"
                        }
                    }
                ],
                "info_boxes": [
                    {
                        "type": "info",
                        "message": "👥 If assets are co-owned, note who must approve decisions. This prevents surprises when planning how to pay for care."
                    }
                ]
            },
            {
                "id": "liquid_assets",
                "title": "Liquid Assets",
                "icon": "🏦",
                "help_text": "Cash and easily accessible funds",
                "layout": "two_column",
                "fields": [
                    {
                        "key": "cash_liquid_total",
                        "label": "Checking & Savings (Total)",
                        "type": "currency",
                        "required": False,
                        "level": "basic",
                        "min": 0,
                        "max": 10000000,
                        "step": 1000,
                        "default": 0,
                        "help": "Estimated current value of all checking and savings accounts",
                        "column": 1
                    },
                    {
                        "key": "checking_balance",
                        "label": "Checking",
                        "type": "currency",
                        "required": False,
                        "level": "advanced",
                        "min": 0,
                        "max": 10000000,
                        "step": 1000,
                        "default": 0,
                        "help": "Total balance in checking accounts",
                        "column": 2
                    },
                    {
                        "key": "savings_cds_balance",
                        "label": "Savings / CDs",
                        "type": "currency",
                        "required": False,
                        "level": "advanced",
                        "min": 0,
                        "max": 10000000,
                        "step": 1000,
                        "default": 0,
                        "help": "Total balance in savings accounts and certificates of deposit",
                        "column": 2
                    }
                ],
                "info_boxes": [
                    {
                        "type": "info",
                        "message": "💰 Liquid assets are important for immediate care costs. Medicaid allows up to $2,000 for individuals (2024)."
                    }
                ]
            },
            {
                "id": "investments",
                "title": "Investments",
                "icon": "📈",
                "help_text": "Brokerage accounts and investment holdings",
                "layout": "two_column",
                "fields": [
                    {
                        "key": "brokerage_total",
                        "label": "Brokerage / Investments (Total)",
                        "type": "currency",
                        "required": False,
                        "level": "basic",
                        "min": 0,
                        "max": 50000000,
                        "step": 5000,
                        "default": 0,
                        "help": "Estimated current value of all brokerage holdings",
                        "column": 1
                    },
                    {
                        "key": "brokerage_mf_etf",
                        "label": "Brokerage - Mutual Funds / ETFs",
                        "type": "currency",
                        "required": False,
                        "level": "advanced",
                        "min": 0,
                        "max": 50000000,
                        "step": 5000,
                        "default": 0,
                        "help": "Value of mutual funds and ETFs",
                        "column": 2
                    },
                    {
                        "key": "brokerage_stocks_bonds",
                        "label": "Brokerage - Stocks / Bonds",
                        "type": "currency",
                        "required": False,
                        "level": "advanced",
                        "min": 0,
                        "max": 50000000,
                        "step": 5000,
                        "default": 0,
                        "help": "Value of individual stocks and bonds",
                        "column": 2
                    }
                ],
                "info_boxes": [
                    {
                        "type": "info",
                        "message": "📈 Investment accounts can provide flexibility for care costs. Note any restrictions or market timing concerns."
                    }
                ]
            },
            {
                "id": "retirement_accounts",
                "title": "Retirement Accounts",
                "icon": "🏦",
                "help_text": "IRAs, 401(k)s, and other retirement savings",
                "layout": "two_column",
                "fields": [
                    {
                        "key": "retirement_total",
                        "label": "Retirement Accounts (Total)",
                        "type": "currency",
                        "required": False,
                        "level": "basic",
                        "min": 0,
                        "max": 50000000,
                        "step": 5000,
                        "default": 0,
                        "help": "Total value of all retirement accounts",
                        "column": 1
                    },
                    {
                        "key": "retirement_traditional",
                        "label": "Traditional IRA / 401(k)",
                        "type": "currency",
                        "required": False,
                        "level": "advanced",
                        "min": 0,
                        "max": 50000000,
                        "step": 5000,
                        "default": 0,
                        "help": "Pre-tax retirement accounts",
                        "column": 2
                    },
                    {
                        "key": "retirement_roth",
                        "label": "Roth IRA",
                        "type": "currency",
                        "required": False,
                        "level": "advanced",
                        "min": 0,
                        "max": 50000000,
                        "step": 5000,
                        "default": 0,
                        "help": "After-tax Roth accounts",
                        "column": 2
                    }
                ],
                "info_boxes": [
                    {
                        "type": "info",
                        "message": "🏦 Retirement accounts often have penalties for early withdrawal (before age 59½) and required minimum distributions (after age 73)."
                    }
                ]
            },
            {
                "id": "real_estate_other",
                "title": "Real Estate & Other",
                "icon": "🏠",
                "help_text": "Property, vehicles, and other valuable assets",
                "layout": "two_column",
                "fields": [
                    {
                        "key": "home_equity_estimate",
                        "label": "Home Equity (Estimate)",
                        "type": "currency",
                        "required": False,
                        "level": "basic",
                        "min": 0,
                        "max": 50000000,
                        "step": 25000,
                        "default": 0,
                        "help": "Estimated home value minus outstanding mortgage",
                        "column": 1
                    },
                    {
                        "key": "real_estate_other",
                        "label": "Real Estate - Other Property",
                        "type": "currency",
                        "required": False,
                        "level": "advanced",
                        "min": 0,
                        "max": 50000000,
                        "step": 25000,
                        "default": 0,
                        "help": "Rental properties, vacation homes, land, etc.",
                        "column": 2
                    },
                    {
                        "key": "life_insurance_cash_value",
                        "label": "Life Insurance Cash Value",
                        "type": "currency",
                        "required": False,
                        "level": "advanced",
                        "min": 0,
                        "max": 10000000,
                        "step": 5000,
                        "default": 0,
                        "help": "Cash surrender value of life insurance policies",
                        "column": 2
                    }
                ],
                "info_boxes": [
                    {
                        "type": "info",
                        "message": "🏠 Primary home is often Medicaid-exempt (up to equity limits). Consider timing and liquidity for accessing home equity."
                    }
                ]
            },
            {
                "id": "results",
                "type": "results",
                "title": "Assets Assessment Complete",
                "icon": "✅",
                "fields": []
            }
        ],
        "summary": {
            "type": "calculated",
            "label": "Total Assets",
            "formula": "sum(cash_liquid_total, brokerage_total, retirement_total, home_equity_estimate, checking_balance, savings_cds_balance, brokerage_mf_etf, brokerage_stocks_bonds, retirement_traditional, retirement_roth, real_estate_other, life_insurance_cash_value)",
            "display_format": "${:,.0f}"
        },
        "output_contract": {
            "asset_has_partner": "string",
            "asset_legal_restrictions": "string",
            "cash_liquid_total": "number",
            "checking_balance": "number",
            "savings_cds_balance": "number",
            "brokerage_total": "number",
            "brokerage_mf_etf": "number",
            "brokerage_stocks_bonds": "number",
            "retirement_total": "number",
            "retirement_traditional": "number",
            "retirement_roth": "number",
            "home_equity_estimate": "number",
            "real_estate_other": "number",
            "life_insurance_cash_value": "number",
            "total_asset_value": "calculated"
        }
    }
    
    output_path = ASSESSMENTS_DIR / "assets.json"
    # Backup first
    import shutil
    backup_path = output_path.with_suffix('.json.bak')
    if output_path.exists():
        shutil.copy(output_path, backup_path)
        print(f"📁 Backed up to {backup_path}")
    
    with open(output_path, 'w') as f:
        json.dump(assets_config, f, indent=2)
    
    print(f"✅ Updated {output_path}")


if __name__ == "__main__":
    print("🚀 Updating assessment configurations with level property...")
    print()
    update_income_json()
    update_assets_json()
    print()
    print("✅ All assessments updated successfully!")
    print()
    print("Next steps:")
    print("1. Update assessment_engine.py to add toggle rendering")
    print("2. Modify assessments.py to persist view_mode")
    print("3. Test toggle functionality")
