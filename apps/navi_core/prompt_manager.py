"""NAVI Core Prompt Management"""
from typing import Dict, Optional, Any
from pathlib import Path
import yaml

class PromptManager:
    def __init__(self, config_path: str = 'apps/navi_core/config/navi_prompt.yaml'):
        self.config_path = Path(config_path)
        self.prompts = self._load_prompts()
    
    def _load_prompts(self) -> Dict[str, Any]:
        try:
            if self.config_path.exists():
                with open(self.config_path) as f:
                    return yaml.safe_load(f) or {}
            else:
                print(f'[NAVI_PROMPT] Config not found: {self.config_path}, using defaults')
                return self._get_default_prompts()
        except Exception as e:
            print(f'[NAVI_PROMPT] Error loading config: {e}, using defaults')
            return self._get_default_prompts()
    
    def _get_default_prompts(self) -> Dict[str, Any]:
        return {
            'system': {
                'base': 'You are NAVI, a compassionate AI advisor helping families navigate senior care planning.',
                'with_context': 'You are NAVI. User: {name}, Care tier: {care_tier}, Journey: {journey_phase}'
            },
            'templates': {
                'basic_question': 'Question: {question}\n\nProvide a clear, empathetic answer:',
                'contextual_question': 'Previous conversation:\n{conversation_history}\n\nCurrent question: {question}\n\nProvide a helpful answer:',
                'personalized_question': 'User: {name}, Care needs: {care_tier}, Concerns: {concerns}\n\nQuestion: {question}\n\nProvide a personalized answer:'
            }
        }
    
    def get_system_prompt(self, include_context: bool = False, context: Optional[Dict[str, Any]] = None) -> str:
        if include_context and context:
            template = self.prompts.get('system', {}).get('with_context', '')
            return template.format(**context)
        else:
            return self.prompts.get('system', {}).get('base', '')
    
    def build_prompt(self, template_key: str, variables: Dict[str, Any]) -> str:
        templates = self.prompts.get('templates', {})
        template = templates.get(template_key, '{question}')
        try:
            return template.format(**variables)
        except KeyError as e:
            print(f'[NAVI_PROMPT] Missing variable {e} in template {template_key}')
            return template
    
    def reload(self) -> None:
        self.prompts = self._load_prompts()
        print('[NAVI_PROMPT] Reloaded prompt configuration')
