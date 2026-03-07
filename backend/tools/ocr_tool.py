"""
OCR Tool - Extract text from images using PaddleOCR.

Supports:
- JPG/PNG image formats
- Confidence score calculation
- Math notation recognition
- HITL integration for low confidence results

Usage:
    from tools.ocr_tool import OCRTool, extract_text
    
    # Initialize tool (loads model on first use)
    tool = OCRTool()
    
    # Extract text from image
    result = tool.extract_text("path/to/image.png")
    print(result["text"])  # Extracted text
    print(result["confidence"])  # 0.0 to 1.0
    
    # Check if HITL is needed
    if result["low_confidence"]:
        print("Please review extracted text")
"""

import io
import os
import uuid
import base64
import threading
from typing import Union, List, Dict, Any, Optional

import numpy as np
from PIL import Image




class OCRTool:
    """
    OCR Tool for extracting text from math problem images.
    
    Uses PaddleOCR for text extraction with confidence scoring.
    Designed for integration with HITL when confidence is low.
    """
    
    # Confidence thresholds
    HIGH_CONFIDENCE = 0.80  # Auto-proceed
    MEDIUM_CONFIDENCE = 0.60  # Review needed
    LOW_CONFIDENCE = 0.40  # Force HITL
    
    def __init__(
        self,
        high_threshold: float = 0.80,
        medium_threshold: float = 0.60,
        low_threshold: float = 0.40,
        use_angle_cls: bool = True,
        lang: str = 'en'
    ):
        """
        Initialize OCR tool.
        
        Args:
            high_threshold: Threshold for auto-proceeding (default 0.80)
            medium_threshold: Threshold for requiring review (default 0.60)
            low_threshold: Threshold for forcing HITL (default 0.40)
            use_angle_cls: Use angle classification for rotated text
            lang: Language for OCR ('en', 'ch', 'japan', 'korean')
        """
        self.high_threshold = high_threshold
        self.medium_threshold = medium_threshold
        self.low_threshold = low_threshold
        self.use_angle_cls = use_angle_cls
        self.lang = lang
        self._ocr = None
        self._ocr_lock = threading.Lock()
    
    @property
    def ocr(self):
        """Thread-safe lazy load of PaddleOCR instance."""
        if self._ocr is None:
            with self._ocr_lock:
                if self._ocr is None:
                    # Monkey patch for PaddleOCR compatibility with latest Langchain
                    import sys
                    if 'langchain.docstore.document' not in sys.modules:
                        import types
                        import langchain_core.documents
                        mock_docstore = types.ModuleType('langchain.docstore')
                        sys.modules['langchain.docstore'] = mock_docstore
                        mock_docstore_document = types.ModuleType('langchain.docstore.document')
                        mock_docstore_document.Document = langchain_core.documents.Document
                        sys.modules['langchain.docstore.document'] = mock_docstore_document
                    if 'langchain.text_splitter' not in sys.modules:
                        import types
                        try:
                            import langchain_text_splitters
                            sys.modules['langchain.text_splitter'] = langchain_text_splitters
                        except ImportError:
                            pass
                    
                    from paddleocr import PaddleOCR
                    self._ocr = PaddleOCR(
                        use_angle_cls=self.use_angle_cls,
                        lang=self.lang,
                        show_log=False,
                        det_db_thresh=0.3,
                        det_db_box_thresh=0.5,
                    )
        return self._ocr
    
    def extract_text(
        self,
        image_source: Union[str, bytes, np.ndarray, Image.Image]
    ) -> Dict[str, Any]:
        """
        Extract text from an image.
        
        Args:
            image_source: Can be file path (str), image bytes, numpy array, or PIL Image
            
        Returns:
            dict: {
                "text": str,           # Full extracted text
                "lines": List[dict],   # List of text lines with positions
                "confidence": float,   # Average confidence score (0-1)
                "low_confidence": bool # Whether confidence is below high threshold
                "needs_hitl": bool     # Whether HITL is recommended
                "session_id": str      # Unique session identifier
            }
        """
        # Convert to numpy array for PaddleOCR
        img_array = self._load_image(image_source)
        
        if img_array is None:
            return {
                "text": "",
                "lines": [],
                "confidence": 0.0,
                "low_confidence": True,
                "needs_hitl": True,
                "error": "Failed to load image",
                "session_id": str(uuid.uuid4())
            }
        
        try:
            # Run OCR
            result = self.ocr.ocr(img_array, cls=True)
            
            # Parse results
            if not result or not result[0]:
                return {
                    "text": "",
                    "lines": [],
                    "confidence": 0.0,
                    "low_confidence": True,
                    "needs_hitl": True,
                    "session_id": str(uuid.uuid4())
                }
            
            lines = []
            total_confidence = 0.0
            count = 0
            
            for line in result[0]:
                bbox = line[0]  # Bounding box coordinates
                text = line[1][0]  # Extracted text
                confidence = float(line[1][1])  # Confidence score
                
                lines.append({
                    "text": text,
                    "confidence": confidence,
                    "bbox": bbox
                })
                
                total_confidence += confidence
                count += 1
            
            avg_confidence = total_confidence / count if count > 0 else 0.0
            
            # Determine if HITL is needed
            needs_hitl = avg_confidence < self.high_threshold
            
            return {
                "text": "\n".join([line["text"] for line in lines]),
                "lines": lines,
                "confidence": avg_confidence,
                "low_confidence": avg_confidence < self.high_threshold,
                "needs_hitl": needs_hitl,
                "hitl_reason": self._get_hitl_reason(avg_confidence),
                "session_id": str(uuid.uuid4())
            }
            
        except Exception as e:
            return {
                "text": "",
                "lines": [],
                "confidence": 0.0,
                "low_confidence": True,
                "needs_hitl": True,
                "error": str(e),
                "session_id": str(uuid.uuid4())
            }
    
    def extract_with_edits(
        self,
        image_source: Union[str, bytes, np.ndarray, Image.Image],
        user_edits: Dict[int, str]
    ) -> Dict[str, Any]:
        """
        Extract text and apply user edits to specific lines.
        
        Args:
            image_source: Image file
            user_edits: Dict mapping line index to edited text
            
        Returns:
            dict: Text with user edits applied
        """
        base_result = self.extract_text(image_source)
        
        if "error" in base_result:
            return base_result
        
        # Apply edits
        lines = base_result["lines"]
        for idx, new_text in user_edits.items():
            if 0 <= idx < len(lines):
                lines[idx]["text"] = new_text
                lines[idx]["user_edited"] = True
        
        full_text = "\n".join([line["text"] for line in lines])
        
        return {
            "text": full_text,
            "lines": lines,
            "confidence": base_result["confidence"],
            "low_confidence": base_result["low_confidence"],
            "needs_hitl": False,  # User approved, so no HITL
            "user_edits_applied": True,
            "session_id": base_result["session_id"]
        }
    
    def _load_image(self, image_source) -> Optional[np.ndarray]:
        """Load image from various sources and convert to numpy array.
        
        Args:
            image_source: Can be file path (str), image bytes, numpy array, or PIL Image
            
        Returns:
            numpy.ndarray or None: Image as numpy array, or None if loading failed
        """
        try:
            if isinstance(image_source, str):
                # File path
                if not os.path.exists(image_source):
                    return None
                image = Image.open(image_source)
                return np.array(image)
            
            elif isinstance(image_source, bytes):
                # Image bytes
                image = Image.open(io.BytesIO(image_source))
                return np.array(image)
            
            elif isinstance(image_source, Image.Image):
                # PIL Image
                return np.array(image_source)
            
            elif isinstance(image_source, np.ndarray):
                # Already a numpy array
                return image_source
            
            return None
            
        except Exception:
            return None
    
    def _get_hitl_reason(self, confidence: float) -> str:
        """Generate human-readable HITL reason based on confidence."""
        if confidence >= self.high_threshold:
            return ""
        elif confidence >= self.medium_threshold:
            return f"Medium confidence ({confidence:.1%}). Please review extracted text."
        elif confidence >= self.low_threshold:
            return f"Low confidence ({confidence:.1%}). Text correction required."
        else:
            return f"Very low confidence ({confidence:.1%}). Manual input recommended."


