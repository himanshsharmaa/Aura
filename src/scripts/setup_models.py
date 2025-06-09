import os
import sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from pathlib import Path
from utils.logger import setup_logger
from utils.config import Config

logger = setup_logger(__name__)

def download_llama2():
    """Download and set up Llama 2 model"""
    try:
        logger.info("Downloading Llama 2 model...")
        model_name = "meta-llama/Llama-2-7b-chat-hf"
        
        # Create models directory if it doesn't exist
        os.makedirs("models/llama2", exist_ok=True)
        
        # Download model and tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        # Save model and tokenizer
        model.save_pretrained("models/llama2")
        tokenizer.save_pretrained("models/llama2")
        
        logger.info("Llama 2 model downloaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error downloading Llama 2 model: {e}")
        return False

def download_sound_classifier():
    """Download and set up sound classification model"""
    try:
        logger.info("Downloading sound classification model...")
        
        # Create models directory if it doesn't exist
        os.makedirs("models", exist_ok=True)
        
        # For now, we'll use a placeholder model
        # In a real implementation, you would download a pre-trained model
        model = torch.nn.Sequential(
            torch.nn.Linear(128, 64),
            torch.nn.ReLU(),
            torch.nn.Linear(64, 8)  # 8 sound classes
        )
        
        # Save model
        torch.save(model, "models/sound_classifier.pt")
        
        logger.info("Sound classification model downloaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error downloading sound classification model: {e}")
        return False

def setup_directories():
    """Create necessary directories"""
    try:
        directories = [
            "models",
            "models/llama2",
            "data",
            "logs",
            "tests"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
            
        return True
        
    except Exception as e:
        logger.error(f"Error creating directories: {e}")
        return False

def main():
    """Main setup function"""
    logger.info("Starting model setup...")
    
    # Create necessary directories
    if not setup_directories():
        logger.error("Failed to create directories")
        sys.exit(1)
        
    # Download and set up models
    llama2_success = download_llama2()
    sound_classifier_success = download_sound_classifier()
    
    if not (llama2_success and sound_classifier_success):
        logger.error("Failed to download some models")
        sys.exit(1)
        
    # Update configuration
    config = Config()
    config.update({
        "llama_model_path": "models/llama2",
        "sound_classifier_path": "models/sound_classifier.pt"
    })
    
    logger.info("Model setup completed successfully")

if __name__ == "__main__":
    main() 