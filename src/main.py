# Main entry point for Aura

import asyncio
import pyaudio
import wave
import tempfile
import os
import cv2
import numpy as np
from ai.stt import SpeechToText
from ai.tts import TextToSpeech
from ai.nlp import Llama2
from ai.emotion import EmotionDetector
from ai.personality import Personality
from ai.user_activity import UserActivity
from tasks.alarms import HotwordDetector
from utils.logger import setup_logger

logger = setup_logger(__name__)

class Aura:
    def __init__(self):
        # Initialize core modules
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.nlp = Llama2(model_path="gpt2")
        self.hotword = HotwordDetector(access_key=None)
        self.emotion_detector = EmotionDetector()
        self.personality = Personality()
        self.user_activity = UserActivity()
        
        # Audio settings
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.RECORD_SECONDS = 5
        
        # Initialize PyAudio
        self.p = pyaudio.PyAudio()
        
        # Initialize camera if available
        self.camera = None
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                logger.warning("No camera available")
                self.camera = None
        except Exception as e:
            logger.error(f"Error initializing camera: {e}")
            self.camera = None
            
        # State tracking
        self.previous_activity = None
        self.is_active = True
        
    def record_audio(self):
        """Record audio from microphone"""
        try:
            stream = self.p.open(format=self.FORMAT,
                                channels=self.CHANNELS,
                                rate=self.RATE,
                                input=True,
                                frames_per_buffer=self.CHUNK)
            
            logger.info("Recording...")
            frames = []
            
            for _ in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
                data = stream.read(self.CHUNK)
                frames.append(data)
                
            logger.info("Recording finished")
            
            stream.stop_stream()
            stream.close()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                wf = wave.open(temp_file.name, 'wb')
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
                wf.setframerate(self.RATE)
                wf.writeframes(b''.join(frames))
                wf.close()
                return temp_file.name
                
        except Exception as e:
            logger.error(f"Error recording audio: {e}")
            return None
            
    def capture_frame(self):
        """Capture a frame from the camera"""
        if self.camera is None:
            return None
            
        try:
            ret, frame = self.camera.read()
            if ret:
                return frame
            return None
        except Exception as e:
            logger.error(f"Error capturing frame: {e}")
            return None
            
    async def process_interaction(self):
        """Process a single interaction cycle"""
        try:
            # Wait for hotword
            logger.info("Waiting for wake word...")
            self.hotword.start_listening()
            
            # Record user input
            audio_file = self.record_audio()
            if not audio_file:
                return
                
            # Analyze emotions
            voice_emotion = self.emotion_detector.analyze_voice(audio_file)
            face_emotion = None
            
            # Capture and analyze facial expression if camera is available
            frame = self.capture_frame()
            if frame is not None:
                face_emotion = self.emotion_detector.analyze_face(frame=frame)
                
            # Combine emotion analysis
            emotion = self.emotion_detector.combine_emotions(voice_emotion, face_emotion)
            
            # Analyze user activity
            audio_data = np.frombuffer(open(audio_file, 'rb').read(), dtype=np.int16)
            current_activity = self.user_activity.classify_sound(audio_data)
            
            # Check for activity changes
            activity_change = self.user_activity.detect_activity_change(
                current_activity,
                self.previous_activity
            )
            self.previous_activity = current_activity
            
            # Check for proactive actions
            if activity_change:
                proactive_action = self.user_activity.should_act_proactively(
                    activity_change,
                    self.personality.get_preference('notifications', 'all')
                )
                if proactive_action:
                    await self.tts.speak(proactive_action['message'])
                    
            # Transcribe audio
            user_input = self.stt.transcribe(audio_file)
            logger.info(f"User said: {user_input}")
            
            # Clean up temporary audio file
            os.unlink(audio_file)
            
            if not user_input:
                logger.warning("No speech detected")
                return
                
            # Get recent interactions for context
            recent_interactions = self.personality.get_recent_interactions(limit=5)
            context = "\n".join([
                f"User: {i['user_input']}\nAura: {i['aura_response']}"
                for i in recent_interactions
            ])
            
            # Generate response
            response = self.nlp.generate_response(user_input)
            logger.info(f"Aura's Response: {response}")
            
            # Store interaction
            self.personality.store_interaction(
                user_input,
                response,
                emotion=emotion['emotion'] if emotion else None,
                context=context
            )
            
            # Speak the response
            await self.tts.speak(response)
            
        except Exception as e:
            logger.error(f"Error in interaction cycle: {e}")
            
    async def run(self):
        """Main loop for Aura"""
        logger.info("Starting Aura...")
        try:
            while self.is_active:
                await self.process_interaction()
        except KeyboardInterrupt:
            logger.info("Shutting down Aura...")
        finally:
            if self.camera is not None:
                self.camera.release()
            self.p.terminate()
            
    def shutdown(self):
        """Gracefully shutdown Aura"""
        self.is_active = False
        if self.camera is not None:
            self.camera.release()
        self.p.terminate()

async def main():
    aura = Aura()
    await aura.run()

if __name__ == "__main__":
    asyncio.run(main())
