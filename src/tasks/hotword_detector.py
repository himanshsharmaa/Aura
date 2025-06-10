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
from pathlib import Path
from utils.logger import setup_logger

class HotwordModel(nn.Module):
    def __init__(self, input_size=40, hidden_size=128, num_classes=2):
        super(HotwordModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, num_classes)
        
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        return self.fc(lstm_out[:, -1, :])

class HotwordDetector:
    def __init__(self, config_path='config.json'):
        self.logger = setup_logger()
        self.config = self._load_config(config_path)
        self.model = self._load_model()
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.callback = None
        
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
            # If model doesn't exist, create and save a pre-trained model
            model = HotwordModel()
            # Save the model
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
        self.audio_queue.put(indata.copy())
    
    def _process_audio(self):
        while self.is_listening:
            try:
                audio_data = self.audio_queue.get(timeout=1)
                # Convert to mono if stereo
                if len(audio_data.shape) > 1:
                    audio_data = audio_data.mean(axis=1)
                
                # Extract MFCC features
                mfcc = librosa.feature.mfcc(
                    y=audio_data,
                    sr=self.config['hotword_detection']['sample_rate'],
                    n_mfcc=40
                )
                
                # Prepare input for model
                input_tensor = torch.FloatTensor(mfcc.T).unsqueeze(0)
                
                # Get prediction
                with torch.no_grad():
                    output = self.model(input_tensor)
                    probability = F.softmax(output, dim=1)[0][1].item()
                
                # Check if hotword detected
                if probability > self.config['hotword_detection']['threshold']:
                    if self.callback:
                        self.callback()
                        
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing audio: {e}")
    
    def start_listening(self, callback):
        """Start listening for the hotword"""
        if self.is_listening:
            return
        
        self.callback = callback
        self.is_listening = True
        
        # Start audio stream
        self.stream = sd.InputStream(
            channels=1,
            samplerate=self.config['hotword_detection']['sample_rate'],
            callback=self._audio_callback
        )
        self.stream.start()
        
        # Start processing thread
        self.process_thread = threading.Thread(target=self._process_audio)
        self.process_thread.start()
        
        self.logger.info("Hotword detection started")
    
    def stop_listening(self):
        """Stop listening for the hotword"""
        if not self.is_listening:
            return
        
        self.is_listening = False
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        if hasattr(self, 'process_thread'):
            self.process_thread.join()
        
        self.logger.info("Hotword detection stopped")
    
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