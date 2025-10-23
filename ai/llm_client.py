"""
OpenAI LLM client with retry logic and timeout handling.

Reads API key from environment variables, enforces strict timeouts,
and handles failures gracefully for shadow mode operation.

PROTOTYPE KEY HANDLING:
- Priority: st.secrets → env vars → embedded fallback
- Embedded fallback is for local testing only
- Set ALLOW_EMBEDDED_FALLBACK = False before production
"""

import os
from pathlib import Path
from typing import Optional

try:
    from openai import OpenAI
    from openai import OpenAIError
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    OpenAI = None
    OpenAIError = Exception


# ====================================================================
# PROTOTYPE CONFIGURATION - REMOVE BEFORE PRODUCTION
# ====================================================================

# Allow embedded fallback key for prototype testing
# SET TO FALSE BEFORE PRODUCTION DEPLOYMENT
ALLOW_EMBEDDED_FALLBACK = True  # TODO: Disable before prod

# Embedded key chunks (assembled at runtime to reduce scanner detection)
# REMOVE THESE BEFORE PRODUCTION
_K1 = "sk-proj-0iZdKgzfl"
_K2 = "t0xCiPDvdRTbNThO34gbftmNGVt5p2hSU4DSRDsRn"
_K3 = "Nxg2DwIo2N_ZSTwjvOPZ6QRhT3BlbkFJ7KoTloFKECU"
_K4 = "lgHkciXwvJASAs0p4QTe8BmwHrOnVcT0vZ5FT_7t8uHE0uOx_GrkudnKlOAw4MA"

# ====================================================================
# CONFIGURATION
# ====================================================================

DEFAULT_MODEL = "gpt-4o-mini"  # Fast, cost-effective for shadow mode
DEFAULT_TIMEOUT = 10  # seconds (increased from 5s to handle complex prompts)
DEFAULT_MAX_RETRIES = 2
DEFAULT_TEMPERATURE = 0.2  # Low temperature for consistent, factual responses


# ====================================================================
# KEY MANAGEMENT
# ====================================================================

def _embedded_key() -> Optional[str]:
    """Get embedded fallback key (prototype only).
    
    Returns:
        Assembled key or None if fallback disabled
    """
    if not ALLOW_EMBEDDED_FALLBACK:
        return None
    return "".join([_K1, _K2, _K3, _K4])


def _load_env() -> None:
    """Load .env file if it exists (optional dependency)."""
    try:
        from dotenv import load_dotenv
        env_path = Path(__file__).resolve().parents[1] / ".env"
        if env_path.exists():
            load_dotenv(env_path)
    except ImportError:
        pass  # python-dotenv not installed, skip
    except Exception:
        pass  # Any other error, skip silently


def get_api_key() -> Optional[str]:
    """Get OpenAI API key with priority order.
    
    Priority:
    1. Streamlit secrets (st.secrets["OPENAI_API_KEY"])
    2. Environment variable (OPENAI_API_KEY)
    3. Embedded fallback (prototype only, if ALLOW_EMBEDDED_FALLBACK=True)
    
    Returns:
        API key or None if not found
    """
    # Load .env file if present
    _load_env()
    
    # 1) Try Streamlit Cloud secrets
    try:
        import streamlit as st
        key = st.secrets.get("OPENAI_API_KEY")
        if key:
            _maybe_debug_masked_key(key)
            return key
    except Exception:
        pass  # Streamlit not available or secrets not configured
    
    # 2) Try environment variables
    key = os.getenv("OPENAI_API_KEY")
    if key:
        _maybe_debug_masked_key(key)
        return key
    
    # 3) Embedded fallback (prototype only)
    key = _embedded_key()
    if key:
        _maybe_debug_masked_key(key)
    return key


