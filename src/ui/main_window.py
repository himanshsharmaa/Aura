import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QPushButton, QTextEdit, QStatusBar, QHBoxLayout,
    QTabWidget, QSlider, QGroupBox, QFormLayout, QSplitter
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
import cv2
import numpy as np
from datetime import datetime
import json
import pyqtgraph as pg
import sounddevice as sd

from utils.logger import setup_logger
from src.core.personality import Personality
from src.core.proactive import ProactiveBehavior
from src.ui.emotion_visualizer import EmotionVisualizer
from src.core.emotion_detector import EmotionDetector
from src.core.stt import SpeechToText
from src.core.tts import TextToSpeech
from src.core.nlp import NLPProcessor
from src.core.memory import MemoryManager
from src.ui.settings_panel import SettingsPanel

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

class AuraWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aura - Your AI Companion")
        self.setMinimumSize(1200, 800)
        
        # Initialize components
        self.personality = Personality()
        self.proactive = ProactiveBehavior(self.personality)
        self.emotion_detector = EmotionDetector()
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.nlp = NLPProcessor()
        self.memory = MemoryManager()
        
        # Initialize camera
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Initialize UI
        self.init_ui()
        
        # Start timers
        self.video_timer = QTimer()
        self.video_timer.timeout.connect(self.update_video)
        self.video_timer.start(30)  # 30ms = ~33 FPS
        
        self.proactive_timer = QTimer()
        self.proactive_timer.timeout.connect(self.check_proactive)
        self.proactive_timer.start(60000)  # Check every minute
        
        self.is_active = False
        
    def init_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create left panel (video and controls)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Video display
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.video_label)
        
        # Status and controls
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Aura is ready")
        self.status_label.setStyleSheet("color: #4CAF50; font-size: 14px;")
        status_layout.addWidget(self.status_label)
        
        self.toggle_button = QPushButton("Start Aura")
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.toggle_button.clicked.connect(self.toggle_aura)
        status_layout.addWidget(self.toggle_button)
        
        left_layout.addLayout(status_layout)
        
        # Create right panel (tabs)
        right_panel = QTabWidget()
        
        # Conversation tab
        conversation_tab = QWidget()
        conversation_layout = QVBoxLayout(conversation_tab)
        
        self.conversation_display = QTextEdit()
        self.conversation_display.setReadOnly(True)
        self.conversation_display.setStyleSheet("""
            QTextEdit {
                background-color: #2C2C2C;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        conversation_layout.addWidget(self.conversation_display)
        
        # Emotion visualization tab
        emotion_tab = QWidget()
        emotion_layout = QVBoxLayout(emotion_tab)
        self.emotion_visualizer = EmotionVisualizer()
        self.emotion_visualizer.emotion_updated.connect(self.on_emotion_updated)
        emotion_layout.addWidget(self.emotion_visualizer)
        
        # Personality tab
        personality_tab = QWidget()
        personality_layout = QVBoxLayout(personality_tab)
        
        # Create personality sliders
        for trait, value in self.personality.traits.items():
            group = QGroupBox(trait.capitalize())
            group_layout = QFormLayout(group)
            
            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, 100)
            slider.setValue(int(value * 100))
            slider.valueChanged.connect(
                lambda v, t=trait: self.personality.adjust_trait(t, v / 100)
            )
            
            group_layout.addRow("Value:", slider)
            personality_layout.addWidget(group)
            
        # Settings tab
        self.settings_panel = SettingsPanel()
        self.settings_panel.settings_changed.connect(self.on_settings_changed)
            
        # Add tabs
        right_panel.addTab(conversation_tab, "Conversation")
        right_panel.addTab(emotion_tab, "Emotions")
        right_panel.addTab(personality_tab, "Personality")
        right_panel.addTab(self.settings_panel, "Settings")
        
        # Add panels to main layout
        main_layout.addWidget(left_panel, 2)
        main_layout.addWidget(right_panel, 1)
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
            }
            QWidget {
                background-color: #1E1E1E;
                color: white;
            }
            QTabWidget::pane {
                border: 1px solid #3C3C3C;
                background-color: #1E1E1E;
            }
            QTabBar::tab {
                background-color: #2C2C2C;
                color: white;
                padding: 8px 16px;
                border: 1px solid #3C3C3C;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #3C3C3C;
            }
            QGroupBox {
                border: 1px solid #3C3C3C;
                border-radius: 5px;
                margin-top: 1em;
                padding-top: 1em;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
        """)
        
    def toggle_aura(self):
        self.is_active = not self.is_active
        if self.is_active:
            self.toggle_button.setText("Stop Aura")
            self.status_label.setText("Aura is active")
            self.status_label.setStyleSheet("color: #4CAF50; font-size: 14px;")
            self.start_aura()
        else:
            self.toggle_button.setText("Start Aura")
            self.status_label.setText("Aura is inactive")
            self.status_label.setStyleSheet("color: #f44336; font-size: 14px;")
            self.stop_aura()
            
    def start_aura(self):
        # Initialize components
        self.stt.start()
        self.tts.start()
        
        # Update time of day
        hour = datetime.now().hour
        if 5 <= hour < 12:
            self.proactive.update_context(time_of_day='morning')
        elif 12 <= hour < 17:
            self.proactive.update_context(time_of_day='afternoon')
        else:
            self.proactive.update_context(time_of_day='evening')
            
    def stop_aura(self):
        # Clean up components
        self.stt.stop()
        self.tts.stop()
        
    def update_video(self):
        ret, frame = self.camera.read()
        if ret:
            # Detect emotions
            emotions = self.emotion_detector.detect_emotions(frame)
            self.emotion_visualizer.update_emotions(emotions)
            
            # Update proactive context
            dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0]
            self.proactive.update_context(user_emotion=dominant_emotion)
            
            # Convert frame to QImage
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # Scale and display
            scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
                self.video_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.video_label.setPixmap(scaled_pixmap)
            
    def check_proactive(self):
        if self.is_active:
            response = self.proactive.get_proactive_response()
            if response:
                self.add_to_conversation("Aura", response)
                self.tts.speak(response)
                
    def on_emotion_updated(self, emotions):
        if self.is_active:
            dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0]
            if emotions[dominant_emotion] > 0.7:  # Strong emotion detected
                response = self.personality.get_emotional_response(dominant_emotion)
                self.add_to_conversation("Aura", response)
                self.tts.speak(response)
                
    def add_to_conversation(self, speaker: str, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.conversation_display.append(f"[{timestamp}] {speaker}: {message}")
        
    def on_settings_changed(self, settings):
        """Handle settings changes"""
        # Update appearance
        if settings['appearance']['theme'] == "Dark":
            self.set_dark_theme()
        elif settings['appearance']['theme'] == "Light":
            self.set_light_theme()
        else:
            # System theme
            pass
            
        # Update behavior
        self.proactive_timer.setInterval(settings['behavior']['interaction_frequency'] * 60000)
        self.tts.set_voice(settings['behavior']['voice'])
        self.tts.set_rate(settings['behavior']['speech_rate'])
        
        # Update privacy
        self.memory.set_data_collection(settings['privacy']['data_collection'])
        self.memory.set_save_history(settings['privacy']['save_history'])
        self.memory.set_data_location(settings['privacy']['data_location'])
        
    def set_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
            }
            QWidget {
                background-color: #1E1E1E;
                color: white;
            }
            QTabWidget::pane {
                border: 1px solid #3C3C3C;
                background-color: #1E1E1E;
            }
            QTabBar::tab {
                background-color: #2C2C2C;
                color: white;
                padding: 8px 16px;
                border: 1px solid #3C3C3C;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #3C3C3C;
            }
            QGroupBox {
                border: 1px solid #3C3C3C;
                border-radius: 5px;
                margin-top: 1em;
                padding-top: 1em;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
        """)
        
    def set_light_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFFFF;
            }
            QWidget {
                background-color: #FFFFFF;
                color: black;
            }
            QTabWidget::pane {
                border: 1px solid #CCCCCC;
                background-color: #FFFFFF;
            }
            QTabBar::tab {
                background-color: #F0F0F0;
                color: black;
                padding: 8px 16px;
                border: 1px solid #CCCCCC;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #FFFFFF;
            }
            QGroupBox {
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                margin-top: 1em;
                padding-top: 1em;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
        """)
        
    def closeEvent(self, event):
        # Clean up
        self.camera.release()
        self.stt.stop()
        self.tts.stop()
        
        # Save states
        self.personality.save_state("data/personality.json")
        self.proactive.save_state("data/proactive.json")
        self.memory.save_state("data/memory.json")
        
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = AuraWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 