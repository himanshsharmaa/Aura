# Main entry point for Aura

import asyncio
import pyaudio
import wave
import tempfile
import os
import cv2
import numpy as np
from ai.stt import SpeechToText
from ai.tts import TextToSpeech
from ai.nlp import Llama2
from ai.emotion import EmotionDetector
from ai.personality import Personality
from ai.user_activity import UserActivity
from ai.sound_event import SoundEventDetector
from tasks.alarms import HotwordDetector
from utils.logger import setup_logger
import threading
import queue
import time
import sys
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer
from ui.main_window import MainWindow
from tasks.hotword_detector import HotwordDetector
from tasks.alarms import AlarmSystem
from pathlib import Path

logger = setup_logger(__name__)

class AuraApplication:
    def __init__(self):
        self.logger = setup_logger()
        self.app = QApplication(sys.argv)
        self.window = None
        self.hotword_detector = None
        self.alarm_system = None
        self.error_count = 0
        self.max_errors = 3
        
        # Set up error handling
        sys.excepthook = self.handle_exception
        
        # Create required directories
        self._create_directories()
        
        # Initialize components
        self._initialize_components()
    
    def _create_directories(self):
        """Create necessary directories"""
        try:
            directories = [
                'models',
                'data/training_samples/positive',
                'data/training_samples/negative',
                'logs',
                'data/cache'
            ]
            for directory in directories:
                Path(directory).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.logger.error(f"Error creating directories: {e}")
            self._show_error("Directory Creation Error", str(e))
    
    def _initialize_components(self):
        """Initialize application components"""
        try:
            # Initialize hotword detector
            self.hotword_detector = HotwordDetector()
            
            # Initialize alarm system
            self.alarm_system = AlarmSystem()
            
            # Create main window
            self.window = MainWindow(self.hotword_detector, self.alarm_system)
            
            # Set up error handling for components
            self._setup_component_error_handling()
            
        except Exception as e:
            self.logger.error(f"Error initializing components: {e}")
            self._show_error("Initialization Error", str(e))
            sys.exit(1)
    
    def _setup_component_error_handling(self):
        """Set up error handling for components"""
        try:
            # Set up hotword detector error handling
            def on_hotword_error(error):
                self.logger.error(f"Hotword detector error: {error}")
                self._show_error("Hotword Detection Error", str(error))
            
            self.hotword_detector.set_error_callback(on_hotword_error)
            
            # Set up alarm system error handling
            def on_alarm_error(error):
                self.logger.error(f"Alarm system error: {error}")
                self._show_error("Alarm System Error", str(error))
            
            self.alarm_system.set_error_callback(on_alarm_error)
            
        except Exception as e:
            self.logger.error(f"Error setting up error handling: {e}")
            self._show_error("Error Handler Setup Error", str(e))
    
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions"""
        try:
            error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self.logger.error(f"Uncaught exception: {error_msg}")
            
            self.error_count += 1
            if self.error_count >= self.max_errors:
                self._show_error("Critical Error", 
                               "Too many errors occurred. Application will exit.")
                sys.exit(1)
            
            self._show_error("Application Error", str(exc_value))
            
        except Exception as e:
            self.logger.error(f"Error in exception handler: {e}")
            sys.exit(1)
    
    def _show_error(self, title, message):
        """Show error message to user"""
        try:
            QMessageBox.critical(self.window, title, message)
        except Exception as e:
            self.logger.error(f"Error showing error message: {e}")
    
    def run(self):
        """Run the application"""
        try:
            # Show main window
            self.window.show()
            
            # Start components
            self.hotword_detector.start_listening(self.window.on_hotword_detected)
            self.alarm_system.start()
            
            # Set up periodic health check
            self._setup_health_check()
            
            # Run application
            return self.app.exec()
            
        except Exception as e:
            self.logger.error(f"Error running application: {e}")
            self._show_error("Runtime Error", str(e))
            return 1
    
    def _setup_health_check(self):
        """Set up periodic health check"""
        def health_check():
            try:
                # Check hotword detector
                if not self.hotword_detector.is_listening:
                    self.logger.warning("Hotword detector stopped. Restarting...")
                    self.hotword_detector.start_listening(self.window.on_hotword_detected)
                
                # Check alarm system
                if not self.alarm_system.is_running:
                    self.logger.warning("Alarm system stopped. Restarting...")
                    self.alarm_system.start()
                
            except Exception as e:
                self.logger.error(f"Health check error: {e}")
        
        # Run health check every 30 seconds
        QTimer.singleShot(30000, health_check)

def main():
    """Main entry point"""
    try:
        app = AuraApplication()
        sys.exit(app.run())
    except Exception as e:
        logger = setup_logger()
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
