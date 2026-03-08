"""
core/audio_transcriber.py
--------------------------
Transcribes audio files using Groq's Whisper API.
No local model download — pure API call with the groq SDK.

Supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm
Max file size: 25 MB (Groq limit)

Flow:
  raw audio bytes
      → Groq Whisper API (whisper-large-v3-turbo)
      → transcript text
      → math-specific post-processing
          ("x squared" → "x^2", "square root of x" → "sqrt(x)", etc.)
      → TranscriptionResult
"""
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from groq import Groq

from core.config import settings


MAX_AUDIO_BYTES = 25 * 1024 * 1024   # 25 MB

SUPPORTED_EXTENSIONS = {
    ".mp3", ".mp4", ".mpeg", ".mpga",
    ".m4a", ".wav", ".webm", ".ogg",
}

# Map file extensions → MIME types for the Groq API
MIME_MAP = {
    ".mp3":  "audio/mpeg",
    ".mp4":  "audio/mp4",
    ".mpeg": "audio/mpeg",
    ".mpga": "audio/mpeg",
    ".m4a":  "audio/mp4",
    ".wav":  "audio/wav",
    ".webm": "audio/webm",
    ".ogg":  "audio/ogg",
}


@dataclass
class TranscriptionResult:
    transcript: str               # raw Whisper output
    cleaned_text: str             # after math post-processing
    language: str                 # detected language (e.g. "en")
    duration_seconds: float       # audio duration
    needs_review: bool            # True if low confidence indicators found
    notes: str = ""               # any warnings or ambiguity notes


# ── Math-specific normalisation ───────────────────────────────────────────────

# Ordered list of (pattern, replacement) for spoken math → text notation
_MATH_NORMALIZATIONS = [
    # Exponents
    (r"\bsquared\b",                    "^2"),
    (r"\bcubed\b",                      "^3"),
    (r"\bto the power of (\w+)\b",      r"^\1"),
    (r"\braised to (\w+)\b",            r"^\1"),
    (r"\bto the (\w+) power\b",         r"^\1"),

    # Roots
    (r"\bsquare root of\b",             "sqrt"),
    (r"\bcube root of\b",               "cbrt"),
    (r"\bsqrt of\b",                    "sqrt"),

    # Fractions / division
    (r"\bdivided by\b",                 "/"),
    (r"\bover\b",                       "/"),

    # Greek letters common in JEE
    (r"\balpha\b",                      "α"),
    (r"\bbeta\b",                       "β"),
    (r"\bgamma\b",                      "γ"),
    (r"\bdelta\b",                      "δ"),
    (r"\btheta\b",                      "θ"),
    (r"\blambda\b",                     "λ"),
    (r"\bsigma\b",                      "σ"),
    (r"\bpi\b",                         "π"),
    (r"\binfinity\b",                   "∞"),
    (r"\binfini\b",                     "∞"),

    # Calculus
    (r"\bintegral of\b",                "∫"),
    (r"\bderivative of\b",              "d/dx"),
    (r"\bd by d x\b",                   "d/dx"),
    (r"\blimit as\b",                   "lim"),
    (r"\bapproaches\b",                 "→"),
    (r"\btends to\b",                   "→"),

    # Logic / sets
    (r"\bbelongs to\b",                 "∈"),
    (r"\bsuch that\b",                  "s.t."),
    (r"\bfor all\b",                    "∀"),
    (r"\bthere exists\b",               "∃"),

    # Trig (ensure no mangling of words like "cosine of x")
    (r"\bcosine of\b",                  "cos"),
    (r"\bsine of\b",                    "sin"),
    (r"\btangent of\b",                 "tan"),
    (r"\bsecant of\b",                  "sec"),
    (r"\bcosecant of\b",                "csc"),
    (r"\bcotangent of\b",               "cot"),

    # Miscellaneous
    (r"\bequals\b",                     "="),
    (r"\bplus or minus\b",              "±"),
    (r"\bminus or plus\b",              "∓"),
    (r"\babsolute value of\b",          "|"),
    (r"\bmod\b",                        "%"),
    (r"\bfactorial\b",                  "!"),
]

