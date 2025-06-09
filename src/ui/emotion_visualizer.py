import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath, QLinearGradient
import numpy as np
import math
import random

class EmotionVisualizer(QWidget):
    emotion_updated = pyqtSignal(dict)  # Signal to notify parent of emotion changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 200)
        
        # Initialize emotion states
        self.emotions = {
            'happy': 0.0,
            'sad': 0.0,
            'angry': 0.0,
            'neutral': 0.0,
            'fear': 0.0,
            'surprise': 0.0,
            'disgust': 0.0
        }
        
        # Animation properties
        self.target_emotions = self.emotions.copy()
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.animate_values)
        self.animation_timer.start(16)  # ~60 FPS
        
        self.wave_phase = 0
        self.wave_timer = QTimer(self)
        self.wave_timer.timeout.connect(self.update_wave)
        self.wave_timer.start(50)  # 20 FPS for wave animation
        
        self.particle_system = []
        self.particle_timer = QTimer(self)
        self.particle_timer.timeout.connect(self.update_particles)
        self.particle_timer.start(16)  # ~60 FPS for particles
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Emotion bars
        self.emotion_bars = {}
        for emotion in self.emotions:
            container = QWidget()
            bar_layout = QVBoxLayout(container)
            
            label = QLabel(emotion.capitalize())
            label.setStyleSheet("color: white;")
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setTextVisible(False)
            bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 2px solid #2c3e50;
                    border-radius: 5px;
                    background-color: #34495e;
                    height: 20px;
                }}
                QProgressBar::chunk {{
                    background-color: {self.get_emotion_color(emotion)};
                    border-radius: 3px;
                }}
            """)
            
            bar_layout.addWidget(label)
            bar_layout.addWidget(bar)
            layout.addWidget(container)
            
            self.emotion_bars[emotion] = bar
            
        # Set background color
        self.setStyleSheet("background-color: #1E1E1E;")
        
    def get_emotion_color(self, emotion):
        colors = {
            'happy': '#f1c40f',    # Yellow
            'sad': '#3498db',      # Blue
            'angry': '#e74c3c',    # Red
            'neutral': '#95a5a6',  # Gray
            'fear': '#9b59b6',     # Purple
            'surprise': '#e67e22', # Orange
            'disgust': '#27ae60'   # Green
        }
        return colors.get(emotion, '#95a5a6')
        
    def update_emotions(self, new_emotions):
        """Update target emotion values"""
        self.target_emotions = new_emotions.copy()
        
    def animate_values(self):
        """Animate emotion values smoothly"""
        changed = False
        for emotion in self.emotions:
            current = self.emotions[emotion]
            target = self.target_emotions[emotion]
            
            # Smooth interpolation
            if abs(current - target) > 0.001:
                self.emotions[emotion] += (target - current) * 0.1
                changed = True
                
                # Update progress bar
                self.emotion_bars[emotion].setValue(int(self.emotions[emotion] * 100))
                
        if changed:
            self.emotion_updated.emit(self.emotions)
            self.update()
            
    def update_wave(self):
        self.wave_phase += 0.1
        self.update()
        
    def update_particles(self):
        # Update existing particles
        for particle in self.particle_system[:]:
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particle_system.remove(particle)
                continue
                
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.1  # Gravity
            
        # Add new particles based on dominant emotion
        if random.random() < 0.3:  # 30% chance each frame
            dominant_emotion = self.get_dominant_emotion()
            if self.emotions[dominant_emotion] > 0.3:
                self.add_particle(dominant_emotion)
                
        self.update()
        
    def add_particle(self, emotion):
        x = random.randint(0, self.width())
        y = self.height()
        vx = random.uniform(-2, 2)
        vy = random.uniform(-5, -2)
        size = random.uniform(2, 6)
        life = random.randint(30, 60)
        color = QColor(self.get_emotion_color(emotion))
        
        self.particle_system.append({
            'x': x, 'y': y, 'vx': vx, 'vy': vy,
            'size': size, 'life': life, 'color': color
        })
        
    def paintEvent(self, event):
        """Custom painting for additional visualizations"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw wave visualization
        if self.get_emotional_intensity() > 0.1:
            self.draw_wave(painter)
            
        # Draw particles
        self.draw_particles(painter)
        
    def draw_wave(self, painter):
        dominant_emotion = self.get_dominant_emotion()
        intensity = self.get_emotional_intensity()
        
        # Create gradient for wave
        gradient = QLinearGradient(0, 0, 0, self.height())
        color = QColor(self.get_emotion_color(dominant_emotion))
        color.setAlpha(int(100 * intensity))
        gradient.setColorAt(0, color)
        gradient.setColorAt(1, QColor(0, 0, 0, 0))
        
        # Draw wave path
        path = QPainterPath()
        path.moveTo(0, self.height())
        
        for x in range(0, self.width() + 1, 5):
            y = self.height() - 50
            y += math.sin(x * 0.02 + self.wave_phase) * 20 * intensity
            y += math.sin(x * 0.01 - self.wave_phase * 0.5) * 10 * intensity
            path.lineTo(x, y)
            
        path.lineTo(self.width(), self.height())
        path.lineTo(0, self.height())
        
        painter.fillPath(path, gradient)
        
    def draw_particles(self, painter):
        for particle in self.particle_system:
            color = particle['color']
            alpha = int(255 * (particle['life'] / 60))
            color.setAlpha(alpha)
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(color))
            painter.drawEllipse(
                particle['x'] - particle['size']/2,
                particle['y'] - particle['size']/2,
                particle['size'],
                particle['size']
            )
        
    def get_dominant_emotion(self):
        """Get the current dominant emotion"""
        return max(self.emotions.items(), key=lambda x: x[1])[0]
        
    def get_emotional_intensity(self):
        """Get the overall emotional intensity"""
        return max(self.emotions.values()) 