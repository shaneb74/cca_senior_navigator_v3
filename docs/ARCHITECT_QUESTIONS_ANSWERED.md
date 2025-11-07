# Architect Questions Answered

**Date**: 2025-11-07  
**Context**: Documentation for development team rebuilding Senior Navigator prototype

---

## The Questions

Your architect asked:

> "When the guided care plan is completed and it has the questions:
> 1. How are they scored?
> 2. How do those scores produce a recommendation?
> 3. How are we using the configurable JSON to manage variability in the questions we ask, in the scoring logic that we implement?
> 4. How is all of that packaged up and sent to the LLM?
> 5. How do JSON guardrails work?"

---

## Answers with Exact Code References

### Q1: How Are Questions Scored?

**Short Answer**: Each question option has a `score` value in `module.json`. When user selects an option, that score is added to a running total.

**Where to Look in Code**:

📁 **Configuration File**: `products/gcp_v4/modules/care_recommendation/module.json`
- Lines 1-2500: Complete JSON configuration
- Structure: Each field → options array → each option has `score` property

Example from JSON:
```json
{
  "field_id": "adl_bathing",
  "options": [
    {"value": "independent", "score": 0},
    {"value": "occasional", "score": 5},
    {"value": "frequent", "score": 15},
    {"value": "total", "score": 25}
  ]
}
```

📁 **Scoring Logic**: `products/gcp_v4/modules/care_recommendation/logic.py`
- **Function**: `_calculate_score(answers, module_data)`
- **Lines**: 800-850
- **Algorithm**:
  1. Loop through user's answers dict
  2. For each answer, find matching option in module.json
  3. Extract that option's `score` value
  4. Sum all scores → `total_score`

Code snippet:
```python
# Line 800-850
def _calculate_score(answers: dict, module_data: dict) -> tuple[int, dict]:
    total_score = 0
    
    for section in module_data["sections"]:
        for field in section["fields"]:
            field_id = field["field_id"]
            
            if field_id in answers:
                selected_value = answers[field_id]
                
                # Find selected option in JSON
                for option in field["options"]:
                    if option["value"] == selected_value:
                        # ADD SCORE FROM JSON
                        total_score += option.get("score", 0)
                        break
    
    return total_score, details
```

**Key Insight**: NO scoring logic is hardcoded. All scores come from JSON. Change JSON = change scoring (no code deploy needed).

---

### Q2: How Do Scores Produce a Recommendation?

**Short Answer**: `module.json` contains `tier_thresholds` that map score ranges to care tiers (Independent, In-Home, Assisted Living, Memory Care).

**Where to Look in Code**:

📁 **Thresholds Configuration**: `products/gcp_v4/modules/care_recommendation/module.json`
- Lines ~2400-2500: `tier_thresholds` object

Example from JSON:
```json
{
  "tier_thresholds": {
    "independent": {"min": 0, "max": 20},
    "in_home": {"min": 21, "max": 40},
    "assisted_living": {"min": 41, "max": 70},
    "memory_care": {"min": 71, "max": 100}
  }
}
```

📁 **Tier Mapping Logic**: `products/gcp_v4/modules/care_recommendation/logic.py`
- **Function**: `_determine_tier(total_score, module_data)`
- **Lines**: 850-900
- **Algorithm**:
  1. Read `tier_thresholds` from module.json
  2. Check which threshold range contains `total_score`
  3. Return that tier name

Code snippet:
```python
# Line 850-900
def _determine_tier(total_score: int, module_data: dict) -> str:
    tier_thresholds = module_data.get("tier_thresholds", {})
    
    for tier, threshold in tier_thresholds.items():
        min_score = threshold.get("min", 0)
        max_score = threshold.get("max", 100)
        
        if min_score <= total_score <= max_score:
            return tier  # e.g., "assisted_living"
    
    return "assisted_living"  # Safe default
```

