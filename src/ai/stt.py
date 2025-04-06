# Speech-to-Text (STT) module
import whisper

class SpeechToText:
    def __init__(self, model_name="base"):
        """
        Initialize the Whisper model for speech-to-text.
        :param model_name: The Whisper model size (e.g., "base", "small", "medium").
        """
        self.model = whisper.load_model(model_name)

    def transcribe(self, audio_path):
        """
        Transcribe speech from an audio file.
        :param audio_path: Path to the audio file.
        :return: Transcribed text.
        """
        try:
            result = self.model.transcribe(audio_path)
            return result["text"]
        except Exception as e:
            print(f"Error in STT: {e}")
            return ""
