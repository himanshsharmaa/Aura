# NLP and Llama 2 integration

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_name = "meta-llama/Llama-2-7b-chat-hf"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
print("Model downloaded successfully!")

class Llama2:
    def __init__(self, model_path="meta-llama/Llama-2-7b-chat-hf", max_length=512):
        """
        Initialize the Llama 2 model and tokenizer.
        :param model_path: Path to the locally stored Llama 2 model.
        :param max_length: Maximum length of the generated response.
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.float16)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = self.model.to(self.device)
        self.max_length = max_length

    def generate_response(self, user_input, context=None):
        """
        Generate a personalized response using Llama 2.
        :param user_input: The user's input text.
        :param context: Additional context for personalization (optional).
        :return: Generated response as a string.
        """
        prompt = f"{context}\nUser: {user_input}\nAura:" if context else f"User: {user_input}\nAura:"
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(
            inputs["input_ids"],
            max_length=self.max_length,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=self.tokenizer.eos_token_id
        )
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response.split("Aura:")[-1].strip()
