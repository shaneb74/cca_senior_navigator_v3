"""
ElevenLabs Text-to-Speech Client for FAQ Audio
Provides simple wrapper for synthesizing FAQ answers to speech.
"""

import os
import time
import hashlib
from typing import Optional
import streamlit as st

# Check if requests is available
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Import logging
from core.logging import get_logger
logger = get_logger("audio")

# Configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "sk_d1c455c20d569fd2fbbb82ca4821f3d8ef5d203d18ec3dd9")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "h8fE15wgH3MZaYwKHXyg")
AUDIO_PLAYBACK_SPEED = float(os.getenv("AUDIO_PLAYBACK_SPEED", "1.0"))
MAX_TEXT_LENGTH = 2000  # Character limit for synthesis
TIMEOUT_SECONDS = 15
MAX_RETRIES = 1

# Session cache for audio to avoid re-generating same content
if "audio_cache" not in st.session_state:
    st.session_state["audio_cache"] = {}


def _get_cache_key(text: str, voice_id: str) -> str:
    """Generate cache key from text and voice ID"""
    combined = f"{text}|{voice_id}"
    return hashlib.md5(combined.encode()).hexdigest()


def synthesize(
    text: str, 
    voice_id: Optional[str] = None, 
    format: str = "mp3_44100_128"
) -> Optional[bytes]:
    """
    Synthesize text to speech using ElevenLabs API
    
    Args:
        text: Text to synthesize (max 2000 chars)
        voice_id: ElevenLabs voice ID (defaults to configured voice)
        format: Audio format (default: mp3_44100_128)
    
    Returns:
        MP3 audio bytes or None on failure
    """
    if not REQUESTS_AVAILABLE:
        logger.warning("requests library not available for audio synthesis")
        return None
    
    if not ELEVENLABS_API_KEY or ELEVENLABS_API_KEY.startswith("your_"):
        logger.warning("ElevenLabs API key not configured")
        return None
    
    # Use configured voice if not specified
    if not voice_id:
        voice_id = ELEVENLABS_VOICE_ID
    
    # Truncate if too long
    if len(text) > MAX_TEXT_LENGTH:
        logger.warning(f"Text truncated from {len(text)} to {MAX_TEXT_LENGTH} chars")
        text = text[:MAX_TEXT_LENGTH] + "..."
    
    # Check cache first
    cache_key = _get_cache_key(text, voice_id)
    if cache_key in st.session_state["audio_cache"]:
        logger.info(f"[FAQ_AUDIO] Cache hit for {len(text)} chars")
        return st.session_state["audio_cache"][cache_key]
    
    # Prepare API request
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }
    
    # Attempt synthesis with retry
    start_time = time.time()
    
    for attempt in range(MAX_RETRIES + 1):
        try:
            logger.info(f"[FAQ_AUDIO] Synthesizing {len(text)} chars (attempt {attempt + 1}/{MAX_RETRIES + 1})")
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=TIMEOUT_SECONDS
            )
            
            if response.status_code == 200:
                audio_bytes = response.content
                duration = time.time() - start_time
                
                # Log success
                word_count = len(text.split())
                logger.info(
                    f"[FAQ_AUDIO] faq_audio_synth | "
                    f"len={word_count} words | "
                    f"voice_id={voice_id} | "
                    f"duration={duration:.2f}s"
                )
                
                # Cache result
                st.session_state["audio_cache"][cache_key] = audio_bytes
                
                return audio_bytes
            
            elif response.status_code >= 500 and attempt < MAX_RETRIES:
                # Retry on server errors
                logger.warning(f"[FAQ_AUDIO] Server error {response.status_code}, retrying...")
                time.sleep(1)
                continue
            
            else:
                # Client error or final retry failure
                logger.error(
                    f"[FAQ_AUDIO] audio_synth_fail | "
                    f"status={response.status_code} | "
                    f"error={response.text[:200]}"
                )
                return None
        
        except requests.Timeout:
            logger.error(f"[FAQ_AUDIO] audio_synth_fail | error=timeout after {TIMEOUT_SECONDS}s")
            return None
        
        except Exception as e:
            logger.error(f"[FAQ_AUDIO] audio_synth_fail | error={str(e)}")
            return None
    
    return None


def clear_audio_cache():
    """Clear the audio cache (useful for memory management)"""
    if "audio_cache" in st.session_state:
        cache_size = len(st.session_state["audio_cache"])
        st.session_state["audio_cache"].clear()
        logger.info(f"[FAQ_AUDIO] Cleared {cache_size} cached audio clips")
