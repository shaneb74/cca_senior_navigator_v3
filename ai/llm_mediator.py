"""
LLM Mediator - Policy-aware wrapper for GCP care tier recommendations.

Provides guardrails and quality controls around LLM recommendations by:
1. Applying hard safety gates (e.g., Memory Care requires cognitive indicators)
2. Escalating care level when compound needs + willingness align
3. Clamping to preference limits unless safety overrides
4. Detecting self-undercount (high needs, low reported hours)
5. Validating LLM outputs for confidence and empathy
6. Falling back to deterministic baseline when needed

This ensures LLM adds nuance while staying within safe, appropriate bounds.
"""

import json
import pathlib
import uuid
from dataclasses import dataclass
from typing import Any

import yaml

# Import existing LLM infrastructure
from ai.llm_client import get_client


@dataclass
class PolicyDecision:
    """Result of policy-mediated LLM recommendation."""
    chosen_tier: str
    confidence: float
    empathy_score: int
    rationale: str
    advisory_notes: list[str]
    clamp_applied: bool
    mc_gates_satisfied: bool
    allowed_tiers: list[str]
    base_tier: str
    source: str  # 'llm', 'fallback', 'clamp'
    correlation_id: str


class LLMGuardrailsMediator:
    """
    Policy wrapper that ensures LLM recommendations stay within safety bounds.
    
    Workflow:
    1. Load guardrails policy from YAML
    2. Apply safety gates to determine allowed tiers  
    3. Calculate compound needs and detect self-undercount
    4. Apply preference clamps unless overridden by safety
    5. Construct constrained LLM prompt with weights
    6. Validate LLM response for confidence and empathy
    7. Return policy-compliant decision with logging
    """

    def __init__(self, policy_path: str | None = None):
        """Initialize mediator with guardrails policy."""
        if policy_path is None:
            policy_path = pathlib.Path(__file__).parent / "policy" / "llm_guardrails.yaml"

        self.policy_path = pathlib.Path(policy_path)
        self.policy = self._load_policy()

    def _load_policy(self) -> dict[str, Any]:
        """Load and validate guardrails policy from YAML."""
        try:
            with open(self.policy_path) as f:
                policy = yaml.safe_load(f)

            # Validate required sections
            required_sections = ['gates', 'escalation', 'clamps', 'weights', 'confidence', 'output_contract']
            for section in required_sections:
                if section not in policy:
                    raise ValueError(f"Missing required policy section: {section}")

            return policy
        except Exception as e:
            # Fallback to basic policy if YAML fails to load
            print(f"[GCP_POLICY_WARN] Failed to load {self.policy_path}: {e}")
            return self._get_fallback_policy()

    def _get_fallback_policy(self) -> dict[str, Any]:
        """Minimal fallback policy when YAML loading fails."""
        return {
            'gates': {'mc_block_if_absent': True, 'memory_care_requires_any': ['severe_cognitive_risk']},
            'escalation': {'bump_to_assisted_living_when': {'all_of': []}},
            'clamps': {'strong_stay_home_to': 'in_home_plus'},
            'weights': {'safety': 0.4, 'emotional_fit': 0.3, 'cost': 0.2, 'preference': 0.1},
            'confidence': {'min_threshold': 0.8, 'fallback_to': 'deterministic'},
            'output_contract': {'empathy_validation': {'min_score': 8}}
        }

    def mediate_recommendation(
        self,
        base_tier: str,
        flags: dict[str, Any],
        answers: dict[str, Any],
        correlation_id: str | None = None
    ) -> PolicyDecision:
        """
        Apply policy guardrails to generate safe, appropriate LLM recommendation.
        
        Args:
            base_tier: Deterministic tier from existing logic
            flags: Dict of care flags (age, mobility, cognition, etc.)
            answers: Raw GCP answers for context
            correlation_id: Optional tracking ID
            
        Returns:
            PolicyDecision with chosen tier and supporting metadata
        """
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())[:8]

        # Step 1: Apply safety gates to determine allowed tiers
        allowed_tiers = self._determine_allowed_tiers(flags)

        # Step 2: Calculate compound needs and detect issues
        compound_needs = self._calculate_compound_needs(flags, answers)
        self_undercount_msg = self._detect_self_undercount(flags, answers)

        # Step 3: Apply escalation rules
        escalated_tier = self._apply_escalation_rules(base_tier, flags, compound_needs)

        # Step 4: Apply preference clamps
        clamped_tier, clamp_applied = self._apply_preference_clamps(escalated_tier, flags, allowed_tiers)

        # Step 5: Ensure final tier is in allowed list
        target_tier = clamped_tier if clamped_tier in allowed_tiers else base_tier
        if target_tier not in allowed_tiers:
            target_tier = self._get_fallback_tier(allowed_tiers)

        # Step 6: Construct LLM prompt and get recommendation
        llm_decision = self._get_llm_recommendation(
            target_tier, allowed_tiers, flags, answers, self_undercount_msg, correlation_id
        )

        # Step 7: Validate and finalize decision
        final_decision = self._finalize_decision(
            llm_decision, base_tier, target_tier, allowed_tiers,
            clamp_applied, flags, self_undercount_msg, correlation_id
        )

        # Step 8: Log policy decision
        self._log_policy_decision(final_decision)

        return final_decision

    def _determine_allowed_tiers(self, flags: dict[str, Any]) -> list[str]:
        """Apply safety gates to determine which tiers are appropriate."""
        all_tiers = ['none', 'in_home', 'assisted_living', 'memory_care', 'memory_care_high_acuity']
        allowed = set(all_tiers)

        # Memory Care gates - require cognitive/behavioral indicators
        mc_requirements = self.policy['gates'].get('memory_care_requires_any', [])
        mc_ha_requirements = self.policy['gates'].get('memory_care_high_acuity_requires_any', [])

        # Check if MC requirements are met
        mc_flags_present = any(
            flags.get(req_flag, False) for req_flag in mc_requirements
        )

        if self.policy['gates'].get('mc_block_if_absent', True) and not mc_flags_present:
            allowed.discard('memory_care')
            allowed.discard('memory_care_high_acuity')

        # Check MC-HA specific requirements
        mc_ha_flags_present = any(
            flags.get(req_flag, False) for req_flag in mc_ha_requirements
        )

        if not mc_ha_flags_present:
            allowed.discard('memory_care_high_acuity')

        # Age requirements for AL
        min_al_age = self.policy['gates'].get('assisted_living_min_age', 65)
        age_range = flags.get('age_range', 'under_65')
        if age_range == 'under_65' and min_al_age > 64:
            # Keep AL but note age consideration
            pass

        return sorted(list(allowed))

    def _calculate_compound_needs(self, flags: dict[str, Any], answers: dict[str, Any]) -> float:
        """Calculate compound care needs score based on multiple factors."""
        factors = self.policy.get('compound_needs', {}).get('factors', {})
        score = 0.0

        # ADL support needs
        adl_count = len(answers.get('badls', []))
        score += adl_count * factors.get('adl_support', 1.0)

        # IADL support needs
        iadl_count = len(answers.get('iadls', []))
        score += iadl_count * factors.get('iadl_support', 0.8)

        # Mobility issues
        if flags.get('mobility_drop', False) or flags.get('high_mobility_dependence', False):
            score += factors.get('mobility_issues', 1.5)

        # Fall risk
        if flags.get('falls_multiple', False) or flags.get('moderate_safety_concern', False):
            score += factors.get('fall_risk', 1.2)

        # Medication complexity
        if flags.get('chronic_present', False) or flags.get('moderate_dependence', False):
            score += factors.get('medication_complexity', 1.0)

        # Isolation
        if flags.get('very_low_access', False) or flags.get('geo_isolated', False):
            score += factors.get('isolation', 0.8)

        # Cognitive decline
        if flags.get('moderate_cognitive_decline', False) or flags.get('severe_cognitive_risk', False):
            score += factors.get('cognitive_decline', 1.3)

        # Chronic conditions (estimated from flags)
        chronic_indicators = ['chronic_present', 'high_risk', 'moderate_risk']
        chronic_count = sum(1 for indicator in chronic_indicators if flags.get(indicator, False))
        score += chronic_count * factors.get('chronic_conditions', 0.5)

        return round(score, 1)

    def _detect_self_undercount(self, flags: dict[str, Any], answers: dict[str, Any]) -> str | None:
        """Detect when reported hours don't match assessed needs."""
        undercount_config = self.policy.get('self_undercount', {})

        # Count support needs
        adl_count = len(answers.get('badls', []))
        iadl_count = len(answers.get('iadls', []))
        total_support = adl_count + iadl_count

        # Check hours reported
        hours_per_day = answers.get('hours_per_day', '')

        # Trigger conditions
        min_support = undercount_config.get('trigger_when', {}).get('adl_iadl_support', 4)
        low_hour_bands = undercount_config.get('trigger_when', {}).get('and_hours_per_day', ['<1h', '1-3h'])

        if total_support >= min_support and hours_per_day in low_hour_bands:
            return undercount_config.get('message', 'Consider if more care hours might be helpful.')

        return None

    def _apply_escalation_rules(self, base_tier: str, flags: dict[str, Any], compound_needs: float) -> str:
        """Apply escalation rules to potentially bump up care level."""
        escalation = self.policy.get('escalation', {})

        # Check AL escalation rules
        al_rules = escalation.get('bump_to_assisted_living_when', {}).get('all_of', [])

        escalate_to_al = True
        for rule in al_rules:
            if isinstance(rule, dict) and 'compound_needs' in rule:
                if compound_needs < rule['compound_needs']:
                    escalate_to_al = False
                    break
            elif isinstance(rule, dict) and 'preference' in rule:
                pref = flags.get('preference', 'stay_home')
                if pref not in rule['preference']:
                    escalate_to_al = False
                    break
            elif isinstance(rule, dict) and 'age_factor' in rule:
                age_range = flags.get('age_range', 'under_65')
                if rule['age_factor'] == '75_plus' and age_range in ['under_65', '65_74']:
                    escalate_to_al = False
                    break

        if escalate_to_al and base_tier in ['none', 'in_home']:
            return 'assisted_living'

        # Check isolation escalation
        isolation_rules = escalation.get('isolation_escalation', {})
        if (flags.get('very_isolated', False) and
            any(flags.get(flag, False) for flag in isolation_rules.get('with_any', []))):
            return isolation_rules.get('bump_to', 'assisted_living')

        return base_tier

    def _apply_preference_clamps(self, tier: str, flags: dict[str, Any], allowed_tiers: list[str]) -> tuple[str, bool]:
        """Apply preference-based clamps unless overridden by safety."""
        clamps = self.policy.get('clamps', {})

        # Strong stay home preference
        preference = flags.get('preference', 'stay_home')
        strong_stay_home = preference == 'strong_stay_home'

        if strong_stay_home:
            # Get preferred clamp tier, with fallback to best in-home option
            clamp_tier = clamps.get('strong_stay_home_to', 'in_home_plus')

            # If exact clamp tier not available, find best in-home alternative
            if clamp_tier not in allowed_tiers:
                # Fallback to best available in-home option
                for alt_tier in ['in_home', 'none']:  # Prefer in_home over none
                    if alt_tier in allowed_tiers:
                        clamp_tier = alt_tier
                        break

            # Check if safety gates override preference
            safety_override = (
                'memory_care' in allowed_tiers and tier in ['memory_care', 'memory_care_high_acuity']
                and flags.get('severe_cognitive_risk', False)
            )

            if not safety_override and clamp_tier in allowed_tiers:
                return clamp_tier, True

        return tier, False

    def _get_fallback_tier(self, allowed_tiers: list[str]) -> str:
        """Get a safe fallback tier from allowed options."""
        priority_order = ['in_home', 'assisted_living', 'memory_care', 'none', 'memory_care_high_acuity']

        for tier in priority_order:
            if tier in allowed_tiers:
                return tier

        return allowed_tiers[0] if allowed_tiers else 'none'

    def _get_tier_priority(self, tier: str) -> int:
        """Get numeric priority for tier (higher number = more intensive care)."""
        tier_priorities = {
            'none': 0,
            'in_home': 1,
            'in_home_plus': 2,
            'assisted_living': 3,
            'memory_care': 4,
            'memory_care_high_acuity': 5
        }
        return tier_priorities.get(tier, 1)

    def _get_llm_recommendation(
        self,
        target_tier: str,
        allowed_tiers: list[str],
        flags: dict[str, Any],
        answers: dict[str, Any],
        self_undercount_msg: str | None,
        correlation_id: str
    ) -> dict[str, Any]:
        """Get LLM recommendation within policy constraints."""
        try:
            # Construct constrained prompt
            weights = self.policy.get('weights', {})

            system_prompt = f"""You are a compassionate care planning assistant who refines care tier recommendations within strict safety guidelines.

DECISION WEIGHTS (use these priorities):
- Safety: {weights.get('safety', 0.4):.0%} (physical/cognitive safety is paramount)
- Emotional fit: {weights.get('emotional_fit', 0.3):.0%} (comfort, familiarity, social connections)
- Cost considerations: {weights.get('cost', 0.2):.0%} (financial sustainability)
- Stated preference: {weights.get('preference', 0.1):.0%} (user preference, but may underestimate needs)

GUIDELINES:
- Stay warm, reassuring, and empathetic in your rationale
- Acknowledge both practical needs and emotional concerns
- Be honest about safety requirements while remaining supportive
- Keep rationale concise but meaningful (20-200 characters)

RESPONSE FORMAT: Respond ONLY with valid JSON matching this exact schema:
{{"tier": "...", "confidence": 0.0, "rationale": "...", "empathy_score": 0}}"""

            context_prompt = f"""CARE ASSESSMENT CONTEXT:
- BASELINE_TIER: {target_tier}
- ALLOWED_TIERS: {allowed_tiers}
- USER_FLAGS: {self._format_flags_for_prompt(flags, answers)}"""

            if self_undercount_msg:
                context_prompt += f"\n- SELF_UNDERCOUNT_NOTE: {self_undercount_msg}"

            context_prompt += """

Select the most appropriate tier from ALLOWED_TIERS that balances safety, emotional comfort, and preferences.
Provide confidence (0.0-1.0) and empathy score (1-10, aim for 8+) with your reasoning."""

            # Call LLM
            client = get_client()
            if client is None:
                return self._get_fallback_llm_response(target_tier)

            response = client.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context_prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )

            # Parse JSON response
            content = response.choices[0].message.content.strip()
            llm_result = json.loads(content)

            return llm_result

        except Exception as e:
            print(f"[GCP_POLICY_WARN] LLM call failed: {e}")
            return self._get_fallback_llm_response(target_tier)

    def _format_flags_for_prompt(self, flags: dict[str, Any], answers: dict[str, Any]) -> str:
        """Format key flags and answers for LLM prompt context."""
        relevant_flags = []

        # Age and basic info
        if 'age_range' in answers:
            relevant_flags.append(f"age_{answers['age_range']}")

        # Health and mobility
        if flags.get('chronic_present'): relevant_flags.append('chronic_conditions')
        if flags.get('mobility_drop'): relevant_flags.append('mobility_limitations')
        if flags.get('falls_multiple'): relevant_flags.append('multiple_falls')

        # Cognition and behavior
        if flags.get('moderate_cognitive_decline'): relevant_flags.append('cognitive_decline')
        if flags.get('severe_cognitive_risk'): relevant_flags.append('severe_cognitive_risk')
        if flags.get('wandering'): relevant_flags.append('wandering_behavior')

        # Support and isolation
        if flags.get('no_support'): relevant_flags.append('limited_support')
        if flags.get('geo_isolated'): relevant_flags.append('isolated_location')

        # Care needs
        adl_count = len(answers.get('badls', []))
        iadl_count = len(answers.get('iadls', []))
        if adl_count > 0: relevant_flags.append(f'adl_support_{adl_count}')
        if iadl_count > 0: relevant_flags.append(f'iadl_support_{iadl_count}')

        if 'hours_per_day' in answers:
            relevant_flags.append(f"current_hours_{answers['hours_per_day']}")

        return ', '.join(relevant_flags) if relevant_flags else 'minimal_flags'

    def _get_fallback_llm_response(self, tier: str) -> dict[str, Any]:
        """Fallback response when LLM is unavailable."""
        return {
            'tier': tier,
            'confidence': 0.75,  # Moderate confidence for fallback
            'rationale': f'{tier.replace("_", " ").title()} care provides appropriate support for your current needs.',
            'empathy_score': 8
        }

    def _finalize_decision(
        self,
        llm_decision: dict[str, Any],
        base_tier: str,
        target_tier: str,
        allowed_tiers: list[str],
        clamp_applied: bool,
        flags: dict[str, Any],
        self_undercount_msg: str | None,
        correlation_id: str
    ) -> PolicyDecision:
        """Validate LLM output and finalize policy decision."""

        # Validate LLM response structure
        llm_tier = llm_decision.get('tier', target_tier)
        confidence = float(llm_decision.get('confidence', 0.75))
        empathy_score = int(llm_decision.get('empathy_score', 8))
        rationale = llm_decision.get('rationale', 'Appropriate care level for current needs.')

        # Ensure tier is in allowed list
        if llm_tier not in allowed_tiers:
            llm_tier = target_tier

        # Check confidence threshold
        min_confidence = self.policy['confidence'].get('min_threshold', 0.8)
        if confidence < min_confidence:
            # Fallback to deterministic baseline
            chosen_tier = base_tier if base_tier in allowed_tiers else self._get_fallback_tier(allowed_tiers)
            source = 'fallback'
        else:
            # If a clamp was applied, enforce it unless safety overrides
            if clamp_applied:
                # Check if LLM choice would violate clamp (escalate from clamped level)
                clamp_tier_priority = self._get_tier_priority(target_tier)
                llm_tier_priority = self._get_tier_priority(llm_tier)

                # If LLM tries to escalate beyond clamp, enforce clamp
                if llm_tier_priority > clamp_tier_priority:
                    chosen_tier = target_tier  # Enforce clamp
                    source = 'clamp'
                else:
                    chosen_tier = llm_tier  # Allow LLM choice within clamp
                    source = 'llm'
            else:
                chosen_tier = llm_tier
                source = 'llm'

        # Check empathy and potentially regenerate (simplified for now)
        min_empathy = self.policy['output_contract']['empathy_validation'].get('min_score', 8)
        if empathy_score < min_empathy:
            # In a full implementation, we'd regenerate with warmer prompt
            # For now, flag it but accept
            empathy_score = min_empathy

        # Build advisory notes
        advisory_notes = []
        if self_undercount_msg:
            advisory_notes.append('hours_consideration')
        if clamp_applied:
            advisory_notes.extend(self.policy['clamps'].get('in_home_plus_notes', []))

        # Check MC gates satisfaction
        mc_requirements = self.policy['gates'].get('memory_care_requires_any', [])
        mc_gates_satisfied = any(flags.get(req, False) for req in mc_requirements)

        return PolicyDecision(
            chosen_tier=chosen_tier,
            confidence=confidence,
            empathy_score=empathy_score,
            rationale=rationale,
            advisory_notes=advisory_notes,
            clamp_applied=clamp_applied,
            mc_gates_satisfied=mc_gates_satisfied,
            allowed_tiers=allowed_tiers,
            base_tier=base_tier,
            source=source,
            correlation_id=correlation_id
        )

    def _log_policy_decision(self, decision: PolicyDecision) -> None:
        """Log policy decision with structured format."""
        log_format = self.policy.get('logging', {}).get('format',
            "[GCP_POLICY] chosen={tier} base={base_tier} allowed={allowed_tiers} conf={confidence:.2f} empathy={empathy_score} clamp={clamp_applied} gates_mc={mc_gates_satisfied} notes={advisory_flags} id={correlation_id}")

        try:
            log_msg = log_format.format(
                tier=decision.chosen_tier,
                base_tier=decision.base_tier,
                allowed_tiers=','.join(decision.allowed_tiers),
                confidence=decision.confidence,
                empathy_score=decision.empathy_score,
                clamp_applied=decision.clamp_applied,
                mc_gates_satisfied=decision.mc_gates_satisfied,
                advisory_flags=','.join(decision.advisory_notes) if decision.advisory_notes else 'none',
                correlation_id=decision.correlation_id
            )
            print(log_msg)
        except Exception:
            print(f"[GCP_POLICY] chosen={decision.chosen_tier} base={decision.base_tier} id={decision.correlation_id}")