# LangChain tool wrapper for agent integration
from langchain_core.tools import tool


# Singleton instance for LangChain tools
_langchain_ocr_tool = None
_langchain_ocr_lock = threading.Lock()


def _get_langchain_ocr_tool() -> OCRTool:
    """Get singleton OCR tool for LangChain integration."""
    global _langchain_ocr_tool
    if _langchain_ocr_tool is None:
        with _langchain_ocr_lock:
            if _langchain_ocr_tool is None:
                _langchain_ocr_tool = OCRTool()
    return _langchain_ocr_tool


@tool
def extract_text(image_path: str) -> str:
    """
    Extract text from a math problem image using OCR.
    
    This tool performs Optical Character Recognition (OCR) on images
    containing math problems. It supports JPG/PNG formats and returns
    both the extracted text and a confidence score.
    
    Args:
        image_path: Path to the image file (JPG or PNG)
    
    Returns:
        JSON string containing:
        - text: The extracted text from the image
        - confidence: Confidence score (0.0 to 1.0)
        - needs_hitl: Whether human review is recommended
        - lines: Individual text lines with their positions
    """
    ocr_tool = _get_langchain_ocr_tool()
    result = ocr_tool.extract_text(image_path)
    
    # Return as formatted string for LangChain
    return (
        f"Extracted Text:\n{result['text']}\n\n"
        f"Confidence: {result['confidence']:.1%}\n"
        f"Needs Review: {'Yes' if result['needs_hitl'] else 'No'}\n"
        f"Lines: {len(result.get('lines', []))}"
    )


