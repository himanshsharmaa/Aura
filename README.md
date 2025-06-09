# Aura - AI Companion

Aura is a human-like AI companion designed to interact naturally with users, adapt to their emotional state, and evolve over time. It uses cutting-edge AI technologies to provide voice-based communication, emotional intelligence, and dynamic responses.

## Features

- **Voice Interaction**
  - Speech-to-Text using Whisper
  - Text-to-Speech using Edge-TTS
  - Hotword detection with "Hey Aura"

- **Emotion Detection**
  - Voice tone analysis
  - Facial expression recognition
  - Combined emotion understanding

- **Memory and Personalization**
  - Stores user preferences and past interactions
  - Learns from conversations
  - Adapts responses based on history

- **Context Awareness**
  - Environmental sound classification
  - Proactive behavior based on context
  - Activity monitoring

## Prerequisites

- Python 3.8 or higher
- CUDA-capable GPU (recommended for optimal performance)
- Microphone
- Webcam (optional, for facial emotion detection)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/aura.git
cd aura
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download required models:
   - Llama 2 model (requires Hugging Face access)
   - Sound classification model (will be downloaded automatically)

## Configuration

1. Create a `config.json` file in the project root:
```json
{
    "llama_model_path": "path/to/llama2/model",
    "sound_classifier_path": "models/sound_classifier.pt",
    "database_path": "data/aura.db",
    "wake_word": "hey aura",
    "voice": "en-US-JennyNeural"
}
```

2. Set up environment variables (optional):
```bash
export AURA_API_KEY=your_api_key  # If using cloud services
```

## Usage

1. Start Aura:
```bash
python src/main.py
```

2. Activate Aura by saying "Hey Aura"

3. Interact naturally with voice commands

## Project Structure

```
aura/
├── src/
│   ├── ai/
│   │   ├── stt.py          # Speech-to-Text
│   │   ├── tts.py          # Text-to-Speech
│   │   ├── nlp.py          # Llama 2 integration
│   │   ├── emotion.py      # Emotion detection
│   │   ├── personality.py  # Memory and personalization
│   │   └── user_activity.py # Sound classification
│   ├── tasks/
│   │   └── alarms.py       # Hotword detection
│   ├── utils/
│   │   ├── config.py       # Configuration
│   │   └── logger.py       # Logging
│   └── main.py             # Main entry point
├── tests/                  # Unit tests
├── data/                   # Data storage
├── models/                 # Model files
├── logs/                   # Log files
├── requirements.txt        # Dependencies
└── README.md              # Documentation
```

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Adding New Features
1. Create a new module in the appropriate directory
2. Add unit tests
3. Update the main pipeline in `main.py`
4. Update documentation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI Whisper for speech recognition
- Microsoft Edge-TTS for text-to-speech
- Picovoice for hotword detection
- Meta AI for Llama 2
- DeepFace for facial emotion recognition

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.
