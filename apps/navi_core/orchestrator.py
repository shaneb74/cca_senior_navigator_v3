"""
NAVI Core Orchestrator - Multi-tier AI routing with tone personalization.
Routes questions through FAQ -> RAG -> LLM with validation and emotional adaptation.
"""

from typing import Optional, List, Dict, Any
from apps.navi_core.models import NaviAnswer, ValidationResult, ChunkMetadata
from apps.navi_core.rag import MiniFAQRetriever, SemanticRetriever
from apps.navi_core.validator import AnswerValidator
from apps.navi_core.memory import ConversationMemory
from apps.navi_core.prompt_manager import PromptManager
from apps.navi_core.tone_adapter import ToneAdapter
from apps.navi_core.sentiment import SentimentAnalyzer


class NaviOrchestrator:
    def __init__(self, config_path: str = "apps/navi_core/config"):
        self.config_path = config_path
        self.faq = MiniFAQRetriever(f"{config_path}/mini_faq.json")
        self.semantic = SemanticRetriever()
        self.validator = AnswerValidator(strict_mode=True)
        self.prompt_manager = PromptManager(f"{config_path}/navi_prompt.yaml")
        self.tone_adapter = ToneAdapter(f"{config_path}/tones.yaml")
        self.sentiment_analyzer = SentimentAnalyzer()
        self.conversations: Dict[str, ConversationMemory] = {}
        print("[NAVI_ORCH] Orchestrator initialized with tone personalization")
    
    def answer(self, question: str, name: Optional[str] = None, tags: Optional[List[str]] = None,
               source: Optional[str] = None, conversation_id: Optional[str] = None, mode: str = "assist",
               enable_tone: bool = True) -> NaviAnswer:
        print(f"[NAVI_ORCH] Processing: '{question}'")
        
        # Analyze sentiment for tone personalization
        sentiment = self.sentiment_analyzer.analyze(question) if enable_tone else None
        
        # Get or create conversation
        if conversation_id:
            conversation = self.conversations.get(conversation_id, ConversationMemory(conversation_id))
            self.conversations[conversation_id] = conversation
        else:
            conversation = None
        
        # Tier 1: FAQ match
        faq_answer = self.faq.match(question)
        if faq_answer:
            result = NaviAnswer(question=question, answer=faq_answer, tier=1, confidence=1.0,
                              validated=ValidationResult(passed=True, confidence=1.0, reason=None), sources=[])
            
            # Apply tone personalization to FAQ answers
            if enable_tone:
                conversation_history = conversation.get_context() if conversation else None
                result = self.tone_adapter.apply(result, question, conversation_history=conversation_history)
                tone_applied = self.tone_adapter.select_tone(question, conversation_history)
            else:
                tone_applied = None
            
            if conversation:
                conversation.add_turn(question, result.answer, tier=result.tier, confidence=1.0, 
                                    tags=tags, sentiment=sentiment, tone_applied=tone_applied)
            
            print(f"[NAVI_ORCH] Tier-{result.tier} FAQ delivered with tone: {tone_applied}")
            return result
        
        # Tier 2: Semantic retrieval (placeholder)
        chunks = self.semantic.retrieve(question, top_k=5)
        
        # Tier 3: LLM generation
        answer_text = self._generate_llm_answer(question, name, conversation.get_context() if conversation else None)
        validation = self.validator.validate(question, answer_text, chunks, 0.7)
        
        result = NaviAnswer(question=question, answer=answer_text, tier=3, confidence=0.7, validated=validation,
                          sources=[ChunkMetadata(id=c.get("id",""), source=c.get("source",""), text=c.get("text",""), similarity=c.get("similarity",0.0)) for c in chunks])
        
        # Apply tone personalization to LLM answers
        if enable_tone:
            conversation_history = conversation.get_context() if conversation else None
            result = self.tone_adapter.apply(result, question, conversation_history=conversation_history)
            tone_applied = self.tone_adapter.select_tone(question, conversation_history)
        else:
            tone_applied = None
        
        if conversation:
            conversation.add_turn(question, result.answer, tier=result.tier, confidence=0.7, 
                                tags=tags, sentiment=sentiment, tone_applied=tone_applied)
        
        print(f"[NAVI_ORCH] Tier-{result.tier} delivered - validated: {validation.passed}, tone: {tone_applied}")
        return result
    
    def _generate_llm_answer(self, question: str, name: Optional[str] = None, context: Optional[List[Dict]] = None) -> str:
        try:
            from ai.llm_client import get_client
            client = get_client()
            if not client:
                return "I'm currently unable to generate a response. Please try again or contact support."
            
            # Build prompt
            if context:
                conv_hist = "\\n".join([f"Q: {t['question']}\\nA: {t['answer']}" for t in context])
                prompt = self.prompt_manager.build_prompt("contextual_question", {"question": question, "conversation_history": conv_hist})
            elif name:
                prompt = self.prompt_manager.build_prompt("personalized_question", {"question": question, "name": name, "care_tier": "unknown", "concerns": "general"})
            else:
                prompt = self.prompt_manager.build_prompt("basic_question", {"question": question})
            
            system_prompt = self.prompt_manager.get_system_prompt(include_context=bool(name),
                context={"name": name, "care_tier": "unknown", "journey_phase": "exploring"} if name else None)
            
            response = client.generate_completion(system_prompt=system_prompt, user_prompt=prompt, temperature=0.7, max_tokens=500)
            return response if response else "I'm having trouble generating a response right now."
        except Exception as e:
            print(f"[NAVI_ORCH] LLM generation failed: {e}")
            return "I apologize, but I'm having technical difficulties. Please try again in a moment."
    
    def clear_conversation(self, conversation_id: str) -> None:
        if conversation_id in self.conversations:
            self.conversations[conversation_id].clear()
            print(f"[NAVI_ORCH] Cleared conversation {conversation_id}")
