# Multimodal Image Input Implementation Plan

## Overview

This document outlines the implementation plan for adding image input capability to the Math Mentor application, enabling users to upload photos or screenshots of math problems for OCR-based text extraction.

---

## 1. Feature Requirements

### 1.1 Core Requirements (from Assignment)

| Requirement | Description |
|-------------|-------------|
| Accept JPG/PNG images | Support photo or screenshot uploads |
| Perform OCR | Extract text from images |
| Show extracted text | Display OCR result to user before solving |
| Allow editing | User can correct extracted text |
| Low confidence HITL | Trigger human-in-the-loop when OCR confidence is low |

### 1.2 Additional Requirements

- Support for handwritten math problems
- Support for printed/math notation (fractions, exponents, etc.)
- Preview extracted text with confidence scores
- Integration with existing Parser Agent
- Memory layer integration for storing OCR corrections

---

## 2. Technology Options Analysis

### 2.1 OCR Solutions Compared

| Solution | Pros | Cons | Recommendation |
|----------|------|------|----------------|
| **PaddleOCR** | Best accuracy for math, free, runs locally, no API costs | Requires Python dependencies | ✅ **Primary Choice** |
| **EasyOCR** | Easy to use, good accuracy | Slower on CPU, less accurate for math | Secondary option |
| **Tesseract** | Free, widely used | Poor accuracy on complex math | Not recommended |
| **Google Cloud Vision** | 1,000 free units/month, high accuracy | Requires billing account, paid after limit | Cloud backup option |
| **Google Gemini Vision** | Multi-modal understanding | Strict rate limits (5-15 RPM), not production-ready | Experimental only |

### 2.2 Recommended Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Image Input Flow                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  User Upload (JPG/PNG)                                         │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐   │
│  │ Image       │───▶│ OCR Engine   │───▶│ Confidence      │   │
│  │ Preprocessor│    │ (PaddleOCR)  │    │ Calculator      │   │
│  └─────────────┘    └──────────────┘    └─────────────────┘   │
│                                                 │               │
│                                                 ▼               │
│                                    ┌─────────────────────┐     │
│                                    │ High Confidence?    │     │
│                                    │ (≥ 80%)             │     │
│                                    └─────────────────────┘     │
│                                       │              │          │
│                                      YES             NO         │
│                                      │              │          │
│                                      ▼              ▼          │
│                            ┌────────────┐   ┌────────────┐     │
│                            │ Proceed to │   │ HITL       │     │
│                            │ Parser     │   │ Trigger    │     │
│                            └────────────┘   └────────────┘     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Implementation Plan

### Phase 1: Core OCR Engine Integration

#### 1.1 Install Dependencies

```bash
# Install PaddleOCR and dependencies
pip install paddlepaddle paddleocr

# Alternative: EasyOCR (lighter weight)
pip install easyocr
```

#### 1.2 Create OCR Tool Module

**File**: `backend/tools/ocr_tool.py`

```python
"""
OCR Tool - Extract text from images using PaddleOCR.

Supports:
- JPG/PNG image formats
- Confidence score calculation
- Math notation recognition
"""

from paddleocr import PaddleOCR
import numpy as np
from PIL import Image
import io

class OCRTool:
    def __init__(self, use_angle_cls=True, lang='en'):
        """
        Initialize PaddleOCR engine.
        
        Args:
            use_angle_cls: Use angle classification for rotated text
            lang: Language ('en', 'ch', 'japan', 'korean')
        """
        self.ocr = PaddleOCR(
            use_angle_cls=use_angle_cls, 
            lang=lang,
            show_log=False
        )
    
    def extract_text(self, image_source) -> dict:
        """
        Extract text from image.
        
        Args:
            image_source: Can be file path, PIL Image, or bytes
            
        Returns:
            dict: {
                "text": str,           # Full extracted text
                "lines": list,         # List of text lines with positions
                "confidence": float,   # Average confidence score (0-1)
                "low_confidence": bool # Whether confidence is below threshold
            }
        """
        # Convert to format PaddleOCR accepts
        if isinstance(image_source, bytes):
            image = Image.open(io.BytesIO(image_source))
            img_array = np.array(image)
        elif isinstance(image_source, str):
            img_array = image_source
        else:
            img_array = np.array(image_source)
        
        # Run OCR
        result = self.ocr.ocr(img_array, cls=True)
        
        if not result or not result[0]:
            return {
                "text": "",
                "lines": [],
                "confidence": 0.0,
                "low_confidence": True
            }
        
        # Extract text and confidence
        lines = []
        total_confidence = 0
        count = 0
        
        for line in result[0]:
            text = line[1][0]
            confidence = line[1][1]
            bbox = line[0]
            
            lines.append({
                "text": text,
                "confidence": confidence,
                "bbox": bbox
            })
            
            total_confidence += confidence
            count += 1
        
        avg_confidence = total_confidence / count if count > 0 else 0
        
        # Combine all text
        full_text = "\n".join([line["text"] for line in lines])
        
        return {
            "text": full_text,
            "lines": lines,
            "confidence": avg_confidence,
            "low_confidence": avg_confidence < 0.80  # 80% threshold
        }
    
    def extract_with_edits(self, image_source, user_edits: dict) -> dict:
        """
        Extract text and apply user edits.
        
        Args:
            image_source: Image file
            user_edits: Dict mapping line index to edited text
            
        Returns:
            dict: Text with user edits applied
        """
        base_result = self.extract_text(image_source)
        
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
            "user_edits_applied": True
        }
```

