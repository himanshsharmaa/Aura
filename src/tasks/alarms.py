# Alarms module

import pvporcupine
import pyaudio
import os
import json
from tasks.hotword_detector import HotwordModel
from utils.logger import setup_logger
import threading
import time
import sounddevice as sd
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import librosa
from datetime import datetime
from pathlib import Path
from collections import deque
import queue
import torch
import torch.nn as nn
import torch.nn.functional as F
from tasks.hotword_detector import HotwordDetector

logger = setup_logger(__name__)

# Load config
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'config.json')
try:
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
except Exception as e:
    logger.error(f"Could not load config: {e}")
    config = {}

class HotwordDetector:
    def __init__(self, config_path='config.json'):
        self.logger = setup_logger()
        self.config = self._load_config(config_path)
        self.model = self._load_model()
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.callback = None
        
        # For real-time visualization
        self.confidence_history = deque(maxlen=100)  # Store last 100 confidence values
        self.visualization_callback = None
        self.last_confidence = 0.0
        
        # For training sample collection
        self.is_collecting_samples = False
        self.collected_samples = []
        self.sample_type = None  # 'positive' or 'negative'
        self.sample_duration = 2.0  # seconds
        self.sample_buffer = []
        
    def _load_config(self, config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return {}
    
    def _load_model(self):
        model_path = self.config['hotword_detection']['model_path']
        if not os.path.exists(model_path):
            model = HotwordModel()
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            torch.save(model.state_dict(), model_path)
        else:
            model = HotwordModel()
            model.load_state_dict(torch.load(model_path))
        model.eval()
        return model
    
    def _audio_callback(self, indata, frames, time, status):
        if status:
            self.logger.warning(f"Audio callback status: {status}")
        
        audio_data = indata.copy()
        
        # Handle training sample collection
        if self.is_collecting_samples:
            self.sample_buffer.append(audio_data)
            if len(self.sample_buffer) * frames / self.config['hotword_detection']['sample_rate'] >= self.sample_duration:
                self._save_collected_sample()
        
        # Handle normal detection
        self.audio_queue.put(audio_data)
    
    def _save_collected_sample(self):
        if not self.sample_buffer:
            return
            
        # Combine collected audio chunks
        audio_data = np.concatenate(self.sample_buffer)
        self.sample_buffer.clear()
        
        # Save the sample
        sample_dir = os.path.join('data', 'training_samples', self.sample_type)
        os.makedirs(sample_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        sample_path = os.path.join(sample_dir, f'sample_{timestamp}.npy')
        
        np.save(sample_path, audio_data)
        self.collected_samples.append(sample_path)
        self.logger.info(f"Saved {self.sample_type} sample to {sample_path}")
    
    def _process_audio(self):
        while self.is_listening:
            try:
                audio_data = self.audio_queue.get(timeout=1)
                if len(audio_data.shape) > 1:
                    audio_data = audio_data.mean(axis=1)
                
                # Extract MFCC features
                mfcc = librosa.feature.mfcc(
                    y=audio_data,
                    sr=self.config['hotword_detection']['sample_rate'],
                    n_mfcc=40
                )
                
                # Get prediction
                input_tensor = torch.FloatTensor(mfcc.T).unsqueeze(0)
                with torch.no_grad():
                    output = self.model(input_tensor)
                    probability = F.softmax(output, dim=1)[0][1].item()
                
                # Update confidence history
                self.last_confidence = probability
                self.confidence_history.append(probability)
                
                # Trigger visualization callback
                if self.visualization_callback:
                    self.visualization_callback(probability, list(self.confidence_history))
                
                # Check if hotword detected
                if probability > self.config['hotword_detection']['threshold']:
                    if self.callback:
                        self.callback()
                        
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing audio: {e}")
    
    def start_listening(self, callback):
        if self.is_listening:
            return
        
        self.callback = callback
        self.is_listening = True
        
        self.stream = sd.InputStream(
            channels=1,
            samplerate=self.config['hotword_detection']['sample_rate'],
            callback=self._audio_callback
        )
        self.stream.start()
        
        self.process_thread = threading.Thread(target=self._process_audio)
        self.process_thread.start()
        
        self.logger.info("Hotword detection started")
    
    def stop_listening(self):
        if not self.is_listening:
            return
        
        self.is_listening = False
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        if hasattr(self, 'process_thread'):
            self.process_thread.join()
        
        self.logger.info("Hotword detection stopped")
    
    def set_visualization_callback(self, callback):
        """Set callback for real-time confidence visualization"""
        self.visualization_callback = callback
    
    def get_current_confidence(self):
        """Get the current detection confidence"""
        return self.last_confidence
    
    def get_confidence_history(self):
        """Get the confidence history for visualization"""
        return list(self.confidence_history)
    
    def start_collecting_samples(self, sample_type):
        """Start collecting training samples"""
        if self.is_collecting_samples:
            return False
        
        if sample_type not in ['positive', 'negative']:
            self.logger.error("Sample type must be 'positive' or 'negative'")
            return False
        
        self.is_collecting_samples = True
        self.sample_type = sample_type
        self.sample_buffer = []
        self.logger.info(f"Started collecting {sample_type} samples")
        return True
    
    def stop_collecting_samples(self):
        """Stop collecting training samples"""
        if not self.is_collecting_samples:
            return False
        
        self.is_collecting_samples = False
        if self.sample_buffer:
            self._save_collected_sample()
        
        self.logger.info(f"Stopped collecting {self.sample_type} samples")
        return True
    
    def get_collected_samples(self):
        """Get list of collected sample paths"""
        return self.collected_samples
    
    def clear_collected_samples(self):
        """Clear the list of collected samples"""
        self.collected_samples = []
        self.logger.info("Cleared collected samples list")
    
    def train_model(self, positive_samples, negative_samples):
        """Train the hotword detection model with new samples"""
        try:
            self.model.train()
            optimizer = torch.optim.Adam(self.model.parameters())
            criterion = nn.CrossEntropyLoss()
            
            # Process positive samples
            for audio_data in positive_samples:
                mfcc = librosa.feature.mfcc(
                    y=audio_data,
                    sr=self.config['hotword_detection']['sample_rate'],
                    n_mfcc=40
                )
                input_tensor = torch.FloatTensor(mfcc.T).unsqueeze(0)
                target = torch.tensor([1])
                
                optimizer.zero_grad()
                output = self.model(input_tensor)
                loss = criterion(output, target)
                loss.backward()
                optimizer.step()
            
            # Process negative samples
            for audio_data in negative_samples:
                mfcc = librosa.feature.mfcc(
                    y=audio_data,
                    sr=self.config['hotword_detection']['sample_rate'],
                    n_mfcc=40
                )
                input_tensor = torch.FloatTensor(mfcc.T).unsqueeze(0)
                target = torch.tensor([0])
                
                optimizer.zero_grad()
                output = self.model(input_tensor)
                loss = criterion(output, target)
                loss.backward()
                optimizer.step()
            
            # Save the trained model
            torch.save(self.model.state_dict(), self.config['hotword_detection']['model_path'])
            self.model.eval()
            
            self.logger.info("Model training completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error training model: {e}")
            return False

class AlarmSystem:
    def __init__(self, config_path='config.json'):
        self.logger = setup_logger(__name__)
        self.config = self._load_config(config_path)
        self.is_running = False
        self.sound_event_model = None
        self.audio_queue = []
        self.last_event_time = {}
        self.event_callbacks = {}
        self.hotword_detector = None  # Initialize in start() method
        
    def _load_config(self, config_path):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                # Ensure required config sections exist
                if 'sound_event_detection' not in config:
                    config['sound_event_detection'] = {
                        'model': 'models/yamnet',
                        'sample_rate': 16000,
                        'threshold': 0.5,
                        'min_duration': 1.0
                    }
                if 'sound_events' not in config:
                    config['sound_events'] = []
                return config
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            # Return default config if file not found
            return {
                'sound_event_detection': {
                    'model': 'models/yamnet',
                    'sample_rate': 16000,
                    'threshold': 0.5,
                    'min_duration': 1.0
                },
                'sound_events': []
            }
    
    def _load_sound_event_model(self):
        """Load YAMNet model for sound event detection"""
        try:
            model_path = self.config['sound_event_detection']['model']
            if not os.path.exists(model_path):
                self.logger.info("Downloading YAMNet model...")
                # Load model directly from TF Hub
                model = hub.load('https://tfhub.dev/google/yamnet/1')
                self.logger.info("Model downloaded successfully")
            else:
                # Load from local path
                model = hub.load(model_path)
                self.logger.info("Model loaded from local path")
            
            # Test model with dummy input to ensure it works
            dummy_input = np.zeros((16000,), dtype=np.float32)
            _ = model(dummy_input)
            self.logger.info("Model test successful")
            
            return model
        except Exception as e:
            self.logger.error(f"Error loading sound event model: {e}")
            return None
    
    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio input stream"""
        if status:
            self.logger.warning(f"Audio callback status: {status}")
        self.audio_queue.append(indata.copy())
        
        # Keep only last 3 seconds of audio
        max_samples = int(3 * self.config['sound_event_detection']['sample_rate'])
        if len(self.audio_queue) * frames > max_samples:
            self.audio_queue.pop(0)
    
    def _process_audio(self):
        """Process audio for sound event detection"""
        while self.is_running:
            try:
                if not self.audio_queue or not self.sound_event_model:
                    time.sleep(0.1)
                    continue
                
                # Combine recent audio chunks
                audio_data = np.concatenate(self.audio_queue)
                self.audio_queue.clear()
                
                # Convert to mono if stereo
                if len(audio_data.shape) > 1:
                    audio_data = audio_data.mean(axis=1)
                
                # Resample if needed
                if self.config['sound_event_detection']['sample_rate'] != 16000:
                    audio_data = librosa.resample(
                        audio_data,
                        orig_sr=self.config['sound_event_detection']['sample_rate'],
                        target_sr=16000
                    )
                
                # Get model predictions
                scores, embeddings, spectrogram = self.sound_event_model(audio_data)
                scores = scores.numpy()
                
                # Process each detected event
                for event_idx, event_name in enumerate(self.config['sound_events']):
                    score = float(scores[0, event_idx])
                    current_time = time.time()
                    
                    # Check if event exceeds threshold and cooldown period
                    if (score > self.config['sound_event_detection']['threshold'] and
                        current_time - self.last_event_time.get(event_name, 0) > 
                        self.config['sound_event_detection']['min_duration']):
                        
                        self.last_event_time[event_name] = current_time
                        self.logger.info(f"Detected sound event: {event_name} (confidence: {score:.2f})")
                        
                        # Trigger callback if registered
                        if event_name in self.event_callbacks:
                            self.event_callbacks[event_name](score)
                
            except Exception as e:
                self.logger.error(f"Error processing audio: {e}")
                time.sleep(0.1)
    
    def start(self):
        """Start the alarm system"""
        if self.is_running:
            return
        
        self.logger.info("Starting alarm system...")
        self.is_running = True
        
        # Initialize hotword detector
        from tasks.hotword_detector import HotwordDetector
        self.hotword_detector = HotwordDetector()
        
        # Load sound event model
        self.sound_event_model = self._load_sound_event_model()
        if not self.sound_event_model:
            self.logger.error("Failed to load sound event model")
            return
        
        # Start hotword detection
        self.hotword_detector.start_listening(self._on_hotword_detected)
        
        # Start audio stream
        self.stream = sd.InputStream(
            channels=1,
            samplerate=self.config['sound_event_detection']['sample_rate'],
            callback=self._audio_callback
        )
        self.stream.start()
        
        # Start processing thread
        self.process_thread = threading.Thread(target=self._process_audio)
        self.process_thread.start()
        
        self.logger.info("Alarm system started successfully")
    
    def stop(self):
        """Stop the alarm system"""
        if not self.is_running:
            return
        
        self.logger.info("Stopping alarm system...")
        self.is_running = False
        
        # Stop hotword detection
        if self.hotword_detector:
            self.hotword_detector.stop_listening()
        
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        
        if hasattr(self, 'process_thread'):
            self.process_thread.join()
        
        self.logger.info("Alarm system stopped")
    
    def _on_hotword_detected(self):
        """Callback for hotword detection"""
        self.logger.info("Hotword detected!")
        # Add your hotword detection handling here
    
    def register_event_callback(self, event_name, callback):
        """Register a callback for a specific sound event"""
        self.event_callbacks[event_name] = callback
    
    def unregister_event_callback(self, event_name):
        """Unregister a callback for a specific sound event"""
        if event_name in self.event_callbacks:
            del self.event_callbacks[event_name]
    
    def get_event_history(self, event_name=None, time_window=3600):
        """Get history of detected events"""
        current_time = time.time()
        history = []
        
        for event, timestamp in self.last_event_time.items():
            if current_time - timestamp <= time_window:
                if event_name is None or event == event_name:
                    history.append({
                        'event': event,
                        'timestamp': timestamp,
                        'time_ago': current_time - timestamp
                    })
        
        return sorted(history, key=lambda x: x['timestamp'], reverse=True)
