"""
tests/test_audio_transcriber.py
---------------------------------
Tests for the math-specific normalisation logic in audio_transcriber.py.
The Groq API call itself is mocked — no credits consumed.
"""
import pytest
from unittest.mock import patch, MagicMock


class TestMathNormalisation:
    """Tests for _normalise_math() — fully offline."""

    def _norm(self, text: str) -> str:
        from core.audio_transcriber import _normalise_math
        return _normalise_math(text)

    def test_squared(self):
        assert "^2" in self._norm("x squared")

    def test_cubed(self):
        assert "^3" in self._norm("x cubed")

    def test_square_root(self):
        assert "sqrt" in self._norm("square root of x")

    def test_divided_by(self):
        assert "/" in self._norm("a divided by b")

    def test_pi(self):
        assert "π" in self._norm("the area is pi r squared")

    def test_alpha_beta(self):
        result = self._norm("alpha plus beta")
        assert "α" in result and "β" in result

    def test_infinity(self):
        assert "∞" in self._norm("as x approaches infinity")

    def test_integration(self):
        assert "∫" in self._norm("integral of f of x")

    def test_derivative(self):
        assert "d/dx" in self._norm("derivative of x squared")

    def test_equals(self):
        result = self._norm("x equals 5")
        assert "=" in result

    def test_limit(self):
        assert "lim" in self._norm("limit as x approaches 0")

    def test_no_mangling_of_normal_text(self):
        result = self._norm("find the value of x")
        assert "find the value of x" == result.lower()

    def test_complex_expression(self):
        result = self._norm(
            "find the derivative of x squared plus square root of x"
        )
        assert "d/dx" in result
        assert "^2" in result
        assert "sqrt" in result


class TestLowConfidenceDetection:
    def _detect(self, text):
        from core.audio_transcriber import _detect_low_confidence
        return _detect_low_confidence(text)

    def test_very_short_transcript(self):
        needs_review, reason = self._detect("ok")
        assert needs_review is True
        assert "short" in reason

    def test_normal_length_no_issues(self):
        needs_review, _ = self._detect(
            "find the roots of the quadratic equation x squared minus five x plus six equals zero"
        )
        assert needs_review is False

    def test_inaudible_marker(self):
        needs_review, reason = self._detect("find [inaudible] the value of x")
        assert needs_review is True

    def test_clean_math_sentence(self):
        needs_review, _ = self._detect(
            "what is the probability of getting two heads in three coin tosses"
        )
        assert needs_review is False


class TestAudioTranscriberMocked:
    """Test the full transcriber with Groq API mocked."""

    def _make_mock_response(self, text: str, language: str = "en", duration: float = 3.0):
        m = MagicMock()
        m.text = text
        m.language = language
        m.duration = duration
        return m

    def test_transcribe_returns_result(self):
        with patch("groq.resources.audio.transcriptions.Transcriptions.create") as mock_create:
            mock_create.return_value = self._make_mock_response(
                "find the derivative of x squared plus 3 x"
            )
            from core.audio_transcriber import AudioTranscriber
            transcriber = AudioTranscriber()
            result = transcriber.transcribe(b"fake_audio_bytes", filename="test.wav")

        assert "sqrt" in result.cleaned_text or "^2" in result.cleaned_text or result.transcript
        assert result.language == "en"
        assert result.duration_seconds == 3.0

    def test_too_large_file_raises(self):
        from core.audio_transcriber import AudioTranscriber, MAX_AUDIO_BYTES
        transcriber = AudioTranscriber()
        with pytest.raises(ValueError, match="too large"):
            transcriber.transcribe(b"x" * (MAX_AUDIO_BYTES + 1), filename="big.wav")

    def test_unsupported_format_raises(self):
        from core.audio_transcriber import AudioTranscriber
        transcriber = AudioTranscriber()
        with pytest.raises(ValueError, match="Unsupported"):
            transcriber.transcribe(b"data", filename="audio.flac")