#### 1.3 Create OCR Request Model

**File**: `backend/models/schemas.py` (add new schema)

```python
from pydantic import BaseModel
from typing import List, Optional

# ... existing schemas ...

class ImageOCRRequest(BaseModel):
    """Request for image OCR processing"""
    image_data: str  # Base64 encoded image
    filename: str
    apply_preprocessing: bool = True


class OCRResult(BaseModel):
    """OCR extraction result"""
    text: str
    lines: List[dict]
    confidence: float
    low_confidence: bool
    needs_hitl: bool
    
    class Config:
        arbitrary_types_allowed = True


class OCRConfirmationRequest(BaseModel):
    """User confirmation after reviewing OCR text"""
    original_image_id: str
    corrected_text: str
    user_approved: bool
    edit_line_indices: Optional[List[int]] = None
```

---

### Phase 2: API Endpoints

#### 2.1 Add OCR Endpoints

**File**: `backend/api/routes.py`

```python
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
import base64
import uuid

from tools.ocr_tool import OCRTool
# ... existing imports ...

# Initialize OCR tool
ocr_tool = OCRTool()

# ... existing endpoints ...

@router.post("/ocr/extract")
async def extract_text_from_image(file: UploadFile = File(...)):
    """
    Extract text from uploaded image.
    
    - Accepts JPG/PNG images
    - Returns extracted text with confidence score
    - Triggers HITL if confidence < 80%
    """
    try:
        # Validate file type
        if file.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(
                status_code=400, 
                detail="Only JPG and PNG images are supported"
            )
        
        # Read image
        image_bytes = await file.read()
        
        # Extract text
        result = ocr_tool.extract_text(image_bytes)
        
        # Generate session ID for tracking
        session_id = str(uuid.uuid4())
        
        response = {
            "session_id": session_id,
            "text": result["text"],
            "lines": result["lines"],
            "confidence": result["confidence"],
            "low_confidence": result["low_confidence"],
            "needs_hitl": result["low_confidence"],
            "message": "Please review and correct the extracted text" 
                      if result["low_confidence"] 
                      else "Text extracted successfully"
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")


@router.post("/ocr/confirm")
async def confirm_ocr_text(request: OCRConfirmationRequest):
    """
    User confirms or edits OCR text.
    
    - If user_approved=True: proceed to solver
    - If user_approved=False: trigger HITL for manual review
    """
    try:
        if request.user_approved:
            # Proceed with corrected text to solver
            return {
                "status": "approved",
                "text": request.corrected_text,
                "message": "Text approved. Proceeding to solve problem."
            }
        else:
            # Trigger HITL
            return {
                "status": "needs_review",
                "text": request.corrected_text,
                "message": "Text flagged for human review."
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ocr/solve")
async def solve_from_image(file: UploadFile = File(...)):
    """
    Complete flow: OCR + Solve + Explain
    
    Convenience endpoint for full image-to-solution pipeline.
    """
    try:
        # Step 1: OCR
        image_bytes = await file.read()
        ocr_result = ocr_tool.extract_text(image_bytes)
        
        # Step 2: Check confidence - if low, return for review
        if ocr_result["low_confidence"]:
            return {
                "status": "needs_review",
                "stage": "ocr",
                "extracted_text": ocr_result["text"],
                "confidence": ocr_result["confidence"],
                "message": "OCR confidence low. Please review and correct text."
            }
        
        # Step 3: Solve the problem
        solution = coordinator.solve_problem(ocr_result["text"])
        
        return {
            "status": "success",
            "ocr_result": {
                "text": ocr_result["text"],
                "confidence": ocr_result["confidence"]
            },
            "solution": solution
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

### Phase 3: HITL Integration

#### 3.1 Modify Agent Coordinator

**File**: `backend/agents/agent_coordinator.py` (add methods)

```python
def process_image_input(self, image_data: bytes, user_id: str = None) -> dict:
    """
    Process image input through OCR and optional HITL.
    
    Args:
        image_data: Raw image bytes
        user_id: Optional user identifier for memory
        
    Returns:
        dict: Contains OCR result and next action
    """
    # Run OCR
    ocr_result = self.ocr_tool.extract_text(image_data)
    
    response = {
        "stage": "ocr",
        "extracted_text": ocr_result["text"],
        "confidence": ocr_result["confidence"],
        "lines": ocr_result["lines"],
    }
    
    # Check if HITL needed
    if ocr_result["low_confidence"]:
        response["status"] = "needs_hitl"
        response["message"] = (
            f"OCR confidence ({ocr_result['confidence']:.1%}) is below 80%. "
            "Please review and correct the extracted text."
        )
        # Store for later retrieval
        self._store_ocr_pending(image_data, response)
    else:
        response["status"] = "ready_to_solve"
    
    return response


