# 🧠 NAVI Core - AI Advisor Orchestration Engine

**Strategic multi-tier RAG system for contextual, personalized senior care guidance.**

NAVI Core is the orchestration engine powering the Senior Navigator's AI Advisor. It implements a hybrid intelligence approach combining deterministic FAQ matching, semantic retrieval, and LLM generation with validation guardrails.

---

## 🎯 Strategic Overview

### The Challenge
Senior care planning involves:
- **Information overload** - Families face 100+ decisions across care levels, costs, legal, and emotional domains
- **Personalization needs** - Each family's situation is unique (health, budget, preferences, geography)
- **Trust requirements** - High-stakes decisions demand accuracy, empathy, and ethical AI behavior
- **Efficiency goals** - Fast answers for common questions, deep guidance for complex scenarios

### The Solution
NAVI Core implements a **tiered orchestration architecture**:

1. **Tier 1: Mini-FAQ** (Instant, deterministic)
   - Exact/fuzzy matching for 50+ common questions
   - Zero latency, 100% confidence
   - Example: "What is assisted living?" → Instant factual answer

2. **Tier 2: Semantic RAG** (Context-aware, retrieval-based) *[Planned]*
   - Embedding-based similarity search across knowledge bases
   - Retrieves relevant chunks from GCP cases, cost data, partner info
   - Combines multiple sources for comprehensive answers

3. **Tier 3: LLM Generation** (Complex reasoning, personalized)
   - Full GPT-4 generation with context and guardrails
   - Handles nuanced questions, emotional support, multi-step guidance
   - Validates output for safety, accuracy, empathy

**Key Innovation**: Graceful degradation - if Tier 1 matches, skip LLM cost/latency. If Tier 2 retrieves high-quality context, use it. Only invoke full LLM when needed.

---

## 🏗️ Technical Architecture

### Module Structure
```
apps/navi_core/
├── api.py                  # Public interface (get_answer, reload_config)
├── orchestrator.py         # Multi-tier routing logic
├── rag.py                  # Tier-1 FAQ + Tier-2 semantic retrieval
├── validator.py            # Answer validation (safety, accuracy, empathy)
├── memory.py               # Conversation tracking (short + long term)
├── prompt_manager.py       # Prompt templates and versioning
├── models.py               # Pydantic v2 data models
├── config/
│   ├── mini_faq.json       # Tier-1 question/answer pairs
│   ├── navi_prompt.yaml    # System prompts and templates
│   ├── sources.json        # Tier-2 knowledge source configuration
│   └── schema.json         # API request/response schema
└── tests/                  # Comprehensive test suite
```

### Data Flow
```
User Question
    ↓
[API Layer] get_answer()
    ↓
[Orchestrator] Route to tier
    ↓
┌─────────────┬─────────────┬─────────────┐
│  Tier 1     │  Tier 2     │  Tier 3     │
│  MiniFAQ    │  Semantic   │  LLM        │
│  Match?     │  Retrieve?  │  Generate   │
└─────────────┴─────────────┴─────────────┘
    ↓
[Validator] Check safety, accuracy, empathy
    ↓
[Memory] Store in conversation history
    ↓
NaviAnswer (question, answer, tier, confidence, sources)
```

### Integration with Existing Systems

**Feature Flag Control** (`core/flags.py`):
```python
FEATURE_LLM_NAVI = "assist"  # off|shadow|assist|adjust
```
- `off` - NAVI Core disabled, static content only
- `shadow` - Run in background, log results, don't show to users
- `assist` - Blend NAVI Core with static content
- `adjust` - Fully replace static content with NAVI Core

**LLM Client** (`ai/llm_client.py`):
- NAVI Core reuses existing `get_client()` infrastructure
- No new API keys or configuration needed
- Respects rate limits and error handling

**Session State**:
- Conversation tracking integrates with Streamlit session
- Future: Persist to `core/session_store.py` for cross-session memory

---

## 📦 Data Models (Pydantic v2)

### NaviAnswer
Complete answer object returned by `get_answer()`:
```python
@dataclass
class NaviAnswer:
    question: str                    # Original question
    answer: str                      # Generated answer
    tier: int                        # 1=FAQ, 2=RAG, 3=LLM
    confidence: float                # 0.0-1.0 confidence score
    validated: ValidationResult      # Safety/accuracy check
    sources: List[ChunkMetadata]     # Retrieved knowledge chunks
```