**Example Flow**:
```
User answers:
  adl_bathing: "frequent" (15 points)
  adl_dressing: "needs_help" (10 points)
  cognition_level: "moderate" (30 points)
  
Total score: 15 + 10 + 30 = 55

Check thresholds:
  independent: 0-20? NO
  in_home: 21-40? NO
  assisted_living: 41-70? YES ✓
  
Result: tier = "assisted_living"
```

**Key Insight**: Thresholds are in JSON, not code. Change ranges = change recommendations (no code deploy needed).

---

### Q3: How Is JSON Used to Manage Variability?

**Short Answer**: The entire assessment (questions, options, scores, thresholds, conditional logic) is in `module.json`. Change JSON = change behavior. No code changes needed.

**Where to Look in Code**:

📁 **JSON Configuration**: `products/gcp_v4/modules/care_recommendation/module.json`
- **Size**: 2500 lines
- **Structure**:
  ```json
  {
    "module_id": "care_recommendation",
    "sections": [
      {
        "section_id": "adls",
        "fields": [
          {
            "field_id": "adl_bathing",
            "type": "radio",
            "label": "Question text",
            "required": true,
            "conditional": {...},  // Show if X is answered
            "options": [
              {
                "value": "independent",
                "label": "Display text",
                "score": 0,
                "flags": []  // For business rules
              }
            ]
          }
        ]
      }
    ],
    "tier_thresholds": {...}
  }
  ```

**What Can Be Changed in JSON (Without Code Changes)**:

| Change Type | Where in JSON | Effect |
|-------------|---------------|--------|
| Add/remove question | `sections[].fields[]` | New question appears in UI |
| Change question text | `field.label` | UI displays new text |
| Add/remove option | `field.options[]` | New choice available |
| Change option score | `option.score` | Changes scoring calculation |
| Adjust tier thresholds | `tier_thresholds` | Changes recommendations |
| Add conditional logic | `field.conditional` | Show/hide questions based on answers |
| Add business rules | `option.flags` | Trigger special logic (gates) |

📁 **Module Renderer**: `core/navi_module.py`
- **Function**: `render_module(module_config)`
- **Lines**: 50-300
- **What it does**: Reads JSON, generates UI dynamically
- **Key point**: NO questions are hardcoded in Python

Code flow:
```python
# Line 50-300
def render_module(module_config: dict) -> dict:
    answers = {}
    
    # Loop through JSON sections
    for section in module_config["sections"]:
        st.header(section["title"])  # From JSON
        
        # Loop through JSON fields
        for field in section["fields"]:
            # Check if should show (conditional logic from JSON)
            if should_show_field(field, answers):
                # Render widget based on type from JSON
                answer = render_field(field)
                answers[field["field_id"]] = answer
    
    return answers
```

**Example: Adding a New Question**

1. **Edit JSON only**:
   ```json
   {
     "field_id": "mobility_wheelchair",
     "type": "radio",
     "label": "Do they use a wheelchair?",
     "required": true,
     "options": [
       {"value": "no", "label": "No", "score": 0, "flags": []},
       {"value": "part_time", "label": "Part-time", "score": 5, "flags": ["mobility_aid"]},
       {"value": "full_time", "label": "Full-time", "score": 15, "flags": ["mobility_limited"]}
     ]
   }
   ```

2. **Deploy JSON** (no code changes)

3. **Result**: New question appears in UI, scores calculated, everything works

**Key Insight**: JSON is the SOURCE OF TRUTH. Code is just an interpreter of JSON.

---

### Q4: How Is It Packaged and Sent to the LLM?

**Short Answer**: The SAME `answers` dict (from user selections) is sent to BOTH the deterministic scoring engine AND the LLM. The LLM also receives the deterministic result as context.

**Where to Look in Code**:

📁 **Orchestration**: `products/gcp_v4/modules/care_recommendation/logic.py`
- **Function**: `derive_outcome(answers, context, config)`
- **Lines**: 1081-1300
- **Flow**:
  1. Calculate deterministic score (line 1115-1120)
  2. Apply gates (line 1140-1180)
  3. Determine allowed tiers (line 1185-1200)
  4. **Send to LLM** (line 1240-1280) ← Same `answers` dict
  5. Adjudicate (line 83)

Code snippet:
```python
# Line 1081-1300
def derive_outcome(answers: dict, context: dict, config: dict):
    # STEP 1: Deterministic scoring
    total_score, details = _calculate_score(answers, module_data)  # Line 1115
    det_tier = _determine_tier(total_score, module_data)  # Line 1120
    
    # STEP 2: Apply gates
    cognitive_level = answers.get("cognition_level")
    allowed_tiers = _apply_cognitive_gate(det_tier, cognitive_level)  # Line 1140
    
    # STEP 3: LLM request (if enabled)
    llm_tier = None
    llm_conf = None
    
    if config.get("FEATURE_GCP_LLM_TIER") != "off":
        # SEND SAME ANSWERS TO LLM
        llm_tier, llm_conf = get_llm_tier_suggestion(
            answers=answers,  # ← SAME dict used for deterministic
            det_tier=det_tier,
            allowed_tiers=allowed_tiers,
            bands={"cog": cognitive_level, "sup": support_level}
        )  # Line 1240-1280
    
    # STEP 4: Choose final tier
    final_tier = _choose_final_tier(det_tier, allowed_tiers, llm_tier, llm_conf)
    
    return final_tier
```

📁 **LLM Request Builder**: `ai/gcp_navi_engine.py`
- **Function**: `get_llm_tier_suggestion(answers, det_tier, allowed_tiers, bands)`
- **Lines**: 50-300
- **What it does**:
  1. Converts `answers` dict to human-readable narrative (line ~100)
  2. Builds structured prompt with JSON schema (line ~150)
  3. Sends to OpenAI (line ~200)
  4. Validates response (line ~250)

Code snippet:
```python
# ai/gcp_navi_engine.py, Line 50-300
def get_llm_tier_suggestion(answers, det_tier, allowed_tiers, bands):
    # STEP 1: Convert answers to narrative
    context = _build_context_narrative(answers)
    # Example output:
    # "Needs frequent assistance with bathing.
    #  Moderate cognitive impairment affecting daily tasks.
    #  No formal diagnosis present."
    
    # STEP 2: Build prompt
    prompt = f"""
    ASSESSMENT:
    {context}
    
    REFERENCE:
    - Deterministic recommendation: {det_tier}
    - Cognitive band: {bands['cog']}
    - Support band: {bands['sup']}
    
    ALLOWED OPTIONS:
    You must choose from: {', '.join(allowed_tiers)}
    
    Respond with JSON only:
    {{
      "tier": "one of: {', '.join(allowed_tiers)}",
      "confidence": 0.0-1.0,
      "reasoning": "explanation"
    }}
    """
    
    # STEP 3: Call LLM
    response = llm_client.complete(
        prompt=prompt,
        timeout=15,
        response_format={"type": "json_object"}  # JSON mode
    )
    
    # STEP 4: Validate
    result = _parse_and_validate_response(response, allowed_tiers)
    return result["tier"], result["confidence"]
```

**Packaging Example**:

Raw answers dict:
```python
{
  "adl_bathing": "frequent",
  "adl_dressing": "needs_help",
  "cognition_level": "moderate",
  "memory_diagnosis": "none"
}
```

Converted to LLM context:
```
Needs frequent assistance with bathing.
Needs help with dressing (buttons, zippers).
Moderate cognitive impairment affecting daily tasks.
No formal diagnosis present.

Deterministic recommendation: assisted_living
Allowed options: in_home, assisted_living
```

**Key Insight**: LLM receives SAME data as deterministic engine, just in different format (narrative vs. dict).

---

### Q5: How Do JSON Guardrails Work?

