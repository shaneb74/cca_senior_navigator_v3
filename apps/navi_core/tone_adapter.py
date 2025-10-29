"""
NAVI Core Tone Adapter

Adjusts NAVI's phrasing and response structure based on user emotional state
and conversational context. Provides empathetic personalization layer.
"""

from typing import Optional
import yaml
import random
from pathlib import Path

from apps.navi_core.models import NaviAnswer
from apps.navi_core.sentiment import SentimentAnalyzer, SentimentType


ToneType = str  # "Empathetic", "Guidance", "Encouraging", "Clinical"


class ToneAdapter:
    """
    Adapts NAVI responses based on user sentiment and context.
    
    Applies tone-appropriate prefixes and suffixes to base answers,
    maintaining empathy and clarity throughout the conversation.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize tone adapter with tone configurations.
        
        Args:
            config_path: Path to tones.yaml file. If None, uses default location.
        """
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "tones.yaml"
        
        self.config_path = str(config_path)
        self.tones = self._load_tones()
        self.sentiment_analyzer = SentimentAnalyzer()
        
        print(f"[NAVI_TONE] Tone adapter initialized with {len(self.tones)} tone profiles")
    
    def _load_tones(self) -> dict:
        """Load tone configurations from YAML file."""
        try:
            with open(self.config_path) as f:
                tones = yaml.safe_load(f)
                if not tones:
                    print(f"[NAVI_TONE] Warning: Empty tones file, using defaults")
                    return self._get_default_tones()
                return tones
        except FileNotFoundError:
            print(f"[NAVI_TONE] Warning: Tones file not found at {self.config_path}, using defaults")
            return self._get_default_tones()
        except yaml.YAMLError as e:
            print(f"[NAVI_TONE] Error loading tones: {e}, using defaults")
            return self._get_default_tones()
    
    def _get_default_tones(self) -> dict:
        """Fallback tone configurations if file not available."""
        return {
            "Empathetic": {
                "prefixes": ["I understand this is important to you."],
                "suffixes": ["You're doing great by seeking support."]
            },
            "Guidance": {
                "prefixes": ["Here's what usually helps:"],
                "suffixes": ["Would you like more details?"]
            },
            "Encouraging": {
                "prefixes": ["That's a great question."],
                "suffixes": ["You're making good progress."]
            }
        }
    
    def select_tone(self, user_text: str, conversation_history: Optional[list] = None) -> ToneType:
        """
        Select appropriate tone based on user sentiment and context.
        
        Args:
            user_text: Current user message
            conversation_history: Optional list of previous conversation turns
            
        Returns:
            Tone identifier (e.g., "Empathetic", "Guidance")
        """
        sentiment = self.sentiment_analyzer.analyze(user_text)
        
        # Sentiment-to-tone mapping
        tone_map = {
            "distressed": "Empathetic",
            "neutral": "Guidance",
            "positive": "Encouraging"
        }
        
        selected_tone = tone_map.get(sentiment, "Guidance")
        print(f"[NAVI_TONE] Selected tone: {selected_tone} (sentiment: {sentiment})")
        
        return selected_tone
    
    def apply(
        self, 
        base_answer: NaviAnswer, 
        user_text: str,
        force_tone: Optional[ToneType] = None,
        conversation_history: Optional[list] = None
    ) -> NaviAnswer:
        """
        Apply tone personalization to a base answer.
        
        Args:
            base_answer: Original NaviAnswer from orchestrator
            user_text: User's original question/message
            force_tone: Optional specific tone to apply (overrides sentiment)
            conversation_history: Optional conversation context
            
        Returns:
            NaviAnswer with personalized tone applied
        """
        # Select tone based on sentiment or use forced tone
        tone = force_tone if force_tone else self.select_tone(user_text, conversation_history)
        
        # Get tone configuration
        if tone not in self.tones:
            print(f"[NAVI_TONE] Warning: Unknown tone '{tone}', using Guidance")
            tone = "Guidance"
        
        tone_config = self.tones[tone]
        
        # Randomly select prefix and suffix for natural variation
        prefix = random.choice(tone_config.get("prefixes", [""]))
        suffix = random.choice(tone_config.get("suffixes", [""]))
        
        # Apply tone wrapping to answer
        original_answer = base_answer.answer.strip()
        
        # Build personalized answer
        parts = []
        if prefix:
            parts.append(prefix)
        parts.append(original_answer)
        if suffix:
            parts.append(suffix)
        
        personalized_answer = " ".join(parts)
        
        # Update answer with tone personalization
        base_answer.answer = personalized_answer
        
        # Mark as Tier 2 personalized
        if base_answer.tier == 1:  # FAQ answers stay Tier 1
            pass  # Keep original tier
        else:
            base_answer.tier = 2  # Mark as personalized
        
        print(f"[NAVI_TONE] Applied {tone} tone (prefix: {len(prefix)} chars, suffix: {len(suffix)} chars)")
        
        return base_answer
    
    def reload(self):
        """Reload tone configurations from file (hot-reload support)."""
        print(f"[NAVI_TONE] Reloading tones from {self.config_path}")
        self.tones = self._load_tones()
    
    def get_available_tones(self) -> list[str]:
        """Get list of available tone profiles."""
        return list(self.tones.keys())
    
    def describe_tone(self, tone: ToneType) -> Optional[str]:
        """Get description of a specific tone profile."""
        if tone in self.tones:
            return self.tones[tone].get("description", "No description available")
        return None
