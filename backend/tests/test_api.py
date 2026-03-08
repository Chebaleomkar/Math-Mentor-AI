"""
tests/test_api.py
------------------
Integration tests for all FastAPI endpoints.
Uses the app_client fixture from conftest.py (all external calls mocked).
"""
import base64
import json

import pytest


# ── Health ────────────────────────────────────────────────────────────────────

class TestHealth:
    def test_health_returns_ok(self, app_client):
        r = app_client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert "knowledge_base_ready" in data


# ── /extract/image ─────────────────────────────────────────────────────────────

class TestImageExtraction:
    @pytest.fixture
    def tiny_png_bytes(self) -> bytes:
        """1x1 white PNG — minimal valid image."""
        import struct, zlib
        def _chunk(name, data):
            c = struct.pack(">I", len(data)) + name + data
            return c + struct.pack(">I", zlib.crc32(name + data) & 0xFFFFFFFF)
        sig = b"\x89PNG\r\n\x1a\n"
        ihdr = _chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
        idat = _chunk(b"IDAT", zlib.compress(b"\x00\xFF\xFF\xFF"))
        iend = _chunk(b"IEND", b"")
        return sig + ihdr + idat + iend

    def test_upload_returns_extraction_shape(self, app_client, tiny_png_bytes):
        from unittest.mock import patch, MagicMock
        mock_result = MagicMock()
        mock_result.extracted_text = "Find the derivative of x^3"
        mock_result.confidence = "high"
        mock_result.needs_review = False
        mock_result.notes = ""

        with patch("core.image_extractor.ImageExtractor.extract", return_value=mock_result):
            r = app_client.post(
                "/extract/image",
                files={"file": ("test.png", tiny_png_bytes, "image/png")},
            )

        assert r.status_code == 200
        data = r.json()
        assert "extracted_text" in data
        assert "confidence" in data
        assert "needs_review" in data

    def test_unsupported_format_returns_415(self, app_client):
        r = app_client.post(
            "/extract/image",
            files={"file": ("test.bmp", b"fake", "image/bmp")},
        )
        assert r.status_code == 415

    def test_base64_endpoint(self, app_client, tiny_png_bytes):
        from unittest.mock import patch, MagicMock
        mock_result = MagicMock()
        mock_result.extracted_text = "Integrate x^2 dx"
        mock_result.confidence = "medium"
        mock_result.needs_review = True
        mock_result.notes = "Handwriting slightly unclear"

        b64 = base64.b64encode(tiny_png_bytes).decode()
        with patch("core.image_extractor.ImageExtractor.extract", return_value=mock_result):
            r = app_client.post(
                "/extract/image/base64",
                json={"image_data": b64, "mime_type": "image/png"},
            )

        assert r.status_code == 200
        data = r.json()
        assert data["needs_review"] is True


# ── /extract/audio ─────────────────────────────────────────────────────────────

class TestAudioExtraction:
    def test_upload_returns_transcription_shape(self, app_client):
        from unittest.mock import patch, MagicMock
        mock_result = MagicMock()
        mock_result.transcript = "find the square root of x squared plus 4"
        mock_result.cleaned_text = "find the sqrt(x^2 + 4)"
        mock_result.language = "en"
        mock_result.duration_seconds = 3.5
        mock_result.needs_review = False
        mock_result.notes = ""

        fake_wav = b"RIFF$\x00\x00\x00WAVEfmt " + b"\x00" * 20

        with patch("core.audio_transcriber.AudioTranscriber.transcribe", return_value=mock_result):
            r = app_client.post(
                "/extract/audio",
                files={"file": ("recording.wav", fake_wav, "audio/wav")},
            )

        assert r.status_code == 200
        data = r.json()
        assert "transcript" in data
        assert "cleaned_text" in data
        assert "duration_seconds" in data

    def test_unsupported_format_returns_415(self, app_client):
        r = app_client.post(
            "/extract/audio",
            files={"file": ("test.flac", b"fake", "audio/flac")},
        )
        assert r.status_code == 415

    def test_base64_endpoint(self, app_client):
        from unittest.mock import patch, MagicMock
        mock_result = MagicMock()
        mock_result.transcript = "probability of getting heads"
        mock_result.cleaned_text = "probability of getting heads"
        mock_result.language = "en"
        mock_result.duration_seconds = 2.0
        mock_result.needs_review = False
        mock_result.notes = ""

        b64 = base64.b64encode(b"fake_audio_data").decode()
        with patch("core.audio_transcriber.AudioTranscriber.transcribe", return_value=mock_result):
            r = app_client.post(
                "/extract/audio/base64",
                json={"audio_data": b64, "filename": "rec.wav", "language": "en"},
            )

        assert r.status_code == 200


