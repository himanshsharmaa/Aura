# NLP and Llama 2 integration

import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from utils.logger import setup_logger

logger = setup_logger(__name__)

class Llama2:
    def __init__(self, model_path="gpt2"):
        """
        Initialize the language model for natural language processing.
        
        Args:
            model_path (str): Path to the model or Hugging Face model ID
        """
        try:
            logger.info(f"Loading language model from {model_path}")
            self.tokenizer = GPT2Tokenizer.from_pretrained(model_path)
            self.model = GPT2LMHeadModel.from_pretrained(
                model_path,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            logger.info("Language model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading language model: {e}")
            raise

    def generate_response(self, user_input, max_length=200):
        """
        Generate a response using the language model.
        
        Args:
            user_input (str): The user's input text
            max_length (int): Maximum length of the generated response
            
        Returns:
            str: Generated response
        """
        try:
            # Prepare the input prompt
            prompt = f"User: {user_input}\nAura:"
            
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=max_length,
                    num_return_sequences=1,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode and clean up response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = response.replace(prompt, "").strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble processing that right now."
