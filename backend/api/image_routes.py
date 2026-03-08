"""
Image extraction endpoint.

POST /extract/image
  - Accepts multipart file upload OR base64 JSON body
  - Returns extracted math text + confidence + needs_review flag
  - If needs_review=True → frontend should show editable text before solving
"""
import io
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from core.image_extractor import get_extractor, MIME_MAP, ExtractionResult

router = APIRouter(prefix="/extract", tags=["extraction"])

ALLOWED_EXTENSIONS = set(MIME_MAP.keys())   # {.jpg, .jpeg, .png, .webp, .gif}


# ── Request/Response models ───────────────────────────────────────────────────

class Base64ImageRequest(BaseModel):
    """For clients that send base64-encoded image (e.g. React frontend)."""
    image_data: str          # base64 string, optionally with data URI prefix
    mime_type: Optional[str] = "image/jpeg"


class ExtractionResponse(BaseModel):
    extracted_text: str
    confidence: str          # "high" | "medium" | "low"
    needs_review: bool       # True → frontend should show editable field
    notes: str


# ── Helpers ───────────────────────────────────────────────────────────────────

def _result_to_response(result: ExtractionResult) -> ExtractionResponse:
    return ExtractionResponse(
        extracted_text=result.extracted_text,
        confidence=result.confidence,
        needs_review=result.needs_review,
        notes=result.notes,
    )


def _validate_extension(filename: str) -> str:
    """Returns MIME type for the file, raises HTTPException if unsupported."""
    suffix = Path(filename).suffix.lower()
    if suffix not in MIME_MAP:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported image type '{suffix}'. Allowed: {list(MIME_MAP.keys())}",
        )
    return MIME_MAP[suffix]


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/image", response_model=ExtractionResponse)
async def extract_from_upload(file: UploadFile = File(...)):
    """
    Upload an image file (multipart/form-data).
    
    Best for:  curl, Postman, Streamlit st.file_uploader
    
    Example:
        curl -X POST /extract/image -F "file=@problem.png"
    """
    mime_type = _validate_extension(file.filename or "upload.jpg")

    image_bytes = await file.read()

    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty file received.")

    try:
        extractor = get_extractor()
        result = extractor.extract(image_bytes, mime_type)
    except ValueError as e:
        # e.g. image too large
        raise HTTPException(status_code=413, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {e}")

    return _result_to_response(result)


@router.post("/image/base64", response_model=ExtractionResponse)
async def extract_from_base64(req: Base64ImageRequest):
    """
    Send image as base64 JSON body.
    
    Best for:  React / Next.js frontends, mobile apps
    
    Example body:
        {
          "image_data": "data:image/png;base64,iVBORw0KGgo...",
          "mime_type": "image/png"
        }
    """
    if not req.image_data:
        raise HTTPException(status_code=400, detail="image_data is required.")

    try:
        extractor = get_extractor()
        result = extractor.extract_from_base64(req.image_data, req.mime_type or "image/jpeg")
    except ValueError as e:
        raise HTTPException(status_code=413, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {e}")

    return _result_to_response(result)