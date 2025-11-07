# Sequence Diagrams - Senior Navigator Core Flows

**Prototype Code References**: See specific line numbers in each diagram for exact implementation locations.

---

## 0. Answer Flow: How User Responses Become Recommendations

**This is THE critical flow to understand** - how the same `answers` dict is used for both deterministic and LLM processing.

**Prototype Implementation**: `products/gcp_v4/modules/care_recommendation/logic.py`

```mermaid
sequenceDiagram
    participant User
    participant UI as Module Engine
    participant Logic as logic.py::derive_outcome()
    participant Score as Scoring Functions
    participant Gates as Gate Functions
    participant LLM as LLM Engine
    participant Adj as _choose_final_tier()

    Note over UI: User completes GCP questions
    UI->>UI: Collect answers dict
    Note over UI: answers = {"adl_bathing": "frequent", <br/>"cognition_level": "moderate", ...}
    
    User->>Logic: Submit assessment (line 1081)
    Note over Logic: STEP 1: DETERMINISTIC (always happens)
    
    Logic->>Score: _calculate_score(answers, module_data)
    Note over Score: Lines 1115-1120<br/>Sum option.score for each answer
    Score-->>Logic: total_score = 52
    
    Logic->>Logic: _determine_tier(total_score)
    Note over Logic: Line ~1120<br/>Map 52 → "assisted_living"
    Logic->>Logic: det_tier = "assisted_living"
    
    Logic->>Gates: cognitive_gate(answers, flags)
    Note over Gates: Lines 1140-1150<br/>Check cognition level + diagnosis
    Gates-->>Logic: passes_cognitive_gate = True
    
    Logic->>Gates: cognition_band(answers, flags)
    Gates-->>Logic: cog_band = "moderate"
    
    Logic->>Gates: support_band(answers, flags)
    Gates-->>Logic: sup_band = "high"
    
    Logic->>Logic: Build allowed_tiers set
    Note over Logic: Line ~1150<br/>Start with all tiers
    
    alt Behavior Gate Enabled
        Logic->>Gates: mc_behavior_gate_enabled()
        Gates-->>Logic: True
        Logic->>Logic: Check: moderate × high without risky?
        Note over Logic: Lines 1170-1180<br/>If yes, block MC/MC-HA
        Logic->>Logic: allowed_tiers = {in_home, AL}
    end
    
    Logic->>Logic: Choose deterministic tier
    Note over Logic: Line ~1190<br/>det_tier must be in allowed_tiers
    
    Note over Logic: Deterministic Complete!<br/>det_tier = "assisted_living"<br/>allowed_tiers = {"in_home", "assisted_living"}
    
    Note over Logic: STEP 2: LLM (only if enabled)
    
    alt LLM Enabled (feature flag on)
        Logic->>LLM: get_llm_tier_suggestion(...)
        Note over LLM: Lines 1240-1280<br/>Receives:<br/>- answers (SAME dict)<br/>- det_tier ("assisted_living")<br/>- allowed_tiers ([in_home, AL])<br/>- bands ({cog: moderate, sup: high})
        
        LLM->>LLM: Build narrative from answers
        LLM->>LLM: Construct prompt with context
        LLM->>LLM: Call OpenAI API (15s timeout)
        
        alt LLM Success
            LLM-->>Logic: llm_tier = "in_home", conf = 0.75
        else LLM Timeout
            LLM-->>Logic: llm_tier = None, conf = None
        end
    else LLM Disabled
        Logic->>Logic: llm_tier = None
    end
    
    Note over Logic: STEP 3: ADJUDICATION (LLM-first policy)
    
    Logic->>Adj: _choose_final_tier(det_tier, allowed_tiers, llm_tier, ...)
    Note over Adj: Line 83-170<br/>LLM-first policy
    
    alt LLM tier valid and in allowed_tiers
        Adj->>Adj: final = llm_tier
        Note over Adj: Line ~130<br/>source = "llm"
        Adj-->>Logic: ("in_home", {source: "llm"})
    else LLM missing or invalid
        Adj->>Adj: final = det_tier
        Note over Adj: Line ~150<br/>source = "fallback"
        Adj-->>Logic: ("assisted_living", {source: "fallback"})
    end
    
    Logic->>Logic: Build CareRecommendation contract
    Logic-->>UI: Return recommendation
    UI->>User: Show results
```

