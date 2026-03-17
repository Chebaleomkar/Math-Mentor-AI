"""
main.py  —  FastAPI backend
----------------------------
All routes:
  POST  /extract/image          upload image  → extracted math text
  POST  /extract/image/base64   base64 image  → extracted math text
  POST  /extract/audio          upload audio  → math transcript
  POST  /extract/audio/base64   base64 audio  → math transcript
  POST  /solve                  confirmed text → full agent pipeline
  POST  /hitl/{id}              human review response
  POST  /feedback/{id}          thumbs up / down
  GET   /memory                 recent solved problems
  GET   /memory/{id}            single record
  GET   /health

Startup:
  uvicorn main:app --reload --port 8000
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from routes.image_routes import router as image_router
from routes.audio_routes import router as audio_router
from core.orchestrator import Orchestrator
from core import memory as mem_store
from models.schemas import HITLResponse, SolveResponse
from rag.vector_store import VectorStore


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not VectorStore.is_populated():
        print(
            "\n[WARNING] ChromaDB collection is empty.\n"
            "Run: python -m rag.embed_kb\n"
            "The app works but RAG retrieval returns no results.\n"
        )
    yield


app = FastAPI(title="Math Mentor AI", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(image_router)
app.include_router(audio_router)

orchestrator = Orchestrator()


class SolveRequest(BaseModel):
    input_type: str
    content: str
    filename: Optional[str] = None


class FeedbackRequest(BaseModel):
    feedback: str
    comment: Optional[str] = ""


@app.post("/solve", response_model=SolveResponse)
async def solve(req: SolveRequest):
    if req.input_type == "text":
        raw_input = req.content
    elif req.input_type == "image":
        from core.image_extractor import get_extractor
        result = get_extractor().extract_from_base64(req.content)
        raw_input = result.extracted_text
    elif req.input_type == "audio":
        import base64 as b64lib
        audio_bytes = b64lib.b64decode(req.content)
        from core.audio_transcriber import get_transcriber
        result = get_transcriber().transcribe(
            audio_bytes=audio_bytes,
            filename=req.filename or "audio.wav",
        )
        raw_input = result.cleaned_text
    if not raw_input or not raw_input.strip():
        raise HTTPException(
            status_code=400, 
            detail="I couldn't hear or read that. Please provide a clear mathematical question."
        )

    return orchestrator.run(raw_input, input_type=req.input_type)


@app.post("/hitl/{memory_id}")
def hitl_response(memory_id: str, hitl: HITLResponse):
    final = orchestrator.apply_hitl_feedback(memory_id, hitl)
    if final is None:
        raise HTTPException(status_code=404, detail="Memory record not found")
    return {"memory_id": memory_id, "final_answer": final}


@app.post("/feedback/{memory_id}")
def feedback(memory_id: str, req: FeedbackRequest):
    orchestrator.record_feedback(memory_id, req.feedback, req.comment or "")
    return {"status": "ok"}


@app.get("/memory")
def list_memory(limit: int = 20):
    return mem_store.list_recent(limit)


@app.get("/memory/{memory_id}")
def get_memory(memory_id: str):
    record = mem_store.get_record(memory_id)
    if not record:
        raise HTTPException(status_code=404, detail="Not found")
    return record


@app.get("/health")
def health():
    return {"status": "ok", "knowledge_base_ready": VectorStore.is_populated()}