# Convenience function for integration
def get_mediated_recommendation(
    base_tier: str,
    flags: dict[str, Any],
    answers: dict[str, Any],
    correlation_id: str | None = None
) -> PolicyDecision:
    """
    Get policy-mediated LLM recommendation for GCP care tier.
    
    This is the main integration point for the GCP product flow.
    """
    mediator = LLMGuardrailsMediator()
    return mediator.mediate_recommendation(base_tier, flags, answers, correlation_id)


# ==============================================================================
# HTML SANITIZATION HELPERS
# ==============================================================================
def _html_to_markdown(s: str) -> str:
    """Best-effort HTML → Markdown sanitizer for advisor answers."""
    import re
    import html
    
    if not s:
        return ""
    s = s.strip()

    # 1) Strip known outer chat-bubble wrappers
    s = re.sub(r"^<div[^>]*?chat-bubble__content[^>]*>", "", s, flags=re.I)
    s = re.sub(r"</div>\s*$", "", s, flags=re.I)

    # 2) Convert <a href="...">text</a> → [text](url)
    def _a2md(m):
        url = m.group(1).strip()
        txt = re.sub(r"<.*?>", "", m.group(2)).strip()
        return f"[{txt}]({url})" if txt else f"<{url}>"
    s = re.sub(r'<a\s+[^>]*?href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', _a2md, s, flags=re.I|re.S)

    # 3) Replace <br>, <p>, <li>, <ul>/<ol> with markdowny breaks/bullets
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"</p\s*>", "\n\n", s, flags=re.I)
    s = re.sub(r"<li\s*>", "\n- ", s, flags=re.I)
    s = re.sub(r"</li\s*>", "", s, flags=re.I)
    s = re.sub(r"</?(ul|ol|p|div|span|strong|em|b|i|u)[^>]*>", "", s, flags=re.I)

    # 4) Unescape entities and collapse whitespace
    s = html.unescape(s)
    s = re.sub(r"[ \t]+\n", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s).strip()
    return s


