"""
Cost Planner v2 Financial Assessment Modules

Each module collects specific financial information and returns
a standard contract for aggregation.

New module structure (v3.0.0):
- income: Monthly income from all sources
- assets: Financial assets and resources
- va_benefits: VA Disability and Aid & Attendance
- health_insurance: Medicare, Medicaid, LTC insurance
- life_insurance: Life insurance policies and cash value
- medicaid_navigation: Medicaid planning and eligibility
"""

__all__ = [
    "income",
    "assets", 
    "va_benefits",
    "health_insurance",
    "life_insurance",
    "medicaid_navigation"
]