_COMPILED_PATTERNS = [
    (re.compile(pat, re.IGNORECASE), repl)
    for pat, repl in _MATH_NORMALIZATIONS
]


def _normalise_math(text: str) -> str:
    """Apply math-specific post-processing to raw transcript."""
    result = text
    for pattern, replacement in _COMPILED_PATTERNS:
        result = pattern.sub(replacement, result)
    return result.strip()


def _detect_low_confidence(transcript: str) -> tuple[bool, str]:
    """
    Heuristics to flag transcripts that likely need human review.
    Returns (needs_review, reason).
    """
    indicators = []

    # Very short (might be a failed transcription)
    if len(transcript.split()) < 4:
        indicators.append("transcript is very short")

    # Contains common Whisper uncertainty markers
    uncertainty_markers = ["[inaudible]", "[unintelligible]", "[?]", "..."]
    for marker in uncertainty_markers:
        if marker.lower() in transcript.lower():
            indicators.append(f"contains '{marker}'")

    # High ratio of numbers without context (might be garbled math)
    words = transcript.split()
    if len(words) > 3:
        digit_ratio = sum(1 for w in words if re.match(r"^\d+$", w)) / len(words)
        if digit_ratio > 0.6:
            indicators.append("unusually high number density")

    needs_review = len(indicators) > 0
    notes = "; ".join(indicators) if indicators else ""
    return needs_review, notes


# ── Main transcriber class ────────────────────────────────────────────────────

class AudioTranscriber:
    def __init__(self):
        self._client = Groq(api_key=settings.GROQ_API_KEY)

    def transcribe(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        language: Optional[str] = "en",
    ) -> TranscriptionResult:
        """
        Transcribe audio bytes using Groq Whisper.

        Args:
            audio_bytes: Raw audio file bytes
            filename:    Original filename — used to infer MIME type
            language:    ISO-639-1 language hint (None = auto-detect)

        Returns:
            TranscriptionResult with transcript and cleaned_text
        """
        if len(audio_bytes) > MAX_AUDIO_BYTES:
            raise ValueError(
                f"Audio file too large ({len(audio_bytes) // (1024*1024):.1f} MB). "
                f"Maximum: {MAX_AUDIO_BYTES // (1024*1024)} MB."
            )

        suffix = Path(filename).suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported audio format '{suffix}'. "
                f"Supported: {sorted(SUPPORTED_EXTENSIONS)}"
            )

        mime_type = MIME_MAP.get(suffix, "audio/wav")

        # Build the file tuple Groq SDK expects: (filename, bytes, mime_type)
        file_tuple = (filename, audio_bytes, mime_type)

        kwargs = dict(
            file=file_tuple,
            model=settings.GROQ_WHISPER_MODEL,
            response_format="verbose_json",   # includes duration, language
            temperature=0.0,
        )
        if language:
            kwargs["language"] = language

        response = self._client.audio.transcriptions.create(**kwargs)

        raw_transcript: str = response.text or ""
        duration: float = getattr(response, "duration", 0.0) or 0.0
        detected_language: str = getattr(response, "language", language or "en")

        cleaned = _normalise_math(raw_transcript)
        needs_review, notes = _detect_low_confidence(raw_transcript)

        return TranscriptionResult(
            transcript=raw_transcript,
            cleaned_text=cleaned,
            language=detected_language,
            duration_seconds=round(duration, 2),
            needs_review=needs_review,
            notes=notes,
        )


# ── Singleton ─────────────────────────────────────────────────────────────────
_transcriber: Optional[AudioTranscriber] = None

def get_transcriber() -> AudioTranscriber:
    global _transcriber
    if _transcriber is None:
        _transcriber = AudioTranscriber()
    return _transcriber