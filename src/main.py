# Main entry point for Aura

import asyncio
from ai.stt import SpeechToText
from ai.tts import TextToSpeech
from ai.nlp import Llama2
from tasks.alarms import HotwordDetector

async def main():
    # Initialize modules
    stt = SpeechToText()
    tts = TextToSpeech()
    nlp = Llama2(model_path="path_to_llama2_model")
    hotword = HotwordDetector()

    # Start hotword detection
    hotword.start_listening()

    # Simulate audio input (replace with real-time audio capture)
    audio_path = "input_audio.wav"  # Replace with actual audio input
    user_input = stt.transcribe(audio_path)
    print(f"User said: {user_input}")

    # Generate response
    response = nlp.generate_response(user_input)
    print(f"Aura's Response: {response}")

    # Speak the response
    await tts.speak(response)

if __name__ == "__main__":
    asyncio.run(main())
