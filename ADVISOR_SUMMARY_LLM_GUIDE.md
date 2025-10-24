# Advisor Summary LLM Templates - Implementation Guide

## Overview

This system generates four natural-language narrative "drawers" for internal advisor dashboards, replacing the deprecated Plan for My Advisor (PFMA) and Advisor Prep modules.

Each drawer presents a short, warm paragraph describing what the system knows about the care recipient, drawn from:
- **Guided Care Plan (GCP)** - Care recommendations and assessment data
- **Cost Planner (CP)** - Financial projections and affordability analysis  
- **Session State** - Profile data, flags, and user preferences

## Target Audience

**Internal business and advisor stakeholders** who need to understand how much insight the platform holds about each person. These narratives are **not customer-facing**.

## Four Drawer Types

### 1. About the Person
**Purpose**: Introduce the care recipient and their current situation
**Content**: Name, age, living situation, geographic area, support network, family involvement
**Length**: 80-120 words
**Tone**: Warm introduction establishing context

**Example**:
> "This plan is for Margaret, who is in her late seventies and currently lives alone in the Baton Rouge area (70808). She has limited access to nearby family and occasionally relies on neighbors for support. Her daughter is assisting with planning and exploring options that would keep Margaret close to familiar surroundings while ensuring she receives appropriate care and oversight."

### 2. Housing Preferences  
**Purpose**: Summarize preferred living arrangements and timeline
**Content**: Recommended care tier, room type, move timeline, home disposition plans
**Length**: 80-120 words
**Tone**: Factual summary of housing goals

**Example**:
> "Margaret has expressed interest in Assisted Living communities that provide both independence and support with daily activities. She would prefer a one-bedroom apartment with services like meal preparation and housekeeping. Her move timeline is flexible, allowing time to research suitable communities nearby. She plans to keep her current home for now while exploring her options."

### 3. Medical & Care Information
**Purpose**: Describe care needs and coordination requirements  
**Content**: Care flags translated to natural language, medical conditions, support needs
**Length**: 80-120 words
**Tone**: Professional medical summary, respectful and person-centered

**Example**:
> "Margaret experiences moderate memory changes and mild mobility challenges that affect her daily stability. Her medical history includes ongoing health conditions requiring regular monitoring, and she takes several daily medications that benefit from professional oversight. Her care plan emphasizes consistent routines, medication management, and access to assistance when needed to maintain safety and independence."

### 4. Financial Overview
**Purpose**: Summarize financial situation and affordability
**Content**: Monthly budget, funding timeline, income sources, benefits eligibility
**Length**: 80-120 words  
**Tone**: Neutral financial overview, not advisory

**Example**:
> "Margaret's projected monthly budget for care is approximately $4,200, which will require careful coordination of her current income and assets. Based on her Social Security, pension income, and available savings, she is estimated to be funded for roughly four to five years of Assisted Living. She may also qualify for Veterans Aid & Attendance benefits, which could extend her coverage timeline."

## Data Sources

### Profile Context
- `person_a_name` - Care recipient's first name
- `person_a_age_range` - Age description (e.g., "late seventies")  
- `relationship_type` - Who is helping with planning
- `geo_zip` - ZIP code or geographic area
- `support_network_low` - Limited family support nearby (boolean)
- `low_access` - Challenges accessing services (boolean)
- `home_carry` - Plans to keep current home (boolean)
- `dual_household` - Lives with family/partner (boolean)

### Guided Care Plan
- `recommended_tier` - Primary care recommendation
- `allowed_tiers` - All eligible care options
- `move_timeline` - Preferred timeline for transition
- `room_type` - Preferred apartment/room type  
- `care_flags[]` - Array of care requirement flags

### Care Flags (Examples)
- `moderate_cognitive_decline` → "moderate memory changes"
- `severe_cognitive_decline` → "significant cognitive concerns"
- `mobility_limited` → "mobility challenges"
- `falls_risk` → "stability concerns"
- `adl_support_high` → "needs assistance with daily activities"
- `chronic_conditions` → "ongoing health conditions"
- `medication_management` → "medication oversight needs"
- `behavioral_concerns` → "behavioral changes"
- `safety_concerns` → "safety supervision requirements"
- `caregiver_fatigue` → "family caregiver stress"

