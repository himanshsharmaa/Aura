import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import json
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QLabel, QPushButton, QFrame, QSplitter,
                            QComboBox, QProgressBar, QMessageBox, QFileDialog)
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
    def __init__(self, hotword_detector, alarm_system):
        super().__init__()
        self.logger = setup_logger(__name__)
        self.hotword_detector = hotword_detector
        self.alarm_system = alarm_system
        self.init_ui()
        
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
        
        # Start cloud sync
        asyncio.create_task(self.cloud_sync.initialize())
        
    def init_ui(self):
        """Initialize the user interface"""
        try:
            self.setWindowTitle('Aura - Voice Assistant')
            self.setGeometry(100, 100, 800, 600)
            
            # Create central widget and layout
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            
            # Status section
            status_layout = QHBoxLayout()
            self.status_label = QLabel('Status: Ready')
            self.status_label.setFont(QFont('Arial', 12))
            status_layout.addWidget(self.status_label)
            layout.addLayout(status_layout)
            
            # Confidence visualization
            self.confidence_bar = QProgressBar()
            self.confidence_bar.setRange(0, 100)
            self.confidence_bar.setValue(0)
            layout.addWidget(self.confidence_bar)
            
            # Control buttons
            button_layout = QHBoxLayout()
            
            self.start_button = QPushButton('Start Listening')
            self.start_button.clicked.connect(self.start_listening)
            button_layout.addWidget(self.start_button)
            
            self.stop_button = QPushButton('Stop Listening')
            self.stop_button.clicked.connect(self.stop_listening)
            self.stop_button.setEnabled(False)
            button_layout.addWidget(self.stop_button)
            
            layout.addLayout(button_layout)
            
            # Training section
            training_layout = QHBoxLayout()
            
            self.collect_positive_button = QPushButton('Collect Positive Samples')
            self.collect_positive_button.clicked.connect(
                lambda: self.start_collecting_samples('positive')
            )
            training_layout.addWidget(self.collect_positive_button)
            
            self.collect_negative_button = QPushButton('Collect Negative Samples')
            self.collect_negative_button.clicked.connect(
                lambda: self.start_collecting_samples('negative')
            )
            training_layout.addWidget(self.collect_negative_button)
            
            self.train_button = QPushButton('Train Model')
            self.train_button.clicked.connect(self.train_model)
            training_layout.addWidget(self.train_button)
            
            layout.addLayout(training_layout)
            
            # Set up visualization callback
            self.hotword_detector.set_visualization_callback(self.update_confidence)
            
            self.logger.info("UI initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing UI: {e}")
            QMessageBox.critical(self, "Error", f"Failed to initialize UI: {e}")
    
    def start_listening(self):
        """Start listening for hotword"""
        try:
            self.hotword_detector.start_listening(self.on_hotword_detected)
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.status_label.setText('Status: Listening...')
            self.logger.info("Started listening")
        except Exception as e:
            self.logger.error(f"Error starting listener: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start listening: {e}")
    
    def stop_listening(self):
        """Stop listening for hotword"""
        try:
            self.hotword_detector.stop_listening()
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.status_label.setText('Status: Ready')
            self.logger.info("Stopped listening")
        except Exception as e:
            self.logger.error(f"Error stopping listener: {e}")
            QMessageBox.critical(self, "Error", f"Failed to stop listening: {e}")
    
    def on_hotword_detected(self):
        """Callback for hotword detection"""
        try:
            self.status_label.setText('Status: Hotword Detected!')
            QTimer.singleShot(2000, lambda: self.status_label.setText('Status: Listening...'))
            self.logger.info("Hotword detected")
        except Exception as e:
            self.logger.error(f"Error in hotword detection callback: {e}")
    
    def update_confidence(self, confidence, history):
        """Update confidence visualization"""
        try:
            self.confidence_bar.setValue(int(confidence * 100))
        except Exception as e:
            self.logger.error(f"Error updating confidence: {e}")
    
    def start_collecting_samples(self, sample_type):
        """Start collecting training samples"""
        try:
            if self.hotword_detector.start_collecting_samples(sample_type):
                self.status_label.setText(f'Status: Collecting {sample_type} samples...')
                self.logger.info(f"Started collecting {sample_type} samples")
        except Exception as e:
            self.logger.error(f"Error starting sample collection: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start sample collection: {e}")
    
    def train_model(self):
        """Train the hotword detection model"""
        try:
            self.status_label.setText('Status: Training model...')
            if self.hotword_detector.train_model([], []):  # Add your samples here
                self.status_label.setText('Status: Model trained successfully')
                self.logger.info("Model training completed")
            else:
                self.status_label.setText('Status: Model training failed')
                self.logger.error("Model training failed")
        except Exception as e:
            self.logger.error(f"Error training model: {e}")
            QMessageBox.critical(self, "Error", f"Failed to train model: {e}")
    
    def closeEvent(self, event):
        """Handle window close event"""
        try:
            self.hotword_detector.stop_listening()
            self.alarm_system.stop()
            self.logger.info("Application closed")
            
            # Stop sync timer
            self.sync_timer.stop()
            
            # Close cloud sync
            asyncio.create_task(self.cloud_sync.close())
            
            # Clean up other resources
            self.emotion_detector.stop()
            self.speech_to_text.stop()
            self.text_to_speech.stop()
            
            event.accept()
        except Exception as e:
            self.logger.error(f"Error closing application: {e}")
            event.accept()

def run_ui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 