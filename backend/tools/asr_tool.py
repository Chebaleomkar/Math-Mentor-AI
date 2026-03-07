"""ASR Tool - Audio Speech Recognition using Groq Whisper API."""

import io
import os
import json
import base64
import threading
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

from langchain_core.tools import tool
from groq import Groq

from core.config import settings

# Thread pool for async API calls
executor = ThreadPoolExecutor(max_workers=2)

# Singleton Groq client
_groq_client = None
_client_lock = threading.Lock()

# Math phrase replacements for converting speech to math notation
MATH_PHRASE_MAPPINGS = {
    "square root": "√",
    "square root of": "√",
    "cube root": "∛",
    "raised to": "^",
    "to the power of": "^",
    "to the power": "^",
    "plus": "+",
    "minus": "-",
    "times": "×",
    "multiplied by": "×",
    "divided by": "÷",
    "over": "/",
    "pi": "π",
    "theta": "θ",
    "alpha": "α",
    "beta": "β",
    "gamma": "γ",
    "delta": "Δ",
    "infinity": "∞",
    "integral": "∫",
    "summation": "Σ",
    "product": "Π",
    "derivative": "d/dx",
    "equals": "=",
    "not equal": "≠",
    "greater than": ">",
    "less than": "<",
    "greater than or equal": "≥",
    "less than or equal": "≤",
    "absolute value": "|",
}

# Confidence thresholds
HIGH_CONFIDENCE = 0.85
MEDIUM_CONFIDENCE = 0.70
LOW_CONFIDENCE = 0.50

# Supported audio formats
SUPPORTED_FORMATS = {"webm", "mp3", "wav", "m4a", "ogg"}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB


def _get_groq_client() -> Groq:
    """Get singleton Groq client."""
    global _groq_client
    if _groq_client is None:
        with _client_lock:
            if _groq_client is None:
                _groq_client = Groq(api_key=settings.GROQ_API_KEY)
    return _groq_client


def _convert_math_phrases(text: str) -> str:
    """Convert spoken math phrases to mathematical notation."""
    result = text.lower()
    for phrase, symbol in MATH_PHRASE_MAPPINGS.items():
        result = result.replace(phrase, symbol)
    return result


def _validate_audio_format(filename: str) -> bool:
    """Check if audio format is supported."""
    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    return ext in SUPPORTED_FORMATS


def _estimate_confidence(audio_size: int, text_length: int) -> float:
    """Estimate transcription confidence based on audio/text characteristics."""
    # Estimate duration based on typical bitrates
    # WebM ~128kbps, MP3 ~128kbps, WAV ~1411kbps
    estimated_duration = audio_size / 16000  # bytes / avg bytes per second
    words_per_minute = (text_length / estimated_duration * 60) if estimated_duration > 0 else 0
    
    # Normal speech is ~150 words per minute
    if 80 <= words_per_minute <= 250:
        return 0.85
    elif 50 <= words_per_minute <= 350:
        return 0.75
    return 0.60


def transcribe_audio(audio_bytes: bytes, filename: str = "audio.webm", language: str = "en") -> dict:
    """
    Transcribe audio using Groq Whisper API.
    
    Args:
        audio_bytes: Raw audio data
        filename: Original filename for format detection
        language: Language code (default: "en")
    
    Returns:
        dict with keys: text, confidence, needs_confirmation, converted_text
    """
    # Validate format
    if not _validate_audio_format(filename):
        return {
            "text": "",
            "converted_text": "",
            "confidence": 0.0,
            "needs_confirmation": True,
            "error": f"Unsupported format. Supported: {SUPPORTED_FORMATS}",
            "hitl_triggered": True
        }
    
    # Validate size
    if len(audio_bytes) > MAX_FILE_SIZE:
        return {
            "text": "",
            "converted_text": "",
            "confidence": 0.0,
            "needs_confirmation": True,
            "error": f"File too large. Max size: {MAX_FILE_SIZE // (1024*1024)}MB",
            "hitl_triggered": True
        }
    
    client = _get_groq_client()
    
    # Create audio file-like object
    audio_file = io.BytesIO(audio_bytes)
    # Set appropriate filename for the API
    ext = filename.split('.')[-1].lower() if '.' in filename else 'webm'
    audio_file.name = f"audio.{ext}"
    
    try:
        # Transcribe using Groq Whisper API
        response = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-large-v3",
            language=language,
            response_format="json",
            temperature=0.0
        )
        
        raw_text = response.text.strip()
        
        # Estimate confidence
        confidence = _estimate_confidence(len(audio_bytes), len(raw_text))
        
        # Convert math phrases
        converted_text = _convert_math_phrases(raw_text)
        
        # Determine if human confirmation is needed
        needs_confirmation = confidence < MEDIUM_CONFIDENCE
        
        return {
            "text": raw_text,
            "converted_text": converted_text,
            "confidence": confidence,
            "needs_confirmation": needs_confirmation,
            "model_used": "whisper-large-v3",
            "language": language,
            "hitl_triggered": needs_confirmation
        }
        
    except Exception as e:
        return {
            "text": "",
            "converted_text": "",
            "confidence": 0.0,
            "needs_confirmation": True,
            "error": str(e),
            "hitl_triggered": True
        }


def transcribe_with_edits(audio_bytes: bytes, user_edits: Optional[dict] = None, filename: str = "audio.webm") -> dict:
    """
    Transcribe audio and apply user edits.
    
    Args:
        audio_bytes: Raw audio data
        user_edits: Dict with edit instructions (e.g., {"line_index": 1, "corrected_text": "new text"})
        filename: Original filename
    
    Returns:
        dict with final text and metadata
    """
    result = transcribe_audio(audio_bytes, filename)
    
    if user_edits and result.get("text"):
        lines = result["text"].split("\n")
        if "line_index" in user_edits and "corrected_text" in user_edits:
            idx = user_edits["line_index"]
            if 0 <= idx < len(lines):
                lines[idx] = user_edits["corrected_text"]
                result["text"] = "\n".join(lines)
                result["converted_text"] = _convert_math_phrases(result["text"])
                result["needs_confirmation"] = False
                result["user_verified"] = True
    
    return result


# LangChain tool wrappers
@tool
def transcribe_speech(audio_data: str, filename: str = "audio.webm") -> str:
    """
    Transcribe speech from audio to text for math problems.
    
    Args:
        audio_data: Base64 encoded audio or file path
        filename: Original filename for format detection
    
    Returns:
        JSON string with transcription results including confidence and HITL status
    """
    # Handle both base64 and file path
    if os.path.exists(audio_data):
        with open(audio_data, "rb") as f:
            audio_bytes = f.read()
    elif isinstance(audio_data, str) and len(audio_data) > 100:
        # Likely base64
        audio_bytes = base64.b64decode(audio_data)
    else:
        return json.dumps({"error": "Invalid audio data format"})
    
    result = transcribe_audio(audio_bytes, filename)
    return json.dumps(result, indent=2)


@tool
def convert_math_speech(text: str) -> str:
    """
    Convert spoken math phrases to mathematical notation.
    
    Args:
        text: The transcribed or input text containing math phrases
    
    Returns:
        Text with math phrases converted to symbols
    """
    converted = _convert_math_phrases(text)
    return json.dumps({"original": text, "converted": converted}, indent=2)