### ValidationResult
Safety and quality validation:
```python
@dataclass
class ValidationResult:
    passed: bool                     # Did validation pass?
    confidence: float                # Validation confidence
    reason: Optional[str]            # Failure reason if applicable
```

### ChunkMetadata
Retrieved knowledge chunk from Tier-2 RAG:
```python
@dataclass
class ChunkMetadata:
    id: str                          # Unique chunk ID
    source: str                      # Source file/document
    text: str                        # Retrieved text
    similarity: float                # Cosine similarity score
```

---

## 🚀 Usage Examples

### Basic Question Answering
```python
from apps.navi_core import get_answer

# Simple FAQ question (Tier-1)
result = get_answer("What is assisted living?")
print(result.answer)
# Output: "Assisted living is a residential care option..."
print(f"Tier: {result.tier}, Confidence: {result.confidence}")
# Output: Tier: 1, Confidence: 1.0
```

### Personalized Guidance
```python
# Include user name for personalization
result = get_answer(
    question="How do I choose between assisted living and memory care?",
    name="Mary",
    tags=["gcp", "care_recommendation"]
)
print(result.answer)
# LLM considers user name and context tags
```

### Conversation Tracking
```python
import uuid

# Start conversation
conv_id = str(uuid.uuid4())

# First question
result1 = get_answer(
    question="What is memory care?",
    conversation_id=conv_id
)

# Follow-up question (has context from first)
result2 = get_answer(
    question="How much does it typically cost per month?",
    conversation_id=conv_id
)
```

### Mode Control
```python
# Shadow mode: Run LLM in background, don't show results
result = get_answer(
    question="What are my options?",
    mode="shadow"
)

# Assist mode: Blend static + LLM
result = get_answer(
    question="What are my options?",
    mode="assist"
)

# Adjust mode: Full LLM replacement
result = get_answer(
    question="What are my options?",
    mode="adjust"
)
```

---

## 🧪 Testing

### Run Full Test Suite
```bash
pytest apps/navi_core/tests -v
```

### Run Specific Tests
```bash
# Test models (Pydantic validation)
pytest apps/navi_core/tests/test_models.py -v

# Test RAG (FAQ matching, retrieval)
pytest apps/navi_core/tests/test_rag.py -v

# Test validator (safety, empathy checks)
pytest apps/navi_core/tests/test_validator.py -v

# Test orchestrator (tier routing)
pytest apps/navi_core/tests/test_orchestrator.py -v

# Test API (public interface)
pytest apps/navi_core/tests/test_api.py -v
```

### Coverage Report
```bash
pytest apps/navi_core/tests --cov=apps.navi_core --cov-report=html
open htmlcov/index.html
```

### Expected Test Results
- **test_models.py**: 9 tests - Pydantic validation, field constraints
- **test_rag.py**: 9 tests - FAQ matching, case sensitivity, reload
- **test_validator.py**: 7 tests - Safety checks, empathy scoring
- **test_orchestrator.py**: 9 tests - Tier routing, conversation tracking
- **test_api.py**: 9 tests - Public API, mode control

**Total: 43 tests** covering core functionality, edge cases, and integration points.

---

## 🔧 Extension Guide

### Adding New Tier-1 FAQ Entries
Edit `apps/navi_core/config/mini_faq.json`:
```json
{
  "Your new question?": "Your answer goes here.",
  "What is respite care?": "Respite care provides..."
}
```
Reload without restart:
```python
from apps.navi_core import api
api.reload_config()
```

### Implementing Tier-2 Semantic Retrieval
1. **Prepare Knowledge Base**:
   - Add training data to `data/training/`
   - Configure sources in `apps/navi_core/config/sources.json`

2. **Generate Embeddings**:
   ```python
   from apps.navi_core.rag import SemanticRetriever
   
   retriever = SemanticRetriever()
   retriever.index_knowledge_base(
       source="data/training/gcp_cases.jsonl",
       chunk_size=512
   )
   ```

3. **Integrate in Orchestrator**:
   ```python
   # In orchestrator.py
   chunks = self.semantic.retrieve(question, top_k=5)
   if chunks and confidence > 0.7:
       answer = self._build_answer_from_chunks(chunks)
       return NaviAnswer(tier=2, ...)
   ```

