from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QSpinBox, QCheckBox,
    QGroupBox, QFormLayout, QColorDialog, QSlider,
    QLineEdit, QFileDialog
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
import json
import os

class SettingsPanel(QWidget):
    settings_changed = pyqtSignal(dict)  # Signal when settings are changed
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Appearance settings
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QFormLayout()
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "System"])
        self.theme_combo.currentTextChanged.connect(self.on_settings_changed)
        appearance_layout.addRow("Theme:", self.theme_combo)
        
        # Accent color
        self.accent_color = QPushButton()
        self.accent_color.setFixedSize(50, 20)
        self.accent_color.clicked.connect(self.choose_accent_color)
        appearance_layout.addRow("Accent Color:", self.accent_color)
        
        # Font size
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setValue(14)
        self.font_size.valueChanged.connect(self.on_settings_changed)
        appearance_layout.addRow("Font Size:", self.font_size)
        
        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)
        
        # Behavior settings
        behavior_group = QGroupBox("Behavior")
        behavior_layout = QFormLayout()
        
        # Proactive interaction
        self.proactive_check = QCheckBox()
        self.proactive_check.setChecked(True)
        self.proactive_check.stateChanged.connect(self.on_settings_changed)
        behavior_layout.addRow("Enable Proactive Interaction:", self.proactive_check)
        
        # Interaction frequency
        self.interaction_freq = QSlider(Qt.Horizontal)
        self.interaction_freq.setRange(1, 60)
        self.interaction_freq.setValue(5)
        self.interaction_freq.valueChanged.connect(self.on_settings_changed)
        behavior_layout.addRow("Interaction Frequency (minutes):", self.interaction_freq)
        
        # Voice settings
        self.voice_combo = QComboBox()
        self.voice_combo.addItems(["Default", "Male", "Female"])
        self.voice_combo.currentTextChanged.connect(self.on_settings_changed)
        behavior_layout.addRow("Voice:", self.voice_combo)
        
        # Speech rate
        self.speech_rate = QSlider(Qt.Horizontal)
        self.speech_rate.setRange(50, 200)
        self.speech_rate.setValue(100)
        self.speech_rate.valueChanged.connect(self.on_settings_changed)
        behavior_layout.addRow("Speech Rate (%):", self.speech_rate)
        
        behavior_group.setLayout(behavior_layout)
        layout.addWidget(behavior_group)
        
        # Privacy settings
        privacy_group = QGroupBox("Privacy")
        privacy_layout = QFormLayout()
        
        # Data collection
        self.data_collection = QCheckBox()
        self.data_collection.setChecked(True)
        self.data_collection.stateChanged.connect(self.on_settings_changed)
        privacy_layout.addRow("Enable Data Collection:", self.data_collection)
        
        # Conversation history
        self.save_history = QCheckBox()
        self.save_history.setChecked(True)
        self.save_history.stateChanged.connect(self.on_settings_changed)
        privacy_layout.addRow("Save Conversation History:", self.save_history)
        
        # Data location
        self.data_location = QLineEdit()
        self.data_location.setReadOnly(True)
        self.data_location.setText("data/")
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.choose_data_location)
        data_location_layout = QHBoxLayout()
        data_location_layout.addWidget(self.data_location)
        data_location_layout.addWidget(browse_button)
        privacy_layout.addRow("Data Location:", data_location_layout)
        
        privacy_group.setLayout(privacy_layout)
        layout.addWidget(privacy_group)
        
        # Save/Reset buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)
        
        self.reset_button = QPushButton("Reset to Default")
        self.reset_button.clicked.connect(self.reset_settings)
        button_layout.addWidget(self.reset_button)
        
        layout.addLayout(button_layout)
        
        # Set dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
                color: white;
            }
            QGroupBox {
                border: 1px solid #3C3C3C;
                border-radius: 5px;
                margin-top: 1em;
                padding-top: 1em;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QComboBox, QSpinBox, QLineEdit {
                background-color: #2C2C2C;
                color: white;
                border: 1px solid #3C3C3C;
                border-radius: 3px;
                padding: 2px;
            }
            QCheckBox {
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
        """)
        
    def choose_accent_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.accent_color.setStyleSheet(f"background-color: {color.name()}")
            self.on_settings_changed()
            
    def choose_data_location(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "Choose Data Directory",
            self.data_location.text()
        )
        if directory:
            self.data_location.setText(directory)
            self.on_settings_changed()
            
    def on_settings_changed(self):
        settings = self.get_current_settings()
        self.settings_changed.emit(settings)
        
    def get_current_settings(self) -> dict:
        return {
            'appearance': {
                'theme': self.theme_combo.currentText(),
                'accent_color': self.accent_color.styleSheet().split(':')[1].strip(),
                'font_size': self.font_size.value()
            },
            'behavior': {
                'proactive': self.proactive_check.isChecked(),
                'interaction_frequency': self.interaction_freq.value(),
                'voice': self.voice_combo.currentText(),
                'speech_rate': self.speech_rate.value()
            },
            'privacy': {
                'data_collection': self.data_collection.isChecked(),
                'save_history': self.save_history.isChecked(),
                'data_location': self.data_location.text()
            }
        }
        
    def save_settings(self):
        settings = self.get_current_settings()
        with open('data/settings.json', 'w') as f:
            json.dump(settings, f, indent=4)
            
    def load_settings(self):
        try:
            with open('data/settings.json', 'r') as f:
                settings = json.load(f)
                
            # Apply appearance settings
            self.theme_combo.setCurrentText(settings['appearance']['theme'])
            self.accent_color.setStyleSheet(f"background-color: {settings['appearance']['accent_color']}")
            self.font_size.setValue(settings['appearance']['font_size'])
            
            # Apply behavior settings
            self.proactive_check.setChecked(settings['behavior']['proactive'])
            self.interaction_freq.setValue(settings['behavior']['interaction_frequency'])
            self.voice_combo.setCurrentText(settings['behavior']['voice'])
            self.speech_rate.setValue(settings['behavior']['speech_rate'])
            
            # Apply privacy settings
            self.data_collection.setChecked(settings['privacy']['data_collection'])
            self.save_history.setChecked(settings['privacy']['save_history'])
            self.data_location.setText(settings['privacy']['data_location'])
            
        except (FileNotFoundError, json.JSONDecodeError):
            # Use default settings if file doesn't exist or is invalid
            self.reset_settings()
            
    def reset_settings(self):
        # Reset to default values
        self.theme_combo.setCurrentText("Dark")
        self.accent_color.setStyleSheet("background-color: #4CAF50")
        self.font_size.setValue(14)
        
        self.proactive_check.setChecked(True)
        self.interaction_freq.setValue(5)
        self.voice_combo.setCurrentText("Default")
        self.speech_rate.setValue(100)
        
        self.data_collection.setChecked(True)
        self.save_history.setChecked(True)
        self.data_location.setText("data/")
        
        self.on_settings_changed() 