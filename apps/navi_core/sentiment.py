"""
NAVI Core Sentiment Analyzer

Basic text-based sentiment and distress detection for tone personalization.
Uses TextBlob for initial polarity analysis. Can be upgraded to transformer models.
"""

from typing import Literal

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    print("[NAVI_SENTIMENT] Warning: textblob not installed. Using fallback heuristics.")


SentimentType = Literal["distressed", "neutral", "positive"]


class SentimentAnalyzer:
    """
    Analyzes user text sentiment to inform tone selection.
    
    Sentiment categories:
    - distressed: negative sentiment, stress indicators
    - neutral: balanced or informational
    - positive: optimistic, confident
    
    Future: Upgrade to cardiffnlp/twitter-roberta-base-sentiment or similar.
    """
    
    # Keywords indicating distress/stress
    DISTRESS_KEYWORDS = {
        'worried', 'scared', 'overwhelmed', 'afraid', 'anxious', 
        'nervous', 'unsure', 'confused', 'difficult', 'hard',
        'struggling', 'lost', 'helpless', 'burden', 'stressful',
        'uncertain', 'concerned', 'frustrated', 'depressed', 'overwhelming'
    }
    
    # Keywords indicating positive sentiment
    POSITIVE_KEYWORDS = {
        'ready', 'confident', 'excited', 'hopeful', 'sure',
        'great', 'good', 'happy', 'comfortable', 'prepared', 'wonderful',
        'excellent', 'perfect', 'amazing'
    }
    
    def __init__(self):
        """Initialize sentiment analyzer."""
        self.use_textblob = TEXTBLOB_AVAILABLE
        print(f"[NAVI_SENTIMENT] Initialized (TextBlob: {self.use_textblob})")
    
    def analyze(self, text: str) -> SentimentType:
        """
        Analyze sentiment of user text.
        
        Args:
            text: User's message or question
            
        Returns:
            Sentiment category: 'distressed', 'neutral', or 'positive'
        """
        if not text or not text.strip():
            return "neutral"
        
        text_lower = text.lower()
        
        # Check for explicit distress keywords first
        if any(keyword in text_lower for keyword in self.DISTRESS_KEYWORDS):
            print(f"[NAVI_SENTIMENT] Distress keyword detected in: '{text[:50]}...'")
            return "distressed"
        
        # Check for positive keywords
        if any(keyword in text_lower for keyword in self.POSITIVE_KEYWORDS):
            print(f"[NAVI_SENTIMENT] Positive keyword detected in: '{text[:50]}...'")
            return "positive"
        
        # Use TextBlob polarity if available
        if self.use_textblob:
            try:
                polarity = TextBlob(text).sentiment.polarity
                
                if polarity < -0.2:
                    print(f"[NAVI_SENTIMENT] Negative polarity ({polarity:.2f}): distressed")
                    return "distressed"
                elif polarity > 0.2:
                    print(f"[NAVI_SENTIMENT] Positive polarity ({polarity:.2f}): positive")
                    return "positive"
                else:
                    print(f"[NAVI_SENTIMENT] Neutral polarity ({polarity:.2f}): neutral")
                    return "neutral"
            except Exception as e:
                print(f"[NAVI_SENTIMENT] TextBlob error: {e}, using fallback")
        
        # Default to neutral
        print(f"[NAVI_SENTIMENT] No strong signals: neutral")
        return "neutral"
    
    def get_emotion_score(self, text: str) -> float:
        """
        Get numerical emotion score (0.0 = very negative, 1.0 = very positive).
        
        Args:
            text: User's message
            
        Returns:
            Score between 0.0 and 1.0
        """
        if not self.use_textblob or not text:
            return 0.5  # Neutral
        
        try:
            # TextBlob polarity is -1 to 1, normalize to 0 to 1
            polarity = TextBlob(text).sentiment.polarity
            return (polarity + 1.0) / 2.0
        except Exception:
            return 0.5
