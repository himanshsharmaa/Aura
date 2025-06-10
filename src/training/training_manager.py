import os
import json
import numpy as np
import tensorflow as tf
from datetime import datetime
from pathlib import Path
from utils.logger import setup_logger

logger = setup_logger(__name__)

class TrainingManager:
    def __init__(self, data_dir='data/models'):
        self.logger = setup_logger(__name__)
        self.data_dir = Path(data_dir)
        self.models_dir = self.data_dir / 'trained_models'
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        """Ensure required directories exist"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def prepare_training_data(self, samples):
        """Prepare training data from samples"""
        try:
            X = []
            y = []
            
            for sample in samples:
                # Convert audio data to numpy array if needed
                if isinstance(sample['audio_data'], list):
                    audio_data = np.array(sample['audio_data'])
                else:
                    audio_data = sample['audio_data']
                
                # Ensure audio data is in correct format
                if len(audio_data.shape) > 1:
                    audio_data = audio_data.mean(axis=1)
                
                X.append(audio_data)
                y.append(1 if sample['type'] == 'positive' else 0)
            
            return np.array(X), np.array(y)
        except Exception as e:
            self.logger.error(f"Error preparing training data: {e}")
            return None, None
    
    def train_hotword_model(self, user_email, samples, model_params=None):
        """Train hotword detection model for a user"""
        try:
            # Prepare training data
            X, y = self.prepare_training_data(samples)
            if X is None or y is None:
                return False, "Failed to prepare training data"
            
            # Create model directory for user
            user_model_dir = self.models_dir / user_email / 'hotword'
            user_model_dir.mkdir(parents=True, exist_ok=True)
            
            # Load base YAMNet model
            base_model = tf.keras.applications.MobileNetV2(
                input_shape=(224, 224, 3),
                include_top=False,
                weights='imagenet'
            )
            
            # Add custom classification head
            model = tf.keras.Sequential([
                base_model,
                tf.keras.layers.GlobalAveragePooling2D(),
                tf.keras.layers.Dense(128, activation='relu'),
                tf.keras.layers.Dropout(0.5),
                tf.keras.layers.Dense(1, activation='sigmoid')
            ])
            
            # Compile model
            model.compile(
                optimizer='adam',
                loss='binary_crossentropy',
                metrics=['accuracy']
            )
            
            # Train model
            history = model.fit(
                X, y,
                epochs=model_params.get('epochs', 10),
                batch_size=model_params.get('batch_size', 32),
                validation_split=0.2
            )
            
            # Save model
            model_path = user_model_dir / f"model_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            model.save(model_path)
            
            # Save training history
            history_path = user_model_dir / f"history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(history_path, 'w') as f:
                json.dump(history.history, f)
            
            return True, str(model_path)
            
        except Exception as e:
            self.logger.error(f"Error training hotword model: {e}")
            return False, str(e)
    
    def train_sound_event_model(self, user_email, samples, model_params=None):
        """Train sound event detection model for a user"""
        try:
            # Prepare training data
            X, y = self.prepare_training_data(samples)
            if X is None or y is None:
                return False, "Failed to prepare training data"
            
            # Create model directory for user
            user_model_dir = self.models_dir / user_email / 'sound_events'
            user_model_dir.mkdir(parents=True, exist_ok=True)
            
            # Load base YAMNet model
            base_model = tf.keras.applications.MobileNetV2(
                input_shape=(224, 224, 3),
                include_top=False,
                weights='imagenet'
            )
            
            # Add custom classification head
            model = tf.keras.Sequential([
                base_model,
                tf.keras.layers.GlobalAveragePooling2D(),
                tf.keras.layers.Dense(256, activation='relu'),
                tf.keras.layers.Dropout(0.5),
                tf.keras.layers.Dense(len(np.unique(y)), activation='softmax')
            ])
            
            # Compile model
            model.compile(
                optimizer='adam',
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy']
            )
            
            # Train model
            history = model.fit(
                X, y,
                epochs=model_params.get('epochs', 10),
                batch_size=model_params.get('batch_size', 32),
                validation_split=0.2
            )
            
            # Save model
            model_path = user_model_dir / f"model_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            model.save(model_path)
            
            # Save training history
            history_path = user_model_dir / f"history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(history_path, 'w') as f:
                json.dump(history.history, f)
            
            return True, str(model_path)
            
        except Exception as e:
            self.logger.error(f"Error training sound event model: {e}")
            return False, str(e)
    
    def get_user_models(self, user_email):
        """Get list of trained models for a user"""
        try:
            user_models = {
                'hotword': [],
                'sound_events': []
            }
            
            # Get hotword models
            hotword_dir = self.models_dir / user_email / 'hotword'
            if hotword_dir.exists():
                for model_dir in hotword_dir.iterdir():
                    if model_dir.is_dir():
                        user_models['hotword'].append({
                            'path': str(model_dir),
                            'created_at': datetime.fromtimestamp(model_dir.stat().st_mtime).isoformat()
                        })
            
            # Get sound event models
            sound_events_dir = self.models_dir / user_email / 'sound_events'
            if sound_events_dir.exists():
                for model_dir in sound_events_dir.iterdir():
                    if model_dir.is_dir():
                        user_models['sound_events'].append({
                            'path': str(model_dir),
                            'created_at': datetime.fromtimestamp(model_dir.stat().st_mtime).isoformat()
                        })
            
            return user_models
            
        except Exception as e:
            self.logger.error(f"Error getting user models: {e}")
            return None
    
    def get_model_metrics(self, model_path):
        """Get training metrics for a model"""
        try:
            history_path = Path(model_path).parent / f"history_{Path(model_path).name.split('_')[1]}.json"
            if history_path.exists():
                with open(history_path, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            self.logger.error(f"Error getting model metrics: {e}")
            return None 