def process_ocr_confirmation(self, session_id: str, corrected_text: str, 
                             user_approved: bool) -> dict:
    """
    Process user confirmation after OCR review.
    
    Args:
        session_id: OCR session ID
        corrected_text: User-corrected text
        user_approved: Whether user approved the text
        
    Returns:
        dict: Next step in pipeline
    """
    if not user_approved:
        # User rejected - trigger full HITL
        return {
            "status": "needs_manual_review",
            "message": "Please contact support for manual review."
        }
    
    # User approved (possibly with corrections) - proceed to solve
    # Also learn from corrections if any
    self._learn_from_ocr_corrections(session_id, corrected_text)
    
    # Solve the problem
    solution = self.solve_problem(corrected_text)
    
    return {
        "status": "success",
        "solution": solution
    }


def _learn_from_ocr_corrections(self, session_id: str, corrected_text: str):
    """
    Learn from OCR corrections to improve future recognition.
    
    Stores correction patterns in memory for pattern matching.
    """
    # This would integrate with the memory layer
    # to store common OCR error patterns
    pass
```

---

### Phase 4: Image Preprocessing (Optional Enhancement)

#### 4.1 Preprocessing Pipeline

To improve OCR accuracy for math problems:

```python
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

class ImagePreprocessor:
    """Preprocess images to improve OCR accuracy."""
    
    @staticmethod
    def preprocess(image: Image.Image) -> Image.Image:
        """
        Apply preprocessing pipeline for math images.
        
        Steps:
        1. Convert to grayscale
        2. Enhance contrast
        3. Denoise
        4. Deskew (if needed)
        """
        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        
        # Sharpen for better text clarity
        image = image.filter(ImageFilter.SHARPEN)
        
        # Optional: Deskew (straighten rotated images)
        # image = ImagePreprocessor._deskew(image)
        
        return image
    
    @staticmethod
    def detect_and_crop_roi(image: Image.Image) -> Image.Image:
        """
        Detect region of interest (text area) and crop.
        
        Uses edge detection to find text boundaries.
        """
        # Convert to numpy for processing
        img_array = np.array(image)
        
        # Find edges
        edges = ImagePreprocessor._find_edges(img_array)
        
        # Find bounding box of text region
        bbox = ImagePreprocessor._get_text_bbox(edges)
        
        # Crop to ROI
        cropped = image.crop(bbox)
        
        return cropped
```

---

### Phase 5: UI Integration (Streamlit)

#### 5.1 Image Input Component

**File**: `frontend/app.py` (Streamlit UI)

```python
import streamlit as st
import base64
from PIL import Image