**Key Takeaway**: The `answers` dictionary flows through THREE stages:
1. **Deterministic scoring** (always) - calculates score and base tier
2. **LLM suggestion** (optional) - same answers sent to AI with deterministic result as context
3. **Adjudication** (always) - chooses between LLM (if valid) and deterministic (fallback)

---

## 1. GCP Assessment Flow (with LLM)

```mermaid
sequenceDiagram
    participant U as User
    participant UI as UI Layer
    participant ME as Module Engine
    participant SE as Scoring Engine
    participant LLM as LLM Mediator
    participant MCIP as MCIP
    participant DB as Persistence

    U->>UI: Start GCP Assessment
    UI->>ME: Load module.json
    ME-->>UI: Render questions
    
    loop For each question
        U->>UI: Answer question
        UI->>ME: Collect answer
        ME->>ME: Validate input
    end
    
    U->>UI: Submit assessment
    UI->>SE: derive_outcome(answers)
    
    SE->>SE: Calculate score (sum option.score)
    SE->>SE: Map score → deterministic_tier
    SE->>SE: Apply behavior gates → allowed_tiers
    
    alt LLM Enabled (FEATURE_GCP_LLM_TIER != "off")
        SE->>LLM: Request tier suggestion
        LLM->>LLM: Build prompt with context
        LLM->>OpenAI: API call (15s timeout)
        
        alt Success
            OpenAI-->>LLM: Tier + confidence
            LLM->>LLM: Validate tier in allowed_tiers
            LLM-->>SE: (llm_tier, confidence)
        else Timeout/Error
            LLM-->>SE: (None, None)
        end
    end
    
    SE->>SE: Adjudicate final tier
    
    alt LLM tier valid
        SE->>SE: final = llm_tier (source: "llm")
    else LLM invalid/missing
        SE->>SE: final = deterministic_tier (source: "fallback")
    end
    
    SE->>SE: Build flags (falls_risk, etc.)
    SE->>SE: Build CareRecommendation contract
    SE->>MCIP: publish_care_recommendation(rec)
    MCIP->>DB: Persist contract
    MCIP->>MCIP: Mark "gcp" complete
    MCIP->>MCIP: Unlock "cost_planner"
    
    MCIP-->>UI: Success
    UI->>U: Show results + next step
```

---

## 2. Cost Planner Quick Estimate Flow

```mermaid
sequenceDiagram
    participant U as User
    participant CP as Cost Planner
    participant MCIP as MCIP
    participant Reg as Regional Pricing
    participant Calc as Cost Calculator
    participant DB as Persistence

    U->>CP: Start Cost Planner
    CP->>MCIP: get_care_recommendation()
    
    alt GCP completed
        MCIP-->>CP: CareRecommendation (tier, hours)
        CP->>CP: Extract tier + hours_llm_band
    else GCP not completed
        MCIP-->>CP: None
        CP->>MCIP: Auto-unlock cost_planner
        CP->>U: Prompt for care type manually
    end
    
    U->>CP: Enter ZIP code
    CP->>Reg: lookup_region(zip)
    
    alt Region found
        Reg-->>CP: Regional pricing data
    else No region
        Reg-->>CP: Default national pricing
    end
    
    alt In-Home Care
        CP->>CP: Convert hours_band → scalar (e.g., "4-8h" → 6.0)
        U->>CP: Adjust hours (optional)
        CP->>Calc: hourly_rate × hours × 30
    else Facility Care
        CP->>Calc: Get base_monthly for tier
        CP->>Calc: Add modifiers (medical, memory)
    end
    
    Calc->>Calc: Apply regional multiplier
    Calc-->>CP: monthly_total + breakdown
    
    CP->>CP: Build FinancialProfile contract
    CP->>MCIP: publish_financial_profile(profile)
    MCIP->>DB: Persist contract
    MCIP->>MCIP: Mark "cost_planner" complete
    
    MCIP-->>CP: Success
    CP->>U: Show cost estimate + next steps
```