### Customizing Validation Rules
Edit `apps/navi_core/validator.py`:
```python
def validate(self, question, answer, sources):
    # Add custom validation logic
    if self._check_medical_advice(answer):
        return ValidationResult(
            passed=False,
            confidence=0.0,
            reason="Medical advice detected - refer to licensed provider"
        )
    # ... existing validation
```

### Adding New Prompt Templates
Edit `apps/navi_core/config/navi_prompt.yaml`:
```yaml
templates:
  your_new_template: |
    Context: {context}
    Question: {question}
    
    Provide a {tone} answer with {detail_level} detail:
```
Use in orchestrator:
```python
prompt = self.prompt_manager.build_prompt(
    "your_new_template",
    {"context": ctx, "question": q, "tone": "empathetic", "detail_level": "high"}
)
```

---

## 🛡️ Data Protection & Compliance

### Privacy by Design
- **No PII in logs**: Question text is logged, but user identifiers are hashed
- **Conversation isolation**: Each conversation has unique UUID, no cross-user leakage
- **Ephemeral memory**: Short-term memory cleared after session timeout
- **Opt-in persistence**: Long-term memory requires explicit user consent

### Ethical AI Guardrails
1. **Safety Validation**: Blocks harmful content (self-harm, medical diagnoses)
2. **Empathy Scoring**: Ensures compassionate tone for sensitive topics
3. **Source Attribution**: Tier-2/3 answers cite sources for fact-checking
4. **Confidence Thresholds**: Low-confidence answers trigger human escalation

### IP & Patent Alignment
NAVI Core's architecture aligns with CCA's patent strategy:
- **Hybrid Intelligence**: Novel tiered approach (deterministic + RAG + LLM)
- **Ethical Personalization**: Context-aware without compromising privacy
- **Validation Layer**: Unique safety/empathy/accuracy pipeline
- **Care Journey Integration**: Seamless with GCP, Cost Planner, Financial Assessment

---

## 🗺️ Roadmap

### Phase 1: Core Scaffold ✅ (Current)
- [x] Pydantic v2 models
- [x] Tier-1 Mini-FAQ retriever
- [x] Multi-tier orchestrator (with Tier-2/3 placeholders)
- [x] Answer validator
- [x] Conversation memory
- [x] Prompt manager
- [x] Public API
- [x] Comprehensive test suite
- [x] Documentation

### Phase 2: Semantic RAG 🚧 (Next)
- [ ] Embedding generation pipeline
- [ ] Vector database integration (Pinecone/ChromaDB)
- [ ] Knowledge base indexing (GCP cases, cost data, partners)
- [ ] Retrieval + reranking logic
- [ ] Chunk metadata enrichment
- [ ] Tier-2 routing implementation

### Phase 3: Personalization 🔮 (Future)
- [ ] User preference extraction from GCP/Cost Planner
- [ ] Long-term memory persistence
- [ ] Emotional context modeling
- [ ] A/B testing framework for prompts
- [ ] Feedback loop (thumbs up/down on answers)
- [ ] Analytics dashboard (tier distribution, confidence trends)

### Phase 4: Production Hardening 🔮 (Future)
- [ ] Rate limiting and caching
- [ ] Async/streaming responses
- [ ] Fallback chain resilience
- [ ] Performance monitoring (latency, cost per answer)
- [ ] Human-in-the-loop escalation
- [ ] Compliance audit logging

---

## 📞 Support & Contribution

### Questions?
- **Architecture**: See `docs/ARCHITECTURE.md`
- **Flag System**: See `docs/FLAG_REGISTRY.md`
- **Contributing**: See `docs/CONTRIBUTING.md`

### Common Issues

**Import errors**:
```python
# Make sure you're importing from the package root
from apps.navi_core import get_answer  # ✅ Correct
from navi_core import get_answer       # ❌ Wrong
```

**FAQ not loading**:
- Check file path: `apps/navi_core/config/mini_faq.json`
- Validate JSON syntax (no trailing commas)
- Reload: `api.reload_config()`

**LLM not responding**:
- Check `FEATURE_LLM_NAVI` flag in `core/flags.py`
- Verify OpenAI API key configured
- Check logs for `[NAVI_ORCH]` error messages

---

## 📄 License & Copyright

© 2025 Care Concierge Associates  
Proprietary and confidential. Patent pending.

---

**Built with ❤️ for families navigating senior care planning.**

*NAVI Core - Because every family deserves compassionate, accurate guidance.*
