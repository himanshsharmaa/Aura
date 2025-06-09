import pytest
import os
import tempfile
import wave
import numpy as np
import cv2
from src.ai.emotion import EmotionDetector

@pytest.fixture
def emotion_detector():
    return EmotionDetector()

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

@pytest.fixture
def sample_image():
    # Create a temporary image file with a simple pattern
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
        # Create a simple image
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        img[25:75, 25:75] = [255, 255, 255]  # White square in the middle
        
        # Save image
        cv2.imwrite(temp_file.name, img)
        return temp_file.name

def test_emotion_detector_initialization(emotion_detector):
    """Test emotion detector initialization"""
    assert emotion_detector is not None
    assert isinstance(emotion_detector.emotions, list)
    assert len(emotion_detector.emotions) > 0

def test_analyze_voice(emotion_detector, sample_audio):
    """Test voice emotion analysis"""
    result = emotion_detector.analyze_voice(sample_audio)
    assert result is not None
    assert 'emotion' in result
    assert 'confidence' in result
    assert 'features' in result
    
    # Clean up
    os.unlink(sample_audio)

def test_analyze_face_image(emotion_detector, sample_image):
    """Test facial emotion analysis with image"""
    result = emotion_detector.analyze_face(image_path=sample_image)
    assert result is not None
    assert 'emotion' in result
    assert 'confidence' in result
    assert 'all_emotions' in result
    
    # Clean up
    os.unlink(sample_image)

def test_analyze_face_frame(emotion_detector):
    """Test facial emotion analysis with frame"""
    # Create a simple frame
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    frame[25:75, 25:75] = [255, 255, 255]  # White square in the middle
    
    result = emotion_detector.analyze_face(frame=frame)
    assert result is not None
    assert 'emotion' in result
    assert 'confidence' in result
    assert 'all_emotions' in result

def test_combine_emotions(emotion_detector):
    """Test emotion combination"""
    voice_emotion = {
        'emotion': 'happy',
        'confidence': 0.8
    }
    face_emotion = {
        'emotion': 'happy',
        'confidence': 0.9
    }
    
    result = emotion_detector.combine_emotions(voice_emotion, face_emotion)
    assert result is not None
    assert 'emotion' in result
    assert 'confidence' in result
    assert result['emotion'] == 'happy'
    assert result['confidence'] > 0.8

def test_combine_emotions_different(emotion_detector):
    """Test emotion combination with different emotions"""
    voice_emotion = {
        'emotion': 'happy',
        'confidence': 0.8
    }
    face_emotion = {
        'emotion': 'sad',
        'confidence': 0.9
    }
    
    result = emotion_detector.combine_emotions(voice_emotion, face_emotion)
    assert result is not None
    assert 'emotion' in result
    assert 'confidence' in result
    assert result['emotion'] in ['happy', 'sad']

def test_combine_emotions_missing(emotion_detector):
    """Test emotion combination with missing data"""
    voice_emotion = {
        'emotion': 'happy',
        'confidence': 0.8
    }
    
    result = emotion_detector.combine_emotions(voice_emotion, None)
    assert result is not None
    assert 'emotion' in result
    assert 'confidence' in result
    assert result['emotion'] == 'happy' 