---

## 3. MCIP Contract Publishing Flow

```mermaid
sequenceDiagram
    participant Prod as Product (GCP/Cost/PFMA)
    participant MCIP as MCIP Coordinator
    participant Valid as Contract Validator
    participant DB as Persistence Layer
    participant Event as Event Bus

    Prod->>MCIP: publish_care_recommendation(rec)
    MCIP->>Valid: validate_contract(rec)
    
    alt Valid contract
        Valid-->>MCIP: OK
        MCIP->>MCIP: Store in state["mcip"]["care_recommendation"]
        MCIP->>DB: persist_contract("care_recommendation", rec)
        MCIP->>Event: emit("contract.published", "care_recommendation")
        MCIP-->>Prod: Success
    else Invalid contract
        Valid-->>MCIP: ValidationError
        MCIP-->>Prod: Error (missing fields)
    end
    
    Note over MCIP: Product completion can happen separately
    
    Prod->>MCIP: mark_product_complete("gcp_v4")
    MCIP->>MCIP: Normalize key: "gcp_v4" → "gcp"
    MCIP->>MCIP: Add to completed_products
    MCIP->>MCIP: Update unlocked_products (journey rules)
    MCIP->>DB: persist_journey_state()
    MCIP->>Event: emit("product.completed", "gcp")
    MCIP-->>Prod: Success
```

---

## 4. LLM-First Adjudication Policy

```mermaid
flowchart TD
    A[Start: User completes GCP] --> B[Calculate deterministic tier]
    B --> C[Apply behavior gates]
    C --> D{LLM Enabled?}
    
    D -->|No| E[Use deterministic tier]
    D -->|Yes| F[Request LLM tier]
    
    F --> G{LLM responds in time?}
    G -->|No timeout| H{LLM tier in allowed_tiers?}
    G -->|Timeout| I[Fallback: Use deterministic]
    
    H -->|Yes| J[Use LLM tier]
    H -->|No| K[Fallback: Use deterministic]
    
    E --> L[Final Recommendation]
    I --> L
    J --> L
    K --> L
    
    L --> M[Publish CareRecommendation]
    M --> N[Mark GCP complete]
    N --> O[Unlock Cost Planner]
    
    style J fill:#90EE90
    style I fill:#FFB6C1
    style K fill:#FFB6C1
    style E fill:#87CEEB
```

**Key Insight**: LLM gets first chance, but deterministic is always ready as fallback.

---

## 5. Behavior Gate Decision Logic

```mermaid
flowchart TD
    A[Start: Calculate deterministic tier] --> B[Tier = Memory Care?]
    
    B -->|No| Z[Keep tier]
    B -->|Yes| C[Check cognition level]
    
    C --> D{Cognition = MODERATE?}
    D -->|No| Z
    D -->|Yes| E[Count ADL dependencies]
    
    E --> F{ADL count >= 4?}
    F -->|No| Z
    F -->|Yes| G[Check risky behaviors]
    
    G --> H{Has wandering/aggression/etc?}
    H -->|Yes| Z[Keep Memory Care]
    H -->|No| I[Gate triggered!]
    
    I --> J[Remove MC/MC-HA from allowed_tiers]
    J --> K[Downgrade to Assisted Living]
    
    Z --> L[Continue to adjudication]
    K --> L
    
    style I fill:#FF6B6B
    style K fill:#FFA500
    style Z fill:#90EE90
```

**Rule**: Moderate cognition + high support needs = AL, unless risky behaviors present.

---

## 6. JSON Configuration Loading & Caching

