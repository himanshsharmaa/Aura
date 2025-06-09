<h1 align="center">🤖 Aura - AI Companion</h1>

<p align="center">
  Aura is a human-like AI companion designed to interact naturally with users, adapt to their emotional state, and evolve over time. It leverages advanced AI technologies for voice-based communication, emotional intelligence, memory, and dynamic context awareness.
</p>

<div align="center">
    <img src="https://github.com/himanshsharmaa/Aura/blob/main/assets/img/aura_banner.png?raw=true" alt="Aura Banner" />
</div>

------

<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=22&pause=1000&color=4CAF50&center=true&vCenter=true&width=435&lines=Conversational+AI+Companion;Emotionally+Intelligent;Personalized+and+Proactive" alt="Typing SVG">
</p>

<h2 align="left">🌟 Features</h2>
<ul>
  <li><strong>Voice Interaction</strong>: Real-time speech-to-text (Whisper), text-to-speech (Edge-TTS), and hotword detection ("Hey Aura").</li>
  <li><strong>Emotion Detection</strong>: Voice tone analysis (librosa) and facial expression recognition (DeepFace) for adaptive responses.</li>
  <li><strong>Memory & Personalization</strong>: SQLite database for storing user preferences, routines, and conversation history.</li>
  <li><strong>Context Awareness</strong>: Advanced sound event detection using YAMNet (TensorFlow) for detecting unusual sounds (shouting, crying, pain, etc.).</li>
  <li><strong>Premium UI</strong>: Modern PyQt6-based interface with real-time audio visualizations and status updates.</li>
  <li><strong>Proactive Behaviors</strong>: Context-aware responses based on sound events and user state.</li>
  <li><strong>Parallel Processing</strong>: Hotword and sound event detection running simultaneously for enhanced responsiveness.</li>
</ul>

<h2 align="left">🔧 Tech Stack</h2>
<p align="left">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/PyQt6-41CD52?style=for-the-badge&logo=qt&logoColor=white"/>
  <img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white"/>
  <img src="https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white"/>
  <img src="https://img.shields.io/badge/Whisper-000000?style=for-the-badge&logo=openai&logoColor=white"/>
  <img src="https://img.shields.io/badge/Edge--TTS-0078D4?style=for-the-badge&logo=microsoft&logoColor=white"/>
  <img src="https://img.shields.io/badge/DeepFace-FF4081?style=for-the-badge&logo=face&logoColor=white"/>
  <img src="https://img.shields.io/badge/Librosa-1DB954?style=for-the-badge&logo=librosa&logoColor=white"/>
  <img src="https://img.shields.io/badge/Porcupine-FF6F00?style=for-the-badge&logo=picovoice&logoColor=white"/>
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white"/>
</p>

<h2 align="left">📂 Project Structure</h2>
<pre>
Aura/
│   .gitignore
│   README.md
│   requirements.txt
│   config.json
│
├───src
│   ├───ai
│   │       stt.py              # Speech-to-Text (Whisper)
│   │       tts.py              # Text-to-Speech (Edge-TTS)
│   │       nlp.py              # GPT-2 integration
│   │       emotion.py          # Emotion detection (librosa, DeepFace)
│   │       personality.py      # Memory & personalization logic
│   │       user_activity.py    # Sound classification & proactive behavior
│   ├───tasks
│   │       alarms.py           # Hotword detection (Porcupine)
│   ├───utils
│   │       config.py           # Configuration management
│   │       logger.py           # Logging utilities
│   ├───ui
│   │       main_window.py      # Main PyQt6 window
│   │       visualizations.py   # Audio visualizations
│   │       settings.py         # Settings panel
│   ├───data
│   │       aura.db            # SQLite database
│   └───main.py                # Main entry point
├───tests
│       test_stt.py
│       test_tts.py
│       test_emotion_detection.py
│       test_integration.py
├───models                      # Model files
├───logs                        # Log files
</pre>