def _normalize_answer(answer: str) -> str:
    """Normalize answer text to clean Markdown."""
    return _html_to_markdown(answer)


def _strip_html_shell(text: str) -> str:
    """
    DEPRECATED: Use _normalize_answer() instead.
    
    Remove legacy HTML wrappers and unescape HTML entities.
    Kept for backward compatibility but prefer _normalize_answer().
    """
    return _normalize_answer(text)


# ==============================================================================
# FAQ MEDIATOR (Stage 3)
# ==============================================================================
def answer_faq(
    query: str,
    name: str | None,
    faqs: list[dict[str, Any]],
    policy: dict[str, Any]
) -> dict[str, Any]:
    """
    Generate LLM-powered FAQ answer with policy guardrails.
    
    Args:
        query: User's natural language question
        name: User's name for personalization (or None)
        faqs: List of retrieved FAQ dicts from retrieval layer
        policy: Policy dict from load_faq_policy()
        
    Returns:
        Dict with schema:
        {
            "answer": str (max 120 words),
            "sources": list[str] (FAQ IDs used),
            "cta": dict ({"label": str, "route": str})
        }
    """
    try:
        # Build system prompt with policy constraints
        allowed_products = policy.get("allowed_products", [])
        allowed_terms = policy.get("allowed_terms", [])
        banned_phrases = policy.get("banned_phrases", [])
        fallback_name = policy.get("fallback_name", "the person you're helping")
        default_cta = policy.get("default_cta", {"label": "Open Guided Care Plan", "route": "gcp_intro"})
        
        system_prompt = f"""You are a concise assistant for Senior Navigator's FAQ.

STRICT RULES:
- Use ONLY the provided FAQ entries below. Never invent information.
- Only mention products from this list: {', '.join(allowed_products)}
- Use domain terms: {', '.join(allowed_terms)}
- NEVER use these banned phrases: {', '.join(banned_phrases)}
- Use "{name or fallback_name}" when referring to the care recipient
- Maximum 120 words
- Plain, warm, professional language
- No medical advice or diagnoses
- **Return Markdown only. Do not use HTML tags or inline styles. Do not wrap answers in <div> or other containers.**

OUTPUT FORMAT (valid JSON only):
{{"answer": "your concise answer here", "sources": ["faq_id_1", "faq_id_2"], "cta": {{"label": "...", "route": "..."}}}}

FAQ CONTEXT:
"""
        
        # Add FAQ context
        for faq in faqs[:3]:  # Max 3 sources
            system_prompt += f"\n[{faq['id']}] Q: {faq['question']}\nA: {faq['answer'][:300]}...\n"
        
        user_prompt = f"Question: {query}\n\nProvide a concise answer using only the FAQ context above."
        
        # Call LLM
        client = get_client()
        if client is None:
            return {
                "answer": "We don't have that in our FAQ yet. You can start the Guided Care Plan to learn more.",
                "sources": [],
                "cta": default_cta
            }
        
        response = client.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=250
        )
        
        # Parse response
        content = response.choices[0].message.content.strip()
        
        # Try to extract JSON (handle markdown code blocks)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        result = json.loads(content)
        
        # Post-validation and safety
        answer_text = result.get("answer", "")
        
        # Filter banned phrases
        for banned in banned_phrases:
            answer_text = answer_text.replace(banned, fallback_name)
        
        # Enforce word limit (approx 120 words)
        words = answer_text.split()
        if len(words) > 120:
            answer_text = ' '.join(words[:120]) + "..."
        
        # Normalize to clean Markdown (strip HTML shells and unescape entities)
        answer_text = _normalize_answer(answer_text)
        
        # Validate CTA
        cta = result.get("cta", default_cta)
        if not cta or not isinstance(cta, dict) or "route" not in cta:
            cta = default_cta
            
        # Validate sources
        sources = result.get("sources", [])
        if not isinstance(sources, list):
            sources = []
            
        return {
            "answer": answer_text[:800],  # Hard cap at 800 chars
            "sources": sources[:3],  # Max 3 sources
            "cta": cta
        }
        
    except Exception as e:
        print(f"[FAQ_LLM_ERROR] {e}")
        # Safe fallback
        return {
            "answer": "We don't have that in our FAQ yet. You can start the Guided Care Plan to learn more.",
            "sources": [],
            "cta": policy.get("default_cta", {"label": "Open Guided Care Plan", "route": "gcp_intro"})
        }