```mermaid
sequenceDiagram
    participant App as Application
    participant Cache as Config Cache
    participant FS as File System
    participant Val as JSON Validator
    participant UI as UI Engine

    App->>Cache: load_module_config("module.json")
    
    alt Cache hit
        Cache-->>App: Cached config
    else Cache miss
        Cache->>FS: Read module.json
        FS-->>Cache: Raw JSON
        Cache->>Val: validate_schema(json)
        
        alt Valid JSON
            Val-->>Cache: OK
            Cache->>Cache: Parse + store
            Cache-->>App: Parsed config
        else Invalid JSON
            Val-->>Cache: SchemaError
            Cache-->>App: Error (load defaults)
        end
    end
    
    App->>UI: render_module(config)
    UI->>UI: Generate form fields
    UI-->>App: Rendered UI
```

**Key Point**: Configuration is loaded once, validated, cached. UI is generated dynamically from JSON.

---

## 7. Multi-Product Journey Flow (Hub Navigation)

```mermaid
sequenceDiagram
    participant U as User
    participant Hub as Hub/Lobby
    participant MCIP as MCIP
    participant GCP as GCP Product
    participant CP as Cost Planner
    participant PFMA as PFMA Product

    U->>Hub: View product lobby
    Hub->>MCIP: get_completed_products()
    MCIP-->>Hub: ["gcp"]
    Hub->>MCIP: get_unlocked_products()
    MCIP-->>Hub: ["gcp", "cost_planner"]
    
    Hub->>U: Show tiles (GCP=complete, CP=unlocked, PFMA=locked)
    
    U->>Hub: Click Cost Planner
    Hub->>CP: Navigate to product
    CP->>MCIP: get_care_recommendation()
    MCIP-->>CP: CareRecommendation (from GCP)
    CP->>U: Show intro with care context
    
    Note over U,CP: User completes Cost Planner
    
    CP->>MCIP: publish_financial_profile(profile)
    CP->>MCIP: mark_product_complete("cost_planner")
    MCIP->>MCIP: Unlock "pfma" (based on journey rules)
    MCIP-->>CP: Success
    
    CP->>Hub: Navigate back to lobby
    Hub->>MCIP: get_unlocked_products()
    MCIP-->>Hub: ["gcp", "cost_planner", "pfma"]
    Hub->>U: Show tiles (PFMA now unlocked)
```

**Journey Gating**: Products unlock based on completion rules in MCIP.

---

## 8. Regional Pricing Lookup Flow

```mermaid
flowchart TD
    A[User enters ZIP: 98001] --> B[Load regional_cost_config.json]
    B --> C{ZIP in regions?}
    
    C -->|Yes| D[Return region pricing]
    C -->|No| E[Check ZIP prefix]
    
    E --> F{Prefix match?}
    F -->|Yes| G[Return prefix region]
    F -->|No| H[Return default national pricing]
    
    D --> I[Get tier-specific rates]
    G --> I
    H --> I
    
    I --> J{Care type?}
    J -->|In-Home| K[hourly_rate]
    J -->|Facility| L[base_monthly]
    
    K --> M[Calculate: rate × hours × 30]
    L --> N[Add modifiers]
    
    M --> O[Apply COL multiplier]
    N --> O
    
    O --> P[Return monthly_total + breakdown]
    
    style H fill:#FFA500
    style D fill:#90EE90
```

**Fallback Strategy**: ZIP → Prefix → Default (always returns a price).

---

## 9. Hours Recommendation Integration

```mermaid
sequenceDiagram
    participant GCP as GCP Assessment
    participant LLM as Hours LLM Engine
    participant MCIP as MCIP
    participant CP as Cost Planner
    participant U as User

    Note over GCP: User selects "In-Home Care"
    
    GCP->>GCP: Calculate deterministic hours (if enabled)
    
    alt LLM Hours Enabled
        GCP->>LLM: Request hours band
        LLM->>LLM: Analyze ADLs, cognition, behaviors
        LLM-->>GCP: "4-8h" (with confidence)
    else LLM Disabled
        GCP->>GCP: Use deterministic only
    end
    
    GCP->>MCIP: publish_care_recommendation(rec)
    Note over MCIP: rec.hours_llm_band = "4-8h"
    
    U->>CP: Navigate to Cost Planner
    CP->>MCIP: get_care_recommendation()
    MCIP-->>CP: rec (includes hours_llm_band)
    
    CP->>CP: Convert "4-8h" → 6.0 hours (midpoint)
    CP->>U: Pre-populate with 6.0 hours
    
    U->>CP: Adjust to 8.0 hours (optional)
    CP->>CP: Calculate cost with 8.0 hours
    CP->>U: Show updated cost estimate
```