**Short Answer**: JSON guardrails are three-layer validation: (1) OpenAI JSON mode forces valid JSON, (2) Prompt includes explicit schema, (3) Code validates every field post-response.

**Where to Look in Code**:

#### Layer 1: OpenAI JSON Mode

📁 **File**: `ai/llm_client.py`
- **Function**: `complete(...)`
- **Lines**: 50-100
- **What it does**: Forces OpenAI to return valid JSON

Code snippet:
```python
# ai/llm_client.py, Line 50-100
def complete(prompt, model="gpt-4o-mini", timeout=15, temperature=0.3, response_format=None):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that responds in JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        response_format=response_format  # {"type": "json_object"} ← ENFORCES JSON
    )
    
    return response.choices[0].message.content
```

**Effect**: LLM cannot return plain text. It MUST return valid JSON.

#### Layer 2: Schema in Prompt

📁 **File**: `ai/gcp_navi_engine.py`
- **Function**: `_build_tier_prompt(...)`
- **Lines**: 150-200
- **What it does**: Includes explicit JSON structure in prompt

Code snippet:
```python
# ai/gcp_navi_engine.py, Line 150-200
def _build_tier_prompt(context, det_tier, allowed_tiers, bands):
    prompt = f"""
    [assessment context...]
    
    Respond with JSON only (no other text):
    {{
      "tier": "one of: {', '.join(allowed_tiers)}",
      "confidence": 0.85,
      "reasoning": "Brief explanation of why this tier is appropriate"
    }}
    
    RULES:
    - "tier" must be one of: {', '.join(allowed_tiers)}
    - "confidence" must be between 0.0 and 1.0
    - "reasoning" must be a string
    """
    return prompt
```

**Effect**: LLM knows EXACTLY what structure to return.

#### Layer 3: Post-Response Validation

📁 **File**: `ai/gcp_navi_engine.py`
- **Function**: `_parse_and_validate_response(response, allowed_tiers)`
- **Lines**: 250-300
- **What it does**: Validates every field after receiving response

Code snippet:
```python
# ai/gcp_navi_engine.py, Line 250-300
def _parse_and_validate_response(response: str, allowed_tiers: list) -> dict:
    # Parse JSON
    try:
        result = json.loads(response)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from LLM: {e}")
    
    # Validate required fields exist
    required_fields = ["tier", "confidence", "reasoning"]
    for field in required_fields:
        if field not in result:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate tier is in allowed set
    if result["tier"] not in allowed_tiers:
        raise ValueError(f"LLM suggested disallowed tier: {result['tier']}")
    
    # Validate confidence range
    if not (0 <= result["confidence"] <= 1):
        raise ValueError(f"Invalid confidence: {result['confidence']}")
    
    # Validate reasoning is non-empty string
    if not isinstance(result["reasoning"], str) or not result["reasoning"]:
        raise ValueError("Reasoning must be non-empty string")
    
    return result
```

**Effect**: Even if LLM returns JSON, code checks that:
- All required fields are present
- Values are in valid ranges
- Tier is one we're allowed to use

### Example: Guardrails in Action

**LLM Returns**:
```json
{
  "tier": "memory_care",
  "confidence": 0.88,
  "reasoning": "High cognitive impairment with behavioral issues"
}
```

**Validation**:
```python
# Check 1: Is it valid JSON? ✓
json.loads(response)  # Works

# Check 2: Has all fields? ✓
"tier" in result  # True
"confidence" in result  # True
"reasoning" in result  # True

# Check 3: Is tier allowed? ✗
allowed_tiers = ["in_home", "assisted_living"]
result["tier"] in allowed_tiers  # False! "memory_care" not allowed

# REJECT: Raise ValueError, fall back to deterministic
```

**Key Insight**: Three layers ensure LLM output is always valid and safe to use.

---

## Complete Flow Summary

