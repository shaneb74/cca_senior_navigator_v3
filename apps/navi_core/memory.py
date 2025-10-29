"""NAVI Core Memory Management"""
from typing import Optional, Dict, List, Any
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class ConversationTurn:
    timestamp: datetime
    question: str
    answer: str
    tier: Optional[int] = None
    confidence: float = 1.0
    tags: List[str] = field(default_factory=list)
    sentiment: Optional[str] = None  # 'distressed', 'neutral', 'positive'
    tone_applied: Optional[str] = None  # 'Empathetic', 'Guidance', 'Encouraging', etc.

class ConversationMemory:
    def __init__(self, conversation_id: Optional[str] = None):
        import uuid
        self.conversation_id = conversation_id or str(uuid.uuid4())
        self.turns: List[ConversationTurn] = []
        self.emotional_state: Dict[str, Any] = {
            "current_sentiment": "neutral",
            "tone_preference": None,
            "distress_count": 0,
            "positive_count": 0
        }
    
    def add_turn(
        self, 
        question: str, 
        answer: str, 
        tier: Optional[int] = None, 
        confidence: float = 1.0, 
        tags: Optional[List[str]] = None,
        sentiment: Optional[str] = None,
        tone_applied: Optional[str] = None
    ) -> None:
        turn = ConversationTurn(
            timestamp=datetime.now(), 
            question=question, 
            answer=answer, 
            tier=tier, 
            confidence=confidence, 
            tags=tags or [],
            sentiment=sentiment,
            tone_applied=tone_applied
        )
        self.turns.append(turn)
        
        # Update emotional state tracking
        if sentiment:
            self.emotional_state["current_sentiment"] = sentiment
            if sentiment == "distressed":
                self.emotional_state["distress_count"] += 1
            elif sentiment == "positive":
                self.emotional_state["positive_count"] += 1
        
        if tone_applied:
            self.emotional_state["tone_preference"] = tone_applied
        
        print(f'[NAVI_MEMORY] Added turn {len(self.turns)} to conversation {self.conversation_id} (sentiment: {sentiment}, tone: {tone_applied})')
    
    def get_emotional_context(self) -> Dict[str, Any]:
        """Get current emotional state and tone preferences."""
        return self.emotional_state.copy()
    
    def get_context(self, max_turns: int = 5) -> List[Dict[str, Any]]:
        recent_turns = self.turns[-max_turns:]
        return [{
            'question': turn.question, 
            'answer': turn.answer, 
            'timestamp': turn.timestamp.isoformat(), 
            'tier': turn.tier,
            'sentiment': turn.sentiment,
            'tone_applied': turn.tone_applied
        } for turn in recent_turns]
    
    def clear(self) -> None:
        self.turns = []
        print(f'[NAVI_MEMORY] Cleared conversation {self.conversation_id}')

class UserMemory:
    def __init__(self, user_id: Optional[str] = None):
        self.user_id = user_id
        self.preferences: Dict[str, Any] = {}
        self.interaction_history: List[str] = []
    
    def set_preference(self, key: str, value: Any) -> None:
        self.preferences[key] = value
        print(f'[NAVI_MEMORY] Set preference {key}={value} for user {self.user_id}')
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        return self.preferences.get(key, default)
    
    def record_interaction(self, interaction_type: str) -> None:
        self.interaction_history.append(interaction_type)
        print(f'[NAVI_MEMORY] Recorded {interaction_type} for user {self.user_id}')
