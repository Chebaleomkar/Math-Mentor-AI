"""API Routes for Math Mentor - Including Memory & Self-Learning."""

from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import uuid
import base64
import asyncio

from agents import (
    ParserAgent,
    IntentRouterAgent,
    SolverAgent,
    VerifierAgent,
    ExplainerAgent,
    AgentCoordinator
)

from tools.ocr_tool import OCRTool
from tools.asr_tool import transcribe_audio, transcribe_with_edits

router = APIRouter()

# Initialize agents
parser_agent = ParserAgent()
router_agent = IntentRouterAgent()
solver_agent = SolverAgent()
verifier_agent = VerifierAgent()
explainer_agent = ExplainerAgent()
coordinator = AgentCoordinator()

# Initialize OCR tool
ocr_tool = OCRTool()


class QuestionRequest(BaseModel):
    question: str
    use_full_pipeline: bool = True


class VerificationRequest(BaseModel):
    question: str
    solution: str


class MemorySearchRequest(BaseModel):
    query: str
    topic: Optional[str] = None
    n_results: int = 5


class FeedbackRequest(BaseModel):
    memory_id: str
    correct_answer: str
    user_comment: str
    feedback_type: str = "correction"


class MemoryAddRequest(BaseModel):
    original_input: str
    parsed_question: dict
    final_answer: str
    topic: str
    complexity: str = "medium"


class OCRConfirmationRequest(BaseModel):
    """Request for OCR text confirmation after user review."""
    session_id: str
    corrected_text: str
    user_approved: bool
    edit_line_indices: Optional[List[int]] = None


class OCRSolveRequest(BaseModel):
    """Request for OCR + Solve endpoint."""
    image_data: str  # Base64 encoded
    filename: str = "image.png"


class ASRBase64Request(BaseModel):
    """Request for ASR transcription from base64."""
    audio_data: str
    filename: str = "audio.webm"
    language: str = "en"


class ASREditRequest(BaseModel):
    """Request to transcribe with user edits."""
    audio_data: str
    user_edits: dict
    filename: str = "audio.webm"


@router.post("/parse")
def parse_question(request: QuestionRequest):
    """Parse a math question into structured format."""
    result = parser_agent.run(request.question)
    return result


@router.post("/route")
def route_question(request: QuestionRequest):
    """Route the problem to determine solution strategy."""
    parsed = parser_agent.run(request.question)
    routing = router_agent.get_routing(parsed)
    return routing


@router.post("/solve", response_model=SolveResponse)
async def solve(req: SolveRequest):
    if req.input_type == "text":
        raw_input = req.content
    elif req.input_type == "image":
        from core.image_extractor import get_extractor
        result = get_extractor().extract_from_base64(req.content)
        raw_input = result.extracted_text
    elif req.input_type == "audio":
        raw_input = req.content
    else:
        raise HTTPException(status_code=400, detail="input_type must be: text | image | audio")

    return orchestrator.run(raw_input, input_type=req.input_type)

@router.post("/verify")
def verify_solution(request: VerificationRequest):
    """Verify an existing solution (for HITL review)."""
    result = coordinator.verify_only(request.question, request.solution)
    return result


@router.post("/explain")
def explain_solution(request: QuestionRequest):
    """Generate explanation for a solution."""
    parsed = parser_agent.run(request.question)
    solution = solver_agent.run(parsed)
    explanation = explainer_agent.run(parsed, solution)
    return explanation


# ==================== Memory & Self-Learning Endpoints ====================

