# Navi LLM Enhancement Documentation

## Overview

Navi's dialogue system has been enhanced with LLM capabilities to provide dynamic, contextual advice generation. This enhancement maintains full backward compatibility while adding intelligent, personalized guidance based on the user's specific journey state, care needs, and situation.

## Features

### 🤖 Dynamic Advice Generation
- **Contextual Responses**: LLM generates advice based on user's current journey phase, care recommendations, and personal context
- **Tone Awareness**: Advice adapts tone (supportive, encouraging, celebratory, urgent) based on user's situation
- **Priority Handling**: High-priority situations get urgent styling and immediate attention

### 💡 Enhanced Contextual Tips
- **Smart Tips**: LLM generates relevant, actionable tips for the current situation
- **Explanations**: "Why this matters" context helps users understand the importance of each step
- **Time Estimates**: Realistic expectations for how long tasks typically take
- **Common Questions**: Anticipates and addresses frequent user concerns

### 🎭 Multiple Operating Modes
- **off**: Static dialogue only (JSON-based messages) - default mode
- **shadow**: LLM runs in background, logs results, shows static messages  
- **assist**: LLM provides additional context tips alongside static messages
- **adjust**: LLM fully replaces static messages with dynamic contextual advice

### 🔄 Graceful Fallback
- Automatic fallback to static dialogue if LLM fails or is unavailable
- No disruption to user experience when LLM services are down
- Maintains existing `render_navi_panel()` interface for backward compatibility

## Architecture

### Core Components

#### 1. **NaviLLMEngine** (`ai/navi_llm_engine.py`)
The main LLM-powered advice generation engine:

```python
from ai.navi_llm_engine import NaviLLMEngine, NaviContext

# Generate contextual advice
context = NaviContext(
    journey_phase="in_progress",
    current_location="cost_planner",
    care_tier="assisted_living",
    user_name="Sarah",
    # ... other context
)

advice = NaviLLMEngine.generate_advice(context)
tips = NaviLLMEngine.generate_contextual_tips(context)
```

#### 2. **Enhanced NaviDialogue** (`core/navi_dialogue.py`)
Seamlessly integrates LLM capabilities with existing static system:

```python
from core.navi_dialogue import NaviDialogue

# Automatically tries LLM first, falls back to static
message = NaviDialogue.get_journey_message(
    phase="in_progress",
    is_authenticated=True,
    context={"name": "Sarah", "tier": "assisted_living"}
)
```

#### 3. **Feature Flag Control** (`core/flags.py`)
Controlled via `FEATURE_LLM_NAVI` flag:

```python
from core.flags import get_flag_value

mode = get_flag_value("FEATURE_LLM_NAVI", "off")
# Returns: "off", "shadow", "assist", or "adjust"
```

#### 4. **Enhanced Navi Core** (`core/navi.py`)
Main `render_navi_panel()` function enhanced with LLM capabilities while maintaining existing interface.

### Context Data Structure

The `NaviContext` dataclass provides rich context for LLM prompt generation:

```python
@dataclass
class NaviContext:
    # Journey state
    journey_phase: str          # getting_started, in_progress, nearly_complete, complete
    current_location: str       # hub, gcp, cost_planner, pfma
    progress_percent: int       # 0-100
    
    # User context
    user_name: Optional[str] = None
    is_authenticated: bool = False
    is_returning_user: bool = False
    
    # Care context
    care_tier: Optional[str] = None              # in_home, assisted_living, memory_care
    care_confidence: Optional[float] = None       # 0.0-1.0
    key_flags: list[str] = None                  # High-priority flags (falls, isolation, etc.)
    
    # Financial context
    estimated_cost: Optional[int] = None          # Monthly cost estimate
    cost_concern_level: Optional[str] = None      # low, medium, high
    has_financial_profile: bool = False
    
    # Emotional context
    stress_indicators: list[str] = None           # overwhelmed, confused, urgent
    previous_interactions: int = 0
    
    # Product-specific context
    product_context: dict[str, Any] = None        # GCP answers, Cost Planner selections
```

## Configuration & Setup

### Environment Setup

1. **Set Feature Flag** (choose your mode):
   ```bash
   export FEATURE_LLM_NAVI=adjust    # Full LLM enhancement
   export FEATURE_LLM_NAVI=assist    # LLM tips + static messages  
   export FEATURE_LLM_NAVI=shadow    # LLM logging only
   export FEATURE_LLM_NAVI=off       # Static only (default)
   ```

2. **Ensure OpenAI API Key** is available:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

### Testing the Enhancement

