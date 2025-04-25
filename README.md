<h1 align="center">🌟 Aura - Your AI Companion</h1>

<p align="center">
  <strong>Aura</strong> is an advanced real-time voice-based AI companion that interacts like a human. From emotional awareness to memory retention, Aura grows and evolves with you—becoming your smart, responsive digital friend.
</p>

<div align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=22&pause=1000&color=FF69B4&center=true&vCenter=true&width=435&lines=Real-Time+Voice+AI;Emotion+Aware+and+Responsive;Listens%2C+Learns%2C+Talks" alt="Typing SVG">
</div>

------

<h2 align="left">🌌 Vision</h2>
<p>
Aura is designed to be an intuitive and emotionally intelligent AI that users can talk to naturally, like a real person. It listens to your voice, understands your tone and emotions, learns from your habits, and speaks back with human-like voice and behavior.
</p>

<h2 align="left">✨ Features</h2>
<ul>
  <li><strong>🎤 Speech-to-Text:</strong> Convert voice into text using Whisper or Vosk for command recognition.</li>
  <li><strong>🗣️ Text-to-Speech:</strong> Speak back in natural human voice using Edge-TTS or Coqui TTS.</li>
  <li><strong>🧠 Conversational AI:</strong> Smart, LLaMA-2-powered dialog engine for dynamic responses.</li>
  <li><strong>😮 Emotion Detection:</strong> Recognize emotions via voice and facial expression (Librosa + DeepFace).</li>
  <li><strong>📕 Long-Term Memory:</strong> Personalized memory powered by SQLite, evolving over time.</li>
  <li><strong>🚨 Wake Word Detection:</strong> Always listening for "Hey Aura" via Porcupine engine.</li>
  <li><strong>🌍 Context Awareness:</strong> Detect environmental sounds and respond appropriately.</li>
  <li><strong>🎨 Visual UI:</strong> Avatar or facial GUI that reacts to emotions and speech.</li>
</ul>

<h2 align="left">🔧 Tech Stack</h2>
<p align="left">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white"/>
  <img src="https://img.shields.io/badge/HuggingFace-FFB000?style=for-the-badge&logo=huggingface&logoColor=white"/>
  <img src="https://img.shields.io/badge/Edge--TTS-blueviolet?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Whisper-brightgreen?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Tkinter_UI-FF69B4?style=for-the-badge"/>
</p>

<h2 align="left">📁 Project Structure</h2>
<pre>
Aura/
├── assets/              # Avatars, voices, visuals
├── config/              # Hugging Face keys, settings
├── data/                # Memory, logs, saved preferences
├── models/              # Local model files
├── modules/
│   ├── stt.py           # Speech recognition logic
│   ├── tts.py           # Voice synthesis logic
│   ├── emotion.py       # Emotion analysis
│   ├── memory.py        # Persistent memory
│   └── conversation.py  # AI chat engine
├── ui/
│   └── main_window.py   # Face or animated UI
├── main.py              # Launcher for Aura
└── requirements.txt     # Dependencies
</pre>

<h2 align="left">🚀 Installation</h2>
<ol>
  <li>Clone the project:
    <pre><code>git clone https://github.com/yourusername/aura-ai.git
cd aura-ai</code></pre>
  </li>
  <li>Create and activate virtual environment:
    <pre><code>python -m venv venv
venv\Scripts\activate</code></pre>
  </li>
  <li>Install dependencies:
    <pre><code>pip install -r requirements.txt</code></pre>
  </li>
  <li>Launch Aura:
    <pre><code>python main.py</code></pre>
  </li>
</ol>

<h2 align="left">🌀 Future Enhancements</h2>
<ul>
  <li><strong>3D Facial Sync</strong>: Lip sync and facial reaction synced with emotion and text.</li>
  <li><strong>Music & Sound Generation</strong>: Generate voice-based or emotion-driven music.</li>
  <li><strong>AR Mode</strong>: Real-world interaction overlay using webcam and visual detection.</li>
  <li><strong>Cloud Memory</strong>: User memories synced across devices with secure cloud access.</li>
</ul>

<h2 align="left">👍 Contribution</h2>
<p>
  Contributions are welcome! Please fork the repository and submit a pull request with detailed explanation of your changes.
</p>

<h2 align="left">📅 License</h2>
<p>
  Licensed under the <strong>MIT License</strong>. See <code>LICENSE</code> file for more info.
</p>

<h2 align="left">📧 Contact</h2>
<p>
  Email: <a href="mailto:aura.dev@yourmail.com">aura.dev@yourmail.com</a>
</p>

------

Made with ❤️ by <a href="https://github.com/keplor-io">Keplor.Io</a>
