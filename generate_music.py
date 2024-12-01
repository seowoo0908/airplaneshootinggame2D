import pygame
import numpy as np
from scipy.io import wavfile

# Create retro arcade music
def generate_arcade_music():
    # Sample rate and duration
    sample_rate = 44100
    duration = 8.0  # 8 seconds loop
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Base melody (simple arcade tune)
    melody_freq = [440, 523.25, 659.25, 783.99]  # A4, C5, E5, G5
    melody = np.zeros_like(t)
    
    # Create melody pattern
    for i, freq in enumerate(melody_freq):
        start = i * duration / len(melody_freq)
        end = (i + 1) * duration / len(melody_freq)
        mask = (t >= start) & (t < end)
        melody[mask] = 0.3 * np.sin(2 * np.pi * freq * t[mask])
    
    # Add some bass
    bass_freq = 220  # A3
    bass = 0.2 * np.sin(2 * np.pi * bass_freq * t)
    
    # Combine melody and bass
    music = melody + bass
    
    # Normalize
    music = np.int16(music * 32767)
    
    # Save as WAV file
    wavfile.write('assets/sounds/background.wav', sample_rate, music)

if __name__ == "__main__":
    generate_arcade_music()
