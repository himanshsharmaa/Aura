import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QRect, QParallelAnimationGroup, QSequentialAnimationGroup
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath, QFont, QBrush, QLinearGradient, QRadialGradient
import numpy as np
import math
import random
from typing import Dict, Any

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
        self.eye_rotation = 0
        self.eye_scale = 1.0
        self.eye_color = QColor(255, 255, 255)
        self.pupil_color = QColor(0, 0, 0)
        self.highlight_color = QColor(255, 255, 255, 180)
        
    def update(self, mouse_pos=None, emotion=None, processing_level=0.0):
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
        
        # Update eye appearance based on emotion and processing
        self.update_eye_appearance(processing_level)
        
    def update_eye_appearance(self, processing_level):
        # Update eye colors based on emotion and processing level
        if self.emotion == "happy":
            self.eye_color = QColor(255, 255, 200)  # Warm white
            self.pupil_color = QColor(255, 215, 0)  # Gold
        elif self.emotion == "sad":
            self.eye_color = QColor(200, 200, 255)  # Cool white
            self.pupil_color = QColor(100, 149, 237)  # Cornflower blue
        elif self.emotion == "angry":
            self.eye_color = QColor(255, 200, 200)  # Red-tinted white
            self.pupil_color = QColor(220, 20, 60)  # Crimson
        elif self.emotion == "thinking":
            self.eye_color = QColor(200, 255, 200)  # Green-tinted white
            self.pupil_color = QColor(50, 205, 50)  # Lime green
        elif self.emotion == "surprised":
            self.eye_color = QColor(255, 255, 255)  # Pure white
            self.pupil_color = QColor(0, 0, 0)  # Black
        else:  # neutral
            self.eye_color = QColor(255, 255, 255)  # White
            self.pupil_color = QColor(0, 0, 0)  # Black
            
        # Add processing effect
        if processing_level > 0:
            # Add a subtle glow effect
            self.eye_color.setAlpha(int(255 * (1 + processing_level * 0.2)))
            # Add a subtle rotation
            self.eye_rotation = math.sin(processing_level * 10) * 5
            # Add a subtle scale
            self.eye_scale = 1.0 + processing_level * 0.1
        
    def draw(self, painter):
        # Save painter state
        painter.save()
        
        # Apply transformations
        painter.translate(self.x, self.y)
        painter.rotate(self.eye_rotation)
        painter.scale(self.eye_scale, self.eye_scale)
        painter.translate(-self.x, -self.y)
        
        # Draw eye socket with gradient
        socket_gradient = QRadialGradient(self.x, self.y, self.radius * 1.2)
        socket_gradient.setColorAt(0, QColor(70, 70, 70))
        socket_gradient.setColorAt(1, QColor(50, 50, 50))
        painter.setPen(QPen(socket_gradient, 2))
        painter.setBrush(QBrush(socket_gradient))
        painter.drawEllipse(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)
        
        # Draw eye white
        if self.blink_state == 0:  # Open
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(self.eye_color))
            painter.drawEllipse(self.x - self.radius * 0.9, self.y - self.radius * 0.9,
                              self.radius * 1.8, self.radius * 1.8)
            
            # Draw pupil
            painter.setBrush(QBrush(self.pupil_color))
            painter.drawEllipse(self.pupil_x - self.pupil_radius,
                              self.pupil_y - self.pupil_radius,
                              self.pupil_radius * 2, self.pupil_radius * 2)
            
            # Draw highlight
            highlight_radius = self.pupil_radius * 0.3
            painter.setBrush(QBrush(self.highlight_color))
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
                              
        # Restore painter state
        painter.restore()