**Key**: Hours flow from GCP → MCIP → Cost Planner, user can override.

---

## 10. Error Handling & Fallback Strategy

```mermaid
flowchart TD
    A[Start: Process user request] --> B{Config loaded?}
    
    B -->|No| C[Load from disk]
    C --> D{Load successful?}
    D -->|No| E[Load default config]
    D -->|Yes| F[Continue]
    E --> F
    B -->|Yes| F
    
    F --> G{LLM enabled?}
    G -->|No| H[Use deterministic only]
    G -->|Yes| I[Request LLM]
    
    I --> J{LLM responds?}
    J -->|Yes| K{Response valid?}
    J -->|No| L[Timeout - fallback]
    
    K -->|Yes| M[Use LLM result]
    K -->|No| N[Invalid - fallback]
    
    H --> O[Final result]
    L --> O
    M --> O
    N --> O
    
    O --> P{Result valid?}
    P -->|Yes| Q[Publish to MCIP]
    P -->|No| R[Show error to user]
    
    Q --> S[Success]
    
    style L fill:#FFB6C1
    style N fill:#FFB6C1
    style E fill:#FFA500
    style R fill:#FF6B6B
    style S fill:#90EE90
```

**Principle**: Every step has a fallback. System never fails completely.

---

## Key Observations for Developers

### Critical Patterns

1. **Defensive Loading**: Always have defaults for config files
2. **Timeout Discipline**: LLM calls must timeout (15s max)
3. **Validation Everywhere**: Validate LLM responses, user inputs, contract fields
4. **Fallback Chain**: LLM → Deterministic → Default
5. **Idempotent Publishing**: Publishing same contract twice is safe

### State Transitions

```
Product States:
  locked → unlocked → in_progress → complete

Contract States:
  None → draft → published → archived

LLM States:
  off → shadow → assist → replace
```

### Integration Points

| From | To | Via | Data |
|------|-----|-----|------|
| GCP | Cost Planner | MCIP | CareRecommendation |
| Cost Planner | PFMA | MCIP | FinancialProfile |
| Any Product | MCIP | Direct call | Contracts |
| MCIP | Persistence | Auto-save | All contracts |

---

## Testing Scenarios

### Scenario 1: Happy Path (with LLM)
1. User completes GCP
2. LLM suggests tier (valid)
3. Tier published to MCIP
4. User navigates to Cost Planner
5. Cost Planner reads GCP recommendation
6. Cost calculated successfully
7. Financial profile published

**Expected**: All products complete, contracts valid.

---

### Scenario 2: LLM Timeout
1. User completes GCP
2. LLM times out (>15s)
3. **Fallback to deterministic tier**
4. Tier published to MCIP (source: "fallback_timeout")
5. Rest of flow continues normally

**Expected**: System works perfectly without LLM.

---

### Scenario 3: Direct Cost Planner Access
1. User navigates to Cost Planner (skips GCP)
2. Cost Planner checks MCIP for CareRecommendation
3. **None found**
4. Cost Planner auto-unlocks itself
5. User manually selects care type
6. Cost calculated with defaults

**Expected**: Cost Planner works standalone.

---

### Scenario 4: Behavior Gate Triggered
1. User answers: moderate cognition + 5 ADLs + no risky behaviors
2. Deterministic tier: Memory Care
3. **Gate blocks Memory Care**
4. Allowed tiers: [Assisted Living, In-Home]
5. LLM suggests Memory Care
6. **Adjudication rejects LLM (not in allowed_tiers)**
7. Final tier: Assisted Living (source: "fallback_gate")

**Expected**: Gate overrides both deterministic and LLM.

---

**Document Version**: 1.0  
**Companion To**: ARCHITECTURE_FOR_REPLATFORM.md  
**Last Updated**: 2025-11-07
