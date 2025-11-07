# JSON Configuration & LLM Integration Deep Dive

**Purpose**: Explain how JSON configuration drives questions, scoring, and LLM communication in the Senior Navigator prototype.

**Audience**: Developers rebuilding the system who need to understand the complete pipeline from JSON → Questions → Scoring → LLM.

---

## Table of Contents

1. [Overview: JSON-Driven Architecture](#overview-json-driven-architecture)
2. [JSON Configuration Files](#json-configuration-files)
3. [Question Rendering from JSON](#question-rendering-from-json)
4. [Scoring Logic from JSON](#scoring-logic-from-json)
5. [LLM Communication Pipeline](#llm-communication-pipeline)
6. [JSON Guardrails & Schema Validation](#json-guardrails--schema-validation)
7. [Complete End-to-End Example](#complete-end-to-end-example)
8. [Code Tracing Guide](#code-tracing-guide)

---

## Overview: JSON-Driven Architecture

### Why JSON Configuration?

**Problem**: Hardcoding questions and scoring in application code makes changes slow and requires developer involvement.

**Solution**: Store questions, options, scores, and business rules in JSON configuration files that can be updated by product teams without code changes.

### The Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    JSON Configuration                         │
│  (module.json - questions, options, scores, flags)           │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Module Rendering Engine                      │
│  (core/navi_module.py - reads JSON, generates UI)           │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    User Interactions                          │
│  (User answers questions rendered from JSON)                 │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Answer Collection                          │
│  answers = {"adl_bathing": "frequent", ...}                  │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ├──────────────────────────────────────┐
                         │                                      │
                         ▼                                      ▼
┌──────────────────────────────────────┐    ┌──────────────────────────────┐
│     Deterministic Scoring Engine     │    │     LLM Communication        │
│  (Reads JSON scores, calculates)     │    │  (Sends answers + context)   │
│  logic.py:_calculate_score()         │    │  ai/gcp_navi_engine.py       │
└──────────────────────┬───────────────┘    └────────────┬─────────────────┘
                       │                                  │
                       └──────────────┬───────────────────┘
                                      │
                                      ▼
                        ┌──────────────────────────┐
                        │    Adjudication          │
                        │  logic.py:line 83        │
                        └──────────────────────────┘
                                      │
                                      ▼
                        ┌──────────────────────────┐
                        │  CareRecommendation      │
                        │  (Final Result)          │
                        └──────────────────────────┘
```

---

## JSON Configuration Files

### Primary Configuration: module.json

**Location**: `products/gcp_v4/modules/care_recommendation/module.json`

**Size**: ~2500 lines

**Structure**:

```json
{
  "module_id": "care_recommendation",
  "version": "4.0",
  "metadata": {
    "title": "Guided Care Plan",
    "description": "Comprehensive care needs assessment"
  },
  
  "sections": [
    {
      "section_id": "adls",
      "title": "Activities of Daily Living",
      "description": "Basic self-care abilities",
      "order": 1,
      
      "fields": [
        {
          "field_id": "adl_bathing",
          "type": "radio",
          "label": "How much help is needed with bathing?",
          "help_text": "Consider safety, frequency, and level of assistance",
          "required": true,
          "order": 1,
          
          "options": [
            {
              "value": "independent",
              "label": "No help needed - bathes independently",
              "score": 0,
              "flags": []
            },
            {
              "value": "occasional",
              "label": "Occasional reminders or supervision",
              "score": 5,
              "flags": ["adl_supervision"]
            },
            {
              "value": "frequent",
              "label": "Frequent hands-on assistance needed",
              "score": 15,
              "flags": ["adl_assistance", "falls_risk"]
            },
            {
              "value": "total",
              "label": "Complete help needed with bathing",
              "score": 25,
              "flags": ["adl_total_care", "falls_risk", "high_support"]
            }
          ]
        },
        
        {
          "field_id": "adl_dressing",
          "type": "radio",
          "label": "How much help is needed with dressing?",
          "required": true,
          "order": 2,
          
          "options": [
            {
              "value": "independent",
              "label": "Dresses independently",
              "score": 0,
              "flags": []
            },
            {
              "value": "needs_help",
              "label": "Needs help with buttons, zippers",
              "score": 10,
              "flags": ["adl_assistance"]
            },
            {
              "value": "total",
              "label": "Needs complete help dressing",
              "score": 20,
              "flags": ["adl_total_care"]
            }
          ]
        }
        
        /* ... more ADL questions ... */
      ]
    },
    
    {
      "section_id": "cognition",
      "title": "Cognitive Assessment",
      "order": 2,
      
      "fields": [
        {
          "field_id": "cognition_level",
          "type": "radio",
          "label": "What level of memory or cognitive changes are present?",
          "required": true,
          
          "options": [
            {
              "value": "none",
              "label": "No memory changes",
              "score": 0,
              "flags": []
            },
            {
              "value": "mild",
              "label": "Mild forgetfulness (names, appointments)",
              "score": 10,
              "flags": ["cognition_mild"]
            },
            {
              "value": "moderate",
              "label": "Moderate - affects daily tasks",
              "score": 30,
              "flags": ["cognition_moderate", "memory_support"]
            },
            {
              "value": "severe",
              "label": "Severe - needs constant supervision",
              "score": 50,
              "flags": ["cognition_severe", "memory_support", "supervision_24h"]
            }
          ]
        },
        
        {
          "field_id": "memory_diagnosis",
          "type": "radio",
          "label": "Has there been a formal diagnosis?",
          "required": false,
          "conditional": {
            "field": "cognition_level",
            "values": ["mild", "moderate", "severe"]
          },
          
          "options": [
            {
              "value": "none",
              "label": "No formal diagnosis",
              "score": 0,
              "flags": []
            },
            {
              "value": "mci",
              "label": "Mild Cognitive Impairment (MCI)",
              "score": 5,
              "flags": ["diagnosed_mci"]
            },
            {
              "value": "alzheimers",
              "label": "Alzheimer's Disease",
              "score": 10,
              "flags": ["diagnosed_alzheimers", "memory_care_eligible"]
            },
            {
              "value": "dementia",
              "label": "Other dementia",
              "score": 10,
              "flags": ["diagnosed_dementia", "memory_care_eligible"]
            }
          ]
        }
        
        /* ... more cognition questions ... */
      ]
    }
    
    /* ... more sections (behaviors, medical, safety) ... */
  ],
  
  "tier_thresholds": {
    "independent": {
      "min": 0,
      "max": 20,
      "label": "Independent Living",
      "description": "Minimal or no assistance needed"
    },
    "in_home": {
      "min": 21,
      "max": 40,
      "label": "In-Home Care",
      "description": "Support needed but can remain at home"
    },
    "assisted_living": {
      "min": 41,
      "max": 70,
      "label": "Assisted Living",
      "description": "24/7 support and supervision needed"
    },
    "memory_care": {
      "min": 71,
      "max": 100,
      "label": "Memory Care",
      "description": "Specialized care for cognitive impairment"
    }
  }
}
```

### How JSON Fields Work

| Field | Purpose | Used By | Example |
|-------|---------|---------|---------|
| `field_id` | Unique identifier for question | Scoring engine, answer lookup | `"adl_bathing"` |
| `type` | UI widget type | Module renderer | `"radio"`, `"checkbox"`, `"text"` |
| `label` | Question text displayed to user | UI | `"How much help..."` |
| `options.value` | Internal value stored | Answers dict | `"frequent"` |
| `options.label` | User-friendly text | UI | `"Frequent assistance"` |
| `options.score` | Point value for scoring | Scoring engine | `15` |
| `options.flags` | Markers for special handling | Gate logic, rationale | `["adl_assistance"]` |

---

## Question Rendering from JSON

### Module Rendering Engine

**File**: `core/navi_module.py`

**Function**: `render_module(module_config)`

**What it does**: Reads `module.json` and generates Streamlit UI components dynamically.

### Rendering Process

```python
# File: core/navi_module.py
# Lines: ~50-300

def render_module(module_config: dict) -> dict:
    """
    Render module UI from JSON configuration.
    
    Args:
        module_config: Parsed module.json
        
    Returns:
        answers: Dict of {field_id: selected_value}
    """
    answers = {}
    
    # Iterate through sections in JSON
    for section in module_config["sections"]:
        st.header(section["title"])
        
        if section.get("description"):
            st.write(section["description"])
        
        # Iterate through fields in section
        for field in section["fields"]:
            # Check conditional logic (if present)
            if should_show_field(field, answers):
                # Render appropriate widget based on type
                answer = render_field(field)
                
                if answer is not None:
                    answers[field["field_id"]] = answer
    
    return answers


def render_field(field: dict):
    """Render individual field based on type from JSON."""
    
    field_type = field["type"]
    field_id = field["field_id"]
    label = field["label"]
    
    if field_type == "radio":
        # Extract option values and labels from JSON
        options = {opt["value"]: opt["label"] for opt in field["options"]}
        
        # Render radio buttons
        selected = st.radio(
            label=label,
            options=list(options.keys()),
            format_func=lambda x: options[x],
            key=field_id
        )
        return selected
        
    elif field_type == "checkbox":
        # Multi-select checkbox
        selected = []
        st.write(label)
        for opt in field["options"]:
            if st.checkbox(opt["label"], key=f"{field_id}_{opt['value']}"):
                selected.append(opt["value"])
        return selected
        
    elif field_type == "text":
        return st.text_input(label, key=field_id)
        
    elif field_type == "number":
        return st.number_input(label, key=field_id)
        
    elif field_type == "select":
        options = {opt["value"]: opt["label"] for opt in field["options"]}
        return st.selectbox(label, options=list(options.keys()), 
                           format_func=lambda x: options[x], key=field_id)


def should_show_field(field: dict, answers: dict) -> bool:
    """Check if field should be shown based on conditional logic in JSON."""
    
    if "conditional" not in field:
        return True  # Always show if no conditionals
    
    conditional = field["conditional"]
    depends_on_field = conditional["field"]
    required_values = conditional["values"]
    
    # Check if dependency is answered with required value
    if depends_on_field in answers:
        return answers[depends_on_field] in required_values
    
    return False  # Hide until dependency is met
```

### Key Insight

**The UI is 100% generated from JSON**. No questions are hardcoded. To add a new question:

1. Add field to `module.json`
2. Specify options with scores
3. Deploy config (no code changes)
4. Module renderer picks it up automatically

---

## Scoring Logic from JSON

### How Scoring Works

**File**: `products/gcp_v4/modules/care_recommendation/logic.py`

**Function**: `_calculate_score(answers, module_data)`

**Lines**: ~800-850

### The Algorithm

```python
# File: products/gcp_v4/modules/care_recommendation/logic.py
# Lines: 800-850

def _calculate_score(answers: dict, module_data: dict) -> tuple[int, dict]:
    """
    Calculate total score from user answers using module.json scoring.
    
    This is PURE JSON-driven scoring - no hardcoded logic.
    
    Args:
        answers: {field_id: selected_value, ...}
        module_data: Parsed module.json
        
    Returns:
        (total_score, scoring_details)
    """
    total_score = 0
    scoring_details = {
        "fields_scored": [],
        "flags_collected": [],
        "breakdown": {}
    }
    
    # Iterate through all sections in JSON
    for section in module_data["sections"]:
        section_score = 0
        
        for field in section["fields"]:
            field_id = field["field_id"]
            
            # Check if user answered this question
            if field_id not in answers:
                continue
            
            selected_value = answers[field_id]
            
            # Find the selected option in JSON
            selected_option = None
            for option in field["options"]:
                if option["value"] == selected_value:
                    selected_option = option
                    break
            
            if selected_option:
                # Add score from JSON
                option_score = selected_option.get("score", 0)
                total_score += option_score
                section_score += option_score
                
                # Collect flags from JSON
                flags = selected_option.get("flags", [])
                scoring_details["flags_collected"].extend(flags)
                
                # Track details for debugging
                scoring_details["fields_scored"].append({
                    "field_id": field_id,
                    "selected": selected_value,
                    "score": option_score,
                    "flags": flags
                })
        
        # Track section breakdown
        scoring_details["breakdown"][section["section_id"]] = section_score
    
    return total_score, scoring_details


def _determine_tier(total_score: int, module_data: dict) -> str:
    """
    Map score to tier using thresholds from module.json.
    
    Args:
        total_score: Calculated total score
        module_data: Parsed module.json
        
    Returns:
        tier: "independent", "in_home", "assisted_living", or "memory_care"
    """
    tier_thresholds = module_data.get("tier_thresholds", {})
    
    # Check which tier range the score falls into
    for tier, threshold in tier_thresholds.items():
        min_score = threshold.get("min", 0)
        max_score = threshold.get("max", 100)
        
        if min_score <= total_score <= max_score:
            print(f"[SCORE] total={total_score} → tier={tier} (range: {min_score}-{max_score})")
            return tier
    
    # Fallback if score doesn't match any range (shouldn't happen)
    return "assisted_living"  # Safe default
```

### Scoring Example

**User Answers**:
```json
{
  "adl_bathing": "frequent",      // score: 15
  "adl_dressing": "needs_help",   // score: 10
  "cognition_level": "moderate",  // score: 30
  "memory_diagnosis": "none"      // score: 0
}
```

**Scoring Calculation**:
```
total_score = 15 + 10 + 30 + 0 = 55

Check tier_thresholds:
  independent: 0-20 → NO
  in_home: 21-40 → NO
  assisted_living: 41-70 → YES ✓
  memory_care: 71-100 → NO

Result: tier = "assisted_living"
```

### Key Insight

**All scoring is driven by JSON**. The code ONLY:
1. Reads JSON
2. Looks up answer in JSON options
3. Sums the scores from JSON
4. Maps total to tier using JSON thresholds

**No business rules in code** - everything is in `module.json`.

---

## LLM Communication Pipeline

### Overview

The LLM receives answers + deterministic result + context, then suggests a tier.

### Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│               User Answers (from JSON questions)             │
│  {"adl_bathing": "frequent", "cognition_level": "moderate"}  │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│        Context Builder (ai/gcp_navi_engine.py:~100)         │
│  Converts answers dict → human-readable narrative            │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│        Prompt Constructor (ai/gcp_navi_engine.py:~150)      │
│  Builds structured prompt with JSON schema for response      │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│          LLM Request (ai/llm_client.py:~50)                  │
│  OpenAI API call with JSON mode + timeout                    │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│      Response Parser (ai/gcp_navi_engine.py:~200)           │
│  Parse JSON response, validate against schema                │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│          Validation (ai/gcp_navi_engine.py:~250)            │
│  Check if LLM tier is in allowed_tiers                       │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
              Return (llm_tier, confidence)
```

### Code Implementation

**File**: `ai/gcp_navi_engine.py`

```python
# File: ai/gcp_navi_engine.py
# Lines: 50-300

def get_llm_tier_suggestion(
    answers: dict,
    det_tier: str,
    allowed_tiers: list[str],
    bands: dict
) -> tuple[str | None, float | None]:
    """
    Request tier suggestion from LLM with structured JSON response.
    
    Args:
        answers: User responses from JSON questions
        det_tier: Deterministic tier (from scoring)
        allowed_tiers: Post-gate allowed tiers
        bands: {"cog": "moderate", "sup": "high"}
        
    Returns:
        (llm_tier, confidence) or (None, None) on timeout/error
    """
    
    # STEP 1: Build narrative context from answers
    context = _build_context_narrative(answers)
    
    # STEP 2: Construct prompt with JSON schema
    prompt = _build_tier_prompt(context, det_tier, allowed_tiers, bands)
    
    # STEP 3: Call LLM with timeout
    try:
        response = llm_client.complete(
            prompt=prompt,
            model="gpt-4o-mini",
            timeout=15,  # seconds
            temperature=0.3,  # Low for consistency
            response_format={"type": "json_object"}  # JSON mode
        )
        
        # STEP 4: Parse and validate response
        result = _parse_and_validate_response(response, allowed_tiers)
        
        return result["tier"], result["confidence"]
        
    except TimeoutError:
        print("[LLM] Timeout after 15s, falling back to deterministic")
        return None, None
    except Exception as e:
        print(f"[LLM] Error: {e}, falling back to deterministic")
        return None, None


def _build_context_narrative(answers: dict) -> str:
    """
    Convert answers dict to human-readable narrative for LLM.
    
    Example:
      Input: {"adl_bathing": "frequent", "cognition_level": "moderate"}
      Output: "Needs frequent assistance with bathing. Moderate cognitive changes affecting daily tasks."
    """
    narrative_parts = []
    
    # ADLs
    adl_fields = {
        "adl_bathing": "bathing",
        "adl_dressing": "dressing",
        "adl_toileting": "toileting",
        "adl_transferring": "transferring",
        "adl_eating": "eating"
    }
    
    needs_help_with = []
    for field_id, label in adl_fields.items():
        value = answers.get(field_id)
        if value and value != "independent":
            needs_help_with.append(label)
    
    if needs_help_with:
        narrative_parts.append(f"Needs assistance with: {', '.join(needs_help_with)}")
    
    # Cognition
    cog_level = answers.get("cognition_level")
    if cog_level and cog_level != "none":
        cog_map = {
            "mild": "Mild cognitive changes (forgetfulness)",
            "moderate": "Moderate cognitive impairment affecting daily tasks",
            "severe": "Severe cognitive impairment requiring constant supervision"
        }
        narrative_parts.append(cog_map.get(cog_level, ""))
    
    # Diagnosis
    diagnosis = answers.get("memory_diagnosis")
    if diagnosis and diagnosis != "none":
        diag_map = {
            "mci": "Diagnosed with Mild Cognitive Impairment (MCI)",
            "alzheimers": "Diagnosed with Alzheimer's Disease",
            "dementia": "Diagnosed with dementia"
        }
        narrative_parts.append(diag_map.get(diagnosis, ""))
    
    # Behaviors
    risky_behaviors = []
    behavior_fields = ["wandering", "aggression", "sundowning", "elopement"]
    for field in behavior_fields:
        if answers.get(field) == "yes":
            risky_behaviors.append(field)
    
    if risky_behaviors:
        narrative_parts.append(f"Risky behaviors present: {', '.join(risky_behaviors)}")
    
    return "\n".join(narrative_parts)


def _build_tier_prompt(
    context: str,
    det_tier: str,
    allowed_tiers: list[str],
    bands: dict
) -> str:
    """
    Construct prompt for LLM with JSON schema guardrails.
    
    This prompt includes:
    1. Assessment context (from answers)
    2. Deterministic recommendation (for reference)
    3. Allowed options (enforced by gates)
    4. JSON schema for response
    """
    
    prompt = f"""You are a senior care advisor AI. Based on the following assessment, suggest the most appropriate care tier.

ASSESSMENT:
{context}

REFERENCE:
- Deterministic recommendation: {det_tier}
- Cognitive band: {bands.get('cog', 'unknown')}
- Support band: {bands.get('sup', 'unknown')}

ALLOWED OPTIONS:
You must choose from: {', '.join(allowed_tiers)}

INSTRUCTIONS:
1. Consider the level of assistance needed (ADLs, IADLs)
2. Consider cognitive impairment level and diagnosis
3. Consider behavioral issues and safety risks
4. Weigh the deterministic recommendation but use your judgment
5. Your suggestion must be from the allowed options

Respond with JSON only (no other text):
{{
  "tier": "one of: {', '.join(allowed_tiers)}",
  "confidence": 0.85,
  "reasoning": "Brief explanation of why this tier is appropriate"
}}
"""
    
    return prompt


def _parse_and_validate_response(
    response: str,
    allowed_tiers: list[str]
) -> dict:
    """
    Parse LLM JSON response and validate against schema.
    
    Args:
        response: JSON string from LLM
        allowed_tiers: Valid tier options
        
    Returns:
        Parsed and validated dict
        
    Raises:
        ValueError: If response is invalid
    """
    # Parse JSON
    try:
        result = json.loads(response)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from LLM: {e}")
    
    # Validate required fields
    required_fields = ["tier", "confidence", "reasoning"]
    for field in required_fields:
        if field not in result:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate tier is in allowed set
    if result["tier"] not in allowed_tiers:
        raise ValueError(f"LLM suggested disallowed tier: {result['tier']} not in {allowed_tiers}")
    
    # Validate confidence range
    if not (0 <= result["confidence"] <= 1):
        raise ValueError(f"Invalid confidence: {result['confidence']} (must be 0-1)")
    
    return result
```

### JSON Schema Enforcement (Guardrails)

**What are JSON Guardrails?**

JSON guardrails are response format constraints that ensure LLM output is:
1. Valid JSON
2. Contains required fields
3. Values are in expected ranges/types
4. Can be parsed programmatically

**How We Use Them**:

1. **OpenAI JSON Mode**: Forces LLM to return valid JSON
   ```python
   response_format={"type": "json_object"}
   ```

2. **Schema in Prompt**: Explicit structure in prompt
   ```json
   {
     "tier": "string (one of: in_home, assisted_living)",
     "confidence": "number (0-1)",
     "reasoning": "string"
   }
   ```

3. **Post-Response Validation**: Code checks every field
   ```python
   if result["tier"] not in allowed_tiers:
       raise ValueError("Invalid tier")
   ```

**File**: `ai/llm_client.py` (Lines ~50-100)

```python
def complete(
    prompt: str,
    model: str = "gpt-4o-mini",
    timeout: int = 15,
    temperature: float = 0.3,
    response_format: dict = None
) -> str:
    """
    Call OpenAI API with JSON mode and guardrails.
    
    Args:
        prompt: Prompt with JSON schema
        model: OpenAI model
        timeout: Max seconds to wait
        temperature: Creativity (0=deterministic, 1=creative)
        response_format: {"type": "json_object"} for JSON mode
        
    Returns:
        JSON string response
    """
    import openai
    import signal
    
    # Set timeout
    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(timeout)
    
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that responds in JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            response_format=response_format  # Enforces JSON response
        )
        
        signal.alarm(0)  # Cancel timeout
        
        return response.choices[0].message.content
        
    except Exception as e:
        signal.alarm(0)
        raise e


def _timeout_handler(signum, frame):
    raise TimeoutError("LLM request timed out")
```

---

## Complete End-to-End Example

Let's trace a COMPLETE flow from JSON → UI → Scoring → LLM → Result.

### Step 1: JSON Configuration

```json
{
  "fields": [
    {
      "field_id": "adl_bathing",
      "type": "radio",
      "label": "Help needed with bathing?",
      "options": [
        {"value": "independent", "label": "No help", "score": 0, "flags": []},
        {"value": "frequent", "label": "Frequent help", "score": 15, "flags": ["adl_assistance"]}
      ]
    },
    {
      "field_id": "cognition_level",
      "type": "radio",
      "label": "Memory changes?",
      "options": [
        {"value": "none", "label": "None", "score": 0, "flags": []},
        {"value": "moderate", "label": "Moderate", "score": 30, "flags": ["cognition_moderate"]}
      ]
    }
  ],
  "tier_thresholds": {
    "in_home": {"min": 21, "max": 40},
    "assisted_living": {"min": 41, "max": 70}
  }
}
```

### Step 2: Module Renderer (core/navi_module.py)

```python
# Reads JSON, generates UI
answers = render_module(module_config)
# User selects: "frequent" for bathing, "moderate" for cognition
# Result: answers = {"adl_bathing": "frequent", "cognition_level": "moderate"}
```

### Step 3: Scoring Engine (logic.py:800-850)

```python
# Calculate score from JSON
total_score = 0
for field_id, value in answers.items():
    option = find_option_in_json(module_config, field_id, value)
    total_score += option["score"]

# adl_bathing: "frequent" → 15 points
# cognition_level: "moderate" → 30 points
# total_score = 45

# Map to tier using JSON thresholds
# 45 is in range 41-70 → "assisted_living"
det_tier = "assisted_living"
```

### Step 4: Gate Logic (logic.py:1140-1180)

```python
# Check cognitive gate
cog_band = "moderate"  # From cognition_level answer
passes_gate = has_memory_diagnosis(answers)  # Check for formal diagnosis

# Build allowed_tiers
allowed_tiers = ["in_home", "assisted_living"]  # MC blocked (no diagnosis)
```

### Step 5: LLM Request (ai/gcp_navi_engine.py)

```python
# Build context from answers
context = """
Needs frequent assistance with bathing.
Moderate cognitive impairment affecting daily tasks.
No formal diagnosis present.
"""

# Build prompt with JSON schema
prompt = f"""
ASSESSMENT:
{context}

REFERENCE:
- Deterministic: assisted_living
- Cognitive: moderate
- Support: high

ALLOWED OPTIONS: in_home, assisted_living

Respond with JSON:
{{
  "tier": "in_home or assisted_living",
  "confidence": 0.0-1.0,
  "reasoning": "explanation"
}}
"""

# Call LLM (with timeout)
llm_response = llm_client.complete(prompt, timeout=15, response_format={"type": "json_object"})

# LLM returns:
{
  "tier": "assisted_living",
  "confidence": 0.82,
  "reasoning": "Moderate cognitive changes plus frequent ADL assistance indicates need for 24/7 supervised environment"
}
```

### Step 6: Validation (ai/gcp_navi_engine.py:250)

```python
# Parse JSON
result = json.loads(llm_response)

# Validate tier is allowed
if result["tier"] not in allowed_tiers:
    raise ValueError("LLM suggested disallowed tier")

# Extract values
llm_tier = "assisted_living"  # Valid
llm_conf = 0.82
```

### Step 7: Adjudication (logic.py:83)

```python
def _choose_final_tier(det_tier, allowed_tiers, llm_tier, llm_conf):
    # LLM-first policy
    if llm_tier and llm_tier in allowed_tiers:
        return llm_tier, {"source": "llm", "conf": llm_conf}
    else:
        return det_tier, {"source": "fallback"}

# In this case:
# llm_tier = "assisted_living" (valid)
# llm_tier in allowed_tiers = True
# → Use LLM tier

final_tier = "assisted_living"
source = "llm"
```

### Step 8: Result

```python
CareRecommendation(
    tier="assisted_living",           # From LLM (matched deterministic)
    tier_score=82,                    # LLM confidence
    confidence=1.0,                   # All questions answered
    flags=["adl_assistance", "cognition_moderate"],
    rationale=[
        "Needs frequent assistance with bathing",
        "Moderate cognitive impairment present",
        "24/7 supervised environment recommended"
    ],
    source="llm",
    deterministic_tier="assisted_living",
    llm_tier="assisted_living",
    allowed_tiers=["in_home", "assisted_living"]
)
```

---

## Code Tracing Guide

### "I need to understand how questions are rendered"

1. **Start**: `core/navi_module.py` line ~50
2. **Function**: `render_module(module_config)`
3. **Key logic**: Lines 100-200 (loops through sections and fields)
4. **Widget creation**: Lines 200-300 (radio, checkbox, text, etc.)

### "I need to understand how scoring works"

1. **Start**: `products/gcp_v4/modules/care_recommendation/logic.py` line 800
2. **Function**: `_calculate_score(answers, module_data)`
3. **Key logic**: Lines 810-840 (loops through answers, sums scores)
4. **Tier mapping**: Line ~850 `_determine_tier(total_score)`

### "I need to understand how answers get to the LLM"

1. **Start**: `products/gcp_v4/modules/care_recommendation/logic.py` line 1240
2. **LLM call**: `ai/gcp_navi_engine.py` line ~50
3. **Context building**: Line ~100 `_build_context_narrative(answers)`
4. **Prompt construction**: Line ~150 `_build_tier_prompt(...)`
5. **API call**: `ai/llm_client.py` line ~50 `complete(...)`

### "I need to understand JSON guardrails"

1. **Prompt schema**: `ai/gcp_navi_engine.py` line ~150 (schema in prompt)
2. **OpenAI JSON mode**: `ai/llm_client.py` line ~70 (`response_format={"type": "json_object"}`)
3. **Validation**: `ai/gcp_navi_engine.py` line ~250 `_parse_and_validate_response(...)`

### "I need to understand adjudication"

1. **Start**: `products/gcp_v4/modules/care_recommendation/logic.py` line 83
2. **Function**: `_choose_final_tier(det_tier, allowed_tiers, llm_tier, ...)`
3. **Key logic**: Lines 130-160 (LLM-first if-else)

---

## Summary: Key Files Reference

| Component | File | Key Functions | Lines |
|-----------|------|---------------|-------|
| **JSON Config** | `products/gcp_v4/modules/care_recommendation/module.json` | N/A (data) | All |
| **Question Rendering** | `core/navi_module.py` | `render_module()`, `render_field()` | 50-300 |
| **Scoring Logic** | `logic.py` | `_calculate_score()`, `_determine_tier()` | 800-900 |
| **LLM Context** | `ai/gcp_navi_engine.py` | `_build_context_narrative()` | ~100-150 |
| **LLM Prompt** | `ai/gcp_navi_engine.py` | `_build_tier_prompt()` | ~150-200 |
| **LLM Call** | `ai/llm_client.py` | `complete()` | ~50-100 |
| **JSON Validation** | `ai/gcp_navi_engine.py` | `_parse_and_validate_response()` | ~250-300 |
| **Adjudication** | `logic.py` | `_choose_final_tier()` | 83-170 |

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-07  
**Questions**: Refer to CODE_REFERENCE_MAP.md for exact line numbers