Run the test script to verify everything works:

```bash
# Test with full LLM enhancement
python test_navi_llm.py adjust

# Test different modes
python test_navi_llm.py shadow
python test_navi_llm.py assist
python test_navi_llm.py off
```

### App Integration

The enhancement automatically integrates with existing Navi usage. No code changes required:

```python
# Existing code continues to work
from core.navi import render_navi_panel

# This now supports LLM enhancement based on feature flag
context = render_navi_panel(
    location="hub",
    hub_key="concierge"
)
```

## Usage Examples

### 1. Basic Journey Message
```python
from core.navi_dialogue import NaviDialogue

# LLM-enhanced if enabled, static fallback otherwise
message = NaviDialogue.get_journey_message(
    phase="in_progress",
    is_authenticated=True,
    context={"name": "Sarah", "tier": "assisted_living", "monthly_cost": 3800}
)

# Returns enhanced message with tone, priority, encouragement
print(message["text"])         # "Let's keep building your care plan, Sarah"
print(message["encouragement"]) # "You're making great progress!"
print(message["priority"])     # "medium"
print(message["tone"])         # "encouraging"
```

### 2. Contextual Tips Generation
```python
from core.navi_dialogue import NaviDialogue

# Get enhanced contextual tips
tips = NaviDialogue.get_context_boost(
    phase="in_progress",
    context={"tier": "assisted_living", "progress": 65, "flags": ["falls_risk"]}
)

# Returns LLM-generated tips with explanations
for tip in tips:
    print(f"• {tip}")
# Output:
# • Consider grab bars and shower chairs for fall prevention
# • Review medication list with doctor for balance effects  
# • 💡 Why this matters: Preventing falls is crucial for maintaining independence
# • ⏱️ Time needed: About 10-15 minutes to review safety measures
```

### 3. Module-Specific Guidance
```python
from core.navi_dialogue import NaviDialogue

# Get LLM-enhanced module guidance
guidance = NaviDialogue.get_module_message(
    product_key="cost_planner",
    module_key="income",
    context={"tier": "assisted_living", "estimated_cost": 4200}
)

print(guidance["text"])     # "Let's look at your income sources"
print(guidance["subtext"])  # "We'll calculate how your income covers the $4,200/month for assisted living"
```

### 4. Enhanced Panel Rendering
```python
from core.navi_dialogue import render_navi_enhanced_panel
from ai.navi_llm_engine import NaviLLMEngine, build_navi_context_from_session

# Build context from current session
context = build_navi_context_from_session()

# Generate LLM advice and tips
advice = NaviLLMEngine.generate_advice(context)
tips = NaviLLMEngine.generate_contextual_tips(context)

# Render enhanced panel
render_navi_enhanced_panel(
    title="Your Care Journey",
    advice=advice.__dict__ if advice else None,
    tips=tips.tips if tips else None,
    show_llm_indicator=True
)
```

## LLM Prompting Strategy

### System Prompts

The LLM uses carefully crafted system prompts to ensure consistent, helpful responses:

#### Advice Generation Prompt
```
You are Navi, a warm and supportive digital concierge advisor helping families navigate senior care planning.

Your personality:
- Warm, encouraging, and empathetic
- Clear and actionable in guidance  
- Supportive without being pushy
- Knowledgeable but not overwhelming
- Celebrates progress and milestones

Your role:
- Guide users through the care planning journey
- Provide contextual advice based on their specific situation
- Help reduce overwhelm by breaking things into manageable steps
- Encourage progress while being sensitive to emotional challenges
```

#### Tips Generation Prompt
```
You are Navi providing helpful tips and context to users navigating senior care planning.

Your role:
- Provide actionable, relevant tips for the current journey phase
- Explain why each step matters in the broader context
- Answer common questions users have at this stage
- Give realistic time estimates to set expectations
```

### Context Building

The system builds rich context for LLM prompts:

```python
def _build_advice_prompt(context: NaviContext) -> str:
    """Build contextual prompt for advice generation."""
    prompt_parts = [
        f"Generate supportive advice for a user in the {context.journey_phase} phase"
    ]
    
    if context.user_name:
        prompt_parts.append(f"User name: {context.user_name}")
        
    if context.care_tier:
        prompt_parts.append(f"Care recommendation: {context.care_tier}")
        
    if context.key_flags:
        prompt_parts.append(f"Important considerations: {', '.join(context.key_flags)}")
        
    if context.stress_indicators:
        prompt_parts.append(f"User may be feeling: {', '.join(context.stress_indicators)}")
        
    return "\n".join(prompt_parts)
```

