"""
core/image_extractor.py
-----------------------
Extracts math problem text from an image (handwritten or printed)
using Groq's vision-capable LLM (llama-4-scout).

Why vision model over OCR:
  - Handles handwritten math symbols correctly (∫, √, fractions, ^)
  - Understands spatial layout (exponents, subscripts, fractions)
  - Returns a cleaned, unambiguous text representation
  - No extra dependencies — same Groq API key already in use

Flow:
  raw image bytes (any format)
      → base64 encode
      → Groq vision model
      → extracted + cleaned math text
      → confidence assessment
      → ExtractionResult
"""
import base64
import json
import re
from pathlib import Path
from typing import Optional

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

from core.config import settings


# ── Groq vision model ────────────────────────────────────────────────────────
# llama-4-scout-17b-16e-instruct is Groq's free vision model (as of 2025)
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

# Supported image MIME types
MIME_MAP = {
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png":  "image/png",
    ".webp": "image/webp",
    ".gif":  "image/gif",
}

MAX_IMAGE_BYTES = 4 * 1024 * 1024  # 4 MB limit (Groq constraint)


# ── Result schema ─────────────────────────────────────────────────────────────
class ExtractionResult:
    def __init__(
        self,
        extracted_text: str,
        confidence: str,          # "high" | "medium" | "low"
        needs_review: bool,
        notes: str = "",
    ):
        self.extracted_text = extracted_text
        self.confidence = confidence
        self.needs_review = needs_review
        self.notes = notes

    def to_dict(self) -> dict:
        return {
            "extracted_text": self.extracted_text,
            "confidence": self.confidence,
            "needs_review": self.needs_review,
            "notes": self.notes,
        }


# ── Core extractor ────────────────────────────────────────────────────────────
class ImageExtractor:

    _SYSTEM_PROMPT = """You are a specialized math problem extractor.

Your job: read the image and extract the math problem as clean text.

Rules:
1. Preserve ALL mathematical meaning exactly.
2. Use standard text notation:
   - Fractions:      a/b  or  (a+b)/(c+d)
   - Exponents:      x^2, x^(n+1)
   - Square root:    sqrt(x)
   - Integrals:      integral(f(x) dx, a, b)
   - Summation:      sum(f(i), i=1, n)
   - Greek letters:  write them out — alpha, beta, theta, pi, sigma
   - Absolute value: |x|
   - Infinity:       inf
3. If the image has multiple parts (a, b, c), extract all of them.
4. Do NOT solve the problem — only extract it.
5. If part of the image is illegible, mark it as [ILLEGIBLE].

After extracting, assess your confidence:
- high   = you are certain about every symbol
- medium = mostly clear, one or two ambiguous symbols
- low    = significant uncertainty or illegibility

Respond ONLY with a JSON object (no markdown fences):
{
  "extracted_text": "<the full problem in clean text notation>",
  "confidence": "high | medium | low",
  "notes": "<any ambiguities, assumptions, or illegible parts>"
}"""

    def __init__(self):
        # Separate LLM instance using vision model
        # (router.get_llm() uses the text model — we need vision here)
        self.llm = ChatGroq(
            model=VISION_MODEL,
            api_key=settings.GROQ_API_KEY,
            temperature=0.0,      # deterministic extraction
            max_tokens=1024,
        )

    def extract(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
    ) -> ExtractionResult:
        """
        Extract math text from raw image bytes.
        
        Args:
            image_bytes: Raw image bytes (JPEG, PNG, WebP, GIF)
            mime_type:   MIME type string, e.g. "image/png"
        
        Returns:
            ExtractionResult with extracted_text, confidence, needs_review
        """
        if len(image_bytes) > MAX_IMAGE_BYTES:
            raise ValueError(
                f"Image too large ({len(image_bytes) // 1024}KB). "
                f"Max allowed: {MAX_IMAGE_BYTES // 1024}KB. "
                "Please compress or resize the image."
            )

        b64 = base64.standard_b64encode(image_bytes).decode("utf-8")

        message = HumanMessage(
            content=[
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{b64}",
                    },
                },
                {
                    "type": "text",
                    "text": self._SYSTEM_PROMPT,
                },
            ]
        )

        response = self.llm.invoke([message])
        return self._parse_response(response.content)

    def extract_from_base64(
        self,
        b64_string: str,
        mime_type: str = "image/jpeg",
    ) -> ExtractionResult:
        """Convenience method when the caller already has a base64 string."""
        # Strip data URI prefix if present: "data:image/png;base64,..."
        if "," in b64_string:
            header, b64_string = b64_string.split(",", 1)
            # Extract mime type from header if not explicitly provided
            if "image/" in header and mime_type == "image/jpeg":
                match = re.search(r"image/[a-zA-Z]+", header)
                if match:
                    mime_type = match.group(0)

        image_bytes = base64.b64decode(b64_string)
        return self.extract(image_bytes, mime_type)

    # ── Private helpers ───────────────────────────────────────────────────────

    def _parse_response(self, raw: str) -> ExtractionResult:
        # Strip any accidental markdown fences Groq might add
        text = raw.strip()
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            # If JSON parsing fails, treat the whole response as extracted text
            # and mark low confidence so HITL triggers
            return ExtractionResult(
                extracted_text=raw.strip(),
                confidence="low",
                needs_review=True,
                notes="Could not parse structured response from vision model.",
            )

        confidence = data.get("confidence", "low")
        needs_review = confidence in ("low",) or "[ILLEGIBLE]" in data.get("extracted_text", "")

        return ExtractionResult(
            extracted_text=data.get("extracted_text", ""),
            confidence=confidence,
            needs_review=needs_review,
            notes=data.get("notes", ""),
        )


# ── Singleton ─────────────────────────────────────────────────────────────────
# Instantiated once and reused across requests (model loading is expensive)
_extractor: Optional[ImageExtractor] = None

def get_extractor() -> ImageExtractor:
    global _extractor
    if _extractor is None:
        _extractor = ImageExtractor()
    return _extractor