```
┌──────────────────────────────────────────────────────────────┐
│ 1. USER ANSWERS QUESTIONS (rendered from module.json)       │
│    Result: answers = {"adl_bathing": "frequent", ...}       │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. DETERMINISTIC SCORING (logic.py:800-900)                 │
│    - Loop through answers                                    │
│    - Look up each answer's score in module.json            │
│    - Sum scores → total_score                               │
│    - Map to tier using tier_thresholds in module.json      │
│    Result: det_tier = "assisted_living", score = 55        │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. APPLY GATES (logic.py:1140-1180)                         │
│    - Check cognitive level from answers                      │
│    - Check behavior patterns from answers                    │
│    - Determine allowed_tiers based on rules                 │
│    Result: allowed_tiers = ["in_home", "assisted_living"]  │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ 4. LLM REQUEST (ai/gcp_navi_engine.py:50-300)               │
│    - Convert answers → narrative                             │
│    - Build prompt with schema                                │
│    - Call OpenAI with JSON mode (Layer 1 guardrail)        │
│    - Parse response                                          │
│    - Validate fields (Layer 3 guardrail)                    │
│    Result: llm_tier = "assisted_living", conf = 0.82       │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ 5. ADJUDICATION (logic.py:83-170)                           │
│    - If LLM tier valid and in allowed_tiers → use LLM      │
│    - Else → use deterministic                               │
│    Result: final_tier = "assisted_living" (from LLM)       │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ 6. PACKAGE RESULT (core/mcip.py:300-400)                    │
│    - Create CareRecommendation contract                      │
│    - Include both det_tier and llm_tier                     │
│    - Add rationale, flags, confidence                       │
│    - Publish to MCIP                                        │
└──────────────────────────────────────────────────────────────┘
```

---

## Key Files Quick Reference

| Question | Primary File | Key Function | Lines |
|----------|-------------|--------------|-------|
| Q1: How are questions scored? | `logic.py` | `_calculate_score()` | 800-850 |
| Q2: How do scores produce recommendations? | `logic.py` | `_determine_tier()` | 850-900 |
| Q3: How does JSON manage variability? | `module.json` | N/A (data file) | All |
| Q3: How are questions rendered? | `core/navi_module.py` | `render_module()` | 50-300 |
| Q4: How is data sent to LLM? | `ai/gcp_navi_engine.py` | `get_llm_tier_suggestion()` | 50-300 |
| Q4: How is context built? | `ai/gcp_navi_engine.py` | `_build_context_narrative()` | 100-150 |
| Q5: JSON Mode (Layer 1)? | `ai/llm_client.py` | `complete()` | 50-100 |
| Q5: Validation (Layer 3)? | `ai/gcp_navi_engine.py` | `_parse_and_validate_response()` | 250-300 |

---

## Recommended Reading Order

For developers who need to understand this system:

1. **Start here**: This document (ARCHITECT_QUESTIONS_ANSWERED.md)
2. **Deep dive**: JSON_CONFIG_AND_LLM_GUIDE.md (complete pipeline explanation)
3. **Find code**: CODE_REFERENCE_MAP.md (exact locations)
4. **Understand architecture**: ARCHITECTURE_FOR_REPLATFORM.md
5. **See flows**: SEQUENCE_DIAGRAMS.md (Section 0: Answer Flow)
6. **Reference daily**: QUICK_REFERENCE.md

**Total reading time**: ~4 hours  
**Result**: Complete understanding of how the system works

---

## Questions or Need Clarification?

All code references in this document are from the prototype codebase at:
- Repository: `cca_senior_navigator_v3`
- Branch: `feature/refactor-gcp-cost-planner`
- Date: 2025-11-07

For additional details, see:
- **JSON_CONFIG_AND_LLM_GUIDE.md** - Expanded explanations with examples
- **CODE_REFERENCE_MAP.md** - Exhaustive file and function reference
- **SEQUENCE_DIAGRAMS.md** - Visual representations of all flows