@tool
def extract_text_from_bytes(image_bytes: str, filename: str = "image.png") -> str:
    """
    Extract text from image bytes (base64 or raw).
    
    Args:
        image_bytes: Base64-encoded image string or raw bytes
        filename: Original filename (for format detection)
    
    Returns:
        JSON string with extracted text and confidence
    """
    ocr_tool = _get_langchain_ocr_tool()
    
    # Try to decode base64 if needed
    try:
        # Check if it looks like base64 (alphanumeric with +/=)
        if isinstance(image_bytes, str) and len(image_bytes) > 200:
            try:
                # Try to decode as base64
                decoded = base64.b64decode(image_bytes)
                image_data = decoded
            except Exception:
                # Not valid base64, treat as raw string
                image_data = image_bytes.encode('utf-8') if isinstance(image_bytes, str) else image_bytes
        elif isinstance(image_bytes, bytes):
            image_data = image_bytes
        else:
            image_data = str(image_bytes).encode('utf-8')
    except Exception:
        image_data = image_bytes if isinstance(image_bytes, bytes) else image_bytes.encode('utf-8')
    
    result = ocr_tool.extract_text(image_data)
    
    return (
        f"Extracted Text:\n{result['text']}\n\n"
        f"Confidence: {result['confidence']:.1%}\n"
        f"Needs Review: {'Yes' if result['needs_hitl'] else 'No'}"
    )


# Default instance for simple usage (thread-safe)
_default_ocr_tool = None
_default_ocr_lock = threading.Lock()


def get_ocr_tool() -> OCRTool:
    """Get default OCR tool instance (thread-safe singleton)."""
    global _default_ocr_tool
    if _default_ocr_tool is None:
        with _default_ocr_lock:
            if _default_ocr_tool is None:
                _default_ocr_tool = OCRTool()
    return _default_ocr_tool