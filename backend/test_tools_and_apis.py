import os
import json
import base64
from fastapi.testclient import TestClient
from main import app
from tools.ocr_tool import extract_text, extract_text_from_bytes, get_ocr_tool
from tools.asr_tool import transcribe_audio, transcribe_speech

client = TestClient(app)

IMAGE_PATH = "test_data/test_image.png"
AUDIO_PATH = "test_data/test_audio.wav"

def test_ocr_tool_direct():
    print("--- Testing OCR Tool Directly ---")
    ocr = get_ocr_tool()
    
    with open(IMAGE_PATH, "rb") as f:
        image_bytes = f.read()
    
    result = ocr.extract_text(image_bytes)
    print("OCR extraction result:", json.dumps(result, indent=2))
    
    # Test LangChain tool
    lc_result = extract_text.invoke({"image_path": IMAGE_PATH})
    print("\nLangchain tool result:\n", lc_result)


def test_asr_tool_direct():
    print("\n--- Testing ASR Tool Directly ---")
    
    with open(AUDIO_PATH, "rb") as f:
        audio_bytes = f.read()
        
    result = transcribe_audio(audio_bytes, "test_audio.wav")
    print("ASR transcription result:", json.dumps(result, indent=2))
    
    # Test LangChain tool
    lc_result = transcribe_speech.invoke({"audio_data": AUDIO_PATH, "filename": "test_audio.wav"})
    print("\nLangchain tool result:\n", lc_result)


def test_ocr_api():
    print("\n--- Testing OCR API ---")
    with open(IMAGE_PATH, "rb") as f:
        response = client.post(
            "/ocr/extract",
            files={"file": ("test_image.png", f, "image/png")}
        )
    print("OCR /extract response:", response.status_code)
    print(response.json())
    
    with open(IMAGE_PATH, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")
        
    response2 = client.post(
        "/ocr/from_base64",
        json={"image_data": image_b64, "filename": "test_image.png"}
    )
    print("OCR /from_base64 response:", response2.status_code)
    print(response2.json())


def test_asr_api():
    print("\n--- Testing ASR API ---")
    with open(AUDIO_PATH, "rb") as f:
        response = client.post(
            "/asr/transcribe",
            files={"file": ("test_audio.wav", f, "audio/wav")}
        )
    print("ASR /transcribe response:", response.status_code)
    print(response.json())
    
    with open(AUDIO_PATH, "rb") as f:
        audio_b64 = base64.b64encode(f.read()).decode("utf-8")
        
    response2 = client.post(
        "/asr/from_base64",
        json={"audio_data": audio_b64, "filename": "test_audio.wav", "language": "en"}
    )
    print("ASR /from_base64 response:", response2.status_code)
    print(response2.json())


if __name__ == "__main__":
    if not os.path.exists("test_data"):
        print("Please run create_test_data.py first.")
        exit(1)
        
    try:
        test_ocr_tool_direct()
    except Exception as e:
        print(f"OCR Tool Test Failed: {e}")
        
    try:
        test_asr_tool_direct()
    except Exception as e:
        print(f"ASR Tool Test Failed: {e}")
        
    try:
        test_ocr_api()
    except Exception as e:
        print(f"OCR API Test Failed: {e}")
        
    try:
        test_asr_api()
    except Exception as e:
        print(f"ASR API Test Failed: {e}")
