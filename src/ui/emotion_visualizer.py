import sys
import numpy as np
import math
import random
import time
import psutil
import os
import platform
import ctypes
from typing import Dict, List, Optional, Tuple, Any
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QApplication
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QSize
from PyQt6.QtGui import (QPainter, QColor, QPen, QPainterPath, QBrush,
                        QLinearGradient, QRadialGradient, QScreen)
import pyqtgraph as pg
import logging
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from collections import deque
import statistics

# Set up logging with file handler
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('emotion_visualizer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Try to import GPUtil, but don't fail if it's not available
try:
    import GPUtil
    HAS_GPU = True
except ImportError:
    HAS_GPU = False
    logger.info("GPUtil not available - GPU monitoring will be disabled")

@dataclass
class EmotionalState:
    current_emotions: Dict[str, float]
    emotional_intensity: float
    emotional_stability: float
    emotional_trend: str
    dominant_emotion: str
    emotional_context: Dict[str, Any]

@dataclass
class SystemMetrics:
    cpu_percent: float
    memory_percent: float
    gpu_memory_percent: Optional[float]
    disk_io_percent: float
    network_io_percent: float
    fps: float
    frame_time: float
    resolution: QSize
    dpi: float

class EmotionalIntelligence:
    def __init__(self):
        self.emotion_history = deque(maxlen=200)
        self.emotional_patterns = {}
        self.context_history = deque(maxlen=100)
        self.learning_rate = 0.1
        self.stability_threshold = 0.2
        self.pattern_recognition_threshold = 0.7
        self.learned_responses = {}
        self.pattern_memory = []
        self.adaptive_weights = {}
        
    def analyze_emotions(self, emotions: Dict[str, float]) -> EmotionalState:
        """Analyze current emotional state and context"""
        self.emotion_history.append(emotions.copy())
        self._learn_patterns(emotions)
        
        # Calculate emotional intensity
        intensity = max(emotions.values())
        
        # Calculate emotional stability
        stability = self._calculate_stability()
        
        # Determine emotional trend
        trend = self._determine_trend()
        
        # Identify dominant emotion
        dominant = max(emotions.items(), key=lambda x: x[1])[0]
        
        # Analyze emotional context
        context = self._analyze_context(emotions)
        
        return EmotionalState(
            current_emotions=emotions,
            emotional_intensity=intensity,
            emotional_stability=stability,
            emotional_trend=trend,
            dominant_emotion=dominant,
            emotional_context=context
        )
        
    def _calculate_stability(self) -> float:
        """Calculate emotional stability based on recent history"""
        if len(self.emotion_history) < 2:
            return 1.0
            
        recent_emotions = list(self.emotion_history)[-10:]
        stability_scores = []
        
        for i in range(1, len(recent_emotions)):
            prev = recent_emotions[i-1]
            curr = recent_emotions[i]
            
            # Calculate change in each emotion
            changes = [abs(curr[e] - prev[e]) for e in prev.keys()]
            stability_scores.append(1 - min(1, sum(changes) / len(changes)))
            
        return statistics.mean(stability_scores) if stability_scores else 1.0
        
    def _determine_trend(self) -> str:
        """Determine the trend in emotional changes"""
        if len(self.emotion_history) < 3:
            return "stable"
            
        recent = list(self.emotion_history)[-3:]
        changes = []
        
        for i in range(1, len(recent)):
            prev = recent[i-1]
            curr = recent[i]
            change = sum(curr[e] - prev[e] for e in prev.keys()) / len(prev)
            changes.append(change)
            
        avg_change = statistics.mean(changes)
        
        if abs(avg_change) < self.stability_threshold:
            return "stable"
        elif avg_change > 0:
            return "increasing"
        else:
            return "decreasing"
            
    def _analyze_context(self, emotions: Dict[str, float]) -> Dict[str, Any]:
        """Analyze emotional context and patterns"""
        context = {
            'emotional_complexity': self._calculate_complexity(emotions),
            'emotional_balance': self._calculate_balance(emotions),
            'pattern_matches': self._find_pattern_matches(emotions),
            'suggested_responses': self._generate_suggested_responses(emotions)
        }
        
        self.context_history.append(context)
        return context
        
    def _calculate_complexity(self, emotions: Dict[str, float]) -> float:
        """Calculate emotional complexity based on distribution"""
        values = list(emotions.values())
        if not values:
            return 0.0
            
        # Normalize values
        total = sum(values)
        if total == 0:
            return 0.0
            
        normalized = [v/total for v in values]
        
        # Calculate entropy as a measure of complexity
        entropy = -sum(p * math.log2(p) if p > 0 else 0 for p in normalized)
        return min(1.0, entropy / math.log2(len(values)))
        
    def _calculate_balance(self, emotions: Dict[str, float]) -> float:
        """Calculate emotional balance"""
        values = list(emotions.values())
        if not values:
            return 1.0
            
        # Calculate how evenly distributed the emotions are
        mean = statistics.mean(values)
        variance = statistics.variance(values) if len(values) > 1 else 0
        return 1 - min(1, variance / (mean + 1e-6))
        
    def _find_pattern_matches(self, emotions: Dict[str, float]) -> List[Dict[str, Any]]:
        """Find matching emotional patterns in history"""
        matches = []
        if len(self.emotion_history) < 2:
            return matches
            
        current_pattern = self._extract_pattern(emotions)
        
        for i, hist_emotions in enumerate(self.emotion_history):
            if i == len(self.emotion_history) - 1:
                continue
                
            hist_pattern = self._extract_pattern(hist_emotions)
            similarity = self._calculate_pattern_similarity(current_pattern, hist_pattern)
            
            if similarity > self.pattern_recognition_threshold:
                matches.append({
                    'similarity': similarity,
                    'index': i,
                    'context': self.context_history[i] if i < len(self.context_history) else None
                })
                
        return sorted(matches, key=lambda x: x['similarity'], reverse=True)
        
    def _extract_pattern(self, emotions: Dict[str, float]) -> Dict[str, float]:
        """Extract emotional pattern features"""
        return {
            'intensity': max(emotions.values()),
            'dominance': max(emotions.items(), key=lambda x: x[1])[1],
            'complexity': self._calculate_complexity(emotions),
            'balance': self._calculate_balance(emotions)
        }
        
    def _calculate_pattern_similarity(self, pattern1: Dict[str, float], pattern2: Dict[str, float]) -> float:
        """Calculate similarity between two emotional patterns"""
        similarities = []
        for key in pattern1.keys():
            if key in pattern2:
                diff = abs(pattern1[key] - pattern2[key])
                similarities.append(1 - min(1, diff))
        return statistics.mean(similarities) if similarities else 0
        
    def _generate_suggested_responses(self, emotions: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate suggested responses based on emotional state"""
        responses = []
        dominant = max(emotions.items(), key=lambda x: x[1])
        
        # Generate responses based on emotional intensity and stability
        intensity = max(emotions.values())
        stability = self._calculate_stability()
        
        if intensity > 0.7:
            responses.append({
                'type': 'calming',
                'priority': 'high',
                'suggestions': ['Reduce visual complexity', 'Smooth transitions', 'Decrease particle count']
            })
        elif stability < 0.3:
            responses.append({
                'type': 'stabilizing',
                'priority': 'medium',
                'suggestions': ['Maintain consistent animation speed', 'Limit emotion changes', 'Increase stability threshold']
            })
            
        # Add responses based on dominant emotion
        if dominant[1] > 0.5:
            responses.append({
                'type': 'emotion_specific',
                'priority': 'medium',
                'suggestions': [f'Enhance {dominant[0]} visualization', 'Adjust color intensity', 'Modify wave pattern']
            })
            
        # Add more sophisticated, context-aware responses
        if dominant[1] > 0.8:
            responses.append({
                'type': 'proactive',
                'priority': 'high',
                'suggestions': [f'Initiate proactive support for {dominant[0]}', 'Engage in context-aware dialogue']
            })
            
        # Use learned responses
        if dominant[0] in self.learned_responses:
            responses.append({
                'type': 'learned',
                'priority': 'medium',
                'suggestions': self.learned_responses[dominant[0]]
            })
            
        return responses

    def _learn_patterns(self, emotions: Dict[str, float]):
        """Learn and update emotional patterns over time."""
        pattern = self._extract_pattern(emotions)
        self.pattern_memory.append(pattern)
        # Continual learning: update adaptive weights
        for k, v in pattern.items():
            if k not in self.adaptive_weights:
                self.adaptive_weights[k] = v
            else:
                self.adaptive_weights[k] += self.learning_rate * (v - self.adaptive_weights[k])

    def update_learned_response(self, emotion: str, response: str):
        """Allow the system to learn new responses for emotions."""
        if emotion not in self.learned_responses:
            self.learned_responses[emotion] = []
        if response not in self.learned_responses[emotion]:
            self.learned_responses[emotion].append(response)

    def continual_learning(self, feedback: Dict[str, Any]):
        """Update learning based on feedback from user or system."""
        for emotion, resp in feedback.get('responses', {}).items():
            self.update_learned_response(emotion, resp)
        # Adjust learning rate or thresholds if needed
        if 'learning_rate' in feedback:
            self.learning_rate = feedback['learning_rate']
        if 'pattern_recognition_threshold' in feedback:
            self.pattern_recognition_threshold = feedback['pattern_recognition_threshold']

class PerformanceMonitor(QThread):
    metrics_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.last_net_io = psutil.net_io_counters()
        self.last_disk_io = psutil.disk_io_counters()
        self.last_check = time.time()
        
    def run(self):
        while self.running:
            try:
                metrics = {
                    'cpu': psutil.cpu_percent(),
                    'memory': psutil.virtual_memory().percent,
                    'fps': 0
                }
                self.metrics_updated.emit(metrics)
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
                
    def _collect_metrics(self) -> SystemMetrics:
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        disk_io = self._get_disk_io_percent()
        net_io = self._get_network_io_percent()
        
        # Get GPU metrics if available
        gpu_memory = None
        if HAS_GPU:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:  # Check if any GPUs are available
                    gpu = gpus[0]  # Get the first GPU
                    gpu_memory = gpu.memoryUtil * 100
                else:
                    logger.info("No GPU found")
            except Exception as e:
                logger.warning(f"Error getting GPU metrics: {e}")
            
        # Get screen metrics
        screen = QApplication.primaryScreen()
        resolution = screen.size()
        dpi = screen.logicalDotsPerInch()
        
        return SystemMetrics(
            cpu_percent=cpu,
            memory_percent=memory,
            gpu_memory_percent=gpu_memory,
            disk_io_percent=disk_io,
            network_io_percent=net_io,
            fps=0,  # Updated by main class
            frame_time=0,  # Updated by main class
            resolution=resolution,
            dpi=dpi
        )
        
    def _get_disk_io_percent(self) -> float:
        current = psutil.disk_io_counters()
        time_diff = time.time() - self.last_check
        if time_diff > 0:
            read_speed = (current.read_bytes - self.last_disk_io.read_bytes) / time_diff
            write_speed = (current.write_bytes - self.last_disk_io.write_bytes) / time_diff
            self.last_disk_io = current
            return (read_speed + write_speed) / (1024 * 1024)  # MB/s
        return 0.0
        
    def _get_network_io_percent(self) -> float:
        current = psutil.net_io_counters()
        time_diff = time.time() - self.last_check
        if time_diff > 0:
            bytes_sent = (current.bytes_sent - self.last_net_io.bytes_sent) / time_diff
            bytes_recv = (current.bytes_recv - self.last_net_io.bytes_recv) / time_diff
            self.last_net_io = current
            return (bytes_sent + bytes_recv) / (1024 * 1024)  # MB/s
        return 0.0

class EmotionVisualizer(QWidget):
    emotion_updated = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 200)
        
        # Emotional intelligence
        self.emotional_intelligence = EmotionalIntelligence()
        self.current_emotional_state: Optional[EmotionalState] = None
        
        # System integration
        self.performance_monitor = PerformanceMonitor()
        self.performance_monitor.metrics_updated.connect(self.update_system_metrics)
        self.performance_monitor.start()
        
        # Performance monitoring
        self.frame_times = []
        self.last_frame_time = time.time()
        self.target_fps = 60
        self.system_metrics: Optional[SystemMetrics] = None
        
        # Thread pool for parallel processing
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        
        # Initialize emotion states with validation
        self.emotions = self._initialize_emotions()
        self.target_emotions = self.emotions.copy()
        self.emotion_history: List[Dict[str, float]] = []
        self.max_history_size = 100
        
        # Animation properties with adaptive timing
        self.animation_speed = 0.1
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_values)
        self._start_animation_timer()
        
        # Wave animation with adaptive parameters
        self.wave_phase = 0
        self.wave_frequency = 0.02
        self.wave_amplitude = 20
        self.wave_timer = QTimer()
        self.wave_timer.timeout.connect(self.update_wave)
        self.wave_timer.start(50)
        
        # Particle system with self-regulation
        self.particle_system: List[Dict] = []
        self.max_particles = 100
        self.particle_spawn_rate = 0.3
        self.particle_timer = QTimer()
        self.particle_timer.timeout.connect(self.update_particles)
        self.particle_timer.start(16)
        
        # Error recovery
        self.error_count = 0
        self.max_errors = 5
        self.recovery_timer = QTimer()
        self.recovery_timer.timeout.connect(self.check_system_health)
        self.recovery_timer.start(5000)
        
        # Desktop integration
        self._setup_desktop_integration()
        
    def _setup_desktop_integration(self):
        """Set up desktop integration features"""
        try:
            if platform.system() == 'Windows':
                # Set process priority
                pid = os.getpid()
                handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, pid)
                ctypes.windll.kernel32.SetPriorityClass(handle, 0x00008000)  # ABOVE_NORMAL_PRIORITY_CLASS
                ctypes.windll.kernel32.CloseHandle(handle)
                
            # Set window flags for better performance
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
            self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
            
        except Exception as e:
            logger.error(f"Error setting up desktop integration: {e}")
            
    def update_system_metrics(self, metrics):
        """Update system metrics and adjust performance accordingly"""
        try:
            current_time = time.time()
            frame_time = current_time - self.last_frame_time
            self.last_frame_time = current_time
            
            self.frame_times.append(frame_time)
            if len(self.frame_times) > 60:
                self.frame_times.pop(0)
                
            metrics['fps'] = 1 / (sum(self.frame_times) / len(self.frame_times)) if self.frame_times else 0
            
            # Adjust performance based on system load
            if metrics['cpu'] > 80 or metrics['memory'] > 80:
                self.animation_timer.setInterval(33)  # Reduce to 30 FPS
            else:
                self.animation_timer.setInterval(16)  # Normal 60 FPS
            
            self.system_metrics = self._collect_metrics()
            
        except Exception as e:
            logger.error(f"Error updating system metrics: {e}")
            
    def _adjust_performance(self, metrics: SystemMetrics):
        """Adjust performance parameters based on system metrics"""
        try:
            # Adjust based on CPU usage
            if metrics.cpu_percent > 80:
                self.max_particles = max(50, self.max_particles - 10)
                self.particle_spawn_rate *= 0.8
                
            # Adjust based on memory usage
            if metrics.memory_percent > 80:
                self.max_history_size = max(50, self.max_history_size - 10)
                self.emotion_history = self.emotion_history[-self.max_history_size:]
                
            # Adjust based on GPU usage if available
            if metrics.gpu_memory_percent and metrics.gpu_memory_percent > 80:
                self.wave_frequency *= 0.8
                self.wave_amplitude *= 0.8
                
            # Adjust based on FPS
            if metrics.fps < self.target_fps * 0.8:
                self.optimize_performance()
                
        except Exception as e:
            logger.error(f"Error adjusting performance: {e}")
            
    def optimize_performance(self):
        """Optimize performance with advanced strategies"""
        try:
            # Reduce visual complexity
            self.max_particles = max(50, self.max_particles - 10)
            self.particle_spawn_rate *= 0.8
            self.wave_frequency *= 0.8
            self.wave_amplitude *= 0.8
            
            # Clear excess resources
            if len(self.particle_system) > self.max_particles:
                self.particle_system = self.particle_system[-self.max_particles:]
                
            # Optimize memory usage
            self.emotion_history = self.emotion_history[-self.max_history_size:]
            
            # Adjust animation timing
            if self.system_metrics and self.system_metrics.cpu_percent > 70:
                self.animation_timer.setInterval(33)  # 30 FPS
            else:
                self.animation_timer.setInterval(16)  # 60 FPS
                
            logger.info("Advanced performance optimization applied")
            
        except Exception as e:
            logger.error(f"Error optimizing performance: {e}")
            
    def recover_from_error(self):
        """Enhanced error recovery with system state preservation"""
        try:
            logger.warning("Starting enhanced error recovery")
            
            # Save current state
            current_emotions = self.emotions.copy()
            current_particles = self.particle_system.copy()
            
            # Reset error count
            self.error_count = 0
            
            # Reset animation parameters
            self.animation_speed = 0.1
            self.wave_frequency = 0.02
            self.wave_amplitude = 20
            
            # Clear and rebuild particle system
            self.particle_system.clear()
            for particle in current_particles[:self.max_particles]:
                self.particle_system.append(particle)
                
            # Reset performance parameters
            self.max_particles = 100
            self.particle_spawn_rate = 0.3
            
            # Restore emotions
            self.emotions = current_emotions
            self.target_emotions = current_emotions.copy()
            
            # Restart timers
            self._start_animation_timer()
            
            # Force garbage collection
            import gc
            gc.collect()
            
            logger.info("Enhanced system recovery completed")
            
        except Exception as e:
            logger.error(f"Error during enhanced recovery: {e}")
            # Fallback to basic recovery
            self._basic_recovery()
            
    def _basic_recovery(self):
        """Basic recovery as fallback"""
        try:
            # Reset to default state
            self.emotions = self._initialize_emotions()
            self.target_emotions = self.emotions.copy()
            self.particle_system.clear()
            self.error_count = 0
            
            # Restart timers
            self._start_animation_timer()
            
        except Exception as e:
            logger.error(f"Error during basic recovery: {e}")
            
    def closeEvent(self, event):
        """Clean up resources on close"""
        try:
            # Stop performance monitor
            self.performance_monitor.running = False
            self.performance_monitor.wait()
            
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True)
            
            # Clear resources
            self.particle_system.clear()
            self.emotion_history.clear()
            
            # Force garbage collection
            import gc
            gc.collect()
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            
        event.accept()

    def _initialize_emotions(self) -> Dict[str, float]:
        """Initialize emotions with validation"""
        try:
            emotions = {
                'happy': 0.0,
                'sad': 0.0,
                'angry': 0.0,
                'neutral': 0.0,
                'fear': 0.0,
                'surprise': 0.0,
                'disgust': 0.0
            }
            return emotions
        except Exception as e:
            logger.error(f"Error initializing emotions: {e}")
            return {'neutral': 0.0}  # Fallback to neutral
            
    def _start_animation_timer(self):
        """Start animation timer with error handling"""
        try:
            self.animation_timer.start(16)  # ~60 FPS
        except Exception as e:
            logger.error(f"Error starting animation timer: {e}")
            self.animation_timer.start(33)  # Fallback to 30 FPS
            
    def get_emotion_color(self, emotion: str) -> str:
        """Get color for emotion with validation"""
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
        
    def update_emotions(self, emotions: Dict[str, float]):
        """Update emotions with emotional intelligence analysis"""
        try:
            # Validate input
            if not isinstance(emotions, dict):
                raise ValueError("Emotions must be a dictionary")
                
            # Validate emotion values
            for emotion, value in emotions.items():
                if not isinstance(value, (int, float)):
                    raise ValueError(f"Invalid value for emotion {emotion}")
                if not 0 <= value <= 1:
                    raise ValueError(f"Emotion value for {emotion} must be between 0 and 1")
                    
            # Update target emotions
            self.target_emotions = emotions.copy()
            
            # Analyze emotional state
            self.current_emotional_state = self.emotional_intelligence.analyze_emotions(emotions)
            
            # Apply emotional intelligence suggestions
            self._apply_emotional_suggestions()
            
            # Track history
            self.emotion_history.append(emotions.copy())
            if len(self.emotion_history) > self.max_history_size:
                self.emotion_history.pop(0)
                
            self.emotion_updated.emit(emotions)
            
            # After updating, optionally provide feedback for continual learning
            if hasattr(self, 'last_feedback') and self.last_feedback:
                self.provide_feedback(self.last_feedback)
                self.last_feedback = None
            
        except Exception as e:
            logger.error(f"Error updating emotions: {e}")
            self.error_count += 1
            if self.error_count >= self.max_errors:
                self.recover_from_error()
                
    def _apply_emotional_suggestions(self):
        """Apply suggestions from emotional intelligence analysis"""
        if not self.current_emotional_state:
            return
            
        suggestions = self.current_emotional_state.emotional_context.get('suggested_responses', [])
        
        for suggestion in suggestions:
            if suggestion['type'] == 'calming' and suggestion['priority'] == 'high':
                self.max_particles = max(50, self.max_particles - 10)
                self.particle_spawn_rate *= 0.8
                self.wave_frequency *= 0.8
                self.wave_amplitude *= 0.8
                
            elif suggestion['type'] == 'stabilizing':
                self.animation_speed = max(0.05, self.animation_speed * 0.9)
                self.stability_threshold = min(0.3, self.stability_threshold * 1.1)
                
            elif suggestion['type'] == 'emotion_specific':
                if 'Enhance visualization' in suggestion['suggestions']:
                    self.wave_amplitude *= 1.2
                    self.particle_spawn_rate *= 1.2
                    
    def animate_values(self):
        """Animate emotion values with emotional intelligence"""
        try:
            changed = False
            for emotion in self.emotions:
                current = self.emotions[emotion]
                target = self.target_emotions[emotion]
                
                # Adaptive animation speed based on emotional state
                if self.current_emotional_state:
                    if self.current_emotional_state.emotional_stability < 0.3:
                        speed = self.animation_speed * 0.5  # Slower for unstable emotions
                    elif self.current_emotional_state.emotional_intensity > 0.7:
                        speed = self.animation_speed * 1.5  # Faster for intense emotions
                    else:
                        speed = self.animation_speed
                else:
                    speed = self.animation_speed
                
                # Smooth interpolation with emotional context
                if abs(current - target) > 0.001:
                    self.emotions[emotion] += (target - current) * speed
                    changed = True
                    
            if changed:
                self.update()
                
        except Exception as e:
            logger.error(f"Error in animation: {e}")
            self.error_count += 1
            
    def update_wave(self):
        """Update wave animation with emotional intelligence"""
        try:
            self.wave_phase += 0.1
            
            if self.current_emotional_state:
                # Adjust wave parameters based on emotional state
                intensity = self.current_emotional_state.emotional_intensity
                stability = self.current_emotional_state.emotional_stability
                
                self.wave_frequency = 0.02 * (1 + intensity * 0.5)
                self.wave_amplitude = 20 * (1 + intensity * 0.5) * stability
                
            self.update()
            
        except Exception as e:
            logger.error(f"Error updating wave: {e}")
            self.error_count += 1
            
    def update_particles(self):
        """Update particle system with emotional intelligence"""
        try:
            # Update existing particles
            for particle in self.particle_system[:]:
                particle['life'] -= 1
                if particle['life'] <= 0:
                    self.particle_system.remove(particle)
                    continue
                    
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                particle['vy'] += 0.1  # Gravity
                
            # Self-regulate particle count based on emotional state
            if self.current_emotional_state:
                intensity = self.current_emotional_state.emotional_intensity
                stability = self.current_emotional_state.emotional_stability
                
                target_particles = int(self.max_particles * (0.5 + intensity * 0.5))
                spawn_rate = self.particle_spawn_rate * (0.5 + stability * 0.5)
                
                if len(self.particle_system) < target_particles:
                    if random.random() < spawn_rate:
                        dominant_emotion = self.current_emotional_state.dominant_emotion
                        if self.emotions[dominant_emotion] > 0.3:
                            self.add_particle(dominant_emotion)
                            
            self.update()
            
        except Exception as e:
            logger.error(f"Error updating particles: {e}")
            self.error_count += 1
            
    def add_particle(self, emotion: str):
        """Add particle with validation"""
        try:
            if len(self.particle_system) >= self.max_particles:
                return
                
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
            
        except Exception as e:
            logger.error(f"Error adding particle: {e}")
            self.error_count += 1
            
    def monitor_performance(self):
        """Monitor and optimize performance"""
        try:
            current_time = time.time()
            frame_time = current_time - self.last_frame_time
            self.frame_times.append(frame_time)
            
            # Keep only recent frame times
            if len(self.frame_times) > 60:
                self.frame_times.pop(0)
                
            # Calculate average FPS
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            current_fps = 1 / avg_frame_time if avg_frame_time > 0 else 0
            
            # Adjust performance parameters
            if current_fps < self.target_fps * 0.8:  # If FPS drops below 80% of target
                self.optimize_performance()
                
            self.last_frame_time = current_time
            
        except Exception as e:
            logger.error(f"Error monitoring performance: {e}")
            
    def check_system_health(self):
        """Check system health and recover if needed"""
        try:
            if self.error_count >= self.max_errors:
                self.recover_from_error()
            else:
                self.error_count = max(0, self.error_count - 1)
                
        except Exception as e:
            logger.error(f"Error checking system health: {e}")
            
    def get_dominant_emotion(self) -> str:
        """Get the current dominant emotion with validation"""
        try:
            return max(self.emotions.items(), key=lambda x: x[1])[0]
        except Exception as e:
            logger.error(f"Error getting dominant emotion: {e}")
            return 'neutral'
            
    def get_emotional_intensity(self) -> float:
        """Get the overall emotional intensity with validation"""
        try:
            return max(self.emotions.values())
        except Exception as e:
            logger.error(f"Error getting emotional intensity: {e}")
            return 0.0
            
    def paintEvent(self, event):
        """Paint event with error handling"""
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Draw background
            painter.fillRect(self.rect(), QColor('#1E1E1E'))
            
            # Draw wave visualization
            if self.get_emotional_intensity() > 0.1:
                self.draw_wave(painter)
                
            # Draw emotion bars
            self.draw_emotion_bars(painter)
            
            # Draw particles
            self.draw_particles(painter)
            
        except Exception as e:
            logger.error(f"Error in paint event: {e}")
            self.error_count += 1
            
    def draw_wave(self, painter: QPainter):
        """Draw wave with error handling"""
        try:
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
                y += math.sin(x * self.wave_frequency + self.wave_phase) * self.wave_amplitude * intensity
                y += math.sin(x * self.wave_frequency * 0.5 - self.wave_phase * 0.5) * self.wave_amplitude * 0.5 * intensity
                path.lineTo(x, y)
                
            path.lineTo(self.width(), self.height())
            path.lineTo(0, self.height())
            
            painter.fillPath(path, gradient)
            
        except Exception as e:
            logger.error(f"Error drawing wave: {e}")
            self.error_count += 1
            
    def draw_emotion_bars(self, painter: QPainter):
        """Draw emotion bars with error handling"""
        try:
            width = self.width()
            height = self.height()
            bar_width = width / len(self.emotions)
            spacing = 10
            
            for i, (emotion, value) in enumerate(self.emotions.items()):
                x = i * bar_width + spacing
                bar_height = value * (height - 2 * spacing)
                
                # Create gradient
                color = QColor(self.get_emotion_color(emotion))
                color.setAlpha(int(255 * value))
                
                # Draw bar
                painter.fillRect(
                    x, height - bar_height - spacing,
                    bar_width - 2 * spacing, bar_height,
                    color
                )
                
                # Draw label
                painter.setPen(QColor('#FFFFFF'))
                painter.drawText(
                    x, height - spacing,
                    bar_width - 2 * spacing, 20,
                    Qt.AlignmentFlag.AlignCenter,
                    emotion.capitalize()
                )
                
        except Exception as e:
            logger.error(f"Error drawing emotion bars: {e}")
            self.error_count += 1
            
    def draw_particles(self, painter: QPainter):
        """Draw particles with error handling"""
        try:
            for particle in self.particle_system:
                color = particle['color']
                alpha = int(255 * (particle['life'] / 60))
                color.setAlpha(alpha)
                
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(color))
                painter.drawEllipse(
                    particle['x'] - particle['size']/2,
                    particle['y'] - particle['size']/2,
                    particle['size'],
                    particle['size']
                )
                
        except Exception as e:
            logger.error(f"Error drawing particles: {e}")
            self.error_count += 1
            
    def provide_feedback(self, feedback: Dict[str, Any]):
        """Allow external feedback to improve emotional intelligence."""
        self.emotional_intelligence.continual_learning(feedback)

    def update_emotions(self, emotions: Dict[str, float]):
        # ... existing code ...
        # After updating, optionally provide feedback for continual learning
        if hasattr(self, 'last_feedback') and self.last_feedback:
            self.provide_feedback(self.last_feedback)
            self.last_feedback = None
        # ... existing code ... 