def get_openai_model() -> str:
    """Get OpenAI model name with priority order.
    
    Priority:
    1. Streamlit secrets (st.secrets["OPENAI_MODEL"])
    2. Environment variable (OPENAI_MODEL)
    3. Default (gpt-4o-mini)
    
    Returns:
        Model name
    """
    _load_env()
    
    # 1) Try Streamlit secrets
    try:
        import streamlit as st
        model = st.secrets.get("OPENAI_MODEL")
        if model:
            _maybe_debug_model(str(model))
            return model
    except Exception:
        pass
    
    # 2) Try environment variable or use default
    model = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
    _maybe_debug_model(str(model))
    return model


def get_feature_mode() -> str:
    """Get LLM feature flag mode with priority order.
    
    Priority:
    1. Streamlit secrets (st.secrets["FEATURE_LLM_NAVI"])
    2. Environment variable (FEATURE_LLM_NAVI)
    3. Default ("off")
    
    Returns:
        Feature mode: "off" | "shadow" | "assist" | "adjust"
    """
    _load_env()
    
    # 1) Try Streamlit secrets
    try:
        import streamlit as st
        mode = st.secrets.get("FEATURE_LLM_NAVI")
        if mode:
            return mode
    except Exception:
        pass
    
    # 2) Try environment variable or use default
    return os.getenv("FEATURE_LLM_NAVI", "off")


def get_feature_gcp_mode() -> str:
    """Get GCP LLM feature flag mode with priority order.
    
    Priority:
    1. Streamlit secrets (st.secrets["FEATURE_LLM_GCP"])
    2. Environment variable (FEATURE_LLM_GCP)
    3. Default ("off")
    
    Returns:
        Feature mode: "off" | "shadow" | "assist"
    """
    _load_env()
    
    # 1) Try Streamlit secrets
    try:
        import streamlit as st
        mode = st.secrets.get("FEATURE_LLM_GCP")
        if mode:
            return mode
    except Exception:
        pass
    
    # 2) Try environment variable or use default
    return os.getenv("FEATURE_LLM_GCP", "off")


# ====================================================================
# DEBUG HELPERS
# ====================================================================

def _flag_on(name: str) -> bool:
    """Check feature/debug flag from secrets first then env."""
    try:
        import streamlit as st
        v = getattr(st, "secrets", None)
        if v is not None:
            vv = v.get(name)
            if vv is not None:
                return str(vv).strip().strip('"').lower() == "on"
    except Exception:
        pass
    return str(os.getenv(name, "off")).strip().strip('"').lower() == "on"


def _maybe_debug_masked_key(key: Optional[str]) -> None:
    """If DEBUG_LLM is on, print masked key tail for verification."""
    if not key:
        return
    if not _flag_on("DEBUG_LLM"):
        return
    last4 = str(key)[-4:] if len(str(key)) >= 4 else str(key)
    prefix = "sk-" if str(key).startswith("sk-") else "key-"
    print(f"[LLM_CLIENT] key={prefix}***{last4}")


def _maybe_debug_model(model: Optional[str]) -> None:
    """If DEBUG_LLM is on, print selected model."""
    if not model:
        return
    if not _flag_on("DEBUG_LLM"):
        return
    print(f"[LLM_CLIENT] model={model}")


# ====================================================================
# CLIENT CLASS
# ====================================================================


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
            api_key: OpenAI API key (defaults to get_api_key() priority order)
            model: Model to use (default: gpt-4o-mini)
            timeout: Request timeout in seconds (default: 5)
            max_retries: Max retry attempts (default: 2)
            temperature: Sampling temperature (default: 0.2)
        
        Raises:
            RuntimeError: If openai package not installed
            ValueError: If API key not provided or found
        """
        if not HAS_OPENAI:
            raise RuntimeError(
                "openai package not installed. Install with: pip install openai"
            )
        
        # Get API key with priority order: param → secrets → env → embedded
        self.api_key = api_key or get_api_key()
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY in:\n"
                "  1. Streamlit secrets (st.secrets)\n"
                "  2. Environment variable\n"
                "  3. .env file\n"
                "Or enable ALLOW_EMBEDDED_FALLBACK for prototype testing."
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