@router.post("/memory/search")
def search_memory(request: MemorySearchRequest):
    """Search memory for similar problems."""
    try:
        result = coordinator.search_memory(
            query=request.query,
            topic=request.topic,
            n_results=request.n_results
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory search failed: {str(e)}")


@router.post("/memory/add")
def add_to_memory(request: MemoryAddRequest):
    """Manually add a memory entry."""
    from memory import MemoryEntry
    
    try:
        entry = MemoryEntry(
            original_input=request.original_input,
            parsed_question=request.parsed_question,
            retrieved_context="",
            final_answer=request.final_answer,
            verifier_outcome={"is_correct": True, "confidence": 1.0},
            topic=request.topic,
            complexity=request.complexity
        )
        
        # Use coordinator's memory store for consistency
        memory_id = coordinator.memory_store.add_entry(entry)
        
        return {"success": True, "memory_id": memory_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add memory: {str(e)}")


@router.post("/feedback")
def submit_feedback(request: FeedbackRequest):
    """Submit user feedback for self-learning."""
    try:
        result = coordinator.add_feedback(
            memory_id=request.memory_id,
            correct_answer=request.correct_answer,
            user_comment=request.user_comment,
            feedback_type=request.feedback_type
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")


@router.get("/memory/stats")
def get_memory_stats():
    """Get memory statistics."""
    try:
        stats = coordinator.get_memory_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


# ==================== OCR Endpoints ====================

@router.post("/ocr/extract")
async def extract_text_from_image(file: UploadFile = File(...)):
    """
    Extract text from uploaded image.
    
    - Accepts JPG/PNG images
    - Returns extracted text with confidence score
    - Triggers HITL if confidence < 80%
    
    Returns:
        session_id: Unique identifier for this OCR session
        text: Extracted text
        lines: Individual text lines with confidence scores
        confidence: Average confidence (0-1)
        low_confidence: Whether confidence is below threshold
        needs_hitl: Whether human review is recommended
    """
    try:
        if file.content_type and not file.content_type.startswith("image/"):
            print(f">>> [API] Rejected file: {file.content_type}")
            raise HTTPException(
                status_code=400,
                detail=f"Uploaded file appears to be {file.content_type}, but an image is required."
            )
        
        # Read image bytes
        image_bytes = await file.read()
        
        # Validate file size (max 10MB)
        if len(image_bytes) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="Image file too large. Maximum size is 10MB."
            )
        
        # Extract text using OCR (run in thread pool for async)
        result = await asyncio.to_thread(ocr_tool.extract_text, image_bytes)
        
        # Generate session ID for tracking
        session_id = str(uuid.uuid4())
        
        response = {
            "session_id": session_id,
            "text": result["text"],
            "lines": result["lines"],
            "confidence": result["confidence"],
            "low_confidence": result["low_confidence"],
            "needs_hitl": result["needs_hitl"],
            "hitl_reason": result.get("hitl_reason", ""),
            "message": "Please review and correct the extracted text" 
                      if result["low_confidence"] 
                      else "Text extracted successfully"
        }
        if "error" in result:
            print(f">>> [API OCR Error] {result['error']}")
            response["message"] = f"Error during OCR: {result['error']}"
            
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")


@router.post("/ocr/confirm")
async def confirm_ocr_text(request: OCRConfirmationRequest):
    """
    User confirms or edits OCR text.
    
    - If user_approved=True: proceed to solver
    - If user_approved=False: trigger HITL for manual review
    
    Returns:
        status: 'approved', 'needs_review', or 'error'
        solution: Full solution result if approved
        message: Status message
    """
    try:
        if request.user_approved:
            # Proceed with corrected text to solver
            solution_result = coordinator.solve_problem(request.corrected_text)
            
            return {
                "status": "approved",
                "text": request.corrected_text,
                "solution": solution_result,
                "message": "Text approved. Problem solved successfully."
            }
        else:
            # User rejected - trigger HITL
            return {
                "status": "needs_review",
                "text": request.corrected_text,
                "message": "Text flagged for human review."
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ocr/solve")
async def solve_from_image(
    file: UploadFile = File(...),
    auto_approve: bool = Query(True, description="Auto-proceed if OCR confidence is high")
):
    """
    Complete flow: OCR + Solve + Explain.
    
    Convenience endpoint for full image-to-solution pipeline.
    
    Args:
        file: Image file (JPG/PNG)
        auto_approve: If True, auto-proceed when confidence is high.
                     If False, always return for user review first.
    
    Returns:
        status: 'success', 'needs_review', or 'error'
        ocr_result: OCR extraction results
        solution: Full solution if successful
    """
    try:
        if file.content_type and not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail=f"Uploaded file appears to be {file.content_type}, but an image is required."
            )
        
        # Step 1: OCR (run in thread pool for async)
        image_bytes = await file.read()
        ocr_result = await asyncio.to_thread(ocr_tool.extract_text, image_bytes)
        
        # Step 2: Check confidence
        if not auto_approve or ocr_result["low_confidence"]:
            # Return for user review
            return {
                "status": "needs_review",
                "stage": "ocr",
                "session_id": str(uuid.uuid4()),
                "extracted_text": ocr_result["text"],
                "confidence": ocr_result["confidence"],
                "lines": ocr_result["lines"],
                "needs_hitl": ocr_result["needs_hitl"],
                "message": "OCR confidence low. Please review and correct text."
            }
        
        # Step 3: Solve the problem
        solution = coordinator.solve_problem(ocr_result["text"])
        
        return {
            "status": "success",
            "ocr_result": {
                "text": ocr_result["text"],
                "confidence": ocr_result["confidence"],
                "lines_count": len(ocr_result["lines"])
            },
            "solution": solution
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ocr/from_base64")
async def extract_from_base64(request: OCRSolveRequest):
    """
    Extract text from base64-encoded image.
    
    Useful for mobile apps or when sending image as base64 string.
    
    Args:
        request: Contains base64 image data and filename
    
    Returns:
        OCR extraction results with session_id
    """
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(request.image_data)
        
        # Extract text
        result = ocr_tool.extract_text(image_bytes)
        
        session_id = str(uuid.uuid4())
        
        return {
            "session_id": session_id,
            "text": result["text"],
            "lines": result["lines"],
            "confidence": result["confidence"],
            "low_confidence": result["low_confidence"],
            "needs_hitl": result["needs_hitl"],
            "message": "Text extracted" if not result["low_confidence"] else "Review recommended"
        }
        
    except base64.binascii.Error:
        raise HTTPException(status_code=400, detail="Invalid base64 encoding")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")


@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "agents": 5, "memory_enabled": True, "ocr_enabled": True, "asr_enabled": True}


# ==================== ASR Endpoints ====================

@router.post("/asr/transcribe")
async def transcribe_audio_file(
    file: UploadFile = File(...),
    language: str = Query("en", description="Language code")
):
    """
    Transcribe audio file.
    """
    try:
        audio_bytes = await file.read()
        result = await asyncio.to_thread(
            transcribe_audio, 
            audio_bytes, 
            file.filename, 
            language
        )
        return {"session_id": str(uuid.uuid4()), **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/asr/from_base64")
async def transcribe_from_base64(request: ASRBase64Request):
    """
    Transcribe audio from base64 string.
    """
    try:
        audio_bytes = base64.b64decode(request.audio_data)
        result = await asyncio.to_thread(
            transcribe_audio, 
            audio_bytes, 
            request.filename, 
            request.language
        )
        return {"session_id": str(uuid.uuid4()), **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

