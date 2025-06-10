import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import sounddevice as sd
import librosa
import threading
import queue
import json
import os
import time
import tensorflow as tf
import tensorflow_hub as hub
from pathlib import Path
from utils.logger import setup_logger
from datetime import datetime
from auth.user_manager import UserManager
from training.training_manager import TrainingManager

logger = setup_logger(__name__)

class HotwordModel(nn.Module):
    def __init__(self, input_size=40, hidden_size=128, num_classes=2):
        super(HotwordModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, num_classes)
        
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        return self.fc(lstm_out[:, -1, :])

class HotwordDetector:
    def __init__(self, config_path='config.json', user_email=None):
        self.logger = setup_logger(__name__)
        self.config = self._load_config(config_path)
        self.is_listening = False
        self.is_collecting = False
        self.model = None
        self.audio_queue = []
        self.visualization_callback = None
        self.confidence_history = []
        self.user_email = user_email
        self.user_manager = UserManager()
        self.training_manager = TrainingManager()
        self._load_model()
        
    def _load_config(self, config_path):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                # Ensure required config sections exist
                if 'hotword_detection' not in config:
                    config['hotword_detection'] = {
                        'model': 'models/yamnet',
                        'sample_rate': 16000,
                        'threshold': 0.5,
                        'class_index': 0
                    }
                return config
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            # Return default config if file not found
            return {
                'hotword_detection': {
                    'model': 'models/yamnet',
                    'sample_rate': 16000,
                    'threshold': 0.5,
                    'class_index': 0
                }
            }
    
    def _load_model(self):
        """Load YAMNet model"""
        try:
            if self.user_email:
                # Try to load user-specific model
                user_models = self.training_manager.get_user_models(self.user_email)
                if user_models and user_models['hotword']:
                    # Use the most recent model
                    latest_model = sorted(user_models['hotword'], 
                                       key=lambda x: x['created_at'])[-1]
                    self.model = tf.keras.models.load_model(latest_model['path'])
                    self.logger.info(f"Loaded user-specific model from {latest_model['path']}")
                    return
            
            # Fall back to default YAMNet model
            model_path = self.config['hotword_detection']['model']
            if not os.path.exists(model_path):
                self.logger.info("Downloading YAMNet model...")
                # Load model directly from TF Hub
                self.model = hub.load('https://tfhub.dev/google/yamnet/1')
                self.logger.info("Model downloaded successfully")
            else:
                # Load from local path
                self.model = hub.load(model_path)
                self.logger.info("Model loaded from local path")
            
            # Test model with dummy input to ensure it works
            dummy_input = np.zeros((16000,), dtype=np.float32)
            _ = self.model(dummy_input)
            self.logger.info("Model test successful")
            
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            self.model = None
    
    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio input stream"""
        if status:
            self.logger.warning(f"Audio callback status: {status}")
        self.audio_queue.append(indata.copy())
        
        # Keep only last 3 seconds of audio
        max_samples = int(3 * self.config['hotword_detection']['sample_rate'])
        if len(self.audio_queue) * frames > max_samples:
            self.audio_queue.pop(0)
    
    def _process_audio(self, callback):
        """Process audio for hotword detection"""
        while self.is_listening:
            try:
                if not self.audio_queue or not self.model:
                    time.sleep(0.1)
                    continue
                
                # Combine recent audio chunks
                audio_data = np.concatenate(self.audio_queue)
                self.audio_queue.clear()
                
                # Convert to mono if stereo
                if len(audio_data.shape) > 1:
                    audio_data = audio_data.mean(axis=1)
                
                # Resample if needed
                if self.config['hotword_detection']['sample_rate'] != 16000:
                    audio_data = librosa.resample(
                        audio_data,
                        orig_sr=self.config['hotword_detection']['sample_rate'],
                        target_sr=16000
                    )
                
                # Get model predictions
                scores, embeddings, spectrogram = self.model(audio_data)
                scores = scores.numpy()
                
                # Get confidence for hotword class
                confidence = float(scores[0, self.config['hotword_detection']['class_index']])
                
                # Update confidence history
                self.confidence_history.append(confidence)
                if len(self.confidence_history) > 100:  # Keep last 100 values
                    self.confidence_history.pop(0)
                
                # Call visualization callback if set
                if self.visualization_callback:
                    self.visualization_callback(confidence, self.confidence_history)
                
                # Check if hotword detected
                if confidence > self.config['hotword_detection']['threshold']:
                    callback()
                
            except Exception as e:
                self.logger.error(f"Error processing audio: {e}")
                time.sleep(0.1)
    
    def start_listening(self, callback):
        """Start listening for hotword"""
        if self.is_listening:
            return
        
        if not self.model:
            self.logger.error("Cannot start listening: model not loaded")
            return
        
        self.logger.info("Starting hotword detection...")
        self.is_listening = True
        
        # Start audio stream
        self.stream = sd.InputStream(
            channels=1,
            samplerate=self.config['hotword_detection']['sample_rate'],
            callback=self._audio_callback
        )
        self.stream.start()
        
        # Start processing thread
        self.process_thread = threading.Thread(
            target=self._process_audio,
            args=(callback,)
        )
        self.process_thread.start()
        
        self.logger.info("Hotword detection started")
    
    def stop_listening(self):
        """Stop listening for hotword"""
        if not self.is_listening:
            return
        
        self.logger.info("Stopping hotword detection...")
        self.is_listening = False
        
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        
        if hasattr(self, 'process_thread'):
            self.process_thread.join()
        
        self.logger.info("Hotword detection stopped")
    
    def start_collecting_samples(self, sample_type):
        """Start collecting training samples"""
        if self.is_collecting:
            return False
        
        if not self.user_email:
            self.logger.error("Cannot collect samples: no user email provided")
            return False
        
        self.logger.info(f"Starting sample collection for {sample_type}...")
        self.is_collecting = True
        self.current_sample_type = sample_type
        return True
    
    def stop_collecting_samples(self):
        """Stop collecting training samples"""
        if not self.is_collecting:
            return False
        
        self.logger.info("Stopping sample collection...")
        self.is_collecting = False
        return True
    
    def set_visualization_callback(self, callback):
        """Set callback for confidence visualization"""
        self.visualization_callback = callback
    
    def train_model(self, positive_samples, negative_samples):
        """Train the hotword detection model"""
        try:
            if not self.user_email:
                self.logger.error("Cannot train model: no user email provided")
                return False
            
            self.logger.info("Training model...")
            # Combine samples
            all_samples = positive_samples + negative_samples
            
            # Train model
            success, model_path = self.training_manager.train_hotword_model(
                self.user_email,
                all_samples,
                model_params={
                    'epochs': 10,
                    'batch_size': 32
                }
            )
            
            if success:
                self.logger.info(f"Model trained successfully: {model_path}")
                # Reload the model
                self._load_model()
                return True
            else:
                self.logger.error(f"Model training failed: {model_path}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error training model: {e}")
            return False 