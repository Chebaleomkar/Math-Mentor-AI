"""
routes/audio_routes.py
-----------------------
Audio transcription endpoint.

POST /extract/audio
  - Accepts multipart audio file upload
  - Returns transcript + cleaned math text + needs_review flag
  - Frontend should show editable transcript before solving (same HITL pattern as images)

POST /extract/audio/base64
  - Accepts base64-encoded audio (for web recorder / mobile apps)
"""
import base64
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from core.audio_transcriber import get_transcriber, SUPPORTED_EXTENSIONS

router = APIRouter(prefix="/extract", tags=["extraction"])


# ── Response model ────────────────────────────────────────────────────────────

class TranscriptionResponse(BaseModel):
    transcript: str           # raw Whisper output
    cleaned_text: str         # after math normalisation ("squared" → "^2" etc.)
    language: str             # detected language
    duration_seconds: float
    needs_review: bool        # True → show editable field in frontend
    notes: str                # any warnings about audio quality


# ── Request model for base64 ──────────────────────────────────────────────────

class Base64AudioRequest(BaseModel):
    audio_data: str           # base64-encoded bytes
    filename: str = "audio.wav"
    language: Optional[str] = "en"


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/audio", response_model=TranscriptionResponse)
async def transcribe_upload(
    file: UploadFile = File(...),
    language: Optional[str] = "en",
):
    """
    Upload an audio file (multipart/form-data) and get a math-aware transcript.

    Supported formats: mp3, mp4, m4a, wav, webm, ogg
    Max size: 25 MB

    Example:
        curl -X POST /extract/audio -F "file=@problem.wav" -F "language=en"

    Returns:
        transcript:    raw Whisper output
        cleaned_text:  transcript with spoken math converted to notation
        needs_review:  True if transcript may be inaccurate
    """
    suffix = Path(file.filename or "audio.wav").suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported audio format '{suffix}'. "
                   f"Allowed: {sorted(SUPPORTED_EXTENSIONS)}",
        )

    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file received.")

    try:
        transcriber = get_transcriber()
        result = transcriber.transcribe(
            audio_bytes=audio_bytes,
            filename=file.filename or "audio.wav",
            language=language,
        )
    except ValueError as e:
        raise HTTPException(status_code=413, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")

    return TranscriptionResponse(
        transcript=result.transcript,
        cleaned_text=result.cleaned_text,
        language=result.language,
        duration_seconds=result.duration_seconds,
        needs_review=result.needs_review,
        notes=result.notes,
    )


@router.post("/audio/base64", response_model=TranscriptionResponse)
async def transcribe_base64(req: Base64AudioRequest):
    """
    Send audio as base64 JSON (useful for browser MediaRecorder API output).

    Example body:
        {
          "audio_data": "<base64 string>",
          "filename": "recording.webm",
          "language": "en"
        }
    """
    if not req.audio_data:
        raise HTTPException(status_code=400, detail="audio_data is required.")

    try:
        audio_bytes = base64.b64decode(req.audio_data)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 encoding.")

    try:
        transcriber = get_transcriber()
        result = transcriber.transcribe(
            audio_bytes=audio_bytes,
            filename=req.filename,
            language=req.language,
        )
    except ValueError as e:
        raise HTTPException(status_code=413, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")

    return TranscriptionResponse(
        transcript=result.transcript,
        cleaned_text=result.cleaned_text,
        language=result.language,
        duration_seconds=result.duration_seconds,
        needs_review=result.needs_review,
        notes=result.notes,
    )