## Performance & Safety

### Response Validation
- **Structured Output**: Uses Pydantic schemas to ensure consistent response format
- **Timeout Handling**: 8-10 second timeouts prevent hanging
- **Error Graceful Degradation**: Automatic fallback to static content on LLM failures

### Content Safety
- **Forbidden Terms**: Filters out inappropriate medical advice or guarantees
- **Tone Validation**: Ensures responses maintain supportive, professional tone
- **Length Limits**: Enforces reasonable message lengths for UI display

### Performance Optimization
- **Fast Model**: Uses GPT-4o-mini for speed and cost efficiency
- **Caching**: Future enhancement opportunity for response caching
- **Lazy Loading**: LLM only called when feature flag enables it

## Monitoring & Debugging

### Logging
All LLM interactions are logged with clear prefixes:

```bash
[NAVI_LLM] Advice generation failed: <error>
[NAVI_LLM_SHADOW] Generated advice: <advice>
[NAVI_LLM] Enhancement failed, falling back to static: <error>
```

### Shadow Mode
Use `FEATURE_LLM_NAVI=shadow` to test LLM generation without affecting user experience:
- LLM runs in background
- Results logged for review
- Static content shown to users
- Perfect for testing and validation

### Debug Flags
```python
# Check current mode
from core.flags import get_flag_value
mode = get_flag_value("FEATURE_LLM_NAVI", "off")
print(f"Current LLM mode: {mode}")

# Test context building
from ai.navi_llm_engine import build_navi_context_from_session
context = build_navi_context_from_session()
print(f"Context: {context}")
```

## Future Enhancements

### Planned Features
1. **Response Caching**: Cache LLM responses for identical contexts
2. **A/B Testing**: Compare LLM vs static message effectiveness
3. **Personalization Learning**: Improve responses based on user interactions
4. **Multi-language Support**: Generate advice in user's preferred language
5. **Voice Integration**: Convert text advice to speech for accessibility

### Extension Points
1. **Custom Prompts**: Product-specific prompt templates
2. **External Data**: Integration with external APIs for real-time context
3. **User Feedback**: Collect ratings on LLM advice quality
4. **Analytics**: Track which advice leads to better user outcomes

## Troubleshooting

### Common Issues

#### LLM Not Working
```bash
# Check feature flag
python -c "from core.flags import get_flag_value; print(get_flag_value('FEATURE_LLM_NAVI'))"

# Check OpenAI key
python -c "from ai.llm_client import get_client; print(get_client() is not None)"
```

#### Import Errors
```bash
# Test imports
python -c "from ai.navi_llm_engine import NaviLLMEngine; print('✅ LLM engine imported')"
python -c "from core.navi_dialogue import NaviDialogue; print('✅ Enhanced dialogue imported')"
```

#### Static Fallback Always Used
- Check that `FEATURE_LLM_NAVI` is set to "assist" or "adjust"
- Verify OpenAI API key is available
- Check console logs for LLM errors

### Testing Commands

```bash
# Full test suite
python test_navi_llm.py

# Test specific mode
python test_navi_llm.py adjust

# Test static fallback
python test_navi_llm.py off

# Test shadow mode
python test_navi_llm.py shadow
```

## Migration Guide

### Existing Code
All existing Navi code continues to work without changes:

```python
# Before (still works)
from core.navi import render_navi_panel
context = render_navi_panel("hub", "concierge")

# After (enhanced, no changes needed)
# Same call now supports LLM enhancement based on feature flag
context = render_navi_panel("hub", "concierge")
```

### New Features
To take advantage of new LLM features:

```python
# Use enhanced rendering
from core.navi_dialogue import render_navi_enhanced_panel

# Get LLM-powered advice
from ai.navi_llm_engine import NaviLLMEngine
advice = NaviLLMEngine.generate_advice(context)
```

### Gradual Rollout
1. Start with `FEATURE_LLM_NAVI=shadow` to test
2. Move to `FEATURE_LLM_NAVI=assist` for gradual enhancement
3. Full enhancement with `FEATURE_LLM_NAVI=adjust`
4. Can roll back to `off` anytime if needed

## Conclusion

The Navi LLM enhancement provides a powerful foundation for dynamic, contextual user guidance while maintaining full backward compatibility. The system is designed for gradual rollout, easy testing, and graceful degradation, ensuring a robust user experience regardless of LLM availability.

The enhancement transforms Navi from a static guidance system into an intelligent, context-aware advisor that adapts to each user's unique situation and needs.