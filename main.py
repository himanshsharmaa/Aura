import pygame
import numpy as np
import sounddevice as sd
import speech_recognition as sr
import threading

# Pygame Setup
pygame.init()
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Audio Configuration
SAMPLE_RATE = 44100  
CHUNK = 1024  

# Initialize Speech Recognizer
recognizer = sr.Recognizer()
mic = sr.Microphone()

# Reactor Orb State
intensity = 0.1
triggered = False  # Only pulse if "Aura" is detected

# Function to process real-time audio
def audio_callback(indata, frames, time, status):
    global intensity
    if triggered:  # Only react when "Aura" is detected
        volume = np.linalg.norm(indata)  
        intensity = min(max(volume, 0.1), 1.0)  

# Function to recognize "Aura" in background
def listen_for_aura():
    global triggered
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)  # Reduce background noise
    while True:
        try:
            with mic as source:
                print("Listening for 'Aura'...")
                audio = recognizer.listen(source)
                text = recognizer.recognize_google(audio).lower()
                print(f"Detected: {text}")
                if "aura" in text:
                    triggered = True  # Activate reactor orb
                    print("Aura detected! Reactor Activated.")
        except sr.UnknownValueError:
            pass  # Ignore unrecognized speech
        except sr.RequestError:
            print("Speech recognition service error.")

# Start Speech Recognition in a Separate Thread
threading.Thread(target=listen_for_aura, daemon=True).start()

# Start Audio Stream (Runs in Background)
stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=SAMPLE_RATE, blocksize=CHUNK)
stream.start()

# Main Loop
running = True
while running:
    screen.fill((0, 0, 0))  # Clear screen

    # Draw Reactor Orb
    color = (0, int(150 + intensity * 100), 255)  
    radius = int(100 + intensity * 50)  
    pygame.draw.circle(screen, color, (WIDTH // 2, HEIGHT // 2), radius)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
    clock.tick(60)  # High FPS for smooth animation

# Cleanup
stream.stop()
stream.close()
pygame.quit()