class Avatar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 400)
        
        # Create eyes
        self.left_eye = Eye(self, 150, 150, 30)
        self.right_eye = Eye(self, 250, 150, 30)
        
        # Animation timers
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16)  # ~60fps
        
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.trigger_blink)
        self.blink_timer.start(3000)  # Blink every 3 seconds
        
        # Emotion state
        self.current_emotion = "neutral"
        self.emotion_intensity = 0.0
        self.processing_level = 0.0
        self.target_processing_level = 0.0
        
        # Mouth animation
        self.mouth_openness = 0.0
        self.target_mouth_openness = 0.0
        self.mouth_shape = "neutral"
        
        # Face features
        self.eyebrow_height = 0
        self.target_eyebrow_height = 0
        self.face_rotation = 0
        self.target_face_rotation = 0
        
        # Animation groups
        self.animation_group = QParallelAnimationGroup()
        self.setup_animations()
        
    def setup_animations(self):
        # Create animations for different features
        self.eyebrow_animation = QPropertyAnimation(self, b"eyebrow_height")
        self.eyebrow_animation.setDuration(300)
        self.eyebrow_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.face_rotation_animation = QPropertyAnimation(self, b"face_rotation")
        self.face_rotation_animation.setDuration(500)
        self.face_rotation_animation.setEasingCurve(QEasingCurve.Type.OutElastic)
        
        self.animation_group.addAnimation(self.eyebrow_animation)
        self.animation_group.addAnimation(self.face_rotation_animation)
        
    def trigger_blink(self):
        if self.left_eye.blink_state == 0 and self.right_eye.blink_state == 0:
            self.left_eye.blink_state = 1
            self.right_eye.blink_state = 1
            
    def update_emotion(self, emotion, intensity=1.0):
        self.current_emotion = emotion
        self.emotion_intensity = intensity
        self.left_eye.emotion = emotion
        self.right_eye.emotion = emotion
        
        # Update facial features based on emotion
        if emotion == "happy":
            self.target_eyebrow_height = -20
            self.target_face_rotation = 5
            self.mouth_shape = "smile"
        elif emotion == "sad":
            self.target_eyebrow_height = 20
            self.target_face_rotation = -5
            self.mouth_shape = "frown"
        elif emotion == "angry":
            self.target_eyebrow_height = -30
            self.target_face_rotation = 0
            self.mouth_shape = "angry"
        elif emotion == "thinking":
            self.target_eyebrow_height = 10
            self.target_face_rotation = 0
            self.mouth_shape = "neutral"
        elif emotion == "surprised":
            self.target_eyebrow_height = -40
            self.target_face_rotation = 0
            self.mouth_shape = "o"
        else:  # neutral
            self.target_eyebrow_height = 0
            self.target_face_rotation = 0
            self.mouth_shape = "neutral"
            
        # Start animations
        self.eyebrow_animation.setStartValue(self.eyebrow_height)
        self.eyebrow_animation.setEndValue(self.target_eyebrow_height)
        self.face_rotation_animation.setStartValue(self.face_rotation)
        self.face_rotation_animation.setEndValue(self.target_face_rotation)
        self.animation_group.start()
        
    def update_processing(self, level):
        self.target_processing_level = level
        
    def update_mouth(self, openness):
        self.target_mouth_openness = openness
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Update processing level
        self.processing_level += (self.target_processing_level - self.processing_level) * 0.1
        
        # Update mouth animation
        self.mouth_openness += (self.target_mouth_openness - self.mouth_openness) * 0.1
        
        # Save painter state
        painter.save()
        
        # Apply face rotation
        painter.translate(self.width()/2, self.height()/2)
        painter.rotate(self.face_rotation)
        painter.translate(-self.width()/2, -self.height()/2)
        
        # Draw face
        self.draw_face(painter)
        
        # Update and draw eyes
        mouse_pos = self.mapFromGlobal(self.cursor().pos())
        self.left_eye.update(mouse_pos, self.current_emotion, self.processing_level)
        self.right_eye.update(mouse_pos, self.current_emotion, self.processing_level)
        self.left_eye.draw(painter)
        self.right_eye.draw(painter)
        
        # Draw eyebrows
        self.draw_eyebrows(painter)
        
        # Draw mouth
        self.draw_mouth(painter)
        
        # Restore painter state
        painter.restore()
        
    def draw_face(self, painter):
        # Create gradient for face
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(70, 70, 70))
        gradient.setColorAt(1, QColor(50, 50, 50))
        
        # Add processing glow effect
        if self.processing_level > 0:
            glow = QRadialGradient(self.width()/2, self.height()/2, 200)
            glow.setColorAt(0, QColor(100, 100, 255, int(50 * self.processing_level)))
            glow.setColorAt(1, QColor(100, 100, 255, 0))
            painter.setBrush(QBrush(glow))
            painter.drawEllipse(0, 0, self.width(), self.height())
        
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
        elif self.current_emotion == "angry":
            # Angry face shape
            path = QPainterPath()
            path.moveTo(100, 120)
            path.quadTo(200, 80, 300, 120)
            path.quadTo(350, 200, 300, 280)
            path.quadTo(200, 320, 100, 280)
            path.quadTo(50, 200, 100, 120)
            painter.drawPath(path)
        elif self.current_emotion == "thinking":
            # Thinking face shape
            path = QPainterPath()
            path.moveTo(100, 130)
            path.quadTo(200, 100, 300, 130)
            path.quadTo(350, 200, 300, 270)
            path.quadTo(200, 300, 100, 270)
            path.quadTo(50, 200, 100, 130)
            painter.drawPath(path)
        elif self.current_emotion == "surprised":
            # Surprised face shape
            path = QPainterPath()
            path.moveTo(100, 110)
            path.quadTo(200, 60, 300, 110)
            path.quadTo(350, 200, 300, 290)
            path.quadTo(200, 340, 100, 290)
            path.quadTo(50, 200, 100, 110)
            painter.drawPath(path)
        else:
            # Neutral face shape
            painter.drawEllipse(50, 50, 300, 300)
            
    def draw_eyebrows(self, painter):
        # Draw left eyebrow
        left_eyebrow = QPainterPath()
        left_eyebrow.moveTo(100, 100 + self.eyebrow_height)
        left_eyebrow.quadTo(150, 90 + self.eyebrow_height, 200, 100 + self.eyebrow_height)
        painter.setPen(QPen(QColor(50, 50, 50), 3))
        painter.drawPath(left_eyebrow)
        
        # Draw right eyebrow
        right_eyebrow = QPainterPath()
        right_eyebrow.moveTo(200, 100 + self.eyebrow_height)
        right_eyebrow.quadTo(250, 90 + self.eyebrow_height, 300, 100 + self.eyebrow_height)
        painter.drawPath(right_eyebrow)
            
    def draw_mouth(self, painter):
        center_x = self.width() / 2
        center_y = 250
        
        if self.mouth_shape == "smile":
            # Happy mouth
            path = QPainterPath()
            path.moveTo(center_x - 50, center_y)
            path.quadTo(center_x, center_y - 50 * self.mouth_openness,
                       center_x + 50, center_y)
            painter.setPen(QPen(QColor(255, 255, 255), 3))
            painter.drawPath(path)
        elif self.mouth_shape == "frown":
            # Sad mouth
            path = QPainterPath()
            path.moveTo(center_x - 50, center_y)
            path.quadTo(center_x, center_y + 50 * self.mouth_openness,
                       center_x + 50, center_y)
            painter.setPen(QPen(QColor(255, 255, 255), 3))
            painter.drawPath(path)
        elif self.mouth_shape == "angry":
            # Angry mouth
            path = QPainterPath()
            path.moveTo(center_x - 40, center_y)
            path.lineTo(center_x + 40, center_y)
            painter.setPen(QPen(QColor(255, 255, 255), 3))
            painter.drawPath(path)
        elif self.mouth_shape == "o":
            # Surprised mouth
            painter.setPen(QPen(QColor(255, 255, 255), 3))
            painter.drawEllipse(center_x - 30, center_y - 30 * self.mouth_openness,
                              60, 60 * self.mouth_openness)
        else:
            # Neutral mouth
            width = 100 * self.mouth_openness
            painter.setPen(QPen(QColor(255, 255, 255), 3))
            painter.drawLine(center_x - width/2, center_y,
                           center_x + width/2, center_y)

    def learn_from_feedback(self, feedback: Dict[str, Any]):
        """Learn and adapt avatar expressions and micro-expressions from feedback."""
        if 'emotion' in feedback and 'expression' in feedback:
            # Store or adapt new micro-expression for emotion
            if not hasattr(self, 'learned_expressions'):
                self.learned_expressions = {}
            if feedback['emotion'] not in self.learned_expressions:
                self.learned_expressions[feedback['emotion']] = []
            self.learned_expressions[feedback['emotion']].append(feedback['expression'])
        # Optionally, adapt animation parameters
        if 'animation_speed' in feedback:
            self.animation_speed = feedback['animation_speed']
        if 'eye_color' in feedback:
            self.left_eye.eye_color = feedback['eye_color']
            self.right_eye.eye_color = feedback['eye_color']

    def continual_learning(self, feedback: Dict[str, Any]):
        self.learn_from_feedback(feedback) 