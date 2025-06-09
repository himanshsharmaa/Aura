import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import json
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QLabel, QPushButton, QFrame, QSplitter)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import (QPainter, QColor, QPen, QPainterPath, QFont, 
                        QBrush, QLinearGradient, QRadialGradient)
import pyqtgraph as pg
import sounddevice as sd
from src.ui.avatar import Avatar
from src.ui.emotion_visualizer import EmotionVisualizer

# Import core modules
from src.ai.emotion import EmotionDetector
from src.ai.stt import SpeechToText
from src.ai.tts import TextToSpeech
from src.ai.nlp import Llama2
from src.ai.personality import Personality
from src.utils.logger import setup_logger
from typing import Dict, List, Optional, Tuple, Any
from src.core.cloud_sync import CloudSync
import asyncio

logger = setup_logger(__name__)

class VisualizationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 200)
        self.audio_data = np.zeros(1024)
        self.spectrum_data = np.zeros(1024)
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update)
        self.animation_timer.start(30)  # 30ms = ~33fps
        
        # Load config
        with open('config.json', 'r') as f:
            self.config = json.load(f)
            
        # Set up audio stream
        self.stream = sd.InputStream(
            channels=1,
            samplerate=44100,
            callback=self.audio_callback
        )
        self.stream.start()
        
    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.audio_data = np.roll(self.audio_data, -frames)
        self.audio_data[-frames:] = indata[:, 0]
        self.spectrum_data = np.abs(np.fft.rfft(self.audio_data))
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get colors from config
        colors = self.config['ui']['visualization']['colors']
        primary = QColor(colors['primary'])
        secondary = QColor(colors['secondary'])
        background = QColor(colors['background'])
        
        # Draw background
        painter.fillRect(self.rect(), background)
        
        # Draw visualization based on style
        if self.config['ui']['visualization']['style'] == 'wave':
            self.draw_wave(painter, primary, secondary)
        else:
            self.draw_spectrum(painter, primary, secondary)
            
    def draw_wave(self, painter, primary, secondary):
        path = QPainterPath()
        width = self.width()
        height = self.height()
        
        # Draw main wave
        path.moveTo(0, height/2)
        for i in range(len(self.audio_data)):
            x = i * width / len(self.audio_data)
            y = height/2 + self.audio_data[i] * height/2
            path.lineTo(x, y)
            
        # Draw wave
        painter.setPen(QPen(primary, 2))
        painter.drawPath(path)
        
        # Draw secondary wave
        path2 = QPainterPath()
        path2.moveTo(0, height/2)
        for i in range(len(self.audio_data)):
            x = i * width / len(self.audio_data)
            y = height/2 + self.audio_data[i] * height/4
            path2.lineTo(x, y)
            
        painter.setPen(QPen(secondary, 1))
        painter.drawPath(path2)
        
    def draw_spectrum(self, painter, primary, secondary):
        width = self.width()
        height = self.height()
        bar_width = width / len(self.spectrum_data)
        
        for i in range(len(self.spectrum_data)):
            x = i * bar_width
            h = self.spectrum_data[i] * height
            color = QColor(primary)
            color.setAlpha(int(255 * (1 - i/len(self.spectrum_data))))
            painter.fillRect(x, height-h, bar_width, h, color)
            
    def closeEvent(self, event):
        self.stream.stop()
        self.stream.close()
        super().closeEvent(event)

class StatusWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        # Status label
        self.status_label = QLabel("Listening...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #7B68EE;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Event label
        self.event_label = QLabel("")
        self.event_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.event_label.setStyleSheet("""
            QLabel {
                color: #9370DB;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.event_label)
        
    def update_status(self, status, event=None):
        self.status_label.setText(status)
        if event:
            self.event_label.setText(f"Detected: {event}")
        else:
            self.event_label.setText("")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aura AI")
        self.setMinimumSize(800, 600)
        
        # Initialize core modules
        self.emotion_detector = EmotionDetector()
        self.speech_to_text = SpeechToText()
        self.text_to_speech = TextToSpeech()
        self.llama = Llama2()
        self.personality = Personality()
        self.cloud_sync = CloudSync()
        
        # Connect TTS amplitude signal to avatar
        self.text_to_speech.amplitude.connect(self.avatar.update_lip_sync)
        
        # Set up cloud sync timer
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.sync_data)
        self.sync_timer.start(300000)  # Sync every 5 minutes
        
        # Initialize UI
        self.init_ui()
        
        # Start cloud sync
        asyncio.create_task(self.cloud_sync.initialize())
        
    async def sync_data(self):
        """Sync user data to cloud"""
        if not hasattr(self, 'user_id'):
            return
            
        # Sync user data
        user_data = {
            'preferences': self.personality.get_preferences(),
            'personality_traits': self.personality.get_traits(),
            'emotional_state': self.emotion_detector.get_current_state()
        }
        await self.cloud_sync.sync_user_data(self.user_id, user_data)
        
        # Sync memories
        memories = self.personality.get_memories()
        for memory in memories:
            await self.cloud_sync.sync_memory(self.user_id, memory)
            
        # Sync preferences
        preferences = self.personality.get_preferences()
        await self.cloud_sync.sync_preferences(self.user_id, preferences)
        
    async def load_user_data(self, user_id: str):
        """Load user data from cloud"""
        self.user_id = user_id
        
        # Get user data
        user_data = await self.cloud_sync.get_user_data(user_id)
        if user_data:
            # Update personality
            if 'preferences' in user_data:
                self.personality.set_preferences(user_data['preferences'])
            if 'personality_traits' in user_data:
                self.personality.set_traits(user_data['personality_traits'])
                
        # Get memories
        memories = await self.cloud_sync.get_memories(user_id)
        if memories:
            for memory in memories:
                self.personality.add_memory(memory)
                
        # Get preferences
        preferences = await self.cloud_sync.get_preferences(user_id)
        if preferences:
            self.personality.set_preferences(preferences)
            
    def init_ui(self):
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        
        # Create left panel for avatar
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        self.avatar = Avatar()
        left_layout.addWidget(self.avatar)
        
        # Create right panel for emotion visualization
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.emotion_visualizer = EmotionVisualizer()
        right_layout.addWidget(self.emotion_visualizer)
        
        # Add panels to main layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 400])
        layout.addWidget(splitter)
        
    def update_emotions(self):
        """Update emotions based on current state"""
        try:
            # Get current emotions from detector
            emotions = self.emotion_detector.get_current_emotions()
            
            # Update avatar
            if emotions:
                dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0]
                self.avatar.set_emotion(dominant_emotion)
            
            # Update emotion visualizer
            self.emotion_visualizer.update_emotions(emotions)
            
        except Exception as e:
            logger.error(f"Error updating emotions: {e}")
            
    def update_status(self, status, event=None):
        """Update UI status and trigger appropriate animations"""
        # Update avatar emotion based on status
        if "error" in status.lower():
            self.avatar.set_emotion("sad")
        elif "detected" in status.lower():
            self.avatar.set_emotion("happy")
        elif "responding" in status.lower():
            self.avatar.set_emotion("thinking")
        else:
            self.avatar.set_emotion("neutral")
            
    def closeEvent(self, event):
        """Handle window close event"""
        # Stop sync timer
        self.sync_timer.stop()
        
        # Close cloud sync
        asyncio.create_task(self.cloud_sync.close())
        
        # Clean up other resources
        self.emotion_detector.stop()
        self.speech_to_text.stop()
        self.text_to_speech.stop()
        
        event.accept()

def run_ui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 