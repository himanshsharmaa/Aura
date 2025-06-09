# Test STT module 

import pytest
import os
import tempfile
import wave
import numpy as np
from src.ai.stt import SpeechToText

@pytest.fixture
def stt():
    return SpeechToText()

@pytest.fixture
def sample_audio():
    # Create a temporary WAV file with a simple sine wave
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        # Generate a 1-second sine wave at 440 Hz
        sample_rate = 16000
        t = np.linspace(0, 1, sample_rate)
        audio_data = np.sin(2 * np.pi * 440 * t)
        
        # Convert to 16-bit PCM
        audio_data = (audio_data * 32767).astype(np.int16)
        
        # Save as WAV file
        with wave.open(temp_file.name, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_data.tobytes())
            
        return temp_file.name

def test_stt_initialization(stt):
    """Test STT module initialization"""
    assert stt is not None
    assert stt.model is not None

def test_transcribe_empty_audio(stt):
    """Test transcription with empty audio"""
    with tempfile.NamedTemporaryFile(suffix='.wav') as temp_file:
        # Create an empty WAV file
        with wave.open(temp_file.name, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(b'')
            
        result = stt.transcribe(temp_file.name)
        assert result == ""

def test_transcribe_sample_audio(stt, sample_audio):
    """Test transcription with sample audio"""
    result = stt.transcribe(sample_audio)
    assert isinstance(result, str)
    
    # Clean up
    os.unlink(sample_audio)

def test_transcribe_nonexistent_file(stt):
    """Test transcription with nonexistent file"""
    with pytest.raises(Exception):
        stt.transcribe("nonexistent.wav")

def test_transcribe_invalid_file(stt):
    """Test transcription with invalid file"""
    with tempfile.NamedTemporaryFile(suffix='.txt') as temp_file:
        temp_file.write(b"Not a WAV file")
        temp_file.flush()
        
        with pytest.raises(Exception):
            stt.transcribe(temp_file.name) 
