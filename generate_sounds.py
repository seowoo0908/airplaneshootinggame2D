import wave
import math
import struct
import os
import random

def generate_shoot_sound():
    # Audio parameters
    sample_rate = 44100
    duration = 0.1  # seconds
    
    # Generate retro shoot sound (descending pitch)
    nframes = int(duration * sample_rate)
    sound_data = []
    for x in range(nframes):
        t = float(x) / sample_rate
        # Start at higher frequency and descend
        frequency = 2000 - (t / duration) * 1000
        # Square wave for more retro sound
        value = 32767.0 * (1.0 - t/duration) * (1 if math.sin(2.0 * math.pi * frequency * t) > 0 else -1)
        sound_data.append(struct.pack('h', int(value)))
    
    sound_data = b''.join(sound_data)
    
    with wave.open('assets/sounds/shoot.wav', 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(sound_data)

def generate_explosion_sound():
    # Audio parameters
    sample_rate = 44100
    duration = 0.4  # seconds
    
    # Generate retro explosion sound
    nframes = int(duration * sample_rate)
    sound_data = []
    
    for x in range(nframes):
        t = float(x) / sample_rate
        # Multiple frequencies for richer sound
        f1 = 100 - (t / duration) * 50  # Low frequency descending
        f2 = 300 - (t / duration) * 200  # Mid frequency descending
        
        # Mix frequencies with noise
        value = 32767.0 * (1.0 - t/duration) * (
            0.7 * (1 if math.sin(2.0 * math.pi * f1 * t) > 0 else -1) +
            0.3 * (1 if math.sin(2.0 * math.pi * f2 * t) > 0 else -1) +
            0.4 * (2 * random.random() - 1)
        )
        
        sound_data.append(struct.pack('h', int(max(-32767, min(32767, value)))))
    
    sound_data = b''.join(sound_data)
    
    with wave.open('assets/sounds/explosion.wav', 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(sound_data)

if __name__ == "__main__":
    # Ensure sounds directory exists
    os.makedirs('assets/sounds', exist_ok=True)
    
    # Generate sound effects
    generate_shoot_sound()
    generate_explosion_sound()
    print("Retro arcade sound effects generated successfully!")
