import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QRect
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath, QFont, QBrush, QLinearGradient
import numpy as np
import math

class Eye:
    def __init__(self, parent, x, y, radius):
        self.parent = parent
        self.x = x
        self.y = y
        self.radius = radius
        self.pupil_radius = radius * 0.4
        self.pupil_x = x
        self.pupil_y = y
        self.target_x = x
        self.target_y = y
        self.blink_state = 0  # 0: open, 1: closing, 2: closed, 3: opening
        self.blink_progress = 0
        self.emotion = "neutral"
        
    def update(self, mouse_pos=None, emotion=None):
        if emotion:
            self.emotion = emotion
            
        # Update blink animation
        if self.blink_state > 0:
            self.blink_progress += 0.1
            if self.blink_progress >= 1:
                self.blink_state = (self.blink_state + 1) % 4
                self.blink_progress = 0
                
        # Update pupil position based on mouse or emotion
        if mouse_pos:
            # Calculate direction to mouse
            dx = mouse_pos.x() - self.x
            dy = mouse_pos.y() - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Limit pupil movement
            max_distance = self.radius - self.pupil_radius
            if distance > max_distance:
                dx = dx * max_distance / distance
                dy = dy * max_distance / distance
                
            self.target_x = self.x + dx
            self.target_y = self.y + dy
            
        # Smooth pupil movement
        self.pupil_x += (self.target_x - self.pupil_x) * 0.1
        self.pupil_y += (self.target_y - self.pupil_y) * 0.1
        
    def draw(self, painter):
        # Draw eye socket
        socket_color = QColor(50, 50, 50)
        painter.setPen(QPen(socket_color, 2))
        painter.setBrush(QBrush(socket_color))
        painter.drawEllipse(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)
        
        # Draw eye white
        if self.blink_state == 0:  # Open
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(self.x - self.radius * 0.9, self.y - self.radius * 0.9,
                              self.radius * 1.8, self.radius * 1.8)
            
            # Draw pupil
            pupil_color = QColor(0, 0, 0)
            if self.emotion == "happy":
                pupil_color = QColor(255, 215, 0)  # Gold
            elif self.emotion == "sad":
                pupil_color = QColor(100, 149, 237)  # Cornflower blue
            elif self.emotion == "angry":
                pupil_color = QColor(220, 20, 60)  # Crimson
                
            painter.setBrush(QBrush(pupil_color))
            painter.drawEllipse(self.pupil_x - self.pupil_radius,
                              self.pupil_y - self.pupil_radius,
                              self.pupil_radius * 2, self.pupil_radius * 2)
            
            # Draw highlight
            highlight_radius = self.pupil_radius * 0.3
            painter.setBrush(QBrush(QColor(255, 255, 255, 180)))
            painter.drawEllipse(self.pupil_x - highlight_radius,
                              self.pupil_y - highlight_radius,
                              highlight_radius * 2, highlight_radius * 2)
        else:  # Blinking
            progress = self.blink_progress
            if self.blink_state == 1:  # Closing
                height = self.radius * 2 * (1 - progress)
            else:  # Opening
                height = self.radius * 2 * progress
                
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(50, 50, 50)))
            painter.drawEllipse(self.x - self.radius,
                              self.y - height/2,
                              self.radius * 2, height)

class Avatar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 400)
        
        # Create eyes
        self.left_eye = Eye(self, 150, 150, 30)
        self.right_eye = Eye(self, 250, 150, 30)
        
        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16)  # ~60fps
        
        # Blink timer
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.trigger_blink)
        self.blink_timer.start(3000)  # Blink every 3 seconds
        
        # Emotion state
        self.current_emotion = "neutral"
        self.emotion_intensity = 0.0
        
        # Mouth animation
        self.mouth_openness = 0.0
        self.target_mouth_openness = 0.0
        
    def trigger_blink(self):
        if self.left_eye.blink_state == 0 and self.right_eye.blink_state == 0:
            self.left_eye.blink_state = 1
            self.right_eye.blink_state = 1
            
    def update_emotion(self, emotion, intensity=1.0):
        self.current_emotion = emotion
        self.emotion_intensity = intensity
        self.left_eye.emotion = emotion
        self.right_eye.emotion = emotion
        
    def update_mouth(self, openness):
        self.target_mouth_openness = openness
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Update mouth animation
        self.mouth_openness += (self.target_mouth_openness - self.mouth_openness) * 0.1
        
        # Draw face
        self.draw_face(painter)
        
        # Update and draw eyes
        mouse_pos = self.mapFromGlobal(self.cursor().pos())
        self.left_eye.update(mouse_pos, self.current_emotion)
        self.right_eye.update(mouse_pos, self.current_emotion)
        self.left_eye.draw(painter)
        self.right_eye.draw(painter)
        
        # Draw mouth
        self.draw_mouth(painter)
        
    def draw_face(self, painter):
        # Create gradient for face
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(70, 70, 70))
        gradient.setColorAt(1, QColor(50, 50, 50))
        
        # Draw face shape
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        
        # Draw face based on emotion
        if self.current_emotion == "happy":
            # Happy face shape
            path = QPainterPath()
            path.moveTo(100, 100)
            path.quadTo(200, 50, 300, 100)
            path.quadTo(350, 200, 300, 300)
            path.quadTo(200, 350, 100, 300)
            path.quadTo(50, 200, 100, 100)
            painter.drawPath(path)
        elif self.current_emotion == "sad":
            # Sad face shape
            path = QPainterPath()
            path.moveTo(100, 150)
            path.quadTo(200, 100, 300, 150)
            path.quadTo(350, 250, 300, 350)
            path.quadTo(200, 400, 100, 350)
            path.quadTo(50, 250, 100, 150)
            painter.drawPath(path)
        else:
            # Neutral face shape
            painter.drawEllipse(50, 50, 300, 300)
            
    def draw_mouth(self, painter):
        center_x = self.width() / 2
        center_y = 250
        
        if self.current_emotion == "happy":
            # Happy mouth
            path = QPainterPath()
            path.moveTo(center_x - 50, center_y)
            path.quadTo(center_x, center_y - 50 * self.mouth_openness,
                       center_x + 50, center_y)
            painter.setPen(QPen(QColor(255, 255, 255), 3))
            painter.drawPath(path)
        elif self.current_emotion == "sad":
            # Sad mouth
            path = QPainterPath()
            path.moveTo(center_x - 50, center_y)
            path.quadTo(center_x, center_y + 50 * self.mouth_openness,
                       center_x + 50, center_y)
            painter.setPen(QPen(QColor(255, 255, 255), 3))
            painter.drawPath(path)
        else:
            # Neutral mouth
            width = 100 * self.mouth_openness
            painter.setPen(QPen(QColor(255, 255, 255), 3))
            painter.drawLine(center_x - width/2, center_y,
                           center_x + width/2, center_y) 