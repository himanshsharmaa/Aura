# Emotion detection module 

import librosa
import numpy as np
from deepface import DeepFace
import cv2
from utils.logger import setup_logger

logger = setup_logger(__name__)

class EmotionDetector:
    def __init__(self):
        """Initialize the emotion detection system."""
        self.emotions = ['happy', 'sad', 'angry', 'neutral', 'fear', 'surprise', 'disgust']
        
    def analyze_voice(self, audio_path):
        """
        Analyze voice characteristics to detect emotions.
        
        Args:
            audio_path (str): Path to the audio file
            
        Returns:
            dict: Detected emotions with confidence scores
        """
        try:
            # Load audio file
            y, sr = librosa.load(audio_path)
            
            # Extract features
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            
            # Calculate statistics
            mfccs_mean = np.mean(mfccs, axis=1)
            spectral_centroid_mean = np.mean(spectral_centroid)
            spectral_rolloff_mean = np.mean(spectral_rolloff)
            
            # Simple rule-based emotion detection
            # This is a basic implementation - could be improved with ML
            if spectral_centroid_mean > 3000:
                emotion = 'happy'
            elif spectral_centroid_mean < 2000:
                emotion = 'sad'
            else:
                emotion = 'neutral'
                
            return {
                'emotion': emotion,
                'confidence': 0.7,  # Placeholder confidence
                'features': {
                    'mfccs_mean': mfccs_mean.tolist(),
                    'spectral_centroid': spectral_centroid_mean,
                    'spectral_rolloff': spectral_rolloff_mean
                }
            }
            
        except Exception as e:
            logger.error(f"Error in voice emotion analysis: {e}")
            return None
            
    def analyze_face(self, image_path=None, frame=None):
        """
        Analyze facial expressions to detect emotions.
        
        Args:
            image_path (str): Path to the image file (optional)
            frame (numpy.ndarray): Video frame (optional)
            
        Returns:
            dict: Detected emotions with confidence scores
        """
        try:
            if image_path:
                result = DeepFace.analyze(
                    img_path=image_path,
                    actions=['emotion'],
                    enforce_detection=False
                )
            elif frame is not None:
                result = DeepFace.analyze(
                    img_path=frame,
                    actions=['emotion'],
                    enforce_detection=False
                )
            else:
                raise ValueError("Either image_path or frame must be provided")
                
            return {
                'emotion': result[0]['dominant_emotion'],
                'confidence': result[0]['emotion'][result[0]['dominant_emotion']] / 100,
                'all_emotions': result[0]['emotion']
            }
            
        except Exception as e:
            logger.error(f"Error in facial emotion analysis: {e}")
            return None
            
    def combine_emotions(self, voice_emotion, face_emotion):
        """
        Combine voice and facial emotion analysis for a more accurate result.
        
        Args:
            voice_emotion (dict): Voice emotion analysis result
            face_emotion (dict): Facial emotion analysis result
            
        Returns:
            dict: Combined emotion analysis result
        """
        if not voice_emotion and not face_emotion:
            return {'emotion': 'neutral', 'confidence': 0.5}
            
        if not voice_emotion:
            return face_emotion
        if not face_emotion:
            return voice_emotion
            
        # Combine emotions with weighted average
        voice_weight = 0.4
        face_weight = 0.6
        
        # If emotions match, increase confidence
        if voice_emotion['emotion'] == face_emotion['emotion']:
            confidence = (voice_emotion['confidence'] * voice_weight + 
                         face_emotion['confidence'] * face_weight) * 1.2
            emotion = voice_emotion['emotion']
        else:
            # If emotions differ, use the one with higher confidence
            if voice_emotion['confidence'] > face_emotion['confidence']:
                emotion = voice_emotion['emotion']
                confidence = voice_emotion['confidence']
            else:
                emotion = face_emotion['emotion']
                confidence = face_emotion['confidence']
                
        return {
            'emotion': emotion,
            'confidence': min(confidence, 1.0),
            'voice_emotion': voice_emotion,
            'face_emotion': face_emotion
        } 