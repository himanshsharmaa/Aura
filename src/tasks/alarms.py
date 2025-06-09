# Alarms module

import pvporcupine
import pyaudio
import os
import json
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Load config
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'config.json')
try:
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
except Exception as e:
    logger.error(f"Could not load config: {e}")
    config = {}

class HotwordDetector:
    def __init__(self, keyword=None, access_key=None):
        if not keyword:
            keyword = config.get('hotword', 'aura')
        if not access_key:
            access_key = config.get('porcupine_access_key', None)
        if not access_key or access_key == 'YOUR_PICOVOICE_ACCESS_KEY_HERE':
            logger.warning("No valid Picovoice access key provided. Hotword detection will be disabled.")
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
            return False

        try:
            pa = pyaudio.PyAudio()
            self.audio_stream = pa.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length,
            )
            logger.info(f"Listening for hotword '{self.porcupine.keywords[0]}'...")

            while True:
                pcm = self.audio_stream.read(self.porcupine.frame_length)
                if self.porcupine.process(pcm) >= 0:
                    logger.info("Hotword detected!")
                    break
            return True
        except Exception as e:
            logger.error(f"Error in hotword detection: {e}")
            return False
        finally:
            if self.audio_stream:
                self.audio_stream.close()
            if 'pa' in locals():
                pa.terminate()
