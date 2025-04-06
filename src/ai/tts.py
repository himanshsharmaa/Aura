# Text-to-Speech (TTS) module
import edge_tts
import asyncio

class TextToSpeech:
    def __init__(self, voice="en-US-JennyNeural"):
        """
        Initialize the Edge-TTS module for text-to-speech.
        :param voice: The voice to use for speech synthesis.
        """
        self.voice = voice

    async def speak(self, text):
        """
        Convert text to speech and save it as an audio file.
        :param text: The text to convert to speech.
        """
        try:
            communicate = edge_tts.Communicate(text, voice=self.voice)
            await communicate.save("output.mp3")
            print("Speech synthesis complete: output.mp3")
        except Exception as e:
            print(f"Error in TTS: {e}")