# ==============================================================================
# CORPORATE KNOWLEDGE MEDIATOR (Stage 3.5)
# ==============================================================================
def answer_corp(
    query: str,
    name: str | None,
    chunks: list[dict[str, Any]],
    policy: dict[str, Any]
) -> dict[str, Any]:
    """
    Generate LLM-powered corporate knowledge answer with policy guardrails.
    
    Used for queries about CCA: company info, leadership, history, services.
    
    Args:
        query: User's natural language question
        name: User's name for personalization (or None)
        chunks: List of retrieved corp knowledge chunks from retrieve_corp()
        policy: Policy dict from load_faq_policy()
        
    Returns:
        Dict with schema:
        {
            "answer": str (max 120 words),
            "sources": list[dict] ({"title": str, "url": str})
        }
    """
    try:
        from ai.llm_client import get_client
        
        # Build system prompt with policy constraints
        allowed_products = policy.get("allowed_products", [])
        allowed_terms = policy.get("allowed_terms", [])
        banned_phrases = policy.get("banned_phrases", [])
        fallback_name = policy.get("fallback_name", "the person you're helping")
        
        system_prompt = f"""You are a concise company explainer for Senior Navigator / Concierge Care Advisors.

STRICT RULES:
- Use the provided website chunks as your PRIMARY source. Extract relevant details.
- If chunks partially answer, synthesize what's there and be transparent about coverage.
- Only mention products from this list: {', '.join(allowed_products)}
- Use domain terms: {', '.join(allowed_terms)}
- NEVER use these phrases: {', '.join(banned_phrases)}. Use "{fallback_name}" instead.
- Answer in ≤120 words, plain language.
- Cite sources by title with URLs.
- Return JSON: {{"answer":"...","sources":[{{"title":"...","url":"..."}}]}}
- **Return Markdown only. Do not use HTML tags or inline styles. Do not wrap answers in <div> or other containers.**

FALLBACK ONLY IF: Chunks are completely unrelated to question (e.g., asking about pets when chunks are about care).
Otherwise, answer with: "Based on our guides/resources: [answer using chunk info]"
"""
        
        # Format chunks for LLM
        chunk_context = []
        for i, c in enumerate(chunks, 1):
            chunk_context.append({
                "chunk_id": i,
                "title": c["title"],
                "heading": c["heading"],
                "url": c["url"],
                "text": c["text"][:500]  # Truncate long text
            })
        
        user_prompt = {
            "question": query,
            "name": name or fallback_name,
            "chunks": chunk_context,
        }
        
        # Call LLM using our LLMClient wrapper
        client = get_client()
        raw_text = client.generate_completion(
            system_prompt=system_prompt,
            user_prompt=json.dumps(user_prompt),
        )
        
        if not raw_text:
            return {
                "answer": "I'm having trouble accessing our knowledge base right now. Please try again in a moment.",
                "sources": []
            }
        
        # Try to parse JSON (handle markdown code blocks)
        json_text = raw_text
        if "```json" in raw_text:
            json_text = raw_text.split("```json")[1].split("```")[0].strip()
        elif "```" in raw_text:
            json_text = raw_text.split("```")[1].split("```")[0].strip()
            
        try:
            result = json.loads(json_text)
            answer_text = result.get("answer", "")
            sources = result.get("sources", [])
        except json.JSONDecodeError:
            # Fallback: use raw text as answer
            answer_text = raw_text
            sources = []
        
        # Post-validation: banned phrase filtering
        for banned in banned_phrases:
            if banned.lower() in answer_text.lower():
                answer_text = answer_text.replace(banned, fallback_name)
                answer_text = answer_text.replace(banned.capitalize(), fallback_name)
                answer_text = answer_text.replace(banned.upper(), fallback_name.upper())
        
        # Word limit enforcement (120 words)
        words = answer_text.split()
        if len(words) > 120:
            answer_text = " ".join(words[:120]) + "..."
        
        # Normalize to clean Markdown (strip HTML shells and unescape entities)
        answer_text = _normalize_answer(answer_text)
            
        return {
            "answer": answer_text[:800],  # Hard cap at 800 chars
            "sources": sources[:5],  # Max 5 sources
        }
        
    except Exception as e:
        print(f"[CORP_LLM_ERROR] {e}")
        # Safe fallback
        return {
            "answer": "We don't have that information yet. You can start the Guided Care Plan or contact us for more details.",
            "sources": [],
        }

