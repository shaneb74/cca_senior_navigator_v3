# Implementation Guide: From Python Prototype to Production

**Purpose**: Step-by-step guide for re-implementing Senior Navigator in a new technology stack.

**Target Audience**: Development teams building production version in Java, C#, TypeScript, etc.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Phase 1: Foundation](#phase-1-foundation)
3. [Phase 2: GCP Core](#phase-2-gcp-core)
4. [Phase 3: Cost Planner](#phase-3-cost-planner)
5. [Phase 4: Integration & Polish](#phase-4-integration--polish)
6. [Testing Strategy](#testing-strategy)
7. [Production Readiness](#production-readiness)

---

## Prerequisites

### What You Need

- [ ] Access to prototype codebase for reference
- [ ] Architecture documents (ARCHITECTURE_FOR_REPLATFORM.md, SEQUENCE_DIAGRAMS.md)
- [ ] JSON configuration files:
  - `products/gcp_v4/modules/care_recommendation/module.json`
  - `config/regional_cost_config.json`
  - `config/cost_planner_v2_modules.json`
- [ ] OpenAI API key (if using LLM features)
- [ ] Understanding of contract schemas (CareRecommendation, FinancialProfile)

### Technology Stack Decisions

**Required**:
- [ ] Backend language/framework (Java Spring, .NET, Node/Express, etc.)
- [ ] Frontend framework (React, Vue, Angular, etc.)
- [ ] Database (PostgreSQL, MySQL, MongoDB, etc.)
- [ ] State management approach
- [ ] API architecture (REST, GraphQL, etc.)

**Optional**:
- [ ] LLM provider (OpenAI, Azure OpenAI, AWS Bedrock, etc.)
- [ ] Caching layer (Redis, Memcached)
- [ ] Queue system (if async processing needed)

---

## Phase 1: Foundation

**Goal**: Build core infrastructure without business logic.

### Step 1.1: MCIP Coordinator

**Estimated Time**: 3-5 days

**Tasks**:
1. Create MCIP singleton/service
2. Define contract DTOs (CareRecommendation, FinancialProfile)
3. Implement contract storage (in-memory + DB persistence)
4. Build journey state manager (completed/unlocked products)
5. Add product key normalization

**Implementation**:

```java
// Example: Java/Spring
@Service
public class MCIPService {
    private Map<String, CareRecommendation> contracts = new ConcurrentHashMap<>();
    private JourneyState journeyState = new JourneyState();
    
    private static final Map<String, String> KEY_NORMALIZATION = Map.of(
        "gcp_v4", "gcp",
        "gcp", "gcp",
        "cost_v2", "cost_planner",
        "cost_planner_v2", "cost_planner"
    );
    
    public void publishCareRecommendation(CareRecommendation rec) {
        // Validate contract
        validateContract(rec);
        
        // Store in memory
        contracts.put("care_recommendation", rec);
        
        // Persist to database
        contractRepository.save(rec);
        
        // Emit event
        eventPublisher.publish("contract.published", "care_recommendation");
    }
    
    public Optional<CareRecommendation> getCareRecommendation() {
        return Optional.ofNullable(contracts.get("care_recommendation"));
    }
    
    public void markProductComplete(String productKey) {
        String canonical = normalizeKey(productKey);
        journeyState.addCompleted(canonical);
        updateUnlockedProducts(canonical);
        persistJourneyState();
        eventPublisher.publish("product.completed", canonical);
    }
    
    private String normalizeKey(String key) {
        return KEY_NORMALIZATION.getOrDefault(key, key);
    }
}
```

**Tests**:
- [ ] Contract validation (valid/invalid contracts)
- [ ] Journey state updates
- [ ] Product key normalization
- [ ] Persistence (save/load)

---

### Step 1.2: JSON Configuration System

**Estimated Time**: 2-3 days

**Tasks**:
1. Define JSON schemas for module configurations
2. Build JSON parser/validator
3. Implement caching layer
4. Create configuration loader service

**Implementation**:

```typescript
// Example: TypeScript/Node
interface ModuleConfig {
  module_id: string;
  version: string;
  sections: Section[];
  tier_thresholds: Record<string, Threshold>;
}

class ConfigurationService {
  private cache = new Map<string, ModuleConfig>();
  
  async loadModuleConfig(modulePath: string): Promise<ModuleConfig> {
    // Check cache
    if (this.cache.has(modulePath)) {
      return this.cache.get(modulePath)!;
    }
    
    // Load from file/database
    const rawJson = await fs.readFile(modulePath, 'utf-8');
    const config = JSON.parse(rawJson);
    
    // Validate schema
    this.validateModuleSchema(config);
    
    // Cache
    this.cache.set(modulePath, config);
    
    return config;
  }
  
  private validateModuleSchema(config: any): void {
    // Use JSON schema validator (ajv, joi, etc.)
    const schema = {
      type: 'object',
      required: ['module_id', 'version', 'sections', 'tier_thresholds'],
      properties: {
        module_id: { type: 'string' },
        version: { type: 'string' },
        sections: { type: 'array' },
        tier_thresholds: { type: 'object' }
      }
    };
    
    if (!validator.validate(schema, config)) {
      throw new ValidationError('Invalid module configuration');
    }
  }
}
```

**Tests**:
- [ ] Valid JSON loading
- [ ] Invalid JSON rejection
- [ ] Caching behavior
- [ ] Schema validation

---

### Step 1.3: Feature Flag System

**Estimated Time**: 1-2 days

**Tasks**:
1. Create flag registry
2. Implement flag checking logic
3. Add environment variable support
4. Build flag override system (for testing)

**Implementation**:

```csharp
// Example: C#/.NET
public class FeatureFlagService
{
    private readonly IConfiguration _config;
    
    public enum LLMMode { Off, Shadow, Assist, Adjust }
    
    public LLMMode GetGlobalLLMMode()
    {
        var value = _config["FEATURE_LLM_NAVI"] ?? "off";
        return Enum.Parse<LLMMode>(value, ignoreCase: true);
    }
    
    public bool IsLLMEnabled()
    {
        return GetGlobalLLMMode() != LLMMode.Off;
    }
    
    public bool ShouldUseLLMTier()
    {
        if (!IsLLMEnabled()) return false;
        
        var value = _config["FEATURE_GCP_LLM_TIER"] ?? "off";
        return value == "shadow" || value == "replace";
    }
}
```

**Tests**:
- [ ] Flag reading from environment
- [ ] Default values
- [ ] Override mechanism

---

## Phase 2: GCP Core

**Goal**: Implement deterministic GCP scoring (no LLM yet).

### Step 2.1: Module Rendering Engine

**Estimated Time**: 5-7 days

**Tasks**:
1. Build dynamic form generator from JSON
2. Implement field type handlers (radio, checkbox, text, etc.)
3. Add validation logic
4. Create step progression system
5. Build answer collection system

**Implementation**:

```javascript
// Example: React
function ModuleRenderer({ config }) {
  const [answers, setAnswers] = useState({});
  const [currentSection, setCurrentSection] = useState(0);
  
  const renderField = (field) => {
    switch (field.type) {
      case 'radio':
        return <RadioField field={field} onChange={(value) => handleAnswer(field.id, value)} />;
      case 'checkbox':
        return <CheckboxField field={field} onChange={(value) => handleAnswer(field.id, value)} />;
      case 'text':
        return <TextField field={field} onChange={(value) => handleAnswer(field.id, value)} />;
      default:
        return <div>Unsupported field type: {field.type}</div>;
    }
  };
  
  const handleAnswer = (fieldId, value) => {
    setAnswers({ ...answers, [fieldId]: value });
  };
  
  const canProgress = () => {
    const section = config.sections[currentSection];
    const requiredFields = section.fields.filter(f => f.required);
    return requiredFields.every(f => answers[f.id] !== undefined);
  };
  
  return (
    <div>
      {config.sections[currentSection].fields.map(field => (
        <div key={field.id}>
          {renderField(field)}
        </div>
      ))}
      
      <button onClick={() => setCurrentSection(currentSection + 1)} disabled={!canProgress()}>
        Next
      </button>
    </div>
  );
}
```

**Tests**:
- [ ] All field types render correctly
- [ ] Validation works
- [ ] Step progression
- [ ] Answer persistence

---

### Step 2.2: Deterministic Scoring Engine

**Estimated Time**: 3-4 days

**Tasks**:
1. Build score calculator (sum option.score values)
2. Implement tier mapping logic
3. Create flag builder
4. Add rationale generator
5. Build CareRecommendation constructor

**Implementation**:

```python
# Example: Python (reference from prototype)
def calculate_tier(answers: dict, config: ModuleConfig) -> CareRecommendation:
    # 1. Calculate total score
    total_score = 0
    flags = []
    
    for field_id, selected_value in answers.items():
        field = find_field(config, field_id)
        option = find_option(field, selected_value)
        
        total_score += option.score
        flags.extend(option.flags)
    
    # 2. Map score to tier
    tier = map_score_to_tier(total_score, config.tier_thresholds)
    
    # 3. Build rationale
    rationale = generate_rationale(answers, tier, flags)
    
    # 4. Calculate confidence
    confidence = len(answers) / len(config.all_fields)
    
    # 5. Build contract
    return CareRecommendation(
        tier=tier,
        tier_score=calculate_tier_confidence(tier, total_score),
        confidence=confidence,
        flags=dedupe_flags(flags),
        rationale=rationale,
        generated_at=datetime.now().isoformat(),
        status="complete"
    )

def map_score_to_tier(score: int, thresholds: dict) -> str:
    for tier, threshold in thresholds.items():
        if threshold.min <= score <= threshold.max:
            return tier
    raise ValueError(f"Score {score} not in any tier range")
```

**Tests**:
- [ ] Score calculation (various answer combinations)
- [ ] Tier mapping (boundary cases)
- [ ] Flag building
- [ ] Rationale generation

---

### Step 2.3: Behavior Gates

**Estimated Time**: 2-3 days

**Tasks**:
1. Implement gate logic (moderate cognition + high support)
2. Add risky behavior detection
3. Build allowed_tiers filter
4. Create gate logging

**Implementation**:

```java
public class BehaviorGateService {
    public List<String> applyGates(Map<String, String> answers, String deterministicTier) {
        List<String> allowedTiers = getAllTiers();
        
        // Gate 1: MC/MC-HA behavior gate
        if (shouldApplyMCBehaviorGate(answers)) {
            if (!hasRiskyBehaviors(answers)) {
                // Block memory care tiers
                allowedTiers.remove("memory_care");
                allowedTiers.remove("memory_care_high_acuity");
                
                logger.info("MC behavior gate triggered: blocking memory care");
            }
        }
        
        return allowedTiers;
    }
    
    private boolean shouldApplyMCBehaviorGate(Map<String, String> answers) {
        int cognitionLevel = getCognitionLevel(answers);  // 0-3
        int adlCount = countADLs(answers);
        
        // Moderate cognition (2) + high support (4+ ADLs)
        return cognitionLevel == 2 && adlCount >= 4;
    }
    
    private boolean hasRiskyBehaviors(Map<String, String> answers) {
        String[] riskyBehaviors = {"wandering", "aggression", "elopement"};
        
        for (String behavior : riskyBehaviors) {
            if ("yes".equals(answers.get(behavior))) {
                return true;
            }
        }
        
        return false;
    }
}
```

**Tests**:
- [ ] Gate triggers correctly (moderate cog + high support)
- [ ] Risky behaviors override gate
- [ ] Gate doesn't trigger incorrectly
- [ ] Logging works

---

### Step 2.4: GCP Integration with MCIP

**Estimated Time**: 1-2 days

**Tasks**:
1. Connect scoring engine to MCIP
2. Publish CareRecommendation
3. Mark GCP complete
4. Unlock Cost Planner
5. Add error handling

**Implementation**:

```typescript
class GCPService {
  constructor(
    private mcip: MCIPService,
    private config: ConfigurationService,
    private scoring: ScoringEngine
  ) {}
  
  async completeAssessment(answers: Record<string, any>): Promise<void> {
    try {
      // 1. Calculate tier (deterministic only for now)
      const recommendation = await this.scoring.calculateTier(answers, this.config);
      
      // 2. Publish to MCIP
      await this.mcip.publishCareRecommendation(recommendation);
      
      // 3. Mark complete & unlock next
      await this.mcip.markProductComplete('gcp');
      await this.mcip.unlockProduct('cost_planner');
      
      logger.info('GCP assessment completed successfully');
      
    } catch (error) {
      logger.error('GCP assessment failed', error);
      throw new AssessmentError('Failed to complete assessment', error);
    }
  }
}
```

**Tests**:
- [ ] End-to-end GCP flow
- [ ] MCIP integration
- [ ] Journey state updates
- [ ] Error handling

---

### Step 2.5: LLM Integration (Optional)

**Estimated Time**: 4-6 days

⚠️ **Note**: Only implement if LLM features are required. System works perfectly without it.

**WHERE TO LOOK IN PROTOTYPE CODE**:

📍 **Key Files**:
- `ai/gcp_navi_engine.py` - GCP-specific LLM tier suggestion logic (~300 lines)
- `ai/hours_engine.py` - Hours recommendation LLM logic (~400 lines)
- `ai/llm_mediator.py` - LLM request orchestration with timeout handling
- `ai/llm_client.py` - OpenAI API wrapper
- `products/gcp_v4/modules/care_recommendation/logic.py:83` - `_choose_final_tier()` shows adjudication policy

📍 **How Answers Flow to LLM**:

**Step 1: Deterministic Calculation** (happens FIRST):
```python
# Line 1115 in logic.py
total_score, scoring_details = _calculate_score(answers, module_data)
tier_from_score = _determine_tier(total_score)
allowed_tiers = apply_gates(answers, tier_from_score)
```

**Step 2: LLM Request** (happens AFTER deterministic is done):
```python
# Line ~1240 in logic.py - only if feature flag enabled
if gcp_llm_tier_mode() in {"shadow", "replace"}:
    llm_tier, llm_conf = get_llm_tier_suggestion(
        answers=answers,                    # Same answers used in deterministic
        det_tier=tier_from_score,          # Deterministic result as context
        allowed_tiers=allowed_tiers,        # Gates already applied
        bands={"cog": cog_band, "sup": sup_band}
    )
```

**Step 3: Adjudication** (LLM-first policy):
```python
# Line 83: _choose_final_tier() function
if llm_tier and llm_tier in allowed_tiers:
    return llm_tier, {"source": "llm", "reason": "llm_valid"}
else:
    return det_tier, {"source": "fallback", "reason": "llm_timeout_or_invalid"}
```

**Critical Insight**: The `answers` dict is used for BOTH deterministic scoring AND LLM context. They see the same data, but LLM also sees the deterministic result and allowed tiers.

**Tasks**:
1. Build LLM client wrapper (OpenAI, Azure, etc.)
2. Implement timeout handling (15s max)
3. Create LLM mediator layer
4. Add adjudication logic
5. Implement fallback to deterministic

**Implementation**:

```python
class LLMMediator:
    def __init__(self, client, timeout=15):
        self.client = client
        self.timeout = timeout
    
    def request_tier(self, answers, deterministic_tier, allowed_tiers):
        """Request tier from LLM with timeout and fallback."""
        try:
            # Build context
            context = self._build_context(answers)
            
            # Build prompt
            prompt = self._build_prompt(context, deterministic_tier, allowed_tiers)
            
            # Call LLM with timeout
            response = self.client.complete(
                prompt=prompt,
                model="gpt-4o-mini",
                timeout=self.timeout,
                temperature=0.3
            )
            
            # Parse response
            result = self._parse_response(response)
            
            # Validate
            if result["tier"] not in allowed_tiers:
                logger.warning(f"LLM suggested blocked tier: {result['tier']}")
                return None
            
            return result["tier"]
            
        except TimeoutError:
            logger.warning("LLM timeout, using deterministic")
            return None
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return None
    
    def _build_context(self, answers):
        # Build narrative from answers
        context_parts = []
        
        # ADLs
        adls = [k for k, v in answers.items() if k.startswith('adl_') and v != 'independent']
        if adls:
            context_parts.append(f"Needs help with: {', '.join(adls)}")
        
        # Cognition
        cog = answers.get('cognition_level')
        if cog:
            context_parts.append(f"Cognition: {cog}")
        
        return "\n".join(context_parts)
    
    def _build_prompt(self, context, det_tier, allowed_tiers):
        return f"""Based on this care assessment:

{context}

Deterministic recommendation: {det_tier}
Allowed options: {allowed_tiers}

Suggest the most appropriate care tier from the allowed options.
Respond with JSON: {{"tier": "...", "confidence": 0.0-1.0, "reasoning": "..."}}
"""
```

**Tests**:
- [ ] LLM success case
- [ ] LLM timeout case
- [ ] LLM invalid response case
- [ ] Adjudication logic
- [ ] Feature flag integration

---

## Phase 3: Cost Planner

**Goal**: Implement cost calculation with regional pricing.

### Step 3.1: Regional Pricing System

**Estimated Time**: 2-3 days

**Tasks**:
1. Load regional pricing JSON
2. Implement ZIP lookup logic
3. Add fallback to default pricing
4. Build pricing query service

**Implementation**:

```csharp
public class RegionalPricingService
{
    private Dictionary<string, RegionPricing> _regions;
    private RegionPricing _defaultRegion;
    
    public RegionalPricingService(IConfigurationLoader config)
    {
        var pricingData = config.LoadRegionalPricing();
        _regions = pricingData.Regions;
        _defaultRegion = pricingData.DefaultRegion;
    }
    
    public RegionPricing GetPricingForZip(string zipCode)
    {
        // Exact match
        if (_regions.ContainsKey(zipCode))
        {
            return _regions[zipCode];
        }
        
        // Prefix match (e.g., 900xx -> 900)
        for (int len = zipCode.Length - 1; len > 0; len--)
        {
            string prefix = zipCode.Substring(0, len);
            if (_regions.ContainsKey(prefix))
            {
                return _regions[prefix];
            }
        }
        
        // Default fallback
        return _defaultRegion;
    }
}
```

**Tests**:
- [ ] Exact ZIP match
- [ ] Prefix matching
- [ ] Default fallback
- [ ] Invalid ZIP handling

---

### Step 3.2: Cost Calculator

**Estimated Time**: 3-4 days

**Tasks**:
1. Implement base cost calculation
2. Add modifier logic (medical, memory)
3. Build in-home hours calculation
4. Apply regional multipliers
5. Create cost breakdown

**Implementation**:

```javascript
class CostCalculator {
  constructor(pricingService) {
    this.pricing = pricingService;
  }
  
  calculateMonthlyCost(tier, zipCode, hours = null, modifiers = {}) {
    // 1. Get regional pricing
    const region = this.pricing.getPricingForZip(zipCode);
    
    // 2. Calculate base cost
    let baseCost;
    if (tier === 'in_home') {
      if (!hours) throw new Error('Hours required for in-home care');
      const hourlyRate = region.in_home_care.hourly_rate;
      baseCost = hourlyRate * hours * 30;  // 30 days
    } else {
      baseCost = region[tier].base_monthly;
    }
    
    // 3. Apply modifiers
    let modifierCost = 0;
    if (modifiers.medical_needs) {
      modifierCost += region[tier].medical_addon || 0;
    }
    if (modifiers.memory_addon && tier === 'assisted_living') {
      modifierCost += region[tier].memory_addon || 0;
    }
    
    // 4. Apply regional multiplier
    const subtotal = baseCost + modifierCost;
    const total = subtotal * region.cost_of_living_multiplier;
    
    return {
      monthly_total: Math.round(total * 100) / 100,
      breakdown: {
        base_cost: baseCost,
        modifiers: modifierCost,
        regional_adjustment: total - subtotal,
        region: region.region_name,
        tier: tier,
        hours: hours
      }
    };
  }
}
```

**Tests**:
- [ ] In-home cost calculation
- [ ] Facility cost calculation
- [ ] Modifier application
- [ ] Regional multipliers
- [ ] Breakdown accuracy

---

### Step 3.3: GCP Integration (Hours)

**Estimated Time**: 1-2 days

**Tasks**:
1. Read CareRecommendation from MCIP
2. Extract hours_llm_band
3. Convert band to scalar hours
4. Pre-populate cost form
5. Allow user override

**Implementation**:

```java
public class CostPlannerService {
    private static final Map<String, Double> HOURS_BAND_MAP = Map.of(
        "1-3h", 2.0,
        "4-8h", 6.0,
        "9-12h", 10.5,
        "12-16h", 14.0,
        "16-24h", 20.0,
        "24h", 24.0
    );
    
    public CostEstimateContext initializeCostPlanner() {
        // Get GCP recommendation
        Optional<CareRecommendation> gcpRec = mcip.getCareRecommendation();
        
        CostEstimateContext context = new CostEstimateContext();
        
        if (gcpRec.isPresent()) {
            CareRecommendation rec = gcpRec.get();
            context.setTier(rec.getTier());
            
            // Convert hours band to scalar
            if (rec.getHoursLlmBand() != null) {
                Double hours = HOURS_BAND_MAP.get(rec.getHoursLlmBand());
                context.setSuggestedHours(hours != null ? hours : 6.0);
            }
        } else {
            // No GCP, auto-unlock Cost Planner
            mcip.unlockProduct("cost_planner");
        }
        
        return context;
    }
}
```

**Tests**:
- [ ] GCP recommendation present
- [ ] GCP recommendation missing
- [ ] Hours conversion
- [ ] User override

---

### Step 3.4: Financial Profile Publishing

**Estimated Time**: 1-2 days

**Tasks**:
1. Build FinancialProfile from cost + income data
2. Calculate coverage percentage
3. Calculate gap and runway
4. Publish to MCIP
5. Mark Cost Planner complete

**Implementation**:

```typescript
async function completeFinancialAssessment(
  cost: CostEstimate,
  incomeSources: IncomeSources
): Promise<void> {
  // 1. Calculate coverage
  const coverage = calculateCoverage(cost.monthly_total, incomeSources);
  
  // 2. Build contract
  const profile: FinancialProfile = {
    estimated_monthly_cost: cost.monthly_total,
    coverage_percentage: coverage.percentage,
    gap_amount: coverage.gap,
    runway_months: coverage.runway,
    confidence: 0.9,
    generated_at: new Date().toISOString(),
    status: 'complete',
    breakdown: cost.breakdown,
    coverage_sources: {
      monthly_income: incomeSources.monthly_income,
      asset_liquidation: incomeSources.monthly_asset_coverage,
      insurance: incomeSources.insurance,
      va_benefits: incomeSources.va_benefits
    }
  };
  
  // 3. Publish to MCIP
  await mcip.publishFinancialProfile(profile);
  
  // 4. Mark complete & unlock PFMA
  await mcip.markProductComplete('cost_planner');
  await mcip.unlockProduct('pfma');
}

function calculateCoverage(monthlyCost: number, sources: IncomeSources) {
  const monthlyCoverage = 
    sources.monthly_income +
    sources.insurance +
    sources.va_benefits +
    (sources.total_assets * 0.05 / 12);  // 5% annual safe withdrawal
  
  const gap = monthlyCost - monthlyCoverage;
  const percentage = Math.min(100, (monthlyCoverage / monthlyCost) * 100);
  const runway = gap > 0 ? sources.total_assets / gap : Infinity;
  
  return { percentage, gap, runway: runway === Infinity ? -1 : Math.floor(runway) };
}
```

**Tests**:
- [ ] Coverage calculation
- [ ] Gap calculation (positive/negative)
- [ ] Runway calculation
- [ ] MCIP publishing

---

## Phase 4: Integration & Polish

**Goal**: Connect all pieces and add production features.

### Step 4.1: Hub/Lobby Navigation

**Estimated Time**: 2-3 days

**Tasks**:
1. Build product tile system
2. Show locked/unlocked/completed states
3. Implement journey rules
4. Add navigation logic

**Implementation**:

```javascript
function ProductLobby() {
  const [products, setProducts] = useState([]);
  
  useEffect(() => {
    loadProducts();
  }, []);
  
  const loadProducts = async () => {
    const completed = await mcip.getCompletedProducts();
    const unlocked = await mcip.getUnlockedProducts();
    
    setProducts([
      {
        id: 'gcp',
        name: 'Guided Care Plan',
        status: completed.includes('gcp') ? 'complete' : 
                unlocked.includes('gcp') ? 'unlocked' : 'locked'
      },
      {
        id: 'cost_planner',
        name: 'Cost Planner',
        status: completed.includes('cost_planner') ? 'complete' :
                unlocked.includes('cost_planner') ? 'unlocked' : 'locked'
      },
      {
        id: 'pfma',
        name: 'My Advisor',
        status: completed.includes('pfma') ? 'complete' :
                unlocked.includes('pfma') ? 'unlocked' : 'locked'
      }
    ]);
  };
  
  return (
    <div className="product-lobby">
      {products.map(product => (
        <ProductTile
          key={product.id}
          product={product}
          onClick={() => navigateToProduct(product.id)}
          disabled={product.status === 'locked'}
        />
      ))}
    </div>
  );
}
```

---

### Step 4.2: State Persistence

**Estimated Time**: 3-4 days

**Tasks**:
1. Design database schema for contracts
2. Implement save/load logic
3. Add session management
4. Build snapshot/history system

**Schema Example**:

```sql
-- Contracts table
CREATE TABLE contracts (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL,
  contract_type VARCHAR(50) NOT NULL,  -- 'care_recommendation', 'financial_profile'
  contract_data JSONB NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Journey state table
CREATE TABLE journey_state (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL UNIQUE,
  completed_products TEXT[] NOT NULL DEFAULT '{}',
  unlocked_products TEXT[] NOT NULL DEFAULT ARRAY['gcp'],
  current_product VARCHAR(50),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Audit/history table
CREATE TABLE assessment_history (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL,
  product VARCHAR(50) NOT NULL,
  answers JSONB NOT NULL,
  outcome JSONB NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

---

### Step 4.3: Error Handling & Logging

**Estimated Time**: 2-3 days

**Tasks**:
1. Add structured logging
2. Implement error boundaries
3. Build retry logic
4. Add monitoring hooks

---

## Testing Strategy

### Unit Tests

**Coverage Target**: 80%+

**Focus Areas**:
- Scoring calculations
- Tier mapping
- Gate logic
- Cost calculations
- Contract validation

**Example**:
```java
@Test
public void testScoringEngine_assistedLiving() {
    Map<String, String> answers = Map.of(
        "adl_bathing", "frequent",      // 15 points
        "adl_dressing", "occasional",   // 5 points
        "cognition_level", "mild"       // 10 points
    );
    
    CareRecommendation rec = scoringEngine.calculate(answers, config);
    
    assertEquals("assisted_living", rec.getTier());
    assertTrue(rec.getTierScore() > 40);
    assertTrue(rec.getTierScore() <= 70);
}
```

---

### Integration Tests

**Focus Areas**:
- GCP → MCIP → Cost Planner flow
- Contract publishing
- Journey state updates
- Database persistence

**Example**:
```typescript
describe('GCP to Cost Planner Flow', () => {
  it('should pass care recommendation to cost planner', async () => {
    // Complete GCP
    const answers = { /* ... */ };
    await gcpService.completeAssessment(answers);
    
    // Check MCIP
    const rec = await mcip.getCareRecommendation();
    expect(rec).toBeDefined();
    expect(rec.tier).toBe('assisted_living');
    
    // Start Cost Planner
    const context = await costPlannerService.initialize();
    expect(context.tier).toBe('assisted_living');
    expect(context.suggestedHours).toBeGreaterThan(0);
  });
});
```

---

### End-to-End Tests

**Scenarios**:
1. **Happy path**: User completes GCP → Cost Planner → PFMA
2. **LLM timeout**: System falls back to deterministic
3. **Direct Cost Planner**: User skips GCP
4. **Behavior gate**: MC blocked for moderate cog + high support

---

## Production Readiness

### Performance Checklist

- [ ] Configuration caching implemented
- [ ] Database queries optimized
- [ ] API response times < 500ms (p95)
- [ ] LLM timeout set (15s max)
- [ ] Pagination for large datasets

### Security Checklist

- [ ] Input validation on all forms
- [ ] SQL injection prevention
- [ ] API authentication/authorization
- [ ] Sensitive data encryption
- [ ] HIPAA compliance (if applicable)

### Monitoring Checklist

- [ ] Application logging (structured)
- [ ] Error tracking (Sentry, etc.)
- [ ] Performance monitoring (APM)
- [ ] LLM usage metrics
- [ ] Contract validation failures

### Deployment Checklist

- [ ] Environment configuration
- [ ] Database migrations
- [ ] Feature flag setup
- [ ] Load testing completed
- [ ] Rollback plan documented

---

## Success Metrics

### Functional Completeness

- [ ] All GCP questions render correctly
- [ ] Scoring matches prototype (±5%)
- [ ] Cost calculations match prototype (±2%)
- [ ] Contract schemas validated
- [ ] Journey flow works end-to-end

### Performance

- [ ] Page load < 2s
- [ ] Assessment completion < 5 minutes
- [ ] LLM responses < 15s (or timeout)
- [ ] Database queries < 100ms

### Quality

- [ ] Test coverage > 80%
- [ ] Zero critical bugs
- [ ] Code review passed
- [ ] Documentation complete

---

## Common Pitfalls

### ❌ Don't:
1. **Hardcode questions** - Always use JSON configuration
2. **Make LLM required** - System must work without it
3. **Couple products directly** - Always go through MCIP
4. **Skip validation** - Validate all inputs and LLM responses
5. **Forget feature flags** - Make everything toggleable
6. **Use versioned keys** - Use canonical keys (gcp, not gcp_v4)

### ✅ Do:
1. **Start simple** - Build deterministic first, add LLM later
2. **Test thoroughly** - Every calculation, every flow
3. **Log extensively** - Especially LLM interactions and gates
4. **Follow patterns** - Contracts, MCIP, JSON-driven
5. **Plan for scale** - Cache configs, optimize queries
6. **Document decisions** - Why gates trigger, how costs calculate

---

## Support Resources

### Documentation
- `docs/ARCHITECTURE_FOR_REPLATFORM.md` - System architecture
- `docs/SEQUENCE_DIAGRAMS.md` - Flow diagrams
- `docs/QUICK_REFERENCE.md` - Code patterns

### Prototype Reference
- `products/gcp_v4/modules/care_recommendation/logic.py` - Scoring engine
- `products/cost_planner_v2/utils/cost_calculator.py` - Cost calculations
- `core/mcip.py` - MCIP implementation

### Configuration Files
- `products/gcp_v4/modules/care_recommendation/module.json` - GCP questions
- `config/regional_cost_config.json` - Pricing data
- `config/cost_planner_v2_modules.json` - Financial modules

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-07  
**Questions**: Contact architecture team
