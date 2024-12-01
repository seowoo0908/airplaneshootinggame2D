import numpy as np
from scipy.io import wavfile
import os

def generate_laser_sound():
    # Sample rate and duration
    sample_rate = 44100
    duration = 0.2
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # High-pitched laser sound with frequency sweep
    freq_start = 2000
    freq_end = 500
    frequency = np.linspace(freq_start, freq_end, len(t))
    laser = 0.5 * np.sin(2 * np.pi * frequency * t)
    
    # Add some "energy" effect
    energy = 0.3 * np.sin(2 * np.pi * 80 * t)
    
    # Combine and add envelope
    envelope = np.exp(-4 * t / duration)
    sound = (laser + energy) * envelope
    
    # Convert to 16-bit integer
    sound = np.int16(sound * 32767)
    
    # Save
    if not os.path.exists('assets/sounds'):
        os.makedirs('assets/sounds')
    wavfile.write('assets/sounds/shoot.wav', sample_rate, sound)

def generate_explosion_sound():
    # Sample rate and duration
    sample_rate = 44100
    duration = 0.5
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Base explosion (white noise with lowpass filter)
    noise = np.random.normal(0, 1, len(t))
    
    # Add some low frequency rumble
    rumble_freq = 30
    rumble = np.sin(2 * np.pi * rumble_freq * t)
    
    # Add some mid-frequency impact
    impact_freq = 150
    impact = np.sin(2 * np.pi * impact_freq * t)
    
    # Combine all elements with envelope
    envelope = np.exp(-6 * t / duration)
    sound = (0.6 * noise + 0.3 * rumble + 0.2 * impact) * envelope
    
    # Normalize and convert to 16-bit integer
    sound = sound / np.max(np.abs(sound))
    sound = np.int16(sound * 32767)
    
    # Save
    wavfile.write('assets/sounds/explosion.wav', sample_rate, sound)

def generate_powerup_sound():
    # Sample rate and duration
    sample_rate = 44100
    duration = 0.3
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Create ascending notes
    freqs = [400, 600, 800]
    sound = np.zeros_like(t)
    
    for i, freq in enumerate(freqs):
        start = i * duration / len(freqs)
        end = (i + 1) * duration / len(freqs)
        mask = (t >= start) & (t < end)
        sound[mask] = np.sin(2 * np.pi * freq * t[mask])
    
    # Add sparkle effect
    sparkle = 0.3 * np.sin(2 * np.pi * 2000 * t)
    
    # Combine and add envelope
    envelope = np.exp(-2 * t / duration)
    sound = (sound + sparkle) * envelope
    
    # Convert to 16-bit integer
    sound = np.int16(sound * 32767)
    
    # Save
    wavfile.write('assets/sounds/powerup.wav', sample_rate, sound)

if __name__ == "__main__":
    print("Generating AI sound effects...")
    generate_laser_sound()
    generate_explosion_sound()
    generate_powerup_sound()
    print("Sound effects generated!")
