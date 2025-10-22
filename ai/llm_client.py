"""
OpenAI LLM client with retry logic and timeout handling.

Reads API key from environment variables, enforces strict timeouts,
and handles failures gracefully for shadow mode operation.
"""

import os
from typing import Optional

try:
    from openai import OpenAI
    from openai import OpenAIError
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    OpenAI = None
    OpenAIError = Exception


# Configuration
DEFAULT_MODEL = "gpt-4o-mini"  # Fast, cost-effective for shadow mode
DEFAULT_TIMEOUT = 5  # seconds
DEFAULT_MAX_RETRIES = 2
DEFAULT_TEMPERATURE = 0.2  # Low temperature for consistent, factual responses


class LLMClient:
    """OpenAI LLM client with shadow mode optimizations.
    
    Enforces strict timeouts, retry logic, and error handling to ensure
    LLM calls never block or crash the main application flow.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        temperature: float = DEFAULT_TEMPERATURE,
    ):
        """Initialize LLM client.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model to use (default: gpt-4o-mini)
            timeout: Request timeout in seconds (default: 5)
            max_retries: Max retry attempts (default: 2)
            temperature: Sampling temperature (default: 0.2)
        
        Raises:
            RuntimeError: If openai package not installed
            ValueError: If API key not provided or found in environment
        """
        if not HAS_OPENAI:
            raise RuntimeError(
                "openai package not installed. Install with: pip install openai"
            )
        
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.temperature = temperature
        
        # Initialize OpenAI client
        self.client = OpenAI(
            api_key=self.api_key,
            timeout=self.timeout,
            max_retries=self.max_retries,
        )
    
    def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: Optional[dict] = None,
    ) -> Optional[str]:
        """Generate completion from OpenAI API.
        
        Args:
            system_prompt: System message defining assistant behavior
            user_prompt: User message with context/question
            response_format: Optional JSON schema for structured output
        
        Returns:
            Response text or None if request fails
        """
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            
            # Build request kwargs
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
            }
            
            # Add JSON mode if requested
            if response_format:
                kwargs["response_format"] = response_format
            
            # Make API call
            response = self.client.chat.completions.create(**kwargs)
            
            # Extract response text
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
            
            return None
            
        except OpenAIError as e:
            # Log error but don't crash (shadow mode must be silent)
            print(f"[LLM_ERROR] OpenAI API error: {e}")
            return None
        
        except Exception as e:
            # Catch-all for unexpected errors
            print(f"[LLM_ERROR] Unexpected error: {e}")
            return None
    
    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> Optional[str]:
        """Generate JSON-formatted completion.
        
        Uses OpenAI's JSON mode to ensure valid JSON response.
        
        Args:
            system_prompt: System message defining assistant behavior
            user_prompt: User message with context/question
        
        Returns:
            JSON string or None if request fails
        """
        return self.generate_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_format={"type": "json_object"},
        )


def get_client(
    model: str = DEFAULT_MODEL,
    timeout: int = DEFAULT_TIMEOUT,
) -> Optional[LLMClient]:
    """Get LLM client with default settings.
    
    Convenience function for creating client with standard configuration.
    Returns None if client cannot be created (missing API key, etc.).
    
    Args:
        model: Model to use (default: gpt-4o-mini)
        timeout: Request timeout in seconds (default: 5)
    
    Returns:
        LLMClient instance or None if creation fails
    """
    try:
        return LLMClient(model=model, timeout=timeout)
    except (RuntimeError, ValueError) as e:
        print(f"[LLM_WARN] Could not create LLM client: {e}")
        return None
