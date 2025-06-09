# Sound Event Detection using YAMNet
import numpy as np
import tensorflow as tf
import librosa
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

class SoundEventDetector:
    def __init__(self, model_path=None, sensitivity=None):
        self.model = tf.keras.models.load_model(model_path or self._get_default_model())
        self.class_map = self._load_class_map()
        self.target_events = config.get('sound_events', ["Shout", "Scream", "Crying, sobbing", "Groan", "Pain"])
        self.sensitivity = sensitivity if sensitivity is not None else config.get('sound_event_sensitivity', 0.7)

    def _get_default_model(self):
        # Download YAMNet if not present
        yamnet_path = os.path.join(os.path.expanduser('~'), '.aura', 'yamnet.h5')
        if not os.path.exists(yamnet_path):
            import tensorflow_hub as hub
            model = hub.KerasLayer('https://tfhub.dev/google/yamnet/1')
            model.save(yamnet_path)
        return yamnet_path

    def _load_class_map(self):
        # YAMNet class map
        import requests
        url = 'https://raw.githubusercontent.com/tensorflow/models/master/research/audioset/yamnet/yamnet_class_map.csv'
        class_map_path = os.path.join(os.path.expanduser('~'), '.aura', 'yamnet_class_map.csv')
        if not os.path.exists(class_map_path):
            r = requests.get(url)
            os.makedirs(os.path.dirname(class_map_path), exist_ok=True)
            with open(class_map_path, 'wb') as f:
                f.write(r.content)
        class_map = {}
        with open(class_map_path, 'r') as f:
            for line in f.readlines()[1:]:
                idx, mid, name = line.strip().split(',')
                class_map[int(idx)] = name.strip('"')
        return class_map

    def detect(self, audio_path):
        try:
            wav, sr = librosa.load(audio_path, sr=16000)
            scores, embeddings, spectrogram = self.model(np.reshape(wav, [1, -1]))
            scores_np = scores.numpy().squeeze()
            top_class = np.argmax(scores_np)
            top_score = scores_np[top_class]
            event_name = self.class_map.get(top_class, "Unknown")
            logger.info(f"Detected sound event: {event_name} (score={top_score:.2f})")
            if event_name in self.target_events and top_score >= self.sensitivity:
                return event_name, top_score
            return None, top_score
        except Exception as e:
            logger.error(f"Error in sound event detection: {e}")
            return None, 0.0 