def main():
    st.title("Math Mentor - Multimodal Input")
    
    # Input mode selector
    input_mode = st.radio(
        "Choose input method:",
        ["📝 Text", "🖼️ Image", "🎤 Audio"],
        horizontal=True
    )
    
    if input_mode == "🖼️ Image":
        image_input_tab()
    elif input_mode == "📝 Text":
        text_input_tab()
    # ... audio tab

def image_input_tab():
    """Handle image upload and OCR."""
    
    st.header("Upload Math Problem Image")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose an image...",
        type=['jpg', 'jpeg', 'png'],
        help="Upload a photo or screenshot of a math problem"
    )
    
    if uploaded_file is not None:
        # Display image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)
        
        # Process button
        if st.button("🔍 Extract Text", type="primary"):
            with st.spinner("Extracting text from image..."):
                # Call OCR endpoint
                files = {"file": uploaded_file}
                response = requests.post(
                    f"{API_BASE}/ocr/extract",
                    files=files
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Display extracted text
                    st.subheader("📄 Extracted Text")
                    
                    # Show confidence indicator
                    confidence = result["confidence"]
                    conf_color = "green" if confidence >= 0.8 else "orange"
                    st.markdown(
                        f"**Confidence:** :{conf_color}[{confidence:.1%}]"
                    )
                    
                    # Editable text area
                    extracted_text = st.text_area(
                        "Review and edit extracted text:",
                        value=result["text"],
                        height=200,
                        help="Correct any OCR errors before proceeding"
                    )
                    
                    # HITL warning
                    if result.get("low_confidence"):
                        st.warning(
                            "⚠️ OCR confidence is low. Please carefully "
                            "review and correct the extracted text."
                        )
                    
                    # Action buttons
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("✅ Confirm & Solve", type="primary"):
                            # Proceed to solve
                            pass
                    
                    with col2:
                        if st.button("❌ Request Review"):
                            # Trigger HITL
                            pass
                            
                else:
                    st.error(f"OCR processing failed: {response.text}")

# ... rest of UI
```

---

## 4. Confidence Threshold Strategy

### 4.1 Default Thresholds

| Confidence Level | Action |
|------------------|--------|
| ≥ 80% | Auto-proceed to solver |
| 60% - 79% | Show text for user review, allow quick approval |
| < 60% | Force HITL - require manual correction |

### 4.2 Adjustable Parameters

```python
# Configuration options
OCR_CONFIG = {
    "confidence_threshold_high": 0.80,  # Auto-proceed
    "confidence_threshold_medium": 0.60,  # Review needed
    "confidence_threshold_low": 0.40,    # Force HITL
    "max_retries": 2,                    # OCR retry attempts
    "fallback_to_cloud": True,           # Use Google Cloud as backup
}
```

---

## 5. Google Vision API Integration (Optional Backup)

### 5.1 Setup

```bash
# Install Google Cloud Vision client
pip install google-cloud-vision
```

### 5.2 Cloud OCR Implementation

```python
from google.cloud import vision
from google.cloud.vision_v1 import types

class GoogleCloudOCR:
    """Backup OCR using Google Cloud Vision API."""
    
    def __init__(self, credentials_path: str = None):
        if credentials_path:
            self.client = vision.ImageAnnotatorClient.from_service_account_json(
                credentials_path
            )
        else:
            self.client = vision.ImageAnnotatorClient()
    
    def extract_text(self, image_source) -> dict:
        """Extract text using Google Cloud Vision."""
        
        # Load image
        if isinstance(image_source, bytes):
            image = vision.Image(content=image_source)
        else:
            with open(image_source, 'rb') as f:
                image = vision.Image(content=f.read())
        
        # Perform text detection
        response = self.client.text_detection(image=image)
        texts = response.text_annotations
        
        if not texts:
            return {
                "text": "",
                "confidence": 0.0,
                "low_confidence": True
            }
        
        # Get full text and confidence
        full_text = texts[0].description
        # Note: Google Vision doesn't provide per-word confidence
        # Use symbol-level confidence as proxy
        confidence = 0.85  # Default assumption
        
        return {
            "text": full_text,
            "lines": self._parse_lines(texts),
            "confidence": confidence,
            "low_confidence": confidence < 0.80
        }
    
    def _parse_lines(self, texts) -> list:
        """Parse Google Vision response into line format."""
        lines = []
        for text in texts[1:]:  # Skip first (full text)
            lines.append({
                "text": text.description,
                "confidence": 0.85
            })
        return lines
```

---

## 6. Testing Plan

### 6.1 Unit Tests

```python
# tests/test_ocr_tool.py

import pytest
from tools.ocr_tool import OCRTool

@pytest.fixture
def ocr_tool():
    return OCRTool()

def test_extract_text_from_image(ocr_tool):
    """Test OCR on sample math problem image."""
    result = ocr_tool.extract_text("tests/fixtures/math_problem_1.png")
    
    assert result["text"] is not None
    assert isinstance(result["confidence"], float)
    assert 0 <= result["confidence"] <= 1

def test_low_confidence_detection(ocr_tool):
    """Test that low confidence triggers HITL."""
    result = ocr_tool.extract_text("tests/fixtures/blurry_image.png")
    
    assert result["low_confidence"] is True

def test_confidence_calculation(ocr_tool):
    """Test average confidence calculation."""
    result = ocr_tool.extract_text("tests/fixtures/clear_print.png")
    
    # Clear printed text should have high confidence
    assert result["confidence"] > 0.7
```

### 6.2 Integration Tests

- Test full OCR → Parser → Solver pipeline
- Test HITL trigger on low confidence
- Test memory layer integration for OCR corrections

---

## 7. File Structure

```
backend/
├── tools/
│   ├── __init__.py
│   ├── ocr_tool.py          # NEW: OCR implementation
│   ├── image_preprocessor.py # NEW: Image preprocessing
│   ├── python_tool.py
│   ├── rag_tool.py
│   └── sympy_tool.py
├── models/
│   └── schemas.py           # MODIFIED: Add OCR schemas
├── api/
│   └── routes.py            # MODIFIED: Add OCR endpoints
├── agents/
│   └── agent_coordinator.py # MODIFIED: Add image input handling
└── main.py                  # MODIFIED: Add OCR tool initialization

docs/
└── image_input_implementation_plan.md  # This document
```

---

## 8. Implementation Checklist

- [ ] **Phase 1: Core OCR Engine**
  - [ ] Install PaddleOCR dependencies
  - [ ] Create `backend/tools/ocr_tool.py`
  - [ ] Add OCRResult schema to models
  - [ ] Test basic OCR functionality

- [ ] **Phase 2: API Endpoints**
  - [ ] Add `/ocr/extract` endpoint
  - [ ] Add `/ocr/confirm` endpoint
  - [ ] Add `/ocr/solve` endpoint
  - [ ] Add file type validation

- [ ] **Phase 3: HITL Integration**
  - [ ] Modify AgentCoordinator for image input
  - [ ] Implement confidence-based HITL triggers
  - [ ] Add OCR correction learning

- [ ] **Phase 4: Image Preprocessing**
  - [ ] Create ImagePreprocessor class
  - [ ] Add contrast enhancement
  - [ ] Add noise reduction

- [ ] **Phase 5: UI Integration**
  - [ ] Add image upload component to Streamlit
  - [ ] Display extracted text for review
  - [ ] Add confidence indicator
  - [ ] Add edit capability

- [ ] **Phase 6: Testing & Refinement**
  - [ ] Unit tests for OCR tool
  - [ ] Integration tests
  - [ ] Performance optimization
  - [ ] Edge case handling

---

## 9. Estimated Timeline

| Phase | Duration | Effort |
|-------|----------|--------|
| Phase 1: Core OCR | 1-2 days | Medium |
| Phase 2: API | 1 day | Low |
| Phase 3: HITL | 1 day | Medium |
| Phase 4: Preprocessing | 1 day | Medium |
| Phase 5: UI | 1-2 days | Medium |
| Phase 6: Testing | 1 day | Low |
| **Total** | **6-8 days** | - |

---

## 10. Conclusion & Recommendation

### Primary Recommendation: **PaddleOCR**

- **Best accuracy** for math notation among open-source solutions
- **Free** with no API costs or rate limits
- **Runs locally** - no dependency on external services
- **Easy to implement** with Python

### Cloud Backup Option: **Google Cloud Vision**

- Use as fallback when local OCR fails
- 1,000 free units/month is sufficient for development/testing
- Higher accuracy on complex layouts

### Not Recommended for Production:

- **Google Gemini Vision**: Too restrictive rate limits (5-15 RPM)
- **Google ML Kit**: Only for mobile, not web
- **Tesseract**: Poor accuracy on math problems