# User activity tracking 

import torch
import torchaudio
import numpy as np
from pathlib import Path
from utils.logger import setup_logger

logger = setup_logger(__name__)

class UserActivity:
    def __init__(self, model_path="models/sound_classifier.pt"):
        """
        Initialize the user activity monitoring system.
        
        Args:
            model_path (str): Path to the pre-trained sound classification model
        """
        self.model_path = model_path
        self.sound_classes = [
            'silence', 'speech', 'music', 'doorbell', 'clapping',
            'glass_breaking', 'baby_crying', 'dog_barking'
        ]
        self._load_model()
        
    def _load_model(self):
        """Load the pre-trained sound classification model."""
        try:
            if Path(self.model_path).exists():
                self.model = torch.load(self.model_path)
                self.model.eval()
                logger.info("Sound classification model loaded successfully")
            else:
                logger.warning("Model file not found, using placeholder model")
                self.model = None
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None
            
    def classify_sound(self, audio_data, sample_rate=16000):
        """
        Classify the type of sound in the audio data.
        
        Args:
            audio_data (numpy.ndarray): Audio data array
            sample_rate (int): Sample rate of the audio
            
        Returns:
            dict: Classification results with confidence scores
        """
        try:
            if self.model is None:
                return {'class': 'unknown', 'confidence': 0.0}
                
            # Convert to tensor and add batch dimension
            audio_tensor = torch.from_numpy(audio_data).float()
            if len(audio_tensor.shape) == 1:
                audio_tensor = audio_tensor.unsqueeze(0)
                
            # Get model prediction
            with torch.no_grad():
                outputs = self.model(audio_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                predicted_class = torch.argmax(probabilities, dim=1).item()
                confidence = probabilities[0][predicted_class].item()
                
            return {
                'class': self.sound_classes[predicted_class],
                'confidence': confidence,
                'all_probabilities': {
                    class_name: prob.item()
                    for class_name, prob in zip(self.sound_classes, probabilities[0])
                }
            }
            
        except Exception as e:
            logger.error(f"Error classifying sound: {e}")
            return {'class': 'unknown', 'confidence': 0.0}
            
    def detect_activity_change(self, current_activity, previous_activity):
        """
        Detect significant changes in user activity.
        
        Args:
            current_activity (dict): Current activity classification
            previous_activity (dict): Previous activity classification
            
        Returns:
            dict: Activity change information
        """
        if not current_activity or not previous_activity:
            return None
            
        # Check if there's a significant change in activity
        if (current_activity['class'] != previous_activity['class'] and
            current_activity['confidence'] > 0.7):
            return {
                'type': 'activity_change',
                'from': previous_activity['class'],
                'to': current_activity['class'],
                'confidence': current_activity['confidence']
            }
            
        return None
        
    def should_act_proactively(self, activity_change, user_preferences):
        """
        Determine if Aura should act proactively based on activity changes.
        
        Args:
            activity_change (dict): Detected activity change
            user_preferences (dict): User preferences and settings
            
        Returns:
            dict: Proactive action recommendation
        """
        if not activity_change:
            return None
            
        # Define proactive actions based on activity changes
        proactive_rules = {
            'doorbell': {
                'action': 'notify',
                'message': 'Someone is at the door!'
            },
            'glass_breaking': {
                'action': 'alert',
                'message': 'Possible break-in detected!'
            },
            'baby_crying': {
                'action': 'notify',
                'message': 'Baby is crying, would you like me to play lullaby music?'
            },
            'dog_barking': {
                'action': 'notify',
                'message': 'Your dog is barking, would you like me to check the security camera?'
            }
        }
        
        # Check if we should act based on the activity change
        if activity_change['to'] in proactive_rules:
            rule = proactive_rules[activity_change['to']]
            
            # Check user preferences for this type of notification
            if user_preferences.get('notifications', {}).get(activity_change['to'], True):
                return {
                    'action': rule['action'],
                    'message': rule['message'],
                    'confidence': activity_change['confidence']
                }
                
        return None
        
    def get_ambient_sound_level(self, audio_data):
        """
        Calculate the ambient sound level in the audio data.
        
        Args:
            audio_data (numpy.ndarray): Audio data array
            
        Returns:
            float: Sound level in decibels
        """
        try:
            # Calculate RMS value
            rms = np.sqrt(np.mean(np.square(audio_data)))
            
            # Convert to decibels
            if rms > 0:
                db = 20 * np.log10(rms)
            else:
                db = -100  # Silence
                
            return db
            
        except Exception as e:
            logger.error(f"Error calculating sound level: {e}")
            return 0.0 