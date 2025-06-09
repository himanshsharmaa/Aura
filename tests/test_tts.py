# Test TTS module 

import pytest
import os
import asyncio
from src.ai.tts import TextToSpeech

@pytest.fixture
def tts():
    return TextToSpeech()

@pytest.mark.asyncio
async def test_tts_initialization(tts):
    """Test TTS module initialization"""
    assert tts is not None
    assert tts.voice is not None

@pytest.mark.asyncio
async def test_speak_empty_text(tts):
    """Test speaking empty text"""
    await tts.speak("")
    assert os.path.exists("output.mp3")
    os.remove("output.mp3")

@pytest.mark.asyncio
async def test_speak_sample_text(tts):
    """Test speaking sample text"""
    text = "Hello, this is a test."
    await tts.speak(text)
    assert os.path.exists("output.mp3")
    os.remove("output.mp3")

@pytest.mark.asyncio
async def test_speak_long_text(tts):
    """Test speaking long text"""
    text = "This is a longer test message that should still work properly. " * 5
    await tts.speak(text)
    assert os.path.exists("output.mp3")
    os.remove("output.mp3")

@pytest.mark.asyncio
async def test_speak_special_characters(tts):
    """Test speaking text with special characters"""
    text = "Hello! This is a test with special characters: @#$%^&*()"
    await tts.speak(text)
    assert os.path.exists("output.mp3")
    os.remove("output.mp3")

@pytest.mark.asyncio
async def test_speak_multiple_times(tts):
    """Test speaking multiple times in sequence"""
    texts = ["First message", "Second message", "Third message"]
    for text in texts:
        await tts.speak(text)
        assert os.path.exists("output.mp3")
        os.remove("output.mp3") 
