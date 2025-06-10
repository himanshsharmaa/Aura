import os
import sys
import json
import time
import sounddevice as sd
import tensorflow as tf
import tensorflow_hub as hub
from datetime import datetime
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from utils.logger import setup_logger
from tasks.hotword_detector import HotwordDetector
from tasks.alarms import AlarmSystem

# Set up logging
logger = setup_logger(__name__)

def test_audio_devices():
    """Test audio input devices"""
    logger.info("Testing audio devices...")
    try:
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        
        if not input_devices:
            logger.error("No input devices found!")
            return False
        
        logger.info(f"Found {len(input_devices)} input devices:")
        for device in input_devices:
            logger.info(f"- {device['name']}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing audio devices: {e}")
        return False

def test_model_loading():
    """Test loading of YAMNet model"""
    logger.info("Testing model loading...")
    try:
        model = hub.load('https://tfhub.dev/google/yamnet/1')
        logger.info("Successfully loaded YAMNet model")
        return True
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return False

def test_hotword_detection():
    """Test hotword detection"""
    logger.info("Testing hotword detection...")
    try:
        detector = HotwordDetector()
        detector.start_listening(lambda: logger.info("Hotword detected!"))
        time.sleep(5)  # Listen for 5 seconds
        detector.stop_listening()
        logger.info("Hotword detection test completed")
        return True
    except Exception as e:
        logger.error(f"Error testing hotword detection: {e}")
        return False

def test_sound_event_detection():
    """Test sound event detection"""
    logger.info("Testing sound event detection...")
    try:
        alarm_system = AlarmSystem()
        alarm_system.start()
        time.sleep(5)  # Listen for 5 seconds
        alarm_system.stop()
        logger.info("Sound event detection test completed")
        return True
    except Exception as e:
        logger.error(f"Error testing sound event detection: {e}")
        return False

def create_test_report(results):
    """Create a test report"""
    report_dir = Path('reports')
    report_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = report_dir / f'test_report_{timestamp}.txt'
    
    with open(report_file, 'w') as f:
        f.write("Aura Component Test Report\n")
        f.write("========================\n\n")
        f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for test_name, result in results.items():
            f.write(f"{test_name}: {'PASS' if result else 'FAIL'}\n")
    
    logger.info(f"Test report created: {report_file}")

def main():
    """Run all tests"""
    logger.info("Starting component tests...")
    
    # Create necessary directories
    for directory in ['models', 'data/training_samples/positive', 
                     'data/training_samples/negative', 'logs', 'data/cache']:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Run tests
    results = {
        'Audio Devices': test_audio_devices(),
        'Model Loading': test_model_loading(),
        'Hotword Detection': test_hotword_detection(),
        'Sound Event Detection': test_sound_event_detection()
    }
    
    # Create test report
    create_test_report(results)
    
    # Print summary
    logger.info("\nTest Results:")
    for test_name, result in results.items():
        logger.info(f"{test_name}: {'PASS' if result else 'FAIL'}")
    
    # Return overall success
    return all(results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 