<h2 align="left">🚀 Installation</h2>
<ol>
  <li>Clone the repository:
    <pre><code>git clone https://github.com/himanshsharmaa/Aura.git
cd Aura</code></pre>
  </li>
  <li>Create a virtual environment:
    <pre><code>python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
</code></pre>
  </li>
  <li>Install dependencies:
    <pre><code>pip install -r requirements.txt</code></pre>
  </li>
  <li>Set up required API keys:
    <ul>
      <li>Get a free Picovoice access key from <a href="https://console.picovoice.ai/">Picovoice Console</a></li>
      <li>Get a Hugging Face token for model downloads</li>
    </ul>
  </li>
</ol>

<h2 align="left">⚙️ Configuration</h2>
<ol>
  <li>Create a <code>config.json</code> file in the project root:
    <pre><code>{
  "hotword": "aura",
  "porcupine_access_key": "YOUR_PICOVOICE_ACCESS_KEY",
  "sound_events": {
    "shouting": true,
    "crying": true,
    "pain": true,
    "sensitivity": 0.7
  },
  "ui": {
    "theme": "dark",
    "colors": {
      "primary": "#4CAF50",
      "secondary": "#2196F3",
      "background": "#1E1E1E"
    }
  },
  "proactive_behaviors": {
    "sound_events": true,
    "emotion_detection": true
  }
}</code></pre>
  </li>
</ol>

<h2 align="left">💡 Usage</h2>
<ol>
  <li>Start Aura:
    <pre><code>python src/main.py</code></pre>
  </li>
  <li>Activate Aura by either:
    <ul>
      <li>Saying "Hey Aura" (requires Picovoice access key)</li>
      <li>Detecting unusual sounds (shouting, crying, pain)</li>
    </ul>
  </li>
  <li>Interact through the modern UI or voice commands</li>
  <li>Monitor real-time audio visualizations and status updates</li>
</ol>

<h2 align="left">📁 File Descriptions</h2>
<ul>
  <li><code>src/ai/</code>: Core AI modules (STT, TTS, NLP, emotion, memory, sound classification).</li>
  <li><code>src/tasks/</code>: Hotword detection and scheduled tasks.</li>
  <li><code>src/utils/</code>: Configuration and logging utilities.</li>
  <li><code>src/ui/</code>: User interface modules (main window, visualizations, settings).</li>
  <li><code>src/data/</code>: User memory and preferences (to be migrated to SQLite).</li>
  <li><code>src/main.py</code>: Main entry point for Aura.</li>
  <li><code>models/</code>: Pre-trained models (Llama 2, sound classifiers, etc.).</li>
  <li><code>tests/</code>: Unit and integration tests.</li>
  <li><code>logs/</code>: Log files for debugging and monitoring.</li>
</ul>

<h2 align="left">🔮 Future Enhancements</h2>
<ul>
  <li><strong>Visual UI</strong>: Animated avatar or face for expressive interaction.</li>
  <li><strong>Cloud Sync</strong>: Synchronize memory and preferences across devices.</li>
  <li><strong>Mobile App</strong>: Native mobile application for on-the-go interaction.</li>
  <li><strong>Multi-language Support</strong>: Support for multiple languages and voices.</li>
  <li><strong>Advanced Analytics</strong>: Insights into user engagement and emotional trends.</li>
</ul>

<h2 align="left">📝 License</h2>
<p align="left">This project is licensed under the <strong>MIT License</strong>.</p>

<h2 align="left">🤝 Contributing</h2>
<p>
  Contributions are welcome! Please open an issue or submit a pull request.
</p>

<h2 align="left">📬 Contact</h2>
<p align="left">Feel free to reach out via <a href="mailto:himanshsharmaa@gmail.com">Email</a> or on <a href="https://github.com/himanshsharmaa">GitHub</a>.</p>

------

<p align="center">Made with ❤️ by <a href="https://github.com/himanshsharmaa">himanshsharmaa</a></p>
