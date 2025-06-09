# Configuration management 

import json
import os
from pathlib import Path
from utils.logger import setup_logger

logger = setup_logger(__name__)

class Config:
    def __init__(self, config_path="config.json"):
        """
        Initialize configuration manager.
        
        Args:
            config_path (str): Path to the configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self):
        """Load configuration from file or create default if not exists."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                # Create default configuration
                default_config = {
                    "llama_model_path": "models/llama2",
                    "sound_classifier_path": "models/sound_classifier.pt",
                    "database_path": "data/aura.db",
                    "wake_word": "hey aura",
                    "voice": "en-US-JennyNeural",
                    "audio": {
                        "sample_rate": 16000,
                        "channels": 1,
                        "chunk_size": 1024
                    },
                    "camera": {
                        "enabled": True,
                        "device_id": 0
                    },
                    "logging": {
                        "level": "INFO",
                        "file": "logs/aura.log"
                    },
                    "personality": {
                        "name": "Aura",
                        "traits": ["friendly", "helpful", "empathetic"],
                        "memory_retention_days": 30
                    }
                }
                
                # Create config directory if it doesn't exist
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                
                # Save default configuration
                with open(self.config_path, 'w') as f:
                    json.dump(default_config, f, indent=4)
                    
                logger.info(f"Created default configuration at {self.config_path}")
                return default_config
                
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return {}
            
    def get(self, key, default=None):
        """
        Get a configuration value.
        
        Args:
            key (str): Configuration key
            default: Default value if key not found
            
        Returns:
            The configuration value or default
        """
        try:
            # Handle nested keys (e.g., "audio.sample_rate")
            keys = key.split('.')
            value = self.config
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
            
    def set(self, key, value):
        """
        Set a configuration value.
        
        Args:
            key (str): Configuration key
            value: Value to set
        """
        try:
            # Handle nested keys
            keys = key.split('.')
            config = self.config
            for k in keys[:-1]:
                config = config.setdefault(k, {})
            config[keys[-1]] = value
            
            # Save to file
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
                
        except Exception as e:
            logger.error(f"Error setting configuration: {e}")
            
    def update(self, updates):
        """
        Update multiple configuration values.
        
        Args:
            updates (dict): Dictionary of updates
        """
        try:
            self.config.update(updates)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            
    def validate(self):
        """
        Validate the configuration.
        
        Returns:
            bool: True if configuration is valid
        """
        required_keys = [
            "llama_model_path",
            "sound_classifier_path",
            "database_path",
            "wake_word",
            "voice"
        ]
        
        try:
            for key in required_keys:
                if key not in self.config:
                    logger.error(f"Missing required configuration key: {key}")
                    return False
            return True
        except Exception as e:
            logger.error(f"Error validating configuration: {e}")
            return False 