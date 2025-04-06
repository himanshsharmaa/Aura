# Alarms module

import pvporcupine
import pyaudio

class HotwordDetector:
    def __init__(self, keyword="hey aura"):
        """
        Initialize the Porcupine hotword detection.
        :param keyword: The wake word to listen for.
        """
        self.porcupine = pvporcupine.create(keywords=[keyword])
        self.audio_stream = None

    def start_listening(self):
        """
        Start listening for the wake word.
        """
        pa = pyaudio.PyAudio()
        self.audio_stream = pa.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length,
        )
        print("Listening for hotword...")

        while True:
            pcm = self.audio_stream.read(self.porcupine.frame_length)
            if self.porcupine.process(pcm) >= 0:
                print("Hotword detected!")
                break
