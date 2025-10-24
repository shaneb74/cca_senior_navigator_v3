"""
Navi LLM Engine: Dynamic dialogue generation for Navi's contextual guidance.

This engine generates personalized, contextual advice for Navi based on:
- User journey state (where they are in the process)
- Care recommendations (GCP outcomes)
- Financial situation (Cost Planner data)
- User context (authenticated, location, progress)

Integrates with existing Navi system while adding LLM-powered intelligence.
"""

import json
from dataclasses import dataclass
from typing import Any, Optional

from ai.llm_client import get_client
from core.flags import get_flag_value
from pydantic import BaseModel, Field


# ====================================================================
# SCHEMAS FOR LLM STRUCTURED OUTPUT
# ====================================================================

class NaviAdvice(BaseModel):
    """Structured advice from Navi's LLM engine."""
    
    title: str = Field(description="Main headline (30-50 chars)")
    message: str = Field(description="Primary supportive message (80-120 chars)")
    guidance: str = Field(description="Specific next step guidance (60-100 chars)")
    encouragement: str = Field(description="Motivational note (40-80 chars)")
    tone: str = Field(description="Emotional tone: supportive|encouraging|celebratory|urgent")
    priority: str = Field(description="Guidance priority: high|medium|low")


class NaviContextualTips(BaseModel):
    """Contextual tips and suggestions from Navi."""
    
    tips: list[str] = Field(description="3-5 actionable tips relevant to current context")
    why_this_matters: str = Field(description="Explanation of why current step is important")
    time_estimate: Optional[str] = Field(description="How long this step typically takes")
    common_questions: list[str] = Field(description="3 common questions users have at this stage")


@dataclass
class NaviContext:
    """Complete context for Navi's LLM-powered advice generation."""
    
    # Journey state
    journey_phase: str  # getting_started, in_progress, nearly_complete, complete
    current_location: str  # hub, gcp, cost_planner, pfma
    progress_percent: int  # 0-100
    
    # User context
    user_name: Optional[str] = None
    is_authenticated: bool = False
    is_returning_user: bool = False
    
    # Care context
    care_tier: Optional[str] = None  # in_home, assisted_living, memory_care, etc.
    care_confidence: Optional[float] = None
    key_flags: list[str] = None  # High-priority flags like falls, isolation, etc.
    
    # Financial context
    estimated_cost: Optional[int] = None
    cost_concern_level: Optional[str] = None  # low, medium, high
    has_financial_profile: bool = False
    
    # Emotional context
    stress_indicators: list[str] = None  # overwhelmed, confused, urgent, etc.
    previous_interactions: int = 0
    
    # Product-specific context
    product_context: dict[str, Any] = None  # GCP answers, Cost Planner selections, etc.


# ====================================================================
# NAVI LLM ENGINE
# ====================================================================

