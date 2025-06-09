# Alarms module

import pvporcupine
import pyaudio
import os
from utils.logger import setup_logger

logger = setup_logger(__name__)

class HotwordDetector:
    def __init__(self, keyword="hey aura", access_key=None):
        """
        Initialize the Porcupine hotword detection.
        :param keyword: The wake word to listen for.
        :param access_key: Picovoice access key for Porcupine.
        """
        if not access_key:
            logger.warning("No Picovoice access key provided. Hotword detection will be disabled.")
            self.porcupine = None
            self.audio_stream = None
            return

        try:
            self.porcupine = pvporcupine.create(
                access_key=access_key,
                keywords=[keyword]
            )
            self.audio_stream = None
        except Exception as e:
            logger.error(f"Error initializing Porcupine: {e}")
            self.porcupine = None
            self.audio_stream = None

    def start_listening(self):
        """
        Start listening for the wake word.
        """
        if not self.porcupine:
            logger.warning("Hotword detection is disabled. Skipping wake word detection.")
            return

        try:
            pa = pyaudio.PyAudio()
            self.audio_stream = pa.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length,
            )
            logger.info("Listening for hotword...")

            while True:
                pcm = self.audio_stream.read(self.porcupine.frame_length)
                if self.porcupine.process(pcm) >= 0:
                    logger.info("Hotword detected!")
                    break
        except Exception as e:
            logger.error(f"Error in hotword detection: {e}")
        finally:
            if self.audio_stream:
                self.audio_stream.close()
            if pa:
                pa.terminate()
