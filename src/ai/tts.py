# Text-to-Speech (TTS) module
import edge_tts
import asyncio
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal
from pydub import AudioSegment
from pydub.playback import play
import threading

class TextToSpeech(QObject):
    amplitude = pyqtSignal(float)  # For lip-sync

    def __init__(self, voice="en-US-JennyNeural"):
        """
        Initialize the Edge-TTS module for text-to-speech.
        :param voice: The voice to use for speech synthesis.
        """
        super().__init__()
        self.voice = voice

    async def speak(self, text):
        """
        Convert text to speech, save as audio, and play with amplitude emission.
        """
        try:
            communicate = edge_tts.Communicate(text, voice=self.voice)
            await communicate.save("output.mp3")
            print("Speech synthesis complete: output.mp3")
            self.play_and_emit_amplitude("output.mp3")
        except Exception as e:
            print(f"Error in TTS: {e}")

    def play_and_emit_amplitude(self, audio_path):
        """Play audio and emit amplitude for lip-sync."""
        def _play():
            audio = AudioSegment.from_file(audio_path)
            samples = np.array(audio.get_array_of_samples())
            frame_size = int(audio.frame_rate * 0.03)  # 30ms frames
            for i in range(0, len(samples), frame_size):
                frame = samples[i:i+frame_size]
                if len(frame) == 0:
                    continue
                amplitude = np.abs(frame).mean() / (2 ** (audio.sample_width * 8 - 1))
                self.amplitude.emit(float(amplitude))
                play(AudioSegment(frame.tobytes(), frame_rate=audio.frame_rate, sample_width=audio.sample_width, channels=audio.channels))
            self.amplitude.emit(0.0)
        threading.Thread(target=_play, daemon=True).start()