# ── /solve ─────────────────────────────────────────────────────────────────────

class TestSolveEndpoint:
    def test_text_solve_returns_full_response(self, app_client):
        from unittest.mock import patch
        with patch("core.orchestrator.Orchestrator.run") as mock_run:
            from models.schemas import (
                SolveResponse, ParsedProblem, SolverResult,
                VerifierResult, ExplanationResult,
            )
            mock_run.return_value = SolveResponse(
                parsed_problem=ParsedProblem(
                    problem_text="x^2 - 5x + 6 = 0", topic="algebra"
                ),
                solver_result=SolverResult(
                    solution="(x-2)(x-3)=0\nFINAL ANSWER: x=2 and x=3",
                    final_answer="x=2 and x=3",
                ),
                verifier_result=VerifierResult(is_correct=True, confidence=0.97),
                explanation=ExplanationResult(
                    explanation="Step 1: Factor...",
                    final_answer="x=2 and x=3",
                    confidence=0.97,
                ),
                hitl_required=False,
                memory_id="test-uuid-001",
            )

            r = app_client.post("/solve", json={
                "input_type": "text",
                "content": "Find the roots of x^2 - 5x + 6 = 0",
            })

        assert r.status_code == 200
        data = r.json()
        assert "parsed_problem" in data
        assert "solver_result" in data
        assert "verifier_result" in data
        assert "explanation" in data
        assert "memory_id" in data
        assert data["hitl_required"] is False

    def test_invalid_input_type_returns_400(self, app_client):
        r = app_client.post("/solve", json={
            "input_type": "video",
            "content": "some content",
        })
        assert r.status_code == 400

    def test_missing_content_returns_422(self, app_client):
        r = app_client.post("/solve", json={"input_type": "text"})
        assert r.status_code == 422


# ── /hitl ──────────────────────────────────────────────────────────────────────

class TestHITLEndpoint:
    def test_approve_hitl(self, app_client):
        from unittest.mock import patch
        with patch("core.orchestrator.Orchestrator.apply_hitl_feedback", return_value="x = 3"):
            r = app_client.post("/hitl/test-mem-001", json={
                "approved": True,
                "comment": "Looks correct",
            })
        assert r.status_code == 200
        data = r.json()
        assert data["final_answer"] == "x = 3"

    def test_reject_with_correction(self, app_client):
        from unittest.mock import patch
        with patch("core.orchestrator.Orchestrator.apply_hitl_feedback", return_value="x = -3"):
            r = app_client.post("/hitl/test-mem-002", json={
                "approved": False,
                "edited_answer": "x = -3",
                "comment": "Sign was wrong",
            })
        assert r.status_code == 200
        assert r.json()["final_answer"] == "x = -3"

    def test_not_found_returns_404(self, app_client):
        from unittest.mock import patch
        with patch("core.orchestrator.Orchestrator.apply_hitl_feedback", return_value=None):
            r = app_client.post("/hitl/nonexistent-id", json={"approved": True})
        assert r.status_code == 404


# ── /feedback ──────────────────────────────────────────────────────────────────

class TestFeedbackEndpoint:
    def test_correct_feedback(self, app_client):
        from unittest.mock import patch
        with patch("core.orchestrator.Orchestrator.record_feedback"):
            r = app_client.post("/feedback/mem-001", json={"feedback": "correct"})
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_incorrect_feedback_with_comment(self, app_client):
        from unittest.mock import patch
        with patch("core.orchestrator.Orchestrator.record_feedback"):
            r = app_client.post("/feedback/mem-002", json={
                "feedback": "incorrect",
                "comment": "The sign is wrong",
            })
        assert r.status_code == 200


# ── /memory ────────────────────────────────────────────────────────────────────

class TestMemoryEndpoints:
    def test_list_memory(self, app_client):
        from unittest.mock import patch
        with patch("core.memory.list_recent", return_value=[
            {
                "id": "abc", "problem_text": "x^2=4", "topic": "algebra",
                "final_answer": "x=2", "user_feedback": "correct",
                "timestamp": "2025-01-01T00:00:00+00:00",
            }
        ]):
            r = app_client.get("/memory")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_get_single_record(self, app_client):
        from unittest.mock import patch
        with patch("core.memory.get_record", return_value={"id": "abc", "raw_input": "x^2=4"}):
            r = app_client.get("/memory/abc")
        assert r.status_code == 200
        assert r.json()["id"] == "abc"

    def test_get_nonexistent_returns_404(self, app_client):
        from unittest.mock import patch
        with patch("core.memory.get_record", return_value=None):
            r = app_client.get("/memory/does-not-exist")
        assert r.status_code == 404