class NaviLLMEngine:
    """LLM-powered engine for Navi's contextual dialogue generation."""
    
    @staticmethod
    def generate_advice(context: NaviContext) -> Optional[NaviAdvice]:
        """Generate contextual advice using LLM based on user's journey state.
        
        Args:
            context: Complete context about user's journey and state
            
        Returns:
            NaviAdvice object or None if LLM generation fails
        """
        # Check if LLM features are enabled
        llm_mode = get_flag_value("FEATURE_LLM_NAVI", "off")
        if llm_mode == "off":
            return None
            
        try:
            client = get_client()
            if not client:
                return None
                
            system_prompt = NaviLLMEngine._get_system_prompt()
            user_prompt = NaviLLMEngine._build_advice_prompt(context)
            
            # Generate completion using the LLMClient interface
            response_text = client.generate_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_format={"type": "json_object"}
            )
            
            if not response_text:
                return None
                
            advice_data = json.loads(response_text)
            return NaviAdvice(**advice_data)
            
        except Exception as e:
            print(f"[NAVI_LLM] Advice generation failed: {e}")
            return None
    
    @staticmethod
    def generate_contextual_tips(context: NaviContext) -> Optional[NaviContextualTips]:
        """Generate contextual tips and explanations for current journey phase.
        
        Args:
            context: User journey context
            
        Returns:
            NaviContextualTips object or None if generation fails
        """
        # Check if LLM features are enabled
        llm_mode = get_flag_value("FEATURE_LLM_NAVI", "off")
        if llm_mode == "off":
            return None
            
        try:
            client = get_client()
            if not client:
                return None
                
            system_prompt = NaviLLMEngine._get_tips_system_prompt()
            user_prompt = NaviLLMEngine._build_tips_prompt(context)
            
            # Generate completion using the LLMClient interface
            response_text = client.generate_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_format={"type": "json_object"}
            )
            
            if not response_text:
                return None
                
            tips_data = json.loads(response_text)
            return NaviContextualTips(**tips_data)
            
        except Exception as e:
            print(f"[NAVI_LLM] Tips generation failed: {e}")
            return None
    
    @staticmethod
    def _get_system_prompt() -> str:
        """System prompt for Navi's advice generation."""
        return '''You are Navi, a warm and supportive digital concierge advisor helping families navigate senior care planning.

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

Response format:
Return valid JSON with these exact fields:
{
  "title": "Encouraging headline (30-50 chars)",
  "message": "Primary supportive message (80-120 chars)", 
  "guidance": "Specific next step (60-100 chars)",
  "encouragement": "Motivational note (40-80 chars)",
  "tone": "supportive|encouraging|celebratory|urgent",
  "priority": "high|medium|low"
}

Guidelines:
- Keep language warm but professional
- Be specific about next steps
- Acknowledge the user's progress
- Address any stress indicators with empathy
- Use "you" and "your" to be personal
- Avoid medical advice or guarantees'''

    @staticmethod
    def _get_tips_system_prompt() -> str:
        """System prompt for contextual tips generation."""
        return '''You are Navi providing helpful tips and context to users navigating senior care planning.

Your role:
- Provide actionable, relevant tips for the current journey phase
- Explain why each step matters in the broader context
- Answer common questions users have at this stage
- Give realistic time estimates to set expectations

Response format:
Return valid JSON with these exact fields:
{
  "tips": ["tip1", "tip2", "tip3", "tip4", "tip5"],
  "why_this_matters": "Clear explanation of importance",
  "time_estimate": "realistic time estimate or null",
  "common_questions": ["question1", "question2", "question3"]
}

Guidelines:
- Tips should be specific and actionable
- Keep tips concise (50-80 chars each)
- Common questions should reflect real user concerns
- Time estimates should be realistic and encouraging
- Explain value without creating pressure'''

    @staticmethod
    def _build_advice_prompt(context: NaviContext) -> str:
        """Build contextual prompt for advice generation."""
        prompt_parts = [
            f"Generate supportive advice for a user in the {context.journey_phase} phase"
        ]
        
        if context.user_name:
            prompt_parts.append(f"User name: {context.user_name}")
            
        if context.current_location:
            prompt_parts.append(f"Currently in: {context.current_location}")
            
        prompt_parts.append(f"Progress: {context.progress_percent}% complete")
        
        if context.care_tier:
            prompt_parts.append(f"Care recommendation: {context.care_tier}")
            
        if context.key_flags:
            prompt_parts.append(f"Important considerations: {', '.join(context.key_flags)}")
            
        if context.estimated_cost:
            prompt_parts.append(f"Estimated monthly cost: ${context.estimated_cost:,}")
            
        if context.stress_indicators:
            prompt_parts.append(f"User may be feeling: {', '.join(context.stress_indicators)}")
            
        if context.is_returning_user:
            prompt_parts.append("This is a returning user")
            
        return "\n".join(prompt_parts)
    
    @staticmethod  
    def _build_tips_prompt(context: NaviContext) -> str:
        """Build contextual prompt for tips generation."""
        prompt_parts = [
            f"Generate helpful tips for a user in the {context.journey_phase} phase",
            f"Current location: {context.current_location}",
            f"Progress: {context.progress_percent}% complete"
        ]
        
        if context.care_tier:
            prompt_parts.append(f"Recommended care level: {context.care_tier}")
            
        if context.product_context:
            # Add specific product context
            for key, value in context.product_context.items():
                if value:
                    prompt_parts.append(f"{key}: {value}")
                    
        return "\n".join(prompt_parts)


# ====================================================================
# CONTEXT BUILDERS
# ====================================================================

def build_navi_context_from_session() -> NaviContext:
    """Build NaviContext from current Streamlit session state."""
    try:
        import streamlit as st
        from core.mcip import MCIP
        from core.state import get_user_name, is_authenticated
        
        # Get journey progress
        progress = MCIP.get_journey_progress()
        journey_phase = progress.get("phase", "getting_started")
        progress_percent = progress.get("progress_percent", 0)
        
        # Get care context
        care_rec = MCIP.get_care_recommendation()
        care_tier = care_rec.tier if care_rec else None
        care_confidence = getattr(care_rec, 'confidence', None) if care_rec else None
        
        # Get financial context
        financial = MCIP.get_financial_profile()
        has_financial_profile = financial is not None
        estimated_cost = getattr(financial, 'monthly_cost', None) if financial else None
        
        # Get user context
        user_name = get_user_name()
        is_auth = is_authenticated()
        
        # Determine current location
        current_page = st.query_params.get("page", "hub_concierge")
        if "gcp" in current_page:
            current_location = "gcp"
        elif "cost" in current_page:
            current_location = "cost_planner"
        elif "pfma" in current_page or "fa_" in current_page:
            current_location = "pfma"
        else:
            current_location = "hub"
            
        # Extract key flags
        flags = st.session_state.get("gcp", {}).get("flags", [])
        key_flags = [flag.get("id", "") for flag in flags if flag.get("priority", 99) <= 2]
        
        return NaviContext(
            journey_phase=journey_phase,
            current_location=current_location,
            progress_percent=progress_percent,
            user_name=user_name,
            is_authenticated=is_auth,
            care_tier=care_tier,
            care_confidence=care_confidence,
            key_flags=key_flags,
            estimated_cost=estimated_cost,
            has_financial_profile=has_financial_profile,
            is_returning_user=progress_percent > 0
        )
        
    except Exception as e:
        print(f"[NAVI_LLM] Context building failed: {e}")
        # Return minimal context
        return NaviContext(
            journey_phase="getting_started",
            current_location="hub",
            progress_percent=0
        )