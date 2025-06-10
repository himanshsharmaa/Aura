import unittest
import os
import sys
import json
import numpy as np
import sounddevice as sd
import torch
from pathlib import Path

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from tasks.hotword_detector import HotwordDetector, HotwordModel
from tasks.alarms import AlarmSystem
from ai.stt import SpeechToText
from ai.tts import TextToSpeech
from ai.emotion import EmotionDetector
from utils.logger import setup_logger

class TestAuraComponents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.logger = setup_logger()
        cls.config_path = 'config.json'
        cls.test_audio_duration = 1.0  # seconds
        
        # Create test directories
        os.makedirs('models', exist_ok=True)
        os.makedirs('data/training_samples/positive', exist_ok=True)
        os.makedirs('data/training_samples/negative', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # Load config
        with open(cls.config_path, 'r') as f:
            cls.config = json.load(f)
    
    def test_01_hotword_detector(self):
        """Test hotword detection component"""
        self.logger.info("Testing hotword detector...")
        
        try:
            detector = HotwordDetector(self.config_path)
            
            # Test model loading
            self.assertIsNotNone(detector.model)
            
            # Test sample collection
            self.assertTrue(detector.start_collecting_samples('positive'))
            self.assertTrue(detector.stop_collecting_samples())
            
            # Test visualization callback
            def on_confidence_update(confidence, history):
                self.assertIsInstance(confidence, float)
                self.assertIsInstance(history, list)
            
            detector.set_visualization_callback(on_confidence_update)
            
            # Test model training
            positive_samples = [np.random.rand(16000) for _ in range(2)]
            negative_samples = [np.random.rand(16000) for _ in range(2)]
            self.assertTrue(detector.train_model(positive_samples, negative_samples))
            
            self.logger.info("Hotword detector tests passed")
            
        except Exception as e:
            self.logger.error(f"Hotword detector test failed: {e}")
            raise
    
    def test_02_alarm_system(self):
        """Test alarm system component"""
        self.logger.info("Testing alarm system...")
        
        try:
            alarm = AlarmSystem(self.config_path)
            
            # Test sound event model loading
            self.assertIsNotNone(alarm._load_sound_event_model())
            
            # Test event callbacks
            event_detected = False
            def on_event(confidence):
                nonlocal event_detected
                event_detected = True
                self.assertIsInstance(confidence, float)
            
            alarm.register_event_callback("Shout", on_event)
            
            # Test event history
            history = alarm.get_event_history()
            self.assertIsInstance(history, list)
            
            self.logger.info("Alarm system tests passed")
            
        except Exception as e:
            self.logger.error(f"Alarm system test failed: {e}")
            raise
    
    def test_03_speech_components(self):
        """Test speech-to-text and text-to-speech components"""
        self.logger.info("Testing speech components...")
        
        try:
            # Test STT
            stt = SpeechToText()
            self.assertIsNotNone(stt)
            
            # Test TTS
            tts = TextToSpeech()
            self.assertIsNotNone(tts)
            
            self.logger.info("Speech components tests passed")
            
        except Exception as e:
            self.logger.error(f"Speech components test failed: {e}")
            raise
    
    def test_04_emotion_detection(self):
        """Test emotion detection component"""
        self.logger.info("Testing emotion detection...")
        
        try:
            emotion_detector = EmotionDetector()
            
            # Test with random audio
            test_audio = np.random.rand(16000)
            emotion = emotion_detector.detect_emotion(test_audio)
            self.assertIsInstance(emotion, dict)
            
            self.logger.info("Emotion detection tests passed")
            
        except Exception as e:
            self.logger.error(f"Emotion detection test failed: {e}")
            raise
    
    def test_05_audio_device(self):
        """Test audio device availability"""
        self.logger.info("Testing audio device...")
        
        try:
            devices = sd.query_devices()
            self.assertGreater(len(devices), 0)
            
            # Test default input device
            default_input = sd.query_devices(kind='input')
            self.assertIsNotNone(default_input)
            
            self.logger.info("Audio device tests passed")
            
        except Exception as e:
            self.logger.error(f"Audio device test failed: {e}")
            raise
    
    def test_06_config_validation(self):
        """Test configuration validation"""
        self.logger.info("Testing configuration...")
        
        try:
            required_keys = [
                'hotword_detection',
                'sound_events',
                'sound_event_detection',
                'emotion_detection',
                'database',
                'ui'
            ]
            
            for key in required_keys:
                self.assertIn(key, self.config)
            
            self.logger.info("Configuration tests passed")
            
        except Exception as e:
            self.logger.error(f"Configuration test failed: {e}")
            raise

def run_tests():
    """Run all tests and generate report"""
    logger = setup_logger()
    logger.info("Starting component tests...")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAuraComponents)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate report
    report = {
        'total_tests': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors),
        'skipped': len(result.skipped)
    }
    
    logger.info(f"Test Report: {report}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1) 