import sys
import json
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QLabel, QPushButton, QFrame, QSplitter)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import (QPainter, QColor, QPen, QPainterPath, QFont, 
                        QBrush, QLinearGradient, QRadialGradient)
import pyqtgraph as pg
import sounddevice as sd
from .avatar import Avatar

# Import core modules
from ai.emotion import EmotionDetector
from ai.stt import SpeechToText
from ai.tts import TextToSpeech
from ai.nlp import Llama2
from ai.personality import Personality
from utils.logger import setup_logger

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
        self.setWindowTitle("Aura AI Companion")
        self.setMinimumSize(1200, 800)
        
        # Load config
        with open('config.json', 'r') as f:
            self.config = json.load(f)
            
        # Set up main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Create splitter for resizable sections
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel (Avatar and Status)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Add avatar
        self.avatar = Avatar()
        left_layout.addWidget(self.avatar)
        
        # Add status widget
        self.status = StatusWidget()
        left_layout.addWidget(self.status)
        
        # Add control buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #7B68EE;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #9370DB;
            }
        """)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #DC143C;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #B22222;
            }
        """)
        button_layout.addWidget(self.stop_button)
        
        left_layout.addLayout(button_layout)
        
        # Right panel (Visualization)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Add visualization
        self.visualization = VisualizationWidget()
        right_layout.addWidget(self.visualization)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([600, 600])  # Initial sizes
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
            }
            QWidget {
                background-color: #1E1E1E;
            }
            QSplitter::handle {
                background-color: #7B68EE;
            }
        """)
        
        # Connect signals
        self.start_button.clicked.connect(self.start_aura)
        self.stop_button.clicked.connect(self.stop_aura)
        
        # Initialize state
        self.stop_button.setEnabled(False)
        
    def start_aura(self):
        self.status.update_status("Aura is active")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.avatar.update_emotion("happy", 0.5)
        
    def stop_aura(self):
        self.status.update_status("Aura is inactive")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.avatar.update_emotion("sad", 0.3)
        
    def update_status(self, status, event=None):
        self.status.update_status(status, event)
        
        # Update avatar emotion based on status
        if "error" in status.lower():
            self.avatar.update_emotion("sad", 0.8)
        elif "detected" in status.lower():
            self.avatar.update_emotion("happy", 0.6)
        elif "responding" in status.lower():
            self.avatar.update_mouth(0.7)  # Open mouth while speaking
        else:
            self.avatar.update_emotion("neutral", 0.5)
            self.avatar.update_mouth(0.0)  # Close mouth when not speaking

def run_ui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 