### Cost Planner
- `monthly_cost` - Projected monthly care expense
- `household_income` - Monthly income available
- `total_assets` - Available assets for care funding
- `years_funded` - Estimated coverage timeline
- `va_benefits_eligible` - VA benefit qualification (boolean)
- `assets_low/assets_high` - Asset level indicators (boolean)
- `benefits_present` - Current benefits active (boolean)  
- `rx_costs_high` - High medication expenses (boolean)
- `transportation_needed` - Transportation assistance required (boolean)
- `auto_present` - Has personal vehicle (boolean)
- `family_travel_needed` - Family travel for visits (boolean)

## LLM Implementation

### File Structure
```
ai/
├── advisor_summary_templates.py    # Prompt templates and context dataclass
├── advisor_summary_engine.py       # LLM generation engine  
├── advisor_summary_schemas.py      # Pydantic schemas for structured output
└── llm_client.py                   # Existing LLM client interface
```

### Usage Example
```python
from ai.advisor_summary_engine import AdvisorSummaryEngine

# Generate all four drawers from current session state
drawers = AdvisorSummaryEngine.generate_all_drawers()

# Returns dict with keys:
# - 'about_person'
# - 'housing_preferences'  
# - 'medical_care'
# - 'financial_overview'

# Each value is a natural-language paragraph
print(drawers['about_person'])
```

### Integration Points

**Session State Extraction**:
```python
context = AdvisorSummaryEngine.build_advisor_context_from_session()
# Automatically pulls from st.session_state using standardized keys
```

**Individual Drawer Generation**:
```python
narrative = AdvisorSummaryEngine.generate_drawer_narrative(
    drawer_type="about_person", 
    context=context
)
```

**Error Handling**:
- Graceful fallback to static content if LLM fails
- Handles missing or incomplete session data
- Proper logging for debugging and monitoring

## Style Guidelines

### Tone Parameters
- **Clear, empathetic, factual** - suitable for internal reports
- **Present tense** throughout
- **No marketing language** or promotional content
- **Assume internal audience** - no customer-facing explanations

### Language Guidelines
- Use person's **first name** throughout
- **No pronouns** like "we" or "our system"
- Speak about the person **directly**
- Emphasize **care coordination needs** rather than deficits
- Use **respectful, person-centered language**

### Technical Requirements
- **80-120 words** per drawer
- **Placeholder variables** in brackets for programmatic binding
- **Complete prose** format, not bullet points
- **Neutral tone** for financial information (not advisory)

## Production Readiness

### LLM Configuration
- **Model**: GPT-4o-mini for fast, cost-effective responses
- **Temperature**: 0.7 for balanced creativity and consistency
- **Max Tokens**: 200 per drawer (allows 80-120 word target)
- **Timeout**: 10 seconds with retry logic

### Quality Assurance
- **Structured output** using Pydantic schemas
- **Word count validation** (80-120 words)
- **Content appropriateness** checks
- **Fallback content** for failed generations
- **Data completeness** scoring

### Integration Requirements
- Uses existing `LLMClient` from `ai/llm_client.py`
- Extracts data from Streamlit `session_state` automatically
- Integrates with GCP `care_recommendation` data structure
- Uses Cost Planner `financial_assessment_complete` data
- Leverages existing `flag_manager_flags` system

## Deployment Considerations

### Feature Flag
Consider adding `FEATURE_ADVISOR_SUMMARY_LLM` flag for gradual rollout:
- `off` - Use static fallback content
- `shadow` - Generate LLM content but log only (don't display)
- `assist` - Show LLM content alongside static content  
- `adjust` - Full LLM-generated content

### Performance
- **Cache generated summaries** in session state to avoid regeneration
- **Batch generation** for all four drawers to minimize API calls  
- **Async generation** if needed for UI responsiveness
- **Monitor token usage** and generation times

### Monitoring
- Track **generation success rates** per drawer type
- Monitor **average word counts** and quality metrics
- Log **fallback usage** to identify data quality issues
- Measure **user engagement** with generated vs. static content

---

## Quick Start

1. **Import the engine**:
   ```python
   from ai.advisor_summary_engine import AdvisorSummaryEngine
   ```

2. **Generate all drawers**:
   ```python
   drawers = AdvisorSummaryEngine.generate_all_drawers()
   ```

3. **Display in UI**:
   ```python
   for drawer_name, narrative in drawers.items():
       st.markdown(f"**{drawer_name.replace('_', ' ').title()}**")
       st.write(narrative)
   ```

The system is designed to be **drop-in ready** with existing codebase and provides **comprehensive fallback handling** for production reliability.